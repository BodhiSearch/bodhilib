from bodhisearch.llm import get_llm
from bodhisearch.openai import OpenAIChat


def test_openai_provider():
    openai = get_llm("openai", "gpt-3.5-turbo")
    assert type(openai) is OpenAIChat
