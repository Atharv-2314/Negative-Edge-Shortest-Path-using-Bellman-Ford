# Algorithmic Specifications & Pseudocode

This document defines the mathematical foundations, pseudocode, and invariants for all four shortest path solvers implemented in `shortest_paths`.

---

## 1. Bellman-Ford (Single-Source Shortest Paths)

### Precondition
Arbitrary directed graph $G = (V, E)$ with edge weights $w(u, v) \in \mathbb{Z} \cup \mathbb{Q}$.

### Invariant
After pass $i \in \{1, \dots, V - 1\}$, for every vertex $v \in V$, $\text{dist}[v]$ equals the minimum weight of any directed path from source $s$ to $v$ containing at most $i$ edges.

### Pseudocode
```text
Algorithm Bellman-Ford(G, source):
    dist[v] = inf for all v in V
    pred[v] = None for all v in V
    dist[source] = 0

    // Passes 1 through V - 1
    for pass from 1 to V - 1:
        changed = False
        for each edge (u, v, w) in E:
            if dist[u] != inf and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
                changed = True
        if not changed:
            break

    // Detection pass (the V-th pass)
    seed = empty set
    for each edge (u, v, w) in E:
        if dist[u] != inf and dist[u] + w < dist[v]:
            dist[v] = dist[u] + w
            pred[v] = u
            seed.add(v)

    // Propagate -inf via BFS
    neg_inf_set = seed
    queue = FIFO_Queue(seed)
    while queue is not empty:
        u = queue.pop()
        for each edge (u, v) in out_edges(u):
            if v not in neg_inf_set:
                neg_inf_set.add(v)
                queue.push(v)

    // Witness cycle extraction (if seed is non-empty)
    if seed is not empty:
        x = any vertex in seed
        repeat V times: x = pred[x]
        cycle = trace pred from x until x repeats
        witness = reverse(cycle) + [first_vertex]

    return SSSPResult(dist, pred, neg_inf_set, witness)
```

---

## 2. Dijkstra (Single-Source Shortest Paths)

### Precondition
All edge weights must be strictly non-negative: $\forall (u, v) \in E, w(u, v) \ge 0$. If any negative edge exists, `NegativeWeightError` is raised immediately before execution.

### Pseudocode
```text
Algorithm Dijkstra(G, source):
    for each edge (u, v, w) in E:
        if w < 0:
            raise NegativeWeightError((u, v, w))

    dist[v] = inf for all v in V
    pred[v] = None for all v in V
    dist[source] = 0

    min_heap = [(0, source)]

    while min_heap is not empty:
        (d_u, u) = heappop(min_heap)
        if d_u > dist[u]:
            continue  // Lazy deletion

        for each (v, w) in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
                heappush(min_heap, (dist[v], v))

    return SSSPResult(dist, pred, passes=0)
```

---

## 3. Floyd-Warshall (All-Pairs Shortest Paths)

### Precondition
Arbitrary directed graph $G = (V, E)$ with edge weights $w(u, v) \in \mathbb{Z} \cup \mathbb{Q}$. Never raises on negative cycles.

### Pseudocode
```text
Algorithm Floyd-Warshall(G):
    D[i][j] = inf for all i, j in V
    next_hop[i][j] = None for all i, j in V
    for i in V:
        D[i][i] = 0
        next_hop[i][i] = i

    for each (u, v, w) in E (taking minimum over parallel edges):
        if w < D[u][v]:
            D[u][v] = w
            next_hop[u][v] = v

    // Dynamic programming triple loop
    for k in V:
        for i in V:
            if D[i][k] == inf: continue
            for j in V:
                if D[k][j] == inf: continue
                if D[i][k] + D[k][j] < D[i][j]:
                    D[i][j] = D[i][k] + D[k][j]
                    next_hop[i][j] = next_hop[i][k]

    // Diagonal negative cycle detection
    neg_cycle_vertices = {i in V : D[i][i] < 0}

    // -inf propagation for pairs
    neg_inf_pairs = empty set
    for i in V:
        for j in V:
            for k in neg_cycle_vertices:
                if D[i][k] < inf and D[k][j] < inf:
                    neg_inf_pairs.add((i, j))
                    break

    return APSPResult(D, next_hop, neg_inf_pairs, neg_cycle_vertices)
```

---

## 4. Johnson's Algorithm (All-Pairs Shortest Paths)

### Precondition
Arbitrary directed graph $G = (V, E)$. Raises `NegativeCycleError(witness)` if any negative cycle exists in the entire graph.

### Pseudocode
```text
Algorithm Johnson(G):
    Add super-source s with directed edges (s, v) of weight 0 to all v in V
    Run Bellman-Ford from s:
        if negative cycle detected:
            raise NegativeCycleError(witness)

    h[v] = dist_BF(s, v) for all v in V

    // Reweight edges
    for each edge (u, v) in E:
        w'(u, v) = w(u, v) + h[u] - h[v]
        assert w'(u, v) >= 0

    // Dijkstra from every vertex
    for each u in V:
        Run Dijkstra core from u using w'
        for each v in V:
            if d'[u][v] != inf:
                real_d[u][v] = d'[u][v] - h[u] + h[v]
            else:
                real_d[u][v] = inf

    return APSPResult(real_d, paths)
```
