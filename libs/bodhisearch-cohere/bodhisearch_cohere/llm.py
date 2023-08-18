import os
from typing import Any, Dict, List, Optional

import cohere

import bodhisearch
from bodhisearch import Provider
from bodhisearch.llm import LLM
from bodhisearch.prompt import Prompt, PromptInput, parse_prompts


@bodhisearch.provider
def bodhisearch_get_providers():
    return [Provider("cohere", "bodhisearch", "llm", get_llm, "0.1.0")]


def get_llm(provider: str, model: str, api_key: Optional[str] = None) -> LLM:
    if provider != "cohere":
        raise ValueError(f"Unknown provider: {provider}")
    if api_key is None:
        if os.environ.get("COHERE_API_KEY") is None:
            raise ValueError("environment variable COHERE_API_KEY is not set")
        else:
            api_key = os.environ["COHERE_API_KEY"]
    return Cohere(model=model, api_key=api_key)


class Cohere(LLM):
    def __init__(self, model, api_key):
        self.model = model
        self.client = cohere.Client(api_key=api_key)
        self.aclient = cohere.AsyncClient(api_key=api_key)

    def generate(self, prompts: PromptInput, **kwargs: Dict[str, Any]) -> Prompt:
        parsed_prompts = parse_prompts(prompts)
        input = self._to_prompt(parsed_prompts)
        # TODO - pass kwargs
        result = self.client.generate(input, model=self.model)
        return Prompt(result.generations[0].text, role="ai", source="output")

    def _to_prompt(self, prompts: List[Prompt]) -> str:
        return "\n".join([p.text for p in prompts])
