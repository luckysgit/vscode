# CodeBattle Architecture v1

Status: proposed implementation baseline, 2026-09-15. This document describes the target system, not features already delivered. Earlier guides remain historical references. The first-release emphasis is pending product scope confirmation.

## Product boundary

Build a coding platform with shared problem, room and grading infrastructure for practice, competitions and teacher-led exams. Start with one complete flow: authenticated teacher creates a room with published problems, students join and save code, the teacher starts the session, submissions are graded by an isolated worker, and authorized users receive results.

Payments, connections, tournaments, AI hints, replay and webcam/screen recording follow the core release. Browser monitoring records reviewable signals; it cannot prove cheating or reliably detect or disable extensions. No application-defined participant limit means capacity depends on provisioned infrastructure, not unlimited capacity.

## Current implementation update

The running Python preview now has SQLite-backed guest and registered accounts, hashed passwords and server-managed cookie sessions. The root submission API and browser no longer manufacture successful grading. This is an incremental local implementation; the production architecture below remains a target. See the root README for current setup and limitations.

## Repository findings

| Existing area | Observed implementation | Treatment |
|---|---|---|
| `web/`, `src/modules/`, `server/` | Browser/local-memory prototype; Python auth now persists; legacy Node grading remains simulated | Preserve as reference; not an exam backend |
| `codebattle-mvp/frontend/` | Next.js client with room and dashboard pages | Reuse suitable UI after API contracts stabilize |
| `codebattle-mvp/backend/` | Express, Socket.IO, PostgreSQL, Redis and BullMQ prototype | Replace incomplete flows incrementally with authenticated modules |
| Existing SQL schemas | Mutable problems; weak submission identity and room relationships | Use new versioned migrations; do not apply incompatible changes to existing data silently |
| Documentation | Multiple incompatible stacks and readiness claims | This baseline and verified release checks supersede those claims |

Specific MVP defects include two submission listeners, client-selected problem IDs, socket IDs used as identities, first joiner becoming host, and persistence after result publication. These must be resolved before reuse in a real session.

## Architecture decisions

- TypeScript for new application code. Next.js web client, Express HTTP API, Socket.IO realtime gateway, and a separate BullMQ judge worker. API and gateway may share a process for development, but use the same authorization services.
- PostgreSQL is authoritative for identities, memberships, immutable problem versions, room lifecycle, drafts, submissions and audit records. Redis handles queue transport, presence and fanout; losing Redis must not erase accepted submissions or room deadlines.
- Use server-validated sessions backed by a standards-based identity provider. Application organization roles come from the database, never client claims or account registration fields. Select the provider during authentication implementation.
- Judge0 runs on a private execution network. Neither API nor gateway executes submitted source code. Worker credentials grant only the database and judge access it needs. Verify actual sandbox and network isolation before enabling public submissions.
- Pin supported dependencies and container versions when implementation begins; historical version numbers and `latest` tags are not a reproducible release specification.
- Local development uses the same persistence and queue semantics as deployment. Demo data and fake grading must be visibly identified and excluded from the authenticated application.

## Planned module boundaries

```text
apps/
  web/                    # Student editor and teacher dashboard
  api/                    # HTTP routing, auth and gateway composition
  realtime/               # Socket authentication, subscriptions and presence
  worker/                 # Outbox dispatch and isolated judging
packages/
  contracts/              # Validated request, response and event schemas
  domain/                 # Room, policy, scoring and permission rules
  database/               # Migrations and repositories
  config/                 # Validated environment settings
tests/
  unit/                   # Timing, scoring and policy rules
  integration/            # PostgreSQL, queue and service behavior
  e2e/                    # Teacher/student browser journeys
  security/               # Tenant, role and hidden-test boundaries
  load/                   # Connection and submission bursts
  resilience/             # Restart, disconnect and dependency failures
infra/                    # Local services and deployment configuration
```

Create directories alongside working code rather than placeholder-only modules. Domain modules cover permissions, organizations, problem versioning, rooms, submissions, draft autosave, exam monitoring and audit.

## Data invariants

1. `organizations`, `users` and `organization_memberships` establish tenant identity and roles. All tenant-owned records contain `organization_id`. Composite foreign keys prevent cross-tenant room/problem/submission references. Every repository query includes tenant scope; database policies provide additional defense.
2. `problems` identify a logical problem; `problem_versions` hold immutable published content and execution limits. `test_cases` reference a version. `room_problems` pins a published version. Editing creates another version; referenced versions cannot be deleted or changed.
3. `rooms` hold creator identity, mode, frozen policies, lifecycle timestamps and capacity. `room_memberships` identify durable participants independently of sockets. A join code is an invitation locator, not authorization for reading another participant's data or starting a room.
4. `submission_drafts` use `(organization_id, room_id, user_id, problem_version_id, language)` as their key and a monotonically increasing revision. Updates require the expected revision; conflicts return the server revision without destroying either draft.
5. `submissions` include source, language, version, participant, server acceptance time, status and request ID. A unique `(organization_id, user_id, request_id)` constraint deduplicates retries. Reusing a key with a different payload returns a conflict.
6. Submission admission and an `outbox_events` record commit in one database transaction. A dispatcher retries queue delivery using submission ID as job identity. Workers use durable state transitions so redelivery cannot score a submission twice.
7. `exam_security_events` contain authenticated participant identity, room, event type, server receipt time, optional client observation time, session ID and bounded metadata. Event IDs deduplicate replay. These records are evidence signals, not verdicts.
8. `audit_events` record actor, tenant, action, resource and server time. Application roles can append but cannot update or delete audit records. Administrative maintenance uses separate controlled credentials and logged procedures.

## Room policies and timing

| Policy | Practice | Competition | Exam |
|---|---|---|---|
| Attempts | Unlimited by default | Configurable | Configurable |
| Leaderboard | Optional | Enabled by default | Hidden by default |
| Results | Immediate | Immediate by default | Teacher released |
| Browser signals | Disabled | Opt-in room policy | Disclosed before joining |
| AI hints | Future feature | Future configurable feature | Disabled |

Policies are validated and frozen on start. Lifecycle: `LOBBY → COUNTDOWN → ACTIVE → ENDED`. Start is an atomic transition restricted to the creator or an authorized teacher. Store `starts_at` and `ends_at`; derive timing from server time even after restart. The admission transaction accepts only when `starts_at <= server_now < ends_at`. Queued work accepted on time may finish after the deadline. No implicit grace period; any accommodation must be an explicit authorized policy change recorded in audit.

## Submission and result contract

1. Authenticate and authorize membership, tenant, room state, pinned problem and allowed language. Validate source size and request ID.
2. Return an existing submission for a matching retry before applying new-attempt limits, including retries after the deadline.
3. Serialize admission per participant to enforce attempt and outstanding-submission limits. Reject unavailable capacity with a retryable error; never acknowledge work that was not persisted.
4. Commit submission and outbox, then return `202` with the durable submission ID. A worker loads hidden cases using the pinned version.
5. Apply bounded execution, worker leases and retry budgets. Infrastructure failures are distinct from wrong answers and do not consume additional attempts. Exhausted jobs remain discoverable for operator recovery.
6. Persist the final result and scoring before publishing a notification. Repeated completion is idempotent. Best valid score is retained; a later failed attempt cannot erase it.
7. Participants can retrieve only their own submissions. Hidden cases expose aggregate counts only, never their input, expected output, actual output, stderr or judge diagnostics. Exam result visibility applies equally to HTTP and socket messages.

Initial configurable admission limits: one outstanding submission per participant, 64 KiB source, and a bounded global queue depth. Set actual queue depth and worker concurrency from measured service capacity before deployment.

## Realtime and recovery

Authenticate the handshake, validate allowed origins, and recheck permissions for every event. Room channels are joined only after membership authorization. Teacher monitoring uses a separate authorized channel; student code and security events are never broadcast to opponents.

Events carry an ID and room revision. On reconnect, fetch an authoritative snapshot and reconcile revisions instead of relying on missed broadcasts. Presence is a Redis lease; multiple sockets do not create multiple students. Expiry indicates disconnection, not automatic disqualification.

Save editor changes locally with account/room/problem/language scoping, then debounce server autosave. Show pending/saved/offline/conflict states. Reconnect uploads preserve revision checks. Submission retries preserve the original request ID; editing and submitting new code creates a new ID. Signing out removes sensitive local drafts from the active browser account.

## Privacy and operations

Display monitoring policy before exam entry and define institution-approved retention and access rules before real student data is collected. Initial monitoring is limited to visibility/focus, fullscreen and clipboard event metadata, without clipboard contents, camera or screen recording. Teachers review context; the application does not automatically accuse or fail students.

Record queue age, admission rejection rate, judge duration, failures, socket reconnect rate and database health without source code, hidden tests or session tokens in logs. Production requires TLS, secret management, session revocation, verified identity, privileged-account MFA, backups and a tested restore process.

## Release sequence and evidence

1. Foundation: migrations, tenant/role enforcement, version publishing, policy contracts and automated invariant tests.
2. Session flow: authenticated room creation/join/start/end, server deadlines and reconnect snapshots.
3. Editor and grading: local/server drafts, transactional submission admission, outbox, worker, hidden-test redaction and result retrieval.
4. Teacher experience: roster, presence, per-problem progress, disclosed monitoring signals and controlled release/export.
5. Hardening: dependency review, sandbox evaluation, privacy configuration, backup restore, browser/accessibility coverage and load/failure tests.

First load milestone is 1,000 concurrent users; 5,000 and 10,000 are later measured targets. No capacity claim is validated by this document. Test synchronized submission bursts as well as steady traffic. Real exam release requires evidence for tenant isolation, version integrity, deadline enforcement, duplicate prevention, draft recovery, worker/Redis/database failures, hidden-test secrecy, monitoring authorization and restore drills.
