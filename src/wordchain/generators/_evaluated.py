from typing import TYPE_CHECKING

from . import _base

if TYPE_CHECKING:
    from ..evaluators import Evaluator
    from ..graph import Graph, Node


class EvaluatedGenerator(_base.StepByStepGenerator):
    __slots__ = '_evaluator',
    _evaluator: 'Evaluator'

    def __init__(self, evaluator: 'Evaluator'):
        self._evaluator = evaluator
        super().__init__()

    def _pop_word(self, node: 'Node', word: str) -> 'Node':
        next_node = super()._pop_word(node, word)
        self._evaluator.remove_transition(node, word, next_node)
        return next_node

    def generate(self, graph: 'Graph') -> tuple[str]:
        self._evaluator.prepare(graph)
        return super().generate(graph)
