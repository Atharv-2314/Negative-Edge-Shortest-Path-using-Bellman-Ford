"""Minimal Bellman-Ford single-source shortest paths solver.

This module provides a straightforward implementation of the Bellman-Ford
algorithm operating on integer-indexed vertices and integer-weighted edges.
"""

import math


def bellman_ford(
    n: int,
    edges: list[tuple[int, int, int]],
    source: int,
) -> tuple[list, list, bool]:
    """Run the Bellman-Ford algorithm on a directed, integer-weighted graph.

    Parameters
    ----------
    n : int
        Number of vertices (labelled 0 … n-1).
    edges : list[tuple[int, int, int]]
        Directed edges as (u, v, w) triples with integer weights.
    source : int
        Source vertex index.

    Returns
    -------
    dist : list
        Shortest distances from *source*. ``math.inf`` for unreachable vertices.
    pred : list
        Predecessor list (``None`` where undefined).
    has_reachable_negative_cycle : bool
        ``True`` if at least one edge can still be relaxed after *n-1* passes,
        indicating a negative-weight cycle reachable from *source*.

    Invariant
    ---------
    After pass *i* (1-indexed), ``dist[v]`` is the weight of the shortest path
    from *source* to *v* using at most *i* edges, for every vertex *v*.
    """
    inf = math.inf

    dist: list = [inf] * n
    pred: list = [None] * n
    dist[source] = 0

    # --- n-1 relaxation passes ---
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] == inf:
                # Tail unreachable – skip to avoid inf + w arithmetic.
                continue
            new_dist = dist[u] + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                pred[v] = u
                changed = True
        if not changed:
            # Early termination: no distance improved in this pass.
            break

    # --- Detection pass (the n-th pass) ---
    has_reachable_negative_cycle = False
    for u, v, w in edges:
        if dist[u] == inf:
            continue
        if dist[u] + w < dist[v]:
            has_reachable_negative_cycle = True
            break

    return dist, pred, has_reachable_negative_cycle
