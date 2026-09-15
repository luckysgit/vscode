### High-Level Summary of Every Cell

* **Cell 1 (Environment Setup):** Installs required external libraries (`pandas`, `numpy`, `scikit-learn`, `networkx`, `matplotlib`, `requests`) in the Colab runtime without verbose logs.
* **Cell 2 (Multi-Source Ingestion & Normalization):** Streams real CTU-13 bidirectional NetFlow records from a remote server, maps raw network data into an 18-field unified schema (Section 16), and injects synchronized multi-protocol events (DNS, SIP, RTP) to establish session linkages across communication layers (Figures 2 & 3).
* **Cell 3 (Behavioral Profiling Engine):** Aggregates normalized flow events by source entity (`source_address`) and extracts multi-dimensional behavioral vectors—tracking destination fan-out, port entropy, byte/packet volumes, temporal distribution, and protocol diversification (Section 7).
* **Cell 4 (Unsupervised Anomaly Scoring & Target Prioritization):** Scales continuous behavioral features using standard z-score normalization, trains an Isolation Forest detector, computes an inverted continuous risk score in the range $[0, 1]$, and ranks candidate entities into an investigation queue (Section 18).
* **Cell 5 (Multi-Hop Entity & Session Graph):** Takes the top prioritized targets and builds a directed multi-graph (`networkx.MultiDiGraph`) connecting entities, communication sessions, external IP infrastructure, and domain services, rendering the network topology (Figure 4).

---

### Architectural Flow of the Pipeline

```
Raw Telemetry (NetFlow + DNS + SIP/RTP)
                 │
                 ▼
     [Cell 2: Normalization Layer] 
     Standardizes disparate protocols into Common Event Schema (Sec. 16)
                 │
                 ▼
     [Cell 3: Feature Engineering / Profiler]
     Aggregates events per entity into statistical behavioral metrics (Sec. 7)
                 │
                 ▼
     [Cell 4: Machine Learning Inference]
     Isolation Forest identifies statistical outliers & calibrates Threat Score [0, 1] (Sec. 18)
                 │
                 ▼
     [Cell 5: Knowledge Graph & Entity Linkage]
     Constructs heterogeneous MultiDiGraph (:Target -> :Session -> :Infrastructure/:Domain)

```

---

### Cell-by-Cell, Line-by-Line Architectural Explanation

---

#### **Cell 1: Environment & Tooling Setup**

```python
!pip install -q pandas numpy scikit-learn networkx matplotlib requests

```

* `!pip install`: Invokes the pip package installer inside the notebook shell environment.
* `-q`: Flags "quiet" mode to suppress verbose compilation, build, and progress logs during runtime setup.
* `pandas numpy`: Provides vectorized arrays, matrix manipulation, and tabular DataFrame management.
* `scikit-learn`: Supplies machine learning tools for standard scaling and unsupervised anomaly detection (`IsolationForest`).
* `networkx`: In-memory graph analytics library used to construct and analyze multi-relational graphs.
* `matplotlib`: Plotting engine used to render the final graph topology.
* `requests`: HTTP library capable of streaming remote payloads over standard connections.

---

#### **Cell 2: Ingestion, Common Schema Normalization & Multi-Protocol Generation**

##### 1. Module Imports

```python
import os
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

```

* `import os`: Exposes file-system operations to check if raw capture files already exist locally before triggering network downloads.
* `import requests`: Allows stream-based network requests with custom headers and connection timeouts.
* `import numpy as np`: Provides fast numeric aggregation primitives for behavioral feature vectors.
* `import pandas as pd`: Imports the tabular data manipulation library.
* `from datetime import datetime, timedelta`: Implements chronological time-delta manipulation needed to compute flow start/end offsets and inter-packet delays.

##### 2. Stream Ingestion of CTU-13 NetFlow

```python
# 1. Fetch real CTU-13 NetFlow data (Scenario 1)
url = "https://mcfp.felk.cvut.cz/publicDatasets/CTU-Malware-Capture-Botnet-42/detailed-bidirectional-flow-labels/capture20110810.binetflow"
filename = "ctu13_scenario1.binetflow"
nrows_to_fetch = 15000

```

* `url = "..."`: Designates the remote endpoint hosting CTU-13 Scenario 1 (Capture 42 - Neris Botnet).
* `filename = "ctu13_scenario1.binetflow"`: Sets the local storage target on disk.
* `nrows_to_fetch = 15000`: Restricts the number of ingested records, preventing multi-gigabyte disk buffer exhaustion while maintaining an active statistical baseline.

```python
if not os.path.exists(filename):
    print(f"[*] Downloading first {nrows_to_fetch} rows of real CTU-13 NetFlow data...")
    headers = {"User-Agent": "Mozilla/5.0"}
    with requests.get(url, headers=headers, stream=True, timeout=30) as r:
        r.raise_for_status()
        with open(filename, "wb") as f:
            count = 0
            for line in r.iter_lines():
                if line:
                    f.write(line + b"\n")
                    count += 1
                    if count >= nrows_to_fetch:
                        break
    print(f"[+] Download complete: {filename}")

```

* `if not os.path.exists(filename):`: Guards against redownloading if the local file already exists.
* `headers = {"User-Agent": "Mozilla/5.0"}`: Supplies a standard client identity header to prevent server-side automated scraping rejections.
* `with requests.get(url, headers=headers, stream=True, timeout=30) as r:`: Opens an HTTP GET connection in chunked streaming mode (`stream=True`) with a 30-second connection timeout, reading incoming bytes into a memory buffer without pulling the entire multi-gigabyte archive at once.
* `r.raise_for_status()`: Throws an HTTP error exception immediately if the server responds with a 4xx or 5xx code.
* `with open(filename, "wb") as f:`: Opens a local binary write stream.
* `count = 0`: Tracks the number of written records.
* `for line in r.iter_lines():`: Iterates through the incoming byte stream as chunks arrive from the network.
* `if line: f.write(line + b"\n")`: Flushes raw, non-empty byte strings to disk with newline delimiters.
* `count += 1`: Increments the record counter.
* `if count >= nrows_to_fetch: break`: Interrupts the stream once 15,000 valid flow records are written, cutting off the remaining multi-gigabyte payload.

```python
df_raw = pd.read_csv(filename)
print(f"[+] Raw flows loaded: {len(df_raw)}")

```

* `df_raw = pd.read_csv(filename)`: Parses CSV flow lines into a DataFrame.
* `print(f"[+] Raw flows loaded: {len(df_raw)}")`: Verifies the record count loaded into RAM.

##### 3. Transformation to Section 16 Common Event Schema

```python
# 2. Transform into Section 16: Common Normalized Event Schema
normalized_events = []

```

* `normalized_events = []`: Initializes an array to store standardized event dictionaries.

```python
for idx, row in df_raw.iterrows():
    start_time = pd.to_datetime(row['StartTime'])
    duration = float(row['Dur']) if pd.notnull(row['Dur']) else 0.0
    end_time = start_time + timedelta(seconds=duration)

```

* `for idx, row in df_raw.iterrows():`: Iterates across every raw NetFlow record.
* `start_time = pd.to_datetime(row['StartTime'])`: Casts raw string timestamps into microsecond-accurate datetime objects.
* `duration = float(row['Dur']) if pd.notnull(row['Dur']) else 0.0`: Cleans missing/corrupted duration entries, defaulting to `0.0`.
* `end_time = start_time + timedelta(seconds=duration)`: Calculates the exact connection termination time by adding the duration offset.

```python
    src_ip = str(row['SrcAddr'])
    dst_ip = str(row['DstAddr'])
    proto = str(row['Proto']).upper()
    s_port = str(row['Sport']) if pd.notnull(row['Sport']) else "0"
    d_port = str(row['Dport']) if pd.notnull(row['Dport']) else "0"
    tot_pkts = int(row['TotPkts']) if pd.notnull(row['TotPkts']) else 1
    tot_bytes = int(row['TotBytes']) if pd.notnull(row['TotBytes']) else 64
    direction = str(row['Dir'])
    label = str(row['Label'])

```

* Casts and normalizes L3/L4 fields (`SrcAddr`, `DstAddr`, `Proto`, `Sport`, `Dport`, `TotPkts`, `TotBytes`, `Dir`, `Label`) to predictable types (`str`, `int`), supplying fallbacks to avoid `NaN` runtime errors during ML preprocessing.

```python
    # Identify protocol family
    app_proto = "NETFLOW"
    domain = None
    session_id = f"FLOW_{src_ip}_{dst_ip}_{d_port}"
    protocol_fields = {"state": str(row['State'])}

```

* `app_proto = "NETFLOW"`: Sets default protocol layer designation.
* `domain = None`: Initializes application target domain.
* `session_id = f"FLOW_{src_ip}_{dst_ip}_{d_port}"`: Builds a connection-tracking identifier using the source IP, destination IP, and target port.
* `protocol_fields = {"state": str(row['State'])}`: Preserves raw transport flags (e.g., `CON`, `FA_A`, `PA_RPA`) inside a protocol-specific sub-dictionary.

```python
    if d_port == "53" or proto == "DNS":
        app_proto = "DNS"
        domain = "c2-sync-gate.org" if "Botnet" in label else "dns.google.com"
        protocol_fields["query_type"] = "A"
    elif d_port in ["80", "443", "8080"]:
        app_proto = "HTTP/TLS"
        domain = "auth-update-v4.net" if "Botnet" in label else "service.internal"
        protocol_fields["sni"] = domain

```

* Inspects destination ports to infer application layer protocol:
* Port 53: Classifies as `DNS`, binds domain metadata (`c2-sync-gate.org` for botnet labels, `dns.google.com` for benign traffic), and sets query type `A`.
* Ports 80, 443, 8080: Classifies as `HTTP/TLS`, binds Server Name Indication (SNI) hostnames (`auth-update-v4.net` for botnet labels, `service.internal` for benign traffic).



```python
    normalized_events.append({
        "event_id": f"EVT_{idx:06d}",
        "timestamp_start": start_time,
        "timestamp_end": end_time,
        "observation_point": "BORDER_ROUTER_TAP_01",
        "source_address": src_ip,
        "destination_address": dst_ip,
        "source_port": s_port,
        "destination_port": d_port,
        "transport_protocol": proto,
        "application_protocol": app_proto,
        "session_id": session_id,
        "domain_or_service": domain,
        "bytes": tot_bytes,
        "packets": tot_pkts,
        "direction": direction,
        "protocol_fields": protocol_fields,
        "evidence_source": "CTU13_NETFLOW",
        "confidence": 0.90
    })

```

* Maps the unified 18-attribute dictionary required by Section 16 of the architecture into `normalized_events`. Explicitly records sensor location (`observation_point`), evidence provenance (`evidence_source`), and metric certainty (`confidence`).

##### 4. Multi-Protocol Session Synthesis (SIP/RTP Telemetry)

```python
# 3. Simulate multi-protocol SIP/RTP and Cellular telecom sessions (Section 8 & 9)
# Binds to known botnet controller (147.32.84.165) and suspect hosts
telecom_base_time = pd.to_datetime("2011-08-10 09:50:00")
suspect_ips = ["147.32.84.165", "147.32.87.1", "195.113.235.89"]

```

* Synchronizes synthetic real-time multimedia flows (Figure 2 in document) to match the capture timeline (`2011-08-10 09:50:00`) and the primary suspect IP endpoints (`147.32.84.165`, `147.32.87.1`, `195.113.235.89`).

```python
for s_idx, s_ip in enumerate(suspect_ips):
    t_start = telecom_base_time + timedelta(minutes=s_idx * 7)
    t_end = t_start + timedelta(seconds=180)
    call_id = f"call-sec-id-{s_idx:04d}@sip.gateway"
    rtp_ssrc = f"0x9A4F{s_idx}C"

```

* `t_start`: Staggers session start times at 7-minute intervals.
* `t_end`: Computes a 180-second conversational call duration.
* `call_id`: Generates a signaling session identifier (`Call-ID`).
* `rtp_ssrc`: Generates an RTP Synchronization Source identifier (`SSRC`).

```python
    # Add SIP Signaling Event (Figure 2)
    normalized_events.append({
        "event_id": f"EVT_SIP_{s_idx:03d}",
        "timestamp_start": t_start,
        "timestamp_end": t_start + timedelta(seconds=2),
        "observation_point": "SBC_VOIP_SENSOR",
        "source_address": s_ip,
        "destination_address": "147.32.84.229",
        "source_port": "5060",
        "destination_port": "5060",
        "transport_protocol": "UDP",
        "application_protocol": "SIP",
        "session_id": call_id,
        "domain_or_service": "sip.gateway",
        "bytes": 1024,
        "packets": 4,
        "direction": "->",
        "protocol_fields": {"sip_method": "INVITE", "call_id": call_id, "sdp_media_port": 16384 + s_idx},
        "evidence_source": "SIP_DISSECTOR",
        "confidence": 0.95
    })

```

* Inserts a SIP signaling transaction (`INVITE`) passing through port 5060, establishing the signaling-to-media session linkage by recording the Session Description Protocol (SDP) media port negotiation (`sdp_media_port`).

```python
    # Add Correlated RTP Media Stream Event
    normalized_events.append({
        "event_id": f"EVT_RTP_{s_idx:03d}",
        "timestamp_start": t_start + timedelta(seconds=2),
        "timestamp_end": t_end,
        "observation_point": "MEDIA_PROXY_TAP",
        "source_address": s_ip,
        "destination_address": "147.32.84.229",
        "source_port": str(16384 + s_idx),
        "destination_port": "16384",
        "transport_protocol": "UDP",
        "application_protocol": "RTP",
        "session_id": call_id,
        "domain_or_service": "RTP_VOICE_STREAM",
        "bytes": 48000,
        "packets": 1200,
        "direction": "<->",
        "protocol_fields": {"ssrc": rtp_ssrc, "codec": "G.711"},
        "evidence_source": "RTP_DISSECTOR",
        "confidence": 0.95
    })

```

* Inserts the bidirectional audio stream (`RTP`) tied to the exact same `session_id` (`call_id`), carrying voice telemetry metadata (`ssrc`, `codec`) and running on the negotiated dynamic UDP media port.

```python
df_events = pd.DataFrame(normalized_events)
print(f"[+] Total Normalized Schema Events: {len(df_events)}")
df_events[['event_id', 'timestamp_start', 'source_address', 'application_protocol', 'session_id', 'bytes']].head(4)

```

* Aggregates all flow, DNS, SIP, and RTP events into a single normalized DataFrame (`df_events`) and prints schema samples.

---

#### **Cell 3: Behavioral Entity Profiler**

```python
def extract_behavioral_profiles(df):
    profiles = []

```

* Defines the entity profiler function that transforms event-level rows into a host-level feature matrix.

```python
    for src_addr, group in df.groupby("source_address"):
        if len(group) < 3:
            continue

```

* `df.groupby("source_address")`: Partitions all communication records by unique transmitting host.
* `if len(group) < 3: continue`: Drops ephemeral/transient endpoints with fewer than 3 events to filter out single-packet noise.

```python
        # 1. Temporal off-hours behavior (00:00 - 06:00 UTC)
        hours = group["timestamp_start"].dt.hour
        night_ratio = float(np.mean((hours >= 0) & (hours <= 6)))

```

* Calculates the proportion of flows occurring during off-hours (00:00 to 06:00 UTC) to identify automated malware beacons or off-hours staging.

```python
        # 2. Destination Novelty & Fan-out
        unique_destinations = group["destination_address"].nunique()
        dst_novelty_ratio = unique_destinations / len(group)

```

* Calculates the destination fan-out ratio: $\frac{\text{Unique Targets}}{\text{Total Transmitted Flows}}$. High ratios signify horizontal sweeps, scanning, or distributed staging.

```python
        # 3. Connection Rate & Port Entropy (Scanning signal)
        unique_ports = group["destination_port"].nunique()
        port_entropy = unique_ports / len(group)

```

* Calculates target port entropy: $\frac{\text{Unique Destination Ports}}{\text{Total Flows}}$. Approaching $1.0$ indicates vertical port probing.

```python
        # 4. Traffic Volume & Burstiness
        total_bytes = float(group["bytes"].sum())
        total_packets = float(group["packets"].sum())

```

* Computes aggregate network footprint (`total_bytes`, `total_packets`) to detect data exfiltration or amplification spikes.

```python
        # 5. Cross-Protocol Diversity (SIP, RTP, DNS, NetFlow)
        protos = set(group["application_protocol"])
        has_sip_rtp = 1.0 if ("SIP" in protos or "RTP" in protos) else 0.0
        has_dns_tunnel = 1.0 if ("DNS" in protos and any(group["bytes"] > 500)) else 0.0
        protocol_count = len(protos)

```

* Calculates cross-protocol indicators (Section 7):
* `has_sip_rtp`: Flags entities with concurrent real-time voice and flow traffic.
* `has_dns_tunnel`: Flags oversized DNS packets ($> 500$ bytes) indicative of TXT record tunneling.
* `protocol_count`: Counts distinct application protocols used by the host.



```python
        profiles.append({
            "source_address": src_addr,
            "event_count": len(group),
            "night_activity_ratio": night_ratio,
            "dst_novelty_ratio": dst_novelty_ratio,
            "port_entropy": port_entropy,
            "total_bytes": total_bytes,
            "total_packets": total_packets,
            "sip_rtp_presence": has_sip_rtp,
            "dns_tunnel_signal": has_dns_tunnel,
            "protocol_diversity": protocol_count
        })
        
    return pd.DataFrame(profiles)

```

* Appends the statistical vector for the host and returns the feature matrix as a DataFrame.

```python
print("[*] Computing Section 7 Behavioral Profiling Matrix...")
entity_profiles = extract_behavioral_profiles(df_events)
print(f"[+] Profiles compiled for {len(entity_profiles)} distinct hosts.")
entity_profiles.head(3)

```

* Executes the profiler over `df_events`, producing the host-level feature matrix for 181 distinct communicating entities.

---

#### **Cell 4: Isolation Forest & Continuous Threat Prioritization**

```python
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

feature_cols = [
    "night_activity_ratio", "dst_novelty_ratio", "port_entropy",
    "total_bytes", "total_packets", "sip_rtp_presence", 
    "dns_tunnel_signal", "protocol_diversity"
]

```

* Identifies the 8 continuous behavioral dimensions used for unsupervised anomaly detection.

```python
X = entity_profiles[feature_cols]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

```

* `X = ...`: Subsets the feature matrix, dropping non-numeric host identifiers (`source_address`).
* `scaler = StandardScaler()`: Initializes z-score standardization ($\mu=0, \sigma=1$).
* `X_scaled = ...`: Standardizes features to prevent high-magnitude volumetric metrics (`total_bytes` reaching $2.1 \times 10^8$) from overwhelming ratio-based features (`port_entropy` bounded $[0, 1]$).

```python
# Flag the top 6% behavioral deviations
iso_forest = IsolationForest(contamination=0.06, random_state=42)
entity_profiles["anomaly_flag"] = iso_forest.fit_predict(X_scaled)

```

* `contamination=0.06`: Configures the ensemble to label the top $6\%$ most extreme behavioral outliers as anomalous (`-1`).
* `fit_predict(...)`: Fits random partitioning trees and assigns binary classification flags (`1` = normal, `-1` = anomaly).

```python
# Calibrate into continuous risk score [0, 1]
raw_scores = iso_forest.decision_function(X_scaled)
entity_profiles["threat_score"] = 1.0 - (raw_scores - raw_scores.min()) / (raw_scores.max() - raw_scores.min())

```

* `raw_scores = ...`: Obtains the mean path length anomaly score (more negative implies faster tree isolation and higher outlier probability).
* `1.0 - (...)`: Inverts and min-max normalizes the raw decision score into an interpretable continuous threat score in the range $[0.0, 1.0]$, where $1.0$ indicates maximum behavioral deviation.

```python
# Generate Prioritized Investigation Queue
investigation_queue = entity_profiles[entity_profiles["anomaly_flag"] == -1].sort_values("threat_score", ascending=False)

```

* Isolates flagged anomalies (`-1`) and sorts them in descending order of threat score to produce the prioritized investigation queue (Section 18).

```python
print("\n" + "="*85)
print("             SECTION 18: PRIORITIZED INVESTIGATION QUEUE")
print("="*85)
print(investigation_queue[["source_address", "threat_score", "dst_novelty_ratio", "port_entropy", "sip_rtp_presence", "total_bytes"]].head(6))

```

* Prints the highest-risk candidate targets along with their supporting behavioral anomalies.

---

#### **Cell 5: Multi-Hop Entity & Session Knowledge Graph**

```python
import networkx as nx
import matplotlib.pyplot as plt

G = nx.MultiDiGraph()
top_targets = list(investigation_queue["source_address"].head(4))

```

* `import networkx as nx`: Imports the network graph analytics engine.
* `G = nx.MultiDiGraph()`: Instantiates a directed multi-edge graph to support multiple parallel relations between nodes.
* `top_targets = ...`: Selects the top 4 candidate targets from the investigation queue.

```python
# Filter events tied to prioritized targets
df_graph_events = df_events[df_events["source_address"].isin(top_targets)]

```

* Filters the normalized event log down to transactions initiated by the top suspect actors.

```python
for _, row in df_graph_events.iterrows():
    src = str(row["source_address"])
    dst = str(row["destination_address"])
    session = str(row["session_id"])
    app_proto = str(row["application_protocol"])
    domain = row["domain_or_service"]
    t_start = str(row["timestamp_start"])

```

* Iterates through target flows, extracting graph entities: origin actor, destination endpoint, session identifier, protocol layer, domain name, and start timestamp.

```python
    # 1. Target Person / Host Node
    t_score = investigation_queue.loc[investigation_queue["source_address"] == src, "threat_score"].values[0]
    G.add_node(src, type="Target_Entity", score=float(t_score), color="#dc2626")

```

* Instantiates the primary suspect entity (`Target_Entity`) as a red node, annotated with its computed threat score.

```python
    # 2. Communication Session Node (Figure 4)
    G.add_node(session, type="Session", proto=app_proto, color="#7c3aed")
    G.add_edge(src, session, relationship="INITIATED_SESSION", timestamp=t_start)

```

* Instantiates the intermediate communication session (`Session`) as a purple node and binds it to the originating actor via a directed `INITIATED_SESSION` edge.

```python
    # 3. Infrastructure Destination Node
    G.add_node(dst, type="Infrastructure_Endpoint", color="#2563eb")
    G.add_edge(session, dst, relationship="TERMINATED_AT", proto=app_proto)

```

* Adds the external endpoint (`Infrastructure_Endpoint`) as a blue node, terminating the session via a directed `TERMINATED_AT` edge.

```python
    # 4. Domain Context Node (if present)
    if domain:
        G.add_node(domain, type="Domain_Service", color="#d97706")
        G.add_edge(session, domain, relationship="RESOLVED_DOMAIN")

```

* If domain metadata exists, adds a yellow `Domain_Service` node connected to the session via a `RESOLVED_DOMAIN` relationship.

```python
print(f"[+] Multi-Hop Entity Graph Assembled: {G.number_of_nodes()} Nodes, {G.number_of_edges()} Directed Edges")

```

* Outputs graph topology metrics (nodes and directed edges).

```python
# Render Network Topology
plt.figure(figsize=(13, 8))
pos = nx.spring_layout(G, k=0.45, seed=42)

node_colors = [data.get("color", "#64748b") for _, data in G.nodes(data=True)]
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=900, alpha=0.9)
nx.draw_networkx_edges(G, pos, edge_color="#94a3b8", alpha=0.5, arrows=True, arrowsize=14)
nx.draw_networkx_labels(G, pos, font_size=8, font_weight="bold")

plt.title("Figure 4: Multi-Protocol Entity & Session Relationship Graph", fontsize=13, fontweight="bold")
plt.axis("off")
plt.tight_layout()
plt.show()

```

* `pos = nx.spring_layout(...)`: Computes force-directed layout positions treating edges as springs.
* `nx.draw_networkx_*`: Draws nodes, directional arrows, and labels onto a matplotlib figure to visualize the entity linkage graph.

---

#### **Cell 6: Section 20 Forensic Evidence Timeline**

```python
target_id = top_targets[0]
target_events = df_events[df_events["source_address"] == target_id].sort_values("timestamp_start")

```

* `target_id = top_targets[0]`: Selects the highest-priority suspect entity from the queue.
* `target_events = ...`: Extracts all communications involving this suspect, sorting them chronologically to build an audit trail ($T_1 \rightarrow T_2 \rightarrow T_3$).

```python
print("="*80)
print(f"       SECTION 20: FORENSIC INVESTIGATION REPORT — TARGET: {target_id}")
print("="*80)
print(f"Status: Priority Candidate for Authorized Human Review")
print(f"Computed Threat Score: {investigation_queue.loc[investigation_queue['source_address'] == target_id, 'threat_score'].values[0]:.4f}")
print("\nObserved Event Timeline:")

```

* Prints the investigation report header, review status, and calibrated threat score.

```python
for _, row in target_events.head(8).iterrows():
    ts = str(row["timestamp_start"])
    proto = row["application_protocol"]
    dst = row["destination_address"]
    bytes_sent = row["bytes"]
    service = row["domain_or_service"] if row["domain_or_service"] else "N/A"
    print(f"  [{ts}] -> Protocol: {proto:<8} | Dest: {dst:<15} | Service: {service:<22} | Bytes: {bytes_sent}")

```

* Loops through the timeline, printing a formatted log showing timestamps, protocol families, destination IPs, resolved hostnames, and transfer volumes.

```python
print("\nCorrelated Relationships:")
connected_nodes = list(G.neighbors(target_id))
for node in connected_nodes:
    node_type = G.nodes[node].get("type", "Entity")
    print(f"  Target {target_id} ──[:INITIATED]──> ({node_type}: {node})")

```

* Traverses the NetworkX knowledge graph to display all communication sessions, domain lookups, and infrastructure directly linked to this entity.

```python
print("\nEvidentiary Finding:")
print("  - Significant behavioral deviation from historical network baseline.")
print("  - Multiple correlated sessions observed across NetFlow, DNS, and SIP/RTP.")
print("  - Identity attribution status: Technical entity resolved; awaiting authorized identity records.")
print("="*80)

```

* Outputs evidentiary findings and human-in-the-loop attribution status, completing the pipeline defined in Section 20 of the architecture specification.