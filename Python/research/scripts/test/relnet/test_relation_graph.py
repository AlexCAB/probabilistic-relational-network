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

from typing import List, Tuple

from scripts.relnet.graph_components import SampleGraphComponentsProvider
from scripts.relnet.relation_graph import BuilderComponentsProvider, RelationGraphBuilder, RelationGraph
from scripts.relnet.sample_graph import SampleGraphBuilder
from scripts.relnet.sample_set import SampleSet, SampleSetBuilder
from scripts.test.relnet.test_graph_components import MockSampleGraphComponentsProvider


class TestRelationGraphBuilder(unittest.TestCase):

    bcp = BuilderComponentsProvider({"a": {"1", "2"}, "b": {"2", "3"}}, {"r", "s"})
    b_1 = RelationGraphBuilder(None, None, "b_1", SampleSetBuilder(bcp, {}), bcp)
    o_1 = SampleGraphBuilder(bcp).set_name("o_1").build_single_node("a", "1")
    o_2 = SampleGraphBuilder(bcp).set_name("o_2").build_single_node("a", "2")

    def test_init(self):
        b_1 = RelationGraphBuilder(None, None, "b_1", SampleSetBuilder(self.bcp, {self.o_1: 1}), self.bcp)
        g_1 = b_1.build()
        self.assertEqual(g_1.variables, self.bcp.variables())
        self.assertEqual(g_1.relations, self.bcp.relations())
        self.assertEqual(g_1.name, "b_1")
        self.assertEqual(g_1.outcomes.length, 1)

        b_2 = RelationGraphBuilder({"a": {"1", "2"}}, {"r"})
        b_2.add_outcome(b_2.sample_builder().build_single_node("a", "2"))
        g_2 = b_2.build()
        self.assertEqual(g_2.variables, frozenset({("a", frozenset({"1", "2"}))}))
        self.assertEqual(g_2.relations,  frozenset({"r"}))
        self.assertEqual(g_2.name, "relation_graph_with_1_outcomes")
        self.assertEqual(g_2.outcomes.length, 1)

    def test_repr(self):
        self.assertEqual(
            str(RelationGraphBuilder(None, None, "b_1", SampleSetBuilder(self.bcp, {self.o_1: 5}), self.bcp)),
            "RelationGraphBuilder(name = b_1, len(outcomes) = 5)")

    def test_set_name(self):
        b_1 = RelationGraphBuilder(
            None, None, "b_1", SampleSetBuilder(self.bcp, {self.o_1: 1}), self.bcp).set_name("rg_123").build()
        self.assertEqual(b_1.name, "rg_123")

    def test_next_id(self):
        b_1 = RelationGraphBuilder({"a": {"1"}}, {"r"})
        self.assertEqual(b_1.next_id(), 1)
        self.assertEqual(b_1.next_id(), 2)
        self.assertEqual(b_1.next_id(), 3)

    def test_add_outcome(self):
        b_1 = RelationGraphBuilder(None, None, "b_1", SampleSetBuilder(self.bcp, {}), self.bcp)

        b_1.add_outcome(self.o_1)
        self.assertEqual(b_1.build().outcomes.items(), {(self.o_1, 1)})

        b_1.add_outcome(self.o_1)
        self.assertEqual(b_1.build().outcomes.items(), {(self.o_1, 2)})

        b_1.add_outcome(self.o_2)
        self.assertEqual(b_1.build().outcomes.items(), {(self.o_1, 2), (self.o_2, 1)})

        with self.assertRaises(AssertionError):  # Not compatible with this relation graph
            b_2 = RelationGraphBuilder({k: set(v) for k, v in self.bcp.variables()}, set(self.bcp.relations()))
            o_2 = b_2.sample_builder().build_single_node("a", "1")
            b_1.add_outcome(o_2)

        with self.assertRaises(AssertionError):  # Expect count be >= 1
            b_1.add_outcome(self.o_1, 0)

    def test_add_outcomes(self):
        b_1 = RelationGraphBuilder(None, None, "b_1", SampleSetBuilder(self.bcp, {}), self.bcp)
        b_1.add_outcomes([self.o_1, self.o_1, self.o_1])
        self.assertEqual(b_1.build().outcomes.items(), {(self.o_1, 3)})

    def test_sample_builder(self):
        sb_1 = self.b_1.sample_builder()
        s_1 = sb_1.build_single_node("a", "2")
        self.assertEqual(s_1.edges_set_view(), ("a", "2"))

    def test_build_sample(self):
        b_1 = RelationGraphBuilder(None, None, "b_1", SampleSetBuilder(self.bcp, {}), self.bcp)
        b_1.build_sample(lambda b: b.build_single_node("a", "2"))
        self.assertEqual(b_1.build().outcomes.length, 1)

    def test_generate_all_possible_outcomes(self):
        builders = [
            RelationGraphBuilder({"a": {"1"}}, {"r"}),
            RelationGraphBuilder({"a": {"1"}, "b": {"1"}}, {"r"}),
            RelationGraphBuilder({"a": {"1"}, "b": {"1"}}, {"r", "s"}),
            RelationGraphBuilder({"a": {"1"}, "b": {"1"}, "c": {"1"}}, {"r"}),
            RelationGraphBuilder({"a": {"1"}, "b": {"1"}, "c": {"1"}}, {"r", "s"}),
            RelationGraphBuilder({"a": {"1", "2"}}, {"r"}),
            RelationGraphBuilder({"a": {"1", "2"}, "b": {"1", "2"}}, {"r"}),
            RelationGraphBuilder({"a": {"1", "2"}, "b": {"1", "2"}}, {"r", "s"}),
            RelationGraphBuilder({"a": {"1", "2"}, "b": {"1"}}, {"r"})]

        generated_graphs = [b.generate_all_possible_outcomes().build().outcomes_as_edges_sets() for b in builders]

        expected_graphs = [
            frozenset({  # {"a": {"1"}}, {"r"}
                (("a", "1"), 1)}),
            frozenset({  # {"a": {"1"}, "b": {"1"}}, {"r"}
                (("a", "1"), 1),
                (("b", "1"), 1),
                (frozenset({(frozenset({("a", "1"), ("b", "1")}), "r")}), 1)}),
            frozenset({  # {"a": {"1"}, "b": {"1"}}, {"r", "s"}
                (("a", "1"), 1),
                (("b", "1"), 1),
                (frozenset({(frozenset({("a", "1"), ("b", "1")}), "r")}), 1),
                (frozenset({(frozenset({("a", "1"), ("b", "1")}), "s")}), 1)}),
            frozenset({  # {"a": {"1"}, "b": {"1"}, "c": {"1"}}, {"r"}
                (("a", "1"), 1),
                (("b", "1"), 1),
                (("c", "1"), 1),
                (frozenset({(frozenset({("b", "1"), ("a", "1")}), "r")}), 1),
                (frozenset({(frozenset({("c", "1"), ("b", "1")}), "r")}), 1),
                (frozenset({(frozenset({("c", "1"), ("a", "1")}), "r")}), 1),
                (frozenset({
                    (frozenset({("b", "1"), ("a", "1")}), "r"),
                    (frozenset({("c", "1"), ("b", "1")}), "r")}),
                 1),
                (frozenset({
                    (frozenset({("c", "1"), ("b", "1")}), "r"),
                    (frozenset({("c", "1"), ("a", "1")}), "r")}),
                 1),
                (frozenset({
                    (frozenset({("b", "1"), ("a", "1")}), "r"),
                    (frozenset({("c", "1"), ("a", "1")}), "r")}),
                 1),
                (frozenset({
                    (frozenset({("b", "1"), ("a", "1")}), "r"),
                    (frozenset({("c", "1"), ("b", "1")}), "r"),
                    (frozenset({("c", "1"), ("a", "1")}), "r")}),
                 1)}),
            frozenset({
                (("a", "1"), 1),
                (("b", "1"), 1),
                (("c", "1"), 1),
                (frozenset({(frozenset({("b", "1"), ("c", "1")}), "r")}), 1),
                (frozenset({(frozenset({("b", "1"), ("a", "1")}), "r")}), 1),
                (frozenset({(frozenset({("c", "1"), ("a", "1")}), "r")}), 1),
                (frozenset({(frozenset({("c", "1"), ("a", "1")}), "s")}), 1),
                (frozenset({(frozenset({("b", "1"), ("a", "1")}), "s")}), 1),
                (frozenset({(frozenset({("b", "1"), ("c", "1")}), "s")}), 1),
                (frozenset({
                    (frozenset({("b", "1"), ("c", "1")}), "r"),
                    (frozenset({("b", "1"), ("a", "1")}), "r")}),
                 1),
                (frozenset({
                    (frozenset({("b", "1"), ("c", "1")}), "r"),
                    (frozenset({("c", "1"), ("a", "1")}), "r")}),
                 1),
                (frozenset({
                    (frozenset({("c", "1"), ("a", "1")}), "r"),
                    (frozenset({("b", "1"), ("a", "1")}), "r")}),
                 1),
                (frozenset({
                    (frozenset({("c", "1"), ("a", "1")}), "s"),
                    (frozenset({("b", "1"), ("c", "1")}), "s")}),
                 1),
                (frozenset({
                    (frozenset({("c", "1"), ("a", "1")}), "s"),
                    (frozenset({("b", "1"), ("a", "1")}), "s")}),
                 1),
                (frozenset({
                    (frozenset({("b", "1"), ("c", "1")}), "s"),
                    (frozenset({("b", "1"), ("a", "1")}), "s")}),
                 1),
                (frozenset({
                    (frozenset({("c", "1"), ("a", "1")}), "s"),
                    (frozenset({("b", "1"), ("a", "1")}), "r")}),
                 1),
                (frozenset({
                    (frozenset({("b", "1"), ("a", "1")}), "s"),
                    (frozenset({("b", "1"), ("c", "1")}), "r")}),
                 1),
                (frozenset({
                    (frozenset({("b", "1"), ("c", "1")}), "s"),
                    (frozenset({("b", "1"), ("a", "1")}), "r")}),
                 1),
                (frozenset({
                    (frozenset({("b", "1"), ("c", "1")}), "s"),
                    (frozenset({("c", "1"), ("a", "1")}), "r")}),
                 1),
                (frozenset({
                    (frozenset({("b", "1"), ("a", "1")}), "s"),
                    (frozenset({("c", "1"), ("a", "1")}), "r")}),
                 1),
                (frozenset({
                    (frozenset({("c", "1"), ("a", "1")}), "s"),
                    (frozenset({("b", "1"), ("c", "1")}), "r")}),
                 1),
                (frozenset({
                    (frozenset({("b", "1"), ("c", "1")}), "r"),
                    (frozenset({("c", "1"), ("a", "1")}), "r"),
                    (frozenset({("b", "1"), ("a", "1")}), "r")}),
                 1),
                (frozenset({
                    (frozenset({("c", "1"), ("a", "1")}), "s"),
                    (frozenset({("b", "1"), ("a", "1")}), "s"),
                    (frozenset({("b", "1"), ("c", "1")}), "s")}),
                 1),
                (frozenset({
                    (frozenset({("b", "1"), ("c", "1")}), "s"),
                    (frozenset({("c", "1"), ("a", "1")}), "r"),
                    (frozenset({("b", "1"), ("a", "1")}), "r")}),
                 1),
                (frozenset({
                    (frozenset({("b", "1"), ("c", "1")}), "s"),
                    (frozenset({("b", "1"), ("a", "1")}), "s"),
                    (frozenset({("c", "1"), ("a", "1")}), "r")}),
                 1),
                (frozenset({
                    (frozenset({("c", "1"), ("a", "1")}), "s"),
                    (frozenset({("b", "1"), ("c", "1")}), "r"),
                    (frozenset({("b", "1"), ("a", "1")}), "r")}),
                 1),
                (frozenset({
                    (frozenset({("c", "1"), ("a", "1")}), "s"),
                    (frozenset({("b", "1"), ("a", "1")}), "s"),
                    (frozenset({("b", "1"), ("c", "1")}), "r")}),
                 1),
                (frozenset({
                    (frozenset({("b", "1"), ("c", "1")}), "r"),
                    (frozenset({("b", "1"), ("a", "1")}), "s"),
                    (frozenset({("c", "1"), ("a", "1")}), "r")}),
                 1),
                (frozenset({
                    (frozenset({("c", "1"), ("a", "1")}), "s"),
                    (frozenset({("b", "1"), ("c", "1")}), "s"),
                    (frozenset({("b", "1"), ("a", "1")}), "r")}),
                 1)}),
            frozenset({  # {"a": {"1", "2"}}, {"r"}
                (("a", "2"), 1),
                (("a", "1"), 1)}),
            frozenset({  # {"a": {"1", "2"}, "b": {"1", "2"}}, {"r"}
                (("a", "1"), 1),
                (("a", "2"), 1),
                (("b", "1"), 1),
                (("b", "2"), 1),
                (frozenset({(frozenset({("a", "1"), ("b", "1")}), "r")}), 1),
                (frozenset({(frozenset({("a", "1"), ("b", "2")}), "r")}), 1),
                (frozenset({(frozenset({("a", "2"), ("b", "1")}), "r")}), 1),
                (frozenset({(frozenset({("b", "2"), ("a", "2")}), "r")}), 1)}),
            frozenset({  # {"a": {"1", "2"}, "b": {"1", "2"}}, {"r", "s"}
                (("a", "1"), 1),
                (("a", "2"), 1),
                (("b", "1"), 1),
                (("b", "2"), 1),
                (frozenset({(frozenset({("a", "1"), ("b", "1")}), "r")}), 1),
                (frozenset({(frozenset({("a", "1"), ("b", "2")}), "r")}), 1),
                (frozenset({(frozenset({("a", "2"), ("b", "1")}), "r")}), 1),
                (frozenset({(frozenset({("a", "2"), ("b", "2")}), "r")}), 1),
                (frozenset({(frozenset({("a", "1"), ("b", "1")}), "s")}), 1),
                (frozenset({(frozenset({("a", "1"), ("b", "2")}), "s")}), 1),
                (frozenset({(frozenset({("a", "2"), ("b", "1")}), "s")}), 1),
                (frozenset({(frozenset({("a", "2"), ("b", "2")}), "s")}), 1)}),
            frozenset({
                (("a", "1"), 1),
                (("a", "2"), 1),
                (("b", "1"), 1),
                (frozenset({(frozenset({("b", "1"), ("a", "1")}), "r")}), 1),
                (frozenset({(frozenset({("a", "2"), ("b", "1")}), "r")}), 1)})]

        for generated, expected in zip(generated_graphs, expected_graphs):
            self.assertEqual(generated, expected)

    def test_build(self):
        b_1 = RelationGraphBuilder(None, None, "b_1", SampleSetBuilder(self.bcp, {self.o_1: 1}), self.bcp)
        self.assertEqual(b_1.build().outcomes.items(), {(self.o_1, 1)})
        with self.assertRaises(AssertionError):  # Expect count be >= 1
            b_2 = RelationGraphBuilder(None, None, "b_1", SampleSetBuilder(self.bcp, {}), self.bcp)
            b_2.build()


class TestRelationGraph(unittest.TestCase):

    bcp = BuilderComponentsProvider(
        {"a": {"1", "2"}, "b": {"2", "3"}, "c": {"3", "4"}, "d": {"4", "5"}},
        {"r", "s"})
    o_1 = SampleGraphBuilder(bcp).set_name("o_1").build_single_node("a", "1")
    o_2 = SampleGraphBuilder(bcp).set_name("o_2").build_single_node("a", "2")
    o_k_0 = SampleGraphBuilder(bcp).set_name("o_k_0").build_empty()
    rg_1 = RelationGraph(bcp, "rg_1", SampleSet(bcp, {o_1: 1, o_2: 2}))

    bcp_join = MockSampleGraphComponentsProvider(
        {"a": {"T", "F"}, "b": {"T", "F"}, "c": {"T", "F"}, "d": {"T", "F"}}, {"r", "s"})

    @staticmethod
    def sample_set(
            bcp_join: SampleGraphComponentsProvider, desc: List[Tuple[List[Tuple[str, str, str, str]], int]]
    ) -> SampleSet:
        ssb = SampleSetBuilder(bcp_join)
        for sample_edges, count in desc:
            sb = SampleGraphBuilder(bcp_join)
            for s_var, s_val, t_var, t_val in sample_edges:
                sb.add_relation({(s_var, s_val), (t_var, t_val)}, "r")
            ssb.add(sb.build(), count)
        return ssb.build()

    ab_samples = sample_set(bcp_join, [
        ([("a", "T", "b", "T")], 2),
        ([("a", "T", "b", "F")], 3),
        ([("a", "F", "b", "T")], 4),
        ([("a", "F", "b", "F")], 5)])

    bc_samples = sample_set(bcp_join, [
        ([("b", "T", "c", "T")], 6),
        ([("b", "T", "c", "F")], 7),
        ([("b", "F", "c", "T")], 8),
        ([("b", "F", "c", "F")], 9)])

    ca_samples = sample_set(bcp_join, [
        ([("c", "T", "a", "T")], 10),
        ([("c", "T", "a", "F")], 11),
        ([("c", "F", "a", "T")], 12),
        ([("c", "F", "a", "F")], 13)])

    bd_samples = sample_set(bcp_join, [
        ([("b", "T", "d", "T")], 14),
        ([("b", "T", "d", "F")], 15),
        ([("b", "F", "d", "T")], 16),
        ([("b", "F", "d", "F")], 17)])

    expected_ab_bc_joint_b = sample_set(bcp_join, [
        ([("a", "T", "b", "T"), ("b", "T", "c", "T")], 2 * 6),
        ([("a", "T", "b", "T"), ("b", "T", "c", "F")], 2 * 7),
        ([("a", "T", "b", "F"), ("b", "F", "c", "T")], 3 * 8),
        ([("a", "T", "b", "F"), ("b", "F", "c", "F")], 3 * 9),
        ([("a", "F", "b", "T"), ("b", "T", "c", "T")], 4 * 6),
        ([("a", "F", "b", "T"), ("b", "T", "c", "F")], 4 * 7),
        ([("a", "F", "b", "F"), ("b", "F", "c", "T")], 5 * 8),
        ([("a", "F", "b", "F"), ("b", "F", "c", "F")], 5 * 9)])

    expected_ab_bc_ca_joint_abc = sample_set(bcp_join, [  # Triangle
        ([("a", "T", "b", "T"), ("b", "T", "c", "T"), ("c", "T", "a", "T")], 2 * 6 * 10),
        ([("a", "T", "b", "T"), ("b", "T", "c", "F"), ("c", "F", "a", "T")], 2 * 7 * 12),
        ([("a", "T", "b", "F"), ("b", "F", "c", "T"), ("c", "T", "a", "T")], 3 * 8 * 10),
        ([("a", "T", "b", "F"), ("b", "F", "c", "F"), ("c", "F", "a", "T")], 3 * 9 * 12),
        ([("a", "F", "b", "T"), ("b", "T", "c", "T"), ("c", "T", "a", "F")], 4 * 6 * 11),
        ([("a", "F", "b", "T"), ("b", "T", "c", "F"), ("c", "F", "a", "F")], 4 * 7 * 13),
        ([("a", "F", "b", "F"), ("b", "F", "c", "T"), ("c", "T", "a", "F")], 5 * 8 * 11),
        ([("a", "F", "b", "F"), ("b", "F", "c", "F"), ("c", "F", "a", "F")], 5 * 9 * 13)])

    expected_ab_bc_bd_joint_abc = sample_set(bcp_join, [  # Star
        ([("a", "T", "b", "T"), ("b", "T", "c", "T"), ("b", "T", "d", "T")], 2 * 6 * 14),
        ([("a", "T", "b", "T"), ("b", "T", "c", "T"), ("b", "T", "d", "F")], 2 * 6 * 15),
        ([("a", "T", "b", "T"), ("b", "T", "c", "F"), ("b", "T", "d", "T")], 2 * 7 * 14),
        ([("a", "T", "b", "T"), ("b", "T", "c", "F"), ("b", "T", "d", "F")], 2 * 7 * 15),
        ([("a", "T", "b", "F"), ("b", "F", "c", "T"), ("b", "F", "d", "T")], 3 * 8 * 16),
        ([("a", "T", "b", "F"), ("b", "F", "c", "T"), ("b", "F", "d", "F")], 3 * 8 * 17),
        ([("a", "T", "b", "F"), ("b", "F", "c", "F"), ("b", "F", "d", "T")], 3 * 9 * 16),
        ([("a", "T", "b", "F"), ("b", "F", "c", "F"), ("b", "F", "d", "F")], 3 * 9 * 17),
        ([("a", "F", "b", "T"), ("b", "T", "c", "T"), ("b", "T", "d", "T")], 4 * 6 * 14),
        ([("a", "F", "b", "T"), ("b", "T", "c", "T"), ("b", "T", "d", "F")], 4 * 6 * 15),
        ([("a", "F", "b", "T"), ("b", "T", "c", "F"), ("b", "T", "d", "T")], 4 * 7 * 14),
        ([("a", "F", "b", "T"), ("b", "T", "c", "F"), ("b", "T", "d", "F")], 4 * 7 * 15),
        ([("a", "F", "b", "F"), ("b", "F", "c", "T"), ("b", "F", "d", "T")], 5 * 8 * 16),
        ([("a", "F", "b", "F"), ("b", "F", "c", "T"), ("b", "F", "d", "F")], 5 * 8 * 17),
        ([("a", "F", "b", "F"), ("b", "F", "c", "F"), ("b", "F", "d", "T")], 5 * 9 * 16),
        ([("a", "F", "b", "F"), ("b", "F", "c", "F"), ("b", "F", "d", "F")], 5 * 9 * 17)])

    def test_init(self):
        rg_1 = RelationGraph(self.bcp, "rg_1",  SampleSet(self.bcp, {self.o_1: 1,  self.o_2: 2}))
        self.assertEqual(rg_1.variables, self.bcp.variables())
        self.assertEqual(rg_1.relations, self.bcp.relations())
        self.assertEqual(rg_1.name, "rg_1")
        self.assertEqual(rg_1.outcomes.length, 3)
        self.assertEqual(rg_1.outcomes.items(), {(self.o_1, 1),  (self.o_2, 2)})

        rg_2 = RelationGraph(self.bcp, None,  SampleSet(self.bcp, {self.o_1: 1, self.o_2: 2}))
        self.assertEqual(rg_2.name, "relation_graph_with_3_outcomes")

    def test_describe(self):
        self.assertEqual(
            self.rg_1.describe(), {
                "name": "rg_1",
                "number_of_outcomes": 3,
                "number_of_relations": 2,
                "number_of_variables": 4,
                "relations": {"r", "s"},
                "variables": {"a", "b", "c", "d"}})

    def test_conditional_graph(self):
        o_1 = SampleGraphBuilder(self.bcp).set_name("o_1")\
            .build_single_node("b", "2")
        o_2 = SampleGraphBuilder(self.bcp).set_name("o_2")\
            .add_relation({("a", "1"), ("b", "2")}, "r")\
            .build()
        o_3 = SampleGraphBuilder(self.bcp).set_name("o_3") \
            .add_relation({("b", "2"), ("c", "3")}, "r") \
            .build()
        o_4 = SampleGraphBuilder(self.bcp).set_name("o_4") \
            .add_relation({("a", "1"), ("b", "2")}, "r") \
            .add_relation({("b", "2"), ("c", "3")}, "r") \
            .add_relation({("c", "3"), ("a", "2")}, "s") \
            .build()
        o_5 = SampleGraphBuilder(self.bcp).set_name("o_5") \
            .add_relation({("c", "3"), ("a", "1")}, "s") \
            .build()

        rg_1 = RelationGraph(self.bcp, "rg_1",  SampleSet(self.bcp, {o_1: 1, o_2: 2, o_3: 3, o_4: 4, o_5: 5}))

        q_1 = SampleGraphBuilder(self.bcp).set_name("q_1") \
            .build_single_node("b", "2")
        q_2 = SampleGraphBuilder(self.bcp).set_name("q_2") \
            .add_relation({("a", "1"), ("b", "2")}, "r") \
            .build()
        q_3 = SampleGraphBuilder(self.bcp).set_name("q_3") \
            .add_relation({("b", "2"), ("c", "3")}, "r") \
            .build()
        q_4 = SampleGraphBuilder(self.bcp).set_name("q_4") \
            .add_relation({("c", "3"), ("a", "1")}, "s") \
            .build()

        ig_1 = rg_1.conditional_graph(q_1, "ig_1")

        self.assertEqual(ig_1.name, "ig_1")

        self.assertEqual(
            ig_1.outcomes.items(),
            {(o_1, 1), (o_2, 2), (o_3, 3), (o_4, 4), (o_5, 5)})

        self.assertEqual(
            rg_1.conditional_graph(q_2).outcomes.items(),
            {(o_2, 2), (o_4, 4)})

        self.assertEqual(
            rg_1.conditional_graph(q_3).outcomes.items(),
            {(o_3, 3), (o_4, 4)})

        self.assertEqual(
            rg_1.conditional_graph(q_4).outcomes.items(),
            {(o_5, 5), (o_1, 1)})

    def test_joined_on_variables(self):
        ab_bc_ss = RelationGraph(self.bcp_join, None, self.ab_samples.union(self.bc_samples))

        ab_bc_joint_a = ab_bc_ss.joined_on_variables({"b"}).outcomes
        self.assertEqual(ab_bc_joint_a.length, 214)
        self.assertEqual(ab_bc_joint_a, self.expected_ab_bc_joint_b)

        ab_bc_joint_abc = ab_bc_ss.joined_on_variables({"a", "b", "c"}).outcomes
        self.assertEqual(ab_bc_joint_abc, self.expected_ab_bc_joint_b)

        ab_bc_joint_none = ab_bc_ss.joined_on_variables().outcomes
        self.assertEqual(ab_bc_joint_none, self.expected_ab_bc_joint_b)

        ab_bc_joint_empty = ab_bc_ss.joined_on_variables(set({})).outcomes
        self.assertEqual(ab_bc_joint_empty, self.ab_samples.union(self.bc_samples))

        exe_ab_bc_ca_joint_b = self.expected_ab_bc_joint_b.union(self.ca_samples)

        ab_bc_ca_ss = RelationGraph(self.bcp_join, None, self.ab_samples.union(self.bc_samples).union(self.ca_samples))

        self.assertEqual(ab_bc_ca_ss.joined_on_variables({"b"}).outcomes, exe_ab_bc_ca_joint_b)
        self.assertEqual(ab_bc_ca_ss.joined_on_variables({"a", "b"}).outcomes, self.expected_ab_bc_ca_joint_abc)
        self.assertEqual(ab_bc_ca_ss.joined_on_variables({"a", "b", "c"}).outcomes, self.expected_ab_bc_ca_joint_abc)

        ab_bc_bd_ss = RelationGraph(self.bcp_join, None, self.ab_samples.union(self.bc_samples).union(self.bd_samples))

        self.assertEqual(ab_bc_bd_ss.joined_on_variables({"b"}).outcomes, self.expected_ab_bc_bd_joint_abc)
        self.assertEqual(ab_bc_bd_ss.joined_on_variables({"a", "b"}).outcomes, self.expected_ab_bc_bd_joint_abc)
        self.assertEqual(ab_bc_bd_ss.joined_on_variables({"a", "b", "c"}).outcomes, self.expected_ab_bc_bd_joint_abc)

    def test_is_joined(self):
        o_3 = SampleGraphBuilder(self.bcp).set_name("o_3").build_single_node("b", "3")

        self.assertTrue(
            RelationGraph(self.bcp, "rg_1", SampleSet(self.bcp, {self.o_1: 1, self.o_2: 2})).is_joined())
        self.assertFalse(
            RelationGraph(self.bcp, "rg_2", SampleSet(self.bcp, {self.o_1: 1, o_3: 3})).is_joined())

    def test_is_factorized(self):
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

        self.assertTrue(
            RelationGraph(self.bcp, "rg_1", SampleSet(self.bcp, {o_ab_1: 1, o_ab_2: 2})).is_factorized())
        self.assertTrue(
            RelationGraph(self.bcp, "rg_2", SampleSet(self.bcp, {o_ab_1: 1, o_bc: 2})).is_factorized())
        self.assertTrue(
            RelationGraph(self.bcp, "rg_3", SampleSet(self.bcp, {o_abc: 1})).is_factorized())
        self.assertFalse(
            RelationGraph(self.bcp, "rg_4", SampleSet(self.bcp, {o_ab_1: 1, o_abc: 2})).is_factorized())
        self.assertFalse(
            RelationGraph(self.bcp, "rg_5", SampleSet(self.bcp, {self.o_k_0: 1, o_abc: 2})).is_factorized())

    def test_make_joined(self):
        rg_empty = RelationGraph(self.bcp_join, None, SampleSetBuilder(self.bcp_join).empty())
        rg_empty_joined = rg_empty.make_joined()
        self.assertEqual(rg_empty.outcomes, rg_empty_joined.outcomes)

        ab_bc_ss = RelationGraph(self.bcp_join, None, self.ab_samples.union(self.bc_samples))
        ab_bc_joint_a = ab_bc_ss.make_joined().outcomes
        self.assertEqual(ab_bc_joint_a.length, 214)
        self.assertEqual(ab_bc_joint_a, self.expected_ab_bc_joint_b)

        ab_bc_ca_ss = RelationGraph(self.bcp_join, None, self.ab_samples.union(self.bc_samples).union(self.ca_samples))
        self.assertEqual(ab_bc_ca_ss.make_joined().outcomes, self.expected_ab_bc_ca_joint_abc)

        ab_bc_bd_ss = RelationGraph(self.bcp_join, None, self.ab_samples.union(self.bc_samples).union(self.bd_samples))
        self.assertEqual(ab_bc_bd_ss.make_joined().outcomes, self.expected_ab_bc_bd_joint_abc)


if __name__ == '__main__':
    unittest.main()
