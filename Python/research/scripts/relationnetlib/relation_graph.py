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

from typing import List, Dict
from pyvis.network import Network
import networkx as nx

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
        assert count > 0, "[RelationGraph.new_sample_graph] Sample count should be > 0"
        return SampleGraph(sample_graph_name, self._relations, self._variables)

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
        nx_graph = nx.MultiGraph()

        for v in variables:
            nx_graph.add_node(v.variable_id, label=v.variable_id)

        for a in variables:
            for b in variables:
                if a.variable_id != b.variable_id:
                    relations = a.get_all_relation_to(b.variable_id)
                    if relations:



                        print(f"AAAAAAAAA a = {a}")
                        print(f"BBBBBBBBB b = {b}")
                        print(f"RRRRRRRRR relations = {relations}")



        # TODO Как построить все рёбра соединяющие переменные



        #
        # nt = Network(height, width)
        # nt.from_nx(nx_graph)
        # nt.show(f"{self.relation_graph_name}_relation_graph.html")


