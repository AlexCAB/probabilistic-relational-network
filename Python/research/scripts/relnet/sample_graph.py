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

from collections import Hashable
from typing import Dict, List, Set, Tuple, Any, Optional

from pyvis.network import Network

from .relation_type import RelationType
from .variable_node import VariableNode


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
        return f"({self.a})--{{{self.relation}}}--({self.b}))"


class SampleBuilder:

    def __init__(self, name: Optional[str] = None):
        self._name = name
        self._nodes: Set[ValueNode] = set([])
        self._edges: Set[RelationEdge] = set([])

    def add_value(self, variable: Any, value: Any) -> 'SampleBuilder':
        node = ValueNode(variable, value)
        assert node not in self._nodes, \
            f"[SampleBuilder.add_value] Node {node} already added to nodes: {self._nodes}"
        self._nodes.add(node)
        return self

    def add_relation(self, endpoints: Set[(Any, Any)], relation: Any) -> 'SampleBuilder':
        edge = RelationEdge(frozenset({ValueNode(var, val) for var, val in endpoints}), relation)
        for e in edge.endpoints:
            assert e in self._nodes, f"[SampleBuilder.add_relation] Endpoint {e} in nodes: {self._nodes}"
        assert edge not in self._edges, \
            f"[SampleBuilder.add_relation] relation {edge} is already added to edges: {self._edges}"
        self._edges.add(edge)
        return self

    def build(self) -> 'SampleGraph':
        name = self._name
        if not name:
            struct = [str(e) for e in self._edges] if self._edges else [str(n) for n in self._nodes]
            name = "{" + '; '.join(struct) + "}"
        return SampleGraph(frozenset(self._nodes), frozenset(self._edges), name)


class SampleGraph:

    def __init__(self, nodes: frozenset[ValueNode], edges: frozenset[RelationEdge], name: str):
        for edge, rel in edges:
            assert edge.endpoints.issubset(nodes), \
                f"[SampleGraph.__init__] Edges endpoints {edge.endpoints} should ne subset of nodes: {nodes}"
        assert name, \
            f"[SampleGraph.__init__] The name should not be empty string"
        self.nodes: frozenset[ValueNode] = nodes
        self.edges: frozenset[RelationEdge] = edges
        self.name: str = name
        self.hash: frozenset[Any] = nodes.union({e for e in edges})

    def __repr__(self):
        return self.name

    def show(self, height="1024px", width="1024px") -> None:
        net = Network(height=height, width=width)
        for node in self.nodes:
            net.add_node(str(node), label=f"{node.variable}_{node.value}")
        for edge in self.edges:
            net.add_edge(str(edge.a), str(edge.b), label=str(edge.relation))
        net.show(f"{self.name}_sample.html")



    # TODO From here


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
            assert used_rel.issubset(provided_rel), \
                f"[SampleGraph.clone] Not all used relation are in provided, used_rel = {used_rel}, " \
                f"provided_rel = {provided_rel}"

        if variables:
            used_var = set([v.variable_id for v in self._values.values()])
            provided_var = set([v.variable_id for v in variables])
            assert used_var.issubset(provided_var), \
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

    def get_neighboring_values(
            self,
            variable_id: str,
            value_id: str,
            rel_ids_filter: List[str] = None
    ) -> List[Tuple[ValueNode, RelationEdge]]:
        """
        Search the neighbors of given node (variable_id, rel_ids_filter), which linked with one of relation type
        from rel_ids_filter list.
        :param variable_id: center node variable_id
        :param value_id: center node value_id
        :param rel_ids_filter: list of relation type IDs to select neighbors with particular set of relation,
                               if None then select roe all relations.
        :return: List[neighbor_node, relation_type_with_which_this_node_connected]
        """

        center_node_id = (variable_id, value_id)
        neighboring_values = []

        assert center_node_id in self._values, \
            f"[SampleGraph.get_neighboring_values] center_node_id = {center_node_id} is not in value " \
            f"list of this sample: {self._values.keys()}"

        for key, edge in self._edges.items():
            node_ids, rel_type_id = key
            if center_node_id in node_ids:
                if not rel_ids_filter or (rel_type_id in rel_ids_filter):
                    found_node = edge.node_b if edge.node_a.get_id() == center_node_id else edge.node_a
                    assert found_node.get_id() in self._values, \
                        f"[SampleGraph.get_neighboring_values] found_node = {center_node_id} is not in value " \
                        f"list of this sample: {self._values.keys()}"
                    assert found_node.get_id() != center_node_id, \
                        f"[SampleGraph.get_neighboring_values] found_node = {found_node.get_id()} can't be equal " \
                        f"center node, it look like bug "
                    neighboring_values.append((found_node, edge))

        neighboring_values_ids = [nv.get_id() for nv, _ in neighboring_values]
        assert len(set(neighboring_values_ids)) == len(neighboring_values), \
            f"[SampleGraph.get_neighboring_values] found neighboring values have duplication, " \
            f"this should not happens since sample is not multi-graph, this is a bug, " \
            f"neighboring_values_ids = {neighboring_values_ids}"

        return neighboring_values

    def get_similarity(self, other: 'SampleGraph') -> float:
        """
        Calculate how similar is this sample to other sample
        :param other: other sample
        :return: 0 - completely different, 1 - completely match
        """
        self_hash = self.get_hash()
        other_hash = other.get_hash()
        intersect_hash = self_hash.intersection(other_hash)
        differ_hash = self_hash.symmetric_difference(other_hash)

        return len(intersect_hash) / (len(intersect_hash) + len(differ_hash))
