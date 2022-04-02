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
created: 2021-10-29
"""

from scripts.relnet.relation_graph import RelationGraphBuilder


def main() -> None:
    b_1 = RelationGraphBuilder({"a": {"1", "2"}, "b": {"2", "3"}, "c": {"3", "4"}, "d": {"4", "5"}}, {"r"}) \
        .build_sample(lambda b: b
                      .build_single_node("a", "1")) \
        .build_sample(lambda b: b
                      .add_relation({("a", "1"), ("b", "2")}, "r")
                      .build()) \
        .build_sample(lambda b: b
                      .add_relation({("a", "1"), ("b", "2")}, "r")
                      .add_relation({("b", "2"), ("c", "3")}, "r")
                      .build()) \
        .build_sample(lambda b: b
                      .add_relation({("a", "1"), ("b", "2")}, "r")
                      .add_relation({("b", "2"), ("c", "3")}, "r")
                      .add_relation({("c", "3"), ("d", "4")}, "r")
                      .build()) \
        .build_sample(lambda b: b
                      .add_relation({("a", "1"), ("b", "2")}, "r")
                      .add_relation({("b", "2"), ("c", "3")}, "r")
                      .add_relation({("c", "3"), ("d", "5")}, "r")
                      .build())
    rg_1 = b_1.build()
    q_1 = b_1.sample_builder().add_relation({("a", "1"), ("b", "2")}, "r").build()
    ig_1 = rg_1.conditional_graph(q_1, "visualization_test_conditional_graph_activation")

    print(f"rg_1 = {rg_1.describe()}")
    print(f"ig_1 = {ig_1.describe()}")

    ig_1.activation_graph().visualize()


if __name__ == '__main__':
    main()
