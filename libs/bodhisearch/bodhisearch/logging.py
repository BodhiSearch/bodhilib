import logging
import os

# TODO import constant from root package
package_name = "bodhisearch"


def init_logger():
    # if library logging level not set, set the logger as the root logger
    if "BODHISEARCH_LOG_LEVEL" not in os.environ:
        return logging.getLogger()
    log_level = os.environ.get("BODHISEARCH_LOG_LEVEL")
    logger = logging.getLogger(package_name)
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    format = os.environ("BODHISEARCH_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


logger = init_logger()
