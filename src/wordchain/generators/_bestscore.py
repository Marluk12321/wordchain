from typing import TYPE_CHECKING

from . import _base

if TYPE_CHECKING:
    from ..evaluators import Evaluator
    from ..graph import Graph, Node


class BestScoreGenerator(_base.StepByStepGenerator):
    __slots__ = '_evaluator',
    _evaluator: 'Evaluator'

    def __init__(self, evaluator: 'Evaluator'):
        self._evaluator = evaluator
        super().__init__()

    def _pick_next_word(self, graph: 'Graph', node: 'Node') -> str:
        best_score: float = -1.0
        best_word: str | None = None
        for word, next_node in node.transitions.items():
            if len(word) == 2:
                best_word = word
                break
            score = self._evaluator.get_score(next_node)
            if score > best_score:
                best_word = word
                best_score = score
        self._evaluator.remove_word(node, best_word)
        return best_word

    def generate(self, graph: 'Graph') -> tuple[str]:
        self._evaluator.prepare(graph)
        return super().generate(graph)
