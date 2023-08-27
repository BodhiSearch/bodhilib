import itertools
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, validator

Source = Literal["input", "output"]


class Role(str, Enum):
    """Role of the prompt.

    Used for fine-grain control over "role" instructions to the LLM service.
    Can be one of - "system", "ai", or "user".
    """

    SYSTEM = "system"
    AI = "ai"
    USER = "user"

    def __str__(self) -> str:
        """Returns the string value of the role enum."""
        return self.value

    def __eq__(self, other: Any) -> bool:
        """Compares the role to other role and string values."""
        if isinstance(other, str):
            return self.value == other
        elif isinstance(other, Role):
            return self.value == other.value
        return False


class Prompt(BaseModel):
    """Prompt encapsulating input/output schema to interact with LLM service."""

    text: str
    """The text or content or input component of the prompt."""

    role: Role = Role.USER
    """The role of the prompt.

    Used for fine-grain control over role instructions to the LLM service.
    Can be one of - "system", "ai", or "user".

    Role can be given as a string or as a Role enum. The string is converted to Role enum.
    If the string value is not one of the allowed values, then a ValueError is raised.

    Defaults to "user"."""

    source: Source = "input"
    """The source of the prompt, links to where it was generated.

    If given as input by the user, then source="input",
    or generated as response by the LLM service, then source="output".

    Defaults to "input"."""

    # overriding __init__ to provide positional argument construction for prompt. E.g. `Prompt("text")`
    def __init__(self, text: str, role: Optional[Union[Role, str]] = Role.USER, source: Optional[Source] = "input"):
        """Initialize a prompt.

        Args:
            text: text of the prompt
            role: role of the prompt. Can be one of "system", "ai", "user". Defaults to "user".
            source: source of the prompt. Can be one of "input", "output". Defaults to "input".
        """
        role = role or Role.USER
        source = source or "input"
        super().__init__(text=text, role=role, source=source)

    @validator("role", pre=True, always=True)
    def convert_to_role_enum(cls, value: Any) -> Role:
        if isinstance(value, str):
            try:
                return Role(value)
            except ValueError as e:
                raise ValueError(f"Invalid role value. Allowed values are {[e.value for e in Role]}") from e
        elif isinstance(value, Role):
            return value
        else:
            raise ValueError("Invalid type for role")


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
    return Prompt(text=text, role="user", source="input")


def prompt_output(text: str, role: Optional[Role] = Role.AI, source: Optional[Source] = "output") -> Prompt:
    """Factory method to generate output prompts.

    Generates a prompt with source="output". Mainly by LLMs to generate output prompts.
    """
    return Prompt(text=text, role=role, source=source)
