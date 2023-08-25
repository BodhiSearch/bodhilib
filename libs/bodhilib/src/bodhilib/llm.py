""":mod:`bodhilib.llm` module defines classes and methods for LLM operations."""

import abc
import itertools
import sys
from typing import Any, Callable, Dict, List, NamedTuple, Optional, cast

import pluggy
from bodhilib.logging import logger
from bodhilib.prompt import Prompt, PromptInput

# TODO - remove packagename duplication, import from core
package_name = "bodhilib"
current_module = sys.modules[__name__]


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


# plugins
hookspec = pluggy.HookspecMarker(package_name)


class Provider(NamedTuple):
    """Provider encapsulates info related to LLM service.

    This object is returned by plugins implementing the method `bodhilib_get_providers` and is used by the PluginManager
    to get an instance of LLM.
    """

    provider: str
    author: str
    type: str  # "llm", "vector_store", "embedder", "loader", "memory"
    func: Callable
    version: str = ""


@hookspec
def bodhilib_get_providers() -> List[Provider]:
    """Return a list of provider classes to be registered with the provider.

    Returns:
        List[Provider]: list of provider classes supported by the plugin
    """
    return []


class PluginManager:
    """Searches for and loads bodhilib plugins."""

    _instance = None

    def __new__(cls) -> "PluginManager":
        """Override `__new__` incase constructor is directly called."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def instance(cls) -> "PluginManager":
        """Singleton method to return instance of PluginManager."""
        # extracting in variable because of mypy warning
        instance = cls._instance
        if instance is None:
            return cls()
        return instance

    def __init__(self) -> None:
        """Initialize plugin manager and load the bodhilib plugins."""
        pm = pluggy.PluginManager(package_name)
        pm.add_hookspecs(current_module)
        pm.load_setuptools_entrypoints(package_name)
        from bodhilib import openai as bodhilib_openai

        pm.register(bodhilib_openai)
        self.pm = pm
        self.providers: Optional[List[Provider]] = None

    def get(self, type: str, provider: str, **kargs: Dict[str, Any]) -> LLM:
        """Get an instance of LLM for the given provider and type."""
        self.providers = self.providers or self._fetch_providers()
        for p in self.providers:
            if p.provider == provider and p.type == type:
                llm = p.func(provider, **kargs)
                return cast(LLM, llm)
        raise ValueError(f"Unknown provider: {provider}, available providers: {self.providers}")

    def _fetch_providers(self) -> List[Provider]:
        logger.debug({"msg": "fetching providers"})
        providers = list(itertools.chain(*self.pm.hook.bodhilib_get_providers()))
        logger.debug({"msg": "fetched providers", "providers": providers})
        # get list of providers which are not instance of Provider and log with warning
        invalid_providers = [p for p in providers if not isinstance(p, Provider)]
        if invalid_providers:
            logger.warning({"msg": "invalid providers, ignoring", "providers": invalid_providers})
        # get list of valid providers and log with debug
        valid_providers = [p for p in providers if isinstance(p, Provider)]
        logger.debug({"msg": "valid providers", "providers": valid_providers})
        return valid_providers


def get_llm(provider: str, model: str, api_key: Optional[str] = None) -> LLM:
    """Get an instance of LLM for the given provider and model.

    Returns:
        LLM: instance of LLM
    """
    manager = PluginManager.instance()
    llm = manager.get("llm", provider, model=model, api_key=api_key)  # type: ignore
    return cast(LLM, llm)


provider = pluggy.HookimplMarker(package_name)
