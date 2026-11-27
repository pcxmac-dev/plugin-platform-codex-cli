"""Codex CLI for Liminal (the user, 2026-11-18: "top 4 inference engines, top 4 agentic harnesses (open source)", "all
platform", "both linux and windows compatibility"; 2026-11-25, answers 5 and 6: its sandbox on Windows "mxc, never
elevated", on Linux "its bundled bubblewrap", and "the terminal screen, both said plainly on its page; the plugin
prunes old transcripts"; and, from 2026-11-16 and 2026-11-17: "they will be classified as AI plugins", "all plugins
are middleware"): OpenAI's open-source Codex CLI, its package installed pinned into the platform's own folder,
configured against one instance of an inference plugin's that speaks the Responses API, and opened in a folder the
user picks. It is not OpenAI's service: that is the Codex plugin's.

A harness (liminal_libs.machines.harness.Harness, liminal-libs 1.66.0), so middleware of that kind: the standard
interface of a harness, with no hook of its own. The base gives the install's job and its forms, Use… (the instance,
asked of the inference plugins through the platform, its model and Codex's options kept through the login), Open… (a
window of its own where there is a desktop, the lines to paste anywhere else), Command…, Liminal's MCP (off unless
Use… turns it on), and keeps every pair of Liminal's out of what it starts. What this plugin says:

- Install: this system's package of Codex CLI 0.170.0 (Windows x64; Linux x64, a musl build that runs on any Linux),
  pinned by name, size and sha256 (constants.py), downloaded only at the user's click, as a job, unpacked into
  <home>/app/0.170.0 as it is laid out (bin/ beside codex-resources/, which holds its sandbox's helpers), and put in
  use once whole. A Codex of the user's own (on PATH) is a fact, never run, read, configured, replaced or removed.
  Never run from here: its install scripts, npm, codex login, codex mcp add, codex sandbox setup.
- The start: `codex --no-daemon` in the folder, its CODEX_HOME the plugin's own (<home>/config/codex), whose
  config.toml is written whole at each start (files.config_toml: local only, every folder opened from here
  untrusted), and what that start is told on its command line (files.overrides: its approvals on-request, its
  sandbox workspace-write with its commands' network off unless chosen on, on Windows MXC and never the unelevated or
  elevated one, the instance as a provider of its own speaking the Responses API, the model and its
  context, Liminal's MCP over HTTP or through its bridge where Use… turned it on). The instance's key, where one is
  kept, is in its environment alone; its commands are never given a pair of Liminal's.
- Its transcripts: Codex saves every session's under CODEX_HOME/sessions and nothing turns that off in its terminal
  screen; the newest 50 (200 MB at the most) are kept, older ones removed as Open… opens a window while none of its
  windows is open.
- Refused before a start, in words: an instance whose plugin does not say it speaks the Responses API (`fits`), a
  context it is not told or under 8,192 tokens, a value Codex's -c cannot be given as it is.
- Before you use it (page.py): what it does as you, its sandbox and what this machine says of it (on Windows its
  build against the ones MXC came with, read from the registry; on Linux bwrap on PATH and what /proc says of user
  namespaces), its start-up fetch, its transcripts, what stays local, its ports, a folder's .codex/, the model, what
  it shares with a Codex of yours, its configuration; a key, plain http and Liminal's MCP where they apply. Nothing
  is run or asked over the network for the page.

    python -m plugin_platform_codex_cli status | command [FOLDER]
"""
from __future__ import annotations

import ntpath
import os
import platform as py_platform
import posixpath
import sys
import tempfile
import threading
import tomllib
from pathlib import Path
from typing import Callable, Mapping

from liminal_libs import mounts
from liminal_libs.machines import download, harness
from liminal_libs.machines.ai import Installed, Outside, Package, Refusal, Setting
from liminal_libs.machines.children import Launch
from liminal_libs.machines.download import Source
from liminal_libs.machines.harness import Harness, HarnessRun, Use, server_words
from liminal_libs.machines.modelserver import spoken

from . import constants as pins
from . import files, page
from .apis import APIS, CODEX, DOWNLOADS

__version__ = "0.1.1"
LIBS_FLOOR = "1.99.0"  # pyproject's floor: the base's changes page-only (1.99.0), the Responses check (1.66.0)


def _get(env: Mapping[str, str], name: str, windows: bool) -> str:
    """A variable of `env`, told apart without regard to case on Windows, as Windows reads a name."""
    if not windows:
        return str(env.get(name) or "")
    wanted = name.upper()
    return next((str(v) for k, v in env.items() if str(k).upper() == wanted and v), "")


def _number(value) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else None


def _registry(key: str, value: str):
    """A value of HKEY_LOCAL_MACHINE\\`key`, read only (OSError where it cannot be)."""
    import winreg

    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key, 0,
                        winreg.KEY_READ | getattr(winreg, "KEY_WOW64_64KEY", 0)) as opened:
        found, _ = winreg.QueryValueEx(opened, value)
    return found


def _proc(path: str) -> str | None:
    """A file of /proc as text, stripped; None where it is not there or cannot be read."""
    try:
        return Path(path).read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return None


class CodexCliRun(HarnessRun):
    """The harness's run state, with this system's build as worked out once (the system it was worked out for, it),
    config.toml written one start at a time, and what the last window's pruning removed."""

    def __init__(self):
        super().__init__()
        self.target: tuple[str, str] | None = None
        self.writing = threading.Lock()  # (two Open… at once)
        self.pruned = 0


class CodexCliPlugin(Harness):
    """Codex CLI, a harness of the platform's AI plugins: its package installed, pinned, into its own folder, started
    against one model server's instance that speaks the Responses API, in a folder you pick (Harness: Use…, Open…,
    Command…, the install's job, Liminal's MCP)."""

    name = "codex-cli"
    title = "Codex CLI"  # beside the Codex plugin, which is OpenAI's service
    about = page.ABOUT
    order = 523  # the harnesses: OpenCode 520, Aider 521, Continue 522, Codex CLI 523, Pi 524, goose 525
    ICON = "codexcli"  # Codex's own mark, not the OpenAI knot of the Codex plugin (liminal-libs 1.66.0's icons.js)
    LIBS_FLOOR = LIBS_FLOOR
    apis = APIS  # what it attaches to: Codex itself, its configuration, its release's files, the Responses API
    RUN_STATE = CodexCliRun
    OPTIONS = (
        Setting("context", "Context", "number", min=pins.FEWEST, max=pins.MOST,
                note=("what the model really has on that server, in tokens: Codex is told it; left empty: the "
                      f"server's word (Ollama's page advises {pins.ADVISED:,} at the least)")),
        Setting("sandbox", "Sandbox", "choice", "mxc",
                choices=(("mxc", "mxc", "Microsoft's MXC: its commands kept off the network and off this machine's "
                                        "own addresses; Windows 11 24H2 26100.9278, 25H2 26200.9278 or later"),),
                note=("Windows alone (on Linux its commands run in bubblewrap), and MXC alone: its unelevated "
                      "sandbox lets its commands reach this machine's loopback, the platform's API among it, and its "
                      "elevated one needs administrator rights and changes the whole system; neither is offered")),
        Setting("network", "Network", "choice", "off",
                choices=(("off", "off", "its commands reach neither the network nor this machine's own addresses"),
                         ("on", "on", "its commands reach the network and this machine's own addresses")),
                note="its commands' network, inside its sandbox (Codex itself always reaches the model server)"),
        harness.MCP_OPTION,
    )
    # Liminal's MCP over HTTP where this platform serves the route, else the MCP plugin's bridge (a stdio server)
    MCP_WIRES = ("http", "stdio")
    # What it says of the interface it shares (read by name by the Internal API tab, liminal-libs 1.63.0): no hook of
    # its own beyond the harness base's, so no read of its own and no change of its own (PAGE_ONLY_HOOKS: the base's);
    # it serves no other plugin; what it asks of the others (serving, models_of, and the MCP plugin's four) and what
    # it keeps through the login (its use) are the base's ASKS and KEEPS.
    READ_HOOKS: tuple[str, ...] = ()
    SERVICE_HOOKS: tuple[str, ...] = ()
    ASKS = (*Harness.ASKS, *harness.MCP_ASKS)
    INTERNAL_NOTES = (
        *Harness.INTERNAL_NOTES,
        *harness.MCP_NOTES,
        "A harness (liminal_libs.machines.harness.Harness): the standard interface of its kind, with no hook of its "
        "own. What it adds is inside launch() and its window: the config.toml it writes for Codex, the -c words of "
        "each start, its old transcripts pruned as a window opens.",
        "It starts Codex only against an instance whose serving row says it speaks the Responses API (speaks: "
        "responses, liminal-libs 1.66.0's families).",
    )
    # What it needs of a machine (the needs plan's rows, in its getattr idiom: the library has no needs module yet, so
    # the base's NEEDS is read only through getattr). Each row is a part: what lacks one is said, the rest still works.
    NEEDS = (*getattr(Harness, "NEEDS", ()),
             ("architecture", "x86-64", "part", "its install: only the x86-64 packages are pinned in 0.1.0"),
             ("desktop", "yes", "part", "its window on Windows; elsewhere Open… gives the lines to paste"),
             ("windows.build", ">=26100.9278 (24H2) or >=26200.9278 (25H2)", "part",
              "MXC, its sandbox on Windows: without it every command fails"),
             ("tool", "bwrap", "part", "bubblewrap on Linux (its package's own needs unprivileged user namespaces: "
                                       "linux.feature userns, proposed to the needs release)"),
             ("internet", "yes", "part", "its install, on a click"))

    def __init__(self, outside: Outside | None = None, *, machine: Callable[[], str] | None = None,
                 registry: Callable[[str, str], object] | None = None, proc: Callable[[str], str | None] | None = None,
                 temp: Callable[[], str] | None = None):
        """`outside`: the AI base's outside things (a test's stand-ins); `machine`: what this processor is
        (platform.machine()); `registry`: a value of HKEY_LOCAL_MACHINE, read only; `proc`: a file of /proc as text;
        `temp`: the system's temporary folder. None: the real ones, looked at when asked. Making it reads nothing."""
        super().__init__(outside)
        self._machine, self._registry, self._proc, self._temp = machine, registry, proc, temp

    # -- this system's build ------------------------------------------------------------------------------------------
    def machine_word(self) -> str:
        """This processor as Python names it ("AMD64", "x86_64", "aarch64"): "" where it cannot say."""
        try:
            return str((self._machine or py_platform.machine)() or "").strip()
        except Exception:  # noqa: BLE001 - a machine that cannot be named has no build here
            return ""

    def target(self) -> str:
        """This system's package of Codex, as this plugin names it ("windows-x64", "linux-x64"): "" for a processor it
        names none for. Worked out once, nothing run."""
        system = self.system
        with self._rt.lock:
            kept = self._rt.target
        if kept is not None and kept[0] == system:
            return kept[1]
        arch = pins.ARCHES.get(self.machine_word().lower(), "")
        found = f"{system}-{arch}" if arch else ""
        with self._rt.lock:
            self._rt.target = (system, found)
        return found

    def build(self) -> tuple[str, int, str] | None:
        """Codex's package for this system: (archive, bytes, sha256); None where none is pinned."""
        return pins.TARGETS.get(self.target())

    def runs_here(self) -> str:
        """"" or why Codex is not installed on this system, in words: macOS (not this plugin's), a processor whose
        package is not pinned here (ARM64 among them)."""
        if self.out.system is None and sys.platform == "darwin":
            return "Codex CLI is installed from here on Windows and Linux only"
        if self.build() is not None:
            return ""
        machine = self.machine_word() or "this processor"
        where = "Windows" if self.system == "windows" else "Linux"
        if pins.ARCHES.get(machine.lower()) == "arm64":
            return (f"Codex CLI {pins.PIN}'s package for {where} on ARM64 is not pinned in this release of the plugin "
                    "(x86-64 alone): it is not installed here")
        return f"Codex CLI {pins.PIN} has no package for {machine} on {where}: it is not installed here"

    def source(self) -> Source:
        """The file Install downloads for this system, pinned by its name, its size and its sha256."""
        build = self.build()
        if build is None:
            raise Refusal(self.runs_here() or f"no package of Codex CLI {pins.PIN} is pinned here")
        asset, size, sha = build
        return Source(pins.FILES + asset, asset, size, sha, pins.ASSET_HOSTS)

    # -- what is installed --------------------------------------------------------------------------------------------
    def _program_in(self, folder: Path) -> Path:
        return Path(folder).joinpath(*pins.PROGRAM[self.system])

    def codex_home(self) -> Path:
        """Codex's own folder for what is started from here (CODEX_HOME), as a whole path: its config.toml, its
        transcripts, its logs, its caches."""
        return Path(os.path.abspath(self.home / "config" / pins.CODEX_HOME))

    def package(self) -> Package | None:
        """What Install brings here: Codex CLI 0.170.0's package for this system, its bytes, its licence and the hosts
        it comes from; None where nothing is installed from here."""
        if self.runs_here():
            return None
        asset, size, _ = self.build()
        return Package("Codex CLI", pins.PIN, size, pins.LICENCE, pins.HOSTS, parts=page.parts(asset),
                       keeps=page.keeps(str(self.codex_home())), checked=page.CHECKED)

    def installed(self) -> Installed | None:
        """This plugin's install, files looked at only: the folder app/CURRENT names, with Codex's program in its bin/.
        One of the user's own is never this (it is the fact `yours`)."""
        folder = self.current()
        if folder is None:
            return None
        program = self._program_in(folder)
        if not program.is_file():
            return None
        return Installed(folder.name, str(program), "plugin")

    def _mine(self, path: Path) -> bool:
        try:
            Path(path).resolve().relative_to(Path(self.home).resolve())
        except (OSError, ValueError):
            return False
        return True

    def _user_home(self) -> Path | None:
        windows = self.system == "windows"
        found = _get(self._env(), "USERPROFILE" if windows else "HOME", windows)
        return Path(found) if found else None

    def yours(self) -> str:
        """A Codex of the user's own ("" when there is none): a program named codex on PATH that is not this plugin's.
        Looked at only: never run, read, configured, replaced or removed from here."""
        try:
            on_path = self.out.which("codex")
        except Exception:  # noqa: BLE001 - a PATH that cannot be read: none found there
            on_path = None
        if on_path and not self._mine(Path(on_path)):
            try:
                if Path(on_path).is_file():
                    return str(on_path)
            except OSError:
                return ""
        return ""

    @staticmethod
    def _package_root(folder: Path, program: tuple[str, ...]) -> Path | None:
        """Where the package's bin/ is: the folder itself, or its one folder (a package laid out under a folder of its
        own); None where neither holds the program."""
        if Path(folder).joinpath(*program).is_file():
            return Path(folder)
        try:
            entries = list(Path(folder).iterdir())
        except OSError:
            return None
        if len(entries) == 1 and entries[0].is_dir() and entries[0].joinpath(*program).is_file():
            return entries[0]
        return None

    def install_into(self, log, cancel) -> list[str]:
        """Codex's package downloaded (checked against its pinned size and sha256) and unpacked into app/0.170.0 as it
        is laid out (bin/ beside codex-resources/, which its sandbox needs; a package under one folder of its own is
        moved up), its program and its sandbox's helpers looked for, then put in use and the archive removed. A
        cancel or a failure leaves the install in use as it was (the base removes the half-built folder)."""
        source = self.source()
        folder = self.building(pins.PIN)
        archive = self.fetch(source, log=log, cancel=cancel)
        self.unpack(archive, folder, log=log, cancel=cancel)
        program = pins.PROGRAM[self.system]
        root = self._package_root(folder, program)
        if root is None:
            raise download.DownloadError(f"{source.name} holds no {'/'.join(program)}: Codex CLI is not installed")
        if root != folder:
            for entry in list(root.iterdir()):
                os.replace(entry, folder / entry.name)
            root.rmdir()
        missing = [p for p in pins.HELPERS[self.system] if not folder.joinpath(*p).is_file()]
        if missing:
            names = page.joined("/".join(p) for p in missing)
            raise download.DownloadError(f"{source.name} holds no {names}, which its sandbox needs: Codex CLI is not "
                                         "installed")
        lines = [f"Codex CLI {pins.PIN}: {self._program_in(folder)}"]
        if self.system != "windows":
            made = []
            for parts in (program, *pins.HELPERS["linux"]):
                path = folder.joinpath(*parts)
                if not os.access(path, os.X_OK):
                    os.chmod(path, (path.stat().st_mode & 0o777) | 0o700)  # (its archive's mode said it was not)
                    made.append(path.name)
            if made:
                lines.append(f"{page.joined(made)} made runnable for you")
        lines += self.adopt(pins.PIN)
        return [*lines, *self.forget_downloads()]

    # -- what this machine says of its sandbox ------------------------------------------------------------------------
    def _read_registry(self, key: str, value: str):
        reader = self._registry or _registry
        return reader(key, value)

    def windows_build(self) -> tuple[int, int] | None:
        """This Windows' build and its update (CurrentBuild, UBR), read from the registry; None where they cannot be
        (or this is not Windows). Read only."""
        if self.system != "windows":
            return None
        try:
            build = int(str(self._read_registry(pins.VERSION_KEY, "CurrentBuild")).strip())
            ubr = int(self._read_registry(pins.VERSION_KEY, "UBR"))
        except Exception:  # noqa: BLE001 - not known: nothing said
            return None
        return build, ubr

    def mxc_state(self) -> tuple[str, str]:
        """What this Windows' build says of MXC: ("listed" | "later" | "older" | "", the build as text). Codex decides
        by its own probe at its start: this is the plugin's word beside it, the build against the ones MXC came with."""
        found = self.windows_build()
        if found is None:
            return "", ""
        build, ubr = found
        text = f"{build}.{ubr}"
        least = pins.MXC_BUILDS.get(build)
        if least is not None:
            return ("listed" if ubr >= least else "older"), text
        return ("later" if build > min(pins.MXC_BUILDS) else "older"), text

    def _read_proc(self, path: str) -> str | None:
        return (self._proc or _proc)(path)

    def bwrap(self) -> str:
        """The bwrap Codex would use on PATH ("": none, so its package's own)."""
        try:
            found = self.out.which("bwrap")
        except Exception:  # noqa: BLE001 - a PATH that cannot be read: none found there
            return ""
        return str(found or "")

    def userns_problem(self) -> str:
        """"" or why bubblewrap cannot run Codex's commands on this Linux, in words, from what /proc says of
        unprivileged user namespaces (read where its files are, never written): none allowed, turned off (Debian's
        switch), or restricted by AppArmor (Ubuntu 24.04's) while no bwrap is on PATH (its package's own copy has no
        AppArmor profile; Ubuntu's covers /usr/bin/bwrap)."""
        if self.system == "windows":
            return ""
        most = self._read_proc(pins.USERNS["max"])
        if most is not None and most.isdigit() and int(most) == 0:
            return page.userns_problem("this Linux allows no user namespaces (max_user_namespaces is 0)")
        if self._read_proc(pins.USERNS["clone"]) == "0":
            return page.userns_problem("unprivileged user namespaces are off (unprivileged_userns_clone is 0)")
        if self._read_proc(pins.USERNS["apparmor"]) == "1" and not self.bwrap():
            return page.userns_problem("AppArmor restricts unprivileged user namespaces "
                                       "(apparmor_restrict_unprivileged_userns is 1), no bwrap is on PATH, and the one "
                                       "its package brings has no AppArmor profile")
        return ""

    def bwrap_words(self) -> str:
        """What this Linux says of bubblewrap, in words, for Before you use it."""
        found = self.bwrap()
        if found:
            return f"Here Codex uses {found}."
        if self.userns_problem():
            return "Here no bwrap is on PATH, and this Linux does not let its package's own run (its problem says why)."
        return "Here no bwrap is on PATH: Codex uses its package's own."

    def home_in_temp(self) -> bool:
        """Whether CODEX_HOME is inside the system's temporary folder, where Codex refuses to make its helpers."""
        try:
            temp = Path(os.path.realpath((self._temp or tempfile.gettempdir)()))
            Path(os.path.realpath(self.codex_home())).relative_to(temp)
        except (OSError, ValueError, TypeError):
            return False
        return True

    def system_files(self) -> tuple[str, ...]:
        """Codex's system files that are there: on Linux /etc/codex/config.toml (beneath what a start is told) and
        /etc/codex/requirements.toml (above it); on Windows the requirements file a policy names. Looked at only."""
        if self.system == "windows":
            try:
                named = str(self._read_registry(pins.POLICY_KEY, pins.POLICY_VALUE) or "").strip()
            except Exception:  # noqa: BLE001 - no policy
                named = ""
            return (named,) if named else ()
        found = []
        for path in pins.SYSTEM_FILES:
            try:
                if Path(path).is_file():
                    found.append(path)
            except OSError:
                continue
        return tuple(found)

    # -- the start ----------------------------------------------------------------------------------------------------
    @staticmethod
    def speaks(at: Mapping) -> tuple[str, ...]:
        """What the instance's serving row says it speaks, in the library's words (modelserver.FAMILIES)."""
        return spoken(at.get("speaks"))

    def fits(self, at: Mapping) -> str:
        """"" or why Codex cannot use the instance `at`, in words: it needs an OpenAI-compatible address (the base's),
        and the Responses API, which the row's plugin must say it speaks. LMDeploy's rows meet this refusal."""
        base = super().fits(at)
        if base:
            return base
        said = self.speaks(at)
        if "responses" in said:
            return ""
        return page.RESPONSES_NONE.format(server=server_words(at), speaks=page.speaks_words(said))

    @staticmethod
    def _listed(at: Mapping, model: str) -> dict:
        """The model's row among what its server lists ({"id", "context", "tools"}), {} when it is not listed."""
        for m in at.get("models") or ():
            if isinstance(m, Mapping) and str(m.get("id") or "").strip() == model:
                return dict(m)
        return {}

    def contexts(self, use: Use, at: Mapping) -> tuple[int | None, int | None, int | None]:
        """The model's context: (typed under Use…, the server's word: the model's as it lists it, else the
        instance's, the one Codex is told: the typed one first), each None where it is not said."""
        typed = _number(use.options.get("context"))
        known = _number(self._listed(at, use.model).get("context")) or _number(at.get("context"))
        return typed, known, typed or known

    @staticmethod
    def sandbox_of(use: Use | None) -> str:
        """Its sandbox on Windows: mxc, whatever a Use… kept says (unelevated and elevated are not offered)."""
        said = str((use.options.get("sandbox") if use is not None else "") or "mxc")
        return said if said in pins.SANDBOXES else "mxc"

    @staticmethod
    def network_of(use: Use | None) -> bool:
        """Whether its commands' network is on: only where Use… chose on."""
        return use is not None and str(use.options.get("network") or "") == "on"

    def _context(self, use: Use, at: Mapping) -> int:
        """The context Codex is told; a Refusal in words when none is said or it leaves Codex no room."""
        words = server_words(at)
        _, _, context = self.contexts(use, at)
        if context is None:
            raise Refusal(f"{words} does not say {use.model}'s context: give it under Use… (Context)")
        if context < pins.FEWEST:
            raise Refusal(page.too_small(words, context))
        return context

    def config_path(self) -> Path:
        return self.codex_home() / "config.toml"

    def _folders_kept(self) -> list[str]:
        """The folders config.toml marks now (any trust), as it is read back; [] when it cannot be."""
        try:
            parsed = tomllib.loads(self.config_path().read_text(encoding="utf-8"))
        except (OSError, UnicodeError, tomllib.TOMLDecodeError):
            return []
        return files.projects_of(parsed)

    def write_config(self, folder: str, sandbox: str, network: bool) -> Path:
        """config.toml written whole (a part file renamed), one start at a time: what holds for every start, its
        sandbox as this start is told it, `folder` and every folder it marked before untrusted (the newest first,
        PROJECTS_KEPT at the most). Never a .env beside it: one there is removed, since Codex would read it."""
        path = self.config_path()
        mounts.owner_only(path.parent, "Configuring Codex CLI")
        with self._rt.writing:
            path.parent.mkdir(parents=True, exist_ok=True)
            folders = list(dict.fromkeys([folder, *self._folders_kept()]))[:pins.PROJECTS_KEPT]
            text = files.config_toml(system=self.system, sandbox=sandbox, network=network, folders=folders)
            try:
                same = path.read_text(encoding="utf-8") == text
            except (OSError, UnicodeError):
                same = False
            if not same:
                part = path.with_name(path.name + download.PART)
                part.write_text(text, encoding="utf-8", newline="\n")
                os.replace(part, path)
            env_file = path.parent / ".env"
            if os.path.lexists(env_file):
                try:
                    env_file.unlink()
                except OSError as e:
                    raise Refusal(f"{env_file}, which Codex would read into its environment, could not be removed "
                                  f"({' '.join(str(e).split())}): Codex is not started") from None
        return path

    def _whole_path(self) -> str | None:
        """The platform's PATH with its relative and empty entries left out (Codex and its commands are given no PATH
        entry that means the folder they are in), None when it has none to leave out."""
        windows = self.system == "windows"
        given = _get(self._env(), "PATH", windows)
        if not given:
            return None
        parts = given.split(";" if windows else ":")
        if windows:
            def absolute(entry: str) -> bool:
                bare = entry.strip().strip('"')
                return len(bare) > 2 and bare[1] == ":" and bare[2] in "\\/" or bare.startswith("\\\\")
            whole = [p for p in parts if absolute(p)]
        else:
            whole = [p for p in parts if p.startswith("/")]
        return None if len(whole) == len(parts) else (";" if windows else ":").join(whole)

    def launch(self, folder: str, use: Use, at: dict, key: str = "") -> Launch:
        """Codex started in `folder` against the instance `at` with `use`'s model and options: config.toml written
        whole into its own CODEX_HOME (`write_config`), `codex --no-daemon` with that start's -c words
        (files.overrides: its approvals and sandbox, the instance as its provider, the model and its context,
        Liminal's MCP where Use… turned it on: `mcp_wiring`), CODEX_HOME and the key (where one is kept, named by
        LIMINAL_SERVER_KEY alone) in its environment, a PATH without relative entries. Refused in words: its own
        folder on another system's drive; not installed; an instance that does not speak the Responses API; what
        Codex would read as more than text in the server's address; a context it is not told, or one under 8,192
        tokens; a value its -c cannot be given as it is."""
        trouble = self.home_problem()
        if trouble:
            raise Refusal(trouble)
        here = self.current()
        if here is None or self.installed() is None:
            raise Refusal(f"{self.title} is not installed here: Install… first")
        unfit = self.fits(at)
        if unfit:
            raise Refusal(unfit)
        address = str(at.get("openai") or "").strip()
        self.clean_value(address, "the server's address")
        context = self._context(use, at)
        sandbox, network = self.sandbox_of(use), self.network_of(use)
        wiring = self.mcp_wiring(use)  # (None while Liminal's MCP is off; asked last: a refusal above asks nothing)
        mcp = None
        if wiring is not None and wiring.wire == "http":
            mcp = {"url": wiring.url, "headers": dict(wiring.headers), "timeout_s": wiring.timeout_s}
        elif wiring is not None:  # (a whole path: Codex looks a bare name up on its PATH, C-X1.4e)
            whole = ntpath.isabs if self.system == "windows" else posixpath.isabs
            if not wiring.argv or not whole(wiring.argv[0]):
                raise Refusal(page.value_words("the MCP plugin's bridge is not named by a whole path"))
            mcp = {"argv": wiring.argv, "timeout_s": wiring.timeout_s}
        try:
            words = files.overrides(system=self.system, sandbox=sandbox, network=network, model=use.model,
                                    base_url=address, context=context, keyed=bool(key), mcp=mcp)
        except ValueError as e:
            raise Refusal(page.value_words(str(e))) from None
        where = os.path.abspath(str(folder))
        self.write_config(where, sandbox, network)
        env = {"CODEX_HOME": str(self.codex_home())}
        path = self._whole_path()
        if path is not None:
            env["PATH"] = path
        if key:
            env[pins.SECRET] = key
        argv = [os.path.abspath(self._program_in(here)), "--no-daemon", *words]  # (a whole path: started in the folder)
        return Launch(tuple(argv), env=env, cwd=folder, drop=pins.DROP, secret=(pins.SECRET,) if key else ())

    # -- its transcripts ----------------------------------------------------------------------------------------------
    def transcripts(self) -> list[tuple[float, int, Path]]:
        """Codex's saved transcripts under CODEX_HOME (sessions/ and archived_sessions/, every .jsonl and .jsonl.zst),
        the newest first: (when written, bytes, path). TRANSCRIPTS_LOOKED files at the most. Looked at only."""
        found: list[tuple[float, int, Path]] = []
        for name in pins.TRANSCRIPTS:
            for root, _, names in os.walk(self.codex_home() / name):
                for n in names:
                    if len(found) >= pins.TRANSCRIPTS_LOOKED:
                        break
                    if not pins.TRANSCRIPT.search(n):
                        continue
                    path = Path(root) / n
                    try:
                        st = path.stat(follow_symlinks=False)
                    except OSError:
                        continue
                    found.append((st.st_mtime, st.st_size, path))
        return sorted(found, key=lambda t: (t[0], str(t[2])), reverse=True)

    def prune_transcripts(self) -> int:
        """Older transcripts removed: all but the newest TRANSCRIPTS_KEPT, and past TRANSCRIPTS_BYTES of them (the
        newest first), then the folders that held them, if empty. Nothing while one of its windows is open (a
        session may be writing its own), and never a transcript written within TRANSCRIPTS_FRESH_S (0.1.1): a Codex
        started from Command…'s lines is no window of the plugin's, and may be writing it (it is kept, and counted
        among the newest). The files removed."""
        if self.running():
            return 0
        now = self.out.clock()
        kept = total = removed = 0
        for written, size, path in self.transcripts():
            if now - written < pins.TRANSCRIPTS_FRESH_S:  # (a time ahead of the clock's, too)
                kept, total = kept + 1, total + size
                continue
            if kept < pins.TRANSCRIPTS_KEPT and total + size <= pins.TRANSCRIPTS_BYTES:
                kept, total = kept + 1, total + size
                continue
            try:
                path.unlink()
                removed += 1
            except OSError:
                continue  # (in use, or gone already: the next Open… looks again)
        if removed:
            for name in pins.TRANSCRIPTS:
                top = self.codex_home() / name
                for root, _, _ in sorted(os.walk(top), key=lambda w: len(w[0]), reverse=True):
                    if Path(root) != top:
                        try:
                            os.rmdir(root)
                        except OSError:
                            pass  # (not empty)
        return removed

    def _window(self, launch: Launch, folder: str, token: str = "") -> tuple[int | None, str]:
        """The base's window, Codex's older transcripts pruned just before it opens."""
        removed = self.prune_transcripts()
        with self._rt.lock:
            self._rt.pruned = removed
        return super()._window(launch, folder, token)

    def open(self, folder=None) -> dict:
        """Codex started in `folder` against the server Use… chose (the base's Open…), its older transcripts pruned as
        the window opens (said among its lines)."""
        with self._rt.lock:
            self._rt.pruned = 0
        out = super().open(folder)
        with self._rt.lock:
            removed, self._rt.pruned = self._rt.pruned, 0
        if removed and out.get("ok"):
            out = {**out, "lines": [*(out.get("lines") or []), page.transcripts_words(removed)]}
        return out

    def open_words(self, use: Use, at) -> str:
        """What Open…'s confirmation ends with: it acts as you in its sandbox, which one, its commands' network, its
        start-up fetch and its transcripts."""
        return page.open_words(system=self.system, sandbox=self.sandbox_of(use), network=self.network_of(use),
                               window=self._desktop())

    # -- its Main ---------------------------------------------------------------------------------------------------
    def main_more(self) -> dict:
        """Before you use it: what Codex does that you should know before a start (page.rows), drawn before the Model
        servers table. Nothing is run or asked over the network."""
        use = self.use_kept()
        at = self.serving_of(use.server) if use is not None else None
        state, build = self.mxc_state()
        common = dict(system=self.system, home=str(self.codex_home()), sandbox=self.sandbox_of(use),
                      network=self.network_of(use), yours=self.yours(), mcp=self.mcp_on(use),
                      mxc=page.mxc_words(state, build), bwrap=self.bwrap_words() if self.system != "windows" else "",
                      system_files=self.system_files())
        if use is None or at is None:
            rows = page.rows(server=page.NO_SERVER, model="", typed=None, known=None, used=None, keyed=False,
                             plain=False, chosen=False, **common)
            return {"tables": [page.table(rows)]}
        typed, known, context = self.contexts(use, at)
        rows = page.rows(server=server_words(at), model=use.model, typed=typed, known=known, used=context,
                         keyed=bool(str(at.get("key") or "").strip()), plain=bool(at.get("plain")), chosen=True,
                         **common)
        return {"tables": [page.table(rows)]}

    def status(self) -> dict:
        """Its Main: the harness's (the install, what it uses, the Model servers, Use…, Open…, Command…), Before you
        use it, and its facts: the package pinned for this system, a Codex of yours, its sandbox; as problems, a
        Windows older than MXC while mxc is chosen, a Linux whose user namespaces bubblewrap cannot use, Codex's
        system files, its folder inside the temporary folder. Nothing is run and nothing is asked over the network.
        Never raises."""
        out = super().status()
        if out.get("applies") is False or not out.get("valid", True):
            return out
        build = self.build()
        if build is not None:
            out["pinned"] = page.pinned(build[0])
        yours = self.yours()
        if yours:
            out["yours"] = page.yours_fact(yours)
        use = self.use_kept()
        sandbox = self.sandbox_of(use)
        out["sandbox"] = page.sandbox_fact(self.system, sandbox)
        problems = [str(out.get("problem") or "")]
        if self.system == "windows":
            state, text = self.mxc_state()
            if state == "older" and sandbox == "mxc":
                problems.append(page.mxc_problem(text))
            named = self.system_files()
            if named:
                problems.append(page.policy_problem(named[0]))
        else:
            problems.append(self.userns_problem())
            found = self.system_files()
            if found:
                problems.append(page.system_problem(found))
        if self.home_in_temp():
            problems.append(page.temp_problem(str(self.codex_home())))
        if any(problems):
            out["problem"] = "; ".join(p for p in problems if p)
        return out

    def api_facts(self) -> dict:
        """What it holds of its APIs, asking nothing: the install, what it is started against, its folder, this
        system's file."""
        try:
            have, use, build = self.installed(), self.use_kept(), self.build()
        except Exception:  # noqa: BLE001 - what it holds is extra: its page is drawn without it
            return {}
        return {
            CODEX: {"Installed": f"{have.version} in {have.path}" if have is not None else "not installed",
                    "Started against": f"{use.server}: {use.model}" if use is not None else "nothing yet",
                    "Its folder": str(self.codex_home())},
            DOWNLOADS: {"This system's package": build[0] if build is not None else "none pinned"},
        }


MACHINE = CodexCliPlugin()

__all__ = ["MACHINE", "CodexCliPlugin", "Refusal", "LIBS_FLOOR", "__version__"]
