"""OpenAI API operations."""
import inspect

from ._openai_llm import OpenAIChat as OpenAIChat
from ._openai_llm import OpenAIText as OpenAIText
from ._openai_plugin import bodhilib_list_services as bodhilib_list_services
from ._openai_plugin import openai_chat_service_builder as openai_chat_service_builder
from ._openai_plugin import openai_text_service_builder as openai_text_service_builder
from ._version import __version__ as __version__

__all__ = [name for name, obj in globals().items() if not (name.startswith("_") or inspect.ismodule(obj))]

del inspect
