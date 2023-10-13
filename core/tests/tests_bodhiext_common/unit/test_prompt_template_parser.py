import pytest
from bodhiext.prompt_source import parse_prompt_template_yaml
from bodhiext.prompt_template import StringPromptTemplate
from bodhilib import Prompt

from tests_bodhiext_common.conftest import TEST_DATA_DIR


@pytest.mark.parametrize(
    ["filename", "format"], [("simple-fstring-prompt.yaml", "fstring"), ("simple-jinja2-prompt.yaml", "jinja2")]
)
def test_prompt_template_parser_parses_simple_templated_prompt(filename, format):
    template = str((TEST_DATA_DIR / "prompt-templates" / filename).resolve())
    actual = parse_prompt_template_yaml(template)
    prompts = [
        Prompt(
            "you are a helpful AI assistant that explains complex concepts as if explaining to a 5-yr old",
            role="system",
            source="input",
        )
    ]
    assert actual[0].to_prompts(adjective="helpful") == prompts
    assert actual[0].metadata == {"tags": ["education", "physics", "simple"], "format": format}


def test_parse_prompt_template_jinja2_few_shot_template():
    template = str((TEST_DATA_DIR / "prompt-templates" / "jinja2-few-shot.yaml").resolve())
    actual = parse_prompt_template_yaml(template)
    examples = [
        {"input": "pirate", "output": "ship"},
        {"input": "pilot", "output": "plane"},
        {"input": "driver", "output": "car"},
    ]
    assert actual[0].to_prompts(examples=examples, query="pirate") == [
        Prompt(
            """Below are few examples of location where item is usually found:

Example input: pirate
Example output: ship

Example input: pilot
Example output: plane

Example input: driver
Example output: car

Example input: pirate
Example output:""",
            role="user",
            source="input",
        )
    ]


def test_parse_prompt_template_collects_metadata():
    filename = "supports-unknown-metafields.yaml"
    template = str((TEST_DATA_DIR / "prompt-templates" / filename).resolve())
    actual = parse_prompt_template_yaml(template)
    assert len(actual) == 1
    assert actual[0].metadata == {"tags": ["education", "physics", "simple"], "format": "jinja2", "unknown": "field"}


def test_prompt_template_parser_with_multiple_templates():
    template = str((TEST_DATA_DIR / "prompt-templates" / "multiple-templates.yaml").resolve())
    p1 = [
        Prompt(
            "you are a helpful AI assistant that explains\ncomplex concepts as if explaining to a 5-yr old\n",
            "system",
            "input",
        ),
        Prompt("what is a black hole?\nExplain in detail in minimum of 3000 words.\n", "user", "input"),
    ]
    p2 = [
        Prompt("you are a helpful AI assistant that entertains using funny jokes", "system", "input"),
        Prompt(
            (
                "tell me a joke, the joke should be-\n"
                "- about astronatus and cowboys\n"
                "- should be funny\n"
                "- should be related to australia\n"
            ),
            "user",
            "input",
        ),
    ]
    pt1 = StringPromptTemplate(prompts=p1, metadata={"tags": ["education", "physics", "simple"], "format": "jinja2"})
    pt2 = StringPromptTemplate(prompts=p2, metadata={"tags": ["entertainment", "jokes", "funny"], "format": "fstring"})
    actual = parse_prompt_template_yaml(template)
    assert len(actual) == 2
    assert actual[0] == pt1
    assert actual[1] == pt2
