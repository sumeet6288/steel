from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid

class AuditAction(str, Enum):
    CREATE_CONNECTION = "create_connection"
    UPDATE_CONNECTION = "update_connection"
    VALIDATE_CONNECTION = "validate_connection"
    AI_SUGGESTION = "ai_suggestion"
    AI_REDLINE = "ai_redline"
    EXPORT_TEKLA = "export_tekla"
    RULE_CHECK = "rule_check"
    USER_APPROVAL = "user_approval"

class AuditLogCreate(BaseModel):
    action: AuditAction
    user_id: str
    connection_id: Optional[str] = None
    project_id: Optional[str] = None
    details: Dict[str, Any] = {}
    ai_involved: bool = False

class AuditLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: AuditAction
    user_id: str
    connection_id: Optional[str] = None
    project_id: Optional[str] = None
    details: Dict[str, Any] = {}
    ai_involved: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))