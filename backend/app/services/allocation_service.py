from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.entities import Listing, NGO, Allocation, ListingStatus
from app.services.allocation_engine import (
    ListingSnapshot, NGOSnapshot, allocate_single, allocate_batch, ENGINE_VERSION
)
from app.services.explanation_service import generate_allocation_explanation, generate_global_explanation

def _listing_to_snapshot(listing: Listing, minutes_to_expiry: float) -> ListingSnapshot:
    return ListingSnapshot(
        listing_id=listing.id,
        quantity_meals=listing.quantity_meals,
        minutes_to_expiry=minutes_to_expiry,
        latitude=listing.latitude,
        longitude=listing.longitude
    )

def _ngo_to_snapshot(ngo: NGO) -> NGOSnapshot:
    return NGOSnapshot(
        ngo_id=ngo.id,
        total_capacity_meals=ngo.total_capacity_meals,
        current_capacity_meals=ngo.current_capacity_meals,
        latitude=ngo.latitude,
        longitude=ngo.longitude,
        verified=ngo.verified
    )

async def execute_allocation(db: AsyncSession, listing_id: str, minutes_to_expiry: float) -> Optional[Allocation]:
    # 1. Lock the listing
    stmt = select(Listing).with_for_update().filter(
        Listing.id == listing_id, Listing.status == ListingStatus.OPEN
    )
    result = await db.execute(stmt)
    listing = result.scalar_one_or_none()
    
    if not listing:
        return None
        
    # 2. Get verified NGOs
    stmt_ngo = select(NGO)
    result_ngo = await db.execute(stmt_ngo)
    ngos = result_ngo.scalars().all()
    
    listing_snap = _listing_to_snapshot(listing, minutes_to_expiry)
    ngo_snaps = [_ngo_to_snapshot(n) for n in ngos]
    
    # 3. Run engine
    decision = allocate_single(listing_snap, ngo_snaps)
    
    if not decision.winner_ngo_id:
        return None
        
    # 5. Persist allocation
    explanation = generate_global_explanation(decision.evidence)
    
    allocation = Allocation(
        listing_id=listing.id,
        ngo_id=decision.winner_ngo_id,
        evidence_json=decision.evidence,
        explanation_text=explanation,
        model_version=ENGINE_VERSION
    )
    db.add(allocation)
    
    # 6. Update listing status
    listing.status = ListingStatus.ALLOCATED
    
    # 7. Decrement NGO capacity
    winner_ngo = next(n for n in ngos if n.id == decision.winner_ngo_id)
    winner_ngo.current_capacity_meals -= listing.quantity_meals
    
    await db.commit()
    await db.refresh(allocation)
    return allocation

async def execute_batch_allocation(db: AsyncSession, listings_with_expiry: List[Tuple[Listing, float]]) -> List[Allocation]:
    listing_ids = [l.id for l, _ in listings_with_expiry]
    if not listing_ids:
        return []
        
    stmt_listing = select(Listing).with_for_update().filter(
        Listing.id.in_(listing_ids), Listing.status == ListingStatus.OPEN
    ).order_by(Listing.id)
    result_listing = await db.execute(stmt_listing)
    locked_listings = result_listing.scalars().all()
    
    if not locked_listings:
        return []
        
    stmt_ngo = select(NGO).with_for_update().order_by(NGO.id)
    result_ngo = await db.execute(stmt_ngo)
    locked_ngos = result_ngo.scalars().all()
    
    expiry_map = {l.id: mins for l, mins in listings_with_expiry}
    
    listing_snaps = [_listing_to_snapshot(l, expiry_map[l.id]) for l in locked_listings]
    ngo_snaps = [_ngo_to_snapshot(n) for n in locked_ngos]
    
    decisions = allocate_batch(listing_snaps, ngo_snaps)
    
    new_allocations = []
    
    for decision in decisions:
        if decision.winner_ngo_id:
            db_listing = next(l for l in locked_listings if l.id == decision.listing_id)
            db_ngo = next(n for n in locked_ngos if n.id == decision.winner_ngo_id)
            
            explanation = generate_global_explanation(decision.evidence)
            
            alloc = Allocation(
                listing_id=db_listing.id,
                ngo_id=db_ngo.id,
                evidence_json=decision.evidence,
                explanation_text=explanation,
                model_version=ENGINE_VERSION
            )
            db.add(alloc)
            db_listing.status = ListingStatus.ALLOCATED
            db_ngo.current_capacity_meals -= db_listing.quantity_meals
            new_allocations.append(alloc)
            
    await db.commit()
    for alloc in new_allocations:
        await db.refresh(alloc)
        
    return new_allocations

