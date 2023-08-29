from unittest.mock import patch

import pytest
from bodhilib.openai import OpenAIChat, OpenAIText
from bodhilib.openai import openai_llm_service_builder

text_model = "text-ada-001"
chat_model = "gpt-3.5-turbo"


def test_get_llm_openai_text():
    llm = openai_llm_service_builder(service_name="openai", model=text_model)
    assert llm.model == text_model
    assert type(llm) is OpenAIText


def test_get_llm_openai_chat():
    llm = openai_llm_service_builder(service_name="openai", model=chat_model)
    assert llm.model == chat_model
    assert type(llm) is OpenAIChat


@patch("openai.ChatCompletion.create")
def test_chat_llm_generate_with_temperature(mock_create):
    mock_create.return_value.choices[0].message = {"content": "Sunday"}
    chat = openai_llm_service_builder(service_name="openai", model=chat_model)
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
    chat = openai_llm_service_builder(service_name="openai", model=chat_model, temperature=0.5)
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
    chat = openai_llm_service_builder(service_name="openai", model=text_model)
    prompt_text = "What comes after Monday?"
    response = chat.generate(prompt_text, temperature=0.5)
    assert response.text == "Sunday"
    mock_create.assert_called_once_with(
        model=text_model,
        prompt=prompt_text,
        temperature=0.5,
    )


@patch("openai.Completion.create")
def test_llm_generate_override_construct_params(mock_create):
    mock_create.return_value.choices = [{"text": "Sunday"}]
    chat = openai_llm_service_builder(service_name="openai", model=text_model, temperature=0.5)
    prompt_text = "What comes after Monday?"
    response = chat.generate(prompt_text, temperature=0.9)
    assert response.text == "Sunday"
    mock_create.assert_called_once_with(
        model=text_model,
        prompt=prompt_text,
        temperature=0.9,
    )


def test_get_llm_openai_raise_error_when_api_key_is_not_set(monkeypatch):
    with monkeypatch.context() as m:
        m.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(ValueError) as e:
            _ = openai_llm_service_builder(service_name="openai", model=chat_model)
    assert str(e.value) == "environment variable OPENAI_API_KEY is not set"


def test_unknown_service_name_raise_error():
    with pytest.raises(ValueError) as e:
        _ = openai_llm_service_builder(service_name="unknown", model="unknown-model")
    assert str(e.value) == "Unknown service: service_name='unknown'"


def test_openai_chat_raise_error_when_called_using_callable():
    llm = openai_llm_service_builder(service_name="openai", model=chat_model)
    with pytest.raises(TypeError) as e:
        _ = llm()
    assert str(e.value) == "'OpenAIChat' object is not callable, did you mean to call 'generate'?"


def test_openai_text_raise_error_when_called_using_callable():
    llm = openai_llm_service_builder(service_name="openai", model=text_model)
    with pytest.raises(TypeError) as e:
        _ = llm()
    assert str(e.value) == "'OpenAIText' object is not callable, did you mean to call 'generate'?"
