"""LLM implementation for Cohere."""
import os
from typing import Any, Dict, List, Optional

from bodhilib.llm import LLM
from bodhilib.plugin import Service, service_provider
from bodhilib.prompt import Prompt, PromptInput, parse_prompts

import cohere


@service_provider
def bodhilib_list_services() -> List[Service]:
    """This function is used by bodhilib to find all services in this module."""
    return [Service("cohere", "llm", "bodhilib", cohere_llm_service_builder, "0.1.0")]


def cohere_llm_service_builder(
    *,
    service_name: Optional[str] = None,
    service_type: Optional[str] = "llm",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> LLM:
    """Returns an instance of Cohere LLM service implementing :class:`bodhilib.llm.LLM`.

    Args:
        service_name: service name to wrap, should be "cohere"
        service_type: service type of the implementation, should be "llm"
        model: Cohere model identifier
        api_key: api key for Cohere service, if not set, it will be read from environment variable COHERE_API_KEY
    Returns:
        LLM: a service instance implementing :class:`bodhilib.llm.LLM` for the given service and model
    Raises:
        ValueError: if service_name is not "cohere"
        ValueError: if service_type is not "llm"
        ValueError: if model is not set
        ValueError: if api_key is not set, and environment variable COHERE_API_KEY is not set
    """
    # TODO use pydantic for parameter validation
    if service_name != "cohere":
        raise ValueError(f"Unknown service: {service_name=}")
    if service_type != "llm":
        raise ValueError(f"Unknown service type: {service_type=}")
    if model is None:
        raise ValueError("model is not set")
    if api_key is None:
        if os.environ.get("COHERE_API_KEY") is None:
            raise ValueError("environment variable COHERE_API_KEY is not set")
        else:
            api_key = os.environ["COHERE_API_KEY"]
    # TODO filter for Cohere configs
    return Cohere(model=model, api_key=api_key, **kwargs)


class Cohere(LLM):
    """Cohere API implementation for :class:`bodhilib.llm.LLM`."""

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
