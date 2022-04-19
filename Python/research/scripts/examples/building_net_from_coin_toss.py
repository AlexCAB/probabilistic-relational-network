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
created: 2022-04-14
"""

from math import isclose
from typing import Any, Dict, Tuple, List

from scripts.relnet.graph_components import DirectedRelation
from scripts.relnet.conditional_graph import ConditionalGraph
from scripts.relnet.relation_graph import RelationGraph, RelationGraphBuilder

from pgmpy.inference import VariableElimination
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD, DiscreteFactor

from scripts.relnet.sample_graph import SampleGraph, SampleGraphBuilder
from itertools import product


experiment_results = [
    "5¢ H",
    "1¢ H",
    "5¢ H",
    "25¢ T",
    "1¢ H",
    "5¢ H",
    "5¢ H then 25¢ H",
    "1¢ H then 5¢ H",
    "25¢ T then 5¢ T",
    "1¢ T then 5¢ T"
]


def build_outcome(t: str, builder: SampleGraphBuilder) -> SampleGraph:

    def pare_var(var: str, val: str) -> (str, str):
        match var:
            case "1¢":
                match val:
                    case "H":
                        return 'V1', 'h1'
                    case "T":
                        return 'V1', 't1'
            case "5¢":
                match val:
                    case "H":
                        return 'V2', 'h2'
                    case "T":
                        return 'V2', 't2'
            case "25¢":
                match val:
                    case "H":
                        return 'V3', 'h3'
                    case "T":
                        return 'V3', 't3'

    match t.split(' '):
        case [var_1, val_1]:
            return builder.build_single_node(*pare_var(var_1, val_1))
        case [var_1, val_1, _, var_2, val_2]:
            return builder\
                .add_relation(
                    {pare_var(var_1, val_1), pare_var(var_2, val_2)},
                    ('r1' if int(var_1[:-1]) < int(var_2[:-1]) else 'r2'))\
                .build()


def build_relation_net(T: List[str]) -> RelationGraph:
    builder = RelationGraphBuilder(
        variables={'V1': {'h1', 't1'}, 'V2': {'h2', 't2'}, 'V3': {'h3', 't3'}},
        relations={'r1', 'r2'})

    for t in T:
        ω = build_outcome(t, builder.sample_builder())
        builder.add_outcome(outcome=ω, count=1)

    return builder.build()


def describe_relation_net(Θ: RelationGraph) -> None:
    print(f"Outcomes:")
    for ω, c in Θ.outcomes.items():
        print(f"    ω = {ω}, c = {c}, P(ω) = {Θ.outcomes.count_of(ω) / Θ.outcomes.length}")


if __name__ == '__main__':
    Θ = build_relation_net(experiment_results)
    describe_relation_net(Θ)
    Θ.visualize_outcomes()
