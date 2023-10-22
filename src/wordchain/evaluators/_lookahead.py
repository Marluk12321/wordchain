import collections
from typing import Iterable, TYPE_CHECKING

from . import _base

if TYPE_CHECKING:
    from ..graph import Graph, Node


class LookaheadEvaluator(_base.Evaluator):
    __slots__ = ('_leaf_evaluator', '_lookahead_depth', '_score_at_depth', '_score',
                 '_predecessors', '_transitions_between')
    _leaf_evaluator: _base.Evaluator
    _lookahead_depth: int
    _score_at_depth: dict['Node', dict[int, int]]  # node -> depth -> transition_count
    _score: dict['Node', int | float]  # node -> score
    _predecessors: dict['Node', set['Node']]  # node -> predecessors
    _transitions_between: dict[tuple['Node', 'Node'], int]  # (prefix, suffix) -> transition_count

    def __init__(self, leaf_evaluator: _base.Evaluator, lookahead_depth: int = 1):
        if lookahead_depth < 1:
            raise ValueError(f'lookahead_depth needs to be > 0, got {lookahead_depth}')
        self._leaf_evaluator = leaf_evaluator
        self._lookahead_depth = lookahead_depth
        super().__init__()

    def _init_caches(self):
        self._score_at_depth = collections.defaultdict(lambda: collections.defaultdict(int))
        self._score = {}
        self._predecessors = collections.defaultdict(set)
        self._transitions_between = collections.defaultdict(int)

    def _calculate_score_at(self, node: 'Node', depth: int) -> int:
        scores = self._score_at_depth[node]
        score = scores.get(depth)
        if score is None:
            if depth == 1:
                score = self._leaf_evaluator.get_score(node)
            else:
                unique_successors = frozenset(node.transitions.values())
                score = sum(self._calculate_score_at(next_node, depth - 1)
                            for next_node in unique_successors)
            scores[depth] = score
        return score

    def _calculate_score(self, node: 'Node'):
        scores = self._score_at_depth[node]
        score = 0
        for depth, count in scores.items():
            if count > 0:
                score = depth * count
        self._score[node] = score

    def _populate_caches(self, graph: 'Graph'):
        for node in graph.start.transitions.values():
            self._predecessors[node].add(graph.start)
            self._transitions_between[graph.start, node] += 1
            for successor in node.transitions.values():
                self._predecessors[successor].add(node)
                self._transitions_between[node, successor] += 1
            self._calculate_score_at(node, self._lookahead_depth)
            self._calculate_score(node)
        self._score[graph.end] = 0

    def prepare(self, graph: 'Graph'):
        self._init_caches()
        self._leaf_evaluator.prepare(graph)
        self._populate_caches(graph)

    def get_score(self, node: 'Node') -> float | int:
        return self._score[node]

    def _iter_nodes_to_update(self, node: 'Node') -> Iterable[tuple[int, 'Node']]:
        to_process: list[tuple[int, 'Node']] = [(0, node)]
        current_index = 0
        while current_index < len(to_process):
            distance, node = to_process[current_index]
            yield distance, node
            if distance < self._lookahead_depth - 1:  # expand until max distance
                to_process.extend((distance + 1, predecessor) for predecessor in self._predecessors[node])
            current_index += 1

    def _remove_unreachable_scores(self, node: 'Node', unreachable_depth: int,
                                   unreachable_scores: dict[int, int]):
        scores = self._score_at_depth[node]
        for depth in range(unreachable_depth, self._lookahead_depth + 1):
            relative_depth = depth - unreachable_depth
            scores[depth] -= unreachable_scores[relative_depth]
        self._calculate_score(node)

    def remove_transition(self, prefix_node: 'Node', word: str, suffix_node: 'Node'):
        self._leaf_evaluator.remove_transition(prefix_node, word, suffix_node)
        new_prefix_score = self._leaf_evaluator.get_score(prefix_node)
        prefix_scores = self._score_at_depth[prefix_node]
        prefix_score_diff = prefix_scores[1] - new_prefix_score

        self._transitions_between[prefix_node, suffix_node] -= 1
        if self._transitions_between[prefix_node, suffix_node] > 0:
            # suffix is still reachable via another word
            for distance, predecessor in self._iter_nodes_to_update(prefix_node):
                self._score_at_depth[predecessor][distance + 1] -= prefix_score_diff
        else:
            # suffix is no longer reachable
            unreachable_scores = {0: prefix_score_diff}
            suffix_scores = self._score_at_depth[suffix_node]
            unreachable_scores.update(suffix_scores)
            for distance, predecessor in self._iter_nodes_to_update(prefix_node):
                self._remove_unreachable_scores(predecessor, distance + 1, suffix_scores)
            self._predecessors[suffix_node].remove(prefix_node)
