from __future__ import annotations

import logging
import os


def init_logger(package_name: str) -> logging.Logger:
    """Initialize logger for bodhilib.

    Returns the default logger if BODHILIB_LOG_LEVEL is not set, else returns a logger with
    the name "bodhilib" and log level set to BODHILIB_LOG_LEVEL. Optionally also sets the
    format of the log message using BODHILIB_LOG_FORMAT.

    Returns:
        logging.Logger: logger for bodhilib
    """
    # if library logging level not set, set the logger as the root logger
    log_level = os.environ.get("BODHILIB_LOG_LEVEL", None)
    if not log_level:
        return logging.getLogger()
    logger = logging.getLogger(package_name)
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    format = os.environ.get("BODHILIB_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
