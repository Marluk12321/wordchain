from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..graph import Graph, Node


class WordChainGenerator:
    def generate(self, graph: 'Graph') -> tuple[str]:
        raise NotImplementedError


class StepByStepGenerator(WordChainGenerator):
    def _pick_next_word(self, graph: 'Graph', node: 'Node') -> str:
        raise NotImplementedError

    def generate(self, graph: 'Graph') -> tuple[str]:
        chain: list[str] = []
        node = graph.start
        while node is not graph.end:
            word = self._pick_next_word(graph, node)
            chain.append(word)
            node = node.pop(word)
        return tuple(chain[1:-1])
