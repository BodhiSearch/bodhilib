import pytest
from bodhilib import get_llm, prompt_output, prompt_system, prompt_user

from tests_bodhitest.llm_data import bodhiext_llms, explode


@pytest.fixture
def llm_params(request):
    return bodhiext_llms[request.param]


@pytest.fixture
def llm_service(request):
    service_name, _, model_name, llm_class, _ = explode(bodhiext_llms[request.param])
    return get_llm(service_name, model_name, oftype=llm_class)


@pytest.mark.live
@pytest.mark.parametrize("llm_params", bodhiext_llms.keys(), indirect=True)
def test_all_llms_generate(llm_params):
    service_name, llm_service_builder, model_name, _, _ = explode(llm_params)
    service = llm_service_builder(service_name=service_name, service_type="llm", model=model_name)
    result = service.generate("Answer in one word. What day comes after Monday?")
    assert "tuesday" in result.text.lower().strip()


@pytest.mark.live
@pytest.mark.parametrize("llm_service", bodhiext_llms.keys(), indirect=True)
def test_all_llms_generate_with_temperature(llm_service):
    result = llm_service.generate("Answer in one word. What day comes after Monday?", temperature=0.5)
    assert "tuesday" in result.text.lower().strip()


@pytest.mark.live
@pytest.mark.parametrize("llm_service", bodhiext_llms.keys(), indirect=True)
def test_all_llms_generate_with_system_prompt(llm_service):
    system = prompt_system("Answer in one word.")
    user = prompt_user("What day comes after Monday?")
    result = llm_service.generate([system, user], temperature=0.5)
    assert "tuesday" in result.text.lower().strip()


@pytest.mark.live
@pytest.mark.parametrize("llm_service", bodhiext_llms.keys(), indirect=True)
def test_all_llms_generate_with_chat_history(llm_service):
    user = prompt_user("What day comes after Monday?")
    response = prompt_output("Tuesday.")
    next_q = prompt_user("What was my previous question?")
    result = llm_service.generate([user, response, next_q], temperature=0.5)
    assert "what day" in result.text.lower().strip()
