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

import logging
from typing import List, Dict, Any, Tuple

from pyvis.network import Network
from .active_value import ActiveValue, ActiveRelation
from .relation_edge import RelationEdge
from .relation_type import RelationType
from .value_node import ValueNode
from .variable_node import VariableNode

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .sample_graph import SampleGraph


class InferenceGraph:

    def __init__(self, query: 'SampleGraph', variables: List[VariableNode], outcomes: List['SampleGraph']):
        self._query = query
        self._variables = variables
        self._outcomes = outcomes
        self._log = logging.getLogger('relationnetlib')

    def __repr__(self):
        return f"InferenceGraph(len(outcomes) = {len( self._outcomes)}, " \
               f"variable ids = {[v.variable_id for v in self._variables]})"

    def show_outcomes(self, height="1024px", width="1024px") -> None:
        net = Network(height=height, width=width)

        for outcome in self._outcomes:
            for v in outcome.get_all_values():
                net.add_node(
                    f"{outcome.sample_id}@{v.value_id}",
                    label=f"{outcome.sample_id}@{v.variable_id}({v.value_id})")

            for e in outcome.all_edges():
                net.add_edge(
                    f"{outcome.sample_id}@{e.node_a.value_id}",
                    f"{outcome.sample_id}@{e.node_b.value_id}",
                    label=e.relation_type.relation_type_id
                )

        net.show(f"Inference_on_{self._query.sample_id}_query.html")

        self._log.debug(f"[InferenceGraph.show_outcomes] len(outcome) = {len(self._outcomes)}")

    def describe(self) -> Dict[str, Any]:
        return {
            "query": self._query,
            "number_variables": len(self._variables),
            "number_outcomes": len(self._outcomes),
            "variable_ids": [v.variable_id for v in self._variables],
        }

    def get_active_values(
            self, relation_filter: List[RelationType] = None,
            limit: int = 100
    ) -> List[ActiveValue]:
        """
        On given inference graph calculate list of active nodes.
        :param relation_filter: list of relation for which activation will be calculated,
                                if None then for all relations.
        :param limit: max number of active values to be returned
        :return List[ActiveValue]: list of calculated active values, sorted on weight:
        """

        in_query_values = {v.get_id(): v for v in self._query.get_all_values()}
        relation_filter_ids = [r.relation_type_id for r in relation_filter] if relation_filter else None
        found_values_per_outcome: Dict[str, Tuple[float, Dict[Tuple[str, str], Tuple[ValueNode, RelationEdge]]]] = {}

        self._log.debug(
            f"[InferenceGraph.get_active_values] in_query_values = {in_query_values}, "
            f"relation_filter_ids = {relation_filter_ids}, limit = {limit}")

        for outcome in self._outcomes:
            checked_value_ids = set(in_query_values.keys())
            found_values: Dict[Tuple[str, str], Tuple[ValueNode, RelationEdge]] = {}
            similarity = outcome.get_similarity(self._query)

            while True:
                one_step_value: Dict[Tuple[str, str], Tuple[ValueNode, RelationEdge]] = {}

                for outcome_val in outcome.get_all_values():
                    if outcome_val.get_id() in checked_value_ids:
                        neighboring_values = outcome.get_neighboring_values(
                            outcome_val.variable_id, outcome_val.value_id, relation_filter_ids)
                        for nv, rel in neighboring_values:
                            if nv.get_id() not in checked_value_ids and nv.get_id() not in one_step_value:
                                one_step_value[nv.get_id()] = (nv, rel)

                if one_step_value:
                    checked_value_ids.update(one_step_value.keys())
                    found_values.update(one_step_value)
                    one_step_value.clear()
                else:
                    break

            self._log.debug(
                f"[InferenceGraph.get_active_values] sample_id = {outcome.sample_id}, "
                f"similarity = {similarity}, found_values = {found_values}")
            found_values_per_outcome[outcome.sample_id] = (similarity, found_values)

        grouped_values: Dict[Tuple[str, str], Tuple[float, Dict[Tuple[str, str, str], int]]] = {}

        for outcome_id, (similarity, found_values) in found_values_per_outcome.items():
            for val_id, (val, rel) in found_values.items():
                other_val = rel.end_node_for_start(val)
                rel_id = (other_val.variable_id, other_val.value_id, rel.relation_type.relation_type_id)
                if val_id in grouped_values:
                    sim_count, rel_acc = grouped_values[val_id]
                    if rel_id in rel_acc:
                        rel_acc[rel_id] += 1
                    else:
                        rel_acc[rel_id] = 1
                    grouped_values[val_id] = (sim_count + similarity, rel_acc)
                else:
                    grouped_values[val_id] = (similarity, {rel_id: 1})

        active_values: List[ActiveValue] = []

        for (variable_id, value_id), (weight, rel_count) in grouped_values.items():
            active_relations = [ActiveRelation(linked_val_id, linked_var_id, rel_type_id, count)
                                for (linked_val_id, linked_var_id, rel_type_id), count in rel_count.items()]
            active_values.append(ActiveValue(variable_id, value_id, weight, active_relations))

        return sorted(active_values, key=lambda x: x.weight, reverse=True)
