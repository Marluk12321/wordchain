from typing import Iterable


class _NodeState:
    __slots__ = '_active_words'
    _active_words: tuple[str]

    def __init__(self, transitions: Iterable[str]):
        self._active_words = tuple(transitions)

    @property
    def active_words(self) -> tuple[str]:
        return self._active_words

    def __eq__(self, other):
        return (isinstance(other, _NodeState) and
                other._active_words == self._active_words)


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

    def get_state(self) -> _NodeState:
        return _NodeState(self.transitions)

    def set_state(self, state: _NodeState):
        assert frozenset(state.active_words) == frozenset(self.transitions) | frozenset(self._hidden_transitions)
        # clear to preserve original order
        self._hidden_transitions.update(self.transitions)
        self.transitions.clear()
        for word in state.active_words:
            self.transitions[word] = self._hidden_transitions.pop(word)


class _GraphState:
    __slots__ = '_start_state', '_node_states'
    _start_state: _NodeState
    _node_states: dict[str, _NodeState]

    def __init__(self, start_node: Node):
        self._start_state = start_node.get_state()
        self._node_states = {node.value: node.get_state()
                             for node in start_node.transitions.values()}

    @property
    def start_state(self) -> _NodeState:
        return self._start_state

    @property
    def node_states(self) -> dict[str, _NodeState]:
        return self._node_states

    def __eq__(self, other):
        return (isinstance(other, _GraphState) and
                other._start_state == self._start_state and
                other._node_states == self._node_states)


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

    def get_state(self) -> _GraphState:
        return _GraphState(self.start)

    def set_state(self, state: _GraphState):
        self.start.set_state(state.start_state)
        nodes: dict[str, Node] = {node.value: node for node in self.start.transitions.values()}
        assert frozenset(state.node_states) == frozenset(nodes)
        for node_value, node_state in state.node_states.items():
            nodes[node_value].set_state(node_state)
