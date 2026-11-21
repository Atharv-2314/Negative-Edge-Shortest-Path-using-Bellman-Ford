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


# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------
def _validate_weight(w: Any, field: str) -> Weight:
    """Return *w* as a valid Weight or raise GraphValidationError."""
    # Reject booleans first (bool is a subclass of int in Python)
    if isinstance(w, bool):
        raise GraphValidationError(
            f"'{field}': weight must be int or Fraction, got bool"
        )
    if isinstance(w, int):
        return w
    if isinstance(w, Fraction):
        return w
    if isinstance(w, float):
        raise GraphValidationError(
            f"'{field}': float weights are not accepted; use int or Fraction"
        )
    raise GraphValidationError(
        f"'{field}': weight must be int or Fraction, got {type(w).__name__!r}"
    )


class Graph:
    """Directed, weighted graph with hashable vertex labels.

    Parameters
    ----------
    vertices : list
        Ordered, duplicate-free sequence of hashable vertex labels.
    edges : list[tuple[Any, Any, int | Fraction]]
        Directed edges as ``(from_label, to_label, weight)`` triples.
        Parallel edges and self-loops are permitted.

    Raises
    ------
    GraphValidationError
        On duplicate vertices, unknown endpoints, or invalid weight types.
    """

    def __init__(
        self,
        vertices: list[Any],
        edges: list[tuple[Any, Any, Any]],
    ) -> None:
        # --- vertex uniqueness ---
        seen: set[Any] = set()
        for label in vertices:
            if label in seen:
                raise GraphValidationError(
                    f"'vertices': duplicate label {label!r}"
                )
            seen.add(label)

        self._labels: list[Any] = list(vertices)
        self._index: dict[Any, int] = {v: i for i, v in enumerate(self._labels)}

        # --- edge validation ---
        self._edges: list[tuple[int, int, Weight]] = []
        for u_label, v_label, w in edges:
            if u_label not in self._index:
                raise GraphValidationError(
                    f"'edges': unknown source vertex {u_label!r}"
                )
            if v_label not in self._index:
                raise GraphValidationError(
                    f"'edges': unknown destination vertex {v_label!r}"
                )
            validated_w = _validate_weight(w, "edges")
            self._edges.append(
                (self._index[u_label], self._index[v_label], validated_w)
            )

    # --- public helpers ---
    @property
    def n(self) -> int:
        """Number of vertices."""
        return len(self._labels)

    @property
    def labels(self) -> list[Any]:
        """Vertex labels in insertion order."""
        return list(self._labels)

    @property
    def index_edges(self) -> list[tuple[int, int, Weight]]:
        """Edges as ``(u_idx, v_idx, weight)`` triples (index-based)."""
        return list(self._edges)

    def label(self, idx: int) -> Any:
        """Return the vertex label for a given index."""
        return self._labels[idx]

    def index_of(self, label: Any) -> int:
        """Return the index for a given vertex label."""
        return self._index[label]

    def validate_source(self, source: Any) -> int:
        """Return the index of *source* or raise GraphValidationError."""
        if source not in self._index:
            raise GraphValidationError(
                f"'source': vertex {source!r} is not in the graph"
            )
        return self._index[source]


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
