""":mod:`bodhilib.splitter` module defines classes and methods for splitting text into shorter text."""
import inspect

from ._splitter import Splitter as Splitter
from ._text_splitter import TextSplitter as TextSplitter

__all__ = [name for name, obj in globals().items() if not (name.startswith("_") or inspect.ismodule(obj))]
