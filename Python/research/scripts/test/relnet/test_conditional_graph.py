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

from scripts.relnet.activation_graph import ActiveNode, ActiveEdge
from scripts.relnet.conditional_graph import ConditionalGraph
from scripts.relnet.relation_graph import BuilderComponentsProvider
from scripts.relnet.sample_graph import SampleGraphBuilder
from scripts.relnet.sample_space import SampleSet


class TestConditionalGraph(unittest.TestCase):

    bcp = BuilderComponentsProvider({"a": {"1", "2"}, "b": {"2", "3"}, "c": {"3", "4"}, "d": {"4", "5"}}, {"r", "s"})
    s_1 = SampleGraphBuilder(bcp) \
        .build_single_node("a", "1")
    s_2 = SampleGraphBuilder(bcp) \
        .add_relation({("a", "1"), ("b", "2")}, "r") \
        .build()
    ig_1 = ConditionalGraph(bcp, s_1, "ig_1", SampleSet(bcp, {s_1: 1, s_2: 2}))

    def test_init(self):
        self.assertEqual(self.ig_1.evidence, self.s_1)
        self.assertEqual(self.ig_1.outcomes.length, 3)

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

        s_1_1_sim = s_1.similarity(s_1)  # =1
        s_1_2_sim = s_1.similarity(s_2)
        s_1_3_sim = s_1.similarity(s_3)
        s_1_4_sim = s_1.similarity(s_4)

        q_1_1_weight = ((1 * s_1_1_sim) + (1 * 2) + (1 * 3) + (1 * 4)) / 10
        q_1_b_weight = ((s_1_2_sim * 2) + (s_1_3_sim * 3) + (s_1_4_sim * 4)) / 10
        q_1_c_weight = ((s_1_3_sim * 3) + (s_1_4_sim * 4)) / 10
        q_1_d_weight = (s_1_4_sim * 4) / 10

        ag_1 = ConditionalGraph(self.bcp, s_1, "ig_1", SampleSet(self.bcp, {s_1: 1, s_2: 2, s_3: 3, s_4: 4}))\
            .activation_graph(name="ag_1")

        self.assertEqual(ag_1.name, "ag_1")
        self.assertEqual(ag_1.number_of_outcomes, 10)

        self.assertEqual(set(ag_1.nodes), {
            ActiveNode("a", {"1": q_1_1_weight, "2": 0}, in_query=True),
            ActiveNode("b", {"2": q_1_b_weight, "3": 0}, in_query=False),
            ActiveNode("c", {"3": q_1_c_weight, "4": 0}, in_query=False),
            ActiveNode("d", {"4": q_1_d_weight, "5": 0}, in_query=False),
        })

        self.assertEqual(set(ag_1.edges), {
            ActiveEdge({"b", "a"}, {"r": 9}, in_query=False),
            ActiveEdge({"c", "b"}, {"s": 7}, in_query=False),
            ActiveEdge({"d", "c"}, {"r": 4}, in_query=False),
        })

        ag_2 = ConditionalGraph(self.bcp, s_2, "ig_2", SampleSet(self.bcp, {s_2: 2, s_3: 3, s_4: 4})).activation_graph()

        self.assertEqual(set(ag_2.nodes), {
            ActiveNode("a", {"1": 1.0, "2": 0}, in_query=True),
            ActiveNode("b", {"2": 1.0, "3": 0}, in_query=True),
            ActiveNode("c", {"3": 0.3904761904761905, "4": 0}, in_query=False),
            ActiveNode("d", {"4": 0.19047619047619047, "5": 0}, in_query=False),
        })

        self.assertEqual(set(ag_2.edges), {
            ActiveEdge({"b", "a"}, {"r": 9}, in_query=True),
            ActiveEdge({"c", "b"}, {"s": 7}, in_query=False),
            ActiveEdge({"d", "c"}, {"r": 4}, in_query=False),
        })

        ag_3 = ConditionalGraph(self.bcp, s_3, "ig_3", SampleSet(self.bcp, {s_3: 3, s_4: 4})).activation_graph()

        self.assertEqual(set(ag_3.nodes), {
            ActiveNode("a", {"1": 1.0, "2": 0}, in_query=True),
            ActiveNode("b", {"2": 1.0, "3": 0}, in_query=True),
            ActiveNode("c", {"3": 1.0, "4": 0}, in_query=True),
            ActiveNode("d", {"4": 0.40816326530612246, "5": 0}, in_query=False),
        })

        self.assertEqual(set(ag_3.edges), {
            ActiveEdge({"b", "a"}, {"r": 7}, in_query=True),
            ActiveEdge({"c", "b"}, {"s": 7}, in_query=True),
            ActiveEdge({"d", "c"}, {"r": 4}, in_query=False),
        })

        ag_4 = ConditionalGraph(self.bcp, s_4, "ig_4", SampleSet(self.bcp, {s_4: 4})).activation_graph()

        self.assertEqual(set(ag_4.nodes), {
            ActiveNode("a", {"1": 1.0, "2": 0}, in_query=True),
            ActiveNode("b", {"2": 1.0, "3": 0}, in_query=True),
            ActiveNode("c", {"3": 1.0, "4": 0}, in_query=True),
            ActiveNode("d", {"4": 1.0, "5": 0}, in_query=True),
        })

        self.assertEqual(set(ag_4.edges), {
            ActiveEdge({"b", "a"}, {"r": 4}, in_query=True),
            ActiveEdge({"c", "b"}, {"s": 4}, in_query=True),
            ActiveEdge({"d", "c"}, {"r": 4}, in_query=True),
        })

        ag_5 = ConditionalGraph(self.bcp, s_1, "ig_1", SampleSet(self.bcp, {s_1: 1, s_2: 2, s_3: 3, s_4: 4}))\
            .activation_graph({"r"})

        self.assertEqual(set(ag_5.nodes), {
            ActiveNode("a", {"1": 1.0, "2": 0}, in_query=True),
            ActiveNode("b", {"2": 0.1838095238095238, "3": 0}, in_query=False),
            ActiveNode("c", {"3": 0, "4": 0}, in_query=False),
            ActiveNode("d", {"4": 0, "5": 0}, in_query=False),
        })

        self.assertEqual(set(ag_5.edges), {
            ActiveEdge({"b", "a"}, {"r": 9}, in_query=False),
        })


if __name__ == '__main__':
    unittest.main()
