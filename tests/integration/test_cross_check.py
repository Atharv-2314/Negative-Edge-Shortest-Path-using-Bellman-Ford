"""Cross-check integration tests (T1, T15, T16) comparing all algorithms."""

import random
from shortest_paths.algorithms import bellman_ford, dijkstra, floyd_warshall, johnson
from shortest_paths.graph import Graph
from shortest_paths.models import Status


def test_t1_all_four_agree():
    """T1: 0->1(2), 0->2(6), 1->2(3), 2->3(1): distances 0, 2, 5, 6, all four agree."""
    edges = [
        (0, 1, 2),
        (0, 2, 6),
        (1, 2, 3),
        (2, 3, 1),
    ]
    g = Graph([0, 1, 2, 3], edges)
    expected = [0, 2, 5, 6]

    bf_res = bellman_ford(g, 0)
    dijk_res = dijkstra(g, 0)
    fw_res = floyd_warshall(g)
    john_res = johnson(g)

    for i, exp in enumerate(expected):
        assert bf_res.vertices[i].distance == exp
        assert dijk_res.vertices[i].distance == exp
        assert fw_res.pairs[(0, i)].distance == exp
        assert john_res.pairs[(0, i)].distance == exp


def test_t15_cross_check_negative_cycle_free():
    """T15: Seeded random graphs (V <= 8) with negative edges generated via
    w = b + p(u) - p(v), b in [0, 10], p in [-10, 10].
    Bellman-Ford, Floyd-Warshall, and Johnson must give identical distance tables.
    """
    rng = random.Random(42)
    for test_idx in range(5):
        num_v = rng.randint(4, 8)
        vertices = list(range(num_v))
        potentials = {v: rng.randint(-10, 10) for v in vertices}

        edges = []
        for u in vertices:
            for v in vertices:
                if u != v and rng.random() < 0.4:
                    base = rng.randint(0, 10)
                    w = base + potentials[u] - potentials[v]
                    edges.append((u, v, w))

        g = Graph(vertices, edges)
        fw_res = floyd_warshall(g)
        john_res = johnson(g)

        assert fw_res.has_negative_cycle is False
        assert john_res.has_negative_cycle is False

        # Cross-check Floyd-Warshall and Johnson for all pairs
        for u in vertices:
            bf_u = bellman_ford(g, u)
            for v in vertices:
                fw_pair = fw_res.pairs[(u, v)]
                john_pair = john_res.pairs[(u, v)]
                bf_v = bf_u.vertices[v]

                assert fw_pair.status == john_pair.status == bf_v.status
                if fw_pair.status == Status.FINITE:
                    assert fw_pair.distance == john_pair.distance == bf_v.distance


def test_t16_cross_check_nonnegative():
    """T16: Seeded random graphs (V <= 8) with non-negative weights.
    All four algorithms (BF, Dijkstra, FW, Johnson) must give identical tables.
    """
    rng = random.Random(1337)
    for test_idx in range(5):
        num_v = rng.randint(4, 8)
        vertices = list(range(num_v))

        edges = []
        for u in vertices:
            for v in vertices:
                if u != v and rng.random() < 0.4:
                    w = rng.randint(0, 20)
                    edges.append((u, v, w))

        g = Graph(vertices, edges)
        fw_res = floyd_warshall(g)
        john_res = johnson(g)

        for u in vertices:
            bf_u = bellman_ford(g, u)
            dijk_u = dijkstra(g, u)

            for v in vertices:
                fw_pair = fw_res.pairs[(u, v)]
                john_pair = john_res.pairs[(u, v)]
                bf_v = bf_u.vertices[v]
                dijk_v = dijk_u.vertices[v]

                assert (
                    fw_pair.status
                    == john_pair.status
                    == bf_v.status
                    == dijk_v.status
                )
                if fw_pair.status == Status.FINITE:
                    assert (
                        fw_pair.distance
                        == john_pair.distance
                        == bf_v.distance
                        == dijk_v.distance
                    )
