import pytest
from bodhilib.models import (
    Prompt,
    Role,
    Source,
    prompt_output,
    prompt_user,
)

from tests.prompt_utils import default_system_prompt, default_user_prompt


def test_prompt_init_with_positional_args():
    prompt = Prompt(default_user_prompt)
    assert prompt.text == default_user_prompt
    assert prompt.role == "user"
    assert prompt.source == "input"


def test_prompt_init_with_positional_args_full():
    prompt = Prompt(default_user_prompt, "system", "output")
    assert prompt.text == default_user_prompt
    assert prompt.role == "system"
    assert prompt.source == "output"


def test_prompt_init_with_role_enum():
    prompt = Prompt(default_user_prompt, role=Role.USER, source="input")
    assert prompt.role == "user"
    assert prompt.role == Role.USER


@pytest.mark.parametrize(
    ["role", "source", "invalid_field", "allowed_values"],
    [
        ("invalid", "input", "role", ["system", "ai", "user"]),
        ("user", "invalid", "source", ["input", "output"]),
    ],
)
def test_prompt_init_with_invalid_strenum(role, source, invalid_field, allowed_values):
    with pytest.raises(ValueError) as e:
        Prompt(default_user_prompt, role, source)
    assert len(e.value.errors()) == 1
    error = e.value.errors()[0]
    assert error["loc"] == (invalid_field,)
    assert error["type"] == "value_error"
    expected_message = f"Invalid value for {invalid_field.capitalize()}. Allowed values are {allowed_values}."
    assert error["msg"] == expected_message


def test_prompt_user():
    prompt = prompt_user(default_user_prompt)
    assert prompt.text == default_user_prompt
    assert prompt.role == Role.USER
    assert prompt.source == Source.INPUT


def test_prompt_output():
    prompt = prompt_output(default_system_prompt)
    assert prompt.text == default_system_prompt
    assert prompt.role == Role.AI
    assert prompt.source == Source.OUTPUT
