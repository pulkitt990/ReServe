from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional, Any
from app.core.database import get_db
from app.models.entities import User, Allocation, Listing, ListingStatus, NGO
from app.schemas.domain import AllocationOut, ListingOut
from app.services.allocation_service import execute_allocation, execute_batch_allocation
from app.services.listing_service import calculate_minutes_to_expiry
from app.services.allocation_engine import allocate_single
from app.services.allocation_service import _listing_to_snapshot, _ngo_to_snapshot

router = APIRouter()

@router.post("/allocate/{listing_id}", response_model=Any)
async def allocate_listing(
    listing_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Listing).filter(Listing.id == listing_id)
    result = await db.execute(stmt)
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
        
    if listing.status != ListingStatus.OPEN:
        raise HTTPException(status_code=409, detail="Listing is not OPEN")
        
    minutes_to_expiry = calculate_minutes_to_expiry(listing.expiry_time)
    
    allocation = await execute_allocation(db, listing_id, minutes_to_expiry)
    if not allocation:
        return {"status": "no_match", "message": "No eligible NGO found."}
        
    # Manually serialize allocation to dict
    a_dict = {
        "id": allocation.id,
        "listing_id": allocation.listing_id,
        "ngo_id": allocation.ngo_id,
        "allocated_at": allocation.allocated_at,
        "picked_up_at": allocation.picked_up_at,
        "status": allocation.status,
        "evidence_json": allocation.evidence_json,
        "explanation_text": allocation.explanation_text,
        "model_version": allocation.model_version
    }
        
    return {
        "status": "success",
        "allocation": a_dict
    }

@router.post("/allocate-batch", response_model=List[Any])
async def allocate_batch_endpoint(
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Listing).filter(Listing.status == ListingStatus.OPEN)
    result = await db.execute(stmt)
    open_listings = result.scalars().all()
    
    listings_with_expiry = [(l, calculate_minutes_to_expiry(l.expiry_time)) for l in open_listings]
    
    allocations = await execute_batch_allocation(db, listings_with_expiry)
    
    res = []
    for allocation in allocations:
        res.append({
            "id": allocation.id,
            "listing_id": allocation.listing_id,
            "ngo_id": allocation.ngo_id,
            "allocated_at": allocation.allocated_at,
            "status": allocation.status,
            "evidence_json": allocation.evidence_json,
        })
    return res

@router.get("/preview/{listing_id}", response_model=Any)
async def preview_allocation(
    listing_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Listing).filter(Listing.id == listing_id)
    result = await db.execute(stmt)
    listing = result.scalar_one_or_none()
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
        
    minutes_to_expiry = calculate_minutes_to_expiry(listing.expiry_time)
    
    stmt_ngo = select(NGO)
    result_ngo = await db.execute(stmt_ngo)
    ngos = result_ngo.scalars().all()
    
    snap_l = _listing_to_snapshot(listing, minutes_to_expiry)
    snap_n = [_ngo_to_snapshot(n) for n in ngos]
    
    decision = allocate_single(snap_l, snap_n)
    return decision.evidence

@router.get("/", response_model=List[AllocationOut])
async def list_allocations(
    listing_id: Optional[str] = None,
    ngo_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Allocation).options(selectinload(Allocation.ngo))
    if listing_id:
        stmt = stmt.filter(Allocation.listing_id == listing_id)
    if ngo_id:
        stmt = stmt.filter(Allocation.ngo_id == ngo_id)
        
    result = await db.execute(stmt)
    allocs = result.scalars().all()
    
    res = []
    for a in allocs:
        a_dict = {
            "id": a.id,
            "listing_id": a.listing_id,
            "ngo_id": a.ngo_id,
            "allocated_at": a.allocated_at,
            "picked_up_at": a.picked_up_at,
            "status": a.status,
            "evidence_json": a.evidence_json,
            "explanation_text": a.explanation_text,
            "model_version": a.model_version,
            "ngo_name": a.ngo.name if a.ngo else None
        }
        res.append(a_dict)
    return res

