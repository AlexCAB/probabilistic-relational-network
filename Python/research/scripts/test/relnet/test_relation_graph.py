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
created: 2021-10-26
"""

import unittest

from scripts.relnet.relation_graph import BuilderComponentsProvider, RelationGraphBuilder
from scripts.relnet.sample_graph import ValueNode, SampleGraphBuilder


class TestBuilderComponentsProvider(unittest.TestCase):

    b_1 = BuilderComponentsProvider({"a": {"1", "2"}, "b": {"2", "3"}}, {"r", "s"})

    def test_init(self):
        b = BuilderComponentsProvider({"a": {"1", "2"}}, {"r"})

        self.assertEqual(b.variables, {"a": {"1", "2"}})
        self.assertEqual(b.nodes, {})
        self.assertEqual(b.edges, {})

        with self.assertRaises(AssertionError):  # Empty set of variables
            BuilderComponentsProvider({}, {"r"})
        with self.assertRaises(AssertionError):  # Empty variable values
            BuilderComponentsProvider({"a": set({})}, {"r"})
        with self.assertRaises(AssertionError):  # Empty set of relations
            BuilderComponentsProvider({"a": {"1", "2"}}, set({}))

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

        with self.assertRaises(AssertionError):  # Unknown endpoint node
            self.b_1.get_edge(frozenset({n_1, ValueNode("a", "2")}), "r")
        with self.assertRaises(AssertionError):  # Unknown relation
            self.b_1.get_edge(frozenset({n_1, n_2}), "unknown_relation")


class TestRelationGraphBuilder(unittest.TestCase):

    bcp = BuilderComponentsProvider({"a": {"1", "2"}, "b": {"2", "3"}}, {"r", "s"})
    b_1 = RelationGraphBuilder(bcp.variables, bcp.relations, "b_1", {}, bcp)
    o_1 = SampleGraphBuilder(bcp).set_name("o_1").build_single_node("a", "1")
    o_2 = SampleGraphBuilder(bcp).set_name("o_2").build_single_node("a", "2")

    def test_init(self):
        b_1 = RelationGraphBuilder(self.bcp.variables, self.bcp.relations, "b_1", {self.o_1: 1}, self.bcp)
        g_1 = b_1.build()
        self.assertEqual(
            g_1.variables,
            frozenset({(var, frozenset(values)) for var, values in self.bcp.variables.items()}))
        self.assertEqual(g_1.relations, frozenset(self.bcp.relations))
        self.assertEqual(g_1.name, "b_1")
        self.assertEqual(g_1.number_of_outcomes, 1)

        b_2 = RelationGraphBuilder({"a": {"1", "2"}}, {"r"})
        b_2.add_outcome(b_2.sample_builder().build_single_node("a", "2"))
        g_2 = b_2.build()
        self.assertEqual(g_2.variables, frozenset({("a", frozenset({"1", "2"}))}))
        self.assertEqual(g_2.relations,  frozenset({"r"}))
        self.assertEqual(g_2.name, "relation_graph_with_1_outcomes")
        self.assertEqual(g_2.number_of_outcomes, 1)

    def test_next_id(self):
        b_1 = RelationGraphBuilder({"a": {"1"}}, {"r"})
        self.assertEqual(b_1.next_id(), 1)
        self.assertEqual(b_1.next_id(), 2)
        self.assertEqual(b_1.next_id(), 3)

    def test_add_outcome(self):
        b_1 = RelationGraphBuilder(self.bcp.variables, self.bcp.relations, "b_1", {}, self.bcp)

        b_1.add_outcome(self.o_1)
        self.assertEqual(b_1.build().outcomes(), frozenset({(self.o_1, 1)}))

        b_1.add_outcome(self.o_1)
        self.assertEqual(b_1.build().outcomes(), frozenset({(self.o_1, 2)}))

        b_1.add_outcome(self.o_2)
        self.assertEqual(b_1.build().outcomes(), frozenset({(self.o_1, 2), (self.o_2, 1)}))

        with self.assertRaises(AssertionError):  # Not compatible with this relation graph
            b_2 = RelationGraphBuilder(self.bcp.variables, self.bcp.relations)
            o_2 = b_2.sample_builder().build_single_node("a", "1")
            b_1.add_outcome(o_2)

        with self.assertRaises(AssertionError):  # Expect count be >= 1
            b_1.add_outcome(self.o_1, 0)

    def test_add_outcomes(self):
        b_1 = RelationGraphBuilder(self.bcp.variables, self.bcp.relations, "b_1", {}, self.bcp)
        b_1.add_outcomes([self.o_1, self.o_1, self.o_1])
        self.assertEqual(b_1.build().outcomes(), frozenset({(self.o_1, 3)}))

    def test_sample_builder(self):
        sb_1 = self.b_1.sample_builder()
        s_1 = sb_1.build_single_node("a", "2")
        self.assertEqual(s_1.edges_set_view(), ("a", "2"))

    def test_build_sample(self):
        b_1 = RelationGraphBuilder(self.bcp.variables, self.bcp.relations, "b_1", {}, self.bcp)
        b_1.build_sample(lambda b: b.build_single_node("a", "2"))
        self.assertEqual(b_1.build().number_of_outcomes, 1)


    def test_generate_all_possible_outcomes(self):
        pass


    def test_build(self):
        b_1 = RelationGraphBuilder(self.bcp.variables, self.bcp.relations, "b_1", {self.o_1: 1}, self.bcp)
        self.assertEqual(b_1.build().outcomes(), frozenset({(self.o_1, 1)}))
        with self.assertRaises(AssertionError):  # Expect count be >= 1
            b_2 = RelationGraphBuilder(self.bcp.variables, self.bcp.relations, "b_1", {}, self.bcp)
            b_2.build()


class TestRelationGraph(unittest.TestCase):

    def test_init(self):
        pass

    def test_repr(self):
        pass

    def test_copy(self):
        pass

    def test_outcomes(self):
        pass

    def test_builder(self):
        pass

    def test_describe(self):
        pass

    def test_disjoint_distribution(self):
        pass

    def test_inference(self):
        pass


if __name__ == '__main__':
    unittest.main()
