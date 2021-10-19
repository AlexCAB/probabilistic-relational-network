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
created: 2021-10-19
"""

from scripts.relnet.sample_graph import SampleGraph, ValueNode, RelationEdge


def show_sample_graph():
    a_1 = ValueNode("a", "1")
    b_1 = ValueNode("b", "1")
    c_1 = ValueNode("c", "1")
    e_1 = RelationEdge(frozenset({a_1, b_1}), "r")
    e_2 = RelationEdge(frozenset({b_1, c_1}), "r")
    s_1 = SampleGraph(frozenset({a_1, b_1, c_1}), frozenset({e_1, e_2}), "sample_1")
    s_1.show()


if __name__ == '__main__':
    show_sample_graph()
