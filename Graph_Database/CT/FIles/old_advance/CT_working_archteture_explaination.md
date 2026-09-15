```
                          MULTI-MODAL THREAT INTELLIGENCE FLOWCHART
                          ==========================================

  [ INGESTION & TRAINING PHASE ]                         [ MCP INVESTIGATION & TRIAGE ]
  ------------------------------                         ------------------------------
   
    ┌──────────────────────┐                                 ┌──────────────────────┐
    │  1. Multi-Datasets   │                                 │   6. Analyst Query   │
    │ (NetFlow/URLs/Fraud) │                                 │ (Target: ENTITY_101) │
    └──────────┬───────────┘                                 └──────────┬───────────┘
               │                                                        │
               ▼                                                        ▼
    ┌──────────────────────┐                                 ┌──────────────────────┐
    │ 2. Feature Extractor │                                 │  7. Query Controller │
    │(One-Hot/TF-IDF/Scale)│                                 │ (Read-Only MCP Tool) │
    └──────────┬───────────┘                                 └──────────┬───────────┘
               │                                                        │
               ▼                                                        │ get_entity_events()
    ┌──────────────────────┐                                            │ get_entity_graph_metrics()
    │  3. ML Classifiers   │                                            ▼
    │ (XGBoost / LogReg)   │                              ┌───────────────────────────┐
    └──────────┬───────────┘ ════════════════════════════►│ 5. Relational Graph DB    │
               │             (Populate Graph Topology)    │   (NetworkX / Neo4j)      │
               ▼                                          └─────────────┬─────────────┘
    ┌──────────────────────┐                                            │
    │ 4. Event Normalizer  │                                            │ Returns JSON Evidence
    │ (Standardized JSON)  │                                            ▼
    └──────────┬───────────┘                                 ┌──────────────────────┐
               │                                             │ 8. ChatML Formatter  │
               └────────────────────────────────────────────►│ (Context & Guidelines│
                                                             └──────────┬───────────┘
                                                                        │
                                                                        ▼
                                                             ┌──────────────────────┐
                                                             │ 9. LLM Reasoner      │
                                                             │ (Qwen2.5-0.5B/1.5B)  │
                                                             └──────────┬───────────┘
                                                                        │
                                                                        ▼
                                                             ┌──────────────────────┐
                                                             │ 10. Threat Dossier   │
                                                             │(Attribution & Actions│
                                                             └──────────────────────┘

```

---

### Component-by-Component Technical Breakdown

#### 1. Data Ingestion & Download

* **Libraries:** `requests`, `datasets` (Hugging Face)
* **Core Classes & Functions:**
* `requests.get(url, stream=True)`: Downloads external benchmark datasets (such as ULB Credit Card Fraud from Zenodo) efficiently in stream chunks.
* `datasets.load_dataset("repo/name", split="train[:N]")`: Streams slices of `UNSW-NB15` (Network Flow) and `pirocheto/phishing-url` datasets into memory.


* **Purpose:** Collects raw data from three isolated intelligence domains without manual file handling.

---

#### 2. Feature Extraction & Engineering

* **Libraries:** `pandas`, `sklearn.feature_extraction.text`, `sklearn.model_selection`
* **Core Classes & Functions:**
* `pd.get_dummies(X_net)`: Converts categorical protocol and service fields (`proto`, `service`, `state`) into numerical one-hot vectors.
* `TfidfVectorizer(analyzer="char", ngram_range=(3, 5), max_features=10000)`: Extracts sub-word character n-grams to capture lexical patterns in phishing domains.
* `train_test_split(..., stratify=y, test_size=0.20)`: Splits data into train and test sets while preserving class distribution across imbalanced data.


* **Purpose:** Transforms unstructured text and tabular network logs into numerical matrices consumable by machine learning classifiers.

---

#### 3. Domain Model Inference & Probability Scoring

* **Libraries:** `xgboost`, `sklearn.linear_model`
* **Core Classes & Functions:**
* `XGBClassifier(n_estimators=50, max_depth=5, scale_pos_weight=...)`: Gradient-boosted decision trees trained on NetFlow and imbalanced financial transactions.


* `LogisticRegression(class_weight="balanced", max_iter=500)`: Fast linear classifier predicting malicious URL probabilities.
* `model.predict_proba(X_test)[:, 1]`: Computes calibrated continuous anomaly risk scores ($\in [0.0, 1.0]$) for each event.




* **Purpose:** Detects point-level domain anomalies independently across network flows, URL requests, and transactions.

---

#### 4. Common Event Normalization & Weighted Fusion

* **Libraries:** `pandas`, `numpy`
* **Core Classes & Functions:**
* `pd.DataFrame({"event_id": ..., "event_type": ..., "entity_id": ..., "risk_score": ..., "source": ...})`: Converts domain-specific outputs into a unified JSON event schema.


* `pd.concat([...], ignore_index=True)`: Merges all multi-domain event streams into a single dataset.


* `DataFrame.groupby("entity_id").agg(...)`: Aggregates risk scores and counts distinct intelligence sources per entity to calculate cross-modal correlation.




* **Purpose:** Eliminates domain silos by enforcing a standardized representation for all telemetry events.



---

#### 5. Relational Knowledge Graph Engine

* **Libraries:** `networkx` (Local Prototyping) / `neo4j` (Production)


* **Core Classes & Functions:**
* `nx.MultiDiGraph()`: Instantiates a multi-directed graph supporting multiple relationship types between the same nodes.


* `G.add_node(id, node_type="entity" | "event", **attrs)`: Creates entity and event nodes containing risk attributes.


* `G.add_edge(entity, event, relation="GENERATED_EVENT")`: Links entities to their corresponding observations.


* `nx.connected_components(G.to_undirected())`: Identifies structural clusters and communities of connected threat actors and assets.




* **Purpose:** Replaces flat tables with an interconnected topology that enables multi-hop path analysis and blast-radius tracing.



---

#### 6 & 7. Model Context Protocol (MCP) Read-Only Tool Server

* **Libraries:** `json`, Standard Python Classes
* **Core Classes & Functions:**
* `MockMCPToolServer(events_df, graph)`: Acts as an isolated abstraction layer between the database and the LLM.


* `mcp_server.get_entity_modality_summary(entity_id)`: Summarizes total event counts, maximum risk scores, and top event samples per modality into a compact JSON object.
* `mcp_server.get_entity_graph_topology(entity_id)`: Extracts node degree centrality and connected subgraphs from the graph engine.


* **Purpose:** Provides bounded, structured evidence queries to the LLM while preventing uncontrolled database access or token context overflow.



---

#### 8 & 9. LLM Prompt Formulation & Inference

* **Libraries:** `transformers`, `torch`
* **Core Classes & Functions:**
* `AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")`: Tokenizes the structured ChatML prompt without corrupting whitespace formatting.
* `AutoModelForCausalLM.from_pretrained(..., dtype=torch.float16, device_map="auto")`: Loads an instruction-tuned small language model optimized for low RAM footprint.


* `pipeline("text-generation", model=model, tokenizer=tokenizer)`: Coordinates prompt submission and autoregressive text generation.
* `pipeline(prompt, max_new_tokens=450, do_sample=False)`: Generates deterministic, hallucination-free analytical assessments based exclusively on provided MCP evidence.




* **Purpose:** Synthesizes multi-source evidence into a human-readable intelligence assessment.



---

#### 10. Final Multi-Modal Evidence Dossier

* **Output Format:** Markdown-formatted Threat Intelligence Briefing


* **Generated Sections:**
* **Executive Attribution:** Assesses campaign severity and cross-domain correlation status.


* **Modality Evidence Breakdown:** Summarizes specific NetFlow anomalies, URL threats, and financial structuring records.


* **Graph Topology Context:** Outlines node connectivity and multi-hop relationships.


* **Actionable Forensic Containment:** Recommends concrete operational actions (e.g., PCAP slices, DNS sinkholing, account freezes).




