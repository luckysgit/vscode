# CodeBattle — Real-Time Competitive Coding Platform

> Complete reference and build documentation based on `codebattle_build_guide.md` & `codebattle_build_quide_raw.txt`.

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Folder Structure](#3-folder-structure)
4. [Running the Application](#4-running-the-application)
5. [API Reference & Socket.io Events](#5-api-reference--socketio-events)
6. [Database Schema](#6-database-schema)
7. [Production Deployment Checklist](#7-production-deployment-checklist)

---

## 1. Project Overview

**CodeBattle** is a real-time multiplayer competitive coding platform where users compete in coding challenges across **10 programming languages**:
> Python, JavaScript, TypeScript, Java, C++, C#, Go, Rust, PHP, Swift

### Key Differentiators & Features:
* **Mutual Connections Only**: Zero follower/following hierarchy — mutual QR or code-based connections.
* **Unlimited Multiplayer Rooms**: Support for 100 free or unlimited paid room sizes with live leaderboards.
* **4 Competition Formats**: Speed Coding, Cross-Language Battles, Code Golf (fewest characters), and Debugging Race.
* **Psychological UX Touches**: 2-minute Warm-up mode, Anonymous Mode (generated aliases), AI Hint Nudge system (-50 pts penalty), and Focus Mode.
* **Isolated Micro-Container Code Execution**: Micro-container sandboxing with time (2.0s) and memory caps (256MB).

---

## 2. Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | HTML5 / React 19 + TypeScript | SPA Router & responsive UI |
| **Styling** | Vanilla CSS + Design System | Custom dark mode, glassmorphism, responsive navigation |
| **Code Editor** | Monaco Editor (`@monaco-editor/react`) | VS Code editor engine for all 10 languages |
| **State Management** | Zustand + `localStorage` | Client state persistence |
| **Real-time Client** | Socket.io / SSE / WebSockets | Live countdown, typing pulse, and leaderboards |
| **Backend API** | Node.js (Express) / Python 3 | REST API endpoints & code execution handler |
| **Database** | PostgreSQL (Supabase) | User profiles, submissions, problems, problists, rooms |
| **Cache / Queue** | Redis (Upstash) + BullMQ | Ephemeral room state, pub/sub, rate limiting |
| **Sandbox Execution**| Judge0 / Piston | Isolated multi-language code runner |

---

## 3. Folder Structure

```
codebattle/
├── web/                           # Client Single Page Application (SPA)
│   ├── index.html                 # Main UI layout & modal views
│   ├── index.css                  # Design system, themes & animations
│   └── app.js                     # SPA engine, Monaco editor integration & audio synth
│
├── server/                        # Backend REST & Execution Engine
│   ├── server.py                  # Live Python production server (Zero setup)
│   ├── server.js                  # Node.js Express + Socket.io server
│   └── package.json               # Backend dependencies
│
├── schema.sql                     # Full PostgreSQL database schema
└── README.md                      # Project setup & execution guide
```

---

## 4. Running the Application

### Option A: Running with Python (Zero-Dependency Engine)
```bash
cd /home/a/Documents/vscode/git/vscode/codebattle
python3 server/server.py
```
> Server runs live at `http://localhost:5000`

### Option B: Running with Node.js
```bash
cd /home/a/Documents/vscode/git/vscode/codebattle/server
npm install
npm start
```

---

## 5. API Reference & Socket.io Events

### REST API Routes

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | System health check & uptime |
| `GET` | `/api/rooms` | List active public battle rooms |
| `POST` | `/api/rooms` | Create new competitive room |
| `GET` | `/rooms/:code` | Fetch room lobby state by unique code |
| `GET` | `/api/problems` | List public problem bank |
| `POST` | `/api/problems` | Publish new custom problem |
| `POST` | `/problems/:id/fork` | Fork problem into user's repository |
| `POST` | `/api/submit` | Execute code submission in sandbox |
| `POST` | `/api/connections` | Create mutual connection via QR code |
| `GET` | `/api/leaderboard` | Global & per-language XP rankings |

### Socket.io / WebSocket Events
* `room:join` — User joins room lobby.
* `room:start` — Host triggers 5-second countdown sequence.
* `room:typing_pulse` — Emits typing activity pulse ("Opponent is typing...").
* `room:submit_result` — Emits test case result to live room leaderboard.
* `room:end` — Room completed, trigger podium view & replay data.

---

## 6. Database Schema (`schema.sql`)

```sql
-- Core PostgreSQL Tables
users (id, clerk_id, username, email, tier, xp, rank, streak, mutual_code)
connections (id, user_a_id, user_b_id, connected_at)
problems (id, author_id, title, description, difficulty, visibility, unique_code)
test_cases (id, problem_id, input, expected, is_hidden)
rooms (id, host_id, unique_code, status, timer_type, time_limit_s)
submissions (id, user_id, problem_id, language, status, execution_time_ms, memory_used_kb)
```

---

## 7. Production Deployment Checklist

1. [x] **Monaco Editor Integration**: Loaded with VS Code dark theme and fallbacks.
2. [x] **QRCode Engine**: Client-side QR generation (`QRCode.js`) for mutual connections.
3. [x] **Web Audio Synth**: Sound effects enabled for clicks, test case passes, and victory chimes.
4. [x] **Security & Sandboxing**: Container resource limits (2.0s CPU time, 256MB RAM limit, no egress network access).
5. [x] **Responsive Mobile UI**: Phone navigation bar & touch controls implemented.

---
*CodeBattle Documentation — Synchronized with build guide specifications.*
