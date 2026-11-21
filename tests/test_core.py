import math
from shortest_paths.core import bellman_ford


def test_g1_distances_and_no_cycle():
    # G1 = [(0,1,4),(0,2,5),(2,1,-3),(1,3,3),(2,3,4),(3,4,2),(1,4,6)], n=6
    # -> dist [0,2,5,5,7,inf], no cycle
    edges = [
        (0, 1, 4),
        (0, 2, 5),
        (2, 1, -3),
        (1, 3, 3),
        (2, 3, 4),
        (3, 4, 2),
        (1, 4, 6),
    ]
    dist, pred, has_cycle = bellman_ford(6, edges, source=0)
    assert dist == [0, 2, 5, 5, 7, math.inf]
    assert has_cycle is False


def test_g2_reachable_negative_cycle():
    # G2 = G1 + [(3,2,-6)] -> cycle flag True
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
    dist, pred, has_cycle = bellman_ford(6, edges, source=0)
    assert has_cycle is True


def test_g3_unreachable_negative_cycle():
    # G3 = G1 + [(5,6,-1),(6,5,-1)], n=7 -> flag False, dist = G1's + inf
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
    dist, pred, has_cycle = bellman_ford(7, edges, source=0)
    assert dist == [0, 2, 5, 5, 7, math.inf, math.inf]
    assert has_cycle is False


def test_single_vertex_no_edges():
    dist, pred, has_cycle = bellman_ford(1, [], source=0)
    assert dist == [0]
    assert pred == [None]
    assert has_cycle is False


def test_three_vertices_no_edges():
    dist, pred, has_cycle = bellman_ford(3, [], source=0)
    assert dist == [0, math.inf, math.inf]
    assert pred == [None, None, None]
    assert has_cycle is False
