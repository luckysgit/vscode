# Neo4j Community Edition — GenAI, RAG, Embeddings & Agentic GraphRAG Exploration

## 1. Overview

This notebook explores how **Generative AI, embeddings, RAG, graph retrieval, and agentic tool calling** can be combined with **Neo4j Community Edition**.

In the notebook :

- Neo4j Community Edition as the knowledge and retrieval layer
- Sentence Transformers for generating document/query embeddings
- Native Neo4j vector indexing and similarity search
- Cypher-based graph traversal
- LLM tool/function calling
- Agent-style iterative execution
- A self-correction/fallback mechanism from graph search to semantic vector search
- A calculator tool to demonstrate that an agent can use multiple tools instead of relying only on generated text
- Both Groq-hosted Llama and Gemini-based agent execution patterns

The notebook therefore moves from **basic RAG components → tool-using agent → self-correcting GraphRAG direction**.

---

## 2. Objective

The objective of this exploration is to understand:

1. How Neo4j Community Edition can support GenAI/RAG workloads.
2. How embeddings can be stored and searched directly in Neo4j.
3. How vector search and graph traversal can complement each other.
4. How an LLM can decide which tool should be used to answer a request.
5. How an agent can continue searching when the first retrieval strategy fails.
6. What technical components are required before extending the solution into a more autonomous agentic system.

This gives us a practical technical baseline instead of evaluating GenAI only from the LLM-response perspective.

---

## 3. Why Neo4j?

Traditional RAG systems commonly retrieve information using semantic similarity over document embeddings.

That works well when the answer is contained in a relevant text chunk, but many technical and business questions depend on **relationships between entities**.

For example:

> "Which documents are related to a particular database feature?"

A vector search can identify semantically similar documents, while a graph can represent explicit relationships such as:

```text
(Document) ──[:BELONGS_TO]──> (Category)
```

Neo4j is useful in this exploration because it can act as both:

- a **knowledge graph**, where entities and relationships are represented explicitly
- a **vector retrieval layer**, where embeddings can be indexed and searched

This creates a foundation for **GraphRAG**, where semantic retrieval and structured graph relationships can be used together.

---

## 4. Why We Use Embeddings

LLMs do not naturally perform database-style semantic search.

An embedding model converts text into a numerical vector representing its semantic meaning.

The notebook uses:

```text
all-MiniLM-L6-v2
```

The document text is converted into a vector and stored on the Neo4j `Document` node:

```text
(Document)
  ├── id
  ├── text
  └── embedding
```

The notebook then creates a Neo4j vector index:

```cypher
CREATE VECTOR INDEX document_embeddings
FOR (d:Document) ON (d.embedding)
```

The query is also converted into an embedding and searched against the vector index.

This allows queries to find relevant information based on **meaning**, rather than requiring an exact keyword match.

---

## 5. Why Compare Retrieval Methods?

The notebook is designed around an important distinction:

### Graph search

Cypher traversal is useful when the required information can be identified through explicit entities, properties, and relationships.

Example:

```text
Document → Category
```

### Vector search

Vector search is useful when the user query is expressed differently from the stored document text and semantic similarity is required.

### Why both?

Neither method is sufficient for every type of query.

A practical AI system can therefore use:

```text
User Query
    ↓
LLM / Agent
    ↓
Choose retrieval strategy
    ├── Graph/Cypher search
    └── Vector search
    ↓
Retrieved context
    ↓
LLM
    ↓
Final answer
```

The notebook demonstrates this idea by exposing both retrieval methods as tools available to the agent.

---

## 6. What the Notebook Implements

### 6.1 Neo4j initialization

The notebook starts a local Neo4j Community Edition instance and connects through the Python Neo4j driver.

The current notebook uses:

```text
Neo4j Community Edition 5.18.0
```

The database is populated with a small demonstration dataset.

---

### 6.2 Document and graph creation

The example creates `Document` and `Category` nodes and connects them using:

```text
(Document)-[:BELONGS_TO]->(Category)
```

This gives the LLM a structured knowledge representation in addition to document text.

---

### 6.3 Embedding generation

Each document is encoded using:

```text
SentenceTransformer("all-MiniLM-L6-v2")
```

The resulting 384-dimensional embedding is stored in Neo4j.

---

### 6.4 Vector retrieval

The notebook performs vector retrieval using Neo4j's vector index:

```cypher
CALL db.index.vector.queryNodes(
    'document_embeddings',
    2,
    $query_vec
)
```

The returned similarity score is also exposed to the agent.

---

### 6.5 Graph retrieval

The notebook provides a Cypher-based graph traversal tool:

```text
graph_cypher_traversal()
```

It searches the connected document/category structure and returns matching graph information.

---

### 6.6 Tool-using LLM

The notebook exposes the following tools to the LLM:

| Tool | Purpose |
|---|---|
| `vector_index_search` | Semantic retrieval using Neo4j vector search |
| `graph_cypher_traversal` | Structured retrieval using Neo4j/Cypher |
| `python_calculator` | Performs numerical calculations |

The LLM is therefore not limited to generating an answer from its internal knowledge. It can decide to call an external tool and use the returned information.

---

## 7. Why Tool Calling Matters

Tool calling is an important step toward agentic AI.

Instead of:

```text
User → LLM → Answer
```

the architecture becomes:

```text
User
  ↓
LLM / Agent
  ↓
Decide what is required
  ↓
Call tool
  ↓
Receive result
  ↓
Evaluate result
  ↓
Call another tool if required
  ↓
Generate final answer
```

This is closer to how a technical AI assistant could operate in a real environment.

For example, an agent could decide:

```text
1. Search the graph
2. If graph search is insufficient
3. Perform vector search
4. Use the retrieved context
5. Perform a calculation if required
6. Generate the final response
```

---

## 8. Self-Correction / Fallback Mechanism

One of the important parts of the notebook is the **self-correction direction**.

The graph traversal function can return a signal when it cannot find a useful graph match:

```text
NO GRAPH MATCHES
FALLBACK REQUIRED
```

The agent is instructed not to immediately stop.

Instead, it should use another retrieval strategy:

```text
Graph Search
     ↓
No useful match
     ↓
Fallback
     ↓
Vector Search
     ↓
Retrieve semantic matches
     ↓
Generate answer
```

This is important because a real knowledge system cannot assume that one retrieval method will always work.

The concept can later be extended to more sophisticated correction mechanisms such as:

- query rewriting
- broader semantic search
- alternative Cypher queries
- multiple retrieval attempts
- result-quality evaluation
- answer verification
- retry limits
- confidence scoring
- human approval for uncertain cases

---

## 9. Why This Saves Technical Time

A system based on this architecture can reduce repetitive technical work.

For example, instead of manually:

```text
Search documentation
      ↓
Open multiple documents
      ↓
Find related information
      ↓
Check relationships
      ↓
Compare information
      ↓
Calculate values
      ↓
Prepare response
```

an agent can potentially perform:

```text
Natural-language request
        ↓
Agent
        ↓
Graph / Vector retrieval
        ↓
Tool execution
        ↓
Context synthesis
        ↓
Answer
```

This can be particularly useful for internal technical knowledge, documentation, troubleshooting information, architecture knowledge, and operational data.

The goal is not to remove technical expertise. The goal is to allow engineers to spend less time on repetitive information retrieval and more time on analysis and decision-making.

---

## 10. Potential Business Value

The same architecture can have business value because the time spent searching for internal information can become significant as an organization grows.

Potential benefits include:

### Faster information access

Employees can ask questions in natural language instead of searching through multiple knowledge sources manually.

### Reduced repetitive work

Common questions can be answered automatically using company-approved knowledge.

### Better knowledge utilization

Information stored in documents and structured relationships can be exposed through a single AI interface.

### More consistent answers

The system can retrieve information from a controlled knowledge source before generating an answer.

### Faster troubleshooting

An agent can retrieve related technical information and potentially perform additional checks automatically.

### Scalability of internal knowledge

As the knowledge graph grows, the same retrieval architecture can be extended rather than building a separate search workflow for every new information source.

---

## 11. Why We Start With a Small Dataset

The notebook intentionally uses a small demonstration dataset.

The purpose at this stage is to validate the **architecture and interaction between components**, not to benchmark a large enterprise knowledge base.

The important flow is:

```text
Documents
   ↓
Embeddings
   ↓
Neo4j Vector Index
   ↓
Graph Relationships
   ↓
LLM Tool Calling
   ↓
Retrieval
   ↓
Fallback / Self-Correction
   ↓
Answer
```

Once this flow is validated, the same architecture can be tested with a larger and more representative dataset.

---

## 12. LLM Selection and Latency Considerations

LLM selection should not be based only on answer quality.

For an agentic system, the following factors are also important:

- response latency
- tool-calling latency
- model capability
- context handling
- reliability
- cost
- token usage
- availability
- suitability for the specific task

A faster model can be valuable for an agent because one user request may require multiple LLM calls and tool calls.

For example:

```text
User request
    ↓
LLM call
    ↓
Tool call
    ↓
LLM call
    ↓
Fallback tool call
    ↓
LLM final answer
```

If every LLM call is slow, total agent latency can increase significantly.

Therefore, the LLM comparison/latency work should be viewed as an **engineering decision input** for selecting an appropriate model for future agentic workflows.

> Note: the current notebook contains the agent implementations and tool/retrieval workflow. Any five-model latency benchmark should be treated as a separate benchmark result unless those five models and their measurements are explicitly present in the notebook.

---

## 13. Technical Architecture

The current exploration can be represented as:

```text
                    ┌──────────────────┐
                    │     User Query   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    LLM / Agent   │
                    └────────┬─────────┘
                             │
                 ┌───────────┼───────────┐
                 │           │           │
                 ▼           ▼           ▼
          ┌──────────┐ ┌──────────┐ ┌─────────────┐
          │  Vector  │ │  Graph   │ │  Calculator │
          │  Search  │ │  Search  │ │    Tool     │
          └────┬─────┘ └────┬─────┘ └─────────────┘
               │            │
               └──────┬─────┘
                      ▼
              ┌───────────────┐
              │ Retrieved      │
              │ Context        │
              └───────┬───────┘
                      ▼
              ┌───────────────┐
              │ LLM Synthesis │
              └───────┬───────┘
                      ▼
              ┌───────────────┐
              │ Final Answer  │
              └───────────────┘
```

The self-correcting extension adds:

```text
Graph Search
     ↓
No useful result?
     ↓
Yes
     ↓
Vector Search
     ↓
Evaluate result
     ↓
Synthesize answer
```

---

## 14. Technical Benefits

From an engineering perspective, the approach demonstrates several useful capabilities:

- Neo4j can be used as a retrieval backend for GenAI workflows.
- Vector and graph retrieval can coexist.
- Embeddings can be generated outside the database and stored in Neo4j.
- LLMs can use Neo4j retrieval through tools.
- Tool calling enables an agent to perform actions instead of only generating text.
- Fallback logic can improve retrieval robustness.
- The architecture can be expanded without changing the fundamental knowledge representation.

This makes the notebook useful as a **technical proof of concept / exploration**, rather than simply an LLM demo.

---

## 15. Possible Extension

The current implementation can be extended in stages.

### Stage 1 — Better GraphRAG

Combine:

```text
Vector similarity
+
Graph relationships
+
LLM synthesis
```

Instead of choosing only one retrieval method, results from both methods can be combined and ranked.

### Stage 2 — Query Understanding

The agent can classify the request before retrieval:

```text
Question
  ↓
Determine intent
  ↓
Graph query / Vector query / Both
```

### Stage 3 — Retrieval Evaluation

The agent can evaluate whether retrieved information is sufficient:

```text
Retrieve
  ↓
Evaluate relevance
  ↓
Good → Generate answer
  ↓
Bad
  ↓
Rewrite query / change retrieval method
```

### Stage 4 — Multi-step Agent

The agent can execute several actions:

```text
Understand task
    ↓
Retrieve
    ↓
Traverse graph
    ↓
Calculate / process
    ↓
Validate
    ↓
Answer
```

### Stage 5 — Production Knowledge Sources

The small example dataset can eventually be replaced or supplemented with:

- technical documentation
- product documentation
- incident information
- tickets
- API documentation
- architecture information
- structured business data
- internal knowledge bases

This would make the system more representative of a real organizational knowledge assistant.

---

## 16. Future Direction — Self-Correcting Agentic GraphRAG System

A natural future direction from this exploration is a:

### **Self-Correcting Agentic GraphRAG System**

The idea is to combine:

```text
LLM
+
Neo4j Knowledge Graph
+
Embeddings
+
Vector Search
+
Graph Traversal
+
Tool Calling
+
Self-Correction
```

The system would not simply retrieve information once.

Instead, it could:

```text
User Question
      ↓
Understand intent
      ↓
Select retrieval strategy
      ↓
Retrieve from Neo4j
      ↓
Evaluate retrieved context
      ↓
Is context sufficient?
    /       \
  Yes        No
   ↓          ↓
Answer    Rewrite / fallback
              ↓
        Another retrieval
              ↓
        Evaluate again
              ↓
             Answer
```

This could eventually create an AI assistant that is more robust than a basic RAG pipeline because it can **choose, evaluate, and correct its own retrieval process**.

The notebook is therefore a foundation for exploring this direction rather than claiming that the complete production-grade system has already been implemented.

---

