"""Graph data structure with label-to-index mapping and endpoint validation.

This module provides the Graph class representing directed weighted graphs
with hashable vertex labels and integer/Fraction edge weights.
"""

from __future__ import annotations

from typing import Any
from shortest_paths.models import GraphValidationError, Weight
from shortest_paths.validation import validate_weight


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
        seen: set[Any] = set()
        for label in vertices:
            if label in seen:
                raise GraphValidationError(
                    f"'vertices': duplicate label {label!r}"
                )
            seen.add(label)

        self._labels: list[Any] = list(vertices)
        self._index: dict[Any, int] = {v: i for i, v in enumerate(self._labels)}

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
            validated_w = validate_weight(w, "edges")
            self._edges.append(
                (self._index[u_label], self._index[v_label], validated_w)
            )

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
