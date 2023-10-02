from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..graph import Graph, Node


class Evaluator:
    def prepare(self, graph: 'Graph'):
        return

    def get_score(self, node: 'Node') -> float | int:
        raise NotImplementedError

    def remove_transition(self, prefix_node: 'Node', word: str, suffix_node: 'Node'):
        return
