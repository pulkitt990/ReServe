import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_synthetic_history(donor_id: str, days: int = 90) -> pd.DataFrame:
    """
    SYNTHETIC DATA GENERATOR
    Generates realistic historical logs for a given donor.
    Includes day_of_week patterns, weekend spikes, and event flags.
    """
    # Fix random seed for reproducibility in tests
    np.random.seed(hash(donor_id) % (2**32))
    
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days-1)
    
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    df = pd.DataFrame({'date': dates})
    df['date'] = pd.to_datetime(df['date'])
    df['donor_id'] = donor_id
    df['day_of_week'] = df['date'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Base quantity
    df['quantity_meals'] = np.random.normal(50, 10, size=len(df)).clip(min=10)
    
    # Weekend spike
    df.loc[df['is_weekend'] == 1, 'quantity_meals'] += np.random.normal(30, 10, size=len(df[df['is_weekend'] == 1]))
    
    # Random event flags
    df['has_event'] = np.random.binomial(1, 0.1, size=len(df))
    df.loc[df['has_event'] == 1, 'quantity_meals'] += np.random.normal(50, 15, size=len(df[df['has_event'] == 1]))
    
    # Add noise
    df['quantity_meals'] += np.random.normal(0, 5, size=len(df))
    df['quantity_meals'] = df['quantity_meals'].round().clip(lower=0)
    
    return df
