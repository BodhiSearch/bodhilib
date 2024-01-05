import pytest
from bodhiext.qdrant import Qdrant
from bodhilib import Distance, Node
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import VectorParams, Distance as D

TEST_COLLECTION = "test_collection"
EMBEDDING = [1.0, 2.0, 3.0, 4.0] * 25


def qdrant_local():
  client = QdrantClient(host="localhost", port=6333)
  collections = client.get_collections().collections
  [client.delete_collection(collection_name=c.name) for c in collections]
  _ = _create_collection(client, TEST_COLLECTION)
  qdrant = Qdrant(client=client)
  return qdrant


def qdrant_mem():
  client = QdrantClient(location=":memory:")
  collections = client.get_collections().collections
  [client.delete_collection(collection_name=c.name) for c in collections]
  _ = _create_collection(client, TEST_COLLECTION)
  qdrant = Qdrant(client=client)
  return qdrant


@pytest.fixture
def qdrant_client(request):
  if request.param == "qdrant_local":
    return qdrant_local()
  elif request.param == "qdrant_mem":
    return qdrant_mem()
  else:
    raise ValueError(f"Unknown fixture {request.param}")


@pytest.mark.live
@pytest.mark.parametrize("qdrant_client", ["qdrant_local", "qdrant_mem"], indirect=True)
def test_qdrant_get_collections(qdrant_client):
  collections = qdrant_client.get_collections()
  assert collections == [TEST_COLLECTION]


@pytest.mark.live
@pytest.mark.parametrize("qdrant_client", ["qdrant_local", "qdrant_mem"], indirect=True)
def test_qdrant_close(qdrant_client):
  result = qdrant_client.close()
  assert result is True


@pytest.mark.live
@pytest.mark.parametrize("qdrant_client", ["qdrant_local", "qdrant_mem"], indirect=True)
def test_qdrant_create_collection(qdrant_client):
  _delete_collection(qdrant_client.client, TEST_COLLECTION)
  result = qdrant_client.create_collection(collection_name=TEST_COLLECTION, dimension=100, distance=Distance.COSINE)
  assert result is True
  collection = qdrant_client.client.get_collection(collection_name=TEST_COLLECTION)
  assert collection is not None
  assert collection.config.params.vectors.size == 100
  assert collection.config.params.vectors.distance == models.Distance.COSINE


@pytest.mark.live
@pytest.mark.parametrize("qdrant_client", ["qdrant_local", "qdrant_mem"], indirect=True)
def test_qdrant_delete_collection(qdrant_client):
  result = qdrant_client.delete_collection(collection_name=TEST_COLLECTION)
  assert result is True


@pytest.mark.live
@pytest.mark.parametrize("qdrant_client", ["qdrant_local", "qdrant_mem"], indirect=True)
def test_qdrant_insert_node(qdrant_client):
  nodes = [Node(id=None, embedding=EMBEDDING, text="test", metadata={"filename": "foo.txt"})]
  result = qdrant_client.upsert(TEST_COLLECTION, nodes)
  assert result is not None
  assert len(result) == 1
  assert result[0].id is not None
  points = _get_point(qdrant_client.client, TEST_COLLECTION, result[0].id)
  assert points is not None
  assert len(points) == 1
  assert points[0].id == result[0].id
  assert points[0].payload["text"] == "test"
  assert points[0].payload["filename"] == "foo.txt"


@pytest.mark.live
@pytest.mark.parametrize("qdrant_client", ["qdrant_local", "qdrant_mem"], indirect=True)
def test_qdrant_query(qdrant_client):
  foo = Node(id=None, embedding=EMBEDDING, text="foo", metadata={"filename": "foo.txt"})
  bar = Node(id=None, embedding=EMBEDDING, text="bar", metadata={"filename": "bar.txt"})
  nodes = [
    foo,
    bar,
  ]
  qdrant_client.upsert(TEST_COLLECTION, nodes)
  result = qdrant_client.query(TEST_COLLECTION, EMBEDDING, filter={"filename": "bar.txt"})
  assert len(result) == 1
  assert result[0].id == bar.id


def _create_collection(client: QdrantClient, collection_name: str):
  return client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=100, distance=D.COSINE),
  )


def _delete_collection(client: QdrantClient, collection_name: str):
  _ = client.delete_collection(collection_name=collection_name)


def _get_point(client: QdrantClient, collection_name: str, point_id: str):
  return client.retrieve(collection_name=collection_name, ids=[point_id])
