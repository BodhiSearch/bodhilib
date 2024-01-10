import os
import tempfile

import pytest
from bodhilib import IsResource, Resource, local_file

from bodhilibrs import GlobProcessor


@pytest.fixture
def glob_processor() -> GlobProcessor:
  return GlobProcessor()


@pytest.fixture
def all_processors(glob_processor):
  return {
    "glob_processor": glob_processor,
  }


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


def _tmpfile(tmpdir, filename, content):
  tmpfilepath = f"{tmpdir}/{filename}"
  tmpfile = open(tmpfilepath, "w")
  tmpfile.write(content)
  tmpfile.close()
  return tmpfilepath


@pytest.mark.parametrize(
  ["processor", "invalid_resource", "msg"],
  [
    (
      "glob_processor",
      local_file(path="invalid"),
      "Unsupported resource type: local_file, supports ['glob']",
    ),
  ],
)
def test_processor_invalid_resource_type(all_processors, processor: str, invalid_resource: IsResource, msg: str):
  processor = all_processors[processor]
  with pytest.raises(ValueError) as e:
    processor.process(invalid_resource)
  assert isinstance(e.value, ValueError)
  assert str(e.value) == msg


@pytest.mark.parametrize(
  ["processor", "invalid_resource", "msg"],
  [
    ("glob_processor", Resource(resource_type="glob"), "Resource metadata does not contain key: 'pattern'"),
    ("glob_processor", Resource(resource_type="glob", pattern=None), "Resource metadata key value is None: 'pattern'"),
  ],
)
def test_processor_mandatory_args(all_processors, processor: str, invalid_resource: IsResource, msg: str):
  processor = all_processors[processor]
  with pytest.raises(ValueError) as e:
    processor.process(invalid_resource)
  assert str(e.value) == msg
