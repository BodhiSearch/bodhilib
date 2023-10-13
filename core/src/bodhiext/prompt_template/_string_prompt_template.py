from __future__ import annotations

import re
import textwrap
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
)

from bodhilib import Prompt, PromptTemplate, Role, Source, TextLike
from jinja2 import Template
from pydantic import BaseModel, Field

# region prompt template
#######################################################################################################################

TemplateFormat = Literal["fstring", "jinja2", "bodhilib-fstring", "bodhilib-jinja2"]


class StringPromptTemplate(BaseModel, PromptTemplate):
    """PromptTemplate used for generating prompts using a template."""

    template_: str = Field(alias="template")
    """Template for generating prompts."""

    metadata_: Dict[str, Any] = Field(default_factory=dict)
    """Metadata associated with the template."""

    format_: TemplateFormat = Field("fstring", alias="format")
    """Template format to use for rendering."""

    role: Role = Role.USER
    """Role of the prompt."""

    source: Source = Source.INPUT
    """Source of the prompt."""

    params: Dict[str, Any] = Field(default_factory=dict)
    """The variables to be used for rendering the template."""

    # overriding __init__ to provide positional argument construction for prompt template.
    # E.g. `PromptTemplate("my template {context}")`
    def __init__(
        self,
        template: str,
        *,
        id: Optional[str] = None,
        role: Optional[Role] = None,
        source: Optional[Source] = None,
        format: Optional[TemplateFormat] = "fstring",
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Dict[str, Any],
    ) -> None:
        """Initializes a prompt template.

        Args:
            template: template string
            id: optional identifier for the template
            role: role of the prompt, defaults to "user"
            source: source of the prompt, defaults to "input"
            format: format to use for rendering the template.
            metadata: the metadata associated with the prompt template
            **kwargs: additional arguments to be used for rendering the template
        """
        role = role or Role.USER
        source = source or Source.INPUT
        super().__init__(
            template=template,
            id=id,
            role=role,
            source=source,
            format=format,
            metadata=metadata or {},
            params=kwargs,
        )

    @property
    def template(self) -> str:
        return self.template_
    
    @property
    def metadata(self) -> Dict[str, Any]:
        return self.metadata_
    
    @property
    def format(self) -> str:
        return self.format_

    @property
    def vars(self) -> Dict[str, Any]:
        return {}

    def to_prompts(self, **kwargs: Dict[str, Any]) -> List[Prompt]:
        """Converts the PromptTemplate into a Prompt.

        Args:
            kwargs: all variables to be used for rendering the template

        Returns:
            Prompt: prompt generated from the template
        """
        all_args = {**self.params, **kwargs}
        all_args = {k: v for k, v in all_args.items() if v is not None}
        if self.format == "fstring":
            return [Prompt(self.template.format(**all_args), role=self.role, source=self.source)]
        if self.format == "jinja2":
            template = Template(textwrap.dedent(self.template))
            result = template.render(**all_args)
            return [Prompt(result, role=self.role, source=self.source)]
        if self.format.startswith("bodhilib-"):
            return self._bodhilib_template_to_prompt(**all_args)
        raise ValueError(
            f"Unknown format {self.format}, allowed values: ['fstring', 'jinja2', 'bodhilib-fstring',"
            " 'bodhilib-jinja2']"
        )

    def _bodhilib_template_to_prompt(self, **kwargs: Dict[str, Any]) -> List[Prompt]:
        prompt_fields = ["text", "role", "source"]
        prompt_fields_matcher = "^" + "|".join(prompt_fields) + ":"
        lines = self.template.splitlines(keepends=True)
        result: List[Prompt] = []
        prompt: Dict[str, Any] = {"text": []}
        text_start = False
        for line in lines:
            if re.match(prompt_fields_matcher, line):
                field, value = line.split(":")
                if field == "text":
                    text_start = True
                    prompt["text"].append(value)
                else:
                    text_start = False
                    prompt[field] = value.strip()
                continue
            if line.startswith("---"):
                if not prompt["text"]:
                    text_start = False
                    prompt = {"text": []}
                    continue
                p = self._build_prompt(prompt, **kwargs)
                result.append(p)
                text_start = False
                prompt = {"text": []}
                continue
            if text_start:
                prompt["text"].append(line)
        if prompt["text"]:
            p = self._build_prompt(prompt, **kwargs)
            result.append(p)
        return result

    def _build_prompt(self, prompt: Dict[str, Any], **kwargs: Dict[str, Any]) -> Prompt:
        template = "".join(prompt.pop("text"))
        if self.format == "bodhilib-fstring":
            text = template.format(**kwargs)
        elif self.format == "bodhilib-jinja2":
            jinja_template = Template(template, keep_trailing_newline=True)
            text = jinja_template.render(**kwargs)
        else:
            raise ValueError("Unknown format {self.format}, allowed values: ['bodhilib-fstring', 'bodhilib-jinja2']")
        return Prompt(text, **prompt)


# TODO deprecate and remove
def prompt_with_examples(template: str, **kwargs: Dict[str, Any]) -> StringPromptTemplate:
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
    return StringPromptTemplate(template, role=role, source=source, format="jinja2", **kwargs)  # type: ignore


# TODO deprecate and remove
def prompt_with_extractive_qna(
    template: str, contexts: List[TextLike], **kwargs: Dict[str, Any]
) -> StringPromptTemplate:
    """Factory method to generate a prompt template for extractive QnA.

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
    return StringPromptTemplate(
        template, role=role, source=source, format="jinja2", contexts=contexts, **kwargs  # type: ignore
    )


# endregion
