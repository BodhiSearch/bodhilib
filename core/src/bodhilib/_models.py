from __future__ import annotations

import io
import itertools
import reprlib
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
    cast,
    no_type_check,
)

from pydantic import BaseModel, Field, validator
from typing_extensions import TypeAlias

# region type aliases
#######################################################################################################################
# Update the documentation in bodhilib.rst file directly. TypeAlias inline documentation not picked up by sphinx.
# Duplicating it here to make it easier when browsing the code.
PathLike: TypeAlias = Union[str, Path]
"""Type alias for Union of :class:`str` and :class:`~pathlib.Path`"""
TextLike: TypeAlias = Union[str, "SupportsText"]
"""Type alias for Union of :class:`str` and protocol :data:`~bodhilib.SupportsText`"""
TextLikeOrTextLikeList: TypeAlias = Union[TextLike, Iterable[TextLike]]
"""Type alias for Union of :data:`~bodhilib.TextLike` or list of :data:`~bodhilib.TextLike`"""
SerializedInput: TypeAlias = Union[TextLikeOrTextLikeList, Dict[str, Any], Iterable[Dict[str, Any]]]
"""Type alias for various inputs that can be passed to the components."""
Embedding: TypeAlias = List[float]
"""Type alias for list of :class:`float`, to indicate the embedding generated
from :class:`~bodhilib.Embedder` operation"""


class SupportsText(Protocol):
    """TextLike is a protocol for types that can be converted to text.

    To support the protocol, the type must have a property `text`.

    Known sub-classes: :class:`~bodhilib.Prompt`, :class:`~bodhilib.Document`, :class:`~bodhilib.Node`
    """

    @property
    def text(self) -> str:
        """Return the content of the object as string."""


class SupportsEmbedding(Protocol):
    """SupportsEmbedding matches the types that contains a field `embedding` of type :data:`~bodhilib.Embedding`."""

    @property
    def embedding(self) -> Embedding:
        """Return the embedding of the object as :data:`~bodhilib.Embedding`."""


def supportstext(obj: object) -> bool:
    """Returns True if the object supports :data:`~bodhilib.SupportsText` protocol."""
    return hasattr(obj, "text")


def istextlike(obj: object) -> bool:
    """Returns True if the object is a :data:`~TextLike`."""
    return isinstance(obj, str) or supportstext(obj)


def supportsembedding(obj: object) -> bool:
    """Returns True if the object supports :data:`~bodhilib.SupportsEmbedding` protocol."""
    return hasattr(obj, "embedding")


# endregion
# region utility
#######################################################################################################################
class _StrEnumMixin:
    """Mixin class for string enums, provides __str__ and __eq__ methods."""

    @no_type_check
    def __str__(self) -> str:
        """Returns the string value of the string enum."""
        return self.value

    @no_type_check
    def __eq__(self, other: Any) -> bool:
        """Compares this string enum to other string enum or string values."""
        if isinstance(other, str):
            return self.value == other
        elif isinstance(other, type(self)):
            return self.value == other.value
        return False

    @no_type_check
    @classmethod
    def membersstr(cls) -> List[str]:
        return [e.value for e in cls.__members__.values()]


_EnumT = TypeVar("_EnumT", bound=Enum)
"""TypeVar for Enum type."""


def _strenum_validator(enum_cls: Type[_EnumT], value: Any) -> _EnumT:
    """Converts a string value to an enum value."""
    if isinstance(value, str):
        try:
            return enum_cls[value.upper()]
        except KeyError as e:
            allowed_values = [e.value for e in enum_cls]
            raise ValueError(f"Invalid value for {enum_cls.__name__}. Allowed values are {allowed_values}.") from e
    elif isinstance(value, enum_cls):
        return value
    else:
        raise ValueError(f"Invalid type for value, {type(value)=}")


# endregion
# region value objects
#######################################################################################################################
class Role(_StrEnumMixin, str, Enum):
    """Role of the prompt.

    Used for fine-grain control over "role" instructions to the LLM service.
    Can be one of - *'system', 'ai', or 'user'*.
    """

    SYSTEM = "system"
    AI = "ai"
    USER = "user"


class Source(_StrEnumMixin, str, Enum):
    """Source of the prompt.

    If the prompt is given as input by the user, then *source="input"*,
    or if the prompt is generated as response by the LLM service, then *source="output"*.
    """

    INPUT = "input"
    OUTPUT = "output"


class Distance(_StrEnumMixin, str, Enum):
    """Vector Distance Method."""

    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"


# endregion
# region prompt
#######################################################################################################################
class Prompt(BaseModel):
    """Prompt encapsulating input/output schema to interact with LLM service."""

    role: Role = Role.USER
    """The role of the prompt.

    Defaults to :obj:`Role.USER`."""

    source: Source = Source.INPUT
    """The source of the prompt.

    Defaults to :obj:`Source.INPUT`."""

    text: str
    """The text or content or input component of the prompt."""

    class Config:
        use_enum_values = True

    # overriding __init__ to provide positional argument construction for prompt. E.g. `Prompt("text")`
    def __init__(
        self,
        text: str,
        role: Optional[Union[Role, str]] = Role.USER,
        source: Optional[Union[Source, str]] = Source.INPUT,
    ):
        """Initialize a prompt.

        Args:
            text (str): text of the prompt
            role (Role): role of the prompt.

                Role can be given as one of the allowed string value ["system", "ai", "user"]
                or as a Role enum [:obj:`Role.SYSTEM`, :obj:`Role.AI`, :obj:`Role.USER`].

                The string is converted to Role enum. If the string value is not one of the allowed values,
                then a ValueError is raised.
            source (Source): source of the prompt.

                Source can be given as a one of the allowed string value ["input", "output"]
                or as a Source enum [:obj:`Source.INPUT`, :obj:`Source.OUTPUT`].

                The string is converted to Source enum. If the string value is not one of the allowed values,
                then a ValueError is raised.

        Raises:
            ValueError: If the role or source is not one of the allowed values.
        """
        role = role or Role.USER
        source = source or Source.INPUT
        super().__init__(text=text, role=role, source=source)

    @validator("role", pre=True, always=True)
    def validate_role(cls, value: Any) -> Role:
        return _strenum_validator(Role, value)

    @validator("source", pre=True, always=True)
    def validate_source(cls, value: Any) -> Source:
        return _strenum_validator(Source, value)

    def isstream(self) -> bool:
        """To check if this is a prompt stream.

        Returns:
            bool: False as this is not a prompt stream.
        """
        return False


T = TypeVar("T")
"""TypeVar for LLM Response Type."""


class PromptStream(Iterator[Prompt]):
    """Iterator over a stream of prompts.

    Used by LLMs to wrap the stream response to an iterable over prompts.
    """

    def __init__(self, api_response: Iterable[T], transformer: Callable[[T], Prompt]):
        """Initialize a prompt stream.

        Args:
            api_response (Iterable[T]): LLM API Response of generic type :data:`~bodhilib.T` as Iterable
            transformer (Callable[[T], Prompt]): Transformer function to convert API response to Prompt
        """
        self.api_response = iter(api_response)
        self.transformer = transformer
        self.output = io.StringIO()
        self.role: Optional[str] = None

    def __iter__(self) -> Iterator[Prompt]:
        """Returns the iterator object itself."""
        return self

    def __next__(self) -> Prompt:
        """Returns the next item from the iterator as Prompt object."""
        try:
            chunk_response = next(self.api_response)
        except StopIteration as e:
            raise StopIteration from e
        prompt = self.transformer(chunk_response)
        if self.role is None:
            self.role = prompt.role
        self.output.write(prompt.text)
        return prompt

    def isstream(self) -> bool:
        """To check if this is a prompt stream.

        Returns:
            bool: False as this is not a prompt stream.
        """
        return True

    @property
    def text(self) -> str:
        # TODO change it to first read all the stream content, and then return the text
        # Create another property to return so-far accumulated text
        """Returns the text accumulated over the stream of responses."""
        return self.output.getvalue()


def prompt_user(text: str) -> Prompt:
    """Factory method to generate user prompt from string.

    Args:
        text: text of the prompt

    Returns:
        Prompt: Prompt object generated from the text. Defaults role="user" and source="input".
    """
    return Prompt(text=text, role=Role.USER, source=Source.INPUT)


def prompt_system(text: str) -> Prompt:
    """Factory method to generate system prompt from string.

    Args:
        text: text of the prompt

    Returns:
        Prompt: Prompt object generated from the text. Defaults role="system" and source="input".
    """
    return Prompt(text=text, role=Role.SYSTEM, source=Source.INPUT)


def prompt_output(text: str) -> Prompt:
    """Factory method to generate output prompts.

    Generates a prompt with source="output". Mainly by LLMs to generate output prompts.
    """
    return Prompt(text=text, role=Role.AI, source=Source.OUTPUT)


# endregion
# region document
#######################################################################################################################
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

    embedding: Optional[Embedding] = None

    def __repr__(self) -> str:
        """Returns a string representation of the document."""
        return f"Node(id={self.id}, text={reprlib.repr(self.text)}, parent={repr(self.parent)})"


# endregion
# region model converters
#######################################################################################################################
def to_document(textlike: TextLike) -> Document:
    """Converts a :data:`~bodhilib.TextLike` to :class:`~bodhilib.Document`."""
    if isinstance(textlike, Document):
        return textlike
    elif isinstance(textlike, str):
        return Document(text=textlike)
    elif supportstext(textlike):
        return Document(text=textlike.text)
    raise ValueError(f"Cannot convert type {type(textlike)} to Document.")


def to_prompt(textlike: TextLike) -> Prompt:
    """Converts a :data:`~TextLike` to :class:`~Prompt`."""
    if isinstance(textlike, Prompt):
        return textlike
    elif isinstance(textlike, str):
        return Prompt(text=textlike)
    elif supportstext(textlike):
        return Prompt(text=textlike.text)
    raise ValueError(f"Cannot convert type {type(textlike)} to Prompt.")


def to_node(textlike: TextLike) -> Node:
    """Converts a :data:`~TextLike` to :class:`~Node`."""
    if isinstance(textlike, Node):
        return textlike
    elif isinstance(textlike, str):
        return Node(text=textlike)
    elif supportstext(textlike):
        return Node(text=textlike.text)
    raise ValueError(f"Cannot convert type {type(textlike)} to Node.")


def to_text(textlike: TextLike) -> str:
    """Converts a :data:`~TextLike` to string."""
    if isinstance(textlike, str):
        return textlike
    if supportstext(textlike):
        return textlike.text
    raise ValueError(f"Cannot convert type {type(textlike)} to text.")


def to_prompt_list(inputs: SerializedInput) -> List[Prompt]:
    """Converts a :data:`~bodhilib.SerializedInput` to list of :class:`~Prompt`."""
    if istextlike(inputs):
        return [to_prompt(cast(TextLike, inputs))]  # cast to fix mypy warning
    elif isinstance(inputs, dict):
        return [Prompt(**inputs)]
    elif isinstance(inputs, Iterable):
        result = [to_prompt_list(textlike) for textlike in inputs]
        return list(itertools.chain(*result))
    else:
        return [to_prompt(inputs)]


def to_document_list(inputs: SerializedInput) -> List[Document]:
    """Converts a :data:`~bodhilib.SerializedInput` to list of :class:`~Document`."""
    if istextlike(inputs):
        return [to_document(cast(TextLike, inputs))]  # cast to fix mypy warning
    elif isinstance(inputs, dict):
        return [Document(**inputs)]
    if isinstance(inputs, Iterable):
        result = [to_document_list(input) for input in inputs]
        return list(itertools.chain(*result))
    else:
        return [to_document(inputs)]


def to_node_list(inputs: SerializedInput) -> List[Node]:
    """Converts a :data:`~bodhilib.SerializedInput` to list of :class:`~Node`."""
    if (
        not isinstance(inputs, BaseModel)  # BaseModel is Iterable
        and isinstance(inputs, Iterable)  # if is list
        and all(isinstance(input, Node) for input in inputs)  # and if all are Node instance
    ):
        return inputs  # type: ignore
    if istextlike(inputs):
        return [to_node(cast(TextLike, inputs))]  # cast to fix mypy warning
    elif isinstance(inputs, dict):
        return [Node(**inputs)]
    elif isinstance(inputs, Iterable):
        result = [to_node_list(input) for input in inputs]
        return list(itertools.chain(*result))
    else:
        return [to_node(inputs)]


# endregion
# region utils
#######################################################################################################################


# endregion
