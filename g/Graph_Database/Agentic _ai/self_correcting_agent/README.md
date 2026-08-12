
# Self-Correcting Agentic GraphRAG Pipeline

An enterprise-grade, autonomous GraphRAG system built with **Neo4j** and **Groq (Llama-3.3-70B-Versatile)**. The pipeline combines HNSW vector similarity search, Cypher graph traversals, and deterministic Python execution tools with dynamic self-correction and fallback capabilities.

---

## Prerequisites

* **Python:** Version 3.10 or higher
* **Neo4j Database:** Neo4j 5.x installed locally (via Docker or standalone Community Edition) or a Neo4j AuraDB instance.
* **Groq API Key:** Free API key from [console.groq.com/keys](https://console.groq.com/keys).

---

## Project Structure

```text
graphrag-agentic-pipeline/
├── README.md                  # Project overview and setup instructions
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Files excluded from Git tracking
├── config/
│   └── settings.py            # Environment configuration & credentials loader
├── notebooks/
│   ├── 01_graphrag_benchmark.ipynb       # Baseline GraphCypherQAChain benchmark
│   └── 02_agentic_graphrag_pipeline.ipynb # Self-correcting Agentic GraphRAG notebook
├── src/
│   ├── __init__.py
│   ├── database/
│   │   └── neo4j_client.py    # Neo4j driver, HNSW index setup, & ingestion
│   ├── tools/
│   │   ├── cypher_tools.py    # Graph traversal tool with fallback hints
│   │   ├── vector_tools.py    # HNSW vector search tool
│   │   └── calc_tools.py      # Python math evaluation tool
│   └── agent/
│       └── groq_agent.py      # ReAct agent execution loop & self-correction
└── docs/
    └── system_architecture.png

```

---

## Setup & Installation

### 1. Extract or Clone the Project

Extract `graphrag-agentic-pipeline.zip` or clone the repository to your local directory:

```bash
cd graphrag-agentic-pipeline

```

### 2. Create and Activate a Virtual Environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate

```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt

```

### 4. Configure Environment Variables

Copy `.env.example` to create a `.env` file in the project root:

```bash
cp .env.example .env

```

Open `.env` and fill in your actual credentials:

```env
GROQ_API_KEY=gsk_your_actual_groq_api_key
NEO4J_URI=bolt://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

```

---

## Starting the Neo4j Database

Ensure your Neo4j instance is running and reachable at the configured URI (`bolt://127.0.0.1:7687`).

### Option A: Via Docker (Recommended)

```bash
docker run -d \
  --name neo4j-agent \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.18.0-community

```

### Option B: Via Neo4j Desktop / Server Binary

```bash
# Start your local server binary
./neo4j-community-5.18.0/bin/neo4j start

```

---

## Running the Application

### Method 1: Command Line Execution (CLI Agent)

Run the agent pipeline directly from your terminal:

```bash
python -m src.agent.groq_agent

```

**Example CLI Execution Output:**

```text
🎯 User Goal: Search the knowledge graph for Neo4j features and calculate 15% of 248.85s latency.
==================================================

🔄 [Iteration 1] Agent Thinking...
🛠️ Agent Action: Executing `graph_cypher_traversal` with args: {'entity_name': 'Neo4j features'}
📥 Tool Output:
NO GRAPH MATCHES for 'Neo4j features'. FALLBACK REQUIRED: Call 'vector_index_search' with a broader query for semantic retrieval.

🔄 [Iteration 2] Agent Thinking...
🛠️ Agent Action: Executing `vector_index_search` with args: {'query': 'Neo4j features'}
📥 Tool Output:
- Neo4j Community Edition supports native HNSW vector indexes without enterprise licensing. (score: 0.8)
- GraphRAG combines vector search with knowledge graph traversals to give LLMs structured context. (score: 0.69)

🛠️ Agent Action: Executing `python_calculator` with args: {'expression': '248.85 * 0.15'}
📥 Tool Output:
37.3275

🔄 [Iteration 3] Agent Thinking...

✅ Final Answer Generated:
--------------------------------------------------
The search for Neo4j features in the knowledge graph did not yield direct matches, so a vector search was performed instead. This revealed that Neo4j Community Edition supports native HNSW vector indexes without enterprise licensing. Additionally, 15% of 248.85s latency is 37.3275s.

```

### Method 2: Running in Jupyter Notebooks

To run interactive explorations, launch Jupyter Lab or Notebooks:

```bash
jupyter lab

```

1. Navigate to `notebooks/01_graphrag_benchmark.ipynb` to evaluate baseline single-pass Cypher QA chains.
2. Navigate to `notebooks/02_agentic_graphrag_pipeline.ipynb` to run the self-correcting agent step-by-step.

---

## Troubleshooting

* **ConnectionRefusedError `[Errno 111]`:** Your local Neo4j database is stopped. Ensure Neo4j is running via Docker or `./neo4j start` before running the agent.
* **AuthError / Unauthorized:** Verify that `NEO4J_USERNAME` and `NEO4J_PASSWORD` in your `.env` match your Neo4j instance configuration.
* **Groq API Key Invalid:** Check [console.groq.com](https://console.groq.com) to confirm your key is active and correctly set in `.env`.