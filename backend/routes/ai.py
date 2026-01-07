from fastapi import APIRouter, Depends
from models.connection import ConnectionType
from ai_service.ai_assistant import AIService
from utils.dependencies import get_current_user
from typing import Dict, Any

router = APIRouter(prefix="/ai", tags=["ai-assistant"])

ai_service = AIService()

@router.post("/suggest-connection")
async def suggest_connection_type(requirements: Dict[str, Any], user_id: str = Depends(get_current_user)):
    result = await ai_service.suggest_connection_type(requirements)
    return {
        **result,
        "disclaimer": "AI suggestion is ADVISORY ONLY. Engineer review required."
    }

@router.post("/generate-rfi")
async def generate_rfi(connection_data: Dict[str, Any], issue: str, user_id: str = Depends(get_current_user)):
    rfi_text = await ai_service.generate_rfi(connection_data, issue)
    return {
        "rfi": rfi_text,
        "disclaimer": "AI-generated RFI draft. Review and edit before sending."
    }