from bodhilib.llm import get_llm
from bodhilib.openai import OpenAIChat

from tests.prompt_utils import gpt35turbo


def test_openai_service_builder():
    openai = get_llm("openai", gpt35turbo)
    assert type(openai) is OpenAIChat
