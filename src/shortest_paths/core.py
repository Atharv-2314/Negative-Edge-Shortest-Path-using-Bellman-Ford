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
    graph: Graph,
    source: Any,
) -> SSSPResult:
    """Run Bellman-Ford on a :class:`Graph`, returning an :class:`SSSPResult`.

    The n-th pass is a *real* relaxation pass: every still-relaxable edge is
    relaxed and the updated vertices are collected as the seed set *S*.  A BFS
    from *S* over out-edges then marks every reachable vertex as
    ``NEG_INFINITE`` (with ``distance = None`` and ``path = None``).

    Invariant
    ---------
    After pass *i* (1-indexed), ``dist[v]`` is the weight of the shortest path
    from *source* to *v* using at most *i* edges, for every vertex *v*.
    """
    from collections import deque

    inf = math.inf

    src_idx = graph.validate_source(source)
    n = graph.n
    edges = graph.index_edges

    dist: list = [inf] * n
    pred: list = [None] * n
    dist[src_idx] = 0

    total_relaxations = 0
    passes = 0

    # --- n-1 relaxation passes ---
    for _ in range(n - 1):
        changed = False
        passes += 1
        for u, v, w in edges:
            if dist[u] == inf:
                continue
            new_dist = dist[u] + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                pred[v] = u
                changed = True
                total_relaxations += 1
        if not changed:
            break

    # --- n-th pass: real relaxation + collect seed set S ---
    seed: set[int] = set()
    for u, v, w in edges:
        if dist[u] == inf:
            continue
        new_dist = dist[u] + w
        if new_dist < dist[v]:
            dist[v] = new_dist
            pred[v] = u
            seed.add(v)
            total_relaxations += 1

    # --- BFS from S to mark all NEG_INFINITE vertices ---
    adj: list[list[int]] = [[] for _ in range(n)]
    for u, v, _w in edges:
        adj[u].append(v)

    neg_inf_set: set[int] = set()
    queue: deque[int] = deque(seed)
    neg_inf_set.update(seed)
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if v not in neg_inf_set:
                neg_inf_set.add(v)
                queue.append(v)

    # --- Witness cycle extraction ---
    negative_cycle: Optional[list[Any]] = None
    if seed:
        # Pick any vertex x in S (seed of relaxation in n-th pass)
        x = next(iter(seed))
        # Step pred n times to guarantee entering a cycle
        for _ in range(n):
            if pred[x] is not None:
                x = pred[x]

        # Now walk pred from x until x repeats to extract the cycle
        cycle_rev = [x]
        curr = pred[x]
        while curr is not None and curr != x:
            cycle_rev.append(curr)
            curr = pred[curr]
        # Reverse to get forward order, then repeat first vertex at the end to close
        cycle_forward = list(reversed(cycle_rev))
        cycle_forward.append(cycle_forward[0])
        # Convert indices to graph labels
        negative_cycle = [graph.label(idx) for idx in cycle_forward]

    # --- Build SSSPResult ---
    vertices_result: dict[Any, VertexResult] = {}
    for idx in range(n):
        label = graph.label(idx)
        if idx in neg_inf_set:
            vertices_result[label] = VertexResult(
                status=Status.NEG_INFINITE, distance=None, path=None,
            )
        elif dist[idx] == inf:
            vertices_result[label] = VertexResult(
                status=Status.UNREACHABLE, distance=None, path=None,
            )
        else:
            # Reconstruct path from pred for FINITE vertices
            path_rev = [idx]
            curr = pred[idx]
            while curr is not None:
                path_rev.append(curr)
                curr = pred[curr]
            path_labels = [graph.label(i) for i in reversed(path_rev)]
            vertices_result[label] = VertexResult(
                status=Status.FINITE, distance=dist[idx], path=path_labels,
            )

    return SSSPResult(
        algorithm="bellman-ford",
        source=source,
        vertices=vertices_result,
        negative_cycle_reachable=len(neg_inf_set) > 0,
        negative_cycle=negative_cycle,
        passes=passes,
        relaxations=total_relaxations,
    )
