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
from pyvis.network import Network

from .variables_graph import VariableNode, VariableEdge, VariablesGraph
from .graph_components import SampleGraphComponentsProvider


class ActiveNode(VariableNode):
    """
    Immutable node which contain all variable values and its weights
    """

    def __init__(self, variable: Any, values: Dict[Any, float], in_query: bool):
        super().__init__(variable)
        self.values: frozenset[(Any, float)] = frozenset(values.items())
        self.in_query = in_query
        self._values_dict: Dict[Any, float] = values

    def __repr__(self):
        values = ",".join(sorted([f"{v}({w})" for v, w in self.values]))
        in_query = "Q" if self.in_query else ""
        return f"{in_query}({self.variable}:{{{values}}})"

    def __hash__(self):
        return (self.variable, self.values).__hash__()

    def __eq__(self, other: Any):
        if isinstance(other, ActiveNode):
            return self.variable == other.variable and self.values == other.values and self.in_query == other.in_query
        return False


class ActiveEdge(VariableEdge):
    """
    Immutable edge which contain all relation in between variables and they count
    """

    def __init__(self, endpoints: Set[Any], relations: Dict[Any, int], in_query: bool):
        super().__init__(endpoints)
        self.relations: frozenset[(Any, int)] = frozenset(relations.items())
        self.in_query = in_query
        self._relation_edges_dict: Dict[Any, int] = relations

    def __repr__(self):
        ep = sorted(self.endpoints)
        relations = ",".join(sorted([f"{r}({c})" for r, c in self.relations]))
        in_query = "Q" if self.in_query else ""
        return f"({ep[0]})--{in_query}{{{relations}}}--({ep[1]})"

    def __hash__(self):
        return (self.endpoints, self.relations).__hash__()

    def __eq__(self, other: Any):
        if isinstance(other, ActiveEdge):
            return self.endpoints == other.endpoints\
                   and self.relations == other.relations\
                   and self.in_query == other.in_query
        return False


class ActivationGraph(VariablesGraph):
    """
    Immutable graph which represent folded structure of set of outcomes
    """

    def __init__(
            self,
            components_provider: SampleGraphComponentsProvider,
            number_of_outcomes: int,
            nodes: Set[ActiveNode],
            edges: Set[ActiveEdge],
            name: str
    ):
        super().__init__(components_provider, number_of_outcomes, nodes, edges, name)
        self.nodes: frozenset[ActiveNode] = frozenset(nodes)
        self.edges: frozenset[ActiveEdge] = frozenset(edges)

    def visualize(self, name: Optional[str] = None, height: str = "1024px", width: str = "1024px") -> None:
        """
        Will render this variable graph as HTML page and show in browser
        :param name: optional name of this visualization, if None then self.name will passed
        :param height: window height
        :param width: window width
        :return: None
        """
        net = Network(height=height, width=width)
        file_name = "".join(c for c in (name if name else self.name) if c.isalnum() or c == '_')
        active_nodes = {n.variable: n for n in self.nodes}

        for var, values in self._components_provider.variables():
            if var not in active_nodes:  # Not in inference graph
                label = "{" + ", ".join([f"{v}=0" for v in values]) + "}"
                color = "black"
            else:
                node = active_nodes[var]
                label = str(node.variable) + ":{" + ", ".join([f"{v}={w}" for v, w in node.values]) + "}"
                color = "green" if node.in_query else ("#%0.2X" % int(max([v for _, v in node.values]) * 255)) + "0000"
            net.add_node(var, label=label, color=color)

        for edge in self.edges:
            ep = list(edge.endpoints)
            label = "{" + ", ".join({f"{r}({c})" for r, c in edge.relations}) + "}"
            color = "green" if edge.in_query else "red"
            net.add_edge(ep[0], ep[1], label=label, color=color)

        net.show(f"{file_name}.html")
