from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Protocol, Union

from pydantic import BaseModel, Field
from typing_extensions import TypeAlias


class Document(BaseModel):
    """Document defines the basic interface for a processible resource.

    Primarily contains text (content) and metadata.
    """

    text: str
    """Text content of the document."""

    metadata: Dict[str, Any] = Field(default_factory=dict)
    """Metadata associated with the document. e.g. filename, dirname, url etc."""


class SupportsText(Protocol):
    """TextLike is a protocol for types that can be converted to text."""

    @property
    def text(self) -> str:
        """Return the text representation of the object."""


TextLike: TypeAlias = Union[str, SupportsText]
"""TextLike is either a string or a Document."""

PathLike: TypeAlias = Union[str, Path]
"""PathLike is either a path to a resource as string or pathlib.Path."""


def to_text(text: TextLike) -> str:
    """Converts a :data:`~TextLike` to string."""
    if isinstance(text, str):
        return text
    if hasattr(text, "text"):
        return text.text
    raise ValueError(f"Cannot convert type {type(text)} to text.")
