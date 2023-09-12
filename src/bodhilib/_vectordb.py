import abc
from typing import Any, Dict, List, Optional, Union

from bodhilib.models import Distance, Node


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
        self, collection_name: str, embedding: List[float], filter: Optional[Dict[str, Any]], **kwargs: Dict[str, Any]
    ) -> List[Node]:
        """Search for the nearest vectors in the database.

        Returns:
            List of nodes with metadata.

        Raises:
            VectorDBError: Wraps any database delete error raised by the underlying client.
        """
