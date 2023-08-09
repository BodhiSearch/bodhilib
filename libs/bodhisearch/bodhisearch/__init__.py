import logging
import os

import pluggy


# name of the package
package_name = "bodhisearch"

# configure library-wide logging
logger = logging.getLogger(package_name)
root_logger = logging.getLogger()
log_level = os.environ.get("BODHISEARCH_LOG_LEVEL", root_logger.getEffectiveLevel())
logger.setLevel(log_level)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# pluggy settings
pluggy_project_name = "bodhisearch"
provider = pluggy.HookimplMarker(pluggy_project_name)
