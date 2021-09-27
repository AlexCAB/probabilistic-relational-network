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
created: 2021-09-24
"""

from typing import List


class ActiveRelation:

    def __init__(self, linked_value_id: str, linked_variable_id: str, relation_type_id: str, count: int):
        self.linked_value_id = linked_value_id
        self.linked_variable_id = linked_variable_id
        self.relation_type_id = relation_type_id
        self.count = count

    def __repr__(self):
        return f"ActiveRelation(" \
               f"linked_value_id = {self.linked_value_id}, " \
               f"linked_variable_id = {self.linked_variable_id}, " \
               f"relation_type_id = {self.relation_type_id}, " \
               f"count = {self.count})"


class ActiveValue:

    def __init__(self, value_id: str, variable_id: str, weight: float, active_relations: List[ActiveRelation]):
        self.value_id = value_id
        self.variable_id = variable_id
        self.weight = weight
        self.active_relations = active_relations

    def __repr__(self):
        return f"ActiveValue(" \
               f"value_id = {self.value_id}, " \
               f"variable_id = {self.variable_id}, " \
               f"weight = {self.weight}, " \
               f"active_relations = {self.active_relations})"
