from bodhilib.llm import get_llm
from bodhilib.openai import OpenAIChat


def test_openai_service_builder():
    openai = get_llm("openai", "gpt-3.5-turbo")
    assert type(openai) is OpenAIChat