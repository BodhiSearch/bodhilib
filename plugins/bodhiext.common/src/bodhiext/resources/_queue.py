"""module for file data loader plugin for bodhilib."""
from __future__ import annotations

import asyncio
import os
import queue
import typing
from pathlib import Path
from queue import Queue
from typing import (
  Any,
  Awaitable,
  Callable,
  Dict,
  List,
  Optional,
)

import aiofiles
from bodhilib import LOCAL_DIR, LOCAL_FILE, RESOURCE_QUEUE, Document, IsResource, PathLike, ResourceQueue
from bodhilib.logging import logger

from ..common._constants import IN_MEMORY_SERVICE

LoaderCallable = Callable[[Path], Document]
AwaitLoaderCallable = Callable[[Path], Awaitable[Document]]


async def _async_txt_loader(path: Path) -> Document:
  async with aiofiles.open(path, mode="r") as file:
    text = await file.read()
    return Document(text=text, metadata={"filename": path.name, "dirname": str(path.parent)})


def _txt_loader(path: Path) -> Document:
  return Document(text=path.read_text(), metadata={"filename": path.name, "dirname": str(path.parent)})


FILE_LOADERS: Dict[str, LoaderCallable] = {
  ".txt": _txt_loader,
}

ASYNC_FILE_LOADERS: Dict[str, AwaitLoaderCallable] = {
  ".txt": _async_txt_loader,
}


class InMemoryResourceQueue(ResourceQueue):
  """InMemoryResource queue.

  Supported file types:
      ".txt": reads txt file and returns a Document with text and metadata
  """

  def __init__(self, maxsize: Optional[int] = 0) -> None:
    maxsize = maxsize if maxsize is not None else 0
    self.queue: Queue[Path] = Queue(maxsize=maxsize)

  def push(self, resource: IsResource) -> None:
    """Add a resource to the queue with given data using :resource:`~bodhilib.IsResource` protocol.

    Args:
        resource (:class:`~bodhilib.IsResource`): Resource to be added to the queue.

    Raises:
        ValueError: if any of the files or the dir provided does not exists.
    """
    if resource.resource_type == LOCAL_FILE:
      self._add_path(resource.metadata["path"])
    elif resource.resource_type == LOCAL_DIR:
      self._add_dir(resource.metadata["path"], resource.metadata["recursive"])
    else:
      logger.info(f"unknown resource type {resource.resource_type}, skipping")

  @typing.overload
  def pop(self, timeout: None = ...) -> Document:
    ...

  @typing.overload
  def pop(self, timeout: float = ...) -> Optional[Document]:
    ...

  def pop(self, timeout: Optional[float] = None) -> Optional[Document]:
    """Pop a document from the queue."""
    while True:
      try:
        path = self.queue.get(timeout=timeout)
        document = self._get_document(path)
        self.queue.task_done()
        if document is not None:
          return document
      except queue.Empty:
        return None

  @typing.overload
  async def apop(self, timeout: None = ...) -> Document:
    ...

  @typing.overload
  async def apop(self, timeout: float = ...) -> Optional[Document]:
    ...

  async def apop(self, timeout: Optional[float] = None) -> Optional[Document]:
    """Pop a document from the queue asynchronously."""
    while True:
      loop = asyncio.get_running_loop()
      path = await loop.run_in_executor(None, self._pop_from_queue, timeout)
      if path is None:
        return None
      document = await self._async_get_document(path)
      self.queue.task_done()
      if document is not None:
        return document

  def load(self) -> List[Document]:
    """Returns the document as list."""
    docs = []
    while True:
      try:
        path = self.queue.get(block=False)
        doc = self._get_document(path)
        if doc is not None:
          docs.append(doc)
      except queue.Empty:
        break
    return docs

  def shutdown(self) -> None:
    raise NotImplementedError("shutdown not implemented")  # TODO

  def _pop_from_queue(self, timeout: Optional[float]) -> Optional[Path]:
    try:
      path = self.queue.get(timeout=timeout)
      return path
    except queue.Empty:
      return None

  def _add_path(self, path: PathLike) -> None:
    if isinstance(path, str):
      path = Path(path)
    if not path.exists():
      raise ValueError(f"Path {path.absolute()} does not exist")
    self.queue.put(path)

  def _add_dir(self, dir: PathLike, recursive: bool) -> None:
    if isinstance(dir, str):
      dir = Path(dir)
    if not os.path.isdir(dir):
      raise ValueError(f"passed argument {dir=} is not a directory")
    if recursive:
      for root, _, files in os.walk(dir):
        for file in files:
          self._add_path(os.path.join(root, file))
    else:
      for file in os.listdir(dir):
        self._add_path(os.path.join(dir, file))

  def _get_document(self, path: Path) -> Optional[Document]:
    if path.suffix in FILE_LOADERS:
      return FILE_LOADERS[path.suffix](path)
    logger.warning(f"For filename={path}, file type {path.suffix} not supported, skipping")
    return None

  async def _async_get_document(self, path: Path) -> Optional[Document]:
    if path.suffix in ASYNC_FILE_LOADERS:
      loader = ASYNC_FILE_LOADERS[path.suffix]
      document = await loader(path)
      return document
    logger.warning(f"For filename={path}, file type {path.suffix} not supported, skipping")
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
