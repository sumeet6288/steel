from motor.motor_asyncio import AsyncIOMotorDatabase
from models.audit_log import AuditLog, AuditLogCreate
from typing import List, Optional
from datetime import datetime

class AuditService:
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def log_action(self, log_create: AuditLogCreate) -> AuditLog:
        audit_log = AuditLog(**log_create.model_dump())
        doc = audit_log.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        
        await self.db.audit_logs.insert_one(doc)
        return audit_log
    
    async def get_connection_audit_trail(self, connection_id: str) -> List[AuditLog]:
        logs = await self.db.audit_logs.find(
            {"connection_id": connection_id},
            {"_id": 0}
        ).sort("timestamp", -1).to_list(1000)
        
        for log in logs:
            if isinstance(log['timestamp'], str):
                log['timestamp'] = datetime.fromisoformat(log['timestamp'])
        
        return [AuditLog(**log) for log in logs]
    
    async def get_user_audit_trail(self, user_id: str, limit: int = 100) -> List[AuditLog]:
        logs = await self.db.audit_logs.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit).to_list(limit)
        
        for log in logs:
            if isinstance(log['timestamp'], str):
                log['timestamp'] = datetime.fromisoformat(log['timestamp'])
        
        return [AuditLog(**log) for log in logs]