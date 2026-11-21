"""Johnson's all-pairs shortest paths algorithm using Bellman-Ford and Dijkstra."""

from __future__ import annotations

import math
from typing import Any

from shortest_paths.algorithms.bellman_ford import bellman_ford
from shortest_paths.algorithms.dijkstra import _dijkstra_core
from shortest_paths.graph import Graph
from shortest_paths.models import (
    APSPResult,
    NegativeCycleError,
    Status,
    VertexResult,
    Weight,
)


def johnson(graph: Graph) -> APSPResult:
    """Run Johnson's APSP algorithm on a Graph.

    Adds a fresh super-source s with 0-weight edges to all vertices, runs
    Bellman-Ford to find potentials h(v), reweights all edges:
        w'(u, v) = w(u, v) + h(u) - h(v) >= 0
    runs Dijkstra from each vertex using reweighted edges, then converts
    distances back:
        d(u, v) = d'(u, v) - h(u) + h(v)

    Raises
    ------
    NegativeCycleError
        If a negative-weight cycle is detected in the graph.
    """
    n = graph.n
    inf = math.inf

    # 1. Create super-source with 0-weight edges to all vertices
    super_source = object()
    extended_vertices = list(graph.labels) + [super_source]
    original_edges = [(graph.label(u), graph.label(v), w) for u, v, w in graph.index_edges]
    super_edges = [(super_source, v, 0) for v in graph.labels]
    extended_graph = Graph(extended_vertices, original_edges + super_edges)

    # 2. Run Bellman-Ford from super-source
    bf_result = bellman_ford(extended_graph, super_source)
    if bf_result.negative_cycle_reachable:
        witness = bf_result.negative_cycle or []
        raise NegativeCycleError(witness)

    # 3. Potentials h(v) for each vertex v
    h: list[Weight] = []
    for i in range(n):
        lbl = graph.label(i)
        dist_val = bf_result.vertices[lbl].distance
        assert dist_val is not None, f"Potential for {lbl} must be finite"
        h.append(dist_val)

    # 4. Reweight edges: w' = w + h[u] - h[v] and assert w' >= 0
    adj_reweighted: list[list[tuple[int, Weight]]] = [[] for _ in range(n)]
    for u, v, w in graph.index_edges:
        w_prime = w + h[u] - h[v]
        assert w_prime >= 0, f"Reweighted edge ({u}->{v}) has negative weight {w_prime}"
        adj_reweighted[u].append((v, w_prime))

    # 5. Run Dijkstra from each vertex
    pairs: dict[tuple[Any, Any], VertexResult] = {}
    for u in range(n):
        u_label = graph.label(u)
        dist_prime, pred, _ = _dijkstra_core(n, adj_reweighted, u)

        for v in range(n):
            v_label = graph.label(v)
            if dist_prime[v] == inf:
                pairs[(u_label, v_label)] = VertexResult(
                    status=Status.UNREACHABLE,
                    distance=None,
                    path=None,
                )
            else:
                # Convert back distance: d = d' - h(u) + h(v)
                real_dist = dist_prime[v] - h[u] + h[v]

                # Reconstruct path
                path_rev = [v]
                curr = pred[v]
                while curr is not None:
                    path_rev.append(curr)
                    curr = pred[curr]
                path = [graph.label(i) for i in reversed(path_rev)]

                pairs[(u_label, v_label)] = VertexResult(
                    status=Status.FINITE,
                    distance=real_dist,
                    path=path,
                )

    return APSPResult(
        algorithm="johnson",
        pairs=pairs,
        has_negative_cycle=False,
        negative_cycle_vertices=set(),
    )
