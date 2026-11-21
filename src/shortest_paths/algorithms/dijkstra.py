"""Dijkstra's single-source shortest paths solver for non-negative weights."""

from __future__ import annotations

import heapq
import math
from typing import Any

from shortest_paths.graph import Graph
from shortest_paths.models import (
    NegativeWeightError,
    SSSPResult,
    Status,
    VertexResult,
    Weight,
)


def _dijkstra_core(
    n: int,
    adj: list[list[tuple[int, Weight]]],
    src_idx: int,
) -> tuple[list[Weight | float], list[int | None], int]:
    """Reusable Dijkstra core relaxation loop using heapq with lazy deletion.

    Parameters
    ----------
    n : int
        Number of vertices (0 .. n-1).
    adj : list[list[tuple[int, Weight]]]
        Adjacency list mapping u -> list of (v, weight).
    src_idx : int
        Source vertex index.

    Returns
    -------
    dist : list[Weight | float]
        Shortest distance array (math.inf for unreachable).
    pred : list[int | None]
        Predecessor array for path reconstruction.
    relaxations : int
        Count of successful relaxations.
    """
    inf = math.inf
    dist: list[Weight | float] = [inf] * n
    pred: list[int | None] = [None] * n
    dist[src_idx] = 0

    relaxations = 0
    # Min-heap of (distance, vertex)
    heap: list[tuple[Weight | float, int]] = [(0, src_idx)]

    while heap:
        d_u, u = heapq.heappop(heap)

        # Lazy deletion: skip if popped distance is stale
        if d_u > dist[u]:
            continue

        for v, w in adj[u]:
            new_dist = dist[u] + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                pred[v] = u
                relaxations += 1
                heapq.heappush(heap, (new_dist, v))

    return dist, pred, relaxations


def dijkstra(graph: Graph, source: Any) -> SSSPResult:
    """Run Dijkstra's algorithm from source on a Graph with non-negative edge weights.

    Raises
    ------
    NegativeWeightError
        If any edge in the graph has negative weight, naming one such edge.
    GraphValidationError
        If source is not in the graph.
    """
    src_idx = graph.validate_source(source)
    n = graph.n
    index_edges = graph.index_edges

    # Check for negative weights BEFORE doing any work
    for u_idx, v_idx, w in index_edges:
        if w < 0:
            u_label = graph.label(u_idx)
            v_label = graph.label(v_idx)
            raise NegativeWeightError(
                f"Negative-weight edge encountered: ({u_label!r} -> {v_label!r}, weight={w})"
            )

    # Build adjacency list
    adj: list[list[tuple[int, Weight]]] = [[] for _ in range(n)]
    for u_idx, v_idx, w in index_edges:
        adj[u_idx].append((v_idx, w))

    dist, pred, relaxations = _dijkstra_core(n, adj, src_idx)

    # Build VertexResults
    vertices_result: dict[Any, VertexResult] = {}
    inf = math.inf
    for idx in range(n):
        label = graph.label(idx)
        if dist[idx] == inf:
            vertices_result[label] = VertexResult(
                status=Status.UNREACHABLE,
                distance=None,
                path=None,
            )
        else:
            # Reconstruct path
            path_rev = [idx]
            curr = pred[idx]
            while curr is not None:
                path_rev.append(curr)
                curr = pred[curr]
            path = [graph.label(i) for i in reversed(path_rev)]
            vertices_result[label] = VertexResult(
                status=Status.FINITE,
                distance=dist[idx],
                path=path,
            )

    return SSSPResult(
        algorithm="dijkstra",
        source=source,
        vertices=vertices_result,
        negative_cycle_reachable=False,
        negative_cycle=None,
        passes=0,
        relaxations=relaxations,
    )
