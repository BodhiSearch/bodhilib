from unittest.mock import patch

import pytest
from bodhilib.plugin import Service
from bodhilib.sentence_transformers import bodhilib_list_services, sentence_transformer_builder


def test_sentence_transformer_bodhilib_list_services():
    service_listing = bodhilib_list_services()
    assert service_listing == [
        Service("sentence_transformers", "embedder", "bodhilib", sentence_transformer_builder, "0.1.0")
    ]


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


@patch("bodhilib.sentence_transformers.SentenceTransformer")
def test_embedder_calls_sentence_transformer(mock_class):
    mock_instance = mock_class.return_value
    stub_embeddings = EmbeddingList([[1, 2, 3], [4, 5, 6]])
    mock_instance.encode.return_value = stub_embeddings

    embedder = sentence_transformer_builder(service_name="sentence_transformers", service_type="embedder")
    result = embedder.embeds(["foo", "bar"])

    mock_instance.encode.assert_called_once_with(["foo", "bar"])
    assert list(result) == [[1, 2, 3], [4, 5, 6]]
