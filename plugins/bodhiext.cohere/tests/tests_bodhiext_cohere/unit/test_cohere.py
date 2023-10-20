from unittest.mock import MagicMock, patch

import cohere
from bodhiext.cohere import Cohere
from bodhilib import Prompt


@patch("cohere.Client", autospec=True)
def test_override_constructor_vars(mock_client_init):
    mock_client_instance = MagicMock()
    mock_client_instance.generate.return_value.generations = [
        cohere.responses.Generation(text="Sunday", likelihood=0.5, token_likelihoods=[])
    ]
    mock_client_init.return_value = mock_client_instance
    llm = Cohere(model="command", api_key="test-api-key", temperature=0.1)
    llm.generate("hello world", temperature=0.9)
    mock_client_instance.generate.assert_called_once_with("hello world", model="command", temperature=0.9)


@patch("cohere.Client", autospec=True)
def test_passthrough_vars(mock_client_init):
    mock_client_instance = MagicMock()
    mock_client_instance.generate.return_value.generations = [
        cohere.responses.Generation(text="Sunday", likelihood=0.5, token_likelihoods=[])
    ]
    mock_client_init.return_value = mock_client_instance
    llm = Cohere(model="command", api_key="test-api-key")
    mock_client_init.assert_called_once_with(api_key="test-api-key")

    result = llm.generate(
        "What day comes after Monday?",
        stream=False,
        temperature=0.8,
        top_p=4,
        top_k=5,
        n=5,
        stop=["\n\n"],
        max_tokens=256,
        presence_penalty=0.9,
        frequency_penalty=0.5,
        user="test-user",
        end_sequences=["Human: "],
        return_likelihoods=True,
        truncate="END",
    )

    expected_args = {
        "model": "command",
        "stream": False,
        "num_generations": 5,
        "max_tokens": 256,
        "temperature": 0.8,
        "p": 4,
        "k": 5,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.9,
        "stop_sequences": ["\n\n"],
        "user": "test-user",
        "end_sequences": ["Human: "],
        "return_likelihoods": True,
        "truncate": "END",
    }
    mock_client_instance.generate.assert_called_once_with("What day comes after Monday?", **expected_args)
    assert type(result) is Prompt
    assert result.text == "Sunday"
    assert result.role == "ai"
    assert result.source == "output"
