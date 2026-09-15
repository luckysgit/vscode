## **protocol stack**

All important modern networking protocols**, 

| #  | Protocol       | Full form                           | Main use                            | OSI   |
| -- | -------------- | ----------------------------------- | ----------------------------------- | ----- |
| 1  | **HTTP/HTTPS** | Hypertext Transfer Protocol         | Web/API communication               | L7    |
| 2  | **DNS**        | Domain Name System                  | Domain name to IP resolution        | L7    |
| 3  | **DHCP**       | Dynamic Host Configuration Protocol | Automatically assigns IP addresses  | L7    |
| 4  | **SIP**        | Session Initiation Protocol         | VoIP/video call signaling           | L7    |
| 5  | **RTP**        | Real-time Transport Protocol        | Voice/video media                   | L7    |
| 6  | **TCP**        | Transmission Control Protocol       | Reliable data delivery              | L4    |
| 7  | **UDP**        | User Datagram Protocol              | Fast, connectionless communication  | L4    |
| 8  | **QUIC**       | Quick UDP Internet Connections      | Modern transport for HTTP/3         | L4    |
| 9  | **TLS**        | Transport Layer Security            | Encryption and secure communication | L6/L7 |
| 10 | **BGP**        | Border Gateway Protocol             | Routing between Internet networks   | L7    |

### For 4G/5G telecom

Some additional protocols are particularly important:

* **SIP**: call/session signaling
* **RTP**: voice/video packets
* **GTP**: carries user/control traffic in mobile networks
* **PFCP**: controls packet forwarding in 5G core
* **HTTP/2**: used extensively in 5G core service-based architecture
* **SCTP**: reliable transport, used by protocols such as NGAP
* **NGAP**: communication between 5G gNB and AMF
* **NAS**: UE signaling with the 5G core
* **eCPRI**: transport interface used in O-RAN fronthaul
* **NETCONF/RESTCONF**: network configuration and management

-----------------------------------------------------------------------------------------------------

Here is a practical table of common packet types and the protocol stack you would typically see in a PCAP.

| Packet / Traffic type | Typical protocol stack                  | What it is used for                            |
| --------------------- | --------------------------------------- | ---------------------------------------------- |
| **Ethernet frame**    | Ethernet                                | Local network communication                    |
| **ARP packet**        | Ethernet -> ARP                         | Find MAC address from IP address               |
| **IPv4 packet**       | Ethernet -> IPv4                        | Network-layer packet delivery                  |
| **IPv6 packet**       | Ethernet -> IPv6                        | IPv6 packet delivery                           |
| **TCP packet**        | Ethernet -> IP -> TCP                   | Reliable transport                             |
| **UDP packet**        | Ethernet -> IP -> UDP                   | Fast, connectionless transport                 |
| **ICMP packet**       | Ethernet -> IP -> ICMP                  | Network diagnostics, errors                    |
| **DNS query**         | Ethernet -> IP -> UDP -> DNS            | Domain name lookup                             |
| **DNS over TCP**      | Ethernet -> IP -> TCP -> DNS            | DNS communication over TCP                     |
| **DHCP**              | Ethernet -> IP -> UDP -> DHCP           | Obtain IP configuration                        |
| **HTTP**              | Ethernet -> IP -> TCP -> HTTP           | Web communication                              |
| **HTTPS**             | Ethernet -> IP -> TCP -> TLS -> HTTP    | Encrypted web communication                    |
| **HTTP/3**            | Ethernet -> IP -> UDP -> QUIC -> HTTP/3 | Modern web communication                       |
| **SSH**               | Ethernet -> IP -> TCP -> SSH            | Secure remote login                            |
| **FTP**               | Ethernet -> IP -> TCP -> FTP            | File transfer                                  |
| **SMTP**              | Ethernet -> IP -> TCP -> SMTP           | Sending email                                  |
| **IMAP**              | Ethernet -> IP -> TCP -> IMAP           | Reading email                                  |
| **SIP**               | Ethernet -> IP -> UDP/TCP -> SIP        | Call/session signaling                         |
| **RTP**               | Ethernet -> IP -> UDP -> RTP            | Voice/video media                              |
| **RTCP**              | Ethernet -> IP -> UDP -> RTCP           | RTP quality/control information                |
| **NTP**               | Ethernet -> IP -> UDP -> NTP            | Time synchronization                           |
| **SNMP**              | Ethernet -> IP -> UDP -> SNMP           | Network monitoring                             |
| **BGP**               | Ethernet -> IP -> TCP -> BGP            | Internet routing                               |
| **OSPF**              | Ethernet -> IP -> OSPF                  | Internal network routing                       |
| **GTP-U**             | Ethernet -> IP -> UDP -> GTP-U -> IP    | Mobile user-plane traffic                      |
| **GTP-C**             | Ethernet -> IP -> UDP -> GTP-C          | Mobile control/session signaling               |
| **PFCP**              | Ethernet -> IP -> UDP -> PFCP           | 4G/5G packet forwarding control                |
| **NGAP**              | Ethernet -> IP -> SCTP -> NGAP          | 5G RAN to core signaling                       |
| **NAS 5G**            | Ethernet -> IP -> SCTP -> NGAP -> NAS   | UE/core signaling, usually carried within NGAP |
| **SCTP**              | Ethernet -> IP -> SCTP                  | Reliable telecom signaling transport           |
| **eCPRI**             | Ethernet -> eCPRI                       | 5G/O-RAN fronthaul                             |
| **VLAN traffic**      | Ethernet -> 802.1Q -> IP -> ...         | Network segmentation                           |

### The important pattern

You can generally visualize a packet like this:

```text
Layer 2
Ethernet
   |
   v
Layer 3
IP
   |
   v
Layer 4
TCP / UDP / SCTP
   |
   v
Layer 5-7
Application protocol
```

For example:

```text
Web:
Ethernet -> IP -> TCP -> TLS -> HTTP
```

```text
DNS:
Ethernet -> IP -> UDP -> DNS
```

```text
VoIP:
Ethernet -> IP -> UDP -> RTP
```

```text
SIP signaling:
Ethernet -> IP -> UDP/TCP -> SIP
```

```text
5G signaling:
Ethernet -> IP -> SCTP -> NGAP -> NAS
```

```text
5G user traffic:
Ethernet -> IP -> UDP -> GTP-U -> IP
```

### One important correction

**"Packet type" and "protocol" are not exactly the same thing.**

For example:

```text
DNS packet
```

really means a packet carrying DNS data. Its complete stack might be:

```text
Ethernet
   |
IPv4
   |
UDP
   |
DNS
```

Likewise, a **TCP packet** might simply be:

```text
Ethernet
   |
IPv4
   |
TCP
```

or it could carry an application protocol:

```text
Ethernet
   |
IPv4
   |
TCP
   |
HTTP
```

This distinction is important when you start doing **PCAP protocol dissection**, because one captured packet can contain multiple nested protocol layers.
