import itertools
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, validator

from ._common import StrEnumMixin, strenum_validator


class Role(StrEnumMixin, str, Enum):
    """Role of the prompt.

    Used for fine-grain control over "role" instructions to the LLM service.
    Can be one of - *'system', 'ai', or 'user'*.
    """

    SYSTEM = "system"
    AI = "ai"
    USER = "user"


class Source(StrEnumMixin, str, Enum):
    """Source of the prompt.

    If the prompt is given as input by the user, then *source="input"*,
    or if the prompt is generated as response by the LLM service, then *source="output"*.
    """

    INPUT = "input"
    OUTPUT = "output"


class Prompt(BaseModel):
    """Prompt encapsulating input/output schema to interact with LLM service."""

    text: str
    """The text or content or input component of the prompt."""

    role: Role = Role.USER
    """The role of the prompt.

    Defaults to :obj:`Role.USER`."""

    source: Source = Source.INPUT
    """The source of the prompt.

    Defaults to :obj:`Source.INPUT`."""

    _role_validator = validator("role", pre=True, always=True, allow_reuse=True)(
        lambda cls, value: strenum_validator(Role, value)
    )
    _source_validator = validator("source", pre=True, always=True, allow_reuse=True)(
        lambda cls, value: strenum_validator(Source, value)
    )

    # overriding __init__ to provide positional argument construction for prompt. E.g. `Prompt("text")`
    def __init__(
        self,
        text: str,
        role: Optional[Union[Role, str]] = Role.USER,
        source: Optional[Union[Source, str]] = Source.INPUT,
    ):
        """Initialize a prompt.

        Args:
            text (str): text of the prompt
            role (Role): role of the prompt.

                Role can be given as one of the allowed string value ["system", "ai", "user"]
                or as a Role enum [:obj:`Role.SYSTEM`, :obj:`Role.AI`, :obj:`Role.USER`].

                The string is converted to Role enum. If the string value is not one of the allowed values,
                then a ValueError is raised.
            source (Source): source of the prompt.

                Source can be given as a one of the allowed string value ["input", "output"]
                or as a Source enum [:obj:`Source.INPUT`, :obj:`Source.OUTPUT`].

                The string is converted to Source enum. If the string value is not one of the allowed values,
                then a ValueError is raised.

        Raises:
            ValueError: If the role or source is not one of the allowed values.
        """
        role = role or Role.USER
        source = source or Source.INPUT
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


def prompt_user(text: str) -> Prompt:
    """Factory method to generate user prompt from string.

    Args:
        text: text of the prompt
    Returns:
        Prompt: Prompt object generated from the text. Defaults role="user" and source="input".
    """
    return Prompt(text=text, role=Role.USER, source=Source.INPUT)


def prompt_output(text: str) -> Prompt:
    """Factory method to generate output prompts.

    Generates a prompt with source="output". Mainly by LLMs to generate output prompts.
    """
    return Prompt(text=text, role=Role.AI, source=Source.OUTPUT)
