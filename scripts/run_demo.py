"""Demo script running Bellman-Ford on hard-coded graphs G1 and G2."""

from shortest_paths.core import bellman_ford, Graph


def main() -> None:
    g1_edges = [
        (0, 1, 4), (0, 2, 5), (2, 1, -3),
        (1, 3, 3), (2, 3, 4), (3, 4, 2), (1, 4, 6),
    ]
    g1 = Graph(list(range(6)), g1_edges)
    result1 = bellman_ford(g1, source=0)
    print("Graph G1 (no negative cycle):")
    for label in g1.labels:
        vr = result1.vertices[label]
        print(f"  vertex {label}: {vr.status.name}  distance={vr.distance}")
    print(f"  Reachable negative cycle: {result1.negative_cycle_reachable}")

    g2_edges = g1_edges + [(3, 2, -6)]
    g2 = Graph(list(range(6)), g2_edges)
    result2 = bellman_ford(g2, source=0)
    print("\nGraph G2 (reachable negative cycle):")
    for label in g2.labels:
        vr = result2.vertices[label]
        print(f"  vertex {label}: {vr.status.name}  distance={vr.distance}")
    print(f"  Reachable negative cycle: {result2.negative_cycle_reachable}")


if __name__ == "__main__":
    main()
