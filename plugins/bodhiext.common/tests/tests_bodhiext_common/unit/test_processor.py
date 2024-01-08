import os
import tempfile
from pathlib import Path

import pytest
from bodhiext.resources import GlobProcessor, LocalDirProcessor, LocalFileProcessor, TextPlainProcessor
from bodhilib import (
  LOCAL_FILE,
  Document,
  IsResource,
  Resource,
  ResourceProcessor,
  glob_pattern,
  local_dir,
  local_file,
  text_plain_file,
)


@pytest.fixture
def local_dir_processor():
  return LocalDirProcessor()


@pytest.fixture
def glob_processor():
  return GlobProcessor()


@pytest.fixture
def local_file_processor():
  return LocalFileProcessor()


@pytest.fixture
def text_plain_processor():
  return TextPlainProcessor()


@pytest.fixture
def all_processors(local_dir_processor, glob_processor, local_file_processor, text_plain_processor):
  return {
    "local_dir_processor": local_dir_processor,
    "glob_processor": glob_processor,
    "local_file_processor": local_file_processor,
    "text_plain_processor": text_plain_processor,
  }


def _tmpfile(tmpdir, filename, content):
  tmpfilepath = f"{tmpdir}/{filename}"
  tmpfile = open(tmpfilepath, "w")
  tmpfile.write(content)
  tmpfile.close()
  return tmpfilepath


@pytest.fixture
def tmp_test_dir():
  with tempfile.TemporaryDirectory() as tmpdir:
    _tmpfile(tmpdir, "test1.txt", "hello world!")
    _tmpfile(tmpdir, "test2.txt", "world hello!")
    _tmpfile(tmpdir, ".test3.txt", "world hello!")
    tmpdir2 = f"{tmpdir}/tmpdir2"
    os.mkdir(tmpdir2)
    _tmpfile(tmpdir2, "test3.txt", "hey world!")
    _tmpfile(tmpdir2, ".test4.txt", "hey world!")
    yield tmpdir


@pytest.mark.parametrize(
  ["processor", "invalid_resource", "msg"],
  [
    (
      "local_dir_processor",
      local_file(path="invalid"),
      "Unsupported resource type: local_file, supports ['local_dir']",
    ),
    (
      "glob_processor",
      local_file(path="invalid"),
      "Unsupported resource type: local_file, supports ['glob']",
    ),
    (
      "local_file_processor",
      local_dir(path="invalid"),
      "Unsupported resource type: local_dir, supports ['local_file']",
    ),
    (
      "text_plain_processor",
      local_file(path="invalid"),
      "Unsupported resource type: local_file, supports ['text/plain']",
    ),
  ],
)
def test_processor_invalid_resource_type(all_processors, processor: str, invalid_resource: IsResource, msg: str):
  processor = all_processors[processor]
  with pytest.raises(ValueError) as e:
    processor.process(invalid_resource)
  assert str(e.value) == msg


@pytest.mark.parametrize(
  ["processor", "invalid_resource", "msg"],
  [
    ("glob_processor", Resource(resource_type="glob"), "Resource metadata does not contain key: 'pattern'"),
    ("glob_processor", Resource(resource_type="glob", pattern=None), "Resource metadata key value is None: 'pattern'"),
    ("local_dir_processor", Resource(resource_type="local_dir"), "Resource metadata does not contain key: 'path'"),
    (
      "local_dir_processor",
      Resource(resource_type="local_dir", path=None),
      "Resource metadata key value is None: 'path'",
    ),
    (
      "local_dir_processor",
      Resource(resource_type="local_dir", path=object()),
      "Unsupported path type: <class 'object'>, supports str or pathlib.Path",
    ),
    (
      "local_dir_processor",
      Resource(resource_type="local_dir", path="missing"),
      "Directory does not exist: missing",
    ),
    ("local_file_processor", Resource(resource_type="local_file"), "Resource metadata does not contain key: 'path'"),
    (
      "local_file_processor",
      Resource(resource_type="local_file", path=None),
      "Resource metadata key value is None: 'path'",
    ),
    (
      "local_file_processor",
      Resource(resource_type="local_file", path=object()),
      "Unsupported path type: <class 'object'>, supports str or pathlib.Path",
    ),
    (
      "local_file_processor",
      Resource(resource_type="local_file", path="missing.txt"),
      "File does not exist: missing.txt",
    ),
    ("text_plain_processor", Resource(resource_type="text/plain"), "Resource metadata does not contain key: 'path'"),
    (
      "text_plain_processor",
      Resource(resource_type="text/plain", path=None),
      "Resource metadata key value is None: 'path'",
    ),
    (
      "text_plain_processor",
      Resource(resource_type="text/plain", path=object()),
      "Unsupported path type: <class 'object'>, supports str or pathlib.Path",
    ),
    (
      "text_plain_processor",
      Resource(resource_type="text/plain", path="missing.txt"),
      "File does not exist: missing.txt",
    ),
  ],
)
def test_processor_mandatory_args(all_processors, processor: str, invalid_resource: IsResource, msg: str):
  processor = all_processors[processor]
  with pytest.raises(ValueError) as e:
    processor.process(invalid_resource)
  assert str(e.value) == msg


@pytest.mark.parametrize(
  ["processor", "resource_type", "msg"],
  [
    ("local_file_processor", "local_file", "Path is not a file: {tmpdir}"),
    ("text_plain_processor", "text/plain", "Path is not a file: {tmpdir}"),
  ],
)
def test_processor_is_dir(tmpdir, all_processors, processor, resource_type, msg):
  processor = all_processors[processor]
  with pytest.raises(ValueError) as e:
    processor.process(Resource(resource_type=resource_type, path=Path(tmpdir)))
  assert str(e.value) == msg.format(tmpdir=tmpdir)


@pytest.mark.parametrize(
  ["processor", "resource_type", "msg"],
  [
    ("local_dir_processor", "local_dir", "Path is not a directory: {tmpfile}"),
  ],
)
def test_processor_is_file(tmpdir, all_processors, processor, resource_type, msg):
  processor = all_processors[processor]
  tmpfile = Path(tmpdir).joinpath("test1.txt")
  _tmpfile(tmpdir, "test1.txt", "hello world!")
  with pytest.raises(ValueError) as e:
    processor.process(Resource(resource_type=resource_type, path=tmpfile))
  assert str(e.value) == msg.format(tmpfile=tmpfile)


def test_processor_local_dir_recursive(tmp_test_dir, local_dir_processor: ResourceProcessor):
  resource = local_dir(path=tmp_test_dir, recursive=True, exclude_hidden=True)
  resources = local_dir_processor.process(resource)
  assert len(resources) == 3
  assert all([resource.resource_type == LOCAL_FILE for resource in resources])
  paths = sorted([resource.metadata["path"] for resource in resources])
  assert paths == [f"{tmp_test_dir}/test1.txt", f"{tmp_test_dir}/test2.txt", f"{tmp_test_dir}/tmpdir2/test3.txt"]


def test_processor_local_dir_recursive_hidden(tmp_test_dir, local_dir_processor: ResourceProcessor):
  resource = local_dir(path=tmp_test_dir, recursive=True, exclude_hidden=False)
  resources = local_dir_processor.process(resource)
  assert len(resources) == 5
  assert all([resource.resource_type == LOCAL_FILE for resource in resources])
  paths = sorted([resource.metadata["path"] for resource in resources])
  assert paths == [
    f"{tmp_test_dir}/.test3.txt",
    f"{tmp_test_dir}/test1.txt",
    f"{tmp_test_dir}/test2.txt",
    f"{tmp_test_dir}/tmpdir2/.test4.txt",
    f"{tmp_test_dir}/tmpdir2/test3.txt",
  ]


def test_processor_local_dir_not_recursive(tmp_test_dir, local_dir_processor: ResourceProcessor):
  resource = local_dir(path=tmp_test_dir, recursive=False, exclude_hidden=True)
  resources = local_dir_processor.process(resource)
  assert len(resources) == 2
  assert all([resource.resource_type == LOCAL_FILE for resource in resources])
  paths = sorted([resource.metadata["path"] for resource in resources])
  assert paths == [f"{tmp_test_dir}/test1.txt", f"{tmp_test_dir}/test2.txt"]


def test_processor_local_dir_not_recursive_hidden(tmp_test_dir, local_dir_processor: ResourceProcessor):
  resource = local_dir(path=tmp_test_dir, recursive=False, exclude_hidden=False)
  resources = local_dir_processor.process(resource)
  assert len(resources) == 3
  assert all([resource.resource_type == LOCAL_FILE for resource in resources])
  paths = sorted([resource.metadata["path"] for resource in resources])
  assert paths == [f"{tmp_test_dir}/.test3.txt", f"{tmp_test_dir}/test1.txt", f"{tmp_test_dir}/test2.txt"]


def test_processor_glob_pattern_not_recursive(tmp_test_dir, glob_processor: ResourceProcessor):
  resource = glob_pattern(f"{str(tmp_test_dir)}/**", recursive=False)
  resources = glob_processor.process(resource)
  assert len(resources) == 2
  assert all([resource.resource_type == LOCAL_FILE for resource in resources])
  paths = sorted([resource.metadata["path"] for resource in resources])
  assert paths == [f"{tmp_test_dir}/test1.txt", f"{tmp_test_dir}/test2.txt"]


def test_processor_glob_pattern_recursive(tmp_test_dir, glob_processor: ResourceProcessor):
  resource = glob_pattern(f"{str(tmp_test_dir)}/**", recursive=True)
  resources = glob_processor.process(resource)
  assert len(resources) == 3
  assert all([resource.resource_type == LOCAL_FILE for resource in resources])
  paths = sorted([resource.metadata["path"] for resource in resources])
  assert paths == [f"{tmp_test_dir}/test1.txt", f"{tmp_test_dir}/test2.txt", f"{tmp_test_dir}/tmpdir2/test3.txt"]


def test_processor_local_file_txt(tmp_test_dir, local_file_processor: ResourceProcessor):
  resource = local_file_processor.process(local_file(path=f"{str(tmp_test_dir)}/test1.txt"))
  assert len(resource) == 1
  assert resource[0].resource_type == "text/plain"
  assert resource[0].metadata["path"] == Path(f"{tmp_test_dir}/test1.txt")


def test_processor_text_plain(tmp_test_dir, text_plain_processor: ResourceProcessor):
  resource = text_plain_processor.process(text_plain_file(path=Path(tmp_test_dir).joinpath("test1.txt")))
  assert len(resource) == 1
  assert isinstance(resource[0], Document)
  assert resource[0].metadata == {"resource_type": "document", "path": str(Path(tmp_test_dir).joinpath("test1.txt"))}


def test_processor_text_plain_unsupported_ext(tmp_test_dir, local_file_processor: ResourceProcessor):
  _tmpfile(tmp_test_dir, "test1.csv", "hello,world")
  with pytest.raises(ValueError) as e:
    _ = local_file_processor.process(local_file(path=Path(tmp_test_dir).joinpath("test1.csv")))
  assert str(e.value) == "Unsupported file extension: .csv, supports ['.txt']"
