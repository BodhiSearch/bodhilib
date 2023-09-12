"""mod:`bodhiext.splitter` bodhiext package for splitters."""
import inspect

from ._text_splitter import TextSplitter as TextSplitter
from ._plugin import bodhilib_list_services as bodhilib_list_services

__all__ = [name for name, obj in globals().items() if not (name.startswith("_") or inspect.ismodule(obj))]

del inspect
