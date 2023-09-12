from unittest.mock import patch

import pytest
from bodhiext.sentence_transformers import (
    SentenceTransformerEmbedder,
    bodhilib_list_services,
    sentence_transformer_builder,
)
from bodhilib import get_embedder
from bodhilib.plugin import Service


def test_sentence_transformer_bodhilib_list_services():
    service_listing = bodhilib_list_services()
    assert service_listing == [
        Service("sentence_transformers", "embedder", "bodhiext", sentence_transformer_builder, "0.1.0")
    ]


def test_sentence_transformer_get_embedder():
    embedder = get_embedder("sentence_transformers", offtype=SentenceTransformerEmbedder)
    assert isinstance(embedder, SentenceTransformerEmbedder)


class _TestEmbedder:
    ...


def test_sentence_transformer_get_embedder_raises_error_if_not_of_given_oftype():
    with pytest.raises(TypeError) as e:
        _ = get_embedder("sentence_transformers", oftype=_TestEmbedder)
    expected = (
        'Expecting embedder of type "<class'
        " 'tests_bodhiext_sentence_transformers.unit.test_plugin._TestEmbedder'>\", but got"
        " \"<class 'bodhiext.sentence_transformers.SentenceTransformerEmbedder'>\""
    )
    assert str(e.value) == expected


@pytest.mark.parametrize(
    ["service_name", "service_type", "error_message"],
    [
        ("invalid_service", "embedder", "Unknown service: service_name='invalid_service'"),
        (
            "sentence_transformers",
            "invalid_type",
            "Service type not supported: service_type='invalid_type', supported service type: 'embedder'",
        ),
    ],
)
def test_raise_error_if_invalid_args(service_name, service_type, error_message):
    with pytest.raises(ValueError) as e:
        sentence_transformer_builder(service_name=service_name, service_type=service_type)
    assert str(e.value) == error_message


class EmbeddingList(list):
    def tolist(self):
        return self


@patch("bodhiext.sentence_transformers.SentenceTransformer")
def test_embedder_calls_sentence_transformer(mock_class):
    mock_instance = mock_class.return_value
    stub_embeddings = EmbeddingList([[1, 2, 3], [4, 5, 6]])
    mock_instance.encode.return_value = stub_embeddings

    embedder = sentence_transformer_builder(service_name="sentence_transformers", service_type="embedder")
    result = embedder.embed(["foo", "bar"])

    mock_instance.encode.assert_called_once_with(["foo", "bar"])
    assert list(result) == [[1, 2, 3], [4, 5, 6]]


@pytest.mark.parametrize(
    ["dimension", "error_message"],
    [(None, "Dimension of the model is None."), ("0", "Unknown type for dimension, type=<class 'str'>")],
)
@patch("bodhiext.sentence_transformers.SentenceTransformer")
def test_embedder_dimension_raises_error(mock_class, dimension, error_message):
    mock_instance = mock_class.return_value
    mock_instance.get_sentence_embedding_dimension.return_value = dimension
    with pytest.raises(ValueError) as e:
        _ = sentence_transformer_builder(service_name="sentence_transformers", service_type="embedder").dimension
    assert str(e.value) == error_message
