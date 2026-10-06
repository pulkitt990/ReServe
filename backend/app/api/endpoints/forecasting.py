from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.services.forecasting_service import ForecastingService
from app.models.entities import Forecast

router = APIRouter()

@router.post("/train/{donor_id}")
async def train_model(donor_id: str, db: AsyncSession = Depends(get_db)):
    service = ForecastingService(db)
    result = service.train_model(donor_id)
    return result

@router.post("/predict/{donor_id}")
async def predict_next_days(donor_id: str, days: int = 7, db: AsyncSession = Depends(get_db)):
    service = ForecastingService(db)
    forecasts = await service.predict_next_days(donor_id, days)
    return [
        {
            "id": f.id,
            "donor_id": f.donor_id,
            "forecast_for_date": f.forecast_for_date,
            "predicted_quantity_meals": f.predicted_quantity_meals,
            "confidence_lower": f.confidence_lower,
            "confidence_upper": f.confidence_upper,
            "features_used": f.features_used,
            "model_version": f.model_version,
            "generated_at": f.generated_at
        }
        for f in forecasts
    ]

@router.get("/donor/{donor_id}")
async def get_donor_forecast(donor_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Forecast).where(Forecast.donor_id == donor_id).order_by(Forecast.forecast_for_date))
    forecasts = result.scalars().all()
    return [
        {
            "id": f.id,
            "donor_id": f.donor_id,
            "forecast_for_date": f.forecast_for_date,
            "predicted_quantity_meals": f.predicted_quantity_meals,
            "confidence_lower": f.confidence_lower,
            "confidence_upper": f.confidence_upper,
            "features_used": f.features_used,
            "model_version": f.model_version,
            "generated_at": f.generated_at
        }
        for f in forecasts
    ]
