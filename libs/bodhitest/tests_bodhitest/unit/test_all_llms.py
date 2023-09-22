import pytest
from bodhilib import Service, get_llm, list_llms

from tests_bodhitest.llm_data import bodhiext_llms, explode


@pytest.fixture
def llm_params(request):
    return bodhiext_llms[request.param]


@pytest.mark.parametrize("llm_params", bodhiext_llms.keys(), indirect=True)
def test_all_llms_service_builder_builds_llm_service(llm_params):
    service_name, llm_service_builder, model_name, llm_class, _ = explode(llm_params)
    service = llm_service_builder(service_name=service_name, service_type="llm", model=model_name)
    assert isinstance(service, llm_class)
    assert service.kwargs["model"] == model_name


@pytest.mark.parametrize("llm_params", bodhiext_llms.keys(), indirect=True)
def test_all_llms_service_builder_raises_exception_on_incorrect_service_name(llm_params):
    llm_service_builder = llm_params["llm_service_builder"]
    with pytest.raises(ValueError):
        _ = llm_service_builder(service_name="incorrect", service_type="llm", model="any_model")


@pytest.mark.parametrize("llm_params", bodhiext_llms.keys(), indirect=True)
def test_all_llms_get_llm(llm_params):
    service_name, _, model_name, llm_class, _ = explode(llm_params)
    service = get_llm(service_name, model_name)
    assert isinstance(service, llm_class)
    assert service.kwargs["model"] == model_name


@pytest.mark.parametrize("llm_params", bodhiext_llms.keys(), indirect=True)
def test_all_llms_list_llms(llm_params):
    service_name, service_builder, _, _, version = explode(llm_params)
    services = list_llms()
    assert (
        Service(
            service_name=service_name,
            service_type="llm",
            publisher="bodhiext",
            service_builder=service_builder,
            version=version,
        )
        in services
    )
