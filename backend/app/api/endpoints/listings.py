from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.entities import ListingStatus, Donor
from app.schemas.domain import (
    ListingCreate,
    ListingUpdate,
    ListingStatusUpdate,
    ListingOut,
)
from app.services.listing_service import ListingService, listing_to_out

router = APIRouter()


@router.get("/", response_model=List[ListingOut])
async def list_listings(
    status: Optional[ListingStatus] = Query(None, description="Filter by status (open, allocated, picked_up, expired)"),
    donor_id: Optional[str] = Query(None, description="Filter by specific donor ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List food listings with live perishability countdown and donor metadata."""
    return await ListingService.get_listings(
        db=db,
        status_filter=status,
        donor_id=donor_id,
        limit=limit,
        offset=offset
    )


@router.get("/{listing_id}", response_model=ListingOut)
async def get_listing(
    listing_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a single listing by ID with remaining shelf life and donor details."""
    listing = await ListingService.get_listing_by_id(db, listing_id)
    return listing_to_out(listing)


@router.post("/", response_model=ListingOut, status_code=status.HTTP_201_CREATED)
async def create_listing(
    listing_in: ListingCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new food listing.
    
    If donor_id is not explicitly provided in payload, automatically binds to first existing donor
    (convenient for prototype and demo flows before strict token authentication).
    """
    donor_id = listing_in.donor_id
    if not donor_id:
        # Find first donor or create default demo donor
        donor_res = await db.execute(select(Donor).limit(1))
        donor = donor_res.scalar_one_or_none()
        if not donor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No donor profile registered yet. Please seed or register a donor first."
            )
        donor_id = donor.id

    return await ListingService.create_listing(db=db, listing_in=listing_in, donor_id=donor_id)


@router.patch("/{listing_id}/status", response_model=ListingOut)
async def update_listing_status(
    listing_id: str,
    status_update: ListingStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Transition listing through its lifecycle:
    
    Open -> Allocated -> Picked Up -> Expired
    """
    return await ListingService.update_status(
        db=db,
        listing_id=listing_id,
        new_status=status_update.status
    )
