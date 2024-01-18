import pytest
from bodhilibrs import GlobProcessorRs
from bodhilib import glob_pattern, ResourceProcessor, IsResource
from bodhiext.resources import GlobProcessor


@pytest.fixture
def glob_pattern_json():
  return glob_pattern("~/Dropbox", "*.json", recursive=True, exclude_hidden=True)


@pytest.fixture
def glob_processor_rs():
  return GlobProcessorRs()


@pytest.fixture
def glob_processor():
  return GlobProcessor()


def run_bench(processor: ResourceProcessor, pattern: IsResource, stream: bool):
  files = processor.process(pattern, stream)
  return len(files)


@pytest.mark.bench
def test_bench_glob_rs_sync_list(benchmark, glob_processor_rs, glob_pattern_json):
  len = benchmark(run_bench, glob_processor_rs, glob_pattern_json, False)
  assert len == 95


@pytest.mark.bench
def test_bench_glob_sync_list(benchmark, glob_processor, glob_pattern_json):
  len = benchmark(run_bench, glob_processor, glob_pattern_json, False)
  assert len == 95
