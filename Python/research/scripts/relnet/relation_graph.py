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

from typing import List, Dict, Set, Any, Tuple, Optional, Callable, Union

from pyvis.network import Network

from .inference_graph import InferenceGraph
from .sample_graph import SampleGraph, ValueNode, RelationEdge, SampleGraphBuilder, SampleGraphComponentsProvider


class BuilderComponentsProvider(SampleGraphComponentsProvider):
    """
    Implementation of sample graph components provider
    """

    def __init__(self, variables: Dict[Any, Set[Any]], relations: Set[Any]):

        assert variables, \
            f"[BuilderComponentsProvider.__init__] Set of variables should not be empty."
        for var, values in variables.items():
            assert values, \
                f"[BuilderComponentsProvider.__init__] Set of variable values should not be empty, found for {var}"
        assert relations, \
            f"[BuilderComponentsProvider.__init__] Set of relations should not be empty."

        self._variables: Dict[Any, Set[Any]] = variables
        self._relations: Set[Any] = relations
        self.nodes: Dict[Tuple[Any, Any], ValueNode] = {}
        self.edges: Dict[Tuple[frozenset[ValueNode], Any], RelationEdge] = {}

    def variables(self) -> frozenset[Tuple[Any, frozenset[Any]]]:
        return frozenset({(k, frozenset(v)) for k, v in self._variables.items()})

    def relations(self) -> frozenset[Any]:
        return frozenset(self._relations)

    def get_node(self, variable: Any, value: Any) -> ValueNode:
        assert variable in self._variables, \
            f"[BuilderComponentsProvider.get_node] Unknown variable {variable}"
        assert value in self._variables[variable], \
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
        assert relation in self._relations, \
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
            variables:  Optional[Dict[Any, Set[Any]]] = None,
            relations:  Optional[Set[Any]] = None,
            name: Optional[str] = None,
            outcomes: Dict[SampleGraph, int] = None,
            components_provider: Optional[SampleGraphComponentsProvider] = None,
    ):
        assert (variables and relations) or components_provider, \
            "[RelationGraphBuilder.__init__] (variables and relations) or components_provider should be passed"

        self._components_provider = components_provider if components_provider \
            else BuilderComponentsProvider(variables, relations)
        self._name: Optional[str] = name
        self._outcomes: Dict[SampleGraph, int] = outcomes if outcomes else {}
        self._id_counter = 0

        self.variables: frozenset[Tuple[Any, frozenset[Any]]] = self._components_provider.variables()
        self.relations: frozenset[Any] = self._components_provider.relations()

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
            f"found {len(self._outcomes)} outcomes"

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
                for outcome in self._outcomes
                for val in values[1:]  # Iterate over all value except first
                if outcome.contains_variable(var)])

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
            self._outcomes)


class RelationGraph:
    """
    Immutable relation graph instance
    """

    def __init__(
            self,
            components_provider: SampleGraphComponentsProvider,
            name: Optional[str],
            outcomes: Dict[SampleGraph, int]
    ):
        self.variables: frozenset[Tuple[Any, frozenset[Any]]] = components_provider.variables()
        self.relations: frozenset[Any] = components_provider.relations()
        self.number_of_outcomes: int = sum(outcomes.values())
        self.name: str = name if name else f"relation_graph_with_{self.number_of_outcomes}_outcomes"
        self._outcomes: Dict[SampleGraph, int] = outcomes
        self._components_provider: SampleGraphComponentsProvider = components_provider

    def __repr__(self):
        return self.name

    def __copy__(self):
        raise AssertionError(
            "[RelationGraph.__copy__] Sample graph should not be copied, "
            "use one of transformation method or builder to get new instance")

    def outcomes(self) -> frozenset[Tuple[SampleGraph, int]]:
        """
        Return relation graph outcomes in form of frozenset
        :return: frozenset[Tuple[SampleGraph, count]]:
        """
        return frozenset({(o, c) for o, c in self._outcomes.items()})

    def outcomes_as_edges_sets(
            self
    ) -> frozenset[Tuple[Union[frozenset[Tuple[frozenset[Tuple[Any, Any]], Any]], Tuple[Any, Any]]], int]:
        """
        Return relation graph outcomes as set of edges_sets
        :return: frozenset[frozenset[(frozenset[(variable, value)], value)] or (variable, value), count]:
        """
        return frozenset({(o.edges_set_view(), c) for o, c in self._outcomes.items()})

    def builder(self) -> RelationGraphBuilder:
        """
        Construct new relation graph builder which contains all outcomes from this relation graph
        :return: new builder instance
        """
        return RelationGraphBuilder(
            {var: set(values) for var, values in self.variables},
            set(self.relations),
            self.name,
            {outcome: count for outcome, count in self._outcomes.items()},
            self._components_provider)

    def visualize_relation_graph(self,  height="1024px", width="1024px") -> None:
        """
        Will render this relation graph as HTML page and show in browser
        :param height: window height
        :param width: window width
        :return: None
        """
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

    def visualize_outcomes(self, height="1024px", width="1024px") -> None:
        """
        Will render all outcomes as HTML page and show in browser
        :param height: window height
        :param width: window width
        :return: None
        """
        net = Network(height=height, width=width)

        for outcome, count in self._outcomes.items():
            for node in outcome.nodes:
                net.add_node(node.string_id, label=f"{node.string_id}@{outcome.name}({count})")
            for edge in outcome.edges:
                ep = list(edge.endpoints)
                net.add_edge(ep[0].string_id, ep[1].string_id, label=str(edge.relation))

        net.show(f"{self.name}_all_outcomes.html")

    def describe(self) -> Dict[str, Any]:
        """
        Return set of properties of this relation graph
        :return: Dict[property_name, property_value]
        """
        return {
            "name": self.name,
            "number_of_variables": len(self.variables),
            "number_of_relations": len(self.relations),
            "number_of_outcomes": self.number_of_outcomes,
            "variables": {str(v) for v, _ in self.variables},
            "relations": {str(r) for r in self.relations},
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

    def inference(self, query: SampleGraph) -> InferenceGraph:
        """
        Do inference for given query. Will filter out outcomes which is sub-graphs of query graph
        and pack in InferenceGraph instance.
        :param query: and SampleGraph to filter on
        :return: new instance of InferenceGraph
        """
        assert query.is_compatible(self._components_provider), \
            f"[RelationGraphBuilder.add_outcome] Query {query} is not compatible with this relation graph, " \
            f"since it vas created with using another SampleGraphComponentsProvider"

        selected_outcomes: Dict[SampleGraph, int] = {
            outcome: count for outcome, count in self._outcomes.items() if query.is_subgraph(outcome)}

        return InferenceGraph(
            self._components_provider,
            query,
            self.name,
            selected_outcomes)
