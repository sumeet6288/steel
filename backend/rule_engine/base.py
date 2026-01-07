from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum
from abc import ABC, abstractmethod

class RuleStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"

class RuleCheck(BaseModel):
    rule_id: str
    rule_name: str
    status: RuleStatus
    message: str
    code_reference: str
    calculated_value: Optional[float] = None
    limit_value: Optional[float] = None
    details: Dict[str, Any] = {}

class RuleResult(BaseModel):
    overall_status: RuleStatus
    checks: List[RuleCheck]
    summary: str
    is_valid: bool

class RuleEngine(ABC):
    @abstractmethod
    def validate_connection(self, connection_type: str, parameters: Dict[str, Any]) -> RuleResult:
        pass