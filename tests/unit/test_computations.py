import math

import polars as pl

from aquarium_adventures.computations import HPCComputations, pairwise_stress_function


def test_pairwise_stress_small():
    # Let's do 2 readings: (pH=7.0, temp=25, cap=500), (pH=7.2, temp=26, cap=500)
    # n=2
    # We'll compute the sum manually:

    # i=0, j=0 => dev pH=0, dev temp=0 => factor= (500/500 + 500/500)=2 => partial=0
    # i=0, j=1 => dev pH=|7.0-7.2|=0.2, dev temp=|25-26|=1 => times 2 =>2.0
    #   factor=2( 500/500 + 500/500 )=2*(1+1)=4 => partial=2.0*4=8.0
    # i=1, j=0 => dev pH=0.2, dev temp=1 => times 2 =>2.0 => factor=4 => partial=8.0
    # i=1, j=1 => dev pH=0, dev temp=0 => partial=0

    # sum=8+8=16 => stress=16/(2*2)=16/4=4.0

    pH = [7.0, 7.2]
    temp = [25.0, 26.0]
    cap = [500.0, 500.0]

    val = pairwise_stress_function(pl.Series(pH).to_numpy(), pl.Series(temp).to_numpy(), pl.Series(cap).to_numpy())
    assert math.isclose(val, 4.0, abs_tol=1e-7), f"Expected 4.0, got {val}"


def test_hpc_computations_class():
    df_input = pl.DataFrame({"tank_id": [1, 1], "pH": [7.0, 7.2], "temp": [25, 26], "capacity_liters": [500, 500]})
    hpc = HPCComputations()
    df_out = hpc.analyze_data(df_input)
    assert "stress_score" in df_out.columns
    # For the data above, we expect stress_score=4.0 for each row
    assert df_out["stress_score"][0] == 4.0
    assert df_out["stress_score"][1] == 4.0
