import pytest
from bodhilib import PluginManager

from tests_bodhitest.all_data import all_plugins


class _TestComponent:
    ...


@pytest.fixture
def plugin_params(request):
    return all_plugins[request.param]


@pytest.mark.parametrize("plugin_params", all_plugins.keys(), indirect=True)
def test_all_plugins_service_builder_builds_service(plugin_params):
    service_name = plugin_params["service_name"]
    service_type = plugin_params["service_type"]
    service_class = plugin_params["service_class"]
    publisher = plugin_params["publisher"]
    version = plugin_params["version"]
    service_args = plugin_params["service_args"]

    service = PluginManager.instance().get(
        service_name, service_type, oftype=service_class, publisher=publisher, version=version, **service_args
    )
    assert isinstance(service, service_class)


type_error_msg = (
    "Expecting {service_type} of type \"<class 'tests_bodhitest.unit.test_all_plugins._TestComponent'>\","
    ' but got "{actual_class}"'
)
invalid_args = [
    {"service_class": _TestComponent, "error_message": type_error_msg, "error_class": TypeError},
    {
        "service_name": "invalid",
        "error_message": (
            "Service service_name='{service_name}' of type service_type='{service_type}' not found in registered"
            " services"
        ),
        "error_class": ValueError,
    },
    {
        "service_type": "invalid",
        "error_message": (
            "Service service_name='{service_name}' of type service_type='{service_type}' not found in registered"
            " services"
        ),
        "error_class": ValueError,
    },
]


@pytest.mark.parametrize("plugin_params", all_plugins.keys(), indirect=True)
@pytest.mark.parametrize("invalid_args", invalid_args)
def test_all_plugins_service_builder_raises_error_on_invalid_args(invalid_args, plugin_params):
    error_message = invalid_args["error_message"]
    error_class = invalid_args["error_class"]
    override_args = {**plugin_params, **invalid_args}
    service_name = override_args["service_name"]
    service_type = override_args["service_type"]
    service_class = override_args["service_class"]
    actual_class = plugin_params["service_class"]
    publisher = override_args["publisher"]
    version = override_args["version"]
    service_args = override_args["service_args"]
    with pytest.raises(error_class) as e:
        _ = PluginManager.instance().get(
            service_name, service_type, oftype=service_class, publisher=publisher, version=version, **service_args
        )
    print(f"{locals()=}")
    assert str(e.value) == error_message.format(**locals())
