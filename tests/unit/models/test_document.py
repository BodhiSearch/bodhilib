from bodhilib.models import Document, Node


def test_document_repr():
    doc = Document(text="Hello World!" * 30, metadata={"filename": "test.txt"})
    assert repr(doc) == "Document(text='Hello World!...!Hello World!', metadata={'filename': 'test.txt'})"


def test_node_repr():
    parent = Document(text="World Hello!" * 30, metadata={"filename": "test.txt"})
    node = Node(text="Hello World!" * 30, parent=parent)
    assert (
        repr(node)
        == "Node(text='Hello World!...!Hello World!', parent=Document(text='World Hello!...!World Hello!',"
        " metadata={'filename': 'test.txt'}))"
    )
