from __future__ import annotations

import abc
import itertools
from typing import Any, Dict, List, Optional, Union, cast

from bodhilib.models import Prompt
from bodhilib.plugin import PluginManager
from typing_extensions import TypeAlias

PromptInput: TypeAlias = Union[str, List[str], Prompt, List[Prompt], Dict[str, Any], List[Dict[str, Any]]]
"""Type alias for the input to parse_prompts function."""


def parse_prompts(input: PromptInput) -> List[Prompt]:
    """Parses from the PromptInput to List[Prompt].

    Args:
        input (:data:`PromptInput`): input to parse from
    """
    if isinstance(input, str):
        return [Prompt(input)]
    if isinstance(input, Prompt):
        return [input]
    if isinstance(input, dict):
        return [Prompt(**input)]
    if isinstance(input, list):
        result = [parse_prompts(p) for p in input]
        return list(itertools.chain(*result))
    raise TypeError(f"Unknown prompt type: {type(input)}")


class LLM(abc.ABC):
    """Abstract Base Class LLM defines the common interface implemented by all LLM implementations."""

    @abc.abstractmethod
    def generate(self, prompts: PromptInput, **kwargs: Dict[str, Any]) -> Prompt:
        """Generate text using LLM with the given prompt.

        Args:
            prompts (:data:`PromptInput`): prompt to generate text from
            **kwargs (Dict[str, Any]): additional arguments

        Returns:
            :class:`bodhilib.models.Prompt`: generated text as a Prompt object
        """
        ...


def get_llm(
    service_name: str,
    model: str,
    api_key: Optional[str] = None,
    *,
    publisher: Optional[str] = None,
    version: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> LLM:
    """Get an instance of LLM for the given service name and model.

    Args:
        service_name (str): name of the service
        model (str): name of the model
        api_key (Optional[str]): API key for the service
        publisher (Optional[str]): publisher of the service
        version (Optional[str]): version of the service
        **kwargs (Dict[str, Any]): additional arguments for the LLM service

    Returns:
        LLM: instance of LLM
    """
    manager = PluginManager.instance()
    llm = manager.get(
        service_name=service_name,
        service_type="llm",
        model=model,
        api_key=api_key,
        publisher=publisher,
        version=version,
        **kwargs,
    )
    return cast(LLM, llm)
