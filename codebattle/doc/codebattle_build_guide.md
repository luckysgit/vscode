# CodeBattle — Complete Build Guide
> Everything you need to rebuild this project from zero on a new machine.
> Written for: Personal.
---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack & Versions](#2-tech-stack--versions)
3. [Complete Folder Structure](#3-complete-folder-structure)
4. [All NPM Packages](#4-all-npm-packages)
5. [Environment Variables](#5-environment-variables)
6. [Step-by-Step Setup](#6-step-by-step-setup)
7. [How to Run Locally](#7-how-to-run-locally)
8. [Database Setup (Supabase)](#8-database-setup-supabase)
9. [Auth Setup (Clerk)](#9-auth-setup-clerk)
10. [Payments Setup (Stripe)](#10-payments-setup-stripe)
11. [Email Setup (Resend)](#11-email-setup-resend)
12. [Every Page — What It Does](#12-every-page--what-it-does)
13. [Every API Route](#13-every-api-route)
14. [Every Component](#14-every-component)
15. [Socket.io Event Map](#15-socketio-event-map)
16. [Database Schema](#16-database-schema)
17. [Security Implementation](#17-security-implementation)
18. [Known Limitations](#18-known-limitations)
19. [Deploy to Production](#19-deploy-to-production)
20. [Rebuild Prompts for Claude Code](#20-rebuild-prompts-for-claude-code)

---

## 1. Project Overview

**CodeBattle** is a real-time competitive coding platform where people compete in coding challenges across 10 programming languages.

### Core Features
- **Rooms** — Create a room, get unique code + QR, share with anyone, compete live
- **Real-time** — Live leaderboard updates as players submit, countdown timer, player list synced
- **10 Languages** — Python, JavaScript, TypeScript, Java, C++, C#, Go, Rust, PHP, Swift
- **Problems** — Browse 30+ problems, filter by difficulty/tag, publish your own
- **Daily Problem** — One problem per day, solve to maintain streak and earn XP
- **Connections** — Mutual connections via QR/code (no follow/follower system)
- **Challenge** — Challenge connections directly, or find random match
- **Leaderboard** — Global + weekly + per-language rankings
- **Profile** — XP, badges, streaks, solve history, weak spot tracker
- **Interview Mode** — Live coding interview with real-time code sync
- **Tournament** — Bracket-style competitions
- **Org Accounts** — Team/company accounts with private problem banks
- **Auth** — Email/password registration, account switcher (multiple accounts)
- **Payments** — Stripe subscription for Pro tier (unlimited rooms, org features)

### Key Differentiators
- No followers/following — mutual connections only
- Editor starts empty — no starter code hints
- Code never visible to opponents (only test results)
- Works offline with local fallbacks
- Session persists across server restarts

---

## 2. Tech Stack & Versions

```
Next.js          16.2.11   (App Router, webpack mode — NOT Turbopack)
React            19.2.4
TypeScript       5
Tailwind CSS     4
Node.js          22.x (required)
npm              10.x+
```

### Frontend Libraries
```
@monaco-editor/react    4.7.0   Code editor (VS Code in browser)
socket.io-client        4.8.3   WebSocket client
zustand                 5.0.14  State management
qrcode                  1.5.4   QR code generation (canvas-based, no CDN)
framer-motion           12.x    Animations
isomorphic-dompurify    3.19.0  XSS sanitization
posthog-js              1.x     Analytics
```

### Backend Libraries
```
express          5.2.1   REST API server
socket.io        4.8.3   WebSocket server
bcryptjs         3.0.3   Password hashing
bullmq           5.81.1  Job queue
ioredis          5.11.1  Redis client
@supabase/supabase-js  2.x  Database client
stripe           22.x    Payments
resend           6.x     Email
svix             1.x     Webhook verification
zod              4.x     Input validation
@sentry/nextjs   10.x    Error tracking
```

### Dev Tools
```
ts-node          10.9.2  Run TypeScript server
concurrently     10.x    Run multiple processes
@types/*         various  Type definitions
```

---

## 3. Complete Folder Structure

```
codebattle/
│
├── app/                          # Next.js App Router pages
│   ├── layout.tsx                # Root layout — PostHog, AuthProvider, InviteToast
│   ├── page.tsx                  # Landing page
│   ├── loading.tsx               # Global loading spinner
│   ├── error.tsx                 # Global error boundary (Sentry)
│   ├── not-found.tsx             # 404 page
│   ├── sitemap.ts                # Dynamic sitemap
│   │
│   ├── dashboard/
│   │   ├── page.tsx              # Main dashboard
│   │   └── loading.tsx           # Dashboard skeleton
│   │
│   ├── sign-in/[[...sign-in]]/
│   │   └── page.tsx              # Sign in (email + password)
│   │
│   ├── sign-up/[[...sign-up]]/
│   │   └── page.tsx              # Sign up (single step, no language)
│   │
│   ├── onboarding/
│   │   └── page.tsx              # Welcome screen after signup
│   │
│   ├── forgot-password/
│   │   └── page.tsx              # Forgot password form
│   │
│   ├── reset-password/
│   │   └── page.tsx              # Reset password (reads ?token=)
│   │
│   ├── room/
│   │   ├── create/page.tsx       # Create room (2 steps: settings + problems)
│   │   ├── [code]/
│   │   │   ├── page.tsx          # Live room (editor + leaderboard + WS)
│   │   │   ├── replay/page.tsx   # Watch how players solved it
│   │   │   └── spectate/page.tsx # Watch live room
│   │   ├── results/page.tsx      # Post-match results
│   │   └── not-found.tsx         # Room 404
│   │
│   ├── problems/
│   │   ├── page.tsx              # Browse problems (filter/search)
│   │   ├── loading.tsx           # Problems skeleton
│   │   ├── [id]/page.tsx         # Solve a problem solo
│   │   └── create/page.tsx       # Publish new problem (4-step wizard)
│   │
│   ├── problists/
│   │   ├── page.tsx              # Browse problem lists
│   │   ├── [id]/page.tsx         # View problist + solve problems
│   │   └── create/page.tsx       # Create problist
│   │
│   ├── daily/page.tsx            # Daily problem + streak tracker
│   ├── matchmaking/page.tsx      # Random match finder
│   ├── connections/page.tsx      # Manage connections (QR-based)
│   ├── leaderboard/
│   │   ├── page.tsx              # Global + weekly leaderboard
│   │   └── loading.tsx           # Leaderboard skeleton
│   ├── profile/
│   │   ├── page.tsx              # Own profile (XP, badges, history)
│   │   ├── [username]/page.tsx   # Public profile
│   │   └── weakspots/page.tsx    # Weak spot tracker
│   ├── tournament/page.tsx       # Tournament browser + bracket
│   ├── interview/page.tsx        # Live coding interview
│   ├── org/page.tsx              # Org/team dashboard
│   ├── admin/page.tsx            # Admin panel
│   ├── settings/page.tsx         # Profile, preferences, billing
│   ├── terms/page.tsx            # Terms of Service
│   ├── privacy/page.tsx          # Privacy Policy
│   │
│   └── api/                      # API routes
│       ├── auth/
│       │   ├── register/route.ts
│       │   ├── login/route.ts
│       │   ├── logout/route.ts
│       │   ├── me/route.ts
│       │   ├── change-password/route.ts
│       │   ├── forgot-password/route.ts
│       │   └── reset-password/route.ts
│       ├── rooms/route.ts
│       ├── problems/route.ts
│       ├── submissions/route.ts
│       ├── users/route.ts
│       ├── connections/route.ts
│       ├── leaderboard/route.ts
│       ├── problists/
│       │   ├── route.ts
│       │   └── [id]/route.ts
│       ├── tournament/route.ts
│       ├── admin/route.ts
│       ├── payments/
│       │   ├── checkout/route.ts
│       │   └── webhook/route.ts
│       └── webhooks/
│           └── clerk/route.ts
│
├── components/
│   ├── editor/
│   │   └── CodeEditor.tsx        # Monaco editor (CDN-loaded, textarea fallback)
│   ├── auth/
│   │   ├── AuthProvider.tsx      # Session restoration on startup
│   │   └── AccountSwitcher.tsx   # Multi-account dropdown
│   ├── analytics/
│   │   ├── PostHogProvider.tsx   # Analytics (lazy loaded)
│   │   └── PostHogWrapper.tsx    # Client wrapper for layout
│   ├── notifications/
│   │   ├── InviteToast.tsx       # Challenge invite notification
│   │   ├── InviteToastWrapper.tsx # Client wrapper for layout
│   │   └── XPToast.tsx           # XP earned notification
│   ├── qr/
│   │   └── RoomQR.tsx            # QR code generator (canvas, no CDN)
│   ├── nav/
│   │   └── Navbar.tsx            # Responsive navbar (not used on all pages yet)
│   ├── skeleton/
│   │   └── CardSkeleton.tsx      # Loading skeletons
│   └── ui/
│       └── DemoBanner.tsx        # "Demo data" warning banner
│
├── lib/                          # Shared utilities
│   ├── auth.ts                   # Local auth (file-based, survives restarts)
│   ├── apiAuth.ts                # Auth middleware for API routes
│   ├── db.ts                     # Supabase helpers (lazy client creation)
│   ├── problems.ts               # Problem type + seed data (uses problemBank)
│   ├── problemBank.ts            # 30+ real problems across DSA topics
│   ├── store.ts                  # Seed data (leaderboard, problists)
│   ├── user.ts                   # User types, badge definitions
│   ├── xp.ts                     # XP logic, badge checks, localStorage helpers
│   ├── socket.ts                 # Socket.io client helpers
│   ├── runCode.ts                # Client-side code runner (calls /api/submissions)
│   ├── codeRunner.ts             # Server-side Judge0/Piston abstraction
│   ├── email.ts                  # Resend email templates
│   ├── stripe.ts                 # Stripe client helper
│   ├── rateLimit.ts              # Upstash rate limiter (in-memory fallback)
│   ├── sanitize.ts               # DOMPurify XSS sanitization
│   └── monitoring.ts             # Sentry + PostHog unified helper
│
├── store/                        # Zustand state
│   ├── authStore.ts              # User session (persisted to localStorage)
│   ├── roomStore.ts              # Room state
│   └── presenceStore.ts          # Online presence, invite state
│
├── server/
│   ├── index.ts                  # Socket.io + Express WS server
│   ├── workers.ts                # BullMQ workers (submissions, XP, daily jobs)
│   └── tsconfig.json             # Server TypeScript config
│
├── supabase/
│   ├── schema.sql                # Full DB schema (run this first)
│   └── seed.sql                  # Seed data (run after schema)
│
├── public/
│   ├── manifest.json             # PWA manifest
│   └── robots.txt                # SEO crawl rules
│
├── .data/
│   └── users.json                # Local user store (auto-created, gitignored)
│
├── next.config.ts                # Next.js config (webpack, security headers, CSP)
├── proxy.ts                      # Route protection middleware
├── package.json                  # Dependencies + scripts
├── tsconfig.json                 # TypeScript config
└── .env.local                    # Environment variables (never commit)
```

---

## 4. All NPM Packages

```bash
# Core
npm install next@16.2.11 react@19.2.4 react-dom@19.2.4 typescript

# UI
npm install tailwindcss @tailwindcss/postcss
npm install framer-motion
npm install @monaco-editor/react

# State & Real-time
npm install zustand
npm install socket.io socket.io-client

# Auth & Security
npm install bcryptjs
npm install svix
npm install isomorphic-dompurify

# Database
npm install @supabase/supabase-js

# Payments & Email
npm install stripe @stripe/stripe-js
npm install resend

# Code Execution & Jobs
npm install bullmq ioredis

# Validation & Utils
npm install zod
npm install qrcode
npm install js-cookie

# Monitoring
npm install @sentry/nextjs
npm install posthog-js

# Rate Limiting
npm install @upstash/ratelimit @upstash/redis

# Dev
npm install -D ts-node concurrently
npm install -D @types/bcryptjs @types/qrcode @types/js-cookie @types/node
npm install -D @types/react @types/react-dom @types/express @types/cors
npm install -D eslint eslint-config-next
```

---

## 5. Environment Variables

Create `.env.local` in project root:

```bash
# ── 1. SUPABASE (Real Database) ─────────────────────────────
# supabase.com → New project → Settings → API
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# ── 2. CLERK (Production Auth — optional, local auth works without) ──
# clerk.com → Create app → API Keys
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
CLERK_WEBHOOK_SECRET=whsec_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/onboarding

# ── 3. UPSTASH REDIS (Room state + Rate limiting) ────────────
# console.upstash.com → Create Redis → REST tab
UPSTASH_REDIS_REST_URL=https://...upstash.io
UPSTASH_REDIS_REST_TOKEN=...
UPSTASH_REDIS_URL=rediss://...  # for ioredis in WS server

# ── 4. JUDGE0 (Secure code execution — optional, Piston is default) ──
# Deploy Judge0 on DigitalOcean or use RapidAPI
JUDGE0_URL=https://your-judge0-instance.com
JUDGE0_API_KEY=your_key

# ── 5. STRIPE (Payments) ────────────────────────────────────
# dashboard.stripe.com → Create "Pro Plan" product
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PAID_PRICE_ID=price_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...

# ── 6. RESEND (Email) ────────────────────────────────────────
# resend.com → API Keys
RESEND_API_KEY=re_...
RESEND_FROM_EMAIL=noreply@yourdomain.com

# ── 7. SENTRY (Error tracking) ──────────────────────────────
# sentry.io → New project (Next.js) → DSN
NEXT_PUBLIC_SENTRY_DSN=https://...@sentry.io/...

# ── 8. POSTHOG (Analytics) ──────────────────────────────────
# posthog.com → Project → API key
NEXT_PUBLIC_POSTHOG_KEY=phc_...

# ── 9. ADMIN ─────────────────────────────────────────────────
# Comma-separated admin emails
ADMIN_EMAILS=admin@yourdomain.com
ADMIN_USER_IDS=local-user  # for dev

# ── 10. APP URLS ─────────────────────────────────────────────
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_WS_URL=http://localhost:3001
FRONTEND_URL=http://localhost:3000
WS_PORT=3001
NODE_ENV=development
```

---

## 6. Step-by-Step Setup

### On a Fresh Machine

```bash
# 1. Install Node.js 22 from nodejs.org

# 2. Create project with Next.js
npx create-next-app@16.2.11 codebattle --typescript --tailwind --app --no-src-dir --import-alias "@/*"

cd codebattle

# 3. Install all packages (copy from section 4 above)

# 4. Create folder structure
mkdir -p app/dashboard app/room/create "app/room/[code]" app/problems "app/problems/[id]" app/problems/create
mkdir -p app/problists "app/problists/[id]" app/problists/create
mkdir -p app/daily app/matchmaking app/connections app/leaderboard
mkdir -p "app/profile/[username]" app/profile/weakspots
mkdir -p app/tournament app/interview app/org app/admin app/settings
mkdir -p app/onboarding "app/sign-in/[[...sign-in]]" "app/sign-up/[[...sign-up]]"
mkdir -p app/forgot-password app/reset-password
mkdir -p app/api/auth/register app/api/auth/login app/api/auth/logout app/api/auth/me
mkdir -p app/api/auth/change-password app/api/auth/forgot-password app/api/auth/reset-password
mkdir -p app/api/rooms app/api/problems app/api/submissions app/api/users
mkdir -p app/api/connections app/api/leaderboard "app/api/problists/[id]"
mkdir -p app/api/tournament app/api/admin
mkdir -p app/api/payments/checkout app/api/payments/webhook
mkdir -p app/api/webhooks/clerk
mkdir -p components/editor components/auth components/analytics
mkdir -p components/notifications components/qr components/nav
mkdir -p components/skeleton components/ui
mkdir -p lib store server supabase public

# 5. Create .env.local (see section 5)

# 6. Update next.config.ts to use webpack (not Turbopack):
# Add: package.json scripts "dev": "next dev --webpack"

# 7. Run
npm run dev
```

---

## 7. How to Run Locally

### Two terminals needed:

**Terminal 1 — Next.js Frontend:**
```bash
cd codebattle
npm run dev
# Runs on http://localhost:3000
```

**Terminal 2 — Socket.io WebSocket Server (for multiplayer):**
```bash
cd codebattle
npm run server
# Runs on http://localhost:3001
```

**Or both at once:**
```bash
npm run dev:all
# Uses concurrently to run both
```

### Package.json scripts:
```json
{
  "dev":     "next dev --webpack",
  "server":  "npx ts-node --project server/tsconfig.json server/index.ts",
  "dev:all": "concurrently --names \"NEXT,WS\" --prefix-colors \"cyan,green\" \"npm run dev\" \"npm run server\"",
  "build":   "next build",
  "start":   "next start"
}
```

**Important:** Always use `--webpack` flag. Turbopack breaks Monaco Editor.

---

## 8. Database Setup (Supabase)

### Step 1: Create Project
1. Go to [supabase.com](https://supabase.com) → Sign up → New Project
2. Name: `codebattle`, choose region closest to you
3. Wait ~2 minutes for setup

### Step 2: Run Schema
1. Supabase dashboard → **SQL Editor** → New Query
2. Paste contents of `supabase/schema.sql` → **Run**

### Step 3: Run Seed Data
1. SQL Editor → New Query
2. Paste contents of `supabase/seed.sql` → **Run**
3. This inserts 10 seed problems + problists

### Step 4: Get Keys
1. Supabase → **Settings → API**
2. Copy: Project URL, anon public key, service_role key
3. Paste into `.env.local`

### Tables Created:
- `users` — user accounts
- `user_credentials` — password hashes (local auth)
- `connections` — mutual user connections
- `problems` — coding problems
- `test_cases` — test cases for problems
- `problists` — curated problem lists
- `problist_problems` — junction table
- `rooms` — competition rooms
- `room_problems` — problems in a room
- `room_participants` — players in a room
- `submissions` — code submissions (partitioned by month)
- `badges` — earned badges
- `problem_flags` — flagged problems
- `audit_logs` — admin audit trail

---

## 9. Auth Setup (Clerk)

### For Production (Optional — local auth works without this)

1. Go to [clerk.com](https://clerk.com) → Create application → "CodeBattle"
2. Enable: Google, GitHub, Email sign-in
3. Copy publishable key + secret key → `.env.local`
4. Add webhook:
   - Clerk dashboard → Webhooks → Add endpoint
   - URL: `https://yourdomain.com/api/webhooks/clerk`
   - Events: `user.created`, `user.updated`, `user.deleted`
   - Copy signing secret → `CLERK_WEBHOOK_SECRET`

### Local Auth (No Clerk needed)
- Users stored in `.data/users.json` (auto-created)
- Passwords hashed with bcrypt (12 rounds)
- Session via httpOnly cookie (base64 encoded)
- Survives server restarts

---

## 10. Payments Setup (Stripe)

1. Go to [dashboard.stripe.com](https://dashboard.stripe.com)
2. Create product: "CodeBattle Pro" → $9/month → copy Price ID
3. Get secret key from Developers → API keys
4. Webhook: Developers → Webhooks → Add endpoint
   - URL: `https://yourdomain.com/api/payments/webhook`
   - Events: `customer.subscription.*`, `invoice.payment_failed`
   - Copy webhook secret

Pro tier unlocks:
- Unlimited players per room (free = max 100)
- Unlimited concurrent rooms
- Interview mode
- Tournament hosting
- Org/team accounts

---

## 11. Email Setup (Resend)

1. Go to [resend.com](https://resend.com) → Sign up free
2. Verify your domain or use Resend's shared domain for testing
3. Create API key → copy to `.env.local`
4. Set `RESEND_FROM_EMAIL=noreply@yourdomain.com`

Emails sent:
- Welcome email on registration
- Password reset link
- Streak reminder (when implemented as scheduled job)
- Weekly digest (when implemented as scheduled job)

---

## 12. Every Page — What It Does

### Public Pages

| Page | URL | Description |
|---|---|---|
| Landing | `/` | Hero, features, sign up CTA |
| Sign In | `/sign-in` | Email + password login, forgot password link |
| Sign Up | `/sign-up` | Single form: username + email + password |
| Onboarding | `/onboarding` | Welcome screen after signup |
| Forgot Password | `/forgot-password` | Enter email, sends reset link |
| Reset Password | `/reset-password?token=X` | Set new password |
| Terms | `/terms` | Terms of Service |
| Privacy | `/privacy` | Privacy Policy |

### Protected Pages (require login)

| Page | URL | Description |
|---|---|---|
| Dashboard | `/dashboard` | Home: daily CTA, create/join room, stats, nav |
| Daily | `/daily` | Today's problem + streak calendar + XP reward |
| Problems | `/problems` | Browse all problems, filter by difficulty/tag |
| Problem Solve | `/problems/[id]` | Solo problem solving with Monaco editor |
| Problem Create | `/problems/create` | 4-step wizard to publish a problem |
| Create Room | `/room/create` | 2-step: settings + problem selection |
| Room Live | `/room/[code]` | Competition room (editor + WS + leaderboard) |
| Room Results | `/room/results?room=CODE` | Post-match results |
| Room Replay | `/room/[code]/replay` | Watch how players solved it |
| Room Spectate | `/room/[code]/spectate` | Watch live room |
| Problists | `/problists` | Browse curated problem lists |
| Problist | `/problists/[id]` | View + solve problems in a list |
| Create Problist | `/problists/create` | Create your own problist |
| Matchmaking | `/matchmaking` | Find random opponent |
| Connections | `/connections` | Manage mutual connections via QR/code |
| Leaderboard | `/leaderboard` | Global + weekly + per-language rankings |
| My Profile | `/profile` | Own profile: XP, badges, history |
| Public Profile | `/profile/[username]` | View anyone's public profile |
| Weak Spots | `/profile/weakspots` | Analysis of where you struggle |
| Tournament | `/tournament` | Browse + register for tournaments |
| Interview | `/interview` | Live coding interview (real-time sync) |
| Org | `/org` | Team/company dashboard |
| Admin | `/admin` | Admin panel (email-gated) |
| Settings | `/settings` | Profile, preferences, account, billing |

---

## 13. Every API Route

### Auth Routes

| Route | Method | Auth | Description |
|---|---|---|---|
| `/api/auth/register` | POST | No | Create account. Body: `{username, email, password}`. Returns user + sets cookie. Blocks duplicate email/username. |
| `/api/auth/login` | POST | No | Sign in. Body: `{email, password}`. Returns user + sets cookie. |
| `/api/auth/logout` | POST | No | Clears session cookie. |
| `/api/auth/me` | GET | Cookie | Returns current user from session. |
| `/api/auth/change-password` | POST | Yes | Body: `{currentPassword, newPassword}`. Verifies current, updates hash. |
| `/api/auth/forgot-password` | POST | No | Body: `{email}`. Sends reset email (always returns success to prevent enumeration). |
| `/api/auth/reset-password` | POST | No | Body: `{token, newPassword}`. Validates token, updates password, auto signs in. |

### Room Routes

| Route | Method | Auth | Description |
|---|---|---|---|
| `/api/rooms` | POST | Yes | Create room. Body: `{languages, difficulty, timerType, timeLimitSeconds, isPublic, problemIds}`. Returns `{code, room}`. |
| `/api/rooms?code=X` | GET | No | Get room by code. Returns room state. |

### Problem Routes

| Route | Method | Auth | Description |
|---|---|---|---|
| `/api/problems` | GET | No | List problems. Params: `?id=`, `?difficulty=`, `?tag=`, `?search=`. Hides hidden test cases. |
| `/api/problems` | POST | Yes | Create problem. Body: `{title, description, difficulty, visibility, languageTags, inputFormat, outputFormat, testCases[]}`. |
| `/api/problems?id=X` | PUT | Yes | Flag problem. Body: `{action:"flag", reason}`. |

### Submission Routes

| Route | Method | Auth | Description |
|---|---|---|---|
| `/api/submissions` | POST | Yes | Run or submit code. Body: `{code, language, problemId, roomId?, stdin?}`. If `stdin` provided → run mode (single test). If not → submit mode (all tests). Returns `{results, testsPassed, allPassed, score, xpEarned}`. |

### User Routes

| Route | Method | Auth | Description |
|---|---|---|---|
| `/api/users?me=true` | GET | Yes | Get current user with badges + recent submissions. |
| `/api/users?username=X` | GET | No | Get public profile. |
| `/api/users` | PUT | Yes | Update user. Body: `{username?, language?}`. |

### Other Routes

| Route | Method | Auth | Description |
|---|---|---|---|
| `/api/connections` | GET | Yes | Get user's connections. |
| `/api/connections` | POST | Yes | Add connection. Body: `{targetUserId}`. |
| `/api/connections` | DELETE | Yes | Remove connection. Body: `{targetUserId}`. |
| `/api/leaderboard` | GET | No | Get leaderboard. Params: `?language=`, `?tab=global\|weekly`, `?limit=`. |
| `/api/problists` | GET | No | List public problists. |
| `/api/problists` | POST | Yes | Create problist. Body: `{title, description, visibility, problemIds[]}`. |
| `/api/problists/[id]` | GET | No | Get problist with problems. |
| `/api/tournament` | GET | No | List tournaments. |
| `/api/tournament` | POST | Yes | Register/create tournament room. |
| `/api/admin?type=overview\|flagged\|logs` | GET | Admin | Admin data. |
| `/api/admin` | POST | Admin | Actions: `approve_problem`, `remove_problem`, `ban_user`, `dismiss_flag`. |
| `/api/payments/checkout` | POST | Yes | Create Stripe checkout session. Returns `{url}`. |
| `/api/payments/webhook` | POST | Stripe | Handle Stripe events (subscription changes). |
| `/api/webhooks/clerk` | POST | Svix | Handle Clerk user events (create/update/delete). |

---

## 14. Every Component

### `components/editor/CodeEditor.tsx`
Monaco Editor wrapper. Loads from CDN (cdn.jsdelivr.net). Falls back to `<textarea>` if CDN blocked (8-second timeout). Supports all 10 languages. Props: `{language, value, onChange, readOnly}`.

### `components/auth/AuthProvider.tsx`
Client component wrapping the entire app. On mount: tries `/api/auth/me`, if fails tries localStorage persisted user. Redirects unauthenticated users from protected pages to `/sign-in`.

### `components/auth/AccountSwitcher.tsx`
Avatar dropdown in dashboard navbar. Shows current account, saved accounts (from localStorage), switch/add/remove options, sign out. Deduplicates by email. Saves accounts to `cb_saved_accounts` in localStorage.

### `components/analytics/PostHogProvider.tsx`
Lazy-loads PostHog. Tracks pageviews on route change. Wraps children.

### `components/analytics/PostHogWrapper.tsx`
Client component wrapper for `PostHogProvider` (needed because layout.tsx is a Server Component).

### `components/notifications/InviteToast.tsx`
Floating challenge invite notification (bottom-right). Shows 30-second countdown bar, challenger info, Accept/Decline buttons. Accept navigates to room. Reads from `presenceStore`.

### `components/notifications/InviteToastWrapper.tsx`
Client component wrapper for `InviteToast`.

### `components/notifications/XPToast.tsx`
Bottom-left XP earned notification. Shows `+XP ⭐` and optional badge unlock. Auto-dismisses after 3 seconds.

### `components/qr/RoomQR.tsx`
QR code generator using `qrcode` npm package (canvas-based, no external requests). Shows room code, copy button, copy link button.

### `components/nav/Navbar.tsx`
Responsive sticky navbar with mobile hamburger. Not yet used on all pages (individual pages have their own navbars).

### `components/skeleton/CardSkeleton.tsx`
Loading skeleton components: `CardSkeleton`, `ListSkeleton`, `ProblemSkeleton`.

### `components/ui/DemoBanner.tsx`
Yellow warning banner shown when page is displaying seed/demo data instead of real DB data.

---

## 15. Socket.io Event Map

### Server URL: `http://localhost:3001`

### Client → Server Events

| Event | Payload | Description |
|---|---|---|
| `room:join` | `{roomCode, userId, username}` | Join a room |
| `room:leave` | `{roomCode, userId}` | Leave a room |
| `room:start` | `{roomCode, userId}` | Host starts the room |
| `room:activity` | `{roomCode, userId}` | Typing indicator pulse |
| `submission:result` | `{roomCode, userId, testsPassed, testsTotal, score, allPassed}` | Broadcast submission result to room |
| `room:reaction` | `{roomCode, userId, emoji}` | Send emoji reaction |
| `interview:join` | `{sessionCode, role, userId}` | Join interview session |
| `interview:code_update` | `{sessionCode, code, language}` | Candidate code changed |
| `interview:leave` | `{sessionCode}` | Leave interview |

### Server → Client Events

| Event | Payload | Description |
|---|---|---|
| `room:state` | Full room state | Sent on join |
| `room:player_joined` | `{userId, username, playerCount}` | Someone joined |
| `room:player_left` | `{userId, playerCount}` | Someone left |
| `room:countdown` | `{seconds: 5}` | Start countdown |
| `room:tick` | `{seconds}` | Countdown tick |
| `room:started` | `{startedAt, timeLimitSec}` | Room went active |
| `room:progress_update` | `{userId, testsPassed, score, leaderboard[]}` | Live leaderboard update |
| `room:player_finished` | `{userId, rank, score, timeTakenMs}` | Player finished |
| `room:ended` | `{leaderboard[], endedAt}` | Room ended |
| `room:activity_pulse` | `{userId}` | Typing indicator |
| `room:reaction` | `{userId, emoji}` | Emoji reaction |
| `interview:user_joined` | `{role, userId}` | Other party joined interview |
| `interview:code_update` | `{code, language}` | Code update from candidate |
| `interview:user_left` | — | Other party left |
| `error` | `{code, message}` | Error (ROOM_NOT_FOUND, NOT_HOST, etc.) |

---

## 16. Database Schema

### Core Tables

```sql
-- Users
users (
  id UUID PRIMARY KEY,
  clerk_id TEXT UNIQUE,     -- Clerk user ID (or local_<id> for local auth)
  username TEXT UNIQUE,
  email TEXT UNIQUE,
  avatar_url TEXT,
  tier TEXT DEFAULT 'free', -- 'free' | 'paid'
  xp INTEGER DEFAULT 0,
  rank TEXT DEFAULT 'Bronze',
  streak INTEGER DEFAULT 0,
  last_solve_at TIMESTAMP,
  stripe_customer_id TEXT,
  created_at TIMESTAMP
)

-- Local auth passwords (dev only — Clerk handles this in production)
user_credentials (
  user_id UUID → users.id,
  password_hash TEXT,
  created_at TIMESTAMP
)

-- Mutual connections
connections (
  user_a_id UUID → users.id,
  user_b_id UUID → users.id,
  connected_at TIMESTAMP,
  UNIQUE(user_a_id, user_b_id),
  CHECK (user_a_id < user_b_id)  -- enforces no duplicates
)

-- Problems
problems (
  id UUID PRIMARY KEY,
  author_id UUID → users.id,
  title TEXT,
  description TEXT,
  difficulty TEXT,           -- 'easy' | 'medium' | 'hard'
  visibility TEXT,           -- 'public' | 'private' | 'connections'
  unique_code TEXT UNIQUE,   -- short code for sharing
  language_tags TEXT[],
  input_format TEXT,
  output_format TEXT,
  solve_count INTEGER DEFAULT 0,
  is_flagged BOOLEAN DEFAULT false,
  is_approved BOOLEAN DEFAULT true,
  created_at TIMESTAMP
)

-- Test cases
test_cases (
  id UUID PRIMARY KEY,
  problem_id UUID → problems.id,
  input TEXT,
  expected TEXT,
  is_hidden BOOLEAN DEFAULT false,
  order_index INTEGER
)

-- Rooms
rooms (
  id UUID PRIMARY KEY,
  host_id UUID → users.id,
  unique_code TEXT UNIQUE,
  status TEXT,               -- 'lobby' | 'countdown' | 'active' | 'ended'
  tier TEXT DEFAULT 'free',
  max_players INTEGER DEFAULT 100,
  timer_type TEXT,           -- 'countdown' | 'countup'
  time_limit_s INTEGER DEFAULT 1800,
  is_public BOOLEAN DEFAULT false,
  languages TEXT[],
  difficulty TEXT,
  started_at TIMESTAMP,
  ended_at TIMESTAMP,
  created_at TIMESTAMP
)

-- Submissions (partitioned by month for scale)
submissions (
  id UUID PRIMARY KEY,
  room_id UUID → rooms.id,
  user_id UUID → users.id,
  problem_id UUID → problems.id,
  language TEXT,
  code TEXT,
  status TEXT,               -- 'accepted' | 'wrong_answer' | etc
  tests_passed INTEGER,
  tests_total INTEGER,
  score INTEGER,
  time_taken_ms INTEGER,
  submitted_at TIMESTAMP
) PARTITION BY RANGE (submitted_at)

-- Badges
badges (
  id UUID PRIMARY KEY,
  user_id UUID → users.id,
  badge_type TEXT,           -- 'first_solve' | 'streak_7' | etc
  awarded_at TIMESTAMP
)
```

### XP System
```
Easy problem solved:    30 XP
Medium problem solved:  60 XP
Hard problem solved:   120 XP
First try bonus:        20 XP
Daily problem bonus:    50 XP
Room win:               40 XP
```

### Rank Thresholds
```
Bronze:   0 XP
Silver:   1,000 XP
Gold:     3,000 XP
Platinum: 6,000 XP
Diamond:  9,000 XP
Master:   15,000 XP
```

---

## 17. Security Implementation

### Authentication
- Passwords hashed with **bcrypt** (12 rounds)
- Session via **httpOnly cookie** (7-day expiry)
- Duplicate email/username blocked at registration

### API Security
- **Rate limiting** on all auth endpoints (Upstash Redis, in-memory fallback)
- **Zod validation** on all POST/PUT request bodies
- **requireAuth middleware** on every protected route
- **Admin RBAC** — admin access requires email in `ADMIN_EMAILS` env var

### Content Security
- **DOMPurify** sanitization on user-submitted problem descriptions
- **Security headers** via Next.js config:
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `Content-Security-Policy` with strict sources
  - `Referrer-Policy: strict-origin-when-cross-origin`

### Code Execution
- All code runs in **Piston API** (sandboxed, no local execution)
- Production path: **Judge0** (isolated Docker container, no network, CPU/RAM limits)

### Data
- Hidden test cases never sent to client
- Submission code only visible to owner
- Connections are mutual (enforced by DB constraint)

---

## 18. Known Limitations

### Currently Fake/Demo Data
- Leaderboard shows seed data when Supabase not connected
- Connections shows empty (correct) but no real presence detection without WS
- Replay page shows demo snapshots (needs DB for real)
- Admin stats are seed data until DB connected
- `"50 players searching"` in matchmaking is hardcoded random

### Not Yet Production-Ready
- Challenge invitation only works locally (no push to other user's browser)
- Replay requires submission history in DB
- Org accounts are UI-only (no real backend)
- Weekly leaderboard computes on-the-fly (no cached weekly scores)
- No email verification on registration
- No 2FA

### Technical Debt
- Monaco editor loads from CDN (cdn.jsdelivr.net) — may be slow/blocked on restricted networks. Fallback: textarea
- WS server uses in-memory room state (Redis configured but optional)
- `.data/users.json` is local-only auth — not suitable for multi-server deployment

---

## 19. Deploy to Production

### Frontend — Vercel (Free)
```bash
# 1. Push to GitHub
git init && git add . && git commit -m "initial"
git remote add origin https://github.com/you/codebattle.git
git push -u origin main

# 2. Go to vercel.com → Import project → Select repo
# 3. Add all environment variables from .env.local
# 4. Deploy → get URL like codebattle.vercel.app
```

### WebSocket Server — Railway ($5/mo)
```bash
# railway.app → New project → Deploy from GitHub
# Set root to /server
# Set start command: npx ts-node --project tsconfig.json index.ts
# Add environment variables
# Get URL like codebattle-ws.railway.app
```

### Database — Supabase (Free tier)
- Already cloud-hosted after setup in section 8
- Free tier: 500MB database, 2GB bandwidth

### Code Runner — Keep Piston API for now
- Free public API, no setup needed
- For production security: deploy Judge0 on DigitalOcean ($12/mo)

### DNS
```
codebattle.gg    → Vercel (A record)
ws.codebattle.gg → Railway (CNAME)
```

---

## 20. Rebuild Prompts for Claude Code

Use these prompts **in order** with Claude Code on your personal laptop to rebuild the entire project.

---

### PROMPT 1 — Project Setup
```
Create a new Next.js 16 project called "codebattle" with TypeScript, Tailwind CSS, App Router.
Use webpack (not Turbopack) by setting the dev script to "next dev --webpack".
Install these packages:
- zustand socket.io socket.io-client @monaco-editor/react framer-motion
- bcryptjs zod isomorphic-dompurify qrcode
- @supabase/supabase-js stripe resend svix
- bullmq ioredis @upstash/ratelimit @upstash/redis
- @sentry/nextjs posthog-js
- express cors dotenv
- ts-node concurrently (dev)
- All @types/* for above packages

Set up the folder structure for a full-stack Next.js app with:
- app/ (all pages)
- components/ (reusable UI)
- lib/ (utilities)
- store/ (Zustand)
- server/ (Socket.io backend)
- supabase/ (SQL files)
- public/ (static assets)

Create .env.local with placeholder keys for Supabase, Clerk, Stripe, Resend, Sentry, PostHog.
```

---

### PROMPT 2 — Auth System
```
Build a complete local authentication system for CodeBattle (a coding competition platform).

Requirements:
- File: lib/auth.ts — persistent file-based user store saved to .data/users.json (survives server restarts)
- File: lib/apiAuth.ts — middleware that checks Clerk JWT first, falls back to local session cookie, falls back to dev mode
- API route: POST /api/auth/register — validates username/email/password, hashes with bcrypt (12 rounds), blocks duplicate email AND username, saves to file store, sets httpOnly session cookie, sends welcome email
- API route: POST /api/auth/login — verifies email+password against file store, sets cookie
- API route: POST /api/auth/logout — clears cookie
- API route: GET /api/auth/me — reads session cookie, returns user
- API route: POST /api/auth/change-password — verifies current password, updates hash
- API route: POST /api/auth/forgot-password — generates reset token, sends email via Resend
- API route: POST /api/auth/reset-password — validates token, updates password, auto signs in

Zustand store: store/authStore.ts — persists to localStorage, has setUser, logout methods
AuthProvider component: restores session on startup, tries /api/auth/me, falls back to localStorage persisted user when server restarts

Sign-up page: single step (username + email + password), no language selection, submits directly to /api/auth/register, redirects to /dashboard
Sign-in page: email + password, forgot password link, handles ?hint= and ?add= params
Onboarding page: simple welcome screen, no re-asking info

AccountSwitcher component: avatar dropdown with current account, switch account, add account, create account, sign out. Saves accounts to localStorage, deduplicates by email.
```

---

### PROMPT 3 — Database Layer
```
Set up Supabase database integration for CodeBattle.

Create lib/db.ts with:
- Lazy client creation (only creates Supabase client when URLs are configured)
- isSupabaseConfigured() function that checks all 3 keys are present
- Helper functions for: users (CRUD, XP update, streak update, leaderboard)
- Helper functions for: rooms (create, get by code, update status, participants)
- Helper functions for: problems (list public, get by ID, get test cases, create, flag)
- Helper functions for: submissions (save, get by user, get by room)
- Helper functions for: connections (get, add, remove)
- Helper functions for: badges (award, get user badges)
- Helper functions for: problists (list public, get by ID, get problems)
- Audit log helper

Create supabase/schema.sql with all tables: users, user_credentials, connections, problems, test_cases, problists, problist_problems, rooms, room_problems, room_participants, submissions (partitioned by month), badges, problem_flags, audit_logs.

Create supabase/seed.sql with 10 seed problems (Two Sum, FizzBuzz, Palindrome, etc.) and 4 seed problists.

All API routes should:
- Check isSupabaseConfigured() first
- Use DB when configured
- Fall back to hardcoded seed data when not (with DemoBanner shown to user)
```

---

### PROMPT 4 — Code Execution
```
Build a code execution system for CodeBattle that supports 10 languages.

Create lib/codeRunner.ts (server-side):
- Uses Judge0 if JUDGE0_URL is configured (production)
- Falls back to Piston API (https://emkc.org/api/v2/piston/execute) when not
- Language map for both Judge0 IDs and Piston names
- Configurable CPU time limit, memory limit
- Returns: { output, stderr, exitCode, timedOut }

Create lib/runCode.ts (client-side):
- runCodeClient(code, language, stdin, problemId) — calls POST /api/submissions with stdin
- submitCodeClient(code, language, problemId, roomId?) — calls POST /api/submissions without stdin

Create API route POST /api/submissions:
- Auth required
- Run mode (stdin provided): runs code against single input, returns output
- Submit mode (no stdin): runs against ALL test cases, returns pass/fail per case, saves to DB, awards XP, checks badges

Create components/editor/CodeEditor.tsx:
- Uses @monaco-editor/react
- Loads Monaco from CDN: https://cdn.jsdelivr.net/npm/monaco-editor@0.52.0/min/vs
- 8-second timeout fallback to plain <textarea> with warning banner
- Props: language, value, onChange, readOnly
- Starts EMPTY by default (no starter code — user writes everything)
```

---

### PROMPT 5 — Problem System
```
Build the problem system for CodeBattle.

Create lib/problemBank.ts with 30 real DSA problems:
- 12 easy: Two Sum, Best Time to Buy/Sell, Contains Duplicate, Move Zeroes, Running Sum, Reverse String, Palindrome, Count Vowels, First Non-Repeating, Anagram, FizzBuzz, Power of Two, Factorial, Sum of Digits
- 12 medium: Max Subarray, 3Sum, Product Except Self, Rotate Array, Longest Substring, Group Anagrams, Longest Common Prefix, Binary Search, Rotated Search, Valid Parentheses, Min Stack, Coin Change, House Robber, Climbing Stairs, Number of Islands, Reverse Linked List
- 6 hard: Median of Two Arrays, LRU Cache, Word Break, Trapping Rain Water, Longest Increasing Subsequence

Each problem has: title, difficulty, tags, description, inputFormat, outputFormat, 3 visible test cases + 2 hidden test cases

Create /problems page: browse all problems, filter by difficulty (easy/medium/hard) and tag, search by title, shows solve count

Create /problems/[id] page: 
- Solo problem solving with Monaco editor (empty start)
- Run button: tests against selected visible test case
- Submit button: tests against ALL cases including hidden
- Shows pass/fail per visible case, hidden case summary
- Awards XP on all-pass, saves to solve history
- XP toast notification on solve

Create /problems/create page: 4-step wizard (details → format → test cases → review)
```

---

### PROMPT 6 — Room System + Real-time
```
Build the real-time room system for CodeBattle.

Create server/index.ts — Socket.io + Express server on port 3001:
- POST /rooms — creates room, stores in-memory (with Redis if configured)
- GET /rooms/:code — get room state
- Socket events: room:join, room:leave, room:start, room:activity, submission:result, room:reaction
- Server emits: room:state, room:player_joined, room:player_left, room:countdown, room:tick, room:started, room:progress_update, room:player_finished, room:ended
- Room state machine: lobby → countdown (5s) → active → ended
- Auto-end when timer expires or all players finish
- Saves room state to Redis with TTL when configured

Create lib/socket.ts — client-side Socket.io helpers: connectSocket, joinRoom, leaveRoom, startRoom, broadcastResult, sendReaction

Create /room/create page:
- Step 1: language, difficulty, timer type, time limit, public/private toggle
- Step 2: problem picker (loads from /api/problems, checkbox selection)
- Creates room via POST /api/rooms, navigates to /room/[code]?problemId=X

Create /room/[code] page:
- Uses useSearchParams to get problemId from URL
- Fetches real problem from /api/problems?id=X
- Monaco editor (locked during lobby, empty on start)
- QR code for sharing (canvas-based, no CDN)
- Players list synced via Socket.io
- Start Room button (host only)
- Run (single test case) + Submit (all test cases) buttons
- Live leaderboard updates
- Leave Room with confirmation dialog
- XP toast after successful submit
- �� Live / ⚫ Solo indicator based on WS connection
```

---

### PROMPT 7 — User Features
```
Build user profile, XP, badges, streaks, and daily features for CodeBattle.

Create lib/xp.ts:
- XP awards: easy=30, medium=60, hard=120, daily bonus=50, first try bonus=20
- Badge checks array (first_solve, clean_code, streak_7, streak_30, publisher, etc.)
- localStorage helpers: getLocalXP, addLocalXP, getLocalStreak, updateLocalStreak, getLocalBadges, saveLocalBadge

Create /daily page:
- Shows today's problem (rotates by day of year)
- 7-day streak calendar visualization
- Empty editor, Run + Submit buttons
- +50 XP reward on solve, streak updates
- Countdown to midnight reset

Create /profile page (own profile):
- All data from localStorage (XP, streak, solve history, rooms played)
- Hydrates from /api/users?me=true when DB configured
- Shows earned badges (empty state for new users)
- Recent solves list (empty state for new users)
- Empty state for problists
- Quick action links

Create /profile/[username] page (public):
- Fetches from /api/users?username=X
- Falls back to leaderboard seed data
- Shows XP progress bar, rank badge, badges

Create /profile/weakspots page:
- Per-tag pass rates from solve history
- Progress bars: green=strong, yellow=improving, red=weak
- "Practice →" links to /problems?tag=X

Create /leaderboard page:
- Global + weekly tabs (weekly fetches ?tab=weekly)
- Language filter
- Top 3 podium
- Full ranked table
- Demo banner when showing seed data
```

---

### PROMPT 8 — Social Features
```
Build connections, matchmaking, and challenge system for CodeBattle.

Create /connections page:
- Two tabs: My Connections | Add Connection
- "My Connections": grouped by Online/In Room/Offline
- Challenge button: opens modal to pick language + difficulty, creates real room via API, sends invite
- Add Connection: shows your QR code (canvas-based), enter someone's code
- Connections start EMPTY (no seed data)
- Fetches from /api/connections on load

Create store/presenceStore.ts:
- onlineUsers map with userId → {status: online|in-room|offline}
- pendingInvite state for incoming challenge
- setPendingInvite, setInviteSent methods

Create InviteToast component:
- Bottom-right floating notification
- 30-second countdown bar
- Shows challenger name, room code, language, difficulty
- Accept navigates to room, Decline closes

Create /matchmaking page:
- Pick language + difficulty
- "Find Random Match" button
- Spinning animation during search (3-8 seconds)
- Creates REAL room via /api/rooms when match found
- VS screen with room code
- Accept navigates to room

Create /connections API routes (GET, POST, DELETE):
- GET: returns user connections from DB, empty array fallback
- POST: add connection by userId
- DELETE: remove connection
```

---

### PROMPT 9 — Admin + Settings + Remaining Pages
```
Build admin panel, settings, and remaining pages for CodeBattle.

Create /admin page (email-gated):
- 4 tabs: Overview (stats + health), Flagged Problems, Suspicious Users, Audit Log
- Overview: fetches real stats from /api/admin?type=overview
- Flagged: Approve (calls POST /api/admin with action:approve_problem) + Remove buttons
- Suspicious: Dismiss + Ban User buttons (calls API to persist)
- Demo banner when showing seed data
- API route /api/admin: requireAdmin() checks ADMIN_EMAILS env var

Create /settings page:
- Profile tab: avatar color picker, username, bio, favourite language → saves via PUT /api/users
- Preferences tab: theme, notifications toggles → saves to localStorage
- Account tab: Change Password (modal, not prompt()), Delete Account (confirmation modal requiring "DELETE")
- Billing tab: current plan, upgrade to Pro (calls /api/payments/checkout)
- All buttons functional, no dead clicks

Create /tournament page:
- Browse upcoming tournaments (from /api/tournament)
- Register button creates real room
- Live bracket view (demo data until DB)

Create /interview page:
- Setup: pick role (interviewer/candidate), pick problem, get session code
- Live: Monaco editor with real-time code sync via Socket.io
- interviewer:code_update events broadcast candidate's code to interviewer
- Connected/disconnected status indicator

Create /org page: demo notice banner (paid feature)
Create /daily, /leaderboard, /problists pages (see earlier prompts)
Create 404 pages, loading.tsx for dashboard/problems/leaderboard
Create robots.txt, sitemap.ts, manifest.json for PWA
```

---

### PROMPT 10 — Security + Production Polish
```
Add security, error handling, and production polish to CodeBattle.

Security:
- lib/rateLimit.ts: Upstash rate limiter with in-memory fallback. Presets: login=5/min, register=3/min, submission=10/10s
- lib/sanitize.ts: DOMPurify sanitizeHtml + sanitizeText. Apply to problem descriptions on create.
- next.config.ts: Add security headers (X-Frame-Options DENY, CSP, X-Content-Type-Options)
- proxy.ts: Route protection middleware. Public routes: /, /sign-in, /sign-up, /problems, /leaderboard. Redirect unauthenticated to /sign-in?redirect=<path>
- API auth: all protected routes use requireAuth from lib/apiAuth.ts

Error handling:
- app/error.tsx: Global error boundary with Sentry reporting
- lib/monitoring.ts: Unified Sentry + PostHog. captureError(), trackEvent(), Events constants
- components/analytics/PostHogWrapper.tsx: Client wrapper for layout
- Add NEXT_PUBLIC_SENTRY_DSN and NEXT_PUBLIC_POSTHOG_KEY to .env.local

Polish:
- components/ui/DemoBanner.tsx: Yellow warning banner for demo data pages
- AccountSwitcher deduplicates by email (no duplicate accounts in switcher)
- Room join validates room exists before navigating (shows error for invalid codes)
- Settings save actually calls PUT /api/users (not fake setTimeout)
- All forms have proper error states and loading indicators
- Empty states for new users (no badges yet, no solves yet, no connections yet)
- XP toast on solve (bottom-left), invite toast on challenge (bottom-right)
```

---

## Quick Reference: What Works Without Any External Services

Running `npm run dev` with empty `.env.local`:

✅ **Works immediately:**
- Sign up / Sign in (stored in `.data/users.json`)
- Session persists across server restarts
- Browse problems (30 seed problems)
- Solve problems solo (via Piston API)
- Daily problem
- Create rooms (local mode)
- Start room + run code
- Profile, XP, streak (localStorage)

�� **Works but shows demo data:**
- Leaderboard (seed users)
- Connections (empty, no seed)
- Problists (seed lists)

❌ **Needs external service:**
- Real-time multiplayer (`npm run server`)
- Persistent rooms/submissions (Supabase)
- Real leaderboard (Supabase)
- Email notifications (Resend)
- Payments (Stripe)
- Error tracking (Sentry)

---

## Important Notes

1. **Always use `--webpack`** — `next dev` without this flag uses Turbopack which breaks Monaco Editor
2. **Two terminals** — frontend on 3000, WS server on 3001
3. **Admin access** — set `ADMIN_EMAILS=youremail@gmail.com` in `.env.local`
4. **Clearing local accounts** — delete `.data/users.json`
5. **Clearing browser data** — localStorage keys: `cb_auth`, `cb_saved_accounts`, `cb_solve_history`, `cb_rooms_played`, `cb_xp`, `cb_streak`, `cb_last_solve`, `cb_badges`

---

*This document was generated from the CodeBattle project built between July 2026.*
*Total: 38 pages, 7 API route groups, 15 components, 14 lib files, 3 store files.*
