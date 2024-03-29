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
  TypeVar,
  Union,
  cast,
  no_type_check,
)

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import TypeAlias


# region type aliases
#######################################################################################################################
# Update the documentation in bodhilib.rst file directly. TypeAlias inline documentation not picked up by sphinx.
# Duplicating it here to make it easier when browsing the code.
class SupportsText(Protocol):
  """TextLike is a protocol for types that can be converted to text.

  To support the protocol, the type must have a property `text`.

  Known sub-classes: :class:`~bodhilib.Prompt`, :class:`~bodhilib.Document`, :class:`~bodhilib.Node`
  """

  @property
  def text(self) -> str:
    """Return the content of the object as string."""


ST = TypeVar("ST", bound=SupportsText)
PathLike: TypeAlias = Union[str, Path]
"""Type alias for Union of :class:`str` and :class:`~pathlib.Path`"""
TextLike: TypeAlias = Union[str, ST]
"""Type alias for Union of :class:`str` and protocol :data:`~bodhilib.SupportsText`"""
TextLikeOrTextLikeList: TypeAlias = Union[TextLike, Iterable[TextLike]]
"""Type alias for Union of :data:`~bodhilib.TextLike` or list of :data:`~bodhilib.TextLike`"""
SerializedInput: TypeAlias = Union[TextLikeOrTextLikeList, Dict[str, Any], Iterable[Dict[str, Any]]]
"""Type alias for various inputs that can be passed to the components."""
Embedding: TypeAlias = List[float]
"""Type alias for list of :class:`float`, to indicate the embedding generated
from :class:`~bodhilib.Embedder` operation"""


class SupportsEmbedding(Protocol):
  """SupportsEmbedding matches the types that contains a field `embedding` of type :data:`~bodhilib.Embedding`."""

  @property
  def embedding(self) -> Optional[Embedding]:
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
  @classmethod
  def membersstr(cls) -> List[str]:
    return [e.value for e in cls.__members__.values()]


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
  model_config = ConfigDict(use_enum_values=True)

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


class LLMApiConfig(BaseModel):
  """Configuration for LLM API calls."""

  api_base: Optional[str] = None
  """Base URL for the LLM API."""

  api_key: Optional[str] = None
  """API Key for the LLM API."""

  model_config = ConfigDict(extra="allow")


class LLMConfig(BaseModel):
  """Configuration for LLM generate call.

  Contains all the arguments that can be passed to LLM generate call.
  """

  model: Optional[str] = None
  """LLM model to use for generation."""

  stream: Optional[bool] = None
  """If the response is to be streamed, or returned as a single response.

    If True, returns a :class:`~bodhilib.PromptStream` object, else returns a :class:`~bodhilib.Prompt` object."""

  temperature: Optional[float] = None
  """Controls randomness in the generated response.

    Lower temperature results in less random completions. Ranges between 0-2."""

  top_p: Optional[float] = None
  """Token consideration probability."""

  top_k: Optional[int] = None
  """Number of tokens to consider for generation."""

  n: Optional[int] = None
  """Number of responses to generate."""

  stop: Optional[List[str]] = None
  """List of tokens to stop generation at."""

  max_tokens: Optional[int] = None
  """Maximum number of tokens to generate."""

  presence_penalty: Optional[float] = None
  """Controls the presence of words from the prompt in the generated response."""

  frequency_penalty: Optional[float] = None
  """Controls the frequency of words in the generated response."""

  logit_bias: Optional[Dict[int, float]] = None
  """Dictionary of token ids and their bias values."""

  seed: Optional[int] = None
  """Seed value for reproducible results."""

  user: Optional[str] = None
  """User identifier for the LLM service."""

  model_config = ConfigDict(extra="allow")


# endregion
# region resource
#######################################################################################################################
LOCAL_FILE = "local_file"
TEXT_PLAIN = "text/plain"
LOCAL_DIR = "local_dir"
GLOB = "glob"
URL = "url"
DOCUMENT = "document"
BODHILIB_RESOURCES = [LOCAL_FILE, LOCAL_DIR, GLOB, URL]
"""List of known resource types provided by bodhilib. This list is non-exhaustive."""


class IsResource(Protocol):
  """Protocol for Resource type."""

  @property
  def resource_type(self) -> str:
    """Returns the resource type."""

  @property
  def metadata(self) -> Dict[str, Any]:
    """Returns the metadata associated with the resource."""


class Resource(BaseModel):
  """Resource defines the basic interface for a processible resource.

  Primarily contains resource type and metadata.
  """

  resource_type: str
  """Type of the resource."""

  model_config = ConfigDict(extra="allow")

  @property
  def metadata(self) -> Dict[str, Any]:
    """Returns the metadata associated with the resource."""
    return self.model_dump()


def local_file(path: PathLike) -> Resource:
  """Factory method to generate a local file resource."""
  return Resource(resource_type=LOCAL_FILE, path=path)


def local_dir(path: PathLike, recursive: Optional[bool] = False, exclude_hidden: Optional[bool] = True) -> Resource:
  """Factory method to generate a local directory resource."""
  return Resource(resource_type=LOCAL_DIR, path=path, recursive=recursive, exclude_hidden=exclude_hidden)


def glob_pattern(
  path: str, pattern: str, recursive: Optional[bool] = False, exclude_hidden: Optional[bool] = False
) -> Resource:
  """Factory method to generate a local directory resource."""
  return Resource(resource_type=GLOB, path=path, pattern=pattern, recursive=recursive, exclude_hidden=exclude_hidden)


def url_resource(url: str) -> Resource:
  """Factory method to generate a url resource."""
  return Resource(resource_type=URL, path=url)


def text_plain_file(path: PathLike) -> Resource:
  """Factory method to generate a local txt file resource."""
  return Resource(resource_type=TEXT_PLAIN, path=path)


# endregion
# region document
#######################################################################################################################
class Document(Resource):
  """Document defines the basic interface for a processible resource.

  Primarily contains text (content) and metadata.
  """

  text: str
  """Text content of the document."""

  resource_type: str = DOCUMENT

  def __repr__(self) -> str:
    """Returns a string representation of the document."""
    all_but_text = {k: v for k, v in self.metadata.items() if k != "text"}
    return f"Document(text={reprlib.repr(self.text)}, metadata={reprlib.repr(all_but_text)})"


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
  elif isinstance(textlike, Resource):
    if not supportstext(textlike):
      raise ValueError(f"Resource of resource_type {textlike.resource_type} does not have property `text`")
    return Document(**textlike.metadata)
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
    return cast(str, textlike.text)
  raise ValueError(f"Cannot convert type {type(textlike)} to text.")


def to_embedding(embedding: Union[Embedding, Node, SupportsEmbedding]) -> Optional[Embedding]:
  if isinstance(embedding, Node):
    return cast(Node, embedding).embedding
  if supportsembedding(embedding):
    return cast(SupportsEmbedding, embedding).embedding
  elif isinstance(embedding, list) and all(isinstance(e, float) for e in embedding):
    return embedding
  raise ValueError(f"Cannot convert type {type(embedding)} to embedding.")


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
    return cast(List[Node], inputs)
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
