"""Unit tests for input validation (T14)."""

import pytest
from shortest_paths.graph import Graph
from shortest_paths.models import GraphValidationError
from shortest_paths.algorithms.bellman_ford import bellman_ford


def test_t14_invalid_input():
    """T14: invalid input -> GraphValidationError naming the field."""
    # Duplicate vertices
    with pytest.raises(GraphValidationError) as exc1:
        Graph([0, 1, 0], [])
    assert "'vertices'" in str(exc1.value)

    # Unknown source vertex in edge
    with pytest.raises(GraphValidationError) as exc2:
        Graph([0, 1], [(2, 1, 1)])
    assert "'edges'" in str(exc2.value)

    # Unknown dest vertex in edge
    with pytest.raises(GraphValidationError) as exc3:
        Graph([0, 1], [(0, 2, 1)])
    assert "'edges'" in str(exc3.value)

    # Bool weight
    with pytest.raises(GraphValidationError) as exc4:
        Graph([0, 1], [(0, 1, True)])
    assert "'edges'" in str(exc4.value)

    # Float weight
    with pytest.raises(GraphValidationError) as exc5:
        Graph([0, 1], [(0, 1, 2.5)])
    assert "'edges'" in str(exc5.value)

    # String weight
    with pytest.raises(GraphValidationError) as exc6:
        Graph([0, 1], [(0, 1, "3")])
    assert "'edges'" in str(exc6.value)

    # Missing source in bellman_ford
    g = Graph([0, 1], [(0, 1, 1)])
    with pytest.raises(GraphValidationError) as exc7:
        bellman_ford(g, 99)
    assert "'source'" in str(exc7.value)
