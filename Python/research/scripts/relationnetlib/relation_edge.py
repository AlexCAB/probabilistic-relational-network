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

from .relation_type import RelationType
from .value_node import ValueNode


class RelationEdge:

    def __init__(self, a: ValueNode, b: ValueNode, relation_type: RelationType):
        self.node_a: ValueNode = a
        self.node_b: ValueNode = b
        self.relation_type: RelationType = relation_type

    def __repr__(self):
        return f"RelationEdge({self.node_a.value_id} ∩ {self.node_b.value_id}, " \
               f"relation = {self.relation_type.relation_type_id})"
