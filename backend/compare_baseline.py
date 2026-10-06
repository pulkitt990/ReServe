import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score
from app.services.synthetic_data import generate_synthetic_history
from app.services.forecasting_service import ForecastingService

donor_id = "b07a23a4-df44-46d0-90ab-ea4e7099b576"

# Run the ForecastingService training which returns the XGBoost metrics
service = ForecastingService(None)
result = service.train_model(donor_id, days=90)

xgb_rmse = result["rmse"]
xgb_r2 = result["r2"]

# Re-generate the exact same seed data to compute the Naive Baseline
df = generate_synthetic_history(donor_id, 90)
df = df.sort_values('date')

# Naive Baseline: The prediction is just the 7-day moving average
# (This perfectly aligns with the 1-step ahead evaluation the XGBoost model used)
df['naive_prediction'] = df['quantity_meals'].rolling(window=7, min_periods=1).mean()

# Split identically to forecasting_service.py (last 14 days is the test set)
train_size = len(df) - 14
test = df.iloc[train_size:]

y_test = test['quantity_meals']
naive_pred = test['naive_prediction']

naive_rmse = mean_squared_error(y_test, naive_pred, squared=False)
naive_r2 = r2_score(y_test, naive_pred)

print(f"XGBoost Model -> RMSE: {xgb_rmse:.2f} | R2: {xgb_r2:.2f}")
print(f"Naive 7-Day MA -> RMSE: {naive_rmse:.2f} | R2: {naive_r2:.2f}")

if xgb_rmse < naive_rmse:
    print(f"\nResult: XGBoost BEATS the naive baseline by {naive_rmse - xgb_rmse:.2f} RMSE.")
else:
    print(f"\nResult: XGBoost LOSES to the naive baseline by {xgb_rmse - naive_rmse:.2f} RMSE.")
