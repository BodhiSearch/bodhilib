from typing import Optional, cast
from bodhisearch.plugin import PluginManager


class LLM:
    pass


def get_llm(provider: str, model: str, api_key: Optional[str] = None) -> LLM:
    return cast(LLM, PluginManager().get("llm", provider, model=model, api_key=api_key))
