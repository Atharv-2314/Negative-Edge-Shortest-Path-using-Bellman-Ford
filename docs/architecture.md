# System Architecture & Data Flow

This document details the module dependencies, data models, and processing pipelines in `shortest_paths`.

---

## 1. Module Dependency Hierarchy

The architecture maintains strict layered separation. In particular:
- `models.py` defines core data structures without importing algorithm or graph modules.
- `validation.py` provides standalone type-checking functions.
- `graph.py` maps arbitrary hashable vertex labels to contiguous integer indices $0 \le i < V$ and validates input structure.
- `algorithms/` contains pure solvers consuming `Graph` and producing `SSSPResult` or `APSPResult`.
- `io.py` handles JSON serialization and constructs `Graph` instances.
- `cli.py` coordinates user flags, invokes algorithms, and prints human-readable or machine-readable outputs.

```text
                      [ CLI / Scripts ]
                              |
                     +--------+--------+
                     |                 |
                 [ io.py ]        [ algorithms/ ]
                     |            /   |     |    \
                     |   bellman_ford dijkstra fw johnson
                     v          \     |     |    /
                 [ graph.py ]    v    v     v   v
                     |          [ models.py ]
                     v                ^
              [ validation.py ]-------+
```

---

## 2. End-to-End Data Flow

```text
JSON file / Input tuples
         |
         v
    [ io.load_graph ]
         |
         v
      [ Graph ]
      - Validates unique vertex labels
      - Validates integer or Fraction weights
      - Maps labels <-> 0..V-1 integer indices
         |
         +-------------------------------------+
         |                                     |
         v                                     v
   [ SSSP Algorithms ]                   [ APSP Algorithms ]
   - bellman_ford                        - floyd_warshall
   - dijkstra                            - johnson
         |                                     |
         v                                     v
   [ SSSPResult ]                        [ APSPResult ]
   - vertices: {label: VertexResult}     - pairs: {(u, v): VertexResult}
   - negative_cycle_reachable            - has_negative_cycle
   - negative_cycle witness              - negative_cycle_vertices
         |                                     |
         +------------------+------------------+
                            |
                            v
               [ Result Contract Verification ]
               - Status.FINITE: distance is int/Fraction, path is non-empty list
               - Status.UNREACHABLE: distance is None, path is None
               - Status.NEG_INFINITE: distance is None, path is None
                            |
                            v
                    [ Formatter / CLI ]
               - Aligned tables or JSON output
               - Exit codes (0: ok, 1: invalid, 2: precondition, 3: cycle)
```

---

## 3. Core Invariants & Boundaries

1. **Precondition Safety**: Algorithms enforce validity contracts prior to computation:
   - `dijkstra` inspects edges in $O(E)$ time for any $w < 0$ and immediately raises `NegativeWeightError`.
   - `johnson` raises `NegativeCycleError(witness)` upon cycle detection from the super-source.
2. **Result Invariant**: Undefined distances are represented strictly as `None`. No numerical sentinel (such as $\infty$ or arbitrary large numbers) is ever exposed through public APIs or CLI output.
