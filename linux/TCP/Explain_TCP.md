Your notes are already quite good. To understand TCP deeply, it helps to think of it as **a reliable conversation between two computers**. IP only tries to deliver packets; TCP adds ordering, reliability, flow control, and connection management on top of that.

---

# 1. What problem does TCP solve?

Imagine sending a 100 MB file across the Internet.

Without TCP:

* Packets might arrive out of order.
* Some packets might be lost.
* Some packets might be duplicated.
* The receiver would have no way to know what is missing.
* The sender would not know whether the data arrived.

TCP solves these problems by creating a **reliable byte stream** between two endpoints.

Think of TCP as a courier service that:

* Numbers every piece of data.
* Requires confirmations.
* Resends missing pieces.
* Prevents overwhelming the receiver.
* Starts and ends conversations cleanly.

---

# 2. TCP tracks bytes, not packets

This is one of the most important concepts.

Suppose Alice wants to send:

```
ABCDEFGHIJ
```

There are 10 bytes.

If her Initial Sequence Number (ISN) is 1000:

```
Byte  A B C D E F G H I J
Seq 1000 1001 1002 ... 1009
```

Now suppose she sends all 10 bytes in one TCP segment.

```
Seq = 1000
Data = ABCDEFGHIJ
Length = 10 bytes
```

Bob replies:

```
Ack = 1010
```

This means:

> "I successfully received bytes 1000 through 1009. The next byte I expect is 1010."

Notice that the ACK is **the next expected byte**, not "the last byte received."

---

# 3. Why ACK means “next expected byte”

Suppose Alice sends:

```
Seq = 5000
Length = 300 bytes
```

The bytes covered are:

```
5000
5001
5002
...
5299
```

Bob sends:

```
Ack = 5300
```

Meaning:

```
Received:
5000-5299

Waiting for:
5300
```

This cumulative acknowledgment is efficient because one ACK can confirm many bytes at once.

---

# 4. Why TCP caches sent data

After sending data, TCP **does not immediately forget it**.

Instead:

```
Application
     │
     ▼
TCP sends packet
     │
     ▼
Stores copy in send buffer
     │
     ▼
Waits for ACK
```

Only after receiving the ACK does it delete that cached data.

Example:

```
Alice sends:

Seq=1000
Length=500 bytes
```

If Bob acknowledges:

```
Ack=1500
```

Alice knows all 500 bytes arrived safely and removes them from memory.

If no ACK arrives, she retransmits the same bytes.

---

# 5. Retransmission Timeout (RTO)

Suppose:

```
Alice ---------> Bob
      Data
```

The packet disappears in the network.

```
Alice ----X----> Bob
```

Alice waits.

A timer starts:

```
5...
4...
3...
2...
1...
0
```

When it expires:

```
Alice ---------> Bob
      Same packet again
```

Because TCP retained a copy, it can retransmit exactly what was lost.

---

# 6. What if the ACK is lost instead?

Suppose:

```
Alice ----Data----> Bob
Bob processes it
Bob ----ACK----X--> Alice
```

Alice never sees the ACK.

Eventually she retransmits:

```
Alice ----Same Data----> Bob
```

Bob notices:

```
Sequence already received.
```

So he:

* Discards the duplicate payload.
* Sends the ACK again.

The application does **not** receive duplicated data.

---

# 7. Delayed ACK

Sending an ACK for every segment creates unnecessary traffic.

Instead:

```
Packet 1 --->

Packet 2 --->

Receiver:
      ACK both together
```

So one acknowledgment may confirm multiple packets.

Many TCP implementations also wait briefly (commonly up to around 200 ms in modern systems, though behavior varies) before sending an ACK if no additional data arrives, allowing ACKs to be combined or "piggybacked" with outgoing data.

---

# 8. Window Size: preventing overload

Imagine Bob has only 500 bytes of free buffer space.

He advertises:

```
Window = 500
```

Alice may send at most 500 unacknowledged bytes.

```
Alice:

[100 bytes]
[100 bytes]
[100 bytes]
[100 bytes]
[100 bytes]

Total = 500 bytes
```

Now she must stop.

Only after ACKs free space can she continue sending.

This mechanism is called **flow control**.

---

# 9. Bytes in flight

Bytes in flight are data that have been sent but not yet acknowledged.

Example:

```
Window = 1000 bytes

Alice sends:
300 bytes

Bytes in flight = 300

Alice sends:
200 more

Bytes in flight = 500

ACK for first 300 arrives

Bytes in flight = 200
```

The sender continuously tracks this value to avoid exceeding the receiver’s advertised window.

---

# 10. Zero Window

Suppose Bob’s application cannot keep up:

```
Receive buffer:

██████████ FULL
```

Bob advertises:

```
Window = 0
```

Meaning:

> "Stop sending. I currently have no room."

Alice pauses data transmission.

Later Bob frees memory and advertises:

```
Window = 600
```

Transmission resumes.

---

# 11. TCP is full duplex

TCP allows both sides to send data independently at the same time.

```
Alice ------------------> Bob
       Seq=1000

Alice <------------------ Bob
                    Seq=7000
```

Each direction maintains its own sequence number space.

So:

```
Alice:
Seq = 1200
Ack = 7300

Bob:
Seq = 7300
Ack = 1200
```

The two sequence spaces do not interfere with one another.

---

# 12. Initial Sequence Numbers (ISNs)

Instead of starting at 0 every time:

```
Alice starts at:
84239102

Bob starts at:
591007733
```

Randomized ISNs reduce confusion with old packets from previous connections and improve robustness and security.

---

# 13. Three-way handshake

Suppose:

```
Alice ISN = 1000
Bob ISN   = 3000
```

### Step 1: SYN

```
Alice ---> Bob

Seq = 1000
SYN = 1
```

Meaning:

> "I want to start a connection. My sequence space begins at 1000."

---

### Step 2: SYN-ACK

```
Bob ---> Alice

Seq = 3000
Ack = 1001
SYN = 1
ACK = 1
```

Meaning:

* "I received your SYN."
* "My own sequence starts at 3000."

---

### Step 3: ACK

```
Alice ---> Bob

Seq = 1001
Ack = 3001
ACK = 1
```

Now both sides know each other's starting sequence numbers and the connection is established.

---

# 14. Why SYN consumes one sequence number

Although a SYN carries no application data, TCP conceptually treats it as consuming one sequence number.

So if Alice sends:

```
SYN
Seq = 1000
```

The next byte of actual data begins at:

```
Seq = 1001
```

FIN behaves similarly by consuming one sequence number.

---

# 15. Graceful connection termination (4-way handshake)

Assume Alice is finished sending but can still receive.

### Step 1

```
Alice ---> Bob

FIN
Seq = 5000
```

Meaning:

> "I have no more data to send."

---

### Step 2

```
Bob ---> Alice

ACK = 5001
```

Bob confirms receipt of the FIN.

---

### Step 3

Bob may continue sending remaining data. When finished:

```
Bob ---> Alice

FIN
Seq = 9000
```

---

### Step 4

```
Alice ---> Bob

ACK = 9001
```

The connection is now cleanly closed in both directions.

---

# 16. Reset (RST)

RST is an immediate abort.

```
Alice ----RST----> Bob
```

Both sides discard the connection state instead of performing a graceful shutdown.

RST is commonly used when:

* A packet arrives for a nonexistent connection.
* A serious protocol error occurs.
* An application or operating system aborts the connection immediately.

---

# 17. Putting it all together

A typical TCP session looks like this:

```text
Client                               Server
  |                                     |
  | -------- SYN (Seq=x) -------------> |
  | <----- SYN+ACK (Seq=y, Ack=x+1) ----|
  | -------- ACK (Ack=y+1) -----------> |
  |                                     |
  | ===== Reliable data transfer =====> |
  | <==== Reliable data transfer ====== |
  |   (Seq/Ack numbers track bytes)     |
  |   (Retransmissions if needed)       |
  |   (Window controls flow)            |
  |                                     |
  | -------- FIN ---------------------> |
  | <-------- ACK --------------------- |
  | <-------- FIN --------------------- |
  | -------- ACK ---------------------> |
  |                                     |
Connection closed
```

## Key ideas to remember

* **Sequence numbers identify bytes sent**, not packets.
* **Acknowledgment numbers indicate the next byte expected**, cumulatively acknowledging all earlier bytes.
* **TCP buffers transmitted data and retransmits it if acknowledgments are not received in time.**
* **The advertised window limits how many unacknowledged bytes may be in flight, implementing flow control.**
* **TCP is full duplex**, with independent sequence spaces in each direction.
* **Connection setup uses a three-way handshake (`SYN → SYN-ACK → ACK`) to synchronize initial sequence numbers.**
* **A graceful shutdown uses `FIN` and `ACK` exchanges in both directions, while `RST` aborts the connection immediately.**
