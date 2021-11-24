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
created: 2021-11-09
"""
from math import prod
from typing import Dict, Set, Any, Optional, Tuple, Union, List
from pyvis.network import Network

from .folded_graph import FoldedGraph, FoldedNode, FoldedEdge
from .graph_components import SampleGraphComponentsProvider, ValueNode, RelationEdge
from .sample_graph import SampleGraph
from .sample_set import SampleSet, SampleSetBuilder


class SampleSpace:
    """
    Base class for the graphs which is a set of samples (relation graph and inference graph), contains a collection
    of the samples and common methods to work with them.
    """

    def __init__(
            self,
            components_provider: SampleGraphComponentsProvider,
            outcomes: SampleSet,
            name: Optional[str] = None,
            evidence: Optional[SampleGraph] = None
    ):
        self._components_provider: SampleGraphComponentsProvider = components_provider
        self._name: Optional[str] = name
        self._evidence: Optional[SampleGraph] = evidence
        self.outcomes: SampleSet = outcomes

    def __copy__(self):
        raise AssertionError(
            "[SampleSpace.__copy__] Sample graph should not be copied, "
            "use one of transformation method or builder to get new instance")

    def outcomes_as_edges_sets(
            self
    ) -> frozenset[Tuple[Union[frozenset[Tuple[frozenset[Tuple[Any, Any]], Any]], Tuple[Any, Any]]], int]:
        """
        Return outcomes as set of edges_sets
        :return: frozenset[frozenset[(frozenset[(variable, value)], value)] or (variable, value), count]:
        """
        return frozenset({(o.edges_set_view(), c) for o, c in self.outcomes.items()})

    def disjoint_distribution(self) -> Dict[Tuple[str, str], float]:
        """
        Calculate probability of appear for each value of each variable base on set of outcomes,
        as if they are independent events.
        :return: Dict[(variable, value), probability_of_appear]
        """
        acc: Dict[ValueNode, int] = {}

        for outcome, count in self.outcomes.items():
            for node in outcome.nodes:
                if node in acc:
                    acc[node] += count
                else:
                    acc[node] = count

        total = sum(acc.values())

        return {(k.variable, k.value): v / total for k, v in acc.items()}

    def included_variables(self) -> frozenset[Tuple[Any, frozenset[Any]]]:
        """
        Calculate variables and values that appear in outcomes set
        :return: frozenset[(variable, frozenset[value])]:
        """
        variables: Dict[Any, Set[Any]] = {}

        for outcome in self.outcomes.samples():
            for node in outcome.nodes:
                variables[node.variable] = variables.get(node.variable, set({})).union({node.value})

        return frozenset({(var, frozenset(values)) for var, values in variables.items()})

    def included_relations(self) -> frozenset[Any]:
        """
        Calculate relations that appear in outcomes set
        :return: frozenset[relation]
        """
        return frozenset({e.relation for o in self.outcomes.samples() for e in o.edges})

    def folded_graph(self, name: Optional[str] = None) -> FoldedGraph:
        """
        Build folded variables graph representation from this set of outcomes
        :return: variables graph
        """
        node_acc: Dict[Any, Dict[ValueNode, int]] = {}
        edge_acc: Dict[frozenset[Any], Dict[RelationEdge, int]] = {}
        variables: Dict[Any, Set[Any]] = {var: set(values) for var, values in self._components_provider.variables()}
        n_of_outcomes: int = self.outcomes.length

        for outcome, count in self.outcomes.items():
            for node in outcome.nodes:
                if node.variable in node_acc:
                    node_acc[node.variable][node] = node_acc[node.variable].get(node, 0) + count
                else:
                    node_acc[node.variable] = {node: count}
            for edge in outcome.edges:
                endpoints = frozenset({ep.variable for ep in edge.endpoints})
                if endpoints in edge_acc:
                    edge_acc[endpoints][edge] = edge_acc[endpoints].get(edge, 0) + count
                else:
                    edge_acc[endpoints] = {edge: count}

        return FoldedGraph(
            self._components_provider,
            self.outcomes.length,
            {FoldedNode(variable, variables[variable], nodes, n_of_outcomes) for variable, nodes in node_acc.items()},
            {FoldedEdge(set(endpoints), edges) for endpoints, edges in edge_acc.items()},
            name if name else f"VariablesGraph(len(nodes) = {len(node_acc)}, len(edges) = {len(edge_acc)})")

    def visualize_outcomes(self, name: Optional[str] = None, height: str = "1024px", width: str = "1024px"):
        """
        Will render all outcomes as HTML page and show in browser
        :param height: window height
        :param width: window width
        :param name: optional name of this visualization, if None then self.name will passed
        :return: None
        """
        file_name = "".join(c for c in (name if name else self._name) if c.isalnum() or c == '_')
        net = Network(height=height, width=width)

        for i, (outcome, count) in enumerate(self.outcomes.items()):
            node_list = list(outcome.nodes)
            head_node = node_list[0]
            net.add_node(head_node.string_id + str(i), label=f"{head_node.string_id}@{outcome.name}({count})")

            for node in node_list[1:]:
                net.add_node(node.string_id + str(i), label=node.string_id)

            for edge in outcome.edges:
                ep = list(edge.endpoints)
                net.add_edge(ep[0].string_id + str(i), ep[1].string_id + str(i), label=str(edge.relation))

        if self._evidence:
            for node in self._evidence.nodes:
                net.add_node(node.string_id + "_query", label=node.string_id, color="red")

            for edge in self._evidence.edges:
                ep = list(edge.endpoints)
                net.add_edge(
                    ep[0].string_id + "_query", ep[1].string_id + "_query", label=str(edge.relation), color="red")

        net.show(f"{file_name}.html")

    def join_outcomes_on_variable_set(self, variables:  Optional[Set[Any]] = None) -> SampleSet:
        """
        Will join over all outcomes
        :param variables: set of variables to join on, if None will join on all variables
        :return: SampleSet of joined outcomes
        """
        join_variables = variables if (variables is not None) else {v for v, _ in self.included_variables()}
        outcomes_acc: SampleSetBuilder = self.outcomes.builder()

        def cross_join(var: Any, groups: List[SampleSet], joints: SampleSetBuilder) -> SampleSet:
            ssb = SampleSetBuilder(self._components_provider)
            if not groups:  # To join if groups empty
                joints_set = joints.build()
                if joints_set.is_all_have_same_value_of_variable(var):
                    joined_sample, counts = joints.build().make_joined_sample()
                    ssb.add(joined_sample, prod(counts))
            else:
                for s, c in groups[0].items():
                    ssb.add_all(cross_join(var, groups[1:], joints.copy().add(s, c)))
            return ssb.build()

        for join_var in join_variables:
            join_outcomes = outcomes_acc.build().filter_samples(lambda o: join_var in o.included_variables)
            groped_outcomes = join_outcomes.group_intersecting()

            print(f"join_var = {join_var}")
            print(f"join_outcomes = {join_outcomes}")
            print(f"groped_outcomes = {groped_outcomes}")

            joined_outcomes = cross_join(
                join_var, list(groped_outcomes.values()), SampleSetBuilder(self._components_provider))

            print(f"joined_outcomes = {joined_outcomes}")

            outcomes_acc.remove_all(join_outcomes)
            outcomes_acc.add_all(joined_outcomes)

            print(f"join_var = {join_var}")
            print(f"outcomes_acc.build() = {outcomes_acc.build()}")

        return outcomes_acc.build()
