import abc
import typing
from typing import (
  Any,
  AsyncGenerator,
  AsyncIterator,
  Dict,
  Generator,
  Generic,
  Iterator,
  List,
  Literal,
  Optional,
  Type,
  TypeVar,
  Union,
)

from ._filter import Filter as Filter
from ._models import (
  Distance as Distance,
)
from ._models import (
  Document as Document,
)
from ._models import (
  Embedding as Embedding,
)
from ._models import (
  LLMApiConfig as LLMApiConfig,
)
from ._models import (
  LLMConfig as LLMConfig,
)
from ._models import (
  Node as Node,
)
from ._models import (
  Prompt as Prompt,
)
from ._models import (
  SerializedInput as SerializedInput,
)
from ._models import (
  SupportsEmbedding as SupportsEmbedding,
)
from ._models import (
  TextLike as TextLike,
)
from ._plugin import PluginManager as PluginManager
from ._plugin import Service as Service

class PromptTemplate(abc.ABC, metaclass=abc.ABCMeta):
  @property
  @abc.abstractmethod
  def template(self) -> str: ...
  @property
  @abc.abstractmethod
  def metadata(self) -> Dict[str, Any]: ...
  @property
  @abc.abstractmethod
  def vars(self) -> Dict[str, Type]: ...
  @property
  @abc.abstractmethod
  def format(self) -> str: ...
  @abc.abstractmethod
  def to_prompts(self, **kwargs: Dict[str, Any]) -> List[Prompt]: ...

class PromptSource(abc.ABC, metaclass=abc.ABCMeta):
  @typing.overload
  @abc.abstractmethod
  def find(self, filter: Filter, stream: Literal[False] = False) -> List[PromptTemplate]: ...
  @typing.overload
  @abc.abstractmethod
  def find(self, filter: Filter, stream: Literal[True]) -> Iterator[PromptTemplate]: ...
  @typing.overload
  @abc.abstractmethod
  def list_all(self, stream: Literal[False] = False) -> List[PromptTemplate]: ...
  @typing.overload
  @abc.abstractmethod
  def list_all(self, stream: Literal[True]) -> Iterator[PromptTemplate]: ...
  @abc.abstractmethod
  def find_by_id(self, id: str) -> Optional[PromptTemplate]: ...

class DataLoader(abc.ABC, metaclass=abc.ABCMeta):
  @abc.abstractmethod
  def add_resource(self, **kwargs: Dict[str, Any]) -> None: ...
  @abc.abstractmethod
  def pop(self) -> Generator[Document, None, None]: ...
  @abc.abstractmethod
  async def apop(self) -> AsyncGenerator[Document, None]: ...
  def load(self) -> List[Document]: ...

class Splitter(abc.ABC, metaclass=abc.ABCMeta):
  @typing.overload
  @abc.abstractmethod
  def split(self, inputs: SerializedInput, stream: None = None, astream: None = None) -> List[Node]: ...
  @typing.overload
  @abc.abstractmethod
  def split(self, inputs: SerializedInput, stream: Literal[True], astream: Optional[bool] = None) -> Iterator[Node]: ...
  @typing.overload
  @abc.abstractmethod
  def split(
    self,
    inputs: SerializedInput,
    astream: Literal[True],
    stream: None = None,
  ) -> AsyncIterator[Node]: ...

class Embedder(abc.ABC, metaclass=abc.ABCMeta):
  @typing.overload
  @abc.abstractmethod
  def embed(self, inputs: SerializedInput, stream: None = None, astream: None = None) -> List[Node]: ...
  @typing.overload
  @abc.abstractmethod
  def embed(self, inputs: SerializedInput, stream: Literal[True], astream: Optional[bool] = None) -> Iterator[Node]: ...
  @typing.overload
  @abc.abstractmethod
  def embed(
    self,
    inputs: SerializedInput,
    astream: Literal[True],
    stream: None = None,
  ) -> AsyncIterator[Node]: ...
  @property
  @abc.abstractmethod
  def dimension(self) -> int: ...
  @property
  def batch_size(self) -> int: ...

class LLM(abc.ABC, metaclass=abc.ABCMeta):
  @typing.overload
  @abc.abstractmethod
  def generate(
    self,
    prompts: SerializedInput,
    *,
    llm_config: Optional[LLMConfig] = None,
    stream: None = None,
    astream: None = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    n: Optional[int] = None,
    stop: Optional[List[str]] = None,
    max_tokens: Optional[int] = None,
    presence_penalty: Optional[float] = None,
    frequency_penalty: Optional[float] = None,
    user: Optional[str] = None,
    **kwargs: Dict[str, Any],
  ) -> Prompt: ...
  @typing.overload
  @abc.abstractmethod
  def generate(
    self,
    prompts: SerializedInput,
    *,
    llm_config: Optional[LLMConfig] = None,
    stream: Literal[True],
    astream: Optional[bool] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    n: Optional[int] = None,
    stop: Optional[List[str]] = None,
    max_tokens: Optional[int] = None,
    presence_penalty: Optional[float] = None,
    frequency_penalty: Optional[float] = None,
    user: Optional[str] = None,
    **kwargs: Dict[str, Any],
  ) -> Iterator[Prompt]: ...
  @typing.overload
  @abc.abstractmethod
  def generate(
    self,
    prompts: SerializedInput,
    *,
    llm_config: Optional[LLMConfig] = None,
    stream: None = None,
    astream: Literal[True],
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    n: Optional[int] = None,
    stop: Optional[List[str]] = None,
    max_tokens: Optional[int] = None,
    presence_penalty: Optional[float] = None,
    frequency_penalty: Optional[float] = None,
    user: Optional[str] = None,
    **kwargs: Dict[str, Any],
  ) -> AsyncIterator[Prompt]: ...

class VectorDBError(Exception): ...

class VectorDB(abc.ABC, metaclass=abc.ABCMeta):
  @abc.abstractmethod
  def ping(self) -> bool: ...
  @abc.abstractmethod
  def connect(self) -> bool: ...
  @abc.abstractmethod
  def close(self) -> bool: ...
  @abc.abstractmethod
  def get_collections(self) -> List[str]: ...
  @abc.abstractmethod
  def create_collection(
    self, collection_name: str, dimension: int, distance: Union[str, Distance], **kwargs: Dict[str, Any]
  ) -> bool: ...
  @abc.abstractmethod
  def delete_collection(self, collection_name: str, **kwargs: Dict[str, Any]) -> bool: ...
  @abc.abstractmethod
  def upsert(self, collection_name: str, nodes: List[Node]) -> List[Node]: ...
  @abc.abstractmethod
  async def aupsert(self, collection_name: str, nodes: List[Node]) -> List[Node]: ...
  @abc.abstractmethod
  def query(
    self,
    collection_name: str,
    embedding: Union[Embedding, SupportsEmbedding],
    filter: Optional[Union[Dict[str, Any], Filter]] = None,
    **kwargs: Dict[str, Any],
  ) -> List[Node]: ...

SSE = TypeVar("SSE", bound="SemanticSearchEngine")

class SemanticSearchEngine(abc.ABC, Generic[SSE], metaclass=abc.ABCMeta):
  @abc.abstractmethod
  def add_resource(self, **kwargs: Dict[str, Any]) -> SSE: ...
  @abc.abstractmethod
  def delete_collection(self) -> bool: ...
  @abc.abstractmethod
  def create_collection(self) -> bool: ...
  @abc.abstractmethod
  def ingest(self) -> None: ...
  @abc.abstractmethod
  async def aingest(self) -> None: ...
  @typing.overload
  @abc.abstractmethod
  def ann(self, query: TextLike, astream: None = None, n: Optional[int] = 5) -> List[Node]: ...
  @typing.overload
  @abc.abstractmethod
  def ann(self, query: TextLike, astream: Literal[True], n: Optional[int] = 5) -> AsyncIterator[List[Node]]: ...
  @typing.overload
  @abc.abstractmethod
  def rag(self, query: TextLike, prompt_template: Optional[PromptTemplate] = None, astream: None = None) -> Prompt: ...
  @typing.overload
  @abc.abstractmethod
  def rag(
    self, query: TextLike, astream: Literal[True], prompt_template: Optional[PromptTemplate] = None
  ) -> AsyncIterator[Prompt]: ...

PS = TypeVar("PS", bound=PromptSource)

def list_prompt_sources() -> List[Service]: ...
def get_prompt_source(
  service_name: str,
  *,
  oftype: Optional[Type[PS]] = None,
  publisher: Optional[str] = "bodhiext",
  version: Optional[str] = None,
  **kwargs: Dict[str, Any],
) -> PS: ...

DL = TypeVar("DL", bound=DataLoader)

def get_data_loader(
  service_name: str,
  *,
  oftype: Optional[Type[DL]] = None,
  publisher: Optional[str] = None,
  version: Optional[str] = None,
  **kwargs: Dict[str, Any],
) -> DL: ...
def list_data_loaders() -> List[Service]: ...

S = TypeVar("S", bound=Splitter)

def list_splitters() -> List[Service]: ...
def get_splitter(
  service_name: str,
  *,
  oftype: Optional[Type[S]] = None,
  publisher: Optional[str] = None,
  version: Optional[str] = None,
  **kwargs: Dict[str, Any],
) -> S: ...

E = TypeVar("E", bound=Embedder)

def get_embedder(
  service_name: str,
  *,
  oftype: Optional[Type[E]] = None,
  publisher: Optional[str] = None,
  version: Optional[str] = None,
  **kwargs: Dict[str, Any],
) -> E: ...
def list_embedders() -> List[Service]: ...

L = TypeVar("L", bound=LLM)

def get_llm(
  service_name: str,
  model: Optional[str] = None,
  api_key: Optional[str] = None,
  *,
  oftype: Optional[Type[L]] = None,
  publisher: Optional[str] = None,
  version: Optional[str] = None,
  api_config: Optional[LLMApiConfig] = None,
  llm_config: Optional[LLMConfig] = None,
  **kwargs: Dict[str, Any],
) -> L: ...
def list_llms() -> List[Service]: ...

V = TypeVar("V", bound=VectorDB)

def get_vector_db(
  service_name: str,
  *,
  oftype: Optional[Type[V]] = None,
  publisher: Optional[str] = None,
  version: Optional[str] = None,
  **kwargs: Dict[str, Any],
) -> V: ...
def list_vector_dbs() -> List[Service]: ...
