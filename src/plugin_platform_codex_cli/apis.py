"""What the Codex CLI plugin attaches to (plugin API 2.2; the user, 2026-11-11: "each plugin should reflect the the API
its attached to, and present links that provide documentation ... it should also expose more of what the API is
about"): Codex CLI itself, the command it starts; its configuration file, which the plugin writes; the file Install
downloads; and the Responses API, the one a model server must speak for it. Each part of each is named with what the
plugin does with it, each call it makes with what it makes it for, and the notable calls it does not make. The pages
are the makers' own (Codex's documentation, its release at rust-v0.170.0, its repository; OpenAI's API reference;
Ollama's page on it), read on 2026-11-18 (liminal_libs.sources.apis.dead_links checks them,
LIMINAL_VENDOR_PAGES=1)."""
from __future__ import annotations

from liminal_libs.sources.apis import Api, Area, Call, Link

from .constants import ANNOUNCEMENT, PIN, TAG

VERIFIED = "2026-11-18"
CODEX = "Codex CLI"
CONFIG = "Codex configuration (config.toml)"
DOWNLOADS = "Codex releases"
RESPONSES = "The Responses API as local servers speak it"

_DOCS = "https://learn.chatgpt.com/docs/"
_REPO = "https://github.com/openai/codex"
_RELEASE = _REPO + "/releases/tag/" + TAG
_README = _REPO + "/blob/" + TAG + "/README.md"
_REFERENCE = _DOCS + "config-file/config-reference"
_ADVANCED = _DOCS + "config-file/config-advanced"
_SCHEMA = _REPO + "/releases/download/" + TAG + "/config-schema.json"
_SANDBOXING = _DOCS + "sandboxing"
_WINDOWS = _DOCS + "windows/windows-sandbox"
_SECURITY = _DOCS + "agent-approvals-security"
_MCP = _DOCS + "extend/mcp?surface=cli"
_OPENAI = "https://platform.openai.com/docs/api-reference/responses"
_OLLAMA = "https://docs.ollama.com/api/openai-compatibility"

CODEX_API = Api(
    name=CODEX, maker="OpenAI", kind="command",
    about=("Codex CLI, OpenAI's open-source coding agent in the terminal (not OpenAI's service: that is the Codex "
           "plugin): its agent reads the folder, runs commands in its sandbox and edits files through a model of a "
           "provider's, with MCP servers for more tools. The plugin starts its own pinned copy in the folder you pick "
           "against one model server's instance, as a provider of its own that speaks the Responses API, its "
           "commands in its sandbox (MXC on Windows, never its unelevated or elevated one; "
           "bubblewrap on Linux) with their network off unless you choose otherwise, asking before going beyond it. "
           "Its analytics, feedback, metrics, update check, web search, plugins and shared background server are "
           f"off; one call it makes by itself is not: its terminal screen fetches {ANNOUNCEMENT} at every start."),
    base="codex (app/0.170.0/bin/codex.exe on Windows, app/0.170.0/bin/codex on Linux, in the plugin's folder)",
    version=f"{PIN}, the tag {TAG} of 2026-11-18",
    auth=("none of its own toward the model server but the server's key, where one is kept, handed over in its "
          "environment (LIMINAL_SERVER_KEY, which its provider's env_key names) and sent as a bearer token"),
    limits=("its context is the one it is told (model_context_window); an MCP server is given 30 s to start, and a "
            "call the MCP plugin's hold and a minute more"),
    costs="free (Apache-2.0); OpenAI's own service, which it can use, is paid, and is never given from here",
    links=(
        Link("Codex CLI's README", _README, "docs"),
        Link("Configuration reference", _REFERENCE, "reference"),
        Link("Advanced configuration", _ADVANCED, "reference"),
        Link("Sandboxing", _SANDBOXING, "guide"),
        Link("The Windows sandbox", _WINDOWS, "guide"),
        Link("Approvals and security", _SECURITY, "guide"),
        Link("MCP in Codex", _MCP, "guide"),
        Link("Codex CLI 0.170.0", _RELEASE, "changelog"),
        Link("openai/codex", _REPO, "source"),
        Link("Its licence (Apache-2.0)", _REPO + "/blob/" + TAG + "/LICENSE", "terms"),
    ),
    areas=(
        Area("Its terminal screen", "codex: a session in the terminal, in the folder it is started in", _README,
             covered=("started in the folder you pick, in a window of its own or by the lines you paste, with "
                      "--no-daemon and its settings for that start on its own command line (-c)")),
        Area("Its sandbox", "read-only, workspace-write or full access; on Windows MXC, unelevated or elevated; on "
                            "Linux bubblewrap; its commands' network", _SANDBOXING,
             covered=("workspace-write; on Windows mxc, never unelevated or elevated; on Linux "
                      "bubblewrap; its commands' network off unless you choose it on")),
        Area("Approvals", "when it asks before acting: on-request, never, or by kind", _SECURITY,
             covered="on-request, written at every start; never is not offered"),
        Area("Model providers", "the providers it may use: a base URL, the Responses API, a key's variable",
             _REFERENCE,
             covered=("one provider of the plugin's (liminal) for each start: the instance's address, the Responses "
                      "API, a key named by its variable and never written")),
        Area("MCP servers", "the MCP servers it starts (stdio) or reaches (streamable HTTP)", _MCP,
             covered=("Liminal's MCP alone, where Use… turns it on: over HTTP with a bearer token by its variable, or "
                      "the MCP plugin's bridge; none of a configuration file's")),
        Area("Its transcripts and logs", "each session's rollout under CODEX_HOME/sessions, its log database, its "
                                         "prompt history", _ADVANCED,
             covered=("its own folder (CODEX_HOME); no prompt history; the newest 50 transcripts kept (200 MB at the "
                      "most), older ones removed as Open… opens a window")),
        Area("What it reaches by itself", "its announcement, its update check, its analytics and metrics, its "
                                          "plugins' sync, its shared background server", _ADVANCED,
             covered=("all off but the announcement, which no setting turns off: said on the page")),
        Area("Sign-in", "codex login: ChatGPT or an OpenAI key, kept in a file or the keyring", _README),
        Area("Automation", "codex exec: instructions run without its terminal screen", _README),
    ),
    calls=(
        Call("codex --no-daemon -c KEY=VALUE ...", "its terminal screen in the working folder, its settings for that "
                                                   "start above its config.toml", "Its terminal screen",
             used="what Open… starts, in the folder you pick (Command… shows the same lines)", docs=_REFERENCE,
             writes=True),
        Call(f"GET {ANNOUNCEMENT}", "its announcement, fetched by its terminal screen at every start, which no "
                                    "setting stops", "What it reaches by itself"),
        Call("codex exec", "instructions run without its terminal screen", "Automation", docs=_README, writes=True),
        Call("codex login", "a sign-in to OpenAI, its credentials kept", "Sign-in", docs=_README, writes=True),
        Call("codex mcp add", "an MCP server added to its configuration", "MCP servers", docs=_MCP, writes=True),
        Call("codex sandbox setup", "its elevated sandbox set up for Windows, as administrator", "Its sandbox",
             docs=_WINDOWS, writes=True),
    ),
    verified=VERIFIED,
)

CONFIG_API = Api(
    name=CONFIG, maker="OpenAI", kind="file",
    about=("Codex's configuration file, CODEX_HOME/config.toml, as its release's config-schema.json describes it. "
           "The plugin writes it whole at every start in its own CODEX_HOME: local only, its sandbox and approvals, "
           "its commands' environment without a pair of Liminal's, every folder opened from here untrusted. What "
           "one start is told comes above it, on its command line."),
    base="<the plugin's folder>/config/codex/config.toml",
    version=f"Codex CLI {PIN}'s schema",
    auth="none: a file of the plugin's own",
    limits="none",
    costs="free",
    links=(
        Link("Configuration reference", _REFERENCE, "reference"),
        Link("Advanced configuration", _ADVANCED, "reference"),
        Link("config-schema.json at 0.170.0", _SCHEMA, "spec"),
    ),
    areas=(
        Area("Local only", "analytics, feedback, otel, check_for_update_on_startup, web_search, "
                           "cli_auth_credentials_store, history", _REFERENCE,
             covered="each off, written at every start"),
        Area("Features", "[features]: the daemon, plugins, remote plugins, apps, tool suggestions", _REFERENCE,
             covered="each off, written at every start"),
        Area("Its commands' environment", "[shell_environment_policy]: inherit, its default excludes, filters, set",
             _ADVANCED,
             covered=("the core variables alone, names holding KEY, SECRET or TOKEN left out, every LIMINAL_*, "
                      "CODEX_* and OPENAI_* excluded")),
        Area("Projects", "[projects]: a folder's trust, which gates its .codex/", _ADVANCED,
             covered="every folder opened from here marked untrusted; project_root_markers empty"),
    ),
    calls=(
        Call("write config.toml", "the file written whole, a part file renamed", "Local only",
             used="at every start, before Codex reads it", writes=True),
    ),
    verified=VERIFIED,
)

DOWNLOADS_API = Api(
    name=DOWNLOADS, maker="OpenAI (its releases on GitHub)", kind="feed",
    about=("What Install downloads, pinned in the plugin by its name, its size and its sha256 and checked against both "
           "before it is used: Codex CLI's package for this system, from its release on GitHub."),
    base=f"github.com/openai/codex/releases/download/{TAG}/",
    version=f"Codex CLI {PIN}",
    auth="none: public files",
    limits="none named; a download is asked only when you click Install… or Update…",
    costs="free: Apache-2.0",
    links=(
        Link("Codex CLI 0.170.0 and its files", _RELEASE, "changelog"),
        Link("Codex CLI's README", _README, "docs"),
    ),
    areas=(
        Area("Its packages", "codex-package-<target>.tar.gz and .tar.zst: bin/, codex-resources/ (its sandbox's "
                             "helpers) and codex-path/rg", _RELEASE,
             covered=("this system's .tar.gz, downloaded as a job, checked against its pinned sha256, unpacked into "
                      "app/0.170.0 as it is laid out")),
        Area("Its other files", "the standalone programs, the Windows sandbox service, bwrap alone, the sums file, "
                                "the Linux packages' Sigstore bundles, config-schema.json", _RELEASE),
        Area("npm and its install scripts", "@openai/codex and the scripts that fetch the newest release", _README),
    ),
    calls=(
        Call("GET codex-package-<target>.tar.gz", "Codex's package for one system, from its release on GitHub",
             "Its packages", used="Install and Update, as a job", docs=_RELEASE),
        Call("npm install -g @openai/codex", "its npm package, the newest release", "npm and its install scripts",
             docs=_README, writes=True),
    ),
    verified=VERIFIED,
)

RESPONSES_API = Api(
    name=RESPONSES, maker="OpenAI (the API); each model server's maker (what it serves of it)", kind="rest",
    about=("OpenAI's Responses API (POST /v1/responses), the one API Codex CLI asks a model server for: its chat "
           "completions API is no longer supported. A local server serves it as far as its maker made it: Ollama "
           "0.13.3 and newer and vLLM do; llama.cpp's is reported unreliable with Codex; LMDeploy has none. Each "
           "model server's plugin says what its instances speak, and the plugin starts Codex against one that says "
           "it speaks this."),
    base="<the instance's OpenAI-compatible address>/responses",
    version="as each server serves it",
    auth="the server's key, where one is kept, as a bearer token",
    limits="the server's",
    costs="free on a local server",
    links=(
        Link("The Responses API", _OPENAI, "reference"),
        Link("Ollama's OpenAI compatibility", _OLLAMA, "docs"),
        Link("Model providers in Codex", _REFERENCE, "reference"),
    ),
    areas=(
        Area("Responses", "a model's answer, streamed, with its tool calls", _OPENAI,
             covered="what Codex asks of the instance chosen under Use…, never of OpenAI"),
    ),
    calls=(
        Call("POST /v1/responses", "a model's answer, streamed", "Responses",
             used="by Codex itself, at each turn", docs=_OPENAI),
    ),
    verified=VERIFIED,
)

APIS = (CODEX_API, CONFIG_API, DOWNLOADS_API, RESPONSES_API)
