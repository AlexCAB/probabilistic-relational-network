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

from typing import Any, Dict, Tuple

from pgmpy.factors.discrete import DiscreteFactor
from pgmpy.models import MarkovNetwork

from scripts.relnet.conditional_graph import ConditionalGraph
from scripts.relnet.relation_graph import RelationGraph, RelationGraphBuilder

nodes = ['A', 'B', 'C', 'D']
edges = [
    (['A', 'B'], [30,  5, 1,  10]),
    (['B', 'C'], [100, 1, 1, 100]),
    (['C', 'D'], [1, 100, 100, 1]),
    (['D', 'A'], [100, 1, 1, 100]),
]

joined_values = [
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
                .add_relation({(edge[0], sn), (edge[1], tn)}, "r")\
                .build()
            print(f"Outcome: {outcome}, count = {values[i]}")
            rgb.add_outcome(outcome, values[i])
    rel_graph = rgb.build()
    # rel_graph.visualize_outcomes()
    return rel_graph


def normalize(values: Dict[Any, int]) -> Dict[Any, float]:
    total = float(sum(values.values()))
    return {k: v / total for k, v in values.items()}


def get_markov_prop(factor: DiscreteFactor) -> Dict[Tuple[int, int, int], float]:
    fc = factor.copy()
    fc.normalize()
    return {
        (a, b, c, d): fc.get_value(A=a, B=b, C=c, D=d)
        for a, b, c, d in joined_values
        if factor.get_value(A=a, B=b, C=c, D=d) > 0}


def get_relation_graph_prop(relation_graph: RelationGraph) -> Dict[Tuple[int, int, int], float]:
    all_counts = {(a, b, c, d):  relation_graph.find_for_values(
        {("A", f"A({a})"), ("B", f"B({b})"), ("C", f"C({c})"), ("D", f"D({d})")})
        for a, b, c, d in joined_values}
    return normalize({k: float(c.items().pop()[1]) for k, c in all_counts.items() if c})


def comparing_variable_joint_probability(markov_net: MarkovNetwork, rel_graph: RelationGraph) -> None:
    ab_factor: DiscreteFactor = markov_net.factors[0].copy()
    bc_factor: DiscreteFactor = markov_net.factors[1].copy()
    cd_factor: DiscreteFactor = markov_net.factors[2].copy()
    da_factor: DiscreteFactor = markov_net.factors[3].copy()

    joint_markov: DiscreteFactor = ab_factor * bc_factor * cd_factor * da_factor
    joint_relation_graph: RelationGraph = rel_graph.joined_on_variables()

    print(f"Joint markov:\n{joint_markov}")
    print(f"Joint relation graph:\n{joint_relation_graph.print_samples()}")
    # joint_relation_graph.visualize_outcomes()

    joint_markov.normalize()

    joint_markov_prop = get_markov_prop(joint_markov)
    joint_relation_graph_prop = get_relation_graph_prop(joint_relation_graph)

    print(f"Joint markov prop:         {joint_markov_prop}")
    print(f"Joint relation graph prop: {joint_relation_graph_prop}")

    assert joint_markov_prop == joint_relation_graph_prop, "Expect evaluated probabilities to be same"


def comparing_inference(markov_net: MarkovNetwork, rel_graph: RelationGraph) -> None:
    ab_factor: DiscreteFactor = markov_net.factors[0].copy()
    bc_factor: DiscreteFactor = markov_net.factors[1].copy()
    cd_factor: DiscreteFactor = markov_net.factors[2].copy()
    da_factor: DiscreteFactor = markov_net.factors[3].copy()

    print(f"ab_factor =\n{ab_factor}")
    print(f"da_factor =\n{da_factor}")

    ab_factor.set_value(0, A=1, B=0)
    ab_factor.set_value(0, A=1, B=1)
    da_factor.set_value(0, A=1, D=0)
    da_factor.set_value(0, A=1, D=1)

    print(f"After inference on E=A_0, ab_factor =\n{ab_factor}")
    print(f"After inference on E=A_0, da_factor =\n{da_factor}")

    joint_markov: DiscreteFactor = ab_factor * bc_factor * cd_factor * da_factor

    print(f"joint_markov =\n{joint_markov}")

    evidence = rel_graph.sample_builder().build_single_node("A", "A(0)")
    inference_on_a_0 = rel_graph.conditional_graph(evidence)

    print(f"Inference graph on A_0:\n{inference_on_a_0.print_samples()}")
    # inference_on_a_0.visualize_outcomes()

    joint_inference_graph: RelationGraph = inference_on_a_0.relation_graph().joined_on_variables()

    print(f"Join inference graph on A_0:\n{joint_inference_graph.print_samples()}")
    # joint_inference_graph.visualize_outcomes()

    joint_markov_prop = get_markov_prop(joint_markov)
    joint_inference_prop = get_relation_graph_prop(joint_inference_graph.relation_graph())

    print(f"joint_markov_prop = {joint_markov_prop}")
    print(f"joint_inference_prop = {joint_inference_prop}")

    assert joint_markov_prop == joint_inference_prop, "Expect evaluated probabilities to be same"


def markov_d_separation(markov_net: MarkovNetwork) -> None:
    ab_factor: DiscreteFactor = markov_net.factors[0].copy()
    bc_factor: DiscreteFactor = markov_net.factors[1].copy()
    cd_factor: DiscreteFactor = markov_net.factors[2].copy()
    da_factor: DiscreteFactor = markov_net.factors[3].copy()

    ab_factor.set_value(0, A=1, B=0)
    ab_factor.set_value(0, A=1, B=1)
    da_factor.set_value(0, A=1, D=0)
    da_factor.set_value(0, A=1, D=1)
    bc_factor.set_value(0, C=1, B=0)
    bc_factor.set_value(0, C=1, B=1)
    cd_factor.set_value(0, C=1, D=0)
    cd_factor.set_value(0, C=1, D=1)

    print(f"After inference on E=[A_0,C_0], ab_factor =\n{ab_factor}")
    print(f"After inference on E=[A_0,C_0], bc_factor =\n{bc_factor}")
    print(f"After inference on E=[A_0,C_0], cd_factor =\n{cd_factor}")
    print(f"After inference on E=[A_0,C_0], da_factor =\n{da_factor}")

    joint_markov_ac: DiscreteFactor = ab_factor * bc_factor * cd_factor * da_factor

    print(f"joint_markov_ac =\n{joint_markov_ac}")

    margin_ac_b = joint_markov_ac.copy()
    margin_ac_b.marginalize(['A', 'C', 'D'])
    margin_ac_d = joint_markov_ac.copy()
    margin_ac_d.marginalize(['A', 'B', 'C'])

    print(f"margin_ac_b =\n{margin_ac_b}")
    print(f"margin_ac_d =\n{margin_ac_d}")

    da_factor.set_value(0, D=1, A=0)
    da_factor.set_value(0, D=1, A=1)
    cd_factor.set_value(0, D=1, C=0)
    cd_factor.set_value(0, D=1, C=1)

    print(f"After inference on E=[A_0,C_0,D_0], da_factor =\n{da_factor}")
    print(f"After inference on E=[A_0,C_0,D_0], cd_factor =\n{cd_factor}")

    joint_markov_acb: DiscreteFactor = ab_factor * bc_factor * cd_factor * da_factor

    print(f"joint_markov_acb =\n{joint_markov_acb}")

    margin_acb_b = joint_markov_acb.copy()
    margin_acb_b.marginalize(['A', 'C', 'D'])

    print(f"margin_acb_b =\n{margin_acb_b}")

    margin_ac_b.normalize()
    margin_acb_b.normalize()

    print(f"margin_ac_b.normalize =\n{margin_ac_b}")
    print(f"margin_acb_b.normalize =\n{margin_acb_b}")

    assert margin_ac_b == margin_acb_b, "Expect evaluated probabilities to be same"


def relation_graph_d_separation(rel_graph: RelationGraph) -> None:
    inference_on_a: ConditionalGraph = rel_graph.conditional_graph(
        rel_graph.sample_builder().build_single_node("A", "A(0)"))
    inference_on_ac: ConditionalGraph = inference_on_a.relation_graph().conditional_graph(
        rel_graph.sample_builder().build_single_node("C", "C(0)"))

    print(f"Inference graph on A_0 and C_0:\n{inference_on_ac.print_samples()}")
    # inference_on_ac.visualize_outcomes()

    joint_graph_ac: RelationGraph = inference_on_ac.relation_graph().joined_on_variables()

    print(f"Joined inference graph on A_0 and C_0:\n{joint_graph_ac.print_samples()}")
    # joint_graph_ac.visualize_outcomes()

    inference_on_acd: ConditionalGraph = inference_on_ac.relation_graph().conditional_graph(
        rel_graph.sample_builder().build_single_node("D", "D(0)"))

    print(f"Inference graph on A_0 and C_0 and D_0:\n{inference_on_acd.print_samples()}")
    # inference_on_acd.visualize_outcomes()

    joint_graph_acd: RelationGraph = inference_on_acd.relation_graph().joined_on_variables()

    print(f"Joined inference graph on A_0 and C_0 and D_0:\n{joint_graph_acd.print_samples()}")
    # joint_graph_acd.visualize_outcomes()

    marginal_prop_ac = joint_graph_ac.marginal_variables_probability()
    marginal_prop_acd = joint_graph_acd.marginal_variables_probability()

    print(f"marginal_prop_ac = {marginal_prop_ac}")
    print(f"marginal_prop_acd = {marginal_prop_acd}")

    assert marginal_prop_ac["B"] == marginal_prop_acd["B"], "Expect evaluated probabilities to be same"


if __name__ == '__main__':
    mn = make_markov_network()
    rg = make_relation_graph()
    comparing_variable_joint_probability(mn, rg)
    comparing_inference(mn, rg)
    markov_d_separation(mn)
    relation_graph_d_separation(rg)
