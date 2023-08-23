import pytest
from bodhisearch_cohere.llm import get_llm


@pytest.mark.live
def test_cohere_generate():
    cohere = get_llm("cohere", "command")
    result = cohere.generate("What day comes after Monday?")
    assert result.role == "ai"
    assert "tuesday" in result.text.strip().lower()
