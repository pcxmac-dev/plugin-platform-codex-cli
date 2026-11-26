"""What the Codex CLI plugin pins and every outside address it names (the library names none: A-revisions 0).

The pins are read from what Codex's maker publishes about its release, never from a download (A-revisions 3), on
2026-11-18 (the pre-build checks, C-X1): GitHub's record of the release
(api.github.com/repos/openai/codex/releases/tags/rust-v0.170.0) and its release page's list of files, the two alike.

- Codex CLI 0.170.0: the tag rust-v0.170.0 of 2026-11-18, the newest release when this plugin was planned. Each file's
  sha256 is the digest GitHub's record gives it (the release's codex-package_SHA256SUMS says the same of its
  packages). The release is not marked immutable, so a file replaced there would no longer match its pinned sha256
  and is refused.
- Its package for each system it is pinned for here (TARGETS), codex-package-<target>.tar.gz: bin/ (codex, its code
  mode host, its exec server), codex-resources/ (on Windows the command runner and the setup helper its sandboxes
  use; on Linux its bubblewrap, bwrap, whose digest Codex checks) and codex-path/rg, beside codex-package.json
  (scripts/codex_package/README.md at the tag). Every Linux build is musl, so the one package runs on any Linux. The
  .tar.zst copies, the standalone codex-<target>.exe.zip (no helpers beside it), the Windows sandbox service (the
  elevated sandbox's, never used) and npm's package are not used. Only the x86-64 packages' sums were read: the ARM64
  ones are not pinned in this release.
- It is fetched from github.com, which sends a release's file on to release-assets.githubusercontent.com.

What Codex is given at a start is read in its sources at the tag (codex-rs/) and on its documentation
(learn.chatgpt.com, where developers.openai.com/codex now sends), each step named where it is used (files.py, the
plugin's launch)."""
from __future__ import annotations

import re

# -- Codex CLI ---------------------------------------------------------------------------------------------------------
PIN = "0.170.0"  # a pin moves only with a release of this plugin
TAG = "rust-v0.170.0"
RELEASED = "2026-11-18"
LICENCE = "Codex CLI: Apache-2.0 (OpenAI)."
REPOSITORY = "openai/codex"
FILES = "https://github.com/openai/codex/releases/download/rust-v0.170.0/"
ASSET_HOSTS = ("release-assets.githubusercontent.com",)  # where github.com sends a release's file on to
HOSTS = ("github.com", "release-assets.githubusercontent.com")  # what Install downloads from
# its package for each system, as its release names it: (archive, bytes, sha256)
TARGETS: dict[str, tuple[str, int, str]] = {
    "windows-x64": ("codex-package-x86_64-pc-windows-msvc.tar.gz", 210098091,
                    "6ff4b22c63645ffd83aed9b722cbb0b9e5b79dc6e8916f50e362b3015fb327a9"),
    "linux-x64": ("codex-package-x86_64-unknown-linux-musl.tar.gz", 193641516,
                  "a77ff87be7ba809d715728270a78f5ce3527dc07529416d1ef8929b90b8475eb"),
}
# what its processor is called, by what Python says (platform.machine()), in this plugin's words
ARCHES = {"amd64": "x64", "x86_64": "x64", "x64": "x64", "arm64": "arm64", "aarch64": "arm64"}
MANIFEST = "codex-package.json"  # at the package's root, beside bin/
PROGRAM = {"windows": ("bin", "codex.exe"), "linux": ("bin", "codex")}
# the helpers its sandbox needs, beside bin/ (Codex finds them in <package>/codex-resources when it runs from bin):
# Windows' command runner (the unelevated sandbox's; MXC runs codex.exe itself as its helper), Linux's bubblewrap
HELPERS = {"windows": (("codex-resources", "codex-command-runner.exe"),), "linux": (("codex-resources", "bwrap"),)}

# -- what it does by itself --------------------------------------------------------------------------------------------
# what its terminal screen fetches at every start, with no setting to stop it (codex-rs/tui/src/tooltips.rs: a GET of
# 2 s at the most, called with no gate; tui.show_tooltips does not stop it)
ANNOUNCEMENT = "https://raw.githubusercontent.com/openai/codex/main/announcement_tip.toml"

# -- where it keeps what it keeps --------------------------------------------------------------------------------------
# CODEX_HOME: <home>/config/codex. It holds config.toml (written whole at each start), its transcripts (sessions/ and
# archived_sessions/: every session's rollout, .jsonl, recompressed to .jsonl.zst after 7 days, never removed by
# Codex), its SQLite databases (its logs among them, capped by Codex at 10 MiB a partition, with no switch to turn
# them off), its caches and its helpers' folders. Never a .env: Codex reads one there into its environment.
CODEX_HOME = "codex"
TRANSCRIPTS = ("sessions", "archived_sessions")
TRANSCRIPT = re.compile(r"\.jsonl(?:\.zst)?$")
TRANSCRIPTS_KEPT = 50  # the newest transcripts kept at each Open… (the user, 2026-11-25: "the plugin prunes them")
TRANSCRIPTS_BYTES = 200_000_000  # and no more than this many bytes of them, the newest first
TRANSCRIPTS_LOOKED = 100_000  # files looked at, at the most, in one pruning
PROJECTS_KEPT = 256  # folders kept untrusted in config.toml, the newest first
# Codex's system files beneath (config.toml) and above (requirements.toml: managed settings, which can force its
# elevated sandbox) what a start is told, on Linux; on Windows the requirements' path a policy names
SYSTEM_FILES = ("/etc/codex/config.toml", "/etc/codex/requirements.toml")
POLICY_KEY = "SOFTWARE\\Policies\\OpenAI\\Codex"  # HKLM: RequirementsPath, where it is set
POLICY_VALUE = "RequirementsPath"

# -- its sandbox -------------------------------------------------------------------------------------------------------
SANDBOXES = ("mxc", "unelevated")  # [windows] sandbox, as offered: never "elevated", never left unset
# the Windows builds Microsoft's MXC came with (the Windows sandbox page: 24H2 26100.9278, 25H2 26200.9278 "or later"):
# a build's lowest update (UBR) that has it. Codex itself decides by a probe at its start, never by the build
MXC_BUILDS = {26100: 9278, 26200: 9278}
VERSION_KEY = "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion"  # HKLM: CurrentBuild (text) and UBR (a number)
# what Linux says of unprivileged user namespaces, which bubblewrap needs (read where they exist, never written)
USERNS = {"max": "/proc/sys/user/max_user_namespaces", "clone": "/proc/sys/kernel/unprivileged_userns_clone",
          "apparmor": "/proc/sys/kernel/apparmor_restrict_unprivileged_userns"}

# -- what Codex is given -----------------------------------------------------------------------------------------------
PROVIDER = "liminal"  # its model provider's id (Codex's own ids, openai, ollama and lmstudio among them, are refused)
PROVIDER_NAME = "Liminal"
SECRET = "LIMINAL_SERVER_KEY"  # the one variable a kept key reaches Codex by (its provider's env_key names it)
MCP_SECRET = "LIMINAL_MCP_TOKEN"  # the variable Liminal's MCP's token reaches it by (bearer_token_env_var, env_vars)
MCP_NAME = "liminal"  # the name Liminal's MCP is given among its MCP servers
STARTUP_S = 30  # an MCP server's start, at the most (Codex's own default in code: 30 s)
FEWEST = 8_192  # the least context Codex is started with
MOST = 2_000_000  # the most context typed under Use…
ADVISED = 65_536  # what Ollama's page on Codex advises at the least
# names never handed to Codex from the platform's environment: the hosted providers' keys and settings (the harnesses'
# list), every CODEX_* (its home, its SQLite home, its built-in Ollama's address, an exec server's URL) and every
# OPENAI_* (the Codex plugin's OpenAI key among them); with every pair of Liminal's, which the harness base adds
DROP = ("ANTHROPIC_*", "OPENAI_*", "AZURE_OPENAI_*", "OPENROUTER_*", "GEMINI_*", "GOOGLE_API_KEY",
        "GOOGLE_GENERATIVE_AI_API_KEY", "MISTRAL_*", "GROQ_*", "DEEPSEEK_*", "XAI_*", "COHERE_*", "TOGETHER_*",
        "FIREWORKS_*", "PERPLEXITY_*", "HF_TOKEN", "OLLAMA_*", "LM_STUDIO_*", "HOSTED_VLLM_*", "LITELLM_*", "OTEL_*",
        "OPENCODE_*", "AIDER_*", "CONTINUE_*", "GOOSE_*", "CODEX_*")
# the hosts of the pages its cards link (people's pages, never fetched)
MAKERS = ("learn.chatgpt.com", "github.com", "platform.openai.com", "docs.ollama.com")
