"""
Visit Record database model representing completed healthcare field entries.
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON
from app.database import Base


class VisitRecord(Base):
    __tablename__ = "visit_records"

    id = Column(String, primary_key=True, index=True)  # e.g., "VISIT-20261112-001"
    beneficiary_id = Column(String, index=True, nullable=False)
    beneficiary_name = Column(String, nullable=True)

    # ANC, PNC, IMMUNISATION, NEWBORN
    visit_type = Column(String, nullable=False)
    visit_date = Column(String, nullable=False)  # YYYY-MM-DD

    # Clinical & field measurements
    weight_kg = Column(Float, nullable=True)
    blood_pressure = Column(String, nullable=True)  # e.g., "120/80"
    ifa_tablets_given = Column(Integer, nullable=True)

    # Vaccinations (stored as JSON lists)
    vaccinations_due = Column(JSON, nullable=True, default=list)
    vaccinations_completed = Column(JSON, nullable=True, default=list)

    # ANC / PNC details & notes
    anc_pnc_details = Column(JSON, nullable=True, default=dict)
    next_visit_date = Column(String, nullable=True)
    visit_notes = Column(Text, nullable=True)

    # Spoken source evidence mapping
    evidence = Column(JSON, nullable=True, default=dict)

    # Danger shield assessment
    has_danger_sign = Column(Boolean, default=False)
    danger_sign_details = Column(JSON, nullable=True, default=list)
    referral_facility = Column(String, nullable=True)

    # Voice confirmation & session tracking
    is_confirmed = Column(Boolean, default=False)
    confirmed_at = Column(DateTime, nullable=True)
    raw_transcript_encrypted = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
