# Neo4j Cypher Language Roadmap

```text
Neo4j + Cypher Query Language
│
├── 1. Graph Database Fundamentals
│
├── 2. Neo4j Environment Setup
│
├── 3. Cypher Query Basics
│
├── 4. Creating Graph Data
│
├── 5. Reading Data (MATCH)
│
├── 6. Filtering and Searching
│
├── 7. Updating and Deleting Data
│
├── 8. Working with Relationships
│
├── 9. Aggregation & Built-in Functions
│
├── 10. WITH Clause and Query Pipelining
│
├── 11. Lists and Collection Processing
│
├── 12. Advanced Cypher Clauses
│
├── 13. Path Queries and Graph Traversals
│
├── 14. Data Modeling
│
├── 15. Constraints, Indexes & Schema
│
├── 16. Importing and Exporting Data
│
├── 17. Query Optimization
│
├── 18. APOC Procedures
│
├── 19. Graph Data Science (GDS)
│
├── 20. Neo4j Administration
│
└── 21. Real World Projects

Neo4j + Cypher Language Complete Roadmap
│
├── 1. Graph Database Fundamentals
│   ├── What is a Graph Database?
│   ├── Graph vs Relational Database
│   ├── Property Graph Model
│   ├── Nodes
│   ├── Relationships
│   ├── Properties
│   ├── Labels
│   ├── Relationship Types
│   ├── Graph Traversal
│   ├── ACID Transactions
│   ├── Native Graph Storage
│   └── Real-world Use Cases
│
├── 2. Neo4j Environment Setup
│   ├── Neo4j Desktop
│   ├── Neo4j AuraDB
│   ├── Neo4j Server
│   ├── Neo4j Browser
│   ├── Neo4j Workspace
│   ├── Cypher Shell
│   ├── Docker Setup
│   ├── Python Driver
│   ├── Java Driver
│   ├── JavaScript Driver
│   ├── .NET Driver
│   ├── Go Driver
│   └── Spring Data Neo4j
│
├── 3. Cypher Query Basics
│   ├── Cypher Syntax
│   ├── Variables
│   ├── Comments
│   ├── RETURN
│   ├── AS
│   ├── DISTINCT
│   ├── ORDER BY
│   ├── LIMIT
│   ├── SKIP
│   └── Query Structure
│
├── 4. Creating Graph Data
│   ├── CREATE
│   ├── CREATE Nodes
│   ├── CREATE Relationships
│   ├── Multiple CREATE
│   ├── Properties
│   ├── Labels
│   ├── MERGE
│   ├── ON CREATE
│   ├── ON MATCH
│   └── Avoiding Duplicates
│
├── 5. Reading Data (MATCH)
│   ├── MATCH
│   ├── Node Matching
│   ├── Relationship Matching
│   ├── Pattern Matching
│   ├── Multi-Hop Queries
│   ├── Variable-Length Relationships
│   ├── Quantified Path Patterns
│   ├── OPTIONAL MATCH
│   └── Pattern Expressions
│
├── 6. Filtering and Searching
│   ├── WHERE
│   ├── Comparison Operators
│   ├── Logical Operators
│   │   ├── AND
│   │   ├── OR
│   │   ├── NOT
│   │   └── XOR
│   ├── IN
│   ├── EXISTS
│   ├── IS NULL
│   ├── STARTS WITH
│   ├── ENDS WITH
│   ├── CONTAINS
│   ├── Regex
│   ├── Range Queries
│   └── Pattern Predicates
│
├── 7. Updating and Deleting Data
│   ├── SET
│   ├── REMOVE
│   ├── DELETE
│   ├── DETACH DELETE
│   ├── Property Updates
│   ├── Label Updates
│   ├── Bulk Updates
│   └── Dynamic Property Updates
│
├── 8. Working with Relationships
│   ├── Directed Relationships
│   ├── Undirected Relationships
│   ├── Relationship Types
│   ├── Relationship Properties
│   ├── Variable-Length Relationships
│   ├── Relationship Patterns
│   ├── shortestPath()
│   ├── allShortestPaths()
│   ├── Relationship Functions
│   └── Pattern Traversal
│
├── 9. Aggregation and Built-in Functions
│   ├── COUNT()
│   ├── SUM()
│   ├── AVG()
│   ├── MIN()
│   ├── MAX()
│   ├── COLLECT()
│   ├── SIZE()
│   ├── LENGTH()
│   ├── TYPE()
│   ├── labels()
│   ├── properties()
│   ├── keys()
│   ├── nodes()
│   ├── relationships()
│   ├── String Functions
│   ├── Numeric Functions
│   ├── Date & Time Functions
│   ├── List Functions
│   └── COALESCE()
│
├── 10. WITH Clause
│   ├── WITH Basics
│   ├── Variable Scope
│   ├── Passing Variables
│   ├── Aggregation
│   ├── ORDER BY
│   ├── LIMIT
│   ├── SKIP
│   ├── DISTINCT
│   ├── WHERE with WITH
│   └── Chaining Queries
│
├── 11. Lists and UNWIND
│   ├── Lists
│   ├── List Literals
│   ├── List Slicing
│   ├── List Concatenation
│   ├── List Comprehension
│   ├── Pattern Comprehension
│   ├── UNWIND
│   ├── range()
│   ├── reduce()
│   ├── any()
│   ├── all()
│   ├── none()
│   └── single()
│
├── 12. Advanced Cypher
│   ├── CASE
│   ├── FOREACH
│   ├── CALL
│   ├── CALL {}
│   ├── EXISTS {}
│   ├── UNION
│   ├── UNION ALL
│   ├── Pattern Comprehension
│   ├── OPTIONAL CALL
│   └── CALL IN TRANSACTIONS
│
├── 13. Path Queries and Traversals
│   ├── Path Variables
│   ├── Path Functions
│   ├── Variable-Length Paths
│   ├── Quantified Paths
│   ├── Cyclic Paths
│   ├── Graph Traversal
│   ├── Path Expansion
│   ├── Path Filtering
│   ├── Breadth-First Search
│   └── Depth-First Search
│
├── 14. Data Modeling
│   ├── Graph Modeling Principles
│   ├── Nodes vs Relationships
│   ├── Labels
│   ├── Properties
│   ├── Cardinality
│   ├── Dense Nodes
│   ├── Super Nodes
│   ├── Hyperedges
│   ├── Social Graph
│   ├── Recommendation Graph
│   ├── Knowledge Graph
│   ├── Fraud Graph
│   └── Best Practices
│
├── 15. Constraints and Indexes
│   ├── Property Index
│   ├── Composite Index
│   ├── Lookup Index
│   ├── Text Index
│   ├── Fulltext Index
│   ├── Vector Index
│   ├── Unique Constraint
│   ├── Node Key Constraint
│   ├── Property Type Constraint
│   ├── Relationship Constraint
│   ├── SHOW INDEXES
│   ├── SHOW CONSTRAINTS
│   └── DROP
│
├── 16. Importing and Exporting Data
│   ├── LOAD CSV
│   ├── WITH HEADERS
│   ├── CSV Cleaning
│   ├── MERGE Import
│   ├── CALL IN TRANSACTIONS
│   ├── neo4j-admin Import
│   ├── APOC Import
│   ├── JSON Import
│   ├── XML Import
│   ├── CSV Export
│   ├── GraphML
│   ├── APOC Export
│   └── Backup
│
├── 17. Query Optimization
│   ├── EXPLAIN
│   ├── PROFILE
│   ├── Execution Plans
│   ├── Cardinality
│   ├── Query Runtime
│   ├── Index Usage
│   ├── Join Order
│   ├── Query Hints
│   ├── Avoid Cartesian Products
│   ├── Memory Usage
│   ├── Performance Tuning
│   └── Best Practices
│
├── 18. APOC Procedures
│   ├── Installation
│   ├── apoc.load.*
│   ├── apoc.export.*
│   ├── apoc.create.*
│   ├── apoc.merge.*
│   ├── apoc.refactor.*
│   ├── apoc.periodic.*
│   ├── apoc.path.*
│   ├── apoc.coll.*
│   ├── apoc.map.*
│   ├── apoc.text.*
│   ├── apoc.convert.*
│   ├── apoc.date.*
│   └── Utility Procedures
│
├── 19. Graph Data Science (GDS)
│   ├── GDS Installation
│   ├── Graph Projection
│   ├── Memory Estimation
│   ├── Centrality Algorithms
│   │   ├── Degree
│   │   ├── PageRank
│   │   ├── Betweenness
│   │   ├── Closeness
│   │   └── Eigenvector
│   ├── Community Detection
│   │   ├── Louvain
│   │   ├── Leiden
│   │   ├── Label Propagation
│   │   └── WCC
│   ├── Similarity Algorithms
│   ├── Shortest Path Algorithms
│   ├── Node Embeddings
│   ├── Link Prediction
│   ├── Machine Learning Pipelines
│   └── Recommendation Systems
│
├── 20. Neo4j Administration
│   ├── User Management
│   ├── Roles
│   ├── Authentication
│   ├── Authorization
│   ├── Security
│   ├── Monitoring
│   ├── Memory Configuration
│   ├── Transactions
│   ├── Clustering
│   ├── Backup
│   ├── Restore
│   └── Disaster Recovery
│
└── 21. Real-World Projects
    ├── Movie Recommendation System
    ├── Social Network
    ├── Knowledge Graph
    ├── Fraud Detection
    ├── Product Recommendation
    ├── Supply Chain Network
    ├── IT Infrastructure Graph
    ├── Network Topology
    ├── Customer 360
    ├── GraphRAG
    ├── LLM + Neo4j
    └── Enterprise Knowledge Base

### Learning Order (Most Important)

```text
Phase 1 (Foundation)
│
├── Graph Fundamentals
├── Neo4j Setup
├── CREATE
├── MATCH
├── WHERE
├── RETURN
└── MERGE

Phase 2 (Core Cypher)
│
├── Relationships
├── SET
├── DELETE
├── Aggregations
├── Functions
├── WITH
└── UNWIND

Phase 3 (Intermediate)
│
├── Data Modeling
├── Constraints
├── Indexes
├── LOAD CSV
├── Path Queries
└── Query Optimization

Phase 4 (Advanced)
│
├── APOC
├── Graph Data Science
├── Performance Tuning
├── Security
└── Administration

Phase 5 (Projects)
│
├── Social Network
├── Recommendation Engine
├── Knowledge Graph
└── Fraud Detection Graph
```
................................................................

Phase 1 – Foundations
─────────────────────
1. Graph Database Fundamentals
2. Neo4j Environment Setup
3. Cypher Basics
4. Creating Data
5. Reading Data
6. Filtering
7. Updating Data

Phase 2 – Core Cypher
─────────────────────
8. Relationships
9. Aggregation & Functions
10. WITH
11. Lists & Collections
12. Advanced Clauses
13. Path Queries

Phase 3 – Database Design
─────────────────────────
14. Data Modeling
15. Constraints & Indexes

Phase 4 – Production
────────────────────
16. Import & Export
17. Query Optimization
18. APOC
19. Graph Data Science
20. Administration

Phase 5 – Projects
──────────────────
21. Real World Projects


This roadmap takes you from **beginner Cypher queries (`CREATE`, `MATCH`, `WHERE`)** all the way to **Graph Data Science, APOC, and production-grade Neo4j development**.
