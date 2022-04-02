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

from .activation_graph import ActivationGraph, ActiveNode, ActiveEdge
from .graph_components import SampleGraphComponentsProvider
from .sample_graph import SampleGraph
from .sample_space import SampleSpace
from .sample_set import SampleSet

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .relation_graph import RelationGraphBuilder, RelationGraph


class ConditionalGraph(SampleSpace):
    """
    Immutable wrapper of list of selected outcomes
    """

    def __init__(
            self,
            components_provider: SampleGraphComponentsProvider,
            evidence: SampleGraph,
            name: str,
            outcomes: SampleSet
    ):
        super().__init__(components_provider, outcomes, name, evidence)
        self.evidence: SampleGraph = evidence
        self.name: str = name
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
            self.outcomes.builder(),
            self._components_provider)

    def describe(self) -> Dict[str, Any]:
        """
        Return set of properties of this inference graph
        :return: Dict[property_name, property_value]
        """
        return {
            "query": self.evidence.text_view(),
            "number_outcomes": self.outcomes.length,
            "included_variables": {str(v) for v, _ in self.included_variables()},
            "included_relations": {str(r) for r in self.included_relations()},
        }

    def joined_on_variables(
            self, variables: Optional[Set[Any]] = None,
            name: Optional[str] = None
    ) -> 'ConditionalGraph':
        """
        Will join over all outcomes and return new inference graph with joined outcomes
        :param variables: set of variables to join on, if None will join on all variables
        :param name: optional name for the joined graph
        :return: new inference graph with joined outcomes
        """
        return ConditionalGraph(
            self._components_provider,
            self.evidence,
            name if name else self.name,
            self.join_outcomes_on_variable_set(variables))

    def relation_graph(self, name: Optional[str] = None) -> 'RelationGraph':
        """
        Convert inference graph to relation graph with same set of outcomes
        :return: new RelationGraph
        """
        from .relation_graph import RelationGraph
        return RelationGraph(
            self._components_provider,
            name if name else self.name,
            self.outcomes)

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
            var: ({val: 0.0 for val in values}, var in self.evidence.included_variables)
            for var, values in self._components_provider.variables()}

        grouped_relations: Dict[frozenset[Any], (Dict[Any, int], bool)] = {}

        for outcome, count in self.outcomes.items():
            similarity = outcome.similarity(self.evidence)
            external_nodes = outcome.external_nodes(set(self.evidence.nodes), relation_filter)
            out_query_nodes = {node: (similarity * count, False) for node in external_nodes.keys()}
            in_query_nodes = {node: (1.0 * count, True) for node in self.evidence.nodes.intersection(outcome.nodes)}
            out_query_edges = {(edge, False) for rel_edges in external_nodes.values() for edge in rel_edges}
            in_query_edges = {(edge, True) for edge in self.evidence.edges}

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
            self.outcomes.length,
            {ActiveNode(var, {v: w / self.outcomes.length for v, w in values.items()}, in_query)
             for var, (values, in_query) in grouped_values.items()},
            {ActiveEdge(set(endpoints), relations, in_query)
             for endpoints, (relations, in_query) in grouped_relations.items()},
            name if name else self.name)
