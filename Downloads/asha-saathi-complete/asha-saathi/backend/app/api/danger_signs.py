"""
Danger Sign Evaluation API Endpoint
Direct deterministic evaluation against MoHFW / IMNCI public health guidelines.
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.danger_shield import danger_shield
from app.schemas.danger_sign import DangerShieldResult

router = APIRouter(prefix="/danger-signs", tags=["Danger Shield Engine"])


class DangerEvalRequest(BaseModel):
    speech_transcript: str = Field(description="Spoken transcript in Indic/code-mixed language")


@router.post("/evaluate", response_model=DangerShieldResult)
async def evaluate_danger_signs(request: DangerEvalRequest):
    return danger_shield.evaluate(request.speech_transcript)
