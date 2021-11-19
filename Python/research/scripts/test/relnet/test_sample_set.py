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

    bcp = MockSampleGraphComponentsProvider({"a": {"1", "2"}}, {"r"})
    o_1 = SampleGraphBuilder(bcp).build_single_node("a", "1")
    o_2 = SampleGraphBuilder(bcp).build_single_node("a", "2")
    s_1 = Samples({o_1: 1, o_2: 2})

    def test_bool(self):
        self.assertTrue(self.s_1)
        self.assertFalse(Samples({}))

    def test_items(self):
        self.assertEqual(self.s_1.items(), {(self.o_1, 1), (self.o_2, 2)})

    def test_samples(self):
        self.assertEqual(self.s_1.samples(), {self.o_1, self.o_2})


class TestSampleSet(unittest.TestCase):

    bcp = MockSampleGraphComponentsProvider({"a": {"1", "2", "3"}, "b": {"1", "2"}}, {"r"})
    o_1 = SampleGraphBuilder(bcp).build_single_node("a", "1")
    o_2 = SampleGraphBuilder(bcp).build_single_node("a", "2")
    ss_1 = SampleSet({o_1: 1, o_2: 2})

    def test_init(self):
        self.assertEqual(self.ss_1.items(), {(self.o_1, 1), (self.o_2, 2)})
        self.assertEqual(self.ss_1.length, 3)

    def test_len(self):
        self.assertEqual(len(self.ss_1), 3)

    def test_eq(self):
        ss_2 = SampleSet({self.o_1: 1, self.o_2: 2})
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
        ss_2 = SampleSet({o_3: 3, o_4: 4})
        u_1 = self.ss_1.union(ss_2)

        self.assertEqual(u_1.items(), {(self.o_1, 4), (self.o_2, 2), (o_4, 4)})

    def test_filter_samples(self):
        o_3 = SampleGraphBuilder(self.bcp).build_single_node("a", "1")
        o_4 = SampleGraphBuilder(self.bcp).build_single_node("b", "2")
        ss_2 = SampleSet({o_3: 3, o_4: 4})

        self.assertEqual(
            ss_2.filter_samples(lambda s: "a" in s.included_variables).items(),
            {(o_3, 3)})


class TestSampleSetBuilder(unittest.TestCase):

    bcp = MockSampleGraphComponentsProvider({"a": {"1", "2"}}, {"r"})
    o_1 = SampleGraphBuilder(bcp).build_single_node("a", "1")
    o_2 = SampleGraphBuilder(bcp).build_single_node("a", "2")
    sb_1 = SampleSetBuilder({o_1: 1, o_2: 2})

    def test_init(self):
        self.assertEqual(self.sb_1.items(), {(self.o_1, 1), (self.o_2, 2)})

    def test_repr(self):
        self.assertEqual(str(self.sb_1), "SampleSetBuilder(length = 3)")

    def test_add(self):
        sb_2 = SampleSetBuilder()
        sb_2.add(self.o_1, 10)
        sb_2.add(self.o_1, 20)
        sb_2.add(self.o_2, 40)
        self.assertEqual(sb_2.items(), {(self.o_1, 30), (self.o_2, 40)})

    def test_length(self):
        self.assertEqual(self.sb_1.length(), 3)

    def test_build(self):
        bs_1 = self.sb_1.build()
        self.assertTrue(isinstance(bs_1, SampleSet))
        self.assertEqual(bs_1.items(), {(self.o_1, 1), (self.o_2, 2)})


if __name__ == '__main__':
    unittest.main()
