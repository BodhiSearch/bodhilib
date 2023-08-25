import abc
from typing import Any, Dict, Optional, cast

from bodhilib.plugin import PluginManager
from bodhilib.prompt import Prompt, PromptInput


class LLM(abc.ABC):
    """Abstract Base Class LLM defines the common interface implemented by all LLM implementations."""

    @abc.abstractmethod
    def generate(self, prompts: PromptInput, **kwargs: Dict[str, Any]) -> Prompt:
        """Generate text using LLM with the given prompt.

        Args:
            prompts: prompt to generate text from. Prompt can be any of the following::
                - str: a string prompt
                - Prompt: a :class:`.Prompt` object
                - List[str]: a list of :obj:`str` prompts
                - List[Prompt]: a list of :class:`.Prompt` objects
                - Dict[str, Any]: a dict of prompt in keyword "prompt" and additional arguments
                - List[Dict[str, Any]]: a list of dict of prompt in keyword "prompt" and additional arguments
            **kwargs: additional arguments

        Returns:
            Prompt: generated text as a Prompt object
        """
        ...


def get_llm(service_name: str, model: str, api_key: Optional[str] = None) -> LLM:
    """Get an instance of LLM for the given service name and model.

    Returns:
        LLM: instance of LLM
    """
    manager = PluginManager.instance()
    llm = manager.get(service_name, "llm", model=model, api_key=api_key)  # type: ignore
    return cast(LLM, llm)
