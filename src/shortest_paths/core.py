"""Bellman-Ford single-source shortest paths solver with result model.

This module provides the Bellman-Ford algorithm together with the data
model that describes its results: Status, VertexResult, SSSPResult, and
the three public exception types.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, auto
from fractions import Fraction
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Weight type
# ---------------------------------------------------------------------------
Weight = int | Fraction


# ---------------------------------------------------------------------------
# Status enum
# ---------------------------------------------------------------------------
class Status(Enum):
    """Reachability / cycle status of a single vertex result."""

    FINITE = auto()
    UNREACHABLE = auto()
    NEG_INFINITE = auto()


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class VertexResult:
    """Result for a single vertex in an SSSP computation.

    Invariant
    ---------
    * ``distance`` and ``path`` are ``None`` unless ``status`` is ``FINITE``.
    * When ``status`` is ``FINITE``, ``distance`` is an exact ``int`` or
      ``Fraction`` and ``path`` is a non-empty list of vertex labels.
    """

    status: Status
    distance: Optional[Weight]
    path: Optional[list[Any]]

    def __post_init__(self) -> None:
        if self.status is not Status.FINITE:
            if self.distance is not None:
                raise ValueError(
                    "distance must be None for non-FINITE vertices"
                )
            if self.path is not None:
                raise ValueError("path must be None for non-FINITE vertices")


@dataclass(frozen=True)
class SSSPResult:
    """Full result of a single-source shortest-paths computation.

    Fields
    ------
    algorithm
        Name of the algorithm that produced this result.
    source
        Label of the source vertex.
    vertices
        Mapping from vertex label to :class:`VertexResult`.
    negative_cycle_reachable
        ``True`` when a negative-weight cycle reachable from *source* was
        detected.
    negative_cycle
        A list of vertex labels forming the witness cycle (closed walk with
        negative total weight), or ``None`` if none was detected.
    passes
        Number of relaxation passes performed (excluding the detection pass).
    relaxations
        Total number of successful edge relaxations across all passes.
    """

    algorithm: str
    source: Any
    vertices: dict[Any, VertexResult]
    negative_cycle_reachable: bool
    negative_cycle: Optional[list[Any]]
    passes: int
    relaxations: int


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------
class GraphValidationError(ValueError):
    """Raised when the input graph or arguments fail validation."""


class NegativeWeightError(ValueError):
    """Raised when an algorithm that requires non-negative weights receives a
    negative-weight edge."""


class NegativeCycleError(ValueError):
    """Raised when an algorithm that cannot handle negative cycles detects one.

    Attributes
    ----------
    cycle
        Witness cycle as a list of vertex labels (closed walk).
    """

    def __init__(self, cycle: list[Any]) -> None:
        self.cycle = cycle
        super().__init__(f"Negative-weight cycle detected: {cycle}")


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
