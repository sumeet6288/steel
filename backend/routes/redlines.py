from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.redline import Redline, RedlineCreate, RedlineStatus, AIExtraction
from models.audit_log import AuditLogCreate, AuditAction
from utils.dependencies import get_current_user
from ai_service.ai_assistant import AIService
from audit_service.audit import AuditService
import os
import base64
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import json

router = APIRouter(prefix="/redlines", tags=["redlines"])

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

ai_service = AIService()
audit_service = AuditService(db)

@router.post("/upload")
async def upload_redline(connection_id: str, file: UploadFile = File(...), user_id: str = Depends(get_current_user)):
    connection = await db.connections.find_one({"id": connection_id, "user_id": user_id}, {"_id": 0})
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")
    
    file_data = await file.read()
    file_b64 = base64.b64encode(file_data).decode('utf-8')
    
    redline = Redline(
        connection_id=connection_id,
        user_id=user_id,
        file_name=file.filename,
        file_path=f"/redlines/{connection_id}/{file.filename}"
    )
    
    doc = redline.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.redlines.insert_one(doc)
    
    return {
        "redline_id": redline.id,
        "status": redline.status,
        "message": "Redline uploaded successfully. Ready for AI interpretation."
    }

@router.post("/{redline_id}/interpret")
async def interpret_redline(redline_id: str, user_id: str = Depends(get_current_user)):
    redline = await db.redlines.find_one({"id": redline_id, "user_id": user_id}, {"_id": 0})
    if not redline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Redline not found")
    
    connection = await db.connections.find_one({"id": redline['connection_id']}, {"_id": 0})
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")
    
    await db.redlines.update_one(
        {"id": redline_id},
        {"$set": {"status": RedlineStatus.PROCESSING.value}}
    )
    
    connection_context = {
        "connection_id": connection['id'],
        "connection_type": connection['connection_type'],
        "current_parameters": connection['parameters']
    }
    
    ai_result = await ai_service.interpret_redline("", connection_context)
    
    extraction = AIExtraction(
        intent=ai_result.get('intent', ''),
        parameters=ai_result.get('parameters', {}),
        confidence=ai_result.get('confidence', 0.0),
        reasoning=ai_result.get('reasoning', '')
    )
    
    await db.redlines.update_one(
        {"id": redline_id},
        {
            "$set": {
                "status": RedlineStatus.EXTRACTED.value,
                "ai_extraction": extraction.model_dump(),
                "updated_at": datetime.now().isoformat()
            }
        }
    )
    
    await audit_service.log_action(AuditLogCreate(
        action=AuditAction.AI_REDLINE,
        user_id=user_id,
        connection_id=connection['id'],
        details={
            "redline_id": redline_id,
            "ai_confidence": ai_result.get('confidence', 0.0),
            "suggested_changes": ai_result.get('parameters', {})
        },
        ai_involved=True
    ))
    
    return {
        "redline_id": redline_id,
        "status": RedlineStatus.EXTRACTED.value,
        "ai_extraction": extraction.model_dump(),
        "disclaimer": "AI interpretation is ADVISORY ONLY. Human approval required before applying changes.",
        "warnings": ai_result.get('warnings', [])
    }

@router.post("/{redline_id}/approve")
async def approve_redline_changes(redline_id: str, approved_params: dict, user_id: str = Depends(get_current_user)):
    redline = await db.redlines.find_one({"id": redline_id, "user_id": user_id}, {"_id": 0})
    if not redline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Redline not found")
    
    connection = await db.connections.find_one({"id": redline['connection_id']}, {"_id": 0})
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connection not found")
    
    current_params = connection['parameters']
    updated_params = {**current_params, **approved_params}
    
    await db.connections.update_one(
        {"id": connection['id']},
        {
            "$set": {
                "parameters": updated_params,
                "updated_at": datetime.now().isoformat(),
                "status": "draft"
            }
        }
    )
    
    await db.redlines.update_one(
        {"id": redline_id},
        {
            "$set": {
                "status": RedlineStatus.APPROVED.value,
                "approved_changes": approved_params,
                "updated_at": datetime.now().isoformat()
            }
        }
    )
    
    await audit_service.log_action(AuditLogCreate(
        action=AuditAction.USER_APPROVAL,
        user_id=user_id,
        connection_id=connection['id'],
        details={
            "redline_id": redline_id,
            "approved_changes": approved_params,
            "human_approved": True
        }
    ))
    
    return {
        "message": "Changes approved and applied to connection",
        "connection_id": connection['id'],
        "updated_parameters": updated_params,
        "note": "Connection status reset to draft. Re-validate before export."
    }

@router.get("/{connection_id}/list")
async def get_connection_redlines(connection_id: str, user_id: str = Depends(get_current_user)):
    redlines = await db.redlines.find(
        {"connection_id": connection_id, "user_id": user_id},
        {"_id": 0}
    ).to_list(100)
    
    for redline in redlines:
        if isinstance(redline['created_at'], str):
            redline['created_at'] = datetime.fromisoformat(redline['created_at'])
        if isinstance(redline['updated_at'], str):
            redline['updated_at'] = datetime.fromisoformat(redline['updated_at'])
    
    return [Redline(**r) for r in redlines]