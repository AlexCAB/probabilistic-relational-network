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
created: 2021-11-19
"""

import unittest

from scripts.relnet.sample_graph import SampleGraphBuilder
from scripts.relnet.sample_set import SampleSet, Samples, SampleSetBuilder
from scripts.test.relnet.test_graph_components import MockSampleGraphComponentsProvider


class TestSamples(unittest.TestCase):

    bcp = MockSampleGraphComponentsProvider({"a": {"1", "2", "3"}}, {"r"})
    o_1 = SampleGraphBuilder(bcp).build_single_node("a", "1")
    o_2 = SampleGraphBuilder(bcp).build_single_node("a", "2")
    o_3 = SampleGraphBuilder(bcp).build_single_node("a", "3")
    s_1 = Samples(bcp, {o_1: 1, o_2: 2})

    def test_bool(self):
        self.assertTrue(self.s_1)
        self.assertFalse(Samples(self.bcp, {}))

    def test_items(self):
        self.assertEqual(self.s_1.items(), {(self.o_1, 1), (self.o_2, 2)})

    def test_samples(self):
        self.assertEqual(self.s_1.samples(), {self.o_1, self.o_2})

    def test_is_compatible(self):
        self.assertTrue(
            self.s_1.is_compatible(Samples(self.bcp, {})))
        self.assertFalse(
            self.s_1.is_compatible(Samples(MockSampleGraphComponentsProvider({"a": {"1"}}, {"r"}), {})))

    def test_count_of(self):
        self.assertEqual(self.s_1.count_of(self.o_2), 2)

        with self.assertRaises(AssertionError):  # Sample not in set
            self.s_1.count_of(self.o_3)


class TestSampleSet(unittest.TestCase):

    bcp = MockSampleGraphComponentsProvider(
        {
            "a": {"1", "2", "3"},
            "b": {"1", "2", "3"},
            "c": {"1", "2", "3"},
            "d": {"1", "2", "3"},
            "e": {"1", "2", "3"},
            "f": {"1", "2", "3"},
            "g": {"1", "2", "3"}},
        {"r", "s", "t"})
    o_1 = SampleGraphBuilder(bcp).build_single_node("a", "1")
    o_2 = SampleGraphBuilder(bcp).build_single_node("a", "2")
    o_3 = SampleGraphBuilder(bcp) \
        .add_relation({("a", "1"), ("b", "1")}, "r") \
        .build()
    o_4 = SampleGraphBuilder(bcp) \
        .add_relation({("b", "1"), ("c", "1")}, "s") \
        .build()
    ss_1 = SampleSet(bcp, {o_1: 1, o_2: 2})
    ss_2 = SampleSet(bcp, {o_3: 3, o_4: 4})

    def test_init(self):
        self.assertEqual(self.ss_1.items(), {(self.o_1, 1), (self.o_2, 2)})
        self.assertEqual(self.ss_1.length, 3)

    def test_len(self):
        self.assertEqual(len(self.ss_1), 3)

    def test_eq(self):
        ss_2 = SampleSet(self.bcp, {self.o_1: 1, self.o_2: 2})
        self.assertNotEqual(id(self.ss_1), id(ss_2))
        self.assertEqual(self.ss_1, ss_2)

    def test_repr(self):
        self.assertEqual(str(self.ss_1), """{\n    {(a_1)}: 1\n    {(a_2)}: 2\n}""")

    def test_builder(self):
        b_1 = self.ss_1.builder()
        self.assertTrue(isinstance(b_1, SampleSetBuilder))
        self.assertEqual(b_1.items(), {(self.o_1, 1), (self.o_2, 2)})

    def test_union(self):
        o_3 = SampleGraphBuilder(self.bcp).build_single_node("a", "1")
        o_4 = SampleGraphBuilder(self.bcp).build_single_node("a", "3")
        ss_2 = SampleSet(self.bcp, {o_3: 3, o_4: 4})
        u_1 = self.ss_1.union(ss_2)

        self.assertEqual(u_1.items(), {(self.o_1, 4), (self.o_2, 2), (o_4, 4)})

        with self.assertRaises(AssertionError):  # Incompatible sample set
            self.ss_1.union(SampleSet(MockSampleGraphComponentsProvider({"a": {"1"}}, {"r"}), {o_3: 3, o_4: 4}))

    def test_filter_samples(self):
        o_3 = SampleGraphBuilder(self.bcp).build_single_node("a", "1")
        o_4 = SampleGraphBuilder(self.bcp).build_single_node("b", "2")
        ss_2 = SampleSet(self.bcp, {o_3: 3, o_4: 4})

        self.assertEqual(
            ss_2.filter_samples(lambda s: "a" in s.included_variables).items(),
            {(o_3, 3)})

    def test_group_intersecting(self):
        o_11 = SampleGraphBuilder(self.bcp) \
            .build_single_node("a", "1")
        o_12 = SampleGraphBuilder(self.bcp) \
            .build_single_node("a", "2")

        o_21 = SampleGraphBuilder(self.bcp)\
            .add_relation({("a", "1"), ("b", "1")}, "r") \
            .build()
        o_22 = SampleGraphBuilder(self.bcp) \
            .add_relation({("c", "2"), ("d", "2")}, "s") \
            .build()
        o_23 = SampleGraphBuilder(self.bcp) \
            .add_relation({("a", "2"), ("b", "2")}, "s") \
            .add_relation({("b", "2"), ("c", "1")}, "t") \
            .add_relation({("c", "1"), ("d", "2")}, "r") \
            .build()

        o_31 = SampleGraphBuilder(self.bcp) \
            .build_single_node("f", "1")

        o_41 = SampleGraphBuilder(self.bcp) \
            .add_relation({("f", "2"), ("g", "1")}, "r") \
            .build()
        o_42 = SampleGraphBuilder(self.bcp) \
            .add_relation({("f", "2"), ("g", "1")}, "s") \
            .build()

        self.assertEqual(
            SampleSet(self.bcp,
                      {o_11: 1, o_12: 2, o_21: 3, o_22: 4, o_23: 5, o_31: 6, o_41: 7, o_42: 8}).group_intersecting(), {
                frozenset({"a"}):  SampleSet(self.bcp, {o_11: 1, o_12: 2}),
                frozenset({"a", "b", "c", "d"}):  SampleSet(self.bcp, {o_21: 3, o_22: 4, o_23: 5}),
                frozenset({"f"}):  SampleSet(self.bcp, {o_31: 6}),
                frozenset({"g", "f"}):  SampleSet(self.bcp, {o_41: 7, o_42: 8})})

    def test_make_joined_sample(self):
        jo_1, cs_1 = self.ss_2.make_joined_sample()

        self.assertEqual(
            jo_1,
            SampleGraphBuilder(self.bcp)
            .add_relation({("a", "1"), ("b", "1")}, "r").add_relation({("b", "1"), ("c", "1")}, "s").build())

        self.assertEqual(set(cs_1), {3, 4})

    def test_is_all_have_variables(self):
        self.assertTrue(SampleSet(self.bcp, {}).is_all_values_match())
        self.assertFalse(self.ss_1.is_all_values_match())
        self.assertTrue(self.ss_2.is_all_values_match())

    def test_probabilities(self):
        self.assertEqual(
            self.ss_2.probabilities(),
            {(self.o_3, 3 / (3 + 4)), (self.o_4, 4 / (3 + 4))})

    def test_have_value(self):
        self.assertTrue(self.ss_2.have_value("a", "1"))
        self.assertTrue(self.ss_2.have_value("c", "1"))
        self.assertFalse(self.ss_2.have_value("a", "not_in_sample"))
        self.assertFalse(self.ss_2.have_value("not_in_sample", "1"))

    def test_have_variable(self):
        self.assertTrue(self.ss_2.have_variable("a"))
        self.assertFalse(self.ss_2.have_variable("not_in_sample"))

    def test_probability_of(self):
        self.assertEqual(self.ss_1.probability_of(self.o_2), 0.6666666666666666)

        with self.assertRaises(AssertionError):  # Sample not in set
            self.ss_1.probability_of(self.o_3)


class TestSampleSetBuilder(unittest.TestCase):

    bcp = MockSampleGraphComponentsProvider({"a": {"1", "2", "3"}}, {"r"})
    o_1 = SampleGraphBuilder(bcp).build_single_node("a", "1")
    o_2 = SampleGraphBuilder(bcp).build_single_node("a", "2")
    sb_1 = SampleSetBuilder(bcp, {o_1: 1, o_2: 2})

    def test_join_sample_set(self):
        o_3 = SampleGraphBuilder(self.bcp).build_single_node("a", "3")
        ss_1 = SampleSetBuilder(self.bcp, {self.o_1: 1, o_3: 3}).build()
        ss_2 = SampleSetBuilder(self.bcp, {o_3: 3}).build()
        self.assertEqual(
            SampleSetBuilder.join_sample_set([self.sb_1.build(), ss_1, ss_2]),
            SampleSetBuilder(self.bcp, {self.o_1: 2, self.o_2: 2, o_3: 6}).build())

    def test_init(self):
        self.assertEqual(self.sb_1.items(), {(self.o_1, 1), (self.o_2, 2)})

    def test_repr(self):
        self.assertEqual(str(self.sb_1), "SampleSetBuilder(length = 3)")

    def test_copy(self):
        sb_2 = self.sb_1.copy()
        self.assertNotEqual(id(self.sb_1), id(sb_2))

    def test_add(self):
        sb_2 = SampleSetBuilder(self.bcp)
        sb_2.add(self.o_1, 10)
        sb_2.add(self.o_1, 20)
        sb_2.add(self.o_2, 40)
        self.assertEqual(sb_2.items(), {(self.o_1, 30), (self.o_2, 40)})

    def test_add_all(self):
        sb_2 = SampleSetBuilder(self.bcp)
        sb_2.add_all(self.sb_1.build())
        self.assertEqual(sb_2.items(), {(self.o_1, 1), (self.o_2, 2)})

    def test_remove(self):
        sb_2 = self.sb_1.copy()
        r_1 = sb_2.remove(self.o_1)
        self.assertEqual(sb_2.items(), {(self.o_2, 2)})
        self.assertEqual(r_1, (self.o_1, 1))

    def test_remove_all(self):
        sb_2 = self.sb_1.copy()
        sb_2.remove_all(sb_2)
        self.assertEqual(sb_2.items(), set({}))

    def test_length(self):
        self.assertEqual(self.sb_1.length(), 3)

    def test_empty(self):
        self.assertTrue(len(SampleSetBuilder(self.bcp).empty()) == 0)

    def test_build(self):
        bs_1 = self.sb_1.build()
        self.assertTrue(isinstance(bs_1, SampleSet))
        self.assertEqual(bs_1.items(), {(self.o_1, 1), (self.o_2, 2)})


if __name__ == '__main__':
    unittest.main()
