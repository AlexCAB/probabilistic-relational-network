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
created: 2021-10-18
"""

import copy
import os
from collections import Hashable
from typing import Dict, List, Set, Any, Optional, Tuple

from pyvis.network import Network


class ValueNode:

    def __init__(self, variable: Any, value: Any):
        assert isinstance(variable, Hashable), \
            f"[ValueNode.add_value] Variable '{variable}' should be hashable"
        assert isinstance(value, Hashable), \
            f"[ValueNode.add_value] Value '{value}' should be hashable"
        self.variable: Any = variable
        self.value: Any = value

    def __hash__(self):
        return (self.variable, self.value).__hash__()

    def __repr__(self):
        return f"({self.variable}_{self.value})"

    def __copy__(self):
        return ValueNode(copy.deepcopy(self.variable), copy.deepcopy(self.value))

    def __eq__(self, other: Any):
        if isinstance(other, ValueNode):
            return self.variable == other.variable and self.value == other.value
        return False

    def with_replaced_value(self, new_value: Any) -> 'ValueNode':
        return ValueNode(copy.deepcopy(self.variable), new_value)


class RelationEdge:

    def __init__(self, endpoints: frozenset[ValueNode], relation: Any):
        assert len(endpoints) == 2, \
            f"[RelationEdge.add_relation] Set of endpoints to be connected should have size exactly 2, " \
            f"but got {len(endpoints)}"
        assert isinstance(relation, Hashable), \
            f"[RelationEdge.add_relation] Relation '{relation}' should be hashable"
        endpoints_list = list(endpoints)
        assert endpoints_list[0] != endpoints_list[1], \
            f"[RelationEdge.add_relation] Endpoints for relation should not be the same node: {endpoints}"
        assert endpoints_list[0].variable != endpoints_list[1].variable, \
            f"[RelationEdge.add_relation] It is impossible to connect two values belong to same variable, " \
            f"found same variable in endpoints: {endpoints}"
        self.endpoints: frozenset[ValueNode] = endpoints
        self.relation: Any = relation
        self.a: ValueNode = endpoints_list[0]
        self.b: ValueNode = endpoints_list[1]

    def __hash__(self):
        return (self.endpoints, self.relation).__hash__()

    def __repr__(self):
        se = sorted(self.endpoints, key=lambda e: str(e))
        return f"{se[0]}--{{{self.relation}}}--{se[1]}"

    def __copy__(self):
        return RelationEdge(copy.deepcopy(self.endpoints), copy.deepcopy(self.relation))

    def __eq__(self, other: Any):
        if isinstance(other, RelationEdge):
            return self.endpoints == other.endpoints and self.relation == other.relation
        return False

    def is_endpoint(self, node: ValueNode) -> bool:
        return node in self.endpoints

    def opposite_endpoint(self, node: ValueNode) -> ValueNode:
        if self.a == node:
            return self.b
        if self.b == node:
            return self.a
        raise AssertionError(
            f"[RelationEdge.opposite_endpoint] Node {node} is not endpoint of this edge: {self}")

    def with_replaced_values(self, to_replace: Dict[Any, Tuple[Any, Any]]) -> 'RelationEdge':
        return RelationEdge(
            frozenset({
                (n.with_replaced_value(to_replace[n.variable][1])
                 if n.variable in to_replace and n.value == to_replace[n.variable][0] else copy.deepcopy(n))
                for n in self.endpoints}),
            copy.deepcopy(self.relation))


class SampleBuilder:

    def __init__(self, name: Optional[str] = None, nodes: Set[ValueNode] = None, edges: Set[RelationEdge] = None):
        self._name = name
        self._nodes: Set[ValueNode] = nodes if nodes else set([])
        self._edges: Set[RelationEdge] = edges if edges else set([])

    def set_name(self, name: str):
        self._name = name
        return self

    def add_value(self, variable: Any, value: Any) -> 'SampleBuilder':
        node = ValueNode(variable, value)
        assert node not in self._nodes, \
            f"[SampleBuilder.add_value] Node {node} already added to nodes: {self._nodes}"
        assert variable not in {n.variable for n in self._nodes}, \
            f"[SampleBuilder.add_value] Variable {variable} already added. Each variable can be used only once."
        self._nodes.add(node)
        return self

    def add_relation(self, endpoints: Set[Tuple[Any, Any]], relation: Any) -> 'SampleBuilder':
        edge = RelationEdge(frozenset({ValueNode(var, val) for var, val in endpoints}), relation)
        for e in edge.endpoints:
            assert e in self._nodes, f"[SampleBuilder.add_relation] Endpoint {e} in nodes: {self._nodes}"
        assert edge not in self._edges, \
            f"[SampleBuilder.add_relation] relation {edge} is already added to edges: {self._edges}"
        self._edges.add(edge)
        return self

    def connected_nodes(self, start_node: ValueNode, traced: Set[ValueNode] = None) -> Set[ValueNode]:
        if not traced:
            traced = {start_node}
        neighbors = [e.opposite_endpoint(start_node) for e in self._edges if e.is_endpoint(start_node)]
        for neighbor in neighbors:
            if neighbor not in traced:
                traced.add(neighbor)
                traced.update(self.connected_nodes(neighbor, traced))
        return traced

    def is_connected(self) -> bool:
        if len(self._nodes) == 1 and len(self._edges) == 0:
            return True  # Single node graph
        if len(self._nodes) > 0 and self.connected_nodes(list(self._nodes)[0]) == self._nodes:
            return True  # All nodes are connected
        return False

    def build(self) -> 'SampleGraph':
        assert self.is_connected(), f"[SampleBuilder.build] Sample graph should be connected"
        return SampleGraph(frozenset(self._nodes), frozenset(self._edges), self._name)


class SampleGraph:

    def __init__(self, nodes: frozenset[ValueNode], edges: frozenset[RelationEdge], name: Optional[str]):
        assert nodes, \
            "[SampleGraph.__init__] Sample graph should have at least 1 node"
        assert len({n.variable for n in nodes}) == len(nodes), \
            f"[SampleGraph.__init__] Found duplicate variable in nodes: {nodes}"
        for edge in edges:
            assert edge.endpoints.issubset(nodes), \
                f"[SampleGraph.__init__] Edges endpoints {edge.endpoints} should be subset of nodes: {nodes}"
        self.nodes: frozenset[ValueNode] = nodes
        self.edges: frozenset[RelationEdge] = edges
        self.hash: frozenset[Any] = nodes.union({e for e in edges})
        self.name: str = name
        if not self.name:
            struct = sorted([str(e) for e in self.edges] if self.edges else [str(n) for n in self.nodes])
            self.name = "{" + '; '.join(struct) + "}"

    def __hash__(self):
        return self.hash.__hash__()

    def __repr__(self):
        return self.name

    def __copy__(self):
        return SampleGraph(copy.deepcopy(self.nodes), copy.deepcopy(self.edges), self.name)

    def __eq__(self, other: Any):
        if isinstance(other, SampleGraph):
            return self.hash == other.hash
        return False

    def text_view(self) -> str:
        if self.edges:
            return "{" + os.linesep + os.linesep.join(sorted(["    " + str(e) for e in self.edges])) + os.linesep + "}"
        else:
            return "{" + str(list(self.nodes)[0]) + "}"

    def show(self, height="1024px", width="1024px") -> None:
        net = Network(height=height, width=width)
        for node in self.nodes:
            net.add_node(str(node), label=f"{node.variable}_{node.value}")
        for edge in self.edges:
            net.add_edge(str(edge.a), str(edge.b), label=str(edge.relation))
        net.show(f"{self.name}_sample.html")

    def builder(self) -> SampleBuilder:
        return SampleBuilder(
            self.name,
            {copy.deepcopy(n) for n in self.nodes},
            {copy.deepcopy(e) for e in self.edges})

    def is_subgraph(self, other: 'SampleGraph') -> bool:
        return self.hash.issubset(other.hash)

    def contains_variable(self, variable: Any) -> bool:
        for n in self.nodes:
            if n.variable == variable:
                return True
        return False

    def value_for_variable(self, variable: Any) -> Any:
        for n in self.nodes:
            if n.variable == variable:
                return n.value
        raise AssertionError(f"[SampleGraph.value_for_variable] Variable {variable} is not in nodes: {self.nodes}")

    def with_replaced_values(self, to_replace: Dict[Any, Tuple[Any, Any]], name: Optional[str] = None) -> 'SampleGraph':
        return SampleGraph(
            frozenset({(
                n.with_replaced_value(to_replace[n.variable][1])
                if n.variable in to_replace and n.value == to_replace[n.variable][0]
                else n)
                for n in self.nodes}),
            frozenset({e.with_replaced_values(to_replace) for e in self.edges}),
            name)

    def neighboring_values(self, center: ValueNode, rel_filter: List[Any] = None) -> Dict[ValueNode, RelationEdge]:
        return {e.opposite_endpoint(center): e
                for e in self.edges
                if e.is_endpoint(center) and (not rel_filter or (e.relation in rel_filter))}

    def similarity(self, other: 'SampleGraph') -> float:
        intersect_hash = self.hash.intersection(other.hash)
        differ_hash = self.hash.symmetric_difference(other.hash)
        return len(intersect_hash) / (len(intersect_hash) + len(differ_hash))
