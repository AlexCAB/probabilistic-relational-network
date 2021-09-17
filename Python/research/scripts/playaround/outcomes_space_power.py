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
created: 2021-09-17
"""

import logging
import math

from scripts.relationnetlib.relation_graph import RelationGraph
from scripts.relationnetlib.relation_type import RelationType
from scripts.relationnetlib.variable_node import VariableNode


def outcomes_space_power():

    # Parameters

    max_number_of_variables = 3
    max_number_of_values = 3
    max_number_of_relation_type = 3

    # Helpers

    log = logging.getLogger('outcomes_space_power')

    def make_relation_graph_and_count_outcomes(n_variables: int, n_values: int, n_rel_type: int) -> int:
        relation_types = [RelationType(f"RT_{i}") for i in range(1, n_rel_type + 1)]
        variables = [VariableNode(f"VAR_{i}", [f"VAL_{i}_{j}" for j in range(1, n_values + 1)])
                     for i in range(1, n_variables + 1)]
        log.info(f"[make_relation_graph] make for relation_types = {relation_types}, variables = {variables}")
        relation_graph = RelationGraph("outcomes_space_power", relation_types, variables)
        relation_graph.generate_all_possible_outcomes()
        number_of_outcomes = relation_graph.get_number_of_outcomes()
        return number_of_outcomes

    def calc_number_of_outcomes(n_gen: int, n_variables: int, n_values: int, n_rel_type: int) -> float:

        math.factorial(n_variables) / (math.factorial(n_values))


        def calc_for_variables(n_v: int) -> float:
            return ((n_rel_type + 1) ** ((n_v * (n_v - 1)) / 2)) + n_v - 1

        n_for_variables = calc_for_variables(n_variables)

        n_subtract = calc_for_variables(n_variables - 1)
        n_to_add = (n_for_variables - n_subtract)
        space_power = 0

        print(
            f"n_gen = {n_gen}, n_variables = {n_variables}, n_values = {n_values}, n_rel_type = {n_rel_type}, "
            f"n_for_variables = {n_for_variables},  n_subtract = {n_subtract}, n_to_add = {n_to_add}")


        for i in range(0, n_values - 1):
            print(f"RRRR i = {i}")
            if i == 0:
                space_power = n_for_variables
            if i == 1:
                space_power += n_to_add
            if i == 2:
                space_power += n_to_add
            if i == 3:
                space_power += n_to_add

        space_power *= n_variables

        print(
            f"n_gen = {n_gen}, space_power = {space_power}, n_variables = {n_variables}, n_values = {n_values}, n_rel_type = {n_rel_type}, "
            f"n_for_variables = {n_for_variables},  n_subtract = {n_subtract}, n_to_add = {n_to_add}")

        # space_power = (n_values * (n_for_variables - n_subtract)) ** n_variables

        log.info(
            f"[calc_number_of_outcomes] n_variables = {n_variables}, n_values = {n_values}, "
            f"n_for_variables = {n_for_variables}, n_subtract = {n_subtract}")

        return space_power

    # Count and compare

    # for n_var in range(1, max_number_of_variables + 1):
    #     for n_val in range(1, max_number_of_values + 1):
    #         for n_rel in range(1, max_number_of_relation_type + 1):
    #             n_generated = make_relation_graph_and_count_outcomes(n_var, n_val, n_rel)
    #             n_counted = calc_number_of_outcomes(n_generated, n_var, n_val, n_rel)
    #             log.info(
    #                 f"[make_relation_graph] n_var = {n_var},  n_val = {n_val}, n_rel = {n_rel}, "
    #                 f"n_generated = {n_generated}, n_counted = {n_counted}")
    n_generated = make_relation_graph_and_count_outcomes(3, 1, 1)
    n_counted = calc_number_of_outcomes(n_generated, 3, 1, 1)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    outcomes_space_power()
