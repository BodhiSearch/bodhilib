from bodhisearch.cohere.llm import Cohere
from bodhisearch.llm import get_llm


def test_cohere_provider():
    cohere = get_llm("cohere", "command")
    assert type(cohere) is Cohere
