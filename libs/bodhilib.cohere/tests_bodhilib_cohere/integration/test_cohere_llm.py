import pytest
from bodhilib.cohere import cohere_llm_service_builder


@pytest.mark.live
def test_cohere_generate():
    cohere = cohere_llm_service_builder(service_name="cohere", model="command")
    result = cohere.generate("What day comes after Monday?")
    assert result.role == "ai"
    assert "tuesday" in result.text.strip().lower()
