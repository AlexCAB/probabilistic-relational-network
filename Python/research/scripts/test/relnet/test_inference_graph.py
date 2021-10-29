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
created: 2021-10-28
"""

import unittest

from scripts.relnet.inference_graph import InferenceGraph, ActiveValue, ActiveRelation
from scripts.relnet.relation_graph import BuilderComponentsProvider
from scripts.relnet.sample_graph import SampleGraphBuilder


class TestActiveRelation(unittest.TestCase):

    ar_1 = ActiveRelation("var", "val", "rel", 123)

    def test_init(self):
        self.assertEqual(self.ar_1.linked_variable, "var")
        self.assertEqual(self.ar_1.linked_value, "val")
        self.assertEqual(self.ar_1.relation, "rel")
        self.assertEqual(self.ar_1.count, 123)

    def test_hash(self):
        self.assertEqual(self.ar_1.__hash__(), ("var", "val", "rel", 123).__hash__())


class TestActiveValue(unittest.TestCase):
    ar_1 = ActiveRelation("var", "val", "rel", 123)
    av_1 = ActiveValue("var", "val", 0.1, frozenset({ar_1}))

    def test_init(self):
        self.assertEqual(self.av_1.variable, "var")
        self.assertEqual(self.av_1.value, "val")
        self.assertEqual(self.av_1.weight, 0.1)
        self.assertEqual(self.av_1.active_relations, frozenset({self.ar_1}))

    def test_hash(self):
        self.assertEqual(self.av_1.__hash__(), ("var", "val", 0.1, frozenset({self.ar_1})).__hash__())


class TestInferenceGraph(unittest.TestCase):

    bcp = BuilderComponentsProvider({"a": {"1", "2"}, "b": {"2", "3"}, "c": {"3", "4"}, "d": {"4", "5"}}, {"r", "s"})
    s_1 = SampleGraphBuilder(bcp) \
        .build_single_node("a", "1")
    s_2 = SampleGraphBuilder(bcp) \
        .add_relation({("a", "1"), ("b", "2")}, "r") \
        .build()
    ig_1 = InferenceGraph(bcp, s_1, "ig_1", {s_1: 1, s_2: 2})

    def test_init(self):
        self.assertEqual(self.ig_1.query, self.s_1)
        self.assertEqual(self.ig_1.number_of_outcomes, 3)

    def test_repr(self):
        self.assertEqual(str(self.ig_1), "ig_1")

    def test_builder(self):
        rg_1 = self.ig_1.builder().set_name("rg_1").build()
        self.assertEqual(rg_1.variables, self.bcp.variables())
        self.assertEqual(rg_1.relations, self.bcp.relations())
        self.assertEqual(rg_1.number_of_outcomes, 3)
        self.assertEqual(rg_1.name, "rg_1")
        self.assertEqual(rg_1.outcomes(), frozenset({(self.s_1, 1), (self.s_2, 2)}))

    def test_describe(self):
        self.assertEqual(self.ig_1.describe(), {
            "included_relations": {"r"},
            "included_variables": {"b", "a"},
            "number_outcomes": 3,
            "query": "{(a_1)}"
        })

    def test_active_values(self):
        s_1 = SampleGraphBuilder(self.bcp)\
            .build_single_node("a", "1")
        s_2 = SampleGraphBuilder(self.bcp) \
            .add_relation({("a", "1"), ("b", "2")}, "r") \
            .build()
        s_3 = SampleGraphBuilder(self.bcp) \
            .add_relation({("a", "1"), ("b", "2")}, "r") \
            .add_relation({("b", "2"), ("c", "3")}, "s") \
            .build()
        s_4 = SampleGraphBuilder(self.bcp) \
            .add_relation({("a", "1"), ("b", "2")}, "r") \
            .add_relation({("b", "2"), ("c", "3")}, "s") \
            .add_relation({("c", "3"), ("d", "4")}, "r") \
            .build()

        s_1_2_sim = s_1.similarity(s_2)
        s_1_3_sim = s_1.similarity(s_3)
        s_1_4_sim = s_1.similarity(s_4)

        q_1_b_weight = (s_1_2_sim * 2) + (s_1_3_sim * 3) + (s_1_4_sim * 4)
        q_1_c_weight = (s_1_3_sim * 3) + (s_1_4_sim * 4)
        q_1_d_weight = (s_1_4_sim * 4)

        self.assertEqual(
            InferenceGraph(self.bcp, s_1, "ig_1", {s_1: 1, s_2: 2, s_3: 3, s_4: 4}).active_values(), [
                ActiveValue("b", "2", q_1_b_weight, frozenset({ActiveRelation("a", "1", "r", count=9)})),
                ActiveValue("c", "3", q_1_c_weight, frozenset({ActiveRelation("b", "2", "s", count=7)})),
                ActiveValue("d", "4", q_1_d_weight, frozenset({ActiveRelation("c", "3", "r", count=4)}))])

        self.assertEqual(
            InferenceGraph(self.bcp, s_2, "ig_2", {s_2: 2, s_3: 3, s_4: 4}).active_values(), [
                ActiveValue("c", "3", 3.5142857142857142, frozenset({ActiveRelation("b", "2",  "s", count=7)})),
                ActiveValue("d", "4", 1.7142857142857142, frozenset({ActiveRelation("c", "3",  "r", count=4)}))])

        self.assertEqual(
            InferenceGraph(self.bcp, s_3, "ig_3", {s_3: 3, s_4: 4}).active_values(), [
                ActiveValue("d", "4", 2.857142857142857, frozenset({ActiveRelation("c", "3",  "r", count=4)}))])

        self.assertEqual(
            InferenceGraph(self.bcp, s_4, "ig_4", {s_4: 4}).active_values(),
            [])  # No values not in query

        self.assertEqual(
            InferenceGraph(self.bcp, s_1, "ig_1", {s_1: 1, s_2: 2, s_3: 3, s_4: 4}).active_values({"r"}), [
                ActiveValue("b", "2", 1.838095238095238, frozenset({ActiveRelation("a", "1", "r", count=9)}))])


if __name__ == '__main__':
    unittest.main()
