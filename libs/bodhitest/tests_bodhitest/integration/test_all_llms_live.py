import pytest
from bodhilib import get_llm, prompt_output, prompt_system, prompt_user

from tests_bodhitest.all_data import bodhiext_llms


@pytest.fixture
def llm_params(request):
  return bodhiext_llms[request.param]


@pytest.fixture
def llm_service(request):
  service_name = bodhiext_llms[request.param]["service_name"]
  service_class = bodhiext_llms[request.param]["service_class"]
  service_args = bodhiext_llms[request.param]["service_args"]
  service_args_copy = {**service_args}  # make a copy to avoid mutating the original, doing a pop in next line
  return get_llm(service_name, service_args_copy.pop("model"), oftype=service_class, **service_args_copy)


@pytest.mark.live
@pytest.mark.parametrize("llm_service", bodhiext_llms.keys(), indirect=True)
def test_all_llms_generate(llm_service):
  result = llm_service.generate("Answer in one word. What day comes after Monday?")
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
