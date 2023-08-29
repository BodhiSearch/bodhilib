import io

import pytest
from bodhilib.cohere import cohere_llm_service_builder
from bodhilib.models import Role, Source


@pytest.mark.live
def test_cohere_stream():
    llm = cohere_llm_service_builder(service_name="cohere", service_type="llm", model="command")
    stream = llm.generate("generate a 50 words article on geography of India?", stream=True)
    chunks = io.StringIO()
    for chunk in stream:
        chunks.write(chunk.text)
        assert chunk.role == Role.AI
        assert chunk.source == Source.OUTPUT
    article = chunks.getvalue()
    assert article != ""
