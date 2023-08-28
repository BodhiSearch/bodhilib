import textwrap

import pytest
from bodhilib.models import (
    Prompt,
    PromptTemplate,
    Role,
    Source,
    prompt_user,
    prompt_output,
    prompt_with_examples,
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


# prompt template
def test_prompt_template():
    template = PromptTemplate(
        "Question: What day of the week comes after {day}?\nAnswer: ", role="user", source="input"
    )
    assert template.to_prompt(day="Monday") == Prompt(
        "Question: What day of the week comes after Monday?\nAnswer: ", role="user", source="input"
    )


def test_prompt_template_source_set_correctly():
    template = PromptTemplate(
        "Question: What day of the week comes after {day}?\nAnswer: ", role="user", source="output"
    )
    assert template.to_prompt(day="Monday") == Prompt(
        "Question: What day of the week comes after Monday?\nAnswer: ", role="user", source="output"
    )


def test_prompt_template_defaults():
    template = PromptTemplate("simple template")
    assert template.engine == "default"


def test_prompt_template_defaults_override():
    template = PromptTemplate("simple template", "system", "output", "jinja2")
    assert template.role == "system"
    assert template.source == "output"
    assert template.engine == "jinja2"


# prompt examples
def test_prompt_with_examples():
    template = """
    Below are few examples of location where item is usually found:
    {% for example in examples %}
    Example input: {{example.input}}
    Example output: {{example.output}}
    {% endfor %}
    Example input: {{query}}
    Example output: """
    print(textwrap.dedent(template))
    examples = [
        {"input": "pirate", "output": "ship"},
        {"input": "pilot", "output": "plane"},
        {"input": "driver", "output": "car"},
    ]

    query = "pirate"

    prompt_template = prompt_with_examples(template, examples=examples, query=query)
    prompt = prompt_template.to_prompt()
    expected = textwrap.dedent("""
    Below are few examples of location where item is usually found:

    Example input: pirate
    Example output: ship

    Example input: pilot
    Example output: plane

    Example input: driver
    Example output: car

    Example input: pirate
    Example output: """)

    assert prompt.text == expected


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
