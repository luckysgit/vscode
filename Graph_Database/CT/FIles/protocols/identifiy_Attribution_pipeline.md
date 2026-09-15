Yes. Your idea is better represented as an **identity attribution pipeline**. But there is an important distinction: protocol dissection gives you network and application identifiers, which can sometimes be correlated to a person or device. It does not automatically reveal a person's real identity.

A technically accurate architecture is:

```text
USER / DEVICE
     |
     | Communication
     v
NETWORK
     |
     v
PACKETS / MESSAGES
     |
     v
PROTOCOL IDENTIFICATION
     |
     v
PROTOCOL DISSECTION
     |
     v
EXTRACT INFORMATION
     |
     +-----------------------------+
     |                             |
     v                             v
NETWORK IDENTIFIERS          APPLICATION IDENTIFIERS
     |                             |
     |                             |
Source IP                     SIP identity
Destination IP               User-Agent
MAC address                  Email address
Source port                  Account ID
Destination port             HTTP metadata
Protocol                     DNS queries
GTP identifiers              IMS identifiers
     |                             |
     +-------------+---------------+
                   |
                   v
             CORRELATION
                   |
                   v
          DEVICE / ACCOUNT
                   |
                   v
        IDENTITY ATTRIBUTION
                   |
                   v
             TARGET PERSON
```

## 1. What "target identification" really means

Suppose:

```text
Person
  |
  v
Mobile phone
  |
  v
5G network
  |
  v
Internet
```

You capture traffic.

Protocol dissection might give you:

```text
Source IP       10.x.x.x
Destination IP  142.x.x.x
Protocol        TCP
Source Port     52341
Destination     443
```

That **does not tell you the person**.

You need additional correlation information.

For example:

```text
Packet
  |
  v
IP address
  |
  v
Network session
  |
  v
Subscriber / device identifier
  |
  v
Account
  |
  v
Person
```

The final steps require appropriate authorized data sources.

---

# 2. Your 10 protocol groups fit into this architecture

You can think of each protocol as producing different types of information.

| Protocol | Dissection can provide                             | Possible attribution value            |
| -------- | -------------------------------------------------- | ------------------------------------- |
| Ethernet | MAC address, VLAN                                  | Device/network                        |
| ARP      | IP <-> MAC mapping                                 | Device                                |
| IP       | Source/destination IP                              | Network endpoint                      |
| TCP      | Ports, flags, sequence information                 | Connection                            |
| UDP      | Ports, length                                      | Connection                            |
| DNS      | Query/domain information                           | Activity/domain correlation           |
| DHCP     | Client identifier, assigned IP                     | Device/network correlation            |
| HTTP     | Host, method, headers                              | Application/session                   |
| TLS      | Certificate/handshake metadata, SNI when available | Service/session correlation           |
| SSH      | Connection metadata                                | Endpoint/session                      |
| SIP      | Call identifiers, addresses, signaling             | Subscriber/session correlation        |
| SDP      | Media addresses, ports, codecs                     | Voice session                         |
| RTP      | SSRC, timestamps, media flow                       | Media-session correlation             |
| BGP      | Routing information                                | Network/infrastructure                |
| SNMP     | Device/network information                         | Infrastructure                        |
| GTP      | Tunnel/session information                         | Mobile subscriber/session correlation |
| NGAP     | UE-related signaling identifiers                   | 5G session correlation                |
| NAS      | Subscriber/session signaling identifiers           | Mobile session correlation            |
| PFCP     | User-plane session rules                           | 5G session correlation                |
| eCPRI    | DU/RU traffic information                          | RAN equipment/flow                    |
| PTP      | Timing/synchronization information                 | RAN infrastructure                    |

Notice that some protocols are much more useful for **person/device attribution** than others.

---

# 3. Example: Internet user

Imagine:

```text
User
 |
 | opens website
 v
Phone
 |
 v
Wi-Fi
 |
 v
Router
 |
 v
Internet
```

Captured communication:

```text
Ethernet
    |
    v
IP
    |
    v
TCP
    |
    v
TLS
    |
    v
HTTP
```

Dissection:

```text
Ethernet
    MAC = XX:XX:XX:XX

IP
    Source = 192.168.1.20
    Destination = Web Server

TCP
    Source Port = 52341
    Destination Port = 443

TLS
    SNI = example.com      [when available]

HTTP
    encrypted
```

Now you have:

```text
Device
   |
   +-- MAC
   +-- private IP
   |
   +-- connection
   |
   +-- destination
   |
   +-- domain/service
```

Still:

```text
Device != Person
```

To associate the device with a person, you need an authorized identity source, such as an account or subscriber record.

---

# 4. Example: 5G is more interesting

For your 5G work, the architecture becomes:

```text
Person
   |
   v
UE / Mobile phone
   |
   v
gNB
   |
   v
5G Core
   |
   +----------------------+
   |                      |
   v                      v
Control Plane          User Plane
   |                      |
   v                      v
NAS                     GTP-U
   |
   v
NGAP
   |
   v
AMF
```

You can dissect:

```text
NAS
  |
  +-- registration information
  +-- session procedures
  +-- mobile signaling

NGAP
  |
  +-- UE identifiers
  +-- procedures
  +-- causes
  +-- information elements

GTP-U
  |
  +-- TEID
  +-- tunnel information
  +-- inner IP traffic
```

Then correlate:

```text
NAS
 |
 v
UE/session identifier
 |
 v
NGAP
 |
 v
gNB/AMF session
 |
 v
GTP tunnel
 |
 v
User-plane traffic
```

This gives you a **network session identity**.

A telecom operator could potentially correlate that authorized network identity with subscriber records to identify the subscriber.

---

# 5. SIP gives another strong example

For VoIP/IMS:

```text
Person
   |
   v
Phone
   |
   v
IMS
   |
   v
SIP
```

Dissection:

```text
INVITE
 |
 +-- From
 +-- To
 +-- Call-ID
 +-- Contact
 +-- CSeq
 +-- Via
 |
 v
SDP
 |
 +-- Media IP
 +-- Media port
 +-- Codec
 |
 v
RTP
 |
 +-- SSRC
 +-- Sequence
 +-- Timestamp
```

You can build:

```text
SIP signaling
      |
      v
Call-ID
      |
      v
SDP
      |
      v
RTP stream
      |
      v
Complete call session
```

Here, **SIP is much more identity-oriented than something like Ethernet**, because signaling can contain application-level user identities.

---

# 6. The key concept is correlation

Your actual system should not be:

```text
Protocol
   |
   v
Person
```

It should be:

```text
Protocol
   |
   v
Dissection
   |
   v
Information
   |
   v
Identifiers
   |
   v
Correlation
   |
   v
Device / Session
   |
   v
Authorized identity data
   |
   v
Person
```

This is much more technically correct.

---

# 7. Your final architecture

For a **network intelligence / target attribution system**, I would draw it like this:

```text
                    USER / DEVICE
                         |
                         v
                NETWORK COMMUNICATION
                         |
                         v
              PACKETS / FRAMES / MESSAGES
                         |
          +--------------+---------------+
          |                              |
          v                              v
     PCAP / CAPTURE                 LIVE TRAFFIC
          |                              |
          +--------------+---------------+
                         |
                         v
                PROTOCOL IDENTIFICATION
                         |
                         v
                 PROTOCOL DISSECTION
                         |
          +--------------+---------------+
          |              |               |
          v              v               v
       L2/L3          L4            Application
     Ethernet/IP    TCP/UDP       DNS/HTTP/SIP
          |              |               |
          +--------------+---------------+
                         |
                         v
                 INFORMATION EXTRACTION
                         |
                         v
                  IDENTIFIER EXTRACTION
                         |
        +----------------+----------------+
        |                |                |
        v                v                v
     Network          Device           Session
     identifiers     identifiers      identifiers
        |                |                |
        +----------------+----------------+
                         |
                         v
                  FLOW / SESSION
                    CORRELATION
                         |
                         v
                   ENTITY GRAPH
                         |
          +--------------+--------------+
          |                             |
          v                             v
       DEVICE                        ACCOUNT
          |                             |
          +--------------+--------------+
                         |
                         v
                IDENTITY ATTRIBUTION
                         |
                         v
                 TARGET PERSON
```

The **Entity Graph** in the middle is especially useful for your project:

```text
Person
  |
  +---- Account
  |       |
  |       +---- IP
  |
  +---- Device
  |       |
  |       +---- MAC
  |       +---- IMS identity
  |
  +---- Session
          |
          +---- SIP Call-ID
          +---- GTP TEID
          +---- IP flow
          +---- DNS activity
```

That is where your different protocol dissections can be combined into a single network intelligence picture.

One important boundary: this should be designed for **authorized network monitoring, incident response, telecom operations, or lawful investigations**. Protocol dissection itself is normal network engineering; linking technical identifiers to a real person requires appropriate authorization and access to the relevant identity records.
