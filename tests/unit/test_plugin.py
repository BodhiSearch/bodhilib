from bodhilib.llm import get_llm
from bodhilib.openai import OpenAIChat
from bodhilib.plugin import PluginManager

from tests.prompt_utils import gpt35turbo


def test_openai_service_builder():
    openai = get_llm("openai", gpt35turbo)
    assert type(openai) is OpenAIChat


def test_list_services():
    manager = PluginManager.instance()
    services = manager.list_services("llm")
    assert len(services) == 2
    assert services[0].service_name == "openai"
    assert services[0].service_type == "llm"
    assert services[0].publisher == "bodhilib"
    assert services[1].service_name == "cohere"
    assert services[1].service_type == "llm"
    assert services[1].publisher == "bodhilib"
