import pytest
from bodhilib import Node, Prompt, Role, Source, prompt_output, prompt_user, to_prompt, to_prompt_list

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


@pytest.mark.parametrize("valid_arg", ["hello", Prompt(text="hello"), Node(text="hello")])
def test_to_prompt_converts_to_prompt_for_valid_args(valid_arg):
    prompt = to_prompt(valid_arg)
    assert isinstance(prompt, Prompt)
    assert prompt.text == "hello"


def test_to_prompt_raises_exception_on_invalid_arg():
    with pytest.raises(ValueError) as e:
        _ = to_prompt(object())
    assert str(e.value) == "Cannot convert type <class 'object'> to Prompt."


@pytest.mark.parametrize("valid_arg", ["hello", Prompt(text="hello"), Node(text="hello")])
def test_to_prompt_list_converts_for_valid_args(valid_arg):
    prompts = to_prompt_list(valid_arg)
    assert len(prompts) == 1
    assert isinstance(prompts[0], Prompt)
    assert prompts[0].text == "hello"


def test_to_prompt_list_raises_exception_on_invalid_arg():
    with pytest.raises(ValueError) as e:
        _ = to_prompt_list(object())
    assert str(e.value) == "Cannot convert type <class 'object'> to Prompt."
