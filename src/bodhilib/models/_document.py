from __future__ import annotations

import reprlib
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Union

from pydantic import BaseModel, Field
from typing_extensions import TypeAlias

from ._prompt import StrEnumMixin

PathLike: TypeAlias = Union[str, Path]
"""PathLike is either a path to a resource as string or pathlib.Path."""


class Distance(StrEnumMixin, str, Enum):
    """Vector Distance Method."""

    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"


class Document(BaseModel):
    """Document defines the basic interface for a processible resource.

    Primarily contains text (content) and metadata.
    """

    text: str
    """Text content of the document."""

    metadata: Dict[str, Any] = Field(default_factory=dict)
    """Metadata associated with the document. e.g. filename, dirname, url etc."""

    def __repr__(self) -> str:
        """Returns a string representation of the document."""
        return f"Document(text={reprlib.repr(self.text)}, metadata={reprlib.repr(self.metadata)})"


class Node(BaseModel):
    """Node defines the basic data structure for a processible resource.

    It contains a unique identifier, content text, metadata associated with its sources,
    and embeddings.
    """

    id: Optional[str] = None
    """Unique identifier for the node.

    Generated during the document split operation, or retrieved from doc/vector database at the time of query."""

    text: str
    """Text content of the document."""

    parent: Optional[Document] = None
    """Metadata associated with the document. e.g. filename, dirname, url etc."""

    metadata: Dict[str, Any] = Field(default_factory=dict)
    """Metadata associated with the node. This is also copied over from parent when splitting Document."""

    embedding: Optional[List[float]] = None

    def __repr__(self) -> str:
        """Returns a string representation of the document."""
        return f"Node(id={self.id}, text={reprlib.repr(self.text)}, parent={repr(self.parent)})"


class SupportsText(Protocol):
    """TextLike is a protocol for types that can be converted to text."""

    @property
    def text(self) -> str:
        """Return the text representation of the object."""


def supportstext(obj: object) -> bool:
    """Returns True if the object supports :class:`~bodhilib.models.SupportsText` protocol."""
    return hasattr(obj, "text")


TextLike: TypeAlias = Union[str, SupportsText]
"""TextLike is either a string or a Document."""


def istextlike(obj: object) -> bool:
    """Returns True if the object is a :data:`~TextLike`."""
    return isinstance(obj, str) or supportstext(obj)


def to_document(textlike: TextLike) -> Document:
    """Converts a :data:`~TextLike` to :class:`~Document`."""
    if isinstance(textlike, Document):
        return textlike
    elif isinstance(textlike, str):
        return Document(text=textlike)
    elif supportstext(textlike):
        return Document(text=textlike.text)
    raise ValueError(f"Cannot convert type {type(textlike)} to Document.")


def to_text(textlike: TextLike) -> str:
    """Converts a :data:`~TextLike` to string."""
    if isinstance(textlike, str):
        return textlike
    if supportstext(textlike):
        return textlike.text
    raise ValueError(f"Cannot convert type {type(textlike)} to text.")
