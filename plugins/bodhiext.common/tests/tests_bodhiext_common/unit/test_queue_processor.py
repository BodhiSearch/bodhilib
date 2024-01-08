from pathlib import Path
import pytest
from bodhiext.resources import DefaultQueueProcessor, InMemoryResourceQueue, DefaultFactory
from bodhilib import text_plain_file


class _TestQueue:
  def __init__(self):
    self.queue = []

  def push(self, item):
    self.queue.append(item)


@pytest.fixture
def docs_queue():
  return _TestQueue()


@pytest.fixture
def resource_queue():
  return InMemoryResourceQueue()


@pytest.fixture
def queue_processor(resource_queue, docs_queue):
  factory = DefaultFactory()
  queue_processor = DefaultQueueProcessor(resource_queue, factory)
  queue_processor.add_docs_queue(docs_queue)
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
  assert document.metadata == {"path": str(source_file), "resource_type": "document"}


def _tmpfile(tmpdir, filename, content):
  tmpfilepath = f"{tmpdir}/{filename}"
  tmpfile = open(tmpfilepath, "w")
  tmpfile.write(content)
  tmpfile.close()
  return tmpfilepath
