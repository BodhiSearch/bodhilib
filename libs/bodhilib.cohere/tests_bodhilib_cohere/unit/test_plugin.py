from bodhilib.cohere.llm import Cohere
from bodhilib.llm import get_llm


def test_cohere_provider():
    cohere = get_llm("cohere", "command")
    assert type(cohere) is Cohere
