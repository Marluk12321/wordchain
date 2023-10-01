import collections
from typing import Iterable, TYPE_CHECKING

from . import _base

if TYPE_CHECKING:
    from ..graph import Graph, Node


class IntuitiveEvaluator(_base.Evaluator):
    __slots__ = ('_lookahead_depth', '_transitions_at_depth', '_score',
                 '_predecessors', '_transitions_to_successor')
    _lookahead_depth: int
    _transitions_at_depth: dict['Node', dict[int, int]]  # node -> depth -> transition_count
    _score: dict['Node', int]  # node -> score
    _predecessors: dict['Node', set['Node']]  # node -> predecessors
    _transitions_to_successor: dict['Node', dict['Node', int]]  # node -> successor -> transition_count

    def __init__(self, lookahead_depth: int = 1):
        if lookahead_depth < 1:
            raise ValueError(f'lookahead_depth needs to be > 0, got {lookahead_depth}')
        self._lookahead_depth = lookahead_depth
        super().__init__()

    def _init_caches(self):
        self._transitions_at_depth = collections.defaultdict(lambda: collections.defaultdict(int))
        self._score = {}
        self._predecessors = collections.defaultdict(set)
        self._transitions_to_successor = collections.defaultdict(lambda: collections.defaultdict(int))

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

    def _calculate_score(self, node: 'Node'):
        transition_counts = self._transitions_at_depth[node]
        score = 0
        for depth, count in transition_counts.items():
            if count > 0:
                score = depth * count
        self._score[node] = score

    def _populate_caches(self, graph: 'Graph'):
        for node in graph.start.transitions.values():
            self._predecessors[node].add(graph.start)
            self._transitions_to_successor[graph.start][node] += 1
            for successor in node.transitions.values():
                self._predecessors[successor].add(node)
                self._transitions_to_successor[node][successor] += 1
            self._calculate_transition_count(node, self._lookahead_depth)
            self._calculate_score(node)
        self._score[graph.end] = 0

    def prepare(self, graph: 'Graph'):
        self._init_caches()
        self._populate_caches(graph)

    def get_score(self, node: 'Node') -> float | int:
        return self._score[node]

    def _remove_unreachable_transition_counts(self, node: 'Node', unreachable_depth: int,
                                              unreachable_transitions: dict[int, int]):
        node_counts = self._transitions_at_depth[node]
        node_counts[unreachable_depth] -= 1
        for further_depth in range(unreachable_depth + 1, self._lookahead_depth + 1):
            relative_depth = further_depth - unreachable_depth
            node_counts[further_depth] -= unreachable_transitions[relative_depth]
        self._calculate_score(node)

    def _iter_nodes_to_update(self, node: 'Node') -> Iterable[tuple[int, 'Node']]:
        to_process: list[tuple[int, 'Node']] = [(0, node)]
        current_index = 0
        while current_index < len(to_process):
            distance, node = to_process[current_index]
            yield distance, node
            if distance < self._lookahead_depth - 1:  # expand until max distance
                to_process.extend((distance + 1, predecessor) for predecessor in self._predecessors[node])
            current_index += 1

    def remove_word(self, node: 'Node', word: str):
        successor = node.transitions[word]
        transitions_to_successor = self._transitions_to_successor[node]
        transitions_to_successor[successor] -= 1
        if transitions_to_successor[successor] > 0:
            # successor is still reachable via another word
            for distance, predecessor in self._iter_nodes_to_update(node):
                self._transitions_at_depth[predecessor][distance + 1] -= 1
        else:
            # successor is no longer reachable
            successor_transitions = self._transitions_at_depth[successor]
            for distance, predecessor in self._iter_nodes_to_update(node):
                self._remove_unreachable_transition_counts(predecessor, distance + 1, successor_transitions)
            self._predecessors[successor].remove(node)
