from typing import NamedTuple


class LLM:
    pass


class OpenAIChat(NamedTuple):
    provider: str
    model: str


class OpenAIClassic(NamedTuple):
    provider: str
    model: str


def get_llm(provider: str, model: str) -> LLM:
    if provider == "openai":
        if model.startswith("gpt"):
            return OpenAIChat(provider, model)
        else:
            return OpenAIClassic(provider, model)
    raise ValueError(f"Unknown provider: {provider}")
