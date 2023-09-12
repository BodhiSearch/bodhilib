import pytest
from bodhilib.llm import LLM, get_llm
from bodhilib.models import Prompt, PromptTemplate

from tests_bodhiext_openai.utils import chat_model, default_system_prompt, default_user_prompt


@pytest.fixture
def llm_davinci() -> LLM:
    return get_llm("openai", "text-davinci-003")


@pytest.fixture
def llm_gpt35_turbo() -> LLM:
    return get_llm("openai", chat_model)


@pytest.mark.live
def test_openai_chat_generate(llm_gpt35_turbo):
    result = llm_gpt35_turbo.generate(default_user_prompt)
    assert result.role == "ai"
    assert "tuesday" in result.text.strip().lower()


@pytest.mark.live
def test_openai_chat_generate_with_system_prompt(llm_gpt35_turbo):
    result = llm_gpt35_turbo.generate([Prompt(default_system_prompt, "system"), default_user_prompt])
    assert result.role == "ai"
    assert "tuesday" in result.text.strip().lower()


@pytest.mark.live
def test_openai_text_generate(llm_davinci):
    result = llm_davinci.generate("say hello\n")
    assert result.role == "ai"
    assert ("hello" in result.text.strip().lower()) or ("hi" in result.text.strip().lower())


@pytest.mark.live
def test_openai_text_generate_with_system_prompt(llm_davinci):
    result = llm_davinci.generate([default_system_prompt, default_user_prompt])
    assert result.role == "ai"
    assert "tuesday" in result.text.strip().lower()


@pytest.mark.live
def test_openai_chat_generate_with_prompt_template(llm_gpt35_turbo):
    template = PromptTemplate("Question: What day comes after {day}?\nAnswer: ")
    prompt = template.to_prompt(day="Tuesday")
    result = llm_gpt35_turbo.generate(prompt)
    assert "wednesday" in result.text.strip().lower()


@pytest.mark.live
def test_openai_chat_generate_with_assistant_prompt(llm_gpt35_turbo):
    prompts = [
        Prompt("What day comes after Monday?", "user"),
        Prompt("Tuesday.", "ai"),
        Prompt("What was my previous question?", "user"),
    ]
    chat_response = llm_gpt35_turbo.generate(prompts)
    assert "monday" in chat_response.text.strip().lower()
