import pluggy

from bodhisearch.logger.logging import init_logger

package_name = "bodhisearch"

logger = init_logger()

# pluggy settings
pluggy_project_name = "bodhisearch"
provider = pluggy.HookimplMarker(pluggy_project_name)
