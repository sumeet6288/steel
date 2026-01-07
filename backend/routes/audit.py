from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.audit_log import AuditLog
from utils.dependencies import get_current_user
from audit_service.audit import AuditService
import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List

router = APIRouter(prefix="/audit", tags=["audit"])

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

audit_service = AuditService(db)

@router.get("/connection/{connection_id}", response_model=List[AuditLog])
async def get_connection_audit_trail(connection_id: str, user_id: str = Depends(get_current_user)):
    return await audit_service.get_connection_audit_trail(connection_id)

@router.get("/my-activity", response_model=List[AuditLog])
async def get_my_audit_trail(limit: int = 50, user_id: str = Depends(get_current_user)):
    return await audit_service.get_user_audit_trail(user_id, limit)