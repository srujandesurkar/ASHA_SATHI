"""
Beneficiary Lookup & Search API Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.beneficiary import Beneficiary
from app.schemas.beneficiary import BeneficiaryResponse

router = APIRouter(prefix="/beneficiaries", tags=["Beneficiaries"])


@router.get("", response_model=List[BeneficiaryResponse])
async def list_beneficiaries(
    search: Optional[str] = Query(None, description="Search by name, ID or village"),
    village: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Beneficiary)
    if village:
        stmt = stmt.where(Beneficiary.village == village)
    if category:
        stmt = stmt.where(Beneficiary.category == category)
    if search:
        term = f"%{search}%"
        stmt = stmt.where(or_(
            Beneficiary.id.ilike(term),
            Beneficiary.name.ilike(term),
            Beneficiary.village.ilike(term)
        ))

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{beneficiary_id}", response_model=BeneficiaryResponse)
async def get_beneficiary(beneficiary_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Beneficiary).where(Beneficiary.id == beneficiary_id.upper())
    result = await db.execute(stmt)
    ben = result.scalars().first()
    if not ben:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    return ben
