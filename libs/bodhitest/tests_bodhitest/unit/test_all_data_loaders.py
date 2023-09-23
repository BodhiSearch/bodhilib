import pytest
from bodhilib import get_data_loader

from tests_bodhitest.components import bodhiext_data_loaders, unwrap_data_loader


class _TestLoader:
    ...


@pytest.fixture
def data_loader_params(request):
    return bodhiext_data_loaders[request.param]


@pytest.mark.parametrize("data_loader_params", bodhiext_data_loaders.keys(), indirect=True)
def test_all_data_loaders_get_data_loader(data_loader_params):
    service_name, _, data_loader_class, _, _ = unwrap_data_loader(data_loader_params)
    service = get_data_loader(service_name)
    assert isinstance(service, data_loader_class)


@pytest.mark.parametrize("data_loader_params", bodhiext_data_loaders.keys(), indirect=True)
def test_all_data_loaders_raise_error_on_mismatch_oftype(data_loader_params):
    service_name = data_loader_params["service_name"]
    data_loader_class = data_loader_params["data_loader_class"]
    with pytest.raises(TypeError) as e:
        _ = get_data_loader(service_name, oftype=_TestLoader)
    assert (
        str(e.value)
        == "Expecting data_loader of type \"<class 'tests_bodhitest.unit.test_all_data_loaders._TestLoader'>\", but"
        f' got "{data_loader_class}"'
    )
