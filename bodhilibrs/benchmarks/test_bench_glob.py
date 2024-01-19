from pathlib import Path

import pytest
from bodhiext.resources import GlobProcessor
from bodhilib import IsResource, ResourceProcessor, glob_pattern

from bodhilibrs import GlobProcessorRs

pytestmark = pytest.mark.filterwarnings("ignore")


@pytest.fixture
def glob_pattern_json():
  return glob_pattern("~/Dropbox", "*.json", recursive=True, exclude_hidden=True)


@pytest.fixture
def glob_processor_rs():
  return GlobProcessorRs()


@pytest.fixture
def glob_processor():
  return GlobProcessor()


@pytest.fixture
def all_processors():
  return {
    "glob_processor": GlobProcessor(),
    "glob_processor_rs": GlobProcessorRs(),
  }


def run_bench(processor: ResourceProcessor, pattern: IsResource, stream: bool):
  files = processor.process(pattern, stream)
  return len(files)


async def run_bench_async(processor: ResourceProcessor, pattern: IsResource, stream: bool):
  files = await processor.process(pattern, stream)
  return len(files)


def run_bench_langchain():
  from langchain_community.document_loaders import DirectoryLoader

  path = str(Path("~/Dropbox").expanduser().resolve())
  loader = DirectoryLoader(path, glob="**/*.json", load_hidden=False)
  docs = loader.load()
  return len(docs)


def run_bench_llama_index():
  from llama_index import SimpleDirectoryReader

  path = str(Path("~/Dropbox").expanduser().resolve())
  reader = SimpleDirectoryReader(
    input_dir=path,
    required_exts="json",
    recursive=True,
    exclude_hidden=True,
  )
  docs = reader.load_data()
  return len(docs)


@pytest.mark.bench
@pytest.mark.parametrize(
  ["processor_key"],
  [("glob_processor",), ("glob_processor_rs",)],
)
def test_bench_glob_rs_sync_list(benchmark, glob_pattern_json, all_processors, processor_key):
  processor = all_processors[processor_key]
  len = benchmark(run_bench, processor, glob_pattern_json, False)
  assert len == 95


@pytest.mark.bench
@pytest.mark.asyncio
@pytest.mark.parametrize(
  ["processor_key"],
  [("glob_processor",), ("glob_processor_rs",)],
)
async def test_bench_glob_rs_async_list(aio_benchmark, all_processors, processor_key, glob_pattern_json):
  processor = all_processors[processor_key]

  @aio_benchmark
  async def _():
    await processor.aprocess(glob_pattern_json, False)


@pytest.mark.bench
def test_bench_glob_sync_list(benchmark, glob_processor, glob_pattern_json):
  len = benchmark(run_bench, glob_processor, glob_pattern_json, False)
  assert len == 95


@pytest.mark.bench
def test_bench_glob_new(benchmark):
  from bodhilibrs.bodhilibrs import find_files
  root_folder = str(Path("~/Dropbox").expanduser().resolve())
  files = benchmark(find_files, root_folder, "*.json", True, True)
  assert len(files) == 118


@pytest.mark.bench
def test_bench_py_glob(benchmark):
  # using python, search for all json files in the dropbox folder
  from pathlib import Path

  root_folder = Path("~/Dropbox").expanduser().resolve()

  def find_all_files(folder, pattern):
    return list(folder.glob(pattern))

  files = benchmark(find_all_files, root_folder, "**/*.json")
  assert len(list(files)) == 118


# @pytest.mark.bench
# def test_bench_glob_langchain(benchmark):
#   len = benchmark(run_bench_langchain)
#   assert len == 95


@pytest.mark.bench
@pytest.mark.skip
def test_bench_glob_llama_index(benchmark):
  len = benchmark(run_bench_llama_index)
  assert len == 95


@pytest.fixture(scope="function")
def aio_benchmark(benchmark):
  import asyncio
  import threading

  class Sync2Async:
    def __init__(self, coro, *args, **kwargs):
      self.coro = coro
      self.args = args
      self.kwargs = kwargs
      self.custom_loop = None
      self.thread = None

    def start_background_loop(self) -> None:
      asyncio.set_event_loop(self.custom_loop)
      self.custom_loop.run_forever()

    def __call__(self):
      evloop = None
      awaitable = self.coro(*self.args, **self.kwargs)
      try:
        evloop = asyncio.get_running_loop()
      except Exception:
        pass
      if evloop is None:
        return asyncio.run(awaitable)
      else:
        if not self.custom_loop or not self.thread or not self.thread.is_alive():
          self.custom_loop = asyncio.new_event_loop()
          self.thread = threading.Thread(target=self.start_background_loop, daemon=True)
          self.thread.start()

        return asyncio.run_coroutine_threadsafe(awaitable, self.custom_loop).result()

  def _wrapper(func, *args, **kwargs):
    if asyncio.iscoroutinefunction(func):
      benchmark(Sync2Async(func, *args, **kwargs))
    else:
      benchmark(func, *args, **kwargs)

  return _wrapper
