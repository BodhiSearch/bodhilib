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


invalid_args = [
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
    pytest.param(
      "glob_processor_rs",
      local_file(path="invalid"),
      "Unsupported resource type: local_file, supports ['glob']",
      marks=pytest.mark.rs,
    )
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
]


@pytest.mark.parametrize(
  ["processor", "invalid_resource", "msg"],
  invalid_args,
)
def test_processor_invalid_resource_type(all_processors, processor: str, invalid_resource: IsResource, msg: str):
  processor = all_processors[processor]
  with pytest.raises(ValueError) as e:
    processor.process(invalid_resource)
  assert isinstance(e.value, ValueError)
  assert str(e.value) == msg


@pytest.mark.parametrize(
  ["processor", "invalid_resource", "msg"],
  invalid_args,
)
@pytest.mark.asyncio
async def test_processor_async_invalid_resource_type(
  all_processors, processor: str, invalid_resource: IsResource, msg: str
):
  processor = all_processors[processor]
  with pytest.raises(ValueError) as e:
    await processor.aprocess(invalid_resource)
  assert isinstance(e.value, ValueError)
  assert str(e.value) == msg


mandatory_args = [
  ("glob_processor", Resource(resource_type="glob"), "Resource metadata does not contain key: 'path'"),
  (
    "glob_processor",
    Resource(resource_type="glob", path=None),
    "Resource metadata key value is None: 'path'",
  ),
  (
    "glob_processor",
    Resource(resource_type="glob", path="."),
    "Resource metadata does not contain key: 'pattern'",
  ),
  (
    "glob_processor",
    Resource(resource_type="glob", path="foo"),
    "Directory does not exist: ",
  ),
  (
    "glob_processor",
    Resource(resource_type="glob", path=".", pattern=None),
    "Resource metadata key value is None: 'pattern'",
  ),
  (
    pytest.param(
      "glob_processor_rs",
      Resource(resource_type="glob"),
      "Resource metadata does not contain key: 'path'",
      marks=pytest.mark.rs,
    )
  ),
  (
    pytest.param(
      "glob_processor_rs",
      Resource(resource_type="glob", path=None),
      "Resource metadata key value is None: 'path'",
      marks=pytest.mark.rs,
    )
  ),
  (
    pytest.param(
      "glob_processor_rs",
      Resource(resource_type="glob", path="."),
      "Resource metadata does not contain key: 'pattern'",
      marks=pytest.mark.rs,
    )
  ),
  (
    pytest.param(
      "glob_processor_rs",
      Resource(resource_type="glob", path="foo"),
      "Directory does not exist: ",
      marks=pytest.mark.rs,
    )
  ),
  (
    pytest.param(
      "glob_processor_rs",
      Resource(resource_type="glob", path=".", pattern=None),
      "Resource metadata key value is None: 'pattern'",
      marks=pytest.mark.rs,
    )
  ),
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
]


@pytest.mark.parametrize(
  ["processor", "invalid_resource", "msg"],
  mandatory_args,
)
def test_processor_mandatory_args(all_processors, processor: str, invalid_resource: IsResource, msg: str):
  processor = all_processors[processor]
  with pytest.raises(ValueError) as e:
    processor.process(invalid_resource)
  assert str(e.value).startswith(msg)


@pytest.mark.parametrize(
  ["processor", "invalid_resource", "msg"],
  mandatory_args,
)
@pytest.mark.asyncio
async def test_processor_async_mandatory_args(all_processors, processor: str, invalid_resource: IsResource, msg: str):
  processor = all_processors[processor]
  with pytest.raises(ValueError) as e:
    await processor.aprocess(invalid_resource)
  assert str(e.value).startswith(msg)


invalid_file_instead_of_dir = [
  ("local_file_processor", "local_file", "Path is not a file: {tmpdir}"),
  ("text_plain_processor", "text/plain", "Path is not a file: {tmpdir}"),
]


@pytest.mark.parametrize(
  ["processor", "resource_type", "msg"],
  invalid_file_instead_of_dir,
)
def test_processor_is_dir(tmpdir, all_processors, processor, resource_type, msg):
  processor = all_processors[processor]
  with pytest.raises(ValueError) as e:
    processor.process(Resource(resource_type=resource_type, path=Path(tmpdir)))
  assert str(e.value) == msg.format(tmpdir=tmpdir)


@pytest.mark.parametrize(
  ["processor", "resource_type", "msg"],
  invalid_file_instead_of_dir,
)
@pytest.mark.asyncio
async def test_processor_async_is_dir(tmpdir, all_processors, processor, resource_type, msg):
  processor = all_processors[processor]
  with pytest.raises(ValueError) as e:
    processor.process(Resource(resource_type=resource_type, path=Path(tmpdir)))
  assert str(e.value) == msg.format(tmpdir=tmpdir)


invalid_dir_instead_of_file = [
  ("local_dir_processor", "local_dir", "Path is not a directory: {tmpfile}"),
  ("glob_processor", "glob", "Path is not a directory: {tmpfile}"),
  (pytest.param("glob_processor_rs", "glob", "Path is not a directory: {tmpfile}", marks=pytest.mark.rs)),
]


@pytest.mark.parametrize(
  ["processor", "resource_type", "msg"],
  invalid_dir_instead_of_file,
)
def test_processor_not_directory(tmpdir, all_processors, processor, resource_type, msg):
  processor = all_processors[processor]
  tmpfile = Path(tmpdir).joinpath("test1.txt")
  _tmpfile(tmpdir, "test1.txt", "hello world!")
  with pytest.raises(ValueError) as e:
    processor.process(Resource(resource_type=resource_type, path=str(tmpfile)))
  assert str(e.value) == msg.format(tmpfile=tmpfile)


@pytest.mark.parametrize(
  ["processor", "resource_type", "msg"],
  invalid_dir_instead_of_file,
)
@pytest.mark.asyncio
async def test_processor_async_not_directory(tmpdir, all_processors, processor, resource_type, msg):
  processor = all_processors[processor]
  tmpfile = Path(tmpdir).joinpath("test1.txt")
  _tmpfile(tmpdir, "test1.txt", "hello world!")
  with pytest.raises(ValueError) as e:
    processor.process(Resource(resource_type=resource_type, path=str(tmpfile)))
  assert str(e.value) == msg.format(tmpfile=tmpfile)


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
