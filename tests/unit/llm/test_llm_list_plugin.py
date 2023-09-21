from unittest.mock import patch

from bodhilib import list_llms
from bodhilib.plugin import PluginManager, Service


@patch.object(PluginManager, "list_services")
def test_list_services_calls_plugin_manager(mock_list_services):
    mock_list_services.return_value = [Service("test", "llm", "bodhilib-test", lambda: None, "0.1.0")]
    _ = list_llms()
    mock_list_services.assert_called_once_with("llm")
