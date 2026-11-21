"""Benchmark runner for shortest path algorithms."""

from __future__ import annotations

import argparse
import csv
import datetime
import platform
import random
import statistics
import sys
import time
from pathlib import Path

from shortest_paths.algorithms import bellman_ford, dijkstra, floyd_warshall, johnson
from shortest_paths.graph import Graph


def generate_graph(
    v: int,
    density: str,
    family: str,
    seed: int,
) -> Graph:
    """Generate a directed graph according to benchmark parameters."""
    rng = random.Random(seed)
    vertices = list(range(v))

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


def run_benchmarks(
    sizes: list[int],
    seed: int,
    runs: int = 5,
    quick: bool = False,
) -> list[dict]:
    records = []
    densities = ["sparse", "dense"]

    # SSSP Grid
    for v in sizes:
        for density in densities:
            # Family A: Bellman-Ford and Dijkstra
            g_a = generate_graph(v, density, "A", seed)
            source = 0

            bf_times = []
            bf_res = None
            for _ in range(runs):
                t0 = time.perf_counter()
                bf_res = bellman_ford(g_a, source)
                bf_times.append(time.perf_counter() - t0)

            records.append({
                "problem": "SSSP",
                "algorithm": "bellman-ford",
                "family": "A",
                "density": density,
                "v": v,
                "e": len(g_a.index_edges),
                "median_time_s": statistics.median(bf_times),
                "passes": bf_res.passes if bf_res else 0,
                "relaxations": bf_res.relaxations if bf_res else 0,
            })

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

            # Family B: Bellman-Ford ONLY (never run Dijkstra on B)
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

    # APSP Grid
    for v in sizes:
        for density in densities:
            for family in ["A", "B"]:
                g = generate_graph(v, density, family, seed)

                # Floyd-Warshall
                fw_times = []
                for _ in range(runs):
                    t0 = time.perf_counter()
                    floyd_warshall(g)
                    fw_times.append(time.perf_counter() - t0)

                records.append({
                    "problem": "APSP",
                    "algorithm": "floyd-warshall",
                    "family": family,
                    "density": density,
                    "v": v,
                    "e": len(g.index_edges),
                    "median_time_s": statistics.median(fw_times),
                    "passes": 0,
                    "relaxations": 0,
                })

                # Johnson
                john_times = []
                for _ in range(runs):
                    t0 = time.perf_counter()
                    johnson(g)
                    john_times.append(time.perf_counter() - t0)

                records.append({
                    "problem": "APSP",
                    "algorithm": "johnson",
                    "family": family,
                    "density": density,
                    "v": v,
                    "e": len(g.index_edges),
                    "median_time_s": statistics.median(john_times),
                    "passes": 0,
                    "relaxations": 0,
                })

    return records


def write_csv(records: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        # Machine header comments
        f.write(f"# Python: {sys.version.split()[0]}\n")
        f.write(f"# Platform: {platform.platform()}\n")
        f.write(f"# Processor: {platform.processor() or 'Unknown'}\n")
        f.write(f"# Timestamp: {datetime.datetime.now().isoformat()}\n")

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "problem",
                "algorithm",
                "family",
                "density",
                "v",
                "e",
                "median_time_s",
                "passes",
                "relaxations",
            ],
        )
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Shortest path benchmarking tool")
    parser.add_argument("--quick", action="store_true", help="Run quick benchmark (< 1 minute)")
    parser.add_argument("--sizes", type=int, nargs="+", default=None, help="Vertex counts V")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--runs", type=int, default=5, help="Number of repetitions for median")
    args = parser.parse_args()

    if args.quick:
        sizes = [10, 20, 30]
        runs = 3
    elif args.sizes:
        sizes = args.sizes
        runs = args.runs
    else:
        sizes = [10, 25, 50]
        runs = args.runs

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = Path("results") / f"benchmark_{timestamp}.csv"

    print(f"Running benchmarks (sizes={sizes}, seed={args.seed}, runs={runs})...")
    records = run_benchmarks(sizes, seed=args.seed, runs=runs, quick=args.quick)
    write_csv(records, csv_file)
    print(f"Benchmark results written to {csv_file}")

    for r in records[:10]:
        print(f"  {r['problem']:<4} {r['algorithm']:<15} {r['family']} {r['density']:<6} V={r['v']:<3} E={r['e']:<4} passes={r['passes']:<2} relax={r['relaxations']:<4} time={r['median_time_s']:.6f}s")
    if len(records) > 10:
        print(f"  ... and {len(records) - 10} more rows.")


if __name__ == "__main__":
    main()
