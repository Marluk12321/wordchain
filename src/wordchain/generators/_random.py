import random
from typing import TYPE_CHECKING

from . import _base
from . import _evaluated

if TYPE_CHECKING:
    from ..graph import Graph, Node


__all__ = 'RandomGenerator', 'WeightedRandomGenerator'


class RandomGenerator(_base.StepByStepGenerator):
    def _pick_next_word(self, graph: 'Graph', node: 'Node') -> str:
        if node.value in node.transitions:
            return node.value
        end_word: str | None = None
        non_end_words: list[str] = []
        for word, next_node in node.transitions.items():
            if next_node is graph.end:
                end_word = word
            else:
                non_end_words.append(word)
        return random.choice(non_end_words) if len(non_end_words) > 0 else end_word


class WeightedRandomGenerator(_evaluated.EvaluatedGenerator):
    def _pick_next_word(self, graph: 'Graph', node: 'Node') -> str:
        if node.value in node.transitions:
            return node.value
        end_word: str | None = None
        non_end_words: list[str] = []
        non_end_scores: list[float | int] = []
        for word, next_node in node.transitions.items():
            if next_node is graph.end:
                end_word = word
            else:
                non_end_words.append(word)
                non_end_scores.append(self._evaluator.get_score(next_node))
        chosen_word = (random.choices(non_end_words, weights=non_end_scores)[0]
                       if len(non_end_words) > 0 else end_word)
        return chosen_word
