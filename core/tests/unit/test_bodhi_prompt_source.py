from bodhiext.prompt_source import LocalDirectoryPromptSource
from bodhilib import PromptTemplate

from tests.conftest import TEST_DATA_DIR


def test_bodhi_prompt_source_returns_tagged_template():
    sources = LocalDirectoryPromptSource(source_dir=str(TEST_DATA_DIR / "prompt-sources"))
    result = sources.find("simple")
    assert len(result) == 2
    t1 = """role: system
source: input
text:
you are a helpful AI assistant that explains
complex concepts as if explaining to a 5-yr old
---
role: user
source: input
text: How are rainbows formed?
"""
    t2 = """role: system
source: input
text:
you are a smart and funny AI assistant telling excellent original jokes
---
role: user
source: input
text: Tell me a joke that is on the topic of {{ topic }}, and
involves characters {{ c1 }} and {{ c2 }}, and
uses the world {{ word1 }}
"""
    expected = PromptTemplate(template=t1, format="bodhilib-fstring", metadata={"tags": ["education", "simple"]})
    assert result[0].template == expected.template
    assert result[0] == expected
    assert result[1] == PromptTemplate(template=t2, format="bodhilib-jinja2", metadata={"tags": ["funny", "simple"]})


def test_bodhi_prompt_soruce_list_all():
    sources = LocalDirectoryPromptSource(source_dir=str(TEST_DATA_DIR / "prompt-sources"))
    result = sources.list_all()
    assert len(result) == 3
