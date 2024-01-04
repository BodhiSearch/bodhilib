import itertools

import pytest
from bodhiext.splitter._text_splitter import _build_sentence_splitter, _build_symbol_splitter

from tests_bodhiext_common.unit.test_text_splitter import _generate_sentence


@pytest.fixture
def sentence_splitter():
  return _build_sentence_splitter([r"\.", r"\?", r"\!", r"\n"])


@pytest.fixture
def word_splitter():
  return _build_symbol_splitter([r"\s", r"-", r":", r"\.", r"\?", r"\!", r"\n"])


def test_word_splitter_for_continuous_spaces(word_splitter):
  words = word_splitter("Hello  World")
  assert len(words) == 2
  assert words[0] == "Hello  "
  assert words[1] == "World"


def test_word_splitter_for_trailing_spaces(word_splitter):
  words = word_splitter("Hello  World  ")
  assert len(words) == 2
  assert words[0] == "Hello  "
  assert words[1] == "World  "


def test_word_splitter_for_continuous_different_symbols(word_splitter):
  words = word_splitter("Hello - World : ")
  assert len(words) == 2
  assert words[0] == "Hello - "
  assert words[1] == "World : "


def test_word_splitter_with_continuous_same_symbols(word_splitter):
  words = word_splitter("Hello ---World ::: Hey")
  assert len(words) == 3
  assert words[0] == "Hello ---"
  assert words[1] == "World ::: "
  assert words[2] == "Hey"


def test_word_splitter_for_a_sentence_with_three_words(word_splitter):
  words = word_splitter("Hello World Hey.")
  assert len(words) == 3
  assert words[0] == "Hello "
  assert words[1] == "World "
  assert words[2] == "Hey."


def test_word_splitter_for_a_sentence_ending_with_newline(word_splitter):
  words = word_splitter("Hello World Hey.\n")
  assert len(words) == 3
  assert words[0] == "Hello "
  assert words[1] == "World "
  assert words[2] == "Hey.\n"


def test_word_splitter_with_a_leading_space(word_splitter):
  words = word_splitter(" -:Hello World")
  assert len(words) == 2
  assert words[0] == " -:Hello "
  assert words[1] == "World"


def test_word_splitter_with_only_spaces(word_splitter):
  words = word_splitter("   ")
  assert len(words) == 1
  assert words[0] == "   "


def test_word_splitter_with_only_symbols(word_splitter):
  words = word_splitter(" . : -- ")
  assert len(words) == 1
  assert words[0] == " . : -- "


def test_sentence_split_with_end_of_string(sentence_splitter):
  sentences = sentence_splitter("Hello World. How are you?")
  assert len(sentences) == 2
  assert sentences[0] == "Hello World."
  assert sentences[1] == " How are you?"


def test_sentence_splitter_with_only_symbol_symbols_for_sentence(sentence_splitter, word_splitter):
  sentences = sentence_splitter(" -: -:.")
  assert len(sentences) == 1
  assert sentences[0] == " -: -:."
  words = word_splitter(sentences[0])
  assert len(words) == 1
  assert words[0] == " -: -:."


def test_sentence_splitter_with_two_sentences(sentence_splitter):
  two_sentences = _generate_sentence(8) + _generate_sentence(6)
  sentences = sentence_splitter(two_sentences)
  assert len(sentences) == 3
  assert sentences[0] == "This is 8 words sentence 6 7 8."
  assert sentences[1] == " This is 6 words sentence 6."
  assert sentences[2] == " "


def test_split_sentence_in_words(sentence_splitter, word_splitter):
  sentences = sentence_splitter("   You: Hello- World.  Me:How are you? ")
  assert len(sentences) == 3
  assert sentences[0] == "   You: Hello- World."
  assert sentences[1] == "  Me:How are you?"
  assert sentences[2] == " "
  words = [word_splitter(s) for s in sentences]
  words = list(itertools.chain.from_iterable(words))
  assert len(words) == 8
  assert words[0] == "   You: "
  assert words[1] == "Hello- "
  assert words[2] == "World."
  assert words[3] == "  Me:"
  assert words[4] == "How "
  assert words[5] == "are "
  assert words[6] == "you?"
  assert words[7] == " "
