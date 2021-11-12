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

from typing import Dict, Set, Any, Optional, Tuple, Union
from pyvis.network import Network

from .folded_graph import FoldedGraph, FoldedNode, FoldedEdge
from .graph_components import SampleGraphComponentsProvider, ValueNode, RelationEdge
from .sample_graph import SampleGraph


class Samples:
    """
    Base class of collection of samples with count
    """

    def __init__(
            self,
            samples: Dict[SampleGraph, int]
    ):
        self._samples: Dict[SampleGraph, int] = samples

    def __bool__(self) -> bool:
        return bool(self._samples)

    def items(self) -> Set[Tuple[SampleGraph, int]]:
        return {(o, c) for o, c in self._samples.items()}

    def samples(self) -> Set[SampleGraph]:
        return set(self._samples.keys())


class SampleSet(Samples):
    """
    Represent immutable collection of samples with count
    """

    def __init__(
            self,
            samples: Dict[SampleGraph, int]
    ):
        super(SampleSet, self).__init__(samples)
        self._samples: Dict[SampleGraph, int] = samples
        self.length: int = sum(samples.values())

    def __len__(self) -> int:
        return self.length

    def __eq__(self, other: Any):
        if isinstance(other, SampleSet):
            return self._samples == other._samples
        return False

    def __repr__(self):
        return f"SampleSet(length = {self.length})"

    def builder(self) -> 'SampleSetBuilder':
        return SampleSetBuilder({o: c for o, c in self._samples.items()})

    def union(self, other: 'SampleSet'):
        builder = self.builder()
        for s, c in other.items():
            builder.add(s, c)
        return builder.build()


class SampleSetBuilder(Samples):
    """
    Mutable builder of collection of samples with count
    """

    def __init__(
            self,
            samples: Optional[Dict[SampleGraph, int]] = None
    ):
        super(SampleSetBuilder, self).__init__(samples if samples else {})

    def __repr__(self):
        return f"SampleSetBuilder(length = {self.length()})"

    def add(self, sample: SampleGraph, count: int) -> None:
        if sample in self._samples:
            self._samples[sample] += count
        else:
            self._samples[sample] = count

    def length(self) -> int:
        return sum(self._samples.values())

    def build(self) -> 'SampleSet':
        return SampleSet(self._samples)


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
            for node in  self._evidence.nodes:
                net.add_node(node.string_id + "_query", label=node.string_id, color="red")

            for edge in  self._evidence.edges:
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
        pass

        # outcomes_acc: Dict[frozenset[Any], List[(SampleGraphBuilder, List[int])]] = {}
        # rel_graph_builder = RelationGraphBuilder(name=name, components_provider=self._components_provider)
        #
        # for outcome, count in self.outcomes.items():
        #     if variables.issubset(outcome.included_variables):  # If have all variables included
        #         outcome_hash = outcome.variables_subgraph_hash(variables)
        #         if outcome_hash in outcomes_acc:
        #             i = 0
        #             while 0 <= i < len(outcomes_acc[outcome_hash]):
        #                 sample_builder, count_acc = outcomes_acc[outcome_hash][i]
        #                 if sample_builder.can_sample_be_joined(outcome):  # Add to one of exist groups
        #                     sample_builder.join_sample(outcome)
        #                     count_acc.append(count)
        #                     i = -1
        #                 else:
        #                     i += 1
        #             if i >= 0:  # Add to new group
        #                 outcomes_acc[outcome_hash].append((outcome.builder().set_name(None), [count]))
        #         else:
        #             outcomes_acc[outcome_hash] = [(outcome.builder().set_name(None), [count])]
        #     else:
        #         rel_graph_builder.add_outcome(outcome, count)
        # for _, sample_builders in outcomes_acc.items():
        #     for sample_builder, counts in sample_builders:
        #         rel_graph_builder.add_outcome(sample_builder.build(), prod(counts))

