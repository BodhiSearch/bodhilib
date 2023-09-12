import pytest
from bodhilib.models import Distance, Node
from bodhiext.qdrant import Qdrant
from qdrant_client import QdrantClient

# from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http import models

TEST_COLLECTION = "test_collection"
EMBEDDING = [1.0, 2.0, 3.0, 4.0] * 25


@pytest.fixture
def qdrant_local():
    client = QdrantClient(host="localhost", port=6333)
    collections = client.get_collections().collections
    [client.delete_collection(collection_name=c.name) for c in collections]
    _ = _create_collection(client, TEST_COLLECTION)
    qdrant = Qdrant(client=client)
    return qdrant


@pytest.fixture
def qdrant_mem():
    client = QdrantClient(location=":memory:")
    collections = client.get_collections().collections
    [client.delete_collection(collection_name=c.name) for c in collections]
    _ = _create_collection(client, TEST_COLLECTION)
    qdrant = Qdrant(client=client)
    return qdrant


@pytest.mark.live
@pytest.mark.parametrize("qdrant_fixture", ["qdrant_local", "qdrant_mem"])
def test_qdrant_get_collections(qdrant_fixture, request):
    qdrant_client: Qdrant = request.getfixturevalue(qdrant_fixture)
    collections = qdrant_client.get_collections()
    assert collections == [TEST_COLLECTION]


@pytest.mark.live
@pytest.mark.parametrize("qdrant_fixture", ["qdrant_local", "qdrant_mem"])
def test_qdrant_close(qdrant_fixture, request):
    qdrant_client: Qdrant = request.getfixturevalue(qdrant_fixture)
    result = qdrant_client.close()
    assert result is True


@pytest.mark.live
@pytest.mark.parametrize("qdrant_fixture", ["qdrant_local", "qdrant_mem"])
def test_qdrant_create_collection(qdrant_fixture, request):
    qdrant_client: Qdrant = request.getfixturevalue(qdrant_fixture)
    _delete_collection(qdrant_client.client, TEST_COLLECTION)
    result = qdrant_client.create_collection(collection_name=TEST_COLLECTION, dimension=100, distance=Distance.COSINE)
    assert result is True
    collection = qdrant_client.client.get_collection(collection_name=TEST_COLLECTION)
    assert collection is not None
    assert collection.config.params.vectors.size == 100
    assert collection.config.params.vectors.distance == models.Distance.COSINE


@pytest.mark.live
@pytest.mark.parametrize("qdrant_fixture", ["qdrant_local", "qdrant_mem"])
def test_qdrant_delete_collection(qdrant_fixture, request):
    qdrant_client: Qdrant = request.getfixturevalue(qdrant_fixture)
    result = qdrant_client.delete_collection(collection_name=TEST_COLLECTION)
    assert result is True


@pytest.mark.live
@pytest.mark.parametrize("qdrant_fixture", ["qdrant_local", "qdrant_mem"])
def test_qdrant_insert_node(qdrant_fixture, request):
    qdrant_client: Qdrant = request.getfixturevalue(qdrant_fixture)
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
@pytest.mark.parametrize("qdrant_fixture", ["qdrant_local", "qdrant_mem"])
def test_qdrant_query(qdrant_fixture, request):
    qdrant_client: Qdrant = request.getfixturevalue(qdrant_fixture)
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
    return client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=100, distance=models.Distance.COSINE),
    )


def _delete_collection(client: QdrantClient, collection_name: str):
    _ = client.delete_collection(collection_name=collection_name)


def _get_point(client: QdrantClient, collection_name: str, point_id: str):
    return client.retrieve(collection_name=collection_name, ids=[point_id])
