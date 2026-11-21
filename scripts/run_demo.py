"""Demo script running every example file through the CLI code path."""

from pathlib import Path
from shortest_paths.cli import main


def run_demo_cli() -> None:
    examples_dir = Path("examples/graphs")
    example_files = [
        "negative_edges.json",
        "reachable_cycle.json",
        "unreachable_cycle.json",
    ]

    for fname in example_files:
        fpath = str(examples_dir / fname)
        print("=" * 70)
        print(f"RUNNING CLI DEMO: {fname}")
        print("=" * 70)
        ret = main(["sssp", fpath, "--source", "0"])
        print(f"[Exit code: {ret}]\n")


if __name__ == "__main__":
    run_demo_cli()
