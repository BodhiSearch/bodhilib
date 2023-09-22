import pytest
from bodhiext.data_loader import FileLoader
from bodhilib import get_data_loader


class _TestLoader:
    ...


def test_data_loader_raises_type_error_if_not_of_given_type():
    with pytest.raises(TypeError) as e:
        _ = get_data_loader("file", oftype=_TestLoader)
    expected = (
        "Expecting data_loader of type \"<class 'tests.unit.test_loader_plugin._TestLoader'>\", "
        "but got \"<class 'bodhiext.data_loader._file.FileLoader'>\""
    )
    assert str(e.value) == expected


def test_data_loader_package_loaders():
    loader = get_data_loader("file", publisher="bodhiext", oftype=FileLoader)
    assert isinstance(loader, FileLoader)
