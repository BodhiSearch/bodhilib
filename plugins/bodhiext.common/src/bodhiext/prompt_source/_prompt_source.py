import importlib.resources
import os
from typing import Any, Dict, List, Optional, Union

from bodhiext.common import __version__
from bodhilib import Filter, PathLike, PromptSource, PromptTemplate, Service, service_provider

from ._yaml import _is_yaml, load_prompt_template_yaml

DEFAULT_TEMPLATES_PKG = "bodhiext.prompt_source.templates"


class LocalPromptSource(PromptSource):
    """BodhiPromptSource is a prompt source implementation by bodhiext."""

    def __init__(self, dir: Optional[PathLike] = None, files: Optional[Union[PathLike, List[PathLike]]] = None) -> None:
        """Initialize LocalPromptSource with the prompt template directory or files.

        If :arg:`dir` is passed, the directory is scanned for all yaml files and loaded as prompt templates.
        If :arg:`files` is passed, the files are loaded as prompt templates.
        If no arguments is passed, the default directory is scanned for all yaml files and loaded as prompt templates.

        Args:
            dir (Optional[:data:`~bodhilib.PathLike`]): Path to the directory containing prompt yaml templates.
                If passed, the directory is scanned for all yaml files and loaded as prompt templates.
            files: Optional[:data:`~bodhilib.PathLike`|List[:data:`~bodhilib.PathLike`]]: Path or list of Path to
                yaml file containing prompt templates.
                If passed, the files are loaded as prompt templates.
        """
        self.files: List[PathLike] = []
        if dir is not None:
            if not os.path.exists(dir):
                raise ValueError(f"Directory does not exists: {dir=}")
            if not os.path.isdir(dir):
                raise ValueError(f"Path is not a directory: {dir=}")
            self.files.extend(self._load_files(dir))
        if files is not None:
            if not isinstance(files, list):
                files = [files]
            missing_files = [file for file in files if not os.path.exists(file)]
            if missing_files:
                raise ValueError(f"File does not exists: {missing_files=}")
            not_files = [file for file in files if not os.path.isfile(file)]
            if not_files:
                raise ValueError(f"Path is not a file: {not_files=}")
            not_yaml = [file for file in files if not _is_yaml(file)]
            if not_yaml:
                raise ValueError(f"File is not in yaml format: {not_yaml=}")
            self.files.extend(files)
        if (files is not None or dir is not None) and not self.files:
            raise ValueError("No files found to load")
        self.templates: Optional[List[PromptTemplate]] = None

    def find(self, filter: Union[Filter, Dict[str, Any]]) -> List[PromptTemplate]:
        if isinstance(filter, dict):
            filter = Filter.from_dict(filter)
        if not self.templates:
            self.templates = self._load_templates()
        return [template for template in self.templates if filter.evaluate(template.metadata)]

    def list_all(self) -> List[PromptTemplate]:
        if not self.templates:
            self.templates = self._load_templates()
        return self.templates

    def _load_files(self, dir: PathLike) -> List[str]:
        return [os.path.join(root, file) for root, _, files in os.walk(dir) for file in files if _is_yaml(file)]

    def _load_templates(self) -> List[PromptTemplate]:
        templates = []
        if self.files:
            for file in self.files:
                parsed_templates = load_prompt_template_yaml(file)
                templates.extend(parsed_templates)
        else:
            templates.extend(self._load_from_pkg(DEFAULT_TEMPLATES_PKG))
        return templates

    def _load_from_pkg(self, pkg: str) -> List[PromptTemplate]:
        templates = []
        with importlib.resources.path(pkg, "") as package_dir:
            package_contents = importlib.resources.contents(pkg)
            for resource_name in package_contents:
                if _is_yaml(resource_name):
                    file_path = package_dir / resource_name
                    parsed_templates = load_prompt_template_yaml(file_path)
                    templates.extend(parsed_templates)
        return templates


@service_provider
def bodhilib_list_services() -> List[Service]:
    """Returns a list of services supported by the plugin.

    Currently supports prompt_source service.
    """
    return [
        Service(
            service_name="local_prompt_source",
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
) -> LocalPromptSource:
    """Returns an instance of BodhiPromptSource."""
    if service_name != "local_prompt_source" or service_type != "prompt_source" or publisher != "bodhiext":
        raise ValueError(
            f"Invalid arguments to the service builder: {service_name=}, {service_type=}, {publisher=}, supported"
            " values are: service_name='local_prompt_source',{service_type='prompt_source', publisher='bodhiext'"
        )

    return LocalPromptSource()
