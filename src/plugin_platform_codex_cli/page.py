"""What the Codex CLI plugin says on its page: constants and pure functions, nothing read, run or asked here.

`rows(...)` is the table "Before you use it" (what Codex does that a user should know before a start, each in a row of
its own), `open_words(...)` the sentences Open…'s confirmation ends with, and the rest the words of a fact, a refusal
or the install. Each sentence follows what was read in Codex CLI 0.170.0's sources and on its maker's pages (the
pre-build checks, C-X1; constants.py names them)."""
from __future__ import annotations

from typing import Iterable

from .constants import (ADVISED, ANNOUNCEMENT, FEWEST, MCP_NAME, MCP_SECRET, PIN, SECRET, TRANSCRIPTS_BYTES,
                        TRANSCRIPTS_KEPT)

ABOUT = "OpenAI's open-source Codex CLI, started against a local model server that speaks the Responses API"
LONG_ABOUT = ("OpenAI's open-source Codex CLI, started against a local model server that speaks the Responses API "
              "(not OpenAI's service: that is the Codex plugin)")
TABLE = "Before you use it"
COLUMNS = [{"title": "What"}, {"title": "Said"}]
CHECKED = ("It is checked against the sha256 pinned in this plugin, as GitHub's record of the release gives it (the "
           "release's codex-package_SHA256SUMS says the same).")
NO_SERVER = "the model server you choose (Use…)"
SANDBOX_WORDS = {
    "mxc": "mxc: Microsoft's MXC, its commands kept off the network and off this machine's own addresses",
    "bubblewrap": "bubblewrap: its commands in a namespace of their own",
}
ACTS = ("It acts as you, inside its sandbox (workspace-write): its commands read what you can read, write in the "
        "folder and the temporary folders alone (its .git, .codex and .agents kept read-only), and it asks you before "
        "going beyond that (approvals on-request; Codex no longer takes untrusted, and never is not offered). What "
        "you allow beyond the sandbox runs with your rights.")
SANDBOX = {
    "mxc": ("On Windows its commands run in Microsoft's MXC (Use…, Sandbox: mxc), which needs no administrator, no "
            "account and no firewall rule of its own. With their network off they reach neither the network nor this "
            "machine's own addresses, so not the platform (MXC's policy denies the host's loopback; a real run "
            "confirms it). MXC also ends every program a command leaves running when that command ends. Where "
            "Windows lacks MXC every command fails, with no other sandbox in its place. Its unelevated sandbox, "
            "whose commands reach this machine's own addresses and through the platform's API run what you can run, "
            "and its elevated sandbox, which asks for administrator rights and adds accounts and firewall rules to "
            "the whole system, are never chosen, set up or offered from here."),
    "linux": ("On Linux its commands run in bubblewrap: the first bwrap on PATH (one under the folder or one you can "
              "write is skipped), else the one its package brings, which needs unprivileged user namespaces. With "
              "their network off they run in a network namespace of their own, which reaches neither the network nor "
              "this machine's own addresses (a real run confirms it)."),
}
NETWORK = {False: "Its commands' network is off (Use…, Network).",
           True: ("Its commands' network is on (Use…, Network): they reach the network and this machine's own "
                  "addresses, the platform's among them.")}
FETCH = (f"Its terminal screen fetches {ANNOUNCEMENT} from GitHub at every start, by itself, from your address (2 s at "
         f"the most): no setting of Codex {PIN} turns it off. It is the one call it makes on its own here.")
TRANSCRIPTS = ("Codex saves every session's transcript (your prompts, its answers, the commands it ran and what they "
               "said) under {home}, in sessions and archived_sessions, and no setting of its terminal screen turns "
               f"this off. The plugin keeps the newest {TRANSCRIPTS_KEPT} ({TRANSCRIPTS_BYTES // 1_000_000} MB at the "
               "most) and removes older ones as each Open… opens a window, while none of its windows is open. Codex "
               "also keeps a log database there, which it caps itself (10 MiB a part) and nothing turns off; no "
               "prompt history is kept.")
LOCAL = ("The one model server it is given is {server}, as a provider of its own (liminal). Its analytics, its "
         "feedback, its metrics and traces, its update check, its web search, its plugins and apps, its tool "
         "suggestions and its shared background server (which would update itself from chatgpt.com) are all off; "
         "no credentials are kept and your keyring is never read. Every pair of Liminal's is dropped from what it "
         "inherits, every OPENAI_* and CODEX_* too, so the Codex plugin's OpenAI key never reaches it.")
PORTS = ("It opens no port by itself here. Its own sign-in (codex login, never run from here) would listen on "
         "127.0.0.1:1455, an MCP server's sign-in on a port of the system's choosing (not used: Liminal's MCP takes "
         "a token), and its network proxy (off) on this machine's own addresses.")
FOLDER = ("A folder's own .codex/ (its configuration, hooks and rules) is never loaded: every folder opened from here "
          "is marked untrusted, so Codex asks no trust either. A trust you give in Codex itself lasts until the next "
          "start, which writes config.toml again.")
MODEL = ("Codex asks a model server for the Responses API alone (/v1/responses): Ollama 0.13.3 and newer and vLLM "
         "serve it; llama.cpp's is reported unreliable with Codex; LMDeploy has none. It needs a model that calls "
         f"tools, and Ollama's page on Codex advises a context of {ADVISED:,} tokens at the least.")
SHARED = ("This copy has its own program and its own folder ({home}: CODEX_HOME): nothing is read from or written "
          "into {theirs}, and a Codex of yours is never run.")
THEIRS = {"windows": "%USERPROFILE%\\.codex", "linux": "~/.codex"}
CONFIGURED = ("config.toml in {home} is written whole at each start (an edit there lasts until the next one), and "
              "what one start is told is on its own command line (-c), so a window still open keeps its server and "
              "lines shown earlier keep theirs.")
SYSTEM_FILES = (" {files} {are} there: Codex reads its system configuration beneath what a start is told and its "
                "requirements above it (they can choose its sandbox).")
PLAIN = "{server} is asked over plain http on another machine: prompts and code can be read on the way."
KEYED = ("{server}'s key reaches Codex in its environment alone (" + SECRET + ", which its provider names), never in "
         "a file or on its command line; its commands are never given it.")
MCP = (f"With Liminal's MCP on (under Use…), each window reaches it as an MCP server of Codex's ({MCP_NAME}): over "
       "HTTP on the platform's address where the platform serves it, else through the MCP plugin's bridge, with a "
       f"token for that window alone in Codex's environment ({MCP_SECRET}), ended once the window is gone. Its "
       "commands are never given the token. What it may list and call is granted on the MCP plugin's page; Codex "
       "waits for a call as long as the MCP plugin holds it, and a minute more.")
RESPONSES_NONE = ("{server} offers no Responses API (its plugin says it speaks {speaks}): Codex CLI asks a model "
                  "server for nothing else")


def row(what: str, said: str) -> list[str]:
    return [what, said]


def joined(names: Iterable[str]) -> str:
    """Names in words: "a", "a and b", "a, b and c"."""
    shown = [str(n) for n in names if str(n)]
    return shown[0] if len(shown) < 2 else ", ".join(shown[:-1]) + " and " + shown[-1]


def speaks_words(speaks: Iterable[str]) -> str:
    said = list(speaks)
    return joined(said) if said else "nothing"


def context_words(server: str, model: str, *, typed: int | None, known: int | None, used: int | None) -> str:
    """What Codex is told of the model's context, in words: the context it is given and where it comes from, or why it
    cannot be started; the server's own word beside a larger one typed under Use…."""
    if used is None:
        return f"{server} does not say {model}'s context: give it under Use… (Context) first."
    if used < FEWEST:
        return (f"A context of {used:,} tokens is under the {FEWEST:,} Codex is started with here: give the real one "
                f"under Use…, or start {server} with more.")
    whence = "given under Use…" if typed else f"as {server} says it"
    said = f"It is told {used:,} tokens of context ({whence})."
    if typed and known and typed > known:
        said += (f" You gave {typed:,} under Use…, and {server} says {model} has {known:,} there: Codex would fill "
                 "more than the server holds.")
    if used < ADVISED:
        said += f" That is under the {ADVISED:,} Ollama's page advises."
    return said


def sandbox_row(system: str, sandbox: str, network: bool, mxc: str = "", bwrap: str = "") -> str:
    """Its sandbox on this system, in words, with what this machine says of it (`mxc`, `bwrap`: a fact, or "")."""
    if system == "windows":
        said = SANDBOX.get(sandbox, SANDBOX["mxc"])
        if sandbox == "mxc" and mxc:
            said += f" {mxc}"
    else:
        said = SANDBOX["linux"] + (f" {bwrap}" if bwrap else "")
    return f"{said} {NETWORK[bool(network)]}"


def rows(*, server: str, model: str, system: str, home: str, sandbox: str, network: bool, typed: int | None,
         known: int | None, used: int | None, keyed: bool, plain: bool, yours: str, chosen: bool,
         mcp: bool = False, mxc: str = "", bwrap: str = "", system_files: tuple[str, ...] = ()) -> list[list[str]]:
    """The rows of Before you use it, in the order a user reads them: what it may do as you, its sandbox, its start-up
    fetch, its transcripts, what stays local, its ports, the folder's .codex/, the model, what it shares with a Codex
    of yours, its configuration; a key, plain http and Liminal's MCP only where they apply."""
    out = [row("It acts as you", ACTS),
           row("Its sandbox", sandbox_row(system, sandbox, network, mxc, bwrap)),
           row("Its start-up fetch", FETCH),
           row("Its transcripts", TRANSCRIPTS.format(home=home)),
           row("Local only", LOCAL.format(server=server)),
           row("Its ports", PORTS),
           row("The folder's .codex", FOLDER)]
    if chosen:
        out.append(row("The model", f"{MODEL} {context_words(server, model, typed=typed, known=known, used=used)}"))
    else:
        out.append(row("The model", MODEL))
    if keyed:
        out.append(row("Its key", KEYED.format(server=server)))
    if plain:
        out.append(row("Plain http", PLAIN.format(server=server)))
    if mcp:
        out.append(row("Liminal's MCP", MCP))
    shared = SHARED.format(home=home, theirs=THEIRS.get(system, THEIRS["linux"]))
    if yours:
        shared += f" {yours} is yours and is left as it is: never run, read, configured, replaced or removed from here."
    out.append(row("What it shares with a Codex of yours", shared))
    configured = CONFIGURED.format(home=home)
    if system_files:
        configured += SYSTEM_FILES.format(files=joined(system_files), are="is" if len(system_files) == 1 else "are")
    out.append(row("Its configuration", configured))
    return out


def table(rows_: list[list[str]]) -> dict:
    return {"title": TABLE, "columns": [dict(c) for c in COLUMNS], "rows": rows_}


def open_words(*, system: str, sandbox: str, network: bool, window: bool) -> str:
    """What Open…'s confirmation ends with (after a space): it acts as you in its sandbox and asks before going beyond
    it; its sandbox and its commands' network; its start-up fetch; its transcripts, pruned when a window opens."""
    if system == "windows":
        box = "Microsoft's MXC"
    else:
        box = "bubblewrap"
    net = "on" if network else "off"
    pruned = ("older transcripts are removed as it opens" if window else
              "older transcripts are removed at the next Open… that opens a window")
    return (f" Codex acts as you inside {box}, its commands' network {net}, and asks before going beyond it. It "
            f"fetches {ANNOUNCEMENT} at each start, and saves each session's transcript: the newest "
            f"{TRANSCRIPTS_KEPT} are kept, {pruned}. A folder's .codex/ is not loaded.")


def parts(asset: str) -> str:
    """What Install downloads, in words (the install's confirmation goes on "… is downloaded from")."""
    return f"Codex CLI {PIN}'s package for this system ({asset}: the program and its sandbox's helpers)"


def keeps(home: str) -> str:
    """What an uninstall leaves, in words."""
    return (f"What it kept stays: {home}, with its transcripts (your prompts and code), its logs and its "
            "configuration.")


def pinned(asset: str) -> str:
    return f"{PIN} ({asset})"


def yours_fact(path: str) -> str:
    return f"{path} is yours: left as it is, not used from here"


def sandbox_fact(system: str, sandbox: str) -> str:
    return SANDBOX_WORDS["bubblewrap"] if system != "windows" else SANDBOX_WORDS.get(sandbox, SANDBOX_WORDS["mxc"])


def mxc_words(state: str, build: str) -> str:
    """What this Windows build says of MXC, in words ("" where nothing is known): `state` listed, later, older."""
    if state == "listed":
        return f"This Windows ({build}) is among the builds MXC came with."
    if state == "later":
        return (f"This Windows ({build}) is later than the builds MXC came with (26100.9278, 26200.9278), so MXC is "
                "expected here, not confirmed: Codex decides by a probe at its start.")
    if state == "older":
        return (f"This Windows ({build}) is older than the builds MXC came with (24H2 26100.9278, 25H2 26200.9278): "
                "every command fails until Windows Update brings it.")
    return ""


def mxc_problem(build: str) -> str:
    return (f"this Windows ({build}) has no MXC yet (it came with 26100.9278 and 26200.9278), and Codex's sandbox is "
            "mxc: every command it runs fails until Windows Update brings it")


def userns_problem(why: str) -> str:
    return (f"bubblewrap cannot run Codex's commands here: {why}. Changing that is root's; until then every command "
            "fails")


def temp_problem(home: str) -> str:
    return (f"Codex's folder {home} is inside the system's temporary folder, where Codex refuses to make its helpers: "
            "move the platform's folder")


def policy_problem(path: str) -> str:
    return (f"a policy names Codex's requirements file ({path}): what it requires comes above what a start is told, "
            "and can choose its sandbox")


def system_problem(paths: Iterable[str]) -> str:
    shown = list(paths)
    return (f"Codex's system {'file' if len(shown) == 1 else 'files'} {joined(shown)} "
            f"{'is' if len(shown) == 1 else 'are'} there: its requirements come above what a start is told, and can "
            "choose its sandbox (Before you use it)")


def too_small(server: str, context: int) -> str:
    return (f"Codex is started with a context of {FEWEST:,} tokens at the least, and {context:,} leaves its "
            f"instructions and its tools no room (give the real one under Use…, or start {server} with more)")


def value_words(why: str) -> str:
    return f"Codex cannot be given what this start needs: {why}. Nothing was started"


def transcripts_words(removed: int) -> str:
    return f"{removed:,} older transcript{'' if removed == 1 else 's'} removed"
