# NebulaGraph + nGQL Learning Roadmap

```text
NebulaGraph + nGQL (Nebula Query Language)
│
├── 1. Graph Database Fundamentals
│
├── 2. NebulaGraph Architecture
│
├── 3. NebulaGraph Installation & Setup
│
├── 4. nGQL Basics
│
├── 5. Schema Design
│
├── 6. Data Insertion
│
├── 7. Querying Vertices and Edges
│
├── 8. Graph Traversal Queries
│
├── 9. Data Modification
│
├── 10. Aggregation and Functions
│
├── 11. Advanced nGQL
│
├── 12. Indexes and Performance
│
├── 13. Data Import and Export
│
├── 14. Graph Modeling
│
├── 15. Query Optimization
│
├── 16. NebulaGraph Analytics
│
├── 17. Administration and Operations
│
├── 18. Ecosystem and Integrations
│
└── 19. Real World Projects
```

```text
NebulaGraph + nGQL (Nebula Query Language)
│
├── 1. Graph Database Fundamentals [✓]
│   ├── What is a Graph Database
│   ├── Graph vs Relational Database
│   ├── Vertices
│   ├── Edges
│   ├── Properties
│   ├── Tags
│   ├── Edge Types
│   ├── Graph Traversal
│   └── Graph Use Cases
│
├── 2. NebulaGraph Architecture [✓]
│   ├── Graph Service
│   ├── Meta Service
│   ├── Storage Service
│   ├── Distributed Architecture
│   ├── Partitions
│   ├── Replication
│   ├── Storage Engine
│   └── Cluster Components
│
├── 3. NebulaGraph Installation & Setup [✓]
│   ├── Docker Deployment
│   ├── Docker Compose
│   ├── Linux Installation
│   ├── Nebula Console
│   ├── Nebula Dashboard
│   ├── Nebula Studio
│   └── Client SDKs
│       ├── Python Client
│       ├── Java Client
│       ├── Go Client
│       └── Spark Connector
│
├── 4. nGQL Basics [✓]
│   ├── nGQL Syntax
│   ├── Statements
│   ├── Variables
│   ├── Comments
│   ├── YIELD
│   ├── LIMIT
│   ├── ORDER BY
│   ├── DISTINCT
│   └── PIPE Operator (|)
│
├── 5. Schema Design [✓]
│   ├── CREATE SPACE
│   ├── USE SPACE
│   ├── CREATE TAG
│   ├── ALTER TAG
│   ├── DROP TAG
│   ├── CREATE EDGE
│   ├── ALTER EDGE
│   ├── DROP EDGE
│   └── Data Types
│       ├── INT
│       ├── DOUBLE
│       ├── BOOL
│       ├── STRING
│       ├── DATE
│       └── DATETIME
│
├── 6. Data Insertion [✓]
│   ├── INSERT VERTEX
│   ├── INSERT EDGE
│   ├── Batch Insert
│   ├── Vertex IDs (VID)
│   ├── Property Assignment
│   ├── UPSERT
│   └── Data Validation
│
├── 7. Querying Vertices and Edges [✓]
│   ├── FETCH PROP ON
│   ├── LOOKUP
│   ├── MATCH
│   ├── GO
│   ├── FIND Vertex
│   ├── FIND Edge
│   ├── Pattern Matching
│   └── Property Access
│
├── 8. Graph Traversal Queries [➤]
│   ├── GO Traversal
│   ├── One-Hop Traversal
│   ├── Multi-Hop Traversal
│   ├── REVERSELY
│   ├── BIDIRECT
│   ├── Path Queries
│   ├── SHORTEST PATH
│   ├── ALL PATH
│   └── Trail Exploration
│
├── 9. Data Modification [➤]
│   ├── UPDATE VERTEX
│   ├── UPDATE EDGE
│   ├── UPSERT VERTEX
│   ├── UPSERT EDGE
│   ├── DELETE VERTEX
│   ├── DELETE EDGE
│   ├── DELETE TAG
│   └── DELETE Operations
│
├── 10. Aggregation and Functions [➤]
│   ├── count()
│   ├── sum()
│   ├── avg()
│   ├── min()
│   ├── max()
│   ├── collect()
│   ├── String Functions
│   ├── Numeric Functions
│   ├── Date Functions
│   └── Type Conversion Functions
│
├── 11. Advanced nGQL [ ]
│   ├── WITH
│   ├── PIPE Operations
│   ├── CASE Expressions
│   ├── Subqueries
│   ├── Variable Assignment
│   ├── Composite Queries
│   ├── MATCH Patterns
│   └── Query Chaining
│
├── 12. Indexes and Performance [ ]
│   ├── Tag Index
│   ├── Edge Index
│   ├── Full Scan vs Index Scan
│   ├── CREATE INDEX
│   ├── REBUILD INDEX
│   ├── SHOW INDEXES
│   └── Index Best Practices
│
├── 13. Data Import and Export [ ]
│   ├── Nebula Importer
│   ├── CSV Import
│   ├── JSON Import
│   ├── SST Import
│   ├── Batch Loading
│   ├── Data Export
│   ├── Backup
│   └── Restore
│
├── 14. Graph Modeling [ ]
│   ├── Vertex Modeling
│   ├── Edge Modeling
│   ├── Social Network Model
│   ├── Knowledge Graph Model
│   ├── Recommendation Graph
│   ├── Fraud Detection Model
│   ├── Network Topology Model
│   └── Best Practices
│
├── 15. Query Optimization [ ]
│   ├── EXPLAIN
│   ├── PROFILE
│   ├── Execution Plans
│   ├── Traversal Optimization
│   ├── Index Utilization
│   ├── Query Tuning
│   ├── Partition Awareness
│   └── Performance Monitoring
│
├── 16. NebulaGraph Analytics [ ]
│   ├── Nebula Algorithm
│   ├── PageRank
│   ├── Connected Components
│   ├── Shortest Path
│   ├── Community Detection
│   ├── Similarity Algorithms
│   ├── Graph Statistics
│   └── Recommendation Analytics
│
├── 17. Administration and Operations [ ]
│   ├── User Management
│   ├── Roles and Permissions
│   ├── Cluster Management
│   ├── Scaling
│   ├── Monitoring
│   ├── Backup
│   ├── Restore
│   └── Security
│
├── 18. Ecosystem and Integrations [ ]
│   ├── Nebula Studio
│   ├── Nebula Dashboard
│   ├── Spark Connector
│   ├── Flink Connector
│   ├── Kafka Integration
│   ├── Python SDK
│   ├── Java SDK
│   └── Graph Visualization Tools
│
└── 19. Real World Projects [ ]
    ├── Knowledge Graph
    ├── Social Network Graph
    ├── Recommendation Engine
    ├── Fraud Detection System
    ├── IT Infrastructure Graph
    ├── Customer 360 Graph
    ├── Supply Chain Network
    └── Enterprise Knowledge Base
```

## Neo4j Cypher → Nebula nGQL Mapping

```text
Neo4j Cypher                Nebula nGQL
│
├── Node                → Vertex
├── Relationship        → Edge
├── Label               → Tag
├── Property            → Property
├── Database            → Space
├── CREATE              → INSERT VERTEX / EDGE
├── MATCH               → MATCH / GO
├── RETURN              → YIELD
├── MERGE               → UPSERT
├── WHERE               → WHERE
├── shortestPath()      → FIND SHORTEST PATH
├── PROFILE             → PROFILE
└── EXPLAIN             → EXPLAIN
```

## Learning Order (Recommended)

```text
Phase 1 (Foundation)
│
├── Graph Fundamentals
├── Nebula Architecture
├── Installation
├── Spaces
├── Tags
└── Edges

Phase 2 (Core nGQL)
│
├── INSERT VERTEX
├── INSERT EDGE
├── FETCH
├── LOOKUP
├── MATCH
├── GO
└── YIELD

Phase 3 (Intermediate)
│
├── Traversals
├── Aggregations
├── Updates
├── Indexes
├── Data Modeling
└── Importer

Phase 4 (Advanced)
│
├── MATCH Patterns
├── PROFILE
├── Query Optimization
├── Analytics
├── Cluster Operations
└── Security

Phase 5 (Projects)
│
├── Knowledge Graph
├── Recommendation System
├── Fraud Detection
└── Large Scale Graph Platform
```

If you're coming from Neo4j, focus first on **Space → Tag → Edge → GO → MATCH → LOOKUP → FETCH PROP → PROFILE**, since these are the core concepts and commands you'll use daily in NebulaGraph.
