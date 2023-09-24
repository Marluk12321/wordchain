import random
from typing import TYPE_CHECKING

from . import _base

if TYPE_CHECKING:
    from ..graph import Graph, Node


class RandomGenerator(_base.StepByStepGenerator):
    def _pick_next_word(self, graph: 'Graph', node: 'Node') -> str:
        return random.choice(tuple(node.transitions))
