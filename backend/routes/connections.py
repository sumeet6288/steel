from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.connection import Connection, ConnectionCreate, ConnectionUpdate, ConnectionStatus
from models.audit_log import AuditLogCreate, AuditAction
from utils.dependencies import get_current_user
from rule_engine import AISC360RuleEngine
from geometry_engine import GeometryGenerator
from validation_engine.validator import ValidationEngine
from export_service.tekla_exporter import TeklaExporter
from audit_service.audit import AuditService
from typing import List
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

router = APIRouter(prefix="/connections", tags=["connections"])

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

rule_engine = AISC360RuleEngine()
audit_service = AuditService(db)

@router.post("/", response_model=Connection)
async def create_connection(connection_create: ConnectionCreate, user_id: str = Depends(get_current_user)):
    project = await db.projects.find_one({"id": connection_create.project_id, "user_id": user_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    connection = Connection(**connection_create.model_dump(), user_id=user_id)
    doc = connection.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.connections.insert_one(doc)
    
    await db.projects.update_one(
        {"id": connection_create.project_id},
        {"$inc": {"connection_count": 1}}
    )
    
    await audit_service.log_action(AuditLogCreate(
        action=AuditAction.CREATE_CONNECTION,
        user_id=user_id,
        connection_id=connection.id,
        project_id=connection_create.project_id,
        details={"connection_type": connection.connection_type}
    ))
    
    return connection

@router.get("/", response_model=List[Connection])
async def get_connections(project_id: str = None, user_id: str = Depends(get_current_user)):
    query = {"user_id": user_id}
    if project_id:
        query["project_id"] = project_id
    
    connections = await db.connections.find(query, {"_id": 0}).to_list(1000)
    
    for conn in connections:
        if isinstance(conn['created_at'], str):
            conn['created_at'] = datetime.fromisoformat(conn['created_at'])
        if isinstance(conn['updated_at'], str):
            conn['updated_at'] = datetime.fromisoformat(conn['updated_at'])
    
    return [Connection(**c) for c in connections]

@router.get("/{connection_id}", response_model=Connection)
async def get_connection(connection_id: str, user_id: str = Depends(get_current_user)):
    connection = await db.connections.find_one({"id": connection_id, "user_id": user_id}, {"_id": 0})
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")
    
    if isinstance(connection['created_at'], str):
        connection['created_at'] = datetime.fromisoformat(connection['created_at'])
    if isinstance(connection['updated_at'], str):
        connection['updated_at'] = datetime.fromisoformat(connection['updated_at'])
    
    return Connection(**connection)

@router.put("/{connection_id}", response_model=Connection)
async def update_connection(connection_id: str, connection_update: ConnectionUpdate, user_id: str = Depends(get_current_user)):
    connection = await db.connections.find_one({"id": connection_id, "user_id": user_id}, {"_id": 0})
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")
    
    update_data = connection_update.model_dump(exclude_unset=True)
    if update_data:
        update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        await db.connections.update_one({"id": connection_id}, {"$set": update_data})
    
    await audit_service.log_action(AuditLogCreate(
        action=AuditAction.UPDATE_CONNECTION,
        user_id=user_id,
        connection_id=connection_id,
        details={"updated_fields": list(update_data.keys())}
    ))
    
    updated_connection = await db.connections.find_one({"id": connection_id}, {"_id": 0})
    if isinstance(updated_connection['created_at'], str):
        updated_connection['created_at'] = datetime.fromisoformat(updated_connection['created_at'])
    if isinstance(updated_connection['updated_at'], str):
        updated_connection['updated_at'] = datetime.fromisoformat(updated_connection['updated_at'])
    
    return Connection(**updated_connection)

@router.post("/{connection_id}/validate")
async def validate_connection(connection_id: str, user_id: str = Depends(get_current_user)):
    connection = await db.connections.find_one({"id": connection_id, "user_id": user_id}, {"_id": 0})
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")
    
    param_validation = ValidationEngine.validate_parameters(
        connection['parameters'],
        connection['connection_type']
    )
    
    if not param_validation['is_valid']:
        return {
            "status": "failed",
            "message": "Parameter validation failed",
            "validation_results": param_validation
        }
    
    rule_result = rule_engine.validate_connection(
        connection['connection_type'],
        connection['parameters']
    )
    
    geometry = GeometryGenerator.generate_connection(
        connection['connection_type'],
        connection['parameters']
    )
    
    geom_validation = ValidationEngine.validate_geometry(geometry)
    
    await db.connections.update_one(
        {"id": connection_id},
        {
            "$set": {
                "validation_results": rule_result.model_dump(),
                "geometry": geometry,
                "rule_checks": [check.model_dump() for check in rule_result.checks],
                "status": ConnectionStatus.VALIDATED if rule_result.is_valid else ConnectionStatus.FAILED,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    await audit_service.log_action(AuditLogCreate(
        action=AuditAction.VALIDATE_CONNECTION,
        user_id=user_id,
        connection_id=connection_id,
        details={
            "rule_result": rule_result.summary,
            "is_valid": rule_result.is_valid
        }
    ))
    
    for check in rule_result.checks:
        await audit_service.log_action(AuditLogCreate(
            action=AuditAction.RULE_CHECK,
            user_id=user_id,
            connection_id=connection_id,
            details=check.model_dump()
        ))
    
    return {
        "status": "validated" if rule_result.is_valid else "failed",
        "rule_validation": rule_result.model_dump(),
        "geometry_validation": geom_validation,
        "geometry": geometry
    }

@router.post("/{connection_id}/export/tekla")
async def export_to_tekla(connection_id: str, user_id: str = Depends(get_current_user)):
    connection = await db.connections.find_one({"id": connection_id, "user_id": user_id}, {"_id": 0})
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")
    
    if not connection.get('geometry'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connection must be validated before export"
        )
    
    tekla_output = TeklaExporter.export_connection(connection, connection['geometry'])
    
    await db.connections.update_one(
        {"id": connection_id},
        {"$set": {"status": ConnectionStatus.EXPORTED.value}}
    )
    
    await audit_service.log_action(AuditLogCreate(
        action=AuditAction.EXPORT_TEKLA,
        user_id=user_id,
        connection_id=connection_id,
        details={"export_format": "tekla_parametric"}
    ))
    
    return {
        "tekla_export": tekla_output,
        "format": "tekla_parametric_json",
        "editable": True,
        "disclaimer": "Engineering review and approval required before fabrication"
    }

@router.delete("/{connection_id}")
async def delete_connection(connection_id: str, user_id: str = Depends(get_current_user)):
    connection = await db.connections.find_one({"id": connection_id, "user_id": user_id}, {"_id": 0})
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")
    
    result = await db.connections.delete_one({"id": connection_id, "user_id": user_id})
    
    await db.projects.update_one(
        {"id": connection['project_id']},
        {"$inc": {"connection_count": -1}}
    )
    
    return {"message": "Connection deleted successfully"}