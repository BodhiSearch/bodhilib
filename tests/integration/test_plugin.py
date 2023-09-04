import pytest
from bodhilib.plugin import PluginManager


@pytest.mark.live
def test_list_llm_models():
    manager = PluginManager.instance()
    llm_models = manager.list_llm_models()
    assert len(llm_models) > 0
    service_names = {model.service_name for model in llm_models}
    assert len(service_names) == 2
    assert service_names == {"openai", "cohere"}
