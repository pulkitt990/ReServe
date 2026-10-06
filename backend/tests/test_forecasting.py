import pytest
from app.services.synthetic_data import generate_synthetic_history
from app.services.forecasting_service import ForecastingService

def test_synthetic_data_generator():
    df = generate_synthetic_history("test_donor_123", days=90)
    assert len(df) == 90
    assert "quantity_meals" in df.columns
    assert "date" in df.columns
    assert "donor_id" in df.columns
    assert df["donor_id"].iloc[0] == "test_donor_123"

def test_training_runs_successfully():
    service = ForecastingService(None)
    result = service.train_model("test_donor_123", days=90)
    assert result["donor_id"] == "test_donor_123"
    assert "rmse" in result
    assert "r2" in result
    assert result["rows_generated"] == 90

@pytest.mark.asyncio
async def test_prediction_outputs_valid_forecasts():
    service = ForecastingService(None)
    # Train first
    service.train_model("test_donor_123")
    
    # Predict
    forecasts = await service.predict_next_days("test_donor_123", days=7)
    assert len(forecasts) == 7
    
    for f in forecasts:
        assert f.donor_id == "test_donor_123"
        assert f.predicted_quantity_meals >= 0
        assert f.confidence_lower <= f.predicted_quantity_meals
        assert f.confidence_upper >= f.predicted_quantity_meals
        assert f.model_version == "xgboost_v1"
        assert f.features_used is not None
