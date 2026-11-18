"""
Schemas for deterministic danger sign detection and emergency escalation.
Based on official Indian public health guidelines:
- MoHFW / NHM Maternal & Child Health
- IMNCI (Integrated Management of Neonatal and Childhood Illness)
- ASHA Handbook Module 6 & 7 (Home Based Newborn Care)
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class DangerSignMatch(BaseModel):
    category: str = Field(description="'PREGNANCY' or 'NEWBORN'")
    sign_code: str = Field(description="Unique code, e.g. PREG_BLEEDING, NB_HIGH_FEVER")
    sign_name: str = Field(description="Clinical title, e.g. 'Vaginal Bleeding in Pregnancy'")
    matched_term: str = Field(description="Exact phrase matched in user speech")
    severity: str = Field(default="EMERGENCY", description="'EMERGENCY' or 'URGENT'")
    guideline_source: str = Field(description="Official guideline reference and module")
    immediate_action: str = Field(description="Fixed non-diagnostic protocol, e.g. 'Refer immediately to PHC/FRU'")


class DangerShieldResult(BaseModel):
    has_danger_sign: bool = False
    priority: str = Field(default="NORMAL", description="'EMERGENCY' | 'URGENT' | 'NORMAL'")
    detected_signs: List[DangerSignMatch] = Field(default_factory=list)
    negations_detected: List[str] = Field(
        default_factory=list,
        description="Explicit negations recognized, e.g. 'bukhar nahi hai' preventing false alert"
    )
    spoken_alert_hi: Optional[str] = Field(
        default=None,
        description="Hindi spoken referral prompt for ASHA worker"
    )
    spoken_alert_en: Optional[str] = Field(
        default=None,
        description="English spoken referral prompt for ASHA worker"
    )
    referral_required: bool = False
    recommended_facility: Optional[str] = Field(
        default=None,
        description="Primary Health Centre (PHC) or First Referral Unit (FRU)"
    )
