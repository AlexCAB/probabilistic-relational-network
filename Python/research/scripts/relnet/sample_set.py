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
created: 2021-11-19
"""

from math import isclose
from typing import Dict, Set, Any, Optional, Tuple, Callable, List

from .graph_components import SampleGraphComponentsProvider
from .sample_graph import SampleGraph, SampleGraphBuilder


class Samples:
    """
    Base class of collection of samples with count
    """

    def __init__(
            self,
            components_provider: SampleGraphComponentsProvider,
            samples: Dict[SampleGraph, int]
    ):
        self._components_provider: SampleGraphComponentsProvider = components_provider
        self._samples: Dict[SampleGraph, int] = samples

    def __bool__(self) -> bool:
        return bool(self._samples)

    def items(self) -> Set[Tuple[SampleGraph, int]]:
        """
        Get all sample graphs and them counts as set
        :return: Set[(SampleGraph, count)]
        """
        return {(o, c) for o, c in self._samples.items()}

    def samples(self) -> Set[SampleGraph]:
        """
        Get only sample graphs without count
        :return: set of samples
        """
        return set(self._samples.keys())

    def is_compatible(self, other: 'Samples') -> bool:
        """
        Validate if this samples compatible to other samples
        :param other: other samples to be checked
        :return: True if compatible, False otherwise
        """
        return id(self._components_provider) == id(other._components_provider)


class SampleSet(Samples):
    """
    Represent immutable collection of samples with count
    """

    def __init__(
            self,
            components_provider: SampleGraphComponentsProvider,
            samples: Dict[SampleGraph, int]
    ):
        super(SampleSet, self).__init__(components_provider, samples.copy())
        self.length: int = sum(self._samples.values())
        self._hash = hash(tuple(sorted([(hash(o), hash(c)) for o, c in samples.items()])))

    def __len__(self) -> int:
        return self.length

    def __eq__(self, other: Any):
        if isinstance(other, SampleSet):
            return self._samples == other._samples
        return False

    def __hash__(self):
        return self._hash

    def __repr__(self):
        return "{\n" + '\n'.join(sorted([f"    {o}: {c}" for o, c in self._samples.items()])) + "\n}"

    def builder(self) -> 'SampleSetBuilder':
        """
        Create SampleSetBuilder with all samples that in this sample set
        :return: SampleSetBuilder with all samples
        """
        return SampleSetBuilder(self._components_provider, self._samples)

    def union(self, other: 'SampleSet') -> 'SampleSet':
        """
        Join all samples and the counts from this and other sample set and return as new one
        :param other: sample set to be joined
        :return: new sample set with all samples from this and other sample set
        """
        assert self.is_compatible(other), \
            f"[SampleSet.union] Incompatible sample sets can't be joined, " \
            f"{self} incompatible to {other}"

        builder = self.builder()
        for s, c in other.items():
            builder.add(s, c)
        return builder.build()

    def filter_samples(self, p: Callable[[SampleGraph], bool]) -> 'SampleSet':
        """
        To filter samples with predicate
        :param p: predicate to filter one
        :return: new sample set without filtered out samples
        """
        return SampleSet(self._components_provider, {s: c for s, c in self._samples.items() if p(s)})

    def group_intersecting(self) -> Dict[frozenset[Any], 'SampleSet']:
        """
        To group samples so each group contain sample that
        intersect (i.e. have at least one edge with same endpoint variables)
        Singe node samples go to separate group.
        :return: Dict[included_variables, sample_set_of_intersected]
        """
        sample_acc: Dict[frozenset[frozenset[Any]], Dict[SampleGraph, int]] = {}

        for sample, count in self._samples.items():
            if sample.edges:
                key = sample.edges_endpoint_variables()
            else:
                key = frozenset(sample.included_variables)  # Singe node graph
            if key in sample_acc:
                sample_acc[key][sample] = count
            else:
                sample_acc[key] = {sample: count}

        def group():
            for k_a in sample_acc.keys():
                for k_b in sample_acc.keys():
                    if k_a != k_b and not k_a.isdisjoint(k_b):
                        sample_acc[k_a | k_b] = sample_acc.pop(k_a) | sample_acc.pop(k_b)
                        group()
                        return
        group()
        grouped = {
            frozenset({v for vs in key for v in vs}): SampleSet(self._components_provider, samples)
            for key, samples in sample_acc.items()}

        assert len(grouped) == len(sample_acc), \
            f"[SampleSet.group_intersecting] Expect each group to have unique list of variables, look like bug, " \
            f"grouped = {grouped}, sample_acc = {sample_acc}"

        return grouped

    def can_join_samples(self) -> bool:
        """
        Will join all contained samples to get new one which include all nodes and edges.
        In case there is conflicting (same endpoint but different relation) AssertionError will be raise.
        In case result sample graph will not connected AssertionError will be raise.
        :return: (new_sample, list_of_counts)
        """
        for var in frozenset.intersection(*[s.included_variables for s in self.samples()]):
            if len({s.value_for_variable(var) for s in self.samples()}) > 1:
                return False
        return True

    def make_joined_sample(self) -> Tuple[SampleGraph, List[int]]:
        """
        Will join all contained samples to get new one which include all nodes and edges.
        In case there is conflicting (same endpoint but different relation) AssertionError will be raise.
        In case result sample graph will not connected AssertionError will be raise.
        :return: (new_sample, list_of_counts)
        """
        sgb = SampleGraphBuilder(self._components_provider)
        for s in self._samples.keys():
            sgb.join_sample(s)
        return sgb.build(), list(self._samples.values())

    def is_all_values_match(self) -> bool:
        """
        Check for all samples if there exist sample which contain different value for the same variable .
        For empty sample set return True
        :return: True if all values match or empty set, False otherwise
        """
        var_acc: Dict[Any, Any] = {}

        for sample in self._samples.keys():
            for node in sample.nodes:
                if node.variable in var_acc:
                    if var_acc[node.variable] != node.value:
                        return False
                else:
                    var_acc[node.variable] = node.value
        return True

    def probabilities(self) -> Set[Tuple[SampleGraph, float]]:
        """
        Calculate and return probabilities of the samples (sum to 1)
        :return: Set[(SampleGraph, probability)]
        """
        props = {(o, c / self.length) for o, c in self._samples.items()}
        p_sum = sum([p for _, p in props])
        assert \
            isclose(p_sum, 1.0, rel_tol=1e-9, abs_tol=0.0), \
            f"[SampleSet.probabilities] Expect all sample props to sum to 1 but got {p_sum}"
        return props

    def have_value(self, variable: Any, value: Any) -> bool:
        """
         Check if given value are in this sample set
        :param variable: variable which have value
        :param value: value to be checked
        :return: True if value in this sample set, False otherwise
        """
        for o in self._samples.keys():
            if o.have_value(variable, value):
                return True
        return False

    def have_variable(self, variable: Any) -> bool:
        """
        Check if given variable is in this sample set
        :param variable: variable to be checked
        :return: True if variable in this sample set, False otherwise
        """
        for o in self._samples.keys():
            if o.have_variable(variable):
                return True
        return False


class SampleSetBuilder(Samples):
    """
    Mutable builder of collection of samples with count
    """

    @staticmethod
    def join_sample_set(sample_sets: List[SampleSet]) -> SampleSet:
        """
        Will join multiple given sample sets in one
        :param sample_sets: smple sets to be joined
        :return: joined sample set
        """
        if len(sample_sets) > 1:
            return sample_sets[0].union(SampleSetBuilder.join_sample_set(sample_sets[1:]))
        else:
            assert sample_sets, \
                "[SampleSetBuilder.join_sample_set] Input sample_sets should not be empty"
            return sample_sets[0]

    def __init__(
            self,
            components_provider: SampleGraphComponentsProvider,
            samples: Optional[Dict[SampleGraph, int]] = None
    ):
        super(SampleSetBuilder, self).__init__(components_provider, samples.copy() if samples else {})

    def __repr__(self):
        return f"SampleSetBuilder(length = {self.length()})"

    def copy(self):
        """
        To copy this SampleSetBuilder
        :return: new sample set builder
        """
        return SampleSetBuilder(self._components_provider, self._samples)

    def add(self, sample: SampleGraph, count: int) -> 'SampleSetBuilder':
        """
        Add sample to this sample set, if already added then just to sum counts
        :param sample: sample graph
        :param count: count of samples
        :return: self
        """

        assert sample.is_compatible(self._components_provider), \
            f"[SampleSetBuilder.add] Sample {sample} is incompatible with this sample set"

        if sample in self._samples:
            self._samples[sample] += count
        else:
            self._samples[sample] = count
        return self

    def add_all(self, samples: Samples) -> 'SampleSetBuilder':
        """
        To add all samples from given sample set
        :param samples: sample set to be added
        :return: self
        """
        for s, c in samples.items():
            self.add(s, c)
        return self

    def remove(self, sample: SampleGraph) -> Tuple[SampleGraph, int]:
        """
        Remove given sample from this builder
        :param sample: SampleGraph to be removed
        :return: removed (sample, count)
        """
        assert sample in self._samples, \
            f"[SampleSetBuilder.remove] Sample {sample} not in this sample set"

        return sample, self._samples.pop(sample)

    def remove_all(self, samples: Samples) -> 'SampleSetBuilder':
        """
        Remove all samples from given sample set
        :param samples: sample set to be removed
        :return: self
        """
        for sample in samples.samples():
            self.remove(sample)
        return self

    def length(self) -> int:
        """
        To count number of added samples
        :return: number of added samples
        """
        return sum(self._samples.values())

    def empty(self) -> 'SampleSet':
        """
        To build empty immutable sample set
        :return: sample set
        """
        return SampleSet(self._components_provider, {})

    def build(self) -> 'SampleSet':
        """
        To build immutable sample set
        :return: sample set
        """
        return SampleSet(self._components_provider, self._samples)
