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

from scripts.relnet.activation_graph import ActiveNode, ActiveEdge, ActivationGraph
from scripts.relnet.relation_graph import BuilderComponentsProvider


class TestActiveNode(unittest.TestCase):

    an_1 = ActiveNode("a", {"1": 0.1, "2": 0.2}, True)

    def test_init(self):
        self.assertEqual(self.an_1.variable, "a")
        self.assertEqual(self.an_1.values, frozenset({("1", 0.1), ("2", 0.2)}))
        self.assertTrue(self.an_1.in_query)

    def test_repr(self):
        self.assertEqual(self.an_1.__repr__(), "Q(a:{1(0.1),2(0.2)})")
        self.assertEqual(ActiveNode("a", {"1": 0.1}, False).__repr__(), "(a:{1(0.1)})")

    def test_hash(self):
        self.assertEqual(self.an_1.__hash__(), ("a",  frozenset({("1", 0.1), ("2", 0.2)})).__hash__())

    def test_eq(self):
        an_2 = ActiveNode("a", {"1": 0.1, "2": 0.2}, True)
        self.assertNotEqual(id(self.an_1), id(an_2))
        self.assertEqual(self.an_1, an_2)


class TestActiveEdge(unittest.TestCase):

    ae_1 = ActiveEdge({"a", "b"}, {"r": 1, "s": 2}, True)

    def test_init(self):
        self.assertEqual(self.ae_1.endpoints, frozenset({"a", "b"}))
        self.assertEqual(self.ae_1.relations, frozenset({("r", 1), ("s", 2)}))
        self.assertTrue(self.ae_1.in_query)

        with self.assertRaises(AssertionError):  # Expect 2 endpoints
            ActiveEdge({"a", "a"}, {}, False)

    def test_repr(self):
        self.assertEqual(self.ae_1.__repr__(), "(a)--Q{r(1),s(2)}--(b)")
        self.assertEqual(ActiveEdge({"a", "b"}, {"r": 1}, False).__repr__(), "(a)--{r(1)}--(b)")

    def test_hash(self):
        self.assertEqual(
            self.ae_1.__hash__(),
            (frozenset({"a", "b"}), frozenset({("r", 1), ("s", 2)})).__hash__())

    def test_eq(self):
        ae_2 = ActiveEdge({"a", "b"}, {"r": 1, "s": 2}, True)
        self.assertNotEqual(id(self.ae_1), id(ae_2))
        self.assertEqual(self.ae_1, ae_2)


class TestActivationGraph(unittest.TestCase):

    bcp = BuilderComponentsProvider({"a": {"1"}, "b": {"2"}}, {"s"})
    an_a = ActiveNode("a", {"1": 0.1}, True)
    an_b = ActiveNode("b", {"2": 0.2}, False)
    ae_1 = ActiveEdge({"a", "b"}, {"r": 1}, True)
    ag_1 = ActivationGraph(bcp, 123, {an_a, an_b}, {ae_1}, "ag_1")

    def test_init(self):
        self.assertEqual(self.ag_1.nodes, frozenset({self.an_a, self.an_b}))
        self.assertEqual(self.ag_1.edges, frozenset({self.ae_1}))
        self.assertEqual(self.ag_1.name, "ag_1")
        self.assertEqual(self.ag_1.variables, frozenset({"a", "b"}))


if __name__ == '__main__':
    unittest.main()
