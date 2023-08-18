from unittest.mock import patch

import pytest
from bodhisearch.openai import OpenAIChat, OpenAIClassic, get_llm

classic_model = "text-ada-001"
chat_model = "gpt-3.5-turbo"


def test_get_llm_openai_classic():
    llm = get_llm("openai", classic_model)
    assert llm.model == classic_model
    assert type(llm) is OpenAIClassic


def test_get_llm_openai_chat():
    llm = get_llm("openai", chat_model)
    assert llm.model == chat_model
    assert type(llm) is OpenAIChat


@patch("openai.ChatCompletion.create")
def test_chat_llm_generate_with_temperature(mock_create):
    mock_create.return_value.choices[0].message = {"content": "Sunday"}
    chat = get_llm("openai", chat_model)
    prompt_text = "What comes after Monday?"
    response = chat.generate(prompt_text, temperature=0.5)
    assert response.text == "Sunday"
    mock_create.assert_called_once_with(
        model=chat_model,
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0.5,
    )


@patch("openai.ChatCompletion.create")
def test_chat_llm_generate_override_construct_params(mock_create):
    mock_create.return_value.choices[0].message = {"content": "Sunday"}
    chat = get_llm("openai", chat_model, temperature=0.5)
    prompt_text = "What comes after Monday?"
    response = chat.generate(prompt_text, temperature=0.9)
    assert response.text == "Sunday"
    mock_create.assert_called_once_with(
        model=chat_model,
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0.9,
    )


@patch("openai.Completion.create")
def test_llm_generate_with_temperature(mock_create):
    mock_create.return_value.choices = [{"text": "Sunday"}]
    chat = get_llm("openai", classic_model)
    prompt_text = "What comes after Monday?"
    response = chat.generate(prompt_text, temperature=0.5)
    assert response.text == "Sunday"
    mock_create.assert_called_once_with(
        model=classic_model,
        prompt=prompt_text,
        temperature=0.5,
    )


@patch("openai.Completion.create")
def test_llm_generate_override_construct_params(mock_create):
    mock_create.return_value.choices = [{"text": "Sunday"}]
    chat = get_llm("openai", classic_model, temperature=0.5)
    prompt_text = "What comes after Monday?"
    response = chat.generate(prompt_text, temperature=0.9)
    assert response.text == "Sunday"
    mock_create.assert_called_once_with(
        model=classic_model,
        prompt=prompt_text,
        temperature=0.9,
    )


def test_get_llm_openai_raise_error_when_api_key_is_not_set(monkeypatch):
    with monkeypatch.context() as m:
        m.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(ValueError) as e:
            _ = get_llm("openai", chat_model)
    assert str(e.value) == "environment variable OPENAI_API_KEY is not set"


def test_unknown_provider_raise_error():
    with pytest.raises(ValueError) as e:
        _ = get_llm("unknown", "unknown-model")
    assert str(e.value) == "Unknown provider: unknown"


def test_openai_chat_raise_error_when_called_using_callable():
    llm = get_llm("openai", chat_model)
    with pytest.raises(TypeError) as e:
        _ = llm()
    assert str(e.value) == "'OpenAIChat' object is not callable, did you mean to call 'generate'?"


def test_openai_classic_raise_error_when_called_using_callable():
    llm = get_llm("openai", classic_model)
    with pytest.raises(TypeError) as e:
        _ = llm()
    assert str(e.value) == "'OpenAIClassic' object is not callable, did you mean to call 'generate'?"
