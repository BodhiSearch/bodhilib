from __future__ import annotations

import io
import itertools
import re
import reprlib
import textwrap
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
    cast,
    no_type_check,
)

from jinja2 import Template
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


def supportstext(obj: object) -> bool:
    """Returns True if the object supports :data:`~bodhilib.SupportsText` protocol."""
    return hasattr(obj, "text")


def istextlike(obj: object) -> bool:
    """Returns True if the object is a :data:`~TextLike`."""
    return isinstance(obj, str) or supportstext(obj)


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

    text: str
    """The text or content or input component of the prompt."""

    role: Role = Role.USER
    """The role of the prompt.

    Defaults to :obj:`Role.USER`."""

    source: Source = Source.INPUT
    """The source of the prompt.

    Defaults to :obj:`Source.INPUT`."""

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
# region prompt template
#######################################################################################################################

TemplateFormat = Literal["fstring", "jinja2", "bodhilib-fstring", "bodhilib-jinja2"]


class PromptTemplate(BaseModel):
    """PromptTemplate used for generating prompts using a template."""

    template: str
    """Template for generating prompts."""

    role: Role = Role.USER
    """Role of the prompt."""

    source: Source = Source.INPUT
    """Source of the prompt."""

    format: TemplateFormat = "fstring"
    """Template format to use for rendering."""

    tags: List[str] = Field(default_factory=list)
    """Searchable tags associated with the template."""

    extras: Dict[str, Any] = Field(default_factory=dict)
    """The context variables to be used for rendering the template."""

    # overriding __init__ to provide positional argument construction for prompt template.
    # E.g. `PromptTemplate("my template {context}")`
    def __init__(
        self,
        template: str,
        role: Optional[Role] = None,
        source: Optional[Source] = None,
        format: Optional[TemplateFormat] = "fstring",
        tags: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ) -> None:
        """Initializes a prompt template.

        Args:
            template: template string
            role: role of the prompt.
            source: source of the prompt.
            format: format to use for rendering the template.
            tags: the searchable tags for the template
            **kwargs: additional arguments to be used for rendering the template
        """
        role = role or Role.USER
        source = source or Source.INPUT
        super().__init__(template=template, role=role, source=source, format=format, tags=tags or [], extras=kwargs)

    def to_prompts(self, **kwargs: Dict[str, Any]) -> List[Prompt]:
        """Converts the PromptTemplate into a Prompt.

        Args:
            kwargs: all variables to be used for rendering the template

        Returns:
            Prompt: prompt generated from the template
        """
        all_args = {**self.extras, **kwargs}
        all_args = {k: v for k, v in all_args.items() if v is not None}
        if self.format == "fstring":
            return [Prompt(self.template.format(**all_args), role=self.role, source=self.source)]
        if self.format == "jinja2":
            template = Template(textwrap.dedent(self.template))
            result = template.render(**all_args)
            return [Prompt(result, role=self.role, source=self.source)]
        if self.format.startswith("bodhilib-"):
            return self._bodhilib_template_to_prompt(**all_args)
        raise ValueError(
            f"Unknown format {self.format}, "
            "allowed values: ['fstring', 'jinja2', 'bodhilib-fstring', 'bodhilib-jinja2']"
        )

    def _bodhilib_template_to_prompt(self, **kwargs: Dict[str, Any]) -> List[Prompt]:
        prompt_fields = ["text", "role", "source"]
        prompt_fields_matcher = "^" + "|".join(prompt_fields) + ":"
        lines = self.template.splitlines(keepends=True)
        result: List[Prompt] = []
        prompt: Dict[str, Any] = {"text": []}
        text_start = False
        for line in lines:
            if re.match(prompt_fields_matcher, line):
                field, value = line.split(":")
                if field == "text":
                    text_start = True
                    prompt["text"].append(value)
                else:
                    text_start = False
                    prompt[field] = value.strip()
                continue
            if line.startswith("---"):
                if not prompt["text"]:
                    text_start = False
                    prompt = {"text": []}
                    continue
                p = self._build_prompt(prompt, **kwargs)
                result.append(p)
                text_start = False
                prompt = {"text": []}
                continue
            if text_start:
                prompt["text"].append(line)
        if prompt["text"]:
            p = self._build_prompt(prompt, **kwargs)
            result.append(p)
        return result

    def _build_prompt(self, prompt: Dict[str, Any], **kwargs: Dict[str, Any]) -> Prompt:
        template = "".join(prompt.pop("text"))
        if self.format == "bodhilib-fstring":
            text = template.format(**kwargs)
        elif self.format == "bodhilib-jinja2":
            jinja_template = Template(template, keep_trailing_newline=True)
            text = jinja_template.render(**kwargs)
        else:
            raise ValueError("Unknown format {self.format}, allowed values: ['bodhilib-fstring', 'bodhilib-jinja2']")
        return Prompt(text, **prompt)


def prompt_with_examples(template: str, **kwargs: Dict[str, Any]) -> PromptTemplate:
    """Factory method to generate a prompt template with examples.

    Prompt uses `jinja2` template engine to generate prompt with examples.

    Args:
        template: a `jinja2` compliant template string to loop through examples
        **kwargs: additional arguments to be used for rendering the template.
            Can also contain `role` and `source` to override the default values.

    Returns:
        PromptTemplate: configured prompt template to generate prompt with examples
    """
    # pop role from kwargs or get None
    role = kwargs.pop("role", None)
    source = kwargs.pop("source", None)
    return PromptTemplate(template, role=role, source=source, format="jinja2", **kwargs)  # type: ignore


def prompt_with_extractive_qna(template: str, contexts: List[TextLike], **kwargs: Dict[str, Any]) -> PromptTemplate:
    """Factory method to generate a prompt template for extractive QnA.

    Args:
        template: a `jinja2` compliant template string to loop through examples
        **kwargs: additional arguments to be used for rendering the template.
            Can also contain `role` and `source` to override the default values.

    Returns:
        PromptTemplate: configured prompt template to generate prompt with examples
    """
    # pop role from kwargs or get None
    role = kwargs.pop("role", None)
    source = kwargs.pop("source", None)
    return PromptTemplate(
        template, role=role, source=source, format="jinja2", contexts=contexts, **kwargs  # type: ignore
    )


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
