import itertools
from typing import Any, Dict, List, NamedTuple, Union


class Prompt(NamedTuple):
    text: str
    role: str = "user"


PromptInput = Union[
    str, List[str], Prompt, List[Prompt], Dict[str, Any], List[Dict[str, Any]]
]


def parse_prompts(input: PromptInput) -> List[Prompt]:
    if type(input) is str:
        return [Prompt(input)]
    if type(input) is Prompt:
        return [input]
    if type(input) is dict:
        return [Prompt(**input)]
    if type(input) is list:
        result = [parse_prompts(p) for p in input]
        return list(itertools.chain(*result))
    raise TypeError(f"Unknown prompt type: {type(input)}")


class PromptTemplate:
    def __init__(self, template: str, role: str = "user"):
        self.template = template
        self.role = role

    def to_prompt(self, **kwargs) -> Prompt:
        return Prompt(self.template.format(**kwargs), role=self.role)
