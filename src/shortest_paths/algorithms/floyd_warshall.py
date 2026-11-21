"""Floyd-Warshall all-pairs shortest paths solver with negative cycle detection."""

from __future__ import annotations

import math
from typing import Any

from shortest_paths.graph import Graph
from shortest_paths.models import APSPResult, Status, VertexResult, Weight


def floyd_warshall(graph: Graph) -> APSPResult:
    """Run Floyd-Warshall algorithm on a Graph.

    Never raises for negative cycles; instead detects them via negative diagonal entries
    D[i][i] < 0 and marks affected pairs as NEG_INFINITE.
    """
    n = graph.n
    inf = math.inf

    # Initialize distance matrix D and next-hop matrix next_hop
    # D: n x n
    # next_hop: n x n (stores next vertex index on path from i to j)
    D: list[list[Weight | float]] = [[inf] * n for _ in range(n)]
    next_hop: list[list[int | None]] = [[None] * n for _ in range(n)]

    for i in range(n):
        D[i][i] = 0
        next_hop[i][i] = i

    # Populate edge weights taking minimum over parallel edges
    for u, v, w in graph.index_edges:
        if w < D[u][v]:
            D[u][v] = w
            next_hop[u][v] = v

    # Triple loop k, i, j
    for k in range(n):
        for i in range(n):
            if D[i][k] == inf:
                continue
            for j in range(n):
                if D[k][j] == inf:
                    continue
                new_dist = D[i][k] + D[k][j]
                if new_dist < D[i][j]:
                    D[i][j] = new_dist
                    next_hop[i][j] = next_hop[i][k]

    # Negative cycle vertices: {i : D[i][i] < 0}
    neg_cycle_indices = {i for i in range(n) if D[i][i] < 0}
    has_negative_cycle = len(neg_cycle_indices) > 0
    negative_cycle_vertices = {graph.label(i) for i in neg_cycle_indices}

    # A pair (i, j) has distance -inf if there exists some k such that:
    # D[k][k] < 0 and D[i][k] < inf and D[k][j] < inf.
    neg_inf_pairs: set[tuple[int, int]] = set()
    if has_negative_cycle:
        for i in range(n):
            for j in range(n):
                for k in neg_cycle_indices:
                    if D[i][k] < inf and D[k][j] < inf:
                        neg_inf_pairs.add((i, j))
                        break

    def reconstruct_path(start: int, end: int) -> list[Any] | None:
        """Reconstruct path from start to end using next_hop matrix."""
        if next_hop[start][end] is None:
            return None
        curr = start
        path_indices = [curr]
        visited = {curr}
        while curr != end:
            nxt = next_hop[curr][end]
            if nxt is None or nxt in visited:
                # Cycle or broken path
                return None
            visited.add(nxt)
            path_indices.append(nxt)
            curr = nxt
        return [graph.label(idx) for idx in path_indices]

    pairs: dict[tuple[Any, Any], VertexResult] = {}
    for i in range(n):
        u_label = graph.label(i)
        for j in range(n):
            v_label = graph.label(j)
            pair_key = (u_label, v_label)

            if (i, j) in neg_inf_pairs:
                pairs[pair_key] = VertexResult(
                    status=Status.NEG_INFINITE,
                    distance=None,
                    path=None,
                )
            elif D[i][j] == inf:
                pairs[pair_key] = VertexResult(
                    status=Status.UNREACHABLE,
                    distance=None,
                    path=None,
                )
            else:
                path = reconstruct_path(i, j)
                pairs[pair_key] = VertexResult(
                    status=Status.FINITE,
                    distance=D[i][j],
                    path=path,
                )

    return APSPResult(
        algorithm="floyd-warshall",
        pairs=pairs,
        has_negative_cycle=has_negative_cycle,
        negative_cycle_vertices=negative_cycle_vertices,
    )
