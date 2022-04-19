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

from scripts.examples.building_net_from_coin_toss import build_relation_net, experiment_results, describe_relation_net


if __name__ == '__main__':
    Θ = build_relation_net(experiment_results)
    ω = Θ.sample_builder().add_relation({('V1', 'h1'), ('V2', 'h2')}, "r1").build()
    Θ_ω = Θ.conditional_graph(ω)
    describe_relation_net(Θ_ω.relation_graph())
    Θ_ω.visualize_outcomes()
