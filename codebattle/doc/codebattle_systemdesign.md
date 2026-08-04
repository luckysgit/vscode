# CodeBattle — System Design Document

> End-to-end system design covering architecture, data flow, components, scalability, and trade-offs.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Breakdown](#component-breakdown)
4. [Data Flow Diagrams](#data-flow-diagrams)
5. [Database Design](#database-design)
6. [Caching Strategy](#caching-strategy)
7. [Real-time Architecture](#real-time-architecture)
8. [Code Execution Pipeline](#code-execution-pipeline)
9. [API Design](#api-design)
10. [Authentication & Authorization](#authentication--authorization)
11. [File & Media Storage](#file--media-storage)
12. [Notification System](#notification-system)
13. [Search System](#search-system)
14. [Scalability Design](#scalability-design)
15. [Fault Tolerance & Reliability](#fault-tolerance--reliability)
16. [Security Architecture](#security-architecture)
17. [Monitoring Architecture](#monitoring-architecture)
18. [Capacity Estimation](#capacity-estimation)
19. [Trade-off Decisions](#trade-off-decisions)

---

## System Requirements

### Functional Requirements

- Users can create rooms with a unique code + QR, others join via code/QR/link
- Rooms support 2 to 100 players (free) or unlimited (paid)
- Users compete by solving programming problems live in any of 10 languages
- Code is executed securely and results returned in real time
- Users can publish problems (public / private / connections-only)
- Users can build Problists (curated problem collections)
- Connections between users are mutual (QR/code-based, no follow system)
- Live leaderboard updates as players submit
- Post-match: results, replays, breakdowns
- Daily problems, streaks, XP, badges, rankings
- Paid tier: unlimited room size, interview mode, org accounts, tournaments

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| API response time | < 200ms (p95) |
| WebSocket latency | < 100ms |
| Code execution time | < 3s (including sandbox overhead) |
| Availability | 99.9% uptime |
| Concurrent rooms | 500+ simultaneously |
| Concurrent users | 10,000+ |
| Data durability | No data loss on submission results |
| Security | No user code escapes sandbox |

---

## High-Level Architecture

```
                    ┌──────────────────────────────┐
                    │         Cloudflare            │
                    │   WAF · DDoS · CDN · HTTPS    │
                    └──────────────┬───────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
   ┌──────▼──────┐         ┌───────▼───────┐       ┌───────▼───────┐
   │  Frontend   │         │  API Server   │       │  WS Server    │
   │  Next.js    │◄───────►│  Node.js      │◄─────►│  Socket.io    │
   │  Vercel     │  HTTPS  │  Express      │       │  Railway      │
   └─────────────┘         └───────┬───────┘       └───────┬───────┘
                                   │                        │
                    ┌──────────────┼────────────────────────┘
                    │              │              │
             ┌──────▼─────┐ ┌─────▼──────┐ ┌────▼────────┐
             │ PostgreSQL  │ │   Redis    │ │  BullMQ     │
             │  Supabase   │ │  Upstash   │ │  Job Queue  │
             │  Main DB    │ │  Cache +   │ │  Workers    │
             └─────────────┘ │  Sessions  │ └────┬────────┘
                             └────────────┘      │
                                            ┌────▼────────┐
                                            │   Judge0    │
                                            │  Isolated   │
                                            │  Droplet    │
                                            │  (Docker)   │
                                            └─────────────┘
```

---

## Component Breakdown

### 1. Frontend (Next.js)

**Responsibilities:**
- Render UI, handle routing, manage client-side state
- Connect to WebSocket server for live room updates
- Display Monaco code editor
- Generate and scan QR codes

**Key Design Decisions:**
- Server-side rendering for problem pages (SEO, fast load)
- Client-side only for room pages (real-time, no SSR needed)
- Monaco editor loaded dynamically (heavy, skip SSR)
- Zustand for local state, Socket.io for shared room state

```
Pages:
    / (landing)
    /dashboard
    /onboarding
    /room/[code]          ← fully client-side
    /problems             ← SSR for SEO
    /problems/[id]
    /problists
    /profile/[username]   ← SSR for SEO
    /leaderboard
    /org/[slug]
```

---

### 2. API Server (Node.js + Express)

**Responsibilities:**
- Handle all HTTP REST requests
- Validate inputs, enforce auth
- Coordinate between DB, Redis, Judge0, BullMQ
- Emit events to WS server via Redis pub/sub

**Key Design Decisions:**
- Stateless — horizontal scaling possible
- API server never runs user code directly
- Communicates with WS server via Redis pub/sub (not direct call)
- All business logic lives here, not in the WS server

---

### 3. WebSocket Server (Socket.io)

**Responsibilities:**
- Maintain persistent connections per user
- Manage room channels (Socket.io rooms)
- Broadcast real-time events (progress, leaderboard, countdown)
- Listen to Redis pub/sub for events from API server

**Key Design Decisions:**
- Separate process from API server (different scaling profile)
- No database writes — read-only from Redis
- Sticky sessions required if multiple WS instances (use Redis adapter)

```typescript
// Redis adapter for multi-instance WS scaling
import { createAdapter } from "@socket.io/redis-adapter";
io.adapter(createAdapter(pubClient, subClient));
```

---

### 4. PostgreSQL (Supabase)

**Responsibilities:**
- Persistent storage for all entities
- Source of truth for users, rooms, problems, submissions

**Key Design Decisions:**
- Row-level security (RLS) enabled on Supabase
- Read replicas for leaderboard + public problem queries
- Connection pooling via PgBouncer (built into Supabase)
- Submissions table partitioned by month (high volume)

---

### 5. Redis (Upstash)

**Responsibilities:**
- Live room state (leaderboard, player list, activity)
- Rate limiting counters
- Session cache
- BullMQ job queue backend
- Pub/sub between API server and WS server

**Key Design Decisions:**
- All room state in Redis, not PostgreSQL (low latency reads)
- Room state auto-expires after 24h (TTL)
- Redis is NOT the source of truth — DB is. Redis is cache only.

---

### 6. Judge0 (Isolated DigitalOcean Droplet)

**Responsibilities:**
- Execute untrusted user code safely
- Run test cases and return results
- Support all 10 languages

**Key Design Decisions:**
- Completely isolated server — separate from all application servers
- Firewall: only accepts requests from API server IP
- Each execution: Docker container, destroyed after run
- Hard limits: 2s CPU, 256MB RAM, no network, no file write

---

### 7. BullMQ Workers

**Responsibilities:**
- Process code submission jobs asynchronously
- Run scheduled jobs (daily problem, weekly room, cleanup)
- Send notifications

**Key Design Decisions:**
- Submissions are async — user gets immediate "submitted" response, result comes via WebSocket
- Job retries: 3 attempts with exponential backoff
- Failed jobs logged to Sentry

---

## Data Flow Diagrams

### Flow 1: User Creates and Starts a Room

```
User                Frontend              API Server         PostgreSQL     Redis
 │                     │                      │                  │            │
 ├─ "Create Room" ────►│                      │                  │            │
 │                     ├─ POST /rooms ────────►│                  │            │
 │                     │                      ├─ INSERT room ────►│            │
 │                     │                      ├─ Generate code    │            │
 │                     │                      ├─ SET room state ──────────────►│
 │                     │◄─ { room_code, qr } ─┤                  │            │
 │◄─ Show lobby ───────┤                      │                  │            │
 │                     │                      │                  │            │
 ├─ "Start Room" ─────►│                      │                  │            │
 │                     ├─ POST /rooms/start ──►│                  │            │
 │                     │                      ├─ UPDATE status ──►│            │
 │                     │                      ├─ Pub: room:start ─────────────►│ (Redis pub/sub)
 │                     │                      │                  │            │
 │             WS Server reads Redis pub/sub                      │            │
 │             WS Server emits to all room members                │            │
 │◄─ room:countdown ───┤                      │                  │            │
```

---

### Flow 2: User Submits Code

```
User           Frontend        API Server      BullMQ       Judge0        Redis       WS Server
 │                │                │              │             │             │             │
 ├─ Submit ──────►│                │              │             │             │             │
 │                ├─POST /submit──►│              │             │             │             │
 │                │                ├─ Validate    │             │             │             │
 │                │                ├─ INSERT sub  │             │             │             │
 │                │                ├─ Add job ───►│             │             │             │
 │                │◄─ { id, pend}─ ┤              │             │             │             │
 │◄─ "Submitted"──┤                │              ├─ POST ─────►│             │             │
 │                │                │              │ /submit     │             │             │
 │                │                │              │◄─ token ────┤             │             │
 │                │                │              ├─ Poll result►│            │             │
 │                │                │              │◄─ { passed }─┤            │             │
 │                │                │              ├─ UPDATE sub  │            │             │
 │                │                │              ├─ ZADD score ──────────────►│             │
 │                │                │              ├─ Pub: result ─────────────►│             │
 │                │                │              │             │             │◄─ sub listen ┤
 │                │                │              │             │             │  emit to room│
 │◄─ test results─┤                │              │             │             │             │
 │◄─ leaderboard──┤                │              │             │             │             │
```

---

### Flow 3: User Joins Room via QR Code

```
User A (host)        User B (joiner)        API Server         Redis         WS Server
      │                     │                    │                │               │
      ├─ Gets QR code        │                    │                │               │
      ├─ Shows QR ──────────►│                    │                │               │
      │              B scans QR                   │                │               │
      │                     ├─ POST /rooms/join ─►│                │               │
      │                     │                    ├─ Check capacity │               │
      │                     │                    ├─ SADD players ─►│               │
      │                     │                    ├─ Pub: joined ──►│               │
      │                     │◄─ { room_data } ───┤                │               │
      │                     ├─ Connect WS ───────────────────────────────────────►│
      │                     │                    │                │◄─ room:joined ─┤
      │◄─ "B joined" ────────────────────────────────────────────────────────────┤
```

---

## Database Design

### Entity Relationship Overview

```
users ──────────────── connections (self-join, mutual)
  │
  ├── problems ──────── test_cases
  │      │
  │      └── problem_flags
  │
  ├── problists ─────── problist_problems ──── problems
  │
  ├── rooms ──────────── room_problems ──────── problems
  │      │
  │      └── room_participants
  │
  ├── submissions ────── (links room + problem + user)
  │
  └── badges
```

### Indexing Strategy

```sql
-- High-frequency queries need indexes:

-- Find room by code (every join attempt)
CREATE INDEX idx_rooms_unique_code ON rooms(unique_code);

-- Find user by clerk_id (every auth check)
CREATE INDEX idx_users_clerk_id ON users(clerk_id);

-- Public problems list (main browse page)
CREATE INDEX idx_problems_visibility_difficulty
    ON problems(visibility, difficulty)
    WHERE visibility = 'public';

-- Submissions per room (leaderboard queries)
CREATE INDEX idx_submissions_room_id ON submissions(room_id);

-- User's submission history
CREATE INDEX idx_submissions_user_id ON submissions(user_id);

-- Connections lookup (both directions)
CREATE INDEX idx_connections_user_a ON connections(user_a_id);
CREATE INDEX idx_connections_user_b ON connections(user_b_id);

-- Leaderboard queries
CREATE INDEX idx_users_xp ON users(xp DESC);
```

### Partitioning

```sql
-- Submissions table partitioned by month (grows very large)
CREATE TABLE submissions (...)
PARTITION BY RANGE (submitted_at);

CREATE TABLE submissions_2026_07 PARTITION OF submissions
    FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');

-- Old partitions archived to cold storage after 6 months
```

---

## Caching Strategy

### What Lives Where

```
PostgreSQL (source of truth):
    users, rooms, problems, submissions, connections, badges

Redis (hot cache, fast reads):
    ├── room:{id}:state         TTL: 24h
    ├── room:{id}:leaderboard   TTL: 24h  (sorted set)
    ├── room:{id}:players       TTL: 24h  (set)
    ├── room:{id}:activity      TTL: 1h   (hash)
    ├── user:{id}:session       TTL: 1h
    ├── daily_problem           TTL: 24h
    ├── leaderboard:global      TTL: 5min (sorted set)
    ├── leaderboard:weekly      TTL: 5min
    └── rate_limit:{ip}:{ep}    TTL: 60s

Not cached (always fresh from DB):
    - Submission results (correctness data)
    - User tier (paid/free) — security sensitive
    - Problem test cases — security sensitive
```

### Cache Invalidation Rules

```
When room ends:
    → DELETE room:{id}:* from Redis
    → Write final state to PostgreSQL

When user upgrades:
    → DELETE user:{id}:session from Redis (force re-fetch tier)

When problem is edited:
    → No cache to invalidate (problems not cached individually)
    → Leaderboard cache expires naturally every 5 min
```

---

## Real-time Architecture

### Room State Machine

```
                ┌─────────┐
                │  LOBBY  │◄─── players join/leave
                └────┬────┘
                     │ host clicks start
                ┌────▼────────┐
                │  COUNTDOWN  │  5 seconds, locked (no new joins)
                └────┬────────┘
                     │ countdown ends
                ┌────▼────┐
                │  ACTIVE │◄─── submissions, progress updates
                └────┬────┘
                     │ timer ends OR host ends OR all finish
                ┌────▼─────┐
                │  ENDED   │  results calculated, saved to DB
                └────┬─────┘
                     │
                ┌────▼─────┐
                │  REPLAY  │  read-only, view solutions
                └──────────┘
```

### WebSocket Rooms (Socket.io namespaces)

```
/room/{room_id}           main room channel
/room/{room_id}/spectator read-only spectator channel
```

### Heartbeat & Reconnection

```typescript
// Client sends heartbeat every 30s
socket.emit("heartbeat", { userId, roomId });

// Server tracks last heartbeat
// If no heartbeat for 60s → mark as disconnected
// Player's progress preserved in Redis for 5min
// If reconnects within 5min → restore state
// If not → remove from room, notify others
```

---

## Code Execution Pipeline

### Execution Limits Per Language

| Language | CPU Time | Memory | Stack |
|---|---|---|---|
| Python | 3s | 256MB | Default |
| JavaScript | 2s | 256MB | Default |
| Java | 5s | 512MB | Default |
| C++ | 2s | 256MB | 64MB |
| Go | 3s | 256MB | Default |
| Rust | 3s | 256MB | Default |
| All others | 3s | 256MB | Default |

### Test Case Execution Strategy

```
For each submission:
    1. Run visible test cases first (fast feedback)
    2. If any visible fail → return early (wrong answer)
    3. If all visible pass → run hidden test cases
    4. Score = (hidden_passed / hidden_total) * base_points + speed_bonus

Speed bonus formula:
    remaining_time = time_limit - solve_time
    speed_bonus = floor(remaining_time / time_limit * 20)
    (max 20 bonus points on top of base score)
```

### Judge0 Response Handling

```typescript
const STATUS = {
  1:  "in_queue",
  2:  "processing",
  3:  "accepted",          // all tests passed
  4:  "wrong_answer",
  5:  "time_limit_exceeded",
  6:  "compilation_error",
  7:  "runtime_error_sigsegv",
  8:  "runtime_error_sigfpe",
  9:  "runtime_error_sigabrt",
  10: "runtime_error_nzec",
  11: "runtime_error_other",
  12: "runtime_error_internal",
  13: "exec_format_error",
  14: "time_limit_exceeded",
};
```

---

## API Design

### Design Principles

- RESTful resource-based URLs
- JSON request/response bodies
- JWT auth via `Authorization: Bearer <token>` header
- Consistent error format:
```json
{
  "error": {
    "code": "ROOM_FULL",
    "message": "This room has reached its player limit",
    "status": 400
  }
}
```
- Pagination via cursor (not offset):
```json
{
  "data": [...],
  "next_cursor": "eyJpZCI6MTIzfQ==",
  "has_more": true
}
```

### Versioning

- API version in URL: `/api/v1/rooms`
- Current: v1
- Breaking changes → new version, old version deprecated with 6-month notice

---

## Authentication & Authorization

### Auth Flow

```
User signs in via Clerk (Google / GitHub / Email) →
    Clerk issues JWT →
    Frontend stores JWT →
    Every API request: Authorization: Bearer <jwt> →
    API server verifies JWT with Clerk SDK →
    Clerk returns { userId, email, tier } →
    Middleware attaches to req.user →
    Controller proceeds
```

### Authorization Rules

```
Resource          | Owner | Connected | Public | Unauth
──────────────────|───────|───────────|────────|────────
Public problem    |  RW   |    R      |   R    |   R
Private problem   |  RW   |    -      |   -    |   -
Conn-only problem |  RW   |    R      |   -    |   -
Public room       |  RW   |    R      |   R    |   R (spectate)
Private room      |  RW   |    R*     |   -    |   -  (*with code)
Own profile       |  RW   |    R      |   R    |   R
Submissions code  |  R    |    -      |   -    |   -

R = read, W = write, - = denied
```

### Tier Enforcement

```typescript
function requirePaidTier(req, res, next) {
  // Always re-check from DB, never trust cached tier for billing
  const user = await db.users.findOne({ clerk_id: req.user.id });
  if (user.tier !== "paid") {
    return res.status(403).json({
      error: { code: "PAID_REQUIRED", message: "Upgrade to access this feature" }
    });
  }
  next();
}
```

---

## File & Media Storage

### What Needs Storage

| Asset | Where | Notes |
|---|---|---|
| User avatars | Supabase Storage | Max 2MB, jpg/png only |
| Problem OG images | Generated on-demand | Use `@vercel/og` |
| Room replay data | PostgreSQL (JSONB) | Compressed keystroke logs |
| QR code images | Generated client-side | Never stored, generated fresh |

### Replay Storage Format

```json
{
  "room_id": "uuid",
  "user_id": "uuid",
  "problem_id": "uuid",
  "language": "python",
  "snapshots": [
    { "t": 0, "code": "" },
    { "t": 5230, "code": "def solve" },
    { "t": 12400, "code": "def solve(n):\n    " }
  ],
  "final_code": "def solve(n):\n    return n * 2",
  "submitted_at_ms": 45230
}
```

Snapshots taken every 5 seconds during active room. Compressed with gzip before storing.

---

## Notification System

### Notification Types & Delivery

```
In-app (real-time via WebSocket):
    ├── Connection joins your room
    ├── Someone uses your problem
    ├── Room starting in 5 min (scheduled room)
    └── Your problem was flagged

Email (via Resend):
    ├── Welcome email (onboarding)
    ├── Streak at risk (daily, only if opted in)
    ├── Weekly digest (top problems, your rank change)
    └── Payment receipts / failures

Push (via OneSignal, opt-in):
    ├── Daily problem available
    ├── Connection challenges you to a room
    └── Streak reminder
```

### Notification Fan-out Architecture

```
Event occurs (e.g., room created by connection)
    │
    ▼
BullMQ: notification job added
    │
    ▼
Notification Worker:
    ├── Fetch user preferences (do they want this type?)
    ├── For each opted-in delivery channel:
    │       ├── In-app: emit via Socket.io
    │       ├── Email: POST to Resend API
    │       └── Push: POST to OneSignal API
    └── Log to notifications table
```

---

## Search System

### Search Scope

- Problems (by title, tag, language, difficulty, author)
- Problists (by title, topic)
- Users (by username, only public profiles)
- Public rooms (open lobbies to join)

### Implementation (MVP)

Use **PostgreSQL full-text search** — no separate search service needed at MVP scale.

```sql
-- Add search vector column to problems
ALTER TABLE problems ADD COLUMN search_vector tsvector;

-- Update on insert/update
CREATE OR REPLACE FUNCTION update_problem_search()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', NEW.title), 'A') ||
        setweight(to_tsvector('english', NEW.description), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER problem_search_update
    BEFORE INSERT OR UPDATE ON problems
    FOR EACH ROW EXECUTE FUNCTION update_problem_search();

-- Search query
SELECT * FROM problems
WHERE search_vector @@ plainto_tsquery('english', 'binary tree')
  AND visibility = 'public'
ORDER BY ts_rank(search_vector, plainto_tsquery('english', 'binary tree')) DESC
LIMIT 20;
```

### Scaling to Algolia/Typesense (later)

When search becomes slow (>100ms at scale), migrate to **Typesense** (self-hosted, free) or **Algolia** (managed, paid). Sync via webhook on problem create/update.

---

## Scalability Design

### Current Architecture Limits

| Component | Current Limit | Bottleneck |
|---|---|---|
| API Server | ~1,000 req/s | Single Railway instance |
| WS Server | ~5,000 connections | Single instance |
| PostgreSQL | ~500 queries/s | Supabase free tier |
| Redis | ~10,000 ops/s | Upstash free tier |
| Judge0 | ~20 concurrent executions | Single droplet |

### Scaling Steps

```
Step 1 (0 → 5,000 users): No changes needed

Step 2 (5,000 → 50,000 users):
    ├── API Server: scale horizontally (2-3 Railway instances)
    ├── WS Server: add Redis adapter for multi-instance sync
    ├── PostgreSQL: upgrade Supabase Pro + read replica
    ├── Judge0: add 2nd droplet, load balance submissions
    └── Redis: upgrade Upstash paid tier

Step 3 (50,000 → 500,000 users):
    ├── Move to AWS/GCP
    ├── API Server: auto-scaling EC2 behind ALB
    ├── WS Server: ECS with Redis cluster adapter
    ├── PostgreSQL: RDS with 2 read replicas
    ├── Judge0: pool of 5-10 containers (ECS)
    └── CDN: Cloudflare for static assets + edge caching

Step 4 (500,000+ users):
    ├── Microservices: split submission service out
    ├── Judge0: Kubernetes autoscaling pool
    ├── Event streaming: Kafka for submission events
    └── Search: dedicated Typesense cluster
```

---

## Fault Tolerance & Reliability

### What Happens When Things Fail

```
Judge0 goes down:
    → BullMQ jobs retry 3x with exponential backoff
    → After 3 fails: job moved to dead-letter queue
    → User notified: "Code execution temporarily unavailable"
    → Status page updated automatically
    → No room state lost (Redis + DB intact)

API Server crashes:
    → Railway auto-restarts in <30s
    → Requests during downtime get 502 from Cloudflare
    → WebSocket clients auto-reconnect with backoff
    → Room state preserved in Redis (no data loss)

Redis goes down:
    → Rate limiting temporarily disabled (fail open)
    → Room state reads fall back to PostgreSQL (slower)
    → Alert fires immediately
    → Upstash has 99.99% SLA

Database goes down:
    → API returns 503 for write operations
    → Cached reads still work for ~5min (Redis TTL)
    → Supabase has auto-failover to replica

WebSocket server crashes:
    → All clients reconnect automatically
    → Room state re-hydrated from Redis on reconnect
    → No data loss (Redis is source of truth for live state)
```

### Data Durability Guarantees

```
Submissions:
    ├── Saved to DB before BullMQ job completes
    ├── Job retries if DB write fails
    └── Never lost

Room results:
    ├── Written to DB when room ends
    ├── Redis state preserved for 24h as backup
    └── Idempotent end-room function (safe to retry)

User XP / badges:
    ├── Updated in DB transaction
    ├── Rollback on failure
    └── BullMQ retry ensures eventual consistency
```

---

## Security Architecture

### Defense in Depth Layers

```
Layer 1 — Network:
    Cloudflare WAF blocks known attack patterns
    DDoS protection at edge
    HTTPS everywhere (TLS 1.3)

Layer 2 — Application Perimeter:
    Rate limiting (Upstash) per IP and per user
    CORS: only frontend domain allowed
    Security headers (CSP, X-Frame-Options, etc.)

Layer 3 — Authentication:
    Clerk JWT verification on every request
    Short JWT expiry (1 hour) + refresh tokens
    OAuth only for social login (no password storage)

Layer 4 — Authorization:
    Every endpoint checks user owns resource
    Tier checked from DB for paid features
    Room capacity enforced server-side

Layer 5 — Input:
    Zod schema validation on all inputs
    DOMPurify sanitization on all HTML
    Parameterized queries (no raw SQL)
    Max payload size: 100KB

Layer 6 — Code Execution:
    Judge0 on isolated server
    Docker container per execution
    No network, no filesystem, CPU/RAM limits
    Firewall: only API server IP accepted

Layer 7 — Data:
    No raw passwords stored (Clerk handles)
    Problem test cases never sent to client
    Submission code only visible to owner
    Audit log for all admin actions
```

### Threat Model

| Threat | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Malicious code execution | High | Critical | Judge0 isolation |
| Room code brute force | Medium | Low | Rate limit + lockout |
| Account takeover | Low | High | Clerk handles (MFA support) |
| Problem scraping | High | Low | Rate limiting |
| Cheating (paste/bot) | High | Medium | Paste detection, time analysis |
| DDoS | Medium | High | Cloudflare |
| SQL injection | Low | Critical | ORM + parameterized queries |
| XSS via problem desc | Medium | High | DOMPurify |
| Spam problems | High | Medium | Trust levels + community flags |

---

## Monitoring Architecture

### Observability Stack

```
Metrics:     PostHog (product) + Railway built-in (infra)
Errors:      Sentry (frontend + backend)
Logs:        Railway log drain → Logtail (free tier)
Uptime:      BetterStack (status.yourapp.com)
Alerting:    BetterStack → PagerDuty (or just email at small scale)
```

### Key Alerts to Set Up

```
Critical (wake you up):
    ├── API error rate > 5% for 2 min
    ├── Judge0 health check failing
    ├── Database connection failures
    └── Payment webhook failures

Warning (check next morning):
    ├── API p95 latency > 1s
    ├── Redis memory > 80%
    ├── BullMQ dead-letter queue > 10 jobs
    └── Suspicious submission patterns (impossible times)

Info (weekly digest):
    ├── New user signups
    ├── Rooms created
    ├── Free → paid conversions
    └── Most popular problems
```

### Structured Logging Format

```json
{
  "timestamp": "2026-07-24T10:30:00Z",
  "level": "info",
  "service": "api",
  "event": "submission.completed",
  "user_id": "uuid",
  "room_id": "uuid",
  "problem_id": "uuid",
  "language": "python",
  "status": "accepted",
  "duration_ms": 1243,
  "judge0_token": "abc123"
}
```

---

## Capacity Estimation

### Assumptions (at 10,000 DAU)

```
Users:
    10,000 DAU
    ~500 concurrent users peak
    ~50 concurrent active rooms

Storage per month:
    Submissions:    ~500K submissions/month
                    avg 2KB code = ~1GB/month
    Room replays:   ~10K rooms/month
                    avg 5KB replay = ~50MB/month
    Problems:       ~1,000 new problems/month
                    avg 1KB = ~1MB/month
    Total new:      ~1.1GB/month → Supabase free (500MB) exceeded
                    → Upgrade Supabase Pro at this scale

Network per day:
    API requests:   ~100 req/user/day = 1M req/day = ~12 req/s avg
    WebSocket msgs: ~500 concurrent × 10 msgs/min = 5,000 msgs/min
    Judge0 calls:   ~500K submissions/day = ~6 submissions/s peak

Judge0 capacity:
    Avg execution: 1.5s
    Single droplet: ~20 concurrent
    At 6 submissions/s: need ~9 concurrent slots
    Single droplet handles 10K DAU comfortably
    Add 2nd droplet at ~25K DAU
```

---

## Trade-off Decisions

### 1. Node.js vs Go for Backend

| | Node.js | Go |
|---|---|---|
| Dev speed | Fast | Slower |
| Performance | Good | Excellent |
| Ecosystem | Huge | Smaller |
| Team familiarity | Usually higher | Lower |
| **Decision** | **Start with Node.js** | Migrate hot paths later |

### 2. Polling vs WebSocket for Submission Results

| | HTTP Polling | WebSocket |
|---|---|---|
| Simplicity | Simple | More complex |
| Latency | 500ms-2s | <100ms |
| Server load | Higher (many requests) | Lower (persistent conn) |
| **Decision** | **WebSocket** | Real-time feel is core UX |

### 3. Self-hosted Judge0 vs Piston API (managed)

| | Judge0 Self-hosted | Piston API |
|---|---|---|
| Cost | ~$12/mo fixed | Pay per execution |
| Control | Full | Limited |
| Security | You configure | Trust provider |
| Maintenance | You manage | Zero |
| **Decision** | **Self-hosted** | Security control is critical |

### 4. PostgreSQL Full-text vs Algolia for Search

| | PostgreSQL FTS | Algolia |
|---|---|---|
| Cost | Free | Paid ($50+/mo) |
| Setup | Already have PG | External service |
| Quality | Good | Excellent (typo tolerance etc.) |
| Scale limit | ~1M rows fine | Unlimited |
| **Decision** | **PG FTS at MVP** | Migrate to Typesense at scale |

### 5. Supabase vs Self-hosted PostgreSQL

| | Supabase | Self-hosted |
|---|---|---|
| Setup time | Minutes | Hours |
| Cost (small) | Free | $10-20/mo |
| Features | RLS, Auth, Storage built-in | Manual |
| Control | Limited | Full |
| **Decision** | **Supabase** | Self-host only at large scale |

---

*Document version: 1.0 — System Design for CodeBattle*
*Last updated: 2026-07-24*
