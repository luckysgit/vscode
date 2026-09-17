# Working Python practice: Run and Submit

## User workflow

Open Problems → Solve Solo. Write a complete Python program with `input()` and `print()`.

- **Run Code** executes the program using editable standard input and shows stdout/stderr. A successful process is “Run completed”, never “Accepted”.
- Guests can Run code. **Submit Solution** opens signup/login for guests; authentication preserves the visible editor draft and returns to the problem. The customer then clicks Submit. The server rejects guest or missing-session submissions, including attempts to bypass the UI.
- **Submit Solution** checks the built-in Two Sum or Valid Parentheses problem using server-owned examples and fresh private cases. It reports accepted, wrong answer, runtime error, timeout, memory limit, or output limit. Private test input/output/errors are withheld.
- Results are saved to `practice_submissions` in the account SQLite database. `GET /api/submissions` returns only the current account's latest 50 results. This does not yet replace the demo dashboard history or award XP.
- Custom problems support Run; submitting them shows an explicit unsupported message until their definitions are stored on the server.
- Other language options are disabled. This local runner requires macOS with `sandbox-exec` and the Python runtime used by the server. Unsupported platforms fail closed.
- Editor drafts persist in browser storage by account/problem. A browser-storage failure does not prevent running code. These are local drafts, not cross-device storage.

Monaco now fills an absolutely positioned container inside a bounded grid/flex layout. Its measured height cannot expand its parent indefinitely. The input, output, and buttons occupy their own space; mobile uses a single scrolling column.

## Local execution boundary

Submitted code runs in a fresh Python process under a macOS deny-default sandbox. Runtime-library reads and filesystem metadata are allowed; application/private file contents, file writes, outbound network connections, and child processes are denied. The environment contains no inherited application secrets. Hard CPU/file-size/open-file/core limits are set by a trusted launcher before entering the sandbox. A parent watchdog enforces a three-second wall deadline and 16KB combined output; a semaphore permits two executions at a time.

This Mac rejects `RLIMIT_AS` and `RLIMIT_DATA`. The parent therefore samples RSS and kills a process above 256MiB; this can overshoot between samples and is **not a hard memory boundary**. This is a loopback-only development runner, not public multi-tenant infrastructure. Production remains blocked. A production rollout requires a separate container/VM runner with hard memory/process limits, a durable queue, fair scheduling, abuse controls, and platform-specific security review. No unsandboxed fallback exists.

## Verification

- Backend: 24 tests cover accounts, actual grading, per-user saved results, output/CPU limits, file/network/process denial, startup guards, and HTTP protection.
- Browser: `tests/browser_runner.py` uses real Monaco and real execution with a temporary database. Checks button visibility and stable editor dimensions, stdout, wrong answer, accepted result, syntax error, timeout recovery, draft reload, and narrow-screen layout.
- Existing browser account and XSS regression suites remain applicable.

The earlier audit and P0 batch document describe historical snapshots. This implementation replaces their “grading unavailable” limitation only for local Python practice.
