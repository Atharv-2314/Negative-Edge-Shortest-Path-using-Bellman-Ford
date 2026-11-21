"""Input validation helpers for graphs and algorithm parameters.

This module provides validation functions to ensure graphs conform to required
invariants such as supported weight types and allowed values before execution.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any
from shortest_paths.models import GraphValidationError, Weight


def validate_weight(w: Any, field: str = "edges") -> Weight:
    """Validate and return an edge weight, rejecting booleans, floats, and strings."""
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
