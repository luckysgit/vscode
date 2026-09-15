While the notebook executes end-to-end and covers the technical baseline of an MVP, several requirements defined in the architecture specification remain unbuilt.

---

### What Is Already Completed

* **Flow Telemetry Ingestion:** Download and line-bounded parsing of real CTU-13 NetFlow records.


* **Event Normalization:** Mapping fields to the 18-attribute schema (timestamps, duration, addresses, ports, protocols, metadata).


* **Behavioral Profiling:** Entity grouping by `source_address` and metric generation (fan-out, entropy, volumes, protocol presence).


* **Anomaly Detection & Ranking:** Scaled feature inference via Isolation Forest and $[0, 1]$ threat score calibration.


* **Heterogeneous Graph Construction:** Directed multi-graph linking Entities, Sessions, Infrastructure, and Domains.



---

### What Is Still Remaining According to the Specification

#### 1. Real Multi-Protocol Dissection (Sections 4, 5, 8, and 9)

* **Status:** Partially Simulated.
* **Missing Work:** In the notebook, DNS, SIP, and RTP records are synthetically constructed via hardcoded Python dictionaries. The architecture document specifies **actual protocol dissection** (e.g., using `pyshark`, `scapy`, or `dpkt`) on real PCAP files to dynamically extract headers such as:
* SIP: `Call-ID`, `From`, `To`, `CSeq`, `Via`, and SDP media attributes.


* RTP: `SSRC`, sequence numbers, and packet timestamps.


* DNS/TLS: Query names, resource records, and TLS SNI.





#### 2. Telecom Layer Ingestion (Section 5, Priority 6)

* **Status:** Not Started.
* **Missing Work:** The document specifically requires mobile telecommunications context (NAS, NGAP, GTP-C, GTP-U, PFCP). Integrating a cellular trace (such as 5G-NIDD) to map `(:Subscriber)-[:ASSOCIATED_WITH]->(:TEID_Tunnel)-[:ENCAPSULATES]->(:IP_Flow)` is still needed for full multi-source correlation.



#### 3. Formal Forensic Timeline Generation (Section 20)

* **Status:** Missing from the script.
* **Missing Work:** The current notebook generates the graph and outputs top candidates, but does not print the structured **Section 20 Investigation Report**. It needs the automated timeline generator showing:


* Chronological progression: $T_1 (\text{DNS}) \rightarrow T_2 (\text{Network Session}) \rightarrow T_3 (\text{SIP}) \rightarrow T_4 (\text{RTP})$.


* Summary of correlated relationships.


* Evidentiary findings and formal identity attribution disclaimers.





#### 4. Graph Density & Layout Optimization (Cell 5)

* **Status:** Unrefined.
* **Missing Work:** As noted in the test run, plotting all unfiltered sessions generated over 4,300 nodes and 4,400 edges. To make the topology clear and interpretable for review, edge aggregation or top-N link sampling needs to be implemented.

#### 5. External Identity Resolution Interface (Sections 3, 14, and 18)

* **Status:** Architectural Stub.
* **Missing Work:** The boundary where a resolved technical entity (`Target_Entity`) maps to authorized identity records (subscriber accounts, SIM registrations, or device identifiers) requires mock lookup tables or schema interfaces to test the final identity attribution stage.