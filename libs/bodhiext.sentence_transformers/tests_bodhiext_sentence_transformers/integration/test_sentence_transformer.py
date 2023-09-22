import pytest
from bodhiext.sentence_transformers import SentenceTransformerEmbedder, sentence_transformer_builder
from bodhilib import Embedder


@pytest.fixture
def embedder() -> SentenceTransformerEmbedder:
    return sentence_transformer_builder(service_name="sentence_transformers")


@pytest.mark.live
def test_sentence_transformer_embeddings(embedder: Embedder):
    nodes = list(embedder.embed(["foo", "bar"]))
    assert len(nodes) == 2
    assert len(nodes[0].embedding) == 384
    assert len(nodes[1].embedding) == 384


@pytest.mark.live
def test_sentence_transformer_dimension(embedder):
    assert embedder.dimension == 384
