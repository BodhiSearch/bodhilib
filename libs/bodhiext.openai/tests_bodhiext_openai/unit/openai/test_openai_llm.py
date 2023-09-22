from unittest.mock import patch

import pytest
from bodhiext.openai import OpenAIChat, OpenAIText, bodhilib_list_services
from bodhiext.openai._openai_plugin import openai_chat_service_builder, openai_text_service_builder
from bodhiext.openai._version import __version__
from bodhilib import Service, get_llm

from tests_bodhiext_openai.utils import chat_model, text_model


@pytest.fixture
def openai_chat() -> OpenAIChat:
    return get_llm("openai_chat", chat_model)


@pytest.fixture
def openai_text() -> OpenAIChat:
    return get_llm("openai_text", text_model)


def test_openai_service_builder_text():
    llm = openai_text_service_builder(service_name="openai_text", model=text_model)
    assert llm.kwargs["model"] == text_model
    assert type(llm) is OpenAIText


def test_openai_service_builder_chat():
    llm = openai_chat_service_builder(service_name="openai_chat", model=chat_model)
    assert llm.kwargs["model"] == chat_model
    assert type(llm) is OpenAIChat


def test_openai_get_llm_openai_chat():
    openai = get_llm("openai_chat", chat_model)
    assert type(openai) is OpenAIChat


def test_openai_get_llm_openai_text():
    openai = get_llm("openai_text", text_model)
    assert type(openai) is OpenAIText


@patch("openai.ChatCompletion.create")
def test_chat_llm_generate_with_temperature(mock_create, openai_chat):
    mock_create.return_value = {"choices": [{"message": {"content": "Sunday"}}]}
    prompt_text = "What comes after Monday?"
    response = openai_chat.generate(prompt_text, temperature=0.5)
    assert response.text == "Sunday"
    mock_create.assert_called_once_with(
        model=chat_model,
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0.5,
    )


@patch("openai.ChatCompletion.create")
def test_chat_llm_generate_override_construct_params(mock_create, openai_chat):
    mock_create.return_value = {"choices": [{"message": {"content": "Sunday"}}]}
    prompt_text = "What comes after Monday?"
    response = openai_chat.generate(prompt_text, temperature=0.9)
    assert response.text == "Sunday"
    mock_create.assert_called_once_with(
        model=chat_model,
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0.9,
    )


@patch("openai.Completion.create")
def test_llm_generate_with_temperature(mock_create, openai_text):
    mock_create.return_value = {"choices": [{"text": "Sunday"}]}
    prompt_text = "What comes after Monday?"
    response = openai_text.generate(prompt_text, temperature=0.5)
    assert response.text == "Sunday"
    mock_create.assert_called_once_with(
        model=text_model,
        prompt=prompt_text,
        temperature=0.5,
    )


@patch("openai.Completion.create")
def test_llm_generate_override_construct_params(mock_create, openai_text):
    mock_create.return_value = {"choices": [{"text": "Sunday"}]}
    prompt_text = "What comes after Monday?"
    response = openai_text.generate(prompt_text, temperature=0.9)
    assert response.text == "Sunday"
    mock_create.assert_called_once_with(
        model=text_model,
        prompt=prompt_text,
        temperature=0.9,
    )


def test_openai_list_services():
    services = bodhilib_list_services()
    assert len(services) == 2
    assert services[0] == Service("openai_chat", "llm", "bodhiext", openai_chat_service_builder, __version__)
    assert services[1] == Service("openai_text", "llm", "bodhiext", openai_text_service_builder, __version__)


@pytest.mark.parametrize(["service_name", "model"], [("openai_chat", chat_model), ("openai_text", text_model)])
def test_get_llm_openai_raise_error_when_api_key_is_not_set(monkeypatch, service_name, model):
    with monkeypatch.context() as m:
        m.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(ValueError) as e:
            _ = get_llm(service_name=service_name, model=model)
    assert str(e.value) == "environment variable OPENAI_API_KEY is not set"


@pytest.mark.parametrize(
    ["builder", "service_name", "service_type", "model", "error_message"],
    [
        (
            openai_chat_service_builder,
            "unknown",
            "llm",
            "gpt-3.5-turbo",
            (
                "Unknown params: service_name='unknown', service_type='llm', supported params:"
                " service_name='openai_chat', service_type='llm'"
            ),
        ),
        (
            openai_chat_service_builder,
            "openai_chat",
            "unknown",
            "gpt-3.5-turbo",
            (
                "Unknown params: service_name='openai_chat', service_type='unknown', supported params:"
                " service_name='openai_chat', service_type='llm'"
            ),
        ),
        (
            openai_text_service_builder,
            "unknown",
            "llm",
            "text-ada-002",
            (
                "Unknown params: service_name='unknown', service_type='llm', supported params:"
                " service_name='openai_text', service_type='llm'"
            ),
        ),
        (
            openai_text_service_builder,
            "openai_text",
            "unknown",
            "text-ada-002",
            (
                "Unknown params: service_name='openai_text', service_type='unknown', supported params:"
                " service_name='openai_text', service_type='llm'"
            ),
        ),
    ],
)
def test_openai_service_builder_raises_error(builder, service_name, service_type, model, error_message):
    with pytest.raises(ValueError) as e:
        _ = builder(service_name=service_name, service_type=service_type, model=model)
    assert str(e.value) == error_message


@pytest.mark.parametrize(
    ["builder", "service_name", "model", "error_message"],
    [
        (
            openai_chat_service_builder,
            "openai_chat",
            chat_model,
            "'OpenAIChat' object is not callable, did you mean to call 'generate'?",
        ),
        (
            openai_text_service_builder,
            "openai_text",
            text_model,
            "'OpenAIText' object is not callable, did you mean to call 'generate'?",
        ),
    ],
)
def test_openai_chat_raise_error_when_called_using_callable(builder, service_name, model, error_message):
    llm = builder(service_name=service_name, model=model)
    with pytest.raises(TypeError) as e:
        _ = llm()
    assert str(e.value) == error_message
