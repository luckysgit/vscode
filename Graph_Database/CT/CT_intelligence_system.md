# CT_intelligence_archtecture

The idea is to build a multimodal threat intelligence platform rather than relying on a single detection model. We collect observations from physical sensors such as RGB cameras, thermal and Wi-Fi sensing, along with cyber telemetry, CTI, OSINT, financial and geospatial data. Each modality has a specialized model, for example YOLO for object detection, speech models for audio, UEBA for cyber behavior, and graph-based models for relationships.

These outputs are normalized into events and passed through entity resolution and temporal correlation. Neo4j becomes the central knowledge graph where we connect people, devices, locations, events, organizations and other entities over time. GNNs can then detect graph anomalies, communities and previously unseen relationships.

On top of that, we use GraphRAG and an LLM for investigation and explanation. MCP acts as the tool interface, allowing the agent to query Neo4j, SIEM, CTI and other approved systems instead of having direct uncontrolled access. The final result is an evidence-backed threat assessment and investigation workflow, with human approval before high-impact actions.

So the key innovation is not one model. It is the correlation of multiple independent modalities into one temporal intelligence graph.

### Integrated Sensing & Intelligence Architecture

| Intelligence / Sensor Layer | Core Technologies & Modern Frameworks | Deep-Dive Technical Mechanics & Cyber Dimensions |
| --- | --- | --- |
| **Edge Object Detection (YOLO)** | YOLOv8 / YOLOv10 / YOLOv11 / YOLO-World, TensorRT, ONNX Runtime, ByteTrack, BoT-SORT | Real-time bounding box regression, keypoint estimation, zero-shot open-vocabulary object grounding; cyber edge deployment on embedded micro-NPU/TPUs for local perimeter surveillance without cloud latency. |
| **Face Detection & Verification** | RetinaFace, SCRFD, MTCNN, ArcFace, AdaFace, CosFace, MagFace | Feature pyramid networks (FPN) for scale-invariant facial landmark localization; deep metric learning via additive angular margin loss for high-dimensional 512-D identity embedding generation and 1:N biometric gallery search. |
| **Thermal Biometrics & Cross-Modal Vision** | Radiometric LWIR/MWIR, Thermal Vascular Extraction, CycleGAN, Contrastive Cross-Spectral Loss (CLIP-style) | Extracts subcutaneous arterial heat maps invariant to external illumination; applies generative neural networks to map thermal matrices into synthetic visible-spectrum RGB embeddings for cross-modal matching. |
| **Radio Frequency & Wi-Fi Sensing (CSI)** | Wi-Fi Channel State Information (CSI), Wi-Fi DensePose, mmWave FMCW Radar, Micro-Doppler signature analysis | Measures subcarrier amplitude and phase distortions in multipath 2.4/5/6 GHz signals; constructs 3D skeletal DensePose through non-line-of-sight (NLOS) barriers (walls/smoke) to track human presence, posture, and micro-vitals (respiration) without optical line of sight. |
| **Physical & Video Behavior** | Spatio-Temporal Graph CNNs (ST-GCN), 3D ResNet, SlowFast, Anomaly Detection Autoencoders | Extracts spatial joint hierarchies over temporal windows to identify anomalous actions (loitering, violent motion, object placement/abandonment, barrier breach). |
| **Facial Behavior & Micro-Expressions** | Action Unit (FACS) recognition, OpenFace, 3D Morphable Models (3DMM), Vision Transformers (ViT) | Quantifies localized muscle contractions (micro-expressions), pupil dilation, and gaze vectors for cognitive load estimation, stress detection, and deepfake/presentation attack detection (PAD). |
| **Speech & Audio Forensics** | Whisper, Conformer ASR, WavLM, Audio Spectrogram Transformers (AST), Voice Biometrics | End-to-end acoustic feature extraction, speaker diarization, vocal tract biometrics, anti-spoofing synthetic voice detection, and paralinguistic distress/stress analysis. |
| **Text & Intent Intelligence** | Fine-tuned LLMs, Sentence Transformers, DeBERTa, Named Entity Recognition (NER), Intent Classifiers | Semantic vector search, role and relation extraction from intercepted text, sentiment analysis, radicalization linguistic markers, and encoded communication decoding. |
| **Social / OSINT & Online Footprint** | Spiderfoot, Maltego, Scrapy, Graph Neural Networks (GNN), Sockpuppet/Botnet Trackers | Cross-platform digital footprinting, automated dark web/forum scraping, Telegram channel parsing, botnet coordination tracking, and metadata extraction (EXIF, PGP keys). |
| **Cyber Behavior (SOC/XDR)** | SIEM (Splunk, Elastic), XDR (CrowdStrike, Sentinel), UEBA, eBPF telemetry, Sigma/YARA-L rules | Kernel-level telemetry collection via eBPF, process tree lineage analysis, lateral movement detection, and unsupervised behavioral baseline deviation modeling. |
| **Threat Intelligence (CTI)** | MISP, OpenCTI, MITRE ATT&CK mapping, STIX/TAXII pipelines, C2 infrastructure tracking | Ingestion and normalization of IOCs (hashes, IPs, domains) and TTPs; automated graph mapping of Advanced Persistent Threat (APT) campaigns and vulnerability exploitation paths. |
| **Network Relationships & Graph Analytics** | Neo4j, Amazon Neptune, NetworkX, GraphSAGE, Entity Resolution (Zenz-style matching) | Heterogeneous graph analytics for link prediction, shortest path analysis, community detection (Louvain/Leiden), and resolving disparate real-world/cyber entities into unified threat clusters. |
| **Financial Behavior & AML** | GNN-based AML detection, Chainalysis, Elliptic, Transaction Graph Monitoring, Rules Engines | Detection of structuring (smurfing), mixing services, nested exchange hops, sanctioned crypto wallet interactions, and illicit fiat-to-crypto bridging. |
| **Geospatial & Location Intelligence** | PostGIS, QGIS, Movement Graph Analytics, Cell-site dumps, ADS-B & AIS tracking | Spatiotemporal clustering (DBSCAN), trajectory co-traveler identification, geofence anomaly alerts, and RF direction-finding triangulation. |
| **Multimodal Fusion Engine** | Late-fusion Ensembles, Cross-Attention Transformers, Joint Latent Embeddings (ImageBind/Multimodal LLMs) | Projects heterogeneous inputs (CSI RF vectors + Thermal + Video + Audio + Network Logs) into a unified vector space, resolving cross-domain temporal and semantic correlations. |
| **AI Orchestration & Autonomous Action** | Model Context Protocol (MCP), LangGraph, AutoGen, SOAR (Cortex XSOAR, Tines) | Autonomous execution pipelines where agentic LLMs query tool APIs (SIEM, firewall, drone dispatch, biometric search), reason over multimodal threat vectors, and execute playbook actions. |

---

### End-to-End Surveillance Pipeline Integration

```
[Raw Physical Sensors] ──► [Feature Extraction] ──────┐
 • Thermal (LWIR)           • Vascular/Face Embeddings │
 • Optical RGB (YOLO)       • Bounding Box / Keypoints │
 • Wi-Fi CSI (DensePose)    • Through-Wall 3D Skeletons│
                                                       ├──► [Cross-Modal Fusion Engine] ──► [Agentic SOAR / Threat Graph]
[Raw Cyber/Data Feeds] ──► [Behavioral Modeling]       │    (Joint Vector Space & Graph)     (Automated Alert & Containment)
 • NetFlow / SIEM Logs      • UEBA Anomalies           │
 • Financial Transactions   • AML Sub-Graph Walks      │
 • CTI / OSINT Feeds        • Entity Resolution        │
                                                       ┘

```

1. **RF/Optical Cross-Cueing:** Wi-Fi CSI senses human movement behind an obstacle or in dense smoke, generating a preliminary 3D pose and vector trajectory.
2. **Line-of-Sight Acquisition:** Once the subject enters the field of view, high-speed YOLO models localize the body, while specialized face extractors (RetinaFace/ArcFace) crop the facial boundaries.
3. **Cross-Spectral Matching:** In low-light or masked environments, LWIR thermal sensors capture vascular contours, projecting them through a cross-modal embedding space into the visible-spectrum identity database.
4. **Entity Resolution & Autonomous Triage:** The resolved identity feeds into the Multimodal Graph Engine, instantly correlating physical presence with cyber logs (active VPN sessions, badge access, device MACs) and transaction histories to score threat probability.


------------------------------------------------------------------------------------------------------



This production-grade system architecture unifies physical edge sensors (YOLO, Thermal, Wi-Fi CSI), cyber telemetry (eBPF, SIEM/XDR), OSINT, and financial feeds into an automated Threat Knowledge Graph powered by Graph Neural Networks (GNNs) and Agentic Orchestration.

---

### High-Level System Architecture

```
                                  =========================================
                                     LAYER 1: MULTI-DOMAIN DATA INGESTION
                                  =========================================
      [ PHYSICAL / RF EDGE ]            [ CYBER / NETWORK ]           [ OSINT / FININT ]
   - Optical RGB (RTSP 4K)          - Host eBPF / Auditd Logs      - Dark Web & Telegram
   - LWIR Thermal Radiometry        - NetFlow / PCAP Telemetry     - AML & Crypto Wallets
   - Wi-Fi CSI (ESP32-S3 / NIC)     - SIEM / XDR / CTI (STIX 2.1)  - Cell Dumps / ADS-B / AIS
              │                                 │                             │
              ▼                                 ▼                             ▼
   ┌──────────────────────┐          ┌──────────────────────┐      ┌──────────────────────┐
   │ Edge Tensor Pipeline │          │ Telemetry Stream     │      │ OSINT / Graph Ingest │
   │ (Jetson / TensorRT)  │          │ (Kafka / Vector.dev) │      │ (Scrapy / Webhooks)  │
   └──────────┬───────────┘          └──────────┬───────────┘      └──────────┬───────────┘
              │                                 │                             │
              └────────────────────────┬────────┴─────────────────────────────┘
                                       │
                                       ▼
                     =======================================
                        LAYER 2: FEATURE EXTRACTION PIPELINE
                     =======================================
                     - YOLOv11 & ByteTrack (BBoxes, 2D/3D Poses)
                     - RetinaFace + ArcFace (512-D Face Vectors)
                     - CycleGAN Cross-Spectral (LWIR -> RGB Latent)
                     - Wi-Fi DensePose (CSI Phase/Amplitude -> 3D Mesh)
                     - Whisper & WavLM (Speaker Diarization / Biometrics)
                     - DeBERTa + NER + Intent Embeddings
                     - eBPF Process Trees & UEBA Anomaly Scoring
                                       │
                                       ▼
                     =======================================
                        LAYER 3: CROSS-MODAL FUSION ENGINE
                     =======================================
                     - Shared Latent Space Projection (ImageBind / CLIP)
                     - Cross-Attention Fusion & Temporal Synchronizer
                     - Probabilistic Entity Resolution & Disambiguation
                                       │
                                       ▼
                     =======================================
                        LAYER 4: DYNAMIC THREAT GRAPH CORE
                     =======================================
                     - Graph DB: Neo4j / AWS Neptune (Property Graphs)
                     - Vector DB: Milvus / Qdrant (1:N Embedding Search)
                     - Graph ML: Dynamic GNN (Temporal Graph Networks / GraphSAGE)
                     - Baseline Anomaly Detection & Threat Scoring
                                       │
                                       ▼
                     =======================================
                        LAYER 5: AI AGENTIC ORCHESTRATION & SOAR
                     =======================================
                     - Autonomous Agent Workflows (LangGraph / AutoGen)
                     - Tool Execution via Model Context Protocol (MCP)
                     - Threat Triage, Containment & Mission Dispatch

```

---

### Layer-by-Layer Technical Specification

#### Layer 1 & 2: Edge Sensing, Telemetry & Feature Extraction

| Modality | Ingestion Protocols | Processing Engine & Models | Extracted Feature Output |
| --- | --- | --- | --- |
| **Optical Video** | RTSP / WebRTC (H.264/H.265) | YOLOv11x + TensorRT FP16, ByteTrack, RetinaFace, ArcFace | Bounding boxes, track IDs, 17-point 2D keypoints, 512-D facial embeddings |
| **Thermal IR** | Radiometric 16-bit LWIR stream | Preprocessing (histogram eq.), CycleGAN, MagFace | Subcutaneous vascular graphs, cross-modal 512-D identity embeddings |
| **Wi-Fi CSI** | Raw I/Q matrices (52 subcarriers, 2.4/5GHz) | Wi-Fi DensePose (1D-CNN + BiLSTM + U-Net) | Non-line-of-sight (NLOS) 3D surface meshes, breathing/heart rate, location coordinates |
| **Audio** | Micro-array audio streams | Whisper ASR, WavLM, Resemblyzer | Audio transcripts, speaker voiceprint embeddings, acoustic stress index |
| **Cyber & Host** | eBPF telemetry, syslog, Kafka | Wazuh, Suricata, Zeek, Elastic Agent | Process lineage, binary hashes, DNS request entropy, TLS ja3 fingerprints |
| **FININT / OSINT** | REST APIs, STIX/TAXII, Scrapy | Chainalysis/TRM APIs, RoBERTa NER | Wallet addresses, sanctions status, alias associations, sentiment/intent tags |

---

#### Layer 3: Cross-Modal Fusion & Entity Resolution

Raw features from different sensors are projected into a unified representation before entering the graph database:

1. **Shared Embedding Space:** Using a multimodal projection model (e.g., ImageBind-style encoder), disparate inputs (Face Embedding, Thermal Signature, Voiceprint, CSI Motion Vector) map into a shared $D=1024$ latent space.
2. **Temporal & Spatial Alignment:** A sliding-window synchronization queue ($T=500\text{ms}$) matches a subject's Wi-Fi CSI coordinate with an optical/thermal bounding box in the same spatial grid $(X, Y, Z)$.
3. **Probabilistic Entity Resolution:** When sensor data arrives without a clear ID:

$$\text{MatchScore} = w_1 \cdot \text{Sim}_{\text{Face}} + w_2 \cdot \text{Sim}_{\text{Voice}} + w_3 \cdot \text{SpatialCorr}(\text{CSI}, \text{Camera}) + w_4 \cdot \text{DeviceMAC}$$



If $\text{MatchScore} \ge \tau_{\text{threshold}}$, the event binds to an existing `(:Person)` entity node; otherwise, a provisional `(:UnknownSubject)` node is created.

---

#### Layer 4: Dynamic Threat Knowledge Graph (Neo4j + Vector DB + GNN)

The graph links physical actions, digital operations, and financial transactions into an evolving network:

```
   (:Person {id, risk_score, last_seen})
       │
       ├──[:HAS_BIOMETRIC]────► (:BiometricProfile {face_emb, voice_emb, lwir_emb})
       ├──[:OPERATES_DEVICE]──► (:Device {mac, imei, ip_address})
       ├──[:CONTROLS_WALLET]──► (:CryptoWallet {address, chain, balance})
       ├──[:COMMUNICATES_WITH {frequency, encrypted: true}]──► (:Person)
       ├──[:LOCATED_AT {timestamp, method: "WIFI_CSI"}]──────► (:SpatialZone {coords, name})
       └──[:ASSOCIATED_WITH]──► (:ThreatGroup {name, ideology})
                                     │
                                     └──[:TARGETS]──► (:CriticalAsset {name, category})

```

**Graph Machine Learning Pipeline:**

* **Graph Database (Neo4j / Amazon Neptune):** Stores persistent relationships and executes graph path traversals (shortest paths, community clusters).
* **Vector Index (Milvus / Qdrant):** Performs millisecond 1:N vector similarity searches on 512-D face and voice embeddings.
* **Temporal Graph Neural Networks (TGN / GraphSAGE):** Ingests dynamic graph snapshots every minute to calculate:
* **Link Prediction:** Anticipating unobserved connections between hidden cells and targets.


* **Anomaly Deviation:** Identifying sudden increases in graph centrality, new bridge nodes, or sudden crypto structuring (smurfing).


* **Dynamic Threat Score:** Evaluating the real-time probability of hostile intent:

$$\text{Threat Index} = f(\text{Actor Centrality}, \text{Intent Signals}, \text{Resource Capability}) \in [0.0, 1.0]$$






---

#### Layer 5: AI Agentic Orchestration & Autonomous Action (MCP + SOAR)

The orchestration layer uses an agentic LLM/framework (LangGraph + Model Context Protocol) to coordinate tools without human latency:

```
                  ┌──────────────────────────────────────────────┐
                  │          LangGraph Orchestration Agent       │
                  │   (Understands context, rules of engagement) │
                  └──────────────────────┬───────────────────────┘
                                         │
                        [ Model Context Protocol (MCP) ]
                                         │
        ┌───────────────────┬────────────┴───────┬───────────────────┐
        ▼                   ▼                    ▼                   ▼
┌───────────────┐   ┌───────────────┐    ┌───────────────┐   ┌───────────────┐
│ Threat Graph  │   │ Edge Camera & │    │ Cyber SOAR /  │   │ Alerting &    │
│ Tool (Cypher) │   │ PTZ / Drone   │    │ Firewall Tool │   │ Tactical Comms│
└───────────────┘   └───────────────┘    └───────────────┘   └───────────────┘

```

1. **Trigger:** The TGN flags an anomaly: a subject tracked via through-wall Wi-Fi CSI in a restricted zone matches a flagged face/thermal profile enrolled in the vector database.
2. **Autonomous Tool Querying:** The Agent queries the Neo4j graph via MCP to pull active phone MACs, associated bank transactions, and active cyber sessions.


3. **Execution & Containment:**
* Automatically pans an optical/thermal PTZ camera to verify visual tracking.
* Sends an API command to the network controller (SDN/Firewall) to isolate active IP/MAC connections.
* Generates a structured operational threat dossier for tactical response units.



---

### Technology Stack Summary

| Subsystem | Selected Frameworks & Infrastructure |
| --- | --- |
| **Edge Hardware** | NVIDIA Jetson AGX Orin, ESP32-S3 (Wi-Fi CSI), FLIR Boson LWIR Core |
| **Edge Vision / ML** | TensorRT, ONNX Runtime, YOLOv11, ArcFace, DeepStream SDK |
| **Data Streaming** | Apache Kafka, Apache Flink (real-time stream analytics), Vector.dev |
| **Databases** | Neo4j Enterprise (Graph), Qdrant / Milvus (Vector), TimescaleDB (Time-series) |
| **Graph Neural Nets** | PyTorch Geometric (PyG), DGL (Deep Graph Library), GraphSAGE / TGN |
| **Agent / Orchestration** | LangGraph, FastMCP / Model Context Protocol, Cortex XSOAR / Tines |