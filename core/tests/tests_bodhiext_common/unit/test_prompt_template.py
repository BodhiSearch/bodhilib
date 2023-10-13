# prompt template
import textwrap

import pytest
from bodhiext.prompt_template import StringPromptTemplate, parse_prompt_template, prompt_with_examples
from bodhilib import (
    Prompt,
)

from tests_bodhiext_common.conftest import TEST_DATA_DIR


def test_prompt_template():
    template = StringPromptTemplate(
        "Question: What day of the week comes after {day}?\nAnswer: ", role="user", source="input"
    )
    assert template.to_prompts(day="Monday")[0] == Prompt(
        "Question: What day of the week comes after Monday?\nAnswer: ", role="user", source="input"
    )


def test_prompt_template_source_set_correctly():
    template = StringPromptTemplate(
        "Question: What day of the week comes after {day}?\nAnswer: ", role="user", source="output"
    )
    assert template.to_prompts(day="Monday")[0] == Prompt(
        "Question: What day of the week comes after Monday?\nAnswer: ",
        role="user",
        source="output",
    )


def test_prompt_template_defaults():
    template = StringPromptTemplate("simple template")
    assert template.format == "fstring"


def test_prompt_template_defaults_override():
    template = StringPromptTemplate("simple template", role="system", source="output", format="jinja2")
    assert template.role == "system"
    assert template.source == "output"
    assert template.format == "jinja2"


@pytest.mark.parametrize("filename", ["simple-prompt.txt", "simple-prompt-fstring.txt"])
def test_prompt_template_with_bodhilib_format(filename):
    templates = parse_prompt_template((TEST_DATA_DIR / "prompt-templates" / filename).read_text())
    assert len(templates) == 1
    prompts = templates[0].to_prompts()
    assert len(prompts) == 1
    # jinja2 strips the trailing newlines
    assert prompts[0] == Prompt(
        "\nyou are a helpful AI assistant that explains\ncomplex concepts as if explaining to a 5-yr old\n",
        "system",
        "input",
    )


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
    prompt = prompt_template.to_prompts()[0]
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
