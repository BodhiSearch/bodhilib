"""Logging module for bodhilib."""

from bodhilib.common import package_name

from ._logging import init_logger

#: logging.Logger: logger used by bodhilib and plugins for logging
logger = init_logger(package_name)

__all__ = ["logger"]
