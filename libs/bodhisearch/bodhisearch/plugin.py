import itertools
from typing import Any, Dict, Optional, cast

import pluggy

import bodhisearch.hookspecs as hookspecs
from bodhisearch import logger, package_name, pluggy_project_name
from bodhisearch.hookspecs import Provider
from bodhisearch.llm import LLM


class PluginManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pm = pluggy.PluginManager(pluggy_project_name)
        pm.add_hookspecs(hookspecs)
        pm.load_setuptools_entrypoints(package_name)
        from bodhisearch import openai as bodhisearch_openai

        pm.register(bodhisearch_openai)
        self.pm = pm
        self.providers = None

    def get(self, type: str, provider: str, **kargs: Dict[str, Any]) -> LLM:
        self.providers = self.providers or self._fetch_providers()
        for p in self.providers:
            if p.provider == provider and p.type == type:
                return p.callable_func(provider, **kargs)  # type: ignore
        raise ValueError(f"Unknown provider: {provider}")

    def _fetch_providers(self):
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


def get_llm(provider: str, model: str, api_key: Optional[str] = None) -> LLM:
    return cast(LLM, PluginManager().get("llm", provider, model=model, api_key=api_key))  # type: ignore
