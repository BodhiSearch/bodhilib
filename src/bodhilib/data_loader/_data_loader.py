from __future__ import annotations

import abc
from typing import Any, Dict, Iterator, List, Optional, Type, TypeVar, cast

from bodhilib.models import Document
from bodhilib.plugin import PluginManager, Service


class DataLoader(abc.ABC):
    """Abstract base class for data loaders.

    A data loader should inherit from this class and implement the abstract methods.
    """

    @abc.abstractmethod
    def add_resource(self, **kwargs: Dict[str, Any]) -> None:
        """Add a resource to the data loader."""

    @abc.abstractmethod
    def __iter__(self) -> Iterator[Document]:
        """Returns the document iterator."""


T = TypeVar("T", bound=DataLoader)
"""TypeVar for DataLoader."""


def get_data_loader(
    service_name: str,
    *,
    oftype: Optional[Type[T]] = None,
    publisher: Optional[str] = None,
    version: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> T:
    """Get an instance of data loader for given arguments.

    Given the service name, publisher (optional) and version(optional),
    return the registered data loader oftype (optional).

    Args:
        service_name (str): name of the service, e.g. "file", "notion", "s3"
        oftype (Optional[Type[T]]): if the type of data loader is known, pass the type in argument `oftype`,
            the data loader is cast to `oftype` and returned for better IDE support.
        publisher (Optional[str]): publisher or developer of the data loader plugin, e.g. "bodhilib","<github-username>"
        version (Optional[str]): version of the data loader
        **kwargs (Dict[str, Any]): pass through arguments for the data loader, e.g. aws_access_key_id, notion_db etc.

    Returns:
        T (:data:`~bodhilib.data_loader._data_loader.T` | :class:`~DataLoader`):
            an instance of DataLoader service of type `oftype`, if oftype is passed, else of type :class:`~DataLoader`

    Raises:
        TypeError: if the type of data loader is not oftype
    """
    if oftype is None:
        return_type: Type[Any] = DataLoader
    else:
        return_type = oftype

    manager = PluginManager.instance()
    data_loader: T = manager.get(
        service_name=service_name,
        service_type="data_loader",
        oftype=return_type,
        publisher=publisher,
        version=version,
        **kwargs,
    )
    if not isinstance(data_loader, return_type):
        raise TypeError(f"Expected data loader type={type(data_loader)} to be oftype={return_type}")
    return cast(T, data_loader)


def list_data_loaders() -> List[Service]:
    """List all data loaders installed and available."""
    manager = PluginManager.instance()
    return manager.list_services("data_loader")
