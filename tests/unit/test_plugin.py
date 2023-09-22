import pytest
from bodhiext.openai import OpenAIChat
from bodhilib import PluginManager, get_llm

from tests.prompt_utils import gpt35turbo


def test_openai_service_builder():
    openai = get_llm("openai_chat", gpt35turbo)
    assert type(openai) is OpenAIChat


class _TestLLM:
    ...


def test_get_llm_raises_type_error_if_oftype_mismatch():
    with pytest.raises(TypeError) as e:
        _ = get_llm("openai_chat", gpt35turbo, oftype=_TestLLM)
    expected = (
        "Expecting llm of type \"<class 'tests.unit.test_plugin._TestLLM'>\", "
        "but got \"<class 'bodhiext.openai._openai_llm.OpenAIChat'>\""
    )
    assert str(e.value) == expected


def test_list_services():
    manager = PluginManager.instance()
    services = manager.list_services("llm")
    assert len(services) == 3
    assert services[0].service_name == "openai_chat"
    assert services[1].service_name == "openai_text"
    assert services[2].service_name == "cohere"
    assert all([service.service_type == "llm" for service in services])
    assert all([service.publisher == "bodhiext" for service in services])
