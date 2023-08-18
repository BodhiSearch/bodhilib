import itertools
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel


class Prompt(BaseModel):
    text: str
    role: Literal["ai", "user", "system"]
    source: Literal["input", "output"]

    def __init__(self, text: str, role: Optional[str] = "user", source: Optional[str] = "input"):
        super().__init__(text=text, role=role, source=source)


PromptInput = Union[str, List[str], Prompt, List[Prompt], Dict[str, Any], List[Dict[str, Any]]]


def parse_prompts(input: PromptInput) -> List[Prompt]:
    if isinstance(input, str):
        return [Prompt(input)]
    if isinstance(input, Prompt):
        return [input]
    if isinstance(input, dict):
        return [Prompt(**input)]
    if isinstance(input, list):
        result = [parse_prompts(p) for p in input]
        return list(itertools.chain(*result))
    raise TypeError(f"Unknown prompt type: {type(input)}")


class PromptTemplate:
    def __init__(self, template: str, role: str = "user"):
        self.template = template
        self.role = role

    def to_prompt(self, **kwargs: Dict[str, Any]) -> Prompt:
        return Prompt(self.template.format(**kwargs), role=self.role)
