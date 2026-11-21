"""File I/O operations for loading graphs from JSON files."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from shortest_paths.graph import Graph
from shortest_paths.models import GraphValidationError


def load_graph(path: str | Path, allow_float: bool = False) -> Graph:
    """Load a Graph instance from a JSON file.

    Format expected:
    {
        "directed": true,
        "vertices": ["0", "1", ...],
        "edges": [
            {"from": "0", "to": "1", "weight": 4}
        ]
    }

    Rules:
    - Integer weights remain int.
    - Decimal strings like "-1.5" or "3/4" become Fraction.
    - JSON float values are rejected unless allow_float=True.
    - Every error is raised as GraphValidationError naming the offending field.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise GraphValidationError(f"'file': path {str(path)!r} does not exist")

    try:
        with open(path_obj, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise GraphValidationError(f"'file': failed to parse JSON from {str(path)!r}: {e}")

    if not isinstance(data, dict):
        raise GraphValidationError("'root': JSON content must be an object")

    # Directed check
    if "directed" in data and not isinstance(data["directed"], bool):
        raise GraphValidationError("'directed': must be a boolean")

    # Vertices check
    if "vertices" not in data:
        raise GraphValidationError("'vertices': missing required field")
    if not isinstance(data["vertices"], list):
        raise GraphValidationError("'vertices': must be a list")

    vertices = data["vertices"]

    # Edges check
    if "edges" not in data:
        raise GraphValidationError("'edges': missing required field")
    if not isinstance(data["edges"], list):
        raise GraphValidationError("'edges': must be a list")

    parsed_edges: list[tuple[Any, Any, Any]] = []
    for idx, edge in enumerate(data["edges"]):
        if not isinstance(edge, dict):
            raise GraphValidationError(f"'edges[{idx}]': each edge must be an object")
        if "from" not in edge:
            raise GraphValidationError(f"'edges[{idx}].from': missing required field")
        if "to" not in edge:
            raise GraphValidationError(f"'edges[{idx}].to': missing required field")
        if "weight" not in edge:
            raise GraphValidationError(f"'edges[{idx}].weight': missing required field")

        u = edge["from"]
        v = edge["to"]
        raw_w = edge["weight"]

        # Parse weight according to rules
        if isinstance(raw_w, bool):
            raise GraphValidationError(
                f"'edges[{idx}].weight': boolean not accepted as weight"
            )
        elif isinstance(raw_w, int):
            parsed_w = raw_w
        elif isinstance(raw_w, float):
            if not allow_float:
                raise GraphValidationError(
                    f"'edges[{idx}].weight': float weights rejected unless allow_float=True"
                )
            parsed_w = Fraction(str(raw_w))
        elif isinstance(raw_w, str):
            try:
                parsed_w = Fraction(raw_w)
            except ValueError:
                raise GraphValidationError(
                    f"'edges[{idx}].weight': cannot parse string {raw_w!r} as Fraction"
                )
        else:
            raise GraphValidationError(
                f"'edges[{idx}].weight': unsupported weight type {type(raw_w).__name__!r}"
            )

        parsed_edges.append((u, v, parsed_w))

    return Graph(vertices, parsed_edges)
