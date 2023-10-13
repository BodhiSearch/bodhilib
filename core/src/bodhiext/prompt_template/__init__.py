"""mod:`bodhiext.prompt_template` bodhiext package for prompt_templates."""
import inspect

from ._string_prompt_template import StringPromptTemplate as StringPromptTemplate
from ._version import __version__ as __version__

__all__ = [name for name, obj in globals().items() if not (name.startswith("_") or inspect.ismodule(obj))]

del inspect
