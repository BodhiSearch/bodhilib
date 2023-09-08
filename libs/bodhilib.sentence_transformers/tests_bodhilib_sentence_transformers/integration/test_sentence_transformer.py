import pytest
from bodhilib.embedder import get_embedder
from bodhilib.sentence_transformers import SentenceTransformerEmbedder, sentence_transformer_builder


@pytest.fixture
def embedder():
    return sentence_transformer_builder(service_name="sentence_transformers")


@pytest.mark.live
def test_sentence_transformer_embeddings(embedder):
    embeddings = list(embedder.embeds(["foo", "bar"]))
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384


@pytest.mark.live
def test_sentence_transformer_dimension(embedder):
    assert embedder.dimension == 384


def test_sentence_transformer_get_embedder():
    embedder = get_embedder("sentence_transformers", offtype=SentenceTransformerEmbedder)
    assert isinstance(embedder, SentenceTransformerEmbedder)


class _TestEmbedder:
    ...


def test_sentence_transformer_get_embedder_raises_error_if_not_of_given_oftype():
    with pytest.raises(TypeError) as e:
        _ = get_embedder("sentence_transformers", oftype=_TestEmbedder)
    expected = (
        "Expecting embedder of type <class"
        " 'tests_bodhilib_sentence_transformers.integration.test_sentence_transformer._TestEmbedder'>, but got <class"
        " 'bodhilib.sentence_transformers.SentenceTransformerEmbedder'>"
    )
    assert str(e.value) == expected
