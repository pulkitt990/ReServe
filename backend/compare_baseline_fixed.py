import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
from app.services.synthetic_data import generate_synthetic_history
import xgboost as xgb

donor_id = "b07a23a4-df44-46d0-90ab-ea4e7099b576"
df = generate_synthetic_history(donor_id, 90)
df = df.sort_values('date')

df['rolling_7d_mean'] = df['quantity_meals'].rolling(window=7, min_periods=1).mean()
df['lag_1d'] = df['quantity_meals'].shift(1).fillna(df['quantity_meals'].mean())

features = ['day_of_week', 'is_weekend', 'has_event', 'rolling_7d_mean', 'lag_1d']
train_size = len(df) - 14

X = df[features]
y = df['quantity_meals']
X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]

model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=50, random_state=42)
model.fit(X_train, y_train)
y_pred_xgb = model.predict(X_test)

naive_pred = X_test['rolling_7d_mean']

xgb_rmse = mean_squared_error(y_test, y_pred_xgb, squared=False)
xgb_r2 = r2_score(y_test, y_pred_xgb)
naive_rmse = mean_squared_error(y_test, naive_pred, squared=False)
naive_r2 = r2_score(y_test, naive_pred)

print(f"XGBoost Model -> RMSE: {xgb_rmse:.2f} | R2: {xgb_r2:.2f}")
print(f"Naive 7-Day MA -> RMSE: {naive_rmse:.2f} | R2: {naive_r2:.2f}")

