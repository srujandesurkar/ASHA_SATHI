"""
Follow-up task database model generated from visit recommendations and danger alerts.
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from app.database import Base


class FollowUpTask(Base):
    __tablename__ = "follow_up_tasks"

    id = Column(String, primary_key=True, index=True)
    beneficiary_id = Column(String, index=True, nullable=False)
    beneficiary_name = Column(String, nullable=True)
    visit_id = Column(String, nullable=True)

    # ANC_CHECKUP, PNC_VISIT, IMMUNISATION, URGENT_REFERRAL, HBNC_VISIT
    task_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    due_date = Column(String, nullable=False)  # YYYY-MM-DD

    # Priority: "EMERGENCY", "HIGH", "NORMAL"
    priority = Column(String, nullable=False, default="NORMAL")

    # Status: "PENDING", "COMPLETED", "ESCALATED"
    status = Column(String, nullable=False, default="PENDING")

    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
