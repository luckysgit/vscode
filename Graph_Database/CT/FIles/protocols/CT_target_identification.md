- There is no network identifier that is guaranteed to remain unchanged and traceable after VPN, Tor, NAT, device changes, SIM changes, etc. In counterterrorism, the stronger approach is multi-protocol correlation across time, rather than relying on one permanent identifier.

- For **counterterrorism (CT)**, do not design the system around "find the person from one IP or one packet." IPs, ports, VPNs, NAT, DHCP assignments, mobile addresses, and other network attributes can change quickly.

Instead, design it around **multi-protocol identity and activity correlation**.

```text
Communication
      |
      v
Packets / Messages
      |
      v
Protocol Dissection
      |
      v
Identity + Session + Behavioral Information
      |
      v
Cross-Protocol Correlation
      |
      v
Persistent Entity / Target
      |
      v
Analyst Investigation
```

## 1. Which protocols are most valuable?

For a CT-oriented network intelligence prototype, I would prioritize them like this:

| Priority | Protocol / source       | Why it matters                                         |
| -------- | ----------------------- | ------------------------------------------------------ |
| 1        | **SIP**                 | VoIP signaling, call/session identifiers, endpoints    |
| 2        | **SDP**                 | Media endpoints, ports, codecs, session information    |
| 3        | **RTP / RTCP**          | Voice/video session and media-flow correlation         |
| 4        | **DNS**                 | Domain activity and infrastructure correlation         |
| 5        | **DHCP**                | Device/IP assignment correlation                       |
| 6        | **HTTP/HTTPS metadata** | Web/application communication metadata                 |
| 7        | **TLS**                 | TLS/session metadata, certificates, SNI when available |
| 8        | **GTP-C / GTP-U**       | Mobile network sessions and user-plane correlation     |
| 9        | **NAS / NGAP**          | 4G/5G control-plane/session identifiers                |
| 10       | **IP/TCP/UDP**          | Foundation for almost everything above                 |
| 11       | **eCPRI / O-RAN**       | RAN infrastructure and DU/RU traffic                   |
| 12       | **NetFlow/IPFIX**       | Useful when packet payload is unavailable              |

The key is that **SIP/RTP are not necessarily "better" than IP/TCP**. They sit at different levels.

For example:

```text
Ethernet
   |
   v
IP
   |
   v
UDP
   |
   +----> SIP
   |
   +----> RTP
```

The lower protocols provide network/session information, while SIP can provide much more meaningful **communication-session information**.

---

# 2. Why SIP is particularly interesting

Suppose you have:

```text
A  <----------->  B
        SIP
```

A SIP transaction may contain things such as:

```text
Call-ID
From
To
Contact
CSeq
Via
SDP
```

You can correlate:

```text
SIP
 |
 +---- Call-ID
 |
 +---- Source
 |
 +---- Destination
 |
 +---- SDP
         |
         +---- media IP
         +---- media port
         +---- codec
 |
 v
RTP
 |
 +---- SSRC
 +---- sequence
 +---- timestamp
```

So instead of treating every packet independently:

```text
Packet 1
Packet 2
Packet 3
...
Packet 500
```

you reconstruct:

```text
Communication Session
        |
        +---- SIP signaling
        |
        +---- SDP negotiation
        |
        +---- RTP media
        |
        +---- endpoints
        |
        +---- timing
```

That is much more useful for network intelligence.

---

# 3. Your point about changing IPs is very important

Yes.

An IP address should generally **not be treated as the person**.

For example:

```text
10:00
Person A -> IP 100.1.1.10

10:05
Person A -> IP 100.1.1.25

10:10
Person A -> IP 100.1.1.42
```

Or:

```text
                +--> IP 1
                |
Device/User ----+--> IP 2
                |
                +--> IP 3
```

Reasons include:

```text
DHCP
NAT
Carrier NAT
Mobile IP assignment
VPN
Roaming
Network changes
Dynamic addressing
```

So:

```text
IP = temporary network identifier
```

not necessarily:

```text
IP = person
```

---

# 4. This is why correlation becomes the core

Instead of:

```text
IP
 |
 v
Person
```

you want:

```text
IP
 |
 +---- timestamp
 |
 +---- port
 |
 +---- protocol
 |
 +---- MAC/device information
 |
 +---- DNS activity
 |
 +---- SIP identity
 |
 +---- mobile session identifiers
 |
 +---- flow
 |
 v
SESSION
 |
 v
DEVICE / ACCOUNT
 |
 v
AUTHORIZED IDENTITY
```

The **timestamp** is extremely important.

For example:

```text
10:01:32
IP = X
Port = 50001

10:01:33
SIP Call-ID = ABC

10:01:34
RTP SSRC = XYZ

10:01:35
GTP TEID = 12345
```

Individually, these identifiers may be weak.

Together:

```text
IP
 +
time
 +
SIP
 +
RTP
 +
GTP
```

can establish that several observations belong to the same communication/session or infrastructure context.

---

# 5. For 4G/5G, your idea becomes even stronger

Your CT architecture could have:

```text
                  4G / 5G NETWORK
                         |
        +----------------+----------------+
        |                                 |
        v                                 v
   CONTROL PLANE                      USER PLANE
        |                                 |
        v                                 v
   NAS / NGAP                         GTP-U
        |                                 |
        v                                 v
   Session identity                 IP traffic
        |                                 |
        +---------------+-----------------+
                        |
                        v
                  Correlation
```

Then potentially correlate:

```text
NAS
 |
 v
UE/session information
 |
 v
NGAP
 |
 v
gNB
 |
 v
GTP session
 |
 v
User-plane IP flow
```

This is much more useful than simply collecting IP addresses.

---

# 6. I would divide your CT protocol work into 4 layers

### Layer 1, Network identity

```text
Ethernet
ARP
IP
TCP
UDP
DHCP
```

Purpose:

```text
Where is the communication coming from?
Where is it going?
What device/network is involved?
```

### Layer 2, Application identity

```text
DNS
HTTP
TLS
SIP
SDP
```

Purpose:

```text
What service?
What domain?
What communication session?
What application-level identifiers?
```

### Layer 3, Telecom identity

```text
GTP-C
GTP-U
NAS
NGAP
SIP/IMS
```

Purpose:

```text
Which mobile session?
Which network element?
Which tunnel?
Which signaling procedure?
```

### Layer 4, Correlation

```text
Timestamp
      |
      v
IP
      |
      v
Session
      |
      v
Device
      |
      v
Account / subscriber
      |
      v
Authorized identity data
```

This is where the different protocol observations become one **entity/session graph**.

---

# 7. Your proposed CT pipeline should therefore be

I would modify your original idea from:

```text
USER
  |
  v
NETWORK
  |
  v
PROTOCOL
  |
  v
DISSECTION
  |
  v
INFORMATION
  |
  v
TARGET IDENTIFICATION
```

to:

```text
COMMUNICATION
      |
      v
NETWORK TRAFFIC
      |
      v
PACKETS / MESSAGES / TRACES
      |
      v
PROTOCOL IDENTIFICATION
      |
      v
PROTOCOL DISSECTION
      |
      v
INFORMATION EXTRACTION
      |
      +----------------------+
      |                      |
      v                      v
NETWORK IDENTIFIERS     APPLICATION /
                       TELECOM IDENTIFIERS
      |                      |
      +----------+-----------+
                 |
                 v
        TIME + FLOW CORRELATION
                 |
                 v
        SESSION RECONSTRUCTION
                 |
                 v
          ENTITY CORRELATION
                 |
                 v
      DEVICE / ACCOUNT / INFRASTRUCTURE
                 |
                 v
       AUTHORIZED IDENTITY DATA
                 |
                 v
       TARGET IDENTIFICATION
```

### The most important idea

**Do not make "IP address" the identity. Make the combination of protocol identifiers, timestamps, sessions, flows, devices, accounts, and authorized identity records the basis for attribution.**

For your project, I would start the actual protocol-dissection implementation with:

```text
1. Ethernet
2. IPv4/IPv6
3. TCP/UDP
4. DNS
5. DHCP
6. SIP
7. SDP
8. RTP/RTCP
9. TLS
10. GTP-C/GTP-U
11. NAS
12. NGAP
13. eCPRI/PTP
```

That gives you a progression from **basic network traffic -> communication sessions -> telecom sessions -> cross-protocol correlation**, which is much closer to the CT intelligence problem you are describing.
