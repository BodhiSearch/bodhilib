import pytest
from bodhilib import PromptTemplate, parse_prompt_template

from tests.conftest import TEST_DATA_DIR


@pytest.mark.parametrize("filename", ["simple-prompt.txt", "ignores-unknown-metafields.txt"])
def test_prompt_template_parser_parses_simple_prompt(filename):
    # read file and close handle in single line
    template = (TEST_DATA_DIR / "prompt-templates" / filename).read_text()
    result = r"""role: system
source: input
text:
you are a helpful AI assistant that explains
complex concepts as if explaining to a 5-yr old
"""
    assert parse_prompt_template(template) == [
        PromptTemplate(
            template=result,
            role="user",
            source="input",
            format="bodhilib-jinja2",
            tags=["education", "physics", "simple"],
        )
    ]


def test_prompt_template_parser_with_multiple_templates():
    template = (TEST_DATA_DIR / "prompt-templates" / "multiple-templates.txt").read_text()
    t1 = r"""role: system
source: input
text:
you are a helpful AI assistant that explains
complex concepts as if explaining to a 5-yr old
---
role: user
source: input
text: what is a black hole?
Explain in detail in minimum of 3000 words.
"""
    t2 = r"""role: system
source: input
text:
you are a helpful AI assistant that entertains using funny jokes
---
role: user
source: input
text: tell me a joke, the joke should be-
- about astronatus and cowboys
- should be funny
- should be related to australia
"""
    pt1 = PromptTemplate(template=t1, format="bodhilib-jinja2", tags=["education", "physics", "simple"])
    pt2 = PromptTemplate(template=t2, format="bodhilib-fstring", tags=["entertainment", "jokes", "funny"])
    assert parse_prompt_template(template) == [pt1, pt2]


def test_prompt_template_parser_escape_break_sequences():
    template = (TEST_DATA_DIR / "prompt-templates" / "escape-break-sequences.txt").read_text()
    t1 = r"""role: system
source: input
text:
you are a helpful +++ AI assistant that
\--- completes high school --- level homework
---
role: user
source: input
text:
What happens when you + and ++ and +++ numbers
\+++ together? Does it matter if you --- or
\---
"""
    t2 = r"""role: user
source: input
text: what is 2---2 and 2+++2 and 2===2
"""
    pt1 = PromptTemplate(template=t1, format="bodhilib-fstring", tags=["entertainment", "jokes", "funny"])
    pt2 = PromptTemplate(template=t2, format="bodhilib-fstring", tags=["simple"])
    assert parse_prompt_template(template) == [pt1, pt2]
