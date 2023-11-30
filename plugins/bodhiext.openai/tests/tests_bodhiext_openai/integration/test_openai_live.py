import pytest
from bodhiext.openai import OpenAIChat, OpenAIText
from bodhilib import LLM, LLMApiConfig, LLMConfig, Prompt, Role, Source, get_llm

default_system_prompt = (
    "Answer my question below based on best of your ability. " + "Say no if you don't know the answer."
)
default_user_prompt = "Question: What day of the week comes after Monday?\nAnswer: "
chat_model = "gpt-3.5-turbo"
text_model = "text-ada-001"


@pytest.fixture
def llm_davinci() -> LLM:
    return get_llm("openai_text", "text-davinci-003")


@pytest.fixture
def llm_gpt35_turbo() -> LLM:
    return get_llm("openai_chat", chat_model)


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
def test_openai_chat_generate_with_assistant_prompt(llm_gpt35_turbo):
    prompts = [
        Prompt("What day comes after Monday?", "user"),
        Prompt("Tuesday.", "ai"),
        Prompt("What was my previous question?", "user"),
    ]
    chat_response = llm_gpt35_turbo.generate(prompts)
    assert "monday" in chat_response.text.strip().lower()


@pytest.mark.live
@pytest.mark.parametrize(["clz", "model"], [(OpenAIChat, chat_model), (OpenAIText, text_model)])
def test_openai_stream(clz, model):
    llm = clz(api_config=LLMApiConfig(), llm_config=LLMConfig(model=model))
    stream = llm.generate("generate a 50 words article on geography of India?", stream=True)
    for chunk in stream:
        assert chunk.role == Role.AI
        assert chunk.source == Source.OUTPUT
    assert stream.text != ""
