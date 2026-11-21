"""Unit tests for Floyd-Warshall algorithm (T1, T4, T6, T8)."""

from shortest_paths.algorithms.floyd_warshall import floyd_warshall
from shortest_paths.graph import Graph
from shortest_paths.models import Status


def test_t1_floyd_warshall():
    """T1: 0->1(2), 0->2(6), 1->2(3), 2->3(1): distances 0, 2, 5, 6 from source 0."""
    edges = [
        (0, 1, 2),
        (0, 2, 6),
        (1, 2, 3),
        (2, 3, 1),
    ]
    g = Graph([0, 1, 2, 3], edges)
    res = floyd_warshall(g)
    assert res.pairs[(0, 0)].distance == 0
    assert res.pairs[(0, 1)].distance == 2
    assert res.pairs[(0, 2)].distance == 5
    assert res.pairs[(0, 3)].distance == 6


def test_t4_g1_floyd_warshall(g1_graph):
    """T4: G1 Floyd-Warshall row 0 equals T2 (0, 2, 5, 5, 7, inf)."""
    res = floyd_warshall(g1_graph)
    assert res.has_negative_cycle is False
    assert res.pairs[(0, 0)].distance == 0
    assert res.pairs[(0, 1)].distance == 2
    assert res.pairs[(0, 2)].distance == 5
    assert res.pairs[(0, 3)].distance == 5
    assert res.pairs[(0, 4)].distance == 7
    assert res.pairs[(0, 5)].status == Status.UNREACHABLE


def test_t6_g2_floyd_warshall(g2_graph):
    """T6: G2: FW negative-cycle vertices = {1, 2, 3}."""
    res = floyd_warshall(g2_graph)
    assert res.has_negative_cycle is True
    assert res.negative_cycle_vertices == {1, 2, 3}


def test_t8_g3_floyd_warshall(g3_graph):
    """T8: G3: FW negative-cycle vertices = {5, 6}."""
    res = floyd_warshall(g3_graph)
    assert res.has_negative_cycle is True
    assert res.negative_cycle_vertices == {5, 6}
