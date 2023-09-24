import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from bodhilib import BasePromptSource, Service, parse_prompt_template, service_provider
from bodhilib._models import PromptTemplate

from ._version import __version__

CURRENT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_TEMPLATES_DIR = CURRENT_DIR / "data"


class LocalDirectoryPromptSource(BasePromptSource):
    """BodhiPromptSource is a prompt source implementation by bodhiext."""

    def __init__(self, source_dir: Optional[str] = None) -> None:
        """Initializes BodhiPromptSource.

        Args:
            source_dir (Optional[str]): Path to the directory containing prompt templates. Defaults to None.
                If None, defaults to bodhiext's default prompt template directory.
        """
        if source_dir is None:
            source_dir = str(DEFAULT_TEMPLATES_DIR)
        self.source_dir = source_dir
        self.templates: Optional[List[PromptTemplate]] = None

    def _find(self, tags: List[str]) -> List[PromptTemplate]:
        if not self.templates:
            self.templates = self._load_templates()
        return [template for template in self.templates if set(tags).issubset(set(template.tags))]

    def _list_all(self) -> List[PromptTemplate]:
        if not self.templates:
            self.templates = self._load_templates()
        return self.templates

    def _load_templates(self) -> List[PromptTemplate]:
        templates = []
        # recursively find all files in the source_dir and parse templates
        for root, _, files in os.walk(self.source_dir):
            for file in files:
                with open(os.path.join(root, file), "r") as f:
                    text = f.read()
                    parsed_templates = parse_prompt_template(text)
                    templates.extend(parsed_templates)
        return templates


@service_provider
def bodhilib_list_services() -> List[Service]:
    """Returns a list of services supported by the plugin.

    Currently supports prompt_source service.
    """
    return [
        Service(
            service_name="local_dir_prompt_source",
            service_type="prompt_source",
            publisher="bodhiext",
            service_builder=bodhi_prompt_source_builder,
            version=__version__,
        )
    ]


def bodhi_prompt_source_builder(
    *,
    service_name: Optional[str] = None,
    service_type: Optional[str] = None,
    publisher: Optional[str] = None,  # QdrantClient fails if passed extra args
    version: Optional[str] = None,  # QdrantClient fails if passed extra args
    **kwargs: Dict[str, Any],
) -> LocalDirectoryPromptSource:
    """Returns an instance of BodhiPromptSource."""
    if service_name != "local_dir_prompt_source" or service_type != "prompt_source" or publisher != "bodhiext":
        raise ValueError(
            f"Invalid arguments to the service builder: {service_name=}, {service_type=}, {publisher=}, supported"
            " values are: service_name='local_dir_prompt_source',{service_type='prompt_source', publisher='bodhiext'"
        )

    return LocalDirectoryPromptSource()
