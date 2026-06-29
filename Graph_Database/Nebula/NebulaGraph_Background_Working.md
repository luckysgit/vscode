# NebulaGraph & nGQL Background Working

## Query Flow

``` text
Client
  │
  ▼
graphd
  │
  ▼
Parser
  │
  ▼
Semantic Analyzer
  │
  ▼
Query Planner
  │
  ▼
Execution Engine
  │
  ▼
metad
  │
  ▼
storaged
  │
  ▼
RocksDB
  │
  ▼
Results
```

## Background Working

1.  Client sends an nGQL query to **graphd**.
2.  The **Parser** checks syntax and builds an AST.
3.  The **Semantic Analyzer** validates tags, edges, properties, and
    variables.
4.  **graphd** requests schema and partition metadata from **metad**.
5.  The **Query Planner** creates an optimized execution plan.
6.  The **Execution Engine** sends requests to the required **storaged**
    nodes.
7.  **storaged** retrieves graph records from **RocksDB**.
8.  Results from multiple partitions are merged.
9.  The final result is returned to the client.

## Example

``` sql
MATCH (v:Person)-[:Friend]->(f)
WHERE v.name == "Alice"
RETURN f.name;
```

### Internal Execution

``` text
MATCH Query
    │
    ▼
Parse
    │
    ▼
Validate Schema
    │
    ▼
Find Partition
    │
    ▼
Read Vertex
    │
    ▼
Traverse Edge
    │
    ▼
Read Destination Vertex
    │
    ▼
Return Result
```

## Why RocksDB?

-   Persistent key-value storage
-   Fast reads and writes
-   Compression
-   Background compaction
-   Crash recovery

## Why Distributed?

-   Handles billions of vertices
-   Horizontal scaling
-   Fault tolerance
-   High availability
