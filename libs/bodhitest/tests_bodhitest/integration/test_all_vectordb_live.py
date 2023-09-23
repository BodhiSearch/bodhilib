import pytest
from bodhilib import Node, VectorDB, get_vector_db

from tests_bodhitest.all_data import bodhiext_vector_dbs

TEST_COLLECTION = "test_collection"


@pytest.fixture
def vector_db_service(request) -> VectorDB:
    service_name = bodhiext_vector_dbs[request.param]["service_name"]
    service_class = bodhiext_vector_dbs[request.param]["service_class"]
    service = get_vector_db(service_name, oftype=service_class)
    service.delete_collection(collection_name=TEST_COLLECTION)
    return service


@pytest.mark.live
@pytest.mark.parametrize("vector_db_service", bodhiext_vector_dbs.keys(), indirect=True)
def test_all_vector_dbs_delete_create_and_get_collection(vector_db_service: VectorDB):
    result = vector_db_service.create_collection(TEST_COLLECTION, dimension=100, distance="cosine")
    assert result is True
    assert TEST_COLLECTION in vector_db_service.get_collections()


@pytest.mark.live
@pytest.mark.parametrize("vector_db_service", bodhiext_vector_dbs.keys(), indirect=True)
def test_all_vector_dbs_upsert_node(vector_db_service: VectorDB):
    vector_db_service.create_collection(TEST_COLLECTION, dimension=100, distance="cosine")
    nodes = [Node(id=None, embedding=[0.1, 0.2, 0.3, 0.4] * 25, text="test", metadata={"filename": "foo.txt"})]
    result = vector_db_service.upsert(TEST_COLLECTION, nodes)
    assert result is not None
    assert len(result) == 1
    assert result[0].id is not None


@pytest.mark.live
@pytest.mark.parametrize("vector_db_service", bodhiext_vector_dbs.keys(), indirect=True)
def test_all_vector_dbs_query(vector_db_service: VectorDB):
    vector_db_service.create_collection(TEST_COLLECTION, dimension=100, distance="cosine")
    nodes = [Node(id=None, embedding=[0.1, 0.2, 0.3, 0.4] * 25, text="test", metadata={"filename": "foo.txt"})]
    _ = vector_db_service.upsert(TEST_COLLECTION, nodes)

    result = vector_db_service.query(TEST_COLLECTION, [0.1, 0.2, 0.3, 0.4] * 25, limit=1)
    assert result is not None
    assert len(result) == 1
    assert result[0].id is not None
    assert result[0].text == "test"
    assert result[0].metadata["filename"] == "foo.txt"


@pytest.mark.live
@pytest.mark.parametrize("vector_db_service", bodhiext_vector_dbs.keys(), indirect=True)
def test_all_vector_dbs_query_filter(vector_db_service: VectorDB):
    vector_db_service.create_collection(TEST_COLLECTION, dimension=100, distance="cosine")
    foo = Node(id=None, embedding=[0.1, 0.2, 0.3, 0.4] * 25, text="test", metadata={"filename": "foo.txt"})
    bar = Node(id=None, embedding=[0.1, 0.2, 0.3, 0.4] * 25, text="test", metadata={"filename": "bar.txt"})
    nodes = [foo, bar]

    _ = vector_db_service.upsert(TEST_COLLECTION, nodes)

    result = vector_db_service.query(
        TEST_COLLECTION, [0.1, 0.2, 0.3, 0.4] * 25, filter={"filename": "bar.txt"}, limit=1
    )
    assert result is not None
    assert len(result) == 1
    assert result[0].id == bar.id
    assert result[0].text == "test"
    assert result[0].metadata["filename"] == "bar.txt"
