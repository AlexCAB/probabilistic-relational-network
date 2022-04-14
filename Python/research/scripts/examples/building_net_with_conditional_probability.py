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
created: 2022-04-14
"""

from math import isclose
from typing import Any, Dict, Tuple, List

from scripts.relnet.graph_components import DirectedRelation
from scripts.relnet.conditional_graph import ConditionalGraph
from scripts.relnet.relation_graph import RelationGraph, RelationGraphBuilder

from pgmpy.inference import VariableElimination
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD, DiscreteFactor

from scripts.relnet.sample_graph import SampleGraph
from itertools import product



if __name__ == '__main__':
    pass
