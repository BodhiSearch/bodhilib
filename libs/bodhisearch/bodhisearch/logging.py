import logging
import os

# TODO import constant from root package
package_name = "bodhisearch"


def init_logger() -> logging.Logger:
    # if library logging level not set, set the logger as the root logger
    log_level = os.environ.get("BODHISEARCH_LOG_LEVEL", None)
    if not log_level:
        return logging.getLogger()
    logger = logging.getLogger(package_name)
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    format = os.environ.get("BODHISEARCH_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = init_logger()
