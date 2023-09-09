from __future__ import annotations

import abc
from typing import Any, Dict, List, Optional, Type, TypeVar, cast

from bodhilib.models import TextLike, istextlike, to_text
from bodhilib.plugin import PluginManager, Service


class Embedder(abc.ABC):
    """Abstract base class for embedders.

    An embedder should inherit from this class and implement the abstract methods.
    """

    def embed(self, texts: List[TextLike]) -> List[List[float]]:
        """Embed the a list of :data:`~TextLike` using the embedder service.

        Args:
            text (List[TextLike]): a list of :data:`~TextLike` objects to embed

        Returns:
            List[List[float]]: list of embeddings
        """
        if not isinstance(texts, list):
            raise ValueError(
                f"Expecting input `texts` to be a list of TextLike, but is of type {type(texts)}. Did you forget to"
                " pass it as a list?"
            )
        if not all(istextlike(t) for t in texts):
            raise ValueError(
                "Expecting input `texts` to be a list of TextLike items (a string or have attribute `text`), "
                "but some elements of the list are not TextLike"
            )
        input = [to_text(t) for t in texts]
        embeddings: List[List[float]] = self._embed(input)
        return embeddings

    @abc.abstractmethod
    def _embed(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of strings using the embedder service.

        Args:
            texts (List[str]): list of texts to embed
        """

    @property
    @abc.abstractmethod
    def dimension(self) -> int:
        """Dimension of the embeddings."""


T = TypeVar("T", bound=Embedder)
"""TypeVar for Embedder."""


def get_embedder(
    service_name: str,
    *,
    oftype: Optional[Type[T]] = None,
    publisher: Optional[str] = None,
    version: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> T:
    """Get an instance of embedder given the service name, publisher (optional) and version(optional).

    Args:
        service_name (str): name of the service, e.g. "sentence-transformers" etc.
        oftype (Optional[Type[T]]): if the type of embedder is known, pass the type in argument `oftype`,
            the embedder is cast to `oftype` and returned for better IDE support.
        publisher (Optional[str]): publisher or developer of the embedder plugin, e.g. "bodhilib","<github-username>"
        version (Optional[str]): version of the embedder
        **kwargs (Dict[str, Any]): pass through arguments for the embedder, e.g. dimension etc.

    Returns:
        T (:data:`~bodhilib.embedder._embedder.T` | :class:`~Embedder`):
            an instance of Embedder service of type `oftype`, if oftype is passed, else of type :class:`~Embedder`

    Raises:
        TypeError: if the type of embedder is not oftype
    """
    if oftype is None:
        return_type: Type[Any] = Embedder
    else:
        return_type = oftype

    manager = PluginManager.instance()
    embedder: T = manager.get(
        service_name=service_name,
        service_type="embedder",
        oftype=return_type,
        publisher=publisher,
        version=version,
        **kwargs,
    )
    return cast(T, embedder)


def list_embedders() -> List[Service]:
    """List all embedders installed and available."""
    manager = PluginManager.instance()
    return manager.list_services("embedder")
