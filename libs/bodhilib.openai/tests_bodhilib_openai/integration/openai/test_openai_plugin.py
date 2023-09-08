import pytest
from bodhilib.llm import get_llm
from bodhilib.openai import (
    OpenAIChat,
    OpenAIText,
    bodhilib_list_llm_models,
)

from tests_bodhilib_openai.utils import chat_model, text_model


def test_openai_service_builder_for_chat():
    openai = get_llm("openai", chat_model)
    assert type(openai) is OpenAIChat


def test_openai_service_builder_for_text():
    openai = get_llm("openai", text_model)
    assert type(openai) is OpenAIText


@pytest.mark.live
def test_list_llm_models():
    llm_models = bodhilib_list_llm_models()
    assert len(llm_models) > 0
    model_names = [model.model_name for model in llm_models]
    assert "gpt-3.5-turbo" in model_names
