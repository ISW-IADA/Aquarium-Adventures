import polars as pl
import pytest

from aquarium_adventures.base import BaseAquariumAnalyzer
from aquarium_adventures.computations import AquariumHPCComputations
from aquarium_adventures.transformations import AquariumTransformer


def test_base_class_is_abstract():
    with pytest.raises(TypeError):
        BaseAquariumAnalyzer()


def test_base_class_abstract_method(sensors_df):
    class WrongConcreteAnalyzer(BaseAquariumAnalyzer):
        def another_analyze_data_method(self, df: pl.DataFrame) -> pl.DataFrame:
            return df

    with pytest.raises(TypeError):
        WrongConcreteAnalyzer()

    class CorrectConcreteAnalyzer(BaseAquariumAnalyzer):
        def analyze_data(self, df: pl.DataFrame) -> pl.DataFrame:
            return df

    analyzer = CorrectConcreteAnalyzer()
    assert analyzer.analyze_data(sensors_df) is sensors_df


def test_subclasses():
    assert issubclass(AquariumTransformer, BaseAquariumAnalyzer)
    assert issubclass(AquariumHPCComputations, BaseAquariumAnalyzer)
