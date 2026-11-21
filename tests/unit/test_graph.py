"""Unit tests for Graph class representation and properties."""

from shortest_paths.graph import Graph


def test_t13_parallel_graph_properties(t13_parallel_graph):
    """Test graph vertex counts, labels, and indices for parallel edge fixture."""
    assert t13_parallel_graph.n == 2
    assert t13_parallel_graph.labels == [0, 1]
    assert t13_parallel_graph.label(0) == 0
    assert t13_parallel_graph.index_of(1) == 1
    assert len(t13_parallel_graph.index_edges) == 2
