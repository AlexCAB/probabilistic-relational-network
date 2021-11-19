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

from typing import Dict, Set, Any, Optional, Tuple, Callable

from .sample_graph import SampleGraph


class Samples:
    """
    Base class of collection of samples with count
    """

    def __init__(
            self,
            samples: Dict[SampleGraph, int]
    ):
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


class SampleSet(Samples):
    """
    Represent immutable collection of samples with count
    """

    def __init__(
            self,
            samples: Dict[SampleGraph, int]
    ):
        super(SampleSet, self).__init__(samples)
        self._samples: Dict[SampleGraph, int] = samples
        self.length: int = sum(samples.values())

    def __len__(self) -> int:
        return self.length

    def __eq__(self, other: Any):
        if isinstance(other, SampleSet):
            return self._samples == other._samples
        return False

    def __repr__(self):
        return "{\n" + '\n'.join(sorted([f"    {o}: {c}" for o, c in self._samples.items()])) + "\n}"

    def builder(self) -> 'SampleSetBuilder':
        """
        Create SampleSetBuilder with all samples that in this sample set
        :return: SampleSetBuilder with all samples
        """
        return SampleSetBuilder({o: c for o, c in self._samples.items()})

    def union(self, other: 'SampleSet'):
        """
        Join all samples and the counts from this and other sample set and return as new one
        :param other: sample set to be joined
        :return: new sample set with all samples from this and other sample set
        """
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
        return SampleSet({s: c for s, c in self._samples.items() if p(s)})

    def group_intersecting(self) -> Dict[frozenset[Any], 'SampleSet']:
        """
        To group samples so each group contain sample that
        intersect (i.e. have at least one edge with same endpoint variables)
        :return: Dict[included_variables, sample_set_of_intersected]
        """
        pass


class SampleSetBuilder(Samples):
    """
    Mutable builder of collection of samples with count
    """

    def __init__(
            self,
            samples: Optional[Dict[SampleGraph, int]] = None
    ):
        super(SampleSetBuilder, self).__init__(samples if samples else {})

    def __repr__(self):
        return f"SampleSetBuilder(length = {self.length()})"

    def add(self, sample: SampleGraph, count: int) -> 'SampleSetBuilder':
        """
        Add sample to this sample set, if already added then just to sum counts
        :param sample: sample graph
        :param count: count of samples
        :return: self
        """
        if sample in self._samples:
            self._samples[sample] += count
        else:
            self._samples[sample] = count
        return self

    def length(self) -> int:
        """
        To count number of added samples
        :return: number of added samples
        """
        return sum(self._samples.values())

    def build(self) -> 'SampleSet':
        """
        To build immutable sample set
        :return: sample set
        """
        return SampleSet(self._samples)