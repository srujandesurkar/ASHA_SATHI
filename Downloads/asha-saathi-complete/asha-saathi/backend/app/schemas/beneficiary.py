"""
Schemas for synthetic beneficiaries.
"""
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class BeneficiaryBase(BaseModel):
    id: str = Field(description="Unique synthetic ID, e.g., BEN-001")
    name: str
    age: Optional[int] = None
    phone: Optional[str] = None
    village: str = "Rampur"
    asha_id: str = "ASHA-RAMPUR-01"
    category: str = "PREGNANT"  # PREGNANT, NEWBORN, MOTHER_INFANT, CHILD
    lmp_date: Optional[str] = None
    edd_date: Optional[str] = None
    parity: Optional[int] = None
    infant_dob: Optional[str] = None
    infant_gender: Optional[str] = None
    birth_weight_kg: Optional[float] = None
    high_risk: bool = False
    high_risk_reason: Optional[str] = None


class BeneficiaryCreate(BeneficiaryBase):
    pass


class BeneficiaryResponse(BeneficiaryBase):
    model_config = ConfigDict(from_attributes=True)
    created_at: Optional[Any] = None
    updated_at: Optional[Any] = None
