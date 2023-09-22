import abc
from typing import Iterable, List

from ._models import Document, Node, TextLikeOrTextLikeList, to_document_list


class Splitter(abc.ABC):
    """Splitter defines abstract method to split longer text into shorter text.

    Splitter takes in longer text as a generic :data:`~bodhilib.models.TextLike`
    and splits them into shorter text and return as :class:`~bodhilib.models.Node`.
    The shorter text are then used to create embeddings.
    """

    @abc.abstractmethod
    def split(self, texts: TextLikeOrTextLikeList) -> List[Node]:
        """Split a :data:`~bodhilib.models.TextLike` into :class:`~bodhilib.models.Node`."""


class BaseSplitter(Splitter):
    """BaseSplitter provides a simpler method for implementing Splitters.

    BaseSplitter overrides the abstract Splitter method :method:`~split`, massages the data and converts it to a
    list of :class:`~Document` and passes to implementing :method:`~_split` method.
    """

    def split(self, texts: TextLikeOrTextLikeList) -> List[Node]:
        docs = to_document_list(texts)
        return self._split(docs)

    @abc.abstractmethod
    def _split(self, docs: Iterable[Document]) -> List[Node]:
        """Split a list of :class:`~bodhilib.models.Document` into list of :class:`~bodhilib.models.Node`.

        The split method preserves the relationship and copies the metadata associated with Document to the Node.
        """
