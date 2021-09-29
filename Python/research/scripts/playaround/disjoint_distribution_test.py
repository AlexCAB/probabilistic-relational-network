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

from scripts.relationnetlib.relation_graph import RelationGraph
from scripts.relationnetlib.relation_type import RelationType
from scripts.relationnetlib.variable_node import VariableNode


def build_rel_graph_example() -> RelationGraph:

    k_relation = RelationType("K")
    l_relation = RelationType("L")

    rel_graph = RelationGraph(
        "disjoint_distribution_example",
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

    rel_graph.add_outcomes([o_1, o_2, o_3, o_4, o_5])

    rel_graph.show_all_outcomes()
    print(rel_graph.describe())

    return rel_graph


def run_disjoint_distribution(rel_graph: RelationGraph):
    print(f"disjoint_distribution = {rel_graph.disjoint_distribution()}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_disjoint_distribution(build_rel_graph_example())
