from unittest.mock import patch

import pytest
from bodhiext.openai import OpenAIChat, OpenAIText, bodhilib_list_services, openai_llm_service_builder
from bodhilib.plugin import Service

from tests_bodhiext_openai.utils import chat_model, text_model


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
    mock_create.return_value = {"choices": [{"message": {"content": "Sunday"}}]}
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
    mock_create.return_value = {"choices": [{"message": {"content": "Sunday"}}]}
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
    mock_create.return_value = {"choices": [{"text": "Sunday"}]}
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
    mock_create.return_value = {"choices": [{"text": "Sunday"}]}
    chat = openai_llm_service_builder(service_name="openai", model=text_model, temperature=0.5)
    prompt_text = "What comes after Monday?"
    response = chat.generate(prompt_text, temperature=0.9)
    assert response.text == "Sunday"
    mock_create.assert_called_once_with(
        model=text_model,
        prompt=prompt_text,
        temperature=0.9,
    )


def test_openai_list_services():
    services = bodhilib_list_services()
    assert len(services) == 1
    assert services[0] == Service("openai", "llm", "bodhilib", openai_llm_service_builder, "0.1.0")


def test_get_llm_openai_raise_error_when_api_key_is_not_set(monkeypatch):
    with monkeypatch.context() as m:
        m.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(ValueError) as e:
            _ = openai_llm_service_builder(service_name="openai", model=chat_model)
    assert str(e.value) == "environment variable OPENAI_API_KEY is not set"


@pytest.mark.parametrize(
    ["service_name", "service_type", "model", "error_message"],
    [
        ("unknown", "llm", "chat-gpt-3.5-turbo", "Unknown service: service_name='unknown'"),
        (
            "openai",
            "unknown",
            "chat-gpt-3.5-turbo",
            "Service type not supported: service_type='unknown', supported service types: 'llm'",
        ),
        ("openai", "llm", None, "model is not set"),
    ],
)
def test_openai_service_builder_raises_error(service_name, service_type, model, error_message):
    with pytest.raises(ValueError) as e:
        _ = openai_llm_service_builder(service_name=service_name, service_type=service_type, model=model)
    assert str(e.value) == error_message


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


def test_openai_bodhilib_list_services():
    services = bodhilib_list_services()
    assert len(services) == 1
    assert services[0] == Service("openai", "llm", "bodhilib", openai_llm_service_builder, "0.1.0")
