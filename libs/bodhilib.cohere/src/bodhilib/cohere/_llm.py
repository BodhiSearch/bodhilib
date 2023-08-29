"""LLM implementation for Cohere."""
from typing import Any, Dict, List, Optional

from bodhilib.llm import LLM
from bodhilib.models import Prompt, prompt_output

import cohere


class Cohere(LLM):
    """Cohere API implementation for :class:`bodhilib.llm.LLM`."""

    def __init__(self, model: str, api_key: Optional[str], **kwargs: Dict[str, Any]):
        self.model = model
        self.client = cohere.Client(api_key=api_key)
        self.aclient = cohere.AsyncClient(api_key=api_key)
        self.kwargs = kwargs

    def _generate(self, prompts: List[Prompt], **kwargs: Dict[str, Any]) -> Prompt:
        input = self._to_cohere_input(prompts)
        # TODO - pass kwargs
        result = self.client.generate(input, model=self.model)
        return prompt_output(result.generations[0].text)

    def _to_cohere_input(self, prompts: List[Prompt]) -> str:
        return "\n".join([p.text for p in prompts])
