# Implementation Checklist — `shortest_paths`

## Rules for editing this file
- Tick a box (`- [x]`) **only** after real command output proves it has been completed.
- Never delete unticked items.
- Never tick a box without real command output backing it.

---

## Status Legend
- `[ ]` Not started / Incomplete
- `[x]` Completed and verified with command output

---

## Phase 0: Setup and Checklist
- [x] 0.1 Inspect: list all files, check `python --version` (>= 3.10), and run `git status`.
- [x] 0.2 Skeleton: initialize git repo, directory layout, `.gitignore`, `pyproject.toml`, and empty `src/shortest_paths/__init__.py`.
- [x] 0.3 Venv + install: create virtual environment, run `pip install -e ".[dev]"`, verify import and run pytest smoke test.
- [x] 0.4 Checklist: create `docs/implementation.md`.
- [x] 0.5 Initial commit: commit skeleton and checklist.
- [x] **Phase 0 Gate**: `pip install -e ".[dev]"` works, `python -m pytest -q` runs, checklist exists, and initial commit exists.

---

## Phase 1: Minimal Bellman-Ford
- [x] 1.1 pyproject/gitignore verified.
- [x] 1.2 `core.bellman_ford` implementation.
- [x] 1.3 `tests/test_core.py` (covering G₁, G₂, G₃, single vertex, empty edges).
- [x] 1.4 `scripts/run_demo.py` hard-coding G₁ and G₂.
- [x] **Phase 1 Gate**: G₁ gives `0, 2, 5, 5, 7, inf`; G₂ flags reachable negative cycle; G₃ flags none; single-vertex and no-edge pass.

---

## Phase 2: Result Model and Edge Cases
- [x] 2.1 Status / VertexResult / SSSPResult / exceptions (`GraphValidationError`, `NegativeWeightError`, `NegativeCycleError`).
- [x] 2.2 Graph representation and input validation.
- [ ] 2.3 n-th pass relaxation and $-\infty$ propagation via BFS to `NEG_INFINITE`.
- [ ] 2.4 Witness cycle extraction.
- [ ] 2.5 Path reconstruction for FINITE only; passes and relaxations counters.
- [ ] 2.6 Tests T2, T5, T7, T9–T14 pass.
- [ ] **Phase 2 Gate**: Tests T2, T5, T7, T9–T14 pass; every `NEG_INFINITE` vertex has `distance is None` and `path is None`; witness is a real closed walk with negative total weight.

---

## Phase 3: Modular Repository Architecture
- [ ] 3.1 Baseline test run recorded.
- [ ] 3.2 Move code to `graph.py`, `models.py`, `validation.py`.
- [ ] 3.3 Move `bellman_ford` to `algorithms/bellman_ford.py` and re-export public API.
- [ ] 3.4 Split tests into `tests/unit/` + add `conftest.py` and JSON fixtures.
- [ ] 3.5 Delete `core.py` and `tests/test_core.py`.
- [ ] 3.6 Behaviour-unchanged check and demo run.
- [ ] **Phase 3 Gate**: Identical test count and assertions; `from shortest_paths import bellman_ford` works.

---

## Phase 4: Comparison Algorithms
- [ ] 4.1 Add `APSPResult` in `models.py`.
- [ ] 4.2 `dijkstra` with negative-edge check first, `heapq` with lazy deletion, reusable core loop.
- [ ] 4.3 `floyd_warshall` with diagonal negative cycle detection, $-\infty$ pairs, next-hop paths.
- [ ] 4.4 `johnson` with super-source Bellman-Ford, reweighting $w'$, Dijkstra per source.
- [ ] 4.5 Registry in `algorithms/__init__.py`.
- [ ] 4.6 Unit tests for comparison algorithms (T1, T3, T4, T6, T8).
- [ ] 4.7 Cross-check tests T15/T16 with seeded random graphs.
- [ ] **Phase 4 Gate**: T1, T3, T4, T6, T8, T15, T16 pass; each algorithm has its own test file.

---

## Phase 5: Input Files and CLI
- [ ] 5.1 `io.load_graph` parser with exact type validation.
- [ ] 5.2 Example JSON files (`negative_edges.json`, `reachable_cycle.json`, `unreachable_cycle.json`).
- [ ] 5.3 `cli.py` and `__main__.py` with `sssp` and `apsp` subcommands, table and `--json` output.
- [ ] 5.4 Exit codes (0 success, 1 invalid input, 2 precondition violated, 3 negative cycle).
- [ ] 5.5 CLI integration tests T14/T17.
- [ ] 5.6 `README.md` Quick start section.
- [ ] 5.7 Update `scripts/run_demo.py` to use CLI code path.
- [ ] **Phase 5 Gate**: T14 and T17 pass; README quick-start works.

---

## Phase 6: Benchmarking (Optional)
- [ ] 6.1 Seeded graph generators (sparse, dense; families A and B).
- [ ] 6.2 SSSP benchmark grid (BF vs Dijkstra on A; BF only on B).
- [ ] 6.3 APSP benchmark grid (Floyd-Warshall vs Johnson on A and B).
- [ ] 6.4 CSV writer + CLI flags (`--quick`, `--sizes`, `--seed`).
- [ ] 6.5 Determinism check.
- [ ] 6.6 Plots generation (optional).
- [ ] **Phase 6 Gate**: Two runs with same seed give same relaxation counts; no algorithm timed on invalid preconditions.

---

## Phase 7: Documentation and CI
- [ ] 7.1 Full `README.md`.
- [ ] 7.2 `docs/architecture.md`.
- [ ] 7.3 `docs/algorithms.md`.
- [ ] 7.4 GitHub Actions workflow (`.github/workflows/tests.yml`).
- [ ] 7.5 Clean-clone verification and check for untracked artifacts.
- [ ] **Phase 7 Gate**: Clean-clone steps succeed as written; nothing generated is tracked.

---

## Phase 8: Final Audit and Demonstration
- [ ] 8.1 Full test suite run, both demo runs, and benchmark verification.
- [ ] 8.2 Audit code against report claims.
- [ ] 8.3 Distance `None` audit for non-FINITE vertices everywhere.
- [ ] 8.4 Demonstration checklist documented.
- [ ] 8.5 Unfinished/optional items list.
- [ ] **Phase 8 Gate**: All tests pass with real output; report and code agree; demonstration checklist verified.
