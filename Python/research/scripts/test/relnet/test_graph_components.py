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

import unittest
from copy import copy
from typing import Any, Dict, Set, Tuple

from scripts.relnet.graph_components import BuilderComponentsProvider
from scripts.relnet.sample_graph import ValueNode, RelationEdge, SampleGraphComponentsProvider, DirectedRelation


class TestValueNode(unittest.TestCase):

    a_1 = ValueNode("a", "1")

    def test_init(self):
        self.assertEqual(self.a_1.variable, "a")
        self.assertEqual(self.a_1.value, "1")
        self.assertEqual(self.a_1.string_id, "a_1")

    def test_hash(self):
        self.assertEqual(self.a_1.__hash__(), ("a", "1").__hash__())

    def test_repr(self):
        self.assertEqual(self.a_1.__repr__(), "(a_1)")

    def test_copy(self):
        with self.assertRaises(AssertionError):
            copy(self.a_1)

    def test_eq(self):
        a_1_1 = ValueNode("a", "1")
        a_1_2 = ValueNode("a", "1")
        self.assertNotEqual(id(a_1_1), id(a_1_2))
        self.assertEqual(a_1_1, a_1_2)

    def test_var_val(self):
        self.assertEqual(self.a_1.var_val(), ("a", "1"))


class TestRelationEdge(unittest.TestCase):

    a_1 = ValueNode("a", "1")
    b_1 = ValueNode("b", "1")
    b_2 = ValueNode("b", "2")
    e_1 = RelationEdge(frozenset({a_1, b_1}), "r")

    def test_init(self):
        self.assertEqual(self.e_1.endpoints, frozenset({self.a_1, self.b_1}))
        self.assertEqual(self.e_1.relation, "r")
        self.assertTrue(self.e_1.a in {self.a_1, self.b_1})
        self.assertTrue(self.e_1.b in {self.a_1, self.b_1})
        self.assertNotEqual(self.e_1.a, self.e_1.b)

    def test_hash(self):
        self.assertEqual(self.e_1.__hash__(), (frozenset({self.a_1, self.b_1}), "r").__hash__())

    def test_repr(self):
        self.assertEqual(self.e_1.__repr__(), "(a_1)--{r}--(b_1)")

    def test_copy(self):
        with self.assertRaises(AssertionError):
            copy(self.e_1)

    def test_eq(self):
        e_1_1 = RelationEdge(frozenset({self.a_1, self.b_1}), "r")
        e_1_2 = RelationEdge(frozenset({self.b_1, self.a_1}), "r")
        self.assertNotEqual(id(e_1_1), id(e_1_2))
        self.assertEqual(e_1_1, e_1_2)

    def test_is_endpoint(self):
        self.assertTrue(self.e_1.is_endpoint(self.a_1))
        self.assertFalse(self.e_1.is_endpoint(self.b_2))

    def test_opposite_endpoint(self):
        self.assertEqual(self.e_1.opposite_endpoint(self.a_1), self.b_1)
        self.assertEqual(self.e_1.opposite_endpoint(self.b_1), self.a_1)
        with self.assertRaises(AssertionError):
            self.e_1.opposite_endpoint(self.b_2)


class TestDirectedRelation(unittest.TestCase):

    dr_1 = DirectedRelation("a", "b", "r")

    def test_init(self):

        self.assertEqual(self.dr_1.source_variable, "a")
        self.assertEqual(self.dr_1.target_variable, "b")
        self.assertEqual(self.dr_1.relation, "r")

    def test_hash(self):
        self.assertEqual(self.dr_1.__hash__(), ("a", "b", "r").__hash__())

    def test_repr(self):
        self.assertEqual(self.dr_1.__repr__(), "b[a->r]")

    def test_copy(self):
        with self.assertRaises(AssertionError):
            copy(self.dr_1)

    def test_eq(self):
        dr_2 = DirectedRelation("a", "b", "r")
        self.assertNotEqual(id(self.dr_1), id(dr_2))
        self.assertEqual(self.dr_1, dr_2)


class MockSampleGraphComponentsProvider(SampleGraphComponentsProvider):

    def __init__(self, variables: Dict[Any, Set[Any]], relations: Set[Any]):
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
            f"[MockSampleGraphComponentsProvider.get_node] Unknown variable {variable}"
        assert value in self._variables[variable], \
            f"[MockSampleGraphComponentsProvider.get_node] Unknown value {value} of variable {variable}"

        if (variable, value) in self.nodes:
            return self.nodes[(variable, value)]
        else:
            node = ValueNode(variable, value)
            self.nodes[(variable, value)] = node
            return node

    def get_edge(self, endpoints: frozenset[ValueNode], relation: Any) -> RelationEdge:
        assert endpoints.issubset(self.nodes.values()), \
            f"[MockSampleGraphComponentsProvider.get_edge] Endpoints nodes should be created first, " \
            f"got {endpoints} where nodes {self.nodes}"
        assert (relation.relation if isinstance(relation, DirectedRelation) else relation) in self._relations, \
            f"[MockSampleGraphComponentsProvider.get_node] Unknown relation {relation}"

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


class TestBuilderComponentsProvider(unittest.TestCase):

    b_1 = BuilderComponentsProvider({"a": {"1", "2"}, "b": {"2", "3"}}, {"r", "s"})

    def test_init(self):
        b = BuilderComponentsProvider({"a": {"1", "2"}}, {"r"})

        self.assertEqual(b.variables(), frozenset({("a", frozenset({"1", "2"}))}))
        self.assertEqual(b.relations(), frozenset({"r"}))
        self.assertEqual(b.nodes, {})
        self.assertEqual(b.edges, {})

        with self.assertRaises(AssertionError):  # Empty set of variables
            BuilderComponentsProvider({}, {"r"})
        with self.assertRaises(AssertionError):  # Empty variable values
            BuilderComponentsProvider({"a": set({})}, {"r"})
        with self.assertRaises(AssertionError):  # Empty set of relations
            BuilderComponentsProvider({"a": {"1", "2"}}, set({}))

    def test_variables(self):
        self.assertEqual(
            self.b_1.variables(),
            frozenset({("a", frozenset({"1", "2"})), ("b", frozenset({"2", "3"}))}))

    def test_relations(self):
        self.assertEqual(self.b_1.relations(), frozenset({"r", "s"}))

    def test_get_node(self):
        n_1 = self.b_1.get_node("a", "1")
        self.assertEqual(n_1.variable, "a")
        self.assertEqual(n_1.value, "1")

        n_2 = self.b_1.get_node("a", "1")
        self.assertEqual(n_2.variable, "a")
        self.assertEqual(n_2.value, "1")
        self.assertEqual(id(n_1), id(n_2))

        n_3 = self.b_1.get_node("a", "2")
        self.assertEqual(n_3.variable, "a")
        self.assertEqual(n_3.value, "2")
        self.assertNotEqual(id(n_1), id(n_3))

        with self.assertRaises(AssertionError):  # Unknown variable
            self.b_1.get_node("unknown_variable", "1")
        with self.assertRaises(AssertionError):  # Unknown value
            self.b_1.get_node("a", "unknown_value")

    def test_get_edge(self):
        n_1 = self.b_1.get_node("a", "1")
        n_2 = self.b_1.get_node("b", "2")

        e_1 = self.b_1.get_edge(frozenset({n_1, n_2}), "r")
        self.assertEqual(e_1.endpoints, frozenset({n_1, n_2}))
        self.assertEqual(e_1.relation, "r")

        e_2 = self.b_1.get_edge(frozenset({n_1, n_2}), "r")
        self.assertEqual(e_2.endpoints, frozenset({n_1, n_2}))
        self.assertEqual(e_2.relation, "r")
        self.assertEqual(id(e_1), id(e_2))

        e_3 = self.b_1.get_edge(frozenset({n_1, n_2}), "s")
        self.assertEqual(e_3.endpoints, frozenset({n_1, n_2}))
        self.assertEqual(e_3.relation, "s")
        self.assertNotEqual(id(e_1), id(e_3))

        n_3 = self.b_1.get_node("b", "3")

        e_4 = self.b_1.get_edge(frozenset({n_1, n_3}), "r")
        self.assertEqual(e_4.endpoints, frozenset({n_1, n_3}))
        self.assertEqual(e_4.relation, "r")
        self.assertNotEqual(id(e_1), id(e_4))

        dr_1 = DirectedRelation("a", "b", "r")
        e_5 = self.b_1.get_edge(frozenset({n_1, n_2}), dr_1)
        self.assertEqual(e_5.endpoints, frozenset({n_1, n_2}))
        self.assertEqual(e_5.relation, dr_1)
        self.assertNotEqual(id(e_1), id(e_5))

        with self.assertRaises(AssertionError):  # Unknown endpoint node
            self.b_1.get_edge(frozenset({n_1, ValueNode("a", "2")}), "r")
        with self.assertRaises(AssertionError):  # Unknown relation
            self.b_1.get_edge(frozenset({n_1, n_2}), "unknown_relation")
        with self.assertRaises(AssertionError):  # Unknown directed relation
            self.b_1.get_edge(frozenset({n_1, n_2}),  DirectedRelation("a", "b", "unknown_relation"))
        with self.assertRaises(AssertionError):  # Unknown directed source variable
            self.b_1.get_edge(frozenset({n_1, n_2}),  DirectedRelation("unknown_variable", "b", "r"))
        with self.assertRaises(AssertionError):  # Unknown directed target variable
            self.b_1.get_edge(frozenset({n_1, n_2}),  DirectedRelation("a", "unknown_variable", "r"))


if __name__ == '__main__':
    unittest.main()
