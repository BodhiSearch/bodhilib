"""
LLM implementation for Cohere.

See https://cohere.ai/docs/quickstart

To use this provider, you must set the COHERE_API_KEY environment variable.

.. code-block:: python

    from bodhisearch import BodhiSearch
    from bodhisearch.cohere import Cohere

    bs = BodhiSearch(providers=[Cohere("curie")]
    bs.generate("Hello, I am a")This module contains

"""
import os
from typing import Any, Dict, List, Optional

from bodhisearch.llm import LLM, Provider, provider
from bodhisearch.prompt import Prompt, PromptInput, parse_prompts

import cohere


@provider
def bodhisearch_get_providers() -> List[Provider]:
    """
    This function is used by bodhisearch to find all providers in this module.
    """
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
    def __init__(self, model: str, api_key: Optional[str]):
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
