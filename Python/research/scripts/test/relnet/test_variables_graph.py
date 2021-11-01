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

from scripts.relnet.relation_graph import BuilderComponentsProvider
from scripts.relnet.variables_graph import VariableNode, VariableEdge, VariablesGraph


class TestVariableNode(unittest.TestCase):

    vr_1 = VariableNode("a")

    def test_init(self):
        self.assertEqual(self.vr_1.variable, "a")

    def test_copy(self):
        with self.assertRaises(AssertionError):
            copy(self.vr_1)

    def test_repr(self):
        self.assertEqual(self.vr_1.__repr__(), "(a)")

    def test_hash(self):
        self.assertEqual(self.vr_1.__hash__(), "a".__hash__())

    def test_eq(self):
        vr_1 = VariableNode("a")
        vr_2 = VariableNode("a")
        self.assertNotEqual(id(vr_1), id(vr_2))
        self.assertEqual(vr_1, vr_2)


class TestVariableEdge(unittest.TestCase):

    ve_1 = VariableEdge({"a", "b"})

    def test_init(self):
        self.assertEqual(self.ve_1.endpoints, frozenset({"a", "b"}))

        with self.assertRaises(AssertionError):  # Expect 2 endpoints
            VariableEdge({"a", "a"})

    def test_copy(self):
        with self.assertRaises(AssertionError):
            copy(self.ve_1)

    def test_repr(self):
        self.assertEqual(self.ve_1.__repr__(), "(a)--(b)")

    def test_hash(self):
        self.assertEqual(
            self.ve_1.__hash__(),
            frozenset({"a", "b"}).__hash__())

    def test_eq(self):
        ve_2 = VariableEdge({"a", "b"})
        self.assertNotEqual(id(self.ve_1), id(ve_2))
        self.assertEqual(self.ve_1, ve_2)


class TestVariablesGraph(unittest.TestCase):

    bcp = BuilderComponentsProvider({"a": {"1"}, "b": {"2"}}, {"s"})
    vr_1 = VariableNode("a")
    vr_2 = VariableNode("b")
    ve_1 = VariableEdge({"a", "b"})
    vg_1 = VariablesGraph(bcp, 123, {vr_1, vr_2}, {ve_1}, "vg_1")

    def test_init(self):
        self.assertEqual(self.vg_1.number_of_outcomes, 123)
        self.assertEqual(self.vg_1.nodes, frozenset({self.vr_1, self.vr_2}))
        self.assertEqual(self.vg_1.edges, frozenset({self.ve_1}))
        self.assertEqual(self.vg_1.name, "vg_1")
        self.assertEqual(self.vg_1.variables, frozenset({"a", "b"}))

    def test_copy(self):
        with self.assertRaises(AssertionError):
            copy(self.vg_1)

    def test_repr(self):
        self.assertEqual(self.vg_1.__repr__(), "vg_1")

    def test_eq(self):
        vg_2 = VariablesGraph(self.bcp, 123, {self.vr_1, self.vr_2}, {self.ve_1}, "vg_2")
        self.assertNotEqual(id(self.vg_1), id(vg_2))
        self.assertEqual(self.vg_1, vg_2)

    def test_variable_node(self):
        self.assertEqual(self.vg_1.variable("a"), self.vr_1)
        self.assertEqual(self.vg_1.variable("s"), None)


if __name__ == '__main__':
    unittest.main()
