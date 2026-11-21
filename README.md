# `shortest_paths`

A robust, exact-arithmetic Python library and CLI for Single-Source Shortest Paths (SSSP) and All-Pairs Shortest Paths (APSP) on directed weighted graphs with negative edge weights and cycle detection.

---

## Algorithms

| Algorithm | Variant | Precondition | Time Complexity | Space Complexity |
|---|---|---|---|---|
| **Bellman-Ford** | SSSP | Arbitrary directed graph, exact weights (`int` or `Fraction`). | $O(V \cdot E)$ | $O(V)$ |
| **Dijkstra** | SSSP | Non-negative edge weights only ($w \ge 0$). Refuses negative weights. | $O((V + E) \log V)$ | $O(V)$ |
| **Floyd-Warshall** | APSP | Arbitrary directed graph, exact weights (`int` or `Fraction`). | $O(V^3)$ | $O(V^2)$ |
| **Johnson's** | APSP | Arbitrary directed graph; refuses graphs with negative cycles. | $O(V \cdot E + V^2 \log V)$ | $O(V^2)$ |

---

## Result Contract
Every vertex result is strictly one of:
- `FINITE`: has exact `distance` (`int` or `Fraction`) and a non-empty `path` list.
- `UNREACHABLE`: `distance` is `None`, `path` is `None`.
- `NEG_INFINITE`: `distance` is `None`, `path` is `None`.

Undefined distances are **never** returned as arbitrary numbers or $\pm\infty$ floats.

---

## Requirements
- Python >= 3.10
- Standard library only inside `shortest_paths` package.

---

## Setup & Installation

Create and activate a virtual environment, then install editable with developer extras:

```bash
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -e ".[dev]"
```

---

## Quick Start & Demo Commands

### SSSP (Single-Source Shortest Paths)
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

### Negative Cycle Detection
```bash
python -m shortest_paths sssp examples/graphs/reachable_cycle.json --source 0
```

Sample output:
```text
Algorithm: bellman-ford
Source:    0
Reachable negative cycle: True
Witness cycle: 3 -> 2 -> 1 -> 3

Vertex     Status          Distance        Path
-----------------------------------------------------------------
0          finite          0               0
1          neg_infinite    -               -
2          neg_infinite    -               -
3          neg_infinite    -               -
4          neg_infinite    -               -
5          unreachable     -               -
```

### APSP (All-Pairs Shortest Paths)
```bash
python -m shortest_paths apsp examples/graphs/negative_edges.json --algorithm johnson
```

### Run Demonstration Script
```bash
python scripts/run_demo.py
```

### Run Benchmarks
```bash
python scripts/benchmark.py --quick
```

---

## Testing
Run the test suite using `pytest`:

```bash
python -m pytest -q
```

---

## JSON Input Format
Input graph files must contain valid JSON:
```json
{
  "directed": true,
  "vertices": ["0", "1", "2"],
  "edges": [
    {"from": "0", "to": "1", "weight": 4},
    {"from": "1", "to": "2", "weight": "-1.5"}
  ]
}
```
- Vertex labels must be unique hashable identifiers (strings, integers).
- Weights are integers or decimal/fraction strings (e.g. `"-1.5"` or `"3/4"` parsed as exact `Fraction`).
- Raw JSON floating point numbers are strictly rejected unless explicit `--allow-float` is supported.

---

## Known Limitations
1. **SSSP Negative Cycle Reachability**: Bellman-Ford flags only negative cycles reachable from the specified `source`. Cycles isolated in unreachable graph components are not flagged by SSSP (use APSP via Floyd-Warshall or Johnson for global detection).
2. **Exact Weights**: Weights must be discrete integers or exact rational fractions (`fractions.Fraction`). Inexact floating point arithmetic is intentionally unsupported to prevent rounding drift in relaxation comparisons.
3. **Static Graphs**: Algorithms operate on static in-memory graphs. Dynamic edge insertions or streaming updates require re-running the solver.

---

## Repository Map
```text
DAA_Project/
├── .github/workflows/       # Continuous integration workflows
├── docs/                    # Design, architecture, and algorithm specs
│   ├── algorithms.md        # Detailed pseudocode and preconditions
│   ├── architecture.md      # Data flow and module dependency graph
│   └── implementation.md    # Living milestone checklist
├── examples/graphs/         # Example JSON graph fixtures (G1, G2, G3)
├── results/                 # Benchmark output CSVs and figures
├── scripts/                 # Runner and benchmarking scripts
│   ├── benchmark.py         # Empirical performance benchmarking
│   ├── plot_results.py      # Runtime log-log curve generator
│   └── run_demo.py          # Demo script driving CLI code path
├── src/shortest_paths/      # Core package library
│   ├── algorithms/          # Solvers (Bellman-Ford, Dijkstra, FW, Johnson)
│   ├── cli.py               # Command-line interface
│   ├── graph.py             # Graph data structure & index mapping
│   ├── io.py                # Graph JSON loading & validation
│   ├── models.py            # Result dataclasses & exceptions
│   └── validation.py        # Input weight validators
└── tests/                   # Pytest test suite (unit, integration, fixtures)
```
