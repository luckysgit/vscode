# NebulaGraph System Design

## High-Level Architecture

``` text
                 Client Applications
                        │
                  TCP (9669)
                        │
                        ▼
                +----------------+
                |    graphd      |
                +----------------+
                        │
      ┌─────────────────┼─────────────────┐
      ▼                 ▼                 ▼
   Parser        Query Planner     Execution Engine
                        │
                        ▼
                +----------------+
                |     metad      |
                +----------------+
                        │
            Schema / Cluster Metadata
                        │
                        ▼
                +----------------+
                |   storaged     |
                +----------------+
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
   Partition 1    Partition 2    Partition N
                        │
                        ▼
                     RocksDB
```

## Components

### graphd

-   Accepts nGQL queries
-   Parses queries
-   Builds execution plans
-   Coordinates distributed execution

### metad

Stores: - Spaces - Tags - Edge Types - Indexes - Users - Roles -
Partition information

### storaged

Stores: - Vertices - Edges - Properties - Replicas

### Partitions

Distribute graph data across storage nodes for scalability.

### RocksDB

Underlying storage engine used by each storage node.

## Why This Design?

  Component          Purpose
  ------------------ ---------------------------
  graphd             Query processing
  metad              Metadata management
  storaged           Graph storage
  Partitions         Horizontal scaling
  RocksDB            Durable key-value storage
  Planner            Query optimization
  Execution Engine   Distributed execution

## Advantages

-   Massive horizontal scalability
-   Distributed architecture
-   High availability
-   Efficient graph traversals
-   Fault tolerance
-   Easy cluster expansion
