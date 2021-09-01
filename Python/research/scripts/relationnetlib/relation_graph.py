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
        self.relation_graph_name = relation_graph_name
        self._relations: Dict[str, RelationType] = {r.relation_type_id: r for r in relations}
        self._variables: Dict[str, VariableNode] = {v.variable_id: v for v in variables}
        self._outcomes: List[SampleGraph] = []

    def __repr__(self):
        return f"RelationGraph(name = {self.relation_graph_name })"

    def new_sample_graph(self, sample_graph_name: str, count: int = 1) -> SampleGraph:
        # TODO Implement count
        assert count > 0, "[RelationGraph.new_sample_graph] Sample count should be > 0"
        return SampleGraph(sample_graph_name, self._relations, self._variables, count)

    def add_outcomes(self, outcomes: List[SampleGraph]) -> None:
        start_outcome_number = len(self._outcomes)
        self._outcomes.extend(outcomes)
        for i in range(0, len(outcomes)):
            for v in outcomes[i].all_values():
                self._variables[v.variable_id].add_value(start_outcome_number + i, v)

    def inference(self, query: SampleGraph) -> InferenceGraph:
        # TODO: Фильтруем все оуткомы по граф-запросу
        pass

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

    def show_all_outcomes(self, height="1024px", width="1024px") -> None:
        net = Network(height=height, width=width)

        for outcome in self._outcomes:
            for v in outcome.all_values():
                net.add_node(
                    f"{outcome.sample_id}@{v.value_id}",
                    label=f"{outcome.sample_id}({outcome.count})@{v.value_id}")

            for e in outcome.all_edges():
                net.add_edge(
                    f"{outcome.sample_id}@{e.node_a.value_id}",
                    f"{outcome.sample_id}@{e.node_b.value_id}",
                    label=e.relation_type.relation_type_id
                )

        net.show(f"{self.relation_graph_name}_all_outcomes.html")
