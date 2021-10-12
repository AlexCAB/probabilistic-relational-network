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

import logging
from pgmpy.factors.discrete import DiscreteFactor
from pgmpy.models import MarkovNetwork
from scripts.relationnetlib.relation_graph import RelationGraph
from scripts.relationnetlib.relation_type import RelationType
from scripts.relationnetlib.variable_node import VariableNode


log = logging.getLogger('comparing_with_markov_network')

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
        log.info(f"[make_markov_network] factor: \n {f}")
    return g


def make_relation_graph() -> RelationGraph:
    r = RelationType("R")
    t = RelationGraph("T", [r], [VariableNode(n, [f"{n}(0)", f"{n}(1)"]) for n in nodes])
    for edge, values in edges:
        for sid, tid, i in [(0, 0, 0), (0, 1, 1), (1, 0, 2), (1, 1, 3)]:
            sn = f"{edge[0]}({sid})"
            tn = f"{edge[1]}({tid})"
            for v in range(1, values[i] + 1):
                sg = t.new_sample_graph(f"{sn}-{tn}_{v}")
                sg.add_relation({sg.add_value_node(edge[0], sn), sg.add_value_node(edge[1], tn)}, r)
                t.add_outcomes([sg])
    log.info(f"[make_relation_graph] relation graph: \n {t.describe()}")
    return t


def comparing_variable_margin_probability(markov_net: MarkovNetwork, rel_graph: RelationGraph) -> None:
    ab_factor = markov_net.factors[0]
    bc_factor = markov_net.factors[1]
    cd_factor = markov_net.factors[2]
    da_factor = markov_net.factors[3]

    product = ab_factor * bc_factor * cd_factor * da_factor
    product.normalize()

    log.info(f"[comparing_variable_margin_probability] joint markov probability: \n {product}")

    m_a = product.marginalize(['B', 'C', 'D'], inplace=False)
    m_b = product.marginalize(['A', 'C', 'D'], inplace=False)
    m_c = product.marginalize(['A', 'B', 'D'], inplace=False)
    m_d = product.marginalize(['A', 'B', 'C'], inplace=False)

    log.info(f"[comparing_variable_margin_probability] margin markov probability: \n {m_a} \n {m_b} \n {m_c} \n {m_d}")

    for nid in nodes:
        md = rel_graph.get_variable(nid).marginal_distribution()
        vmd = rel_graph.get_variable(nid).values_marginal_distribution()
        log.info(
            f"[comparing_variable_margin_probability] rel net  node '{nid}' margin probability:\n  {md},\n  {vmd}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    mn = make_markov_network()
    rg = make_relation_graph()
    comparing_variable_margin_probability(mn, rg)
