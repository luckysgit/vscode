# TRACKER

- **there is currently no single commercial system that reliably takes every layer we discussed, facial behavior, speech, psychology, financial networks, social networks, logistics, physical activity, digital activity, etc., and produces a single "threat" answer.**

The market is fragmented into specialized systems.

### What exists today

| Layer                  | Existing technology                                    |
| ---------------------- | ------------------------------------------------------ |
| Financial behavior     | AML, transaction monitoring, financial crime analytics |
| Cyber behavior         | SIEM, XDR, UEBA, threat detection                      |
| Threat intelligence    | CTI platforms, IOC/TTP analysis                        |
| Network relationships  | Graph analytics, link analysis, entity resolution      |
| Social/online behavior | OSINT and social-media intelligence platforms          |
| Physical behavior      | Video analytics, anomaly detection                     |
| Speech                 | Speech-to-text + NLP                                   |
| Text/intent            | NLP/LLMs, entity extraction, sentiment/intent models   |
| Facial behavior        | Computer vision, facial-expression analysis            |
| Geospatial behavior    | Location intelligence, geospatial analytics            |
| Multimodal analysis    | Computer vision + NLP + audio + graph systems          |
| AI orchestration       | Agents, MCP, SIEM/SOAR integrations                    |

For example, **Feedly Threat Intelligence** now offers AI models, threat-actor analysis, TTP analysis, a Threat Graph, and a Threat Graph MCP Server. ([Feedly][1])

**Tidal Cyber** focuses on threat-informed defense and adversary TTPs, and it has also released an MCP server for bringing threat intelligence into AI workflows. ([Tidal Cyber][2])

But these are primarily **cyber threat intelligence**, not a universal physical + psychological + financial threat detector.

---

## The architecture you are describing is different

From everything you have been asking, I think the actual concept you are reaching toward is:

```text
                 MULTIMODAL THREAT INTELLIGENCE
                              |
       +----------------------+----------------------+
       |                      |                      |
   FINANCIAL                HUMAN                 DIGITAL
       |                      |                      |
 Transactions             Behavior             Activity
 Accounts                 Speech               Accounts
 Companies                Relationships        Devices
 Funding                  Social network       Cyber events
       |                      |                      |
       +----------------------+----------------------+
                              |
                         GRAPH LAYER
                              |
                    Neo4j / Graph Database
                              |
                 +------------+------------+
                 |                         |
             GNN / ML                    LLM
                 |                         |
          Pattern detection          Reasoning
          Anomaly detection          Explanation
          Link prediction            Investigation
                 |                         |
                 +------------+------------+
                              |
                         MCP / Agent
                              |
                Tools + Data Sources
                              |
                         Analyst
```

That is much closer to a **multimodal threat intelligence platform** than a conventional neural network.

### Where MCP fits

This is an important distinction:

**MCP is not the neural network.**

MCP is a protocol that allows an AI system to access tools and data.

Think:

```text
                  LLM / Agent
                       |
                      MCP
                       |
       +---------------+---------------+
       |               |               |
     Neo4j           SQL           Threat API
       |               |               |
    Graph data      Financial      Intelligence
                    records          feeds
```

The model does the reasoning. MCP provides controlled access to external tools and data.

Current security research is increasingly examining exactly this architecture because MCP-connected agents can create new security and observability challenges. ([Lab Space][3])

---

# What is still missing

The major gap is **cross-domain correlation**.

Imagine you have:

```text
Financial
    |
    v
Account A -> Account B -> Company C

Social
    |
    v
Person X -> Person Y -> Organization Z

Digital
    |
    v
Account X -> Device Y -> IP Z

Physical
    |
    v
Person X -> Location A -> Location B

Communication
    |
    v
Person X <-> Person Y
```

Individually, these systems may not see the complete picture.

A graph could potentially connect them:

```text
                  Person X
                 /   |    \
                /    |     \
               v     v      v
           Account  Device  Person Y
              |       |       |
              v       v       v
           Company   IP    Organization
              |              |
              +------+-------+
                     |
                     v
                   Event
```

That is where **Graph ML + entity resolution + temporal analysis + LLM reasoning** becomes interesting.

---

# Neural Network vs Graph Neural Network

For the problem you are describing, I would not make a normal neural network the center of the architecture.

A normal neural network sees something like:

```text
X1, X2, X3, X4 -> Neural Network -> Prediction
```

But your problem is inherently relational:

```text
Person -> Account -> Transaction -> Company
   |                         |
   +-> Person -> Organization
                |
                +-> Location
```

So **GNNs are much more naturally suited to the relationship layer.**

A possible architecture is:

```text
Raw data
   |
   +---- Financial data
   +---- Communication data
   +---- Cyber data
   +---- OSINT
   +---- Geospatial data
   +---- Event data
   |
   v
Entity Resolution
   |
   v
Knowledge Graph
   |
   v
Neo4j
   |
   +---- Graph features
   +---- Community detection
   +---- Link prediction
   +---- Anomaly detection
   |
   v
GNN
   |
   v
Risk indicators
   |
   v
LLM
   |
   v
Investigation / explanation
   |
   v
MCP
   |
   +---- Query additional sources
   +---- Run graph queries
   +---- Retrieve intelligence
   +---- Generate analyst report
```

### One major caution

I would **not** build the system around "facial expression -> threat" or "political/religious viewpoint -> threat." Those signals have poor specificity and create serious false-positive and civil-liberties problems.

A technically stronger system focuses on **observable events, relationships, behavioral changes, explicit intent, capability, and corroborating evidence**, with a human analyst making the final assessment.

And there is a real market opportunity here: today's products generally solve **pieces** of this architecture. A system that genuinely performs **multilayer temporal graph correlation across financial + human + digital + physical + organizational data** is a substantially broader problem than conventional CTI.

If your objective is to explore this as an R&D project, the next thing I would do is map **what commercial products already cover each layer, what they do not cover, and where a Neo4j + GNN + LLM + MCP architecture could provide something genuinely differentiated.**

[1]: https://feedly.com/threat-intelligence/pricing?utm_source=chatgpt.com "Pricing | Feedly Threat Intelligence"
[2]: https://www.tidalcyber.com/?utm_source=chatgpt.com "Tidal Cyber | Threat-Led Defense"
[3]: https://labs.cloudsecurityalliance.org/research/csa-research-note-ai-induced-lateral-movement-20260309-csa-s/?utm_source=chatgpt.com "AI-Induced Lateral Movement: Autonomous Agents as a Third Dimension of Network Traversal – Lab Space"

----------------------------------------------------------------------------------------------

# Multilayer threat platform

**face/vision, thermal, Wi-Fi sensing, RF/radar, cyber, financial, human, organizational, and graph intelligence**, you are essentially describing a **multimodal, multilayer threat-intelligence and situational-awareness platform**.

I checked current technology and research, including YOLO, Wi-Fi sensing/802.11bf, thermal AI, graph-based cyber intelligence, and current AI threat-analysis work. There are systems covering many individual layers, and some platforms fuse several domains, but I did not find a single mainstream product that completely unifies all of these layers into one threat-detection stack.

## 1. The complete hierarchy

I would structure the system into **12 major layers**:

```text
                         MULTIMODAL THREAT INTELLIGENCE
                                      |
       +------------------------------+------------------------------+
       |                              |                              |
   PHYSICAL WORLD                 HUMAN/BEHAVIOR                DIGITAL WORLD
       |                              |                              |
   1. Vision                      5. Behavior                   8. Cyber
   2. Thermal                     6. Speech/NLP                 9. OSINT
   3. RF/Wi-Fi                    7. Social Network             10. Information
   4. Radar/Location
       |
       +------------------------------+------------------------------+
                                      |
                              ORGANIZATIONAL WORLD
                                      |
                              11. Financial / Network
                              12. Operational / Logistics
                                      |
                                      v
                              KNOWLEDGE GRAPH
                                      |
                                      v
                              TEMPORAL GRAPH
                                      |
                         +------------+------------+
                         |                         |
                       GNN                       LLM
                         |                         |
                  Pattern detection          Reasoning/RAG
                  Link prediction            Investigation
                  Anomaly detection          Explanation
                         |                         |
                         +------------+------------+
                                      |
                                    MCP
                                      |
                         Tools / APIs / Databases
                                      |
                              HUMAN ANALYST
```

The key idea is that **the sensors do not directly decide "threat."** They generate observations. The graph and analytical layers correlate those observations.

---

# 2. Layer 1: Visible computer vision

This is your normal camera layer.

### What it can observe

* Person detection
* Vehicle detection
* Object detection
* Person tracking
* Vehicle tracking
* Crowd density
* Human pose
* Activity recognition
* Object interactions
* Perimeter intrusion
* Abandoned objects
* Scene changes
* License plates
* Face detection
* Face recognition, where legally permitted

### Current technologies

**YOLO** is one of the major real-time computer-vision families. Current Ultralytics tooling supports detection, segmentation, pose estimation, oriented bounding boxes, classification, depth estimation and tracking. Its current documentation lists YOLO26 as the newest model family and also recommends YOLO11 for stable production workloads. ([Ultralytics Docs][1])

Other important technologies include:

* YOLO
* RT-DETR
* SAM
* Vision Transformers
* CNNs
* DeepSORT
* ByteTrack
* BoT-SORT
* OpenCV
* OpenMMLab
* NVIDIA DeepStream

### Architecture

```text
Camera
   |
   v
YOLO / RT-DETR
   |
   +---- Person
   +---- Vehicle
   +---- Object
   +---- Animal
   |
   v
Tracking
   |
   v
Track ID
   |
   v
Behavior analysis
```

YOLO's tracking pipeline can maintain object identities across video frames using trackers such as BoT-SORT and ByteTrack. ([Ultralytics Docs][2])

---

# 3. Layer 2: Face intelligence

Face analysis should be treated as a separate layer from generic object detection.

```text
Camera
   |
Face Detection
   |
Face Alignment
   |
Face Embedding
   |
Identity Matching
   |
Temporal Tracking
```

### Technologies

* RetinaFace
* SCRFD
* MTCNN
* InsightFace
* ArcFace
* FaceNet
* DeepFace
* Vision Transformers

### What can be extracted

```text
Face
 |
 +-- Detection
 +-- Landmark
 +-- Embedding
 +-- Identity matching
 +-- Pose
 +-- Occlusion
 +-- Temporal appearance
```

I would **not** make facial expression or "micro-expression = threat" a core threat classifier. Those signals are too nonspecific. Face recognition also introduces significant privacy, bias, security, and legal considerations.

NIST's AI Risk Management Framework specifically emphasizes privacy, cybersecurity, validity, reliability, transparency, and risk management for AI systems. ([NIST Publications][3])

---

# 4. Layer 3: Thermal imaging

This is extremely interesting for your architecture.

A thermal camera does not primarily see visible color. It measures infrared radiation and produces a representation of temperature differences.

### Useful for

* Night-time detection
* Human detection
* Vehicle detection
* Perimeter monitoring
* Smoke/fog conditions
* Low-light environments
* Heat signatures
* Object classification

FLIR already has commercial thermal-security systems using AI/DNN analytics to detect and classify humans and vehicles. Its systems are designed to operate in darkness and difficult visibility conditions. ([Flir][4])

Architecture:

```text
Thermal Camera
      |
      v
Thermal Frame
      |
      v
DNN / YOLO-like detector
      |
      +---- Person
      +---- Vehicle
      +---- Animal
      |
      v
Tracking
      |
      v
Thermal behavior
```

You can also fuse visible + thermal:

```text
Visible Camera --------+
                       |
                       v
                    Sensor Fusion
                       ^
                       |
Thermal Camera --------+
                       |
                       v
                 Better Detection
```

Commercial systems already combine thermal and visible sensors for persistent tracking. ([Flir][5])

---

# 5. Layer 4: Wi-Fi sensing

This is one of the most interesting additions to your idea.

You are not using Wi-Fi primarily to identify network traffic. You are using **wireless signals as a sensing modality**.

### Basic concept

```text
Wi-Fi transmitter
       |
       | electromagnetic signal
       v
     PERSON
       |
       | changes multipath propagation
       v
Wi-Fi receiver
       |
       v
       CSI
       |
       v
Neural Network
       |
       v
Human activity / pose / presence
```

CSI means **Channel State Information**.

A person moving through the environment changes the propagation characteristics of the wireless signal.

Research has demonstrated Wi-Fi CSI applications including:

* Presence detection
* Activity recognition
* Gesture recognition
* Human pose estimation
* Gait analysis
* Crowd counting
* Indoor localization
* People identification
* Vital-sign sensing

A 2025 survey specifically describes deep learning applied to CSI for human sensing, including preprocessing, temporal/frequency/spatial features, and neural-network-based recognition. ([ScienceDirect][6])

IEEE 802.11bf is the major standardization effort for WLAN sensing. IEEE describes WLAN sensing as using PHY/MAC measurements to estimate properties such as range, velocity, angle and motion of objects including humans. ([IEEE 802][7])

NIST also describes 802.11bf as supporting applications such as presence detection and environmental monitoring using Wi-Fi sensing. ([NIST][8])

### Why this is interesting

Unlike ordinary cameras:

```text
Camera:
Need line of sight
        |
        v
       Person
```

Wi-Fi sensing can potentially work without direct visual observation.

Research has demonstrated device-free human pose sensing using Wi-Fi CSI and neural networks. ([PubMed][9])

However, Wi-Fi sensing is still much less mature and standardized than conventional camera surveillance.

---

# 6. Layer 5: Radar / RF sensing

Another sensing modality is radar.

```text
Radar
  |
  v
Reflection
  |
  v
Range
Velocity
Angle
  |
  v
Object tracking
```

Technologies include:

* FMCW radar
* mmWave radar
* RF sensing
* Doppler analysis
* Synthetic aperture radar in other domains

Possible outputs:

```text
Person
  |
  +-- Position
  +-- Velocity
  +-- Direction
  +-- Movement
  +-- Pose
```

Radar is particularly useful when cameras are affected by darkness, weather, or occlusion.

---

# 7. Layer 6: Speech and audio

Now move into the human layer.

```text
Microphone
    |
    v
Speech-to-text
    |
    v
NLP / LLM
    |
    +-- Entities
    +-- Topics
    +-- Intent
    +-- Events
    +-- Relationships
    |
    v
Knowledge Graph
```

Technologies:

* Whisper
* wav2vec 2.0
* Speech Transformers
* speaker diarization
* speaker embeddings
* NLP
* LLMs

Potential outputs:

```text
Person A
   |
   | spoke_to
   v
Person B

Person A
   |
   | mentioned
   v
Organization X

Person B
   |
   | mentioned
   v
Location Y
```

Again, speech sentiment or accent should not be treated as a threat detector.

---

# 8. Layer 7: Human behavior

This is where your earlier question about psychological behavior fits.

Instead of:

```text
Facial expression -> threat
```

use:

```text
Observed events
      |
      v
Behavior sequence
      |
      v
Baseline
      |
      v
Behavioral deviation
```

Possible signals:

* Activity change
* Interaction change
* Movement change
* Communication change
* Network change
* Temporal patterns
* Repeated actions
* Explicit statements of intent
* Preparation-related activity

The model should generate **risk indicators**, not psychological diagnoses.

---

# 9. Layer 8: Social / relationship network

Now we enter graph intelligence.

```text
Person A
   |
   +---- Person B
   |
   +---- Company C
   |
   +---- Organization D
   |
   +---- Location E
```

Technologies:

* Knowledge graphs
* Entity resolution
* Graph databases
* Community detection
* Link prediction
* Graph embeddings
* GNNs

Neo4j is already used for cyber-threat intelligence analysis and graph-based investigation workflows. ([Neo4j Graph Intelligence Platform][10])

---

# 10. Layer 9: Financial network

This is your earlier idea.

```text
Person
  |
owns
  v
Account
  |
transaction
  v
Account
  |
belongs_to
  v
Company
```

Possible analytical features:

* Transaction frequency
* Transaction amount
* Counterparty relationships
* Account connectivity
* Community structure
* Temporal changes
* Ownership relationships
* Entity resolution
* Network centrality
* Anomalous flows

This overlaps heavily with **AML and financial-crime technology**.

The important architectural point is:

```text
Financial Graph
       |
       v
Network Features
       |
       v
Risk Indicators
```

not:

```text
Transaction -> Terrorist
```

---

# 11. Layer 10: Cybersecurity

This is a huge layer by itself.

Modern cyber systems monitor:

```text
Users
Devices
Endpoints
Applications
Networks
Cloud
Identity
DNS
Email
Files
Processes
Logs
```

A useful hierarchy is:

```text
                    CYBER
                      |
       +--------------+--------------+
       |              |              |
    Identity       Endpoint        Network
       |              |              |
     Users          EDR/XDR        NDR
       |              |              |
       +--------------+--------------+
                      |
                    SIEM
                      |
                    UEBA
                      |
                    SOAR
                      |
                 Threat Intel
```

Modern security platforms combine SIEM, UEBA, anomaly models, risk scoring and SOAR workflows. Splunk's current Enterprise Security material, for example, describes UEBA anomaly models, risk-based alerting, user-centric analysis, case management and SOAR integration. ([Splunk][11])

And for the actual cyber behavior taxonomy, **MITRE ATT&CK** remains one of the most important frameworks. It represents adversary behavior through tactics, techniques and sub-techniques. ([MITRE][12])

---

# 12. Layer 11: OSINT / external intelligence

This layer connects your internal data to external information.

```text
News
Social media
Websites
Reports
Research
Government data
Corporate records
Threat feeds
Public databases
       |
       v
NLP / Entity extraction
       |
       v
Knowledge Graph
```

The important technology here is **entity resolution**.

For example:

```text
"ABC Ltd"
"ABC Limited"
"ABC Pvt. Ltd."
"ABC Technologies"
```

might or might not refer to the same entity.

The system needs to determine that relationship before graph analysis becomes reliable.

---

# 13. Layer 12: Logistics / operational network

This is the physical support layer:

```text
Person
  |
  +-- Location
  |
  +-- Vehicle
  |
  +-- Organization
  |
  +-- Asset
  |
  +-- Event
  |
  +-- Supplier
```

Possible data sources include:

* GPS
* Transportation systems
* Asset tracking
* IoT
* access control
* physical security systems
* supply-chain systems
* event systems

This becomes particularly powerful when combined with temporal graphs.

---

# The real architecture

Now combine everything.

```text
                         SENSORS / DATA
                              |
       +----------------------+----------------------+
       |                      |                      |
     VISION                  RF                  DIGITAL
       |                      |                      |
   RGB Camera             Wi-Fi CSI             Network
   Face                   Radar                 Endpoint
   YOLO                   Thermal               Cloud
   Pose                   RF                    Identity
       |                      |                      |
       +----------------------+----------------------+
                              |
                         AI PERCEPTION
                              |
       +----------+-----------+-----------+----------+
       |          |           |           |          |
    Vision      Audio      Behavior    Cyber      Finance
       |          |           |           |          |
       +----------+-----------+-----------+----------+
                              |
                         ENTITY RESOLUTION
                              |
                              v
                       KNOWLEDGE GRAPH
                              |
                        Neo4j / Graph DB
                              |
                    TEMPORAL MULTILAYER GRAPH
                              |
              +---------------+---------------+
              |                               |
             GNN                             LLM
              |                               |
       Pattern detection                 GraphRAG
       Link prediction                   Reasoning
       Anomaly detection                 Explanation
       Community detection               Investigation
              |                               |
              +---------------+---------------+
                              |
                             MCP
                              |
          +-------------------+-------------------+
          |                   |                   |
       Neo4j                  SIEM              APIs
       SQL                    CTI               OSINT
       Vector DB              EDR               Sensors
          |                   |                   |
          +-------------------+-------------------+
                              |
                       ANALYST / OPERATOR
```

This is much closer to what I think you are envisioning.

---

# Where the current market stands

The interesting thing is that the market already has **pieces of this architecture**.

### Computer vision

YOLO and other vision models can perform real-time detection, segmentation, pose, depth and tracking. ([Ultralytics Docs][1])

### Thermal

FLIR has production thermal AI systems for human/vehicle detection, classification and tracking. ([Flir][4])

### Wi-Fi sensing

802.11bf is standardizing WLAN sensing, while research is already using CSI + deep learning for human presence, activity, pose and other sensing tasks. ([IEEE 802][7])

### Cyber

SIEM + UEBA + SOAR + threat intelligence is already a mature enterprise architecture. Splunk is one example. ([Splunk][11])

### Graph intelligence

Neo4j and other graph platforms are being used for cyber-threat investigation and relationship analysis. ([Neo4j Graph Intelligence Platform][10])

### AI-enabled multi-domain intelligence

Palantir Gotham is probably one of the closest commercial examples to the **multi-domain fusion** concept. Its architecture describes an all-domain data foundation with perception AI, fusion AI, reasoning AI, situational awareness and decision-support applications. ([Palantir][13])

### GraphRAG + cyber

This is also moving quickly. A 2026 research paper specifically evaluated GraphRAG for operationalizing cyber threat intelligence into detection and hunting plans, reporting better resilience to changes in simple indicators such as IPs, domains and hashes. ([arXiv][14])

---

# One important missing piece

There is still a major research gap between:

**"I can detect a person with YOLO"**

and

**"I can understand the person's position in a large, evolving, multimodal network."**

That intermediate layer is:

## Multimodal temporal knowledge graph

For example:

```text
                     Person A
                  /     |      \
                 /      |       \
              Face    Voice    Account
               |        |         |
            Camera   Audio     Transaction
               |        |         |
               +--------+---------+
                        |
                     Time T1
                        |
                     Location
                        |
                     Device
                        |
                     Wi-Fi
                        |
                     CSI data
                        |
                    Behavior
                        |
                     Event
```

Then at another time:

```text
Time T1 -> Time T2 -> Time T3 -> Time T4
```

Now you are not merely detecting objects.

You are modeling **entities + relationships + behavior + time + sensors**.

That is where **Temporal GNNs, multimodal learning, knowledge graphs, GraphRAG and agentic/MCP architectures** become relevant.

There is already very recent research in this direction for cyber, including temporal graph learning for reconstructing multi-stage APT activity from large provenance graphs. ([arXiv][15])

## And I would add one more layer: confidence/provenance

Your final system should never simply say:

> "Threat detected."

It should produce something like:

```text
Risk Assessment
|
+-- Evidence
|   +-- Vision observation
|   +-- Wi-Fi sensing observation
|   +-- Financial relationship
|   +-- Cyber event
|   +-- Communication event
|
+-- Confidence
|
+-- Source provenance
|
+-- Timeline
|
+-- Graph relationships
|
+-- Alternative explanations
|
+-- Analyst review
```

That makes the system much more defensible and useful.

Also, because this architecture involves biometric identification, behavioral inference, financial information, and potentially surveillance data, **privacy, legal authority, false-positive control, data provenance, and human review need to be architectural components, not an afterthought**. NIST's AI RMF explicitly emphasizes privacy, cybersecurity, validity, reliability and risk management. ([NIST Publications][3])

If you are considering this as an R&D architecture, I would call the overall technical concept **"Multimodal Temporal Threat Knowledge Graph"**, with **YOLO/vision + thermal + Wi-Fi CSI + radar + audio/NLP + cyber + financial + OSINT -> Neo4j -> GNN -> GraphRAG/LLM -> MCP**. That is a coherent architecture rather than simply putting many unrelated AI models together.

[1]: https://docs.ultralytics.com/tasks/detect?utm_source=chatgpt.com "Object Detection with Ultralytics YOLO | Ultralytics"
[2]: https://docs.ultralytics.com/?utm_source=chatgpt.com "YOLO Object Detection & Segmentation | Ultralytics"
[3]: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf?utm_source=chatgpt.com "Artificial Intelligence Risk Management Framework (AI RMF 1.0)"
[4]: https://www.flir.in/security/thermal-cameras/?utm_source=chatgpt.com "Thermal Security Cameras | Teledyne FLIR"
[5]: https://www.flir.in/browse/security/?utm_source=chatgpt.com "Thermal & Visible Security Cameras | Teledyne FLIR"
[6]: https://www.sciencedirect.com/org/science/article/pii/S1546221825010380?utm_source=chatgpt.com "Deep Learning-Enhanced Human Sensing with Channel State Information: A Survey - ScienceDirect"
[7]: https://www.ieee802.org/11/Reports/tgbf_update.htm?utm_source=chatgpt.com "IEEE P802.11 - TASK GROUP BF (WLAN SENSING)"
[8]: https://www.nist.gov/publications/ieee-80211bf-enabling-widespread-adoption-wi-fi-sensing?utm_source=chatgpt.com "IEEE 802.11bf: Enabling the Widespread Adoption of Wi-Fi Sensing | NIST"
[9]: https://pubmed.ncbi.nlm.nih.gov/36433335/?utm_source=chatgpt.com "Skeleton-Based Human Pose Recognition Using Channel State Information: A Survey - PubMed"
[10]: https://neo4j.com/blog/developer/cyber-threat-intelligence-analysis/?utm_source=chatgpt.com "Open-source cyber threat intelligence analysis with graph visualization"
[11]: https://conf.splunk.com/files/2025/slides/SEC1720.pdf?linkId=859596252&utm_source=chatgpt.com "© 2025 SPLUNK LLC"
[12]: https://www.mitre.org/sites/default/files/2021-11/prs-19-01075-28-mitre-attack-design-and-philosophy.pdf?utm_source=chatgpt.com "ATTACK Design and Philosophy March 2020 Revision"
[13]: https://www.palantir.com/assets/xrfr7uokpv1b/3A0y10xksgXENvRMNaAsUu/ed8f7f1ed534c0101f64536a85f7297b/Gotham_AI-Enabled_Operations_White_Paper.pdf?utm_source=chatgpt.com "PALANTIR GOTHAM –"
[14]: https://arxiv.org/abs/2608.13050?utm_source=chatgpt.com "Operationalizing Cyber Threat Intelligence with GraphRAG"
[15]: https://arxiv.org/abs/2608.19750?utm_source=chatgpt.com "TGL-APT: Temporal Graph Learning with Graph Distillation for Efficient APT Investigation"
