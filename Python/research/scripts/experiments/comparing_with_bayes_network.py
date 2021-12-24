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

from typing import Any, Dict, Tuple, List

from pgmpy.factors.discrete import DiscreteFactor
from pgmpy.models import MarkovNetwork

from scripts.relnet.graph_components import DirectedRelation
from scripts.relnet.inference_graph import InferenceGraph
from scripts.relnet.relation_graph import RelationGraph, RelationGraphBuilder

from pgmpy.inference import VariableElimination
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD, DiscreteFactor

from scripts.relnet.sample_graph import SampleGraph

net_config = {
    'D': (2, [[.6], [.4]], None, None),  # Difficulty
    'I': (2, [[.7], [.3]], None, None),  # Intelligence
    'G': (3, [
        [.3, .05, .9, .5],
        [.4, .25, .08, .3],
        [.3, .7, .02, .2]], ['I', 'D'], [2, 2]),  # Grade
    'S': (2, [[.95, .2],
              [.05, .8]], ['I'], [2]),  # SAT
    'L': (2, [[.1, .4, .99],
              [.9, .6, .01]], ['G'], [3])   # Latter
}

prop_factor = 100  # User to convert float probability to int number of outcomes


def make_bayes_network() -> BayesianNetwork:
    all_cpd = [
        TabularCPD(var, var_card, values, e_var, e_card)
        for var, (var_card, values, e_var, e_card) in net_config.items()]

    for cpd in all_cpd:
        print(f"bayes_cpd:\n{cpd}")

    model = BayesianNetwork([('D', 'G'), ('I', 'G'), ('I', 'S'), ('G', 'L')])
    model.add_cpds(*all_cpd)

    return model


def value_combination(variables: List[Tuple[str, int]]) -> List[List[str]]:
    (var, card) = variables[0]
    if len(variables) > 1:
        return [[f"{var}({j})"] + vs for j in range(0, card) for vs in value_combination(variables[1:])]
    else:
        return [[f"{var}({j})"] for j in range(0, card)]


def value_map_from_cpd(
        var: str, card: int, p_var: List[str], p_card: List[int], cpd: List[List[float]]
) -> Dict[frozenset[str], float]:
    values = {}

    for i in range(0, card):
        if p_var and p_card:
            p_vs = [[f"{var}({i})"] + vs for vs in value_combination(list(zip(p_var, p_card)))]
            for v, p in list(zip(p_vs, cpd[i])):
                values[frozenset(v)] = p
        else:
            values[frozenset({f"{var}({i})"})] = cpd[i][0]

    return values


def build_outcome(rgb: RelationGraphBuilder, var: str, p_var: List[str], vs: List[str]) -> SampleGraph:
    if p_var:
        o_builder = rgb.sample_builder()
        for p_v in p_var:
            o_builder.add_relation(
                {(p_v, next(v for v in vs if p_v in v)), (var, next(v for v in vs if var in v))},
                DirectedRelation(p_v, var, "r"))
        return o_builder.build()
    else:
        assert len(vs) == 1, f"[make_relation_graph] Expect exactly 1 value but got: {vs}"
        return rgb.sample_builder().build_single_node(var, vs[0])


def make_relation_graph() -> RelationGraph:
    rgb = RelationGraphBuilder(
        variables={var: {f"{var}({i})" for i in range(0, card)} for var, (card, _, _, _) in net_config.items()},
        relations={"r"})

    for var, (card, cpd, p_var, p_card) in net_config.items():
        for vs, prop in value_map_from_cpd(var, card, p_var, p_card, cpd).items():
            outcome = build_outcome(rgb, var, p_var, list(vs))
            count = int(prop * prop_factor)
            assert count == (prop * prop_factor), "[make_relation_graph] Select correct 'prop_factor'"
            print(f"Outcome: {outcome}, count = {count}")
            rgb.add_outcome(outcome, count)

    rel_graph = rgb.build()
    rel_graph.visualize_outcomes()
    # rel_graph.folded_graph().visualize()

    return rel_graph





#
# def normalize(values: Dict[Any, int]) -> Dict[Any, float]:
#     total = float(sum(values.values()))
#     return {k: v / total for k, v in values.items()}
#
#
# def get_markov_prop(factor: DiscreteFactor) -> Dict[Tuple[int, int, int], float]:
#     fc = factor.copy()
#     fc.normalize()
#     return {
#         (a, b, c, d): fc.get_value(A=a, B=b, C=c, D=d)
#         for a, b, c, d in joined_values
#         if factor.get_value(A=a, B=b, C=c, D=d) > 0}
#
#
# def get_relation_graph_prop(relation_graph: RelationGraph) -> Dict[Tuple[int, int, int], float]:
#     all_counts = {(a, b, c, d):  relation_graph.find_for_values(
#         {("A", f"A({a})"), ("B", f"B({b})"), ("C", f"C({c})"), ("D", f"D({d})")})
#         for a, b, c, d in joined_values}
#     return normalize({k: float(c.items().pop()[1]) for k, c in all_counts.items() if c})
#
#
# def comparing_variable_joint_probability(markov_net: MarkovNetwork, rel_graph: RelationGraph) -> None:
#     ab_factor: DiscreteFactor = markov_net.factors[0].copy()
#     bc_factor: DiscreteFactor = markov_net.factors[1].copy()
#     cd_factor: DiscreteFactor = markov_net.factors[2].copy()
#     da_factor: DiscreteFactor = markov_net.factors[3].copy()
#
#     joint_markov: DiscreteFactor = ab_factor * bc_factor * cd_factor * da_factor
#     joint_relation_graph: RelationGraph = rel_graph.joined_on_variables()
#
#     print(f"Joint markov:\n{joint_markov}")
#     print(f"Joint relation graph:\n{joint_relation_graph.print_samples()}")
#     # joint_relation_graph.visualize_outcomes()
#
#     joint_markov.normalize()
#
#     joint_markov_prop = get_markov_prop(joint_markov)
#     joint_relation_graph_prop = get_relation_graph_prop(joint_relation_graph)
#
#     print(f"Joint markov prop:         {joint_markov_prop}")
#     print(f"Joint relation graph prop: {joint_relation_graph_prop}")
#
#     assert joint_markov_prop == joint_relation_graph_prop, "Expect evaluated probabilities to be same"
#
#
# def comparing_inference(markov_net: MarkovNetwork, rel_graph: RelationGraph) -> None:
#     ab_factor: DiscreteFactor = markov_net.factors[0].copy()
#     bc_factor: DiscreteFactor = markov_net.factors[1].copy()
#     cd_factor: DiscreteFactor = markov_net.factors[2].copy()
#     da_factor: DiscreteFactor = markov_net.factors[3].copy()
#
#     print(f"ab_factor =\n{ab_factor}")
#     print(f"da_factor =\n{da_factor}")
#
#     ab_factor.set_value(0, A=1, B=0)
#     ab_factor.set_value(0, A=1, B=1)
#     da_factor.set_value(0, A=1, D=0)
#     da_factor.set_value(0, A=1, D=1)
#
#     print(f"After inference on E=A_0, ab_factor =\n{ab_factor}")
#     print(f"After inference on E=A_0, da_factor =\n{da_factor}")
#
#     joint_markov: DiscreteFactor = ab_factor * bc_factor * cd_factor * da_factor
#
#     print(f"joint_markov =\n{joint_markov}")
#
#     evidence = rel_graph.sample_builder().build_single_node("A", "A(0)")
#     inference_on_a_0 = rel_graph.inference(evidence)
#
#     print(f"Inference graph on A_0:\n{inference_on_a_0.print_samples()}")
#     # inference_on_a_0.visualize_outcomes()
#
#     joint_inference_graph: InferenceGraph = inference_on_a_0.joined_on_variables()
#
#     print(f"Join inference graph on A_0:\n{joint_inference_graph.print_samples()}")
#     # joint_inference_graph.visualize_outcomes()
#
#     joint_markov_prop = get_markov_prop(joint_markov)
#     joint_inference_prop = get_relation_graph_prop(joint_inference_graph.relation_graph())
#
#     print(f"joint_markov_prop = {joint_markov_prop}")
#     print(f"joint_inference_prop = {joint_inference_prop}")
#
#     assert joint_markov_prop == joint_inference_prop, "Expect evaluated probabilities to be same"
#
#
# def markov_d_separation(markov_net: MarkovNetwork) -> None:
#     ab_factor: DiscreteFactor = markov_net.factors[0].copy()
#     bc_factor: DiscreteFactor = markov_net.factors[1].copy()
#     cd_factor: DiscreteFactor = markov_net.factors[2].copy()
#     da_factor: DiscreteFactor = markov_net.factors[3].copy()
#
#     ab_factor.set_value(0, A=1, B=0)
#     ab_factor.set_value(0, A=1, B=1)
#     da_factor.set_value(0, A=1, D=0)
#     da_factor.set_value(0, A=1, D=1)
#     bc_factor.set_value(0, C=1, B=0)
#     bc_factor.set_value(0, C=1, B=1)
#     cd_factor.set_value(0, C=1, D=0)
#     cd_factor.set_value(0, C=1, D=1)
#
#     print(f"After inference on E=[A_0,C_0], ab_factor =\n{ab_factor}")
#     print(f"After inference on E=[A_0,C_0], bc_factor =\n{bc_factor}")
#     print(f"After inference on E=[A_0,C_0], cd_factor =\n{cd_factor}")
#     print(f"After inference on E=[A_0,C_0], da_factor =\n{da_factor}")
#
#     joint_markov_ac: DiscreteFactor = ab_factor * bc_factor * cd_factor * da_factor
#
#     print(f"joint_markov_ac =\n{joint_markov_ac}")
#
#     margin_ac_b = joint_markov_ac.copy()
#     margin_ac_b.marginalize(['A', 'C', 'D'])
#     margin_ac_d = joint_markov_ac.copy()
#     margin_ac_d.marginalize(['A', 'B', 'C'])
#
#     print(f"margin_ac_b =\n{margin_ac_b}")
#     print(f"margin_ac_d =\n{margin_ac_d}")
#
#     da_factor.set_value(0, D=1, A=0)
#     da_factor.set_value(0, D=1, A=1)
#     cd_factor.set_value(0, D=1, C=0)
#     cd_factor.set_value(0, D=1, C=1)
#
#     print(f"After inference on E=[A_0,C_0,D_0], da_factor =\n{da_factor}")
#     print(f"After inference on E=[A_0,C_0,D_0], cd_factor =\n{cd_factor}")
#
#     joint_markov_acb: DiscreteFactor = ab_factor * bc_factor * cd_factor * da_factor
#
#     print(f"joint_markov_acb =\n{joint_markov_acb}")
#
#     margin_acb_b = joint_markov_acb.copy()
#     margin_acb_b.marginalize(['A', 'C', 'D'])
#
#     print(f"margin_acb_b =\n{margin_acb_b}")
#
#     margin_ac_b.normalize()
#     margin_acb_b.normalize()
#
#     print(f"margin_ac_b.normalize =\n{margin_ac_b}")
#     print(f"margin_acb_b.normalize =\n{margin_acb_b}")
#
#     assert margin_ac_b == margin_acb_b, "Expect evaluated probabilities to be same"
#
#
# def relation_graph_d_separation(rel_graph: RelationGraph) -> None:
#     inference_on_a: InferenceGraph = rel_graph.inference(
#         rel_graph.sample_builder().build_single_node("A", "A(0)"))
#     inference_on_ac: InferenceGraph = inference_on_a.relation_graph().inference(
#         rel_graph.sample_builder().build_single_node("C", "C(0)"))
#
#     print(f"Inference graph on A_0 and C_0:\n{inference_on_ac.print_samples()}")
#     # inference_on_ac.visualize_outcomes()
#
#     joint_graph_ac: InferenceGraph = inference_on_ac.joined_on_variables()
#
#     print(f"Joined inference graph on A_0 and C_0:\n{joint_graph_ac.print_samples()}")
#     # joint_graph_ac.visualize_outcomes()
#
#     inference_on_acd: InferenceGraph = inference_on_ac.relation_graph().inference(
#         rel_graph.sample_builder().build_single_node("D", "D(0)"))
#
#     print(f"Inference graph on A_0 and C_0 and D_0:\n{inference_on_acd.print_samples()}")
#     # inference_on_acd.visualize_outcomes()
#
#     joint_graph_acd: InferenceGraph = inference_on_acd.joined_on_variables()
#
#     print(f"Joined inference graph on A_0 and C_0 and D_0:\n{joint_graph_acd.print_samples()}")
#     # joint_graph_acd.visualize_outcomes()
#
#     marginal_prop_ac = joint_graph_ac.marginal_variables_probability()
#     marginal_prop_acd = joint_graph_acd.marginal_variables_probability()
#
#     print(f"marginal_prop_ac = {marginal_prop_ac}")
#     print(f"marginal_prop_acd = {marginal_prop_acd}")
#
#     assert marginal_prop_ac["B"] == marginal_prop_acd["B"], "Expect evaluated probabilities to be same"


if __name__ == '__main__':
    # bn = make_bayes_network()
    rg = make_relation_graph()
    # comparing_variable_joint_probability(mn, rg)
    # comparing_inference(mn, rg)
    # markov_d_separation(mn)
    # relation_graph_d_separation(rg)
