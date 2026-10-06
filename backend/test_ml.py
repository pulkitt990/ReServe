import asyncio
from app.core.database import AsyncSessionLocal
from app.models.entities import Donor
from sqlalchemy.future import select
from app.services.forecasting_service import ForecastingService

async def test():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Donor))
        donor = result.scalars().first()
        if not donor:
            print("No donors found!")
            return
        
        print(f"Testing for donor: {donor.id}")
        
        service = ForecastingService(db)
        
        # Test Train
        train_res = service.train_model(donor.id)
        print("\n--- Training Result ---")
        print(f"RMSE: {train_res['rmse']}")
        print(f"R2: {train_res['r2']}")
        
        # Test Predict
        forecasts = await service.predict_next_days(donor.id, days=2)
        print("\n--- Prediction Output ---")
        for f in forecasts:
            print(f"Date: {f.forecast_for_date.date()}, Predicted: {f.predicted_quantity_meals:.2f} meals, Bounds: [{f.confidence_lower:.2f}, {f.confidence_upper:.2f}]")

asyncio.run(test())
