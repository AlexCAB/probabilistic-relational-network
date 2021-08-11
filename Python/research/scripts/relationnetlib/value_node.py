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
from scripts.relationnetlib.relation_edge import RelationEdge
from scripts.relationnetlib.variable_node import VariableNode


class ValueNode:

    def __init__(self, value_id: str, variable: VariableNode):
        self.value_id = value_id
        self.variable = variable

    def connect_to(self, value: ValueNode, relation: RelationEdge) -> None:
        pass