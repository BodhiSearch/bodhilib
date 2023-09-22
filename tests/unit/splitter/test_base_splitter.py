from typing import Iterable, List
from unittest.mock import MagicMock, patch

import pytest
from bodhilib import BaseSplitter
from bodhilib.models import Document, Node, Prompt


class TestSplitter(BaseSplitter):
    def _split(self, docs: Iterable[Document]) -> List[Node]:
        ...


class TestObject:
    ...


def test_base_splitter_raise_error_if_texts_invalid():
    splitter = TestSplitter()
    with pytest.raises(ValueError) as e:
        splitter.split(TestObject())
    assert (
        str(e.value) == "Cannot convert type <class 'tests.unit.splitter.test_base_splitter.TestObject'> to Document."
    )


def test_base_splitter_parses_str():
    splitter = TestSplitter()
    with patch.object(splitter, "_split", MagicMock()) as mock_method:
        splitter.split("split this")
        mock_method.assert_called_once_with([Document(text="split this")])


def test_base_splitter_parses_list_of_str():
    splitter = TestSplitter()
    with patch.object(splitter, "_split", MagicMock()) as mock_method:
        splitter.split(["split this", "and this"])
        mock_method.assert_called_once_with([Document(text="split this"), Document(text="and this")])


def test_base_splitter_parses_text_like():
    splitter = TestSplitter()
    with patch.object(splitter, "_split", MagicMock()) as mock_method:
        splitter.split(Prompt(text="this is prompt"))
        mock_method.assert_called_once_with([Document(text="this is prompt")])


def test_base_splitter_parses_text_like_list():
    splitter = TestSplitter()
    with patch.object(splitter, "_split", MagicMock()) as mock_method:
        splitter.split([Prompt(text="this is prompt"), Prompt(text="second prompt")])
        mock_method.assert_called_once_with([Document(text="this is prompt"), Document(text="second prompt")])


def test_base_splitter_parses_document():
    splitter = TestSplitter()
    with patch.object(splitter, "_split", MagicMock()) as mock_method:
        splitter.split(Document(text="this is document"))
        mock_method.assert_called_once_with([Document(text="this is document")])


def test_base_splitter_parses_document_list():
    splitter = TestSplitter()
    with patch.object(splitter, "_split", MagicMock()) as mock_method:
        splitter.split([Document(text="this is document"), Document(text="second document")])
        mock_method.assert_called_once_with([Document(text="this is document"), Document(text="second document")])
