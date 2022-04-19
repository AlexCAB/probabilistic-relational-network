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
    Θ_hat = Θ.make_joined()
    describe_relation_net(Θ_hat)
    Θ_hat.visualize_outcomes()
