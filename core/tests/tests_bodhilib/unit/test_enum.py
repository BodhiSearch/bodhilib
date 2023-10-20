import pytest

from tests_bodhilib.utils import all_enum_str


@pytest.mark.parametrize(
    ["enum_obj", "str_val"],
    all_enum_str,
)
def test_enum_eq_str_value(enum_obj, str_val):
    assert enum_obj == str_val
    assert str_val == enum_obj
