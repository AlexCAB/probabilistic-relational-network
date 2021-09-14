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

from .relation_edge import RelationEdge
from .value_node import ValueNode


class VariableNode:

    def __init__(self, variable_id: str, value_ids: List[str]):
        assert variable_id, f"[VariableNode.__init__] variable_id should not be empty string"
        assert value_ids, f"[VariableNode.__init__] value_ids should not be empty list"
        assert len(set(value_ids)) == len(value_ids), \
            f"[VariableNode.__init__] value_ids be list of unique ids"
        self.variable_id = variable_id
        self.value_ids = value_ids
        self._values: Dict[(int, str), ValueNode] = {}  # key: (outcome_number, value_id)

    def __repr__(self):
        return f"VariableNode(variable_id = {self.variable_id}, value_ids = {self.value_ids})"

    def add_value(self, outcome_number: int, node: ValueNode) -> None:
        self._values[(outcome_number, node.value_id)] = node

    def get_all_relation_between(self, variable_id: str) -> List[RelationEdge]:
        relations = []
        for v in self._values.values():
            for r in v.relations:
                if r.node_a.variable_id == self.variable_id and r.node_b.variable_id == variable_id:
                    relations.append(r)
                if r.node_b.variable_id == self.variable_id and r.node_a.variable_id == variable_id:
                    relations.append(r)
        return relations
