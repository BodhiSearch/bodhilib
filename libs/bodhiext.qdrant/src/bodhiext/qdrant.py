""":mod:`bodhiext.qdrant` module defines classes and methods for Qdrant Vector Database related operations."""
import uuid
from typing import Any, Dict, List, Optional, Union

from bodhilib import Distance, Embedding, Node, Service, VectorDB, VectorDBError, service_provider

# TODO: Once the module is separate, import this from the extension version file
from bodhilib import __version__ as bodhilib_version
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance as QdrantDistance
from qdrant_client.http.models import Filter, PointStruct, ScoredPoint, VectorParams

__version__ = bodhilib_version

_qdrant_distance_mapping = {
    Distance.COSINE.value: QdrantDistance.COSINE,
    Distance.DOT_PRODUCT.value: QdrantDistance.DOT,
    Distance.EUCLIDEAN.value: QdrantDistance.EUCLID,
}


class Qdrant(VectorDB):
    """Qdrant wraps the QdrantClient to provide a VectorDB interface."""

    def __init__(
        self,
        *,
        client: Optional[QdrantClient] = None,
        location: Optional[str] = None,
        url: Optional[str] = None,
        port: Optional[int] = 6333,
        grpc_port: int = 6334,
        prefer_grpc: Optional[bool] = False,
        https: Optional[bool] = None,
        api_key: Optional[str] = None,
        prefix: Optional[str] = None,
        timeout: Optional[float] = None,
        host: Optional[str] = None,
        path: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ) -> None:
        """Mimics the QdrantClient interface.

        Raises:
            VectorDBError: Wraps any connection error raised by the underlying database and raises.
        """
        if client:
            self.client = client
            return
        try:
            args = {
                "location": location,
                "url": url,
                "port": port,
                "grpc_port": grpc_port,
                "prefer_grpc": prefer_grpc,
                "https": https,
                "api_key": api_key,
                "prefix": prefix,
                "timeout": timeout,
                "host": host,
                "path": path,
                **kwargs,
            }
            args = {key: value for key, value in args.items() if value is not None}
            self.client = QdrantClient(**args)
        except (ValueError, RuntimeError) as e:
            raise VectorDBError(e) from e

    def ping(self) -> bool:
        return True

    def connect(self) -> bool:
        return True

    def close(self) -> bool:
        try:
            self.client.close()
            return True
        except (RuntimeError, ValueError) as e:
            raise VectorDBError(e) from e

    def get_collections(self) -> List[str]:
        try:
            collections = self.client.get_collections().collections
            names = [collection.name for collection in collections]
            return names
        except (ValueError, RuntimeError) as e:
            raise VectorDBError(e) from e

    def create_collection(
        self, collection_name: str, dimension: int, distance: Union[str, Distance], **kwargs: Dict[str, Any]
    ) -> bool:
        if not collection_name:
            raise VectorDBError(ValueError("Collection name cannot be empty"))
        if not dimension or dimension < 0:
            raise VectorDBError(ValueError("`dimension` cannot be empty"))
        if not distance:
            raise VectorDBError(ValueError("`distance` cannot be empty"))
        if str(distance) not in Distance.membersstr():
            raise VectorDBError(ValueError(f"Invalid distance: {distance}, valid values are {Distance.membersstr()}"))
        qdrant_distance = _qdrant_distance_mapping[str(distance)]
        params = {
            key: value for key, value in kwargs.items() if key in ["hnsw_config", "quantization_config", "on_disk"]
        }
        other_params = {
            key: value for key, value in kwargs.items() if key not in ["hnsw_config", "quantization_config", "on_disk"]
        }
        vector_config = VectorParams(size=dimension, distance=qdrant_distance, **params)
        try:
            result: bool = self.client.create_collection(collection_name, vectors_config=vector_config, **other_params)
            return result
        except (ValueError, RuntimeError) as e:
            raise VectorDBError(e) from e

    def delete_collection(self, collection_name: str, **kwargs: Dict[str, Any]) -> bool:
        try:
            result: bool = self.client.delete_collection(collection_name, **kwargs)
            return result
        except (ValueError, RuntimeError) as e:
            raise VectorDBError(e) from e

    def upsert(self, collection_name: str, nodes: List[Node]) -> List[Node]:
        try:
            for node in nodes:
                if node.id is None:
                    node.id = str(uuid.uuid4())

            points: List[PointStruct] = [
                PointStruct(id=node.id, vector=node.embedding, payload={"text": node.text, **node.metadata})
                for node in nodes
            ]
            _ = self.client.upsert(collection_name, points=points)
            return nodes
        except (ValueError, RuntimeError) as e:
            raise VectorDBError(e) from e

    def query(
        self,
        collection_name: str,
        embedding: Embedding,
        filter: Optional[Dict[str, Any]] = None,
        **kwargs: Dict[str, Any],
    ) -> List[Node]:
        try:
            if filter:
                qdrant_filter = _mongodb_to_qdrant_filter(filter)
                query_filter = Filter(**qdrant_filter)
            else:
                query_filter = None
            results = self.client.search(collection_name, embedding, query_filter=query_filter, **kwargs)
            return _to_nodes(results)
        except (ValueError, RuntimeError) as e:
            raise VectorDBError(e) from e


def qdrant_service_builder(
    *,
    service_name: Optional[str] = None,
    service_type: Optional[str] = None,
    publisher: Optional[str] = None,  # QdrantClient fails if passed extra args
    version: Optional[str] = None,  # QdrantClient fails if passed extra args
    client: Optional[QdrantClient] = None,
    url: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: Optional[float] = None,
    **kwargs: Dict[str, Any],
) -> Qdrant:
    """Returns an QDrant client instance.

    Lists only most used args required by Qdrant DB.
    """
    if service_name != "qdrant":
        raise ValueError(f"Unknown service: {service_name=}")
    if service_type != "vector_db":
        raise ValueError(f"Service type not supported: {service_type=}, supported service types: 'vector_db'")
    service_args: Dict[str, Any] = {
        "client": client,
        "url": url,
        "api_key": api_key,
        "timeout": timeout,
        **kwargs,
    }
    # TODO filter invalid args, only pass args recognized by QdrantClient
    return Qdrant(**service_args)


@service_provider
def bodhilib_list_services() -> List[Service]:
    """Returns a list of services supported by the plugin.

    Current supports vector_db service.
    """
    return [
        Service(
            service_name="qdrant",
            service_type="vector_db",
            publisher="bodhiext",
            service_builder=qdrant_service_builder,
            version=__version__,
        )
    ]


def _match(value: Any) -> Dict[str, Any]:
    if isinstance(value, (bool, int)):
        return {"value": value}
    if isinstance(value, str):
        return {"text": value}
    raise ValueError(f"Invalid type: {type(value)}")


def _mongodb_to_qdrant_filter(mongo_filter: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    qdrant_filter: Dict[str, Any] = {}
    if not mongo_filter:
        return qdrant_filter
    must_conditions: List[Dict[str, Any]] = []
    should_conditions: List[Dict[str, Any]] = []
    must_not_conditions: List[Dict[str, Any]] = []

    for key, value in mongo_filter.items():
        # Direct equal condition
        if isinstance(value, (bool, int, str)):
            must_conditions.append({"key": key, "match": _match(value)})

        # Special MongoDB conditions
        elif isinstance(value, dict):
            condition: Dict[str, Any] = {"key": key}
            if "$eq" in value:
                condition["match"] = _match(value["$eq"])
                must_conditions.append(condition)
            elif "$ne" in value:
                condition["match"] = _match(value["$ne"])
                must_not_conditions.append(condition)
            elif "$in" in value:
                for v in value["$in"]:
                    should_conditions.append({"key": key, "match": _match(v)})
            elif "$nin" in value:
                for v in value["$nin"]:
                    must_not_conditions.append({"key": key, "match": _match(v)})
            else:
                range_condition = {}
                if "$gt" in value:
                    range_condition["gt"] = value["$gt"]
                if "$gte" in value:
                    range_condition["gte"] = value["$gte"]
                if "$lt" in value:
                    range_condition["lt"] = value["$lt"]
                if "$lte" in value:
                    range_condition["lte"] = value["$lte"]
                if range_condition:
                    condition["range"] = range_condition
                    must_conditions.append(condition)

    if must_conditions:
        qdrant_filter["must"] = must_conditions
    if should_conditions:
        qdrant_filter["should"] = should_conditions
    if must_not_conditions:
        qdrant_filter["must_not"] = must_not_conditions

    return qdrant_filter


def _to_nodes(results: List[ScoredPoint]) -> List[Node]:
    nodes: List[Node] = []
    for result in results:
        text = result.payload.pop("text", "")
        node = Node(
            id=result.id,
            text=text,
            embedding=result.vector,
            metadata=result.payload,
        )
        nodes.append(node)
    return nodes
