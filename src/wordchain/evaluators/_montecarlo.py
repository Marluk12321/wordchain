from typing import TYPE_CHECKING

from .. import generators

from . import _base

if TYPE_CHECKING:
    from ..graph import Graph, Node


class MonteCarloEvaluator(_base.Evaluator):
    __slots__ = '_graph', '_samples', '_evaluator',
    _graph: 'Graph'
    _samples: int
    _evaluator: _base.Evaluator

    def __init__(self, samples: int, evaluator: _base.Evaluator):
        

    def prepare(self, graph: 'Graph'):
        self._graph = graph

    def get_score(self, node: 'Node') -> float | int:

