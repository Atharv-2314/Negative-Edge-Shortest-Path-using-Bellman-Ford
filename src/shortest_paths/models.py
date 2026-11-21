"""Data models and exception definitions for shortest path algorithms.

This module defines the result status enumeration, result containers for
single-source shortest paths (SSSP), and standard exceptions raised during
graph validation or algorithmic execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from fractions import Fraction
from typing import Any, Optional

Weight = int | Fraction


class Status(Enum):
    """Reachability and cycle status for a vertex."""

    FINITE = auto()
    UNREACHABLE = auto()
    NEG_INFINITE = auto()


@dataclass(frozen=True)
class VertexResult:
    """Result for a single vertex in an SSSP computation.

    Invariant: distance and path must be None unless status is FINITE.
    """

    status: Status
    distance: Optional[Weight]
    path: Optional[list[Any]]

    def __post_init__(self) -> None:
        if self.status is not Status.FINITE:
            if self.distance is not None:
                raise ValueError("distance must be None for non-FINITE vertices")
            if self.path is not None:
                raise ValueError("path must be None for non-FINITE vertices")


@dataclass(frozen=True)
class SSSPResult:
    """Full result of a single-source shortest path calculation."""

    algorithm: str
    source: Any
    vertices: dict[Any, VertexResult]
    negative_cycle_reachable: bool
    negative_cycle: Optional[list[Any]]
    passes: int
    relaxations: int


@dataclass(frozen=True)
class APSPResult:
    """Full result of an all-pairs shortest paths calculation.

    pairs: mapping of (source, target) -> VertexResult
    has_negative_cycle: True if any negative-weight cycle is detected
    negative_cycle_vertices: set/list of vertex labels involved in negative cycles
    """

    algorithm: str
    pairs: dict[tuple[Any, Any], VertexResult]
    has_negative_cycle: bool
    negative_cycle_vertices: set[Any]



class GraphValidationError(ValueError):
    """Raised when the input graph structure or arguments fail validation."""


class NegativeWeightError(ValueError):
    """Raised when an algorithm receives a negative-weight edge it cannot handle."""


class NegativeCycleError(ValueError):
    """Raised when an algorithm detects an invalid negative cycle.

    Attributes:
        cycle: List of vertex labels forming the witness cycle.
    """

    def __init__(self, cycle: list[Any]) -> None:
        self.cycle = cycle
        super().__init__(f"Negative-weight cycle detected: {cycle}")
