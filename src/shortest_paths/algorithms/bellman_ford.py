"""Bellman-Ford single-source shortest paths solver with negative cycle detection.

This module implements the Bellman-Ford algorithm operating on a Graph instance,
with full negative cycle reachability detection, propagation of -inf distances,
and closed-walk witness extraction.
"""

from __future__ import annotations

import math
from collections import deque
from typing import Any, Optional

from shortest_paths.graph import Graph
from shortest_paths.models import SSSPResult, Status, VertexResult


def bellman_ford(
    graph: Graph,
    source: Any,
) -> SSSPResult:
    """Run Bellman-Ford on a Graph, returning an SSSPResult.

    The n-th pass is a real relaxation pass: every still-relaxable edge is
    relaxed and the updated vertices are collected as the seed set S. A BFS
    from S over out-edges marks every reachable vertex as NEG_INFINITE.

    Invariant:
    After pass i (1-indexed), dist[v] is the weight of the shortest path
    from source to v using at most i edges, for every vertex v.
    """
    inf = math.inf

    src_idx = graph.validate_source(source)
    n = graph.n
    edges = graph.index_edges

    dist: list = [inf] * n
    pred: list = [None] * n
    dist[src_idx] = 0

    total_relaxations = 0
    passes = 0

    # --- n-1 relaxation passes ---
    for _ in range(n - 1):
        changed = False
        passes += 1
        for u, v, w in edges:
            if dist[u] == inf:
                continue
            new_dist = dist[u] + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                pred[v] = u
                changed = True
                total_relaxations += 1
        if not changed:
            break

    # --- n-th pass: real relaxation + collect seed set S ---
    seed: set[int] = set()
    for u, v, w in edges:
        if dist[u] == inf:
            continue
        new_dist = dist[u] + w
        if new_dist < dist[v]:
            dist[v] = new_dist
            pred[v] = u
            seed.add(v)
            total_relaxations += 1

    # --- BFS from S to mark all NEG_INFINITE vertices ---
    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v, _w in edges:
        adj[u].append(v)

    neg_inf_set: set[int] = set()
    queue: deque[int] = deque(seed)
    neg_inf_set.update(seed)
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if v not in neg_inf_set:
                neg_inf_set.add(v)
                queue.append(v)

    # --- Witness cycle extraction ---
    negative_cycle: Optional[list[Any]] = None
    if seed:
        x = next(iter(seed))
        for _ in range(n):
            if pred[x] is not None:
                x = pred[x]

        cycle_rev = [x]
        curr = pred[x]
        while curr is not None and curr != x:
            cycle_rev.append(curr)
            curr = pred[curr]
        cycle_forward = list(reversed(cycle_rev))
        cycle_forward.append(cycle_forward[0])
        negative_cycle = [graph.label(idx) for idx in cycle_forward]

    # --- Build SSSPResult ---
    vertices_result: dict[Any, VertexResult] = {}
    for idx in range(n):
        label = graph.label(idx)
        if idx in neg_inf_set:
            vertices_result[label] = VertexResult(
                status=Status.NEG_INFINITE, distance=None, path=None,
            )
        elif dist[idx] == inf:
            vertices_result[label] = VertexResult(
                status=Status.UNREACHABLE, distance=None, path=None,
            )
        else:
            path_rev = [idx]
            curr = pred[idx]
            while curr is not None:
                path_rev.append(curr)
                curr = pred[curr]
            path_labels = [graph.label(i) for i in reversed(path_rev)]
            vertices_result[label] = VertexResult(
                status=Status.FINITE, distance=dist[idx], path=path_labels,
            )

    return SSSPResult(
        algorithm="bellman-ford",
        source=source,
        vertices=vertices_result,
        negative_cycle_reachable=len(neg_inf_set) > 0,
        negative_cycle=negative_cycle,
        passes=passes,
        relaxations=total_relaxations,
    )
