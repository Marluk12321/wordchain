from typing import TYPE_CHECKING

from . import _base

if TYPE_CHECKING:
    from ..graph import Graph


class Repeater(_base.WordChainGenerator):
    __slots__ = '_inner', '_repeats',
    _inner: _base.WordChainGenerator
    _repeats: int

    def __init__(self, inner_generator: _base.WordChainGenerator, repeats: int):
        self._inner = inner_generator
        self._repeats = repeats
        super().__init__()

    def generate(self, graph: 'Graph') -> tuple[str]:
        best_chain: tuple[str] = tuple()
        initial_grap_state = graph.get_state()
        for _ in range(self._repeats):
            chain = self._inner.generate(graph)
            if len(chain) > len(best_chain):
                best_chain = chain
            graph.set_state(initial_grap_state)
        return best_chain
