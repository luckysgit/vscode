# Canonical feature matrix — current implementation

> Remediation update (2026-09-16): [P0 batch 1](P0_BATCH_1.md) records subsequent fixes and launcher containment. The audit findings below describe the pre-remediation snapshot.

**Date:** 2026-09-16. Phase 1 inventory, not a promise of completed implementation. The current product path is the Python-served `web/` application; MVP differences are stated explicitly. `WORKING` is restricted to the observed local subflow. Production DONE still requires the full definition in the request, including authorization, recovery and operational evidence.

See [implementation audit](IMPLEMENTATION_AUDIT.md) for priorities, routes and evidence; [security audit](SECURITY_AUDIT.md) for trust boundaries and confirmed findings.

## Complete chain profiles

Every feature row below references one of these fully specified current chains. Missing stages are explicitly absent, not assumed. A profile plus its row-specific exceptions defines that feature's observed path. UI-only utilities do not need a database/API; domain actions do.

| Chain | UI | Validation | API | Authentication | Authorization | Business logic | Database/Redis/queue | Response | UI update | Error/loading | Audit/monitoring |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | Account form/guest/restore | HTML fields; backend auth validation | /api/auth/* | Cookie hash/expiry or credential check | Own session; no roles | AuthStore transactions | SQLite accounts/sessions/limits | JSON plus HttpOnly cookie | Header/profile/welcome refreshed | Busy button + error text; no request timeout | No audit trail/request ID; default access log |
| L | Local domain UI | Limited HTML/trim; no domain schema | No request from UI | UI navigation gate only | None | Browser service mutates local objects | Global localStorage or memory | Local object, not API response | Immediate render/navigation | Console errors or none; fake success possible | None |
| S | Static/demo UI | None | None; unrelated mock GET may exist | UI gate only | None | Fixed seeds/statistics | No authoritative state | No response | Static/local render | None | None |
| R | Run/Submit | Nonempty source; JSON/body size | POST /api/submit | Python session required | No resource permission because judging unavailable | Explicit refusal | No write or job | 503 JSON | Console error displayed | Busy button then reset | No audit/queue metrics |
| W | MVP room UI | Code trim; no backend/event schemas | POST /api/rooms + Socket.IO | Absent | First socket host only for start | Redis room ops; process timers | PG room + Redis, not atomic | HTTP code/socket events | Separate Next page state | Create spinner; many events unhandled | Console logging only |
| Q | MVP submit UI | No source payload / limits | submission:submit | Absent | No membership/problem binding | BullMQ worker; mutable score | Queue + Redis; final PG insert after broadcast | Pending/results | Pending mislabeled wrong answer | No reliable failure terminal state | No metrics/audit |
| U | UI utility | Local allowlists/targets as applicable | N/A | N/A | N/A | Local theme/navigation/modal behavior | Theme preference only; others N/A | N/A | Immediate utility update | Storage exceptions handled; accessibility varies | N/A; no sensitive business mutation |
| N | No implementation | Absent | Absent | Absent | Absent | Absent | Absent | Absent | Absent | Absent | Absent |

| ID | Area | Feature | Status | Current chain | Evidence/path | Missing links / proposed issue |
| --- | --- | --- | --- | --- | --- | --- |
| F-001 | Authentication | Guest entry | WORKING | A | web/app.js:132; AuthService; server/auth.py; tests/test_auth.py + test_http.py + browser_auth.py | Local core verified; not full production auth. CB-016/017/019. |
| F-002 | Authentication | Sign up | WORKING | A | web/app.js:132; AuthService; server/auth.py; tests/test_auth.py + test_http.py + browser_auth.py | Local core verified; not full production auth. CB-016/017/019. |
| F-003 | Authentication | Guest upgrade | WORKING | A | web/app.js:132; AuthService; server/auth.py; tests/test_auth.py + test_http.py + browser_auth.py | Local core verified; not full production auth. CB-016/017/019. |
| F-004 | Authentication | Sign in | WORKING | A | web/app.js:132; AuthService; server/auth.py; tests/test_auth.py + test_http.py + browser_auth.py | Local core verified; not full production auth. CB-016/017/019. |
| F-005 | Authentication | Sign out | WORKING | A | web/app.js:132; AuthService; server/auth.py; tests/test_auth.py + test_http.py + browser_auth.py | Local core verified; not full production auth. CB-016/017/019. |
| F-006 | Authentication | Session restoration | WORKING | A | web/app.js:132; AuthService; server/auth.py; tests/test_auth.py + test_http.py + browser_auth.py | Local core verified; not full production auth. CB-016/017/019. |
| F-007 | Authentication | Forgot password | NOT_IMPLEMENTED | N | No corresponding forms/endpoints/tables; account dropdown is navigation only | CB-019; use expiring single-use tokens and server session controls. |
| F-008 | Authentication | Reset password | NOT_IMPLEMENTED | N | No corresponding forms/endpoints/tables; account dropdown is navigation only | CB-019; use expiring single-use tokens and server session controls. |
| F-009 | Authentication | Email verification | NOT_IMPLEMENTED | N | No corresponding forms/endpoints/tables; account dropdown is navigation only | CB-019; use expiring single-use tokens and server session controls. |
| F-010 | Authentication | Change password | NOT_IMPLEMENTED | N | No corresponding forms/endpoints/tables; account dropdown is navigation only | CB-019; use expiring single-use tokens and server session controls. |
| F-011 | Authentication | Account switcher | NOT_IMPLEMENTED | N | No corresponding forms/endpoints/tables; account dropdown is navigation only | CB-019; use expiring single-use tokens and server session controls. |
| F-012 | Authentication | MFA | NOT_IMPLEMENTED | N | No corresponding forms/endpoints/tables; account dropdown is navigation only | CB-019; use expiring single-use tokens and server session controls. |
| F-013 | Authentication | Session list/revoke all | NOT_IMPLEMENTED | N | No corresponding forms/endpoints/tables; account dropdown is navigation only | CB-019; use expiring single-use tokens and server session controls. |
| F-014 | Problems | Browse | MOCK | L | ProblemService.getAllProblems; web/app.js:500 | Seed/local list, no authenticated API-backed bank. CB-011/015. |
| F-015 | Problems | Search | NOT_IMPLEMENTED | N | No problem search/filter/pagination controls or handlers | CB-015; validated query/limits and paginated DB lookup. |
| F-016 | Problems | Filters | NOT_IMPLEMENTED | N | No problem search/filter/pagination controls or handlers | CB-015; validated query/limits and paginated DB lookup. |
| F-017 | Problems | Pagination | NOT_IMPLEMENTED | N | No problem search/filter/pagination controls or handlers | CB-015; validated query/limits and paginated DB lookup. |
| F-018 | Problems | Open problem | PARTIAL | L | Generated .btn-solve-solo → getProblemById → arena | Description changes; examples remain static and editor carries previous content. CB-012. |
| F-019 | Problems | Create | BROKEN | L | btn-open-create-problem-modal has no handler; custom room form writes browser bank | Standalone action broken; local alternate has no ownership/server persistence. CB-001/011/015. |
| F-020 | Problems | Edit | PARTIAL | L | ProblemService.commitProblemUpdate only; no UI/API | Overwrites content and increments number, no immutable snapshot/permission. CB-011. |
| F-021 | Problems | Delete/archive | NOT_IMPLEMENTED | N | Root schema has related flags/fields but no runtime workflow | CB-011/015/018. |
| F-022 | Problems | Publish | NOT_IMPLEMENTED | N | Root schema has related flags/fields but no runtime workflow | CB-011/015/018. |
| F-023 | Problems | Fork | NOT_IMPLEMENTED | N | Root schema has related flags/fields but no runtime workflow | CB-011/015/018. |
| F-024 | Problems | Flag/report | NOT_IMPLEMENTED | N | Root schema has related flags/fields but no runtime workflow | CB-011/015/018. |
| F-025 | Problems | Visible tests | PARTIAL | S | Static HTML examples; browser problem seed contains testCases | Examples are not populated from selected problem. CB-012. |
| F-026 | Problems | Hidden tests | SECURITY_RISK | L | ProblemService seed publicly served; legacy GET returns tests | Hidden input/expected cannot be client data. CB-002. |
| F-027 | Problems | Run code | BROKEN | R | SubmissionService → Python 503; MVP Q separately | Safe unavailable state, not grading. CB-005/006/007/012. |
| F-028 | Problems | Submit code | BROKEN | R | SubmissionService → Python 503; MVP Q separately | Safe unavailable state, not grading. CB-005/006/007/012. |
| F-029 | Problems | Solve history | MOCK | L | DashboardService.getPastRoomsHistory | Origin-global seeds/local storage; no final submissions. CB-008/020. |
| F-030 | Rooms | Create | MOCK | L | form-create-room → RoomService.createRoom; separate MVP W | No shared durable room. CB-010. |
| F-031 | Rooms | Join | MOCK | L | joinRoom, btn-leave-room, btn-host-start-battle; MVP W partial | Local view changes only; no membership/host authority. CB-010/013. |
| F-032 | Rooms | Leave | MOCK | L | joinRoom, btn-leave-room, btn-host-start-battle; MVP W partial | Local view changes only; no membership/host authority. CB-010/013. |
| F-033 | Rooms | Start | MOCK | L | joinRoom, btn-leave-room, btn-host-start-battle; MVP W partial | Local view changes only; no membership/host authority. CB-010/013. |
| F-034 | Rooms | Invite | BROKEN | U | QR URLs hardcoded to codebattle.app/join; no root join URL handler | Rendered QR does not establish a working invite. CB-010. |
| F-035 | Rooms | Countdown | NOT_IMPLEMENTED | N | Root absent; MVP W in-process 5-second delay | Persist transition and recover after restart. CB-013. |
| F-036 | Rooms | Timer | MOCK | S | setupBattleArena fixed 14:59 or relaxed label | MVP decrements local state and ends via process timeout; no durable cutoff. CB-013. |
| F-037 | Rooms | Participant management | NOT_IMPLEMENTED | N | No root membership API or MVP kick/leave handler | CB-004/010/014. |
| F-038 | Rooms | Kick participant | NOT_IMPLEMENTED | N | No root membership API or MVP kick/leave handler | CB-004/010/014. |
| F-039 | Rooms | Room settings | PARTIAL | L | Create form source/time controls; hardcoded difficulty/language defaults | Only local config; no frozen policy or server allowlist. CB-010/011/012. |
| F-040 | Rooms | Language restrictions | PARTIAL | L | Create form source/time controls; hardcoded difficulty/language defaults | Only local config; no frozen policy or server allowlist. CB-010/011/012. |
| F-041 | Rooms | Problem selection | PARTIAL | L | Create form source/time controls; hardcoded difficulty/language defaults | Only local config; no frozen policy or server allowlist. CB-010/011/012. |
| F-042 | Rooms | Live leaderboard | MOCK | S | Root static; MVP Q Redis fanout exists | MVP finalization/identity/reconnect broken. CB-007/014. |
| F-043 | Rooms | Submission status | BROKEN | R | Root unavailable message; MVP Q pending false interpreted as wrong | Explicit async state machine needed. CB-012. |
| F-044 | Rooms | Reconnect | NOT_IMPLEMENTED | N | Root no WS; MVP W no rejoin snapshot/manual end | Auto timeout not durable/manual room end. CB-013/014. |
| F-045 | Rooms | End room | NOT_IMPLEMENTED | N | Root no WS; MVP W no rejoin snapshot/manual end | Auto timeout not durable/manual room end. CB-013/014. |
| F-046 | Rooms | Results | MOCK | S | Root static results; history seed/local; no replay controls/storage | MVP ended view exists but fanout/final data inconsistent. CB-007/014/015. |
| F-047 | Rooms | Replay/history | MOCK | S | Root static results; history seed/local; no replay controls/storage | MVP ended view exists but fanout/final data inconsistent. CB-007/014/015. |
| F-048 | Competition | Scoring | MOCK | S | Root fixed outcomes; unused lib/xp.js; MVP Q formula | Persist server-calculated ledger, best score and accepted-time scoring. CB-005/007/014/020. |
| F-049 | Competition | Ranking | MOCK | S | Root fixed outcomes; unused lib/xp.js; MVP Q formula | Persist server-calculated ledger, best score and accepted-time scoring. CB-005/007/014/020. |
| F-050 | Competition | Tie breaking | NOT_IMPLEMENTED | N | No root rules; MVP status-only and no recovery | CB-007/013/014; deterministic policies and negative tests. |
| F-051 | Competition | Attempts | NOT_IMPLEMENTED | N | No root rules; MVP status-only and no recovery | CB-007/013/014; deterministic policies and negative tests. |
| F-052 | Competition | Late submissions | NOT_IMPLEMENTED | N | No root rules; MVP status-only and no recovery | CB-007/013/014; deterministic policies and negative tests. |
| F-053 | Competition | Reconnect behavior | NOT_IMPLEMENTED | N | No root rules; MVP status-only and no recovery | CB-007/013/014; deterministic policies and negative tests. |
| F-054 | Competition | Timers | MOCK | S | Root fixed clock; MVP W relative state | Server cutoff must govern. CB-013. |
| F-055 | Competition | Matchmaking | MOCK | L | web/app.js:590 timeout creates DevNinja room; selects ignored | No matching queue or another user. CB-015. |
| F-056 | Competition | Daily challenge | MOCK | L | Always p1; hardcoded daily counters | No schedule/unique completion/streak award. CB-015/020. |
| F-057 | Competition | Interview mode | MOCK | L | Role select ignored; opens p1 solo arena | No shared room/role/code synchronization. CB-015. |
| F-058 | Exam | Exam mode | NOT_IMPLEMENTED | N | No runtime exam policy, telemetry table, event handler or teacher dashboard | CB-018/021; evidence signals only, no extension-blocking claims or invasive recording. |
| F-059 | Exam | Teacher controls | NOT_IMPLEMENTED | N | No runtime exam policy, telemetry table, event handler or teacher dashboard | CB-018/021; evidence signals only, no extension-blocking claims or invasive recording. |
| F-060 | Exam | Student monitoring | NOT_IMPLEMENTED | N | No runtime exam policy, telemetry table, event handler or teacher dashboard | CB-018/021; evidence signals only, no extension-blocking claims or invasive recording. |
| F-061 | Exam | Tab switch events | NOT_IMPLEMENTED | N | No runtime exam policy, telemetry table, event handler or teacher dashboard | CB-018/021; evidence signals only, no extension-blocking claims or invasive recording. |
| F-062 | Exam | Fullscreen exit | NOT_IMPLEMENTED | N | No runtime exam policy, telemetry table, event handler or teacher dashboard | CB-018/021; evidence signals only, no extension-blocking claims or invasive recording. |
| F-063 | Exam | Copy/paste events | NOT_IMPLEMENTED | N | No runtime exam policy, telemetry table, event handler or teacher dashboard | CB-018/021; evidence signals only, no extension-blocking claims or invasive recording. |
| F-064 | Exam | Disconnect/reconnect | NOT_IMPLEMENTED | N | No runtime exam policy, telemetry table, event handler or teacher dashboard | CB-018/021; evidence signals only, no extension-blocking claims or invasive recording. |
| F-065 | Exam | Security alerts | NOT_IMPLEMENTED | N | No runtime exam policy, telemetry table, event handler or teacher dashboard | CB-018/021; evidence signals only, no extension-blocking claims or invasive recording. |
| F-066 | Exam | Submission locking | NOT_IMPLEMENTED | N | No runtime exam policy, telemetry table, event handler or teacher dashboard | CB-018/021; evidence signals only, no extension-blocking claims or invasive recording. |
| F-067 | Exam | Result visibility | NOT_IMPLEMENTED | N | No runtime exam policy, telemetry table, event handler or teacher dashboard | CB-018/021; evidence signals only, no extension-blocking claims or invasive recording. |
| F-068 | Profile | Edit profile | BROKEN | L | form-update-settings → unavailable alert | No save API or validated update. CB-020. |
| F-069 | Profile | Avatar | NOT_IMPLEMENTED | N | Decorative avatar markup; no upload endpoint | CB-020/022 if uploads become in scope. |
| F-070 | Profile | Statistics | PARTIAL | S | Current /me zeros and empty-badge copy; other services/HTML seeds; lib/xp.js unused | No authoritative ledger/grading aggregation. CB-020. |
| F-071 | Profile | XP | PARTIAL | S | Current /me zeros and empty-badge copy; other services/HTML seeds; lib/xp.js unused | No authoritative ledger/grading aggregation. CB-020. |
| F-072 | Profile | Badges | PARTIAL | S | Current /me zeros and empty-badge copy; other services/HTML seeds; lib/xp.js unused | No authoritative ledger/grading aggregation. CB-020. |
| F-073 | Profile | Streak | PARTIAL | S | Current /me zeros and empty-badge copy; other services/HTML seeds; lib/xp.js unused | No authoritative ledger/grading aggregation. CB-020. |
| F-074 | Profile | Solve history | PARTIAL | S | Current /me zeros and empty-badge copy; other services/HTML seeds; lib/xp.js unused | No authoritative ledger/grading aggregation. CB-020. |
| F-075 | Connections | Add | SECURITY_RISK | L | web/app.js:619 inserts arbitrary code into HTML and alerts success | No mutual consent/persistence; DOM injection. CB-001/015. |
| F-076 | Connections | Remove | NOT_IMPLEMENTED | N | No removal/invitation protocol; .btn-challenge-user has no handler | CB-015/021. |
| F-077 | Connections | Invitations | NOT_IMPLEMENTED | N | No removal/invitation protocol; .btn-challenge-user has no handler | CB-015/021. |
| F-078 | Connections | QR | BROKEN | U | CDN renderer encodes external /connect?code=; modal code static | No receiving handshake or local route. CB-015/022. |
| F-079 | Leaderboard | Global | MOCK | S | LeaderboardService constants; server seeds | No persisted aggregate. CB-014/020. |
| F-080 | Leaderboard | Weekly | NOT_IMPLEMENTED | N | No runtime endpoints/queries | CB-014/020. |
| F-081 | Leaderboard | Pagination | NOT_IMPLEMENTED | N | No runtime endpoints/queries | CB-014/020. |
| F-082 | Leaderboard | Room | PARTIAL | Q | MVP Redis sorted set; not current root | No durable final snapshot; score decrease/tie/time flaws. CB-007/014. |
| F-083 | Leaderboard | Language | BROKEN | S | leaderboard-lang-filter select unbound | No filtering/query contract. CB-015. |
| F-084 | Organizations | Create organization | NOT_IMPLEMENTED | N | OrgService returns two fixed organizations, no visible org flow/API/schema | CB-018/021; tenant model and permission checks before institution use. |
| F-085 | Organizations | Invite members | NOT_IMPLEMENTED | N | OrgService returns two fixed organizations, no visible org flow/API/schema | CB-018/021; tenant model and permission checks before institution use. |
| F-086 | Organizations | Student/teacher roles | NOT_IMPLEMENTED | N | OrgService returns two fixed organizations, no visible org flow/API/schema | CB-018/021; tenant model and permission checks before institution use. |
| F-087 | Organizations | Organization settings | NOT_IMPLEMENTED | N | OrgService returns two fixed organizations, no visible org flow/API/schema | CB-018/021; tenant model and permission checks before institution use. |
| F-088 | Organizations | Tenant isolation | NOT_IMPLEMENTED | N | OrgService returns two fixed organizations, no visible org flow/API/schema | CB-018/021; tenant model and permission checks before institution use. |
| F-089 | Admin | Users | MOCK | S | AdminService/static hidden admin view; Python GET admin always 403 | No admin authority or management endpoints. CB-018/021. |
| F-090 | Admin | Rooms | MOCK | S | AdminService/static hidden admin view; Python GET admin always 403 | No admin authority or management endpoints. CB-018/021. |
| F-091 | Admin | Statistics | MOCK | S | AdminService/static hidden admin view; Python GET admin always 403 | No admin authority or management endpoints. CB-018/021. |
| F-092 | Admin | Problems | BROKEN | S | Static moderation row; Approve/Remove have no listeners | No mutation/API/audit. CB-015/021. |
| F-093 | Admin | Flags | BROKEN | S | Static moderation row; Approve/Remove have no listeners | No mutation/API/audit. CB-015/021. |
| F-094 | Admin | Moderation | BROKEN | S | Static moderation row; Approve/Remove have no listeners | No mutation/API/audit. CB-015/021. |
| F-095 | Admin | Audit logs | NOT_IMPLEMENTED | N | No audit schema/writer/reader | CB-021/024. |
| F-096 | Payments | Checkout | NOT_IMPLEMENTED | N | Only tier/stripe_customer_id schema placeholders and documentation | CB-021; signed provider events/idempotency/reconciliation. |
| F-097 | Payments | Webhook | NOT_IMPLEMENTED | N | Only tier/stripe_customer_id schema placeholders and documentation | CB-021; signed provider events/idempotency/reconciliation. |
| F-098 | Payments | Subscription state | NOT_IMPLEMENTED | N | Only tier/stripe_customer_id schema placeholders and documentation | CB-021; signed provider events/idempotency/reconciliation. |
| F-099 | Payments | Cancellation | NOT_IMPLEMENTED | N | Only tier/stripe_customer_id schema placeholders and documentation | CB-021; signed provider events/idempotency/reconciliation. |
| F-100 | Payments | Failed payment handling | NOT_IMPLEMENTED | N | Only tier/stripe_customer_id schema placeholders and documentation | CB-021; signed provider events/idempotency/reconciliation. |
| F-101 | Notifications | In-app | PARTIAL | U | NotificationService local timed toast, no delivery usage in controller | Toast primitive only; no durable feed/recipient/read state. CB-021. |
| F-102 | Notifications | Email | NOT_IMPLEMENTED | N | No provider/event/outbox delivery; challenge handlers absent | CB-021. |
| F-103 | Notifications | Challenge invitation | NOT_IMPLEMENTED | N | No provider/event/outbox delivery; challenge handlers absent | CB-021. |
| F-104 | Notifications | Room invitation | NOT_IMPLEMENTED | N | No provider/event/outbox delivery; challenge handlers absent | CB-021. |
| F-105 | UX | Light/dark mode | WORKING | U | web/theme.js; CSS tokens; saved preference/system fallback | Existing manual browser check from prior turn; no committed theme regression suite. |
| F-106 | UX | Navigation | WORKING | U | web/app.js:62,132; static/dynamic control bindings | Navigation observed in Chrome; focus/accessibility coverage incomplete. CB-022. |
| F-107 | UX | Account menu | WORKING | U | web/app.js:62,132; static/dynamic control bindings | Navigation observed in Chrome; focus/accessibility coverage incomplete. CB-022. |
| F-108 | UX | Auth dialog switching | WORKING | U | web/app.js:62,132; static/dynamic control bindings | Navigation observed in Chrome; focus/accessibility coverage incomplete. CB-022. |
| F-109 | UX | Sound toggle | PARTIAL | U | state.soundEnabled/icon toggle only | No audio playback uses state; not a working sound-effects feature. |
| F-110 | Recovery | Draft autosave | NOT_IMPLEMENTED | N | No draft storage/save/revision API in any runtime | CB-008. |
| F-111 | Recovery | Conflict resolution | NOT_IMPLEMENTED | N | No draft storage/save/revision API in any runtime | CB-008. |
| F-112 | Recovery | Offline recovery | NOT_IMPLEMENTED | N | No draft storage/save/revision API in any runtime | CB-008. |

## Definition-of-done application

For the core account path, browser/API/store tests demonstrate local validation, credential/session handling, persistence, loading/errors and reload. They do **not** demonstrate production availability, recovery email, MFA, full audit logging or capacity. A design utility can be locally complete without an API. No room, problem-authoring, grading, competition or institutional workflow meets the complete requested production definition.

A template/SQL column or imported unused helper is not backend integration. The inventories below deliberately retain visible but nonfunctional controls rather than removing them during an audit.
