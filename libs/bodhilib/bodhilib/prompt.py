import itertools
import textwrap
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel

from bodhilib.logging import logger

Role = Literal["system", "ai", "user"]
Source = Literal["input", "output"]


class Prompt(BaseModel):
    text: str
    role: Role
    source: Source

    def __init__(self, text: str, role: Optional[Role] = "user", source: Optional[Source] = "input"):
        role = role or "user"
        source = source or "input"
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


Engine = Literal["default", "jinja2"]


class PromptTemplate:
    def __init__(
        self,
        template: str,
        role: Optional[Role] = None,
        source: Optional[Source] = None,
        engine: Optional[Engine] = "default",
        **kwargs: Dict[str, Any],
    ) -> None:
        self.template = template
        self.role = role
        self.source = source
        self.engine = engine
        self.kwargs = kwargs

    def to_prompt(self, **all_vars: Dict[str, Any]) -> Prompt:
        if self.engine == "default":
            return Prompt(self.template.format(**all_vars), role=self.role, source=self.source)
        if self.engine == "jinja2":
            try:
                import jinja2  # noqa: F401
            except ImportError as e:
                logger.error(
                    "jinja2 is required for advance prompt templates. "
                    "Install the jinja2 dependency separately using `pip install jinja2`, "
                    "or install the additional dependencies on bodhilib.prompt package using `pip install"
                    " bodhilib[prompt]`."
                )
                raise e
            from jinja2 import Template

            template = Template(textwrap.dedent(self.template))
            result = template.render(self.kwargs)
            return Prompt(result, role=self.role, source=self.source)
        raise ValueError(f"Unknown engine {self.engine}")


def user_prompt(text: str) -> Prompt:
    return Prompt(text=text, role="user", source="input")


def prompt_with_examples(
    template: str, role: Optional[Role] = None, source: Optional[Source] = None, **kwargs: Dict[str, Any]
) -> PromptTemplate:
    return PromptTemplate(template, role=role, source=source, engine="jinja2", **kwargs)


def prompt_output(text: str, role: Optional[Role] = "ai", source: Optional[Source] = "output") -> Prompt:
    return Prompt(text=text, role=role, source=source)
