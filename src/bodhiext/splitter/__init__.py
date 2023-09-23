"""mod:`bodhiext.splitter` bodhiext package for splitters."""
import inspect

from ._plugin import bodhilib_list_services as bodhilib_list_services
from ._plugin import text_splitter_service_builder as text_splitter_service_builder
from ._text_splitter import TextSplitter as TextSplitter
from ._version import __version__ as __version__

__all__ = [name for name, obj in globals().items() if not (name.startswith("_") or inspect.ismodule(obj))]

del inspect
