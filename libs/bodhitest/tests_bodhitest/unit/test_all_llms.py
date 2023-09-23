import pytest
from bodhilib import Service, list_llms

from tests_bodhitest.all_data import bodhiext_llms


@pytest.fixture
def llm_params(request):
    return bodhiext_llms[request.param]


@pytest.mark.parametrize("llm_params", bodhiext_llms.keys(), indirect=True)
def test_all_llms_list_llms(llm_params):
    service_name, service_builder, publisher, version = (
        llm_params["service_name"],
        llm_params["service_builder"],
        llm_params["publisher"],
        llm_params["version"],
    )
    services = list_llms()
    assert (
        Service(
            service_name=service_name,
            service_type="llm",
            publisher=publisher,
            service_builder=service_builder,
            version=version,
        )
        in services
    )
