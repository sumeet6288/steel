from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone
from enum import Enum
import uuid

class ConnectionType(str, Enum):
    BEAM_TO_COLUMN_SHEAR = "beam_to_column_shear"
    BEAM_TO_BEAM_SHEAR = "beam_to_beam_shear"
    SINGLE_PLATE = "single_plate"
    DOUBLE_ANGLE = "double_angle"
    END_PLATE = "end_plate"

class ConnectionStatus(str, Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    FAILED = "failed"
    EXPORTED = "exported"

class ConnectionBase(BaseModel):
    name: str
    connection_type: ConnectionType
    description: Optional[str] = None

class ConnectionCreate(ConnectionBase):
    project_id: str
    parameters: Dict[str, Any] = {}

class ConnectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    status: Optional[ConnectionStatus] = None

class Connection(ConnectionBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    user_id: str
    parameters: Dict[str, Any] = {}
    geometry: Optional[Dict[str, Any]] = None
    validation_results: Optional[Dict[str, Any]] = None
    rule_checks: List[Dict[str, Any]] = []
    status: ConnectionStatus = ConnectionStatus.DRAFT
    ai_suggested: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))