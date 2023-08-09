from bodhisearch.plugin import PluginManager


class LLM:
    pass


def get_llm(provider: str, model: str, api_key: str = None) -> LLM:
    return PluginManager().get("llm", provider, model=model, api_key=api_key)
