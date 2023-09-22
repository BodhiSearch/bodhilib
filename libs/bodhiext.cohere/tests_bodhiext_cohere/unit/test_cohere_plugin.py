import pytest
from bodhiext.cohere import Cohere, __version__, bodhilib_list_services, cohere_llm_service_builder
from bodhilib import Service, get_llm


def test_cohere_service_builder():
    cohere = get_llm("cohere", "command")
    assert type(cohere) is Cohere


def test_cohere_bodhilib_list_services():
    services = bodhilib_list_services()
    assert len(services) == 1
    service = services[0]
    assert service == Service("cohere", "llm", "bodhiext", cohere_llm_service_builder, __version__)


@pytest.mark.parametrize(
    ["kwargs", "error_msg"],
    [
        (
            {},
            (
                "Unknown params: service_name=None, service_type='llm', supported params: service_name='cohere',"
                " service_type='llm'"
            ),
        ),
        (
            {"service_name": "cohere", "service_type": "vector_db"},
            (
                "Unknown params: service_name='cohere', service_type='vector_db', supported params:"
                " service_name='cohere', service_type='llm'"
            ),
        ),
    ],
)
def test_cohere_llm_service_builder_validations(kwargs, error_msg):
    with pytest.raises(ValueError) as e:
        _ = cohere_llm_service_builder(**kwargs)
    assert str(e.value) == error_msg


def test_cohere_llm_service_builder_api_key_not_set(monkeypatch):
    with monkeypatch.context() as m:
        m.delenv("COHERE_API_KEY", raising=False)
        with pytest.raises(ValueError) as e:
            _ = cohere_llm_service_builder(service_name="cohere", model="command")
    assert str(e.value) == "environment variable COHERE_API_KEY is not set"


def test_cohere_llm_service_builder_happy_path():
    service = cohere_llm_service_builder(service_name="cohere", model="command", api_key="foobar")
    assert type(service) is Cohere


def test_cohere_llm_service_builder_api_key_from_env(monkeypatch):
    with monkeypatch.context() as m:
        m.setenv("COHERE_API_KEY", "foobar")
        service = cohere_llm_service_builder(service_name="cohere", model="command")
    assert type(service) is Cohere
