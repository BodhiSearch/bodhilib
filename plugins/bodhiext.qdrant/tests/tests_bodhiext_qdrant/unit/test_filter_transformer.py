import pytest
from bodhiext.qdrant._qdrant import _mongodb_to_qdrant_filter


@pytest.fixture(scope="module")
def mongo_filter(request):
  return request.param


@pytest.mark.parametrize(
  ["test_name", "mongo_filter", "expected"],
  [
    ("test_qdrant_filter_eq_str", {"name": "John"}, {"must": [{"key": "name", "match": {"text": "John"}}]}),
    ("test_qdrant_filter_eq_bool", {"admin": True}, {"must": [{"key": "admin", "match": {"value": True}}]}),
    (
      "test_qdrant_filter_eq_int",
      {"age": 25},
      {"must": [{"key": "age", "match": {"value": 25}}]},
    ),
    (
      "test_qdrant_filter_neq",
      {"name": {"$ne": "John"}},
      {"must_not": [{"key": "name", "match": {"text": "John"}}]},
    ),
    (
      "test_qdrant_filter_in",
      {"name": {"$in": ["John", "Jane"]}},
      {"should": [{"key": "name", "match": {"text": "John"}}, {"key": "name", "match": {"text": "Jane"}}]},
    ),
    (
      "test_qdrant_filter_not_in",
      {"name": {"$nin": ["John", "Jane"]}},
      {"must_not": [{"key": "name", "match": {"text": "John"}}, {"key": "name", "match": {"text": "Jane"}}]},
    ),
    ("test_qdrant_filter_gt", {"age": {"$gt": "30"}}, {"must": [{"key": "age", "range": {"gt": "30"}}]}),
    ("test_qdrant_filter_gte", {"age": {"$gte": "30"}}, {"must": [{"key": "age", "range": {"gte": "30"}}]}),
    ("test_qdrant_filter_lt", {"age": {"$lt": "30"}}, {"must": [{"key": "age", "range": {"lt": "30"}}]}),
    ("test_qdrant_filter_lte", {"age": {"$lte": "30"}}, {"must": [{"key": "age", "range": {"lte": "30"}}]}),
    (
      "test_qdrant_filter_combine_must",
      {"age": {"$lte": "30"}, "name": {"$eq": "John"}},
      {"must": [{"key": "age", "range": {"lte": "30"}}, {"key": "name", "match": {"text": "John"}}]},
    ),
    (
      "test_qdrant_filter_combine_must_and_must_not",
      {"age": {"$lte": "30"}, "name": {"$ne": "John"}},
      {
        "must": [{"key": "age", "range": {"lte": "30"}}],
        "must_not": [{"key": "name", "match": {"text": "John"}}],
      },
    ),
    (
      "test_qdrant_filter_combine_must_and_should",
      {"age": {"$lte": "30"}, "name": {"$in": ["John", "Jane"]}},
      {
        "must": [{"key": "age", "range": {"lte": "30"}}],
        "should": [{"key": "name", "match": {"text": "John"}}, {"key": "name", "match": {"text": "Jane"}}],
      },
    ),
  ],
)
def test_mongodb_to_qdrant_filter(test_name, mongo_filter, expected):
  parsed_filter = _mongodb_to_qdrant_filter(mongo_filter)
  assert parsed_filter == expected
  # bodhi_filter = Filter.from_dict(mongo_filter)
  # parsed_bodhi_filter = _mongodb_to_qdrant_filter(bodhi_filter)
  # assert (
  #     parsed_bodhi_filter == expected
  # ), f"{mongo_filter=}\n{expected=},\n{bodhi_filter.to_dict()=},\n{parsed_bodhi_filter=}"
