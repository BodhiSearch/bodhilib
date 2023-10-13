"""mod:`bodhiext.prompt_template` bodhiext package for prompt_templates."""
import inspect

from ._string_prompt_template import StringPromptTemplate as StringPromptTemplate

__all__ = [name for name, obj in globals().items() if not (name.startswith("_") or inspect.ismodule(obj))]

del inspect
