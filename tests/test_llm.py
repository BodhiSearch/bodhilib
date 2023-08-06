import pytest

from bodhisearch.llm import OpenAIChat, OpenAIClassic, get_llm


def test_get_llm_openai_classic():
    llm = get_llm("openai", "text-ada-001")
    assert llm.provider == "openai"
    assert llm.model == "text-ada-001"
    assert type(llm) is OpenAIClassic


def test_get_llm_openai_chat():
    llm = get_llm("openai", "gpt-3.5-turbo")
    assert llm.provider == "openai"
    assert llm.model == "gpt-3.5-turbo"
    assert type(llm) is OpenAIChat


def test_unknown_provider_raise_error():
    with pytest.raises(ValueError) as e:
        _ = get_llm("unknown", "unknown-model")
    assert str(e.value) == "Unknown provider: unknown"
