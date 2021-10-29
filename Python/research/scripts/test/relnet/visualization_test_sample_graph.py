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

from scripts.relnet.sample_graph import SampleGraphBuilder
from scripts.test.relnet.test_sample_graph import MockSampleGraphComponentsProvider


def main() -> None:
    bcp = MockSampleGraphComponentsProvider({"a": {"1", "2"}, "b": {"2", "3"}, "c": {"3", "4"}}, {"r", "s"})

    s_1 = SampleGraphBuilder(bcp) \
        .add_relation({("a", "1"), ("b", "2")}, "r") \
        .add_relation({("b", "2"), ("c", "3")}, "s") \
        .add_relation({("c", "3"), ("a", "1")}, "r") \
        .build()

    s_1.visualize()


if __name__ == '__main__':
    main()
