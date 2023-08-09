import pytest

from bodhisearch.openai import OpenAIChat, OpenAIClassic, get_llm


def test_get_llm_openai_classic():
    llm = get_llm("openai", "text-ada-001")
    assert llm.model == "text-ada-001"
    assert type(llm) is OpenAIClassic


def test_get_llm_openai_chat():
    llm = get_llm("openai", "gpt-3.5-turbo")
    assert llm.model == "gpt-3.5-turbo"
    assert type(llm) is OpenAIChat


def test_get_llm_openai_raise_error_when_api_key_is_not_set(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError) as e:
        _ = get_llm("openai", "gpt-3.5-turbo")
    assert str(e.value) == "environment variable OPENAI_API_KEY is not set"


def test_unknown_provider_raise_error():
    with pytest.raises(ValueError) as e:
        _ = get_llm("unknown", "unknown-model")
    assert str(e.value) == "Unknown provider: unknown"


def test_openai_chat_raise_error_when_called_using_callable():
    llm = get_llm("openai", "gpt-3.5-turbo")
    with pytest.raises(TypeError) as e:
        _ = llm()
    assert str(e.value) == "'OpenAIChat' object is not callable, did you mean to call 'generate'?"


def test_openai_classic_raise_error_when_called_using_callable():
    llm = get_llm("openai", "text-davinci-003")
    with pytest.raises(TypeError) as e:
        _ = llm()
    assert str(e.value) == "'OpenAIClassic' object is not callable, did you mean to call 'generate'?"
