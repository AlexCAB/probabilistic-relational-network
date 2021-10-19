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
import unittest
from copy import copy

from scripts.relnet.sample_graph import ValueNode, RelationEdge, SampleBuilder, SampleGraph


class TestValueNode(unittest.TestCase):

    a_1 = ValueNode("a", "1")

    def test_init(self):
        self.assertEqual(self.a_1.variable, "a")
        self.assertEqual(self.a_1.value, "1")
        with self.assertRaises(AssertionError):
            ValueNode("a", {})
        with self.assertRaises(AssertionError):
            ValueNode({}, "1")

    def test_hash(self):
        self.assertEqual(self.a_1.__hash__(), ("a", "1").__hash__())

    def test_repr(self):
        self.assertEqual(self.a_1.__repr__(), "(a_1)")

    def test_copy(self):
        self.assertNotEqual(id(self.a_1), id(copy(self.a_1)))
        self.assertEqual(self.a_1, copy(self.a_1))
        self.assertEqual(self.a_1.__hash__(), copy(self.a_1).__hash__())

    def test_eq(self):
        a_1_1 = ValueNode("a", "1")
        a_1_2 = ValueNode("a", "1")
        self.assertNotEqual(id(a_1_1), id(a_1_2))
        self.assertEqual(a_1_1, a_1_2)

    def test_with_replaced_value(self):
        a_2 = self.a_1.with_replaced_value("2")
        self.assertEqual(a_2.value, "2")


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
        with self.assertRaises(AssertionError):
            RelationEdge(frozenset({self.b_1}), "r")
        with self.assertRaises(AssertionError):
            RelationEdge(frozenset({self.a_1, self.a_1}), "r")
        with self.assertRaises(AssertionError):
            RelationEdge(frozenset({self.b_1, self.b_2}), "r")
        with self.assertRaises(AssertionError):
            RelationEdge(frozenset({self.b_1, self.b_2}), {})

    def test_hash(self):
        self.assertEqual(self.e_1.__hash__(), (frozenset({self.a_1, self.b_1}), "r").__hash__())

    def test_repr(self):
        self.assertEqual(self.e_1.__repr__(), "(a_1)--{r}--(b_1)")

    def test_copy(self):
        self.assertNotEqual(id(self.e_1), id(copy(self.e_1)))
        self.assertEqual(self.e_1, copy(self.e_1))
        self.assertEqual(self.e_1.__hash__(), copy(self.e_1).__hash__())

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

    def test_with_replaced_values(self):
        self.assertEqual(
            self.e_1.with_replaced_values({"a": ("1", "3"), "b": ("1", "4")}),
            RelationEdge(frozenset({ValueNode("a", "3"), ValueNode("b", "4")}), "r")
        )


class TestSampleBuilder(unittest.TestCase):

    a_1 = ValueNode("a", "1")
    b_1 = ValueNode("b", "1")
    e_1 = RelationEdge(frozenset({a_1, b_1}), "r")

    def test_init(self):
        s_1 = SampleBuilder("s", {self.a_1, self.b_1}, {self.e_1}).build()
        self.assertEqual(s_1.name, "s")
        self.assertEqual(s_1.nodes, frozenset({self.a_1, self.b_1}))
        self.assertEqual(s_1.edges, frozenset({self.e_1}))

    def test_set_name(self):
        s_1 = SampleBuilder(None, {self.a_1})\
            .set_name("s")\
            .build()
        self.assertEqual(s_1.name, "s")

    def test_add_value(self):
        s_1 = SampleBuilder() \
            .add_value(self.a_1.variable, self.a_1.value) \
            .build()
        self.assertEqual(s_1.nodes, frozenset({self.a_1}))

    def test_add_relation(self):
        s_1 = SampleBuilder() \
            .add_value(self.a_1.variable, self.a_1.value) \
            .add_value(self.b_1.variable, self.b_1.value) \
            .add_relation(
                {(self.a_1.variable, self.a_1.value), (self.b_1.variable, self.b_1.value)},
                self.e_1.relation) \
            .build()
        self.assertEqual(s_1.nodes, frozenset({self.a_1, self.b_1}))
        self.assertEqual(s_1.edges, frozenset({self.e_1}))

    def test_connected_nodes(self):
        s_1 = SampleBuilder() \
            .add_value("a", "1") \
            .add_value("b", "1") \
            .add_value("c", "1") \
            .add_value("d", "1") \
            .add_relation({("a", "1"), ("b", "1")}, "r") \
            .add_relation({("b", "1"), ("c", "1")}, "r")
        self.assertEqual(
            s_1.connected_nodes(ValueNode("a", "1")),
            {ValueNode("a", "1"), ValueNode("b", "1"), ValueNode("c", "1")})
        self.assertEqual(
            s_1.connected_nodes(ValueNode("d", "1")),
            {ValueNode("d", "1")})

    def test_is_connected(self):
        self.assertTrue(SampleBuilder()
                        .add_value("a", "1").add_value("b", "1").add_relation({("a", "1"), ("b", "1")}, "r")
                        .is_connected())
        self.assertTrue(SampleBuilder()
                        .add_value("a", "1")
                        .is_connected())
        self.assertFalse(SampleBuilder()
                         .is_connected())
        self.assertFalse(SampleBuilder()
                         .add_value("a", "1").add_value("b", "1")
                         .is_connected())
        self.assertFalse(SampleBuilder()
                         .add_value("a", "1").add_value("b", "1").add_value("c", "1")
                         .add_relation({("a", "1"), ("b", "1")}, "r")
                         .is_connected())

    def test_build(self):
        with self.assertRaises(AssertionError):
            SampleBuilder().add_value("a", "1").add_value("b", "1").build()


class TestSampleGraph(unittest.TestCase):

    a_1 = ValueNode("a", "1")
    b_1 = ValueNode("b", "1")
    c_1 = ValueNode("c", "1")
    e_1 = RelationEdge(frozenset({a_1, b_1}), "r")
    e_2 = RelationEdge(frozenset({b_1, c_1}), "r")
    s_1 = SampleGraph(frozenset({a_1, b_1}), frozenset({e_1}), "s_1")

    def test_init(self):
        self.assertEqual(self.s_1.nodes, frozenset({self.a_1, self.b_1}))
        self.assertEqual(self.s_1.edges, frozenset({self.e_1}))
        self.assertEqual(self.s_1.hash, frozenset({self.a_1, self.b_1, self.e_1}))
        self.assertEqual(self.s_1.name, "s_1")
        with self.assertRaises(AssertionError):
            SampleGraph(frozenset({}), frozenset({}), None)
        with self.assertRaises(AssertionError):
            SampleGraph(frozenset({ValueNode("a", "1"),  ValueNode("a", "2")}), frozenset({}), None)
        with self.assertRaises(AssertionError):
            SampleGraph(frozenset({ValueNode("c", "1"),  ValueNode("d", "1")}), frozenset({self.e_1}), None)

    def test_hash(self):
        self.assertEqual(self.s_1.__hash__(), self.s_1.hash.__hash__())

    def test_repr(self):
        self.assertEqual(self.s_1.__repr__(), "s_1")
        self.assertEqual(
            SampleGraph(frozenset({self.a_1, self.b_1, self.c_1}), frozenset({self.e_1, self.e_2}), None).__repr__(),
            "{(a_1)--{r}--(b_1); (b_1)--{r}--(c_1)}")

    def test_copy(self):
        self.assertNotEqual(id(self.s_1), id(copy(self.s_1)))
        self.assertEqual(self.s_1, copy(self.s_1))
        self.assertEqual(self.s_1.hash, copy(self.s_1).hash)

    def test_eq(self):
        s_1_1 = SampleGraph(frozenset({self.a_1, self.b_1}), frozenset({self.e_1}), None)
        s_1_2 = SampleGraph(frozenset({self.a_1, self.b_1}), frozenset({self.e_1}), None)
        self.assertNotEqual(id(s_1_1), id(s_1_2))
        self.assertEqual(s_1_1, s_1_2)

    def test_text_view(self):
        self.assertEqual(SampleGraph(frozenset({self.a_1}), frozenset(), None).text_view(), "{(a_1)}")
        self.assertEqual(self.s_1.text_view(),  "{" + os.linesep + "    (a_1)--{r}--(b_1)" + os.linesep + "}")

    def test_builder(self):
        b_1 = self.s_1.builder()
        b_1.add_value("f", "1")
        b_1.add_relation({("b", "1"), ("f", "1")}, "g")
        s_2 = b_1.build()
        self.assertTrue(ValueNode("f", "1") in s_2.nodes)
        self.assertTrue(RelationEdge(frozenset({self.b_1, ValueNode("f", "1")}), "g") in s_2.edges)

    def test_is_subgraph(self):
        self.assertTrue(
            self.s_1.is_subgraph(
                SampleGraph(frozenset({self.a_1, self.b_1, self.c_1}), frozenset({self.e_1, self.e_2}), None)))
        self.assertFalse(
            self.s_1.is_subgraph(SampleGraph(frozenset({self.a_1}), frozenset({}), None)))

    def test_contains_variable(self):
        self.assertTrue(self.s_1.contains_variable("a"))
        self.assertFalse(self.s_1.contains_variable("not_in_graph"))

    def test_with_replaced_values(self):
        s_2 = self.s_1.with_replaced_values({"a": ("1", "5"), "b": ("1", "7")}, "s_2")
        self.assertEqual(
            s_2.nodes,
            frozenset({ValueNode("a", "5"), ValueNode("b", "7")}))
        self.assertEqual(
            s_2.edges,
            frozenset({RelationEdge(frozenset({ValueNode("a", "5"), ValueNode("b", "7")}), "r")}))
        self.assertEqual(s_2.name, "s_2")

    def test_neighboring_values(self):
        s = SampleBuilder()\
            .add_value("a", "1")\
            .add_value("b", "1")\
            .add_value("c", "1")\
            .add_value("d", "1")\
            .add_relation({("a", "1"), ("b", "1")}, "r")\
            .add_relation({("a", "1"), ("c", "1")}, "g")\
            .add_relation({("a", "1"), ("d", "1")}, "b")\
            .build()

        self.assertEqual(
            s.neighboring_values(ValueNode("a", "1")), {
                ValueNode("b", "1"): RelationEdge(frozenset({ValueNode("a", "1"), ValueNode("b", "1")}), "r"),
                ValueNode("c", "1"): RelationEdge(frozenset({ValueNode("a", "1"), ValueNode("c", "1")}), "g"),
                ValueNode("d", "1"): RelationEdge(frozenset({ValueNode("a", "1"), ValueNode("d", "1")}), "b")})
        self.assertEqual(
            s.neighboring_values(ValueNode("b", "1")), {
                ValueNode("a", "1"): RelationEdge(frozenset({ValueNode("a", "1"), ValueNode("b", "1")}), "r")})

        self.assertEqual(
            s.neighboring_values(ValueNode("a", "1"), ["r", "g"]), {
                ValueNode("b", "1"): RelationEdge(frozenset({ValueNode("a", "1"), ValueNode("b", "1")}), "r"),
                ValueNode("c", "1"): RelationEdge(frozenset({ValueNode("a", "1"), ValueNode("c", "1")}), "g")})

    def test_similarity(self):
        s_1 = SampleBuilder() \
            .add_value("a", "1") \
            .add_value("b", "1") \
            .add_value("c", "1") \
            .add_relation({("a", "1"), ("b", "1")}, "r") \
            .add_relation({("a", "1"), ("c", "1")}, "r") \
            .build()
        s_2 = SampleBuilder() \
            .add_value("a", "1") \
            .add_value("b", "1") \
            .add_relation({("a", "1"), ("b", "1")}, "r") \
            .build()
        s_3 = SampleBuilder() \
            .add_value("a", "1") \
            .build()

        self.assertEqual(s_1.similarity(s_2), 0.6)
        self.assertEqual(s_1.similarity(s_3), 0.2)
        self.assertEqual(s_2.similarity(s_1), 0.6)
        self.assertEqual(s_2.similarity(s_3), 0.3333333333333333)
        self.assertEqual(s_3.similarity(s_1), 0.2)
        self.assertEqual(s_3.similarity(s_2), 0.3333333333333333)


if __name__ == '__main__':
    unittest.main()
