"""Command-line interface for shortest_paths package."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from shortest_paths.algorithms import ALGORITHMS
from shortest_paths.io import load_graph
from shortest_paths.models import (
    APSPResult,
    GraphValidationError,
    NegativeCycleError,
    NegativeWeightError,
    SSSPResult,
    Status,
)


def format_sssp_table(result: SSSPResult, graph_labels: list[Any]) -> str:
    lines = []
    lines.append(f"Algorithm: {result.algorithm}")
    lines.append(f"Source:    {result.source}")
    lines.append(f"Reachable negative cycle: {result.negative_cycle_reachable}")
    if result.negative_cycle:
        cycle_str = " -> ".join(str(v) for v in result.negative_cycle)
        lines.append(f"Witness cycle: {cycle_str}")
    lines.append("")
    lines.append(f"{'Vertex':<10} {'Status':<15} {'Distance':<15} {'Path'}")
    lines.append("-" * 65)

    for v in graph_labels:
        vr = result.vertices[v]
        status_str = vr.status.name.lower()
        dist_str = str(vr.distance) if vr.status == Status.FINITE else "-"
        if vr.status == Status.FINITE and vr.path is not None:
            path_str = " -> ".join(str(p) for p in vr.path)
        else:
            path_str = "-"
        lines.append(f"{str(v):<10} {status_str:<15} {dist_str:<15} {path_str}")

    return "\n".join(lines)


def format_apsp_table(result: APSPResult, graph_labels: list[Any]) -> str:
    lines = []
    lines.append(f"Algorithm: {result.algorithm}")
    lines.append(f"Has negative cycle: {result.has_negative_cycle}")
    if result.negative_cycle_vertices:
        nc_str = ", ".join(str(v) for v in sorted(result.negative_cycle_vertices, key=str))
        lines.append(f"Negative cycle vertices: {nc_str}")
    lines.append("")
    lines.append(f"{'Source':<10} {'Target':<10} {'Status':<15} {'Distance':<15} {'Path'}")
    lines.append("-" * 75)

    for u in graph_labels:
        for v in graph_labels:
            vr = result.pairs[(u, v)]
            status_str = vr.status.name.lower()
            dist_str = str(vr.distance) if vr.status == Status.FINITE else "-"
            if vr.status == Status.FINITE and vr.path is not None:
                path_str = " -> ".join(str(p) for p in vr.path)
            else:
                path_str = "-"
            lines.append(f"{str(u):<10} {str(v):<10} {status_str:<15} {dist_str:<15} {path_str}")

    return "\n".join(lines)


def sssp_to_dict(result: SSSPResult, graph_labels: list[Any]) -> dict[str, Any]:
    return {
        "algorithm": result.algorithm,
        "source": result.source,
        "negative_cycle_reachable": result.negative_cycle_reachable,
        "negative_cycle": result.negative_cycle,
        "passes": result.passes,
        "relaxations": result.relaxations,
        "vertices": {
            str(v): {
                "status": result.vertices[v].status.name.lower(),
                "distance": (
                    float(result.vertices[v].distance)
                    if isinstance(result.vertices[v].distance, (int, float))
                    else str(result.vertices[v].distance)
                    if result.vertices[v].distance is not None
                    else None
                ),
                "path": result.vertices[v].path,
            }
            for v in graph_labels
        },
    }


def apsp_to_dict(result: APSPResult, graph_labels: list[Any]) -> dict[str, Any]:
    return {
        "algorithm": result.algorithm,
        "has_negative_cycle": result.has_negative_cycle,
        "negative_cycle_vertices": list(result.negative_cycle_vertices),
        "pairs": {
            f"{u}->{v}": {
                "status": result.pairs[(u, v)].status.name.lower(),
                "distance": (
                    float(result.pairs[(u, v)].distance)
                    if isinstance(result.pairs[(u, v)].distance, (int, float))
                    else str(result.pairs[(u, v)].distance)
                    if result.pairs[(u, v)].distance is not None
                    else None
                ),
                "path": result.pairs[(u, v)].path,
            }
            for u in graph_labels
            for v in graph_labels
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shortest-paths",
        description="Single-Source and All-Pairs Shortest Paths CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # sssp subcommand
    sssp_parser = subparsers.add_parser("sssp", help="Compute single-source shortest paths")
    sssp_parser.add_argument("file", help="Path to graph JSON file")
    sssp_parser.add_argument("--source", "-s", required=True, help="Source vertex label")
    sssp_parser.add_argument(
        "--algorithm",
        "-a",
        choices=["bellman-ford", "dijkstra"],
        default="bellman-ford",
        help="Algorithm to run (default: bellman-ford)",
    )
    sssp_parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    # apsp subcommand
    apsp_parser = subparsers.add_parser("apsp", help="Compute all-pairs shortest paths")
    apsp_parser.add_argument("file", help="Path to graph JSON file")
    apsp_parser.add_argument(
        "--algorithm",
        "-a",
        choices=["floyd-warshall", "johnson"],
        default="floyd-warshall",
        help="Algorithm to run (default: floyd-warshall)",
    )
    apsp_parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        graph = load_graph(args.file)
    except GraphValidationError as e:
        sys.stderr.write(f"Validation error: {e}\n")
        return 1

    algo_func = ALGORITHMS[args.algorithm]

    try:
        if args.command == "sssp":
            # Check source exists
            if args.source not in graph.labels:
                sys.stderr.write(f"Validation error: 'source': vertex {args.source!r} is not in the graph\n")
                return 1

            result = algo_func(graph, args.source)
            if args.json:
                print(json.dumps(sssp_to_dict(result, graph.labels), indent=2))
            else:
                print(format_sssp_table(result, graph.labels))

            if result.negative_cycle_reachable:
                return 3
            return 0

        elif args.command == "apsp":
            result = algo_func(graph)
            if args.json:
                print(json.dumps(apsp_to_dict(result, graph.labels), indent=2))
            else:
                print(format_apsp_table(result, graph.labels))

            if result.has_negative_cycle:
                return 3
            return 0

    except NegativeWeightError as e:
        sys.stderr.write(f"Precondition error: {e}\n")
        return 2
    except NegativeCycleError as e:
        sys.stderr.write(f"Negative cycle error: {e}\n")
        return 3
    except GraphValidationError as e:
        sys.stderr.write(f"Validation error: {e}\n")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
