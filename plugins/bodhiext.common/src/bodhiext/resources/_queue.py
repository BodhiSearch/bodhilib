"""module for file data loader plugin for bodhilib."""
from __future__ import annotations

import asyncio
import queue
import typing
from queue import Queue
from typing import (
  Any,
  Dict,
  Literal,
  Optional,
)

from bodhilib import RESOURCE_QUEUE, IsResource, ResourceQueue

from ..common._constants import IN_MEMORY_SERVICE


class InMemoryResourceQueue(ResourceQueue):
  """InMemoryResource queue.

  Supported file types:
      ".txt": reads txt file and returns a Document with text and metadata
  """

  def __init__(self, maxsize: Optional[int] = 0) -> None:
    maxsize = maxsize if maxsize is not None else 0
    self.queue: Queue[IsResource] = Queue(maxsize=maxsize)

  def push(self, resource: IsResource) -> None:
    """Add a resource to the queue with given data using :resource:`~bodhilib.IsResource` protocol.

    Args:
        resource (:class:`~bodhilib.IsResource`): Resource to be added to the queue.

    Raises:
        ValueError: if any of the files or the dir provided does not exists.
    """
    self.queue.put(resource)

  @typing.overload
  def pop(self, block: Literal[True] = ..., timeout: Optional[float] = ...) -> IsResource:
    ...

  @typing.overload
  def pop(self, block: Literal[False] = ..., timeout: Optional[float] = ...) -> Optional[IsResource]:
    ...

  def pop(self, block: Optional[bool] = True, timeout: Optional[float] = None) -> Optional[IsResource]:
    """Pop a document from the queue."""
    try:
      block = block if block is not None else True
      resource = self.queue.get(block=block, timeout=timeout)
      self.queue.task_done()
      return resource
    except queue.Empty:
      return None

  @typing.overload
  async def apop(self, block: Literal[True] = ..., timeout: Optional[float] = ...) -> IsResource:
    ...

  @typing.overload
  async def apop(self, block: Literal[False] = ..., timeout: Optional[float] = ...) -> Optional[IsResource]:
    ...

  async def apop(self, block: Optional[bool] = True, timeout: Optional[float] = None) -> Optional[IsResource]:
    """Pop a document from the queue asynchronously."""
    loop = asyncio.get_running_loop()
    resource = await loop.run_in_executor(None, self._pop_from_queue, timeout)
    self.queue.task_done()
    return resource

  def shutdown(self) -> None:
    raise NotImplementedError("shutdown not implemented")  # TODO

  def _pop_from_queue(self, timeout: Optional[float]) -> Optional[IsResource]:
    try:
      resource = self.queue.get(timeout=timeout)
      return resource
    except queue.Empty:
      return None


def resource_queue_service_builder(
  *,
  service_name: Optional[str] = IN_MEMORY_SERVICE,
  service_type: Optional[str] = RESOURCE_QUEUE,
  publisher: Optional[str] = "bodhiext",
  **kwargs: Dict[str, Any],
) -> InMemoryResourceQueue:
  """Return a in-memory resource queue service builder.

  Builds and returns an instance of :class:`~bodhiext.data_loader._file.InMemoryResourceQueue`
  with the passed arguments.

  Returns:
      InMemoryResourceQueue (:class:`~bodhiext.data_loader._file.InMemoryResourceQueue`): InMemoryResourceQueue instance
        to process resources in-memory.
  """
  if service_name != IN_MEMORY_SERVICE:
    raise ValueError(f"Unknown service: {service_name=}")
  if service_type != RESOURCE_QUEUE:
    raise ValueError(f"Service type not supported: {service_type=}, supported service types: {RESOURCE_QUEUE}")
  if publisher is not None and publisher != "bodhiext":
    raise ValueError(f"Unknown publisher: {publisher=}")
  return InMemoryResourceQueue()
