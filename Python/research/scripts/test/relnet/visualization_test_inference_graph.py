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
    b_1 = RelationGraphBuilder({"a": {"1", "2"}, "b": {"2", "3"}, "c": {"3", "4"}}, {"r", "s"})\
        .generate_all_possible_outcomes()
    rg_1 = b_1.build()
    q_1 = b_1.sample_builder().add_relation({("a", "1"), ("b", "2")}, "r").build()
    ig_1 = rg_1.inference(q_1, "visualization_test_inference_graph")

    print(f"rg_1 = {rg_1.describe()}")
    print(f"ig_1 = {ig_1.describe()}")

    ig_1.visualize()


if __name__ == '__main__':
    main()
