import polars as pl
import pytest

from aquarium_adventures.transformations import AquariumTransformer


def test_transformer_analyze_data(sensors_df, tank_info_df_fish_species_split):
    transformer = AquariumTransformer(tank_info_df_fish_species_split)
    out_df = transformer.analyze_data(sensors_df)

    assert (
        "avg_pH_per_tank" in out_df.columns
        and "tank_num_readings" in out_df.columns
        and "fish_species_num_readings" in out_df.columns
        and "temperature_deviation_scaled" in out_df.columns
    )


def test_add_avg_ph_per_tank(sensors_df):
    transformer = AquariumTransformer(None)
    out_df = transformer.add_avg_ph_per_tank(sensors_df)

    assert out_df["avg_pH_per_tank"][0] == 7.1
    assert out_df["avg_pH_per_tank"][1] == 7.1
    assert out_df["avg_pH_per_tank"][2] == 7.5


def test_add_num_readings_per_tank(sensors_df):
    transformer = AquariumTransformer(None)
    out_df = transformer.add_num_readings_per_tank(sensors_df)

    assert out_df["tank_num_readings"][0] == 2
    assert out_df["tank_num_readings"][1] == 2
    assert out_df["tank_num_readings"][2] == 1


def test_add_num_readings_per_fish_species(sensors_df, tank_info_df_fish_species_split):
    transformer = AquariumTransformer(tank_info_df_fish_species_split)
    out_df = transformer.add_num_readings_per_fish_species(sensors_df)

    assert out_df.filter(pl.col("fish_species") == "VelvetLoach")["fish_species_num_readings"][0] == 3
    assert out_df.filter(pl.col("fish_species") == "VelvetLoach")["tank_id"].unique().len() == 2
    assert out_df.filter(pl.col("fish_species") == "FantasticZebrafish")["fish_species_num_readings"][0] == 1
    assert out_df.filter(pl.col("fish_species") == "FantasticZebrafish")["tank_id"][0] == 2
    assert out_df.filter(pl.col("fish_species") == "FantasticZebrafish")["tank_id"].len() == 1

    transformer = AquariumTransformer(None)
    with pytest.raises(AttributeError):
        transformer.add_num_readings_per_fish_species(sensors_df)


def test_standard_temperature():
    assert AquariumTransformer.STANDARD_TEMPERATURE == 26.0


def test_add_temperature_deviation(sensors_df, sensors_df_without_quantities):
    transformer = AquariumTransformer(None)
    out_df = transformer.add_temperature_deviation(sensors_df)

    assert out_df["temperature_deviation_scaled"][0] == 2.0
    assert out_df["temperature_deviation_scaled"][1] is None
    assert out_df["temperature_deviation_scaled"][2] == 1.5

    out_df = transformer.add_temperature_deviation(sensors_df_without_quantities)
    assert out_df["temperature_deviation"][0] == 1.0
    assert out_df["temperature_deviation"][1] == 0.0
    assert out_df["temperature_deviation"][2] == 1.5
    assert "temperature_deviation_scaled" not in out_df.columns
