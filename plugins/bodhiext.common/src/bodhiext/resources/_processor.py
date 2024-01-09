import os
from glob import glob
from pathlib import Path
from typing import Any, Dict, List, Optional

from bodhilib import (
  RESOURCE_FACTORY,
  RESOURCE_PROCESSOR,
  Document,
  IsResource,
  ResourceProcessor,
  ResourceProcessorFactory,
  ResourceQueue,
  ResourceQueueProcessor,
  Service,
  get_resource_processor,
  list_resource_processors,
  local_file,
  text_plain_file,
)
from bodhilib.logging import logger

from ..common._constants import DEFAULT_RESOURCE_FACTORY

GLOB = "glob"
LOCAL_DIR = "local_dir"
LOCAL_FILE = "local_file"
TEXT_PLAIN = "text_plain"
SUPPORTED_PROCESSORS = {
  f"{GLOB}": [GLOB],
  f"{LOCAL_DIR}": [LOCAL_DIR],
  f"{LOCAL_FILE}": [LOCAL_FILE],
  f"{TEXT_PLAIN}": ["text/plain"],
}
SUPPORTED_EXTS = [".txt"]


class GlobProcessor(ResourceProcessor):
  def __init__(self) -> None:
    super().__init__()

  def process(self, resource: IsResource) -> List[IsResource]:
    if resource.resource_type != "glob":
      raise ValueError(f"Unsupported resource type: {resource.resource_type}, supports {self.supported_types}")
    if "pattern" not in resource.metadata:
      raise ValueError("Resource metadata does not contain key: 'pattern'")
    pattern = resource.metadata["pattern"]
    if pattern is None:
      raise ValueError("Resource metadata key value is None: 'pattern'")
    recursive = resource.metadata.get("recursive", False)
    exclude_hidden = resource.metadata.get("exclude_hidden", True)
    resources: List[IsResource] = []
    for file in glob(pattern, recursive=recursive):
      if file.startswith(".") and exclude_hidden:
        continue
      if os.path.isdir(file):
        continue
      resources.append(local_file(file))
    return resources

  @property
  def supported_types(self) -> List[str]:
    return [GLOB]

  @property
  def service_name(self) -> str:
    return GLOB


class LocalDirProcessor(ResourceProcessor):
  def __init__(self) -> None:
    super().__init__()

  def process(self, resource: IsResource) -> List[IsResource]:
    if resource.resource_type != LOCAL_DIR:
      raise ValueError(f"Unsupported resource type: {resource.resource_type}, supports ['local_dir']")
    if "path" not in resource.metadata:
      raise ValueError("Resource metadata does not contain key: 'path'")
    path = resource.metadata["path"]
    if path is None:
      raise ValueError("Resource metadata key value is None: 'path'")
    if not isinstance(path, Path) and not isinstance(path, str):
      raise ValueError(f"Unsupported path type: {type(path)}, supports str or pathlib.Path")
    path = Path(path)
    if not path.exists():
      raise ValueError(f"Directory does not exist: {path}")
    if not path.is_dir():
      raise ValueError(f"Path is not a directory: {path}")
    recursive = resource.metadata.get("recursive", False)
    exclude_hidden = resource.metadata.get("exclude_hidden", True)
    resources = []
    if not exclude_hidden:
      pattern = "**/.*" if recursive else ".*"
      resources.extend(self._glob_files(path, pattern, recursive))
    pattern = "**/*" if recursive else "*"
    resources.extend(self._glob_files(path, pattern, recursive))
    return resources

  def _glob_files(self, path: Path, pattern: str, recursive: bool) -> List[IsResource]:
    resources: List[IsResource] = []
    for file in glob(str(Path(path).joinpath(pattern)), recursive=recursive):
      if os.path.isdir(file):
        continue
      resources.append(local_file(file))
    return resources

  @property
  def supported_types(self) -> List[str]:
    return [LOCAL_DIR]

  @property
  def service_name(self) -> str:
    return LOCAL_DIR


class LocalFileProcessor(ResourceProcessor):
  def __init__(self) -> None:
    super().__init__()

  def process(self, resource: IsResource) -> List[IsResource]:
    if resource.resource_type != "local_file":
      raise ValueError(f"Unsupported resource type: {resource.resource_type}, supports ['local_file']")
    if "path" not in resource.metadata:
      raise ValueError("Resource metadata does not contain key: 'path'")
    path = resource.metadata["path"]
    if path is None:
      raise ValueError("Resource metadata key value is None: 'path'")
    if not isinstance(path, Path) and not isinstance(path, str):
      raise ValueError(f"Unsupported path type: {type(path)}, supports str or pathlib.Path")
    if isinstance(path, str):
      path = Path(path)
    if not path.exists():
      raise ValueError(f"File does not exist: {path}")
    if not path.is_file():
      raise ValueError(f"Path is not a file: {path}")
    # get path extension
    ext = path.suffix
    if ext == ".txt":
      return [text_plain_file(path=path)]
    raise ValueError(f"Unsupported file extension: {ext}, supports {SUPPORTED_EXTS}")

  @property
  def supported_types(self) -> List[str]:
    return ["local_file"]

  @property
  def service_name(self) -> str:
    return LOCAL_FILE


class TextPlainProcessor(ResourceProcessor):
  def __init__(self) -> None:
    super().__init__()

  def process(self, resource: IsResource) -> List[IsResource]:
    if resource.resource_type != "text/plain":
      raise ValueError(f"Unsupported resource type: {resource.resource_type}, supports ['text/plain']")
    if "path" not in resource.metadata:
      raise ValueError("Resource metadata does not contain key: 'path'")
    path = resource.metadata["path"]
    if path is None:
      raise ValueError("Resource metadata key value is None: 'path'")
    if not isinstance(path, Path) and not isinstance(path, str):
      raise ValueError(f"Unsupported path type: {type(path)}, supports str or pathlib.Path")
    if isinstance(path, str):
      path = Path(path)
    if not path.exists():
      raise ValueError(f"File does not exist: {path}")
    if not path.is_file():
      raise ValueError(f"Path is not a file: {path}")
    return [Document(text=path.read_text(), path=str(path))]

  @property
  def supported_types(self) -> List[str]:
    return ["text/plain"]

  @property
  def service_name(self) -> str:
    return "text_plain"


class DefaultFactory(ResourceProcessorFactory):
  def __init__(self) -> None:
    self.services: Optional[Dict[str, List[Service]]] = None
    self.cached: Dict[str, List[ResourceProcessor]] = {}

  def add_resource_processor(self, processor: ResourceProcessor) -> None:
    for supported_type in processor.supported_types:
      if supported_type not in self.cached:
        self.cached[supported_type] = []
      self.cached[supported_type].append(processor)

  def find(self, resource_type: str) -> List[ResourceProcessor]:
    if resource_type in self.cached:
      return self.cached[resource_type]
    if self.services is None:
      self._set_processors_from_plugins()
    if resource_type not in self.services:  # type: ignore
      logger.warning(f"No processors found for resource type: {resource_type}")
      return []
    processors: List[ResourceProcessor] = [
      get_resource_processor(service.service_name, publisher=service.publisher, version=service.version)
      for service in self.services[resource_type]  # type: ignore
    ]
    self.cached[resource_type] = processors
    return processors

  def _set_processors_from_plugins(self) -> None:
    self.services = self._fetch_processors()

  def _fetch_processors(self) -> Dict[str, List[Service]]:
    processors: Dict[str, List[Service]] = {}
    services = list_resource_processors()
    for service in services:
      if service.metadata is None:
        logger.warning(f"Service {service.publisher}:{service.service_name} does not have metadata")
        continue
      supported_types: List[str] = service.metadata.get("supported_types", [])
      for supported_type in supported_types:
        if supported_type not in processors:
          processors[supported_type] = []
        processors[supported_type].append(service)
    return processors


class DefaultQueueProcessor(ResourceQueueProcessor):
  def __init__(
    self,
    resource_queue: ResourceQueue,
    factory: ResourceProcessorFactory,
    **kwargs: Dict[str, Any],
  ):
    self.resource_queue = resource_queue
    self.factory = factory

  def add_resource_processor(self, processor: ResourceProcessor) -> None:
    return self.factory.add_resource_processor(processor)

  def process(self) -> None:
    while (resource := self.resource_queue.pop(block=False)) is not None:
      results = self._process(resource)
      for result in results:
        self.resource_queue.push(result)

  def start(self) -> None:
    while (resource := self.resource_queue.pop()) is not None:
      logger.info("[start] received item")
      self._process(resource)
      logger.info("[start] process complete")

  async def astart(self) -> None:
    while (resource := await self.resource_queue.apop()) is not None:
      logger.info("[astart] received item")
      processor = self._find_processor(resource)
      if processor is None:
        continue
      results = await processor.aprocess(resource)
      for result in results:
        self.resource_queue.push(result)
      logger.info("[astart] process complete")

  def shutdown(self) -> None:
    raise NotImplementedError()

  def _process(self, resource: IsResource) -> List[IsResource]:
    processor = self._find_processor(resource)
    if processor is None:
      return []
    results = processor.process(resource)
    return results

  def _find_processor(self, resource: IsResource) -> Optional[ResourceProcessor]:
    resource_type = resource.resource_type
    processors = self.factory.find(resource_type)
    if len(processors) == 0:
      # TODO: fail for missing processor
      logger.warning(f"No processor found for {resource_type=}, skipping")
      return None
    if len(processors) > 1:
      logger.warning(f"Multiple processors found for {resource_type=}, picking {processors[0].service_name}")
    return processors[0]


def resource_factory_service_builder(
  *,
  service_name: Optional[str] = DEFAULT_RESOURCE_FACTORY,
  service_type: Optional[str] = RESOURCE_FACTORY,
  publisher: Optional[str] = "bodhiext",
  **kwargs: Dict[str, Any],
) -> DefaultFactory:
  if service_name != RESOURCE_FACTORY:
    raise ValueError(f"Unknown service: {service_name=}")
  if service_type != DEFAULT_RESOURCE_FACTORY:
    raise ValueError(
      f"Service type not supported: {service_type=}, supported service types: {DEFAULT_RESOURCE_FACTORY}"
    )
  if publisher is not None and publisher != "bodhiext":
    raise ValueError(f"Unknown publisher: {publisher=}")
  return DefaultFactory()


def resource_processor_service_builder(
  *,
  service_name: str,
  service_type: Optional[str] = RESOURCE_PROCESSOR,
  publisher: Optional[str] = "bodhiext",
  **kwargs: Dict[str, Any],
) -> ResourceProcessor:
  if service_name not in SUPPORTED_PROCESSORS.keys():
    raise ValueError(f"Unknown service: {service_name=}, supported_processors={SUPPORTED_PROCESSORS.keys()}")
  if service_type != RESOURCE_PROCESSOR:
    raise ValueError(f"Service type not supported: {service_type=}, supported service_type: {RESOURCE_PROCESSOR}")
  if publisher is not None and publisher != "bodhiext":
    raise ValueError(f"Unknown publisher: {publisher=}")
  if service_name == GLOB:
    return GlobProcessor()
  if service_name == LOCAL_DIR:
    return LocalDirProcessor()
  if service_name == LOCAL_FILE:
    return LocalFileProcessor()
  if service_name == TEXT_PLAIN:
    return TextPlainProcessor()
  raise ValueError(f"Unknown service: {service_name=}, {SUPPORTED_PROCESSORS}")
