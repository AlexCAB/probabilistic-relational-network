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

from abc import abstractmethod, ABC
from collections import defaultdict
from typing import Dict, List, Set, Any, Optional, Tuple, Union

from pyvis.network import Network


class ValueNode:
    """
    Immutable value node of sample graph, wrapping provided variable and its value
    """

    def __init__(self, variable: Any, value: Any):
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


class RelationEdge:
    """
    Immutable relation edge of sample graph, wrapping two endpoints nodes and provided relation
    """

    def __init__(self, endpoints: frozenset[ValueNode], relation: Any):
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

    @staticmethod
    def is_edges_connected(edges: frozenset[Tuple[frozenset[Tuple[Any, Any]], Any]]) -> bool:
        """
        Will to trace given edges to ensure that the graph they formed are connected
        :param edges: Set[(endpoints, relation)]
        :return: True if graph connected and False otherwise
        """
        tracing_map = defaultdict(set)
        traced: Set[(Any, Any)] = set({})

        for endpoints in [list(endpoints) for endpoints, _ in edges]:
            assert len(endpoints) == 2, \
                f"[SampleGraphBuilder.is_edges_connected] expect endpoints have exactly 2 node, got {endpoints}"
            tracing_map[endpoints[0]].add(endpoints[1])
            tracing_map[endpoints[1]].add(endpoints[0])

        def trace(start_node: (Any, Any)):
            if start_node not in traced:
                traced.add(start_node)
                for next_node in tracing_map[start_node]:
                    trace(next_node)

        trace(next(iter(tracing_map.keys())))
        return len(tracing_map) == len(traced)

    @staticmethod
    def validate_endpoints(endpoints: frozenset[Tuple[Any, Any]]) -> None:
        """
        Will validate given endpoints and in case invalid will raise AssertionError
        :param endpoints: frozenset[(variable, value))])
        :return: None if all OK or raise AssertionError
        """
        assert len(endpoints) == 2, \
            f"[SampleGraphBuilder.validate_endpoints] Exactly 2 endpoint should be passed, got {len(endpoints)}"
        assert len({var for var, _ in endpoints}) == 2, \
            f"[SampleGraphBuilder.validate_endpoints] Endpoints can't have same variable, got {endpoints}"

    def build_from_edges(
            self,
            edges: frozenset[Tuple[frozenset[Tuple[Any, Any]], Any]],
            validate_connectivity: bool = True
    ) -> 'SampleGraph':
        """
        Creates sample graph from set of edges.
        :param edges: frozenset[(endpoints, relation)]
        :param validate_connectivity: if False then connectivity will not be checked,
               use it if is_edges_connected was called first
        :return: built sample graph
        """
        if validate_connectivity:
            assert self.is_edges_connected(edges), \
                f"[SampleGraphBuilder.build_from_edges] Passed edges are not form connected graph, edges: {edges}"

        for endpoints, relation in edges:
            self.validate_endpoints(endpoints)
            nodes = {self._components_provider.get_node(var, val) for var, val in endpoints}
            edge = self._components_provider.get_edge(frozenset(nodes), relation)
            self._edges.add(edge)
            self._nodes.update(nodes)

        return self.build()

    def add_relation(self, endpoints: Set[Tuple[Any, Any]], relation: Any) -> 'SampleGraphBuilder':
        """
        To add relation edge in to sample graph, with validation of graph connectivity
        :param endpoints: Exactly 2 nodes which will connected with relation edge
        :param relation: relation type
        :return: self
        """
        self.validate_endpoints(frozenset(endpoints))
        nodes = {self._components_provider.get_node(var, val) for var, val in endpoints}
        edge = self._components_provider.get_edge(frozenset(nodes), relation)

        assert not nodes.isdisjoint(self._nodes) or not self._nodes, \
            f"[SampleGraphBuilder.add_relation] One or both endpoint should be previously added node, " \
            f"to keep graph connected, got nodes {nodes} where previously added {self._nodes}"
        assert edge not in self._edges, \
            f"[SampleGraphBuilder.add_relation] Edge {edge} was added previously"

        self._edges.add(edge)
        self._nodes.update(nodes)
        return self

    def build(self) -> 'SampleGraph':
        """
        To build composed sample graph
        :return: composed sample graph
        """
        assert self._nodes, \
            "[SampleGraphBuilder.build] Sample graph should have at least 1 node"

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

    def is_compatible(self, other_components_provider: SampleGraphComponentsProvider) -> bool:
        """
        Validate if this sample graph compatible to other components provider
        :param other_components_provider: other SampleGraphComponentsProvider
        :return: True if compatible, False otherwise
        """
        return id(self._components_provider) == id(other_components_provider)

    def text_view(self) -> str:
        """
        Create textual representation of this sample graph to print in terminal
        :return: string representation of this sample
        """
        if self.edges:
            return "{" + "; ".join(sorted([str(e) for e in self.edges])) + "}"
        else:
            return "{" + str(list(self.nodes)[0]) + "}"

    def edges_set_view(self) -> Union[frozenset[Tuple[frozenset[Tuple[Any, Any]], Any]], Tuple[Any, Any]]:
        """
        Build and return this sample graph in form of simple edges (same format as used in
        SampleGraphBuilder.build_from_edges). I case graph is single node will return just this node
        :return: frozenset[Tuple[frozenset[Tuple[variable, value]], relation] or for single node Tuple[variable, value]
        """
        if self.edges:
            return frozenset({
                (frozenset({(n.variable, n.value) for n in e.endpoints}), e.relation) for e in self.edges})
        else:
            single_node = list(self.nodes)[0]
            return single_node.variable, single_node.value

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
