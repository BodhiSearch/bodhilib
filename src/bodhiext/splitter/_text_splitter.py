import re
from typing import Callable, Iterable, List, Optional, Tuple

from bodhilib import BaseSplitter, Document, Node


class TextSplitter(BaseSplitter):
    """Splitter splits a :class:`~bodhilib.Document` into :class:`~bodhilib.Node`."""

    def __init__(
        self,
        *,
        max_len: int = 512,
        min_len: int = 128,
        overlap: int = 16,
        eos_patterns: Optional[List[str]] = None,
        eow_patterns: Optional[List[str]] = None,
    ) -> None:
        r"""Initializing splitter to split text based on sentence and word splits.

        Args:
            max_len (Optional[int]): Maximum number of words in split text. Defaults to 512.
            min_len (Optional[int]): Minimum number of words in split text. Defaults to 128.
            overlap (Optional[int]): Number of words to overlap between splits. Defaults to 16.
            eos_patterns (Optional[List[str]]): List of patterns to split sentences.
                The patterns should be regex. E.g. `[r"\n", r"\."]`.
                Defaults to `[r"\.", r"\?", r"\!", r"\n"]`.
            eow_patterns (Optional[List[str]]): List of patterns to split words.
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

    def _split(self, docs: Iterable[Document]) -> List[Node]:
        nodes = []
        for doc in docs:
            current_words: List[str] = []
            sentences = self.sentence_splitter(doc.text)
            for sentence in sentences:
                words = self.word_splitter(sentence)
                # the sentence can be combined without exceeding max_len
                if len(current_words) + len(words) < self.max_len:
                    current_words += words
                    words = []
                    continue
                # the sentence cannot be combined without exceeding max_len
                new_nodes, new_current_words, new_words = self._build_nodes(doc, current_words, words)
                nodes.extend(new_nodes)
                assert new_words == [], f"{new_words=} should be empty"
                current_words = new_current_words
            if len(current_words) > self.overlap:
                node_text = "".join(current_words)
                node = Node(text=node_text, parent=doc)
                nodes.append(node)
        return nodes

    def _build_nodes(
        self, doc: Document, current_words: List[str], words: List[str]
    ) -> Tuple[List[Node], List[str], List[str]]:
        nodes = []
        while True:
            # start of sentence, take all the words
            if len(current_words) == 0:
                current_words = words
                words = []
                continue

            # the sentence can be combined with next sentence without exceeding max_len
            if len(words) != 0 and len(current_words) + len(words) < self.max_len:
                current_words += words
                words = []
                continue

            # current sentence has more words than max_len
            # take the max len words and build the node, pass the remaining words to next iteration
            if len(current_words) >= self.max_len:
                node_text = "".join(current_words[: self.max_len])
                remaining_words = current_words[self.max_len - self.overlap :]
                new_node = Node(text=node_text, parent=doc)
                nodes.append(new_node)
                current_words = remaining_words
                continue

            # if combined  with next sentence, the words will exceed max_len
            # and current words is more than min_len
            # so build the node with current words, pass the remaining words to next iteration
            if len(current_words) + len(words) > self.max_len and len(current_words) >= self.min_len:
                node_text = "".join(current_words)
                new_node = Node(text=node_text, parent=doc)
                nodes.append(new_node)
                remaining_words = current_words[-self.overlap :] if self.overlap != 0 else []
                current_words = remaining_words
                continue

            # if combined  with next sentence, the words will exceed max_len
            # and current words is less than min_len
            # so take as many words needed to reach min_len, build the node and return remaining words to next iteration
            if len(current_words) + len(words) > self.max_len and len(current_words) < self.min_len:
                all_words = current_words + words
                node_text = "".join(all_words[: self.min_len])
                new_node = Node(text=node_text, parent=doc)
                nodes.append(new_node)
                remaining_words = all_words[self.min_len - self.overlap :]
                current_words = remaining_words
                words = []
                continue

            # the combined sentence will be less than max_len
            # add the words and return
            current_words += words
            words = []
            break
        return nodes, current_words, words


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
