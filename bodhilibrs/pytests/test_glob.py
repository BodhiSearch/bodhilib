import os
import tempfile

import pytest
from bodhilib import glob_pattern
from pydantic import ValidationError

from bodhilibrs import GlobProcessorRs
from bodhilibrs._glob import GlobInput


@pytest.fixture
def glob_processor() -> GlobProcessorRs:
  return GlobProcessorRs()


@pytest.fixture
def all_processors(glob_processor):
  return {
    "glob_processor": glob_processor,
  }


@pytest.fixture
def invalid_resources(tmp_test_dir):
  resource = glob_pattern(tmp_test_dir, "*.txt", True, False)
  resource.resource_type = "local_file"
  return {"glob": resource}


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


def test_glob_input_invalid_resource_type(tmp_test_dir):
  with pytest.raises(ValidationError) as e:
    _ = GlobInput(resource_type="invalid", path=tmp_test_dir, pattern="*.txt", recursive=True, exclude_hidden=False)
  assert isinstance(e.value, ValidationError)
  assert e.value.error_count() == 1
  errors = e.value.errors()[0]
  assert errors["type"] == "literal_error"
  assert errors["msg"] == "Input should be 'glob'"


def test_glob_input_path_missing(tmp_test_dir):
  with pytest.raises(ValidationError) as e:
    _ = GlobInput(resource_type="glob", pattern="*.txt", recursive=True, exclude_hidden=False)
  assert isinstance(e.value, ValidationError)
  assert e.value.error_count() == 1
  errors = e.value.errors()[0]
  assert errors["type"] == "missing"
  assert errors["msg"] == "Field required"
