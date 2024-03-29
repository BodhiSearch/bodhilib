import typing
from pathlib import Path
from typing import AsyncIterator, Iterator, List, Literal, Optional, Union

from beartype import beartype
from bodhilib import AbstractResourceProcessor, IsResource, local_file
from pydantic import BaseModel, BeforeValidator
from typing_extensions import Annotated

from bodhilibrs.bodhilibrs import find_files

from ._aiter import AsyncListIterator


def _validate_path(input: Union[str, Path]) -> str:
  assert input is not None, "Path is None"
  path = input if isinstance(input, Path) else Path(str(input))
  path = path.expanduser()
  path = path.resolve()
  assert path.exists(), f"Directory does not exist: {str(path)}"
  assert path.is_dir(), f"Path is not a directory: {str(path)}"
  return str(path)


class GlobInput(BaseModel):
  resource_type: Literal["glob"]
  path: Annotated[str, BeforeValidator(_validate_path)]
  pattern: str
  recursive: bool = False
  exclude_hidden: bool = False


class GlobProcessorRs(AbstractResourceProcessor):
  @typing.overload
  def process(self, resource: IsResource, stream: Optional[Literal[False]] = ...) -> List[IsResource]:
    ...

  @typing.overload
  def process(self, resource: IsResource, stream: Literal[True]) -> Iterator[IsResource]:
    ...

  @beartype
  def process(
    self, resource: IsResource, stream: Optional[bool] = False
  ) -> Union[List[IsResource], Iterator[IsResource]]:
    """Process the resource and return a Document or another resource for further processing."""
    input = GlobInput(**resource.metadata)
    files: List[str] = find_files(input.path, input.pattern, input.recursive, not input.exclude_hidden)
    resources: List[IsResource] = [local_file(path) for path in files]
    if stream:
      resources_iter: Iterator[IsResource] = iter(resources)
      return resources_iter
    return resources

  @typing.overload
  async def aprocess(self, resource: IsResource, astream: Optional[Literal[False]] = ...) -> List[IsResource]:
    ...

  @typing.overload
  async def aprocess(self, resource: IsResource, astream: Literal[True]) -> AsyncIterator[IsResource]:
    ...

  @beartype
  async def aprocess(
    self, resource: IsResource, astream: Optional[bool] = False
  ) -> Union[List[IsResource], AsyncIterator[IsResource]]:
    """Process the resource and return a Document or another resource for further processing."""
    local_files = self.process(resource, False)
    if astream:
      return AsyncListIterator[IsResource](local_files)
    return local_files

  @property
  def supported_types(self) -> List[str]:
    """List of supported resource types."""
    return ["glob"]

  @property
  def service_name(self) -> str:
    """Service name of the component."""
    return self.__class__.__name__
