import tempfile

import pytest
from bodhilib import get_data_loader


@pytest.fixture
def file_loader():
  return get_data_loader("file")


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


def test_file_loader_recursive_true(file_loader, tmp_loader_dir):
  # initialize file loader and add dir as resource with recursive=True
  file_loader.add_resource(dir=tmp_loader_dir, recursive=True)

  # iterate over documents and check if they are loaded correctly
  docs = file_loader.load()
  assert_docs(docs, tmp_loader_dir)


@pytest.mark.asyncio
async def test_file_loader_async_recursive_true(file_loader, tmp_loader_dir):
  file_loader.add_resource(dir=tmp_loader_dir, recursive=True)
  docs = [doc async for doc in file_loader.apop()]
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


def test_file_loader_loads_recursive_false(file_loader, tmp_loader_dir):
  file_loader.add_resource(dir=tmp_loader_dir, recursive=False)
  docs = file_loader.load()
  assert_recursive_false(docs, tmp_loader_dir)


@pytest.mark.asyncio
async def test_file_loader_loads_async_recursive_false(file_loader, tmp_loader_dir):
  file_loader.add_resource(dir=tmp_loader_dir, recursive=False)
  docs = [doc async for doc in file_loader.apop()]
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


def test_file_loader_loads_given_files(file_loader, tmp_loader_dir):
  file_loader.add_resource(file=f"{tmp_loader_dir}/test1.txt")
  docs = file_loader.load()
  assert_loads_given_file(docs, tmp_loader_dir)


@pytest.mark.asyncio
async def test_file_loader_loads_async_given_files(file_loader, tmp_loader_dir):
  file_loader.add_resource(file=f"{tmp_loader_dir}/test1.txt")
  docs = [doc async for doc in file_loader.apop()]
  assert_loads_given_file(docs, tmp_loader_dir)


def assert_loads_given_file(docs, tmp_loader_dir):
  assert len(docs) == 1
  doc = docs[0]
  assert doc.text == "hello world!"
  assert doc.metadata["filename"] == "test1.txt"
  assert doc.metadata["dirname"] == tmp_loader_dir


def test_file_loader_loads_method(file_loader, tmp_loader_dir):
  file_loader.add_resource(dir=tmp_loader_dir, recursive=True)
  docs = file_loader.load()
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
