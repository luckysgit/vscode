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