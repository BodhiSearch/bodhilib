"""Contains model classes used by bohilib as inputs and outputs to operations."""
import inspect

from ._models import Distance as Distance
from ._models import Document as Document
from ._models import Node as Node
from ._models import PathLike as PathLike
from ._models import Prompt as Prompt
from ._models import PromptStream as PromptStream
from ._models import Role as Role
from ._models import Source as Source
from ._models import StrEnumMixin as StrEnumMixin
from ._models import SupportsText as SupportsText
from ._models import TextLike as TextLike
from ._models import istextlike as istextlike
from ._models import prompt_output as prompt_output
from ._models import prompt_user as prompt_user
from ._models import supportstext as supportstext
from ._models import to_document as to_document
from ._models import to_text as to_text
from ._template import PromptTemplate as PromptTemplate
from ._template import prompt_with_examples as prompt_with_examples

__all__ = [name for name, obj in globals().items() if not (name.startswith("_") or inspect.ismodule(obj))]

del inspect
