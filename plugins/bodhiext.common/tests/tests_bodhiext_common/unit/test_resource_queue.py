import tempfile

import pytest
from bodhilib import ResourceQueue, get_resource_queue, local_dir, local_file


@pytest.fixture
def in_memory_queue() -> ResourceQueue:
  return get_resource_queue("in_memory")


def _tmpfile(tmpdir, filename, content):
  tmpfilepath = f"{tmpdir}/{filename}"
  tmpfile = open(tmpfilepath, "w")
  tmpfile.write(content)
  tmpfile.close()
  return tmpfilepath


@pytest.fixture
def tmp_loader_dir():
  with tempfile.TemporaryDirectory() as tmpdir:
    _tmpfile(tmpdir, "test1.txt", "hello world!")
    _tmpfile(tmpdir, "test2.txt", "world hello!")
    tmpdir2 = tempfile.mkdtemp(dir=tmpdir, prefix="tmpdir2")
    _tmpfile(tmpdir2, "test3.txt", "hey world!")
    yield tmpdir


def test_resource_queue_local_dir(in_memory_queue: ResourceQueue, tmp_loader_dir):
  in_memory_queue.push(local_dir(path=tmp_loader_dir, recursive=True))
  docs = in_memory_queue.load()
  assert_docs(docs, tmp_loader_dir)


def test_resource_queue_pop(in_memory_queue: ResourceQueue, tmp_loader_dir):
  in_memory_queue.push(local_dir(path=tmp_loader_dir, recursive=True))
  docs = []
  while (doc := in_memory_queue.pop(timeout=1)) is not None:
    docs.append(doc)
  assert_docs(docs, tmp_loader_dir)


@pytest.mark.asyncio
async def test_resource_queue_async_recursive_true(in_memory_queue: ResourceQueue, tmp_loader_dir):
  in_memory_queue.push(local_dir(path=tmp_loader_dir, recursive=True))
  docs = []
  while (doc := await in_memory_queue.apop(timeout=1)) is not None:
    docs.append(doc)
  assert_docs(docs, tmp_loader_dir)


def assert_docs(docs, tmp_loader_dir):
  assert len(docs) == 3
  docs = sorted(docs, key=lambda x: x.metadata["filename"])
  doc = docs[0]
  assert doc.text == "hello world!"
  assert doc.metadata["filename"] == "test1.txt"
  assert doc.metadata["dirname"] == tmp_loader_dir
  doc = docs[1]
  assert doc.text == "world hello!"
  assert doc.metadata["filename"] == "test2.txt"
  assert doc.metadata["dirname"] == tmp_loader_dir
  doc = docs[2]
  assert doc.text == "hey world!"
  assert doc.metadata["filename"] == "test3.txt"
  assert doc.metadata["dirname"].startswith(tmp_loader_dir + "/tmpdir2")


def test_resource_queue_loads_recursive_false(in_memory_queue: ResourceQueue, tmp_loader_dir):
  in_memory_queue.push(local_dir(path=tmp_loader_dir, recursive=False))
  docs = in_memory_queue.load()
  assert_recursive_false(docs, tmp_loader_dir)


@pytest.mark.asyncio
async def test_in_memory_loads_async_recursive_false(in_memory_queue: ResourceQueue, tmp_loader_dir):
  in_memory_queue.push(local_dir(path=tmp_loader_dir, recursive=False))
  docs = []
  while (doc := await in_memory_queue.apop(timeout=1)) is not None:
    docs.append(doc)
  assert_recursive_false(docs, tmp_loader_dir)


def assert_recursive_false(docs, tmp_loader_dir):
  assert len(docs) == 2
  docs = sorted(docs, key=lambda x: x.metadata["filename"])
  doc = docs[0]
  assert doc.text == "hello world!"
  assert doc.metadata["filename"] == "test1.txt"
  assert doc.metadata["dirname"] == tmp_loader_dir
  doc = docs[1]
  assert doc.text == "world hello!"
  assert doc.metadata["filename"] == "test2.txt"
  assert doc.metadata["dirname"] == tmp_loader_dir


def test_resource_queue_loads_given_files(in_memory_queue: ResourceQueue, tmp_loader_dir):
  in_memory_queue.push(local_file(path=f"{tmp_loader_dir}/test1.txt"))
  docs = in_memory_queue.load()
  assert_loads_given_file(docs, tmp_loader_dir)


@pytest.mark.asyncio
async def test_resource_queue_loads_async_given_files(in_memory_queue: ResourceQueue, tmp_loader_dir):
  in_memory_queue.push(local_file(path=f"{tmp_loader_dir}/test1.txt"))
  docs = []
  while (doc := await in_memory_queue.apop(timeout=1)) is not None:
    docs.append(doc)
  assert_loads_given_file(docs, tmp_loader_dir)


def assert_loads_given_file(docs, tmp_loader_dir):
  assert len(docs) == 1
  doc = docs[0]
  assert doc.text == "hello world!"
  assert doc.metadata["filename"] == "test1.txt"
  assert doc.metadata["dirname"] == tmp_loader_dir


def test_resource_queue_loads_method(in_memory_queue: ResourceQueue, tmp_loader_dir):
  in_memory_queue.push(local_dir(path=tmp_loader_dir, recursive=True))
  docs = in_memory_queue.load()
  assert len(docs) == 3
  docs = sorted(docs, key=lambda x: x.metadata["filename"])
  doc = docs[0]
  assert doc.text == "hello world!"
  assert doc.metadata["filename"] == "test1.txt"
  assert doc.metadata["dirname"] == tmp_loader_dir
  doc = docs[1]
  assert doc.text == "world hello!"
  assert doc.metadata["filename"] == "test2.txt"
  assert doc.metadata["dirname"] == tmp_loader_dir
  doc = docs[2]
  assert doc.text == "hey world!"
  assert doc.metadata["filename"] == "test3.txt"
  assert doc.metadata["dirname"].startswith(tmp_loader_dir + "/tmpdir2")
