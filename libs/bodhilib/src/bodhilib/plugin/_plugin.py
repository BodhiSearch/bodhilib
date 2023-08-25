import itertools
import sys
from typing import Any, Callable, Dict, List, NamedTuple, Optional

import pluggy
from bodhilib.common import package_name
from bodhilib.logging import logger

hookspec = pluggy.HookspecMarker(package_name)
provider = pluggy.HookimplMarker(package_name)
current_module = sys.modules[__name__]


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

    def get(self, type: str, provider: str, **kargs: Dict[str, Any]) -> Any:
        """Get an instance of service for the given provider and type."""
        self.providers = self.providers or self._fetch_providers()
        for p in self.providers:
            if p.provider == provider and p.type == type:
                component = p.func(provider, **kargs)
                return component
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
