# Neo4j Community Edition – GenAI & Agentic RAG Exploration

## Objective

Explore how **GenAI, embeddings, RAG, and Agentic AI** can be implemented using **Neo4j Community Edition**.

The notebook demonstrates Neo4j as both a **knowledge graph and vector retrieval layer** for an LLM-based system.

## What Is Implemented

* Document knowledge graph creation in Neo4j.
* Document embedding generation using `all-MiniLM-L6-v2`.
* Embedding storage in Neo4j.
* Neo4j vector index for semantic search.
* Cypher-based graph traversal.
* LLM latency/performance comparison for model selection.
* Neo4j search and other functions exposed as **LLM tools**.
* Tool selection and execution through an agent.
* Vector-search fallback when graph search does not return useful results.

## Why This Approach?

A standard LLM may not have access to **company-specific or structured knowledge**.

Combining:

**LLM + Embeddings + Vector Search + Knowledge Graph**

allows relevant information to be retrieved before response generation.

Neo4j provides two complementary retrieval capabilities:

* **Graph relationships** — structured and connected information.
* **Vector search** — semantic similarity-based retrieval.

Together, these provide a foundation for **GraphRAG**.

## Why Compare LLMs?

Different LLMs provide different levels of latency and capability.

An agentic workflow can require multiple LLM and tool calls for a single request. Model selection therefore directly affects:

* Response latency
* Overall agent execution time
* Processing efficiency
* Potential operational cost

The comparison provides a technical basis for selecting an appropriate LLM for future Agentic RAG workflows.

## Benefits

### Technical

* Faster access to relevant technical information.
* Combination of semantic search and graph relationships.
* Reduced manual document searching.
* Foundation for tool-using AI agents.
* Extensible retrieval and tool architecture.

### Business

The approach can provide faster access to internal knowledge and reduce repetitive information-search activities.

Traditional workflow:

**Question → Search → Find → Connect Information → Answer**

Agentic workflow:

**Question → Agent → Retrieve → Reason → Answer**

This can reduce time spent on repetitive technical and knowledge-based tasks.

## Future Extension

Potential extensions include:

* Query rewriting
* Retrieval evaluation
* Multiple retrieval strategies
* Answer validation
* Additional tools
* Multi-step agent workflows
* Larger organizational knowledge graphs

### Future Direction: Self-Correcting Agentic GraphRAG System

The long-term direction is a **Self-Correcting Agentic GraphRAG System** capable of:

**Understand → Retrieve → Evaluate → Correct → Retrieve Again → Answer**

The system can automatically change its retrieval strategy when the initial result is insufficient, improving reliability and retrieval efficiency.

---

## System Architecture

```text
                    User Question
                          |
                          v
                  Intent / Routing
                    /         \
                   /           \
          Structured Query   Semantic Search
                |                  |
                v                  v
         Text-to-Cypher       Vector Search
                |                  |
                v                  v
         Cypher Traversal    Vector Matches
                \                  /
                 \                /
                  v              v
                Subgraph Context
                       |
                       v
              LLM Response Synthesis
                       |
                       v
                  Final Answer
```

## Data Flow

| Step                      | Component                  | Output                  | Purpose                                     |
| ------------------------- | -------------------------- | ----------------------- | ------------------------------------------- |
| **1. Document Ingestion** | Document loader            | Structured documents    | Prepare raw text for processing             |
| **2. Graph Extraction**   | `LLMGraphTransformer`      | Nodes & relationships   | Extract entities and relationships          |
| **3. Vector Embedding**   | `all-MiniLM-L6-v2`         | 384-dimensional vectors | Enable semantic retrieval                   |
| **4. Neo4j Persistence**  | `Neo4jGraph`               | Graph + vector index    | Store relationships and embeddings          |
| **5. Query Processing**   | `GraphCypherQAChain` / LLM | Cypher query            | Convert natural language into graph queries |
| **6. Context Retrieval**  | Neo4j                      | Graph/vector context    | Retrieve relevant information               |
| **7. Answer Generation**  | LLM                        | Final response          | Generate an answer from retrieved context   |

---

## Future Architecture Direction

```text
User Question
      ↓
Understand Intent
      ↓
Select Retrieval Strategy
      ↓
Neo4j Graph / Vector Retrieval
      ↓
Evaluate Retrieved Context
      ↓
Sufficient?
   /       \
 Yes        No
  ↓          ↓
Answer   Query Rewrite /
          Retrieval Fallback
               ↓
        Retrieve Again
               ↓
            Answer
```

The architecture provides a foundation for extending the current implementation toward a **Self-Correcting Agentic GraphRAG System**.
