# Multi-Modal Counter-Terrorism Intelligence 

An automated system designed to identify covert threat cells by fusing cyber, digital communication, and financial indicators into a grounded investigation dossier.

---

### 1. Project Overview & Problem Statement

* **Siloed Detection:** Conventional security operations analyze network telemetry, malicious URLs, and financial transaction streams in isolated monitoring consoles.
* **Weak Signal Invisibility:** Sophisticated threat actors intentionally distribute low-signature actions across domains (e.g., an ordinary port scan, a URL delivery link, and an un-flagged monetary transfer) that appear benign when viewed separately.
* **Alert Fatigue & Hallucination Risk:** Manually pivoting between platforms causes significant latency. Furthermore, passing unstructured, raw event streams directly to language models leads to context window saturation, token truncation, and hallucinated findings.
* **Core Objective:** Build a fused architecture that ingests heterogeneous data streams, runs specialized domain models, normalizes event structures, builds an entity-relationship knowledge graph, and exposes evidence to an instruction-tuned LLM through a read-only Model Context Protocol (MCP) server.

```text
┌───────────────────────────────────────────────────────────────────────────┐
│                          MULTI-DATASET INGESTION                          │
├─────────────────────┬───────────────────────────────┬─────────────────────┤
│ 1. UNSW-NB15 NetFlow│ 2. Phishing URL Corpus        │ 3. ULB Credit Card  │
└──────────┬──────────┘───────────────┬───────────────┴──────────┬──────────┘
           │                          │                          │
           ▼                          ▼                          ▼
    [ Model A: XGBoost ]       [ Model B: TF-IDF + LR ]    [ Model C: XGBoost ]
           │                          │                          │
           └──────────────────────────┼──────────────────────────┘
                                      ▼
                       ┌──────────────────────────────┐
                       │   COMMON EVENT NORMALIZER    │
                       └──────────────┬───────────────┘
                                      ▼
                       ┌──────────────────────────────┐
                       │  ENTITY KNOWLEDGE GRAPH (NX) │
                       └──────────────┬───────────────┘
                                      ▼
                       ┌──────────────────────────────┐
                       │   READ-ONLY MCP TOOL SERVER  │
                       └──────────────┬───────────────┘
                                      ▼
                       ┌──────────────────────────────┐
                       │  LOCAL LLM INVESTIGATION     │
                       └──────────────┬───────────────┘
                                      ▼
                       ┌──────────────────────────────┐
                       │ FINAL EVIDENCE DOSSIER / SOC │
                       └──────────────────────────────┘

```

---

### 2. Pipeline Technology & Model Architecture

| Layer / Modality | Dataset / Source | Features & Embeddings | Storage & Topology Engine | Primary Model Architecture |
| --- | --- | --- | --- | --- |
| **Cyber Telemetry** | **UNSW-NB15** (49 features, 9 attack classes) | Numerical flow metrics / `GraphSAGE` topological vectors | NetworkX (Local) / **Neo4j** (Enterprise) | **XGBoost Classifier** (`max_depth=6`, `eval_metric="logloss"`) |
| **Digital Comms / URLs** | **Phishing URL Dataset** (Kaggle / Pirocheto corpus) | Character N-Gram (3–5) TF-IDF vectors / `BAAI/bge-m3` | **FAISS** (In-Memory) / **ChromaDB** / **Neo4j** | **Balanced Logistic Regression** |
| **Financial / Fraud** | **ULB Credit Card Fraud** (284,807 transaction records) | Standardized tabular features / `Node2Vec` embeddings | **Neo4j Property Graph** / **Qdrant** | **Cost-Sensitive XGBoost** (`scale_pos_weight`) |
| **Entity Extraction** | Unstructured CTI & Threat Reports | `BAAI/bge-large-en-v1.5` / `all-mpnet-base-v2` | **Neo4j Vector Store** / **Milvus** | **DeBERTa-v3** / **Qwen2.5-1.5B-Instruct** |
| **Investigation Co-Pilot** | Extracted multi-modal subgraphs | Topological event context via MCP JSON schema | Read-Only MCP Tool Server | **Qwen2.5-0.5B-Instruct** (Colab) / **Qwen2.5-7B** (Prod) |

---

### 3. Step-by-Step System Workflow

* **Step 1: Multi-Domain Data Ingestion:** Download benchmark feeds across network flows, suspicious URLs, and financial transactions, generating stratified train/test partitions.
* **Step 2: Domain-Specific Model Inference:** Execute independent classifiers optimized for tabular distribution, character n-gram lexical patterns, and severe class imbalance.
* **Step 3: Event Normalization:** Map discrete model predictions into a common JSON payload: `event_id`, `event_type`, `entity_id`, `risk_score`, and `source_engine`.
* **Step 4: Weighted Multi-Modal Risk Scoring:** Compute composite risk prioritizing cross-domain convergence:

$$\text{Composite Risk} = (\text{NetFlow} \times 0.40) + (\text{Financial} \times 0.35) + (\text{URL} \times 0.25)$$


* **Step 5: Knowledge Graph Construction:** Ingest normalized records into a directed graph structure, binding entities to events with `GENERATED_EVENT` edges and computing shared entity relationships.
* **Step 6: Controlled MCP Tool Abstraction:** Provide read-only diagnostic tools (`get_entity_modality_summary`, `get_entity_graph_topology`) to supply bounded context without unconstrained database queries.
* **Step 7: LLM Grounded Dossier Synthesis:** The reasoning LLM processes verified MCP outputs via ChatML templating to compile an incident assessment detailing attribution, signal breakdowns, and forensic next steps.

---

### 4. Planned Dataset & Telemetry Expansions

* **MITRE ATT&CK & STIX 2.1 CTI Reports:** Correlates detected IPs and payloads with known Advanced Persistent Threat (APT) groups, threat tactics, and intrusion sets.
* **Elliptic Bitcoin & Crypto Transaction Graphs:** Uncovers illicit funding conduits, un-hosted wallets, and transaction mixer patterns used for operational logistics.
* **Telecommunications CDRs & SMS Metadata:** Identifies burner phone coordination clusters and connects call frequencies with active cyber operations.
* **Host-Level Enterprise Telemetry (Sysmon, Zeek, eBPF):** Links network-level anomalies with endpoint process execution trees and command-line activity.

---

### 5. Business Value & Strategic Differentiation

* **Multi-Modal Threat Attribution:** Eliminates operational silos by uniting network telemetry, URL clicks, and financial funding trails into an auditable evidence chain.
* **Reduction of Alert Fatigue:** Correlates thousands of disconnected alerts into single connected entity graphs, cutting Mean Time to Respond (MTTR).
* **Defensible, Explainable AI:** Grounds all AI assessments in verifiable graph paths, providing the chain of custody required for lawful interventions.
* **Enterprise NDR Differentiation:** Advances beyond conventional anomaly sensors (e.g., Darktrace, ExtraHop) by incorporating a fused graph-agent fabric designed for complex intelligence missions.

---

### 6. Production Roadmap

* **Phase 1: Interactive Analyst Triage UI:** Provide an analyst interface (Streamlit or native `ipywidgets` with Pyvis) allowing real-time entity selection, visual subgraph exploration, and one-click dossier generation.
* **Phase 2: Persistent Graph Migration (Neo4j):** Replace transient in-memory graphs with production Neo4j property stores, replacing dictionary traversals with multi-hop Cypher queries:
```cypher
MERGE (e:Entity {id: $entity_id})
MERGE (ev:Event {id: $event_id, type: $event_type, risk_score: $risk_score, source: $source})
MERGE (e)-[:GENERATED_EVENT]->(ev);

```


* **Phase 3: Identity & Entity Resolution Engine:** Upgrade from deterministic modulo groupings to semantic resolution using shared subnets, registrant metadata, and embedding-based alias matching (`BAAI/bge-m3`).
* **Phase 4: Graph Data Science & Anomaly Detection:** Implement Louvain/Leiden community detection and Betweenness Centrality to surface hidden bridge nodes across communication and financial infrastructures.


7. Future Work & Production Roadmap
Plaintext
┌────────────────────────────────────────────────────────────────────────────┐
│                        FUTURE DATASET EXPANSIONS                           │
├──────────────────────────┬─────────────────────────┬───────────────────────┤
│ 1. CTI & STIX/TAXII      │ 2. Blockchain / Crypto  │ 3. Telecom CDR Feeds  │
│    (MITRE ATT&CK / OSINT)│    (Elliptic Bitcoin)   │    (Call Detail Logs) │
├──────────────────────────┼─────────────────────────┼───────────────────────┤
│ • Maps TTPs & actor      │ • Traces crypto-funded  │ • Maps covert comms & │
│   campaign infrastructure│   weapons & safehouses  │   burner phone rings  │
└──────────────────────────┴─────────────────────────┴───────────────────────┘
Dataset & Telemetry Expansion:

STIX 2.1 Threat Feeds & MITRE ATT&CK Reports: Map alerts directly to known Advanced Persistent Threat (APT) groups, tactics, and adversary techniques.

Elliptic Bitcoin & Crypto Transaction Graphs: Uncover cryptocurrency mixers and un-hosted wallets used to fund terrorist logistics.

Telecommunications CDRs & SMS Metadata: Trace burner phone networks and isolate cross-border communication spikes.

Host-Level Enterprise Telemetry (Sysmon, Zeek, eBPF): Correlate network alerts with process execution trees and command-line execution traces.

Architecture & Infrastructure Scalability:

Persistent Neo4j Knowledge Graph Migration: Transition from transient Python NetworkX instances to production Neo4j property graph clusters with Cypher-optimized graph queries:

Cypher
MERGE (e:Entity {id: $entity_id})
MERGE (ev:Event {id: $event_id, type: $event_type, risk_score: $risk_score, source: $source})
MERGE (e)-[:GENERATED_EVENT]->(ev);
Semantic Identity & Entity Resolution: Upgrade synthetic modulo entity mapping to real-world resolution using shared IP subnets, BGP Autonomous System Numbers (ASNs), WHOIS records, and text embedding similarity (BAAI/bge-m3).

Graph Data Science (GDS) Algorithms: Apply Louvain/Leiden community detection and Betweenness Centrality to surface hidden broker nodes linking digital infrastructure to physical entities.

Production Analyst UI: Package the pipeline into a persistent web console (via FastAPI and React/Streamlit) with interactive visual subgraphs, real-time threat streaming, and human-in-the-loop analyst feedback logging.

------------------------------------------------------------------------------------

## next step:

To operationalize these three future dataset expansions, each data modality must be defined by its mathematical features, schema integration, Graph ML algorithms, and specific read-only MCP tool interfaces.

---

### Dataset Architecture & Expansion Specifications

| Expansion Modality | Benchmark Dataset / Standard | Native Feature Representation | Storage & Graph Schema | Core ML / Graph Model |
| --- | --- | --- | --- | --- |
| **1. CTI & STIX/TAXII** | **MITRE ATT&CK Enterprise Matrix** / OpenCTI STIX 2.1 JSON Feeds | Dense text embeddings (`BAAI/bge-m3`, 1024-d) over TTP descriptions and technique scopes | Heterogeneous Graph (`:ThreatActor`, `:AttackPattern`, `:Malware`, `:Indicator`) with typed relationships (`:USES`, `:ATTRIBUTED_TO`, `:TARGETS`) | **Link Prediction via RGCN** (Relational Graph Convolutional Network) + Semantic Cosine Similarity |
| **2. Blockchain / Crypto** | **Elliptic Bitcoin Dataset** (203,769 transactions, 234,355 directed edges) | 166 local & 1-hop topological attributes (inputs/outputs, fees, neighbor variances) + temporal step | Directed Transaction Graph (`:Transaction`, `:WalletAddress`) with `:TRANSFERS_BTC` edges | **Temporal GNN** (EvolveGCN / GraphSAGE) or Cost-Sensitive XGBoost on 1-hop topological aggregations |
| **3. Telecom CDR Feeds** | **Synthetic Telecom Call Detail Records (CDR)** & Cell Tower Triangulation | Tabular sequence features (call duration, IMEI/IMSI entropy, night-time ratio, geo-velocity) | Multi-DiGraph (`:Subscriber`, `:CellTower`, `:IMEI`) with `:CALLS`, `:SMS`, and `:ATTACHED_TO` edges | **Louvain Community Detection** + Geo-Velocity Anomaly Isolation + Isolation Forest on burst calling |

---

### In-Depth Modality Breakdowns

#### 1. CTI & STIX 2.1 (MITRE ATT&CK / OSINT)

* **Operational Goal:** Map observed network anomalies and phishing URLs to known Advanced Persistent Threat (APT) campaigns, intrusion sets, and tactics, techniques, and procedures (TTPs).
* **Graph Schema Binding:**
* **Nodes:** `ThreatActor` (e.g., `APT28`, `Lazarus`), `AttackPattern` (e.g., `T1566.002 Spearphishing Link`), `Malware` (e.g., `CobaltStrike`).
* **Relationships:**
```cypher
(:ThreatActor)-[:USES]->(:AttackPattern)
(:ThreatActor)-[:DEPLOYS]->(:Malware)
(:Indicator {type: "url"})-[:INDICATES]->(:AttackPattern)

```




* **Integration Logic:** When the phishing URL model flags a malicious URL, its structural features (TLD, lexical pattern) are queried against the vector index of STIX Indicators using embedding similarity to assign probable actor attribution.

#### 2. Blockchain & Crypto Forensics (Elliptic Bitcoin)

* **Operational Goal:** Trace ransom payments, weapons procurement, and operational funding chains moving through mixers, peel chains, and un-hosted wallets.
* **Graph Schema Binding:**
* **Nodes:** `WalletAddress`, `TxNode` (with properties: `tx_id`, `amount_btc`, `timestep`, `fee`).
* **Relationships:**
```cypher
(:WalletAddress)-[:SENDS]->(:TxNode)-[:RECEIVES]->(:WalletAddress)
(:Entity)-[:CONTROLS_WALLET]->(:WalletAddress)

```




* **Detection Mechanism:** Temporal Graph Neural Networks (GNNs) or GCNs flag illicit sub-graphs (`Class 1`) that display transaction splitting (structuring) across multiple hops within narrow time windows.

#### 3. Telecommunications CDR Feeds (Call Detail Records)

* **Operational Goal:** Uncover burner phone networks, sleeper cell coordination rings, and geographic co-location of suspected operatives.
* **Graph Schema Binding:**
* **Nodes:** `MSISDN` (Phone Number), `IMEI` (Device Hardware ID), `CellTower` (Latitude, Longitude, Azimuth).
* **Relationships:**
```cypher
(:MSISDN)-[:CALLS {duration: 142, timestamp: "..."}]->(:MSISDN)
(:MSISDN)-[:ATTACHED_TO]->(:CellTower)
(:MSISDN)-[:USED_DEVICE]->(:IMEI)

```




* **Detection Mechanism:**
* **Burner Identification:** High IMEI churn (multiple SIM cards sequentially inserted into a single handset).
* **Co-Travel / Co-Location:** Identifying pairs of MSISDNs that consistently switch cell towers in geographic synchrony without placing calls directly to each other.



---

### Extended Common Event Schema

To support all 6 modalities without altering the core pipeline, the normalization layer accepts this unified JSON schema:

```json
{
  "event_id": "CRYPTO_TX_230425980",
  "event_type": "crypto_transfer",
  "entity_id": "ENTITY_48",
  "risk_score": 0.942,
  "source": "elliptic_gnn_model",
  "metadata": {
    "network": "bitcoin",
    "amount_crypto": 4.82,
    "hops_to_mixer": 1,
    "temporal_step": 34
  }
}

```

```json
{
  "event_id": "CDR_CALL_883012",
  "event_type": "telecom_anomaly",
  "entity_id": "ENTITY_48",
  "risk_score": 0.887,
  "source": "cdr_burner_detector",
  "metadata": {
    "imei_churn_count": 4,
    "night_call_ratio": 0.92,
    "cell_id": "TOWER_404_SEC_3"
  }
}

```

---

### Updated Fused Risk Formula

The expanded composite risk score accounts for cross-domain operational correlation across cyber, physical, and financial signals:

$$\text{Composite Risk} = \sum_{m \in M} w_m \cdot R_m + \gamma \cdot \mathbb{I}(\text{distinct sources} \ge 3)$$

Where weights are calibrated to operational urgency:

* $\text{NetFlow Cyber Telemetry} = 0.25$
* $\text{Phishing / Delivery URLs} = 0.15$
* **CTI & STIX TTP Attribution = 0.15**
* $\text{Banking / Credit Card Fraud} = 0.15$
* **Blockchain / Crypto Transactions = 0.15**
* **Telecom CDR / Physical Location = 0.15**
* Multi-source correlation booster ($\gamma = 0.30$ bonus when $\ge 3$ distinct sources flag the entity).

---

### Expanded Model Context Protocol (MCP) Tool Specifications

To ground the Qwen LLM in these new domains, the read-only MCP server introduces three purpose-built diagnostic endpoints:

#### 1. `get_crypto_peel_chain(wallet_address: str, max_hops: int = 3) -> dict`

* **Input:** Target cryptocurrency address.
* **Payload Output:** Returns the forward and backward transaction trace, identifying high-risk transaction hops, known illicit cluster tags (e.g., Hydra, Wasabi Mixer), and total volume transferred.

#### 2. `get_telecom_co_location(msisdn: str, time_window_hours: int = 24) -> dict`

* **Input:** Target phone identifier.
* **Payload Output:** Returns device IMEI churn frequency, cell tower transit paths, and identifiers of other devices appearing within the same sector within a 15-minute window.

#### 3. `get_threat_actor_attribution(indicator: str) -> dict`

* **Input:** Flagged IP, Domain, or File Hash.
* **Payload Output:** Executes STIX graph traversal to return associated APT groups, matching MITRE ATT&CK technique IDs (e.g., `T1071.001 - Web Protocols`), and historical campaign names.

---

### Implementation Next Step

Choose which modality to implement first into our Google Colab prototype:

1. **Blockchain Module (Elliptic Bitcoin):** Download the transaction edge list, run the XGBoost/GNN classifier, and integrate crypto-peel edges into the NetworkX knowledge graph.
2. **Telecom CDR Simulator:** Generate a structured Call Detail Record event stream with burner phone and cell tower co-location logic.
3. **STIX 2.1 Threat Actor Linker:** Ingest MITRE ATT&CK TTPs and build semantic vector attribution for the existing URL and NetFlow indicators.