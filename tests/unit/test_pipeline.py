import polars as pl
import wandb

from aquarium_adventures.computations import HPCComputations
from aquarium_adventures.pipeline import AquariumPipeline
from aquarium_adventures.transformations import AquariumTransformer


def test_pipeline_chain(monkeypatch):
    # Minimal DataFrame
    df_main = pl.DataFrame({"tank_id": [1, 2], "pH": [7.0, 7.2], "temp": [25.0, 26.0], "capacity_liters": [500, 1000]})

    logs = []

    def fake_init(*args, **kwargs):
        return "mock_run"

    def fake_log(data, step=None):
        logs.append(data)

    def fake_finish():
        pass

    monkeypatch.setattr(wandb, "init", fake_init)
    monkeypatch.setattr(wandb, "log", fake_log)
    monkeypatch.setattr(wandb, "finish", fake_finish)

    # Build a pipeline with 2 analyzers
    pipeline = AquariumPipeline([AquariumTransformer(), HPCComputations()], project_name="TestProj")
    df_out = pipeline.run(df_main, log_to_wandb=True)

    # Check transformations
    assert "avg_pH_per_tank" in df_out.columns, "Missing transformation column"
    assert "stress_score" in df_out.columns, "Missing HPC column"

    # Check wandb logs
    assert any("stress_score" in d for d in logs), "No 'stress_score' logs found"
