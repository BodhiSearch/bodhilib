import pytest

from bodhisearch.llm import OpenAIChat, OpenAIClassic, get_llm
from bodhisearch.prompt import Prompt, PromptTemplate

from .test_prompt import default_system_prompt, default_user_prompt


@pytest.fixture
def llm_davinci():
    return get_llm("openai", "text-davinci-003")


@pytest.fixture
def llm_gpt35_turbo():
    return get_llm("openai", "gpt-3.5-turbo")


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


@pytest.mark.live
def test_openai_chat_generate(llm_gpt35_turbo):
    result = llm_gpt35_turbo.generate(default_user_prompt)
    assert result.role == "ai"
    assert "tuesday" in result.text.strip().lower()


@pytest.mark.live
def test_openai_chat_generate_with_system_prompt(llm_gpt35_turbo):
    result = llm_gpt35_turbo.generate(
        [Prompt(default_system_prompt, "system"), default_user_prompt]
    )
    assert result.role == "ai"
    assert "tuesday" in result.text.strip().lower()


@pytest.mark.live
def test_openai_classic_generate(llm_davinci):
    result = llm_davinci.generate("say hello\n")
    assert result.role == "ai"
    assert "hello" in result.text.strip().lower()


@pytest.mark.live
def test_openai_classic_generate_with_system_prompt(llm_davinci):
    result = llm_davinci.generate([default_system_prompt, default_user_prompt])
    assert result.role == "ai"
    assert "tuesday" in result.text.strip().lower()


@pytest.mark.live
def test_openai_chat_generate_with_prompt_template(llm_gpt35_turbo):
    template = PromptTemplate(
        "Question: What day comes after {day}?\nAnswer: "
    )
    prompt = template.to_prompt({"day": "Tuesday"})
    result = llm_gpt35_turbo.generate(prompt)
    assert "wednesday" in result.text.strip().lower()
