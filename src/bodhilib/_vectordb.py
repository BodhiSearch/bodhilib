import abc
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast

from bodhilib.models import Distance, Embedding, Node

from ._plugin import PluginManager


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


T = TypeVar("T", bound=VectorDB)
"""TypeVar for VectorDB."""


def get_vector_db(
    service_name: str,
    *,
    oftype: Optional[Type[T]] = None,
    publisher: Optional[str] = None,
    version: Optional[str] = None,
    **kwargs: Dict[str, Any],
) -> T:
    """Get an instance of VectorDB for the given service name."""
    if oftype is None:
        return_type: Type[Any] = VectorDB
    else:
        return_type = oftype

    manager = PluginManager.instance()
    vectordb: T = manager.get(
        service_name=service_name,
        service_type="vector_db",
        oftype=return_type,
        publisher=publisher,
        version=version,
        **kwargs,
    )
    return cast(T, vectordb)
