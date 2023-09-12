from typing import List

import pytest
from bodhilib import Embedder


class _TestEmbedder(Embedder):
    def _embed(self, texts: List[str]) -> List[List[float]]:
        return [[1.0, 2.0, 3.0]] * len(texts)

    @property
    def dimension(self) -> int:
        return 3


@pytest.fixture
def embedder():
    return _TestEmbedder()


def test_embedder_embed_raise_error_if_called_with_non_list(embedder):
    with pytest.raises(ValueError) as e:
        embedder.embed("hello")
    assert (
        str(e.value)
        == "Expecting input `texts` to be a list of TextLike, but is of type <class 'str'>. Did you forget to pass it"
        " as a list?"
    )


def test_embedder_embed_raise_error_if_called_with_non_textlike(embedder):
    with pytest.raises(ValueError) as e:
        embedder.embed([1])
    expected = (
        "Expecting input `texts` to be a list of TextLike items (a string or have attribute `text`), but some elements"
        " of the list are not TextLike"
    )
    assert str(e.value) == expected


def test_embed_calls_calls_impl_for_single_item(embedder):
    embeddings = embedder.embed(["hello"])
    assert embeddings == [[1.0, 2.0, 3.0]]


def test_embeds_calls_impl_for_multiple_items(embedder):
    embeddings = embedder.embed(["hello world", "world hello"])
    assert embeddings == [[1.0, 2.0, 3.0], [1.0, 2.0, 3.0]]


def test_dimension_calls_impl(embedder):
    assert embedder.dimension == 3
