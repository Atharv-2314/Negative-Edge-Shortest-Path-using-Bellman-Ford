"""Unit tests for Johnson's algorithm (T1, T4, T6, T8)."""

import pytest
from shortest_paths.algorithms.bellman_ford import bellman_ford
from shortest_paths.algorithms.johnson import johnson
from shortest_paths.graph import Graph
from shortest_paths.models import NegativeCycleError, Status


def test_t1_johnson():
    """T1: 0->1(2), 0->2(6), 1->2(3), 2->3(1): distances 0, 2, 5, 6 from source 0."""
    edges = [
        (0, 1, 2),
        (0, 2, 6),
        (1, 2, 3),
        (2, 3, 1),
    ]
    g = Graph([0, 1, 2, 3], edges)
    res = johnson(g)
    assert res.pairs[(0, 0)].distance == 0
    assert res.pairs[(0, 1)].distance == 2
    assert res.pairs[(0, 2)].distance == 5
    assert res.pairs[(0, 3)].distance == 6


def test_t4_g1_johnson(g1_graph):
    """T4: G1 Johnson row 0 equals T2; Johnson potentials h = (0, -3, 0, 0, 0, 0)."""
    # Check Johnson potentials by running bellman_ford with super-source
    super_src = "s"
    ext_v = list(g1_graph.labels) + [super_src]
    ext_e = [(g1_graph.label(u), g1_graph.label(v), w) for u, v, w in g1_graph.index_edges] + [
        (super_src, v, 0) for v in g1_graph.labels
    ]
    ext_g = Graph(ext_v, ext_e)
    bf_super = bellman_ford(ext_g, super_src)
    h = [bf_super.vertices[v].distance for v in g1_graph.labels]
    assert h == [0, -3, 0, 0, 0, 0]

    res = johnson(g1_graph)
    assert res.has_negative_cycle is False
    assert res.pairs[(0, 0)].distance == 0
    assert res.pairs[(0, 1)].distance == 2
    assert res.pairs[(0, 2)].distance == 5
    assert res.pairs[(0, 3)].distance == 5
    assert res.pairs[(0, 4)].distance == 7
    assert res.pairs[(0, 5)].status == Status.UNREACHABLE


def test_t6_g2_johnson(g2_graph):
    """T6: G2: Johnson raises NegativeCycleError."""
    with pytest.raises(NegativeCycleError):
        johnson(g2_graph)


def test_t8_g3_johnson(g3_graph):
    """T8: G3: Johnson raises NegativeCycleError (global detection via super-source)."""
    with pytest.raises(NegativeCycleError):
        johnson(g3_graph)
