"""
Visit Records API Endpoints
Handles extraction from speech, strict confirmation checks, and saving with automatic follow-up task creation.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.visit_record import VisitRecord
from app.models.beneficiary import Beneficiary
from app.models.follow_up import FollowUpTask
from app.schemas.visit_record import VisitRecordExtraction, VisitRecordResponse
from app.services.extraction_service import extraction_engine
from app.services.danger_shield import danger_shield

router = APIRouter(prefix="/visits", tags=["Visits"])


class ExtractRequest(BaseModel):
    speech_text: str


class ConfirmAndSaveRequest(BaseModel):
    beneficiary_id: Optional[str] = None
    beneficiary_name: Optional[str] = None
    visit_type: str
    visit_date: str
    weight_kg: Optional[float] = None
    blood_pressure: Optional[str] = None
    ifa_tablets_given: Optional[int] = None
    vaccinations_due: List[str] = []
    vaccinations_completed: List[str] = []
    anc_pnc_details: dict = {}
    next_visit_date: Optional[str] = None
    visit_notes: Optional[str] = None
    evidence: dict = {}
    has_danger_sign: bool = False
    danger_sign_details: list = []
    referral_facility: Optional[str] = None
    is_confirmed: bool = False


@router.post("/extract", response_model=VisitRecordExtraction)
async def extract_visit_from_speech(request: ExtractRequest, db: AsyncSession = Depends(get_db)):
    """
    Extracts structured visit record from Indic/code-mixed speech transcript.
    Links beneficiary name if ID is recognized.
    """
    extraction = extraction_engine.extract(request.speech_text)

    # Link beneficiary name if known
    if extraction.beneficiary_id:
        stmt = select(Beneficiary).where(Beneficiary.id == extraction.beneficiary_id.upper())
        result = await db.execute(stmt)
        ben = result.scalars().first()
        if ben:
            extraction.beneficiary_name = ben.name

    return extraction


@router.post("/confirm-and-save", response_model=VisitRecordResponse)
async def confirm_and_save_visit(request: ConfirmAndSaveRequest, db: AsyncSession = Depends(get_db)):
    """
    Strict safety check: Will NEVER save an unconfirmed record!
    Generates follow-up tasks and updates risk status if danger signs are present.
    """
    if not request.is_confirmed:
        raise HTTPException(
            status_code=400,
            detail="Visit record cannot be saved without explicit spoken confirmation."
        )

    visit_id = f"VISIT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"

    # Auto-resolve beneficiary name if missing
    ben_name = request.beneficiary_name
    if request.beneficiary_id and not ben_name:
        stmt = select(Beneficiary).where(Beneficiary.id == request.beneficiary_id.upper())
        result = await db.execute(stmt)
        ben = result.scalars().first()
        if ben:
            ben_name = ben.name

    # Check for danger signs deterministically if not already computed
    has_danger = request.has_danger_sign
    danger_details = request.danger_sign_details
    if not danger_details and request.visit_notes:
        eval_res = danger_shield.evaluate(request.visit_notes)
        has_danger = eval_res.has_danger_sign
        danger_details = [d.dict() for d in eval_res.detected_signs]

    record = VisitRecord(
        id=visit_id,
        beneficiary_id=request.beneficiary_id or "UNKNOWN",
        beneficiary_name=ben_name,
        visit_type=request.visit_type,
        visit_date=request.visit_date,
        weight_kg=request.weight_kg,
        blood_pressure=request.blood_pressure,
        ifa_tablets_given=request.ifa_tablets_given,
        vaccinations_due=request.vaccinations_due,
        vaccinations_completed=request.vaccinations_completed,
        anc_pnc_details=request.anc_pnc_details,
        next_visit_date=request.next_visit_date,
        visit_notes=request.visit_notes,
        evidence=request.evidence,
        has_danger_sign=has_danger,
        danger_sign_details=danger_details,
        referral_facility="Primary Health Centre (PHC)" if has_danger else None,
        is_confirmed=True,
        confirmed_at=datetime.utcnow()
    )
    db.add(record)

    # 1. If danger sign present: flag beneficiary and add emergency follow-up task
    if has_danger and request.beneficiary_id:
        ben_stmt = select(Beneficiary).where(Beneficiary.id == request.beneficiary_id.upper())
        ben_res = await db.execute(ben_stmt)
        ben_obj = ben_res.scalars().first()
        if ben_obj:
            ben_obj.high_risk = True
            sign_names = [d.get("sign_name", "Danger Sign") for d in danger_details]
            ben_obj.high_risk_reason = f"Danger Sign: {', '.join(sign_names)}"

        # Create emergency follow-up task
        task_id = f"TASK-EMERGENCY-{uuid.uuid4().hex[:6].upper()}"
        emergency_task = FollowUpTask(
            id=task_id,
            beneficiary_id=request.beneficiary_id,
            beneficiary_name=ben_name,
            visit_id=visit_id,
            task_type="URGENT_REFERRAL",
            title=f"URGENT: PHC Referral for {ben_name or request.beneficiary_id}",
            description=f"Danger sign detected: {', '.join([d.get('sign_name', '') for d in danger_details])}. Verify PHC admission.",
            due_date=request.visit_date,
            priority="EMERGENCY",
            status="PENDING"
        )
        db.add(emergency_task)

    # 2. If next visit scheduled: create standard follow-up task
    if request.next_visit_date:
        task_id = f"TASK-SCHEDULED-{uuid.uuid4().hex[:6].upper()}"
        scheduled_task = FollowUpTask(
            id=task_id,
            beneficiary_id=request.beneficiary_id or "UNKNOWN",
            beneficiary_name=ben_name,
            visit_id=visit_id,
            task_type=f"{request.visit_type}_FOLLOWUP",
            title=f"Scheduled {request.visit_type} Follow-up for {ben_name or 'Beneficiary'}",
            description=f"Follow-up visit as planned during visit {visit_id}.",
            due_date=request.next_visit_date,
            priority="NORMAL",
            status="PENDING"
        )
        db.add(scheduled_task)

    # 3. If vaccinations due: create immunization follow-up task
    if request.vaccinations_due:
        vac_task_id = f"TASK-VAC-{uuid.uuid4().hex[:6].upper()}"
        vac_task = FollowUpTask(
            id=vac_task_id,
            beneficiary_id=request.beneficiary_id or "UNKNOWN",
            beneficiary_name=ben_name,
            visit_id=visit_id,
            task_type="IMMUNISATION",
            title=f"Immunisation Due: {', '.join(request.vaccinations_due)}",
            description=f"Administer due vaccines: {', '.join(request.vaccinations_due)}",
            due_date=request.next_visit_date or request.visit_date,
            priority="HIGH",
            status="PENDING"
        )
        db.add(vac_task)

    await db.commit()
    await db.refresh(record)
    return record


@router.get("", response_model=List[VisitRecordResponse])
async def list_visits(
    beneficiary_id: Optional[str] = None,
    visit_type: Optional[str] = None,
    has_danger_sign: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(VisitRecord).order_by(desc(VisitRecord.created_at)).limit(limit)
    if beneficiary_id:
        stmt = stmt.where(VisitRecord.beneficiary_id == beneficiary_id.upper())
    if visit_type:
        stmt = stmt.where(VisitRecord.visit_type == visit_type)
    if has_danger_sign is not None:
        stmt = stmt.where(VisitRecord.has_danger_sign == has_danger_sign)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{visit_id}", response_model=VisitRecordResponse)
async def get_visit_details(visit_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(VisitRecord).where(VisitRecord.id == visit_id)
    result = await db.execute(stmt)
    rec = result.scalars().first()
    if not rec:
        raise HTTPException(status_code=404, detail="Visit record not found")
    return rec
