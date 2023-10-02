from typing import TYPE_CHECKING

from . import _evaluated

if TYPE_CHECKING:
    from ..graph import Graph, Node


__all__ = 'BestScoreGenerator',


class BestScoreGenerator(_evaluated.EvaluatedGenerator):
    def _pick_next_word(self, graph: 'Graph', node: 'Node') -> str:
        if node.value in node.transitions:
            return node.value
        best_score: float = -1.0
        best_word: str | None = None
        for word, next_node in node.transitions.items():
            score = self._evaluator.get_score(next_node)
            if score > best_score:
                best_word = word
                best_score = score
        return best_word
