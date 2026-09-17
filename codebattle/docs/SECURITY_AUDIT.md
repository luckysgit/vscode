# Security audit — CodeBattle

> Remediation update (2026-09-16): [P0 batch 1](P0_BATCH_1.md) records subsequent fixes and launcher containment. The audit findings below describe the pre-remediation snapshot.

**Date:** 2026-09-16. **Scope:** local source/configuration review plus existing isolated tests and harmless browser probes. Phase 1 only: no vulnerability fixes or application changes. Findings reference the [implementation plan](IMPLEMENTATION_AUDIT.md) IDs. Severity is release priority, not a fabricated CVSS score.

## Release decision

**Do not describe or deploy the current tree as a production-ready competition/exam service.** The current Python server binds to loopback and refuses grading; that reduces immediate exposure. It does not make its local HTML injection harmless, nor secure the alternative Node/MVP launch paths. P0 applies to unsafe behavior/data loss if those paths are used for real customers.

## Trust boundaries

1. Browser content/localStorage → DOM: vulnerable interpolated room/problem/connection content. LocalStorage is not an authorization or private per-account boundary.
2. Browser → Python: current cookie identity, origin checks, auth field validation, bounded JSON and contained static assets are present. Domain RBAC, ownership and endpoint schemas are not.
3. Browser → legacy Node: no identity checks, wildcard CORS, mock writes and missing path containment. Not the server used by current account flow.
4. Browser → MVP Socket.IO: unauthenticated handshake; client room/problem values select resources and expensive jobs. Code is not safely bound to a room/member/version.
5. API → Redis/BullMQ → worker → Judge0: no transactional admission/outbox; secrets/tests/source in queue payload; same-process worker; exposed runner and unverified isolation controls.
6. Database → results/fanout: MVP publishes before committing durable results, with mutable identity, timing and score state.

## Confirmed runtime findings

### CB-001 — persistent browser-side HTML injection (P0)

**Evidence:** `web/app.js:356` interpolates `room.title` into `card.innerHTML`; `RoomService.createRoom` accepts the form title and stores it in origin-wide localStorage. Related sinks are `renderProblemBank` and `initConnections`.

**Safe reproduction performed:** using an isolated temporary test server/database and a fresh Chrome profile, enter a room title containing an image with a nonexistent local URL and an inline error handler that sets a harmless `window.__auditXSS` marker. Creating the room sets the marker. Reloading the page sets it again from the persisted localStorage entry. No external URL, credential extraction, customer account or application-code mutation was involved.

**Impact qualification:** this proves stored DOM XSS within the browser holding the crafted room data. The current root app does not share rooms between browsers, so cross-user remote propagation has not been demonstrated. The unsafe rendering would become a cross-user vulnerability if shared/backend content is added without fixing it. HttpOnly blocks direct cookie reads, but does not stop injected script from making same-origin authenticated requests.

**Remediation:** textContent/DOM construction for plain fields; safe attributes and schemas; CSP as defense in depth. Test both direct form inputs and stored/network payloads. Fixed theme SVG markup and clearing containers with `innerHTML = ''` are not the vulnerable cases.

### CB-002 — hidden seed test disclosure (P0)

**Evidence:** unauthenticated GET `/src/modules/problems/problem.service.js` contains the supposedly hidden Two Sum input and expected answer (`isHidden: true`). This was checked against the temporary HTTP server. Legacy Node `/api/problems` also statically returns complete test objects. `lib/problemBank.js` contains similar seeds but is not imported or served through the current Python static roots; do not confuse its presence with that route's exposure.

**Impact qualification:** these are current seed problems, not confirmed confidential customer test cases. The design nevertheless fails the hidden-test boundary required before grading real exams.

**Remediation:** separate visible/public problem DTOs from server-only test storage and worker access. Ensure network responses, scripts, result summaries and logs never carry hidden test input/output/IDs to participants.

## Additional high-priority findings (source-confirmed, not exploit-tested)

| ID | Priority | Affected files | Evidence/problem | Impact | Proposed remediation | Required negative tests |
| --- | --- | --- | --- | --- | --- | --- |
| CB-003 | P0 | server/server.js:169,208; server/package.json | Legacy Node static serving joins raw paths without containment; npm start launches this unauthenticated alternative with fake grading. | Potential file disclosure if raw traversal reaches the legacy server; no auth on writes; no request body cap. Not the current Python path. | Quarantine legacy startup behind explicit demo mode or secure and align it; enforce canonical static roots and body limits. | Raw/encoded/symlink traversal, unknown API 404, oversized JSON, unauthenticated writes, startup-mode checks. |
| CB-004 | P0 | codebattle-mvp/backend/src/server.js:40,80,138,201,237 | MVP API and sockets have no account authentication; first joiner becomes host; no membership check for submission/activity. | Unauthorized room control, activity injection, judge resource abuse; socket ID is not durable user identity. | Session-authenticated gateway and HTTP middleware; server-derived identity, validated payloads and per-event membership/permissions. | Unauthenticated sockets; student start/end; cross-room submission/activity; revoked session; malformed/null events. |
| CB-005 | P0 | codebattle-mvp/backend/src/server.js:251,318 | Client-selected problem is not bound to room; zero test rows cause 0 == 0 acceptance. | Forged passing score without executing code. Static confirmed logic, runtime not exercised. | Validate pinned problem version and nonempty published tests; fail closed on unavailable/invalid problem. | Unknown/other-room/zero-test problem rejected; client score/XP ignored. |
| CB-006 | P0 | codebattle-mvp/docker-compose.yml; backend/src/services/judge0.js; backend/Dockerfile | Judge published on host port, empty auth key, latest image; only CPU/memory request limits, no HTTP timeout/output cap or verified sandbox controls. | Unsafe to enable untrusted public execution; container configuration is not sandbox-escape evidence. | Private authenticated execution network, pinned vetted image, separate bounded worker, explicit wall/PID/output/source/stdin/network/filesystem controls. | Network/file/env isolation, fork/memory/output bombs in isolated infrastructure; timeout and judge failure; never run hostile code in app. |
| CB-007 | P0 | codebattle-mvp/backend/src/server.js:255,279,322,342,353 | Queue accepts before pending DB record; score and broadcast precede persistence; no idempotency/outbox/lease/retry policy. | Duplicate execution, lost acknowledged submissions and inconsistent published scores on failure. | Transactional admission plus outbox; stable request/job IDs and payload digest; durable result finalization before fanout; retry/dead-letter policies. | Double click/retry/race executes logically once; crash at every boundary; queue/DB outages; replayed completion. |
| CB-008 | P0 | web/app.js:530; src/modules/* browser stores; codebattle-mvp/frontend/app/room/[code]/page.tsx | Editor has no local/server draft save; account switching clears editor; room/problem/history storage keys are shared across accounts. | Lost student work on refresh/crash/switch; local data appears under another account. | Account-scoped local drafts and authenticated revision-controlled server drafts; explicit recovery/conflict UX. | Refresh/offline/reconnect; stale revision; account A/B isolation; no automatic submit. |
| CB-009 | P0 | server/server.py; server/server.js; codebattle-mvp/backend/src/server.js; docker-compose.yml | No fail-closed staging/production profile; demo state is always enabled; no readiness checks for required services. | Accidental deployment of mock or insecure paths; public readiness cannot be claimed. | Explicit environments and separate demo seed opt-in; production startup validation and readiness gates. | Production rejects missing auth/DB/queue/judge settings; never seeds mocks or falls back on outage. |

## Controls already present — preserve them

- Current auth uses random URL-safe session tokens; only SHA-256 token digests are persisted. Passwords have independent random salts and scrypt hashes; credential comparison is constant-time. Username/email uniqueness is enforced in SQLite.
- Session token rotation on login/registration; old browser session revoked; guest upgrade retains identity and removes old guest sessions. Expired/revoked/fake tokens do not authenticate in existing tests.
- HttpOnly, SameSite=Lax, Path=/ cookies; Secure is added when the configured origin starts with HTTPS. This requires correct deployment configuration and does not prove HTTPS/HSTS deployment exists.
- Python rejects cross-site Origin and Sec-Fetch-Site writes, requires application/json, bounds declared body size and rejects non-object JSON. Absence of Origin is accepted for CLI/same-origin contexts; browser cookie/SameSite/content-type controls must be preserved.
- SQLite and MVP PostgreSQL query values use placeholders. No string-concatenated SQL value injection was found in reviewed runtime queries.
- Python serves only contained web/src paths, blocks dot segments/files and directory listings, and rejects tested plain/encoded traversal. Node legacy containment is a separate unresolved finding.
- Python admin returns 403 for everyone and submit returns 503. Neither is an implemented admin or grading feature; both are safer than simulated success.
- The application source does not directly execute submitted code with eval/exec or subprocess. Judge0 remains an external boundary requiring actual deployment validation.

## Detailed security control assessment

| Control | Current state | Gap / required proof |
| --- | --- | --- |
| Authentication | Local guest/register/login/logout/me tested | No recovery, verification, MFA, password change, session inventory or privileged roles. Guest create and register share a global per-IP bucket. |
| Authorization / IDOR | Current me/logout scoped to cookie; current admin denied | No role/tenant model; public seed GETs expose emails; invalid IDs return first seed record; MVP rooms/jobs are unprotected. |
| Validation / mass assignment | Python auth regex/type/length checks and request cap; parameterized queries | No central room/problem/language/pagination schemas. MVP event destructuring and code.toUpperCase can receive invalid/null values. Directly spreading updatedData in local problem update trusts caller fields. |
| XSS | Some safe textContent paths; theme SVG fixed markup | Confirmed room title sink; related local problem/connection sinks; no CSP. |
| CSRF / CORS | Python same-origin JSON writes and SameSite cookie | Legacy/MVP wildcard CORS; unauthenticated writes already bypass identity entirely. Validate allowed origins and authenticated event checks before enabling credentials. |
| SSRF | Judge base URL comes from environment, not client input | No confirmed client-controlled URL SSRF found; private allowlisted judge destination, no redirects to untrusted hosts, and restricted runner egress need validation. |
| Open redirects | Navigation destinations are fixed/local or room-code route construction | No confirmed open redirect; root hardcoded external QR is a functional/ownership issue, not itself proof of open redirect. |
| Headers | nosniff, DENY and same-origin referrer in Python | No CSP, Permissions-Policy, HTTPS/HSTS config; BaseHTTP server version headers remain; unhandled exceptions default to disconnect/log rather than structured JSON. |
| Rate limits / abuse | 30 guest/register/login attempts per raw client IP per 15min, persisted in SQLite | No user+operation limits; reverse proxy can collapse all clients onto same IP; no bounded thread pool/request-read timeout; unbounded sessions/guests until cleanup. |
| Secrets | No live credential-shaped candidate found by limited working-tree scan | Known development DB defaults; empty runner key; parent ignore covers env variants here but project alone does not. No Git-history/SBOM/container scan. |
| Data integrity | Some SQL PK/FK/UNIQUE/CHECK; auth transactions | No domain migration path, immutable versions, idempotent result transaction, tenant composite keys, audit table or restore proof. |
| Execution isolation | Adapter sends CPU/memory limits to Judge0 | No validated wall/output/PID/network/filesystem controls; exposed host port; no authenticated runner by default; no malicious-code tests performed. |
| Queue reliability | MVP BullMQ declaration + Worker | No pending DB admission/outbox, retry/backoff/lease/dead-letter or capacity policy; broadcasts precede persistence. |
| WebSocket security | Only socket host comparison for start | No authenticated handshake, membership/origin allowlist, per-event schema or rate limit; unknown input/reconnect/expiry/removal cases untested. |
| Server time | MVP records startedAt in Redis | No persisted ends_at/admission cutoff; process timers lose state; root time fixed display. |
| Privacy | No webcam/screen capture implementation | No consent/retention/deletion/export/security-event policy; seed user emails returned publicly must not become real-user DTO design. |
| Audit/monitoring | Console/default HTTP logs; simple health | No append-only audit records, correlation IDs, redaction policy, metrics/alerts or backup recovery evidence. |
| Supply chain | Manifests and CDN URLs exist | No lockfiles or completed vulnerability audit; no integrity attributes for runtime CDN scripts; setup curl-to-shell step is privileged and not executed. |

## Secrets and environment findings

Scanned executable/config/docs text and the duplicate ZIP for credential-shaped keys/private-key markers; results are limited to that pattern scan. No verified live third-party secret was found. Default database credentials are hardcoded in Compose, setup and the PostgreSQL fallback. The MVP template contains default values (not only variable names); Judge0 key defaults empty. No root `.env.example` exists for the Python settings.

`git check-ignore -v` shows this checkout inherits `.env.*` exclusions from the parent repository. The CodeBattle-local `.gitignore` only covers `.env`; copying this project alone loses the parent protection. Add self-contained variant exclusions and a template exception in a later batch. Existing tracked MVP `.env.example` is a template, not evidence of a leaked real credential. `server/data/` is ignored. Account database contents were deliberately not printed or scanned.

There is no production startup validation or automatic refusal to serve demo paths when NODE_ENV changes. The `NODE_ENV=development` Compose value is not a runtime enforcement boundary. No Redis-failure fail-open auth implementation was found in Python (it uses SQLite); instead, failed DB calls lack consistent safe API error handling. Do not describe missing functionality as a tested failover strategy.

## Validation evidence and limits

- **PASS:** existing `python3 -m unittest discover -s tests -v`: 11 tests on temporary SQLite data and an ephemeral local port, 2026-09-16.
- **PASS:** existing Chrome auth/navigation/mobile flow run from a temporary copy with additional harmless audit probes; guest/upgrade/login/logout/reload/wrong password/cookie invisibility/isolated mobile identity confirmed.
- **CONFIRMED:** room title localStorage-backed XSS and public hidden seed case delivery, as above.
- **Not exercised:** legacy Node traversal runtime, MVP SQL/Redis/BullMQ/WS/judge end-to-end, malicious runner payloads, RLS in a deployed database, chaos/10K bursts, TLS/proxy configuration, production build, dependency CVEs, other browsers or screen readers.
- Node/npm/psql/redis-cli are absent from PATH; Docker CLI exists but no infrastructure was started for this audit. Lack of runtime tooling is a validation limit, not evidence that all static findings are false or that dependencies are safe.
- Do not infer successful security certification from passing auth tests. Existing tests cover a narrow local account boundary, not the requested application.

## P0 verification gates before expanding real usage

1. Untrusted strings remain text in all room/problem/connection renderers, including reload and another account on the same browser.
2. Participant-delivered scripts/DTOs/results contain no hidden tests.
3. Canonical startup cannot expose unauthenticated legacy APIs or uncontained files; production rejects demo/default infrastructure.
4. Any enabled websocket/job submission derives identity from a verified session and checks resource membership/version/permissions.
5. Unknown/empty/other-room tests cannot yield acceptance; hostile code runs only behind a validated isolated boundary.
6. Accepted submission survives crashes and duplicate delivery without duplicate awards or published uncommitted results.
7. Editor work has revision-aware recovery and per-account isolation.

This document proposes fixes; none were applied in Phase 1.
