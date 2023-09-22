import pytest
from bodhiext.cohere import cohere_llm_service_builder
from bodhilib import Role, Source


@pytest.mark.live
def test_cohere_stream():
    llm = cohere_llm_service_builder(service_name="cohere", service_type="llm", model="command")
    stream = llm.generate("generate a 50 words article on geography of India?", stream=True)
    for chunk in stream:
        assert chunk.role == Role.AI
        assert chunk.source == Source.OUTPUT
    assert stream.text != ""
