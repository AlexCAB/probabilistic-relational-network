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

from scripts.relnet.sample_graph import SampleGraphBuilder
from scripts.relnet.folded_graph import FoldedNode, FoldedEdge
from scripts.relnet.sample_space import SampleSpace
from scripts.test.relnet.test_graph_components import MockSampleGraphComponentsProvider


class TestSampleSpace(unittest.TestCase):

    bcp = MockSampleGraphComponentsProvider({"a": {"1", "2"}, "b": {"2", "3"}, "c": {"3", "4"}}, {"r", "s"})
    o_1 = SampleGraphBuilder(bcp).set_name("o_1").build_single_node("a", "1")
    o_2 = SampleGraphBuilder(bcp).set_name("o_2").build_single_node("a", "2")
    o_3 = SampleGraphBuilder(bcp) \
        .add_relation({("a", "1"), ("b", "2")}, "r") \
        .build()
    ss_1 = SampleSpace(bcp, {o_1: 1, o_2: 2, o_3: 3})

    def test_init(self):
        self.assertEqual(self.ss_1.number_of_outcomes, 6)

    def test_copy(self):
        with self.assertRaises(AssertionError):
            copy(self.ss_1)

    def test_outcomes(self):
        self.assertEqual(self.ss_1.outcomes(), frozenset({(self.o_1, 1),  (self.o_2, 2), (self.o_3, 3)}))

    def test_outcomes_as_edges_sets(self):
        self.assertEqual(self.ss_1.outcomes_as_edges_sets(), frozenset({
            (frozenset({(frozenset({("a", "1"), ("b", "2")}), "r")}), 3),
            (("a", "1"), 1),
            (("a", "2"), 2)}))

    def test_disjoint_distribution(self):
        self.assertEqual(
            self.ss_1.disjoint_distribution(),
            {("a", "1"): 0.4444444444444444,
             ("a", "2"): 0.2222222222222222,
             ("b", "2"): 0.3333333333333333})

    def test_included_variables(self):
        self.assertEqual(
            self.ss_1.included_variables(),
            frozenset({("a", frozenset({"1", "2"})), ("b", frozenset({"2"}))}))

    def test_included_relations(self):
        self.assertEqual(self.ss_1.included_relations(), frozenset({"r"}))

    def test_folded_graph(self):
        vg_1 = self.ss_1.folded_graph("vg_1")
        gn = self.bcp.get_node
        ge = self.bcp.get_edge

        self.assertEqual(
            vg_1.name,
            "vg_1")

        self.assertEqual(
            vg_1.nodes, frozenset({
                FoldedNode("b", {"2", "3"}, {gn("b", "2"): 3}, 3),
                FoldedNode("a", {"1", "2"}, {gn("a", "1"): 4, gn("a", "2"): 2}, 3)}))

        self.assertEqual(
            vg_1.edges, frozenset({
                FoldedEdge({"a", "b"}, {ge(frozenset({gn("a", "1"), gn("b", "2")}), "r"): 3})}))


if __name__ == '__main__':
    unittest.main()
