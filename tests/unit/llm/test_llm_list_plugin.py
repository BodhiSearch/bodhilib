from unittest.mock import patch

from bodhilib.llm import list_llms
from bodhilib.plugin import LLMModel, PluginManager, Service


@patch.object(PluginManager, "list_services")
def test_list_services_calls_plugin_manager(mock_list_services):
    mock_list_services.return_value = [Service("test", "llm", "bodhilib-test", lambda: None, "0.1.0")]
    _ = list_llms()
    mock_list_services.assert_called_once_with("llm")


@patch.object(PluginManager, "list_llm_models")
def test_list_llm_models_calls_plugin_manager(list_llm_models):
    list_llm_models.return_value = [LLMModel("openai", "chat-gpt-3.5", "bodhilib")]
    _ = list_llm_models()
    list_llm_models.assert_called_once_with()
