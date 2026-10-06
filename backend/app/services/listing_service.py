import math
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.entities import (
    Listing,
    ListingStatus,
    Donor,
    NGO,
    Allocation,
)
from app.schemas.domain import ListingCreate, ListingUpdate, ListingOut


def calculate_minutes_to_expiry(expiry_time: datetime) -> float:
    """Calculates minutes remaining until expiry. Can be negative if already expired."""
    now = datetime.utcnow()
    # Normalize naive datetimes
    if expiry_time.tzinfo is not None:
        expiry_naive = expiry_time.astimezone(timezone.utc).replace(tzinfo=None)
    else:
        expiry_naive = expiry_time
    
    delta = (expiry_naive - now).total_seconds() / 60.0
    return round(delta, 1)


def listing_to_out(listing: Listing) -> ListingOut:
    mins = calculate_minutes_to_expiry(listing.expiry_time)
    # Check if status should be expired
    is_expired = mins <= 0
    return ListingOut(
        id=listing.id,
        donor_id=listing.donor_id,
        title=listing.title,
        food_type=listing.food_type,
        quantity_meals=listing.quantity_meals,
        description=listing.description,
        pickup_address=listing.pickup_address,
        latitude=listing.latitude,
        longitude=listing.longitude,
        prep_time=listing.prep_time,
        expiry_time=listing.expiry_time,
        status=listing.status,
        photo_url=listing.photo_url,
        dietary_flags=listing.dietary_flags or [],
        created_at=listing.created_at,
        updated_at=listing.updated_at,
        minutes_to_expiry=mins,
        is_expired=is_expired,
        donor_name=listing.donor.name if listing.donor else None,
    )


class ListingService:
    @staticmethod
    async def get_listings(
        db: AsyncSession,
        status_filter: Optional[ListingStatus] = None,
        donor_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ListingOut]:
        query = select(Listing).options(selectinload(Listing.donor))
        if status_filter:
            query = query.where(Listing.status == status_filter)
        if donor_id:
            query = query.where(Listing.donor_id == donor_id)
        
        query = query.order_by(Listing.expiry_time.asc()).limit(limit).offset(offset)
        result = await db.execute(query)
        listings = result.scalars().all()

        # Check and update expired status on the fly if still OPEN
        updated_outs = []
        for l in listings:
            mins = calculate_minutes_to_expiry(l.expiry_time)
            if mins <= 0 and l.status == ListingStatus.OPEN:
                l.status = ListingStatus.EXPIRED
                await db.commit()
                await db.refresh(l)
            updated_outs.append(listing_to_out(l))

        return updated_outs

    @staticmethod
    async def get_listing_by_id(db: AsyncSession, listing_id: str) -> Listing:
        query = select(Listing).options(selectinload(Listing.donor)).where(Listing.id == listing_id)
        result = await db.execute(query)
        listing = result.scalar_one_or_none()
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Listing with id {listing_id} not found"
            )
        
        # Check automatic expiration
        mins = calculate_minutes_to_expiry(listing.expiry_time)
        if mins <= 0 and listing.status == ListingStatus.OPEN:
            listing.status = ListingStatus.EXPIRED
            await db.commit()
            await db.refresh(listing)

        return listing

    @staticmethod
    async def create_listing(db: AsyncSession, listing_in: ListingCreate, donor_id: str) -> ListingOut:
        # Validate that prep_time is before expiry_time
        if listing_in.prep_time >= listing_in.expiry_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prep time must be earlier than expiry time"
            )
        
        # Verify donor exists
        donor_query = select(Donor).where(Donor.id == donor_id)
        donor_res = await db.execute(donor_query)
        donor = donor_res.scalar_one_or_none()
        if not donor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Donor with id {donor_id} not found"
            )

        listing = Listing(
            donor_id=donor_id,
            title=listing_in.title,
            food_type=listing_in.food_type,
            quantity_meals=listing_in.quantity_meals,
            description=listing_in.description,
            pickup_address=listing_in.pickup_address,
            latitude=listing_in.latitude,
            longitude=listing_in.longitude,
            prep_time=listing_in.prep_time,
            expiry_time=listing_in.expiry_time,
            photo_url=listing_in.photo_url,
            dietary_flags=listing_in.dietary_flags,
            status=ListingStatus.OPEN
        )
        db.add(listing)
        await db.commit()
        await db.refresh(listing)
        
        # Fetch with relationship loaded
        return listing_to_out(await ListingService.get_listing_by_id(db, listing.id))

    @staticmethod
    async def update_status(
        db: AsyncSession,
        listing_id: str,
        new_status: ListingStatus
    ) -> ListingOut:
        listing = await ListingService.get_listing_by_id(db, listing_id)

        # Validate allowed transitions
        # Open -> Allocated or Expired
        # Allocated -> Picked Up or Expired or Open (if cancelled)
        # Picked Up -> Terminal
        # Expired -> Terminal
        current = listing.status
        if current == ListingStatus.PICKED_UP:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Listing has already been picked up. Status cannot be changed."
            )
        if current == ListingStatus.EXPIRED and new_status != ListingStatus.EXPIRED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Listing has expired and cannot be reactivated."
            )

        listing.status = new_status
        if new_status == ListingStatus.PICKED_UP:
            from app.models.entities import Allocation
            from sqlalchemy.future import select
            import datetime
            stmt = select(Allocation).filter(Allocation.listing_id == listing_id)
            res = await db.execute(stmt)
            alloc = res.scalar_one_or_none()
            if alloc:
                alloc.picked_up_at = datetime.datetime.utcnow()
                alloc.status = "completed"
                
        await db.commit()
        await db.refresh(listing)
        return listing_to_out(listing)
