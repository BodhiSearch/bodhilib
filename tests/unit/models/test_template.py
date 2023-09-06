# prompt template
import textwrap

from bodhilib.models import (
    Prompt,
    PromptTemplate,
    prompt_with_examples,
)


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
