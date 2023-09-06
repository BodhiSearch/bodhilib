from __future__ import annotations

import textwrap
from typing import Any, Dict, Literal, Optional

from bodhilib.logging import logger

from ._prompt import Prompt, Role, Source

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


def prompt_with_examples(template: str, **kwargs: Dict[str, Any]) -> PromptTemplate:
    """Factory method to generate a prompt template with examples.

    Prompt uses `jinja2` template engine to generate prompt with examples.

    Args:
        template: a `jinja2` compliant template string to loop through examples
        **kwargs: additional arguments to be used for rendering the template.
            Can also contain `role` and `source` to override the default values.

    Returns:
        PromptTemplate: configured prompt template to generate prompt with examples
    """
    # pop role from kwargs or get None
    role = kwargs.pop("role", None)
    source = kwargs.pop("source", None)
    return PromptTemplate(template, role=role, source=source, engine="jinja2", **kwargs)  # type: ignore
