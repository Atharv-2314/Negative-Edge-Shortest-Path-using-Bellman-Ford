"""Unit tests for Bellman-Ford algorithm (T2, T5, T7, T9-T13)."""

from shortest_paths.algorithms.bellman_ford import bellman_ford
from shortest_paths.graph import Graph
from shortest_paths.models import Status


def test_t2_g1(g1_graph):
    """T2: G1 / src 0 -> 0,2,5,5,7; vertex 5 UNREACHABLE; path to 4 = 0,2,1,3,4."""
    res = bellman_ford(g1_graph, 0)

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


def test_t5_g2(g2_graph):
    """T5: G2 / src 0 -> vertices 1-4 NEG_INFINITE (distance None); 5 UNREACHABLE;
    witness has total weight -6 and every consecutive pair is a real edge.
    """
    res = bellman_ford(g2_graph, 0)

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

    witness = res.negative_cycle
    assert witness is not None
    assert len(witness) >= 2
    assert witness[0] == witness[-1]

    edge_map = {(u, v): w for u, v, w in [(e[0], e[1], e[2]) for e in g2_graph.index_edges]}
    total_w = 0
    for i in range(len(witness) - 1):
        u, v = witness[i], witness[i + 1]
        assert (u, v) in edge_map
        total_w += edge_map[(u, v)]

    assert total_w == -6


def test_t7_g3(g3_graph):
    """T7: G3 / src 0 -> no reachable cycle; distances as T2; 5 and 6 UNREACHABLE."""
    res = bellman_ford(g3_graph, 0)

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


def test_t11_multiple_paths(t11_diamond_graph):
    """T11: 0->1(1), 0->2(1), 1->3(1), 2->3(1) -> d(3)=2, path weight = 2."""
    res = bellman_ford(t11_diamond_graph, 0)
    assert res.vertices[3].status == Status.FINITE
    assert res.vertices[3].distance == 2
    path = res.vertices[3].path
    assert path in ([0, 1, 3], [0, 2, 3])
    edge_map = {(u, v): w for u, v, w in t11_diamond_graph.index_edges}
    path_weight = sum(edge_map[(path[i], path[i + 1])] for i in range(len(path) - 1))
    assert path_weight == 2


def test_t12_negative_self_loop(t12_self_loop_graph):
    """T12: 0->1(1), 1->1(-1), 1->2(1) -> vertices 1,2 NEG_INFINITE; witness (1,1)."""
    res = bellman_ford(t12_self_loop_graph, 0)
    assert res.negative_cycle_reachable is True
    assert res.vertices[0].status == Status.FINITE
    assert res.vertices[1].status == Status.NEG_INFINITE
    assert res.vertices[2].status == Status.NEG_INFINITE
    assert res.vertices[1].distance is None
    assert res.vertices[2].distance is None
    assert res.negative_cycle == [1, 1]


def test_t13_parallel_edges(t13_parallel_graph):
    """T13: parallel edges 0->1(5), 0->1(2) -> d(1)=2."""
    res = bellman_ford(t13_parallel_graph, 0)
    assert res.vertices[1].status == Status.FINITE
    assert res.vertices[1].distance == 2
    assert res.vertices[1].path == [0, 1]
