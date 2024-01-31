from glob import glob
import pytest
import os
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter


@pytest.fixture
def lc_splitter():
  text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=60,
    length_function=len,
    is_separator_regex=False,
  )
  return text_splitter


@pytest.fixture
def data_folder():
  return str(Path(os.environ["PG_ESSAYS_FOLDER"]))


def run_lc_splitter_bench(lc_splitter, files):
  result = []
  for file in files:
    with open(file, "r") as f:
      text = f.read()
    chunks = lc_splitter.split_text(text)
    filename = file.rsplit("/", 1)[-1]
    result.append((filename, len(chunks)))
  return result


@pytest.mark.bench
def test_lc_splitter_bench(benchmark, lc_splitter, data_folder):
  files = glob(os.path.join(data_folder, "*.md")) * 10
  _ = benchmark(run_lc_splitter_bench, lc_splitter, files)
