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

import os
from abc import abstractmethod, ABC
from typing import Dict, List, Set, Any, Optional, Tuple

from pyvis.network import Network


class ValueNode:
    """
    Immutable value node of sample graph, wrapping provided variable and its value
    """

    def __init__(self, variable: Any, value: Any):

        # TODO: Move to SampleGraphComponentsProvider
        # assert isinstance(variable, Hashable), \
        #     f"[ValueNode.add_value] Variable '{variable}' should be hashable"
        # assert isinstance(value, Hashable), \
        #     f"[ValueNode.add_value] Value '{value}' should be hashable"

        self.variable: Any = variable
        self.value: Any = value
        self.string_id: str = f"{variable}_{value}"

    def __hash__(self):
        return (self.variable, self.value).__hash__()

    def __repr__(self):
        return f"({self.string_id})"

    def __copy__(self):
        raise AssertionError(
            "[ValueNode.__copy__] Value node should not be copied, "
            "use SampleGraphComponentsProvider to get cached instance")

    def __eq__(self, other: Any):
        if isinstance(other, ValueNode):
            return self.variable == other.variable and self.value == other.value
        return False

    # def with_replaced_value(self, new_value: Any) -> 'ValueNode':
    #     """
    #     Creates new instance of ValueNode with replace self.value on new_value
    #     :param new_value:
    #     :return: new ValueNode with updated value
    #     """
    #     return ValueNode(copy.deepcopy(self.variable), new_value)


class RelationEdge:
    """
    Immutable relation edge of sample graph, wrapping two endpoints nodes and provided relation
    """

    def __init__(self, endpoints: frozenset[ValueNode], relation: Any):

        # TODO: Move to SampleGraphComponentsProvider
        # endpoints_list = list(endpoints)
        # assert len(endpoints) == 2, \
        #     f"[RelationEdge.add_relation] Set of endpoints to be connected should have size exactly 2, " \
        #     f"but got {len(endpoints)}"
        # assert isinstance(relation, Hashable), \
        #     f"[RelationEdge.add_relation] Relation '{relation}' should be hashable"
        # assert endpoints_list[0] != endpoints_list[1], \
        #     f"[RelationEdge.add_relation] Endpoints for relation should not be the same node: {endpoints}"
        # assert endpoints_list[0].variable != endpoints_list[1].variable, \
        #     f"[RelationEdge.add_relation] It is impossible to connect two values belong to same variable, " \
        #     f"found same variable in endpoints: {endpoints}"

        endpoints_list = list(endpoints)
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
        raise AssertionError(
            "[RelationEdge.__copy__] Relation edge should not be copied, "
            "use SampleGraphComponentsProvider to get cached instance")

    def __eq__(self, other: Any):
        if isinstance(other, RelationEdge):
            return self.endpoints == other.endpoints and self.relation == other.relation
        return False

    def is_endpoint(self, node: ValueNode) -> bool:
        """
        To check if given node is one of edge endpoints
        :param node: node to check on
        :return: True if node is endpoint
        """
        return node in self.endpoints

    def opposite_endpoint(self, node: ValueNode) -> Optional[ValueNode]:
        """
        Will return node from opposite endpoint against given node.
        :param node: one of endpoint nodes
        :return: opposite endpoint node or None in case given is not one of endpoint
        """
        if self.a == node:
            return self.b
        if self.b == node:
            return self.a
        return None

    # def with_replaced_values(self, to_replace: Dict[Any, Any]) -> 'RelationEdge':
    #     """
    #     Will return copy of this edge with replaced values in endpoint nodes
    #     :param to_replace: Dict[variable, new_variable_value]
    #     :return: copy of RelationEdge with
    #     """
    #     return RelationEdge(
    #         frozenset({
    #             (n.with_replaced_value(to_replace[n.variable]) if n.variable in to_replace else copy.deepcopy(n))
    #             for n in self.endpoints}),
    #         copy.deepcopy(self.relation))


class SampleGraphComponentsProvider(ABC):

    @abstractmethod
    def get_node(self, variable: Any, value: Any) -> ValueNode:
        pass

    @abstractmethod
    def get_edge(self, endpoints: frozenset[ValueNode], relation: Any) -> RelationEdge:
        pass


class SampleGraphBuilder:
    """
    Mutable builder for composing of the sample graphs
    """

    def __init__(
            self,
            components_provider: SampleGraphComponentsProvider,
            name: Optional[str] = None,
            nodes: Set[ValueNode] = None,
            edges: Set[RelationEdge] = None
    ):
        self._components_provider: SampleGraphComponentsProvider = components_provider
        self._name: Optional[str] = name
        self._nodes: Set[ValueNode] = nodes if nodes else set([])
        self._edges: Set[RelationEdge] = edges if edges else set([])
        # self._tracing_map: Dict[ValueNode, Set[ValueNode]] = {
        #     n: {e.opposite_endpoint(n) for e in self._edges if e.is_endpoint(n)} for n in self._nodes}

    def __copy__(self):
        return SampleGraphBuilder(self._components_provider, self._name, self._nodes, self._edges)

    def set_name(self, name: Optional[str]):
        """
        Update sample graphs name with given
        :param name: new name
        :return: self
        """
        self._name = name
        return self

    def build_single_node(self, variable: Any, value: Any) -> 'SampleGraph':
        """
        Will build sample graph which contains single node with given variable and value
        :param variable: node variable
        :param value: node value
        :return: single node sample graph
        """
        return SampleGraph(
            self._components_provider,
            frozenset({self._components_provider.get_node(variable, value)}),
            frozenset({}),
            self._name)

    # def add_value(self, variable: Any, value: Any) -> 'SampleGraphBuilder':
    #     node = ValueNode(variable, value)
    #
    #     assert node not in self._nodes, \
    #         f"[SampleGraphBuilder.add_value] Node {node} already added to nodes: {self._nodes}"
    #     assert variable not in {n.variable for n in self._nodes}, \
    #         f"[SampleGraphBuilder.add_value] Variable {variable} already added. Each variable can be used only once."
    #
    #     self._tracing_map[node] = set({})
    #     self._nodes.add(node)
    #     return self

    def add_relation(self, endpoints: Set[Tuple[Any, Any]], relation: Any) -> 'SampleGraphBuilder':
        """
        To add relation edge in to sample graph, with validation of graph connectivity
        :param endpoints: Exactly 2 nodes which will connected with relation edge
        :param relation: relation type
        :return: self
        """
        assert len(endpoints) == 2, \
            f"[SampleGraphBuilder.add_relation] Exactly 2 endpoint should be passed, got {len(endpoints)}"
        assert len({var for var, _ in endpoints}) == 2, \
            f"[SampleGraphBuilder.add_relation] Endpoints can't have same variable, got {endpoints}"

        nodes = {self._components_provider.get_node(var, val) for var, val in endpoints}

        assert not nodes.isdisjoint(self._nodes) or not self._nodes, \
            f"[SampleGraphBuilder.add_relation] One or both endpoint should be previously added node, " \
            f"to keep graph connected, got nodes {nodes} where previously added {self._nodes}"

        edge = self._components_provider.get_edge(frozenset(nodes), relation)

        assert edge not in self._edges, \
            f"[SampleGraphBuilder.add_relation] Edge {edge} was added previously"

        self._edges.add(edge)
        self._nodes.update(nodes)
        return self

    # def connected_nodes(self, start_node: ValueNode, traced: Set[ValueNode] = None) -> Set[ValueNode]:
    #     if not traced:
    #         traced = {start_node}
    #
    #     neighbors = self._tracing_map[start_node]
    #
    #     for neighbor in neighbors:
    #         if neighbor not in traced:
    #             traced.add(neighbor)
    #             traced.update(self.connected_nodes(neighbor, traced))
    #     return traced
    #
    # def is_connected(self) -> bool:
    #     if len(self._nodes) == 1 and len(self._edges) == 0:
    #         return True  # Single node graph
    #     if len(self._nodes) > 0 and self.connected_nodes(list(self._nodes)[0]) == self._nodes:
    #         return True  # All nodes are connected
    #     return False

    def build(self) -> 'SampleGraph':
        """
        To build composed sample graph
        :return: composed sample graph
        """
        return SampleGraph(self._components_provider, frozenset(self._nodes), frozenset(self._edges), self._name)


class SampleGraph:
    """
    Immutable sample graph
    """

    def __init__(
            self,
            components_provider: SampleGraphComponentsProvider,
            nodes: frozenset[ValueNode],
            edges: frozenset[RelationEdge],
            name: Optional[str]
    ):
        self.nodes: frozenset[ValueNode] = nodes
        self.edges: frozenset[RelationEdge] = edges
        self.hash: frozenset[Any] = nodes.union({e for e in edges})
        self.name: str = name if name else (
                "{" + '; '.join(sorted([str(e) for e in self.edges] if self.edges else
                                       [str(n) for n in self.nodes])) + "}")
        self._components_provider: SampleGraphComponentsProvider = components_provider

    def __hash__(self):
        return self.hash.__hash__()

    def __repr__(self):
        return self.name

    def __copy__(self):
        raise AssertionError(
            "[RelationEdge.__copy__] Sample graph should not be copied, "
            "use one of transformation method to get new instance")

    def __eq__(self, other: Any):
        if isinstance(other, SampleGraph):
            return self.hash == other.hash
        return False

    def text_view(self) -> str:
        """
        Create textual representation of this sample graph to print in terminal
        :return: string representation of this sample
        """
        if self.edges:
            return "{" + os.linesep + os.linesep.join(sorted(["    " + str(e) for e in self.edges])) + os.linesep + "}"
        else:
            return "{" + str(list(self.nodes)[0]) + "}"

    def show(self, height="1024px", width="1024px") -> None:
        """
        Use pyvis.network to visualize this sample graph
        :param height: screen height
        :param width: screen width
        :return: None
        """
        net = Network(height=height, width=width)

        for node in self.nodes:
            net.add_node(node.string_id, label=node.string_id)
        for edge in self.edges:
            net.add_edge(edge.a.string_id, edge.b.string_id, label=str(edge.relation))

        net.show(f"{self.name}_sample.html")

    def builder(self) -> SampleGraphBuilder:
        """
        Creates SampleGraphBuilder which will contain this graph edges and nodes
        :return: created SampleGraphBuilder
        """
        return SampleGraphBuilder(
            self._components_provider,
            self.name,
            {n for n in self.nodes},
            {e for e in self.edges})

    def is_subgraph(self, other: 'SampleGraph') -> bool:
        """
        Check if other sample graph is subgraph of this
        :param other: sample graph to check with
        :return: True if  other sample graph is subgraph, False otherwise
        """
        return self.hash.issubset(other.hash)

    def contains_variable(self, variable: Any) -> bool:
        """
        Check if this graph have value node of given variable
        :param variable: variable to check with
        :return: True if have value node if given variable, False otherwise
        """
        for n in self.nodes:
            if n.variable == variable:
                return True
        return False

    def value_for_variable(self, variable: Any) -> Optional[Any]:
        """
        Will return value of given variable if variable in this sample graph
        :param variable: variable to search value of.
        :return: Found value or None if variable value is not in this sample
        """
        for n in self.nodes:
            if n.variable == variable:
                return n.value
        return None

    def transform_with_replaced_values(self, to_replace: Dict[Any, Any], name: Optional[str] = None) -> 'SampleGraph':
        """
        Will create new instance of this sample graph with replacement of value for given variables,
        if no values was replaced will return this instance of sample graph
        :param to_replace: Dict[variable, new_variable_value]
        :param name: name for new sample graph, if None will generated from structure
        :return: sample graph with replaced values
        """
        node_provider = self._components_provider.get_node
        edge_provider = self._components_provider.get_edge

        def transform_nodes(nodes: frozenset[ValueNode]) -> frozenset[ValueNode]:
            return frozenset({
                (node_provider(node.variable, to_replace[node.variable]) if node.variable in to_replace else node)
                for node in nodes})

        def transform_edges(edges: frozenset[RelationEdge]) -> frozenset[RelationEdge]:
            return frozenset({
                (edge_provider(transform_nodes(edge.endpoints), edge.relation)
                 if not {e.variable for e in edge.endpoints}.isdisjoint(to_replace.keys()) else edge)
                for edge in edges})

        transformed_nodes, transformed_edges = transform_nodes(self.nodes), transform_edges(self.edges)

        return self if (transformed_nodes == self.nodes and transformed_edges == self.edges) else \
            SampleGraph(self._components_provider, transformed_nodes, transformed_edges, name)

    def neighboring_values(
            self,
            center: ValueNode,
            relation_filter: List[Any] = None
    ) -> Dict[ValueNode, RelationEdge]:
        """
        Search the neighbors of given  center node, which linked with one of relation
        from relation_filter list.
        :param center: center node
        :param relation_filter: list of relations to select neighbors with particular relation,
                                if None then select all neighbors.
        :return: List[neighbor_node, relation_edge_with_which_this_node_connected_to_center_node]
        """
        return {e.opposite_endpoint(center): e
                for e in self.edges
                if e.is_endpoint(center) and (not relation_filter or (e.relation in relation_filter))}

    def similarity(self, other: 'SampleGraph') -> float:
        """
        Calculate how similar is this sample to other sample
        :param other: other sample
        :return: 0 - completely different, 1 - completely match
        """
        intersect_hash = self.hash.intersection(other.hash)
        differ_hash = self.hash.symmetric_difference(other.hash)
        return len(intersect_hash) / (len(intersect_hash) + len(differ_hash))
