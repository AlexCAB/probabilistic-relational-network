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
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Set
from pyvis.network import Network
from scripts.relnet.sample_graph import SampleGraph, ValueNode, RelationEdge, SampleGraphComponentsProvider

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scripts.relnet.relation_graph import RelationGraphBuilder


@dataclass(frozen=True)
class ActiveRelation:
    """
    Immutable data class which represent active relation
    """

    linked_variable: Any
    linked_value: Any
    relation: Any
    count: int


@dataclass(frozen=True)
class ActiveValue:
    """
    Immutable data class which represent active value
    """

    variable: Any
    value: Any
    weight: float
    active_relations: frozenset[ActiveRelation]


class InferenceGraph:
    """
    Immutable wrapper of list of selected outcomes
    """

    def __init__(
            self,
            components_provider: SampleGraphComponentsProvider,
            query: SampleGraph,
            relation_graph_name: str,
            outcomes: Dict[SampleGraph, int]
    ):
        self.query: SampleGraph = query
        self.number_of_outcomes: int = sum([c for _, c in outcomes.items()])
        self._relation_graph_name: str = relation_graph_name
        self._outcomes: Dict[SampleGraph, int] = outcomes
        self._components_provider: SampleGraphComponentsProvider = components_provider

    def __repr__(self):
        return f"inference_of_{self._relation_graph_name}"

    def __copy__(self):
        raise AssertionError(
            "[InferenceGraph.__copy__] Inference graph should not be copied, "
            "use one of transformation method or builder to get new instance")

    def included_variables(self) -> frozenset[Tuple[Any, frozenset[Any]]]:
        """
        Calculate variables and values that appear in this inference graph
        :return: frozenset[(variable, frozenset[value])]:
        """
        variables: Dict[Any, Set[Any]] = {}

        for outcome in self._outcomes.keys():
            for node in outcome.nodes:
                variables[node.variable] = variables.get(node.variable, set({})).union({node.value})

        return frozenset({(var, frozenset(values)) for var, values in variables.items()})

    def included_relations(self) -> frozenset[Any]:
        """
        Calculate relations that appear in this inference graph
        :return: frozenset[relation]
        """
        return frozenset({e.relation for o in self._outcomes.keys()for e in o.edges})

    def outcomes(self) -> frozenset[Tuple[SampleGraph, int]]:
        """
        Return inference graph outcomes in form of frozenset
        :return: frozenset[Tuple[SampleGraph, count]]:
        """
        return frozenset({(o, c) for o, c in self._outcomes.items()})

    def builder(self) -> 'RelationGraphBuilder':
        """
        Construct new relation graph builder which contains all outcomes from this inference graph
        :return: new builder instance
        """
        from scripts.relnet.relation_graph import RelationGraphBuilder
        return RelationGraphBuilder(
            None,
            None,
            None,
            {outcome: count for outcome, count in self._outcomes.items()},
            self._components_provider)

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
            "number_outcomes": self.number_of_outcomes,
            "included_variables": {str(v) for v, _ in self.included_variables()},
            "included_relations": {str(r) for r in self.included_relations()},
        }

    def active_values(self, relation_filter: Set[Any] = None) -> List[ActiveValue]:
        """
        On given inference graph calculate list of active nodes.
        :param relation_filter: list of relation for which activation will be calculated,
                                if None then for all relations.
        :return List[ActiveValue]: list of calculated active values, sorted on weight:
        """
        grouped_values: Dict[ValueNode, Tuple[float, Dict[RelationEdge, int]]] = {}
        active_values: List[ActiveValue] = []

        for outcome, count in self._outcomes.items():
            similarity = outcome.similarity(self.query)
            for val_node, rel_edges in outcome.external_nodes(set(self.query.nodes), relation_filter).items():
                if val_node in grouped_values:
                    sim_acc, edges_count = grouped_values[val_node]
                    sim_acc += (similarity * count)
                    for edge in rel_edges:
                        edges_count[edge] = edges_count.get(edge, 0) + count
                    grouped_values[val_node] = (sim_acc, edges_count)
                else:
                    grouped_values[val_node] = (similarity * count, {e: count for e in rel_edges})

        for value_node, (weight, relation_edges) in grouped_values.items():
            active_relations: Set[ActiveRelation] = set({})
            for rel_edge, num in relation_edges.items():
                opp_value = rel_edge.opposite_endpoint(value_node)
                active_relations.add(ActiveRelation(opp_value.variable, opp_value.value, rel_edge.relation, num))
            active_values.append(
                ActiveValue(value_node.variable, value_node.value, weight, frozenset(active_relations)))

        return sorted(active_values, key=lambda x: x.weight, reverse=True)
