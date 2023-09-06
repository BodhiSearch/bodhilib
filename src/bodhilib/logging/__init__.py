"""Logging module for bodhilib."""
import inspect

from ._logging import init_logger

#: logging.Logger: logger used by bodhilib and plugins for logging
logger = init_logger()

__all__ = [name for name, obj in globals().items() if not (name.startswith("_") or inspect.ismodule(obj))]
