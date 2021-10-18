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
from typing import Tuple

from .relation_type import RelationType
from .value_node import ValueNode


class RelationEdge:

    def __init__(self, a: ValueNode, b: ValueNode, relation_type: RelationType):
        assert a.variable_id != b.variable_id, \
            f"[RelationEdge.__init__] Can't crate relation edge between values which belong to same variable, " \
            f"variable_id = {a.value_id}, a.value_id = {a.value_id}, b.value_id = {b.value_id}"
        assert a.sample_id == b.sample_id, \
            f"[RelationEdge.__init__] Can't crate relation edge between values which not belong " \
            f"to same sample graph, sample_id = {a.sample_id}, a.value_id = {a.value_id}, b.value_id = {b.value_id}"
        self.node_a: ValueNode = a
        self.node_b: ValueNode = b
        self.relation_type: RelationType = relation_type

    def __repr__(self):
        return f"RelationEdge({self.node_a.value_id} ∩ {self.node_b.value_id}, " \
               f"relation = {self.relation_type.relation_type_id})"

    def get_id(self) -> (frozenset[Tuple[str, str]], str):
        return frozenset([self.node_a.get_id(), self.node_b.get_id()]), self.relation_type.relation_type_id

    def have_node(self, node: ValueNode) -> bool:
        return self.node_a.is_equivalent(node) or self.node_b.is_equivalent(node)

    def end_node_for_start(self, start_node: ValueNode) -> ValueNode:
        if self.node_a.is_equivalent(start_node):
            return self.node_b
        elif self.node_b.is_equivalent(start_node):
            return self.node_a
        else:
            raise AssertionError(
                f"[RelationEdge.end_node_for_start] A node {start_node} is not end or start node of this edge.")
