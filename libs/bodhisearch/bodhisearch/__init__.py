import itertools

import pluggy

import bodhisearch.hookspecs as hookspecs

package_name = "bodhisearch"
pluggy_project_name = "bodhisearch"


provider = pluggy.HookimplMarker(pluggy_project_name)


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

    def get(self, type: str, provider: str, **kargs):
        self.providers = self.providers or list(itertools.chain(*self.pm.hook.bodhisearch_get_providers()))
        for p in self.providers:
            if p.provider == provider and p.type == type:
                return p.callable_func(provider, **kargs)
        raise ValueError(f"Unknown provider: {provider}")
