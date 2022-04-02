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
from math import isclose
from typing import Any, Dict, Tuple, List

from scripts.relnet.graph_components import DirectedRelation
from scripts.relnet.conditional_graph import ConditionalGraph
from scripts.relnet.relation_graph import RelationGraph, RelationGraphBuilder

from pgmpy.inference import VariableElimination
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD, DiscreteFactor

from scripts.relnet.sample_graph import SampleGraph
from itertools import product


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
        print(f"[make_bayes_network] bayes_cpd:\n{cpd}")

    model = BayesianNetwork([('D', 'G'), ('I', 'G'), ('I', 'S'), ('G', 'L')])
    model.add_cpds(*all_cpd)

    return model


def _value_combination(variables: List[Tuple[str, int]]) -> List[List[str]]:
    (var, card) = variables[0]
    if len(variables) > 1:
        return [[f"{var}({j})"] + vs for j in range(0, card) for vs in _value_combination(variables[1:])]
    else:
        return [[f"{var}({j})"] for j in range(0, card)]


def _value_map_from_cpd(
        var: str, card: int, p_var: List[str], p_card: List[int], cpd: List[List[float]]
) -> Dict[frozenset[str], float]:
    values = {}

    for i in range(0, card):
        if p_var and p_card:
            p_vs = [[f"{var}({i})"] + vs for vs in _value_combination(list(zip(p_var, p_card)))]
            for v, p in list(zip(p_vs, cpd[i])):
                values[frozenset(v)] = p
        else:
            values[frozenset({f"{var}({i})"})] = cpd[i][0]

    return values


def _build_outcome(rgb: RelationGraphBuilder, var: str, p_var: List[str], vs: List[str]) -> SampleGraph:
    if p_var:
        o_builder = rgb.sample_builder()
        for p_v in p_var:
            o_builder.add_relation(
                {(p_v, next(v for v in vs if p_v in v)), (var, next(v for v in vs if var in v))},
                DirectedRelation(p_v, var, "r"))
        return o_builder.build()
    else:
        assert len(vs) == 1, f"[_build_outcome] Expect exactly 1 value but got: {vs}"
        return rgb.sample_builder().build_single_node(var, vs[0])


def make_relation_graph() -> RelationGraph:
    rgb = RelationGraphBuilder(
        variables={var: {f"{var}({i})" for i in range(0, card)} for var, (card, _, _, _) in net_config.items()},
        relations={"r"})

    for var, (card, cpd, p_var, p_card) in net_config.items():
        for vs, prop in _value_map_from_cpd(var, card, p_var, p_card, cpd).items():
            outcome = _build_outcome(rgb, var, p_var, list(vs))
            count = int(prop * prop_factor)
            assert count == (prop * prop_factor), "[make_relation_graph] Select correct 'prop_factor'"
            print(f"[make_relation_graph] Outcome: {outcome}, count = {count}")
            rgb.add_outcome(outcome, count)

    rel_graph = rgb.build()
    print(f"[make_relation_graph] rel_graph:\n{rel_graph.print_samples()}")
    # rel_graph.visualize_outcomes()
    # rel_graph.folded_graph().visualize()

    return rel_graph


def _value_map_from_factor(factor: DiscreteFactor) -> Dict[frozenset[str], float]:
    return {frozenset(vs): factor.get_value(**{v[0]: int(v[2]) for v in vs})
            for vs in _value_combination(list(zip(factor.variables, factor.cardinality)))}


def _value_map_from_graph(graph: RelationGraph) -> Dict[frozenset[str], float]:
    return {frozenset(v for _, v in o.values()): c for o, c in graph.outcomes.items()}


def _normalize(values: Dict[Any, float]) -> Dict[Any, float]:
    total = float(sum(values.values()))
    return {k: v / total for k, v in values.items()}


def _marginals_from_factor(factor: DiscreteFactor) -> Dict[str, Dict[str, float]]:
    vs = list(zip(factor.variables, factor.cardinality))
    vl = len(vs)
    acc = {}

    for i in range(0, vl):
        mf = factor.marginalize([v for v, _ in (vs[:i] + vs[i + 1:])], inplace=False)
        v, c = vs[i]
        acc[v] = {f"{v}({j})": mf.get_value(**{v: j}) for j in range(0, c)}

    return acc


def _compare_margin_map(factor_map: Dict[str, Dict[str, float]], graph_map: Dict[str, Dict[str, float]]) -> None:
    assert factor_map.keys() == graph_map.keys(), \
        f"[_compare_margin_map] Keys set of factor_values and graph_values are not " \
        f"same: {factor_map.keys()} != {graph_map.keys()}"

    for var_k in sorted(factor_map):
        factor_mar = factor_map[var_k]
        graph_mar = graph_map[var_k]

        print(f"[_compare_margin_map] At key = {var_k} factor_mar = {factor_mar}, graph_mar = {graph_mar}")

        assert factor_mar.keys() == graph_mar.keys(), \
            f"[_compare_margin_map] Keys set of factor_mar and graph_mar are not " \
            f"same: {factor_mar.keys()} != {graph_mar.keys()}"

        for val_k in sorted(factor_mar):
            assert isclose(factor_mar[val_k], graph_mar[val_k], rel_tol=1e-15, abs_tol=0.0), \
                f"At key = {var_k}_{val_k} marginal probability is not equals factor_mar = {factor_mar[val_k]}, " \
                f"graph_mar = {graph_mar[val_k]}"


def _compare_values_map(factor_values: Dict[frozenset[str], float], graph_values: Dict[frozenset[str], float]) -> None:
    assert factor_values.keys() == graph_values.keys(), \
        f"[_compare_values_map] Keys set of factor_values and graph_values are not " \
        f"same: {factor_values.keys()} != {graph_values.keys()}"

    for key in sorted(factor_values):
        factor_val = factor_values[key]
        graph_val = graph_values[key]

        print(f"[comparing_joint_probability] At key = {key} factor_value = {factor_val}, graph_value = {graph_val}")

        assert isclose(factor_val, graph_val, rel_tol=1e-15, abs_tol=0.0), \
            f"At key = {key} joint probability is not equals factor_value = {factor_val}, graph_value = {graph_val}"


def comparing_joint_probability(bayes_net: BayesianNetwork, rel_graph: RelationGraph) -> None:
    joint_factor: DiscreteFactor = VariableElimination(bayes_net).query(variables=list(net_config.keys()))
    joint_graph: RelationGraph = rel_graph.joined_on_variables()
    joint_factor_len = sum(1 for _ in product(*[range(card) for card in joint_factor.cardinality]))
    joint_graph_len = len(joint_graph.outcomes.items())

    print(f"[comparing_joint_probability] joint_factor ({joint_factor_len}):\n{joint_factor}")
    print(f"[comparing_joint_probability] Joint relation graph({joint_graph_len}):\n{joint_graph.print_samples()}")
    # joint_rgraph.visualize_outcomes()

    assert joint_factor_len == joint_graph_len, \
        "Number of joint outcomes should be same as number rows in joint factor"

    factor_values = _value_map_from_factor(joint_factor)
    graph_values = _normalize(_value_map_from_graph(joint_graph))

    _compare_values_map(factor_values, graph_values)

    factor_marginals = _marginals_from_factor(joint_factor)
    graph_marginals = joint_graph.marginal_variables_probability()

    _compare_margin_map(factor_marginals, graph_marginals)


def _run_inference_on(
        variables: List[str], bayes_net: BayesianNetwork, rel_graph: RelationGraph
) -> Tuple[Dict[str, Dict[str, float]], Dict[str, Dict[str, float]]]:
    inf_factor_i: DiscreteFactor = VariableElimination(bayes_net).query(
            variables=(list(net_config.keys() - variables)),
            evidence={v: 0 for v in variables})
    inf_graph_i = rel_graph

    for v in variables:
        if isinstance(inf_graph_i, ConditionalGraph):
            inf_graph_i = inf_graph_i.relation_graph()
        inf_graph_i = inf_graph_i \
            .conditional_graph(rel_graph.sample_builder().build_single_node(v, f"{v}(0)")) \
            .joined_on_variables()

    return _marginals_from_factor(inf_factor_i), inf_graph_i.marginal_variables_probability()


def comparing_inference(bayes_net: BayesianNetwork, rel_graph: RelationGraph) -> None:
    margin_factor_i, margin_graph_i = _run_inference_on(['I'], bayes_net, rel_graph)

    print(f"[comparing_inference] margin_factor_i = {margin_factor_i}")
    print(f"[comparing_inference] margin_graph_i = {margin_graph_i}")

    margin_graph_i.pop('I')
    _compare_margin_map(margin_factor_i, margin_graph_i)

    margin_factor_ig, margin_graph_ig = _run_inference_on(['I', 'G'], bayes_net, rel_graph)

    print(f"[comparing_inference] margin_factor_ig = {margin_factor_ig}")
    print(f"[comparing_inference] margin_graph_ig = {margin_graph_ig}")

    margin_graph_ig.pop('I')
    margin_graph_ig.pop('G')
    _compare_margin_map(margin_factor_ig, margin_graph_ig)


def comparing_d_separation(rel_graph: RelationGraph) -> None:
    joint_graph: RelationGraph = rel_graph.joined_on_variables()
    graph_marginals = joint_graph.marginal_variables_probability()

    print(f"[comparing_d_separation_v_shape] Joint relation graph:\n{joint_graph.print_samples()}")
    print(f"[comparing_d_separation_v_shape] graph_marginals = {graph_marginals}")

    margin_graph_i = rel_graph \
        .conditional_graph(rel_graph.sample_builder().build_single_node('I', f"I(0)")) \
        .joined_on_variables()\
        .marginal_variables_probability()

    print(f"[comparing_d_separation_v_shape] margin_graph_i = {margin_graph_i}")

    assert graph_marginals['D'] == margin_graph_i['D'], \
        "Variable D should not impacted in case variable G is not observed"
    assert graph_marginals['S'] != margin_graph_i['S'], \
        "Variable S should be impacted in case variable I is observed"

    inf_graph_g = rel_graph \
        .conditional_graph(rel_graph.sample_builder().build_single_node('G', f"G(0)")) \
        .joined_on_variables()
    margin_graph_g = inf_graph_g.marginal_variables_probability()

    print(f"[comparing_d_separation_v_shape] margin_graph_g = {margin_graph_g}")

    margin_graph_gi = inf_graph_g \
        .relation_graph()\
        .conditional_graph(rel_graph.sample_builder().build_single_node('I', f"I(0)")) \
        .joined_on_variables() \
        .marginal_variables_probability()

    print(f"[comparing_d_separation_v_shape] margin_graph_gi = {margin_graph_gi}")

    assert margin_graph_g['D'] != margin_graph_gi['D'], \
        "Variable D should be impacted by variable I  in case variable G is observed"

    inf_graph_l = rel_graph \
        .conditional_graph(rel_graph.sample_builder().build_single_node('L', f"L(0)")) \
        .joined_on_variables()
    margin_graph_l = inf_graph_l.marginal_variables_probability()

    print(f"[comparing_d_separation_v_shape] margin_graph_l = {margin_graph_l}")

    margin_graph_li = inf_graph_l \
        .relation_graph() \
        .conditional_graph(rel_graph.sample_builder().build_single_node('I', f"I(0)")) \
        .joined_on_variables() \
        .marginal_variables_probability()

    print(f"[comparing_d_separation_v_shape] margin_graph_li = {margin_graph_li}")

    assert margin_graph_l['D'] != margin_graph_li['D'], \
        "Variable D should be impacted by variable I in case variable L is observed"


if __name__ == '__main__':
    bn = make_bayes_network()
    rg = make_relation_graph()
    comparing_joint_probability(bn, rg)
    comparing_inference(bn, rg)
    comparing_d_separation(rg)
