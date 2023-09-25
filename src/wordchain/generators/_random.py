import random
from typing import TYPE_CHECKING

from . import _base

if TYPE_CHECKING:
    from ..evaluators import Evaluator
    from ..graph import Graph, Node


__all__ = 'RandomGenerator', 'WeightedRandomGenerator'


class RandomGenerator(_base.StepByStepGenerator):
    def _pick_next_word(self, graph: 'Graph', node: 'Node') -> str:
        return random.choice(tuple(node.transitions))


class WeightedRandomGenerator(_base.StepByStepGenerator):
    __slots__ = '_evaluator',
    _evaluator: 'Evaluator'

    def __init__(self, evaluator: 'Evaluator'):
        self._evaluator = evaluator
        super().__init__()

    def _pick_next_word(self, graph: 'Graph', node: 'Node') -> str:
        scores = tuple(self._evaluator.get_score(next_node) + 1  # avoid having all 0s
                       for next_node in node.transitions.values())
        return random.choices(tuple(node.transitions), weights=scores)[0]

    def generate(self, graph: 'Graph') -> tuple[str]:
        self._evaluator.prepare(graph)
        return super().generate(graph)
