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

from typing import Any, Dict, Set, Optional
from pyvis.network import Network
from scripts.relnet.variables_graph import VariableNode, VariableEdge, VariablesGraph

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scripts.relnet.sample_graph import ValueNode, RelationEdge, SampleGraphComponentsProvider


class FoldedNode(VariableNode):
    """
    Immutable node which contain all variable values
    """

    def __init__(self, variable: Any, values: Set[Any], value_nodes: Dict['ValueNode', int], number_of_outcomes: int):
        super().__init__(variable)
        self.values: frozenset[Any] = frozenset(values)
        self.value_nodes: frozenset[('ValueNode', int)] = frozenset(value_nodes.items())
        self._value_nodes_dict: Dict['ValueNode', int] = value_nodes
        self._number_of_outcomes: int = number_of_outcomes

    def __repr__(self):
        values = ",".join(sorted([f"{n.value}({c})" for n, c in self.value_nodes]))
        return f"({self.variable}:{{{values}}})"

    def __hash__(self):
        return (self.variable, self.value_nodes).__hash__()

    def __eq__(self, other: Any):
        if isinstance(other, FoldedNode):
            return self.variable == other.variable and self.value_nodes == other.value_nodes
        return False

    def unobserved_count(self) -> int:
        """
        Will count number of appears of unobserved value for this variable
        :return: number of unobserved
        """
        return self._number_of_outcomes - sum(self._value_nodes_dict.values())

    def marginal_distribution(self) -> Dict[Any, float]:
        """
        For each value of this variable count number of outcome where value enters,
        then count outcomes where no one of values of this variable enters (unobserved),
        then normalize all counts ant return.
        :return:  Dict[value, normalized_marginal_probability]
        """
        acc: Dict[Any, float] = {v: 0.0 for v in self.values}
        total: int = 0

        for value_node, count in self.value_nodes:
            assert value_node.value in acc, \
                f"[FoldedNode.marginal_distribution] Unknown value {value_node.value}, seems a bug."
            acc[value_node.value] += count
            total += count

        assert self._number_of_outcomes >= total, \
            f"[FoldedNode.marginal_distribution] Total count ({total}) " \
            f"can't be grater then number of outcomes ({self._number_of_outcomes}), seems a bug."

        acc['unobserved'] = self._number_of_outcomes - total

        return {val: count / self._number_of_outcomes for val, count in acc.items()}


class FoldedEdge(VariableEdge):
    """
    Immutable edge which contain all relation in between variables
    """

    def __init__(self, endpoints: Set[Any], relation_edges: Dict['RelationEdge', int]):
        super().__init__(endpoints)
        self.relation_edges: frozenset[('ValueNode', int)] = frozenset(relation_edges.items())
        self._relation_edges_dict: Dict['RelationEdge', int] = relation_edges

    def __repr__(self):
        ep = sorted(self.endpoints)
        relations = ",".join(sorted([f"{e.relation}({c})" for e, c in self.relation_edges]))
        return f"({ep[0]})--{{{relations}}}--({ep[1]})"

    def __hash__(self):
        return (self.endpoints, self.relation_edges).__hash__()

    def __eq__(self, other: Any):
        if isinstance(other, FoldedEdge):
            return self.endpoints == other.endpoints and self.relation_edges == other.relation_edges
        return False


class FoldedGraph(VariablesGraph):
    """
    Immutable graph which represent folded structure of set of outcomes
    """

    def __init__(
            self,
            components_provider: 'SampleGraphComponentsProvider',
            number_of_outcomes: int,
            nodes: Set[FoldedNode],
            edges: Set[FoldedEdge],
            name: str
    ):
        super().__init__(components_provider, number_of_outcomes, nodes, edges, name)
        self.nodes: frozenset[FoldedNode] = frozenset(nodes)
        self.edges: frozenset[FoldedEdge] = frozenset(edges)
        self._nodes_dict: Dict[Any, FoldedNode] = {n.variable: n for n in nodes}

    def folded_node(self, variable: Any) -> Optional[FoldedNode]:
        """
        Find folded node
        :param variable: variable to search on
        :return: FoldedNode or None if not in folded graph
        """
        return self._nodes_dict.get(variable)

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

        for node in self.nodes:
            values = ",".join({f"{n.value}({c})" for n, c in node.value_nodes})
            net.add_node(
                node.variable,
                label=f"{node.variable}:{{{values}, u({node.unobserved_count()})}}")

        for edge in self.edges:
            ep = list(edge.endpoints)
            relations = ",".join({f"{e.relation}({c})" for e, c in edge.relation_edges})
            net.add_edge(ep[0], ep[1], label=f"{{{relations}}}")

        for var, values in self._components_provider.variables():
            if var not in self.variables:
                values = ",".join([f"{v}(0)" for v in values])
                net.add_node(
                    var,
                    label=f"{var}:{{{values}, u({self.number_of_outcomes})}}",
                    color="gray")

        net.show(f"{file_name}.html")
