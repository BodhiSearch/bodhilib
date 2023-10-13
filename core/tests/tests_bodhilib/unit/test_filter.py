import pytest
from bodhilib import Filter

data = {
    "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
    "age": [25, 30, 35, 40, 45],
    "score": [90, 85, 80, 75, 70],
    "hobbies": [
        ["reading", "music"],
        ["sports", "travel"],
        ["music", "travel"],
        ["sports", "reading"],
        ["music", "movies"],
    ],
}

# Test Data
test_data_list = [dict(zip(data.keys(), values)) for values in zip(*data.values())]

# Expected Results for the test queries
expected_results = {
    '{"$and": [{"age": {"$gt": 30}}, {"score": {"$lt": 85}}]}': [
        "Charlie",
        "David",
        "Eve",
    ],
    '{"$or": [{"age": {"$lt": 30}}, {"score": {"$gt": 85}}]}': ["Alice"],
    '{"$nor": [{"hobbies": {"$eq": "music"}}, {"score": {"$eq": 75}}]}': [
        "Alice",
        "Bob",
        "Charlie",
        "Eve",
    ],
    '{"name": {"$eq": "Alice"}}': ["Alice"],
    '{"age": {"$lt": 30}}': ["Alice"],
    '{"name": {"$ne": "Charlie"}}': ["Alice", "Bob", "David", "Eve"],
    '{"hobbies": {"$in": ["reading"]}}': ["Alice", "David"],
    '{"hobbies": {"$in": ["reading", "travel"]}}': ["Alice", "Bob", "Charlie", "David"],
    '{"hobbies": {"$nin": ["travel"]}}': ["Alice", "David", "Eve"],
    '{"hobbies": {"$nin": ["travel", "movies"]}}': ["Alice", "David"],
    '{"hobbies": {"$all": ["sports"]}}': ["Bob", "David"],
    '{"hobbies": {"$all": ["sports", "reading"]}}': ["David"],
}

# Test Functions


@pytest.mark.parametrize("query, expected_result", expected_results.items())
def test_filter(query, expected_result):
    # Convert string representation of dict to actual dict
    query_dict = eval(query)

    # Convert dict to Filter object
    filter_obj = Filter.from_dict(query_dict)

    # Test to_dict returns the original dict
    assert filter_obj.to_dict() == query_dict

    # Test the evaluate logic
    result = [record for record in test_data_list if filter_obj.evaluate(record)]
    result_names = [record["name"] for record in result]
    assert result_names == expected_result


def test_converts_implicit_eq_to_explicit_eq():
    filter_obj = Filter.from_dict({"name": "Alice"})
    assert filter_obj.to_dict() == {"name": {"$eq": "Alice"}}
