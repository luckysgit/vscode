### What Was Built

An automated cybersecurity threat detection pipeline that ingests raw network flow telemetry into a graph database (Neo4j), represents network interactions as graph structures, and utilizes a Graph Neural Network (GraphSAGE) to classify communication flows as benign or malicious.

---

### Goal

To transition network intrusion detection from static, isolated tabular log analysis to context-aware graph modeling, identifying malicious patterns and lateral movements across interconnected network entities in real time.

---

### Dataset Used

* **Dataset:** UNSW-NB15 NetFlow threat dataset (accessed via Hugging Face).


* **Contents:** Real and synthesized network communications containing flow attributes (e.g., duration `dur`, source/destination bytes `sbytes`/`dbytes`, packet counts, TTL values, jitters) paired with binary threat labels (`Normal` vs. `Attack`).



---

### Architecture & Pipeline Flow

```
1. Hugging Face (UNSW-NB15 Data)
   │
   ▼
2. Graph Modeling & Ingestion (Neo4j AuraDB)
   ├── Nodes: Source and Destination IP Hosts
   └── Edges: COMMUNICATES_WITH (Carrying flow metrics: dur, sbytes, dbytes)
   │
   ▼
3. Graph Feature Extraction (PyTorch Geometric)
   ├── Node Features: Structural degree metrics (in-degree, out-degree)
   └── Edge Features: Normalized NetFlow telemetry vectors
   │
   ▼
4. Graph Neural Network (GraphSAGE Threat Classifier)
   ├── 2-Hop Neighbor Message Passing (Generates host contextual embeddings)
   └── Edge Classification Head: Concatenates [Source Node + Target Node + Flow Metrics]
   │
   ▼
5. Intelligence Feedback (Cypher Batch Writes)
   └── Annotates Neo4j edges with predicted threat scores and 'SUSPICIOUS' status flags

```

---

### How Embeddings Work

1. **Host Context (Node Embeddings):** GraphSAGE layers aggregate information across neighboring connected devices. A single machine's representation is shaped by the behavior of every device communicating with it.


2. **Flow Context (Edge Embeddings):** The model concatenates the learned source host representation, the target host representation, and the raw flow metrics into a unified vector: $[h_{\text{src}} \,\Vert{}\, h_{\text{dst}} \,\Vert{}\, e_{\text{flow}}]$.


3. **Classification:** A multi-layer perceptron analyzes this combined vector to output an attack probability.



---

### Technical Value

* **Topology-Aware Detection:** Captures structural attack footprints (such as port scanning, distributed denial of service, and lateral traversal) that standalone tabular classifiers fail to identify.
* **Neighborhood Correlation:** Resolves false positives by analyzing whether an unusual packet volume originated from an isolated host or a known malicious cluster.
* **Bidirectional Sync:** Operates directly with enterprise graph databases (Neo4j), enabling fast Cypher query inspections on high-risk subgraphs.



---

### Business Value

* **Reduced Alert Fatigue:** Correlates multi-hop network events into single malicious graph paths rather than triggering thousands of disconnected perimeter alerts.
* **Faster Incident Response (MTTR):** Security Operations Center (SOC) analysts can visually track the blast radius and isolate "Patient Zero" machines within Neo4j.
* **Proactive Asset Defense:** Automated tagging allows firewall and network orchestration tools to quarantine compromised subnets before critical data exfiltration occurs.