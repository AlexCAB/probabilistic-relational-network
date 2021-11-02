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

from scripts.relnet.relation_graph import RelationGraphBuilder, RelationGraph


def random_variables_distribution_for_all_outcomes():

    # Parameters

    max_number_of_variables = 3
    max_number_of_values = 3
    max_number_of_relation_type = 3

    # Helpers

    def make_relation_graph(n_variables: int, n_values: int, n_rel_type: int) -> RelationGraph:
        relation_types = {f"RT_{i}" for i in range(1, n_rel_type + 1)}
        variables = {
            f"VAR_{i}": [f"VAL_{i}_{j}" for j in range(1, n_values + 1) if not (i == 1 and j == 2)]
            for i in range(1, n_variables + 1)}

        relation_graph = RelationGraphBuilder(variables, relation_types, "outcomes_space_power") \
            .generate_all_possible_outcomes() \
            .build()

        return relation_graph

    def calc_variables_distribution(relation_graph: RelationGraph) -> None:
        folded_graph = relation_graph.folded_graph()

        for variable, _ in relation_graph.variables:
            distribution = folded_graph.folded_node(variable).marginal_distribution()

            print(f"V_ID = {variable}, distribution = {distribution}")

            unobserved = distribution.pop('unobserved')
            first_value, first_value_prop = list(distribution.items())[0]

            for value, prop in distribution.items():
                assert first_value_prop == prop, \
                    f"Value {value} of variable {variable} have not same prob {prop} as first " \
                    f"value {first_value}, which have prob {first_value_prop}, this should not happens."
                assert unobserved != prop, \
                    f"Value {value} have same prob {prop} as unobserved value, " \
                    f"this should not happens."

    # Run over ala graphs

    for n_var in range(1, max_number_of_variables + 1):
        for n_val in range(1, max_number_of_values + 1):
            for n_rel in range(1, max_number_of_relation_type + 1):
                calc_variables_distribution(make_relation_graph(n_var, n_val, n_rel))


if __name__ == '__main__':
    random_variables_distribution_for_all_outcomes()
