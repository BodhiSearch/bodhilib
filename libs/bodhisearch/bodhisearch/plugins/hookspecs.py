from typing import List

import pluggy

from bodhisearch import Provider

pluggy_project_name = "bodhisearch"

hookspec = pluggy.HookspecMarker(pluggy_project_name)


@hookspec
def bodhisearch_get_providers() -> List[Provider]:
    """Return a list of provider classes to be registered with the provider
    :return: list of provider with identifiers and a callable function get an instance
    """
    return []
