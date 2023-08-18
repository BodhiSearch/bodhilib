from bodhisearch_cohere.llm import Cohere

from bodhisearch import get_llm
from bodhisearch.openai import OpenAIChat


def test_openai_provider():
    openai = get_llm("openai", "gpt-3.5-turbo")
    assert type(openai) is OpenAIChat


def test_cohere_provider():
    cohere = get_llm("cohere", "command")
    assert type(cohere) is Cohere
