from __future__ import annotations

import abc
from typing import Any, Dict, List, Optional, Type, TypeVar, cast

from bodhilib.models import Embedding, Node, TextLikeOrTextLikeList, to_node_list
from bodhilib.plugin import PluginManager, Service


class Embedder(abc.ABC):
    """Abstract base class for embedders.

    An embedder should inherit from this class and implement the abstract methods.
    """

    @abc.abstractmethod
    def embed(self, texts: TextLikeOrTextLikeList) -> List[Embedding]:
        """Embed the a list of :data:`~bodhilib.models.TextLike` using the embedder service.

        Args:
            text (List[TextLike]): a list of :data:`~bodhilib.models.TextLike` objects to embed

        Returns:
            List[Embedding]: list of embeddings, see :data:`~bodhilib.models.Embedding`
        """

    @property
    @abc.abstractmethod
    def dimension(self) -> int:
        """Dimension of the embeddings."""


class BaseEmbedder(Embedder):
    """BaseEmbedder provides a simpler method for implementing Embedders.

    BaseEmbedder overrides the abstract Embedder method :method:`~embed`, massages the data and converts the input
    to a list of :class:`~Node`, and passes to the abstract method to implement :method:`~_embed`.
    """

    def embed(self, texts: TextLikeOrTextLikeList) -> List[Embedding]:
        nodes = to_node_list(texts)
        return self._embed(nodes)

    @abc.abstractmethod
    def _embed(self, nodes: List[Node]) -> List[Embedding]:
        """Embed a list of strings using the embedder service.

        Args:
            nodes (List[Node]): list of :class:`~Node` to embed
        """


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
        T (:data:`~bodhilib._embedder.T` | :class:`~Embedder`):
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
