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
created: 2021-09-27
"""

import logging
from typing import Tuple

from scripts.relationnetlib.relation_graph import RelationGraph
from scripts.relationnetlib.relation_type import RelationType
from scripts.relationnetlib.variable_node import VariableNode


def build_rel_graph_example() -> (RelationGraph, Tuple[RelationType, RelationType]):

    k_relation = RelationType("K")
    l_relation = RelationType("L")

    rel_graph = RelationGraph(
        "inference_example",
        relations=[
            k_relation,
            l_relation,
        ],
        variables=[
            VariableNode("A", ["a_t", "a_f"]),
            VariableNode("B", ["b_t", "b_f"]),
            VariableNode("C", ["c_t", "c_f"]),
        ]
    )

    o_1 = rel_graph.new_sample_graph("o1")
    o_1_a_t = o_1.add_value_node("A", "a_t")
    o_1_b_t = o_1.add_value_node("B", "b_t")
    o_1.add_relation({o_1_a_t, o_1_b_t}, k_relation)

    o_2 = rel_graph.new_sample_graph("o2")
    o_2_b_t = o_2.add_value_node("B", "b_t")
    o_2_c_t = o_2.add_value_node("C", "c_t")
    o_2.add_relation({o_2_b_t, o_2_c_t}, k_relation)

    rel_graph.add_outcomes([o_1, o_2])

    print(rel_graph.describe())
    # rel_graph.show_all_outcomes()

    return rel_graph, (k_relation, l_relation)


def run_inference(rel_graph: RelationGraph, relations: Tuple[RelationType, RelationType]):
    k_relation, l_relation = relations

    q_b = rel_graph.new_sample_graph("q_b")
    q_b.add_value_node("B", "b_t")
    i_b = rel_graph.inference(q_b)
    print(i_b.describe())
    i_b.show_outcomes()

    q_a = rel_graph.new_sample_graph("q_a")
    q_a.add_value_node("A", "a_t")
    i_a = rel_graph.inference(q_a)
    print(i_a.describe())
    # i_a.show_outcomes()

    q_b_c = rel_graph.new_sample_graph("q_b_c")
    q_b_c_b = q_b_c.add_value_node("B", "b_t")
    q_b_c_c = q_b_c.add_value_node("C", "c_t")
    q_b_c.add_relation({q_b_c_b, q_b_c_c}, l_relation)
    i_b_c = rel_graph.inference(q_b_c)
    print(i_b_c.describe())
    # i_b_c.show_outcomes()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    graph, rs = build_rel_graph_example()
    run_inference(graph, rs)
