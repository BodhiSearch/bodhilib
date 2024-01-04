from collections import Counter

import pytest
from bodhilib import Distance, Role, Source

from tests_bodhilib.utils import all_enum_str, distances_str, roles_str, sources_str


@pytest.mark.parametrize(
  ["enum_obj", "expected_str"],
  all_enum_str,
)
def test_enum_serialization(enum_obj, expected_str):
  assert str(enum_obj) == expected_str


@pytest.mark.parametrize(["enum", "expected"], [(Role, roles_str), (Source, sources_str), (Distance, distances_str)])
def test_membersstr(enum, expected):
  assert Counter(enum.membersstr()) == Counter(expected)
