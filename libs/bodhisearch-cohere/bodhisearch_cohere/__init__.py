import os
from typing import List

import cohere

import bodhisearch
from bodhisearch.hookspecs import Provider
from bodhisearch.prompt import Prompt, PromptInput, parse_prompts


@bodhisearch.provider
def bodhisearch_get_providers():
    return [Provider("cohere", "bodhisearch", "llm", get_llm, "0.1.0")]


def get_llm(provider: str, model: str, api_key: str = None):
    if provider != "cohere":
        raise ValueError(f"Unknown provider: {provider}")
    if api_key is None:
        if os.environ.get("COHERE_API_KEY") is None:
            raise ValueError("environment variable COHERE_API_KEY is not set")
        else:
            api_key = os.environ["COHERE_API_KEY"]
    return Cohere(model=model, api_key=api_key)


class Cohere:
    def __init__(self, model, api_key):
        self.model = model
        self.client = cohere.Client(api_key=api_key)
        self.aclient = cohere.AsyncClient(api_key=api_key)

    def generate(self, prompt_input: PromptInput):
        prompts = parse_prompts(prompt_input)
        input = self._to_prompt(prompts)
        result = self.client.generate(input, model=self.model)
        return Prompt(result.generations[0].text, role="ai")

    def _to_prompt(self, prompts: List[Prompt]) -> str:
        return "\n".join([p.text for p in prompts])
