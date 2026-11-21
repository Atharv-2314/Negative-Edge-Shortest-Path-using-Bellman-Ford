"""Algorithmic implementations of shortest path solvers."""

from shortest_paths.algorithms.bellman_ford import bellman_ford
from shortest_paths.algorithms.dijkstra import dijkstra
from shortest_paths.algorithms.floyd_warshall import floyd_warshall
from shortest_paths.algorithms.johnson import johnson

ALGORITHMS = {
    "bellman-ford": bellman_ford,
    "dijkstra": dijkstra,
    "floyd-warshall": floyd_warshall,
    "johnson": johnson,
}

__all__ = [
    "bellman_ford",
    "dijkstra",
    "floyd_warshall",
    "johnson",
    "ALGORITHMS",
]


