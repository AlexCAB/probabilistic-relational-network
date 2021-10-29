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
    rg_1 = RelationGraphBuilder({"a": {"1", "2"}, "b": {"2", "3"}, "c": {"3", "4"}}, {"r", "s"})\
        .set_name("visualization_test_relation_graph")\
        .generate_all_possible_outcomes()\
        .build()

    print(str(rg_1.describe()))

    rg_1.visualize()


if __name__ == '__main__':
    main()
