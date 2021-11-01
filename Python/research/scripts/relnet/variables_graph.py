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
created: 2021-11-01
"""

from typing import Any, Dict, Set, Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.relnet.sample_graph import SampleGraphComponentsProvider


class VariableNode:
    """
    Immutable node which represent an variable
    """

    def __init__(self, variable: Any):
        self.variable: Any = variable

    def __copy__(self):
        raise AssertionError("[VariableNode.__copy__] variable node should not be copied")

    def __repr__(self):
        return f"({self.variable})"

    def __hash__(self):
        return self.variable.__hash__()

    def __eq__(self, other: Any):
        if isinstance(other, VariableNode):
            return self.variable == other.variable
        return False


class VariableEdge:
    """
    Immutable edge in between variables
    """

    def __init__(self, endpoints: Set[Any]):
        assert len(endpoints) == 2, f"[VariableEdge.__init__] Expect exactly 2 endpoints, got {endpoints}"
        self.endpoints: frozenset[Any] = frozenset(endpoints)

    def __copy__(self):
        raise AssertionError("[VariableEdge.__copy__] variable edge should not be copied")

    def __repr__(self):
        ep = sorted(self.endpoints)
        return f"({ep[0]})--({ep[1]})"

    def __hash__(self):
        return self.endpoints.__hash__()

    def __eq__(self, other: Any):
        if isinstance(other, VariableEdge):
            return self.endpoints == other.endpoints
        return False


class VariablesGraph:
    """
    Immutable graph which represent variables level of relation graph
    """

    def __init__(
            self,
            components_provider: 'SampleGraphComponentsProvider',
            number_of_outcomes: int,
            nodes: Set[VariableNode],
            edges: Set[VariableEdge],
            name: str
    ):
        self.number_of_outcomes: int = number_of_outcomes
        self.nodes: frozenset[VariableNode] = frozenset(nodes)
        self.edges: frozenset[VariableEdge] = frozenset(edges)
        self.name: str = name
        self.variables: frozenset[Any] = frozenset({n.variable for n in self.nodes})
        self._nodes_dict: Dict[Any, VariableNode] = {n.variable: n for n in nodes}
        self._components_provider: 'SampleGraphComponentsProvider' = components_provider

    def __copy__(self):
        raise AssertionError("[VariableGraph.__copy__] Variable graph should not be copied")

    def __repr__(self):
        return self.name

    def __eq__(self, other: Any):
        if isinstance(other, VariablesGraph):
            return self.nodes == other.nodes and self.edges == other.edges
        return False

    def variable(self, variable: Any) -> Optional[VariableNode]:
        """
        Find variable node for it's variable
        :param variable: variable to search on
        :return: VariableNode or None if not in this graph
        """
        return self._nodes_dict.get(variable)
