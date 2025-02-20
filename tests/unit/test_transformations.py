import pytest
import polars as pl
from aquarium_adventures.transformations import AquariumTransformer

def test_transformer_joins_and_computes():
    df_main = pl.DataFrame({
        "tank_id": [1, 1, 2],
        "time": ["2025-01-01 00:00", "2025-01-01 01:00", "2025-01-01 00:30"],
        "pH": [7.0, 7.2, 7.5],
        "temp": [25.0, 26.0, 24.5]
    })
    df_info = pl.DataFrame({
        "tank_id": [1, 2],
        "capacity_liters": [500, 1000],
        "fish_species": ["guppy", "discus"]
    })
    transformer = AquariumTransformer(df_info)
    out_df = transformer.analyze_data(df_main)

    # Check columns exist
    assert all(col in out_df.columns for col in [
        "avg_pH_per_tank", "num_readings"
    ]), "Missing expected aggregator or window columns"

    # If capacity_liters is present, expect 'temp_dev_scaled'
    assert "temp_dev_scaled" in out_df.columns
    # For tank_id=1, we expect 2 readings
    assert out_df.filter(pl.col("tank_id") == 1)["num_readings"][0] == 2
