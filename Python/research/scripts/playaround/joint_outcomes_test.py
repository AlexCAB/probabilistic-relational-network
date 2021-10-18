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
created: 2021-10-13
"""

import logging
from typing import List, Tuple

from scripts.relationnetlib.relation_graph import RelationGraph
from scripts.relationnetlib.relation_type import RelationType
from scripts.relationnetlib.sample_graph import SampleGraph
from scripts.relationnetlib.variable_node import VariableNode


log = logging.getLogger('joint_outcomes_test')


def make_relation_graph() -> RelationGraph:

    k_relation = RelationType("k")
    l_relation = RelationType("l")

    rel_graph = RelationGraph(
        "disjoint_distribution_example",
        relations=[
            k_relation,
            l_relation,
        ],
        variables=[
            VariableNode("a", ["a_t", "a_f"]),
            VariableNode("b", ["b_t", "b_f"]),
            VariableNode("c", ["c_t", "c_f"]),
            VariableNode("d", ["d_t", "d_f"]),
        ]
    )

    def make_chain_outcome(value_ids: List[Tuple[str, str]], relations: List[RelationType]) -> SampleGraph:
        outcome = rel_graph.new_sample_graph('--'.join([vid for _, vid in value_ids]))
        value_nodes = [outcome.add_value_node(var_id, val_id) for var_id, val_id in value_ids]
        for i in range(0, len(value_nodes) - 1):
            outcome.add_relation({value_nodes[i], value_nodes[i + 1]}, relations[i])
        return outcome

    o_abc_ttt = make_chain_outcome([("a", "a_t"), ("b", "b_t"), ("c", "c_t")], [k_relation, k_relation])
    o_dbc_ttt = make_chain_outcome([("b", "b_t"), ("c", "c_t"), ("d", "d_t")], [k_relation, k_relation])

    rel_graph.add_outcomes_with_count([(o_abc_ttt, 10), (o_dbc_ttt, 5)])

    rel_graph.show_all_outcomes()

    return rel_graph


def joint_outcomes_test(rg: RelationGraph) -> None:
    pass




















if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    joint_outcomes_test(make_relation_graph())
