import pytest
from bodhilib.sentence_transformers import sentence_transformer_builder


@pytest.mark.live
def test_sentence_transformer_embeddings():
    embedder = sentence_transformer_builder(service_name="sentence_transformers", service_type="embedder")
    embeddings = list(embedder.embeds(["foo", "bar"]))
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384
