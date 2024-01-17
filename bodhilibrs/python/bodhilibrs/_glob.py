import typing
from pathlib import Path
from typing import AsyncIterator, Iterator, List, Literal, Optional, Union, cast

from beartype import beartype
from bodhilib import AbstractResourceProcessor, IsResource
from pydantic import BaseModel, BeforeValidator
from typing_extensions import Annotated

from bodhilibrs.bodhilibrs import GlobProcessor


def _validate_path(input: Union[str, Path]) -> str:
  assert input is not None, "Path is None"
  path = input if isinstance(input, Path) else Path(str(input))
  assert path.exists(), f"Directory does not exist: {str(path)}"
  assert path.is_dir(), f"Path is not a directory: {str(path)}"
  return str(path.absolute())


class GlobInput(BaseModel):
  resource_type: Literal["glob"]
  path: Annotated[str, BeforeValidator(_validate_path)]
  pattern: str
  recursive: bool = False
  exclude_hidden: bool = False


class GlobProcessorRs(AbstractResourceProcessor):
  def __init__(self) -> None:
    self._processor = GlobProcessor()

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
    _ = GlobInput(**resource.metadata)
    return self._processor.process(input, stream)  # type: ignore

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
    _ = GlobInput(**resource.metadata)
    return await self._processor.aprocess(resource, astream)  # type: ignore

  @property
  def supported_types(self) -> List[str]:
    """List of supported resource types."""
    return cast(List[str], self._processor.supported_types)

  @property
  def service_name(self) -> str:
    """Service name of the component."""
    return cast(str, self._processor.service_name)
