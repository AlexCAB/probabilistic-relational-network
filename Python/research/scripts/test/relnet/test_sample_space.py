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

import os
import unittest
from copy import copy

from scripts.relnet.sample_graph import SampleGraphBuilder
from scripts.relnet.folded_graph import FoldedNode, FoldedEdge
from scripts.relnet.sample_space import SampleSpace, SampleSet
from scripts.test.relnet.test_graph_components import MockSampleGraphComponentsProvider


class TestSampleSpace(unittest.TestCase):

    bcp = MockSampleGraphComponentsProvider({"a": {"1", "2"}, "b": {"2", "3"}, "c": {"3", "4"}}, {"r", "s"})
    o_1 = SampleGraphBuilder(bcp).build_single_node("a", "1")
    o_2 = SampleGraphBuilder(bcp).build_single_node("a", "2")
    o_3 = SampleGraphBuilder(bcp) \
        .add_relation({("a", "1"), ("b", "2")}, "r") \
        .build()
    o_k_0 = SampleGraphBuilder(bcp).set_name("o_k_0").build_empty()
    ss_1 = SampleSpace(bcp, SampleSet(bcp, {o_1: 1, o_2: 2, o_3: 3}), "ss_1", None)

    def test_init(self):
        self.assertEqual(self.ss_1.outcomes.length, 6)

    def test_copy(self):
        with self.assertRaises(AssertionError):
            copy(self.ss_1)

    def test_repr(self):
        self.assertEqual(str(self.ss_1), "ss_1")

    def test_builder(self):
        ss_2 = self.ss_1.builder().set_name("ss_2").build()
        self.assertEqual(ss_2.variables, self.bcp.variables())
        self.assertEqual(ss_2.relations, self.bcp.relations())
        self.assertEqual(ss_2.outcomes.length, 6)
        self.assertEqual(ss_2.name, "ss_2")
        self.assertEqual(ss_2.outcomes.items(), {(self.o_1, 1),  (self.o_2, 2), (self.o_3, 3)})

    def test_relation_graph(self):
        rg_1 = self.ss_1.relation_graph("rg_1")
        self.assertEqual(rg_1.outcomes, self.ss_1.outcomes)
        self.assertEqual(rg_1.name, "rg_1")

    def test_outcomes(self):
        self.assertEqual(self.ss_1.outcomes.items(), {(self.o_1, 1),  (self.o_2, 2), (self.o_3, 3)})

    def test_sample_builder(self):
        sb_1 = self.ss_1.sample_builder()
        s_1 = sb_1.build_single_node("a", "2")
        self.assertEqual(s_1.edges_set_view(), ("a", "2"))

    def test_outcomes_as_edges_sets(self):
        self.assertEqual(self.ss_1.outcomes_as_edges_sets(), frozenset({
            (frozenset({(frozenset({("a", "1"), ("b", "2")}), "r")}), 3),
            (("a", "1"), 1),
            (("a", "2"), 2)}))

    def test_marginal_variables_probability(self):
        self.assertEqual(
            self.ss_1.marginal_variables_probability(),
            {"a": {"1": 0.6666666666666666, "2": 0.3333333333333333},
             "b": {"2": 1.0}})

        self.assertEqual(
            self.ss_1.marginal_variables_probability({"a"}),
            {"a": {"1": 0.6666666666666666, "2": 0.3333333333333333}})

        self.assertEqual(
            self.ss_1.marginal_variables_probability(unobserved=True),
            {"a": {"1": 0.6666666666666666, "2": 0.3333333333333333, "u": 0.0},
             "b": {"2": 0.5, "u": 0.5}})

        self.assertEqual(
            self.ss_1.marginal_variables_probability({"a"}, unobserved=True),
            {"a": {"1": 0.6666666666666666, "2": 0.3333333333333333, "u": 0.0}})

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

    def test_print_samples(self):
        self.assertEqual(
            self.ss_1.print_samples(),
            os.linesep.join(["{(a_1)--{r}--(b_2)}(3)", "{(a_1)}(1)", "{(a_2)}(2)"]))

    def test_find_for_values(self):
        self.assertEqual(
            self.ss_1.find_for_values({("a", "1"), ("b", "2")}),
            SampleSet(self.bcp, {self.o_3: 3}))

    def test_factorized(self):
        o_ab_1 = SampleGraphBuilder(self.bcp).set_name("o_ab")\
            .add_relation({("a", "1"), ("b", "2")}, "r")\
            .build()
        o_ab_2 = SampleGraphBuilder(self.bcp).set_name("o_ab") \
            .add_relation({("a", "2"), ("b", "3")}, "r") \
            .build()
        o_bc = SampleGraphBuilder(self.bcp).set_name("o_bc")\
            .add_relation({("b", "2"), ("c", "3")}, "r")\
            .build()
        o_abc = SampleGraphBuilder(self.bcp).set_name("o_abc")\
            .add_relation({("a", "1"), ("b", "2")}, "r") \
            .add_relation({("b", "2"), ("c", "3")}, "r") \
            .build()

        self.assertEqual(
            SampleSpace(self.bcp, SampleSet(self.bcp, {o_ab_1: 1}), "ss_1", None).factorized(),
            frozenset({SampleSet(self.bcp, {o_ab_1: 1})}))

        self.assertEqual(
            SampleSpace(self.bcp, SampleSet(self.bcp, {o_ab_1: 1, o_ab_2: 2}), "ss_2", None).factorized(),
            frozenset({SampleSet(self.bcp, {o_ab_1: 1, o_ab_2: 2})}))

        self.assertEqual(
            SampleSpace(self.bcp, SampleSet(self.bcp, {o_ab_1: 1, o_ab_2: 2, o_bc: 3}), "ss_3", None).factorized(),
            frozenset({SampleSet(self.bcp, {o_ab_1: 1, o_ab_2: 2}), SampleSet(self.bcp, {o_bc: 3})}))

        with self.assertRaises(AssertionError):  # Overlapping outcomes
            SampleSpace(self.bcp, SampleSet(self.bcp, {o_ab_1: 1, o_abc: 2}), "ss_4", None).factorized()

        with self.assertRaises(AssertionError):  # Empty outcomes
            SampleSpace(self.bcp, SampleSet(self.bcp, {o_ab_1: 1, self.o_k_0: 2}), "ss_5", None).factorized()


if __name__ == '__main__':
    unittest.main()
