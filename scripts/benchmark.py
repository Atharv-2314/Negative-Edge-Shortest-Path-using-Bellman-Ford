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


def run_sssp_benchmark_grid(
    sizes: list[int],
    seed: int,
    runs: int = 5,
) -> list[dict]:
    """Run SSSP benchmark: BF and Dijkstra on family A; BF ONLY on family B.

    NEVER runs Dijkstra on family B.
    """
    import statistics
    import time
    from shortest_paths.algorithms import bellman_ford, dijkstra

    records = []
    densities = ["sparse", "dense"]

    for v in sizes:
        for density in densities:
            # Family A: non-negative weights -> run both Bellman-Ford and Dijkstra
            g_a = generate_graph(v, density, "A", seed)
            source = 0

            # 1. Bellman-Ford on A
            bf_a_times = []
            bf_a_res = None
            for _ in range(runs):
                t0 = time.perf_counter()
                bf_a_res = bellman_ford(g_a, source)
                bf_a_times.append(time.perf_counter() - t0)
            records.append({
                "problem": "SSSP",
                "algorithm": "bellman-ford",
                "family": "A",
                "density": density,
                "v": v,
                "e": len(g_a.index_edges),
                "median_time_s": statistics.median(bf_a_times),
                "passes": bf_a_res.passes if bf_a_res else 0,
                "relaxations": bf_a_res.relaxations if bf_a_res else 0,
            })

            # 2. Dijkstra on A
            dijk_times = []
            dijk_res = None
            for _ in range(runs):
                t0 = time.perf_counter()
                dijk_res = dijkstra(g_a, source)
                dijk_times.append(time.perf_counter() - t0)
            records.append({
                "problem": "SSSP",
                "algorithm": "dijkstra",
                "family": "A",
                "density": density,
                "v": v,
                "e": len(g_a.index_edges),
                "median_time_s": statistics.median(dijk_times),
                "passes": dijk_res.passes if dijk_res else 0,
                "relaxations": dijk_res.relaxations if dijk_res else 0,
            })

            # Family B: negative weights cycle-free -> run Bellman-Ford ONLY
            g_b = generate_graph(v, density, "B", seed)
            bf_b_times = []
            bf_b_res = None
            for _ in range(runs):
                t0 = time.perf_counter()
                bf_b_res = bellman_ford(g_b, source)
                bf_b_times.append(time.perf_counter() - t0)
            records.append({
                "problem": "SSSP",
                "algorithm": "bellman-ford",
                "family": "B",
                "density": density,
                "v": v,
                "e": len(g_b.index_edges),
                "median_time_s": statistics.median(bf_b_times),
                "passes": bf_b_res.passes if bf_b_res else 0,
                "relaxations": bf_b_res.relaxations if bf_b_res else 0,
            })

    return records

