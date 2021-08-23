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

from __future__ import annotations
from typing import List

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .relation_edge import RelationEdge
    from .variable_node import VariableNode


class ValueNode:

    def __init__(self, value_id: str, variable: 'VariableNode'):
        self.value_id = value_id
        self.variable = variable
        self.connected_to: List['ValueNode'] = []
        self.relations: List['RelationEdge'] = []

    def connect_to(self, value: ValueNode, relation: 'RelationEdge') -> None:
        assert value.value_id != self.value_id, \
            f"[ValueNode.connect_to] Can't connect to myself."
        assert value.variable.variable_id != self.variable.variable_id, \
            f"[ValueNode.connect_to]  Can't connect to value from the same variable, " \
            f"variable_id = {self.variable.variable_id}"
        self.connected_to.append(value)
        self.relations.append(relation)
