import collections
from typing import Iterable, TYPE_CHECKING

from . import _base

if TYPE_CHECKING:
    from ..graph import Graph, Node


class DeterministicIntuitiveGenerator(_base.StepByStepGenerator):
    __slots__ = '_lookahead_depth', '_transitions_at_depth', '_transitions_at_max_depth', '_predecessors'
    _lookahead_depth: int
    _transitions_at_depth: dict['Node', dict[int, int]]  # node -> depth -> transition_count
    _transitions_at_max_depth: dict['Node', int]  # node -> transition_count
    _predecessors: dict['Node', set['Node']]  # node -> predecessors

    def __init__(self, lookahead_depth: int = 1):
        if lookahead_depth < 1:
            raise ValueError(f'lookahead_depth needs to be > 0, got {lookahead_depth}')
        self._lookahead_depth = lookahead_depth
        self._transitions_at_depth = collections.defaultdict(lambda: collections.defaultdict(int))
        self._transitions_at_max_depth = {}
        self._predecessors = collections.defaultdict(set)
        super().__init__()

    def _calculate_transition_count(self, node: 'Node', depth: int) -> int:
        transition_counts = self._transitions_at_depth[node]
        transition_count = transition_counts.get(depth)
        if transition_count is None:
            if depth == 1:
                transition_count = len(node.transitions)
            else:
                unique_successors = frozenset(node.transitions.values())
                transition_count = sum(self._calculate_transition_count(next_node, depth - 1)
                                       for next_node in unique_successors)
            transition_counts[depth] = transition_count
        return transition_count

    def _update_transitions_at_max_depth(self, node: 'Node'):
        self._transitions_at_max_depth[node] = self._transitions_at_depth[node][self._lookahead_depth]

    def _populate_caches(self, graph: 'Graph'):
        for node in graph.start.transitions.values():
            self._transitions_to_successor[graph.start][node] += 1
            for successor in node.transitions.values():
                self._predecessors[successor].add(node)
                self._transitions_to_successor[node][successor] += 1
            self._calculate_transition_count(node, self._lookahead_depth)
            self._update_transitions_at_max_depth(node)
        self._transitions_at_max_depth[graph.end] = 0

    def _remove_unreachable_transition_counts(self, node: 'Node', unreachable_depth: int,
                                              unreachable_transitions: dict[int, int]):
        node_counts = self._transitions_at_depth[node]
        node_counts[unreachable_depth] -= 1
        for further_depth in range(unreachable_depth + 1, self._lookahead_depth + 1):
            relative_depth = further_depth - unreachable_depth
            node_counts[further_depth] -= unreachable_transitions[relative_depth]
        self._update_transitions_at_max_depth(node)

    def _iter_predecessors(self, node: 'Node', max_distance: int) -> Iterable[tuple[int, 'Node']]:
        to_process: list[tuple[int, 'Node']] = [(0, node)]
        current_index = 0
        while current_index < len(to_process):
            distance, node = to_process[current_index]
            current_index += 1
            if distance > 0:
                yield distance, node
            # expand until max distance
            if distance < max_distance:
                to_process.extend((distance + 1, predecessor) for predecessor in self._predecessors[node])

    def _update_cache(self, node: 'Node', removed_word: str):
        unreachable_successor = node.transitions[removed_word]
        unreachable_transitions = self._transitions_at_depth[unreachable_successor]
        self._remove_unreachable_transition_counts(node, 1, unreachable_transitions)
        for distance, predecessor in self._iter_predecessors(node, self._lookahead_depth - 1):
            self._remove_unreachable_transition_counts(predecessor, distance + 1, unreachable_transitions)

    def _pick_next_word(self, graph: 'Graph', node: 'Node') -> str:
        most_transitions: int = -1
        best_word: str | None = None
        for word, next_node in node.transitions.items():
            if len(word) == 2:
                best_word = word
                break
            transition_count = self._transitions_at_max_depth[next_node]
            if transition_count > most_transitions:
                best_word = word
                most_transitions = transition_count
        self._update_cache(node, best_word)
        return best_word

    def _clear_caches(self):
        self._transitions_at_max_depth.clear()
        self._transitions_at_depth.clear()
        self._predecessors.clear()

    def generate(self, graph: 'Graph') -> tuple[str]:
        self._populate_caches(graph)
        chain = super().generate(graph)
        self._clear_caches()
        return chain
