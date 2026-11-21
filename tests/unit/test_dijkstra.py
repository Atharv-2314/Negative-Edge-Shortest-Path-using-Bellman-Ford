"""Unit tests for Dijkstra's algorithm (T1, T3)."""

import pytest
from shortest_paths.algorithms.dijkstra import dijkstra
from shortest_paths.graph import Graph
from shortest_paths.models import NegativeWeightError, Status


def test_t1_dijkstra():
    """T1: 0->1(2), 0->2(6), 1->2(3), 2->3(1): distances 0, 2, 5, 6."""
    edges = [
        (0, 1, 2),
        (0, 2, 6),
        (1, 2, 3),
        (2, 3, 1),
    ]
    g = Graph([0, 1, 2, 3], edges)
    res = dijkstra(g, 0)
    assert res.vertices[0].status == Status.FINITE
    assert res.vertices[0].distance == 0
    assert res.vertices[1].distance == 2
    assert res.vertices[2].distance == 5
    assert res.vertices[3].distance == 6
    assert res.passes == 0


def test_t3_g1_dijkstra_raises(g1_graph):
    """T3: G1 + Dijkstra raises NegativeWeightError."""
    with pytest.raises(NegativeWeightError) as exc_info:
        dijkstra(g1_graph, 0)
    assert "Negative-weight edge" in str(exc_info.value)
