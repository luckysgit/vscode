a pure software and data-driven counter-terrorism platform, physical edge components are completely decommissioned, while the core natural language, graph intelligence, and agentic workflows are retained and expanded.

---

### What We Are Removing (Hardware & Edge Layer)

| Layer / Technology to Remove | What It Included | Why We Are Removing It |
| --- | --- | --- |
| **Edge Object & Pose Detection** | NVIDIA Jetson AGX Orin, YOLOv11, TensorRT, DeepStream, ByteTrack

 | Eliminates physical camera deployments, on-prem edge accelerators, and video stream ingestion.

 |
| **Facial & Biometric Vision** | 4K Optical PTZ cameras, RetinaFace, ArcFace, MagFace

 | Removes reliance on visual line-of-sight hardware, camera calibration, and video RTSP feeds.

 |
| **Thermal Biometrics** | FLIR Boson LWIR radiometric cores, CycleGAN cross-spectral models

 | Eliminates specialized thermal sensors and complex infrared-to-visible image conversion.

 |
| **RF & Wi-Fi Sensing** | ESP32-S3 boards, Wi-Fi CSI extraction, mmWave Radar, DensePose

 | Removes physical microcontroller deployment, RF calibration, and through-wall tracking complexity.

 |
| **Audio Hardware Forensics** | Microphone arrays, ALSA ingest, real-time directional acoustics

 | Removes listening hardware maintenance and physical sound capture infrastructure.

 |
| **Hardware Actuation Tools** | Automated PTZ tracking controllers, drone dispatch integrations

 | The system no longer needs to control physical security hardware.

 |

---

### What We Are Keeping (Software, ML & Graph Intelligence)

| Core Software Layer | Retained Technologies & Models | Why We Are Keeping It |
| --- | --- | --- |
| **Data Ingestion (Pure Digital)** | Scrapy, Playwright, Telethon, STIX/TAXII client, Web3/Crypto RPC APIs

 | Collects public text, open-source intelligence (OSINT), threat reports (CTI), and on-chain blockchain records without physical sensors.

 |
| **LLM Information Extraction** | Fine-Tuned LLM (Llama 3.1 / Mistral with QLoRA), Outlines/Instructor, DeBERTa NER

 | Parses unstructured text reports, forums, and chat dumps into structured entities and relationships (`Head-Relation-Tail`).

 |
| **Knowledge Graph Database** | Neo4j / Amazon Neptune, Cypher query engine

 | Maps complex networks connecting actors, organizations, wallets, aliases, and planned events dynamically.

 |
| **Vector Similarity Database** | Qdrant / Milvus

 | Enables semantic entity deduplication and vector retrieval for GraphRAG workflows.

 |
| **Graph Machine Learning** | PyTorch Geometric (PyG), NetworkX, GraphSAGE, Leiden/Louvain algorithms

 | Detects covert operational clusters, community shifts, link predictions, and high-centrality bridge actors.

 |
| **Agentic AI & Orchestration** | LangGraph, Model Context Protocol (MCP), FastAPI

 | Enables autonomous threat triage, automated Cypher querying, dossier generation, and SIEM/firewall API execution.

 |
| **Analyst UI** | Streamlit, Cytoscape.js / vis-network | Provides an interactive visual interface for analysts to inspect threat subgraphs and natural-language summaries. |

---

### The New Software-Only Intelligence Flow

```
[ Unstructured Text / CTI / OSINT / Financial Feeds ]
                         │
                         ▼
[ Fine-Tuned Extraction LLM (Llama 3.1 + Instructor) ]
  • Extracts: Actors, Groups, Wallets, Targets, Relationships
                         │
                         ▼
[ Entity Resolution & Graph Construction (Neo4j) ]
  • Resolves aliases & handles into canonical Actor profiles
                         │
                         ▼
[ Graph Machine Learning & Analytics (PyTorch Geometric) ]
  • Leiden Community Detection (Finds covert cells)
  • Betweenness Centrality (Finds coordinators & financial bridges)
                         │
                         ▼
[ GraphRAG & LangGraph AI Agent (MCP Interface) ]
  • Generates actionable threat dossiers and answers investigative queries

```

By removing sensor arrays and edge computing devices, the platform becomes a clean **Cyber/OSINT Threat Intelligence Graph Platform** that can be developed, tested, and deployed entirely on standard cloud infrastructure.