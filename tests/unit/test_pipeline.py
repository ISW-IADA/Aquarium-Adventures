import polars as pl

import wandb
from aquarium_adventures.computations import AquariumHPCComputations
from aquarium_adventures.pipeline import AquariumPipeline
from aquarium_adventures.transformations import AquariumTransformer


def test_pipeline_chain(monkey_wandb_run, sensors_df):
    pipeline = AquariumPipeline([AquariumTransformer(), AquariumHPCComputations()], project_name="TestProj")
    df_out = pipeline.run(sensors_df, log_to_wandb=True)

    assert "avg_pH_per_tank" in df_out.columns, "Missing transformation column"
    assert "stress_score" in df_out.columns, "Missing HPC column"

    assert wandb.run == monkey_wandb_run, "wandb.init() should be called"
    assert any("stress_score" in d for d in monkey_wandb_run.logs), "No 'stress_score' logs found"


def test_analyzers_run(sensors_df):
    pipeline = AquariumPipeline([AquariumTransformer(), AquariumHPCComputations()], project_name="TestProj")
    df_out = pipeline.run(sensors_df, log_to_wandb=False)

    assert "avg_pH_per_tank" in df_out.columns, "Missing transformation column"
    assert "stress_score" in df_out.columns, "Missing HPC column"


def test_null_analyzers_run(sensors_df):
    class MockAnalyzer:
        def analyze_data(self, df):
            return df

    pipeline = AquariumPipeline([MockAnalyzer(), MockAnalyzer()])
    df_out = pipeline.run(sensors_df)

    assert df_out is sensors_df, "Pipeline should return the input DataFrame"


def test_log_wandb(monkey_wandb_run):
    pipeline = AquariumPipeline([AquariumTransformer(), AquariumHPCComputations()], project_name="TestProj")
    pipeline.log_to_wandb(pl.DataFrame({"tank_id": [1, 2], "stress_score": [0.5, 0.6]}))

    assert wandb.run == monkey_wandb_run, "wandb.init() should be called"
    assert any("stress_score" in d for d in monkey_wandb_run.logs), "No 'stress_score' logs found"
