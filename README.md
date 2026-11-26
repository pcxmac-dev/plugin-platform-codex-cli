# plugin-platform-codex-cli

Codex CLI for Liminal: OpenAI's open-source coding agent in the terminal, its package installed pinned into the
platform's own folder, configured against one instance of an inference plugin's that speaks the Responses API, and
opened in a folder you pick, its commands in its sandbox and every step beyond it asked first. It is not OpenAI's
service: that is the Codex plugin's. One call Codex makes by itself is not switched off: its terminal screen fetches
an announcement from GitHub at every start (below).

The user's words: 2026-11-18, "top 4 inference engines, top 4 agentic harnesses (open source)", "all platform", "both
linux and windows compatibility"; 2026-11-25, answer 5, its sandbox on Windows "mxc, never elevated" and on Linux its
bundled bubblewrap; answer 6, its start-up fetch and its saved transcripts "said plainly on its page; the plugin
prunes old transcripts"; answer 8, the ports a tool opens by itself said on its page.

## What it does

A harness (`liminal_libs.machines.harness.Harness`, liminal-libs 1.66.0, plugin API 2.2), drawn under the platform's AI
plugins, Harnesses, at 523 (OpenCode 520, Aider 521, Continue 522, Pi 524, goose 525), its icon Codex's own mark
(`codexcli`), not the OpenAI knot of the Codex plugin. It is middleware of that kind: the standard interface of a
harness, with no hook of its own. Valid wherever it runs: what a system lacks is a fact and a refusal in words.

- **Install, Update, Uninstall**, each from the page, Install a job with its size, its hosts and its licence said first
  and the licence accepted in a second confirmation. It downloads Codex CLI 0.170.0's package for this system, from
  `github.com` (sent on to `release-assets.githubusercontent.com`), pinned by name, size and sha256 as GitHub's record
  of the release gives them (the release is not marked immutable: a file replaced there no longer matches and is
  refused):
  - Windows x64: `codex-package-x86_64-pc-windows-msvc.tar.gz` (210 MB);
  - Linux x64: `codex-package-x86_64-unknown-linux-musl.tar.gz` (194 MB), a musl build that runs on any Linux.
  ARM64's packages are not pinned in this release: there the page says so. The package is unpacked into
  `app/0.170.0` as it is laid out, `bin/` beside `codex-resources/`, which holds its sandbox's helpers (Windows'
  command runner, Linux's `bwrap`): a package without them installs nothing. Never run from here: its install
  scripts, npm, `codex login`, `codex mcp add`, `codex sandbox setup`. A Codex of yours (on PATH, `~/.codex`) is left
  as it is, never run.
- **Use…, Open…, Command…** (the base's): one inference plugin's instance and its model, with Codex's options
  (Context; Sandbox, on Windows: mxc alone; Network: off or on; Liminal's MCP). There is no approvals choice:
  `on-request` is written at every start (Codex no longer takes `untrusted`, `on-failure` is deprecated, and `never`
  is not offered). Open… opens `codex --no-daemon` in a window of its own where there is a desktop, the lines to paste
  elsewhere.
- **Only the Responses API.** Codex asks a model server for nothing else (`wire_api = "responses"`; `chat` is no
  longer supported). An instance is offered only when its plugin's serving row says it speaks `responses`
  (liminal-libs 1.66.0's families): LMDeploy's rows do not, and neither does a plugin that says nothing.

### How Codex is started

- **CODEX_HOME** is the plugin's own, `<home>/config/codex`. Its `config.toml` is written whole at every start
  (`files.config_toml`), what holds for every start:
  - `approval_policy = "on-request"`, `sandbox_mode = "workspace-write"`, `[sandbox_workspace_write] network_access`;
  - on Windows `[windows] sandbox`, always written (with no mode Codex prefers its elevated one), `mxc` alone, never
    `unelevated` or `elevated`; no `prefer_mxc`;
  - local only: `[analytics]` and `[feedback]` off, `[otel]` exporter, trace and metrics exporters `none`,
    `check_for_update_on_startup = false`, `web_search = "disabled"`, `cli_auth_credentials_store = "ephemeral"`
    (nothing kept, the keyring never read), `[history] persistence = "none"`;
  - `[features]` off: `daemon_auto_start` (its shared background server, which would update itself from
    chatgpt.com every hour), `plugins` (a git sync of openai/plugins at each start), `remote_plugin`, `apps`,
    `tool_suggest`, `skill_mcp_dependency_install`;
  - its commands' environment: `inherit = "core"`, `ignore_default_excludes = false` (names holding KEY, SECRET or
    TOKEN left out), filters excluding `LIMINAL_*`, `CODEX_*` and `OPENAI_*`; on Windows
    `NoDefaultCurrentDirectoryInExePath` set, so `cmd.exe` never runs a program from the folder by a bare name;
  - `project_root_markers = []`, `allow_login_shell = false`, and every folder opened from here marked `untrusted`,
    so a folder's own `.codex/` (its configuration, hooks and rules) is never loaded and no trust is asked. A trust
    given in Codex itself lasts until the next start, which writes the file again.
  A `.env` beside it is removed before a start, since Codex reads one into its environment.
- **Its command line** carries what one start is told (`files.overrides`), above `config.toml`: its approvals, its
  sandbox and its network again (Codex edits `config.toml` itself), the instance as a provider of its own
  (`liminal`: its address, `wire_api = "responses"`, the key's variable where one is kept), the model and its
  context (`model_context_window`), and Liminal's MCP where Use… turned it on. A window keeps what its own command
  says, and lines shown earlier keep theirs. Each value is a number, a boolean, a bare word or a literal string in
  single quotes, so no word holds a double quote, which Windows PowerShell 5.1 would not hand over as it is; a value
  that cannot be given so is refused in words.
- **Its environment**: `CODEX_HOME`, the instance's key in `LIMINAL_SERVER_KEY` alone where one is kept, a PATH
  without relative entries. Every pair of Liminal's, every `CODEX_*` and `OPENAI_*` (the Codex plugin's OpenAI key
  among them) and the hosted providers' keys are dropped from what it inherits.
- **Liminal's MCP** (off unless Use… turns it on): over HTTP on the platform's route where the MCP plugin offers it
  (`url`, `bearer_token_env_var = "LIMINAL_MCP_TOKEN"`, its header), else through the MCP plugin's bridge as a stdio
  server (`command`, `args`, `env_vars = ["LIMINAL_MCP_TOKEN"]`); `tool_timeout_sec` is the MCP plugin's hold and a
  minute more. Each window has a token of its own, in Codex's environment alone, ended once the window is gone; its
  commands are never given it.

### Its sandbox

- **Windows, MXC** (the default): Microsoft's MXC needs no administrator, no account and no firewall rule. With its
  commands' network off they reach neither the network nor this machine's own addresses, so not the platform (MXC's
  policy denies the host's loopback). It came with Windows 11 24H2 26100.9278 and 25H2 26200.9278: the page reads this
  Windows' build from the registry (`CurrentBuild`, `UBR`) and says it against them; a later build, like this PC's
  26300 (26H2), is expected to have it, not confirmed: Codex decides by its own probe. Where MXC is missing every
  command fails, with no other sandbox in its place, and the page says so as a problem.
- **Never the unelevated sandbox** (the user's answer 5, "mxc, never elevated"): with its commands' network off it
  only points them at a proxy that is not there, so a program that ignores proxy settings reaches the network, and
  every one reaches this machine's own addresses, the platform's among them, whose API runs what you can run, outside
  the sandbox. It is not offered under Use…, and a choice of it kept from before starts mxc.
- **Never the elevated sandbox**: its setup asks for administrator rights and adds accounts, firewall rules and
  policy changes across the whole system, which an uninstall could not take back. It is never chosen, set up or
  offered from here, and with `mxc` Codex never offers it itself.
- **Linux, bubblewrap**: the first `bwrap` on PATH, else the package's own, which needs unprivileged user namespaces.
  The page reads `/proc/sys/user/max_user_namespaces`, `/proc/sys/kernel/unprivileged_userns_clone` and
  `/proc/sys/kernel/apparmor_restrict_unprivileged_userns` where they exist, and says as a problem a Linux that
  allows none, has them off, or restricts them with AppArmor (Ubuntu 24.04's) while no `bwrap` is on PATH: changing
  that is root's.

### What it still does by itself, and what it keeps

- **Its start-up fetch**: its terminal screen fetches
  `https://raw.githubusercontent.com/openai/codex/main/announcement_tip.toml` from GitHub at every start (2 s at the
  most), from your address. No setting of Codex 0.170.0 turns it off. The page says so plainly.
- **Its transcripts**: Codex saves every session's transcript (your prompts, its answers, the commands it ran and what
  they said) under `CODEX_HOME/sessions` and `archived_sessions`, and no setting of its terminal screen turns this
  off. The plugin keeps the newest 50 (200 MB at the most) and removes older ones as each Open… opens a window, while
  none of its windows is open; Command… removes nothing. Codex also keeps a log database there, which it caps itself
  (10 MiB a part) and nothing turns off. No prompt history is kept.
- **Its ports**: none opened by itself here. Its own sign-in (`codex login`, never run from here) would listen on
  `127.0.0.1:1455`, an MCP server's sign-in on a port of the system's choosing (not used: Liminal's MCP takes a token),
  and its network proxy (off) on this machine's own addresses.
- **Codex's system files**: on Linux `/etc/codex/config.toml` (read beneath what a start is told) and
  `/etc/codex/requirements.toml` (above it: they can choose its sandbox), on Windows the requirements file a policy
  names (`HKLM\SOFTWARE\Policies\OpenAI\Codex`, `RequirementsPath`): each is said as a problem where it is there.

## Its API

Four cards (`apis.py`, read on 2026-11-18): Codex CLI (its README, the configuration reference, the sandboxing, Windows
sandbox, approvals and MCP pages, its release); its configuration (config.toml and the release's
`config-schema.json`); its release's files; the Responses API as local servers speak it.

## Its hooks

The harness base's alone: `present`, `status`, `refresh`, `install`, `uninstall`, `use`, `open`, `command`,
`ask_models`. Its changes (`install`, `uninstall`, `use`, `open`) are asked from its page alone (liminal-libs 1.99.0).

## From the command line

    python -m plugin_platform_codex_cli status
    python -m plugin_platform_codex_cli command [FOLDER]

Its reads alone: `status` prints its Main as JSON; `command` prints the lines that start Codex in FOLDER against
what Use… keeps (without the platform it says so). Install, Uninstall, Use… and Open… are the page's.

## Where it is built

A local repository (`pcxmac-dev`), built 2026-11-26 against liminal-libs 1.99.0 (`22515e3`); its floor is 1.66.0.

## What was read in Codex's sources

At the tag `rust-v0.170.0` and on learn.chatgpt.com (the pre-build checks, C-X1): every `config.toml` key above and
its values (`approval_policy` rejects an explicit `untrusted`; `[windows]` holds only `sandbox` and `allow_mxc`;
`shell_environment_policy.filters` cannot be mixed with the legacy lists; `wire_api = "chat"` is rejected); the `-c`
syntax (its value read as TOML, else as text); the package's layout and the helpers it holds; that with
`windows.sandbox = "mxc"` Codex never offers or starts the elevated setup; MXC's policy, which denies the host's
loopback with the network off, and bubblewrap's network namespace; what `CODEX_HOME` holds; the announcement fetch,
which has no switch; that `--no-daemon` and `daemon_auto_start = false` keep its shared server from starting; its MCP
client (2025-06-18, plain JSON answers, a 405 to GET skipped); the environment it gives a stdio MCP server (empty but
for a fixed list and `env_vars`).

## Not yet confirmed by a real run

- The package's layout as it unpacks (no package was downloaded): `bin/` and `codex-resources/` at its root, or under
  one folder, which the install moves up.
- MXC on this PC's build (26300, 26H2) and its probe; that a command with its network off cannot reach
  127.0.0.1:8775 in MXC and in bubblewrap.
- The form of a Windows folder's key under `[projects]` (the plain absolute path is written), and that the terminal
  screen asks no trust for a folder marked untrusted.
- That no shared background server starts with `--no-daemon`, `daemon_auto_start = false` and the `-c` words, and
  that `CODEX_HOME` never gains `app-server-daemon/` or `packages/`.
- That a window still open keeps what its own command says when a later start writes `config.toml` again.
- That a TOML literal string after `-c` is read as text for every value written so (the `-c` parser read at the tag).
- Liminal's MCP with Codex: the route's answers and the bridge.
- The bundled `bwrap` in the user's WSL Ubuntu, and Ubuntu's AppArmor profile for `/usr/bin/bwrap`.
- Which model servers serve `/v1/responses` well enough for Codex (Ollama 0.13.3+ and vLLM by their makers' word).

## Tests

    python -m pytest -q

Stand-ins only (`tests/conftest.py`): no process, socket or name lookup is reached; the registry, `/proc`, Codex's
system files and the temporary folder are stand-ins; archives are made in memory and unpacked for real.
