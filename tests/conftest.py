"""Pytest configuration and fixture loaders for graph tests."""

import json
from pathlib import Path
import pytest
from shortest_paths.graph import Graph

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_graph_from_json(filename: str) -> Graph:
    with open(FIXTURES_DIR / filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    edges = [(e["from"], e["to"], e["weight"]) for e in data["edges"]]
    return Graph(data["vertices"], edges)


@pytest.fixture
def g1_graph() -> Graph:
    return load_graph_from_json("g1.json")


@pytest.fixture
def g2_graph() -> Graph:
    return load_graph_from_json("g2.json")


@pytest.fixture
def g3_graph() -> Graph:
    return load_graph_from_json("g3.json")


@pytest.fixture
def t11_diamond_graph() -> Graph:
    return load_graph_from_json("t11_diamond.json")


@pytest.fixture
def t12_self_loop_graph() -> Graph:
    return load_graph_from_json("t12_self_loop.json")


@pytest.fixture
def t13_parallel_graph() -> Graph:
    return load_graph_from_json("t13_parallel.json")
