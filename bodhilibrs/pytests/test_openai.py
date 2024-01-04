import os
import pytest
from bodhilibrs import OpenAI


@pytest.mark.live
def test_openai_live():
  api_key = os.environ.get("OPENAI_API_KEY")
  client = OpenAI(api_key=api_key)
  response = client.generate(model="gpt-3.5-turbo", prompt="What day comes after Monday?")
  assert "Tuesday" in response[0]
