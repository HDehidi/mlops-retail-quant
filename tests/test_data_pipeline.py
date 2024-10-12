import pytest
import pandas as pd
from src.data_pipeline import clean_data

def test_clean_data():
    raw_data = {
        'Quantity': [5, -1, 10, 0],
        'UnitPrice': [3.0, 2.5, -5.0, 10.0]
    }
    df = pd.DataFrame(raw_data)
    cleaned_df = clean_data(df)
    assert (cleaned_df['Quantity'] >= 0).all()
    assert (cleaned_df['UnitPrice'] >= 0).all()
    assert len(cleaned_df) == 2