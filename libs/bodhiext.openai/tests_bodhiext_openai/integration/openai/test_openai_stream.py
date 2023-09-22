import pytest
from bodhiext.openai import OpenAIChat, OpenAIText
from bodhilib import Role, Source

from tests_bodhiext_openai.utils import chat_model, text_model


@pytest.mark.live
@pytest.mark.parametrize(["clz", "model"], [(OpenAIChat, chat_model), (OpenAIText, text_model)])
def test_openai_stream(clz, model):
    llm = clz(model=model)
    stream = llm.generate("generate a 50 words article on geography of India?", stream=True)
    for chunk in stream:
        assert chunk.role == Role.AI
        assert chunk.source == Source.OUTPUT
    assert stream.text != ""
