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

from typing import List

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
        self._relations = {r.relation_type_id: r for r in relations}
        self._variables = {v.variable_id: v for v in variables}

    def new_sample_graph(self, sample_graph_name: str, count: int = 1) -> SampleGraph:
        assert count > 0, "[RelationGraph.new_sample_graph] Sample count should be > 0"
        return SampleGraph(sample_graph_name, self._relations, self._variables)

    def add_outcomes(self, outcomes: List[SampleGraph]) -> None:
        # TODO: Для каждого проверяет чтобы ИД переменных и значений были корректны
        # TODO: Добавляе ссылки на узля значения в переменные, где они будут сканироваться при выводе
        pass

    def inference(self, query: SampleGraph) -> InferenceGraph:
        # TODO: Фильтруем все оуткомы по граф-запросу
        pass
