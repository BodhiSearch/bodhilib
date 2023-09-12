import pytest
from bodhiext.sentence_transformers import SentenceTransformerEmbedder, sentence_transformer_builder
from bodhilib import Embedder


@pytest.fixture
def embedder() -> SentenceTransformerEmbedder:
    return sentence_transformer_builder(service_name="sentence_transformers")


@pytest.mark.live
def test_sentence_transformer_embeddings(embedder: Embedder):
    embeddings = list(embedder.embed(["foo", "bar"]))
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384


@pytest.mark.live
def test_sentence_transformer_dimension(embedder):
    assert embedder.dimension == 384
