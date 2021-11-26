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
created: 2021-10-12
"""

from typing import Any, Dict

from pgmpy.factors.discrete import DiscreteFactor
from pgmpy.models import MarkovNetwork

from scripts.relnet.relation_graph import RelationGraph, RelationGraphBuilder


nodes = ['A', 'B', 'C', 'D']
edges = [
    (['A', 'B'], [30,  5, 1,  10]),
    (['B', 'C'], [100, 1, 1, 100]),
    (['C', 'D'], [1, 100, 100, 1]),
    (['D', 'A'], [100, 1, 1, 100]),
]


def make_markov_network() -> MarkovNetwork:
    g = MarkovNetwork()
    g.add_nodes_from(nodes=nodes)
    g.add_edges_from(ebunch=[e[0] for e in edges])
    for edge, values in edges:
        f = DiscreteFactor(edge, cardinality=[2, 2], values=values)
        g.add_factors(f)
        print(f"Factor: \n {f}")
    return g


def make_relation_graph() -> RelationGraph:
    rgb = RelationGraphBuilder(
        variables={n: {f"{n}(0)", f"{n}(1)"} for n in nodes},
        relations={"r"})
    for edge, values in edges:
        for sid, tid, i in [(0, 0, 0), (0, 1, 1), (1, 0, 2), (1, 1, 3)]:
            sn = f"{edge[0]}({sid})"
            tn = f"{edge[1]}({tid})"
            outcome = rgb.sample_builder()\
                .set_name(f"{sn}-{tn}_{values[i]}")\
                .add_relation({(edge[0], sn), (edge[1], tn)}, "r")\
                .build()
            print(f"Outcome: {outcome}")
            rgb.add_outcome(outcome, values[i])
    rel_graph = rgb.build()
    # rel_graph.visualize_outcomes()
    return rel_graph


def normalize(values: Dict[Any, int]) -> Dict[Any, float]:
    total = float(sum(values.values()))
    return {k: v / total for k, v in values.items()}


def comparing_variable_margin_probability(markov_net: MarkovNetwork, rel_graph: RelationGraph) -> None:
    ab_factor = markov_net.factors[0]
    bc_factor = markov_net.factors[1]
    cd_factor = markov_net.factors[2]
    da_factor = markov_net.factors[3]

    joint_markov: DiscreteFactor = ab_factor * bc_factor * cd_factor * da_factor
    joint_relation_graph: RelationGraph = rel_graph.joined_on_variables()

    print(f"Joint markov:\n{joint_markov}")
    print(f"Joint relation graph:\n{joint_relation_graph.print_samples()}")

    values = [
        (0, 0, 0, 0),
        (0, 0, 0, 1),
        (0, 0, 1, 0),
        (0, 0, 1, 1),
        (0, 1, 0, 0),
        (0, 1, 0, 1),
        (0, 1, 1, 0),
        (0, 1, 1, 1),
        (1, 0, 0, 0),
        (1, 0, 0, 1),
        (1, 0, 1, 0),
        (1, 0, 1, 1),
        (1, 1, 0, 0),
        (1, 1, 0, 1),
        (1, 1, 1, 0),
        (1, 1, 1, 1)]

    joint_markov.normalize()

    joint_markov_prop = {
        (a, b, c, d): joint_markov.get_value(A=a, B=b, C=c, D=d)
        for a, b, c, d in values}

    joint_relation_graph_prop = normalize({
        (a, b, c, d): float(joint_relation_graph
                            .find_for_values({("A", f"A({a})"), ("B", f"B({b})"), ("C", f"C({c})"), ("D", f"D({d})")})
                            .items().pop()[1])
        for a, b, c, d in values})

    print(f"Joint markov prop:         {joint_markov_prop}")
    print(f"Joint relation graph prop: {joint_relation_graph_prop}")

    assert joint_markov_prop == joint_relation_graph_prop, "Expect evaluated probabilities to be same"


if __name__ == '__main__':
    mn = make_markov_network()
    rg = make_relation_graph()
    comparing_variable_margin_probability(mn, rg)
