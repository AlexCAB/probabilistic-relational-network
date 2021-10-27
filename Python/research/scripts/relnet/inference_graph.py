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

from typing import List, Dict, Any, Tuple
from pyvis.network import Network
from scripts.relnet.sample_graph import SampleGraph, ValueNode, RelationEdge, SampleGraphComponentsProvider


class ActiveRelation:
    """
    Immutable data class which represent active relation
    """

    def __init__(self, linked_variable: Any, linked_value: Any, relation: Any, count: int):
        self.linked_variable = linked_variable
        self.linked_value = linked_value
        self.relation = relation
        self.count = count

    def __repr__(self):
        return f"ActiveRelation(" \
               f"linked_variable = {self.linked_variable}, " \
               f"linked_value = {self.linked_value}, " \
               f"relation = {self.relation}, " \
               f"count = {self.count})"


class ActiveValue:
    """
    Immutable data class which represent active value
    """

    def __init__(self, variable: Any, value: Any, weight: float, active_relations: List[ActiveRelation]):
        self.variable = variable
        self.value = value
        self.weight = weight
        self.active_relations = active_relations

    def __repr__(self):
        return f"ActiveValue(" \
               f"variable = {self.variable}, " \
               f"value = {self.value}, " \
               f"weight = {self.weight}, " \
               f"active_relations = {self.active_relations})"


class InferenceGraph:
    """
    Immutable wrapper of list of selected outcomes
    """

    def __init__(
            self,
            components_provider: SampleGraphComponentsProvider,
            query: SampleGraph,
            variables: frozenset[Tuple[Any, frozenset[Any]]],
            relation_graph_name: str,
            outcomes: Dict[SampleGraph, int]):
        self.query: SampleGraph = query
        self.number_of_outcomes: int = sum([c for _, c in outcomes.items()])
        self._variables: frozenset[Tuple[Any, frozenset[Any]]] = variables
        self._relation_graph_name: str = relation_graph_name
        self._outcomes: Dict[SampleGraph, int] = outcomes
        self._components_provider: SampleGraphComponentsProvider = components_provider

    def __repr__(self):
        return f"inference_of_{self._relation_graph_name}"

    def outcomes(self) -> frozenset[Tuple[SampleGraph, int]]:
        """
        Return inference graph outcomes in form of frozenset
        :return: frozenset[Tuple[SampleGraph, count]]:
        """
        return frozenset({(o, c) for o, c in self._outcomes.items()})

    def visualize_inference_graph(self,  height="1024px", width="1024px") -> None:
        """
        Will render this inference graph as HTML page and show in browser
        :param height: window height
        :param width: window width
        :return: None
        """
        pass

    def visualize_outcomes(self, height="1024px", width="1024px") -> None:
        """
        Will render all outcomes as HTML page and show in browser
        :param height: window height
        :param width: window width
        :return: None
        """
        net = Network(height=height, width=width)

        for outcome, count in self._outcomes.items():
            for node in outcome.nodes:
                net.add_node(node.string_id, label=f"{node.string_id}@{outcome.name}({count})")
            for edge in outcome.edges:
                ep = list(edge.endpoints)
                net.add_edge(ep[0].string_id, ep[1].string_id, label=str(edge.relation))

        net.show(f"{str(self)}.html")

    def visualize_activation(self, height="1024px", width="1024px") -> None:
        """
        Will calculate active values and render inference graph with it as HTML page and show in browser
        :param height: window height
        :param width: window width
        :return: None
        """
        pass

    def describe(self) -> Dict[str, Any]:
        """
        Return set of properties of this inference graph
        :return: Dict[property_name, property_value]
        """
        return {
            "query": self.query.text_view(),
            "number_variables": len(self._variables),
            "number_outcomes": self.number_of_outcomes,
            "variables": {str(v) for v, _ in self._variables},
        }

    def active_values(self, relation_filter: List[Any] = None) -> List[ActiveValue]:
        """
        On given inference graph calculate list of active nodes.
        :param relation_filter: list of relation for which activation will be calculated,
                                if None then for all relations.
        :return List[ActiveValue]: list of calculated active values, sorted on weight:
        """

        found_values_per_outcome: Dict[(SampleGraph, int), Tuple[float, Dict[ValueNode, List[RelationEdge]]]] = {}

        for outcome, count in self._outcomes.items():
            checked_values = set(self.query.nodes)
            found_values: Dict[ValueNode, List[RelationEdge]] = {}
            similarity = outcome.similarity(self.query)

            while True:
                one_step_values: Dict[ValueNode, List[RelationEdge]] = {}
                for value_node in outcome.nodes:
                    if value_node in checked_values:
                        neighboring_nodes = outcome.neighboring_values(value_node, relation_filter)
                        for neighboring_node, relation_edge in neighboring_nodes.items():
                            if neighboring_node not in checked_values:
                                if neighboring_node in one_step_values:
                                    one_step_values[neighboring_node].append(relation_edge)
                                else:
                                    one_step_values[neighboring_node] = [relation_edge]

                if one_step_values:
                    checked_values.update(one_step_values.keys())
                    for val_node, rel_edges in one_step_values.items():
                        if val_node in found_values:
                            found_values[val_node].extend(rel_edges)
                        else:
                            found_values[val_node] = rel_edges
                    checked_values.clear()
                else:
                    break

            found_values_per_outcome[(outcome, count)] = (similarity, found_values)

        grouped_values: Dict[ValueNode, Tuple[float, Dict[RelationEdge, int]]] = {}

        for (outcome, count), (similarity, found_values) in found_values_per_outcome.items():
            for value_node, rel_edges in found_values.items():

                relation_acc: Dict[RelationEdge, int] = {}
                for edge in rel_edges:
                    if edge in relation_acc:
                        relation_acc[edge] += 1
                    else:
                        relation_acc[edge] = 1

                relation_with_count: Dict[RelationEdge, int] = {re: num * count for re, num in relation_acc.items()}

                if value_node in grouped_values:

                    weight, relation_edges = grouped_values[value_node]
                    weight += (similarity * count)

                    for rel, c in relation_with_count.items():
                        if rel in relation_edges:
                            relation_edges[rel] += c
                        else:
                            relation_edges[rel] = c

                    grouped_values[value_node] = (weight, relation_edges)

                else:
                    grouped_values[value_node] = (similarity * count, relation_with_count)

        active_values: List[ActiveValue] = []

        for value_node, (weight, relation_edges) in grouped_values.items():

            active_relations: List[ActiveRelation] = []
            for rel_edge, c in relation_edges.items():
                opp_value = rel_edge.opposite_endpoint(value_node)

                assert opp_value, \
                    f"[InferenceGraph.active_values] Expect to find opposite value for node {value_node} " \
                    f"in edge {rel_edge}, look like bug"

                active_relations.append(ActiveRelation(opp_value.variable, opp_value.value, rel_edge.relation, c))

            active_values.append(ActiveValue(value_node.variable, value_node.value, weight, active_relations))

        return sorted(active_values, key=lambda x: x.weight, reverse=True)
