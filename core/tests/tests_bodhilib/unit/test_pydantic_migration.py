import itertools

import pytest
from bodhilib import Distance, Role, Source

roles = [Role.USER, Role.AI, Role.SYSTEM]
roles_str = ["user", "ai", "system"]
sources = [Source.INPUT, Source.OUTPUT]
sources_str = ["input", "output"]
distances = [Distance.COSINE, Distance.EUCLIDEAN, Distance.DOT_PRODUCT]
distances_str = ["cosine", "euclidean", "dot_product"]

all_enum_str = list(itertools.chain(*map(zip, [roles, sources, distances], [roles_str, sources_str, distances_str])))


@pytest.mark.parametrize(
    ["enum_obj", "expected_str"],
    all_enum_str,
)
def test_enum_serialization(enum_obj, expected_str):
    assert str(enum_obj) == expected_str


@pytest.mark.parametrize(
    ["enum_obj", "str_val"],
    all_enum_str,
)
def test_enum_eq_str_value(enum_obj, str_val):
    assert enum_obj == str_val
    assert str_val == enum_obj
