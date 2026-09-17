# Problem Bank implementation

## Scope and entry point

Open **http://localhost:5000/problems/my** or **My Problems** in navigation. Sign in with a registered account. Guests see an account prompt.

The existing Python/SQLite server, cookie sessions, theme styles, form controls, and text-only rendering are reused. No new room, competition, WebSocket, leaderboard, exam, organization, payment, or AI functionality was added.

### Working workflow

1. **Create Problem**: title, short/full description, difficulty, normalized tags, Private/Public visibility (Private by default).
2. **Input / Output**: formats, constraints, notes.
3. **Test Cases**: input, expected output, sample/hidden switch; add, duplicate, delete, reorder.
4. **Preview**: student-facing content and sample tests only.
5. **Save Draft** permits incomplete statements and zero cases. **Publish** requires title, description, input/output formats, at least one sample and one hidden test. Empty input or expected output is permitted as an explicitly provided string, since these can be valid tests.
6. Search/filter/sort My Problems; open, edit, duplicate, archive, and inspect version history.
7. **Select a problem** searches My/Public published problems and pins both problem ID and published version ID. Archived problems and unpublished drafts cannot be selected.

Every test case stores input and expected output, not a reference code solution. Published source versions and their tests remain unchanged after later edits.

## Created files

| File | Purpose |
|---|---|
| `server/migrations/001_problem_bank.sql` | Additive, transactional, repeatable SQLite migration and immutability triggers |
| `server/problems.py` | Validation, ownership, persistence, public/author projections, version lifecycle, filtering |
| `src/modules/problems/problem-bank.api.js` | Authenticated API client; no localStorage author data |
| `web/problem-bank.js` | My Problems, four-step authoring, previews, version history, save/error states |
| `web/problem-selector.js` | Reusable selector with pinned version selection |
| `web/problem-bank.css` | Responsive styling using existing theme variables |
| `tests/test_problems.py` | Store-level authorization, persistence, validation, concurrency and version tests |
| `tests/browser_problems.py` | Full browser workflow, failure handling, XSS, mobile and authorization checks |
| `docs/PROBLEM_BANK.md` | Implementation and operational notes |

## Modified files in this task

- `server/server.py`: initialize migration/store; replace demo `/api/problems` APIs; route authoring pages; support PATCH and structured database errors.
- `web/app.js`: connect authoring navigation, protect unsaved changes, clear authoring state on identity changes, return to authoring after authentication.
- `web/index.html`: My Problems navigation/view, authoring assets, link old practice page's Create button to the wizard. Built-in practice examples remain separately accessible as Practice.
- `tests/test_http.py`: PATCH support and HTTP ownership, public-response, origin, validation, database-failure checks.
- `README.md`: new feature entry point and verification commands.

Earlier uncommitted account/runner/security work is outside this change list.

## Database migration and compatibility

`ProblemStore` applies `001_problem_bank.sql` on server startup. It adds:

- `problems`: authenticated account owner, published/current pointer, optional working-draft pointer, published and pending visibility, status, timestamps, archive timestamp, optimistic revision.
- `problem_versions`: numbered content snapshots, author, creation/publication timestamps.
- `problem_tags`: version-specific normalized tags.
- `test_cases`: version-specific input/output, hidden flag, order, independent UUID.
- `problem_create_requests`: owner-scoped idempotency keys for creation/duplication.
- `problem_bank_migrations`: migration version ledger.

Foreign keys, required fields, enum checks, unique version numbers/test order, owner/public/tag indexes, and triggers protect consistency. Every write uses a transaction. Updates require the revision the client opened; stale or simultaneous writes return **409** instead of overwriting work. Creation retries with the same request ID and content return the same problem; reusing the ID with changed content returns 409.

A draft is mutable until publication. Editing a published version creates the next working version; subsequent draft saves update that draft. The previous version remains current for public access and selectors until Publish. Visibility changes are also staged until publication. Published version rows, tags, and tests reject updates/deletes at the database level.

The active database previously contained `accounts`, `sessions`, `auth_limits`, and `practice_submissions`; these are retained. The PostgreSQL schema files are separate, inactive prototypes and are not migrated. Legacy localStorage problems lack trustworthy ownership and are not silently imported. New authoring records use SQLite exclusively.

Back up `server/data/accounts.sqlite3` using SQLite's backup API before deployment/migration; backups must remain outside served directories. A local backup is taken before applying this feature to the current preview. There is no destructive down migration.

## APIs

Successful responses use `success: true` plus `problem`, `problems`, or `versions`. Domain failures use `success: false`, a human-readable `error`, and stable `code`; no raw SQL or test payload is returned in errors/logs. Existing HTTP envelope checks retain their existing error convention.

| Method | Endpoint | Access / behavior |
|---|---|---|
| GET | `/api/problems` | Public published summaries; no test contents |
| GET | `/api/problems/my` | Registered owner summaries |
| POST | `/api/problems` | Registered account; create draft; `requestId` required |
| GET | `/api/problems/:id` | Public published content or owner's content; **samples only** |
| GET | `/api/problems/:id/manage` | Owner only; complete authoring data including hidden cases |
| PATCH | `/api/problems/:id` | Owner only; save draft; `revision` required |
| POST | `/api/problems/:id/publish` | Owner only; validate/publish draft; `revision` required |
| POST | `/api/problems/:id/duplicate` | Owner only; new Private draft with independent IDs; `requestId` required |
| POST | `/api/problems/:id/archive` | Owner only; retain history; `revision` required |
| GET | `/api/problems/:id/versions` | Owner-only version metadata |

Detail/manage GETs accept `versionId`. Other clients can fetch only published versions of an available public problem; a draft version UUID does not grant access. Private and archived problems are owner-only. Unknown IDs return 404; unauthorized existing records return 403.

Lists support `search`, `difficulty`, `tag`, `visibility`, `status`, `sort` (`updated`, `created`, `title`, `difficulty`), `page` (30 rows), and `selectable=true`. Selection lists always use the published current version.

Frontend routes: `/problems/my`, `/problems/create`, `/problems/:id`, `/problems/:id/edit`, `/problems/select`. Deep links and reloads serve the existing app shell. `/problems` redirects to My Problems.

### Reusable selector contract

```js
const selector = new ProblemSelector(container, {
  api: new ProblemBankAPI(),
  onSelect: ({problemId, problemVersionId}) => { /* consume later */ }
});
// selector.value is a frozen {problemId, problemVersionId}, initially null.
// container also emits a bubbling `problem-selected` CustomEvent with this detail.
// Call selector.destroy() when removing the component.
```

No room is created or changed by selecting a problem.

## Security and validation

- Session-derived owner; unknown ownership/status fields from the browser are rejected.
- Registered-account requirement for authoring; no inferred teacher/admin permissions.
- Owner-only management, edits, duplication, archive and history.
- Public projection queries only non-hidden test rows. Lists include metadata/counts, never test contents.
- No hidden tests cached in localStorage. Author data is cleared on account changes; cache headers are `no-store`.
- Plain text statements/previews: no arbitrary HTML or Markdown renderer. Existing CSP remains enforced.
- Same-origin mutation checks apply to POST and PATCH; parameterized SQL and allowlisted sorting.
- Limits: title 160 characters, short description 500, statement 50,000, formats/constraints/notes 10,000 each, 20 tags of 32 characters, 50 tests, 4,096 bytes each input/output, 512KiB authoring request cap.
- Buttons disable during saves; create retries are idempotent; failed writes retain the form without claiming success. Navigation/unload warns about unsaved changes; archive requires confirmation.

## Validation executed

- `CODEBATTLE_TEST_NODE=<Playwright bundled node> python3 -m unittest discover -s tests -v`: **30 tests passed**.
- `<Playwright Python> tests/browser_problems.py`: full creation → draft → publish v1 → search/open → publish v2 → original version verification → selector flow passed. Also checks test operations, duplicate, archive, failed-save recovery, discard cancellation, reload, XSS, another account's denial, and mobile overflow.
- `<Playwright Python> tests/browser_auth.py`: passed.
- `<Playwright Python> tests/browser_security.py`: passed.
- `<Playwright Python> tests/browser_runner.py`: passed.
- Node `--check` on new/changed JavaScript, Python `py_compile`, and `git diff --check`: passed.

The active app is plain JavaScript plus standard-library Python; it has no TypeScript compiler, configured lint task, bundler, or production build command. Syntax checks and real runtime tests apply. The unrelated quarantined Next.js MVP was not built, since that would not verify this feature.

## Remaining limits

- Organization visibility is shown disabled; there is no organization/teacher/admin authorization model yet. Private/Public authoring works.
- The server is still an explicitly local preview. Production deployment remains blocked by the existing runtime guard; production infrastructure and multi-tenant load/abuse hardening are separate work.
- Published authoring problems are ready for version-pinned reuse, but are not yet connected to rooms or the existing built-in-only code judge. Those are intentionally separate tasks.
- Authoring forms are retained in memory after failed saves; unsaved data cannot survive a browser crash. Save Draft persists it to SQLite. Hidden content is deliberately not stored in browser storage.
- Archived history is preserved for the owner; future historical room access needs its own authorization.
