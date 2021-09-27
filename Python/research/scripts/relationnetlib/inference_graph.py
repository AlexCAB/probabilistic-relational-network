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
from typing import List, Dict, Any

from pyvis.network import Network
from .active_value import ActiveValue
from .relation_type import RelationType
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
        pass
