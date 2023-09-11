import collections
from typing import Iterable, TYPE_CHECKING

from . import _base

if TYPE_CHECKING:
    from ..graph import Graph, Node


class DeterministicIntuitiveGenerator(_base.StepByStepGenerator):
    __slots__ = '_lookahead_depth', '_count_cache', '_end_count_cache', '_predecessors'
    _lookahead_depth: int
    _count_cache: dict['Node', dict[int, int]]  # node -> depth -> transition_count
    _end_count_cache: dict['Node', int]
    _predecessors: dict['Node', set['Node']]  # node -> distance -> predecessors

    def __init__(self, lookahead_depth: int = 1):
        if lookahead_depth < 1:
            raise ValueError(f'lookahead_depth needs to be > 0, got {lookahead_depth}')
        self._lookahead_depth = lookahead_depth
        self._count_cache = collections.defaultdict(lambda: collections.defaultdict(int))
        self._end_count_cache = {}
        self._predecessors = collections.defaultdict(set)
        super().__init__()

    def _calculate_transition_count(self, node: 'Node', depth: int) -> int:
        transition_counts = self._count_cache[node]
        transition_count = transition_counts.get(depth)
        if transition_count is None:
            if depth == 1:
                transition_count = len(node.transitions)
            else:
                transition_count = sum(self._calculate_transition_count(next_node, depth - 1)
                                       for next_node in node.transitions.values())
            transition_counts[depth] = transition_count
        return transition_count

    def _update_end_count_cache(self, node: 'Node'):
        self._end_count_cache[node] = self._count_cache[node][self._lookahead_depth]

    def _populate_caches(self, graph: 'Graph'):
        for node in graph.start.transitions.values():
            for successor in node.transitions.values():
                self._predecessors[successor].add(node)
            self._calculate_transition_count(node, self._lookahead_depth)
            self._update_end_count_cache(node)
        self._end_count_cache[graph.end] = 0

    def _reduce_cached_counts(self, node: 'Node', distance: int, reductions: dict[int, int]):
        node_counts = self._count_cache[node]
        for depth in range(distance, self._lookahead_depth + 1):
            reduction = (1 if depth == distance else reductions[depth - distance])
            node_counts[depth] -= reduction
        self._update_end_count_cache(node)

    def _iter_predecessors(self, node: 'Node', max_distance) -> Iterable[tuple[int, 'Node']]:
        to_process: collections.deque[tuple[int, 'Node']] = collections.deque(((0, node),))
        while len(to_process) > 0:
            distance, node = to_process.popleft()
            if distance > 0:
                yield distance, node
            if distance < max_distance:
                to_process.extend((distance + 1, predecessor) for predecessor in self._predecessors[node])

    def _update_cache(self, node: 'Node', removed_word: str):
        removed_node = node.transitions[removed_word]
        removed_counts = self._count_cache[removed_node]
        self._reduce_cached_counts(node, 1, removed_counts)
        for distance, predecessor in self._iter_predecessors(node, self._lookahead_depth - 1):
            self._reduce_cached_counts(predecessor, distance + 1, removed_counts)

    def _pick_next_word(self, graph: 'Graph', node: 'Node') -> str:
        most_transitions: int = -1
        best_word: str | None = None
        for word, next_node in node.transitions.items():
            if len(word) == 2:
                best_word = word
                break
            transition_count = self._end_count_cache[next_node]
            if transition_count > most_transitions:
                best_word = word
                most_transitions = transition_count
        self._update_cache(node, best_word)
        return best_word

    def _clear_caches(self):
        self._end_count_cache.clear()
        self._count_cache.clear()
        self._predecessors.clear()

    def generate(self, graph: 'Graph') -> tuple[str]:
        self._populate_caches(graph)
        chain = super().generate(graph)
        self._clear_caches()
        return chain
