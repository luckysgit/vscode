# Complete Database List with Languages

> **Languages** = Implementation Language (built in) + Query Language (used to interact)

---

## Relational (SQL) Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| MySQL | C, C++ | SQL |
| PostgreSQL | C | SQL |
| Microsoft SQL Server | C, C++ | T-SQL |
| Oracle Database | C, C++ | PL/SQL |
| SQLite | C | SQL |
| MariaDB | C, C++ | SQL |
| IBM Db2 | C, C++ | SQL |
| Amazon RDS | C, C++ (MySQL/PostgreSQL base) | SQL |
| Google Cloud SQL | C (MySQL/PostgreSQL base) | SQL |
| CockroachDB | Go | SQL |
| YugabyteDB | C, C++ | SQL |
| TiDB | Go | SQL |
| Percona Server | C, C++ | SQL |
| Greenplum | C | SQL |
| Amazon Aurora | C++ (MySQL/PostgreSQL compatible) | SQL |
| Neon | Rust | SQL |
| PlanetScale | Go (MySQL compatible) | SQL |
| Supabase | TypeScript (PostgreSQL based) | SQL |

---

## Document Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| MongoDB | C++ | MQL (MongoDB Query Language) |
| CouchDB | Erlang | JavaScript / Mango Query |
| Couchbase | C++ | N1QL (SQL-like) |
| Amazon DocumentDB | C++ (MongoDB compatible) | MQL |
| Firebase Firestore | Java | NoSQL (Firestore API) |
| RethinkDB | C++ | ReQL |
| MarkLogic | C++ | XQuery, JavaScript, SPARQL |
| RavenDB | C# (.NET) | RQL |
| FerretDB | Go (MongoDB compatible) | MQL |

---

## Key-Value Stores

| Database | Built In | Query Language |
|----------|----------|----------------|
| Redis | C | Redis CLI / Commands |
| Memcached | C | Memcached Protocol |
| Amazon DynamoDB | Java | PartiQL / DynamoDB API |
| Riak | Erlang | HTTP API / Protocol Buffers |
| Voldemort | Java | Key-Value API |
| Etcd | Go | gRPC / HTTP API |
| Aerospike | C | AQL |
| LevelDB | C++ | Key-Value API |
| RocksDB | C++ | Key-Value API |
| LMDB | C | C API |
| Valkey | C (Redis fork) | Redis Commands |

---

## Wide-Column / Column-Family Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| Apache Cassandra | Java | CQL (Cassandra Query Language) |
| Apache HBase | Java | HBase Shell / Java API |
| Google Bigtable | C++ | CBT / Bigtable API |
| Amazon Keyspaces | Java (Cassandra compatible) | CQL |
| ScyllaDB | C++ | CQL |
| Hypertable | C++ | HQL |

---

## Graph Databases

> **150+ graph databases** — native, multi-model, RDF-based, cloud, embedded, and research systems.

### Native Property Graph Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| Neo4j | Java, Scala | Cypher |
| Memgraph | C++ | Cypher |
| FalkorDB | C (RedisGraph fork) | Cypher |
| RedisGraph *(deprecated)* | C | Cypher |
| TigerGraph | C++ | GSQL |
| Dgraph | Go | DQL / GraphQL |
| Cayley | Go | Gremlin, MQL, GraphQL |
| HugeGraph | Java | Gremlin |
| TypeDB | Java | TypeQL |
| TerminusDB | Rust, Prolog | WOQL, GraphQL |
| Nebula Graph | C++ | nGQL |
| Ultipa | C++ | UQL |
| KuzuDB | C++ | Cypher |
| GraphScope | C++, Python | Gremlin, SPARQL, NetworkX |
| CosmosDB (Gremlin API) | C++ | Gremlin |
| Bitsy | Java | Gremlin |
| Flockdb *(deprecated)* | Scala | Thrift API |
| Titan *(deprecated)* | Java | Gremlin |
| BlazeGraph *(now Wikidata)* | Java | SPARQL, Gremlin |

### Distributed / Cloud Graph Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| Amazon Neptune | Java | SPARQL, Gremlin, openCypher |
| JanusGraph | Java | Gremlin |
| Google Cloud Spanner Graph | C++ | GQL, SQL |
| Azure Cosmos DB (Graph) | C++ | Gremlin |
| Oracle Graph (PGQL) | C, Java | PGQL, SQL |
| IBM Db2 Graph | C, C++ | SQL / Graph extensions |
| SAP HANA Graph | C++ | SQL / Graph procedures |
| TigerGraph Cloud | C++ | GSQL |
| Dgraph Cloud | Go | DQL / GraphQL |
| Memgraph Cloud | C++ | Cypher |
| Neo4j Aura | Java, Scala | Cypher |
| GraphDB Cloud (Ontotext) | Java | SPARQL |
| Stardog Cloud | Java | SPARQL, SQL |

### Multi-Model Databases (with Graph Support)

| Database | Built In | Query Language |
|----------|----------|----------------|
| ArangoDB | C++ | AQL |
| OrientDB | Java | SQL-like / Gremlin |
| SurrealDB | Rust | SurrealQL |
| EdgeDB | Python, Rust | EdgeQL |
| Couchbase | C++ | N1QL / Graph API |
| MarkLogic | C++ | SPARQL, XQuery |
| Virtuoso | C | SPARQL, SQL |
| AnzoGraph DB | C++ | SPARQL, SQL |
| TupleSpace / TupleGraph | Java | Gremlin |

### RDF / Semantic / Triple-Store Graph Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| Apache Jena (TDB2) | Java | SPARQL |
| Stardog | Java | SPARQL, SQL, GraphQL |
| GraphDB (Ontotext) | Java | SPARQL |
| AllegroGraph | Common Lisp, C | SPARQL, Prolog |
| BlazeGraph | Java | SPARQL |
| Amazon Neptune (RDF) | Java | SPARQL |
| Oxigraph | Rust | SPARQL |
| QLever | C++ | SPARQL |
| RDFLib *(Python library)* | Python | SPARQL |
| Corese | Java | SPARQL |
| 4store | C | SPARQL |
| Parliament | Java | SPARQL |
| Mulgara | Java | iTQL, SPARQL |
| Sesame / RDF4J | Java | SPARQL |
| Halyard | Java | SPARQL |
| Strabon | Java | stSPARQL, GeoSPARQL |
| Allegrograph Cloud | Common Lisp, C | SPARQL |
| Dydra | Ruby | SPARQL |
| Anzo (Cambridge Semantics) | Java | SPARQL, SQL |
| SYSTAP Blazegraph | Java | SPARQL |
| TopBraid EDG | Java | SPARQL, SHACL |
| Metaphactory | Java | SPARQL, LPG |

### Embedded / Lightweight Graph Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| KuzuDB | C++ | Cypher |
| Tinkerpop / TinkerGraph | Java | Gremlin |
| LightGraph *(Rust)* | Rust | Rust API |
| DGraph Embedded | Go | DQL |
| RedBeanGraph | PHP | PHP API |
| Graphology | JavaScript | JS API |
| Sigma.js *(visualization)* | JavaScript | JS API |
| ngdb | Go | Go API |
| Cog | Python | Python API |

### Academic / Research Graph Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| DEX / Sparksee | C++ | C++ / Java API |
| G-Store | C++ | Custom API |
| gStore | C++ | SPARQL |
| TriAD | C++ | SPARQL |
| RDF-3X | C++ | SPARQL |
| WHIRL | C | Datalog |
| Grail | C++ | Custom |
| GraphBase | C | Custom |
| InfiniteGraph | Java | Java API / Gremlin |
| FlockDB | Scala | Thrift API |
| TurboGraph | C++ | Cypher-like |
| Trinity Graph Engine | C# | TSL / LIKQ |
| GraphX (Apache Spark) | Scala | Scala / Python API |
| Gradoop | Java | GDL |
| GrDB | Haskell | Haskell API |

### Graph Extensions / Plugins for Other Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| Apache AGE *(PostgreSQL ext.)* | C | Cypher + SQL |
| PgRouting *(PostgreSQL ext.)* | C | SQL |
| MySQL Graph *(HeatWave)* | C++ | SQL / GraphQL |
| SQL Server Graph | C++ | T-SQL / Graph extensions |
| Oracle Spatial & Graph | C, Java | PGQL, SQL |
| Aerospike Graph | C, Java | Gremlin |
| Redis Graph *(FalkorDB)* | C | Cypher |
| Cosmos DB Gremlin | C++ | Gremlin |
| Hive Graph *(LDBC)* | Java | HiveQL |

### Chinese / Asian Ecosystem Graph Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| Nebula Graph | C++ | nGQL |
| Ultipa Graph | C++ | UQL |
| TuGraph (Ant Group) | C++ | Cypher / GQL |
| GalaxyBase | C++ | GQL |
| GeaFlow (Ant Group) | Java | SQL / Graph API |
| KgGraph | Java | Custom API |
| HugeGraph (Baidu) | Java | Gremlin |
| IndraDB | Rust | IndraDB API |
| Galaxybase | C++ | Cypher |

### Graph Analytics / Processing Engines *(not pure DBs but graph-focused)*

| Database / Engine | Built In | Query Language |
|-------------------|----------|----------------|
| Apache Giraph | Java | Java API (Pregel model) |
| GraphX (Spark) | Scala | Scala / Python |
| GraphLab / Turi Create | C++ | Python |
| PowerGraph | C++ | C++ API |
| Pregel (Google) | C++ | C++ API |
| Ligra | C++ | C++ API |
| NetworkX *(library)* | Python | Python API |
| GraphFrames (Spark) | Scala | Spark SQL / Scala |
| Graph-tool | C++, Python | Python API |
| SNAP (Stanford) | C++ | C++ / Python |

### Commercial / Enterprise Graph Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| Cambridge Semantics Anzo | Java | SPARQL |
| Franz AllegroGraph | Common Lisp | SPARQL, Prolog |
| Stardog Enterprise | Java | SPARQL, SQL |
| TigerGraph Enterprise | C++ | GSQL |
| DataStax Graph | Java | Gremlin, DQL |
| GRAKN / TypeDB | Java | TypeQL |
| Fluree | Clojure | FlureeQL, SPARQL |
| Objectivity / ThingSpan | C++ | Java / Python API |
| Teradata Aster | C | SQL-MR |
| ObjectDB | Java | JPQL / JPA |
| Complexica | Java | Custom |
| Ontotext GraphDB | Java | SPARQL |
| PoolParty Semantic Suite | Java | SPARQL |
| Eccenca Corporate Memory | Java | SPARQL |
| metaphacts | Java | SPARQL |

### Query Language Summary for Graph Databases

| Query Language | Databases Using It |
|----------------|--------------------|
| **Cypher** | Neo4j, Memgraph, FalkorDB, RedisGraph, KuzuDB, Apache AGE, Amazon Neptune |
| **Gremlin** | JanusGraph, Amazon Neptune, OrientDB, HugeGraph, Titan, Aerospike Graph, TinkerGraph |
| **SPARQL** | All RDF/triple stores, Amazon Neptune, GraphDB, Stardog, AllegroGraph |
| **GSQL** | TigerGraph |
| **AQL** | ArangoDB |
| **nGQL** | Nebula Graph |
| **GQL (ISO standard)** | Google Spanner Graph, TuGraph, future standard |
| **TypeQL** | TypeDB / GRAKN |
| **DQL** | Dgraph |
| **SurrealQL** | SurrealDB |
| **PGQL** | Oracle Graph |
| **UQL** | Ultipa Graph |
| **WOQL** | TerminusDB |
| **LIKQ** | Trinity Graph Engine |

---

## Time-Series Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| InfluxDB | Go | Flux, InfluxQL |
| TimescaleDB | C (PostgreSQL extension) | SQL |
| Prometheus | Go | PromQL |
| Graphite | Python | Graphite API |
| OpenTSDB | Java | HTTP API / TQL |
| QuestDB | Java, C++ | SQL |
| TDengine | C | SQL-like |
| KDB+ | C | Q language |
| VictoriaMetrics | Go | MetricsQL / PromQL |
| Apache IoTDB | Java | IoTDB-SQL |

---

## Search Engines / Full-Text Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| Elasticsearch | Java | Query DSL (JSON) |
| Apache Solr | Java | Solr Query Syntax |
| OpenSearch | Java | Query DSL (JSON) |
| Typesense | C++ | Typesense API |
| Meilisearch | Rust | Meilisearch API |
| Manticore Search | C++ | SQL-like |
| Sphinx Search | C++ | SphinxQL |
| Zinc Search | Go | Zinc Query DSL |

---

## In-Memory Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| Redis | C | Redis Commands |
| Memcached | C | Memcached Protocol |
| VoltDB | Java, C++ | SQL |
| Apache Ignite | Java | SQL / Key-Value API |
| Hazelcast | Java | SQL / Predicate API |
| GridGain | Java | SQL |
| Tarantool | C, Lua | Lua / SQL |

---

## NewSQL Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| CockroachDB | Go | SQL |
| Google Spanner | C++ | SQL |
| NuoDB | C++ | SQL |
| VoltDB | Java, C++ | SQL |
| MemSQL / SingleStore | C++ | SQL |
| Splice Machine | Java, Scala | SQL |

---

## Analytical / OLAP / Data Warehouses

| Database | Built In | Query Language |
|----------|----------|----------------|
| Snowflake | C++ | SQL |
| Google BigQuery | C++ | SQL |
| Amazon Redshift | C++ | SQL |
| ClickHouse | C++ | SQL |
| Apache Druid | Java | SQL / Druid SQL |
| Apache Pinot | Java | SQL |
| Vertica | C++ | SQL |
| DuckDB | C++ | SQL |
| StarRocks | C++ | SQL |
| Apache Hive | Java | HiveQL (SQL-like) |
| Presto / Trino | Java | SQL |
| Databricks | Scala, Python | SQL, Python, Scala, R |
| Teradata | C | ANSI SQL / BTEQ |
| Exasol | C++ | SQL |
| Firebolt | C++ | SQL |
| Dremio | Java | SQL |
| SingleStore | C++ | SQL |

---

## Embedded Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| SQLite | C | SQL |
| LevelDB | C++ | Key-Value API |
| RocksDB | C++ | Key-Value API |
| LMDB | C | C API |
| H2 | Java | SQL |
| Apache Derby | Java | SQL |
| Realm | C++ | Realm Query Language |
| Berkeley DB | C | C / Java API |

---

## RDF / Semantic / Triple Stores

| Database | Built In | Query Language |
|----------|----------|----------------|
| Apache Jena | Java | SPARQL |
| Stardog | Java | SPARQL, SQL |
| Virtuoso | C | SPARQL, SQL |
| AllegroGraph | Common Lisp, C | SPARQL |
| GraphDB (Ontotext) | Java | SPARQL |
| BlazeGraph | Java | SPARQL |
| Amazon Neptune (RDF) | Java | SPARQL |

---

## Multi-Model Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| ArangoDB | C++ | AQL |
| OrientDB | Java | SQL-like, Gremlin |
| FaunaDB / Fauna | Scala | FQL (Fauna Query Language) |
| Couchbase | C++ | N1QL |
| Azure Cosmos DB | C++ | SQL API, Gremlin, Cassandra API |
| SurrealDB | Rust | SurrealQL |
| EdgeDB | Python, Rust | EdgeQL |

---

## Vector Databases (AI/ML)

| Database | Built In | Query Language |
|----------|----------|----------------|
| Pinecone | Python, Go | Pinecone API |
| Weaviate | Go | GraphQL / REST |
| Milvus | C++ | Python / Go SDK |
| Qdrant | Rust | REST / gRPC API |
| Chroma | Python | Python API |
| PgVector | C (PostgreSQL ext.) | SQL |
| Zilliz | C++ (Milvus cloud) | Python SDK |
| Vespa | C++, Java | YQL |
| Vald | Go | gRPC |
| LanceDB | Rust | SQL-like / Python API |
| Marqo | Python | Marqo API |

---

## Ledger / Immutable Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| Amazon QLDB | Java | PartiQL |
| immudb | Go | SQL / Key-Value API |
| Hyperledger Fabric | Go | Go / JavaScript chaincode |

---

## Spatial / GIS Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| PostGIS | C (PostgreSQL extension) | SQL |
| SpatiaLite | C (SQLite extension) | SQL |
| Oracle Spatial | C, C++ | SQL |
| MongoDB Geospatial | C++ | MQL |

---

## Cloud-Native / Serverless Databases

| Database | Built In | Query Language |
|----------|----------|----------------|
| PlanetScale | Go (MySQL compatible) | SQL |
| Neon | Rust (PostgreSQL compatible) | SQL |
| Turso | Rust (SQLite compatible) | SQL |
| Upstash | Go (Redis compatible) | Redis Commands |
| Xata | TypeScript | TypeScript API / SQL |
| Convex | Rust, TypeScript | TypeScript API |
| Fauna | Scala | FQL |

---

## Summary: Most Common Implementation Languages

| Language | Databases Built With It |
|----------|------------------------|
| **C / C++** | MySQL, PostgreSQL, SQLite, Redis, MongoDB, ClickHouse, Cassandra (via C ext.), Memcached, LevelDB, RocksDB, TigerGraph, Memgraph, and many more |
| **Java** | Apache Cassandra, HBase, Neo4j, JanusGraph, Elasticsearch, Solr, Druid, Presto, HugeGraph, Hive, Trino, and more |
| **Go** | CockroachDB, TiDB, Etcd, Dgraph, Cayley, InfluxDB, Prometheus, VictoriaMetrics, Weaviate |
| **Rust** | Neon, Meilisearch, Qdrant, SurrealDB, LanceDB, TerminusDB, Convex |
| **Python** | Graphite, Chroma, Marqo |
| **Scala** | Neo4j (partial), Splice Machine, Fauna |
| **Erlang** | CouchDB, Riak |
| **C#** | RavenDB |
| **Lua** | Tarantool (scripting layer) |
| **Common Lisp** | AllegroGraph |

---

*Last updated: July 2026*
