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
created: 2021-10-11
tutorial: https://pgmpy.org/models/markovnetwork.html
"""

from pgmpy.models import MarkovNetwork
from pgmpy.factors.discrete import DiscreteFactor


def pgmpy_markov_net_test() -> None:

    G = MarkovNetwork()

    G.add_node('A')
    G.add_node('B')
    G.add_node('C')
    G.add_node('D')

    G.add_edge('A', 'B')
    G.add_edge('B', 'C')
    G.add_edge('C', 'D')
    G.add_edge('D', 'A')

    ab_factor = DiscreteFactor(['A', 'B'], cardinality=[2, 2], values=[30, 5, 1, 10])
    bc_factor = DiscreteFactor(['B', 'C'], cardinality=[2, 2], values=[100, 1, 1, 100])
    cd_factor = DiscreteFactor(['C', 'D'], cardinality=[2, 2], values=[1, 100, 100, 1])
    da_factor = DiscreteFactor(['D', 'A'], cardinality=[2, 2], values=[100, 1, 1, 100])

    G.add_factors(ab_factor)
    G.add_factors(bc_factor)
    G.add_factors(cd_factor)
    G.add_factors(da_factor)

    print(ab_factor)
    print(bc_factor)
    print(cd_factor)
    print(da_factor)

    product = ab_factor * bc_factor * cd_factor * da_factor

    print(product)

    product.normalize()

    print(product)

    m_a = product.marginalize(['B', 'C', 'D'], inplace=False)

    print(m_a)


if __name__ == '__main__':
    pgmpy_markov_net_test()
