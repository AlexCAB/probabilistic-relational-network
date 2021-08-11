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
from .relation_type import RelationType
from .value_node import ValueNode
from .variable_node import VariableNode


class SampleGraph:

    def __init__(self, name: str, relations: Dict[str, RelationType], variables: Dict[str, VariableNode]):
        assert name, "[SampleGraph.__init__] name hould not be empty string"
        self._name = name
        self._relations = relations
        self._variables = variables
        self._values: Dict[(str, str), ValueNode] = {}  # key: (variable_id, value_id)

    def add_value_node(self, variable_id: str, value_id: str) -> ValueNode:
        assert variable_id in self._variables, \
            f"[SampleGraph.add_value_node] Unknown variable ID {variable_id}, acceptable: {self._variables.keys()}"
        assert value_id in self._variables[variable_id].value_ids, \
            f"[SampleGraph.add_value_node] Unknown value ID {value_id}, " \
            f"acceptable: {self._variables[variable_id].value_ids}"
        vn = ValueNode(value_id, self._variables[variable_id])
        self._values[(variable_id, value_id)] = vn
        self._variables[variable_id].add_value(vn)
        return vn

    def add_relation(self, a: ValueNode, b: ValueNode, relation_type_id: str) -> RelationEdge:
        assert relation_type_id in self._relations, \
            f"[SampleGraph.add_relation] Unknown relation_type_id {relation_type_id}, " \
            f"acceptable: {self._relations.keys()}"
        assert a.variable.variable_id in self._variables, \
            f"[SampleGraph.add_relation] Unknown 'a' value {a}, not found variable_id {a.variable.variable_id}"
        assert a.value_id in self._variables[a.variable.variable_id].value_ids, \
            f"[SampleGraph.add_relation] Unknown 'a' value {a}, not found value_id {a.value_id}"
        assert b.variable.variable_id in self._variables, \
            f"[SampleGraph.add_relation] Unknown 'b' value {b}, not found variable_id {b.variable.variable_id}"
        assert b.value_id in self._variables[b.variable.variable_id].value_ids, \
            f"[SampleGraph.add_relation] Unknown 'b' value {b}, not found value_id {b.value_id}"
        re = RelationEdge(a, b, self._relations[relation_type_id])
        a.connect_to(b, re)
        b.connect_to(a, re)
        return re
