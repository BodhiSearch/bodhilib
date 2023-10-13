from __future__ import annotations

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
    cast,
)

from bodhilib import Prompt, PromptTemplate, TextLike, yaml_dump
from jinja2 import Template
from pydantic import BaseModel, Field

# region prompt template
#######################################################################################################################


class StringPromptTemplate(BaseModel, PromptTemplate):
    """PromptTemplate used for generating prompts using a template."""

    prompts: List[Prompt] = Field(default_factory=list)
    """A list of templated prompts."""

    metadata_: Dict[str, Any] = Field(default_factory=dict)
    """Metadata associated with the template."""

    params: Dict[str, Any] = Field(default_factory=dict)
    """The variables to be used for rendering the template."""

    # overriding __init__ to provide positional argument construction for prompt template.
    # E.g. `PromptTemplate("my template {context}")`
    def __init__(
        self,
        prompts: Union[List[Prompt], Prompt],
        *,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Dict[str, Any],
    ) -> None:
        """Initializes a prompt template.

        Args:
            prompts: a list of templated prompts
            metadata: the metadata associated with the prompt template
            **kwargs: additional arguments to be used for rendering the template
        """
        if isinstance(prompts, Prompt):
            prompts = [prompts]
        super().__init__(
            prompts=prompts,
            metadata_=metadata or {},
            params=kwargs,
        )

    @property
    def template(self) -> str:
        """Returns the template as string representation."""
        return yaml_dump({"prompts": [prompt.dict() for prompt in self.prompts]})

    @property
    def metadata(self) -> Dict[str, Any]:
        return self.metadata_

    @property
    def format(self) -> str:
        return cast(str, self.metadata.get("format", "fstring"))

    # TODO: return vars by parsing the templates
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
            return [Prompt(prompt.text.format(**all_args), prompt.role, prompt.source) for prompt in self.prompts]
        if self.format == "jinja2":
            results = []
            for prompt in self.prompts:
                template = Template(prompt.text)
                text = template.render(**all_args)
                result = Prompt(text, role=prompt.role, source=prompt.source)
                results.append(result)
            return results
        raise ValueError(f"Unknown format {self.format}, allowed values: ['fstring', 'jinja2']")


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
