"""Unit tests for core functionality and edge cases (T2, T5, T7, T9-T14)."""

import pytest
from fractions import Fraction
from shortest_paths.core import (
    Graph,
    Status,
    bellman_ford,
    GraphValidationError,
)


def test_t2_g1():
    """T2: G1 / src 0 -> 0,2,5,5,7; vertex 5 UNREACHABLE; path to 4 = 0,2,1,3,4."""
    edges = [
        (0, 1, 4),
        (0, 2, 5),
        (2, 1, -3),
        (1, 3, 3),
        (2, 3, 4),
        (3, 4, 2),
        (1, 4, 6),
    ]
    g = Graph(list(range(6)), edges)
    res = bellman_ford(g, 0)

    assert res.negative_cycle_reachable is False
    assert res.negative_cycle is None

    expected_dist = {0: 0, 1: 2, 2: 5, 3: 5, 4: 7}
    for v, d in expected_dist.items():
        assert res.vertices[v].status == Status.FINITE
        assert res.vertices[v].distance == d

    assert res.vertices[5].status == Status.UNREACHABLE
    assert res.vertices[5].distance is None
    assert res.vertices[5].path is None

    assert res.vertices[4].path == [0, 2, 1, 3, 4]


def test_t5_g2():
    """T5: G2 / src 0 -> vertices 1-4 NEG_INFINITE (distance None); 5 UNREACHABLE;
    witness has total weight -6 and every consecutive pair is a real edge.
    """
    edges = [
        (0, 1, 4),
        (0, 2, 5),
        (2, 1, -3),
        (1, 3, 3),
        (2, 3, 4),
        (3, 4, 2),
        (1, 4, 6),
        (3, 2, -6),
    ]
    g = Graph(list(range(6)), edges)
    res = bellman_ford(g, 0)

    assert res.negative_cycle_reachable is True
    assert res.vertices[0].status == Status.FINITE
    assert res.vertices[0].distance == 0

    for v in [1, 2, 3, 4]:
        assert res.vertices[v].status == Status.NEG_INFINITE
        assert res.vertices[v].distance is None
        assert res.vertices[v].path is None

    assert res.vertices[5].status == Status.UNREACHABLE
    assert res.vertices[5].distance is None
    assert res.vertices[5].path is None

    # Witness checks
    witness = res.negative_cycle
    assert witness is not None
    assert len(witness) >= 2
    assert witness[0] == witness[-1]

    # Check consecutive pairs are real edges and sum to negative weight
    edge_map = {(u, v): w for u, v, w in edges}
    total_w = 0
    for i in range(len(witness) - 1):
        u, v = witness[i], witness[i + 1]
        assert (u, v) in edge_map
        total_w += edge_map[(u, v)]

    assert total_w == -6


def test_t7_g3():
    """T7: G3 / src 0 -> no reachable cycle; distances as T2; 5 and 6 UNREACHABLE."""
    edges = [
        (0, 1, 4),
        (0, 2, 5),
        (2, 1, -3),
        (1, 3, 3),
        (2, 3, 4),
        (3, 4, 2),
        (1, 4, 6),
        (5, 6, -1),
        (6, 5, -1),
    ]
    g = Graph(list(range(7)), edges)
    res = bellman_ford(g, 0)

    assert res.negative_cycle_reachable is False
    assert res.negative_cycle is None

    expected_dist = {0: 0, 1: 2, 2: 5, 3: 5, 4: 7}
    for v, d in expected_dist.items():
        assert res.vertices[v].status == Status.FINITE
        assert res.vertices[v].distance == d

    for v in [5, 6]:
        assert res.vertices[v].status == Status.UNREACHABLE
        assert res.vertices[v].distance is None
        assert res.vertices[v].path is None


def test_t9_single_vertex():
    """T9: single vertex -> source FINITE 0."""
    g = Graph([0], [])
    res = bellman_ford(g, 0)
    assert res.vertices[0].status == Status.FINITE
    assert res.vertices[0].distance == 0
    assert res.vertices[0].path == [0]
    assert res.negative_cycle_reachable is False
    assert res.passes == 0
    assert res.relaxations == 0


def test_t10_three_vertices_no_edges():
    """T10: three vertices, no edges -> source 0, others UNREACHABLE."""
    g = Graph([0, 1, 2], [])
    res = bellman_ford(g, 0)
    assert res.vertices[0].status == Status.FINITE
    assert res.vertices[0].distance == 0
    assert res.vertices[0].path == [0]
    for v in [1, 2]:
        assert res.vertices[v].status == Status.UNREACHABLE
        assert res.vertices[v].distance is None
        assert res.vertices[v].path is None
    assert res.negative_cycle_reachable is False


def test_t11_multiple_paths():
    """T11: 0->1(1), 0->2(1), 1->3(1), 2->3(1) -> d(3)=2, path weight = 2."""
    edges = [
        (0, 1, 1),
        (0, 2, 1),
        (1, 3, 1),
        (2, 3, 1),
    ]
    g = Graph([0, 1, 2, 3], edges)
    res = bellman_ford(g, 0)
    assert res.vertices[3].status == Status.FINITE
    assert res.vertices[3].distance == 2
    path = res.vertices[3].path
    assert path in ([0, 1, 3], [0, 2, 3])
    edge_map = {(u, v): w for u, v, w in edges}
    path_weight = sum(edge_map[(path[i], path[i + 1])] for i in range(len(path) - 1))
    assert path_weight == 2


def test_t12_negative_self_loop():
    """T12: 0->1(1), 1->1(-1), 1->2(1) -> vertices 1,2 NEG_INFINITE; witness (1,1)."""
    edges = [
        (0, 1, 1),
        (1, 1, -1),
        (1, 2, 1),
    ]
    g = Graph([0, 1, 2], edges)
    res = bellman_ford(g, 0)
    assert res.negative_cycle_reachable is True
    assert res.vertices[0].status == Status.FINITE
    assert res.vertices[1].status == Status.NEG_INFINITE
    assert res.vertices[2].status == Status.NEG_INFINITE
    assert res.vertices[1].distance is None
    assert res.vertices[2].distance is None
    assert res.negative_cycle == [1, 1]


def test_t13_parallel_edges():
    """T13: parallel edges 0->1(5), 0->1(2) -> d(1)=2."""
    edges = [
        (0, 1, 5),
        (0, 1, 2),
    ]
    g = Graph([0, 1], edges)
    res = bellman_ford(g, 0)
    assert res.vertices[1].status == Status.FINITE
    assert res.vertices[1].distance == 2
    assert res.vertices[1].path == [0, 1]


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
