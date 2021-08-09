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

from .variable_node import VariableNode
from .sample_graph import SampleGraph
from .inference_graph import InferenceGraph


class RelationGraph:

    def __init__(self, name: str, relation_types: List[str], variable_nodes: List[VariableNode]):
        # TODO: Конструирует граф отношений
        pass

    def add_outcomes(self, outcomes: List[SampleGraph]) -> None:
        # TODO: Для каждого проверяет чтобы ИД переменных и значений были корректны
        # TODO: Добавляе ссылки на узля значения в переменные, где они будут сканироваться при выводе
        pass

    def inference(self, query: SampleGraph) -> InferenceGraph:
        pass
