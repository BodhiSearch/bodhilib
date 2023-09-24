from bodhiext.qdrant import _mongodb_to_qdrant_filter
from qdrant_client.http.models import Filter


def test_qdrant_filter_eq_str():
    mongo_filter = {"name": "John"}
    qdrant_filter = _mongodb_to_qdrant_filter(mongo_filter)
    assert qdrant_filter == {"must": [{"key": "name", "match": {"text": "John"}}]}
    _ = Filter(**qdrant_filter)


def test_qdrant_filter_eq_bool():
    mongo_filter = {"admin": True}
    qdrant_filter = _mongodb_to_qdrant_filter(mongo_filter)
    assert qdrant_filter == {"must": [{"key": "admin", "match": {"value": True}}]}
    _ = Filter(**qdrant_filter)


def test_qdrant_filter_eq_int():
    mongo_filter = {"age": 25}
    qdrant_filter = _mongodb_to_qdrant_filter(mongo_filter)
    assert qdrant_filter == {"must": [{"key": "age", "match": {"value": 25}}]}
    _ = Filter(**qdrant_filter)


def test_qdrant_filter_neq():
    mongo_filter = {"name": {"$ne": "John"}}
    qdrant_filter = _mongodb_to_qdrant_filter(mongo_filter)
    assert qdrant_filter == {"must_not": [{"key": "name", "match": {"text": "John"}}]}
    _ = Filter(**qdrant_filter)


def test_qdrant_filter_in():
    mongo_filter = {"name": {"$in": ["John", "Jane"]}}
    qdrant_filter = _mongodb_to_qdrant_filter(mongo_filter)
    assert qdrant_filter == {
        "should": [{"key": "name", "match": {"text": "John"}}, {"key": "name", "match": {"text": "Jane"}}]
    }
    _ = Filter(**qdrant_filter)


def test_qdrant_filter_not_in():
    mongo_filter = {"name": {"$nin": ["John", "Jane"]}}
    qdrant_filter = _mongodb_to_qdrant_filter(mongo_filter)
    assert qdrant_filter == {
        "must_not": [{"key": "name", "match": {"text": "John"}}, {"key": "name", "match": {"text": "Jane"}}]
    }
    _ = Filter(**qdrant_filter)


def test_qdrant_filter_gt():
    mongo_filter = {"age": {"$gt": "30"}}
    qdrant_filter = _mongodb_to_qdrant_filter(mongo_filter)
    assert qdrant_filter == {"must": [{"key": "age", "range": {"gt": "30"}}]}
    _ = Filter(**qdrant_filter)


def test_qdrant_filter_gte():
    mongo_filter = {"age": {"$gte": "30"}}
    qdrant_filter = _mongodb_to_qdrant_filter(mongo_filter)
    assert qdrant_filter == {"must": [{"key": "age", "range": {"gte": "30"}}]}
    _ = Filter(**qdrant_filter)


def test_qdrant_filter_lt():
    mongo_filter = {"age": {"$lt": "30"}}
    qdrant_filter = _mongodb_to_qdrant_filter(mongo_filter)
    assert qdrant_filter == {"must": [{"key": "age", "range": {"lt": "30"}}]}
    _ = Filter(**qdrant_filter)


def test_qdrant_filter_lte():
    mongo_filter = {"age": {"$lte": "30"}}
    qdrant_filter = _mongodb_to_qdrant_filter(mongo_filter)
    assert qdrant_filter == {"must": [{"key": "age", "range": {"lte": "30"}}]}
    _ = Filter(**qdrant_filter)


def test_qdrant_filter_combine_must():
    mongo_filter = {"age": {"$lte": "30"}, "name": {"$eq": "John"}}
    qdrant_filter = _mongodb_to_qdrant_filter(mongo_filter)
    assert qdrant_filter == {
        "must": [{"key": "age", "range": {"lte": "30"}}, {"key": "name", "match": {"text": "John"}}]
    }
    _ = Filter(**qdrant_filter)


def test_qdrant_filter_combine_must_and_must_not():
    mongo_filter = {"age": {"$lte": "30"}, "name": {"$ne": "John"}}
    qdrant_filter = _mongodb_to_qdrant_filter(mongo_filter)
    assert qdrant_filter == {
        "must": [{"key": "age", "range": {"lte": "30"}}],
        "must_not": [{"key": "name", "match": {"text": "John"}}],
    }
    _ = Filter(**qdrant_filter)


def test_qdrant_filter_combine_must_and_should():
    mongo_filter = {"age": {"$lte": "30"}, "name": {"$in": ["John", "Jane"]}}
    qdrant_filter = _mongodb_to_qdrant_filter(mongo_filter)
    assert qdrant_filter == {
        "must": [{"key": "age", "range": {"lte": "30"}}],
        "should": [{"key": "name", "match": {"text": "John"}}, {"key": "name", "match": {"text": "Jane"}}],
    }
    _ = Filter(**qdrant_filter)
