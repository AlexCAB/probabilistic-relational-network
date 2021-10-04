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
created: 2021-09-29
"""


import logging
import math

from scripts.relationnetlib.relation_graph import RelationGraph
from scripts.relationnetlib.relation_type import RelationType
from scripts.relationnetlib.variable_node import VariableNode


def random_variables_distribution_for_all_outcomes():

    # Parameters

    max_number_of_variables = 3
    max_number_of_values = 4
    max_number_of_relation_type = 2

    # Helpers

    log = logging.getLogger('random_variables_distribution_for_all_outcomes')

    def make_relation_graph(n_variables: int, n_values: int, n_rel_type: int) -> RelationGraph:
        relation_types = [RelationType(f"RT_{i}") for i in range(1, n_rel_type + 1)]
        variables = [VariableNode(f"VAR_{i}",
                                  [f"VAL_{i}_{j}" for j in range(1, n_values + 1) if not (i == 1 and j == 2)])
                     for i in range(1, n_variables + 1)]
        relation_graph = RelationGraph("outcomes_space_power", relation_types, variables)
        relation_graph.generate_all_possible_outcomes()
        log.info(f"########### {relation_graph.describe()}")
        return relation_graph

    def calc_variables_distribution(relation_graph: RelationGraph) -> None:
        for var in relation_graph.get_variable_nodes().values():
            distribution = var.marginal_distribution()
            log.info(f"V_ID = {var.variable_id}, distribution = {distribution}")
            unobserved = distribution.pop('unobserved')
            first_var_id, first_var_prop = list(distribution.items())[0]
            for var_id, prop in distribution.items():
                assert first_var_prop == prop, \
                    f"Variable {var_id} have not same prob {prop} as first variable {first_var_id}, " \
                    f"which have prob {first_var_id}, this should not happens."
                assert unobserved != prop, \
                    f"Variable {var_id} have same prob {prop} as unobserved variable, " \
                    f"which have prob {unobserved}, this should not happens."

    # Run over ala graphs

    for n_var in range(1, max_number_of_variables + 1):
        for n_val in range(1, max_number_of_values + 1):
            for n_rel in range(1, max_number_of_relation_type + 1):
                calc_variables_distribution(make_relation_graph(n_var, n_val, n_rel))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    random_variables_distribution_for_all_outcomes()
