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
created: 2021-09-28
"""

import logging
from typing import Tuple, List

from scripts.relationnetlib.active_value import ActiveValue
from scripts.relationnetlib.relation_graph import RelationGraph
from scripts.relationnetlib.relation_type import RelationType
from scripts.relationnetlib.variable_node import VariableNode


def build_rel_graph_example() -> (RelationGraph, Tuple[RelationType, RelationType]):

    k_relation = RelationType("K")
    l_relation = RelationType("L")

    rel_graph = RelationGraph(
        "active_values",
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

    o_2 = o_1.clone("o2")

    o_3 = rel_graph.new_sample_graph("o3")
    o_3_b_t = o_3.add_value_node("B", "b_t")
    o_3_c_t = o_3.add_value_node("C", "c_t")
    o_3.add_relation({o_3_b_t, o_3_c_t}, k_relation)

    o_4 = o_3.clone("o4")
    o_5 = o_3.clone("o5")

    o_6 = rel_graph.new_sample_graph("o6")
    o_6_a_t = o_6.add_value_node("A", "a_t")
    o_6_b_t = o_6.add_value_node("B", "b_t")
    o_6_c_t = o_6.add_value_node("C", "c_t")
    o_6.add_relation({o_6_a_t, o_6_b_t}, k_relation)
    o_6.add_relation({o_6_b_t, o_6_c_t}, k_relation)

    o_7 = rel_graph.new_sample_graph("o7")
    o_7.add_value_node("C", "c_t")

    o_8 = rel_graph.new_sample_graph("o8")
    o_8_b_t = o_8.add_value_node("B", "b_t")
    o_8_c_t = o_8.add_value_node("C", "c_t")
    o_8.add_relation({o_8_b_t, o_8_c_t}, l_relation)

    o_9 = rel_graph.new_sample_graph("o9")
    o_9_a_t = o_9.add_value_node("A", "a_t")
    o_9_b_t = o_9.add_value_node("B", "b_t")
    o_9_c_t = o_9.add_value_node("C", "c_t")
    o_9.add_relation({o_9_a_t, o_9_b_t}, l_relation)
    o_9.add_relation({o_9_b_t, o_9_c_t}, k_relation)

    o_10 = rel_graph.new_sample_graph("o10")
    o_10_a_t = o_10.add_value_node("A", "a_t")
    o_10_b_t = o_10.add_value_node("B", "b_t")
    o_10_c_t = o_10.add_value_node("C", "c_t")
    o_10.add_relation({o_10_a_t, o_10_c_t}, l_relation)
    o_10.add_relation({o_10_b_t, o_10_c_t}, k_relation)

    rel_graph.add_outcomes([o_1, o_2, o_3, o_4, o_5, o_6, o_7, o_8, o_9, o_10])

    # rel_graph.show_all_outcomes()
    print(rel_graph.describe())

    return rel_graph, (k_relation, l_relation)


def run_active_values(rel_graph: RelationGraph, relations: Tuple[RelationType, RelationType]):
    k_relation, l_relation = relations

    q_c = rel_graph.new_sample_graph("q_c")
    q_c.add_value_node("C", "c_t")
    i_c = rel_graph.inference(q_c)
    print(i_c.describe())
    i_c.show_outcomes()

    def print_data(act_values: List[ActiveValue]) -> None:
        for av in act_values:
            print(f"    {av}")
            for r in av.active_relations:
                print(f"        {r}")

    print("##### all active_values:")
    print_data( i_c.get_active_values())
    print("##### K active_values:")
    print_data(i_c.get_active_values([k_relation]))
    print("##### L active_values:")
    print_data(i_c.get_active_values([l_relation]))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    graph, rs = build_rel_graph_example()
    run_active_values(graph, rs)
