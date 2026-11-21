"""Integration tests for CLI execution (T14, T17)."""

import json
import subprocess
import sys
from pathlib import Path


def run_cli(*args: str) -> tuple[int, str, str]:
    """Helper to run the CLI in a subprocess and return (returncode, stdout, stderr)."""
    proc = subprocess.run(
        [sys.executable, "-m", "shortest_paths"] + list(args),
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def test_t14_cli_invalid_input(tmp_path: Path):
    """T14: Invalid inputs produce exit code 1 and name the offending field."""
    # 1. Unknown source vertex
    ret, out, err = run_cli("sssp", "examples/graphs/negative_edges.json", "--source", "99")
    assert ret == 1
    assert "'source'" in err

    # 2. Duplicate vertices in JSON
    bad_json_1 = tmp_path / "bad_vertices.json"
    bad_json_1.write_text(json.dumps({"vertices": ["0", "0"], "edges": []}))
    ret, out, err = run_cli("sssp", str(bad_json_1), "--source", "0")
    assert ret == 1
    assert "'vertices'" in err

    # 3. Unknown edge destination
    bad_json_2 = tmp_path / "bad_edge.json"
    bad_json_2.write_text(
        json.dumps(
            {
                "vertices": ["0", "1"],
                "edges": [{"from": "0", "to": "2", "weight": 1}],
            }
        )
    )
    ret, out, err = run_cli("sssp", str(bad_json_2), "--source", "0")
    assert ret == 1
    assert "'edges'" in err

    # 4. Bool weight in JSON
    bad_json_3 = tmp_path / "bad_weight_bool.json"
    bad_json_3.write_text(
        json.dumps(
            {
                "vertices": ["0", "1"],
                "edges": [{"from": "0", "to": "1", "weight": True}],
            }
        )
    )
    ret, out, err = run_cli("sssp", str(bad_json_3), "--source", "0")
    assert ret == 1
    assert "weight" in err


def test_t17_three_example_files():
    """T17: Three example files give exit codes 0, 3, 0 and contain the expected statuses."""
    # 1. negative_edges.json -> exit code 0
    ret1, out1, err1 = run_cli("sssp", "examples/graphs/negative_edges.json", "--source", "0", "--json")
    assert ret1 == 0
    data1 = json.loads(out1)
    assert data1["negative_cycle_reachable"] is False
    assert data1["vertices"]["0"]["status"] == "finite"
    assert data1["vertices"]["0"]["distance"] == 0
    assert data1["vertices"]["1"]["status"] == "finite"
    assert data1["vertices"]["1"]["distance"] == 2
    assert data1["vertices"]["2"]["status"] == "finite"
    assert data1["vertices"]["2"]["distance"] == 5
    assert data1["vertices"]["3"]["status"] == "finite"
    assert data1["vertices"]["3"]["distance"] == 5
    assert data1["vertices"]["4"]["status"] == "finite"
    assert data1["vertices"]["4"]["distance"] == 7
    assert data1["vertices"]["5"]["status"] == "unreachable"
    assert data1["vertices"]["5"]["distance"] is None

    # 2. reachable_cycle.json -> exit code 3
    ret2, out2, err2 = run_cli("sssp", "examples/graphs/reachable_cycle.json", "--source", "0", "--json")
    assert ret2 == 3
    data2 = json.loads(out2)
    assert data2["negative_cycle_reachable"] is True
    assert data2["negative_cycle"] is not None
    assert data2["vertices"]["0"]["status"] == "finite"
    for v in ["1", "2", "3", "4"]:
        assert data2["vertices"][v]["status"] == "neg_infinite"
        assert data2["vertices"][v]["distance"] is None
    assert data2["vertices"]["5"]["status"] == "unreachable"
    assert data2["vertices"]["5"]["distance"] is None

    # 3. unreachable_cycle.json -> exit code 0 for SSSP from 0
    ret3, out3, err3 = run_cli("sssp", "examples/graphs/unreachable_cycle.json", "--source", "0", "--json")
    assert ret3 == 0
    data3 = json.loads(out3)
    assert data3["negative_cycle_reachable"] is False
    assert data3["vertices"]["0"]["status"] == "finite"
    assert data3["vertices"]["1"]["distance"] == 2
    assert data3["vertices"]["4"]["distance"] == 7
    assert data3["vertices"]["5"]["status"] == "unreachable"
    assert data3["vertices"]["6"]["status"] == "unreachable"
