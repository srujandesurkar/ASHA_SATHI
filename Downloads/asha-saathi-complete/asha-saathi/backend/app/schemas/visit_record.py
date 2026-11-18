"""
Schemas for visit records and structured entity extraction with evidence linking.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class FieldEvidence(BaseModel):
    field_name: str
    spoken_source: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.9)
    extracted_value: Any


class VisitRecordBase(BaseModel):
    beneficiary_id: Optional[str] = None
    beneficiary_name: Optional[str] = None
    visit_type: Optional[str] = None  # ANC, PNC, IMMUNISATION, NEWBORN
    visit_date: Optional[str] = None  # YYYY-MM-DD
    weight_kg: Optional[float] = None
    blood_pressure: Optional[str] = None
    ifa_tablets_given: Optional[int] = None
    vaccinations_due: List[str] = Field(default_factory=list)
    vaccinations_completed: List[str] = Field(default_factory=list)
    anc_pnc_details: Dict[str, Any] = Field(default_factory=dict)
    next_visit_date: Optional[str] = None
    visit_notes: Optional[str] = None


class VisitRecordExtraction(VisitRecordBase):
    """Extraction output containing field evidence and missing field prompts."""
    evidence: Dict[str, FieldEvidence] = Field(default_factory=dict)
    missing_fields: List[str] = Field(default_factory=list)
    clarification_prompt_hi: Optional[str] = None
    clarification_prompt_en: Optional[str] = None
    has_danger_sign: bool = False
    danger_signs: List[str] = Field(default_factory=list)


class VisitRecordCreate(VisitRecordBase):
    id: Optional[str] = None
    evidence: Dict[str, Any] = Field(default_factory=dict)
    has_danger_sign: bool = False
    danger_sign_details: List[Dict[str, Any]] = Field(default_factory=list)
    referral_facility: Optional[str] = None
    is_confirmed: bool = False
    raw_transcript_encrypted: Optional[str] = None


class VisitRecordResponse(VisitRecordCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: Any
