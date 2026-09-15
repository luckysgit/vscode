Yes, your direction is broadly correct, but I would change the architecture and one important assumption:

**There is no network identifier that is guaranteed to remain unchanged and traceable after VPN, Tor, NAT, device changes, SIM changes, etc.** In counterterrorism, the stronger approach is **multi-protocol correlation across time**, rather than relying on one permanent identifier.

For CT, think of the problem as:

```text
Communication
      |
      v
Protocol Dissection
      |
      v
Identifiers + Metadata + Behavior
      |
      v
Cross-protocol correlation
      |
      v
Device / Account / Session / Infrastructure
      |
      v
Identity attribution
      |
      v
Target assessment
```

## 1. Which protocols are most valuable?

Not all protocols are equally useful for identifying or correlating a target.

### Very high value for identity/session correlation

| Protocol          | Important information                                | Why useful                              |
| ----------------- | ---------------------------------------------------- | --------------------------------------- |
| **SIP**           | From, To, Contact, Call-ID, SDP                      | Voice/session identity and correlation  |
| **SDP**           | Media IP, ports, codecs                              | Links signaling to media                |
| **RTP/RTCP**      | SSRC, timestamps, sequence, media metadata           | Links packets to a media session        |
| **IMS signaling** | Subscriber/session related identifiers               | Telecom identity correlation            |
| **NAS**           | UE/subscriber/session identifiers                    | Mobile network correlation              |
| **NGAP**          | UE identifiers, procedures, causes                   | Links UE to 5G core signaling           |
| **GTP-C**         | TEID, session information                            | Links control-plane sessions            |
| **GTP-U**         | TEID, tunnel endpoints                               | Links user traffic to mobile tunnels    |
| **PFCP**          | PDR/FAR/QER and session information                  | Links SMF control to UPF forwarding     |
| **DHCP**          | Client identifier, MAC, assigned IP                  | Device/IP correlation                   |
| **DNS**           | Query, response, timing                              | Activity and infrastructure correlation |
| **TLS**           | Handshake metadata, certificates, SNI when available | Service/session correlation             |
| **HTTP**          | Host, headers, cookies, user-agent when visible      | Application/account correlation         |

For your project, I would prioritize:

```text
SIP / IMS
   |
   v
NAS + NGAP
   |
   v
GTP-C + GTP-U
   |
   v
DNS
   |
   v
TLS
   |
   v
HTTP
   |
   v
RTP / RTCP
```

But do not interpret this as "these protocols reveal the person directly." They provide **correlation evidence**.

---

# 2. Why IP alone is weak

Your observation is correct:

```text
IP address
    |
    +-- DHCP changes
    +-- NAT
    +-- mobile networks
    +-- VPN
    +-- proxies
    +-- cloud infrastructure
```

So:

```text
IP = useful identifier
IP != permanent identity
```

For example:

```text
10:00
Target -> IP A

10:05
Target -> IP B

10:10
Target -> VPN IP

10:15
Target -> different VPN exit
```

Looking only at IP addresses can therefore produce fragmented observations.

The solution is correlation.

---

# 3. Think in terms of "stable" and "volatile" information

This is a much better model for your CT architecture.

## Volatile identifiers

These can change relatively easily:

```text
Public IP
Private IP
Source port
Destination port
DHCP-assigned address
NAT mapping
VPN exit IP
Tor exit IP
Temporary network addresses
```

Represent them as:

```text
IP_A
   |
   | valid 10:00 to 10:05
   v
IP_B
   |
   | valid 10:05 to 10:15
   v
IP_C
```

The **timestamp** becomes extremely important.

---

# 4. Semi-stable identifiers

These may remain useful for some period, but cannot be considered permanent.

```text
MAC address
Device identifier
SIM-related identifiers
Subscriber identifiers
SIP identity
SIP Call-ID
GTP TEID
TLS/session characteristics
Application account
User-Agent
Device characteristics
```

Their usefulness depends heavily on the network and whether the identifier is exposed, randomized, rotated, encrypted, or changed.

For example:

```text
Device
  |
  +-- MAC
  +-- IP
  +-- TCP ports
  +-- DNS activity
  +-- TLS metadata
  +-- application sessions
```

No single one should be treated as proof of identity.

---

# 5. Stronger concept: relationships are more persistent than identifiers

This is the most important idea for your system.

Instead of asking:

> "Which identifier never changes?"

ask:

> "Which relationships can be correlated across multiple observations?"

For example:

```text
Observation 1
IP A
 |
 +-- DNS activity
 +-- TLS session
 +-- SIP session
 |
 v
Device / account X


Observation 2

IP B
 |
 +-- similar service activity
 +-- related session metadata
 +-- related telecom records
 |
 v
Device / account X
```

You are building evidence that:

```text
IP A ----+
         |
IP B ----+----> Entity X
         |
SIP ----+
         |
GTP ----+
```

This is where a **graph-based architecture** becomes very useful.

---

# 6. VPN: what changes and what may remain observable?

Conceptually:

```text
Target
  |
  v
VPN
  |
  v
Internet
```

An outside observer generally sees:

```text
Target -> VPN endpoint
```

rather than:

```text
Target -> Final destination
```

The target's original public IP may therefore be hidden from the destination.

However, depending on the observation point and available lawful records, other information can still exist, such as:

```text
VPN connection timing
Connection duration
Traffic volume
Packet timing
VPN endpoint
Authentication/account records
Network-provider records
Device/network information
```

So:

```text
VPN
 |
 +-- hides some information
 |
 +-- does NOT make all information disappear
```

---

# 7. Tor

Conceptually:

```text
Target
  |
  v
Tor Guard
  |
  v
Tor Relay
  |
  v
Tor Exit
  |
  v
Destination
```

The destination generally sees the Tor exit rather than the originating client.

Again:

```text
Original IP
     X
     |
     v
Destination
```

But there can still be observable information at different points:

```text
Timing
Traffic volume
Connection behavior
Entry/exit observations
Endpoint activity
Application-level identifiers
Account information
Operational/log records
```

Importantly, **Tor does not make application-layer identity disappear**.

If a person voluntarily authenticates to an account, for example, the network anonymity mechanism does not magically remove the account identity from that service.

---

# 8. What can be hidden or changed?

A useful CT threat-intelligence table is:

| Information        |                  Can change/hide? | General reliability           |
| ------------------ | --------------------------------: | ----------------------------- |
| Public IP          |                               Yes | Low to medium                 |
| Private IP         |                               Yes | Low                           |
| Source port        |                               Yes | Low                           |
| NAT mapping        |                               Yes | Low                           |
| VPN exit IP        |                               Yes | Low                           |
| Tor exit IP        |                               Yes | Low                           |
| MAC address        |                               Yes | Medium                        |
| DHCP address       |                               Yes | Low                           |
| DNS activity       |           Can be encrypted/hidden | Medium                        |
| HTTP information   |                  Can be encrypted | Medium                        |
| TLS metadata       |          Partially hidden/changed | Medium                        |
| SIP identity       | Can be masked depending on system | Medium to high                |
| Call-ID            |                  Session-specific | Medium                        |
| GTP TEID           |                  Session-specific | Medium                        |
| NAS identifiers    |        May be temporary/protected | Medium to high                |
| NGAP identifiers   |          Session/network specific | Medium to high                |
| Account identity   |             Can be changed/abused | High when verified            |
| Subscriber records |            Controlled by operator | High when lawfully correlated |
| Device records     |          Can change or be spoofed | Medium to high                |
| Provider logs      |       Depends on retention/access | Potentially high              |

---

# 9. Things that are NOT "never changing"

I would **not** design your architecture around claims such as:

```text
MAC = permanent
IP = permanent
IMEI = impossible to change
Phone number = permanent
SIP identity = permanent
Device fingerprint = permanent
```

Those assumptions are too strong.

Instead use:

```text
Identifier
+
Timestamp
+
Source
+
Confidence
+
Validity period
```

For example:

```text
Identifier: IP_A
Type: Public IP
Observed: 10:03
Source: Network sensor
Confidence: High
Valid until: 10:11
```

Then another observation:

```text
Identifier: IP_B
Type: Public IP
Observed: 10:12
Source: Network sensor
Confidence: High
```

Your correlation engine can reason about the relationship rather than assuming either IP is permanent.

---

# 10. What I would build for CT

Your architecture could become:

```text
                 NETWORK / TELECOM
                        |
        +---------------+----------------+
        |               |                |
        v               v                v
      PCAP           Live Traffic     Network Logs
        |               |                |
        +---------------+----------------+
                        |
                        v
                PROTOCOL DISSECTION
                        |
       +----------------+----------------+
       |                |                |
       v                v                v
    Network          Telecom          Application
    Protocols        Protocols        Protocols
       |                |                |
       v                v                v
   IP/TCP/UDP       NAS/NGAP/GTP     DNS/HTTP/SIP
                        |
                        v
               INFORMATION EXTRACTION
                        |
                        v
              IDENTIFIER EXTRACTION
                        |
                        v
               TEMPORAL CORRELATION
                        |
                        v
                 FLOW CORRELATION
                        |
                        v
                  ENTITY GRAPH
                        |
        +---------------+---------------+
        |               |               |
        v               v               v
      Device          Account         Session
        |               |               |
        +---------------+---------------+
                        |
                        v
              IDENTITY ATTRIBUTION
                        |
                        v
              TARGET IDENTIFICATION
```

And the **entity graph** could contain nodes such as:

```text
Person
 |
 +---- Account
 |
 +---- Device
 |       |
 |       +---- MAC
 |       +---- IMEI/device identifier
 |
 +---- Subscriber
 |       |
 |       +---- SIM/subscriber identifiers
 |
 +---- IP
 |
 +---- SIP identity
 |
 +---- Call
 |
 +---- GTP session
 |
 +---- DNS domain
 |
 +---- VPN endpoint
 |
 +---- Tor-related observation
```

The important design principle is:

> **Do not search for one identifier that survives everything. Build a temporal, cross-protocol identity graph where changing identifiers are connected through sessions, devices, accounts, telecom records, infrastructure, and timestamps.**

For your specific CT prototype, I would therefore make **SIP/IMS, NAS, NGAP, GTP-C, GTP-U, DNS, DHCP, TLS, HTTP, RTP/RTCP, IP/TCP/UDP** the first protocol-dissection families to study. O-RAN/eCPRI is important for telecom infrastructure attribution, but it is generally more useful for **identifying RAN infrastructure and communications context** than directly identifying an individual person.
