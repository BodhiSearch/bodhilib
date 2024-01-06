"""module for file data loader plugin for bodhilib."""
from __future__ import annotations

import asyncio
import os
import queue
from pathlib import Path
from queue import Queue
from typing import (
  Any,
  AsyncGenerator,
  Awaitable,
  Callable,
  Dict,
  List,
  Optional,
)

import aiofiles
from bodhilib import DataLoader, Document, PathLike
from bodhilib.logging import logger

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


class FileLoader(DataLoader):
  """File data loader plugin for bodhilib.

  Supported file types:
      ".txt": reads txt file and returns a Document with text and metadata
  """

  def __init__(self, max_size: Optional[int] = 0) -> None:
    self.queue: Queue[Path] = Queue(maxsize=max_size)

  def push(  # type: ignore
    self,
    *,
    files: Optional[List[PathLike]] = None,
    file: Optional[PathLike] = None,
    dir: Optional[PathLike] = None,
    recursive: bool = False,
  ) -> None:
    """Add a file or directory resource to the data loader with given :data:`~bodhilib.PathLike` location.

    Args:
        files (Optional[List[PathLike]]): A list of file paths to add.
        file (Optional[PathLike]): A file path to add.
        dir (Optional[PathLike]): A directory path to add.
        recursive (bool): Whether to add files recursively from the directory.

    Raises:
        ValueError: if any of the files or the dir provided does not exists.
    """
    if file:
      self._add_path(file)
    elif files:
      for path in files:
        self._add_path(path)
    elif dir:
      self._add_dir(dir, recursive)
    else:
      logger.info("paths or path must be provided")

  def pop(self, timeout: Optional[float] = None) -> Optional[Document]:
    """Pop a document from the data loader."""
    try:
      path = self.queue.get(timeout=timeout)
      document = self._get_document(path)
      self.queue.task_done()
      return document
    except queue.Empty:
      return None

  async def apop(self, timeout: Optional[float] = None) -> AsyncGenerator[Document, None]:  # type: ignore
    """Pop a document from the data loader asynchronously."""
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
    raise NotImplementedError("shutdown not implemented") # TODO

  def _pop_from_queue(self, timeout):
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


def file_loader_service_builder(
  *,
  service_name: Optional[str] = "file",
  service_type: Optional[str] = "data_loader",
  publisher: Optional[str] = "bodhiext",
  **kwargs: Dict[str, Any],
) -> FileLoader:
  """Return a file data loader service builder.

  Builds and returns an instance of :class:`~bodhiext.data_loader._file.FileLoader`
  with the passed arguments.

  Returns:
      FileLoader (:class:`~bodhiext.data_loader._file.FileLoader`): FileLoader instance to load local files
          as resources.
  """
  if service_name != "file":
    raise ValueError(f"Unknown service: {service_name=}")
  if service_type != "data_loader":
    raise ValueError(f"Service type not supported: {service_type=}, supported service types: data_loader")
  if publisher is not None and publisher != "bodhiext":
    raise ValueError(f"Unknown publisher: {publisher=}")
  return FileLoader()
