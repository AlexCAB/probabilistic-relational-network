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
created: 2021-10-18
"""

import unittest
from copy import copy
from typing import Any, Dict, Set, Tuple

from scripts.relnet.sample_graph import ValueNode, RelationEdge, SampleGraphBuilder, SampleGraph, \
    SampleGraphComponentsProvider, SampleSpace, DirectedRelation
from scripts.relnet.folded_graph import FoldedNode, FoldedEdge


class MockSampleGraphComponentsProvider(SampleGraphComponentsProvider):

    def __init__(self, variables: Dict[Any, Set[Any]], relations: Set[Any]):
        self._variables: Dict[Any, Set[Any]] = variables
        self._relations: Set[Any] = relations

        self.nodes: Dict[Tuple[Any, Any], ValueNode] = {}
        self.edges: Dict[Tuple[frozenset[ValueNode], Any], RelationEdge] = {}

    def variables(self) -> frozenset[Tuple[Any, frozenset[Any]]]:
        return frozenset({(k, frozenset(v)) for k, v in self._variables.items()})

    def relations(self) -> frozenset[Any]:
        return frozenset(self._relations)

    def get_node(self, variable: Any, value: Any) -> ValueNode:
        assert variable in self._variables, \
            f"[MockSampleGraphComponentsProvider.get_node] Unknown variable {variable}"
        assert value in self._variables[variable], \
            f"[MockSampleGraphComponentsProvider.get_node] Unknown value {value} of variable {variable}"

        if (variable, value) in self.nodes:
            return self.nodes[(variable, value)]
        else:
            node = ValueNode(variable, value)
            self.nodes[(variable, value)] = node
            return node

    def get_edge(self, endpoints: frozenset[ValueNode], relation: Any) -> RelationEdge:
        assert endpoints.issubset(self.nodes.values()), \
            f"[MockSampleGraphComponentsProvider.get_edge] Endpoints nodes should be created first, " \
            f"got {endpoints} where nodes {self.nodes}"
        assert (relation.relation if isinstance(relation, DirectedRelation) else relation) in self._relations, \
            f"[MockSampleGraphComponentsProvider.get_node] Unknown relation {relation}"

        if isinstance(relation, DirectedRelation):
            variables = {ep.variable for ep in endpoints}
            assert relation.source_variable in variables, \
                f"[MockSampleGraphComponentsProvider.get_node] Unknown relation source " \
                f"variable {relation.source_variable}"
            assert relation.target_variable in variables, \
                f"[MockSampleGraphComponentsProvider.get_node] Unknown relation target " \
                f"variable {relation.target_variable}"

        if (endpoints, relation) in self.edges:
            return self.edges[(endpoints, relation)]
        else:
            edge = RelationEdge(endpoints, relation)
            self.edges[(endpoints, relation)] = edge
            return edge


class TestValueNode(unittest.TestCase):

    a_1 = ValueNode("a", "1")

    def test_init(self):
        self.assertEqual(self.a_1.variable, "a")
        self.assertEqual(self.a_1.value, "1")
        self.assertEqual(self.a_1.string_id, "a_1")

    def test_hash(self):
        self.assertEqual(self.a_1.__hash__(), ("a", "1").__hash__())

    def test_repr(self):
        self.assertEqual(self.a_1.__repr__(), "(a_1)")

    def test_copy(self):
        with self.assertRaises(AssertionError):
            copy(self.a_1)

    def test_eq(self):
        a_1_1 = ValueNode("a", "1")
        a_1_2 = ValueNode("a", "1")
        self.assertNotEqual(id(a_1_1), id(a_1_2))
        self.assertEqual(a_1_1, a_1_2)


class TestRelationEdge(unittest.TestCase):

    a_1 = ValueNode("a", "1")
    b_1 = ValueNode("b", "1")
    b_2 = ValueNode("b", "2")
    e_1 = RelationEdge(frozenset({a_1, b_1}), "r")

    def test_init(self):
        self.assertEqual(self.e_1.endpoints, frozenset({self.a_1, self.b_1}))
        self.assertEqual(self.e_1.relation, "r")
        self.assertTrue(self.e_1.a in {self.a_1, self.b_1})
        self.assertTrue(self.e_1.b in {self.a_1, self.b_1})
        self.assertNotEqual(self.e_1.a, self.e_1.b)

    def test_hash(self):
        self.assertEqual(self.e_1.__hash__(), (frozenset({self.a_1, self.b_1}), "r").__hash__())

    def test_repr(self):
        self.assertEqual(self.e_1.__repr__(), "(a_1)--{r}--(b_1)")

    def test_copy(self):
        with self.assertRaises(AssertionError):
            copy(self.e_1)

    def test_eq(self):
        e_1_1 = RelationEdge(frozenset({self.a_1, self.b_1}), "r")
        e_1_2 = RelationEdge(frozenset({self.b_1, self.a_1}), "r")
        self.assertNotEqual(id(e_1_1), id(e_1_2))
        self.assertEqual(e_1_1, e_1_2)

    def test_is_endpoint(self):
        self.assertTrue(self.e_1.is_endpoint(self.a_1))
        self.assertFalse(self.e_1.is_endpoint(self.b_2))

    def test_opposite_endpoint(self):
        self.assertEqual(self.e_1.opposite_endpoint(self.a_1), self.b_1)
        self.assertEqual(self.e_1.opposite_endpoint(self.b_1), self.a_1)
        with self.assertRaises(AssertionError):
            self.e_1.opposite_endpoint(self.b_2)


class TestDirectedRelation(unittest.TestCase):

    dr_1 = DirectedRelation("a", "b", "r")

    def test_init(self):

        self.assertEqual(self.dr_1.source_variable, "a")
        self.assertEqual(self.dr_1.target_variable, "b")
        self.assertEqual(self.dr_1.relation, "r")

    def test_hash(self):
        self.assertEqual(self.dr_1.__hash__(), ("a", "b", "r").__hash__())

    def test_repr(self):
        self.assertEqual(self.dr_1.__repr__(), "b[a->r]")

    def test_copy(self):
        with self.assertRaises(AssertionError):
            copy(self.dr_1)

    def test_eq(self):
        dr_2 = DirectedRelation("a", "b", "r")
        self.assertNotEqual(id(self.dr_1), id(dr_2))
        self.assertEqual(self.dr_1, dr_2)


class TestSampleGraphBuilder(unittest.TestCase):

    builder = MockSampleGraphComponentsProvider(
        {"a": {"1", "2"}, "b": {"1"}, "c": {"1"}, "d": {"1"}, "f": {"1"}},
        {"r", "s"})
    a_1 = builder.get_node("a", "1")
    b_1 = builder.get_node("b", "1")
    c_1 = builder.get_node("c", "1")
    e_1 = builder.get_edge(frozenset({a_1, b_1}), "r")
    e_2 = builder.get_edge(frozenset({b_1, c_1}), "r")
    e_3 = builder.get_edge(frozenset({a_1, b_1}), "s")
    e_4 = builder.get_edge(frozenset({b_1, c_1}), "s")
    de_1 = builder.get_edge(frozenset({a_1, b_1}), DirectedRelation("a", "b", "r"))
    de_2 = builder.get_edge(frozenset({b_1, c_1}), DirectedRelation("b", "c", "r"))

    def test_init(self):
        s_1 = SampleGraphBuilder(self.builder, "s", {self.a_1, self.b_1}, {self.e_1}).build()
        self.assertEqual(s_1.name, "s")
        self.assertEqual(s_1.nodes, frozenset({self.a_1, self.b_1}))
        self.assertEqual({id(n) for n in s_1.nodes}, {id(n) for n in {self.a_1, self.b_1}})
        self.assertEqual(s_1.edges, frozenset({self.e_1}))
        self.assertEqual({id(e) for e in s_1.edges}, {id(self.e_1)})

    def test_copy(self):
        b_1 = SampleGraphBuilder(self.builder, "s", {self.a_1, self.b_1}, {self.e_1})
        b_2 = copy(b_1)
        self.assertNotEqual(id(b_1), id(b_2))
        self.assertEqual(b_1.build(), b_2.build())

    def test_repr(self):
        self.assertEqual(
            str(SampleGraphBuilder(self.builder, "b_1", {self.a_1, self.b_1}, {self.e_1})),
            "RelationGraphBuilder(name = b_1, len(nodes) = 2, len(edges) = 1)")

    def test_set_name(self):
        s_1 = SampleGraphBuilder(self.builder, None, {self.a_1})\
            .set_name("s")\
            .build()
        self.assertEqual(s_1.name, "s")

    def test_build_single_node(self):
        s_1 = SampleGraphBuilder(self.builder) \
            .build_single_node("a", "1")
        self.assertEqual(s_1.nodes, frozenset({self.a_1}))
        self.assertEqual({id(e) for e in s_1.nodes}, {id(self.a_1)})

    def test_is_edges_connected(self):
        self.assertTrue(SampleGraphBuilder.is_edges_connected(frozenset({
            (frozenset({("a", "1"), ("b", "1")}), "r"),
        })))
        self.assertTrue(SampleGraphBuilder.is_edges_connected(frozenset({
            (frozenset({("a", "1"), ("b", "1")}), "r"),
            (frozenset({("b", "1"), ("c", "1")}), "r"),
        })))
        self.assertTrue(SampleGraphBuilder.is_edges_connected(frozenset({
            (frozenset({("a", "1"), ("b", "1")}), "r"),
            (frozenset({("b", "1"), ("c", "1")}), "r"),
            (frozenset({("a", "1"), ("d", "1")}), "r"),
        })))
        self.assertTrue(SampleGraphBuilder.is_edges_connected(frozenset({
            (frozenset({("a", "1"), ("b", "1")}), "r"),
            (frozenset({("b", "1"), ("c", "1")}), "r"),
            (frozenset({("c", "1"), ("d", "1")}), "r"),
            (frozenset({("d", "1"), ("a", "1")}), "r"),
        })))
        self.assertFalse(SampleGraphBuilder.is_edges_connected(frozenset({
            (frozenset({("a", "1"), ("b", "1")}), "r"),
            (frozenset({("c", "1"), ("d", "1")}), "r"),
        })))
        self.assertFalse(SampleGraphBuilder.is_edges_connected(frozenset({
            (frozenset({("a", "1"), ("b", "1")}), "r"),
            (frozenset({("b", "1"), ("c", "1")}), "r"),
            (frozenset({("d", "1"), ("f", "1")}), "r"),
        })))

    def test_validate_endpoints(self):
        with self.assertRaises(AssertionError):
            SampleGraphBuilder.validate_endpoints(frozenset({("a", "1")}))
        with self.assertRaises(AssertionError):
            SampleGraphBuilder.validate_endpoints(frozenset({("a", "1"), ("b", "1"), ("c", "1")}))
        with self.assertRaises(AssertionError):
            SampleGraphBuilder.validate_endpoints(frozenset({("a", "1"), ("a", "1")}))

    def test_build_from_edges(self):
        s_1 = SampleGraphBuilder(self.builder).set_name("s_1").build_from_edges(frozenset({
            (frozenset({("a", "1"), ("b", "1")}), "r"),
            (frozenset({("b", "1"), ("c", "1")}), "r")}))
        self.assertEqual(s_1.name, "s_1")
        self.assertEqual(s_1.nodes, frozenset({self.a_1, self.b_1, self.c_1}))
        self.assertEqual({id(n) for n in s_1.nodes}, {id(n) for n in {self.a_1, self.b_1, self.c_1}})
        self.assertEqual(s_1.edges, frozenset({self.e_1, self.e_2}))
        self.assertEqual({id(e) for e in s_1.edges}, {id(self.e_1), id(self.e_2)})

        s_2 = SampleGraphBuilder(self.builder).set_name("s_2").build_from_edges(
            frozenset({
                (frozenset({("a", "1"), ("b", "1")}), "r"),
                (frozenset({("c", "1"), ("d", "1")}), "r")}),
            validate_connectivity=False)  # Should not fail even when passes disconnected graph
        self.assertEqual(s_2.name, "s_2")

    def test_add_relation(self):
        b_1 = SampleGraphBuilder(self.builder) \
            .add_relation({("a", "1"), ("b", "1")}, "r") \
            .add_relation({("b", "1"), ("c", "1")}, "r")
        s_1 = b_1.build()

        self.assertEqual(s_1.nodes, frozenset({self.a_1, self.b_1, self.c_1}))
        self.assertEqual({id(n) for n in s_1.nodes}, {id(n) for n in {self.a_1, self.b_1, self.c_1}})
        self.assertEqual(s_1.edges, frozenset({self.e_1, self.e_2}))
        self.assertEqual({id(e) for e in s_1.edges}, {id(e) for e in {self.e_1, self.e_2}})

        b_1.add_relation({("c", "1"), ("d", "1")}, "s")
        s_2 = b_1.build()

        self.assertTrue(("d", "1") in [(n.variable, n.value) for n in s_2.nodes])
        self.assertTrue("s" in [e.relation for e in s_2.edges])

        with self.assertRaises(AssertionError):  # len(endpoints) != 2
            b_1.add_relation({("c", "1")}, "r")

        with self.assertRaises(AssertionError):  # len(endpoints) != 2
            b_1.add_relation({("a", "1"), ("b", "1"), ("c", "1")}, "r")

        with self.assertRaises(AssertionError):  # len({var for var, _ in endpoints}) != 2
            b_1.add_relation({("a", "1"), ("a", "2")}, "r")

        with self.assertRaises(AssertionError):  # nodes.isdisjoint(self._nodes)
            SampleGraphBuilder(self.builder) \
                .add_relation({("a", "1"), ("b", "1")}, "r") \
                .add_relation({("c", "1"), ("d", "1")}, "r")

        with self.assertRaises(AssertionError):  # edge in self._edges
            SampleGraphBuilder(self.builder) \
                .add_relation({("a", "1"), ("b", "1")}, "s") \
                .add_relation({("a", "1"), ("b", "1")}, "r")

    def test_add_directed_relation(self):
        b_1 = SampleGraphBuilder(self.builder) \
            .add_directed_relation(("a", "1"), ("b", "1"), "r") \
            .add_directed_relation(("b", "1"), ("c", "1"), "r")
        s_1 = b_1.build()

        self.assertEqual(s_1.nodes, frozenset({self.a_1, self.b_1, self.c_1}))
        self.assertEqual(s_1.edges, frozenset({self.de_1, self.de_2}))

    def test_can_sample_be_joined(self):
        sgb_1 = SampleGraphBuilder(self.builder, "b_1", {self.a_1, self.b_1}, {self.e_1})
        s_1 = SampleGraph(self.builder, frozenset({self.a_1, self.b_1}), frozenset({self.e_1}), "s_1")
        s_2 = SampleGraph(self.builder, frozenset({self.a_1, self.b_1}), frozenset({self.e_3}), "s_2")
        s_3 = SampleGraph(self.builder, frozenset({self.b_1, self.c_1}), frozenset({self.e_4}), "s_3")
        s_4 = SampleGraph(copy(self.builder), frozenset({self.b_1, self.c_1}), frozenset({self.e_3}), "s_4")

        self.assertTrue(sgb_1.can_sample_be_joined(s_1))
        self.assertFalse(sgb_1.can_sample_be_joined(s_2))
        self.assertTrue(sgb_1.can_sample_be_joined(s_3))

        with self.assertRaises(AssertionError):
            sgb_1.can_sample_be_joined(s_4)

    def test_join_sample(self):
        sgb_1 = SampleGraphBuilder(self.builder, "b_1", {self.a_1, self.b_1}, {self.e_1})
        s_1 = SampleGraph(self.builder, frozenset({self.b_1, self.c_1}), frozenset({self.e_2}), "s_1")
        s_2 = SampleGraph(self.builder, frozenset({self.a_1, self.b_1}), frozenset({self.e_4}), "s_2")

        js_1 = sgb_1.join_sample(s_1).build()

        self.assertEqual(js_1.nodes, frozenset({self.a_1, self.b_1, self.c_1}))
        self.assertEqual(js_1.edges, frozenset({self.e_1, self.e_2}))

        with self.assertRaises(AssertionError):
            sgb_1.join_sample(s_2)

    def test_build(self):
        with self.assertRaises(AssertionError):
            SampleGraphBuilder(self.builder).build()


class TestSampleGraph(unittest.TestCase):

    builder = MockSampleGraphComponentsProvider(
        {"a": {"1", "5"}, "b": {"1", "7"}, "c": {"1"}, "d": {"1"}, "f": {"1"}},
        {"r", "g", "b"})
    a_1 = builder.get_node("a", "1")
    b_1 = builder.get_node("b", "1")
    c_1 = builder.get_node("c", "1")
    e_1 = builder.get_edge(frozenset({a_1, b_1}), "r")
    e_2 = builder.get_edge(frozenset({b_1, c_1}), "r")
    s_1 = SampleGraph(builder, frozenset({a_1, b_1}), frozenset({e_1}), "s_1")
    s_2 = SampleGraph(builder, frozenset({a_1}), frozenset({}), "s_2")

    def test_init(self):
        self.assertEqual(self.s_1.nodes, frozenset({self.a_1, self.b_1}))
        self.assertEqual(self.s_1.edges, frozenset({self.e_1}))
        self.assertEqual(self.s_1.hash, frozenset({self.a_1, self.b_1, self.e_1}))
        self.assertEqual(self.s_1.name, "s_1")

    def test_hash(self):
        self.assertEqual(self.s_1.__hash__(), self.s_1.hash.__hash__())

    def test_repr(self):
        self.assertEqual(self.s_1.__repr__(), "s_1")
        self.assertEqual(
            SampleGraph(
                self.builder,
                frozenset({self.a_1, self.b_1, self.c_1}),
                frozenset({self.e_1, self.e_2}),
                None).__repr__(),
            "{(a_1)--{r}--(b_1); (b_1)--{r}--(c_1)}")

    def test_copy(self):
        with self.assertRaises(AssertionError):
            copy(self.s_1)

    def test_eq(self):
        s_1_1 = SampleGraph(self.builder, frozenset({self.a_1, self.b_1}), frozenset({self.e_1}), None)
        s_1_2 = SampleGraph(self.builder, frozenset({self.a_1, self.b_1}), frozenset({self.e_1}), None)
        self.assertNotEqual(id(s_1_1), id(s_1_2))
        self.assertEqual(s_1_1, s_1_2)

    def test_is_compatible(self):
        self.assertTrue(self.s_1.is_compatible(self.builder))
        self.assertFalse(self.s_1.is_compatible(copy(self.builder)))

    def test_text_view(self):
        self.assertEqual(SampleGraph(self.builder, frozenset({self.a_1}), frozenset(), None).text_view(), "{(a_1)}")
        self.assertEqual(self.s_1.text_view(),  "{(a_1)--{r}--(b_1)}")

    def test_edges_set_view(self):
        self.assertEqual(
            self.s_1.edges_set_view(),
            frozenset({(frozenset({("a", "1"), ("b", "1")}), "r")}))
        self.assertEqual(
            self.s_2.edges_set_view(),
            ("a", "1"))

    def test_builder(self):
        b_1 = self.s_1.builder()
        b_1.add_relation({("b", "1"), ("f", "1")}, "g")
        s_2 = b_1.build()
        self.assertTrue(("f", "1") in {(n.variable, n.value) for n in s_2.nodes})
        self.assertTrue("g" in [e.relation for e in s_2.edges])

    def test_is_subgraph(self):
        self.assertTrue(
            self.s_1.is_subgraph(
                SampleGraph(
                    self.builder,
                    frozenset({self.a_1, self.b_1, self.c_1}), frozenset({self.e_1, self.e_2}), None)))

        self.assertFalse(
            self.s_1.is_subgraph(SampleGraph(self.builder, frozenset({self.a_1}), frozenset({}), None)))

    def test_value_for_variable(self):
        self.assertEqual(self.s_1.value_for_variable("a"), "1")
        self.assertEqual(self.s_1.value_for_variable("b"), "1")
        self.assertEqual(self.s_1.value_for_variable("not_in_graph"), None)

    def test_transform_with_replaced_values(self):
        s_1 = SampleGraph(
            self.builder,
            frozenset({self.a_1, self.b_1, self.c_1}),
            frozenset({self.e_1, self.e_2}),
            "s_1")

        s_2 = s_1.transform_with_replaced_values({"a": "5", "b": "7"}, "s_2")

        self.assertNotEqual(id(s_2), id(s_1))
        self.assertTrue(id(self.c_1) in {id(n) for n in s_2.nodes})

        self.assertEqual(
            {(n.variable, n.value) for n in s_2.nodes},
            {("a", "5"), ("b", "7"), ("c", "1")})

        self.assertEqual(
            {frozenset({(n.variable, n.value) for n in e.endpoints}) for e in s_2.edges},
            {frozenset({("a", "5"), ("b", "7")}), frozenset({("b", "7"), ("c", "1")})})

        self.assertEqual(id(s_1.transform_with_replaced_values({}, "s_2")), id(s_1))
        self.assertEqual(id(s_1.transform_with_replaced_values({"x": "1"}, "s_2")), id(s_1))

    def test_neighboring_values(self):
        s = SampleGraphBuilder(self.builder)\
            .add_relation({("a", "1"), ("b", "1")}, "r")\
            .add_relation({("a", "1"), ("c", "1")}, "g")\
            .add_relation({("a", "1"), ("d", "1")}, "b")\
            .build()

        gn = self.builder.get_node
        ge = self.builder.get_edge

        self.assertEqual(
            s.neighboring_values(gn("a", "1")), {
                gn("b", "1"): ge(frozenset({gn("a", "1"), gn("b", "1")}), "r"),
                gn("c", "1"): ge(frozenset({gn("a", "1"), gn("c", "1")}), "g"),
                gn("d", "1"): ge(frozenset({gn("a", "1"), gn("d", "1")}), "b")})

        self.assertEqual(
            s.neighboring_values(self.builder.get_node("b", "1")), {
                gn("a", "1"): ge(frozenset({gn("a", "1"), gn("b", "1")}), "r")})

        self.assertEqual(
            s.neighboring_values(self.builder.get_node("a", "1"), {"r", "g"}), {
                gn("b", "1"): ge(frozenset({gn("a", "1"), gn("b", "1")}), "r"),
                gn("c", "1"): ge(frozenset({gn("a", "1"), gn("c", "1")}), "g")})

    def test_similarity(self):
        s_1 = SampleGraphBuilder(self.builder) \
            .add_relation({("a", "1"), ("b", "1")}, "r") \
            .add_relation({("a", "1"), ("c", "1")}, "r") \
            .build()

        s_2 = SampleGraphBuilder(self.builder) \
            .add_relation({("a", "1"), ("b", "1")}, "r") \
            .build()

        s_3 = SampleGraphBuilder(self.builder) \
            .build_single_node("a", "1") \

        self.assertEqual(s_1.similarity(s_2), 0.6)
        self.assertEqual(s_1.similarity(s_3), 0.2)
        self.assertEqual(s_2.similarity(s_1), 0.6)
        self.assertEqual(s_2.similarity(s_3), 0.3333333333333333)
        self.assertEqual(s_3.similarity(s_1), 0.2)
        self.assertEqual(s_3.similarity(s_2), 0.3333333333333333)

    def test_belt_nodes(self):
        s_1 = SampleGraphBuilder(self.builder) \
            .add_relation({("a", "1"), ("b", "1")}, "r") \
            .add_relation({("a", "1"), ("b", "7")}, "g") \
            .add_relation({("a", "1"), ("c", "1")}, "g") \
            .build()

        gn = self.builder.get_node
        ge = self.builder.get_edge
        n_a1, n_b1, n_b7, n_c1 = gn("a", "1"), gn("b", "1"), gn("b", "7"), gn("c", "1")
        e_abr = ge(frozenset({n_a1, n_b1}), "r")
        e_abg = ge(frozenset({n_a1, n_b7}), "g")
        e_acg = ge(frozenset({n_a1, n_c1}), "g")

        self.assertEqual(
            s_1.belt_nodes({n_a1}),
            {n_b1: {e_abr}, n_b7: {e_abg}, n_c1: {e_acg}})
        self.assertEqual(
            s_1.belt_nodes({n_b1, n_c1}),
            {n_a1: {e_abr, e_acg}})
        self.assertEqual(
            s_1.belt_nodes({n_a1, n_b1, n_b7, n_c1}),
            {})
        self.assertEqual(
            s_1.belt_nodes({n_a1}, {"r"}),
            {n_b1: {e_abr}})

        with self.assertRaises(AssertionError):
            s_1.belt_nodes(set({}))

    def test_external_nodes(self):
        s_1 = SampleGraphBuilder(self.builder) \
            .add_relation({("a", "1"), ("b", "1")}, "r") \
            .add_relation({("b", "1"), ("c", "1")}, "r") \
            .add_relation({("c", "1"), ("d", "1")}, "g") \
            .add_relation({("d", "1"), ("f", "1")}, "g") \
            .build()

        gn = self.builder.get_node
        ge = self.builder.get_edge
        n_a1, n_b1, n_c1, n_d1, n_f1 = gn("a", "1"), gn("b", "1"), gn("c", "1"), gn("d", "1"), gn("f", "1")
        e_abr = ge(frozenset({n_a1, n_b1}), "r")
        e_bcr = ge(frozenset({n_b1, n_c1}), "r")
        e_cdg = ge(frozenset({n_c1, n_d1}), "g")
        e_dfg = ge(frozenset({n_d1, n_f1}), "g")

        self.assertEqual(s_1.external_nodes({n_a1}), {n_b1: {e_abr}, n_c1: {e_bcr}, n_d1: {e_cdg}, n_f1: {e_dfg}})
        self.assertEqual(s_1.external_nodes({n_a1, n_c1}), {n_b1: {e_abr, e_bcr}, n_d1: {e_cdg}, n_f1: {e_dfg}})
        self.assertEqual(s_1.external_nodes({n_a1}, {"r"}), {n_b1: {e_abr}, n_c1: {e_bcr}})

    def test_variables_subgraph_hash(self):
        self.assertEqual(
            self.s_1.variables_subgraph_hash({"a"}),
            frozenset({self.a_1}))

        self.assertEqual(
            self.s_1.variables_subgraph_hash({"a", "b"}),
            (frozenset({self.a_1, self.b_1, self.e_1})))


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
