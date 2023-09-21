import abc
from typing import Iterable, List

from bodhilib.models import Document, Node, TextLike, to_document


class Splitter(abc.ABC):
    """Splitter defines abstract method to split longer text into shorter text.

    Splitter takes in longer text as a generic :data:`~bodhilib.models.TextLike`
    and splits them into shorter text and return as :class:`~bodhilib.models.Node`.
    The shorter text are then used to create embeddings.
    """

    def split(self, texts: Iterable[TextLike]) -> List[Node]:
        """Split a :data:`~bodhilib.models.TextLike` into :class:`~bodhilib.models.Node`."""
        docs: List[Document] = [to_document(text) for text in texts]
        return self._split(docs)

    @abc.abstractmethod
    def _split(self, docs: Iterable[Document]) -> List[Node]:
        """Split a :class:`~bodhilib.models.Document` into :class:`~bodhilib.models.Node`."""