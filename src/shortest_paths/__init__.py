"""Shortest paths algorithms package."""

__version__ = "0.1.0"

from shortest_paths.models import (
    Status,
    VertexResult,
    SSSPResult,
    APSPResult,
    GraphValidationError,
    NegativeWeightError,
    NegativeCycleError,
    Weight,
)
from shortest_paths.graph import Graph
from shortest_paths.algorithms.bellman_ford import bellman_ford
from shortest_paths.algorithms.dijkstra import dijkstra

__all__ = [
    "Status",
    "VertexResult",
    "SSSPResult",
    "APSPResult",
    "GraphValidationError",
    "NegativeWeightError",
    "NegativeCycleError",
    "Weight",
    "Graph",
    "bellman_ford",
    "dijkstra",
]
