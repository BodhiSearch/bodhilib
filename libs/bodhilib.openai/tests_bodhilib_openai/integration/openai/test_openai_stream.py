import io

import pytest
from bodhilib.models import Role, Source
from bodhilib.openai import OpenAIChat, OpenAIText

from tests_bodhilib_openai.utils import chat_model, text_model


@pytest.mark.live
@pytest.mark.parametrize(["clz", "model"], [(OpenAIChat, chat_model), (OpenAIText, text_model)])
def test_openai_stream(clz, model):
    llm = clz(model=model)
    stream = llm.generate("generate a 50 words article on geography of India?", stream=True)
    chunks = io.StringIO()
    for chunk in stream:
        chunks.write(chunk.text)
        assert chunk.role == Role.AI
        assert chunk.source == Source.OUTPUT
    article = chunks.getvalue()
    assert article != ""
