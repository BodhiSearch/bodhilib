import pytest
from bodhilib import Document, Node, Prompt, to_document, to_document_list


def test_document_repr():
    doc = Document(text="Hello World!" * 30, metadata={"filename": "test.txt"})
    assert repr(doc) == "Document(text='Hello World!...!Hello World!', metadata={'filename': 'test.txt'})"


def test_node_repr():
    parent = Document(text="World Hello!" * 30, metadata={"filename": "test.txt"})
    node = Node(text="Hello World!" * 30, parent=parent)
    assert (
        repr(node)
        == "Node(id=None, text='Hello World!...!Hello World!', parent=Document(text='World Hello!...!World Hello!',"
        " metadata={'filename': 'test.txt'}))"
    )


@pytest.mark.parametrize(
    "valid_arg",
    [
        "hello",
        (Document(text="hello")),
        (Prompt(text="hello")),
    ],
)
def test_to_document_converts_valid_arg_to_document(valid_arg):
    document = to_document(valid_arg)
    assert isinstance(document, Document)
    assert document.text == "hello"


def test_to_document_raises_exception_for_invalid_arg():
    with pytest.raises(ValueError) as e:
        _ = to_document(object())
    assert str(e.value) == "Cannot convert type <class 'object'> to Document."


@pytest.mark.parametrize(
    "valid_arg",
    [
        "hello",
        ["hello"],
        (Document(text="hello")),
        [(Document(text="hello"))],
        (Prompt(text="hello")),
        [(Prompt(text="hello"))],
        ({"text": "hello"}),
        ([{"text": "hello"}]),
    ],
)
def test_to_document_list_converts_valid_arg_to_document_list(valid_arg):
    documents = to_document_list(valid_arg)
    assert len(documents) == 1
    assert isinstance(documents[0], Document)
    assert documents[0].text == "hello"


def test_to_document_list_raises_exception_for_invalid_args():
    with pytest.raises(ValueError) as e:
        _ = to_document_list(object())
    assert str(e.value) == "Cannot convert type <class 'object'> to Document."
