import pytest
import polars as pl
import wandb
from pathlib import Path

@pytest.mark.slow
def test_aquarium_pipeline_end_to_end(tmp_path, monkeypatch):
    """
    1) Create a CSV with columns [tank_id, time, pH, temp, capacity_liters].
    2) Create an optional 'tank_info' CSV to test the join. 
    3) Run the full pipeline. 
    4) Check final CSV and wandb logs.
    """
    sensor_csv = tmp_path / "sensors.csv"
    sensor_csv.write_text(
        "tank_id,time,pH,temp,capacity_liters\n"
        "1,2025-01-01 00:00,7.0,25,500\n"
        "1,2025-01-01 01:00,7.2,26,500\n"
        "2,2025-01-01 00:30,7.5,24.5,1000\n"
    )

    # Suppose we have an extra CSV with fish_species, just to demonstrate the join
    info_csv = tmp_path / "tank_info.csv"
    info_csv.write_text(
        "tank_id,fish_species\n"
        "1,guppy\n"
        "2,discus\n"
    )

    output_csv = tmp_path / "results.csv"

    logs = []
    def fake_init(*args, **kwargs):
        return "mock_wandb_run"
    def fake_log(data, step=None):
        logs.append(data)
    def fake_finish():
        pass

    monkeypatch.setattr(wandb, "init", fake_init)
    monkeypatch.setattr(wandb, "log", fake_log)
    monkeypatch.setattr(wandb, "finish", fake_finish)

    from aquarium_adventures.main import run_full_pipeline
    run_full_pipeline(
        input_csv=str(sensor_csv),
        tank_info_csv=str(info_csv),
        output_csv=str(output_csv),
        project_name="AcceptanceTest"
    )

    # 3) Check wandb logs
    assert any("stress_score" in d for d in logs), "No stress_score logged to wandb"

    # 4) Read final CSV
    df_result = pl.read_csv(output_csv)
    # Should have columns from transformations + HPC
    for col in ["avg_pH_per_tank", "stress_score"]:
        assert col in df_result.columns, f"Missing {col} in final output"
    # We won't do an exact numeric check, but you could if you wanted to.
    assert df_result.shape[0] == 3
