import pytest
from aquarium_adventures.base import BaseAquariumAnalyzer

def test_base_class_is_abstract():
    with pytest.raises(TypeError):
        BaseAquariumAnalyzer()
