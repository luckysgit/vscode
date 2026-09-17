# Implementation audit — CodeBattle

> Remediation update (2026-09-16): [P0 batch 1](P0_BATCH_1.md) records subsequent fixes and launcher containment. The audit findings below describe the pre-remediation snapshot.

**Audit date:** 2026-09-16 (Asia/Kolkata). **Scope:** Phase 1 only; inspect and document, no application implementation or UI redesign. Assessment covers the existing working tree, including uncommitted work. This is not a production certification.

## Executive assessment

**Not production ready.** The local Python account flow is the only persisted, authenticated customer workflow with automated coverage. Light/dark styling and local navigation are functional UI utilities. Core coding, shared rooms, scoring, exam, organization and payment workflows are incomplete, simulated, or absent. Existing frontend disclosures are helpful but do not isolate demo behavior from production.

Three alternative servers must not be mistaken for a single integrated application. Preserve working account and UI code; document the runtime decision before migrating anything. Stop at the audit in this batch, as explicitly requested.

## Scope and evidence method

- Enumerated all project files recursively, including dotfiles, source, schemas, setup/container files, tests, documentation and the ZIP archive. No applicable AGENTS.md found in the parent search.
- Read runtime sources/configurations and all test files; searched documentation for stack/schema/security/feature claims and compared those claims with actual code. Documents are design references, not proof of implementation.
- Parsed every static interactive HTML element; separately inspected generated controls and all React pages/handlers. See the exhaustive control register below and [feature matrix](FEATURE_MATRIX.md).
- Searched TODO/FIXME/mock/demo/placeholder/hardcoding, timeouts, alerts, console logging, localStorage, innerHTML, route/event bindings, secrets and missing persistence. Benign delays (toast expiry/countdown/clipboard feedback) are distinguished from fake matchmaking/judging.
- Compared all 22 ZIP members byte-for-byte against `codebattle-mvp/`: identical. No need to execute/extract a second copy. `setup.sh` is an additional unpacked file.
- Excluded account DB contents, runtime caches and unrelated parent-repository data from content/secret scans. Did not print live credentials or customer records. No destructive tests, external scans, infrastructure launch, dependency installs or deployment.

## Architecture actually present

| Path | Runtime/data flow | Assessment |
| --- | --- | --- |
| `web/` + `src/modules/` + `server/server.py` | Static HTML/JS → auth/submit fetch → Python HTTP → SQLite accounts; other UI modules → localStorage or constants | Current local preview; no websocket/Redis/BullMQ integration |
| `server/server.js` + `server/package.json` | Alternate built-in Node HTTP server → process memory, simulated judging | `npm start` starts this incompatible legacy path; it lacks Python account APIs and correct `/src/` serving |
| `codebattle-mvp/frontend/` + `backend/` | Next 14/React18 → Express/Socket.IO → PostgreSQL/Redis/BullMQ → Judge0 adapter | Incomplete separate MVP, not used by current browser |
| `schema.sql` | Postgres/Clerk-shaped account and competition schema | Not loaded by Python; differs from MVP schema |
| `server/auth.py` | SQLite accounts/sessions/auth_limits created on startup | Actual account persistence; no domain data or migrations |
| `lib/` | Problem seed bank and XP helper exports | Not imported by active app/server; not working reward infrastructure |
| `doc/` | Next14/16, Clerk/local auth, Express/Python, Judge0/Piston alternatives | Conflicting target claims; root README and architecture-v1 distinguish preview from target |
| `codebattle-mvp.zip` | Duplicate MVP source | Carries same defects as unpacked MVP |

### Contradictions requiring a future decision

1. Target TypeScript/PostgreSQL architecture versus current Python/SQLite release. This audit does not authorize a rewrite or select a migration silently.
2. Three schemas/identity systems: SQLite IDs; root Postgres UUID/Clerk fields; MVP socket IDs persisted as text. No mapping/migration exists.
3. Runtime frontend is vanilla JS, not Next.js. Rebuilding only the Next app will not fix the UI currently served at port 5000.
4. Python submit correctly fails with 503; legacy Node invents ACCEPTED; MVP attempts Judge0. No common submission contract.
5. Room codes/routes differ (`CB-####`, six characters, `/join?code=`, `/room/[code]`, `/rooms/:code`). Root QR links point to a hardcoded external hostname and have no corresponding local entry handler.
6. Root current accounts do not use Clerk/Supabase/Stripe; those integrations described in guides do not exist in runtime code. Piston is documentation-only.
7. Root version metadata is mutable; canonical architecture promises immutable published snapshots. Root guide production checkmarks exceed tested behavior.
8. Both themes are already implemented. Preserve them and the GitHub-inspired design while fixing functionality.

## Classification

`WORKING`: observed narrow function works, not a production sign-off. `PARTIAL`: a chain exists but has material missing links. `BROKEN`: reachable intended action cannot complete. `MOCK`: simulated/hardcoded/browser-only domain outcome presented by UI. `SECURITY_RISK`: identified unsafe boundary. `NOT_IMPLEMENTED`: no runtime implementation found. A full product feature is not DONE just because its modal opens or an API returns 200. N/A means the control is genuinely local, not that a missing backend is acceptable.

## Implementation table

| Feature | Page/component | Button/action | Frontend implemented? | Backend implemented? | Database implemented? | Authorization implemented? | Validation implemented? | Loading state? | Error state? | Tests? | Security risk | Status | Required fix |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Guest/signup/login/logout/restore | web/app.js; AuthService | Account forms/buttons | Yes | Yes, Python | SQLite | Own session; no roles | Auth fields/JSON | Yes, buttons | Yes; transport failures limited | 11 baseline tests + Chrome flow | Hardening/recovery gaps | WORKING (local account core) | CB-016/017/019; preserve core |
| Theme/navigation | web/theme.js; web/app.js | Toggle/tabs | Yes | N/A | Theme local preference | N/A | Theme allowlist | N/A | Storage fallback | Browser checks; theme checks not committed | Low | WORKING (UI only) | Preserve; extend browser coverage |
| Room create/custom problem | form-create-room; RoomService | Launch | Local only | Separate memory endpoint unused | No domain DB | Client host | HTML required title only | No | Storage exceptions console only | No | HTML injection/data loss | SECURITY_RISK | CB-001/008/010 |
| Room join/start/leave | web/app.js | Join/start/leave | View transitions | None connected | No | No host/membership checks | Unknown ID falls back to first | No | No | No | Authority bypass | MOCK | CB-010/013 |
| Room invite/QR | web/app.js | QR | Renders external URL | Missing local invite resolution | No | No | No | No | Missing CDN silently ignored | No | Misleading invite | BROKEN | CB-010/022 |
| Problems browse/solo | ProblemService | Solve solo | Local bank | Mock GET unused | localStorage | No owner boundary | No domain schema | No | Fallback first problem | Navigation only | Hidden seed tests public | SECURITY_RISK | CB-002/011/012 |
| Create/edit/publish problems | ProblemService; problem page | Create problem | Create button unbound; room form creates local | None current | No immutable versions | No | No | No | No | No | XSS/history mutation | BROKEN | CB-001/011/015 |
| Run/submit | SubmissionService | Run/Submit | Fetches actual editor code | Explicit 503 | None | Session required | Nonempty code + body cap | Yes | Explicit error | 503 rejection only | No sandbox enabled | BROKEN | CB-005/006/007/012 |
| Editor recovery/language | Monaco/editor-lang-select | Edit/change language | Editor partial; select not bound to Monaco | None | No drafts | None | No | CDN-dependent | No fallback | No editor tests | Work loss | PARTIAL | CB-008/012/022 |
| History/results/leaderboard | Dashboard/LeaderboardService | History/filter/results | Seed rows/static results | Unused mock lists | History local only | Not user-scoped | Filter unbound | No | No | No | Misleading outcomes | MOCK | CB-007/014/015/020 |
| Daily/matchmaking/interview | web/app.js | Start | Local p1/fake opponent | None | No | No | Selections ignored | Fake wait | No | No | False matching claim | MOCK | CB-015 |
| Connections/challenge | web/app.js | Add/QR/challenge | Fake row; challenge unbound | Mock lookup unused | No connection written | No mutual consent | Trim only | No | Success alert | No | DOM XSS | SECURITY_RISK | CB-001/015 |
| Profile/settings | ProfileService; settings form | Save | Identity real; save unavailable | No update | Accounts read only | Own me only | Not implemented | No | Honest unavailable alert | Identity only | No persistence | PARTIAL | CB-020 |
| Admin/org | AdminService/OrgService; admin view | Approve/remove | Hidden admin mock; org service only | Python admin 403 | No | Deny-all, no roles | No | No | No | 403 test | UI badge not authorization | MOCK | CB-018/021 |
| Payments/exam/email | No runtime modules | Not present | No | No | No | No | No | No | No | No | Must not claim implemented | NOT_IMPLEMENTED | CB-021 |
| MVP room API/sockets | backend/src/server.js | Create/join/start/activity | Separate Next client | Partial | PG+Redis nontransactional | No auth; socket host only | No schemas | Create spinner | Generic errors; client misses socket error | No | Unauthorized controls | SECURITY_RISK | CB-004/010/013/014 |
| MVP submit/worker | MVP room page/backend | Submit | Omits sourceCode | Two listeners + inline worker | Only final insert | No membership/pinned problem | No bounds/deadline | Pending rendered wrong | No terminal infrastructure handling | No | Forged score/lost result | SECURITY_RISK | CB-005/006/007/012 |
| Operations/release | setup.sh/Compose/tests | Start/build/deploy | Conflicting launch paths | Health not readiness | No backups/migrations | Unsafe defaults | No startup schema | N/A | Console logs | No load/failure tests | Unverified deployment | PARTIAL | CB-009/023/024 |

## Prioritized implementation plan — proposed, not executed

P0 = security/data-loss/release blocker; P1 = broken core functionality; P2 = important missing capability; P3 = polish/optimization. Priorities reflect the requested future customer release; legacy-path findings are not claims that those paths are currently exposed.

| ID | Severity | Affected files | Problem | Security impact | Proposed fix | Required tests |
| --- | --- | --- | --- | --- | --- | --- |
| CB-001 | P0 | web/app.js:356,508,632; src/modules/rooms/room.service.js; src/modules/problems/problem.service.js | User-controlled room/problem titles and connection codes enter innerHTML. Local storage persists room/problem injection. | Same-origin script execution; attacker reach currently requires entering/importing data in a victim browser; future shared data would amplify it. | Build nodes with textContent and validated attributes; audit every dynamic sink; add a compatible CSP. | Title, description, code and stored-payload injection; safe rendering after refresh; legitimate text preserved. |
| CB-002 | P0 | src/modules/problems/problem.service.js:25; server/server.js:93; lib/problemBank.js | Hidden seed input/expected output ships in public client source; legacy Node returns complete testCases. | Hidden-case secrecy is already absent in preview; disqualifies competitive grading. | Keep public examples separate; load hidden cases only in worker; redact every participant result DTO. | Inspect network/source/results for hidden inputs, outputs and IDs; author-only test editing. |
| CB-003 | P0 | server/server.js:169,208; server/package.json | Legacy Node static serving joins raw paths without containment; npm start launches this unauthenticated alternative with fake grading. | Potential file disclosure if raw traversal reaches the legacy server; no auth on writes; no request body cap. Not the current Python path. | Quarantine legacy startup behind explicit demo mode or secure and align it; enforce canonical static roots and body limits. | Raw/encoded/symlink traversal, unknown API 404, oversized JSON, unauthenticated writes, startup-mode checks. |
| CB-004 | P0 | codebattle-mvp/backend/src/server.js:40,80,138,201,237 | MVP API and sockets have no account authentication; first joiner becomes host; no membership check for submission/activity. | Unauthorized room control, activity injection, judge resource abuse; socket ID is not durable user identity. | Session-authenticated gateway and HTTP middleware; server-derived identity, validated payloads and per-event membership/permissions. | Unauthenticated sockets; student start/end; cross-room submission/activity; revoked session; malformed/null events. |
| CB-005 | P0 | codebattle-mvp/backend/src/server.js:251,318 | Client-selected problem is not bound to room; zero test rows cause 0 == 0 acceptance. | Forged passing score without executing code. Static confirmed logic, runtime not exercised. | Validate pinned problem version and nonempty published tests; fail closed on unavailable/invalid problem. | Unknown/other-room/zero-test problem rejected; client score/XP ignored. |
| CB-006 | P0 | codebattle-mvp/docker-compose.yml; backend/src/services/judge0.js; backend/Dockerfile | Judge published on host port, empty auth key, latest image; only CPU/memory request limits, no HTTP timeout/output cap or verified sandbox controls. | Unsafe to enable untrusted public execution; container configuration is not sandbox-escape evidence. | Private authenticated execution network, pinned vetted image, separate bounded worker, explicit wall/PID/output/source/stdin/network/filesystem controls. | Network/file/env isolation, fork/memory/output bombs in isolated infrastructure; timeout and judge failure; never run hostile code in app. |
| CB-007 | P0 | codebattle-mvp/backend/src/server.js:255,279,322,342,353 | Queue accepts before pending DB record; score and broadcast precede persistence; no idempotency/outbox/lease/retry policy. | Duplicate execution, lost acknowledged submissions and inconsistent published scores on failure. | Transactional admission plus outbox; stable request/job IDs and payload digest; durable result finalization before fanout; retry/dead-letter policies. | Double click/retry/race executes logically once; crash at every boundary; queue/DB outages; replayed completion. |
| CB-008 | P0 | web/app.js:530; src/modules/* browser stores; codebattle-mvp/frontend/app/room/[code]/page.tsx | Editor has no local/server draft save; account switching clears editor; room/problem/history storage keys are shared across accounts. | Lost student work on refresh/crash/switch; local data appears under another account. | Account-scoped local drafts and authenticated revision-controlled server drafts; explicit recovery/conflict UX. | Refresh/offline/reconnect; stale revision; account A/B isolation; no automatic submit. |
| CB-009 | P0 | server/server.py; server/server.js; codebattle-mvp/backend/src/server.js; docker-compose.yml | No fail-closed staging/production profile; demo state is always enabled; no readiness checks for required services. | Accidental deployment of mock or insecure paths; public readiness cannot be claimed. | Explicit environments and separate demo seed opt-in; production startup validation and readiness gates. | Production rejects missing auth/DB/queue/judge settings; never seeds mocks or falls back on outage. |
| CB-010 | P1 | web/app.js:254,347,381,406; src/modules/rooms/room.service.js; server/server.py:221 | Root room UI never calls room API; local create/join/start/leave do not create shared membership or lifecycle. | No authoritative ownership, capacity or reliable invite; room state lost/shared incorrectly. | Keep UI; implement durable room CRUD/membership and lifecycle service with server-derived host, unique code, transactions and authorization. | Two browsers create/join/leave; duplicate/capacity/missing/private room; host-only state transitions. |
| CB-011 | P1 | schema.sql; codebattle-mvp/database/schema.sql; src/modules/problems/problem.service.js:100 | Version number and commit messages overwrite current content; rooms reference mutable problems. | Historical questions/results can change; schemas have no tenant or immutable version boundary. | Versioned migrations for immutable published snapshots/test cases and pinned room versions; ownership and tenant FK constraints. | V1 room unchanged after V2; edits/deletes forbidden on referenced versions; concurrent publish; cross-tenant FK/permission rejection. |
| CB-012 | P1 | web/app.js:406,475,530; src/modules/submissions/submission.service.js; MVP frontend room page:151 | Root grading deliberately returns 503; language selector does not change Monaco; MVP submit omits sourceCode and pending is shown as wrong answer. | Core coding journey is broken; selecting a language can misrepresent editor language. | Connect actual editor source/language to validated async submission API after P0 execution controls; public run/hidden submit distinction and result polling/realtime. | Exact source delivered; language change; empty/large code; pending/error/accepted UI; explicit retry. |
| CB-013 | P1 | web/app.js:475; codebattle-mvp/backend/src/server.js:138,172,192,237 | Root timer is fixed text; MVP ends via process timeout and status only; start read/write is non-atomic. | Late submissions, duplicate starts, restarted rooms stuck active; queue delay affects score. | Persist starts_at/ends_at and atomic transitions; admission uses server time; scoring based on accepted time; restart reconciliation. | Before/exactly-at/after cutoff; modified client clock; concurrent start; restart near end; queued-on-time results. |
| CB-014 | P1 | codebattle-mvp/backend/src/server.js:80,224,322; frontend/app/room/[code]/page.tsx | Reconnect does not rejoin on connect or rehydrate problem/time; disconnect deletes player; no Redis Socket.IO adapter; later failure overwrites best score. | Identity/score loss and inconsistent multi-instance results. | Durable membership; presence leases; reconnect snapshots/revisions; shared adapter; atomic best-score and explicit tie-break policy. | Disconnect/rejoin/multiple tabs; WS restart; late completion; equal scores; success followed by wrong answer. |
| CB-015 | P1 | web/index.html; web/app.js:590,619,660,674; src/modules/{admin,leaderboard,profile,organisations}/*.js | Unwired create-problem/problist/challenge/moderation/filter controls; simulated matching and connections; static daily/result/admin data. | False success and inconsistent customer expectations; alerts are not persistence. | Make a feature flag/inventory-driven batch for each action; connect API or clearly unavailable states until complete; no silent fake fallback. | Every control intentional; submitted selections honored; refresh persists real actions; no success on failure. |
| CB-016 | P1 | server/server.py:113,175,246; server/auth.py; src/modules/auth/auth.service.js | Validation limited to auth; room fields unbounded semantically; non-auth writes unthrottled; unexpected DB exceptions lack structured JSON; health ignores dependencies. | Availability/error leakage risks; shared-IP auth limiter causes lockout/DoS; sessions may remain visually stale. | Central validators/errors, per-operation/user/IP limits and timeouts; bounded server concurrency; auth-expiry handling; readiness and request IDs. | Wrong types/enums/lengths; slow requests; DB unavailable; limiter boundaries/NAT; non-JSON errors; expired sessions. |
| CB-017 | P1 | server/server.py:91; web/index.html; .gitignore; codebattle-mvp/.env.example | No CSP/Permissions-Policy/HSTS production handling; CDN scripts lack integrity; .env variants rely on parent-repository ignore rules rather than project-local rules. | XSS impact, supply-chain exposure and accidental secret commit. | Restrictive tested CSP/security headers, self-hosted or integrity-pinned assets; env variant exclusions with template exception; secret scanning. | Header assertions in HTTPS deployment; editor/QR/CSP compatibility; ignored secret variants; no secrets in bundles/logs. |
| CB-018 | P1 | schema.sql; codebattle-mvp/database/schema.sql; server/auth.py | No migrations/RLS/RBAC/tenant schema; nullable relationship columns; missing lookup indexes and account-state checks. | Future data integrity/authorization gaps; no institutional isolation. | Migration baseline with NOT NULL/CHECK/FK/unique/index constraints; tenant-scoped permission services; DB roles/RLS where deployed. | Migration/rollback/restore; null/orphan/duplicate/state constraints; roles and cross-tenant negative cases. |
| CB-019 | P2 | server/auth.py; web/index.html; src/modules/auth/auth.service.js | No password recovery/change, email verification, MFA, session list/revoke-all or true account switcher. | Account recovery and privileged-account security missing; email ownership unverified. | Implement expiring single-use recovery/verification, password change/revocation, privileged MFA and explicit session controls. | Replay/expiry/guessing; mail failure; password-change invalidation; account enumeration policy. |
| CB-020 | P2 | web/app.js:571,674; src/modules/profile/profile.service.js; lib/xp.js | Preferences do not save; avatar absent; XP/badges/streaks/history not backed by grading. | Misleading stats and duplicate reward risk when grading is introduced. | Profile endpoint; deterministic server rewards and ledger; safe avatar upload if required. | Own-profile only; validated changes; duplicate reward; streak timezone; refresh. |
| CB-021 | P2 | No runtime exam, organization, payment or audit module; org mock only | Exam/teacher telemetry, institutional roles, immutable audit, payments and delivered notifications not implemented. | Requirements unmet; no evidence trail, tenant isolation or verified payment state. | Separate incremental feature batches after core; no invasive recording; provider signatures and idempotent payment processing. | Teacher/student/tenant authorization; telemetry consent/rate limits; audit append-only; webhook replay/signature/failure. |
| CB-022 | P2 | web/index.html; web/app.js; frontend/app/room/[code]/page.tsx | Many labels lack for/id; only auth dialogs have focus trap; editor CDN failure has no recovery; mobile nav hidden; clipboard errors unhandled in MVP. | Keyboard/assistive-tech and network-failure usability gaps. | Label all fields; dialog/menu focus restore; live-region statuses; local editor fallback; browser compatibility checks. | Keyboard-only, screen reader, 320px/zoom, blocked CDN, clipboard denial, Chrome/Firefox/Edge/Safari. |
| CB-023 | P1 | All package.json; codebattle-mvp/setup.sh; Dockerfile; tests/ | No lockfiles or CI, unsupported setup instructions point to missing server-local.js; no lint/typecheck/test pipeline outside small auth suite. | Unreproducible build/dependency exposure and untested regressions. | Pin supported runtime/dependencies, commit lockfiles; canonical scripts and CI gates; scanner/SBOM and isolated integration environments. | Clean install/build/lint/typecheck; dependency audit; bootstrap on supported OS; full core E2E. |
| CB-024 | P2 | codebattle-mvp/backend/src/server.js; server/server.py; no monitoring/load scripts | No meaningful queue/DB/judge metrics, backup restore, load/chaos suite, graceful shutdown or capacity evidence. | No supportable availability/capacity claim or recovery evidence. | Structured redacted logging, traces/metrics, backups, drain/restart procedures and staged 100/1000/5000/10000 load harness. | Burst/soak; judge/Redis/DB failure; worker kill/replay; restore drill; latency/queue-age/failure thresholds. |
| CB-025 | P3 | web/index.css; web/github.css; web/index.html; frontend room page | Layered styling overrides, inline styles, placeholder copy and loose TypeScript any/unused imports remain. | Maintenance cost; not a reason to redesign the working UI. | After core, consolidate styles/contracts, remove stale copy, optimize assets and measure rendering cost. | Visual regression in both themes; keyboard/mobile; strict typecheck without suppressions. |

### Suggested batches after the audit

1. **Contain immediate P0 risks:** CB-001/002/003/009; safe DOM rendering, hidden-case boundaries, explicit runtime/demo separation. Keep grading unavailable until the execution boundary is verified. Preserve current account/UI behavior.
2. **Protect work and identity:** CB-008 and CB-004; durable participant identity, authorization and drafts. Choose/document the runtime integration here before database migrations.
3. **Repair grading integrity:** CB-005/006/007 with CB-011/012; immutable versions, safe queue admission, worker isolation, bounded execution and durable results.
4. **Complete room lifecycle:** CB-010/013/014; multi-browser membership, host controls, authoritative deadline and reconnect.
5. **Replace remaining mock actions:** CB-015/016/018/020; one feature chain per batch, explicit failure UX.
6. **Institutional/release features:** CB-017/019/021/022/023/024; separate exam, organization, payment, observability and performance gates. Finish CB-025 after correctness.

No fixes in these batches were applied in Phase 1.

## API and event audit

### Current Python routes

All POSTs enforce same-origin when Origin exists, reject `Sec-Fetch-Site: cross-site`, require JSON and cap the request at 65,536 bytes. After auth-route handling, POSTs require a session (guests included). This does not supply endpoint-specific validation or permissions.

| Method/path (aliases grouped) | Actual behavior | Auth/authorization and gap |
| --- | --- | --- |
| GET /api/auth/me, /auth/me | Returns current account or null | Session token hash/expiry verified |
| POST /api/auth/{guest,register,login,logout}, /auth/... | Persistent account/session flows | guest/register/login share 30 attempts/IP/15min; logout not rate limited |
| GET /api/health, /health | Always ok; uptime_sec is process CPU time | Public; no DB/queue/judge readiness |
| GET /api/rooms, /rooms | All process-memory rooms | Public; no visibility/member policy |
| GET /rooms/:id-or-code | Lookup or first room fallback | Public; /api/rooms/:code not implemented |
| GET /api/daily, /daily | First demo problem, fixed streak/bonus | Public; not date/user-derived |
| GET /api/problems, /problems; /problems/:id | Memory list; invalid detail ID falls back to first | Public; /api/problems/:id absent |
| GET /api/problists, /problists | Static lists | Public |
| GET /api/connections, /connections | Seed connections for a fixed identity | Public; no current-user scope |
| GET /users/:name, /api/users/:name | Seed user including email; invalid name returns first | Public; not registered-account profile API |
| GET /api/profile/weakspots, /profile/weakspots | First seed user weakspots | Public; not current user |
| GET /api/admin, /admin | 403 deny-all | Safe refusal; no admin feature |
| GET /leaderboard* | Seed users sorted by fixed XP, includes emails | Public; /api/leaderboard absent |
| POST /api/submit, /submissions | 503 explicitly not configured | Requires session; no execution |
| POST /api/rooms, /rooms | Appends memory record; host from session | No detailed schema/rate/capacity; UI does not use it |
| POST /api/connections/request, /connections/request | Seed lookup + success, no write | Requires session; no invitation or consent |
| GET/HEAD static assets; OPTIONS | Contained web/src roots; HEAD inherited; OPTIONS 204 | No directory listing; no CSP/Permissions-Policy; unknown API generally HTML 404 |

### Alternate Node routes

`server/server.js`: GET `/api/health`, `/api/rooms`, `/api/problems`, `/api/leaderboard`; POST `/api/rooms`, `/api/problems`, `/api/submit`, `/api/connections`; wildcard OPTIONS. All lack authentication and domain validation; the body buffer is unbounded; invalid JSON becomes `{}`. `/api/submit` invents success after 500 ms. Problem GET includes hidden cases. Unknown API/static requests fall back to index HTML with 200. No account endpoints, websocket server or working `/src/` mount. Raw-path containment is absent and requires a negative runtime regression test before any reuse.

### MVP HTTP and websocket contracts

MVP HTTP: GET `/api/health` (always ok), POST `/api/rooms` (random DB problem, DB then Redis), GET `/api/rooms/:code` (parameterized lookup). All public with permissive CORS. No user, problems, drafts, results or auth REST endpoints.

| Event/direction | Implementation and defect |
| --- | --- |
| room:join client→server | Code/alias only, no auth/schema; first member becomes host; no cap, expiry/visibility policy, immutable user membership or active-room recovery |
| room:start client→server | Socket host check and lobby read then Redis write; race-prone; absent durable starts_at/ends_at |
| room:activity client→server | No room membership/rate/payload validation; malformed input can reject outside catch |
| submission:submit client→server | Two listeners; active-status-only gate; arbitrary problem; source missing from supplied UI; no logical request deduplication |
| disconnect server lifecycle | Deletes current player; previous rooms may retain stale membership when socket joined multiple rooms; no durable reconnect |
| room:state, room:player_joined/left server→client | Snapshot has problem:null and no timeLeft; countdown snapshot clears players; no revision/version |
| room:countdown, room:started server→client | 5s in-process countdown; fixed 300s active interval; process restart loses timeout |
| room:activity_pulse server→client | Visual pulse only; authorized fanout absent |
| submission:result, room:leaderboard server→client | Published before final DB insert; pending passed:false becomes Wrong Answer; room score may decrease on later failure |
| room:ended server→client | Automatic helper only; frontend stores results but renders leaderboard state; emits before room DB update |
| error server→client | Generic messages emitted, but client has no error/connect_error handler |
| room:leave/end/settings/kick, exam:security_event | No handlers. Documented typing_pulse and submit_result names differ from actual activity/submission names. |

## Database, queue and reliability review

- **SQLite:** parameterized SQL; session FK enabled on each connection; username/email unique and case-insensitive; salted password hash and token hash; explicit transactions and guest-upgrade predicate. Missing schema migrations, guest flag CHECK, registered-account email/hash CHECK, expires_at index, retention/cleanup of abandoned guests, roles, audit and domain tables. Hash parameters are embedded in code rather than versioned in password records. Duplicate guest-name collision is not retried. Login sessions expire absolutely after 7 days; no refresh/revoke-all/device management.
- **Root Postgres SQL:** useful PK/FK/unique/check declarations, ordered connection pair constraint and room_problems PK, but many FK/status fields remain nullable; no nonnegative XP/capacity/duration constraints, version snapshots, idempotency, memberships, drafts, tenants, audit, indexes for common FK lookups or RLS. Referenced problem deletion can delete historical submissions/test cases. PostgreSQL deployment not running/validated in this audit.
- **MVP SQL:** room/submission user IDs are unrelated text; submissions omit problem/version/language and lack room/user FKs. Room schema lacks host/members/start/end-deadline data. Countdown is not an allowed persisted status (currently only Redis uses it). Mutable test/problem rows and no tenant columns.
- **Redis:** root app does not use it. MVP uses hashes/sets/sorted sets and room-key TTL only; player/leaderboard keys can outlive the room. `redis.options` reused for queue/worker; no dedicated tested worker connection configuration, no maxRetriesPerRequest:null setting, no explicit persistence/eviction policy, adapter or recovery. Worker connection compatibility needs runtime validation once Node/dependencies are available.
- **Queue:** no attempts/backoff/jobId/per-user concurrency/queue depth budget, durable pending admission/outbox, dead-letter handling or queue-age metrics. Source and hidden tests are embedded in job payloads. Worker is created in API process. A judge failure has no reliable terminal UI state. Queued completion after room end can still mutate ranking. Empty test set is accepted. Score time includes queue/runner time and same computed time is assigned to all leaderboard rows.
- **Judge:** only outbound adapter to Judge0; no direct eval/exec/subprocess of user source found in app code. This is a positive boundary, not proof of safe deployed sandbox. Language fallback silently picks Python; HTTP request has no timeout; stdout/stdin/source limits and runner credentials missing. Compose one-container Judge0 bootability and env-variable enforcement are unverified.
- **Operations:** no migration runner, CI, deployment rollout/rollback, restore script, tracing, request IDs, latency/queue metrics, alert rules, graceful drain or failure/load harness. Health endpoints do not establish service readiness. No evidence for 100/1000/5000/10000 concurrent users.

## Search findings and interpretation

- No literal TODO/FIXME markers in executable source; absence of those comments does not imply completeness.
- Fake timers: matchmaking in `web/app.js:597`, fabricated grading in `server/server.js:123`. Legitimate but incomplete lifecycle timers: MVP countdown/end. Benign timers: toast dismissal, typing pulse and clipboard feedback.
- `alert()` remains in root fake connection success and honest settings-unavailable notice, plus MVP create failure. No root `href="#"`; the actual `#main-view-container` is a functional skip link.
- `innerHTML`: 13 root controller sites (including harmless clearing and fixed templates); dangerous interpolations listed in CB-001. Theme SVG markup is fixed allowlisted content, not an untrusted sink.
- `localStorage`: room/problem/history stores are global to origin, not user; theme preference is legitimately device-local; AuthService removes legacy browser-trusted sessions and does not authenticate from storage.
- Empty/unhandled behavior: standalone create-problem/create-problist, challenge buttons, moderation buttons and multiple filters/selects. Details follow.
- Seven explicit TypeScript `any` occurrences in the MVP room client; no centralized runtime payload validator or Zod dependency. No @ts-ignore found during source review.
- Secrets: pattern scan found no credential-shaped live keys/private-key blocks in audited source/docs/archive. Hardcoded development DB credentials exist in Compose, setup and connection fallback; empty Judge0 token; template contains concrete default URLs rather than names only. `.env` ignored, `.env.local`/`.env.production` variants are covered by the parent Git repository, not by the CodeBattle-local ignore file (portability gap). No full Git-history or external secret-store scan was performed; do not interpret this as a clean-bill guarantee.

## Exhaustive static control register

HTML parser found **90 interactive elements** (buttons, forms, anchors, inputs, selects and textarea). Counts include hidden views/modals and CSS-hidden mobile navigation. Inputs inherit the form workflow, not an independent server action. Current IDs/classes and line numbers are supplied so each control can be tested.

| Control | Location | Element | ID/selector | Form | Status | Observed handler/chain |
| --- | --- | --- | --- | --- | --- | --- |
| C-001 | web/index.html:21 | a | skip-link | — | WORKING | Skip link → main landmark (main inert before sign-in); no external links in root HTML |
| C-002 | web/index.html:32 | button | #nav-brand | — | WORKING | switchView target; mobile duplicate navigation is CSS-hidden; underlying feature status varies |
| C-003 | web/index.html:40 | button | #btn-toggle-theme | — | WORKING | theme.js allowlisted toggle, local preference + system default |
| C-004 | web/index.html:43 | button | #btn-toggle-sound | — | PARTIAL | Only local flag/icon; no audio integration |
| C-005 | web/index.html:47 | button | #btn-open-qr | — | BROKEN | Modal/QR primitive works if CDN loads; hardcoded external invite URL, no handshake |
| C-006 | web/index.html:52 | button | #btn-nav-sign-in | — | WORKING | Open/switch/close auth modal; full account flow tested separately |
| C-007 | web/index.html:53 | button | #btn-nav-sign-up | — | WORKING | Open/switch/close auth modal; full account flow tested separately |
| C-008 | web/index.html:57 | button | #user-pill-trigger | — | PARTIAL | Menu toggle/aria-expanded; outside-close implemented, Escape/menu keyboard handling incomplete |
| C-009 | web/index.html:73 | button | #btn-drop-profile | — | PARTIAL | Navigation works; profile/settings feature gaps remain |
| C-010 | web/index.html:74 | button | #btn-drop-settings | — | PARTIAL | Navigation works; profile/settings feature gaps remain |
| C-011 | web/index.html:75 | button | #btn-drop-admin | — | MOCK | Hidden after auth sync; navigates to static admin view; Python API denies all |
| C-012 | web/index.html:77 | button | #btn-drop-sign-out | — | WORKING | Persistent server guest/session action, busy/error state |
| C-013 | web/index.html:83 | button | [data-target="view-dashboard"] | — | WORKING | switchView target; mobile duplicate navigation is CSS-hidden; underlying feature status varies |
| C-014 | web/index.html:84 | button | [data-target="view-rooms"] | — | WORKING | switchView target; mobile duplicate navigation is CSS-hidden; underlying feature status varies |
| C-015 | web/index.html:85 | button | [data-target="view-problems"] | — | WORKING | switchView target; mobile duplicate navigation is CSS-hidden; underlying feature status varies |
| C-016 | web/index.html:86 | button | [data-target="view-daily"] | — | WORKING | switchView target; mobile duplicate navigation is CSS-hidden; underlying feature status varies |
| C-017 | web/index.html:87 | button | [data-target="view-matchmaking"] | — | WORKING | switchView target; mobile duplicate navigation is CSS-hidden; underlying feature status varies |
| C-018 | web/index.html:88 | button | [data-target="view-connections"] | — | WORKING | switchView target; mobile duplicate navigation is CSS-hidden; underlying feature status varies |
| C-019 | web/index.html:89 | button | [data-target="view-problists"] | — | WORKING | switchView target; mobile duplicate navigation is CSS-hidden; underlying feature status varies |
| C-020 | web/index.html:90 | button | [data-target="view-leaderboard"] | — | WORKING | switchView target; mobile duplicate navigation is CSS-hidden; underlying feature status varies |
| C-021 | web/index.html:91 | button | [data-target="view-profile"] | — | WORKING | switchView target; mobile duplicate navigation is CSS-hidden; underlying feature status varies |
| C-022 | web/index.html:92 | button | [data-target="view-interview"] | — | WORKING | switchView target; mobile duplicate navigation is CSS-hidden; underlying feature status varies |
| C-023 | web/index.html:99 | button | [data-target="view-dashboard"] | — | WORKING | switchView target; mobile duplicate navigation is CSS-hidden; underlying feature status varies |
| C-024 | web/index.html:100 | button | [data-target="view-rooms"] | — | WORKING | switchView target; mobile duplicate navigation is CSS-hidden; underlying feature status varies |
| C-025 | web/index.html:101 | button | [data-target="view-problems"] | — | WORKING | switchView target; mobile duplicate navigation is CSS-hidden; underlying feature status varies |
| C-026 | web/index.html:102 | button | [data-target="view-leaderboard"] | — | WORKING | switchView target; mobile duplicate navigation is CSS-hidden; underlying feature status varies |
| C-027 | web/index.html:103 | button | [data-target="view-profile"] | — | WORKING | switchView target; mobile duplicate navigation is CSS-hidden; underlying feature status varies |
| C-028 | web/index.html:130 | button | [data-open-auth="modal-sign-up"] | — | WORKING | Open/switch/close auth modal; full account flow tested separately |
| C-029 | web/index.html:131 | button | [data-open-auth="modal-sign-in"] | — | WORKING | Open/switch/close auth modal; full account flow tested separately |
| C-030 | web/index.html:133 | button | #btn-continue-guest | — | WORKING | Persistent server guest/session action, busy/error state |
| C-031 | web/index.html:152 | button | #btn-dash-create-room | — | PARTIAL | Modal open/close works; domain create is only localStorage |
| C-032 | web/index.html:153 | button | #btn-dash-quick-match | — | MOCK | setTimeout creates fabricated opponent room, no matching service |
| C-033 | web/index.html:204 | button | #btn-create-room-modal | — | PARTIAL | Modal open/close works; domain create is only localStorage |
| C-034 | web/index.html:223 | button | #btn-leave-room | — | MOCK | View transition, not authenticated lifecycle/membership |
| C-035 | web/index.html:224 | button | #btn-host-start-battle | — | MOCK | View transition, not authenticated lifecycle/membership |
| C-036 | web/index.html:249 | button | tab-btn active | — | PARTIAL | Local tab switch works; example content is static and not tied to selected problem |
| C-037 | web/index.html:250 | button | tab-btn | — | PARTIAL | Local tab switch works; example content is static and not tied to selected problem |
| C-038 | web/index.html:271 | select | #editor-lang-select | — | PARTIAL | Value sent on submit; no editor language-change listener or runtime allowlist |
| C-039 | web/index.html:289 | button | #btn-run-code | — | BROKEN | Nonempty code → POST submit → 503; busy/error handled, grading unavailable |
| C-040 | web/index.html:290 | button | #btn-submit-code | — | BROKEN | Nonempty code → POST submit → 503; busy/error handled, grading unavailable |
| C-041 | web/index.html:303 | button | #btn-back-to-dashboard | — | PARTIAL | Navigation works; result view remains static, no completed grading path |
| C-042 | web/index.html:315 | button | #btn-open-create-problem-modal | — | BROKEN | No handler found for this element |
| C-043 | web/index.html:341 | button | #btn-create-problist-modal | — | BROKEN | No handler found for this element |
| C-044 | web/index.html:353 | button | btn btn-outline btn-sm btn-solve-problist | — | MOCK | Navigates to all problems, ignores selected track |
| C-045 | web/index.html:364 | button | btn btn-outline btn-sm btn-solve-problist | — | MOCK | Navigates to all problems, ignores selected track |
| C-046 | web/index.html:378 | button | #btn-start-daily-challenge | — | MOCK | Always local p1; no daily schedule, ledger or submission |
| C-047 | web/index.html:417 | select | #mm-lang-select | — | BROKEN | Control renders; selected value never used by workflow |
| C-048 | web/index.html:426 | select | #mm-diff-select | — | BROKEN | Control renders; selected value never used by workflow |
| C-049 | web/index.html:441 | button | #btn-start-matchmaking | — | MOCK | setTimeout creates fabricated opponent room, no matching service |
| C-050 | web/index.html:453 | button | #btn-show-my-qr | — | BROKEN | Modal/QR primitive works if CDN loads; hardcoded external invite URL, no handshake |
| C-051 | web/index.html:458 | input | #input-add-connection-code | — | SECURITY_RISK | Arbitrary nonempty code inserted with innerHTML; fake success/no relationship write |
| C-052 | web/index.html:459 | button | #btn-submit-connection-code | — | SECURITY_RISK | Arbitrary nonempty code inserted with innerHTML; fake success/no relationship write |
| C-053 | web/index.html:479 | button | btn btn-outline btn-sm btn-challenge-user | — | BROKEN | No challenge click handler (static and generated copies) |
| C-054 | web/index.html:485 | button | btn btn-outline btn-sm btn-challenge-user | — | BROKEN | No challenge click handler (static and generated copies) |
| C-055 | web/index.html:500 | select | #leaderboard-lang-filter | — | BROKEN | Control renders; selected value never used by workflow |
| C-056 | web/index.html:611 | select | #interview-role-select | — | BROKEN | Control renders; selected value never used by workflow |
| C-057 | web/index.html:618 | button | #btn-start-interview-session | — | MOCK | Opens solo p1; role ignored; no shared interview |
| C-058 | web/index.html:628 | form | #form-update-settings | form-update-settings | BROKEN | Unavailable alert; username/language/sound fields not persisted |
| C-059 | web/index.html:631 | input | #settings-username | form-update-settings | BROKEN | Unavailable alert; username/language/sound fields not persisted |
| C-060 | web/index.html:636 | select | #settings-pref-lang | form-update-settings | BROKEN | Unavailable alert; username/language/sound fields not persisted |
| C-061 | web/index.html:647 | select | #settings-sound-select | form-update-settings | BROKEN | Unavailable alert; username/language/sound fields not persisted |
| C-062 | web/index.html:654 | button | btn btn-primary | form-update-settings | BROKEN | Unavailable alert; username/language/sound fields not persisted |
| C-063 | web/index.html:702 | button | btn btn-success btn-sm | — | BROKEN | Static admin Approve/Remove without ID/listener/backend |
| C-064 | web/index.html:703 | button | btn btn-outline btn-sm text-danger | — | BROKEN | Static admin Approve/Remove without ID/listener/backend |
| C-065 | web/index.html:718 | button | #btn-close-create-room | — | PARTIAL | Modal open/close works; domain create is only localStorage |
| C-066 | web/index.html:721 | form | #form-create-room | form-create-room | MOCK | Form/source/test/time fields → local ProblemService/RoomService; title required, no API/authorization, XSS sink |
| C-067 | web/index.html:724 | input | #input-room-title | form-create-room | MOCK | Form/source/test/time fields → local ProblemService/RoomService; title required, no API/authorization, XSS sink |
| C-068 | web/index.html:730 | select | #select-problem-source | form-create-room | MOCK | Form/source/test/time fields → local ProblemService/RoomService; title required, no API/authorization, XSS sink |
| C-069 | web/index.html:739 | select | #select-problem-bank-item | form-create-room | MOCK | Form/source/test/time fields → local ProblemService/RoomService; title required, no API/authorization, XSS sink |
| C-070 | web/index.html:750 | input | #input-custom-prob-title | form-create-room | MOCK | Form/source/test/time fields → local ProblemService/RoomService; title required, no API/authorization, XSS sink |
| C-071 | web/index.html:754 | textarea | #input-custom-prob-desc | form-create-room | MOCK | Form/source/test/time fields → local ProblemService/RoomService; title required, no API/authorization, XSS sink |
| C-072 | web/index.html:759 | input | #input-custom-prob-tc-in | form-create-room | MOCK | Form/source/test/time fields → local ProblemService/RoomService; title required, no API/authorization, XSS sink |
| C-073 | web/index.html:763 | input | #input-custom-prob-tc-out | form-create-room | MOCK | Form/source/test/time fields → local ProblemService/RoomService; title required, no API/authorization, XSS sink |
| C-074 | web/index.html:771 | select | #select-time-mode | form-create-room | MOCK | Form/source/test/time fields → local ProblemService/RoomService; title required, no API/authorization, XSS sink |
| C-075 | web/index.html:778 | button | #btn-cancel-create-room | form-create-room | PARTIAL | Modal open/close works; domain create is only localStorage |
| C-076 | web/index.html:779 | button | btn btn-primary btn-lg | form-create-room | MOCK | Form/source/test/time fields → local ProblemService/RoomService; title required, no API/authorization, XSS sink |
| C-077 | web/index.html:789 | button | #btn-close-sign-in | — | WORKING | Open/switch/close auth modal; full account flow tested separately |
| C-078 | web/index.html:790 | form | #form-sign-in | form-sign-in | WORKING | Auth form fields/submit → AuthService → Python validation → SQLite; exact form constraints in HTML |
| C-079 | web/index.html:791 | input | #signin-email | form-sign-in | WORKING | Auth form fields/submit → AuthService → Python validation → SQLite; exact form constraints in HTML |
| C-080 | web/index.html:792 | input | #signin-password | form-sign-in | WORKING | Auth form fields/submit → AuthService → Python validation → SQLite; exact form constraints in HTML |
| C-081 | web/index.html:793 | button | btn btn-primary btn-block | form-sign-in | WORKING | Auth form fields/submit → AuthService → Python validation → SQLite; exact form constraints in HTML |
| C-082 | web/index.html:793 | button | [data-open-auth="modal-sign-up"] | form-sign-in | WORKING | Open/switch/close auth modal; full account flow tested separately |
| C-083 | web/index.html:801 | button | #btn-close-sign-up | — | WORKING | Open/switch/close auth modal; full account flow tested separately |
| C-084 | web/index.html:802 | form | #form-sign-up | form-sign-up | WORKING | Auth form fields/submit → AuthService → Python validation → SQLite; exact form constraints in HTML |
| C-085 | web/index.html:803 | input | #signup-username | form-sign-up | WORKING | Auth form fields/submit → AuthService → Python validation → SQLite; exact form constraints in HTML |
| C-086 | web/index.html:804 | input | #signup-email | form-sign-up | WORKING | Auth form fields/submit → AuthService → Python validation → SQLite; exact form constraints in HTML |
| C-087 | web/index.html:805 | input | #signup-password | form-sign-up | WORKING | Auth form fields/submit → AuthService → Python validation → SQLite; exact form constraints in HTML |
| C-088 | web/index.html:807 | button | btn btn-primary btn-block | form-sign-up | WORKING | Auth form fields/submit → AuthService → Python validation → SQLite; exact form constraints in HTML |
| C-089 | web/index.html:808 | button | [data-open-auth="modal-sign-in"] | form-sign-up | WORKING | Open/switch/close auth modal; full account flow tested separately |
| C-090 | web/index.html:816 | button | #btn-close-qr-modal | — | BROKEN | Modal/QR primitive works if CDN loads; hardcoded external invite URL, no handshake |

### Dynamically generated controls and React controls

| Location/control | Behavior | Status / missing link |
| --- | --- | --- |
| web/app.js renderRooms .btn-join-action | joinRoom(local ID) → lobby | MOCK; no membership API |
| web/app.js renderProblemBank .btn-solve-solo | sets local problem/room → arena | PARTIAL; no real grading/draft, fixed examples |
| web/app.js initConnections .btn-challenge-user | generated button, no listener | BROKEN |
| MVP app/layout.tsx Home/logo/Dashboard anchors | Routes to / and /dashboard | WORKING local navigation, dashboard data is mock |
| MVP app/page.tsx Create Room | axios POST /api/rooms; loading flag; alert on failure; navigate | PARTIAL W, no identity/permissions |
| MVP app/page.tsx Join input/button | trim/uppercase maxLength 6 then navigate | PARTIAL W, no existence/joinable validation before route; no form Enter behavior |
| MVP room page Copy | clipboard.writeText + copied tick timeout | PARTIAL, permission errors not caught |
| MVP room page Start | emit room:start if local player looks host | SECURITY_RISK W, insecure host assignment |
| MVP room page Monaco onChange | state update and activity emit on every edit | PARTIAL, no autosave, throttle or authoritative language selection |
| MVP room page Submit | emit code/language/problemId only; disable while submitting | BROKEN Q, sourceCode omitted, no acceptance ACK/retry key |
| MVP room page Back to Home | window.location navigation | WORKING UI utility, result chain incomplete |

## Verification performed in this audit

| Check | Result | Practical limit |
| --- | --- | --- |
| Recursive file/control inventory | 90 static HTML controls, generated controls and all three React pages reviewed; 112 feature entries | Counts include hidden views and duplicate navigation; not 112 completed features |
| Existing unit/HTTP suite | PASS: 11 tests, `python3 -m unittest discover -s tests -v` | Temporary SQLite DB and local port; primarily account/security-refusal tests |
| Existing browser journey | PASS: Chrome guest, conversion, reload, logout, wrong password, login, cookies, navigation and mobile entry | CDN libraries deliberately blocked, so Monaco execution/QR delivery are not validated |
| Harmless isolated XSS probe | CONFIRMED: room title executes marker on create and refresh | LocalStorage-backed DOM injection; no external exfiltration or cross-user delivery tested |
| Hidden test delivery | CONFIRMED: public problem service JS includes hidden input/expected output | Seed test exposure; not a claim of customer data theft |
| Secret-pattern scan | No verified live key found; default DB credentials/empty judge key identified | No account DB contents, Git history, external providers or full scanner database inspected |
| Environment ignore check | Current parent repository ignores `.env.*`; project-local rules do not | Document portability gap, not a false claim of unignored files in this checkout |
| ZIP comparison | All 22 members match unpacked MVP counterpart | Archive is a duplicate, not another implementation |
| Lint/format/typecheck/build | NOT RUN: no Node/npm on PATH; no root lint/format scripts; no lockfiles | No dependency install/build attempted during audit-only work |
| PostgreSQL/Redis/BullMQ/WS/Judge integration | NOT RUN; source/config audit only | Runtime defects and sandbox controls require provisioned isolated test infrastructure |
| Dependency/container vulnerability audit | NOT RUN | Manifest versions reviewed, no CVE assertions or clean vulnerability claim |
| Firefox/Edge/Safari/accessibility tooling | NOT RUN | Chrome mobile viewport is not Safari or a physical-device test |
| Load/failure/restore/security escape tests | NOT IMPLEMENTED / NOT RUN | No 100, 1K, 5K or 10K capacity claim is substantiated |
| Change-scope check | PASS: SHA-256 snapshots show no changes to pre-existing app/config/test/reference files during audit | Only new `docs/` audit artifacts written; pre-existing uncommitted work preserved |

### File coverage register

| Group | Inspected scope | Outcome |
| --- | --- | --- |
| Browser shell | `web/index.html`, `app.js`, `theme.js`, `index.css`, `github.css` | Pages/controls/state transitions/auth/editor/CDN/theme/accessibility/static fake content |
| Browser services | All 10 `src/modules/*/*.js` files plus `src/shared/constants/languages.js` | Actual fetch boundaries versus constants/localStorage; unused services; starter templates contain solutions rather than empty editor |
| Current backend | `server/server.py`, `server/auth.py` | Every GET/POST branch, cookie handling, body parsing, path containment, SQLite tables/transactions/limits |
| Alternate backend | `server/server.js`, `server/package.json` | Every route, body/static handling and incompatible start command |
| Shared helpers | `lib/problemBank.js`, `lib/xp.js` | Unused seed/reward code is not a connected feature |
| MVP frontend | All three page files, layout, globals, API/socket helpers, package/config/Tailwind/PostCSS/TS settings | Source omission, missing reconnect/error states, hardcoded URLs and loose payload types |
| MVP backend | server plus db/redis/judge services, package, Dockerfile | Complete HTTP/socket/queue/worker flow and security boundaries |
| Data | Root schema, MVP schema/seed; SQLite CREATE TABLE definitions | Constraints/identity/versioning/isolation gaps; no schema migration framework |
| Deployment | MVP Compose/setup/env template; local dotfiles and ignore rules | Defaults, exposed services, missing server-local.js, Linux-specific privileged setup and no production guard |
| Tests | `test_auth.py`, `test_http.py`, `browser_auth.py` | Narrow real coverage; browser harness hardcodes macOS Chrome/port 5099 and temp screenshots |
| Documentation | Root README and all seven supplied `doc/` references plus architecture-v1 | Design/runtime contradictions and misleading old production claims; no instruction from a guide executed |
| Archive | `codebattle-mvp.zip` | 22 byte-identical members; same findings apply |

## Recommended next action

Review the P0 batch proposal, beginning with CB-001/002/003/009, while preserving the working UI and auth flow. **This turn ends at Phase 1; no remediation, migration, deployment or architecture replacement has started.**
