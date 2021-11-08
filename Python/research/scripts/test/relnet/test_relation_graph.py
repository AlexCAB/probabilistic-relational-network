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
from copy import copy

from scripts.relnet.relation_graph import BuilderComponentsProvider, RelationGraphBuilder, RelationGraph
from scripts.relnet.sample_graph import ValueNode, SampleGraphBuilder, DirectedRelation


class TestBuilderComponentsProvider(unittest.TestCase):

    b_1 = BuilderComponentsProvider({"a": {"1", "2"}, "b": {"2", "3"}}, {"r", "s"})

    def test_init(self):
        b = BuilderComponentsProvider({"a": {"1", "2"}}, {"r"})

        self.assertEqual(b.variables(), frozenset({("a", frozenset({"1", "2"}))}))
        self.assertEqual(b.relations(), frozenset({"r"}))
        self.assertEqual(b.nodes, {})
        self.assertEqual(b.edges, {})

        with self.assertRaises(AssertionError):  # Empty set of variables
            BuilderComponentsProvider({}, {"r"})
        with self.assertRaises(AssertionError):  # Empty variable values
            BuilderComponentsProvider({"a": set({})}, {"r"})
        with self.assertRaises(AssertionError):  # Empty set of relations
            BuilderComponentsProvider({"a": {"1", "2"}}, set({}))

    def test_variables(self):
        self.assertEqual(
            self.b_1.variables(),
            frozenset({("a", frozenset({"1", "2"})), ("b", frozenset({"2", "3"}))}))

    def test_relations(self):
        self.assertEqual(self.b_1.relations(), frozenset({"r", "s"}))

    def test_get_node(self):
        n_1 = self.b_1.get_node("a", "1")
        self.assertEqual(n_1.variable, "a")
        self.assertEqual(n_1.value, "1")

        n_2 = self.b_1.get_node("a", "1")
        self.assertEqual(n_2.variable, "a")
        self.assertEqual(n_2.value, "1")
        self.assertEqual(id(n_1), id(n_2))

        n_3 = self.b_1.get_node("a", "2")
        self.assertEqual(n_3.variable, "a")
        self.assertEqual(n_3.value, "2")
        self.assertNotEqual(id(n_1), id(n_3))

        with self.assertRaises(AssertionError):  # Unknown variable
            self.b_1.get_node("unknown_variable", "1")
        with self.assertRaises(AssertionError):  # Unknown value
            self.b_1.get_node("a", "unknown_value")

    def test_get_edge(self):
        n_1 = self.b_1.get_node("a", "1")
        n_2 = self.b_1.get_node("b", "2")

        e_1 = self.b_1.get_edge(frozenset({n_1, n_2}), "r")
        self.assertEqual(e_1.endpoints, frozenset({n_1, n_2}))
        self.assertEqual(e_1.relation, "r")

        e_2 = self.b_1.get_edge(frozenset({n_1, n_2}), "r")
        self.assertEqual(e_2.endpoints, frozenset({n_1, n_2}))
        self.assertEqual(e_2.relation, "r")
        self.assertEqual(id(e_1), id(e_2))

        e_3 = self.b_1.get_edge(frozenset({n_1, n_2}), "s")
        self.assertEqual(e_3.endpoints, frozenset({n_1, n_2}))
        self.assertEqual(e_3.relation, "s")
        self.assertNotEqual(id(e_1), id(e_3))

        n_3 = self.b_1.get_node("b", "3")

        e_4 = self.b_1.get_edge(frozenset({n_1, n_3}), "r")
        self.assertEqual(e_4.endpoints, frozenset({n_1, n_3}))
        self.assertEqual(e_4.relation, "r")
        self.assertNotEqual(id(e_1), id(e_4))

        dr_1 = DirectedRelation("a", "b", "r")
        e_5 = self.b_1.get_edge(frozenset({n_1, n_2}), dr_1)
        self.assertEqual(e_5.endpoints, frozenset({n_1, n_2}))
        self.assertEqual(e_5.relation, dr_1)
        self.assertNotEqual(id(e_1), id(e_5))

        with self.assertRaises(AssertionError):  # Unknown endpoint node
            self.b_1.get_edge(frozenset({n_1, ValueNode("a", "2")}), "r")
        with self.assertRaises(AssertionError):  # Unknown relation
            self.b_1.get_edge(frozenset({n_1, n_2}), "unknown_relation")
        with self.assertRaises(AssertionError):  # Unknown directed relation
            self.b_1.get_edge(frozenset({n_1, n_2}),  DirectedRelation("a", "b", "unknown_relation"))
        with self.assertRaises(AssertionError):  # Unknown directed source variable
            self.b_1.get_edge(frozenset({n_1, n_2}),  DirectedRelation("unknown_variable", "b", "r"))
        with self.assertRaises(AssertionError):  # Unknown directed target variable
            self.b_1.get_edge(frozenset({n_1, n_2}),  DirectedRelation("a", "unknown_variable", "r"))


class TestRelationGraphBuilder(unittest.TestCase):

    bcp = BuilderComponentsProvider({"a": {"1", "2"}, "b": {"2", "3"}}, {"r", "s"})
    b_1 = RelationGraphBuilder(None, None, "b_1", {}, bcp)
    o_1 = SampleGraphBuilder(bcp).set_name("o_1").build_single_node("a", "1")
    o_2 = SampleGraphBuilder(bcp).set_name("o_2").build_single_node("a", "2")

    def test_init(self):
        b_1 = RelationGraphBuilder(None, None, "b_1", {self.o_1: 1}, self.bcp)
        g_1 = b_1.build()
        self.assertEqual(g_1.variables, self.bcp.variables())
        self.assertEqual(g_1.relations, self.bcp.relations())
        self.assertEqual(g_1.name, "b_1")
        self.assertEqual(g_1.number_of_outcomes, 1)

        b_2 = RelationGraphBuilder({"a": {"1", "2"}}, {"r"})
        b_2.add_outcome(b_2.sample_builder().build_single_node("a", "2"))
        g_2 = b_2.build()
        self.assertEqual(g_2.variables, frozenset({("a", frozenset({"1", "2"}))}))
        self.assertEqual(g_2.relations,  frozenset({"r"}))
        self.assertEqual(g_2.name, "relation_graph_with_1_outcomes")
        self.assertEqual(g_2.number_of_outcomes, 1)

    def test_repr(self):
        self.assertEqual(
            str(RelationGraphBuilder(None, None, "b_1", {self.o_1: 5}, self.bcp)),
            "RelationGraphBuilder(name = b_1, len(outcomes) = 1)")

    def test_set_name(self):
        b_1 = RelationGraphBuilder(None, None, "b_1", {self.o_1: 1}, self.bcp).set_name("rg_123").build()
        self.assertEqual(b_1.name, "rg_123")

    def test_next_id(self):
        b_1 = RelationGraphBuilder({"a": {"1"}}, {"r"})
        self.assertEqual(b_1.next_id(), 1)
        self.assertEqual(b_1.next_id(), 2)
        self.assertEqual(b_1.next_id(), 3)

    def test_add_outcome(self):
        b_1 = RelationGraphBuilder(None, None, "b_1", {}, self.bcp)

        b_1.add_outcome(self.o_1)
        self.assertEqual(b_1.build().outcomes(), frozenset({(self.o_1, 1)}))

        b_1.add_outcome(self.o_1)
        self.assertEqual(b_1.build().outcomes(), frozenset({(self.o_1, 2)}))

        b_1.add_outcome(self.o_2)
        self.assertEqual(b_1.build().outcomes(), frozenset({(self.o_1, 2), (self.o_2, 1)}))

        with self.assertRaises(AssertionError):  # Not compatible with this relation graph
            b_2 = RelationGraphBuilder({k: set(v) for k, v in self.bcp.variables()}, set(self.bcp.relations()))
            o_2 = b_2.sample_builder().build_single_node("a", "1")
            b_1.add_outcome(o_2)

        with self.assertRaises(AssertionError):  # Expect count be >= 1
            b_1.add_outcome(self.o_1, 0)

    def test_add_outcomes(self):
        b_1 = RelationGraphBuilder(None, None, "b_1", {}, self.bcp)
        b_1.add_outcomes([self.o_1, self.o_1, self.o_1])
        self.assertEqual(b_1.build().outcomes(), frozenset({(self.o_1, 3)}))

    def test_sample_builder(self):
        sb_1 = self.b_1.sample_builder()
        s_1 = sb_1.build_single_node("a", "2")
        self.assertEqual(s_1.edges_set_view(), ("a", "2"))

    def test_build_sample(self):
        b_1 = RelationGraphBuilder(None, None, "b_1", {}, self.bcp)
        b_1.build_sample(lambda b: b.build_single_node("a", "2"))
        self.assertEqual(b_1.build().number_of_outcomes, 1)

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
        b_1 = RelationGraphBuilder(None, None, "b_1", {self.o_1: 1}, self.bcp)
        self.assertEqual(b_1.build().outcomes(), frozenset({(self.o_1, 1)}))
        with self.assertRaises(AssertionError):  # Expect count be >= 1
            b_2 = RelationGraphBuilder(None, None, "b_1", {}, self.bcp)
            b_2.build()


class TestRelationGraph(unittest.TestCase):

    bcp = BuilderComponentsProvider(
        {"a": {"1", "2"}, "b": {"2", "3"}, "c": {"3", "4"}, "d": {"4", "5"}},
        {"r", "s"})
    o_1 = SampleGraphBuilder(bcp).set_name("o_1").build_single_node("a", "1")
    o_2 = SampleGraphBuilder(bcp).set_name("o_2").build_single_node("a", "2")
    rg_1 = RelationGraph(bcp, "rg_1", {o_1: 1, o_2: 2})

    def test_init(self):
        rg_1 = RelationGraph(self.bcp, "rg_1", {self.o_1: 1,  self.o_2: 2})
        self.assertEqual(rg_1.variables, self.bcp.variables())
        self.assertEqual(rg_1.relations, self.bcp.relations())
        self.assertEqual(rg_1.name, "rg_1")
        self.assertEqual(rg_1.number_of_outcomes, 3)
        self.assertEqual(rg_1.outcomes(), frozenset({(self.o_1, 1),  (self.o_2, 2)}))

        rg_2 = RelationGraph(self.bcp, None, {self.o_1: 1, self.o_2: 2})
        self.assertEqual(rg_2.name, "relation_graph_with_3_outcomes")

    def test_repr(self):
        self.assertEqual(str(self.rg_1), "rg_1")

    def test_builder(self):
        b_1 = self.rg_1.builder()
        o_3 = SampleGraphBuilder(self.bcp).set_name("o_3").build_single_node("b", "2")
        b_1.add_outcome(o_3)
        rg_2 = b_1.build()
        self.assertEqual(rg_2.outcomes(), frozenset({(self.o_1, 1), (self.o_2, 2), (o_3, 1)}))

    def test_describe(self):
        self.assertEqual(
            self.rg_1.describe(), {
                "name": "rg_1",
                "number_of_outcomes": 3,
                "number_of_relations": 2,
                "number_of_variables": 4,
                "relations": {"r", "s"},
                "variables": {"a", "b", "c", "d"}})

    def test_inference(self):
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

        rg_1 = RelationGraph(self.bcp, "rg_1", {o_1: 1, o_2: 2, o_3: 3, o_4: 4, o_5: 5})

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

        ig_1 = rg_1.inference(q_1, "ig_1")

        self.assertEqual(ig_1.name, "ig_1")

        self.assertEqual(
            ig_1.outcomes(),
            frozenset({(o_1, 1), (o_2, 2), (o_3, 3), (o_4, 4)}))

        self.assertEqual(
            rg_1.inference(q_2).outcomes(),
            frozenset({(o_2, 2), (o_4, 4)}))

        self.assertEqual(
            rg_1.inference(q_3).outcomes(),
            frozenset({(o_3, 3), (o_4, 4)}))

        self.assertEqual(
            rg_1.inference(q_4).outcomes(),
            frozenset({(o_5, 5)}))

    def test_joined_on_variables(self):
        o_11 = SampleGraphBuilder(self.bcp).set_name("o_11") \
            .add_relation({("a", "1"), ("b", "2")}, "r") \
            .add_relation({("b", "2"), ("c", "3")}, "r") \
            .build()
        o_12 = SampleGraphBuilder(self.bcp).set_name("o_12") \
            .add_relation({("b", "2"), ("c", "3")}, "r") \
            .add_relation({("c", "3"), ("d", "4")}, "r") \
            .build()

        rg_1 = RelationGraph(self.bcp, "rg_1", {o_11: 2, o_12: 3})
        jg_1 = rg_1.joined_on_variables({"b", "c"}, "jg_1")

        self.assertEqual(jg_1.name, "jg_1")
        self.assertEqual(
            jg_1.outcomes(), frozenset({
                (SampleGraphBuilder(self.bcp)
                 .add_relation({("a", "1"), ("b", "2")}, "r")
                 .add_relation({("b", "2"), ("c", "3")}, "r")
                 .add_relation({("c", "3"), ("d", "4")}, "r")
                 .build(), 6)}))

        o_21 = SampleGraphBuilder(self.bcp).set_name("o_21") \
            .add_relation({("a", "1"), ("b", "2")}, "s") \
            .add_relation({("b", "2"), ("c", "3")}, "r") \
            .build()
        o_22 = SampleGraphBuilder(self.bcp).set_name("o_22") \
            .add_relation({("a", "1"), ("b", "2")}, "s") \
            .build()
        o_23 = SampleGraphBuilder(self.bcp).set_name("o_23") \
            .add_relation({("a", "1"), ("b", "2")}, "r") \
            .add_relation({("b", "2"), ("c", "3")}, "r") \
            .build()
        o_24 = SampleGraphBuilder(self.bcp).set_name("o_24") \
            .add_relation({("a", "1"), ("b", "2")}, "r") \
            .build()

        rg_2 = RelationGraph(self.bcp, "rg_2", {o_21: 2, o_22: 3, o_23: 4, o_24: 5})

        self.assertEqual(
            rg_2.joined_on_variables({"a", "b"}, "jg_2").outcomes(), frozenset({
                (SampleGraphBuilder(self.bcp)
                 .add_relation({("a", "1"), ("b", "2")}, "s")
                 .add_relation({("b", "2"), ("c", "3")}, "r")
                 .build(), 6),
                (SampleGraphBuilder(self.bcp)
                 .add_relation({("a", "1"), ("b", "2")}, "r")
                 .add_relation({("b", "2"), ("c", "3")}, "r")
                 .build(), 20)}))

        o_31 = SampleGraphBuilder(self.bcp).set_name("o_31") \
            .add_relation({("a", "1"), ("b", "2")}, "r") \
            .add_relation({("b", "2"), ("c", "3")}, "r") \
            .build()
        o_32 = SampleGraphBuilder(self.bcp).set_name("o_32") \
            .add_relation({("a", "1"), ("b", "2")}, "r") \
            .build()
        o_33 = SampleGraphBuilder(self.bcp).set_name("o_33") \
            .add_relation({("a", "1"), ("b", "2")}, "r") \
            .add_relation({("b", "2"), ("c", "3")}, "s") \
            .build()
        o_34 = SampleGraphBuilder(self.bcp).set_name("o_34") \
            .add_relation({("a", "1"), ("b", "2")}, "r") \
            .add_relation({("b", "2"), ("c", "3")}, "s") \
            .add_relation({("c", "3"), ("d", "4")}, "r") \
            .build()

        rg_3 = RelationGraph(self.bcp, "rg_3", {o_31: 2, o_32: 3, o_33: 4, o_34: 5})

        self.assertEqual(
            rg_3.joined_on_variables({"a", "b"}, "jg_3").outcomes(), frozenset({
                (SampleGraphBuilder(self.bcp)
                 .add_relation({("a", "1"), ("b", "2")}, "r")
                 .add_relation({("b", "2"), ("c", "3")}, "r")
                 .build(), 6),
                (SampleGraphBuilder(self.bcp)
                 .add_relation({("a", "1"), ("b", "2")}, "r")
                 .add_relation({("b", "2"), ("c", "3")}, "s")
                 .add_relation({("c", "3"), ("d", "4")}, "r")
                 .build(), 20)}))


if __name__ == '__main__':
    unittest.main()
