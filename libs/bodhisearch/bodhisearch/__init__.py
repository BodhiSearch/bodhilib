import logging
import os

import pluggy


package_name = "bodhisearch"

logger = None


def set_logger(logger_: logging.Logger, /) -> None:
    global logger
    logger = logger_


def init_logger():
    # if library logging level not set, set the logger as the root logger
    if "BODHISEARCH_LOG_LEVEL" not in os.environ:
        set_logger(logging.getLogger())
        return
    log_level = os.environ.get("BODHISEARCH_LOG_LEVEL")
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    format = os.environ("BODHISEARCH_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


init_logger()

# pluggy settings
pluggy_project_name = "bodhisearch"
provider = pluggy.HookimplMarker(pluggy_project_name)
