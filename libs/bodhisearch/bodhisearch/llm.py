import abc
import itertools
import sys
from typing import Any, Callable, Dict, List, NamedTuple, Optional, cast

import pluggy
from bodhisearch.logging import logger
from bodhisearch.prompt import Prompt, PromptInput

# TODO - remove packagename duplication, import from core
package_name = "bodhisearch"
current_module = sys.modules[__name__]


class LLM(abc.ABC):
    @abc.abstractmethod
    def generate(self, prompts: PromptInput, **kwargs: Dict[str, Any]) -> Prompt:
        ...


# plugins
pluggy_project_name = "bodhisearch"

hookspec = pluggy.HookspecMarker(pluggy_project_name)


class Provider(NamedTuple):
    provider: str
    author: str
    type: str  # "llm", "vector_store", "embedder", "loader", "memory"
    func: Callable
    version: str = ""


@hookspec
def bodhisearch_get_providers() -> List[Provider]:
    """Return a list of provider classes to be registered with the provider
    :return: list of provider with identifiers and a callable function get an instance
    """
    return []


class PluginManager:
    _instance = None

    def __new__(cls) -> "PluginManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def instance(cls) -> "PluginManager":
        # extracting in variable because of mypy warning
        instance = cls._instance
        if instance is None:
            return cls()
        return instance

    def __init__(self) -> None:
        pm = pluggy.PluginManager(pluggy_project_name)
        pm.add_hookspecs(current_module)
        pm.load_setuptools_entrypoints(package_name)
        from bodhisearch import openai as bodhisearch_openai

        pm.register(bodhisearch_openai)
        self.pm = pm
        self.providers: Optional[List[Provider]] = None

    def get(self, type: str, provider: str, **kargs: Dict[str, Any]) -> LLM:
        self.providers = self.providers or self._fetch_providers()
        for p in self.providers:
            if p.provider == provider and p.type == type:
                llm = p.func(provider, **kargs)
                return cast(LLM, llm)
        raise ValueError(f"Unknown provider: {provider}, available providers: {self.providers}")

    def _fetch_providers(self) -> List[Provider]:
        logger.debug({"msg": "fetching providers"})
        providers = list(itertools.chain(*self.pm.hook.bodhisearch_get_providers()))
        logger.debug({"msg": "fetched providers", "providers": providers})
        # get list of providers which are not instance of Provider and log with warning
        invalid_providers = [p for p in providers if not isinstance(p, Provider)]
        if invalid_providers:
            logger.warning({"msg": "invalid providers, ignoring", "providers": invalid_providers})
        # get list of valid providers and log with debug
        valid_providers = [p for p in providers if isinstance(p, Provider)]
        logger.debug({"msg": "valid providers", "providers": valid_providers})
        return valid_providers


# factories
def get_llm(provider: str, model: str, api_key: Optional[str] = None) -> LLM:
    manager = PluginManager.instance()
    llm = manager.get("llm", provider, model=model, api_key=api_key)  # type: ignore
    return cast(LLM, llm)


pluggy_project_name = "bodhisearch"
provider = pluggy.HookimplMarker(pluggy_project_name)
