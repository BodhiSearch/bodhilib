import itertools
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel

Role = Literal["system", "ai", "user"]
Source = Literal["input", "output"]


class Prompt(BaseModel):
    """Prompt encapsulating input/output schema to interact with LLM service."""

    text: str
    """The text or content or input component of the prompt."""

    role: Role = "user"
    """The role of the prompt.

    Used for fine-grain control over role instructions to the LLM model.
    Can be one of - "system", "ai", or "user".

    Defaults to "user"."""

    source: Source = "input"
    """The source of the prompt, links to where it was generated.

    If given as input by the user, then source="input",
    or generated as response by the LLM service, then source="output".

    Defaults to "input"."""

    # overriding __init__ to provide positional argument construction for prompt. E.g. `Prompt("text")`
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


def prompt_user(text: str) -> Prompt:
    """Factory method to generate user prompt from string.

    Args:
        text: text of the prompt
    Returns:
        Prompt: Prompt object generated from the text. Defaults role="user" and source="input".
    """
    return Prompt(text=text, role="user", source="input")


def prompt_output(text: str, role: Optional[Role] = "ai", source: Optional[Source] = "output") -> Prompt:
    """Factory method to generate output prompts.

    Generates a prompt with source="output". Mainly by LLMs to generate output prompts.
    """
    return Prompt(text=text, role=role, source=source)
