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

import logging
from typing import Dict, List, Set

from .relation_edge import RelationEdge
from pyvis.network import Network

from .relation_type import RelationType
from .value_node import ValueNode
from .variable_node import VariableNode


class SampleGraph:

    def __init__(
            self, sample_id: str, relations: Dict[str, RelationType], variables: Dict[str, VariableNode], count: int):
        assert sample_id, "[SampleGraph.__init__] sample_id should not be empty string"
        assert count > 0, "[SampleGraph.__init__] count should be > 0"
        self.sample_id: str = sample_id
        self.count: int = count
        self._relations: Dict[str, RelationType] = relations
        self._variables: Dict[str, VariableNode] = variables
        self._values: Dict[(str, str), ValueNode] = {}  # key: (variable_id, value_id)
        self._edges: Dict[(str, str, str), RelationEdge] = {}  # key: (a.value_id, b.value_id, relation_type_id)
        self._log = logging.getLogger('relationnetlib')

    def __repr__(self):
        return f"SampleGraph(sample_id = {self.sample_id})"

    def add_value_node(self, variable_id: str, value_id: str) -> ValueNode:
        assert variable_id in self._variables, \
            f"[SampleGraph.add_value_node] Unknown variable ID {variable_id}, acceptable: {self._variables.keys()}"
        assert value_id in self._variables[variable_id].value_ids, \
            f"[SampleGraph.add_value_node] Unknown value ID {value_id}, " \
            f"acceptable: {self._variables[variable_id].value_ids}"
        assert value_id not in self._values, \
            f"[SampleGraph.add_value_node] Value with value_id = {value_id} already exist"
        vn = ValueNode(value_id, variable_id, self.sample_id)
        self._values[(variable_id, value_id)] = vn
        self._log.debug(
            f"[SampleGraph.add_value_node] Added for variable_id = {variable_id}, value_id = {value_id}")
        return vn

    def add_relation(self, nodes: Set[ValueNode], relation_type_id: str) -> RelationEdge:
        assert len(nodes) == 2, \
            f"[SampleGraph.add_relation] Set of nodes to be connected should have size exactly 2, " \
            f"but got {len(nodes)}"
        node_a = list(nodes)[0]
        node_b = list(nodes)[1]
        assert relation_type_id in self._relations, \
            f"[SampleGraph.add_relation] Unknown relation_type_id = {relation_type_id}, " \
            f"acceptable: {self._relations.keys()}"
        assert relation_type_id in self._relations, \
            f"[SampleGraph.add_relation] Unknown relation_type_id = {relation_type_id}, " \
            f"acceptable: {self._relations.keys()}"
        assert node_a.variable_id in self._variables, \
            f"[SampleGraph.add_relation] Unknown 'a' value {node_a}, not found variable_id = {node_a.variable_id}"
        assert node_a.value_id in self._variables[node_a.variable_id].value_ids, \
            f"[SampleGraph.add_relation] Unknown 'a' value {node_a}, not found value_id = {node_a.value_id}"
        assert node_b.variable_id in self._variables, \
            f"[SampleGraph.add_relation] Unknown 'b' value {node_b}, not found variable_id = {node_b.variable_id}"
        assert node_b.value_id in self._variables[node_b.variable_id].value_ids, \
            f"[SampleGraph.add_relation] Unknown 'b' value {node_b}, not found value_id = {node_b.value_id}"
        assert node_a.value_id != node_b.value_id, \
            f"[SampleGraph.add_relation] Sample graph can't contain loop, try on value_id = {node_a.value_id}"
        assert node_a.variable_id != node_b.variable_id, \
            f"[SampleGraph.add_relation] It is impossible to connect two values belong to same variable, " \
            f"variable_id = {node_a.variable_id}"
        assert (node_a.value_id, node_b.value_id, relation_type_id) not in self._edges, \
            f"[SampleGraph.add_relation] Relation '{relation_type_id}' already exist in " \
            f"between node {node_a} and node {node_b}"
        assert node_a.sample_id == self.sample_id, \
            f"[SampleGraph.add_relation] Value a with a.sample_id = '{node_a.sample_id}' " \
            f"not belongs to this sample with self.sample_id = '{self.sample_id}'"
        assert node_b.sample_id == self.sample_id, \
            f"[SampleGraph.add_relation] Value b with b.sample_id = '{node_b.sample_id}' " \
            f"not belongs to this sample with self.sample_id = '{self.sample_id}'"
        re = RelationEdge(node_a, node_b, self._relations[relation_type_id])
        node_a.connect_to(node_b, re)
        node_b.connect_to(node_a, re)
        self._edges[(node_a.value_id, node_b.value_id, relation_type_id)] = re
        self._log.debug(
            f"[SampleGraph.add_relation] Added for node_a = {node_a}, node_b = {node_b}, ")
        return re

    def all_values(self) -> List[ValueNode]:
        return list(self._values.values())

    def all_edges(self) -> List[RelationEdge]:
        return list(self._edges.values())

    def have_value(self, variable_id: str, value_id: str) -> bool:
        return (variable_id, value_id) in self._values

    def get_value(self, variable_id: str, value_id: str) -> ValueNode:
        assert (variable_id, value_id) in self._values, \
            f"[SampleGraph.get_value] Not found value for variable_id = {variable_id} and value_id = {value_id}" \
            f"in sample_id = {self.sample_id}"
        return self._values[(variable_id, value_id)]

    def show(self, height="1024px", width="1024px") -> None:
        net = Network(height=height, width=width)
        for v in self._values.values():
            net.add_node(v.value_id, label=v.value_id)
        for e in self._edges.values():
            net.add_edge(e.node_a.value_id, e.node_b.value_id, label=e.relation_type.relation_type_id)
        net.show(f"{self.sample_id}_sample.html")
        self._log.debug(
            f"[SampleGraph.show] node count = {len(net.get_nodes())}, edge count = {len(net.get_edges())}")
