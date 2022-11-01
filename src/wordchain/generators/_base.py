from typing import Iterable

from ..graph import Graph, Node


class WordChainGenerator:
    def generate(self, graph: Graph) -> tuple[str]:
        raise NotImplementedError


class StepByStepGenerator(WordChainGenerator):
    __slots__ = '_seen_words'
    _seen_words: set[str]

    def __init__(self):
        self._seen_words = set()

    def _iter_unseen_words(self, node: Node) -> Iterable[str]:
        return (word for word in node.transitions
                if word not in self._seen_words)

    def _pick_next_word(self, node: Node) -> (str | None):
        raise NotImplementedError

    def generate(self, graph: Graph) -> tuple[str] | tuple[()]:
        chain: list[str] = []
        node = graph.start
        while node is not graph.end:
            word = self._pick_next_word(node)
            chain.append(word)
            self._seen_words.add(word)
            node = node.transitions[word]
        self._seen_words.clear()
        return tuple(chain[1:-1])
