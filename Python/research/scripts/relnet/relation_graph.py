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

import copy
from collections import Hashable
from typing import List, Dict, Set, Any, Tuple, Optional, Callable

from pyvis.network import Network
from .sample_graph import SampleGraph, ValueNode, RelationEdge, SampleGraphBuilder, SampleGraphComponentsProvider


class BuilderComponentsProvider(SampleGraphComponentsProvider):
    """
    Implementation of sample graph components provider
    """

    def __init__(self, variables: Dict[Any, Set[Any]], relations: Set[Any]):

        assert variables, \
            f"[BuilderComponentsProvider.__init__] Set of variables should not be empty."
        for var, values in variables.items():
            assert isinstance(var, Hashable), \
                f"[BuilderComponentsProvider.__init__] Variable '{var}' should be hashable"
            assert values, \
                f"[BuilderComponentsProvider.__init__] Set of variable values should not be empty, found for {var}"
            for val in values:
                assert isinstance(val, Hashable), \
                    f"[BuilderComponentsProvider.__init__] Value '{val}' of variable '{var}' should be hashable"
        assert relations, \
            f"[BuilderComponentsProvider.__init__] Set of relations should not be empty."
        for rel in relations:
            assert isinstance(rel, Hashable), \
                f"[BuilderComponentsProvider.__init__] Relation '{rel}' should be hashable"

        self.variables: Dict[Any, Set[Any]] = variables
        self.relations: Set[Any] = relations
        self.nodes: Dict[Tuple[Any, Any], ValueNode] = {}
        self.edges: Dict[Tuple[frozenset[ValueNode], Any], RelationEdge] = {}

    def get_node(self, variable: Any, value: Any) -> ValueNode:
        assert variable in self.variables, \
            f"[BuilderComponentsProvider.get_node] Unknown variable {variable}"
        assert value in self.variables[variable], \
            f"[BuilderComponentsProvider.get_node] Unknown value {value} of variable {variable}"

        if (variable, value) in self.nodes:
            return self.nodes[(variable, value)]
        else:
            node = ValueNode(variable, value)
            self.nodes[(variable, value)] = node
            return node

    def get_edge(self, endpoints: frozenset[ValueNode], relation: Any) -> RelationEdge:
        assert endpoints.issubset(self.nodes.values()), \
            f"[BuilderComponentsProvider.get_edge] Endpoints nodes should be created first, " \
            f"got {endpoints} where nodes {self.nodes}"
        assert relation in self.relations, \
            f"[BuilderComponentsProvider.get_node] Unknown relation {relation}"

        if (endpoints, relation) in self.edges:
            return self.edges[(endpoints, relation)]
        else:
            edge = RelationEdge(endpoints, relation)
            self.edges[(endpoints, relation)] = edge
            return edge


class RelationGraphBuilder:
    """
    Mutable builder for composing of the relation graphs
    """

    def __init__(
            self,
            variables: Dict[Any, Set[Any]],
            relations: Set[Any],
            name: Optional[str] = None,
            outcomes: Dict[SampleGraph, int] = None,
            components_provider: Optional[SampleGraphComponentsProvider] = None,
    ):
        self._variables: Dict[Any, Set[Any]] = variables
        self._relations: Set[Any] = relations
        self._name: Optional[str] = name
        self._outcomes: Dict[SampleGraph, int] = outcomes if outcomes else {}
        self._id_counter = 0
        self._components_provider = components_provider if components_provider \
            else BuilderComponentsProvider(variables, relations)

    def next_id(self) -> int:
        """
        Generate unique int ID for whatever reason
        :return: unique int ID
        """
        self._id_counter += 1
        return self._id_counter

    def add_outcome(self, outcome: SampleGraph, count: int = 1) -> 'RelationGraphBuilder':
        """
        Will add to relation graph
        :param outcome: outcome to be added, should be created with same SampleGraphComponentsProvider
        :param count: outcome count, should be >= 1
        :return: self
        """
        assert outcome.is_compatible(self._components_provider), \
            f"[RelationGraphBuilder.add_outcome] Outcome {outcome} is not compatible with this relation graph, " \
            f"since it vas created with using another SampleGraphComponentsProvider"
        assert count >= 1, \
            f"[RelationGraphBuilder.add_outcome] Expect count be >= 1, but got {count}"

        if outcome in self._outcomes:
            self._outcomes[outcome] += count
        else:
            self._outcomes[outcome] = count
        return self

    def add_outcomes(self, outcomes: List[SampleGraph], count: int = 1) -> 'RelationGraphBuilder':
        """
        To add multiple outcomes with same count
        :param outcomes: list of outcomes
        :param count: count for each outcome, should be >= 1
        :return: self
        """
        for outcome in outcomes:
            self.add_outcome(outcome, count)
        return self

    def sample_builder(self) -> SampleGraphBuilder:
        """
        Create new SampleGraphBuilder
        :return: new SampleGraphBuilder
        """
        return SampleGraphBuilder(self._components_provider)

    def build_sample(self, build: Callable[[SampleGraphBuilder], SampleGraph]) -> 'RelationGraphBuilder':
        """
        Will call provided build function with injection of new SampleGraphBuilder
        :param build: build function SampleGraphBuilder -> SampleGraph
        :return: self
        """
        return self.add_outcome(build(SampleGraphBuilder(self._components_provider)))

    def generate_all_possible_outcomes(self) -> 'RelationGraphBuilder':
        """
        Will generate all possible outcomes on relation graph set of variables and they values
        :return: self, with generated outcomes
        """
        assert not self._outcomes, \
            f"[RelationGraphBuilder.generate_all_possible_outcomes] Builder should not have outcomes added, " \
            f"found {len(self._outcomes)}"

        indexed_variables = [(var, list(values)) for var, values in self._variables]
        indexed_relations = list(self._relations)

        all_nodes: List[(Any, Any)] = [(var, values[0]) for var, values in indexed_variables]
        all_endpoints: List[Set[(Any, Any)]] = [{n_1, n_2} for n_2 in all_nodes for n_1 in all_nodes]

        index_acc: List[int] = [-1 for _ in range(0,  len(all_endpoints))]
        edges_indices: List[List[int]] = []

        while set([i < (len(indexed_relations) - 1) for i in index_acc]) != {False} and len(all_endpoints) != 0:
            i = 0
            while index_acc[i] >= (len(indexed_relations) - 1) and i < len(all_endpoints):
                index_acc[i] = -1
                i += 1
            index_acc[i] += 1
            edges_indices.append(index_acc.copy())

        for var, val in all_nodes:  # To add all single node samples
            self.build_sample(lambda b: b.set_name(f"O_{self.next_id()}").build_single_node(var, val))

        for edges_index in edges_indices:
            active_edges: frozenset[(frozenset[(Any, Any)], Any)] = frozenset({
                (frozenset(all_endpoints[j]), indexed_relations[edges_index[j]])
                for j in range(0, len(edges_index))
                if edges_index[j] >= 0})
            builder = self.sample_builder()
            if builder.is_edges_connected(active_edges):
                self.add_outcome(
                    builder.set_name(f"O_{self.next_id()}").build_from_edges(
                        active_edges, validate_connectivity=False))

        for var, values in indexed_variables:
            self.add_outcomes([
                outcome.transform_with_replaced_values({var: val}, f"O_{self.next_id()}")
                for val in values[1:]   # Iterate over all value except first
                for outcome in self._outcomes])

        for outcome, count in self._outcomes:
            assert count == 1, \
                f"[RelationGraphBuilder.generate_all_possible_outcomes] Outcome {outcome} added {count} times"
        return self

    def build(self) -> 'RelationGraph':
        """
        Build relation graph from added outcomes
        :return: built relation graph
        """
        assert self._outcomes, \
            f"[RelationGraphBuilder.build] relation graph should have at least 1 outcome"

        return RelationGraph(
            self._name,
            frozenset({(k, frozenset(v)) for k, v in self._variables.items()}),
            frozenset(self._relations),
            self._outcomes)


class RelationGraph:

    def __init__(
            self,
            name: Optional[str],
            variables: frozenset[Tuple[Any, frozenset[Any]]],
            relations: frozenset[Any],
            outcomes: Dict[SampleGraph, int]
    ):
        self.variables: frozenset[Tuple[Any, frozenset[Any]]] = variables
        self.relations: frozenset[Any] = relations
        self.name: str = name if name else f"relation_graph_with_{len(outcomes)}_outcomes"
        self.number_of_outcomes: int = sum([c for _, c in outcomes.items()])
        self._outcomes: Dict[SampleGraph, int] = outcomes

    def __repr__(self):
        return self.name

    def __copy__(self):
        return RelationGraph(self.name, self.variables, self.relations, copy.deepcopy(self._outcomes))

    def show_relation_graph(self,  height="1024px", width="1024px") -> None:
        net = Network(height=height, width=width)

        for var, _ in self.variables:
            net.add_node(var, label=var)

        sample_edges: Dict[frozenset[Any], Set[Any]] = {}
        for sample in self._outcomes.keys():
            for edge in sample.edges:
                endpoints = frozenset({ep.variable for ep in edge.endpoints})
                if endpoints in sample_edges:
                    sample_edges[endpoints].add(str(edge.relation))
                else:
                    sample_edges[endpoints] = set(str(edge.relation))

        for endpoints, relations in sample_edges.items():
            ep = list(endpoints)
            net.add_edge(ep[0], ep[1], label=' | '.join(relations))

        net.set_options('''
          {
            "physics": {
              "forceAtlas2Based": {
                "gravitationalConstant": -200,
                "centralGravity": 0.03,
                "springLength": 200,
                "springConstant": 0.09
              },
              "solver": "forceAtlas2Based"
            }
          }
        ''')

        net.show(f"{self.name}_relation_graph.html")

    def show_all_outcomes(self, height="1024px", width="1024px") -> None:
        net = Network(height=height, width=width)

        for outcome, count in self._outcomes.items():
            for node in outcome.nodes:
                net.add_node(node.string_id, label=f"{node.string_id}@{outcome.name}({count})")
            for edge in outcome.edges:
                ep = list(edge.endpoints)
                net.add_edge(ep[0].string_id, ep[1].string_id, label=str(edge.relation))

        net.show(f"{self.name}_all_outcomes.html")

    def describe(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "number_of_variables": len(self.variables),
            "number_of_relations": len(self.relations),
            "number_of_outcomes": self.number_of_outcomes,
            "variables": [str(v) for v, _ in self.variables],
            "relations": [str(r) for r in self.relations],
        }

    def disjoint_distribution(self) -> Dict[Tuple[str, str], float]:
        """
        Calculate probability of appear for each value of each variable, as if they are independent events.
        :return: Dict[(variable, value), probability_of_appear]
        """
        acc: Dict[ValueNode, int] = {}

        for outcome, count in self._outcomes.items():
            for node in outcome.nodes:
                if node in acc:
                    acc[node] += count
                else:
                    acc[node] = count

        total = sum(acc.values())

        return {(k.variable, k.value): v / total for k, v in acc.items()}

    # TODO:
    # def inference(self, query: SampleGraph) -> InferenceGraph:
    #     query_errors = query.validate()
    #
    #     assert not query_errors, f"[RelationGraph.inference] query {query} is invalid, query_errors: {query_errors}"
    #
    #     query_hash = query.get_hash()
    #     selected_outcomes = [o for o in self._outcomes if query_hash.issubset(o.get_hash())]
    #     cloned_variables = {}
    #
    #     for o in selected_outcomes:
    #         for v in o.get_all_values():
    #             if v.variable_id not in cloned_variables:
    #                 cloned_variables[v.variable_id] = self._variables[v.variable_id].clean_copy()
    #
    #     cloned_outcomes = [
    #         o.clone(o.sample_id, relations=list(self._relations.values()), variables=list(cloned_variables.values()))
    #         for o in selected_outcomes]
    #
    #     for outcome in cloned_outcomes:
    #         for value in outcome.get_all_values():
    #             cloned_variables[value.variable_id].add_value(outcome.sample_id, value)
    #
    #     self._log.debug(
    #         f"[RelationGraph.inference] len(cloned_outcomes) = {len(cloned_outcomes)}, "
    #         f"len(cloned_variables) = {len(cloned_variables)}")
    #
    #     return InferenceGraph(query, list(cloned_variables.values()), cloned_outcomes)
