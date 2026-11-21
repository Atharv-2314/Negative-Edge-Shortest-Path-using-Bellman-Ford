# Shortest Paths

## Quick start

### Requirements
- Python >= 3.10

### Installation
Create a virtual environment and install the package in editable mode with development dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Running SSSP
Compute Single-Source Shortest Paths using Bellman-Ford (default) or Dijkstra:

```bash
python -m shortest_paths sssp examples/graphs/negative_edges.json --source 0
```

Sample output:
```text
Algorithm: bellman-ford
Source:    0
Reachable negative cycle: False

Vertex     Status          Distance        Path
-----------------------------------------------------------------
0          finite          0               0
1          finite          2               0 -> 2 -> 1
2          finite          5               0 -> 2
3          finite          5               0 -> 2 -> 1 -> 3
4          finite          7               0 -> 2 -> 1 -> 3 -> 4
5          unreachable     -               -
```

Detecting reachable negative cycles:
```bash
python -m shortest_paths sssp examples/graphs/reachable_cycle.json --source 0
```

### Running APSP
Compute All-Pairs Shortest Paths using Floyd-Warshall or Johnson:

```bash
python -m shortest_paths apsp examples/graphs/negative_edges.json --algorithm johnson
```

### Running Tests
Execute the full pytest suite:

```bash
python -m pytest -q
```
