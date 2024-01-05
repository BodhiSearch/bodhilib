"""module for file data loader plugin for bodhilib."""
from __future__ import annotations

import os
import threading
from collections import deque
from pathlib import Path
from typing import (
  Any,
  AsyncGenerator,
  Awaitable,
  Callable,
  Deque,
  Dict,
  Generator,
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

  def __init__(self) -> None:
    self.paths: Deque[Path] = deque()
    self.lock = threading.Lock()

  def add_resource(  # type: ignore
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

  def pop(self) -> Generator[Document, None, None]:
    """Pop a document from the data loader."""
    while True:
      with self.lock:
        if not self.paths:
          break
        path = self.paths.popleft()
        document = self._get_document(path)
        if document is not None:
          yield document

  async def apop(self) -> AsyncGenerator[Document, None]:  # type: ignore
    """Pop a document from the data loader asynchronously."""
    while True:
      with self.lock:
        if not self.paths:
          break
        path = self.paths.popleft()
        document = await self._async_get_document(path)
        if document is not None:
          yield document

  def _add_path(self, path: PathLike) -> None:
    if isinstance(path, str):
      path = Path(path)
    if not path.exists():
      raise ValueError(f"Path {path.absolute()} does not exist")
    with self.lock:
      self.paths.append(path)

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
