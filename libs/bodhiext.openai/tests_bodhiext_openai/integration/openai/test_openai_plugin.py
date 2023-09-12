import pytest
from bodhiext.openai import bodhilib_list_llm_models


@pytest.mark.live
def test_list_llm_models():
    llm_models = bodhilib_list_llm_models()
    assert len(llm_models) > 0
    model_names = [model.model_name for model in llm_models]
    assert "gpt-3.5-turbo" in model_names
