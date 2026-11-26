"""What Codex CLI is given at a start, as text: pure functions, nothing read, written or run here.

Two parts, each read in Codex's sources at rust-v0.170.0 (the pre-build checks, C-X1.1):

- `config_toml(...)`: CODEX_HOME/config.toml, written whole at every start. It holds what is the same for every start:
  local only (analytics, feedback, its metrics and its traces off, no update check, no web search, no credentials
  kept, no prompt history), none of its features that reach out or start a daemon, the folders opened from here
  marked untrusted (so a folder's own .codex/ is never loaded and no trust is asked), its commands' environment
  narrowed. Every text is a TOML basic string (json.dumps writes one) and the file is read back with tomllib in the
  tests.
- `overrides(...)`: the -c key=value words of one start, which come above config.toml (C-X1.1m): its sandbox and its
  approvals again (Codex edits config.toml itself, its sandbox mode among it after a setup), the model server, the
  model, its context, and Liminal's MCP where Use… turned it on. A window keeps what its own command says, and lines
  shown earlier keep theirs, whatever a later start writes. Each value is one Codex reads as TOML: a number, a
  boolean, a bare word, or a literal string in single quotes, so no word holds a double quote, which Windows
  PowerShell 5.1 would not hand over as it is (children.not_passed). None holds a secret: a key and a token are
  named by their variables alone."""
from __future__ import annotations

import json
from typing import Iterable, Mapping

from .constants import MCP_NAME, MCP_SECRET, PROVIDER, PROVIDER_NAME, SECRET, STARTUP_S

# the features that reach out by themselves or start what keeps running (C-X1.1, C-X1.4b and C-X1.4c): its shared
# background daemon (which updates itself from chatgpt.com every hour), its plugins (a git sync of openai/plugins at
# each start), its remote plugins and apps, its tool suggestions and its skills' MCP installs
FEATURES_OFF = ("daemon_auto_start", "plugins", "remote_plugin", "apps", "tool_suggest", "skill_mcp_dependency_install")
# what its commands are never given from Codex's own environment (shell_environment_policy.filters, C-X1.1d): every
# pair of Liminal's (the server's key and Liminal's MCP's token among them), and Codex's and OpenAI's own
FILTERED = ("LIMINAL_*", "CODEX_*", "OPENAI_*")


def basic(value) -> str:
    """A TOML basic string (json.dumps writes one: TOML reads JSON's escapes as its own)."""
    return json.dumps(str(value), ensure_ascii=False)


def literal(value, what: str) -> str:
    """A TOML literal string, '...', as a -c value: ValueError in words for a value one cannot hold (a single quote, a
    line break, a control character) or that is empty."""
    text = str(value)
    if not text:
        raise ValueError(f"{what} is empty")
    if "'" in text or any(ord(c) < 32 or ord(c) == 127 for c in text):
        raise ValueError(f"{what} holds a single quote or a control character, which Codex's -c cannot be given "
                         f"as it is: {text!r}")
    return f"'{text}'"


def boolean(value: bool) -> str:
    return "true" if value else "false"


def _table(name: str, pairs: Iterable[tuple[str, str]]) -> list[str]:
    return ["", f"[{name}]", *(f"{k} = {v}" for k, v in pairs)]


def config_toml(*, system: str, sandbox: str = "mxc", network: bool = False, folders: Iterable[str] = ()) -> str:
    """CODEX_HOME/config.toml as every start writes it: the keys that hold for every start (C-X1.1's overview), its
    sandbox as the start's -c words say it too (on Windows `sandbox`, mxc alone; its commands' `network`), the
    `folders` opened from here each marked untrusted (the newest first), `system` "windows" or "linux"."""
    if sandbox != "mxc":
        raise ValueError(f"Codex's sandbox on Windows is mxc here, never {sandbox!r}")
    top = [("approval_policy", basic("on-request")), ("sandbox_mode", basic("workspace-write")),
           ("web_search", basic("disabled")), ("check_for_update_on_startup", "false"),
           ("cli_auth_credentials_store", basic("ephemeral")), ("project_root_markers", "[]"),
           ("allow_login_shell", "false")]
    lines = ["# Written whole by Liminal's Codex CLI plugin at every start: an edit here lasts until the next one.",
             *(f"{k} = {v}" for k, v in top)]
    lines += _table("sandbox_workspace_write", [("network_access", boolean(network))])
    if system == "windows":
        lines += _table("windows", [("sandbox", basic(sandbox))])
    lines += _table("features", [(f, "false") for f in FEATURES_OFF])
    lines += _table("analytics", [("enabled", "false")])
    lines += _table("feedback", [("enabled", "false")])
    lines += _table("otel", [("exporter", basic("none")), ("trace_exporter", basic("none")),
                             ("metrics_exporter", basic("none"))])
    lines += _table("history", [("persistence", basic("none"))])
    policy = [("inherit", basic("core")), ("ignore_default_excludes", "false")]
    if system == "windows":  # (cmd.exe looks in the folder first for a bare name unless it is set: C-X1.4e)
        policy.append(("set", "{ NoDefaultCurrentDirectoryInExePath = " + basic("1") + " }"))
    lines += _table("shell_environment_policy", policy)
    lines += _table("shell_environment_policy.filters", [(basic(p), basic("exclude")) for p in FILTERED])
    for folder in dict.fromkeys(str(f) for f in folders if str(f)):
        lines += _table(f"projects.{basic(folder)}", [("trust_level", basic("untrusted"))])
    return "\n".join(lines) + "\n"


def projects_of(parsed: Mapping) -> list[str]:
    """The folders a config.toml read back marks (any trust: one Codex's own prompt trusted is marked again), in its
    order."""
    table = parsed.get("projects") if isinstance(parsed, Mapping) else None
    if not isinstance(table, Mapping):
        return []
    return [str(k) for k, v in table.items() if isinstance(k, str) and k and isinstance(v, Mapping)]


def _pair(key: str, value: str) -> list[str]:
    return ["-c", f"{key}={value}"]


def overrides(*, system: str, sandbox: str, network: bool, model: str, base_url: str, context: int, keyed: bool,
              mcp: Mapping | None = None) -> list[str]:
    """The -c words of one start, in their order: its approvals and its sandbox (on Windows its mode, `sandbox`: mxc
    alone, never unelevated or elevated), its commands' network (`network`), the model server as Codex's provider
    `liminal` (`base_url`, the Responses API, the key by its variable where one is kept: `keyed`), the model and its
    context, and Liminal's MCP where `mcp` gives it ({"url", "headers", "timeout_s"} or {"argv", "timeout_s"}).
    ValueError in words for a value Codex's -c cannot be given as it is."""
    if sandbox != "mxc":
        raise ValueError(f"Codex's sandbox on Windows is mxc here, never {sandbox!r}")
    words = [*_pair("approval_policy", "on-request"), *_pair("sandbox_mode", "workspace-write"),
             *_pair("sandbox_workspace_write.network_access", boolean(network))]
    if system == "windows":
        words += _pair("windows.sandbox", sandbox)
    words += [*_pair("model_provider", PROVIDER),
              *_pair(f"model_providers.{PROVIDER}.name", literal(PROVIDER_NAME, "the provider's name")),
              *_pair(f"model_providers.{PROVIDER}.base_url", literal(base_url, "the server's address")),
              *_pair(f"model_providers.{PROVIDER}.wire_api", "responses")]
    if keyed:
        words += _pair(f"model_providers.{PROVIDER}.env_key", SECRET)
    words += [*_pair("model", literal(model, "the model's id")), *_pair("model_context_window", str(int(context)))]
    if mcp:
        words += mcp_words(mcp)
    return words


def mcp_words(mcp: Mapping) -> list[str]:
    """Liminal's MCP as one MCP server of Codex's (`liminal`), its -c words: over HTTP (`url`, its `headers`, the token
    by its variable as a bearer token), or the bridge over stdio (`argv`: its command, a whole path, and its words,
    the token's variable among those Codex hands it); its start and its calls' timeouts, on."""
    at = f"mcp_servers.{MCP_NAME}"
    timeout = int(mcp.get("timeout_s") or 0)
    if timeout <= 0:
        raise ValueError("Liminal's MCP gives no timeout for its calls")
    url = str(mcp.get("url") or "")
    if url:
        words = [*_pair(f"{at}.url", literal(url, "the MCP plugin's address")),
                 *_pair(f"{at}.bearer_token_env_var", MCP_SECRET)]
        headers = dict(mcp.get("headers") or {})
        if headers:
            inner = ", ".join(f"{literal(k, 'a header of the MCP plugin')} = {literal(v, f'its header {k}')}"
                              for k, v in headers.items())
            words += _pair(f"{at}.http_headers", "{ " + inner + " }")
    else:
        argv = [str(w) for w in mcp.get("argv") or ()]
        if not argv:
            raise ValueError("Liminal's MCP gives neither an address nor a bridge")
        args = ", ".join(literal(w, "a word of the MCP plugin's bridge") for w in argv[1:])
        words = [*_pair(f"{at}.command", literal(argv[0], "the MCP plugin's bridge")),
                 *_pair(f"{at}.args", f"[{args}]"),
                 *_pair(f"{at}.env_vars", f"[{literal(MCP_SECRET, 'its variable')}]")]
    return [*words, *_pair(f"{at}.startup_timeout_sec", str(STARTUP_S)),
            *_pair(f"{at}.tool_timeout_sec", str(timeout)), *_pair(f"{at}.enabled", "true")]

