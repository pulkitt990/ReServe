from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, Any, Dict
from app.core.database import get_db
from app.models.entities import User, Allocation
from app.services.explanation_service import generate_allocation_explanation
from app.services.allocation_engine import reproduce_from_evidence

router = APIRouter()

@router.get("/allocation/{allocation_id}")
async def get_explanation(
    allocation_id: str,
    ngo_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Allocation).filter(Allocation.id == allocation_id)
    result = await db.execute(stmt)
    allocation = result.scalar_one_or_none()
    
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
        
    explanation = generate_allocation_explanation(allocation.evidence_json, ngo_id)
    
    per_candidate_texts = {}
    for c in allocation.evidence_json.get("candidates", []):
        cid = c["ngo_id"]
        per_candidate_texts[cid] = generate_allocation_explanation(allocation.evidence_json, cid)
        
    return {
        "evidence": allocation.evidence_json,
        "explanation": explanation,
        "per_candidate_texts": per_candidate_texts
    }

@router.get("/allocation/{allocation_id}/verify")
async def verify_allocation(
    allocation_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Allocation).filter(Allocation.id == allocation_id)
    result = await db.execute(stmt)
    allocation = result.scalar_one_or_none()
    
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
        
    is_reproducible = reproduce_from_evidence(allocation.evidence_json)
    
    return {
        "reproducible": is_reproducible,
        "model_version": allocation.model_version
    }

