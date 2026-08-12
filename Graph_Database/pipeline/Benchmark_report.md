# Graph Database Benchmark Report

## Dataset Specs

* **Vertices (`users.csv`):** 10,000 nodes
* **Edges (`follows.csv`):** 100,000 relationships
* **Total Scale:** 110,000 entities (~4 MB CSV file size)

---

## Results Summary

| Graph Database | Architecture | Ingestion Time | 2-Hop Query Time |
| --- | --- | --- | --- |
| **KùzuDB** | Embedded / In-Memory | **~1.0s** | **0.0020s** ⚡ *(Fastest)* |
| **Memgraph** | Client-Server / In-Memory | 182.20s | **0.0146s** |
| **ArangoDB** | Client-Server / Multi-Model | 30.72s | **0.0392s** |
| **FalkorDB** | Client-Server / Redis Engine | 50.71s | **0.0672s** |
| **Neo4j** | Client-Server / Disk-Based | **26.04s** | 0.7447s |

---

## Direct Takeaways

1. **Fastest Traversals:** **KùzuDB** and **Memgraph** win query speeds because data connections are held directly in RAM instead of reading from disk.
2. **Fastest Ingestion:** **KùzuDB** leads ingestion by running in-process inside Python, eliminating network traffic. **Neo4j** leads client-server ingestion (26s) using native Docker file loading.
3. **When to use what:**
* **KùzuDB:** Best for local Python apps, AI/RAG workflows, and embedded speed.
* **Memgraph:** Best for high-speed, real-time in-memory graph servers.
* **Neo4j:** Best for large, disk-backed enterprise graphs that exceed system memory.

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# NEW Result

## 1. Dataset & Benchmark Specifications

* **Vertices (`users.csv`):** 10,000 nodes (~50 attributes per node)
* **Edges (`follows.csv`):** 100,000 directed relationships
* **Total Scale:** 110,000 graph entities (~4 MB total CSV footprint)
* **Node Density:** Wide-node schema testing high-property memory overhead and attribute filtering

---

#| Engine | Architecture | Ingestion (s) | Q1: Point Lookup (s) | Q2: 2-Hop Traversal (s) | Q3: 3-Hop Filtered (s) | Q4: Complex Agg (s) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NebulaGraph** | Distributed C++ | **1.43** | 0.0102 (10.2 ms) | **0.0010** (1.0 ms) | **0.0008** (0.8 ms) | **0.0009** (0.9 ms) |
| **KùzuDB** | Embedded C++ | 1.85 | 0.6921 | 0.0138 (13.8 ms) | 0.0344 (34.4 ms) | 0.0207 (20.7 ms) |
| **ArangoDB** | Multi-Model Server | 4.54 | **0.0031** (3.1 ms) | 0.0068 (6.8 ms) | 0.0447 (44.7 ms) | 0.0080 (8.0 ms) |
| **Neo4j** | Native Server (Java) | 6.61 | 1.8497 | 0.2647 (264.7 ms) | 0.5144 (514.4 ms) | 0.1981 (198.1 ms) |
| **Memgraph** | In-Memory C++ | 40.67 | 0.0088 (8.8 ms) | 0.0031 (3.1 ms) | 0.0227 (22.7 ms) | 0.0123 (12.3 ms) |
| **FalkorDB** | In-Memory Redis | 166.56 | 0.0040 (4.0 ms) | 0.0278 (27.8 ms) | 0.0226 (22.6 ms) | 0.0020 (2.0 ms) |

---

## 2. Key Architectural Takeaways

1. **Overall Winner:** **NebulaGraph** leads both ingestion (1.43s) and multi-hop graph traversal speeds (~0.8–1.0 ms) through native C++ storage pushdown filters and compiled nGQL execution trees.
2. **Embedded Efficiency:** **KùzuDB** remains the top choice for zero-dependency local Python applications, offering fast vectorized CSV ingestion without server overhead.
3. **Multi-Model Workloads:** **ArangoDB** provides fast point lookups (3.1 ms) and versatile document/graph query capabilities.
4. **Enterprise Memory Usage:** **Neo4j** persists wide-node schemas reliably on disk, making it ideal for graphs exceeding available physical RAM.

## 3. Detailed Explanation of Terms & Metrics

### Architectural Classifications

* **Embedded / In-Process (KùzuDB):** Runs directly inside the host application process binary (Python). Eliminates network socket serialization, HTTP/Bolt IPC overhead, and client-server latency.
* **Multi-Model Server (ArangoDB):** Document-graph hybrid database server. Stores entities as JSON-like documents with specialized edge collection indices for path traversals.
* **In-Memory Graph Server (Memgraph & FalkorDB):** Holds graph topology and wide-node property sets entirely in system RAM. Uses direct C++ memory pointer-swizzling (Memgraph) or sparse matrices (FalkorDB) for rapid path expansions.
* **Disk-Backed Enterprise Graph (Neo4j):** Persistent Java-based native graph store. Writes nodes and relationships to disk storage with JVM page caching to handle graph structures exceeding physical memory.

### Performance Metrics & Query Levels

* **Ingestion Time (s):** Wall-clock duration required to parse raw CSV files, allocate schemas, generate primary key indices, and commit all 110,000 nodes/edges into database storage.
* **Q1: Point Lookup (s):** Execution speed to locate and hydrate a single node by its primary key (`MATCH (u:User {id: 100}) RETURN u`). Evaluates index lookup overhead and property deserialization.
* **Q2: 2-Hop Traversal (s):** Two-step relational graph path expansion (`A -> B -> C`). Measures raw pointer-chasing latency across node relationships.
* **Q3: 3-Hop Filtered (s):** Deep three-step expansion combined with node property filtering (`A -> B -> C -> D WHERE d.age > 30`). Tests multi-hop graph expansion paired with property verification.
* **Q4: Complex Aggregation (s):** Multi-hop traversal combined with analytical grouping, sorting, and top-N limits (`COUNT()`, `ORDER BY DESC`, `LIMIT 10`). Evaluates query processing pipelines under analytical workloads.

---

## 4. Key Engineering Takeaways

1. **Ingestion Winner:** **KùzuDB** (1.85s) leads bulk ingestion through its vectorized C++ direct-disk loader, bypassing network transport bottlenecks.
2. **Traversal Performance:** **Memgraph** (3.1 ms for 2-hop) and **FalkorDB** (2.0 ms for Q4 aggregation) deliver top traversal speeds due to pure in-memory pointer structures.
3. **Multi-Model Versatility:** **ArangoDB** delivers balanced performance, yielding sub-millisecond point lookups (3.1 ms) and fast multi-hop traversals (6.8 ms).
4. **Engine Selection Guidelines:**
   * **KùzuDB:** Ideal for embedded Python apps, AI/RAG workflows, local analytics, and fast prototyping.
   * **Memgraph / FalkorDB:** Best for real-time streaming, high-throughput microservices, and sub-50ms analytics.
   * **ArangoDB:** Best for multi-model workloads requiring JSON document store capabilities alongside graph queries.
   * **Neo4j:** Best for enterprise systems requiring ACID compliance and graphs larger than physical RAM.
