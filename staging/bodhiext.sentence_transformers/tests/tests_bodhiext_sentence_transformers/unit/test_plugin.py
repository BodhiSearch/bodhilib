from unittest.mock import patch

import pytest
from bodhiext.sentence_transformers import sentence_transformer_builder
from bodhilib import Node


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


@pytest.mark.parametrize(["pass_as_client"], [(False,), (True,)])
@patch("sentence_transformers.SentenceTransformer")
def test_embedder_calls_sentence_transformer(mock_class, pass_as_client):
    mock_instance = mock_class.return_value
    stub_embeddings = EmbeddingList([[1, 2, 3], [4, 5, 6]])
    mock_instance.encode.return_value = stub_embeddings
    client = mock_instance if pass_as_client else None
    args = {"service_name": "sentence_transformers", "service_type": "embedder", "client": client}
    embedder = sentence_transformer_builder(**args)
    result = embedder.embed(["foo", "bar"])

    mock_instance.encode.assert_called_once_with(["foo", "bar"])
    assert list(result) == [Node(text="foo", embedding=[1, 2, 3]), Node(text="bar", embedding=[4, 5, 6])]


@pytest.mark.parametrize(
    ["dimension", "error_message"],
    [(None, "Dimension of the model is None."), ("0", "Unknown type for dimension, type=<class 'str'>")],
)
@patch("sentence_transformers.SentenceTransformer")
def test_embedder_dimension_raises_error(mock_class, dimension, error_message):
    mock_instance = mock_class.return_value
    mock_instance.get_sentence_embedding_dimension.return_value = dimension
    with pytest.raises(ValueError) as e:
        _ = sentence_transformer_builder(service_name="sentence_transformers", service_type="embedder").dimension
    assert str(e.value) == error_message
