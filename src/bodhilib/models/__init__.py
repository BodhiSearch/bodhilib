"""Contains model classes used by bohilib as inputs and outputs to operations."""
import inspect

from ._prompt import Prompt as Prompt
from ._prompt import Role as Role
from ._prompt import Source as Source
from ._prompt import StrEnumMixin as StrEnumMixin
from ._prompt import prompt_output as prompt_output
from ._prompt import prompt_user as prompt_user
from ._template import PromptTemplate as PromptTemplate
from ._template import prompt_with_examples as prompt_with_examples

__all__ = [name for name, obj in globals().items() if not (name.startswith("_") or inspect.ismodule(obj))]