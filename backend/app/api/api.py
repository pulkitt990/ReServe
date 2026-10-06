from fastapi import APIRouter
from app.api.endpoints import auth, listings, forecasting, allocation, explanation, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(listings.router, prefix="/listings", tags=["Listings"])
api_router.include_router(forecasting.router, prefix="/forecasting", tags=["Forecasting"])
api_router.include_router(allocation.router, prefix="/allocation", tags=["Allocation"])
api_router.include_router(explanation.router, prefix="/explanation", tags=["Explanation"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
