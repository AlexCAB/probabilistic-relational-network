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
from typing import Dict, List, Set, Tuple, Any

from .relation_edge import RelationEdge
from pyvis.network import Network

from .relation_type import RelationType
from .value_node import ValueNode
from .variable_node import VariableNode


class SampleGraph:

    def __init__(self, sample_id: str, relations: List[RelationType], variables: List[VariableNode]):
        assert sample_id, "[SampleGraph.__init__] sample_id should not be empty string"
        self.sample_id: str = sample_id
        self._relations: Dict[str, RelationType] = {r.relation_type_id: r for r in relations}
        self._variables: Dict[str, VariableNode] = {v.variable_id: v for v in variables}
        self._values: Dict[(str, str), ValueNode] = {}  # key: (variable_id, value_id)
        self._edges: Dict[(frozenset[(str, str)], str), RelationEdge] = {}  # key: (node ids, relation_type_id)
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
        self._values[vn.get_id()] = vn
        self._log.debug(
            f"[SampleGraph.add_value_node] Added for variable_id = {variable_id}, value_id = {value_id}")
        return vn

    def add_relation(self, nodes: Set[ValueNode], relation_type: RelationType) -> RelationEdge:
        assert len(nodes) == 2, \
            f"[SampleGraph.add_relation] Set of nodes to be connected should have size exactly 2, " \
            f"but got {len(nodes)}"
        node_a = list(nodes)[0]
        node_b = list(nodes)[1]
        assert relation_type.relation_type_id in self._relations, \
            f"[SampleGraph.add_relation] Unknown relation_type_id = {relation_type.relation_type_id}, " \
            f"acceptable: {self._relations.keys()}"
        assert relation_type.relation_type_id in self._relations, \
            f"[SampleGraph.add_relation] Unknown relation_type_id = {relation_type.relation_type_id}, " \
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
        assert (frozenset([node_a.get_id, node_b.get_id]), relation_type.relation_type_id) not in self._edges, \
            f"[SampleGraph.add_relation] Relation '{relation_type.relation_type_id}' already exist in " \
            f"between node {node_a} and node {node_b}"
        assert node_a.sample_id == self.sample_id, \
            f"[SampleGraph.add_relation] Value a with a.sample_id = '{node_a.sample_id}' " \
            f"not belongs to this sample with self.sample_id = '{self.sample_id}'"
        assert node_b.sample_id == self.sample_id, \
            f"[SampleGraph.add_relation] Value b with b.sample_id = '{node_b.sample_id}' " \
            f"not belongs to this sample with self.sample_id = '{self.sample_id}'"
        re = RelationEdge(node_a, node_b, relation_type)
        node_a.connect_to(node_b, re)
        node_b.connect_to(node_a, re)
        self._edges[re.get_id()] = re
        self._log.debug(
            f"[SampleGraph.add_relation] Added for node_a = {node_a}, node_b = {node_b}, ")
        return re

    def get_all_values(self) -> List[ValueNode]:
        return list(self._values.values())

    def get_number_of_values(self) -> int:
        return len(self._values)

    def get_number_of_edges(self) -> int:
        return len(self._edges)

    def all_edges(self) -> List[RelationEdge]:
        return list(self._edges.values())

    def have_value(self, variable_id: str, value_id: str) -> bool:
        return (variable_id, value_id) in self._values

    def get_value(self, variable_id: str, value_id: str) -> ValueNode:
        assert (variable_id, value_id) in self._values, \
            f"[SampleGraph.get_value] Not found value for variable_id = {variable_id} and value_id = {value_id}" \
            f"in sample_id = {self.sample_id}"
        return self._values[(variable_id, value_id)]

    def get_hash(self) -> frozenset[Any]:
        return frozenset(self._values.keys()).union(frozenset(self._edges.keys()))

    def show(self, height="1024px", width="1024px") -> None:
        net = Network(height=height, width=width)
        for v in self._values.values():
            net.add_node(v.value_id, label=v.value_id)
        for e in self._edges.values():
            net.add_edge(e.node_a.value_id, e.node_b.value_id, label=e.relation_type.relation_type_id)
        net.show(f"{self.sample_id}_sample.html")
        self._log.debug(
            f"[SampleGraph.show] node count = {len(net.get_nodes())}, edge count = {len(net.get_edges())}")

    def have_variable_value(self, variable_id: str) -> bool:
        return variable_id in [vid for vid, _ in self._values.keys()]

    def get_value_id_for_variable(self, variable_id: str) -> bool:
        found_val_ids = [val_id for var_id, val_id in self._values.keys() if var_id == variable_id]
        assert len(found_val_ids) == 1, \
            f"[SampleGraph.get_value_id_for_variable] Expect to find exactly one value for " \
            f"variable_id = {variable_id}, but found: {found_val_ids}"
        return found_val_ids[0]

    def clone(
            self,
            sample_id: str,
            values_to_replace: Dict[str, str] = None,
            relations: List[RelationType] = None,
            variables: List[VariableNode] = None
    ) -> 'SampleGraph':
        """
        Clone this SampleGraph with replacing of values in selected variables
        :param sample_id: ID for new SampleGraph
        :param values_to_replace: # Dict{variable_id for which value need to be replaced, value_id new value ID}
        :param relations: # Alternative relations if None self._relation will used
        :param variables: # Alternative variables if None self._variables will used
        :return: new SampleGraph
        """
        if relations:
            used_rel = set([e.relation_type.relation_type_id for e in self._edges.values()])
            provided_rel = set([r.relation_type_id for r in relations])
            assert used_rel.issubset(provided_rel),  \
                f"[SampleGraph.clone] Not all used relation are in provided, used_rel = {used_rel}, " \
                f"provided_rel = {provided_rel}"

        if variables:
            used_var = set([v.variable_id for v in self._values.values()])
            provided_var = set([v.variable_id for v in variables])
            assert used_var.issubset(provided_var),  \
                f"[SampleGraph.clone] Not all used variables are in provided, used_var = {used_var}, " \
                f"provided_var = {provided_var}"

        sg = SampleGraph(
            sample_id,
            relations if relations else self._relations.values(),
            variables if variables else self._variables.values()
        )

        vtr = values_to_replace if values_to_replace else {}

        for v in self._values.values():
            sg.add_value_node(
                v.variable_id,
                vtr[v.variable_id] if v.variable_id in vtr else v.value_id)

        for e in self._edges.values():
            def get_node(n: ValueNode) -> ValueNode:
                return sg.add_value_node(
                    n.variable_id,
                    vtr[n.variable_id] if n.variable_id in vtr else n.value_id)
            sg.add_relation({get_node(e.node_a), get_node(e.node_b)}, e.relation_type)

        self._log.debug(
            f"[SampleGraph.clone] Cloned from this sample_id = {self.sample_id} to new sample_id = {sample_id}")

        return sg

    def validate(self) -> List[str]:  # Returns list of error messages
        if len(self._values) == 1 and len(self._edges) == 0:
            return []

        if len(self._values) > 1 and len(self._edges) == 0:
            return [f"Graph is not linked, {len(self._values)} values where 0 edges"]

        if not self._values:
            return [f"Graph should not be empty"]

        edges = list(self._edges.values())
        start_node = edges[0].node_a

        def trace_graph(start: ValueNode, traced: Set[Tuple[str, str]]) -> Set[Tuple[str, str]]:
            neighbors = [e.end_node_for_start(start) for e in edges if e.have_node(start)]
            for neighbor in neighbors:
                if neighbor.get_id() not in traced:
                    traced.add(neighbor.get_id())
                    traced.update(trace_graph(neighbor, traced))
            return traced

        traced_nodes_ids = trace_graph(start_node, {start_node.get_id()})
        actual_node_ids = set(self._values.keys())

        if traced_nodes_ids != actual_node_ids:
            return [f"Graph is not linked, traced_nodes_ids = {traced_nodes_ids}, actual_node_ids = {actual_node_ids}"]
        else:
            return []

    def is_equivalent(self, other: 'SampleGraph') -> bool:
        return self.get_hash() == other.get_hash()
