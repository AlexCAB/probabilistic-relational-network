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
from typing import List

from scripts.relationnetlib.relation_graph import RelationGraph
from scripts.relationnetlib.relation_type import RelationType
from scripts.relationnetlib.variable_node import VariableNode


def outcomes_space_power():

    # Parameters

    max_number_of_variables = 5
    max_number_of_values = 5
    max_number_of_relation_type = 5

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

    def calc_number_of_outcomes(n_variables: int, n_values: int, n_rel_type: int) -> int:

        def c_k(k: int) -> float:
            if k == 0:
                return 1
            else:
                st = 0
                for i in range(1, k):
                    g = i * math.comb(k, i) * ((n_rel_type + 1) ** ((k - i) * ((k - i - 1) / 2))) * c_k(i)
                    st += g
                r = ((n_rel_type + 1) ** (k * ((k - 1) / 2))) - (st / k)
                return r

        def n_k(n: int) -> float:
            sk = 0
            for k in range(1, n + 1):
                ck = c_k(k) * (n_values ** k)
                t = (math.comb(n, k) * ck)
                sk += t
            return sk

        space_power = int(n_k(n_variables))

        log.info(
            f"[calc_number_of_outcomes] n_variables = {n_variables}, n_values = {n_values}, "
            f"n_rel_type = {n_rel_type}, space_power = {space_power}")

        return space_power

    # Count and compare

    for n_var in range(1, max_number_of_variables + 1):
        for n_val in range(1, max_number_of_values + 1):
            for n_rel in range(1, max_number_of_relation_type + 1):
                n_generated = make_relation_graph_and_count_outcomes(n_var, n_val, n_rel)
                n_counted = calc_number_of_outcomes(n_var, n_val, n_rel)
                log.info(
                    f"[make_relation_graph] n_var = {n_var},  n_val = {n_val}, n_rel = {n_rel}, "
                    f"n_generated = {n_generated}, n_counted = {n_counted}")
                assert n_generated == n_counted, f"Ops! n_generated ({n_generated}) != n_counted ({n_counted})"


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    outcomes_space_power()
