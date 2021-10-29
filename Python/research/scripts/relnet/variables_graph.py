#!/usr/bin/python
# -*- coding: utf-8 -*-

r"""
                __              __\/
              | S  \          | R  \
              \ __ |          \ __ |
              /    \          /
            /       \       /
       __ /          \ __ /            __
     | N  \          | G  \          | A  \
     \ __ |          \ __ |          \ __ |

   # # # # # # # # # # # # # # # # # # # # # #

author: CAB
website: github.com/alexcab
created: 2021-10-29
"""

from typing import Any, Dict, Set

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scripts.relnet.sample_graph import ValueNode, RelationEdge


class VariableNode:
    """
    Immutable variable node which contain all variable values
    """

    def __init__(self, variable: Any, value_nodes: Dict['ValueNode', int]):
        self.variable: Any = variable
        self.value_nodes: frozenset[('ValueNode', int)] = frozenset(value_nodes.items())
        self._value_nodes_dict: Dict['ValueNode', int] = value_nodes

    def __copy__(self):
        raise AssertionError("[VariableNode.__copy__] variable node should not be copied")

    def __repr__(self):
        values = ",".join(sorted([f"{n.value}({c})" for n, c in self.value_nodes]))
        return f"({self.variable}:{{{values}}})"

    def __hash__(self):
        return (self.variable, self.value_nodes).__hash__()

    def __eq__(self, other: Any):
        if isinstance(other, VariableNode):
            return self.variable == other.variable and self.value_nodes == other.value_nodes
        return False

    def unobserved_count(self, number_of_outcomes: int) -> int:
        return number_of_outcomes - sum(self._value_nodes_dict.values())


class VariableEdge:
    """
    Immutable variable edge which contain all relation in between variables
    """

    def __init__(self, endpoints: frozenset[Any], relation_edges: Dict['RelationEdge', int]):
        self.endpoints: frozenset[Any] = endpoints
        self.relation_edges: frozenset[('ValueNode', int)] = frozenset(relation_edges.items())
        self._relation_edges_dict: Dict['RelationEdge', int] = relation_edges

    def __copy__(self):
        raise AssertionError("[VariableEdge.__copy__] variable edge should not be copied")

    def __repr__(self):
        ep = sorted(list(self.endpoints))
        relations = ",".join(sorted([f"{e.relation}({c})" for e, c in self.relation_edges]))
        return f"({ep[0]})--{{{relations}}}--({ep[1]})"

    def __hash__(self):
        return (self.endpoints, self.relation_edges).__hash__()

    def __eq__(self, other: Any):
        if isinstance(other, VariableEdge):
            return self.endpoints == other.endpoints and self.relation_edges == other.relation_edges
        return False


class VariablesGraph:
    """
    Immutable variables graph which represent folded structure of set of outcomes
    """

    def __init__(self, nodes: Set[VariableNode], edges: Set[VariableEdge], name: str):
        self.nodes: frozenset[VariableNode] = frozenset(nodes)
        self.edges: frozenset[VariableEdge] = frozenset(edges)
        self.name: str = name

    def __copy__(self):
        raise AssertionError("[VariablesGraph.__copy__] folded graph should not be copied")

    def __repr__(self):
        return self.name

    def __eq__(self, other: Any):
        if isinstance(other, VariablesGraph):
            return self.nodes == other.nodes and self.edges == other.edges
        return False
