from typing import List
from unittest.mock import MagicMock, patch

import pytest
from bodhilib import BaseEmbedder
from bodhilib.models import Embedding, Node


class _TestEmbedder(BaseEmbedder):
    def _embed(self, texts: List[Node]) -> List[Embedding]:
        return [[1.0, 2.0, 3.0]] * len(texts)

    @property
    def dimension(self) -> int:
        return 3


@pytest.fixture
def embedder():
    return _TestEmbedder()


def test_embedder_embed_str(embedder):
    with patch.object(embedder, "_embed", MagicMock()) as mock_embed:
        _ = embedder.embed("hello")
        mock_embed.assert_called_once_with([Node(text="hello")])


def test_embedder_embed_raise_error_if_called_with_non_textlike(embedder):
    with pytest.raises(ValueError) as e:
        embedder.embed([1])
    expected = "Cannot convert type <class 'int'> to Node."
    assert str(e.value) == expected


def test_embed_calls_calls_impl_for_single_item(embedder):
    embeddings = embedder.embed(["hello"])
    assert embeddings == [[1.0, 2.0, 3.0]]


def test_embeds_calls_impl_for_multiple_items(embedder):
    embeddings = embedder.embed(["hello world", "world hello"])
    assert embeddings == [[1.0, 2.0, 3.0], [1.0, 2.0, 3.0]]


def test_dimension_calls_impl(embedder):
    assert embedder.dimension == 3
