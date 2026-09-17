# Shared room lobbies

## What was wrong

The old room service read browser-local data and supplied seeded rooms. A fake matchmaking timer also created rooms with a hardcoded host. Different devices could not share these records. The server had a separate in-memory demo API. None represented real customer activity.

## Current behavior

- Room lists start empty. Only successful server-side creates produce a room.
- Registered accounts create rooms using their own published problem or a public published problem. The selected version must still be the current published version at creation time.
- The server derives the host from the session, generates a unique random code, saves the room, and adds the host as its first member in one transaction.
- Public rooms are searchable by title or code. Unlisted rooms require their exact invitation code or existing membership.
- Registered accounts join once; repeated joins are idempotent. Capacity is enforced transactionally, including concurrent joins.
- Member lists and problem samples are visible to joined members. Hidden tests are never included. The original pinned problem version remains unchanged when the author later edits the problem.
- Members can leave. Only the host can close; the host closes instead of leaving. Closed rooms disappear from discovery and reject joins.
- Browser polling refreshes open room lists/lobbies every five seconds. These are durable memberships, not claimed online presence.
- Unknown codes return an error instead of opening an unrelated room.
- Browser-local legacy room/history records are discarded and never imported as real records.
- Fake matchmaking and sample activity were removed from the active flow. Incomplete navigation is hidden, and former fabricated backend endpoints return unavailable/not-found responses.

## Files and persistence

- `server/migrations/002_rooms.sql`: additive `rooms` and `room_members` tables, unique invitation codes/request IDs, membership primary key, foreign keys and discovery indexes.
- `server/rooms.py`: transactional creation, account checks, discovery, version validation, membership, capacity and closure.
- `server/server.py`: actual room APIs, removal of demo responses, optional bind configuration.
- `src/modules/rooms/room.service.js`: server-only API client; no seeded rooms or localStorage room source.
- `web/rooms.js`: create/search/join/member-list/leave/close UI, reusing ProblemSelector.
- `web/app.js`, `web/index.html`, dashboard service: remove simulated entry points and show real empty states.
- `server/runtime.py`: `development` mode name; legacy `demo` alias retained only for command compatibility. Production startup remains blocked.

Migration 002 is applied after the Problem Bank migration. Existing accounts, published problem versions, and submissions remain intact. There is no migration of unverified browser-local room records.

## APIs

| Method | Path | Behavior |
|---|---|---|
| GET | `/api/rooms?search=...&page=1` | Shared open-room summaries, paginated 30 per page |
| POST | `/api/rooms` | Registered creator; title, published `problemVersionId`, visibility, capacity, UUID `requestId` |
| GET | `/api/rooms/:idOrCode` | Room summary; joined members additionally receive participant names and sample-only problem content |
| POST | `/api/rooms/:idOrCode/join` | Registered account; no browser-supplied identity; `{}` body |
| POST | `/api/rooms/:idOrCode/leave` | Remove own membership; `{}` body |
| POST | `/api/rooms/:idOrCode/close` | Host only; `{}` body |

Legacy `/rooms` paths dispatch to these same checks. No client-side host, player count, status, or problem definition is trusted. Create retries with the same request ID/content return the same record; changed content with the same key returns 409. Room codes have 64 random bits and a database unique constraint.

## Two-device testing

Both devices must reach **the same backend URL and database**. `localhost` on two separate devices does not meet this requirement. Browser profiles on one computer can verify independent account behavior while deployment/network access is arranged.

Default startup remains local-only:

```bash
CODEBATTLE_MODE=development python3 server/server.py
```

For a deliberately configured local-network test, set the listening interface and exact browser origin:

```bash
CODEBATTLE_MODE=development CODEBATTLE_BIND=0.0.0.0 CODEBATTLE_ORIGIN=http://SERVER_LAN_IP:5000 python3 server/server.py
```

Replace `SERVER_LAN_IP` with the server computer's reachable address and use that same URL on both devices. This configuration is documented, not activated automatically. Different-network access requires a shared hosted endpoint. No public deployment was performed in this task.

## Verification

- `tests/test_rooms.py`: empty initial state, real identity, discovery, duplicate create/join, persistence, forbidden host impersonation/private problem reuse, concurrent capacity enforcement, unlisted invitations, host-only closure, pinned versions.
- `tests/browser_rooms.py`: two isolated registered browser sessions; A creates, B searches and joins, A sees B; hidden tests absent; B leaves; room remains after reload; A closes; fake legacy cache ignored.
- `tests/browser_security.py`: updated to test real room title XSS protection and removal of legacy room cache.
- Backend suite: 34 tests passed, including development mode and the explicit-origin guard for a shared bind. Account, Problem Bank, Python practice, and room-security browser regressions also passed.

## Still incomplete

Room lobbies are real persisted functionality. Live competition execution, server-controlled start/deadlines, competition scoring, reconnect handling, production hosting, and production operational hardening remain unfinished. No Start Battle button simulates those features. Local code execution remains the existing isolated Python practice runner, not a production competition executor.
