from pathlib import Path
from typing import List

import pytest
from bodhiext.resources import DefaultFactory, DefaultQueueProcessor, InMemoryResourceQueue
from bodhilib import DOCUMENT, IsResource, ResourceProcessor, text_plain_file


class _DocProcessor(ResourceProcessor):
  def __init__(self):
    self.queue = []

  def process(self, resource: IsResource) -> List[IsResource]:
    self.queue.append(resource)
    return []

  async def aprocess(self, resource: IsResource) -> List[IsResource]:
    self.queue.append(resource)
    return []

  @property
  def supported_types(self) -> List[str]:
    return [DOCUMENT]

  @property
  def service_name(self) -> str:
    return "_test_doc_processor"


@pytest.fixture
def docs_queue():
  return _DocProcessor()


@pytest.fixture
def resource_queue():
  return InMemoryResourceQueue()


@pytest.fixture
def queue_processor(resource_queue, docs_queue):
  factory = DefaultFactory()
  factory.add_resource_processor(docs_queue)
  queue_processor = DefaultQueueProcessor(resource_queue, factory)
  return queue_processor


def test_queue_processor_processes_to_doc(tmpdir, queue_processor, resource_queue, docs_queue):
  _tmpfile(tmpdir, "test.txt", "test")
  source_file = Path(tmpdir).joinpath("test.txt")
  resource = text_plain_file(source_file)
  resource_queue.push(resource)
  queue_processor.process()
  assert len(docs_queue.queue) == 1
  document = docs_queue.queue[0]
  assert document.text == "test"
  assert document.resource_type == "document"
  assert document.metadata["path"] == str(source_file)
  assert document.metadata["resource_type"] == DOCUMENT


def _tmpfile(tmpdir, filename, content):
  tmpfilepath = f"{tmpdir}/{filename}"
  tmpfile = open(tmpfilepath, "w")
  tmpfile.write(content)
  tmpfile.close()
  return tmpfilepath
