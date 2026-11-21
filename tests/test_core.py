"""Tests for the Bellman-Ford solver (Phase 1 + Phase 2 API)."""

from shortest_paths.core import bellman_ford, Graph, Status


def test_g1_distances_and_no_cycle():
    """G1: dist [0,2,5,5,7], vertex 5 UNREACHABLE, no cycle."""
    edges = [
        (0, 1, 4), (0, 2, 5), (2, 1, -3),
        (1, 3, 3), (2, 3, 4), (3, 4, 2), (1, 4, 6),
    ]
    g = Graph(list(range(6)), edges)
    result = bellman_ford(g, source=0)

    assert result.vertices[0].status is Status.FINITE
    assert result.vertices[0].distance == 0
    assert result.vertices[1].distance == 2
    assert result.vertices[2].distance == 5
    assert result.vertices[3].distance == 5
    assert result.vertices[4].distance == 7
    assert result.vertices[5].status is Status.UNREACHABLE
    assert result.negative_cycle_reachable is False


def test_g2_reachable_negative_cycle():
    """G2 = G1 + (3->2, -6): vertices 1-4 NEG_INFINITE, vertex 5 UNREACHABLE."""
    edges = [
        (0, 1, 4), (0, 2, 5), (2, 1, -3),
        (1, 3, 3), (2, 3, 4), (3, 4, 2), (1, 4, 6),
        (3, 2, -6),
    ]
    g = Graph(list(range(6)), edges)
    result = bellman_ford(g, source=0)

    assert result.negative_cycle_reachable is True
    for v in [1, 2, 3, 4]:
        assert result.vertices[v].status is Status.NEG_INFINITE
        assert result.vertices[v].distance is None
    assert result.vertices[5].status is Status.UNREACHABLE


def test_g3_unreachable_negative_cycle():
    """G3 = G1 + (5->6,-1),(6->5,-1): no reachable cycle; 5,6 UNREACHABLE."""
    edges = [
        (0, 1, 4), (0, 2, 5), (2, 1, -3),
        (1, 3, 3), (2, 3, 4), (3, 4, 2), (1, 4, 6),
        (5, 6, -1), (6, 5, -1),
    ]
    g = Graph(list(range(7)), edges)
    result = bellman_ford(g, source=0)

    assert result.vertices[0].distance == 0
    assert result.vertices[1].distance == 2
    assert result.vertices[2].distance == 5
    assert result.vertices[3].distance == 5
    assert result.vertices[4].distance == 7
    assert result.vertices[5].status is Status.UNREACHABLE
    assert result.vertices[6].status is Status.UNREACHABLE
    assert result.negative_cycle_reachable is False


def test_single_vertex_no_edges():
    g = Graph([0], [])
    result = bellman_ford(g, source=0)
    assert result.vertices[0].status is Status.FINITE
    assert result.vertices[0].distance == 0
    assert result.negative_cycle_reachable is False


def test_three_vertices_no_edges():
    g = Graph([0, 1, 2], [])
    result = bellman_ford(g, source=0)
    assert result.vertices[0].distance == 0
    assert result.vertices[1].status is Status.UNREACHABLE
    assert result.vertices[2].status is Status.UNREACHABLE
    assert result.negative_cycle_reachable is False
