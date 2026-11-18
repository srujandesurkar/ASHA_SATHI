"""
Schemas for voice session management, read-back, corrections, and confirmations.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from app.schemas.visit_record import VisitRecordExtraction
from app.schemas.danger_sign import DangerShieldResult


class SpokenCorrectionRequest(BaseModel):
    session_id: str
    spoken_correction: str = Field(description="Spoken phrase, e.g. 'No, weight is 2.8 kilo'")
    current_record: Dict[str, Any]


class SpokenCorrectionResponse(BaseModel):
    field_modified: str
    previous_value: Any
    updated_value: Any
    updated_record: Dict[str, Any]
    readback_speech_hi: str
    readback_speech_en: str
    ready_for_confirmation: bool = True


class SpokenConfirmationRequest(BaseModel):
    session_id: str
    spoken_phrase: str = Field(description="e.g. 'Haan save karo' or 'Cancel'")
    record_data: Dict[str, Any]


class SpokenConfirmationResponse(BaseModel):
    confirmed: bool
    saved: bool
    record_id: Optional[str] = None
    message: str
    audio_readback_url: Optional[str] = None


class VoiceSessionState(BaseModel):
    session_id: str
    status: str = "LISTENING"  # LISTENING, EXTRACTED, READBACK, CORRECTION, CONFIRMED
    current_transcript: str = ""
    language: str = "hi-IN-codemix"
    extracted_record: Optional[VisitRecordExtraction] = None
    danger_assessment: Optional[DangerShieldResult] = None
    readback_text_hi: Optional[str] = None
    readback_text_en: Optional[str] = None
    is_confirmed: bool = False
    is_demo_mode: bool = True
