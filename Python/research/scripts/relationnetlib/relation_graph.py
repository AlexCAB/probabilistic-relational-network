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
import logging
from typing import List, Dict, Set

from pyvis.network import Network

from .sample_graph import SampleGraph
from .inference_graph import InferenceGraph
from .relation_type import RelationType
from .variable_node import VariableNode


class RelationGraph:

    def __init__(self, relation_graph_name: str, relations: List[RelationType], variables: List[VariableNode]):
        assert relation_graph_name, "[RelationGraph.__init__] The relation_graph_name should not be empty string"
        assert relations, "[RelationGraph.__init__] The relations should not be empty string"
        assert variables, "[RelationGraph.__init__] The variables should not be empty string"
        assert len(set([r.relation_type_id for r in relations])) == len(relations), \
            "[RelationGraph.__init__] relations parameter should be a list with unique relations"
        assert len(set([v.variable_id for v in variables])) == len(variables), \
            "[RelationGraph.__init__] variables parameter should be a list with unique variables"
        self.relation_graph_name = relation_graph_name
        self._relations: Dict[str, RelationType] = {r.relation_type_id: copy.deepcopy(r) for r in relations}
        self._variables: Dict[str, VariableNode] = {v.variable_id: copy.deepcopy(v) for v in variables}
        self._outcomes: List[SampleGraph] = []
        self._log = logging.getLogger('relationnetlib')
        self._log.debug(f"[RelationGraph.__init__] Created relation graph '{relation_graph_name}'")

    def __repr__(self):
        return f"RelationGraph(name = {self.relation_graph_name })"

    def get_relation_types(self) -> Dict[str, RelationType]:
        return self._relations

    def get_variable_nodes(self) -> Dict[str, VariableNode]:
        return self._variables

    def new_sample_graph(self, sample_graph_name: str, count: int = 1) -> SampleGraph:
        assert count > 0, "[RelationGraph.new_sample_graph] Sample count should be > 0"
        self._log.debug(
            f"[RelationGraph.new_sample_graph] sample_graph_name = {sample_graph_name}, count = {count}")
        return SampleGraph(sample_graph_name, count, self)

    def add_outcomes(self, outcomes: List[SampleGraph]) -> None:
        start_outcome_number = len(self._outcomes)
        for o in outcomes:
            errors = o.validate()
            assert not errors, f"[RelationGraph.add_outcomes] Invalid outcome found: {o}, errors: {errors}"
        self._outcomes.extend(outcomes)
        for i in range(0, len(outcomes)):
            for v in outcomes[i].all_values():
                self._variables[v.variable_id].add_value(start_outcome_number + i, v)
        self._log.debug(f"[RelationGraph.add_outcomes] len(outcomes) = {len(outcomes)}")

    def show_relation_graph(self,  height="1024px", width="1024px") -> None:
        variables = self._variables.values()
        net = Network(height=height, width=width)
        edges: Dict[frozenset, Set[str]] = {}

        for v in variables:
            net.add_node(v.variable_id, label=v.variable_id)

        for var_a in variables:
            for var_b in variables:
                if var_a.variable_id != var_b.variable_id:
                    for relation in var_a.get_all_relation_between(var_b.variable_id):
                        k = frozenset([var_a.variable_id, var_b.variable_id])
                        if k in edges:
                            edges[k].add(relation.relation_type.relation_type_id)
                        else:
                            edges[k] = {relation.relation_type.relation_type_id}

        for k, elation_types in edges.items():
            net.add_edge(list(k)[0], list(k)[1], label=' | '.join(elation_types))

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

        net.show(f"{self.relation_graph_name}_relation_graph.html")

        self._log.debug(
            f"[RelationGraph.show_relation_graph] node count = {len(net.get_nodes())}, "
            f"edge count = {len(net.get_edges())}")

    def show_all_outcomes(self, height="1024px", width="1024px") -> None:
        net = Network(height=height, width=width)

        for outcome in self._outcomes:
            for v in outcome.all_values():
                net.add_node(
                    f"{outcome.sample_id}@{v.value_id}",
                    label=f"{outcome.sample_id}({outcome.count})@{v.variable_id}({v.value_id})")

            for e in outcome.all_edges():
                net.add_edge(
                    f"{outcome.sample_id}@{e.node_a.value_id}",
                    f"{outcome.sample_id}@{e.node_b.value_id}",
                    label=e.relation_type.relation_type_id
                )

        net.show(f"{self.relation_graph_name}_all_outcomes.html")

        self._log.debug(f"[RelationGraph.show_all_outcomes] len(outcome) = {len(self._outcomes)}")

    def inference(self, query: SampleGraph) -> InferenceGraph:
        # TODO: Фильтруем все оуткомы по граф-запросу
        pass

    def generate_all_possible_outcomes(self) -> None:
        variables = list(self._variables.values())
        relation_types = list(self._relations.values())
        node_ids = [(v.variable_id, v.value_ids[0]) for v in variables]

        self._log.debug(
            f"[RelationGraph.generate_all_possible_outcomes] len(node_ids) = {len(node_ids)}, "
            f"node_ids = {node_ids}, relation_types = {relation_types}")

        edge_ids = []
        for n1 in node_ids:
            for n2 in node_ids:
                if n1 != n2 and (n2, n1) not in edge_ids:
                    edge_ids.append((n1, n2))

        self._log.debug(
            f"[RelationGraph.generate_all_possible_outcomes] len(edge_ids) = {len(edge_ids)}, edge_ids = {edge_ids}")

        rel_lim = len(relation_types) - 1
        n_edges = len(edge_ids)
        index_acc = [-1 for _ in range(0, n_edges)]
        edge_indices = []

        while set([i < rel_lim for i in index_acc]) != {False}:
            i = 0
            while index_acc[i] >= rel_lim and i < n_edges:
                index_acc[i] = -1
                i += 1
            index_acc[i] += 1
            edge_indices.append(index_acc.copy())

        self._log.debug(f"[RelationGraph.generate_all_possible_outcomes] len(edge_indices) = {len(edge_indices)}")

        outcomes = []
        outcome_count = 1

        for variable_id, value_id in node_ids:
            sg = self.new_sample_graph(f"O_{outcome_count}")
            outcome_count += 1
            sg.add_value_node(variable_id, value_id)
            outcomes.append(sg)

        for index in edge_indices:

            sg = self.new_sample_graph(f"O_{outcome_count}")
            outcome_count += 1

            for j in range(0, len(index)):
                if index[j] >= 0:
                    node_a_id, node_b_id = edge_ids[j]
                    for variable_id, value_id in [node_a_id, node_b_id]:
                        if not sg.have_value(variable_id, value_id):
                            sg.add_value_node(variable_id, value_id)

            for j in range(0, len(index)):
                if index[j] >= 0:
                    node_a_id, node_b_id = edge_ids[j]
                    rel_type = relation_types[index[j]]
                    nodes = [sg.get_value(variable_id, value_id)
                             for variable_id, value_id in [node_a_id, node_b_id]]
                    sg.add_relation(set(nodes), rel_type)

            outcomes.append(sg)

        self._log.debug(f"[RelationGraph.generate_all_possible_outcomes] Init len(outcomes) = {len(outcomes)}")

        var_len = len(variables)
        val_i, var_j = 1, 0
        cloned_outcomes = []

        while var_j < var_len:
            var = variables[var_j]
            if len(var.value_ids) > 1:
                val_id = var.value_ids[val_i]

                for o in outcomes:
                    if o.have_variable_value(var.variable_id):
                        cloned_outcomes.append(
                            o.clone(f"O_{outcome_count}", values_to_replace={var.variable_id: val_id}))
                        outcome_count += 1

                if val_i >= (len(var.value_ids) - 1):
                    var_j += 1
                    val_i = 0
                    outcomes.extend(cloned_outcomes)
                    cloned_outcomes = []
                val_i += 1

            else:
                var_j += 1

        self._log.debug(f"[RelationGraph.generate_all_possible_outcomes] Total len(outcomes) = {len(outcomes)}")

        o_i, o_j = 0, 0

        while o_j < len(outcomes):
            assert o_i == o_j or not outcomes[o_i].is_equivalent(outcomes[o_j]), \
                f"[RelationGraph.generate_all_possible_outcomes] Duplicate outcomes " \
                f"found: {outcomes[o_i]} and {outcomes[o_j]}"
            o_i += 1
            if o_i >= len(outcomes):
                o_j += 1
                o_i = 0

        self.add_outcomes(outcomes)
