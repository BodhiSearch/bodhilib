from __future__ import annotations

import abc
from typing import Any, Dict, Iterable, Iterator, List, Optional, Type, TypeVar, Union, cast

from ._models import (
    Distance,
    Document,
    Embedding,
    Node,
    Prompt,
    PromptStream,
    PromptTemplate,
    SerializedInput,
    to_document_list,
    to_node_list,
)
from ._plugin import PluginManager, Service


# region prompt source
#######################################################################################################################
class PromptSource(abc.ABC):
    """Abstract base class for prompt sources.

    A prompt source provides a browsable/searchable interface for prompt templates.
    """

    @abc.abstractmethod
    def find(self, tags: Union[str, List[str]]) -> List[PromptTemplate]:
        """Find a prompt template for given tags.

        Args:
            tags (str | List[str]): list of tags to search for

        Returns:
            List[PromptTemplate]: list of prompt templates matching the tags
        """

    @abc.abstractmethod
    def list_all(self) -> List[PromptTemplate]:
        """List all prompt templates in the source.

        Returns:
            List[PromptTemplate]: list of all prompt templates in the source
        """


class BasePromptSource(PromptSource):
    """BasePromptSource provides a simpler method for implementing PromptSources.

    Class implementing :class:`~bodhilib.PromptSource` should extend this base class.
    In case the abstract method changes in :class:`~bodhilib.PromptSource`,
    this BaseClass tries to safely adapt new changes to old interface.
    """

    def find(self, tags: Union[str, List[str]]) -> List[PromptTemplate]:
        if isinstance(tags, str):
            tags = [tags]
        return self._find(tags)

    def list_all(self) -> List[PromptTemplate]:
        return self._list_all()

    @abc.abstractmethod
    def _find(self, tags: List[str]) -> List[PromptTemplate]:
        raise NotImplementedError(f"find method is not implemented by class {self.__class__.__name__}")

    @abc.abstractmethod
    def _list_all(self) -> List[PromptTemplate]:
        raise NotImplementedError(f"list_all method is not implemented by class {self.__class__.__name__}")


# endregion
# region data loader
#######################################################################################################################
class DataLoader(Iterable[Document], abc.ABC):
    """Abstract base class for data loaders.

    A data loader should inherit from this class and implement the abstract methods.
    """

    @abc.abstractmethod
    def add_resource(self, **kwargs: Dict[str, Any]) -> None:
        """Add a resource to the data loader."""

    @abc.abstractmethod
    def __iter__(self) -> Iterator[Document]:
        """Returns the document iterator.

        It is for the sub-class to ensure the `__iter__` method returns a new instance of iterator
        """

    def load(self) -> List[Document]:
        """Returns the document as list."""
        return list(self)


# endregion
# region splitter
#######################################################################################################################
class Splitter(abc.ABC):
    """Splitter defines abstract method to split longer text into shorter text.

    Splitter takes in longer text as a generic :data:`~bodhilib.TextLike`
    and splits them into shorter text and return as :class:`~bodhilib.Node`.
    The shorter text are then used to create embeddings.
    """

    @abc.abstractmethod
    def split(self, inputs: SerializedInput) -> List[Node]:
        """Split a :data:`~bodhilib.SerializedInput` into a list of :class:`~bodhilib.Node`.

        Args:
            inputs (:data:`~bodhilib.SerializedInput`): takes input as :data:`~bodhilib.SerializedInput`,
                a generic type that can be a :data:`~bodhilib.TextLike`, a list of :data:`~bodhilib.TextLike`,
                or a serialized dict of the object.

        Returns:
            List[:class:`~bodhilib.Node`]: a list of :class:`~bodhilib.Node` as result of the split
        """


class BaseSplitter(Splitter):
    """BaseSplitter provides a simpler method for implementing Splitters.

    BaseSplitter overrides the abstract Splitter method :func:`~bodhilib.Splitter.split`, massages the data
    and converts it to a list of :class:`~bodhilib.Document`
    and passes to implementing :func:`~bodhilib.BaseSplitter._split` method.
    """

    def split(self, inputs: SerializedInput) -> List[Node]:
        docs = to_document_list(inputs)
        return self._split(docs)

    @abc.abstractmethod
    def _split(self, docs: Iterable[Document]) -> List[Node]:
        """Split a list of :class:`~bodhilib.Document` into list of :class:`~bodhilib.Node`.

        The split method preserves the relationship and copies the metadata associated with Document to the Node.
        """


# endregion
# region embedder
#######################################################################################################################
class Embedder(abc.ABC):
    """Abstract base class for embedders.

    An embedder should inherit from this class and implement the abstract methods.
    """

    @abc.abstractmethod
    def embed(self, inputs: SerializedInput) -> List[Node]:
        """Embed a :data:`~bodhilib.SerializedInput` using the embedder service.

        Args:
            inputs (:data:`~bodhilib.SerializedInput`): takes input as :data:`~bodhilib.SerializedInput`,
                a generic type that can be a :data:`~bodhilib.TextLike`, a list of :data:`~bodhilib.TextLike`,
                or a serialized dict of the object.

        Returns:
            List[:data:`~bodhilib.Node`]: list of :data:`~bodhilib.Node` enriched with :data:`~bodhilib.Embedding`
        """

    @property
    @abc.abstractmethod
    def dimension(self) -> int:
        """Dimension of the embeddings."""


class BaseEmbedder(Embedder):
    """BaseEmbedder provides a simpler method for implementing Embedders.

    BaseEmbedder overrides the abstract Embedder method :func:`~bodhilib.Embedder.embed`,
    massages the data and converts the input to a list of :class:`~bodhilib.Node`,
    and passes to the abstract method to implement :func:`~bodhilib.BaseEmbedder._embed`.
    """

    def embed(self, inputs: SerializedInput) -> List[Node]:
        """Embed a :data:`~bodhilib.SerializedInput` using the embedder service.

        Massages the data and converts the input to a list of :class:`~bodhilib.Node`. Then passes to
        the :func:`~bodhilib.BaseEmbedder._embed` for processing.

        Args:
            inputs (:data:`~bodhilib.SerializedInput`): takes input as :data:`~bodhilib.SerializedInput`,
                a generic type that can be a :data:`~bodhilib.TextLike`, a list of :data:`~bodhilib.TextLike`,
                or a serialized dict of the object.

        Returns:
            List[:data:`~bodhilib.Node`]: list of :class:`~bodhilib.Node` enriched with :data:`~bodhilib.Embedding`
        """
        nodes = to_node_list(inputs)
        return self._embed(nodes)

    @abc.abstractmethod
    def _embed(self, nodes: List[Node]) -> List[Node]:
        """Embed a list of :class:`~bodhilib.Node` using the embedder service.

        Args:
            nodes (List[:class:`~bodhilib.Node`]): list of :class:`~bodhilib.Node` to embed

        Returns:
            List[:data:`~bodhilib.Node`]: list of :class:`~bodhilib.Node` enriched with :data:`~bodhilib.Embedding`
        """


# endregion
# region llm
#######################################################################################################################
class LLM(abc.ABC):
    """Abstract Base Class LLM defines the common interface implemented by all LLM implementations."""

    @abc.abstractmethod
    def generate(
        self,
        prompt_input: SerializedInput,
        *,
        stream: Optional[bool] = None,
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
    ) -> Union[Prompt, PromptStream]:
        """Base class :func:`~bodhilib.LLM.generate` method interface common to all LLM service implementation.

        Takes in :data:`bodhilib.SerializedInput`, a flexible input supporting from plain string,
        or a :class:`~bodhilib.Prompt` object, or a dict representation of Prompt.
        Returns the response from LLM service as :class:`~bodhilib.Prompt` object with `source="output"`.

        Args:
            prompts (:data:`bodhilib.SerializedInput`): input to the LLM service
            stream (bool): whether to stream the response from the LLM service
            temperature (Optional[float]): temperature or randomness of the generation
            top_p (Optional[float]): token consideration probability top_p for the generation
            top_k (Optional[int]): token consideration number top_k for the generation
            n (Optional[int]): number of responses to generate
            stop (Optional[List[str]]): list of stop tokens to stop the generation
            max_tokens (Optional[int]): maximum number of tokens to generate
            presence_penalty (Optional[float]): presence penalty for the generation, between -2 and 2
            frequency_penalty (Optional[float]): frequency penalty for the generation, between -2 and 2
            user (Optional[str]): user making the request, for monitoring purpose
            kwargs (Dict[str, Any]): pass through arguments for the LLM service

        Returns:
            :class:`~bodhilib.Prompt`: a Prompt object, if stream is False
            Iterator[:class:`~bodhilib.Prompt`]: an iterator of Prompt objects, if stream is True
        """


# endregion
# region vector db
#######################################################################################################################
class VectorDBError(Exception):
    """Error to wrap any exception raised by the vector database client."""


class VectorDB(abc.ABC):
    """VectorDB defines the interface for a vector database client."""

    @abc.abstractmethod
    def ping(self) -> bool:
        """Check the connection to the vector db.

        Returns:
            True if the database is up and running.

        Raises:
            VectorDBError: Wraps any connection error raised by the underlying database and raises.
        """

    @abc.abstractmethod
    def connect(self) -> bool:
        """Establishes a connection with the vector db.

        Returns:
            True if the connection with vector db is successful.

        Raises:
            VectorDBError: Wraps any connection error raised by the underlying database and raises.
        """

    @abc.abstractmethod
    def close(self) -> bool:
        """Closes the connection with the vector db.

        Returns:
            True if the connection with vector db is closed successfully.

        Raises:
            VectorDBError: Wraps any connection error raised by the underlying database and raises.
        """

    @abc.abstractmethod
    def get_collections(self) -> List[str]:
        """List all the vector databases.

        Returns:
            List of vector database names.

        Raises:
            VectorDBError: Wraps any database list error raised by the underlying database.
        """

    @abc.abstractmethod
    def create_collection(
        self,
        collection_name: str,
        dimension: int,
        distance: Union[str, Distance],
        **kwargs: Dict[str, Any],
    ) -> bool:
        """Create a collection in vector database.

        Returns:
            True if the database is created successfully.

        Raises:
            VectorDBError: Wraps any database create error raised by the underlying database.
        """

    @abc.abstractmethod
    def delete_collection(self, collection_name: str, **kwargs: Dict[str, Any]) -> bool:
        """Deletes a collection in vector database.

        Returns:
            True if the database is deleted successfully.

        Raises:
            VectorDBError: Wraps any database delete error raised by the underlying client.
        """

    @abc.abstractmethod
    def upsert(self, collection_name: str, nodes: List[Node]) -> List[Node]:
        """Insert or update a node into the database along with metadata.

        This updates the nodes with record ids and other DB information, similar to using an ORM.

        Returns:
            List of record ids for the inserted embeddings.

        Raises:
            VectorDBError: Wraps any database delete error raised by the underlying client.
        """

    @abc.abstractmethod
    def query(
        self, collection_name: str, embedding: Embedding, filter: Optional[Dict[str, Any]], **kwargs: Dict[str, Any]
    ) -> List[Node]:
        """Search for the nearest vectors in the database.

        Returns:
            List of nodes with metadata.

        Raises:
            VectorDBError: Wraps any database delete error raised by the underlying client.
        """


# endregion
# region plugin
#######################################################################################################################
# PromptSource
PS = TypeVar("PS", bound=PromptSource)
"""TypeVar for PromptSource."""


def get_prompt_source(
    service_name: str,
    *,
    oftype: Optional[Type[PS]] = None,
    publisher: Optional[str] = None,
    version: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> PS:
    """Get an instance of PromptSource for given arguments."""
    if oftype is None:
        return_type: Type[Any] = PromptSource
    else:
        return_type = oftype

    manager = PluginManager.instance()
    prompt_source: PS = manager.get(
        service_name=service_name,
        service_type="prompt_source",
        oftype=return_type,
        publisher=publisher,
        version=version,
        **kwargs,
    )
    return cast(PS, prompt_source)


# DataLoader
DL = TypeVar("DL", bound=DataLoader)
"""TypeVar for DataLoader."""


def get_data_loader(
    service_name: str,
    *,
    oftype: Optional[Type[DL]] = None,
    publisher: Optional[str] = None,
    version: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> DL:
    """Get an instance of data loader for given arguments.

    Given the service name, publisher (optional) and version(optional),
    return the registered data loader oftype (optional).

    Args:
        service_name (str): name of the service, e.g. "file", "notion", "s3"
        oftype (Optional[Type[T]]): if the type of data loader is known, pass the type in argument `oftype`,
            the data loader is cast to `oftype` and returned for better IDE support.
        publisher (Optional[str]): publisher or developer of the data loader plugin, e.g. "bodhilib","<github-username>"
        version (Optional[str]): version of the data loader
        **kwargs (Dict[str, Any]): pass through arguments for the data loader, e.g. aws_access_key_id, notion_db etc.

    Returns:
        DL (:data:`~bodhilib.DL` | :class:`~bodhilib.DataLoader`): an instance of DataLoader service
            of type `oftype`, if oftype is passed, else of type :class:`~bodhilib.DataLoader`

    Raises:
        TypeError: if the type of data loader is not oftype
    """
    if oftype is None:
        return_type: Type[Any] = DataLoader
    else:
        return_type = oftype

    manager = PluginManager.instance()
    data_loader: DL = manager.get(
        service_name=service_name,
        service_type="data_loader",
        oftype=return_type,
        publisher=publisher,
        version=version,
        **kwargs,
    )
    return cast(DL, data_loader)


def list_data_loaders() -> List[Service]:
    """List all data loaders installed and available."""
    manager = PluginManager.instance()
    return manager.list_services("data_loader")


# Splitter
S = TypeVar("S", bound=Splitter)
"""TypeVar for Splitter."""


def get_splitter(
    service_name: str,
    *,
    oftype: Optional[Type[S]] = None,
    publisher: Optional[str] = None,
    version: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> S:
    """Get an instance of splitter for given arguments.

    Returns:
        S (:data:`~bodhilib.S` | :class:`~bodhilib.Splitter`): an instance of Splitter service
    """
    if oftype is None:
        return_type: Type[Any] = Splitter
    else:
        return_type = oftype

    manager = PluginManager.instance()
    splitter: S = manager.get(
        service_name=service_name,
        service_type="splitter",
        oftype=return_type,
        publisher=publisher,
        version=version,
        **kwargs,
    )
    return cast(S, splitter)


# Embedder
E = TypeVar("E", bound=Embedder)
"""TypeVar for Embedder."""


def get_embedder(
    service_name: str,
    *,
    oftype: Optional[Type[E]] = None,
    publisher: Optional[str] = None,
    version: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> E:
    """Get an instance of embedder given the service name, publisher (optional) and version(optional).

    Args:
        service_name (str): name of the service, e.g. "sentence-transformers" etc.
        oftype (Optional[Type[T]]): if the type of embedder is known, pass the type in argument `oftype`,
            the embedder is cast to `oftype` and returned for better IDE support.
        publisher (Optional[str]): publisher or developer of the embedder plugin, e.g. "bodhilib","<github-username>"
        version (Optional[str]): version of the embedder
        **kwargs (Dict[str, Any]): pass through arguments for the embedder, e.g. dimension etc.

    Returns:
        E (:data:`~bodhilib.E` | :class:`~bodhilib.Embedder`): an instance of Embedder service
            of type `oftype`, if oftype is passed, else of type :class:`~bodhilib.Embedder`

    Raises:
        TypeError: if the type of embedder is not oftype
    """
    if oftype is None:
        return_type: Type[Any] = Embedder
    else:
        return_type = oftype

    manager = PluginManager.instance()
    embedder: E = manager.get(
        service_name, "embedder", oftype=return_type, publisher=publisher, version=version, **kwargs
    )
    return cast(E, embedder)


def list_embedders() -> List[Service]:
    """List all embedders installed and available."""
    manager = PluginManager.instance()
    return manager.list_services("embedder")


# LLM
L = TypeVar("L", bound=LLM)
"""TypeVar for LLM."""


def get_llm(
    service_name: str,
    model: str,
    api_key: Optional[str] = None,
    *,
    oftype: Optional[Type[L]] = None,
    publisher: Optional[str] = None,
    version: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> L:
    """Get an instance of LLM for the given service name and model.

    Args:
        service_name (str): name of the service, e.g. "openai", "cohere", "anthropic"
        model (str): name of the model, e.g. "chat-gpt-3.5", "command", "claude-2"
        api_key (Optional[str]): API key for the service, if the api_key is not provided,
            it will be looked in the environment variables
        oftype (Optional[Type[T]]): if the type of LLM is known, pass the type in argument `oftype`,
            the LLM is cast to `oftype` and returned for better IDE support.
        publisher (Optional[str]): publisher or developer of the service plugin, e.g. "bodhilib", "<github-username>"
        version (Optional[str]): version of the service
        **kwargs (Dict[str, Any]): pass through arguments for the LLM service, e.g. "temperature", "max_tokens", etc.

    Returns:
        T (:data:`~bodhilib.L` | :class:`~bodhilib.LLM`):
            an instance of LLM service of type `oftype`, if oftype is passed,
            else of type :class:`~bodhilib.LLM`

    Raises:
        TypeError: if the type of LLM is not oftype
    """
    if oftype is None:
        return_type: Type[Any] = LLM
    else:
        return_type = oftype

    manager = PluginManager.instance()
    llm: L = manager.get(
        service_name=service_name,
        service_type="llm",
        oftype=return_type,
        publisher=publisher,
        version=version,
        model=model,
        api_key=api_key,
        **kwargs,
    )
    return cast(L, llm)


def list_llms() -> List[Service]:
    """List all LLM services installed and available."""
    manager = PluginManager.instance()
    return manager.list_services("llm")


# VectorDB
V = TypeVar("V", bound=VectorDB)
"""TypeVar for VectorDB."""


def get_vector_db(
    service_name: str,
    *,
    oftype: Optional[Type[V]] = None,
    publisher: Optional[str] = None,
    version: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> V:
    """Get an instance of VectorDB for the given service name.

    Returns:
        V (:data:`~bodhilib.V` | :class:`~bodhilib.VectorDB`): an instance of VectorDB service
    """
    if oftype is None:
        return_type: Type[Any] = VectorDB
    else:
        return_type = oftype

    manager = PluginManager.instance()
    vector_db: V = manager.get(
        service_name=service_name,
        service_type="vector_db",
        oftype=return_type,
        publisher=publisher,
        version=version,
        **kwargs,
    )
    return cast(V, vector_db)


def list_vector_dbs() -> List[Service]:
    """List all VectorDB services installed and available."""
    manager = PluginManager.instance()
    return manager.list_services("vector_db")


# endregion
