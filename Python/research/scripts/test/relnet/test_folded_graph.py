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
created: 2021-11-01
"""

import unittest

from scripts.relnet.relation_graph import BuilderComponentsProvider
from scripts.relnet.sample_graph import ValueNode, RelationEdge
from scripts.relnet.folded_graph import FoldedNode, FoldedEdge, FoldedGraph


class TestFoldedNode(unittest.TestCase):

    vn_1 = ValueNode("a", "1")
    vn_2 = ValueNode("a", "2")
    fr_1 = FoldedNode("a", {vn_1: 1, vn_2: 2})

    def test_init(self):
        self.assertEqual(self.fr_1.variable, "a")
        self.assertEqual(self.fr_1.value_nodes, frozenset({(self.vn_1, 1), (self.vn_2, 2)}))

    def test_repr(self):
        self.assertEqual(self.fr_1.__repr__(), "(a:{1(1),2(2)})")

    def test_unobserved_count(self):
        self.assertEqual(self.fr_1.unobserved_count(5), 2)


class TestFoldedEdge(unittest.TestCase):

    vn_a1 = ValueNode("a", "1")
    vn_b1 = ValueNode("b", "1")
    vn_b2 = ValueNode("b", "2")
    re_1 = RelationEdge(frozenset({vn_a1, vn_b1}), "r")
    re_2 = RelationEdge(frozenset({vn_a1, vn_b2}), "s")
    fe_1 = FoldedEdge({"a", "b"}, {re_1: 1, re_2: 2})

    def test_init(self):
        self.assertEqual(self.fe_1.endpoints, frozenset({"a", "b"}))
        self.assertEqual(self.fe_1.relation_edges, frozenset({(self.re_1, 1), (self.re_2, 2)}))

    def test_repr(self):
        self.assertEqual(self.fe_1.__repr__(), "(a)--{r(1),s(2)}--(b)")


class TestFoldedGraph(unittest.TestCase):

    bcp = BuilderComponentsProvider({"a": {"1"}, "b": {"2"}}, {"s"})
    vn_a1 = ValueNode("a", "1")
    vn_b1 = ValueNode("b", "1")
    vn_b2 = ValueNode("b", "2")
    re_1 = RelationEdge(frozenset({vn_a1, vn_b1}), "r")
    re_2 = RelationEdge(frozenset({vn_a1, vn_b2}), "s")
    fr_a = FoldedNode("a", {vn_a1: 1})
    fr_b = FoldedNode("b", {vn_b1: 1, vn_b2: 2})
    fe_1 = FoldedEdge({fr_a, fr_b}, {re_1: 1, re_2: 2})
    fg_1 = FoldedGraph(bcp, 123, {fr_a, fr_b}, {fe_1}, "vg_1")

    def test_init(self):
        self.assertEqual(self.fg_1.nodes, frozenset({self.fr_a, self.fr_b}))
        self.assertEqual(self.fg_1.edges, frozenset({self.fe_1}))
        self.assertEqual(self.fg_1.name, "vg_1")
        self.assertEqual(self.fg_1.variables, frozenset({"a", "b"}))


if __name__ == '__main__':
    unittest.main()
