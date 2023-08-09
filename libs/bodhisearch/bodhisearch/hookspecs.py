from typing import List, NamedTuple

import pluggy

package_name = "bodhisearch"
pluggy_project_name = "bodhisearch"


class Provider(NamedTuple):
    provider: str
    author: str
    type: str  # "llm", "vector_store", "embedder", "loader", "memory"
    callable_func: callable
    version: str = ""


hookspec = pluggy.HookspecMarker(pluggy_project_name)


@hookspec
def bodhisearch_get_providers() -> List[Provider]:
    """Return a list of provider classes to be registered with the provider
    :return: list of provider with identifiers and a callable function get an instance
    """
