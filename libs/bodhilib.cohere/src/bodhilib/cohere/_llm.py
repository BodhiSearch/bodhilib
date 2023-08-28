"""LLM implementation for Cohere."""
from typing import Any, Dict, List, Optional

from bodhilib.llm import LLM, PromptInput, parse_prompts
from bodhilib.models import Prompt

import cohere


class Cohere(LLM):
    """Cohere API implementation for :class:`bodhilib.llm.LLM`."""

    def __init__(self, model: str, api_key: Optional[str], **kwargs: Dict[str, Any]):
        self.model = model
        self.client = cohere.Client(api_key=api_key)
        self.aclient = cohere.AsyncClient(api_key=api_key)
        self.kwargs = kwargs

    def generate(self, prompts: PromptInput, **kwargs: Dict[str, Any]) -> Prompt:
        parsed_prompts = parse_prompts(prompts)
        input = self._to_prompt(parsed_prompts)
        # TODO - pass kwargs
        result = self.client.generate(input, model=self.model)
        return Prompt(result.generations[0].text, role="ai", source="output")

    def _to_prompt(self, prompts: List[Prompt]) -> str:
        return "\n".join([p.text for p in prompts])
