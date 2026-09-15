### System Realignment: Operational Threat Intelligence & Target Identification

The system is now completely decoupled from financial fraud classification. All pipelines, graph structures, and algorithms are redirected toward **Target Identification**, **Entity Linkage**, **Composite Risk Scoring**, and **Temporal Actor Tracking**.

```
                                THREAT
                                  │
          ┌───────────────────────┼───────────────────────┐
          ▼                       ▼                       ▼
        ACTOR                   INTENT                CAPABILITY
       ("Who?")          ("What do they want?")    ("Can they do it?")
          │
    ┌─────┴─────┬─────────────┐
    ▼           ▼             ▼
 Individual   Group        Network
                              │
                        SUPPORT SYSTEM
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
    Personnel             Logistics             Technology
  (Recruitment)           (Travel)            (Comms/Infra)

```

---

### Core Operational Pillars

#### 1. Target Identification (Multi-Behavioral Signals)

* **Goal:** Detect emerging actors from weak, distributed signals across digital activity, infrastructure probing, and communications before operational execution.
* **Signals Ingested:**
* **Cyber Telemetry (NetFlow):** Reconnaissance scanning, port probes to industrial/critical protocols, command-and-control beaconing.
* **Delivery Infrastructure:** Spearphishing links, weaponized domains, newly registered operational landing sites.
* **Cellular / Physical Movement (CDR):** Burner device churning, high-entropy subscriber behaviors, burst-calling near critical assets.
* **Threat Feed Alignment (CTI / STIX):** Automated pattern matching of incoming telemetry against known MITRE ATT&CK tactics (e.g., T1190, T1071).



#### 2. Entity Linkage (Relational Knowledge Graph)

* **Goal:** Connect isolated technical artifacts to resolve actor identity, organizational roles, and indirect relationships.
* **Graph Structure (`NetworkX` / `Neo4j`):**
* **Nodes:** `:Actor`, `:Group`, `:Network`, `:Device` (IMEI/MAC), `:Infrastructure` (IP/Domain), `:Location` (Cell Tower/Coordinates), `:Event`.
* **Typed Edges:**
* `(:Actor)-[:MEMBER_OF]->(:Group)`
* `(:Actor)-[:OPERATES]->(:Device)-[:ATTACHED_TO]->(:Location)`
* `(:Actor)-[:DEPLOYS]->(:Infrastructure)-[:COMMUNICATES_WITH]->(:Target)`
* `(:Actor)-[:INTERFACES_WITH {weight, frequency}]->(:Actor)`




* **Link Discovery:** Traverses multi-hop paths to uncover non-obvious intermediary nodes (e.g., two operatives who never directly call each other, but communicate through a common handler or connect to the same staging server).

#### 3. Composite Risk Scoring (Multi-Source Prioritization)

* **Goal:** Rank suspect entities to establish an actionable triage queue for analysts, minimizing false positives from high-volume routine noise.
* **Non-Financial Fusion Formula:**

$$\text{Target Priority Score}(A) = \sum_{m \in M} w_m \cdot R_m(A) + \gamma \cdot \mathbb{I}(\text{distinct corroborated domains} \ge 3)$$



Where $M = \{\text{NetFlow}, \text{Infrastructure/URLs}, \text{CTI TTPs}, \text{Telecom CDRs}, \text{Logistics}\}$ and $\gamma = 0.35$ is the convergence booster rewarding multi-source corroboration.

#### 4. Temporal Actor Tracking (Evolution Over Time)

* **Goal:** Monitor how threat networks expand, mutate, or change tactics across operational planning phases.
* **Analytical Mechanics:**
* **Timeline Reconstruction:** Sequences observed events from initial reconnaissance to resource acquisition and final staging.
* **Centrality Drift:** Measures changes in Betweenness and Degree Centrality over time windows ($T_1, T_2, T_3$) to detect when an actor transitions from an observer to an active operational coordinator.
* **Infrastructure Churn Tracking:** Detects automated rotation of IP subnets, domains, and burner devices to maintain attribution despite defensive evasion.



---

### Redesigned Pipeline Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               MULTI-MODAL INGESTION LAYER                              │
├─────────────────────────┬──────────────────────────┬───────────────────────────────────┤
│ 1. Network Telemetry    │ 2. Delivery Domains      │ 3. Telecom / CDR Feeds            │
│    (NetFlow, Scans)     │    (Phishing, Staging)   │    (Burner SIMs, Co-Location)     │
└───────────┬─────────────┴────────────┬─────────────┴─────────────────┬─────────────────┘
            │                          │                               │
            ▼                          ▼                               ▼
    [ NetFlow Engine ]         [ Domain Engine ]               [ Mobility Engine ]
            │                          │                               │
            └──────────────────────────┼───────────────────────────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────────┐
                    │       COMMON EVENT NORMALIZER        │
                    │       (Actor / Entity Schemas)       │
                    └──────────────────┬───────────────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────────┐
                    │     ENTITY RESOLUTION & LINKAGE      │
                    │   (Subnets, Shared Infrastructure)   │
                    └──────────────────┬───────────────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────────┐
                    │     RELATIONAL KNOWLEDGE GRAPH       │
                    │  (Actor <-> Device <-> Infra Nodes)  │
                    └──────────────────┬───────────────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────────┐
                    │       TEMPORAL RISK PRIORITIZER      │
                    │  (Convergence Bonus + Centrality)    │
                    └──────────────────┬───────────────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────────┐
                    │      READ-ONLY MCP SERVER TOOLS      │
                    │  • get_actor_linkage_graph           │
                    │  • get_infrastructure_attribution    │
                    │  • get_temporal_movement_path        │
                    └──────────────────┬───────────────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────────┐
                    │       REASONING LLM DOSSIER          │
                    │    (Zero-Hallucination Triage)       │
                    └──────────────────────────────────────┘

```

---

### Immediate Implementation Plan for Google Colab

1. **Refactor Event Generator:** Strip out credit card records entirely. Reallocate simulated telemetry purely to **NetFlow scans**, **staging URLs**, **telecom cell tower transits**, and **MITRE CTI technique links**.
2. **Update Graph Schema:** Define explicit node types (`Actor`, `Device`, `IP`, `Domain`, `CellTower`) with directional operational edges (`USES_DEVICE`, `RESOLVES_TO`, `COMMUNICATES_WITH`).
3. **Align MCP Tools:** Expose endpoints focused exclusively on entity resolution:
* `get_actor_linkage_subgraph(actor_id)`: Traverses multi-hop links to uncover affiliated infrastructure and peers.
* `get_infrastructure_timeline(actor_id)`: Returns chronological activation dates for IPs, domains, and phone numbers.
* `get_network_centrality_metrics(actor_id)`: Outputs degree, betweenness, and community membership to determine operational hierarchy.


4. **Tune LLM System Prompt:** Restrict `Qwen2.5-0.5B-Instruct` to assess **Actor Identification**, **Operational Role (Logistics vs. Comms vs. Execution)**, and **Immediate Technical Interdiction Strategies**.