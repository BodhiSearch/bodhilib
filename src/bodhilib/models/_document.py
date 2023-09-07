from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Protocol, Union

from pydantic import BaseModel, Field
from typing_extensions import TypeAlias

PathLike: TypeAlias = Union[str, Path]
"""PathLike is either a path to a resource as string or pathlib.Path."""


class Document(BaseModel):
    """Document defines the basic interface for a processible resource.

    Primarily contains text (content) and metadata.
    """

    text: str
    """Text content of the document."""

    metadata: Dict[str, Any] = Field(default_factory=dict)
    """Metadata associated with the document. e.g. filename, dirname, url etc."""


class Node(BaseModel):
    """Chunk defines the basic interface for a processible resource.

    Primarily contains text (content) and metadata.
    """

    text: str
    """Text content of the document."""

    parent: Optional[Document] = None
    """Metadata associated with the document. e.g. filename, dirname, url etc."""


class SupportsText(Protocol):
    """TextLike is a protocol for types that can be converted to text."""

    @property
    def text(self) -> str:
        """Return the text representation of the object."""


def supportstext(obj: object) -> bool:
    """Returns True if the object supports :class:`~SupportText` protocol."""
    return hasattr(obj, "text")


TextLike: TypeAlias = Union[str, SupportsText]
"""TextLike is either a string or a Document."""


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
