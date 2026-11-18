"""
Beneficiary database model for synthetic pregnant women and newborns.
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime
from app.database import Base


class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id = Column(String, primary_key=True, index=True)  # e.g., "BEN-001"
    name = Column(String, nullable=False, index=True)
    age = Column(Integer, nullable=True)
    phone = Column(String, nullable=True)  # Synthetic 555-XXXX
    village = Column(String, nullable=False, default="Rampur")
    asha_id = Column(String, nullable=False, default="ASHA-RAMPUR-01")

    # Category: "PREGNANT", "NEWBORN", "MOTHER_INFANT", "CHILD"
    category = Column(String, nullable=False, default="PREGNANT")

    # Pregnancy specific
    lmp_date = Column(String, nullable=True)  # Last Menstrual Period
    edd_date = Column(String, nullable=True)  # Estimated Due Date
    parity = Column(Integer, nullable=True)   # Gravida/Parity

    # Infant specific
    infant_dob = Column(String, nullable=True)
    infant_gender = Column(String, nullable=True)
    birth_weight_kg = Column(Float, nullable=True)

    # Risk tracking
    high_risk = Column(Boolean, default=False)
    high_risk_reason = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
