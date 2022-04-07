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

import os
from math import isclose
from typing import Dict, Set, Any, Optional, Tuple, Union
from pyvis.network import Network

from .folded_graph import FoldedGraph, FoldedNode, FoldedEdge
from .graph_components import SampleGraphComponentsProvider, ValueNode, RelationEdge
from .sample_graph import SampleGraph, SampleGraphBuilder
from .sample_set import SampleSet, SampleSetBuilder

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .relation_graph import RelationGraphBuilder, RelationGraph


class SampleSpace:
    """
    Base class for the graphs which is a set of samples (relation graph and inference graph), contains a collection
    of the samples and common methods to work with them.
    """

    def __init__(
            self,
            components_provider: SampleGraphComponentsProvider,
            outcomes: SampleSet,
            name: Optional[str],
            evidence: Optional[SampleGraph]
    ):
        self._components_provider: SampleGraphComponentsProvider = components_provider
        self._name: Optional[str] = name
        self._evidence: Optional[SampleGraph] = evidence
        self.outcomes: SampleSet = outcomes

    def __repr__(self):
        return self._name

    def __copy__(self):
        raise AssertionError(
            "[SampleSpace.__copy__] Sample graph should not be copied, "
            "use one of transformation method or builder to get new instance")

    def builder(self) -> 'RelationGraphBuilder':
        """
        Construct new relation graph builder which contains all outcomes from this inference graph
        :return: new builder instance
        """
        from scripts.relnet.relation_graph import RelationGraphBuilder
        return RelationGraphBuilder(
            None,
            None,
            self._name,
            self.outcomes.builder(),
            self._components_provider)

    def relation_graph(self, name: Optional[str] = None) -> 'RelationGraph':
        """
        Convert inference graph to relation graph with same set of outcomes
        :return: new RelationGraph
        """
        from .relation_graph import RelationGraph
        return RelationGraph(
            self._components_provider,
            name if name else self._name,
            self.outcomes)

    def sample_builder(self) -> SampleGraphBuilder:
        """
        Create new SampleGraphBuilder
        :return: new SampleGraphBuilder
        """
        return SampleGraphBuilder(self._components_provider)

    def outcomes_as_edges_sets(
            self
    ) -> frozenset[Tuple[Union[frozenset[Tuple[frozenset[Tuple[Any, Any]], Any]], Tuple[Any, Any]]], int]:
        """
        Return outcomes as set of edges_sets
        :return: frozenset[frozenset[(frozenset[(variable, value)], value)] or (variable, value), count]:
        """
        return frozenset({(o.edges_set_view(), c) for o, c in self.outcomes.items()})

    def marginal_variables_probability(
            self, variables: Optional[Set[Any]] = None, unobserved: bool = False
    ) -> Dict[str, Dict[str, float]]:
        """
        Count marginal distribution for given set of variables (including unobserved values)
        :param variables: List of variable to marginalize, if no then all will marginalized
        :param unobserved: if True unobserved values will added
        :return: Dict[variable, Dict[value, probability]]
        """
        variables_to_check = variables if variables else {v for v, _ in self._components_provider.variables()}
        group_acc:  Dict[str, Dict[str, int]] = {}
        norm_acc: Dict[str, Dict[str, float]] = {}

        for outcome, count in self.outcomes.items():
            for in_var in outcome.included_variables:
                if in_var in variables_to_check:
                    in_val = outcome.value_for_variable(in_var)
                    if in_var in group_acc:
                        group_acc[in_var][in_val] = group_acc[in_var].get(in_val, 0) + count
                    else:
                        group_acc[in_var] = {in_val: count}

        for in_val, values in group_acc.items():
            c_sum = sum(values.values())
            assert \
                0 <= c_sum <= self.outcomes.length, \
                f"[SampleSpace.marginal_variables_probability] Expect sum of probability of variable '{in_val}' " \
                f"value to be within [0, {self.outcomes.length}] but got {c_sum}"
            if unobserved:
                values['u'] = self.outcomes.length - c_sum
                norm_acc[in_val] = {v: p / self.outcomes.length for v, p in values.items()}
            else:
                norm_acc[in_val] = {v: p / c_sum for v, p in values.items()}

        for in_val, values in norm_acc.items():
            p_sum = sum(values.values())
            assert \
                isclose(p_sum, 1.0, rel_tol=1e-9, abs_tol=0.0), \
                f"[SampleSpace.marginal_variables_probability] Expect sum of probability of variable '{in_val}' " \
                f"to be close to 1 but got {p_sum}"

        return norm_acc

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

    def print_samples(self) -> str:
        """
        Print all samples as string
        :return: string
        """
        return os.linesep.join(sorted([f"{s}({c})" for s, c in self.outcomes.items()]))

    def find_for_values(self, values: Set[Tuple[Any, Any]]) -> SampleSet:
        """
        Will scan over all samples and return that one which contains all given values
        :param values: Set[(variable, value)]
        :return: SampleSet of found values
        """
        ssb = SampleSetBuilder(self._components_provider)

        for s, c in self.outcomes.items():
            if values.issubset(s.values()):
                ssb.add(s, c)

        return ssb.build()

    def factorized(self) -> frozenset[SampleSet]:
        """
        Will split outcomes of this sample set by factors, or raise error if this sample set is not factorized
        :return: set of SampleSet
        """
        acc: Dict[frozenset[frozenset[Any]], SampleSetBuilder] = {}

        for o, c in self.outcomes.items():
            assert not o.is_k_0, \
                f"[SampleSpace.factorized] Sample spase which contains empty outcome can't be factorized"
            evs = o.edges_endpoint_variables()
            if evs not in acc:
                for aep in acc.keys():
                    assert aep.isdisjoint(evs), \
                        f"[SampleSpace.factorized] Sample spase which contains overlapping outcome can't be factorized"
                acc[evs] = SampleSetBuilder(self._components_provider, {o: c})
            else:
                acc[evs].add(o, c)

        return frozenset({b.build() for b in acc.values()})
