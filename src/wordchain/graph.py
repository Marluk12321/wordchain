from typing import Iterable


class Node:
    __slots__ = 'value', 'transitions', '_hidden_transitions', '_hash'
    value: str
    transitions: dict[str, 'Node']
    _hidden_transitions: dict[str, 'Node']
    _hash: int

    def __init__(self, value: str):
        self.value = value
        self.transitions = {}
        self._hidden_transitions = {}
        self._hash = hash(value)

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other) -> bool:
        return (isinstance(other, Node)
                and self.value == other.value)

    def __repr__(self):
        return f'<{type(self).__name__}[{id(self):#x}] value={repr(self.value)}>'

    def pop(self, word: str) -> 'Node':
        node = self.transitions.pop(word)
        self._hidden_transitions[word] = node
        return node

    def reset(self):
        self.transitions.update(self._hidden_transitions)
        self._hidden_transitions.clear()


class Graph:
    __slots__ = 'start', 'end'
    start: Node
    end: Node

    def __init__(self, words: Iterable[str]):
        self.start = Node('<start>')
        self.end = Node('<end>')
        nodes: dict[str, Node] = {}
        for word in words:
            prefix = word[:2]
            suffix = word[-2:]
            if (prefix_node := nodes.get(prefix)) is None:
                prefix_node = self._make_node(prefix)
                nodes[prefix] = prefix_node
            if (suffix_node := nodes.get(suffix)) is None:
                suffix_node = self._make_node(suffix)
                nodes[suffix] = suffix_node
            prefix_node.transitions[word] = suffix_node

    def _connect_to_start(self, node: Node):
        start = self.start
        start_transition_key = f'<start_{node.value}>'
        start.transitions[start_transition_key] = node

    def _connect_to_end(self, node: Node):
        end = self.end
        end_transition_key = f'<{node.value}_end>'
        node.transitions[end_transition_key] = end

    def _make_node(self, value: str) -> Node:
        node = Node(value)
        self._connect_to_start(node)
        self._connect_to_end(node)
        return node

    def reset(self):
        self.start.reset()
        for node in self.start.transitions.values():
            node.reset()

    def make_checkpoint(self) -> 'Graph':
        checkpoint = Graph(())
        checkpoint_nodes: dict[str, Node] = {node.value: checkpoint._make_node(node.value)
                                             for node in self.start.transitions.values()}
        for node in self.start.transitions.values():
            checkpoint_node = checkpoint_nodes[node.value]
            checkpoint_node.transitions.update({word: checkpoint_nodes[word[-2:]]
                                                for word, successor in node.transitions.items()
                                                if successor is not self.end})
        return checkpoint
