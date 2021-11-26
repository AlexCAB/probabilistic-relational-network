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

from typing import List, Dict, Set, Any, Tuple, Optional, Callable

from .graph_components import SampleGraphComponentsProvider, BuilderComponentsProvider
from .inference_graph import InferenceGraph
from .sample_graph import SampleGraph, SampleGraphBuilder
from .sample_space import SampleSpace
from .sample_set import SampleSet, SampleSetBuilder


class RelationGraphBuilder:
    """
    Mutable builder for composing of the relation graphs
    """

    def __init__(
            self,
            variables:  Optional[Dict[Any, Set[Any]]] = None,
            relations:  Optional[Set[Any]] = None,
            name: Optional[str] = None,
            outcomes: SampleSetBuilder = None,
            components_provider: Optional[SampleGraphComponentsProvider] = None,
    ):
        assert (variables and relations) or components_provider, \
            "[RelationGraphBuilder.__init__] (variables and relations) or components_provider should be passed"

        self._components_provider = components_provider if components_provider \
            else BuilderComponentsProvider(variables, relations)
        self._name: Optional[str] = name
        self._outcomes: SampleSetBuilder = outcomes if outcomes else SampleSetBuilder(self._components_provider)
        self._id_counter = 0
        self.variables: frozenset[Tuple[Any, frozenset[Any]]] = self._components_provider.variables()
        self.relations: frozenset[Any] = self._components_provider.relations()

    def __repr__(self):
        return f"RelationGraphBuilder(name = {self._name}, len(outcomes) = {self._outcomes.length()})"

    def set_name(self, name: Optional[str]):
        """
        Update relation graphs name with given
        :param name: new name
        :return: self
        """
        self._name = name
        return self

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

        self._outcomes.add(outcome, count)
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
            f"found {self._outcomes.length()} outcomes"

        indexed_variables = [(var, list(values)) for var, values in self.variables]
        indexed_relations = list(self.relations)

        all_nodes: List[(Any, Any)] = [
            (var, values[0])
            for var, values in indexed_variables]

        all_endpoints: List[frozenset[(Any, Any)]] = list({
            frozenset({n_1, n_2})
            for n_2 in all_nodes for n_1 in all_nodes if n_1 != n_2})

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
                for outcome in self._outcomes.samples()
                for val in values[1:]  # Iterate over all value except first
                if var in outcome.included_variables])

        for outcome, count in self._outcomes.items():
            assert count == 1, \
                f"[RelationGraphBuilder.generate_all_possible_outcomes] Outcome {outcome.text_view()} " \
                f"added {count} times"
        return self

    def build(self) -> 'RelationGraph':
        """
        Build relation graph from added outcomes
        :return: built relation graph
        """
        assert self._outcomes, \
            f"[RelationGraphBuilder.build] relation graph should have at least 1 outcome"

        return RelationGraph(
            self._components_provider,
            self._name,
            self._outcomes.build())


class RelationGraph(SampleSpace):
    """
    Immutable relation graph instance
    """

    def __init__(
            self,
            components_provider: SampleGraphComponentsProvider,
            name: Optional[str],
            outcomes: SampleSet
    ):
        self.name: str = name if name else f"relation_graph_with_{outcomes.length}_outcomes"
        super().__init__(components_provider, outcomes, self.name)
        self.variables: frozenset[Tuple[Any, frozenset[Any]]] = components_provider.variables()
        self.relations: frozenset[Any] = components_provider.relations()

    def __repr__(self):
        return self.name

    def builder(self) -> RelationGraphBuilder:
        """
        Construct new relation graph builder which contains all outcomes from this relation graph
        :return: new builder instance
        """
        return RelationGraphBuilder(
            {var: set(values) for var, values in self.variables},
            set(self.relations),
            self.name,
            self.outcomes.builder(),
            self._components_provider)

    def describe(self) -> Dict[str, Any]:
        """
        Return set of properties of this relation graph
        :return: Dict[property_name, property_value]
        """
        return {
            "name": self.name,
            "number_of_variables": len(self.variables),
            "number_of_relations": len(self.relations),
            "number_of_outcomes": self.outcomes.length,
            "variables": {str(v) for v, _ in self.variables},
            "relations": {str(r) for r in self.relations},
        }

    def inference(self, evidence: SampleGraph, name: Optional[str] = None) -> InferenceGraph:
        """
        Do inference for given query. Will filter out outcomes which is sub-graphs of query graph
        and pack in InferenceGraph instance.
        :param evidence: and SampleGraph to filter on
        :param name: optional name for the inference graph
        :return: new instance of InferenceGraph
        """
        assert evidence.is_compatible(self._components_provider), \
            f"[RelationGraphBuilder.add_outcome] Evidence {evidence} is not compatible with this relation graph, " \
            f"since it vas created with using another SampleGraphComponentsProvider"

        selected_outcomes: Dict[SampleGraph, int] = {
            outcome: count for outcome, count in self.outcomes.items()
            if evidence.is_subgraph(outcome) or evidence.included_variables.isdisjoint(outcome.included_variables)}

        return InferenceGraph(
            self._components_provider,
            evidence,
            name if name else f"inference_of_{self.name}",
            SampleSet(self._components_provider, selected_outcomes))

    def joined_on_variables(self, variables: Optional[Set[Any]] = None, name: Optional[str] = None) -> 'RelationGraph':
        """
        Will join over all outcomes and return new relation graph with joined outcomes
        :param variables: set of variables to join on, if None will join on all variables
        :param name: optional name for the joined graph
        :return: new relation graph with joined outcomes
        """
        return RelationGraph(
            self._components_provider,
            name if name else self.name,
            self.join_outcomes_on_variable_set(variables))
