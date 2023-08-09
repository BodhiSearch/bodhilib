class LLM:
    pass


def get_llm(provider: str, model: str, api_key: str = None) -> LLM:
    if provider == "openai":
        from bodhisearch.openai import get_llm as get_openai_llm

        return get_openai_llm(provider, model, api_key)
    raise ValueError(f"Unknown provider: {provider}")
