# NebulaGraph System Design and nGQL Background

## High-Level Architecture

``` text
Client Application
        │
        ▼
graphd (Graph Service)
        │
 ├── Parser
 ├── Semantic Analyzer
 ├── Query Planner
 └── Execution Engine
        │
        ▼
metad (Metadata Service)
        │
        ▼
storaged (Storage Service)
        │
 ├── Partition 1
 ├── Partition 2
 └── Partition N
        │
        ▼
RocksDB
```

## Components

### graphd

-   Accepts nGQL queries
-   Parses and validates syntax
-   Builds execution plans
-   Coordinates distributed execution

### metad

Stores: - Spaces - Tags - Edge Types - Indexes - Users & Roles -
Partition mapping - Cluster metadata

### storaged

Stores: - Vertices - Edges - Properties

Runs on multiple machines for horizontal scaling.

### RocksDB

NebulaGraph stores graph records as key-value pairs in RocksDB.

Example:

``` text
Key: VertexID
Value:
  name=Alice
  age=30
```

## Query Lifecycle

``` text
nGQL
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
graphd
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
Result
```

## Example

``` sql
MATCH (v:Person)-[:Friend]->(f)
WHERE v.name == "Alice"
RETURN f.name;
```

Execution:

1.  Client sends query to graphd.
2.  Parser builds an AST.
3.  Semantic analyzer validates schema.
4.  graphd requests metadata from metad.
5.  Query planner selects indexes and partitions.
6.  graphd contacts relevant storaged nodes.
7.  storaged reads data from RocksDB.
8.  Results are merged and returned.

## Why This Architecture?

  Component          Why it Exists
  ------------------ -----------------------------------------
  graphd             Separates query processing from storage
  metad              Centralizes schema and cluster metadata
  storaged           Enables distributed graph storage
  Partitions         Scale data across many servers
  RocksDB            Fast persistent key-value storage
  Query Planner      Optimizes execution
  Execution Engine   Coordinates distributed queries

## Neo4j vs NebulaGraph

  Neo4j                      NebulaGraph
  -------------------------- ---------------------------------
  Native graph engine        Distributed graph database
  Index-free adjacency       Partitioned distributed storage
  Cypher                     nGQL
  Best for deep traversals   Best for billion-scale graphs
  Simpler architecture       graphd + metad + storaged
