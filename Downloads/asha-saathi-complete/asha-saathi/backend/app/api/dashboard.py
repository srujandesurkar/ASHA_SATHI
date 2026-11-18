"""
Dashboard Statistics & Summary API Endpoint (Module 6)
Aggregates key public healthcare field metrics:
- Total visits, ANC, Newborn/PNC, Immunisation
- Urgent danger-sign referrals
- Overdue and pending follow-ups
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Dict, Any

from app.database import get_db
from app.models.visit_record import VisitRecord
from app.models.follow_up import FollowUpTask
from app.models.beneficiary import Beneficiary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


class DashboardStats(BaseModel):
    total_visits: int
    pregnancy_visits: int
    newborn_visits: int
    immunisation_visits: int
    urgent_referrals: int
    pending_follow_ups: int
    overdue_follow_ups: int
    high_risk_beneficiaries: int
    recent_visits: List[Dict[str, Any]]
    urgent_tasks: List[Dict[str, Any]]


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_statistics(db: AsyncSession = Depends(get_db)):
    # Total visits
    total_q = await db.execute(select(func.count(VisitRecord.id)))
    total_visits = total_q.scalar() or 0

    # ANC visits
    anc_q = await db.execute(select(func.count(VisitRecord.id)).where(VisitRecord.visit_type == "ANC"))
    pregnancy_visits = anc_q.scalar() or 0

    # Newborn visits
    nb_q = await db.execute(select(func.count(VisitRecord.id)).where(VisitRecord.visit_type.in_(["NEWBORN", "PNC"])))
    newborn_visits = nb_q.scalar() or 0

    # Immunisation visits
    imm_q = await db.execute(select(func.count(VisitRecord.id)).where(VisitRecord.visit_type == "IMMUNISATION"))
    immunisation_visits = imm_q.scalar() or 0

    # Urgent referrals
    urg_q = await db.execute(select(func.count(VisitRecord.id)).where(VisitRecord.has_danger_sign == True))
    urgent_referrals = urg_q.scalar() or 0

    # High-risk beneficiaries
    hr_q = await db.execute(select(func.count(Beneficiary.id)).where(Beneficiary.high_risk == True))
    high_risk_ben = hr_q.scalar() or 0

    # Pending follow-ups
    pending_q = await db.execute(select(func.count(FollowUpTask.id)).where(FollowUpTask.status == "PENDING"))
    pending_follow_ups = pending_q.scalar() or 0

    # Overdue follow-ups (due_date < today)
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    overdue_q = await db.execute(
        select(func.count(FollowUpTask.id)).where(
            and_(FollowUpTask.status == "PENDING", FollowUpTask.due_date < today_str)
        )
    )
    overdue_follow_ups = overdue_q.scalar() or 0

    # Recent visits (last 5)
    rec_q = await db.execute(
        select(VisitRecord).order_by(VisitRecord.created_at.desc()).limit(5)
    )
    recent_visits_list = [
        {
            "id": r.id,
            "beneficiary_id": r.beneficiary_id,
            "beneficiary_name": r.beneficiary_name,
            "visit_type": r.visit_type,
            "visit_date": r.visit_date,
            "weight_kg": r.weight_kg,
            "has_danger_sign": r.has_danger_sign,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in rec_q.scalars().all()
    ]

    # Urgent tasks (priority == EMERGENCY or HIGH and status == PENDING)
    urg_tasks_q = await db.execute(
        select(FollowUpTask).where(
            and_(
                FollowUpTask.status == "PENDING",
                FollowUpTask.priority.in_(["EMERGENCY", "HIGH"])
            )
        ).limit(5)
    )
    urgent_tasks_list = [
        {
            "id": t.id,
            "beneficiary_id": t.beneficiary_id,
            "beneficiary_name": t.beneficiary_name,
            "title": t.title,
            "description": t.description,
            "due_date": t.due_date,
            "priority": t.priority
        }
        for t in urg_tasks_q.scalars().all()
    ]

    return DashboardStats(
        total_visits=total_visits,
        pregnancy_visits=pregnancy_visits,
        newborn_visits=newborn_visits,
        immunisation_visits=immunisation_visits,
        urgent_referrals=urgent_referrals,
        pending_follow_ups=pending_follow_ups,
        overdue_follow_ups=overdue_follow_ups,
        high_risk_beneficiaries=high_risk_ben,
        recent_visits=recent_visits_list,
        urgent_tasks=urgent_tasks_list
    )
