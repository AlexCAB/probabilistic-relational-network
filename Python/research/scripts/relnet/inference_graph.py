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
created: 2021-08-09
"""

from typing import Dict, Any, Set, Optional

from scripts.relnet.activation_graph import ActivationGraph, ActiveNode, ActiveEdge
from scripts.relnet.sample_graph import \
    SampleGraph, SampleGraphComponentsProvider, SampleSpace

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scripts.relnet.relation_graph import RelationGraphBuilder


class InferenceGraph(SampleSpace):
    """
    Immutable wrapper of list of selected outcomes
    """

    def __init__(
            self,
            components_provider: SampleGraphComponentsProvider,
            query: SampleGraph,
            name: str,
            outcomes: Dict[SampleGraph, int]
    ):
        super().__init__(components_provider, outcomes)
        self.query: SampleGraph = query
        self.name: str = name
        self._outcomes: Dict[SampleGraph, int] = outcomes
        self._components_provider: SampleGraphComponentsProvider = components_provider

    def __repr__(self):
        return self.name

    def builder(self) -> 'RelationGraphBuilder':
        """
        Construct new relation graph builder which contains all outcomes from this inference graph
        :return: new builder instance
        """
        from scripts.relnet.relation_graph import RelationGraphBuilder
        return RelationGraphBuilder(
            None,
            None,
            None,
            {outcome: count for outcome, count in self._outcomes.items()},
            self._components_provider)

    def visualize_outcomes(self, name: Optional[str] = None, height: str = "1024px", width: str = "1024px") -> None:
        """
        Will render all outcomes as HTML page and show in browser
        :param name: optional name of this visualization, if None then self.name will passed
        :param height: window height
        :param width: window width
        :return: None
        """
        self._visualize_outcomes(name if name else self.name, height, width, self.query)

    def describe(self) -> Dict[str, Any]:
        """
        Return set of properties of this inference graph
        :return: Dict[property_name, property_value]
        """
        return {
            "query": self.query.text_view(),
            "number_outcomes": self.number_of_outcomes,
            "included_variables": {str(v) for v, _ in self.included_variables()},
            "included_relations": {str(r) for r in self.included_relations()},
        }

    def activation_graph(self, relation_filter: Set[Any] = None, name: Optional[str] = None) -> ActivationGraph:
        """
        On given inference graph builds activation graph.
        As norm constant we using number_of_outcomes, since assume for values that in query graph the similarity = 1,
        for the rest of values the similarity < 1
        :param relation_filter: list of relation for which activation will be calculated,
                                if None then for all relations.
        :param name: optional name for activation graph, if None then self.name will passed
        :return ActivationGraph: activation graph:
        """
        grouped_values: Dict[Any, (Dict[Any, float], bool)] = {
            var: ({val: 0.0 for val in values}, var in self.query.included_variables)
            for var, values in self._components_provider.variables()}

        grouped_relations: Dict[frozenset[Any], (Dict[Any, int], bool)] = {}

        for outcome, count in self._outcomes.items():
            similarity = outcome.similarity(self.query)
            external_nodes = outcome.external_nodes(set(self.query.nodes), relation_filter)
            out_query_nodes = {node: (similarity * count, False) for node in external_nodes.keys()}
            in_query_nodes = {node: (1.0 * count, True) for node in self.query.nodes.intersection(outcome.nodes)}
            out_query_edges = {(edge, False) for rel_edges in external_nodes.values() for edge in rel_edges}
            in_query_edges = {(edge, True) for edge in self.query.edges}

            assert out_query_nodes.keys().isdisjoint(in_query_nodes.keys()), \
                f"[InferenceGraph.active_values] out_query_nodes and in_query_nodes should not intersect, seems a bug"
            assert out_query_edges.isdisjoint(in_query_edges), \
                f"[InferenceGraph.active_values] out_query_edges and in_query_edges should not intersect, seems a bug"

            for node, (weight, node_in_query) in (out_query_nodes | in_query_nodes).items():
                values, in_query = grouped_values[node.variable]
                assert node_in_query == in_query, \
                    "[InferenceGraph.active_values] All value of same variable should belong to " \
                    "query or not, this is a bug"
                values[node.value] += weight

            for edge, edge_in_query in out_query_edges | in_query_edges:
                endpoints = frozenset({e.variable for e in edge.endpoints})
                if endpoints in grouped_relations:
                    relations, in_query = grouped_relations[endpoints]
                    assert edge_in_query == in_query, \
                        "[InferenceGraph.active_values] All edges with same endpoints should belong to " \
                        "query or not, this is a bug"
                    relations[edge.relation] = relations.get(edge.relation, 0) + count
                else:
                    grouped_relations[endpoints] = ({edge.relation: count}, edge_in_query)

        return ActivationGraph(
            self._components_provider,
            self.number_of_outcomes,
            {ActiveNode(var, {v: w / self.number_of_outcomes for v, w in values.items()}, in_query)
             for var, (values, in_query) in grouped_values.items()},
            {ActiveEdge(set(endpoints), relations, in_query)
             for endpoints, (relations, in_query) in grouped_relations.items()},
            name if name else self.name)
