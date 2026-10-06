from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.core.database import get_db
from app.models.entities import Listing, ListingStatus

router = APIRouter()

@router.get("/stats")
async def get_admin_stats(db: AsyncSession = Depends(get_db)):
    # Total food rescued (picked_up)
    rescued_query = select(func.sum(Listing.quantity_meals)).where(Listing.status == ListingStatus.PICKED_UP)
    rescued_result = await db.execute(rescued_query)
    total_food_rescued = rescued_result.scalar() or 0

    # Active listings (open)
    active_query = select(func.count(Listing.id)).where(Listing.status == ListingStatus.OPEN)
    active_result = await db.execute(active_query)
    active_listings = active_result.scalar() or 0

    return {
        "total_food_rescued": total_food_rescued,
        "active_listings": active_listings,
        "system_health": "ok"
    }
