import random
from typing import TYPE_CHECKING

from . import _base

if TYPE_CHECKING:
    from ..graph import Graph, Node


class RandomGenerator(_base.StepByStepGenerator):
    __slots__ = '_repeats',
    _repeats: int

    def __init__(self, repeats: int):
        self._repeats = repeats
        super().__init__()

    def _pick_next_word(self, graph: 'Graph', node: 'Node') -> str:
        return random.choice(tuple(node.transitions))

    def generate(self, graph: 'Graph') -> tuple[str]:
        best_chain: tuple[str] = ()
        for _ in range(self._repeats):
            chain = super().generate(graph)
            if len(chain) > len(best_chain):
                best_chain = chain
            graph.restore_transitions()
        return best_chain
