import pytest
from bodhilib import PluginManager, get_llm

from tests_bodhilib.utils import gpt35turbo


class _TestLLM:
    ...


@pytest.mark.skip(reason="TODO: fix this test")
def test_get_llm_raises_type_error_if_oftype_mismatch():
    with pytest.raises(TypeError) as e:
        _ = get_llm("openai_chat", gpt35turbo, oftype=_TestLLM)
    expected = (
        "Expecting llm of type \"<class 'tests_bodhilib.unit.test_plugin._TestLLM'>\", "
        "but got \"<class 'bodhiext.openai._openai_llm.OpenAIChat'>\""
    )
    assert str(e.value) == expected


@pytest.mark.skip(reason="TODO: fix this test")
def test_list_services():
    manager = PluginManager.instance()
    services = manager.list_services("llm")
    assert len(services) == 3
    service_names = [service.service_name for service in services]
    assert "openai_chat" in service_names
    assert "openai_text" in service_names
    assert "cohere" in service_names
    assert all([service.service_type == "llm" for service in services])
    assert all([service.publisher == "bodhiext" for service in services])
