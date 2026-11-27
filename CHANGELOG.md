# Changelog

## 0.1.1 (2026-11-27)

The review of item 14 (plugins-os-ai P3-5): a transcript written within the last day is never pruned.

- **Before**, the pruning at each Open… checked only for the windows this plugin opened. A Codex started from
  Command…'s lines (the only way where there is no desktop: Linux, WSL) is no such window, and on Linux a file it
  holds open is unlinked all the same: its live transcript could go at the next Open… (past the newest 50, or alone
  past the 200 MB kept) and be lost when Codex exits.
- **Now** a transcript written within a day of now (`TRANSCRIPTS_FRESH_S`), or later than now, is kept and counted
  among the newest; the older ones are pruned as before. The page says so.
- Tests: `tests/test_launch.py`, on Windows and on Linux, a transcript written a minute ago with no window open,
  alone past the bytes kept, stays.

## 0.1.0 (2026-11-26)

The first release: Codex CLI as one of the platform's top four open-source harnesses (the user, 2026-11-18: "top 4
inference engines, top 4 agentic harnesses (open source)", "both linux and windows compatibility"; 2026-11-25, answers
5, 6 and 8: its sandbox on Windows "mxc, never elevated", on Linux its bundled bubblewrap; its start-up fetch and its
saved transcripts said plainly on its page, old transcripts pruned; the ports it opens by itself said). A harness on
liminal-libs 1.66.0's AI bases (`Harness`, plugin API 2.2), `SECTION = "ai"`, `GROUP = "harness"`, `order = 523`,
`ICON = "codexcli"`: the standard interface of a harness, with no hook of its own. Needs liminal-libs>=1.99.0, whose
harness base asks its changes only from the page.

- **Install, Update, Uninstall** from the page: Codex CLI 0.170.0's package for this system (Windows x64; Linux x64,
  a musl build for any Linux), pinned by name, size and sha256 as GitHub's record of the release gives them,
  downloaded as a job with its licence (Apache-2.0) accepted first, checked, and unpacked into the plugin's own
  folder (`app/0.170.0`) as it is laid out, its sandbox's helpers looked for. ARM64 is said as not pinned. A Codex of
  yours is a fact, never run or touched. Its install scripts, npm and `codex sandbox setup` are never run.
- **Use…, Open…, Command…** (the base's): one inference plugin's instance that speaks the Responses API, its model,
  and Codex's options (Context; Sandbox on Windows: mxc alone, never unelevated or elevated; Network: off or on;
  Liminal's MCP); `codex --no-daemon` in a window of its own, the lines to paste elsewhere. Approvals are
  `on-request`, always.
- **Configured at launch**, nothing written into a Codex of yours: its own `CODEX_HOME`, whose `config.toml` is written
  whole at every start (local only, its features that reach out or keep running off, its commands' environment
  without a pair of Liminal's, every folder untrusted, a `.env` beside it removed), and each start's choice on its
  own command line (`-c`), so a window keeps its own and lines shown earlier keep theirs. Liminal's MCP over HTTP
  with a bearer token by its variable, or through the bridge.
- **Its transcripts**: the newest 50 kept (200 MB at the most), older ones removed as Open… opens a window while none
  of its windows is open.
- **Before you use it**: what it does as you, its sandbox and what this machine says of it (the Windows build against
  the ones MXC came with, read from the registry; bwrap on PATH and what /proc says of user namespaces on Linux), its
  start-up fetch, its transcripts, what stays local, its ports, a folder's `.codex/`, the model, what it shares with a
  Codex of yours, its configuration; a key, plain http and Liminal's MCP where they apply. As problems: a Windows
  without MXC while mxc is chosen, a Linux whose user namespaces bubblewrap cannot use, Codex's system and
  requirements files, its folder inside the temporary folder.
- **NEEDS** in the needs plan's getattr idiom: architecture x86-64, a desktop, the Windows build MXC needs, bwrap,
  the internet for its install; each a part.
- Four API cards: Codex CLI, its configuration, its release's files, the Responses API.
