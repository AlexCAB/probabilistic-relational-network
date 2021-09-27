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

from typing import List, Dict, Union

from .relation_edge import RelationEdge
from .value_node import ValueNode

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .relation_graph import RelationGraph
    from .inference_graph import InferenceGraph


class VariableNode:

    def __init__(self, variable_id: str, value_ids: List[str]):
        assert variable_id, f"[VariableNode.__init__] variable_id should not be empty string"
        assert value_ids, f"[VariableNode.__init__] value_ids should not be empty list"
        assert len(set(value_ids)) == len(value_ids), \
            f"[VariableNode.__init__] value_ids be list of unique ids"
        assert "unobserved" not in value_ids, \
            f"[VariableNode.__init__] 'unobserved' is invalid name for value, " \
            f"in variable_id = {variable_id}"
        self.variable_id = variable_id
        self.value_ids = value_ids
        self._values: Dict[(str, str), ValueNode] = {}  # key: (outcome_id, value_id)
        self._relation_graph: Union['RelationGraph', 'InferenceGraph', None] = None

    def __repr__(self):
        return f"VariableNode(variable_id = {self.variable_id}, value_ids = {self.value_ids})"

    def set_relation_graph(self, relation_graph: Union['RelationGraph', 'InferenceGraph']) -> None:
        assert not self._relation_graph, \
            "[VariableNode.set_relation_graph] Variable node can't be added to relation graph twice"
        self._relation_graph = relation_graph

    def add_value(self, outcome_id: str, node: ValueNode) -> None:
        self._values[(outcome_id, node.value_id)] = node

    def get_all_relation_between(self, variable_id: str) -> List[RelationEdge]:
        relations = []
        for v in self._values.values():
            for r in v.relations:
                if r.node_a.variable_id == self.variable_id and r.node_b.variable_id == variable_id:
                    relations.append(r)
                if r.node_b.variable_id == self.variable_id and r.node_a.variable_id == variable_id:
                    relations.append(r)
        return relations

    def clean_copy(self) -> 'VariableNode':
        return VariableNode(self.variable_id, self.value_ids)

    def marginal_distribution(self) -> Dict[str, float]:
        """
        For each value of this variable count number of outcome where value enters,
        then count outcomes where no one of values of this variable enters (unobserved),
        then normalize all counts ant return.
        :return: Dict[value_id, normalized marginal probability]
        """
        
        assert self._relation_graph, \
            "[VariableNode.marginal_distribution] Variable node should be added to relation graph"
        outcomes = self._relation_graph.get_outcomes()

        if not outcomes:
            return {}

        count = {v: 0 for v in self.value_ids}
        for o in outcomes:
            if o.have_variable_value(self.variable_id):
                vid = o.get_value_id_for_variable(self.variable_id)
                assert vid in count, \
                    f"[VariableNode.marginal_distribution] Found unknown value Id '{vid}', " \
                    f"where available: {self.value_ids} in variable_id = {self.variable_id}"
                count[vid] += 1

        n_outcomes = len(outcomes)

        assert n_outcomes > 0, \
            f"[VariableNode.marginal_distribution] n_outcomes <= 0 (n_outcomes = {n_outcomes}), which look like bug."

        n_unobserved = n_outcomes - sum([val_count for val_count in count.values()])

        assert (n_unobserved >= 0) and (n_unobserved <= n_outcomes), \
            f"[VariableNode.marginal_distribution] n_unobserved > n_outcomes or n_unobserved < 0 " \
            f"(n_outcomes = {n_outcomes}, n_unobserved = {n_unobserved}), which look like bug."
        assert "unobserved" not in count.keys(), \
            f"[VariableNode.marginal_distribution] 'unobserved' is invalid name for value, " \
            f"in variable_id = {self.variable_id}"

        count['unobserved'] = n_unobserved
        normalized = {vid: c / n_outcomes for vid, c in count.items()}

        assert sum([c for c in normalized.values()]) == 1,  \
            f"[VariableNode.marginal_distribution] Normalized probabilities not sum to 1, " \
            f"n_outcomes = {n_outcomes}, count = {count}"

        return normalized
