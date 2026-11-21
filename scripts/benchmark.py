"""Benchmark suite for shortest path algorithms."""

from __future__ import annotations

import random
from shortest_paths.graph import Graph


def generate_graph(
    v: int,
    density: str,
    family: str,
    seed: int,
) -> Graph:
    """Generate a directed graph according to benchmark parameters.

    Parameters
    ----------
    v : int
        Number of vertices.
    density : str
        'sparse' (E ~ 4V) or 'dense' (E ~ V^2 / 2).
    family : str
        'A': non-negative weights in [0, 100].
        'B': negative edges generated cycle-free via w = b + p(u) - p(v),
             with b in [0, 100], p(u) in [-50, 50].
    seed : int
        Explicit seed for reproducibility.
    """
    rng = random.Random(seed)
    vertices = list(range(v))

    # All possible directed pairs without self-loops
    possible_edges = [(u, target) for u in vertices for target in vertices if u != target]

    if density == "sparse":
        target_e = min(4 * v, len(possible_edges))
    elif density == "dense":
        target_e = min((v * v) // 2, len(possible_edges))
    else:
        raise ValueError(f"Unknown density: {density}")

    chosen_pairs = rng.sample(possible_edges, target_e)

    if family == "A":
        edges = [(u, target, rng.randint(0, 100)) for u, target in chosen_pairs]
    elif family == "B":
        potentials = {node: rng.randint(-50, 50) for node in vertices}
        edges = []
        for u, target in chosen_pairs:
            b = rng.randint(0, 100)
            w = b + potentials[u] - potentials[target]
            edges.append((u, target, w))
    else:
        raise ValueError(f"Unknown family: {family}")

    return Graph(vertices, edges)
