# CodeBattle

A coding competition and exam platform under development.

## Run locally

```bash
CODEBATTLE_MODE=development python3 server/server.py
```

Open **http://localhost:5000**. Python 3.10+ with SQLite is sufficient; the local server has no pip dependencies. It listens on the loopback interface only.

## Working account flows

Every page opening or refresh shows a welcome popup with Create account, Sign in, and Continue as guest. A restored registered session also offers Continue as your username. Selecting guest from a registered session explicitly switches to a guest session.

- Continue as a guest without an email or password.
- Create an account with a unique username, email and a 12–128 character password.
- Upgrade the current guest identity to a registered account.
- Sign in, reload with the session intact, and sign out with server-side session revocation.
- Passwords use salted scrypt hashes. Session tokens are random, stored hashed on the server, and delivered through HttpOnly, SameSite cookies. Auth requests have persistent IP throttling and same-origin checks.

Accounts and sessions persist in `server/data/accounts.sqlite3`, which is excluded from Git and HTTP file serving. Back up that file to retain accounts. Guest sessions expire after seven days; signing out of a guest identity removes browser access to it. Registered accounts can sign in again. The prototype's old browser-only accounts are not valid accounts: create a new account through the form.

Startup requires `CODEBATTLE_MODE=development` for local use (`demo` remains a compatibility alias only; neither seeds rooms) or `CODEBATTLE_MODE=test` for tests. Unset/unknown modes and staging/production are rejected before the database opens. If `NODE_ENV` is set, only `development` or `test` is permitted. Environment variables must be exported or supplied with the command; the Python server does not read `.env` files automatically.

The older Node server and separate MVP backend are quarantined and refuse to start because they contain unauthenticated APIs and unsafe execution paths. Their source remains for reference. `server/package.json` now launches the Python preview. The ZIP archive is an old, unsupported snapshot, not a deployment artifact.

Optional environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `CODEBATTLE_BIND` | `127.0.0.1` | Listening interface; non-loopback use also requires explicit `CODEBATTLE_ORIGIN` |
| `PORT` | `5000` | Local listening port |
| `CODEBATTLE_DB` | `server/data/accounts.sqlite3` | Account database location |
| `CODEBATTLE_ORIGIN` | `http://localhost:<PORT>` | Exact permitted browser origin; HTTPS enables Secure cookies |

## Problem Bank

Open **http://localhost:5000/problems/my** after signing in. Create problems with input/output formats and sample/hidden tests, preview, save drafts, publish immutable versions, search/filter, duplicate, archive, and select a published version for later reuse. New problems persist in SQLite; hidden tests are accessible only through owner-authorized management APIs.

See [Problem Bank implementation](docs/PROBLEM_BANK.md) for files, schema migration, API endpoints, security controls, validation results, and current limits. Existing built-in coding examples are available under **Practice**.

## Shared room lobbies

Create and publish a problem in **My Problems**, then open **Rooms → Create Room**. Select a published version and create a Public or Unlisted room. A second registered account can search by title (Public rooms) or exact code, join, and see the same membership. Lists refresh every five seconds and also have a Refresh button. Membership is persisted, not an online-presence estimate.

See [Shared rooms](docs/SHARED_ROOMS.md) for APIs, migration, verification, and connection requirements.

## Current limits

This is a local preview, not a public customer release. Room creation, discovery, membership, and closure now use shared SQLite records. Fabricated room/history data and matchmaking have been removed from the active flow; unfinished navigation is hidden. Live competition execution and rankings are not implemented. Python Run/Submit works on macOS with `sandbox-exec`: Run uses editable standard input; Submit grades the two built-in problems against server-owned examples and private cases. Programs must read stdin and print their answer. Submission results persist per account in SQLite; the competition history is empty until real competition execution exists. Other languages are disabled, and custom problems support Run only. Guest conversion retains identity, not a claim of server-persisted room history. Account preference editing, password recovery and email verification are not implemented. Monaco and QR rendering use optional external CDN libraries.

See [Run and Submit](docs/RUN_SUBMIT.md) for runner limits and validation.

## Verification

```bash
python3 -m unittest discover -s tests -v
```

The tests use temporary databases and an ephemeral local HTTP port. They cover account persistence, password checking, guest conversion, duplicate registration races, session isolation/revocation/expiry, throttling, cookie flags, cross-origin rejection and private-file protection.

Optional browser checks require Python Playwright and an installed Google Chrome at the macOS application path:

```bash
python3 tests/browser_auth.py
python3 tests/browser_entry.py
python3 tests/browser_security.py
python3 tests/browser_runner.py
python3 tests/browser_problems.py
python3 tests/browser_rooms.py
```

Browser checks use temporary databases on ports 5099 (account flow) and 5101 (security). The security suite verifies that untrusted values render as text even with CSP bypassed in the test profile, cleans legacy hidden-case caches, and separately verifies real CSP enforcement. The backend suite includes fail-closed startup and launcher quarantine tests; Node is needed for the latter (`CODEBATTLE_TEST_NODE` may specify its path).

See [P0 batch 1](docs/P0_BATCH_1.md) for changes, validation and remaining risks. Previously exposed hidden demo cases cannot become secret again; private grading must use new server-only cases.

## Build baseline

Read [Architecture v1](doc/architecture-v1.md) for the target architecture and implementation sequence. The local Python account implementation is an incremental improvement to the already running preview; it does not implement the proposed TypeScript/PostgreSQL production stack.

`codebattle-mvp/` remains a separate incomplete Next.js/Express prototype. Earlier guides in `doc/` contain conflicting stacks and unverified completion claims.
