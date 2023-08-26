import textwrap

from bodhilib.models import Prompt, PromptTemplate, parse_prompts, prompt_with_examples

from tests.prompt_utils import default_system_prompt, default_user_prompt


def test_parse_prompt_from_str():
    prompts = parse_prompts(default_user_prompt)
    assert len(prompts) == 1
    assert prompts[0] == Prompt(default_user_prompt)


def test_empty_list():
    prompts = parse_prompts([])
    assert prompts == []


def test_parse_prompt_from_list_of_str():
    prompts = parse_prompts([default_user_prompt])
    assert len(prompts) == 1
    assert prompts[0] == Prompt(default_user_prompt)


def test_parse_prompt_from_prompt():
    input = Prompt(default_user_prompt)
    prompts = parse_prompts(input)
    assert len(prompts) == 1
    assert prompts[0] == input


def test_parse_prompt_from_dict():
    input = {"text": default_user_prompt}
    prompts = parse_prompts(input)
    assert len(prompts) == 1
    assert prompts[0] == Prompt(default_user_prompt, "user")


def test_parse_prompt_from_dict_full():
    input = {"text": default_system_prompt, "role": "system"}
    prompts = parse_prompts(input)
    assert len(prompts) == 1
    assert prompts[0] == Prompt(default_system_prompt, "system")


def test_parse_prompt_mix():
    prompts = parse_prompts(
        [
            default_user_prompt,
            {"text": default_system_prompt, "role": "system"},
            Prompt(default_user_prompt, "system"),
        ]
    )
    assert len(prompts) == 3
    assert prompts[0] == Prompt(default_user_prompt)
    assert prompts[1] == Prompt(default_system_prompt, "system")
    assert prompts[2] == Prompt(default_user_prompt, "system")


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
