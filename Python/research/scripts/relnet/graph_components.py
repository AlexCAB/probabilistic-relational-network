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
created: 2021-11-09
"""

from abc import abstractmethod, ABC
from typing import Dict, Set, Any, Tuple


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

    def opposite_endpoint(self, node: ValueNode) -> ValueNode:
        """
        Will return node from opposite endpoint against given node.
        :param node: one of endpoint nodes
        :return: opposite endpoint node or None in case given is not one of endpoint
        """
        if self.a == node:
            return self.b
        if self.b == node:
            return self.a
        raise AssertionError(f"[ValueNode.opposite_endpoint] Value node {node} is not one of endpoints")


class DirectedRelation:
    """
    Immutable relation which encode directionality beside relation type itself
    """

    def __init__(self, source_variable: Any, target_variable: Any, relation: Any):
        self.source_variable: Any = source_variable
        self.target_variable: Any = target_variable
        self.relation: Any = relation

    def __hash__(self):
        return (self.source_variable, self.target_variable, self.relation).__hash__()

    def __repr__(self):
        return f"{self.target_variable}[{self.source_variable}->{self.relation}]"

    def __copy__(self):
        raise AssertionError(
            "[DirectedRelation.__copy__] Directed relation should not be copied")

    def __eq__(self, other: Any):
        if isinstance(other, DirectedRelation):
            return self.source_variable == other.source_variable and self.target_variable == other.target_variable\
                   and self.relation == other.relation
        return False


class SampleGraphComponentsProvider(ABC):
    """
    Interface if sample graph components provider which construct nodes and edges
    """

    @abstractmethod
    def variables(self) -> frozenset[Tuple[Any, frozenset[Any]]]:
        raise NotImplementedError

    @abstractmethod
    def relations(self) -> frozenset[Any]:
        raise NotImplementedError

    @abstractmethod
    def get_node(self, variable: Any, value: Any) -> ValueNode:
        raise NotImplementedError

    @abstractmethod
    def get_edge(self, endpoints: frozenset[ValueNode], relation: Any) -> RelationEdge:
        raise NotImplementedError


class BuilderComponentsProvider(SampleGraphComponentsProvider):
    """
    Implementation of sample graph components provider
    """

    def __init__(self, variables: Dict[Any, Set[Any]], relations: Set[Any]):
        assert variables, \
            f"[BuilderComponentsProvider.__init__] Set of variables should not be empty."
        for var, values in variables.items():
            assert values, \
                f"[BuilderComponentsProvider.__init__] Set of variable values should not be empty, found for {var}"
        assert relations, \
            f"[BuilderComponentsProvider.__init__] Set of relations should not be empty."

        self._variables: Dict[Any, Set[Any]] = variables
        self._relations: Set[Any] = relations
        self.nodes: Dict[Tuple[Any, Any], ValueNode] = {}
        self.edges: Dict[Tuple[frozenset[ValueNode], Any], RelationEdge] = {}

    def variables(self) -> frozenset[Tuple[Any, frozenset[Any]]]:
        return frozenset({(k, frozenset(v)) for k, v in self._variables.items()})

    def relations(self) -> frozenset[Any]:
        return frozenset(self._relations)

    def get_node(self, variable: Any, value: Any) -> ValueNode:
        assert variable in self._variables, \
            f"[BuilderComponentsProvider.get_node] Unknown variable {variable}"
        assert value in self._variables[variable], \
            f"[BuilderComponentsProvider.get_node] Unknown value {value} of variable {variable}"

        if (variable, value) in self.nodes:
            return self.nodes[(variable, value)]
        else:
            node = ValueNode(variable, value)
            self.nodes[(variable, value)] = node
            return node

    def get_edge(self, endpoints: frozenset[ValueNode], relation: Any) -> RelationEdge:
        assert endpoints.issubset(self.nodes.values()), \
            f"[BuilderComponentsProvider.get_edge] Endpoints nodes should be created first, " \
            f"got {endpoints} where nodes {self.nodes}"
        assert (relation.relation if isinstance(relation, DirectedRelation) else relation) in self._relations, \
            f"[BuilderComponentsProvider.get_node] Unknown relation {relation}"

        if isinstance(relation, DirectedRelation):
            variables = {ep.variable for ep in endpoints}
            assert relation.source_variable in variables, \
                f"[MockSampleGraphComponentsProvider.get_node] Unknown relation source " \
                f"variable {relation.source_variable}"
            assert relation.target_variable in variables, \
                f"[MockSampleGraphComponentsProvider.get_node] Unknown relation target " \
                f"variable {relation.target_variable}"

        if (endpoints, relation) in self.edges:
            return self.edges[(endpoints, relation)]
        else:
            edge = RelationEdge(endpoints, relation)
            self.edges[(endpoints, relation)] = edge
            return edge
