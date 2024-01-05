from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Protocol, TypeVar, Union

from _typeshed import Incomplete
from pydantic import BaseModel
from typing_extensions import TypeAlias

PathLike: TypeAlias = Union[str, Path]
TextLike: TypeAlias = Union[str, "SupportsText"]
TextLikeOrTextLikeList: TypeAlias = Union[TextLike, Iterable[TextLike]]
SerializedInput: TypeAlias = Union[TextLikeOrTextLikeList, Dict[str, Any], Iterable[Dict[str, Any]]]
Embedding: TypeAlias = List[float]

class SupportsText(Protocol):
  @property
  def text(self) -> str: ...

class SupportsEmbedding(Protocol):
  @property
  def embedding(self) -> Embedding: ...

def supportstext(obj: object) -> bool: ...
def istextlike(obj: object) -> bool: ...
def supportsembedding(obj: object) -> bool: ...

class _StrEnumMixin:
  @classmethod
  def membersstr(cls) -> List[str]: ...

class Role(_StrEnumMixin, str, Enum):
  SYSTEM: str
  AI: str
  USER: str

class Source(_StrEnumMixin, str, Enum):
  INPUT: str
  OUTPUT: str

class Distance(_StrEnumMixin, str, Enum):
  COSINE: str
  EUCLIDEAN: str
  DOT_PRODUCT: str

class Prompt(BaseModel):
  role: Role
  source: Source
  text: str
  def __init__(
    self, text: str, role: Optional[Union[Role, str]] = ..., source: Optional[Union[Source, str]] = ...
  ) -> None: ...
  def isstream(self) -> bool: ...

T = TypeVar("T")

class PromptStream(Iterator[Prompt]):
  api_response: Incomplete
  transformer: Incomplete
  output: Incomplete
  role: Incomplete
  def __init__(self, api_response: Iterable[T], transformer: Callable[[T], Prompt]) -> None: ...
  def __iter__(self) -> Iterator[Prompt]: ...
  def __next__(self) -> Prompt: ...
  def isstream(self) -> bool: ...
  @property
  def text(self) -> str: ...

def prompt_user(text: str) -> Prompt: ...
def prompt_system(text: str) -> Prompt: ...
def prompt_output(text: str) -> Prompt: ...

class LLMApiConfig(BaseModel):
  api_base: Optional[str]
  api_key: Optional[str]

class LLMConfig(BaseModel):
  model: Optional[str]
  stream: Optional[bool]
  temperature: Optional[float]
  top_p: Optional[float]
  top_k: Optional[int]
  n: Optional[int]
  stop: Optional[List[str]]
  max_tokens: Optional[int]
  presence_penalty: Optional[float]
  frequency_penalty: Optional[float]
  logit_bias: Optional[Dict[int, float]]
  seed: Optional[int]
  user: Optional[str]

class Document(BaseModel):
  text: str
  metadata: Dict[str, Any]

class Node(BaseModel):
  id: Optional[str]
  text: str
  parent: Optional[Document]
  metadata: Dict[str, Any]
  embedding: Optional[Embedding]

def to_document(textlike: TextLike) -> Document: ...
def to_prompt(textlike: TextLike) -> Prompt: ...
def to_node(textlike: TextLike) -> Node: ...
def to_text(textlike: TextLike) -> str: ...
def to_embedding(embedding: Union[Embedding, SupportsEmbedding]) -> Embedding: ...
def to_prompt_list(inputs: SerializedInput) -> List[Prompt]: ...
def to_document_list(inputs: SerializedInput) -> List[Document]: ...
def to_node_list(inputs: SerializedInput) -> List[Node]: ...
