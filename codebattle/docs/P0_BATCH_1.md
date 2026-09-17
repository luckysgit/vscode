# P0 batch 1 — contain the preview security risks

Date: 2026-09-16. Scope: CB-001, current-delivery portion of CB-002, quarantine mitigation for CB-003, and fail-closed startup portion of CB-009. The Phase 1 documents remain an audit snapshot, not a live assertion that those fixes are absent.

## Changes and current status

| Finding | Change | Status / remaining work |
| --- | --- | --- |
| CB-001: unsafe HTML rendering | Room/problem/history/ranking/connection fields now use DOM nodes and textContent; IDs use dataset assignments. No dynamic HTML parsing remains in the root controller. | Fixed for identified root sinks; schema validation and real shared-resource permissions remain separate work. |
| CB-002: hidden tests in browser data | Removed hidden seed data from public JS; preserved the demo fixture outside static roots. Cleans old problem/embedded room caches without removing public examples or replacing loaded data when cache writes fail. | Current delivery contained. Already exposed examples cannot become secret again. Real grading needs fresh private cases, immutable version storage and worker-only access. |
| CB-003: unsafe legacy Node server | Quarantine guard throws before imports/listening; package start points to current Python preview. Original code retained as reference. | Exposure mitigated by disabling the launcher, not by pretending its internals are repaired. |
| CB-004/006: insecure alternative MVP | MVP backend likewise refuses startup before loading modules or connecting to infrastructure. | Contained while future identity/queue/sandbox work remains open. No unsafe execution switch is provided. |
| CB-009: environment fallbacks | Python requires explicit demo/test mode. Staging/production/unknown values and conflicting NODE_ENV fail before creating a DB or socket. Health identifies the preview and production_ready:false. | Startup gate complete for supported working-tree launchers. Production deployment remains intentionally unavailable. Archived ZIP is unsupported and must not be deployed. |
| CB-017 (partial) | Added CSP and Permissions-Policy; local ignore rules now cover env variants and retain .env.example. Added root names-only template. | Broader supply-chain, HTTPS/HSTS and production configuration work remains open. |

## Content security policy

Scripts may load only from this origin and the existing version-specific Monaco/QRCode CDN paths. Inline script handlers and string evaluation are forbidden; no unsafe-inline or unsafe-eval in script-src. The policy denies embedding, objects, base URL changes and off-origin form actions. Camera/microphone/location/screen capture are disabled.

Styles still allow inline CSS because the existing UI has authored style attributes and Monaco generates styles. This is a documented style-only allowance; executable inline JavaScript is blocked. Worker blobs and version-specific Monaco assets are allowed for the editor. This does not add code execution capability to the backend.

## Run the current app

```bash
CODEBATTLE_MODE=demo python3 server/server.py
```

The listener remains loopback-only. Registered accounts stay in the existing database. No account/schema migration or destructive cleanup is included. The app's design, guest entry, account flows and themes are preserved. Non-auth domain behavior is still explicitly a preview.

Direct legacy Node/MVP launch now fails intentionally. These paths contain unauthenticated endpoints, fake results and an unverified execution boundary; continuing to expose them would bypass the fixes. Their source is retained for review and incremental future repair, not deleted or silently replaced.

## Verification

- **17 backend/startup tests passed** with a Node runtime explicitly supplied through CODEBATTLE_TEST_NODE (the Node bundled with the installed test driver; no project dependencies installed).
- **Browser account regression passed:** guest, signup/upgrade, wrong password, login/logout/reload, isolated mobile account and navigation.
- **Browser security regression passed:** hostile room/problem/connection/history/ranking values and attribute payloads remain text; reload remains safe; cached hidden examples removed while public cases remain. CSP bypassed only in the test profile to prove renderer correctness independently.
- **Separate enforced-CSP checks passed:** inline event handlers and injected inline scripts do not execute.
- **Real-CDN smoke passed:** Monaco and QR renderer initialize under the actual enforced CSP. Initial test-helper string evaluation was itself blocked by CSP; the test was corrected to use direct browser evaluation/polling, not by weakening the application policy. One nonblocking resource 404 appeared in the smoke run; no script-policy failure remained.
- JavaScript syntax check and git diff whitespace check passed. No root formatter/linter or production build exists; no broad production/security/capacity claim is made.

Reproduce:

```bash
python3 -m unittest discover -s tests -v
python3 tests/browser_auth.py
python3 tests/browser_security.py
# Optional, requires CDN connectivity:
python3 tests/browser_assets.py
```

Browser checks require Python Playwright and Chrome (CODEBATTLE_TEST_CHROME can override the path for security/assets checks). Backend quarantine tests require Node; set CODEBATTLE_TEST_NODE if it is not on PATH. Without Node that specific test reports skipped, not passed. No tests use the customer account database.

## Next batch

Continue with CB-008: protect editor work with account-scoped local drafts, revision-aware server persistence and explicit recovery. Then implement durable room/membership/version contracts and authenticated realtime/submission admission before reopening the MVP or enabling judging. CB-004 through CB-007 are not complete simply because their unsafe launcher is quarantined.
