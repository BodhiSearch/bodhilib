"""module for file data loader plugin for bodhilib."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional

from bodhilib import DataLoader, Document, PathLike
from bodhilib.logging import logger

LoaderCallable = Callable[[Path], List[Document]]

FILE_LOADERS: Dict[str, LoaderCallable] = {
    ".txt": lambda path: _txt_loader(path),
}


def _txt_loader(path: Path) -> List[Document]:
    return [Document(text=path.read_text(), metadata={"filename": path.name, "dirname": str(path.parent)})]


class FileLoader(DataLoader):
    """File data loader plugin for bodhilib.

    Supported file types:
        ".txt": reads txt file and returns a Document with text and metadata
    """

    def __init__(self) -> None:
        self.paths: List[Path] = []

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

    def __iter__(self) -> Iterator[Document]:
        """Return an iterator over the documents in the data loader."""
        return _FileIterator(self.paths)

    def _add_path(self, path: PathLike) -> None:
        if isinstance(path, str):
            path = Path(path)
        if not path.exists():
            raise ValueError(f"Path {path.absolute()} does not exist")
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


class _FileIterator(Iterator[Document]):
    def __init__(self, paths: List[Path]) -> None:
        self.paths = paths
        self._generator = self._doc_generator()

    def __iter__(self) -> Iterator[Document]:
        return self

    def __next__(self) -> Document:
        return next(self._generator)

    def _doc_generator(self) -> Iterator[Document]:
        for path in self.paths:
            if path.suffix in FILE_LOADERS:
                yield from FILE_LOADERS[path.suffix](path)
            else:
                logger.warning(f"For filename={path}, file type {path.suffix} not supported, skipping")


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
