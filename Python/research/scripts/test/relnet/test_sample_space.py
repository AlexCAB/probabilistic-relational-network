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
from typing import List, Tuple

from scripts.relnet.sample_graph import SampleGraphBuilder
from scripts.relnet.folded_graph import FoldedNode, FoldedEdge
from scripts.relnet.sample_space import SampleSpace, SampleSet, SampleSetBuilder
from scripts.test.relnet.test_graph_components import MockSampleGraphComponentsProvider


class TestSampleSpace(unittest.TestCase):

    bcp = MockSampleGraphComponentsProvider({"a": {"1", "2"}, "b": {"2", "3"}, "c": {"3", "4"}}, {"r", "s"})
    o_1 = SampleGraphBuilder(bcp).build_single_node("a", "1")
    o_2 = SampleGraphBuilder(bcp).build_single_node("a", "2")
    o_3 = SampleGraphBuilder(bcp) \
        .add_relation({("a", "1"), ("b", "2")}, "r") \
        .build()
    ss_1 = SampleSpace(bcp, SampleSet({o_1: 1, o_2: 2, o_3: 3}))

    def test_init(self):
        self.assertEqual(self.ss_1.outcomes.length, 6)

    def test_copy(self):
        with self.assertRaises(AssertionError):
            copy(self.ss_1)

    def test_outcomes(self):
        self.assertEqual(self.ss_1.outcomes.items(), {(self.o_1, 1),  (self.o_2, 2), (self.o_3, 3)})

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

    def test_join_outcomes_on_variable_set(self):
        bcp = MockSampleGraphComponentsProvider(
            {"a": {"T", "F"}, "b": {"T", "F"}, "c": {"T", "F"}, "d": {"T", "F"}}, {"r", "s"})

        def sample_set(desc: List[Tuple[List[Tuple[str, str, str, str]], int]]) -> SampleSet:
            ssb = SampleSetBuilder()
            for sample_edges, count in desc:
                sb = SampleGraphBuilder(bcp)
                for s_var, s_val,  t_var, t_val in sample_edges:
                    sb.add_relation({(s_var, s_val), (t_var, t_val)}, "r")
                ssb.add(sb.build(), count)
            return ssb.build()

        ab_samples = sample_set([
            ([("a", "T", "b", "T")], 2),
            ([("a", "T", "b", "F")], 3),
            ([("a", "F", "b", "T")], 4),
            ([("a", "F", "b", "F")], 5)])

        bc_samples = sample_set([
            ([("b", "T", "c", "T")], 6),
            ([("b", "T", "c", "F")], 7),
            ([("b", "F", "c", "T")], 8),
            ([("b", "F", "c", "F")], 9)])

        ca_samples = sample_set([
            ([("c", "T", "a", "T")], 10),
            ([("c", "T", "a", "F")], 11),
            ([("c", "F", "a", "T")], 12),
            ([("c", "F", "a", "F")], 13)])

        bd_samples = sample_set([
            ([("b", "T", "d", "T")], 14),
            ([("b", "T", "d", "F")], 15),
            ([("b", "F", "d", "T")], 16),
            ([("b", "F", "d", "F")], 17)])

        expected_ab_bc_joint_a = sample_set([
            ([("a", "T", "b", "T"), ("b", "T", "c", "T")], 2 * 6),
            ([("a", "T", "b", "T"), ("b", "T", "c", "F")], 2 * 7),
            ([("a", "T", "b", "F"), ("b", "F", "c", "T")], 3 * 8),
            ([("a", "T", "b", "F"), ("b", "F", "c", "F")], 3 * 9),
            ([("a", "F", "b", "T"), ("b", "T", "c", "T")], 4 * 6),
            ([("a", "F", "b", "T"), ("b", "T", "c", "F")], 4 * 7),
            ([("a", "F", "b", "F"), ("b", "F", "c", "T")], 5 * 8),
            ([("a", "F", "b", "F"), ("b", "F", "c", "F")], 5 * 9)])

        ab_bc_ss = SampleSpace(bcp, ab_samples.union(bc_samples))

        ab_bc_joint_a = ab_bc_ss.join_outcomes_on_variable_set({"b"})
        # self.assertEqual(ab_bc_joint_a.length, 8)
        # self.assertEqual(ab_bc_joint_a, expected_ab_bc_joint_a)
        #
        # ab_bc_joint_abc = ab_bc_ss.join_outcomes_on_variable_set({"a", "b", "c"})
        # self.assertEqual(ab_bc_joint_abc, expected_ab_bc_joint_a)
        #
        # ab_bc_joint_none = ab_bc_ss.join_outcomes_on_variable_set()
        # self.assertEqual(ab_bc_joint_none, expected_ab_bc_joint_a)
        #
        # ab_bc_joint_empty = ab_bc_ss.join_outcomes_on_variable_set(set({}))
        # self.assertEqual(ab_bc_joint_empty, ab_samples.union(bc_samples))
        #
        # exe_ab_bc_ca_joint_a = expected_ab_bc_joint_a.union(ca_samples)
        #
        # expected_ab_bc_ca_joint_abc = sample_set({  # Triangle
        #     [("a", "T", "b", "T"), ("b", "T", "c", "T"), ("c", "T", "a", "T")]: 2 * 6 * 10,
        #     [("a", "T", "b", "T"), ("b", "T", "c", "T"), ("c", "T", "a", "F")]: 2 * 6 * 11,
        #     [("a", "T", "b", "T"), ("b", "T", "c", "F"), ("c", "T", "a", "T")]: 2 * 7 * 10,
        #     [("a", "T", "b", "T"), ("b", "T", "c", "F"), ("c", "T", "a", "F")]: 2 * 7 * 11,
        #     [("a", "T", "b", "F"), ("b", "F", "c", "T"), ("c", "F", "a", "T")]: 3 * 8 * 12,
        #     [("a", "T", "b", "F"), ("b", "F", "c", "T"), ("c", "F", "a", "F")]: 3 * 8 * 13,
        #     [("a", "T", "b", "F"), ("b", "F", "c", "F"), ("c", "F", "a", "T")]: 3 * 9 * 12,
        #     [("a", "T", "b", "F"), ("b", "F", "c", "F"), ("c", "F", "a", "F")]: 3 * 9 * 13,
        #     [("a", "F", "b", "T"), ("b", "T", "c", "T"), ("c", "T", "a", "T")]: 4 * 6 * 10,
        #     [("a", "F", "b", "T"), ("b", "T", "c", "T"), ("c", "T", "a", "F")]: 4 * 6 * 11,
        #     [("a", "F", "b", "T"), ("b", "T", "c", "F"), ("c", "T", "a", "T")]: 4 * 7 * 10,
        #     [("a", "F", "b", "T"), ("b", "T", "c", "F"), ("c", "T", "a", "F")]: 4 * 7 * 11,
        #     [("a", "F", "b", "F"), ("b", "F", "c", "T"), ("c", "F", "a", "T")]: 5 * 8 * 12,
        #     [("a", "F", "b", "F"), ("b", "F", "c", "T"), ("c", "F", "a", "F")]: 5 * 8 * 13,
        #     [("a", "F", "b", "F"), ("b", "F", "c", "F"), ("c", "F", "a", "T")]: 5 * 9 * 12,
        #     [("a", "F", "b", "F"), ("b", "F", "c", "F"), ("c", "F", "a", "F")]: 5 * 9 * 13})
        #
        # ab_bc_ca_ss = SampleSpace(bcp, SampleSet(ab_samples.union(bc_samples).union(ca_samples)))
        #
        # self.assertEqual(ab_bc_ca_ss.join_outcomes_on_variable_set({"a"}), exe_ab_bc_ca_joint_a)
        # self.assertEqual(ab_bc_ca_ss.join_outcomes_on_variable_set({"a", "b"}), expected_ab_bc_ca_joint_abc)
        # self.assertEqual(ab_bc_ca_ss.join_outcomes_on_variable_set({"a", "b", "c"}), expected_ab_bc_ca_joint_abc)
        #
        # expected_ab_bc_bd_joint_abc = sample_set({  # Star
        #     [("a", "T", "b", "T"), ("b", "T", "c", "T"), ("b", "T", "d", "T")]: 2 * 6 * 14,
        #     [("a", "T", "b", "T"), ("b", "T", "c", "T"), ("b", "T", "d", "F")]: 2 * 6 * 15,
        #     [("a", "T", "b", "T"), ("b", "T", "c", "F"), ("b", "T", "d", "T")]: 2 * 7 * 14,
        #     [("a", "T", "b", "T"), ("b", "T", "c", "F"), ("b", "T", "d", "F")]: 2 * 7 * 15,
        #     [("a", "T", "b", "F"), ("b", "F", "c", "T"), ("b", "F", "d", "T")]: 3 * 8 * 16,
        #     [("a", "T", "b", "F"), ("b", "F", "c", "T"), ("b", "F", "d", "F")]: 3 * 8 * 17,
        #     [("a", "T", "b", "F"), ("b", "F", "c", "F"), ("b", "F", "d", "T")]: 3 * 9 * 16,
        #     [("a", "T", "b", "F"), ("b", "F", "c", "F"), ("b", "F", "d", "F")]: 3 * 9 * 17,
        #     [("a", "F", "b", "T"), ("b", "T", "c", "T"), ("b", "T", "d", "T")]: 4 * 6 * 14,
        #     [("a", "F", "b", "T"), ("b", "T", "c", "T"), ("b", "T", "d", "F")]: 4 * 6 * 15,
        #     [("a", "F", "b", "T"), ("b", "T", "c", "F"), ("b", "T", "d", "T")]: 4 * 7 * 10,
        #     [("a", "F", "b", "T"), ("b", "T", "c", "F"), ("b", "T", "d", "F")]: 4 * 7 * 15,
        #     [("a", "F", "b", "F"), ("b", "F", "c", "T"), ("b", "F", "d", "T")]: 5 * 8 * 16,
        #     [("a", "F", "b", "F"), ("b", "F", "c", "T"), ("b", "F", "d", "F")]: 5 * 8 * 17,
        #     [("a", "F", "b", "F"), ("b", "F", "c", "F"), ("b", "F", "d", "T")]: 5 * 9 * 16,
        #     [("a", "F", "b", "F"), ("b", "F", "c", "F"), ("b", "F", "d", "F")]: 5 * 9 * 17})
        #
        # ab_bc_bd_ss = SampleSpace(bcp, SampleSet(ab_samples.union(bc_samples).union(bd_samples)))
        #
        # self.assertEqual(ab_bc_bd_ss.join_outcomes_on_variable_set({"b"}), expected_ab_bc_bd_joint_abc)
        # self.assertEqual(ab_bc_bd_ss.join_outcomes_on_variable_set({"a", "b"}), expected_ab_bc_bd_joint_abc)
        # self.assertEqual(ab_bc_bd_ss.join_outcomes_on_variable_set({"a", "b", "c"}), expected_ab_bc_bd_joint_abc)


if __name__ == '__main__':
    unittest.main()
