This notebook JSON output captures the initialization and interactive rendering of your **6-Modality Counter-Terrorism Intelligence Platform**. It documents three distinct execution phases: the background data pull, model weight loading, and the live triage dashboard.

---

### 1. Ingestion of Multi-Modal Benchmark Datasets (Cell 2 Output)

The initial progress bars show the notebook downloading raw dataset files directly into memory from Hugging Face Hub:

* **Phishing URL Corpus (`pirocheto/phishing-url`):** Ingested `data/train.parquet` (789 kB) and `data/test.parquet` (431 kB), generating 7,658 training records and 3,772 test records.


* **Network Flow Telemetry (`Mouwiya/UNSW-NB15`):** Downloaded two large parquet shards totaling ~230 MB (`train-00000` at 124 MB and `train-00001` at 106 MB), generating 2,280,090 raw NetFlow records.


* **Completion Message:** `✅ Successfully cached 6-Modality Intelligence Graph in /content/fusion_cache.pkl!` confirms that all six models (NetFlow, URL, Credit Card, MITRE CTI, Elliptic Crypto, and Telecom CDR) executed and their outputs were written into the cached graph.



---

### 2. Low-Resource Model Weights Loading (Cell 4 Top Output)

Cell 4 sets up the local inference copilot (`Qwen/Qwen2.5-0.5B-Instruct`):

* Ingested configuration and tokenizer tables (`config.json`, `tokenizer_config.json`, `vocab.json` at 2.78 MB, and `merges.txt` at 1.67 MB).


* Downloaded and reconstructed the core neural network weights (`model.safetensors` at 988 MB).


* Loaded all 290 tensor layers in 2.1 seconds (~134 it/s), preparing the LLM for localized inference without external cloud APIs.



---

### 3. The Live Interactive Analyst Workbench (Cell 4 Rendered View)

The remaining widgets compose the active triage dashboard:

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Suspect Target: [ ENTITY_45 ▼ ]     [ 🛡️ Execute 6-Modality MCP Dossier ]  │
├────────────────────────────────────────────────────────────────────────────┤
│ Target ID: ENTITY_45  |  Composite Risk: 3.039  |  Total Evidence: 53      │
│ Corroborating Modality Sources: 6/6 (CRITICAL CONVERGENCE)                 │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│                           [Interactive Pyvis Graph]                        │
│                 🔴 ENTITY_45 (Target Suspect Core Hub)                     │
│                 ├── 🟢 TX_45 ... TX_795 (High-velocity fiat withdrawals)   │
│                 ├── 🟡 URL_45 ... URL_495 (Malicious delivery domains)     │
│                 └── 🔵 NET_45 ... NET_445 (Anomalous NetFlow scans)        │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘

```

* **Interactive Controls (`HBoxModel`):** Displays the target suspect selector populated with 50 entities (`ENTITY_45`, `ENTITY_2`, `ENTITY_14`, etc.) next to the red **"Execute 6-Modality MCP Dossier"** button.


* **Active Suspect Banner (`ENTITY_45`):**
* **Composite Risk (3.039):** A critical score driven by cross-domain accumulation and the multi-source convergence booster.


* **Corroborating Modality Sources (6/6):** Confirms that all six independent operational engines detected activity mapped to this suspect.


* **Total Evidence Events (53):** The suspect is connected to 53 distinct anomalous events in the knowledge graph.




* **Topology Canvas (Embedded Pyvis HTML):** Renders the target suspect `ENTITY_45` as a central red node (`#ef4444`, size 26) linked via directed edges to its peripheral indicators:


* 🟢 **Green Nodes (`TX_*`):** Financial fraud events, such as `TX_245` (Risk Score: 0.863).


* 🟡 **Yellow Nodes (`URL_*`):** Suspicious URLs, such as `URL_245` (Risk Score: 0.947) and `URL_395` (Risk Score: 0.968).


* 🔵 **Blue Nodes (`NET_*`):** NetFlow scan telemetry, such as `NET_95` (Risk Score: 0.944).




* **Investigation Output Slot (`OutputModel`):** The final empty container is primed to display the Qwen-generated threat assessment dossier as soon as you click the **"Execute 6-Modality MCP Dossier"** button.