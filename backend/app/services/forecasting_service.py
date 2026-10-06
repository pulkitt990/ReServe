import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_squared_error, r2_score
from app.services.synthetic_data import generate_synthetic_history
from app.models.entities import Forecast
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

# Global dictionary to store models in-memory for this milestone
global_models = {}

class ForecastingService:
    def __init__(self, db: AsyncSession = None):
        self.db = db

    def train_model(self, donor_id: str, days: int = 90):
        # 1. Generate synthetic data
        df = generate_synthetic_history(donor_id, days)
        
        # 2. Feature engineering
        df = df.sort_values('date')
        df['rolling_7d_mean'] = df['quantity_meals'].rolling(window=7, min_periods=1).mean()
        df['lag_1d'] = df['quantity_meals'].shift(1).fillna(df['quantity_meals'].mean())
        
        # Features
        features = ['day_of_week', 'is_weekend', 'has_event', 'rolling_7d_mean', 'lag_1d']
        X = df[features]
        y = df['quantity_meals']
        
        # Split (last 14 days for test to get metrics)
        train_size = len(df) - 14
        X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
        y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]
        
        model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        rmse = mean_squared_error(y_test, y_pred, squared=False)
        r2 = r2_score(y_test, y_pred)
        
        # Save model state
        global_models[donor_id] = {
            'model': model,
            'last_rolling_mean': float(df['rolling_7d_mean'].iloc[-1]),
            'last_quantity': float(df['quantity_meals'].iloc[-1])
        }
        
        return {
            "donor_id": donor_id,
            "rmse": float(rmse),
            "r2": float(r2),
            "model_version": "xgboost_v1",
            "rows_generated": len(df)
        }

    async def predict_next_days(self, donor_id: str, days: int = 7):
        if donor_id not in global_models:
            self.train_model(donor_id)
            
        model_data = global_models[donor_id]
        model = model_data['model']
        
        predictions = []
        current_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        last_qty = model_data['last_quantity']
        rolling = model_data['last_rolling_mean']
        
        forecasts = []
        
        for i in range(1, days + 1):
            pred_date = current_date + timedelta(days=i)
            day_of_week = pred_date.weekday()
            is_weekend = 1 if day_of_week >= 5 else 0
            has_event = 0 # default to no event
            
            # Feature array order matches training
            X_pred = pd.DataFrame([{
                'day_of_week': day_of_week,
                'is_weekend': is_weekend,
                'has_event': has_event,
                'rolling_7d_mean': rolling,
                'lag_1d': last_qty
            }])
            
            pred = float(model.predict(X_pred)[0])
            pred = max(0.0, pred)
            
            # Update for next iteration
            last_qty = pred
            rolling = (rolling * 6 + pred) / 7
            
            lower = max(0.0, pred - 15) # simple confidence bound
            upper = pred + 15
            
            forecast = Forecast(
                donor_id=donor_id,
                forecast_for_date=pred_date,
                predicted_quantity_meals=pred,
                confidence_lower=lower,
                confidence_upper=upper,
                features_used={"day_of_week": day_of_week, "is_weekend": is_weekend},
                model_version="xgboost_v1"
            )
            if self.db:
                self.db.add(forecast)
            forecasts.append(forecast)
            
        if self.db:
            await self.db.commit()
            
        return forecasts
