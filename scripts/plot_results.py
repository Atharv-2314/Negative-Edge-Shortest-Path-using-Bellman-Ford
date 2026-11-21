"""Generate log-log runtime vs V plots from benchmark CSV."""

from __future__ import annotations

import csv
import sys
from pathlib import Path
import matplotlib.pyplot as plt


def plot_results(csv_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            rows.append(line)

    reader = csv.DictReader(rows)
    data = list(reader)

    # Plot 1: SSSP Runtime vs V
    fig, ax = plt.subplots(figsize=(8, 5))
    for algo in ["bellman-ford", "dijkstra"]:
        for family in ["A", "B"]:
            if algo == "dijkstra" and family == "B":
                continue
            subset = [
                d for d in data
                if d["problem"] == "SSSP" and d["algorithm"] == algo and d["family"] == family and d["density"] == "dense"
            ]
            if subset:
                v_vals = [int(d["v"]) for d in subset]
                t_vals = [float(d["median_time_s"]) for d in subset]
                ax.plot(v_vals, t_vals, marker="o", label=f"{algo} (Fam {family}, dense)")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Number of vertices V")
    ax.set_ylabel("Median execution time (s)")
    ax.set_title("measured: SSSP Runtime vs V (Dense)")
    ax.legend()
    ax.grid(True, which="both", ls="--")
    sssp_plot = output_dir / "sssp_runtime_measured.png"
    plt.tight_layout()
    plt.savefig(sssp_plot, dpi=150)
    plt.close()
    print(f"Saved: {sssp_plot}")

    # Plot 2: APSP Runtime vs V
    fig, ax = plt.subplots(figsize=(8, 5))
    for algo in ["floyd-warshall", "johnson"]:
        subset = [
            d for d in data
            if d["problem"] == "APSP" and d["algorithm"] == algo and d["family"] == "A" and d["density"] == "dense"
        ]
        if subset:
            v_vals = [int(d["v"]) for d in subset]
            t_vals = [float(d["median_time_s"]) for d in subset]
            ax.plot(v_vals, t_vals, marker="s", label=f"{algo} (Fam A, dense)")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Number of vertices V")
    ax.set_ylabel("Median execution time (s)")
    ax.set_title("measured: APSP Runtime vs V (Dense)")
    ax.legend()
    ax.grid(True, which="both", ls="--")
    apsp_plot = output_dir / "apsp_runtime_measured.png"
    plt.tight_layout()
    plt.savefig(apsp_plot, dpi=150)
    plt.close()
    print(f"Saved: {apsp_plot}")


def main() -> None:
    results_dir = Path("results")
    csv_files = sorted(results_dir.glob("benchmark_*.csv"))
    if not csv_files:
        print("No benchmark CSV found in results/")
        sys.exit(1)

    latest_csv = csv_files[-1]
    print(f"Plotting results from {latest_csv}...")
    plot_results(latest_csv, results_dir / "figures")


if __name__ == "__main__":
    main()
