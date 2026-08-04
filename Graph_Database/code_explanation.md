# Graph Database Benchmark Code Architecture & Technical Guide

## 1. Project Structure & Code Layout

The pipeline is organized into modular Python scripts to ensure clean separation of concerns, reproducibility, and unbiased performance measurement across all evaluated graph engines:

```text
Graph_Database/
└── pipeline/
    ├── generate_data.py       # Generates synthetic vertices and edges (users.csv, follows.csv)
    ├── benchmark.py           # Core execution and metrics tracking framework
    ├── users.csv              # Synthetic node data (10,000 rows)
    ├── follows.csv            # Synthetic edge data (100,000 rows)
    ├── kuzu_pipeline.py       # KùzuDB ingestion & traversal benchmark
    ├── memgraph_pipeline.py   # Memgraph ingestion & traversal benchmark
    ├── neo4j_pipeline.py      # Neo4j ingestion & traversal benchmark
    ├── arango_pipeline.py     # ArangoDB ingestion & traversal benchmark
    └── falkordb_pipeline.py   # FalkorDB ingestion & traversal benchmark
```

---
## 2. Shared Utilities & Data Generation

### 2.1 Synthetic Data Generator (`generate_data.py`)

* **What:** Generates two standardized CSV files representing a synthetic social network graph.
* **How:** Uses standard Python library modules (`csv`, `random`) to construct discrete vertices and directed edges.
  * `users.csv`: Contains `id`, `name`, and `age` columns representing `:User` vertices.
  * `follows.csv`: Contains `source_id`, `target_id`, and `since` columns representing directed `-[:FOLLOWS]->` edges.
* **Why:** Using pre-generated, static CSV files guarantees every database engine ingests identical schema structures, field types, and entity counts (10,000 nodes, 100,000 edges), ensuring strict benchmark fairness.

### 2.2 Benchmarking Engine (`benchmark.py`)

* **What:** Provides a universal execution wrapper `measure_execution(func, *args, **kwargs)` used across all individual database pipeline scripts.
* **How:**
```python
import time
import psutil
os

def measure_execution(func, *args, **kwargs):
    process = psutil.Process(os.getpid())
    start_time = time.time()
    start_mem = process.memory_info().rss / (1024 * 1024)  # Resident Set Size in MB
    
    result = func(*args, **kwargs)
    
    end_time = time.time()
    end_mem = process.memory_info().rss / (1024 * 1024)
    
    return {
        "result": result,
        "execution_time_sec": round(end_time - start_time, 4),
        "memory_used_mb": round(end_mem - start_mem, 2)
    }
```
* **Why:** High-level profilers introduce runtime overhead. By inspecting process Resident Set Size (RSS) and system time immediately before and after function execution, we record client-side wall-clock execution time and RAM differential without polluting the measurement environment.

---
## 3. Database Pipeline Implementation Details

### 3.1 KùzuDB Pipeline (`kuzu_pipeline.py`)

* **Architecture:** Embedded / In-Process columnar graph database.
* **Ingestion Strategy:** Native bulk CSV copy.
```python
import kuzu

db = kuzu.Database('./kuzu_db')
conn = kuzu.Connection(db)

# Schema Setup
conn.execute("CREATE NODE TABLE User(id INT64, name STRING, age INT64, PRIMARY KEY (id))")
conn.execute("CREATE REL TABLE FOLLOWS(FROM User TO User, since INT64)")

# Ingestion via native COPY FROM
conn.execute("COPY User FROM 'users.csv'")
conn.execute("COPY FOLLOWS FROM 'follows.csv'")
```
* **Query Implementation:**
```python
conn.execute("MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User) RETURN c.name")
```
* **Why this design:** KùzuDB runs directly within the Python process memory space. Native `COPY FROM` directly parses CSV files into vectorized columnar chunks without IPC, network serialization, or socket serialization penalties.

---
### 3.2 Neo4j Pipeline (`neo4j_pipeline.py`)

* **Architecture:** Client-Server disk-backed native graph database.
* **Ingestion Strategy:** Transaction-batched Cypher `LOAD CSV`.
```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

with driver.session() as session:
    # Primary Index Creation
    session.run("CREATE INDEX user_id_index IF NOT EXISTS FOR (u:User) ON (u.id)")

    # Node Import
    session.run('''
        LOAD CSV WITH HEADERS FROM 'file:///users.csv' AS row
        CREATE (:User {id: toInteger(row.id), name: row.name, age: toInteger(row.age)})
    ''')

    # Edge Import
    session.run('''
        LOAD CSV WITH HEADERS FROM 'file:///follows.csv' AS row
        MATCH (u1:User {id: toInteger(row.source_id)})
        MATCH (u2:User {id: toInteger(row.target_id)})
        CREATE (u1)-[:FOLLOWS {since: toInteger(row.since)}]->(u2)
    ''')
```
* **Query Implementation:**
```python
session.run("MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User) RETURN c.name")
```
* **Why this design:** Mounts the current working directory into `/var/lib/neo4j/import` inside the Docker container. Using `file:///` paths allows Neo4j's internal engine to process CSV streams directly inside server memory, avoiding sending 110,000 string statements over the Bolt wire protocol.

---
### 3.3 Memgraph Pipeline (`memgraph_pipeline.py`)

* **Architecture:** Client-Server fully in-memory Cypher-compliant database.
* **Ingestion Strategy:** Parameterized driver execution with explicit transactions.
```python
import mgclient

conn = mgclient.connect(host='127.0.0.1', port=7688)
conn.autocommit = True
cursor = conn.cursor()

cursor.execute("CREATE INDEX ON :User(id);")
conn.autocommit = False

# Transactionally committed batch iteration
for row in user_reader:
    cursor.execute("CREATE (:User {id: %s, name: '%s', age: %s});" % (...))
conn.commit()
```
* **Query Implementation:**
```python
cursor.execute("MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User) RETURN c.name;")
```
* **Why this design:** Uses `mgclient` (C-bindings client) over port `7688`. Enforcing explicit transaction control (`autocommit = False`) aggregates write operations into larger transaction blocks rather than committing individual micro-transactions to disk log per statement.

---
### 3.4 ArangoDB Pipeline (`arango_pipeline.py`)

* **Architecture:** Client-Server multi-model (Document + Graph) engine.
* **Ingestion Strategy:** Bulk document collection insertions via batch arrays.
```python
from arango import ArangoClient

client = ArangoClient(hosts='http://localhost:8529')
db = client.db('_system', username='root', password='')

graph = db.create_graph('social_graph')
users = graph.create_vertex_collection('users')
follows = graph.create_edge_definition(
    edge_collection='follows',
    from_vertex_collections=['users'],
    to_vertex_collections=['users']
)

# Primary Index
users.add_persistent_index(fields=['id'])

# Bulk array insertion
users.insert_many(user_docs)
follows.insert_many(edge_docs)
```
* **Query Implementation:**
```python
aql_query = """
FOR v, e, p IN 2..2 OUTBOUND 'users/100' GRAPH 'social_graph'
    RETURN v.name
"""
db.aql.execute(aql_query)
```
* **Why this design:** ArangoDB treats graph relationships as edge documents (`_from`, `_to`). Using `insert_many()` transmits JSON batches over HTTP/REST rather than sending single-document HTTP POST requests, significantly improving bulk write efficiency.

---
### 3.5 FalkorDB Pipeline (`falkordb_pipeline.py`)

* **Architecture:** Client-Server low-latency Redis-based graph database engine.
* **Ingestion Strategy:** Parameterized Cypher query batching with `UNWIND`.
```python
from falkordb import FalkorDB

db = FalkorDB(host='localhost', port=6379)
g = db.select_graph('social_graph')
g.query("CREATE INDEX FOR (u:User) ON (u.id)")

# Unwound Parameter Batching (500 items/chunk)
query = """
UNWIND $batch AS row
MATCH (u1:User {id: row.s}), (u2:User {id: row.t})
CREATE (u1)-[:FOLLOWS {since: row.since}]->(u2)
"""
g.query(query, {"batch": edge_batch})
```
* **Query Implementation:**
```python
query = "MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User) RETURN c.name"
g.query(query)
```
* **Why this design:** FalkorDB executes graph operations directly over Redis RESP protocol sockets. Unwinding parameterized array payloads reduces Redis command network round-trips by 500x compared to single-statement execution loops.

---
## 4. Execution & Orchestration Summary

Each client-server engine is isolated inside containerized Docker runtimes with dedicated host port mappings:
* **Neo4j:** `7687` (Bolt)
* **Memgraph:** `7688` (Bolt)
* **ArangoDB:** `8529` (HTTP/AQL)
* **FalkorDB:** `6379` (Redis RESP)
* **KùzuDB:** Embedded in-process C++ library loaded via Python bindings.

This decoupled architecture isolates resource consumption, prevents state leakage between database runs, and allows repeatable, deterministic evaluation of graph query execution speeds.