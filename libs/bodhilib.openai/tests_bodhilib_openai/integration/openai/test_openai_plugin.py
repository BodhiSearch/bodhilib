from bodhilib.llm import get_llm
from bodhilib.openai import OpenAIChat, OpenAIText, bodhilib_list_services

from tests_bodhilib_openai.utils import chat_model, text_model


def test_openai_service_builder_for_chat():
    openai = get_llm("openai", chat_model)
    assert type(openai) is OpenAIChat


def test_openai_service_builder_for_text():
    openai = get_llm("openai", text_model)
    assert type(openai) is OpenAIText


def test_list_services():
    services = bodhilib_list_services()
    assert len(services) == 1
    assert services[0].service_name == "openai"
    assert services[0].service_type == "llm"
    assert services[0].publisher == "bodhilib"
    assert services[0].version == "0.1.0"
    assert services[0].service_builder is not None
