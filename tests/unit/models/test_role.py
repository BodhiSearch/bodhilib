import json

from bodhilib.models import Prompt, Role


def test_role_eq_str_value():
    assert Role.SYSTEM == "system"
    assert Role.AI == "ai"
    assert Role.USER == "user"
    assert "system" == Role.SYSTEM
    assert "ai" == Role.AI
    assert "user" == Role.USER


def test_create_prompt_with_role():
    prompt = Prompt("text", role=Role.SYSTEM)
    assert prompt.role == Role.SYSTEM
    prompt = Prompt("text", role="system")
    assert prompt.role == Role.SYSTEM


def test_json_serialize_role():
    result = json.dumps({"text": "prompt", "role": Role.SYSTEM})
    assert result == '{"text": "prompt", "role": "system"}'
