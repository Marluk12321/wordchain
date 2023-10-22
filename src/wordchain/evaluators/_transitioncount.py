from typing import TYPE_CHECKING

from . import _base

if TYPE_CHECKING:
    from ..graph import Node


class TransitionCountEvaluator(_base.Evaluator):
    def get_score(self, node: 'Node') -> float | int:
        return len(node.transitions)
