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
created: 2021-08-23
"""

from scripts.relationnetlib.relation_graph import RelationGraph
from scripts.relationnetlib.relation_type import RelationType
from scripts.relationnetlib.variable_node import VariableNode


def main():

    relation_types = [
        RelationType("forward"),
        RelationType("backward")
    ]

    variables = [
        VariableNode("A", ["a_1", "a_2", "a_3"]),
        VariableNode("B", ["b_1", "b_2", "b_3"]),
        VariableNode("C", ["c_1", "c_2", "c_3"])
    ]

    rel_graph = RelationGraph("test_relation_graph", relation_types, variables)

    outcome_1 = rel_graph.new_sample_graph("o1", 1)
    outcome_1_a_1 = outcome_1.add_value_node("A", "a_1")
    outcome_1_b_2 = outcome_1.add_value_node("B", "b_2")
    outcome_1_c_3 = outcome_1.add_value_node("C", "c_3")
    outcome_1.add_relation(outcome_1_a_1, outcome_1_b_2, "forward")
    outcome_1.add_relation(outcome_1_b_2, outcome_1_c_3, "forward")
    outcome_1.add_relation(outcome_1_c_3, outcome_1_a_1, "forward")

    outcome_2 = rel_graph.new_sample_graph("o2", 2)
    outcome_2_a_2 = outcome_2.add_value_node("A", "a_2")
    outcome_2_b_3 = outcome_2.add_value_node("B", "b_3")
    outcome_2.add_relation(outcome_2_a_2, outcome_2_b_3, "backward")

    outcome_3 = rel_graph.new_sample_graph("o3", 1)
    outcome_1_b_1 = outcome_3.add_value_node("B", "b_1")
    outcome_1_c_1 = outcome_3.add_value_node("C", "c_3")
    outcome_1.add_relation(outcome_1_b_1, outcome_1_c_1, "backward")

    rel_graph.add_outcomes([outcome_1, outcome_2, outcome_3])

    rel_graph.show_relation_graph()






































if __name__ == '__main__':
    main()
