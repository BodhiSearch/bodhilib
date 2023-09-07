import re
from typing import Callable, Iterable, List, Optional, Tuple

from bodhilib.models import Document, Node

from ._splitter import Splitter


class TextSplitter(Splitter):
    """Splitter splits a :class:`~bodhilib.models.Document` into :class:`~Node` based on sentence and word splits."""

    def __init__(
        self,
        max_len: int = 512,
        min_len: int = 128,
        overlap: int = 16,
        eos_patterns: Optional[List[str]] = None,
        eow_patterns: Optional[List[str]] = None,
    ) -> None:
        r"""Initializing splitter to split text based on sentence and word splits.

        Args:
            max_len (int, optional): Maximum number of words in split text. Defaults to 512.
            min_len (int, optional): Minimum number of words in split text. Defaults to 128.
            overlap (int, optional): Number of words to overlap between splits. Defaults to 16.
            eos_patterns (Optional[List[str]], optional): List of patterns to split sentences.
                The patterns should be regex. E.g. `[r"\n", r"\."]`.
                Defaults to `[r"\.", r"\?", r"\!", r"\n"]`.
            eow_patterns (Optional[List[str]], optional): List of patterns to split words.
                The patterns should be regex. E.g. `[r"\s", r"\-"]`.
                Defaults to `[r"\s", r"\-", r"\:", r"\.", r"\?", r"\!", r"\n"]`.
        """
        assert max_len > min_len, f"{max_len=} should be greater than {min_len=}"
        assert overlap < max_len, f"{overlap=} should be less than {max_len=}"
        assert overlap < min_len, f"{overlap=} should be less than {min_len=}"

        self.max_len = max_len
        self.min_len = min_len
        self.overlap = overlap

        if eos_patterns is None:
            eos_patterns = [r"\.", r"\?", r"\!", r"\n"]
        self.sentence_splitter = _build_sentence_splitter(eos_patterns)

        if eow_patterns is None:
            eow_patterns = [r"\s", r"-", r":", r"\.", r"\?", r"\!", r"\n"]
        self.word_splitter = _build_word_splitter(eow_patterns)

    def _split(self, docs: Iterable[Document]) -> Iterable[Node]:
        for doc in docs:
            current_words: List[str] = []
            sentences = self.sentence_splitter(doc.text)
            for sentence in sentences:
                words = self.word_splitter(sentence)
                nodes, new_current_words, new_words = self._build_nodes(doc, current_words, words)
                for node in nodes:
                    yield node
                assert new_words == [], f"{new_words=} should be empty"
                current_words = new_current_words
            if len(current_words) > self.overlap:
                node_text = "".join(current_words)
                node = Node(text=node_text, parent=doc)
                yield node

    def _build_nodes(
        self, doc: Document, current_words: List[str], words: List[str]
    ) -> Tuple[List[Node], List[str], List[str]]:
        # exit condition of recursion
        # will have words == []
        # the sentence can be combined without exceeding max_len
        if len(current_words) + len(words) < self.max_len:
            return [], current_words + words, []

        # current_words in itself is larger than max_len
        # chop current_words to max_len and build the node
        if len(current_words) >= self.max_len:
            node_text = "".join(current_words[: self.max_len])
            remaining_words = current_words[self.max_len - self.overlap :]
            this_nodes = [Node(text=node_text, parent=doc)]
            nodes, new_current_words, new_words = self._build_nodes(doc, remaining_words, words)
            return this_nodes + nodes, new_current_words, new_words

        # if the combined words are equal to max_len, build the node and return
        if len(current_words) + len(words) == self.max_len:
            all_words = current_words + words
            node_text = "".join(all_words)
            remaining_words = all_words[-self.overlap :]
            this_nodes = [Node(text=node_text, parent=doc)]
            nodes, new_current_words, new_words = self._build_nodes(doc, remaining_words, [])
            return this_nodes + nodes, new_current_words, new_words

        # else: cannot be combined with next sentence without exceeding max_len
        # so, if the current sentence has more words than min_len, build the node with the current words
        if len(current_words) >= self.min_len:
            node_text = "".join(current_words)
            this_nodes = [Node(text=node_text, parent=doc)]
            remaining_words = current_words[-self.overlap :]
            nodes, new_current_words, new_words = self._build_nodes(doc, remaining_words, words)
            return this_nodes + nodes, new_current_words, new_words
        # else: if current_words is empty, hence start of sentence
        if len(current_words) == 0:
            return self._build_nodes(doc, words, [])

        # else: the current sentence has less words than min_len
        # and cannot be combined with next sentence without exceeding max_len,
        # so take as many words required to reach min_len
        all_words = current_words + words
        node_text = "".join(all_words[: self.min_len])
        this_nodes = [Node(text=node_text, parent=doc)]
        remaining_words = all_words[self.min_len - self.overlap :]
        nodes, new_current_words, new_words = self._build_nodes(doc, remaining_words, [])
        return this_nodes + nodes, new_current_words, new_words


def _build_sentence_splitter(eos_patterns: List[str]) -> Callable[[str], List[str]]:
    return _build_symbol_splitter(eos_patterns)


def _build_word_splitter(eow_patterns: List[str]) -> Callable[[str], List[str]]:
    return _build_symbol_splitter(eow_patterns)


def _build_symbol_splitter(symbols: List[str]) -> Callable[[str], List[str]]:
    # Construct the non-symbol pattern
    non_symbol_pattern = f"(?:(?!{'|'.join(symbols)}).)+"

    # Construct the symbol pattern
    symbol_pattern = "|".join(symbols)

    # Pattern to check if entire string consists of only symbols
    only_symbol_matcher = re.compile(f"^(?:{symbol_pattern})+$")

    # Modify the word pattern to capture leading symbols
    word_pattern = f"(?:{symbol_pattern})*{non_symbol_pattern}(?:{symbol_pattern})*"
    word_splitter = re.compile(word_pattern)

    def splitter(text: str) -> List[str]:
        if only_symbol_matcher.match(text):
            return [text]
        return word_splitter.findall(text)

    return splitter
