from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from enum import Enum
import uuid

class RedlineStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    APPROVED = "approved"
    REJECTED = "rejected"

class AIExtraction(BaseModel):
    intent: str
    parameters: Dict[str, Any] = {}
    confidence: float = 0.0
    reasoning: str = ""

class RedlineCreate(BaseModel):
    connection_id: str
    file_name: str
    file_data: str

class Redline(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    connection_id: str
    user_id: str
    file_name: str
    file_path: str
    status: RedlineStatus = RedlineStatus.UPLOADED
    ai_extraction: Optional[AIExtraction] = None
    approved_changes: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))