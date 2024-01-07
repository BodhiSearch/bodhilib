import os
from pathlib import Path

import pytest
from bodhiext.splitter import TextSplitter
from bodhilib import Document

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def text_splitter():
  return TextSplitter(max_len=10, min_len=6, overlap=2)


def test_text_splitter_multiline():
  text_splitter = TextSplitter(max_len=6, min_len=2, overlap=1)
  text = "This is a 10 word line one two three four.\nThis is short line.\nThis is third line."
  docs = [Document(text=text)]
  splits = text_splitter.split(docs)
  assert len(splits) == 4
  assert splits[0].text == "This is a 10 word line "
  assert splits[1].text == "line one two three four.\n"
  assert splits[2].text == "four.\nThis is short line.\n"
  assert splits[3].text == "line.\nThis is third line."


def test_text_splitter_for_document_with_less_than_min_len(text_splitter):
  text = "This is 4 words."
  docs = [Document(text=text)]
  splits = text_splitter.split(docs)
  assert len(splits) == 1
  assert splits[0].text == text


def test_text_splitter_for_document_with_two_nodes_in_a_sentence(text_splitter):
  text = "This is 14 words sentence six seven eight nine ten eleven twelve thirteen fourteen."
  docs = [Document(text=text)]
  splits = text_splitter.split(docs)
  assert len(splits) == 2
  assert splits[0].text == "This is 14 words sentence six seven eight nine ten "
  assert splits[1].text == "nine ten eleven twelve thirteen fourteen."


def test_text_splitter_for_document_with_three_nodes_in_a_sentence(text_splitter):
  text = _generate_sentence(25)
  docs = [Document(text=text)]
  splits = text_splitter.split(docs)
  assert len(splits) == 3
  assert splits[0].text == "This is 25 words sentence 6 7 8 9 10 "
  assert splits[1].text == "9 10 11 12 13 14 15 16 17 18 "
  assert splits[2].text == "17 18 19 20 21 22 23 24 25. "


def test_text_splitter_for_document_with_three_nodes_in_2_sentence(text_splitter):
  text = _generate_sentence(8) + _generate_sentence(6)
  docs = [Document(text=text)]
  splits = text_splitter.split(docs)
  assert len(splits) == 2
  assert splits[0].text == "This is 8 words sentence 6 7 8."
  assert splits[1].text == "7 8. This is 6 words sentence 6. "


def test_text_splitter_sync(text_splitter):
  text = _generate_sentence(8) + _generate_sentence(6)
  docs = [Document(text=text)]
  split_async = text_splitter.split(docs, astream=False)
  splits = [s for s in split_async]
  assert len(splits) == 2
  assert splits[0].text == "This is 8 words sentence 6 7 8."
  assert splits[1].text == "7 8. This is 6 words sentence 6. "


@pytest.mark.asyncio
async def test_text_splitter_async(text_splitter):
  text = _generate_sentence(8) + _generate_sentence(6)
  docs = [Document(text=text)]
  split_async = text_splitter.split(docs, astream=True)
  splits = [s async for s in split_async]
  assert len(splits) == 2
  assert splits[0].text == "This is 8 words sentence 6 7 8."
  assert splits[1].text == "7 8. This is 6 words sentence 6. "


def test_preserves_original_text():
  zero_overlap_splitter = TextSplitter(max_len=10, min_len=6, overlap=0)
  text = _generate_sentence(64)
  splits = zero_overlap_splitter.split([Document(text=text)])
  assert len(splits) == 7
  assert "".join([s.text for s in splits]) == text


def test_zero_overlap_splitter_on_essay():
  zero_overlap_splitter = TextSplitter(max_len=1000, min_len=100, overlap=0)
  with open(current_dir / ".." / "test_data" / "pg-great-work.txt", "r") as f:
    text = f.read()
  splits = zero_overlap_splitter.split([Document(text=text)])
  assert "".join([s.text for s in splits]) == text


def _generate_sentence(i: int):
  return f"This is {i} words sentence " + " ".join([str(i) for i in range(6, i + 1)]) + ". "
