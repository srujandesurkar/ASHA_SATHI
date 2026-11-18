"""
Follow-Up Task Management API Endpoints (Module 5)
Handles:
- Scheduled ANC/PNC/Immunisation follow-up tasks.
- Urgent danger-sign referral follow-ups.
- Status updates (Pending -> Completed).
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, ConfigDict

from app.database import get_db
from app.models.follow_up import FollowUpTask

router = APIRouter(prefix="/follow-ups", tags=["Follow-Up Manager"])


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    beneficiary_id: str
    beneficiary_name: Optional[str] = None
    visit_id: Optional[str] = None
    task_type: str
    title: str
    description: Optional[str] = None
    due_date: str
    priority: str
    status: str
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


@router.get("", response_model=List[TaskResponse])
async def list_follow_ups(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    beneficiary_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(FollowUpTask).order_by(
        # Order emergencies first
        FollowUpTask.priority == "EMERGENCY",
        FollowUpTask.due_date
    )
    if status:
        stmt = stmt.where(FollowUpTask.status == status.upper())
    if priority:
        stmt = stmt.where(FollowUpTask.priority == priority.upper())
    if beneficiary_id:
        stmt = stmt.where(FollowUpTask.beneficiary_id == beneficiary_id.upper())

    result = await db.execute(stmt)
    return result.scalars().all()


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def mark_task_complete(task_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(FollowUpTask).where(FollowUpTask.id == task_id)
    result = await db.execute(stmt)
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "COMPLETED"
    task.completed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(task)
    return task
