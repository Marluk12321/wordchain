import random

from ..graph import Graph, Node

from . import _base


class RandomGenerator(_base.StepByStepGenerator):
    __slots__ = '_repeats',
    _repeats: int

    def __init__(self, repeats: int):
        self._repeats = repeats
        super().__init__()

    def _pick_next_word(self, node: Node) -> (str | None):
        unseen_words = tuple(self._iter_unseen_words(node))
        return (random.choice(unseen_words) if len(unseen_words) > 0
                else None)

    def generate(self, graph: Graph) -> tuple[str] | tuple[()]:
        best_chain: tuple[str] | tuple[()] = ()
        for _ in range(self._repeats):
            chain = super().generate(graph)
            if len(chain) > len(best_chain):
                best_chain = chain
        return best_chain
