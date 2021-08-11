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
created: 2021-08-09
"""
from typing import List, Dict

from .value_node import ValueNode


class VariableNode:

    def __init__(self, variable_id: str, value_ids: List[str]):
        self.variable_id = variable_id
        self.value_ids = value_ids
        self._values: Dict[str, ValueNode] = {}  # key: value_id

    def add_value(self, node: ValueNode) -> None:
        pass
