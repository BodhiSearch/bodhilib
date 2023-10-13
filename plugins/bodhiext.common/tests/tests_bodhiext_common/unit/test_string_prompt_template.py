# prompt template

from bodhiext.prompt_template import StringPromptTemplate
from bodhilib import (
    Prompt,
)


def test_prompt_template_fstring():
    template = StringPromptTemplate(
        prompts=Prompt("Question: What day of the week comes after {day}?\nAnswer: ", role="user", source="input")
    )
    assert template.to_prompts(day="Monday")[0] == Prompt(
        "Question: What day of the week comes after Monday?\nAnswer: ", role="user", source="input"
    )


def test_prompt_template_source_set_correctly():
    template = StringPromptTemplate(
        Prompt("Question: What day of the week comes after {day}?\nAnswer: ", role="user", source="output")
    )
    assert template.to_prompts(day="Monday")[0] == Prompt(
        "Question: What day of the week comes after Monday?\nAnswer: ",
        role="user",
        source="output",
    )


def test_prompt_template_defaults():
    template = StringPromptTemplate(Prompt("simple template"))
    assert template.format == "fstring"


def test_prompt_template_defaults_override():
    template = StringPromptTemplate(
        Prompt("simple template", role="system", source="output"), metadata={"format": "jinja2"}
    )
    assert template.format == "jinja2"
