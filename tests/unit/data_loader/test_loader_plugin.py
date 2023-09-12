import pytest
from bodhilib.data_loader import get_data_loader


class _TestLoader:
    ...


def test_loader_raises_type_error_if_not_of_given_type():
    with pytest.raises(TypeError) as e:
        _ = get_data_loader("file", oftype=_TestLoader)
    expected = (
        "Expecting data_loader of type <class 'tests.unit.data_loader.test_loader_plugin._TestLoader'>, but got <class"
        " 'bodhiext.data_loader.file.FileLoader'>"
    )
    assert str(e.value) == expected
