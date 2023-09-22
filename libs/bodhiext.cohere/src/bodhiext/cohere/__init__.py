"""Cohere is a library for creating and managing a corpus of text documents."""
import inspect

from ._cohere_llm import Cohere as Cohere
from ._cohere_plugin import bodhilib_list_services as bodhilib_list_services
from ._cohere_plugin import cohere_llm_service_builder as cohere_llm_service_builder
from ._version import __version__ as __version__

__all__ = [name for name, obj in globals().items() if not (name.startswith("_") or inspect.ismodule(obj))]

del inspect
