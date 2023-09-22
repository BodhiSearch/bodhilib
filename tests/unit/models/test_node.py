import pytest
from bodhilib.models import Node, Prompt, to_node, to_node_list


@pytest.mark.parametrize(["valid_arg"], [(["hello"]), ([Node(text="hello")]), ([Prompt(text="hello")])])
def test_to_node_converts_valid_arg_to_node(valid_arg):
    node = to_node(valid_arg)
    assert isinstance(node, Node)
    assert node.text == "hello"


def test_to_node_raise_error_if_not_of_valid_type():
    with pytest.raises(ValueError) as e:
        to_node(object())
    assert str(e.value) == "Cannot convert type <class 'object'> to Node."


@pytest.mark.parametrize(
    "valid_arg",
    [
        (["hello"]),
        ([["hello"]]),
        (Node(text="hello")),
        ([Node(text="hello")]),
        (Prompt(text="hello")),
        ([Prompt(text="hello")]),
    ],
)
def test_to_node_list_converts_valid_arg_to_node_list(valid_arg):
    nodes = to_node_list(valid_arg)
    assert len(nodes) == 1
    assert isinstance(nodes[0], Node)
    assert nodes[0].text == "hello"


def test_to_node_list_raises_exception_for_invalid_arg():
    with pytest.raises(ValueError) as e:
        _ = to_node_list(object())
    assert str(e.value) == "Cannot convert type <class 'object'> to Node."
