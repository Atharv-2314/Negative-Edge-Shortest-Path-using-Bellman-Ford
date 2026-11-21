"""Demo script running Bellman-Ford on hard-coded graphs G1 and G2."""

from shortest_paths.core import bellman_ford


def main() -> None:
    g1_edges = [
        (0, 1, 4),
        (0, 2, 5),
        (2, 1, -3),
        (1, 3, 3),
        (2, 3, 4),
        (3, 4, 2),
        (1, 4, 6),
    ]
    dist_g1, pred_g1, cycle_g1 = bellman_ford(6, g1_edges, source=0)
    print("Graph G1 (no negative cycle):")
    print(f"  Distances: {dist_g1}")
    print(f"  Reachable negative cycle: {cycle_g1}")

    g2_edges = g1_edges + [(3, 2, -6)]
    dist_g2, pred_g2, cycle_g2 = bellman_ford(6, g2_edges, source=0)
    print("\nGraph G2 (reachable negative cycle):")
    print(f"  Distances: {dist_g2}")
    print(f"  Reachable negative cycle: {cycle_g2}")


if __name__ == "__main__":
    main()
