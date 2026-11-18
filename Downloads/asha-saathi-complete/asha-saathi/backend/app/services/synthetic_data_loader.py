"""
Synthetic Beneficiary & Field Data Seeder
-----------------------------------------
Loads realistic synthetic data for ASHA workers in rural/semi-urban India.
All data is 100% synthetic (compliant with DPDP Act and Responsible AI guardrails).
"""
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.beneficiary import Beneficiary
from app.models.visit_record import VisitRecord
from app.models.follow_up import FollowUpTask

SYNTHETIC_BENEFICIARIES = [
    {
        "id": "BEN-001",
        "name": "Sunita Devi",
        "age": 24,
        "phone": "555-0101",
        "village": "Rampur",
        "asha_id": "ASHA-RAMPUR-01",
        "category": "PREGNANT",
        "lmp_date": "2026-03-15",
        "edd_date": "2026-12-22",
        "parity": 2,
        "high_risk": False,
        "high_risk_reason": None
    },
    {
        "id": "BEN-002",
        "name": "Pooja Sharma",
        "age": 28,
        "phone": "555-0102",
        "village": "Rampur",
        "asha_id": "ASHA-RAMPUR-01",
        "category": "NEWBORN",
        "infant_dob": "2026-11-02",
        "infant_gender": "Female",
        "birth_weight_kg": 2.7,
        "high_risk": False,
        "high_risk_reason": None
    },
    {
        "id": "BEN-003",
        "name": "Anita Kumari",
        "age": 22,
        "phone": "555-0103",
        "village": "Shivpur",
        "asha_id": "ASHA-RAMPUR-01",
        "category": "PREGNANT",
        "lmp_date": "2026-04-10",
        "edd_date": "2027-01-17",
        "parity": 1,
        "high_risk": True,
        "high_risk_reason": "Severe Anemia (Hb 7.8 g/dL)"
    },
    {
        "id": "BEN-004",
        "name": "Rekha Yadav",
        "age": 26,
        "phone": "555-0104",
        "village": "Rampur",
        "asha_id": "ASHA-RAMPUR-01",
        "category": "CHILD",
        "infant_dob": "2026-08-14",
        "infant_gender": "Male",
        "birth_weight_kg": 3.1,
        "high_risk": False,
        "high_risk_reason": None
    },
    {
        "id": "BEN-005",
        "name": "Kavita Verma",
        "age": 30,
        "phone": "555-0105",
        "village": "Anandpur",
        "asha_id": "ASHA-RAMPUR-01",
        "category": "NEWBORN",
        "infant_dob": "2026-11-09",
        "infant_gender": "Male",
        "birth_weight_kg": 2.5,
        "high_risk": True,
        "high_risk_reason": "Low birth weight (LBW)"
    }
]

INITIAL_VISITS = [
    {
        "id": "VISIT-SEED-001",
        "beneficiary_id": "BEN-001",
        "beneficiary_name": "Sunita Devi",
        "visit_type": "ANC",
        "visit_date": "2026-10-20",
        "weight_kg": 52.0,
        "blood_pressure": "118/76",
        "ifa_tablets_given": 30,
        "vaccinations_due": ["TT-2"],
        "vaccinations_completed": ["TT-1"],
        "next_visit_date": "2026-11-20",
        "visit_notes": "ANC checkup routine. Fundal height 28 weeks. Mother feeling healthy.",
        "has_danger_sign": False,
        "is_confirmed": True
    },
    {
        "id": "VISIT-SEED-002",
        "beneficiary_id": "BEN-002",
        "beneficiary_name": "Pooja Sharma",
        "visit_type": "NEWBORN",
        "visit_date": "2026-11-05",
        "weight_kg": 2.7,
        "vaccinations_due": ["Pentavalent-1", "Rotavirus-1"],
        "vaccinations_completed": ["BCG", "OPV-0", "Hepatitis B"],
        "next_visit_date": "2026-11-19",
        "visit_notes": "HBNC Day 3 visit. Baby feeding well. Cord clean and dry.",
        "has_danger_sign": False,
        "is_confirmed": True
    }
]

INITIAL_FOLLOW_UPS = [
    {
        "id": "TASK-SEED-001",
        "beneficiary_id": "BEN-001",
        "beneficiary_name": "Sunita Devi",
        "visit_id": "VISIT-SEED-001",
        "task_type": "ANC_CHECKUP",
        "title": "3rd Trimester ANC Checkup",
        "description": "Routine blood pressure, hemoglobin check, and TT-2 injection.",
        "due_date": "2026-11-20",
        "priority": "NORMAL",
        "status": "PENDING"
    },
    {
        "id": "TASK-SEED-002",
        "beneficiary_id": "BEN-003",
        "beneficiary_name": "Anita Kumari",
        "visit_id": None,
        "task_type": "URGENT_REFERRAL",
        "title": "Severe Anemia PHC Referral Check",
        "description": "Confirm patient visited PHC for iron sucrose IV infusion.",
        "due_date": "2026-11-14",
        "priority": "HIGH",
        "status": "PENDING"
    },
    {
        "id": "TASK-SEED-003",
        "beneficiary_id": "BEN-004",
        "beneficiary_name": "Rekha Yadav",
        "visit_id": None,
        "task_type": "IMMUNISATION",
        "title": "14-Week Immunisation Due",
        "description": "Pentavalent-3, OPV-3, IPV-2, and Rotavirus-3.",
        "due_date": "2026-11-25",
        "priority": "NORMAL",
        "status": "PENDING"
    }
]


async def seed_synthetic_data(db: AsyncSession):
    """Seed initial synthetic database if empty."""
    # Check if beneficiaries already exist
    stmt = select(Beneficiary)
    result = await db.execute(stmt)
    existing = result.scalars().first()
    if existing:
        return

    # Seed beneficiaries
    for b in SYNTHETIC_BENEFICIARIES:
        db.add(Beneficiary(**b))

    # Seed visits
    for v in INITIAL_VISITS:
        db.add(VisitRecord(**v))

    # Seed tasks
    for t in INITIAL_FOLLOW_UPS:
        db.add(FollowUpTask(**t))

    await db.commit()
