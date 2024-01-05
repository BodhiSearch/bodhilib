from unittest.mock import Mock, patch
import pydantic

import pytest
from bodhiext.qdrant import Qdrant
from bodhilib import Distance, Node, VectorDBError
from qdrant_client.http.models import (
  CollectionDescription,
  Filter,
  PointStruct,
  ScoredPoint,
  UpdateResult,
  VectorParams,
)
from qdrant_client.http.models import Distance as QdrantDistance


@patch("qdrant_client.QdrantClient")
def test_qrant_ping(mock_client_class):
  mock_client = mock_client_class.return_value
  qdrant = Qdrant(client=mock_client)
  assert qdrant.ping() is True


@patch("qdrant_client.QdrantClient")
def test_qrant_connect(mock_client_class):
  mock_client = mock_client_class.return_value
  qdrant = Qdrant(client=mock_client)
  assert qdrant.connect() is True


@patch("qdrant_client.QdrantClient")
def test_qrant_close_calls_mock_client(mock_client_class):
  mock_client = mock_client_class.return_value
  mock_client.close.return_value = True
  qdrant = Qdrant(client=mock_client)
  assert qdrant.close() is True
  mock_client.close.assert_called_once()


@patch("qdrant_client.QdrantClient")
@pytest.mark.parametrize("error", [(ValueError("test error")), (RuntimeError("test error"))])
def test_qrant_close_raise_error(mock_client_class, error):
  mock_client = mock_client_class.return_value
  mock_client.close.side_effect = error
  qdrant = Qdrant(client=mock_client)
  with pytest.raises(VectorDBError) as e:
    qdrant.close()
  mock_client.close.assert_called_once()
  assert str(e.value) == "test error"


@patch("qdrant_client.QdrantClient")
def test_qdrant_get_collections_calls_client(mock_client_class):
  mock_client = mock_client_class.return_value
  mock_client.get_collections.return_value = Mock(
    collections=[
      _mock_collection("test_collection_1"),
      _mock_collection(name="test_collection_2"),
    ]
  )
  qdrant = Qdrant(client=mock_client)
  collections = qdrant.get_collections()
  assert collections == ["test_collection_1", "test_collection_2"]


@patch("qdrant_client.QdrantClient")
@pytest.mark.parametrize("error", [(ValueError("test error")), (RuntimeError("test error"))])
def test_qdrant_get_collections_raises_error(mock_client_class, error):
  mock_client = mock_client_class.return_value
  mock_client.get_collections.side_effect = error
  qdrant = Qdrant(client=mock_client)
  with pytest.raises(VectorDBError) as e:
    _ = qdrant.get_collections()
  assert str(e.value) == "test error"


@patch("qdrant_client.QdrantClient")
def test_qdrant_delete_collection_calls_client(mock_client_class):
  mock_client = mock_client_class.return_value
  mock_client.delete_collection.return_value = True
  qdrant = Qdrant(client=mock_client)
  result = qdrant.delete_collection("test_collection")
  assert result is True
  mock_client.delete_collection.assert_called_once_with("test_collection")


@patch("qdrant_client.QdrantClient")
@pytest.mark.parametrize("error", [(ValueError("test error")), (RuntimeError("test error"))])
def test_qdrant_delete_collections_raises_error(mock_client_class, error):
  mock_client = mock_client_class.return_value
  mock_client.delete_collection.side_effect = error
  qdrant = Qdrant(client=mock_client)
  with pytest.raises(VectorDBError) as e:
    _ = qdrant.delete_collection("test_collection")
  assert str(e.value) == "test error"


@patch("qdrant_client.QdrantClient")
@pytest.mark.parametrize(
  ["collection_name", "dimension", "distance", "qdistance", "expected_vector_params", "expected_kwargs", "kwargs"],
  [
    ("test_collection", 368, Distance.COSINE, QdrantDistance.COSINE, {}, {}, {}),
    ("test_collection", 368, "cosine", QdrantDistance.COSINE, {}, {}, {}),
    ("test_collection", 368, Distance.DOT_PRODUCT, QdrantDistance.DOT, {}, {}, {}),
    ("test_collection", 368, "dot_product", QdrantDistance.DOT, {}, {}, {}),
    ("test_collection", 368, Distance.EUCLIDEAN, QdrantDistance.EUCLID, {}, {}, {}),
    ("test_collection", 368, "euclidean", QdrantDistance.EUCLID, {}, {}, {}),
    (
      "test_collection",
      368,
      "euclidean",
      QdrantDistance.EUCLID,
      {"hnsw_config": {"m": 10}},
      {},
      {"hnsw_config": {"m": 10}},
    ),
    (
      "test_collection",
      368,
      "euclidean",
      QdrantDistance.EUCLID,
      {"hnsw_config": {"m": 10}},
      {"timeout": 10},
      {"hnsw_config": {"m": 10}, "timeout": 10},
    ),
  ],
)
def test_qdrant_create_collection_calls_client(
  mock_client_class, collection_name, dimension, distance, qdistance, expected_vector_params, expected_kwargs, kwargs
):
  mock_client = mock_client_class.return_value
  mock_client.create_collection.return_value = True
  qdrant = Qdrant(client=mock_client)
  result = qdrant.create_collection(collection_name, dimension, distance, **kwargs)
  assert result is True
  vector_params = VectorParams(size=dimension, distance=qdistance, **expected_vector_params)
  mock_client.create_collection.assert_called_once_with(
    collection_name, vectors_config=vector_params, **expected_kwargs
  )


@patch("qdrant_client.QdrantClient")
def test_qdrant_insert_calls_client(mock_client_class):
  mock_client = mock_client_class.return_value
  mock_client.upsert.return_value = UpdateResult(operation_id=1, status="acknowledged")
  qdrant = Qdrant(client=mock_client)
  nodes = [Node(id="1", text="test node", embedding=[1.0, 2.0, 3.0], metadata={"filename": "foo.txt"})]
  result = qdrant.upsert(
    "test_collection",
    nodes,
  )
  assert result == nodes
  mock_client.upsert.assert_called_once_with(
    "test_collection",
    points=[PointStruct(id="1", vector=[1.0, 2.0, 3.0], payload={"text": "test node", "filename": "foo.txt"})],
  )


@patch("qdrant_client.QdrantClient")
@pytest.mark.parametrize("error", [(ValueError("test error")), (RuntimeError("test error"))])
def test_qdrant_insert_raises_error(mock_client_class, error):
  mock_client = mock_client_class.return_value
  mock_client.upsert.side_effect = error
  qdrant = Qdrant(client=mock_client)
  with pytest.raises(VectorDBError) as e:
    _ = qdrant.upsert("test_collection", [Node(id="1", text="test node", embedding=[1.0, 2.0, 3.0])])
  assert str(e.value) == "test error"


@patch("qdrant_client.QdrantClient")
@pytest.mark.parametrize(
  ["collection_name", "docs_filter", "extra_args", "qdrant_filter", "expected_args"],
  [
    (
      "test_collection",
      {"filename": "foo.txt"},
      {},
      {"must": [{"key": "filename", "match": {"text": "foo.txt"}}]},
      {},
    ),
    (
      "test_collection",
      {"filename": "foo.txt"},
      {"page": "10"},
      {"must": [{"key": "filename", "match": {"text": "foo.txt"}}]},
      {"page": "10"},
    ),
    ("test_collection", {"age": {"$lt": 10}}, {}, {"must": [{"key": "age", "range": {"lt": 10}}]}, {}),
  ],
)
def test_qdrant_query_calls_client(
  mock_client_class, collection_name, docs_filter, extra_args, qdrant_filter, expected_args
):
  mock_client = mock_client_class.return_value
  stub_result = [
    ScoredPoint(
      id="1", version=1, score=0.1, payload={"text": "test node", "filename": "foo.txt"}, vector=[1.0, 2.0, 3.0]
    )
  ]
  mock_client.search.return_value = stub_result
  qdrant = Qdrant(client=mock_client)
  result = qdrant.query(collection_name, [1.0, 2.0, 3.0], docs_filter, **extra_args)
  assert result == [Node(id="1", text="test node", embedding=[1.0, 2.0, 3.0], metadata={"filename": "foo.txt"})]
  mock_client.search.assert_called_once_with(
    collection_name, [1.0, 2.0, 3.0], query_filter=Filter(**qdrant_filter), **expected_args
  )


def _mock_collection(name):
  with pytest.warns(pydantic.warnings.PydanticDeprecatedSince20):
    collection = Mock(spec=CollectionDescription)
    collection.configure_mock(name=name)
    return collection
