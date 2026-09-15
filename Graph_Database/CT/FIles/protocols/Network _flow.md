

The networking part can be understood as:

```text
Network communication
       |
       v
Packets / Frames / Messages
       |
       +----------------------+
       |                      |
       v                      v
   PCAP file              Live traffic
       |                      |
       |                      |
       +----------+-----------+
                  |
                  v
          Protocol Dissection
                  |
                  v
          Protocol Fields
                  |
                  v
            Flow Creation
                  |
                  v
          Flow-level data
```

## 1. What is the actual networking flow?

When devices communicate:

```text
UE / PC / Server / Router / Phone
             |
             v
      Network communication
             |
             v
     Packets / Frames
             |
             v
    Capture or observation
             |
             v
    Protocol Dissection
             |
             v
    Extract protocol fields
             |
             v
       Build flows
```

For example, when you open a website:

```text
Your PC
  |
  | Ethernet / Wi-Fi
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
HTTPS
  |
  v
Web Server
```

A captured packet may therefore contain:

```text
Ethernet
   |
   v
IPv4
   |
   v
TCP
   |
   v
TLS
   |
   v
Encrypted application data
```

Protocol dissection means taking that data and understanding:

```text
Ethernet
    -> MAC addresses
    -> EtherType

IP
    -> Source IP
    -> Destination IP
    -> Protocol
    -> TTL

TCP
    -> Source port
    -> Destination port
    -> Sequence number
    -> ACK
    -> Flags

TLS
    -> Version
    -> Handshake information
    -> Cipher information
    -> SNI, when available
```

---