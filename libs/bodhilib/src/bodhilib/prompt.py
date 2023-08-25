"""Prompt module. Contains classes and functions related to prompt."""
import itertools
import textwrap
from typing import Any, Dict, List, Literal, Optional, Union

from bodhilib.logging import logger
from pydantic import BaseModel

Role = Literal["system", "ai", "user"]
Source = Literal["input", "output"]


class Prompt(BaseModel):
    """Prompt encapsulating inputs to interact with LLM."""

    text: str
    role: Role
    source: Source

    def __init__(self, text: str, role: Optional[Role] = "user", source: Optional[Source] = "input"):
        """Initialize a prompt.

        Args:
            text: text of the prompt
            role: role of the prompt. Can be one of "system", "ai", "user". Defaults to "user".
            source: source of the prompt. Can be one of "input", "output". Defaults to "input".
        """
        role = role or "user"
        source = source or "input"
        super().__init__(text=text, role=role, source=source)


PromptInput = Union[str, List[str], Prompt, List[Prompt], Dict[str, Any], List[Dict[str, Any]]]


def parse_prompts(input: PromptInput) -> List[Prompt]:
    """Parses from the PromptInput to List[Prompt]."""
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
    """PromptTemplate used for generating prompts using a template."""

    def __init__(
        self,
        template: str,
        role: Optional[Role] = None,
        source: Optional[Source] = None,
        engine: Optional[Engine] = "default",
        **kwargs: Dict[str, Any],
    ) -> None:
        """Initializes a prompt template.

        Args:
            template: template string
            role: role of the prompt.
            source: source of the prompt.
            engine: engine to use for rendering the template.
            **kwargs: additional arguments to be used for rendering the template
        """
        self.template = template
        self.role = role
        self.source = source
        self.engine = engine
        self.kwargs = kwargs

    def to_prompt(self, **kwargs: Dict[str, Any]) -> Prompt:
        """Converts the PromptTemplate into a Prompt.

        Args:
            kwargs: all variables to be used for rendering the template
        Returns:
            Prompt: prompt generated from the template
        """
        if self.engine == "default":
            return Prompt(self.template.format(**{**self.kwargs, **kwargs}), role=self.role, source=self.source)
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
    """Factory method to generate user prompt from string.

    Args:
        text: text of the prompt
    Returns:
        Prompt: Prompt object generated from the text. Defaults role="user" and source="input".
    """
    return Prompt(text=text, role="user", source="input")


def prompt_with_examples(template: str, **kwargs: Dict[str, Any]) -> PromptTemplate:
    """Factory method to generate a prompt template with examples.

    Prompt uses `jinja2` template engine to generate prompt with examples.

    Args:
        template: a `jinja2` compliant template string to loop through examples
        **kwargs: additional arguments to be used for rendering the template.
            Can also contain `role` and `source` to override the default values.
    """
    # pop role from kwargs or get None
    role = kwargs.pop("role", None)
    source = kwargs.pop("source", None)
    return PromptTemplate(template, role=role, source=source, engine="jinja2", **kwargs)  # type: ignore


def prompt_output(text: str, role: Optional[Role] = "ai", source: Optional[Source] = "output") -> Prompt:
    """Factory method to generate output prompts.

    Generates a prompt with source="output". Mainly by LLMs to generate output prompts.
    """
    return Prompt(text=text, role=role, source=source)
