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
created: 2021-12-10
tutorial: https://pgmpy.org/models/bayesiannetwork.html
"""

from typing import Dict

from pgmpy.inference import VariableElimination
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD, DiscreteFactor


def pgmpy_bayes_net_test() -> None:

    model = BayesianNetwork([('D', 'G'), ('I', 'G')])

    print(f"model.nodes = {model.nodes}")
    print(f"model.edges = {model.edges}")

    cpd_d = TabularCPD('D', 2, [[0.6], [0.4]])
    cpd_i = TabularCPD('I', 2, [[0.7], [0.3]])
    cpd_g = TabularCPD('G', 2,
                       [[0.3, 0.05, 0.9, 0.5],
                        [0.7, 0.95, 0.1, 0.5]],
                       ['I', 'D'], [2, 2])

    print(f"cpd_d:\n{cpd_d}")
    print(f"cpd_i:\n{cpd_i}")
    print(f"cpd_g:\n{cpd_g}")

    model.add_cpds(cpd_d, cpd_i, cpd_g)
    assert model.check_model(), "Model inconsistent"

    joint_factor: DiscreteFactor = VariableElimination(model).query(variables=['D', 'G', 'I'])

    print(f"joint_factor:\n{joint_factor}")

    margin_d = joint_factor.marginalize(['G', 'I'], inplace=False)
    margin_g = joint_factor.marginalize(['D', 'I'], inplace=False)
    margin_i = joint_factor.marginalize(['D', 'G'], inplace=False)

    print(f"margin_d:\n{margin_d}")
    print(f"margin_g:\n{margin_g}")
    print(f"margin_i:\n{margin_i}")

    joint_factor_d: DiscreteFactor = VariableElimination(model).query(
        variables=['G', 'I'], evidence={'D': 0})

    print(f"joint_factor_d:\n{joint_factor_d}")

    margin_g_d = joint_factor_d.marginalize(['I'], inplace=False)
    margin_i_d = joint_factor_d.marginalize(['G'], inplace=False)

    print(f"margin_g_d:\n{margin_g_d}")
    print(f"margin_i_d:\n{margin_i_d}")


def manual_bayes_net_test() -> None:

    cpd_d = {
        frozenset({'d_0'}): 0.6,
        frozenset({'d_1'}): 0.4}

    cpd_i = {
        frozenset({'i_0'}): 0.7,
        frozenset({'i_1'}): 0.3}

    cpd_g = {
        frozenset({'i_0', 'd_0', 'g_0'}): 0.3,
        frozenset({'i_0', 'd_0', 'g_1'}): 0.7,

        frozenset({'i_0', 'd_1', 'g_0'}): 0.05,
        frozenset({'i_0', 'd_1', 'g_1'}): 0.95,

        frozenset({'i_1', 'd_0', 'g_0'}): 0.9,
        frozenset({'i_1', 'd_0', 'g_1'}): 0.1,

        frozenset({'i_1', 'd_1', 'g_0'}): 0.5,
        frozenset({'i_1', 'd_1', 'g_1'}): 0.5,
    }

    def cpd_product(x_1: Dict[frozenset, float], x_2: Dict[frozenset, float]) -> Dict[frozenset, float]:
        res = {}
        for k_1, v_1 in x_1.items():
            for k_2, v_2 in x_2.items():
                if not k_1.isdisjoint(k_2):
                    res[k_1.union(k_2)] = v_1 * v_2
        return res

    def norm(x:  Dict[frozenset, float]) -> Dict[frozenset, float]:
        t = sum(x.values())
        return {k: v / t for k, v in x.items()}

    def margin(cpd:  Dict[frozenset, float], var: str) -> Dict[str, float]:
        res = {}
        for k, v in cpd.items():
            vs = [e for e in k if var in e]
            if vs:
                res[vs[0]] = res.get(vs[0], 0.0) + v
        return res

    def select_value(cpd:  Dict[frozenset, float], val: str) -> Dict[frozenset, float]:
        return {k: v for k, v in cpd.items() if val in k}

    joint_factor = cpd_product(cpd_d, cpd_product(cpd_i, cpd_g))

    print(f"joint_factor = {joint_factor}")
    print(f"margin on D = {margin(joint_factor, 'd')}")
    print(f"margin on I = {margin(joint_factor, 'i')}")
    print(f"margin on G = {margin(joint_factor, 'g')}")

    cpd_d_1 = select_value(cpd_d, 'd_1')

    print(f"cpd_d_1 = {cpd_d_1}")

    joint_factor_d = norm(cpd_product(cpd_d_1, cpd_product(cpd_i, cpd_g)))

    print(f"joint_factor_d = {joint_factor_d}")
    print(f"margin on D where d = {margin(joint_factor_d, 'd')}")
    print(f"margin on I where d  = {margin(joint_factor_d, 'i')}")
    print(f"margin on G where d  = {margin(joint_factor_d, 'g')}")

    cpd_g_1 = select_value(cpd_g, 'g_1')

    print(f"cpd_g_1 = {cpd_g_1}")

    joint_factor_g = norm(cpd_product(cpd_d, cpd_product(cpd_i, cpd_g_1)))

    print(f"joint_factor_g = {joint_factor_g}")
    print(f"margin on D where g = {margin(joint_factor_g, 'd')}")
    print(f"margin on I where g = {margin(joint_factor_g, 'i')}")
    print(f"margin on G where g = {margin(joint_factor_g, 'g')}")

    joint_factor_g_d = norm(cpd_product(cpd_d_1, joint_factor_g))

    print(f"joint_factor_g_d = {joint_factor_g_d}")
    print(f"margin on D where g and d = {margin(joint_factor_g_d, 'd')}")
    print(f"margin on I where g and d  = {margin(joint_factor_g_d, 'i')}")
    print(f"margin on G where g and d  = {margin(joint_factor_g_d, 'g')}")


if __name__ == '__main__':
    pgmpy_bayes_net_test()
    manual_bayes_net_test()
