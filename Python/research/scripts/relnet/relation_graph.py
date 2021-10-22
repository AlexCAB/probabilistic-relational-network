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
from typing import List, Dict, Set, Any, Tuple, Optional

from pyvis.network import Network
from .sample_graph import SampleGraph, ValueNode, RelationEdge, SampleGraphBuilder


# TODO Новый рефактроинг:
# TODO  1) RelationGraphBuilder предоставляет SampleGraphBuilder методы для получения ValueNode и RelationEdge
# TODO     они создаются один раз и затем кешируются, что будет экономить память
# TODO     Нужно создать интерфейс и передовать через парамтры в билдер.
# TODO  2) RelationGraphBuilder имеет метод .sample_builder() -> SampleGraphBuilder
# TODO  3) RelationGraphBuilder имеет метод .build_sample(lambda: Callable[SampleGraphBuilder, [SampleGraph]])
# TODO  4) В SampleGraphBuilder мы просто соеденяем ValueNode при помощи RelationEdge (полученых из кеша),
# TODO     т.е. по сути SampleGraph просто колекция ссылок на ValueNode и RelationEdge.
# TODO     так можно сэкономить память, сразу же валидировать связаность SampleGraph (при добавлении ребра).
# TODO  5) SampleGraphBuilder имеет метод .build_single_node() -> SampleGraph, создаёт граф из одной ноды
# TODO     и метод add_relation() как он есть и здесь проверяется связаность, и build() который
# TODO     проверят только что семпл граф не пустой.
# TODO
# TODO
# TODO
# TODO
# TODO
# TODO


class RelationGraphBuilder:

    def __init__(
            self,
            variables: Dict[Any, Set[Any]],
            relations: Set[Any],
            name: Optional[str] = None,
            outcomes: Dict[SampleGraph, int] = None
    ):
        for var, values in variables.items():
            assert isinstance(var, Hashable), \
                f"[RelationGraphBuilder.__init__] Variable '{var}' should be hashable"
            assert values, \
                f"[RelationGraphBuilder.__init__] Set of variable values should not be empty, found for {var}"
            for val in values:
                assert isinstance(val, Hashable), \
                    f"[RelationGraphBuilder.__init__] Value '{val}' of variable '{var}' should be hashable"
        assert relations, \
            f"[RelationGraphBuilder.__init__] Set of relations should not be empty."
        for rel in relations:
            assert isinstance(rel, Hashable), \
                f"[RelationGraphBuilder.__init__] Relation '{rel}' should be hashable"

        self._variables: Dict[Any, Set[Any]] = variables
        self._relations: Set[Any] = relations
        self._name: Optional[str] = name
        self._outcomes: Dict[SampleGraph, int] = outcomes if outcomes else {}
        self._id_counter = 0

    def next_id(self) -> int:
        self._id_counter += 1
        return self._id_counter

    def can_be_added(self, outcome: SampleGraph) -> Optional[str]:
        for node in outcome.nodes:
            if node.variable not in self._variables:
                return f"Variable {node.variable} of node {node} not in list of variables {self._variables}"
            if node.value not in self._variables[node.variable]:
                return f"Value {node.value} of node {node} not in list of values {self._variables[node.variable]}"

        for edge in outcome.edges:
            if edge.relation not in self._relations:
                return f"Relation {edge.relation} not in list of relations {self._relations}"

    def add_outcome_unsafe(self, outcome: SampleGraph, count: int = 1) -> 'RelationGraphBuilder':
        if outcome in self._outcomes:
            self._outcomes[outcome] += count
        else:
            self._outcomes[outcome] = count
        return self

    def add_outcomes_unsafe(self, outcomes: List[SampleGraph]) -> 'RelationGraphBuilder':
        for outcome in outcomes:
            self.add_outcome_unsafe(outcome)
        return self

    def add_outcome(self, outcome: SampleGraph, count: int = 1) -> 'RelationGraphBuilder':
        assert count >= 1, \
            f"[RelationGraphBuilder.add_outcome] Count '{count}' should be >= 1"
        cant_be_added_reason = self.can_be_added(outcome)
        assert not cant_be_added_reason, \
            f"[RelationGraphBuilder.add_outcome] Outcome can't be added since: {cant_be_added_reason}"

        return self.add_outcome_unsafe(outcome, count)

    def generate_all_possible_outcomes(self) -> 'RelationGraphBuilder':
        assert not self._outcomes, \
            f"[RelationGraphBuilder.generate_all_possible_outcomes] Builder should not have outcomes added, " \
            f"found {len(self._outcomes)}"

        indexed_variables = [(var, list(values)) for var, values in self._variables]
        indexed_relations = list(self._relations)

        all_nodes: List[ValueNode] = [ValueNode(var, values[0]) for var, values in indexed_variables]
        all_edges: List[(ValueNode, ValueNode)] = [(n_1, n_2) for n_2 in all_nodes for n_1 in all_nodes]

        index_acc: List[int] = [-1 for _ in range(0,  len(all_edges))]
        edges_indices: List[List[int]] = []

        while set([i < (len(indexed_relations) - 1) for i in index_acc]) != {False} and len(all_edges) != 0:
            i = 0
            while index_acc[i] >= (len(indexed_relations) - 1) and i < len(all_edges):
                index_acc[i] = -1
                i += 1
            index_acc[i] += 1
            edges_indices.append(index_acc.copy())

        for node in all_nodes:
            self.add_outcome_unsafe(
                SampleGraphBuilder(nodes={node}, name=f"O_{self.next_id()}").build_unsafe())

        for edges_index in edges_indices:
            active_edges = {
                RelationEdge(frozenset(all_edges[j]), indexed_relations[edges_index[j]])
                for j in range(0, len(edges_index))
                if edges_index[j] >= 0}

            builder = SampleGraphBuilder(
                nodes=set([n for e in active_edges for n in e.endpoints]),
                edges=active_edges)

            if builder.is_connected():
                self.add_outcome_unsafe(
                    builder.set_name(f"O_{self.next_id()}").build_unsafe())

        for var, values in indexed_variables:
            self.add_outcomes_unsafe([
                outcome.with_replaced_values({var: val}, f"O_{self.next_id()}")
                for val in values[1:]   # Iterate over all value except first
                for outcome in self._outcomes])

        for outcome, count in self._outcomes:
            assert count == 1, \
                f"[RelationGraphBuilder.generate_all_possible_outcomes] Outcome {outcome} added {count} times"
        return self

    def build(self) -> 'RelationGraph':
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
