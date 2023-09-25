from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..graph import Graph, Node


class Evaluator:
    def prepare(self, graph: 'Graph'):
        return

    def get_score(self, node: 'Node') -> float | int:
        raise NotImplementedError

    def remove_word(self, node: 'Node', word: str):
        return
