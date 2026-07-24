# CodeBattle — Full Concept Document

> A real-time competitive coding platform where people compete in rooms across the top 10 most-used programming languages.

---

## Table of Contents

1. [Core Idea](#core-idea)
2. [Competition Formats](#competition-formats)
3. [Room System](#room-system)
4. [Freemium Model](#freemium-model)
5. [Connection System](#connection-system)
6. [Problem Publishing System](#problem-publishing-system)
7. [Problist System](#problist-system)
8. [Psychological & UX Features](#psychological--ux-features)
9. [Social System](#social-system)
10. [User Progression](#user-progression)
11. [Moderation & Trust Levels](#moderation--trust-levels)
12. [Automation](#automation)
13. [Missing Features to Add](#missing-features-to-add)
14. [Monetization](#monetization)

---

## Core Idea

A web application where people compete together in coding challenges across the **top 10 most-used programming languages**:

> Python, JavaScript, TypeScript, Java, C++, C#, Go, Rust, PHP, Swift/Kotlin

**Key differentiators:**
- No follower/following system — mutual QR/code-based connections only
- Unlimited players per room (paid) or up to 100 (free)
- User-published problems with public/private visibility
- Live real-time competition with spectator mode
- Cross-language battles on the same problem

---

## Competition Formats

| Format | Description |
|---|---|
| Speed Coding | Solve the same problem the fastest |
| Cross-Language Battle | Same problem, different languages — scored on correctness + performance |
| Code Golf | Fewest characters wins |
| Debugging Race | Fix broken code faster than opponents |
| Progressive Difficulty | Q1 easy → Q2 medium → Q3 hard in same room |

---

## Room System

### Room Creation Flow

```
Host creates room → gets unique_code + QR code
                 → shares code/QR with others
                 → others join via code, QR, or link
                 → host configures settings
                 → host starts when ready
```

### Room Settings (Host Controls)

- Language(s) allowed (one specific or all 10)
- Problem difficulty (easy / medium / hard)
- Time limit per problem
- Timer type: **Countdown** (pressure) or **Countup** (relaxed)
- Public room (discoverable) vs Private (code/QR only)
- Max players override (paid tier)

### Room Lifecycle

```
LOBBY → COUNTDOWN (5s) → ACTIVE → RESULTS → REPLAY
```

- **LOBBY:** Players join, host configures
- **COUNTDOWN:** 5-second auto-start sequence, room locks
- **ACTIVE:** All players coding live simultaneously
- **RESULTS:** Ranked leaderboard shown to all
- **REPLAY:** Watch how top finisher solved it step by step

### Scheduled Rooms (RSVP)

```
Host creates room for future date/time →
    Players RSVP via code/QR →
    Auto-reminder notification 10 min before →
    Room auto-opens at scheduled time
```

### Problem Order in Room

- **Sequential** — everyone does Q1 before Q2
- **Free-for-all** — pick any problem, finish most wins

### Scoring Formula

- Points per problem (harder = more points)
- Speed bonus per question
- Final rank = total points at end of room

---

## Freemium Model

| Feature | Free | Paid |
|---|---|---|
| Max players per room | 100 | Unlimited |
| Room history / replays | Last 5 | Full archive |
| Custom problems | No | Yes |
| Private leaderboard | No | Yes |
| Room branding | No | Yes (orgs/schools) |
| Concurrent rooms hosted | 1 | Many |
| Scheduled rooms | No | Yes |
| Tournament bracket | No | Yes |
| Interview mode | No | Yes |
| Org/team account | No | Yes |
| AI hints per problem | 1 | 3 |

---

## Connection System

**No follow/follower. Fully mutual.**

```
User A shares QR code or unique_code
    → User B scans or enters code
    → Both are now "Connected" (symmetric, no hierarchy)
```

- No follower count visible anywhere
- Feed shows what connections are doing (rooms they host, problems they publish)
- Think of it as **adding a contact**, not subscribing
- Connections can see your connections-only problems and rooms

---

## Problem Publishing System

### Visibility Options

```
Author publishes problem → sets visibility:
    ├── Public        → anyone can find, use, add to their room
    ├── Private       → only via unique_code / QR
    └── Connections   → visible only to connected users
```

### Problem Card Contains

- Title, description, difficulty tag
- Input/output examples
- Visible test cases (shown to solver)
- Hidden test cases (used for scoring)
- Language tags
- Author name, solve count, avg solve time
- Fork button (for public problems)

### Problem Validation (Automated)

- Must have minimum 3 test cases
- Author's solution must pass all own test cases before publishing
- Auto-sanitize HTML/XSS in description
- Auto-tag difficulty based on avg solve time after 50 solves
- Auto-flag if solve rate is 0% after 100 attempts (likely broken)

### Fork / Clone Problems

```
See a good public problem →
    ├── Fork it → edit test cases or description
    ├── Original author credited
    └── Forked version added to your problem list
```

### Problem Versioning

```
Author edits published problem →
    ├── Old version preserved for rooms that used it
    ├── New version becomes v2
    └── Rooms choose which version to load
```

### Embed & Share

```
Any public problem gets:
    ├── Shareable link → opens in solve mode
    ├── Embed widget → paste on any website
    └── OG image preview for social sharing (Twitter/LinkedIn)
```

---

## Problist System

A **Problist** is a curated collection of problems.

```
Problist
    ├── Created by you (from your problems + public ones)
    ├── Visibility: Public / Private (unique_code/QR)
    └── Usable as a room template when creating a room
```

### Use Cases

- "My JavaScript Interview Prep" → share with friend via QR
- Professor creates "Week 3 Assignment" → private code for students
- Creator builds "Ultimate Rust Challenge" → public room template

---

## Psychological & UX Features

### Reduce Anxiety During Competition

- **Warm-up mode** — 2-3 min easy problem before room starts, kills cold-start freeze
- **Anonymous mode** — compete with generated alias (e.g. "SilentFox"), not real name
- **Hide live score during solving** — shown only at end, prevents panic from seeing you're losing
- **"I'm stuck" hint button** — gives conceptual nudge, costs points, max 3 per problem
- **Focus mode** — one click hides all UI except problem + editor

### AI Hint System

```
User stuck → clicks "Hint"
    ├── AI gives conceptual nudge (not the answer)
    │       e.g. "Think about what data structure gives O(1) lookup"
    ├── Costs small points penalty
    ├── Max 3 hints per problem
    └── Hint quality rated by users after match
```

### Flow State Triggers

- **Progressive difficulty** in room (easy → medium → hard)
- **Live activity pulse** — "opponent is typing" indicator (not their code, just activity)
- **Timer style choice** — host picks countdown or countup
- **Post-match breakdown:**
  - Your approach vs fastest solver's approach (side by side)
  - Which test cases failed and why
  - Time spent per section
  - "Solve again" button — beat your own time

### Healthy Competition

- **Skill-based room tagging** — auto-tags based on who's in it
- **Personal best focus** — leaderboard shows rank AND your all-time best finish
- **No text chat during live round** — emoji reactions only (🔥 😅 👏)
- **"Well played" button** after match — peer recognition without likes/followers
- **Watch mode replay** — watch how top finisher solved it, step by step

### Retention & Habit Loops

- **Daily problem** — one free problem every day, earns streak badge (Duolingo model)
- **Weekly themed room** — auto-created public room ("Graph Week", "JS Only Friday")
- **Revenge room** — after losing, one-click rematch creates new room + challenges same players
- **Behavior-based badges:**
  - "First to Submit"
  - "Clean Code" (all test cases passed on first try)
  - "Comeback" (was last, finished top 3)
  - "Streak Master" (7-day solve streak)

### Explain Your Solution (Post-Match)

After solving, optionally write a short explanation of your approach. Others can rate it. Even a 5th-place finisher can have the best-rated explanation — reputation as a thinker, not just a fast typer.

---

## Social System

### User Profile / Portfolio Page

Public page at `yourapp.com/@username`:
- Languages, rank, total solves, badges
- Published problems and problists
- Match history
- Shareable — usable on resumes, LinkedIn, GitHub bio

### Search & Discovery

- Search problems by language, difficulty, tag, author
- Search public rooms to join (open lobby list)
- Search problists by topic
- Trending problems this week
- Recommended problems based on your weak spots

### Global & Language Leaderboards

- Global rank (all languages combined)
- Per-language rank ("Top 50 Python coders this month")
- Weekly reset leaderboard (fresh competition every week)
- All-time hall of fame

### Spectator Mode

- Watch any live public room as a spectator
- See live leaderboard and progress (not others' code)
- Good for virality — streamers, content creators

---

## User Progression

### Skill Tracker

- **Weak spot tracker** — "You consistently fail array problems in Python" based on history
- **Language-specific rank** — be the #1 Python competitor separately from JS rank
- Tracks: solve count, avg time, first-try success rate, hint usage

### XP & Ranks

```
Bronze → Silver → Gold → Platinum → Diamond → Master
```

- XP gained per solve (more for harder problems, speed bonus)
- Rank recalculates after every match
- Weekly leaderboard resets for fresh competition

### Badges

Awarded automatically based on behavior:
- First solve, clean run, comeback, streak, top finisher, well-played votes received, best explanation rated

---

## Moderation & Trust Levels

### Trust System

```
New User
    └── can: join rooms, solve problems, create private rooms

Verified User (email confirmed + 10 solves)
    └── can: publish problems, create public rooms

Trusted User (50+ solves + good standing)
    └── can: review flagged problems, approve new public problems

Moderator (appointed by admin)
    └── can: ban users, remove problems, see abuse logs

Admin (you)
    └── full access
```

### Community Moderation

- Any user can flag a problem (offensive, plagiarized, broken test cases)
- If 10+ users flag a problem → auto-hide pending review
- Trusted users can approve/reject flagged problems
- Community does the moderation work — scales for free

### Audit Logs

Every sensitive action logged with who did it and when:
- Problem deleted
- User banned
- Room force-closed
- Protects legally and helps debug abuse patterns

---

## Automation

### Room Lifecycle
- Auto countdown, auto-lock, auto-start timer, auto-end, auto-score, auto-save history

### Code Submission Pipeline
- Auto-send to sandbox, auto-run test cases, auto-score, auto-broadcast progress, auto-update leaderboard

### User Progression
- Auto-update XP, rank, streak, badges, weak spot tracker after every match

### Notifications
- Connection joins your room, someone uses your problem, daily problem ready, streak at risk, room starting soon, problem flagged

### Scheduled Jobs
- **Daily midnight:** pick daily problem, reset counts, check streaks, send reminders
- **Weekly Monday:** create themed public room, generate weekly leaderboard digest
- **Monthly:** archive old room data, recalculate global rankings

### Payments (Stripe Webhooks)
- payment_succeeded → auto-upgrade tier
- subscription_cancelled → auto-downgrade
- payment_failed → notify + 3-day grace period

### Cleanup
- Delete rooms stuck in lobby 2+ hours
- Clear expired Redis states
- Remove unverified accounts older than 7 days

---

## Missing Features to Add

### Must Have at Launch
| Feature | Why |
|---|---|
| Onboarding flow | Users leave without guidance |
| Practice / offline mode | Solve problems without competition pressure |
| Search & discovery | Public pool is useless without search |
| Legal pages | Terms, Privacy Policy, GDPR |
| Public profile page | Free marketing, resume use |

### Add Shortly After Launch
| Feature | Why |
|---|---|
| Scheduled rooms | Tournaments, classes, weekly events |
| AI hint system | Reduces rage-quit |
| Fork problems | Builds community problem quality |
| Global leaderboards | Retention and competition motivation |
| Feedback / changelog | Community trust and product direction |

### Monetization Unlocks (Paid Tier)
| Feature | Why |
|---|---|
| Interview mode | B2B — companies pay for hiring tool |
| Org/team accounts | B2B — bootcamps, universities, companies |
| Tournament bracket | Esports-style events |
| Analytics dashboard | Orgs want to track member performance |

### Interview Mode Detail
```
Special room type (paid):
    ├── 1 interviewer + 1 candidate
    ├── Interviewer adds problems live during session
    ├── Interviewer sees candidate's code in real-time (with permission)
    ├── Interviewer leaves private notes
    └── Session replay for hiring team
```

### Org / Team Accounts
```
Org account (paid):
    ├── Company/university name + logo
    ├── Manage members (add/remove)
    ├── Private problem bank for org only
    ├── Internal leaderboard
    ├── Analytics dashboard
    └── Branded room links (company.yourapp.com)
```

### Tournament Bracket (Paid)
```
Round 1 (16 players) → Round 2 (8) → Semi (4) → Final (2)
    ├── Auto-advance top N players per round
    ├── Auto-generate bracket visual
    └── Spectators watch any match
```

---

## Monetization Summary

**Who pays:**
- Companies — hiring challenges, internal hackathons
- Universities / bootcamps — competitive coding classes
- Content creators / streamers — host public tournaments
- Tournament organizers — esports-style coding events

**Revenue streams:**
1. Individual paid tier (unlimited rooms)
2. Org/team plan (B2B, highest revenue)
3. Interview mode add-on
4. Tournament hosting add-on

---

*Document version: 1.0 — based on full brainstorming session*
