import os
import tempfile
from pathlib import Path
from typing import AsyncIterator, Iterator, List

import pytest
from beartype.roar import BeartypeCallHintParamViolation
from bodhiext.resources import GlobProcessor, LocalDirProcessor, LocalFileProcessor, TextPlainProcessor
from bodhilib import (
  DOCUMENT,
  LOCAL_FILE,
  Document,
  Resource,
  ResourceProcessor,
  glob_pattern,
  local_dir,
  local_file,
  text_plain_file,
)
from pydantic import ValidationError


@pytest.fixture
def local_dir_processor():
  return LocalDirProcessor()


@pytest.fixture
def glob_processor():
  return GlobProcessor()


@pytest.fixture
def glob_processor_rs():
  # from bodhilibrs.bodhilibrs import GlobProcessor
  from bodhilibrs import GlobProcessorRs as GlobProcessor

  return GlobProcessor()


@pytest.fixture
def local_file_processor():
  return LocalFileProcessor()


@pytest.fixture
def text_plain_processor():
  return TextPlainProcessor()


@pytest.fixture
def all_processors(local_dir_processor, glob_processor, glob_processor_rs, local_file_processor, text_plain_processor):
  return {
    "local_dir_processor": local_dir_processor,
    "glob_processor": glob_processor,
    "glob_processor_rs": glob_processor_rs,
    "local_file_processor": local_file_processor,
    "text_plain_processor": text_plain_processor,
  }


@pytest.fixture
def tmp_test_dir():
  with tempfile.TemporaryDirectory() as tmpdir:
    _tmpfile(tmpdir, "test1.txt", "hello world!")
    _tmpfile(tmpdir, "test2.csv", "world hello!")
    _tmpfile(tmpdir, ".test3.txt", "world hello!")
    tmpdir2 = f"{tmpdir}/tmpdir2"
    os.mkdir(tmpdir2)
    _tmpfile(tmpdir2, "test4.txt", "hey world!")
    _tmpfile(tmpdir2, ".test5.txt", "hey world!")
    yield tmpdir


def _tmpfile(tmpdir, filename, content):
  tmpfilepath = f"{tmpdir}/{filename}"
  tmpfile = open(tmpfilepath, "w")
  tmpfile.write(content)
  tmpfile.close()
  return tmpfilepath


processors = [
  ("local_dir_processor",),
  ("glob_processor",),
  (pytest.param("glob_processor_rs", marks=pytest.mark.rs)),
  ("local_file_processor",),
  ("text_plain_processor",),
]


@pytest.mark.parametrize(["processor"], processors)
def test_processor_repr(all_processors, processor):
  processor = all_processors[processor]
  assert (
    repr(processor)
    == f"{processor.__class__.__name__}"
    + f"(service_name={processor.service_name}, "
    + f"supported_types={repr(processor.supported_types)})"
  )


@pytest.mark.parametrize(["processor"], processors)
def test_processor_called_with_invalid_resource(all_processors, processor):
  processor = all_processors[processor]
  with pytest.raises(BeartypeCallHintParamViolation) as e:
    processor.process("")
  assert isinstance(e.value, BeartypeCallHintParamViolation)
  assert 'not instance of <protocol "bodhilib._models.IsResource"' in str(e.value)


def override_resource_type(resource, resource_type):
  resource.resource_type = resource_type
  return resource


@pytest.fixture
def invalid_resource_args(tmp_test_dir):
  tmpfile = f"{tmp_test_dir}/test1.txt"
  return {
    "glob_missing_resource_type": [{"path": tmp_test_dir, "pattern": "*.txt"}, "missing", "Field required"],
    "glob_invalid_resource_type": [
      {"resource_type": "local_file", "path": tmp_test_dir, "pattern": "*.txt"},
      "literal_error",
      "Input should be 'glob'",
    ],
    "glob_missing_path": [{"resource_type": "glob", "pattern": "*.txt"}, "missing", "Field required"],
    "glob_path_is_file": [
      {"resource_type": "glob", "path": tmpfile, "pattern": "*.txt"},
      "assertion_error",
      f"Assertion failed, Path is not a directory: {tmpfile}",
    ],
    "glob_missing_pattern": [{"resource_type": "glob", "path": tmp_test_dir}, "missing", "Field required"],
    "glob_invalid_path": [
      {"resource_type": "glob", "path": "/non-exist", "pattern": "*.txt"},
      "assertion_error",
      "Assertion failed, Directory does not exist: /non-exist",
    ],
    "glob_pattern_none": [
      {"resource_type": "glob", "path": tmp_test_dir, "pattern": None},
      "string_type",
      "Input should be a valid string",
    ],
    "glob_path_none": [
      {"resource_type": "glob", "path": None, "pattern": "*.txt"},
      "assertion_error",
      "Assertion failed, Path is None",
    ],
    "local_dir_resource_type_invalid": [
      {"resource_type": "glob", "path": tmp_test_dir},
      "literal_error",
      "Input should be 'local_dir'",
    ],
    "local_dir_resource_type_missing": [{"path": tmp_test_dir}, "missing", "Field required"],
    "local_dir_resource_type_none": [
      {"resource_type": None, "path": tmp_test_dir},
      "string_type",
      "Input should be a valid string",
    ],
    "local_dir_path_missing": [{"resource_type": "local_dir"}, "missing", "Field required"],
    "local_dir_path_none": [
      {"resource_type": "local_dir", "path": None},
      "assertion_error",
      "Assertion failed, Path is None",
    ],
    "local_dir_path_invalid_dir": [
      {"resource_type": "local_dir", "path": "/non-exist"},
      "assertion_error",
      "Assertion failed, Directory does not exist: /non-exist",
    ],
    "local_dir_path_is_file": [
      {"resource_type": "local_dir", "path": tmpfile},
      "assertion_error",
      f"Assertion failed, Path is not a directory: {tmpfile}",
    ],
    "local_file_resource_type_invalid": [
      {"resource_type": "local_dir", "path": tmpfile},
      "literal_error",
      "Input should be 'local_file'",
    ],
    "local_file_resource_type_missing": [{"path": tmpfile}, "missing", "Field required"],
    "local_file_resource_type_none": [
      {"resource_type": None, "path": tmpfile},
      "string_type",
      "Input should be a valid string",
    ],
    "local_file_path_missing": [{"resource_type": None}, "string_type", "Input should be a valid string"],
    "local_file_path_none": [
      {"resource_type": "local_file", "path": None},
      "assertion_error",
      "Assertion failed, Path is None",
    ],
    "local_file_path_invalid_file": [
      {"resource_type": "local_file", "path": "/non-exist"},
      "assertion_error",
      "Assertion failed, File does not exist: /non-exist",
    ],
    "local_file_path_is_dir": [
      {"resource_type": "local_file", "path": tmp_test_dir},
      "assertion_error",
      f"Assertion failed, Path is not a file: {tmp_test_dir}",
    ],
    "txt_file_resource_type_missing": [{"path": tmpfile}, "missing", "Field required"],
    "txt_file_resource_type_invalid": [
      {"resource_type": "local_file", "path": tmpfile},
      "literal_error",
      "Input should be 'text/plain'",
    ],
    "txt_file_resource_type_none": [
      {"resource_type": None, "path": tmpfile},
      "string_type",
      "Input should be a valid string",
    ],
    "txt_file_path_missing": [{"resource_type": "text/plain"}, "missing", "Field required"],
    "txt_file_path_none": [
      {"resource_type": "text/plain", "path": None},
      "assertion_error",
      "Assertion failed, Path is None",
    ],
    "txt_file_path_invalid_file": [
      {"resource_type": "text/plain", "path": "/non-exist"},
      "assertion_error",
      "Assertion failed, File does not exist: /non-exist",
    ],
    "txt_file_path_is_dir": [
      {"resource_type": "text/plain", "path": tmp_test_dir},
      "assertion_error",
      f"Assertion failed, Path is not a file: {tmp_test_dir}",
    ],
  }


mandatory_args = [
  ("glob_processor", "glob_missing_resource_type"),
  ("glob_processor", "glob_invalid_resource_type"),
  ("glob_processor", "glob_missing_path"),
  ("glob_processor", "glob_missing_pattern"),
  ("glob_processor", "glob_invalid_path"),
  ("glob_processor", "glob_path_is_file"),
  ("glob_processor", "glob_pattern_none"),
  ("glob_processor", "glob_path_none"),
  (
    pytest.param(
      "glob_processor_rs",
      "glob_missing_resource_type",
      marks=pytest.mark.rs,
    )
  ),
  (
    pytest.param(
      "glob_processor_rs",
      "glob_invalid_resource_type",
      marks=pytest.mark.rs,
    )
  ),
  (
    pytest.param(
      "glob_processor_rs",
      "glob_missing_path",
      marks=pytest.mark.rs,
    )
  ),
  (
    pytest.param(
      "glob_processor_rs",
      "glob_path_none",
      marks=pytest.mark.rs,
    )
  ),
  (
    pytest.param(
      "glob_processor_rs",
      "glob_missing_pattern",
      marks=pytest.mark.rs,
    )
  ),
  (
    pytest.param(
      "glob_processor_rs",
      "glob_invalid_path",
      marks=pytest.mark.rs,
    )
  ),
  (
    pytest.param(
      "glob_processor_rs",
      "glob_path_is_file",
      marks=pytest.mark.rs,
    )
  ),
  (
    pytest.param(
      "glob_processor_rs",
      "glob_pattern_none",
      marks=pytest.mark.rs,
    )
  ),
  ("local_dir_processor", "local_dir_resource_type_missing"),
  ("local_dir_processor", "local_dir_resource_type_invalid"),
  ("local_dir_processor", "local_dir_resource_type_none"),
  ("local_dir_processor", "local_dir_path_missing"),
  ("local_dir_processor", "local_dir_path_none"),
  ("local_dir_processor", "local_dir_path_invalid_dir"),
  ("local_dir_processor", "local_dir_path_is_file"),
  ("local_file_processor", "local_file_resource_type_missing"),
  ("local_file_processor", "local_file_resource_type_invalid"),
  ("local_file_processor", "local_file_resource_type_none"),
  ("local_file_processor", "local_file_path_missing"),
  ("local_file_processor", "local_file_path_none"),
  ("local_file_processor", "local_file_path_invalid_file"),
  ("local_file_processor", "local_file_path_is_dir"),
  ("text_plain_processor", "txt_file_resource_type_missing"),
  ("text_plain_processor", "txt_file_resource_type_invalid"),
  ("text_plain_processor", "txt_file_resource_type_none"),
  ("text_plain_processor", "txt_file_path_missing"),
  ("text_plain_processor", "txt_file_path_none"),
  ("text_plain_processor", "txt_file_path_invalid_file"),
  ("text_plain_processor", "txt_file_path_is_dir"),
]


@pytest.mark.parametrize(
  ["processor", "invalid_resource_key"],
  mandatory_args,
)
def test_processor_mandatory_args(all_processors, invalid_resource_args, processor: str, invalid_resource_key):
  processor = all_processors[processor]
  param = invalid_resource_args[invalid_resource_key]
  invalid_resource = param[0]
  error_type = param[1]
  error_msg = param[2]
  with pytest.raises(ValidationError) as e:
    processor.process(Resource(**invalid_resource))
  assert isinstance(e.value, ValidationError)
  assert e.value.error_count() == 1
  error = e.value.errors()[0]
  assert error["type"] == error_type
  assert error["msg"] == error_msg


@pytest.mark.parametrize(
  ["processor", "invalid_resource_key"],
  mandatory_args,
)
@pytest.mark.asyncio
async def test_processor_async_mandatory_args(
  all_processors, invalid_resource_args, processor: str, invalid_resource_key
):
  processor = all_processors[processor]
  param = invalid_resource_args[invalid_resource_key]
  invalid_resource = param[0]
  error_type = param[1]
  error_msg = param[2]
  with pytest.raises(ValidationError) as e:
    await processor.aprocess(Resource(**invalid_resource))
  assert isinstance(e.value, ValidationError)
  assert e.value.error_count() == 1
  error = e.value.errors()[0]
  assert error["type"] == error_type
  assert error["msg"] == error_msg


@pytest.mark.parametrize(
  ["stream"],
  [(True,), (False,)],
)
def test_processor_local_dir_recursive(tmp_test_dir, local_dir_processor: ResourceProcessor, stream):
  resource = local_dir(path=tmp_test_dir, recursive=True, exclude_hidden=True)
  return_type = Iterator if stream else List
  resources = local_dir_processor.process(resource, stream=stream)
  assert isinstance(resources, return_type)
  resources = list(resources) if stream else resources
  assert len(resources) == 3
  assert all([resource.resource_type == LOCAL_FILE for resource in resources])
  paths = sorted([resource.metadata["path"] for resource in resources])
  assert paths == [f"{tmp_test_dir}/test1.txt", f"{tmp_test_dir}/test2.csv", f"{tmp_test_dir}/tmpdir2/test4.txt"]


@pytest.mark.parametrize(
  ["astream"],
  [(True,), (False,)],
)
@pytest.mark.asyncio
async def test_processor_async_local_dir_recursive(tmp_test_dir, local_dir_processor: ResourceProcessor, astream):
  resource = local_dir(path=tmp_test_dir, recursive=True, exclude_hidden=True)
  return_type = AsyncIterator if astream else List
  resources = await local_dir_processor.aprocess(resource, astream=astream)
  assert isinstance(resources, return_type)
  resources = [i async for i in resources] if astream else resources
  assert len(resources) == 3
  assert all([resource.resource_type == LOCAL_FILE for resource in resources])
  paths = sorted([resource.metadata["path"] for resource in resources])
  assert paths == [f"{tmp_test_dir}/test1.txt", f"{tmp_test_dir}/test2.csv", f"{tmp_test_dir}/tmpdir2/test4.txt"]


@pytest.mark.parametrize(
  ["stream"],
  [(True,), (False,)],
)
def test_processor_local_dir_recursive_hidden(tmp_test_dir, local_dir_processor: ResourceProcessor, stream):
  resource = local_dir(path=tmp_test_dir, recursive=True, exclude_hidden=False)
  resources = local_dir_processor.process(resource, stream=stream)
  return_type = Iterator if stream else List
  assert isinstance(resources, return_type)
  resources = list(resources) if stream else resources
  assert len(resources) == 5
  assert all([resource.resource_type == LOCAL_FILE for resource in resources])
  paths = sorted([resource.metadata["path"] for resource in resources])
  assert paths == [
    f"{tmp_test_dir}/.test3.txt",
    f"{tmp_test_dir}/test1.txt",
    f"{tmp_test_dir}/test2.csv",
    f"{tmp_test_dir}/tmpdir2/.test5.txt",
    f"{tmp_test_dir}/tmpdir2/test4.txt",
  ]


@pytest.mark.parametrize(
  ["astream"],
  [(True,), (False,)],
)
@pytest.mark.asyncio
async def test_processor_async_local_dir_recursive_hidden(
  tmp_test_dir, local_dir_processor: ResourceProcessor, astream
):
  resource = local_dir(path=tmp_test_dir, recursive=True, exclude_hidden=False)
  resources = await local_dir_processor.aprocess(resource, astream=astream)
  return_type = AsyncIterator if astream else List
  assert isinstance(resources, return_type)
  resources = [i async for i in resources] if astream else resources
  assert len(resources) == 5
  assert all([resource.resource_type == LOCAL_FILE for resource in resources])
  paths = sorted([resource.metadata["path"] for resource in resources])
  assert paths == [
    f"{tmp_test_dir}/.test3.txt",
    f"{tmp_test_dir}/test1.txt",
    f"{tmp_test_dir}/test2.csv",
    f"{tmp_test_dir}/tmpdir2/.test5.txt",
    f"{tmp_test_dir}/tmpdir2/test4.txt",
  ]


@pytest.mark.parametrize(
  ["stream"],
  [(True,), (False,)],
)
def test_processor_local_dir_not_recursive(tmp_test_dir, local_dir_processor: ResourceProcessor, stream):
  resource = local_dir(path=tmp_test_dir, recursive=False, exclude_hidden=True)
  resources = local_dir_processor.process(resource, stream=stream)
  return_type = Iterator if stream else List
  assert isinstance(resources, return_type)
  resources = list(resources) if stream else resources
  assert len(resources) == 2
  assert all([resource.resource_type == LOCAL_FILE for resource in resources])
  paths = sorted([resource.metadata["path"] for resource in resources])
  assert paths == [f"{tmp_test_dir}/test1.txt", f"{tmp_test_dir}/test2.csv"]


@pytest.mark.parametrize(
  ["astream"],
  [(True,), (False,)],
)
@pytest.mark.asyncio
async def test_processor_async_local_dir_not_recursive(tmp_test_dir, local_dir_processor: ResourceProcessor, astream):
  resource = local_dir(path=tmp_test_dir, recursive=False, exclude_hidden=True)
  resources = await local_dir_processor.aprocess(resource, astream=astream)
  return_type = AsyncIterator if astream else List
  assert isinstance(resources, return_type)
  resources = [i async for i in resources] if astream else resources
  assert len(resources) == 2
  assert all([resource.resource_type == LOCAL_FILE for resource in resources])
  paths = sorted([resource.metadata["path"] for resource in resources])
  assert paths == [f"{tmp_test_dir}/test1.txt", f"{tmp_test_dir}/test2.csv"]


@pytest.mark.parametrize(
  ["stream"],
  [(True,), (False,)],
)
def test_processor_local_dir_not_recursive_hidden(tmp_test_dir, local_dir_processor: ResourceProcessor, stream):
  resource = local_dir(path=tmp_test_dir, recursive=False, exclude_hidden=False)
  resources = local_dir_processor.process(resource, stream=stream)
  return_type = Iterator if stream else List
  assert isinstance(resources, return_type)
  resources = list(resources) if stream else resources
  assert len(resources) == 3
  assert all([resource.resource_type == LOCAL_FILE for resource in resources])
  paths = sorted([resource.metadata["path"] for resource in resources])
  assert paths == [f"{tmp_test_dir}/.test3.txt", f"{tmp_test_dir}/test1.txt", f"{tmp_test_dir}/test2.csv"]


@pytest.mark.parametrize(
  ["astream"],
  [(True,), (False,)],
)
@pytest.mark.asyncio
async def test_processor_async_local_dir_not_recursive_hidden(
  tmp_test_dir, local_dir_processor: ResourceProcessor, astream
):
  resource = local_dir(path=tmp_test_dir, recursive=False, exclude_hidden=False)
  resources = await local_dir_processor.aprocess(resource, astream=astream)
  return_type = AsyncIterator if astream else List
  assert isinstance(resources, return_type)
  resources = [i async for i in resources] if astream else resources
  assert len(resources) == 3
  assert all([resource.resource_type == LOCAL_FILE for resource in resources])
  paths = sorted([resource.metadata["path"] for resource in resources])
  assert paths == [f"{tmp_test_dir}/.test3.txt", f"{tmp_test_dir}/test1.txt", f"{tmp_test_dir}/test2.csv"]


glob_expects = [
  (False, False, ["test1.txt", ".test3.txt"]),
  (False, True, ["test1.txt"]),
  (True, False, ["test1.txt", ".test3.txt", "tmpdir2/test4.txt", "tmpdir2/.test5.txt"]),
  (True, True, ["test1.txt", "tmpdir2/test4.txt"]),
  (False, False, ["test1.txt", ".test3.txt"]),
  (False, True, ["test1.txt"]),
  (True, False, ["test1.txt", ".test3.txt", "tmpdir2/test4.txt", "tmpdir2/.test5.txt"]),
  (True, True, ["test1.txt", "tmpdir2/test4.txt"]),
]


@pytest.mark.parametrize(
  ["processor"],
  [
    ("glob_processor",),
    (
      pytest.param(
        "glob_processor_rs",
        marks=pytest.mark.rs,
      )
    ),
  ],
)
@pytest.mark.parametrize(
  ["stream"],
  [(True,), (False,)],
)
@pytest.mark.parametrize(
  ["recursive", "exclude_hidden", "files"],
  glob_expects,
)
def test_processor_glob_pattern(tmp_test_dir, all_processors, processor, stream, recursive, exclude_hidden, files):
  glob_processor = all_processors[processor]
  resource = glob_pattern(str(tmp_test_dir), "*.txt", recursive=recursive, exclude_hidden=exclude_hidden)
  resources = glob_processor.process(resource, stream=stream)
  return_type = Iterator if stream else List
  assert isinstance(resources, return_type)
  resources = list(resources) if stream else resources
  assert len(resources) == len(files)
  assert all([resource.resource_type == LOCAL_FILE for resource in resources])
  paths = sorted([resource.metadata["path"] for resource in resources])
  expected = sorted([f"{tmp_test_dir}/{f}" for f in files])
  assert paths == expected


@pytest.mark.parametrize(
  ["processor"],
  [
    ("glob_processor",),
    (
      pytest.param(
        "glob_processor_rs",
        marks=pytest.mark.rs,
      )
    ),
  ],
)
@pytest.mark.parametrize(
  ["astream"],
  [(True,), (False,)],
)
@pytest.mark.parametrize(
  ["recursive", "exclude_hidden", "files"],
  glob_expects,
)
@pytest.mark.asyncio
async def test_processor_async_glob_pattern(
  tmp_test_dir, all_processors, processor, astream, recursive, exclude_hidden, files
):
  glob_processor = all_processors[processor]
  resource = glob_pattern(str(tmp_test_dir), "*.txt", recursive=recursive, exclude_hidden=exclude_hidden)
  resources = await glob_processor.aprocess(resource, astream=astream)
  return_type = AsyncIterator if astream else List
  assert isinstance(resources, return_type)
  resources = [i async for i in resources] if astream else resources
  assert len(resources) == len(files)
  assert all([resource.resource_type == LOCAL_FILE for resource in resources])
  paths = sorted([resource.metadata["path"] for resource in resources])
  expected = sorted([f"{tmp_test_dir}/{f}" for f in files])
  assert paths == expected


@pytest.mark.parametrize(
  ["stream"],
  [(True,), (False,)],
)
def test_processor_local_file_txt(tmp_test_dir, local_file_processor: ResourceProcessor, stream):
  resources = local_file_processor.process(local_file(path=f"{str(tmp_test_dir)}/test1.txt"), stream=stream)
  return_type = Iterator if stream else List
  assert isinstance(resources, return_type)
  resources = list(resources) if stream else resources
  assert len(resources) == 1
  assert resources[0].resource_type == "text/plain"
  assert resources[0].metadata["path"] == Path(f"{tmp_test_dir}/test1.txt")


@pytest.mark.parametrize(
  ["astream"],
  [(True,), (False,)],
)
@pytest.mark.asyncio
async def test_processor_async_local_file_txt(tmp_test_dir, local_file_processor: ResourceProcessor, astream):
  resources = await local_file_processor.aprocess(local_file(path=f"{str(tmp_test_dir)}/test1.txt"), astream=astream)
  return_type = AsyncIterator if astream else List
  assert isinstance(resources, return_type)
  resources = [i async for i in resources] if astream else resources
  assert len(resources) == 1
  assert resources[0].resource_type == "text/plain"
  assert resources[0].metadata["path"] == Path(f"{tmp_test_dir}/test1.txt")


@pytest.mark.parametrize(
  ["stream"],
  [(True,), (False,)],
)
def test_processor_text_plain(tmp_test_dir, text_plain_processor: ResourceProcessor, stream):
  resources = text_plain_processor.process(
    text_plain_file(path=Path(tmp_test_dir).joinpath("test1.txt")), stream=stream
  )
  return_type = Iterator if stream else List
  assert isinstance(resources, return_type)
  resources = list(resources) if stream else resources
  assert len(resources) == 1
  assert isinstance(resources[0], Document)
  assert resources[0].metadata["resource_type"] == DOCUMENT
  assert resources[0].metadata["path"] == str(Path(tmp_test_dir).joinpath("test1.txt"))


@pytest.mark.parametrize(
  ["astream"],
  [(True,), (False,)],
)
@pytest.mark.asyncio
async def test_processor_async_text_plain(tmp_test_dir, text_plain_processor: ResourceProcessor, astream):
  resources = await text_plain_processor.aprocess(
    text_plain_file(path=Path(tmp_test_dir).joinpath("test1.txt")), astream=astream
  )
  return_type = AsyncIterator if astream else List
  assert isinstance(resources, return_type)
  resources = [i async for i in resources] if astream else resources
  assert len(resources) == 1
  assert isinstance(resources[0], Document)
  assert resources[0].metadata["resource_type"] == DOCUMENT
  assert resources[0].metadata["path"] == str(Path(tmp_test_dir).joinpath("test1.txt"))


def test_processor_text_plain_unsupported_ext(tmp_test_dir, local_file_processor: ResourceProcessor):
  _tmpfile(tmp_test_dir, "test1.csv", "hello,world")
  with pytest.raises(ValueError) as e:
    _ = local_file_processor.process(local_file(path=Path(tmp_test_dir).joinpath("test1.csv")))
  assert str(e.value) == "Unsupported file extension: .csv, supports ['.txt']"


@pytest.mark.asyncio
async def test_processor_async_text_plain_unsupported_ext(tmp_test_dir, local_file_processor: ResourceProcessor):
  _tmpfile(tmp_test_dir, "test1.csv", "hello,world")
  with pytest.raises(ValueError) as e:
    _ = await local_file_processor.aprocess(local_file(path=Path(tmp_test_dir).joinpath("test1.csv")))
  assert str(e.value) == "Unsupported file extension: .csv, supports ['.txt']"


@pytest.mark.rs
def test_resource_object_repr(tmp_test_dir, glob_processor_rs):
  file_path = str(Path(tmp_test_dir).joinpath("test1.txt"))
  resources = glob_processor_rs.process(Resource(resource_type="glob", path=tmp_test_dir, pattern="test1.txt"))
  assert len(resources) == 1
  assert resources[0].resource_type == LOCAL_FILE
  assert resources[0].metadata["path"] == file_path
  assert resources[0].metadata["resource_type"] == LOCAL_FILE
  assert resources[0].path == file_path
  assert repr(resources[0]) == repr(local_file(path=file_path))


@pytest.mark.asyncio
@pytest.mark.rs
async def test_resource_async_object_repr(tmp_test_dir, glob_processor_rs):
  file_path = str(Path(tmp_test_dir).joinpath("test1.txt"))
  resources = await glob_processor_rs.aprocess(Resource(resource_type="glob", path=tmp_test_dir, pattern="test1.txt"))
  assert len(resources) == 1
  assert resources[0].resource_type == LOCAL_FILE
  assert resources[0].metadata["path"] == file_path
  assert resources[0].metadata["resource_type"] == LOCAL_FILE
  assert resources[0].path == file_path
  assert repr(resources[0]) == repr(local_file(path=file_path))
