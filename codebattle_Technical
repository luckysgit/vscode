# CodeBattle — Technical Implementation Guide

> How to build, secure, deploy, and run CodeBattle in production.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Tech Stack](#tech-stack)
3. [Frontend](#frontend)
4. [Backend Services](#backend-services)
5. [Database Schema](#database-schema)
6. [Real-time System (WebSockets)](#real-time-system-websockets)
7. [Code Execution Engine](#code-execution-engine)
8. [Authentication](#authentication)
9. [Payments](#payments)
10. [Security](#security)
11. [Infrastructure & Hosting](#infrastructure--hosting)
12. [Automation & Background Jobs](#automation--background-jobs)
13. [Monitoring & Observability](#monitoring--observability)
14. [Development Phases](#development-phases)
15. [Environment Variables](#environment-variables)

---

## Architecture Overview

```
                        ┌─────────────────┐
                        │   Cloudflare     │  WAF + DDoS + CDN
                        └────────┬────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
        ┌─────▼──────┐   ┌───────▼───────┐  ┌──────▼──────┐
        │  Frontend   │   │  API Server   │  │  WS Server  │
        │  (Next.js)  │   │  (Node.js)    │  │ (Socket.io) │
        │  Vercel     │   │  Railway      │  │  Railway    │
        └─────┬──────┘   └───────┬───────┘  └──────┬──────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
        ┌─────▼──────┐   ┌───────▼───────┐  ┌──────▼──────┐
        │ PostgreSQL  │   │    Redis      │  │   Judge0    │
        │ (Supabase)  │   │  (Upstash)    │  │ (Isolated   │
        │  main DB    │   │  room state   │  │  Droplet)   │
        └────────────┘   └───────────────┘  └─────────────┘
```

---

## Tech Stack

### Complete Stack Table

| Layer | Technology | Why |
|---|---|---|
| Frontend | Next.js 14 + TypeScript | SSR, API routes, great ecosystem |
| Styling | Tailwind CSS + shadcn/ui | Fast, consistent UI |
| Animations | Framer Motion | Smooth UX transitions |
| Code Editor | Monaco Editor | Same as VS Code, all languages |
| State Management | Zustand | Simple, no boilerplate |
| Real-time Client | Socket.io client | Matches server |
| QR Generate | qrcode.react | Easy QR generation |
| QR Scan | html5-qrcode | Camera-based QR scan |
| Backend | Node.js + Express | Fast to build, huge ecosystem |
| Real-time Server | Socket.io | Industry standard WebSockets |
| Job Queue | BullMQ | Redis-backed job queue |
| Database | PostgreSQL (Supabase) | Relational, reliable |
| Cache / State | Redis (Upstash) | Fast ephemeral data |
| Code Runner | Judge0 (self-hosted) | Sandboxed multi-language execution |
| Auth | Clerk | Production-ready, OAuth included |
| Payments | Stripe | Industry standard subscriptions |
| Email | Resend | Developer-friendly, free tier |
| Push Notifications | OneSignal | Free tier, cross-platform |
| Analytics | PostHog | Open source, self-hostable |
| Error Tracking | Sentry | Free tier, full stack |
| WAF / CDN | Cloudflare | Free WAF, DDoS protection |
| Rate Limiting | Upstash Redis | Per-IP rate limiting |
| Deploy (frontend) | Vercel | Zero config Next.js |
| Deploy (backend) | Railway | Simple Node.js hosting |
| Code Runner Host | DigitalOcean Droplet | Isolated from main servers |

---

## Frontend

### Project Structure

```
/app
    /page.tsx                  → landing page
    /dashboard/page.tsx        → user dashboard
    /room/[code]/page.tsx      → live room
    /problems/page.tsx         → problem discovery
    /problems/[id]/page.tsx    → problem detail + solve
    /problists/page.tsx        → problist discovery
    /profile/[username]/page.tsx → public profile
    /onboarding/page.tsx       → new user setup

/components
    /editor/                   → Monaco editor wrapper
    /room/                     → room lobby, live, results
    /problems/                 → problem card, form, viewer
    /leaderboard/              → live + final rankings
    /qr/                       → QR generate + scan

/lib
    /socket.ts                 → Socket.io client setup
    /api.ts                    → API call helpers
    /auth.ts                   → Clerk helpers

/store
    /roomStore.ts              → Zustand room state
    /userStore.ts              → Zustand user state
```

### Key Frontend Rules

- All code execution results come through WebSocket, not HTTP polling
- Monaco editor must be loaded client-side only (`dynamic(() => import(...), { ssr: false })`)
- Room state lives in Zustand + synced via Socket.io
- Never send raw code to your own API — always route through submission endpoint which forwards to Judge0

---

## Backend Services

### API Server Endpoints

```
POST   /auth/webhook              → Clerk webhook (user created/updated)

GET    /rooms/:code               → get room details
POST   /rooms                     → create room
POST   /rooms/:code/join          → join room
POST   /rooms/:code/start         → host starts room
POST   /rooms/:code/end           → host ends room early
GET    /rooms/:code/results       → final leaderboard

POST   /submissions               → submit code for judging
GET    /submissions/:id           → get submission result

GET    /problems                  → list public problems (paginated)
POST   /problems                  → publish new problem
GET    /problems/:id              → get problem details
PUT    /problems/:id              → edit own problem
POST   /problems/:id/flag         → flag a problem
POST   /problems/:id/fork         → fork a problem

GET    /problists                 → list own + public problists
POST   /problists                 → create problist
PUT    /problists/:id             → update problist
POST   /problists/:id/problems    → add problem to problist

GET    /connections               → list own connections
POST   /connections/request       → send connection request via code
POST   /connections/:id/accept    → accept request
DELETE /connections/:id           → remove connection

GET    /users/:username           → public profile
GET    /users/me                  → own profile + stats
PUT    /users/me                  → update profile

GET    /leaderboard/global        → global rankings
GET    /leaderboard/:language     → per-language rankings
GET    /leaderboard/weekly        → this week's rankings

POST   /payments/webhook          → Stripe webhook
POST   /payments/subscribe        → create Stripe checkout session
POST   /payments/cancel           → cancel subscription
```

### Middleware Stack (Every Request)

```
Request →
    Cloudflare WAF →
    Rate Limiter (Upstash) →
    Auth check (Clerk JWT) →
    Input validation (Zod) →
    Controller →
    Response
```

---

## Database Schema

### Full PostgreSQL Schema

```sql
-- Users
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clerk_id      TEXT UNIQUE NOT NULL,
    username      TEXT UNIQUE NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    avatar_url    TEXT,
    tier          TEXT DEFAULT 'free' CHECK (tier IN ('free', 'paid')),
    xp            INTEGER DEFAULT 0,
    rank          TEXT DEFAULT 'bronze',
    streak        INTEGER DEFAULT 0,
    last_solve_at TIMESTAMP,
    stripe_customer_id TEXT,
    created_at    TIMESTAMP DEFAULT NOW()
);

-- Connections (mutual, no direction)
CREATE TABLE connections (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_a_id   UUID REFERENCES users(id) ON DELETE CASCADE,
    user_b_id   UUID REFERENCES users(id) ON DELETE CASCADE,
    connected_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_a_id, user_b_id),
    CHECK (user_a_id < user_b_id) -- enforce no duplicates
);

-- Problems
CREATE TABLE problems (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id    UUID REFERENCES users(id) ON DELETE SET NULL,
    forked_from  UUID REFERENCES problems(id) ON DELETE SET NULL,
    version      INTEGER DEFAULT 1,
    title        TEXT NOT NULL,
    description  TEXT NOT NULL,
    difficulty   TEXT CHECK (difficulty IN ('easy', 'medium', 'hard')),
    visibility   TEXT DEFAULT 'public' CHECK (visibility IN ('public', 'private', 'connections')),
    unique_code  TEXT UNIQUE,
    language_tags TEXT[],
    solve_count  INTEGER DEFAULT 0,
    avg_solve_ms INTEGER,
    is_flagged   BOOLEAN DEFAULT false,
    is_approved  BOOLEAN DEFAULT false,
    created_at   TIMESTAMP DEFAULT NOW()
);

-- Test Cases
CREATE TABLE test_cases (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id  UUID REFERENCES problems(id) ON DELETE CASCADE,
    input       TEXT NOT NULL,
    expected    TEXT NOT NULL,
    is_hidden   BOOLEAN DEFAULT false,
    order_index INTEGER
);

-- Problists
CREATE TABLE problists (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id    UUID REFERENCES users(id) ON DELETE CASCADE,
    title       TEXT NOT NULL,
    description TEXT,
    visibility  TEXT DEFAULT 'private' CHECK (visibility IN ('public', 'private', 'connections')),
    unique_code TEXT UNIQUE,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Problist → Problems (join table)
CREATE TABLE problist_problems (
    problist_id UUID REFERENCES problists(id) ON DELETE CASCADE,
    problem_id  UUID REFERENCES problems(id) ON DELETE CASCADE,
    order_index INTEGER NOT NULL,
    PRIMARY KEY (problist_id, problem_id)
);

-- Rooms
CREATE TABLE rooms (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    host_id      UUID REFERENCES users(id) ON DELETE SET NULL,
    unique_code  TEXT UNIQUE NOT NULL,
    status       TEXT DEFAULT 'lobby' CHECK (status IN ('lobby', 'countdown', 'active', 'ended')),
    tier         TEXT DEFAULT 'free' CHECK (tier IN ('free', 'paid')),
    max_players  INTEGER DEFAULT 100,
    timer_type   TEXT DEFAULT 'countdown' CHECK (timer_type IN ('countdown', 'countup')),
    time_limit_s INTEGER DEFAULT 1800,
    problem_order TEXT DEFAULT 'sequential' CHECK (problem_order IN ('sequential', 'freeforall')),
    is_public    BOOLEAN DEFAULT false,
    scheduled_at TIMESTAMP,
    started_at   TIMESTAMP,
    ended_at     TIMESTAMP,
    created_at   TIMESTAMP DEFAULT NOW()
);

-- Room → Problems
CREATE TABLE room_problems (
    room_id     UUID REFERENCES rooms(id) ON DELETE CASCADE,
    problem_id  UUID REFERENCES problems(id),
    order_index INTEGER NOT NULL,
    PRIMARY KEY (room_id, problem_id)
);

-- Room Participants
CREATE TABLE room_participants (
    room_id     UUID REFERENCES rooms(id) ON DELETE CASCADE,
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    alias       TEXT NOT NULL,
    is_spectator BOOLEAN DEFAULT false,
    joined_at   TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (room_id, user_id)
);

-- Submissions
CREATE TABLE submissions (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id      UUID REFERENCES rooms(id) ON DELETE SET NULL,
    user_id      UUID REFERENCES users(id) ON DELETE SET NULL,
    problem_id   UUID REFERENCES problems(id) ON DELETE SET NULL,
    language     TEXT NOT NULL,
    code         TEXT NOT NULL,
    status       TEXT CHECK (status IN ('pending', 'accepted', 'wrong_answer', 'time_limit', 'runtime_error', 'compile_error')),
    tests_passed INTEGER DEFAULT 0,
    tests_total  INTEGER DEFAULT 0,
    score        INTEGER DEFAULT 0,
    time_taken_ms INTEGER,
    judge0_token TEXT,
    submitted_at TIMESTAMP DEFAULT NOW()
);

-- Badges
CREATE TABLE badges (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    badge_type  TEXT NOT NULL,
    awarded_at  TIMESTAMP DEFAULT NOW()
);

-- Problem Flags
CREATE TABLE problem_flags (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_id  UUID REFERENCES problems(id) ON DELETE CASCADE,
    reporter_id UUID REFERENCES users(id) ON DELETE SET NULL,
    reason      TEXT,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Audit Logs
CREATE TABLE audit_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id    UUID REFERENCES users(id) ON DELETE SET NULL,
    action      TEXT NOT NULL,
    target_type TEXT,
    target_id   UUID,
    metadata    JSONB,
    created_at  TIMESTAMP DEFAULT NOW()
);
```

---

## Real-time System (WebSockets)

### Socket.io Event Map

```
Client → Server events:
    room:join          { room_code, user_id, alias }
    room:leave         { room_code }
    room:start         { room_code }        ← host only
    submission:submit  { room_id, problem_id, language, code }
    room:reaction      { room_code, emoji }

Server → Client events:
    room:player_joined    { user_id, alias, player_count }
    room:player_left      { user_id }
    room:countdown        { seconds_left }
    room:started          { problems, time_limit }
    room:activity_pulse   { user_id }       ← "someone is typing"
    room:progress_update  { user_id, tests_passed, tests_total }
    room:player_finished  { user_id, rank, score, time_ms }
    room:ended            { leaderboard[] }
    submission:result     { status, tests_passed, score }
    room:reaction         { user_id, emoji }
    error                 { code, message }
```

### Redis Room State Structure

```
room:{room_id}:state        → { status, started_at, time_limit }
room:{room_id}:players      → Set of user_ids
room:{room_id}:leaderboard  → Sorted set (score as rank)
room:{room_id}:progress     → Hash { user_id: tests_passed }
room:{room_id}:activity     → Hash { user_id: last_keystroke_ts }
rate_limit:{ip}:{endpoint}  → Integer (request count)
session:{user_id}           → { clerk_jwt_cache }
```

---

## Code Execution Engine

### Judge0 Setup (Isolated Server)

**Never run on your main application server.**

```
Deploy Judge0 on separate DigitalOcean Droplet:
    - 2 vCPU, 4GB RAM minimum
    - Ubuntu 22.04 LTS
    - Docker installed
    - No public ports except 2358 (Judge0 API)
    - Firewall: only accept from your API server IP
```

### Judge0 Installation

```bash
git clone https://github.com/judge0/judge0.git
cd judge0
cp judge0.conf.example judge0.conf
# Edit judge0.conf:
#   CPU_TIME_LIMIT=2
#   MEMORY_LIMIT=262144 (256MB)
#   ENABLE_NETWORK=false
docker-compose up -d
```

### Submission Flow

```
User submits code
    │
    ▼
Your API Server
    ├── Validates: is room active? is user in room? is language allowed?
    ├── Sanitizes: strip null bytes, check max length (50KB)
    ├── Queues job in BullMQ (async, don't wait)
    │
    ▼
BullMQ Worker
    ├── Calls Judge0 API:
    │       POST /submissions
    │       { source_code, language_id, stdin, expected_output,
    │         cpu_time_limit: 2, memory_limit: 262144 }
    ├── Polls for result (or uses Judge0 callback)
    ├── Calculates score
    ├── Saves to submissions table
    └── Emits submission:result via Socket.io to user
        + room:progress_update to all room members
```

### Supported Languages (Judge0 IDs)

| Language | Judge0 ID |
|---|---|
| Python 3 | 71 |
| JavaScript (Node.js) | 63 |
| TypeScript | 74 |
| Java | 62 |
| C++ | 54 |
| C# | 51 |
| Go | 60 |
| Rust | 73 |
| PHP | 68 |
| Swift | 83 |
| Kotlin | 78 |

---

## Authentication

### Clerk Setup

```typescript
// middleware.ts (Next.js)
import { authMiddleware } from "@clerk/nextjs";

export default authMiddleware({
  publicRoutes: ["/", "/problems", "/leaderboard", "/profile/:username"],
});
```

### JWT Verification (Backend)

```typescript
import { clerkClient } from "@clerk/clerk-sdk-node";

async function verifyToken(req, res, next) {
  const token = req.headers.authorization?.split(" ")[1];
  if (!token) return res.status(401).json({ error: "Unauthorized" });

  try {
    const payload = await clerkClient.verifyToken(token);
    req.userId = payload.sub; // clerk user ID
    next();
  } catch {
    return res.status(401).json({ error: "Invalid token" });
  }
}
```

### Clerk Webhook → Sync to DB

```typescript
// When user creates account in Clerk → create row in your users table
app.post("/auth/webhook", async (req, res) => {
  const { type, data } = req.body;
  if (type === "user.created") {
    await db.users.create({
      clerk_id: data.id,
      email: data.email_addresses[0].email_address,
      username: data.username || generateUsername(),
    });
  }
});
```

---

## Payments

### Stripe Subscription Flow

```
User clicks "Upgrade" →
    POST /payments/subscribe →
    Create Stripe Checkout Session →
    Redirect to Stripe hosted page →
    User pays →
    Stripe sends webhook: payment_intent.succeeded →
    Your server: UPDATE users SET tier = 'paid' WHERE stripe_customer_id = X
```

### Stripe Webhook Handler

```typescript
app.post("/payments/webhook", express.raw({ type: "application/json" }), async (req, res) => {
  const sig = req.headers["stripe-signature"];
  let event;

  try {
    event = stripe.webhooks.constructEvent(req.body, sig, process.env.STRIPE_WEBHOOK_SECRET);
  } catch (err) {
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  switch (event.type) {
    case "customer.subscription.created":
    case "customer.subscription.updated":
      await upgradeUser(event.data.object.customer);
      break;
    case "customer.subscription.deleted":
      await downgradeUser(event.data.object.customer);
      break;
    case "invoice.payment_failed":
      await notifyPaymentFailed(event.data.object.customer);
      break;
  }

  res.json({ received: true });
});
```

---

## Security

### 1. Code Execution Security

```
Every submission:
    ├── Max code size: 50KB (reject larger)
    ├── Runs in isolated Docker container (Judge0)
    ├── CPU time limit: 2 seconds
    ├── Memory limit: 256MB
    ├── No network access (ENABLE_NETWORK=false)
    ├── No file system write access
    ├── Container destroyed after execution
    └── Judge0 server: firewall blocks all IPs except your API server
```

### 2. Rate Limiting (Upstash Redis)

```typescript
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, "10 s"),
});

// Per endpoint limits:
//   /submissions     → 5 per 10s per user
//   /rooms (create)  → 3 per minute per user
//   /auth/*          → 10 per minute per IP
//   /rooms/join      → 10 attempts per minute per IP
//   Room code entry  → 5 attempts per minute per IP (lockout after)
```

### 3. Input Validation (Zod)

```typescript
import { z } from "zod";

const CreateRoomSchema = z.object({
  max_players: z.number().min(2).max(100),
  timer_type: z.enum(["countdown", "countup"]),
  time_limit_s: z.number().min(60).max(7200),
  problem_ids: z.array(z.string().uuid()).min(1).max(20),
  is_public: z.boolean(),
});

// Always validate at API boundary, never trust client input
```

### 4. XSS Prevention

```typescript
import DOMPurify from "isomorphic-dompurify";

// Before saving any user-generated HTML (problem descriptions):
const cleanDescription = DOMPurify.sanitize(rawInput, {
  ALLOWED_TAGS: ["p", "code", "pre", "ul", "ol", "li", "strong", "em"],
  ALLOWED_ATTR: [],
});
```

### 5. SQL Injection Prevention

- Use Supabase client or Drizzle ORM — never raw SQL string interpolation
- Parameterized queries only

```typescript
// NEVER do this:
db.query(`SELECT * FROM users WHERE username = '${username}'`);

// Always do this:
db.query("SELECT * FROM users WHERE username = $1", [username]);
```

### 6. Anti-Cheat Measures

```typescript
// Track paste events in Monaco editor
editor.onDidPaste((e) => {
  const pastedLength = e.range.endColumn - e.range.startColumn;
  if (pastedLength > 200) {
    logSuspiciousEvent(userId, "large_paste", { length: pastedLength });
  }
});

// Flag statistically impossible solve times
function isSuspiciousSolveTime(problemDifficulty, solveTimeMs) {
  const minimums = { easy: 15000, medium: 30000, hard: 60000 };
  return solveTimeMs < minimums[problemDifficulty];
}
```

### 7. Security Headers (Next.js)

```typescript
// next.config.js
const securityHeaders = [
  { key: "X-Frame-Options", value: "DENY" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(self), microphone=()" },
  {
    key: "Content-Security-Policy",
    value: "default-src 'self'; script-src 'self' 'unsafe-eval'; ...",
  },
];
```

### 8. CORS Configuration

```typescript
app.use(cors({
  origin: process.env.FRONTEND_URL, // only your frontend domain
  credentials: true,
  methods: ["GET", "POST", "PUT", "DELETE"],
}));
```

### 9. Environment Secrets

```
Never commit secrets. Use environment variables:
    CLERK_SECRET_KEY
    STRIPE_SECRET_KEY
    STRIPE_WEBHOOK_SECRET
    JUDGE0_API_KEY
    DATABASE_URL
    REDIS_URL
    RESEND_API_KEY

Store in:
    - Local: .env.local (gitignored)
    - Production: Railway / Vercel environment variables dashboard
```

---

## Infrastructure & Hosting

### Services Map

| Service | Provider | Tier | Monthly Cost |
|---|---|---|---|
| Frontend | Vercel | Free (Hobby) | $0 |
| API + WS Server | Railway | Starter | ~$10 |
| PostgreSQL | Supabase | Free | $0 |
| Redis | Upstash | Free | $0 |
| Judge0 Runner | DigitalOcean | Basic Droplet | ~$12 |
| Auth | Clerk | Free (10k MAU) | $0 |
| Email | Resend | Free (3k/mo) | $0 |
| CDN + WAF | Cloudflare | Free | $0 |
| Error Tracking | Sentry | Free (5k errors) | $0 |
| Analytics | PostHog | Free (1M events) | $0 |
| **Total MVP** | | | **~$22/month** |

### Cloudflare Setup

```
Your domain → Cloudflare →
    ├── yourapp.com         → Vercel (frontend)
    ├── api.yourapp.com     → Railway (API)
    ├── ws.yourapp.com      → Railway (WebSocket)
    └── judge0.yourapp.com  → DigitalOcean (internal only, blocked from public)
```

### DigitalOcean Judge0 Droplet Security

```bash
# Firewall: only allow your Railway API server IP
ufw default deny incoming
ufw allow from YOUR_RAILWAY_IP to any port 2358
ufw allow 22  # SSH for you only
ufw enable
```

### Scaling Path

```
0 → 1,000 users:   Current setup (~$22/mo)
1,000 → 10,000:    Upgrade Supabase Pro ($25) + Railway Pro ($20)
10,000 → 100,000:  Add read replicas, Redis cluster, multiple Judge0 instances
100,000+:          Move to AWS/GCP, Kubernetes, Judge0 auto-scaling pool
```

---

## Automation & Background Jobs

### BullMQ Queue Setup

```typescript
import { Queue, Worker } from "bullmq";
import { Redis } from "ioredis";

const connection = new Redis(process.env.REDIS_URL);

// Queues
export const submissionQueue = new Queue("submissions", { connection });
export const notificationQueue = new Queue("notifications", { connection });
export const cleanupQueue = new Queue("cleanup", { connection });
export const scheduledQueue = new Queue("scheduled", { connection });
```

### Submission Worker

```typescript
new Worker("submissions", async (job) => {
  const { submissionId, code, language, problemId, roomId, userId } = job.data;

  // Call Judge0
  const result = await judge0.submit({ code, language, testCases });

  // Save to DB
  await db.submissions.update({ id: submissionId, ...result });

  // Update room leaderboard in Redis
  await redis.zadd(`room:${roomId}:leaderboard`, result.score, userId);

  // Broadcast to room via Socket.io
  io.to(roomId).emit("room:progress_update", {
    userId, tests_passed: result.testsPassed
  });
}, { connection });
```

### Scheduled Cron Jobs

```typescript
// Daily at midnight UTC
scheduledQueue.add("daily-reset", {}, {
  repeat: { pattern: "0 0 * * *" }
});

// Weekly Monday 9am UTC
scheduledQueue.add("weekly-room", {}, {
  repeat: { pattern: "0 9 * * 1" }
});

// Hourly cleanup
scheduledQueue.add("cleanup", {}, {
  repeat: { pattern: "0 * * * *" }
});
```

### Scheduled Worker Tasks

```typescript
new Worker("scheduled", async (job) => {
  switch (job.name) {
    case "daily-reset":
      await pickDailyProblem();
      await checkAndUpdateStreaks();
      await sendStreakReminderNotifications();
      break;

    case "weekly-room":
      await createWeeklyThemeRoom();
      await generateWeeklyLeaderboardDigest();
      break;

    case "cleanup":
      await deleteStaleRooms();      // stuck in lobby 2+ hours
      await clearExpiredRedisKeys();
      await removeUnverifiedAccounts(); // older than 7 days
      break;
  }
}, { connection });
```

---

## Monitoring & Observability

### What to Monitor

```
Application health:
    ├── API response times (p50, p95, p99)
    ├── WebSocket connection count
    ├── Error rate per endpoint
    └── Judge0 execution queue depth

Business metrics (PostHog):
    ├── Daily / weekly / monthly active users
    ├── Rooms created per day
    ├── Submissions per day
    ├── Free → paid conversion rate
    ├── Most used languages
    └── Drop-off points in room flow

Infrastructure:
    ├── Judge0 CPU / memory usage
    ├── Redis memory usage
    ├── PostgreSQL query times
    └── Cloudflare blocked requests
```

### Sentry Error Tracking

```typescript
import * as Sentry from "@sentry/node";

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1, // 10% of requests
});

// Capture unhandled errors
app.use(Sentry.Handlers.errorHandler());
```

### Status Page

- Use **BetterStack** (free tier) for uptime monitoring
- Public status page at `status.yourapp.com`
- Monitors: API health, WebSocket, Judge0, Database
- Auto-notify users if Judge0 is down (code execution unavailable)

---

## Development Phases

### Phase 1 — MVP (Weeks 1-8)

```
Goal: People can create a room, join it, and compete on one problem.

Week 1-2: Foundation
    ├── Next.js + Tailwind setup
    ├── Clerk auth integration
    ├── Supabase DB setup + migrations
    └── Basic user profile

Week 3-4: Core Room
    ├── Create room + generate unique code
    ├── Join room via code
    ├── Room lobby UI
    └── WebSocket setup (Socket.io)

Week 5-6: Code Execution
    ├── Deploy Judge0 on DigitalOcean
    ├── Monaco editor integration
    ├── Submission pipeline
    └── Test case result display

Week 7-8: Complete Room Flow
    ├── Countdown + start + end
    ├── Live leaderboard
    ├── Results page
    └── Basic scoring
```

### Phase 2 — Core Features (Weeks 9-16)

```
Week 9-10: Problems
    ├── Problem publishing (public/private)
    ├── QR code generation + scanning
    ├── Problem search

Week 11-12: Connections + Problists
    ├── Connection system (QR/code based)
    ├── Problist CRUD
    └── Add problems to room from problist

Week 13-14: Progression
    ├── XP + ranks
    ├── Streaks + daily problem
    ├── Badges system

Week 15-16: Polish
    ├── Onboarding flow
    ├── Public profile page
    ├── Mobile responsive
    └── Performance optimization
```

### Phase 3 — Growth (Weeks 17-24)

```
Week 17-18: Payments
    ├── Stripe integration
    ├── Free vs paid tier enforcement
    └── Upgrade flow

Week 19-20: Advanced Features
    ├── Replays
    ├── AI hints
    ├── Weak spot tracker

Week 21-22: B2B
    ├── Interview mode
    ├── Org accounts

Week 23-24: Scale
    ├── Tournament bracket
    ├── Leaderboards
    └── Analytics dashboard
```

---

## Environment Variables

### Frontend (.env.local)

```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_API_URL=https://api.yourapp.com
NEXT_PUBLIC_WS_URL=wss://ws.yourapp.com
NEXT_PUBLIC_POSTHOG_KEY=phc_...
SENTRY_DSN=https://...
```

### Backend (.env)

```bash
NODE_ENV=production
PORT=3001

# Auth
CLERK_SECRET_KEY=sk_test_...
CLERK_WEBHOOK_SECRET=whsec_...

# Database
DATABASE_URL=postgresql://...

# Redis
REDIS_URL=redis://...

# Judge0
JUDGE0_URL=http://your-droplet-ip:2358
JUDGE0_API_KEY=your_key

# Payments
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PAID_PRICE_ID=price_...

# Email
RESEND_API_KEY=re_...

# Notifications
ONESIGNAL_APP_ID=...
ONESIGNAL_API_KEY=...

# Monitoring
SENTRY_DSN=https://...
POSTHOG_KEY=phc_...

# App
FRONTEND_URL=https://yourapp.com
```

---

## Pre-Launch Checklist

```
Security:
    ☐ All environment secrets in env vars, not code
    ☐ Judge0 firewall only allows API server IP
    ☐ Rate limiting on all endpoints
    ☐ Input validation on all POST/PUT endpoints
    ☐ XSS sanitization on problem descriptions
    ☐ CORS only allows your frontend domain
    ☐ Security headers configured
    ☐ HTTPS everywhere (Cloudflare handles this)

Legal:
    ☐ Terms of Service page
    ☐ Privacy Policy page (GDPR compliant)
    ☐ Cookie consent banner
    ☐ Account deletion flow working
    ☐ Problem ownership policy published

Functionality:
    ☐ Room create → join → compete → results flow end-to-end
    ☐ Judge0 running all 10 languages correctly
    ☐ Stripe payments tested in test mode
    ☐ Email notifications sending
    ☐ WebSocket reconnection handling
    ☐ Room cleanup on disconnect

Monitoring:
    ☐ Sentry capturing errors
    ☐ PostHog tracking key events
    ☐ Uptime monitoring on status page
    ☐ Judge0 health check alert
```

---

*Document version: 1.0 — Technical implementation guide for CodeBattle*
