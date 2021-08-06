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
created: 2021-07-23
"""

from pyvis.network import Network


def make_all_sub_graphs(n: int) -> Network:

    # Make all node IDs

    node_ids = list(range(1, n + 1))

    print(f"node_ids = {node_ids}")

    # Make all edges IDs

    edges = []
    for n1 in node_ids:
        for n2 in node_ids:
            if n1 != n2 and (n2, n1) not in edges:
                edges.append((n1, n2))

    print(f"len(edges) = {len(edges)}, edges = {edges}")

    assert len(set(edges)) == len(edges), \
        f"expect edges_types to be unique ({len(set(edges))} != {len(edges)})"

    types = ["AB", "BA"]

    # Generate indices for building of sub-playaround

    index_acc = [-1 for _ in range(0, len(edges))]
    indices = []

    while set([i < (len(types) - 1) for i in index_acc]) != {False}:
        i = 0
        while index_acc[i] >= (len(types) - 1) and i < len(edges):
            index_acc[i] = -1
            i += 1
        index_acc[i] += 1
        indices.append(index_acc.copy())

    # print(f"indices = {indices}")
    print(f"len(indices) = {len(indices)}")

    counted_size = ((len(types) + 1) ** ((n * (n - 1)) / 2)) + n - 1

    print(f"counted_size = {counted_size}")

    assert len(set([tuple(i) for i in indices])) == len(indices), \
        f"expect indices to be unique ({len(set(indices))} != {len(indices)})"

    # Build sub-graphs

    net = Network()

    for nid in node_ids:
        net.add_node(f"N{nid}_0")

    for i in range(1, len(indices) + 1):

        index = indices[i - 1]

        nodes = []
        for j in range(0, len(index)):
            if index[j] >= 0:
                nodes.extend(edges[j])
        nodes = list(set(nodes))

        for nid in nodes:
            net.add_node(f"N{nid}_{i}")

        for j in range(0, len(index)):
            if index[j] >= 0:
                t = types[index[j]]
                sid, tid = edges[j]
                net.add_edge(f"N{sid}_{i}", f"N{tid}_{i}", title=t)

    return net


def main():
    net = make_all_sub_graphs(3)
    net.show_buttons(filter_=['physics'])
    net.show("number_of_subgraphs.html")


if __name__ == '__main__':
    main()
