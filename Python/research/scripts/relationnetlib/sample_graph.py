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

from .value_node import ValueNode


class SampleGraph:

    def __init__(self, name: str):
        # TODO: Конструирует граф-образец
        pass

    def add_value_node(self, variable_id: str, value_id: str) -> ValueNode:
        # TODO: создаёт узел-значение и добавляет во внутренний список
        pass

    def add_relation(self, a: ValueNode, b: ValueNode, relation_type: str) -> ValueNode:
        # TODO: Добавляет отношение
        # TODO: Вызывает _connect_to на каждом из узлов чтобы обьединить их
        pass