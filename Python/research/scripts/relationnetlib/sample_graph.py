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

from typing import Dict, List

from .relation_edge import RelationEdge

from .relation_type import RelationType
from .value_node import ValueNode
from .variable_node import VariableNode


class SampleGraph:

    def __init__(self, name: str, relations: Dict[str, RelationType], variables: Dict[str, VariableNode]):
        assert name, "[SampleGraph.__init__] Name should not be empty string"
        self._name: str = name
        self._relations: Dict[str, RelationType] = relations
        self._variables: Dict[str, VariableNode] = variables
        self._values: Dict[(str, str), ValueNode] = {}  # key: (variable_id, value_id)
        self._edges: Dict[(str, str, str), RelationEdge] = {}  # key: (a.value_id, b.value_id, relation_type_id)

    def __repr__(self):
        return f"SampleGraph(name = {self._name})"

    def add_value_node(self, variable_id: str, value_id: str) -> ValueNode:
        assert variable_id in self._variables, \
            f"[SampleGraph.add_value_node] Unknown variable ID {variable_id}, acceptable: {self._variables.keys()}"
        assert value_id in self._variables[variable_id].value_ids, \
            f"[SampleGraph.add_value_node] Unknown value ID {value_id}, " \
            f"acceptable: {self._variables[variable_id].value_ids}"
        assert value_id not in self._values, \
            f"[SampleGraph.add_value_node] Value with value_id = {value_id} already exist"
        vn = ValueNode(value_id, variable_id)
        self._values[(variable_id, value_id)] = vn
        return vn

    def add_relation(self, a: ValueNode, b: ValueNode, relation_type_id: str) -> RelationEdge:
        assert relation_type_id in self._relations, \
            f"[SampleGraph.add_relation] Unknown relation_type_id = {relation_type_id}, " \
            f"acceptable: {self._relations.keys()}"
        assert a.variable_id in self._variables, \
            f"[SampleGraph.add_relation] Unknown 'a' value {a}, not found variable_id = {a.variable_id}"
        assert a.value_id in self._variables[a.variable_id].value_ids, \
            f"[SampleGraph.add_relation] Unknown 'a' value {a}, not found value_id = {a.value_id}"
        assert b.variable_id in self._variables, \
            f"[SampleGraph.add_relation] Unknown 'b' value {b}, not found variable_id = {b.variable_id}"
        assert b.value_id in self._variables[b.variable_id].value_ids, \
            f"[SampleGraph.add_relation] Unknown 'b' value {b}, not found value_id = {b.value_id}"
        assert a.value_id != b.value_id, \
            f"[SampleGraph.add_relation] Sample graph can't contain loop, try on value_id = {a.value_id}"
        assert a.variable_id != b.variable_id, \
            f"[SampleGraph.add_relation] It is impossible to connect two values belong to same variable, " \
            f"variable_id = {a.variable_id}"
        assert (a.value_id, b.value_id, relation_type_id) not in self._edges, \
            f"[SampleGraph.add_relation] Relation '{relation_type_id}' already exist in " \
            f"between node {a} and node {b}"
        re = RelationEdge(a, b, self._relations[relation_type_id])
        a.connect_to(b, re)
        b.connect_to(a, re)
        self._edges[(a.value_id, b.value_id, relation_type_id)] = re
        return re

    def all_values(self) -> List[ValueNode]:
        return list(self._values.values())
