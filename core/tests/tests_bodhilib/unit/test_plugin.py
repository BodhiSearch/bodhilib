from typing import List
from unittest.mock import Mock

import pytest
from bodhilib import LLM, LLMApiConfig, LLMConfig, PluginManager, Service, get_llm

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


class PluginManagerStub(PluginManager):
  def __new__(cls) -> "PluginManagerStub":
    return object.__new__(cls)

  def __init__(self) -> "PluginManagerStub":
    self.services = []

  def register(self, service: Service) -> None:
    self.services.append(service)

  def _fetch_services(self) -> List[Service]:
    return self.services


def test_plugin_manager_get_passes_config_to_service_builder():
  mock_service_builder = Mock()
  plugin_manager = PluginManagerStub()
  plugin_manager.register(Service("test", "llm", "test_bodhilib", mock_service_builder, "0.1.0"))
  mock_llm = Mock(spec=LLM)
  mock_service_builder.return_value = mock_llm

  api_config = LLMApiConfig()
  llm_config = LLMConfig()
  plugin_manager.get("test", "llm", oftype=type(mock_llm), api_config=api_config, llm_config=llm_config)

  mock_service_builder.assert_called_once_with(
    **{
      "service_name": "test",
      "service_type": "llm",
      "api_config": api_config,
      "llm_config": llm_config,
    }
  )


def test_plugin_service_eq():
  first = Service("test", "llm", "test_bodhilib", object(), "0.1.0")
  other = Service("test", "llm", "test_bodhilib", object(), "0.1.0", {})
  assert first == other
  assert hash(first) == hash(other)
