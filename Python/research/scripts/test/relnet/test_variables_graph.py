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
created: 2021-10-29
"""

import unittest
from copy import copy

from scripts.relnet.sample_graph import ValueNode, RelationEdge
from scripts.relnet.variables_graph import VariableNode, VariableEdge, VariablesGraph


class TestVariableNode(unittest.TestCase):

    vn_1 = ValueNode("a", "1")
    vn_2 = ValueNode("a", "2")
    vr_1 = VariableNode("a", {vn_1: 1, vn_2: 2})

    def test_init(self):
        self.assertEqual(self.vr_1.variable, "a")
        self.assertEqual(self.vr_1.value_nodes, frozenset({(self.vn_1, 1), (self.vn_2, 2)}))

    def test_copy(self):
        with self.assertRaises(AssertionError):
            copy(self.vr_1)

    def test_repr(self):
        self.assertEqual(self.vr_1.__repr__(), "(a:{1(1),2(2)})")

    def test_hash(self):
        self.assertEqual(self.vr_1.__hash__(), ("a", frozenset({(self.vn_1, 1), (self.vn_2, 2)})).__hash__())

    def test_eq(self):
        vr_1 = VariableNode("a", {self.vn_1: 1, self.vn_2: 2})
        vr_2 = VariableNode("a", {self.vn_1: 1, self.vn_2: 2})
        self.assertNotEqual(id(vr_1), id(vr_2))
        self.assertEqual(vr_1, vr_2)

    def test_unobserved_count(self):
        self.assertEqual(self.vr_1.unobserved_count(5), 2)


class TestVariableEdge(unittest.TestCase):

    vn_a1 = ValueNode("a", "1")
    vn_b1 = ValueNode("b", "1")
    vn_b2 = ValueNode("b", "2")
    re_1 = RelationEdge(frozenset({vn_a1, vn_b1}), "r")
    re_2 = RelationEdge(frozenset({vn_a1, vn_b2}), "s")
    ve_1 = VariableEdge(frozenset({"a", "b"}), {re_1: 1, re_2: 2})

    def test_init(self):
        self.assertEqual(self.ve_1.endpoints, frozenset({"a", "b"}))
        self.assertEqual(self.ve_1.relation_edges, frozenset({(self.re_1, 1), (self.re_2, 2)}))

    def test_copy(self):
        with self.assertRaises(AssertionError):
            copy(self.ve_1)

    def test_repr(self):
        self.assertEqual(self.ve_1.__repr__(), "(a)--{r(1),s(2)}--(b)")

    def test_hash(self):
        self.assertEqual(
            self.ve_1.__hash__(),
            (frozenset({"a", "b"}), frozenset({(self.re_1, 1), (self.re_2, 2)})).__hash__())

    def test_eq(self):
        ve_1 = VariableEdge(frozenset({"a", "b"}), {self.re_1: 1, self.re_2: 2})
        ve_2 = VariableEdge(frozenset({"a", "b"}), {self.re_1: 1, self.re_2: 2})
        self.assertNotEqual(id(ve_1), id(ve_2))
        self.assertEqual(ve_1, ve_2)


class TestVariablesGraph(unittest.TestCase):

    vn_a1 = ValueNode("a", "1")
    vn_b1 = ValueNode("b", "1")
    vn_b2 = ValueNode("b", "2")
    re_1 = RelationEdge(frozenset({vn_a1, vn_b1}), "r")
    re_2 = RelationEdge(frozenset({vn_a1, vn_b2}), "s")
    vr_1 = VariableNode("a", {vn_a1: 1})
    vr_2 = VariableNode("b", {vn_b1: 1, vn_b2: 2})
    ve_1 = VariableEdge(frozenset({"a", "b"}), {re_1: 1, re_2: 2})
    vg_1 = VariablesGraph({vr_1, vr_2}, {ve_1}, "vg_1")

    def test_init(self):
        self.assertEqual(self.vg_1.nodes, frozenset({self.vr_1, self.vr_2}))
        self.assertEqual(self.vg_1.edges, frozenset({self.ve_1}))
        self.assertEqual(self.vg_1.name, "vg_1")

    def test_copy(self):
        with self.assertRaises(AssertionError):
            copy(self.vg_1)

    def test_repr(self):
        self.assertEqual(self.vg_1.__repr__(), "vg_1")

    def test_eq(self):
        vg_1 = VariablesGraph({self.vr_1, self.vr_2}, {self.ve_1}, "vg_1")
        vg_2 = VariablesGraph({self.vr_1, self.vr_2}, {self.ve_1}, "vg_2")
        self.assertNotEqual(id(vg_1), id(vg_2))
        self.assertEqual(vg_1, vg_2)


if __name__ == '__main__':
    unittest.main()
