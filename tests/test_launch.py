"""How Codex CLI is started (the plan's X1 and the pre-build checks, C-X1): each model server's start as Codex reads its
command (Ollama found here; llama.cpp with a key; vLLM on another machine over plain http; LMDeploy refused, since it
speaks no Responses API); the exact command, folder and environment of a window on Windows and the lines to paste on
both systems; the key and the token in no command, no file and no line; config.toml written whole, every folder
untrusted, a .env beside it removed; what is dropped from what Codex inherits; each option's effect; Liminal's MCP over
HTTP and through the bridge; each refusal in its words; its older transcripts pruned as a window opens, and never by
Command… or while a window is open.

Nothing is started: the window's process is a stand-in, the platform and the login are stand-ins."""
from __future__ import annotations

import os
import tomllib
from pathlib import Path

import pytest

from conftest import (BRIDGE, CODER, DECLARED, ENDPOINT, HTTP, KEY, KEY_VARIABLE, chosen, installed, made,
                      overridden, refused)
from liminal_libs import console
from liminal_libs.machines import children
from liminal_libs.machines.children import PLACEHOLDER
from liminal_libs.machines.harness import BREAKAWAY, NEW_CONSOLE, RUN_IT
from plugin_platform_codex_cli import constants, files

# what each model server's start is told (its -c words as Codex reads them), the sandbox's words aside
SERVED = {
    "ollama/default": ("qwen3:8b", {"name": "Liminal", "base_url": HTTP + "127.0.0.1:11434/v1",
                                    "wire_api": "responses"}, 40960),
    "llamacpp/gpu": (CODER, {"name": "Liminal", "base_url": HTTP + "127.0.0.1:9931/v1", "wire_api": "responses",
                             "env_key": "LIMINAL_SERVER_KEY"}, 65536),
    "vllm/box": ("Qwen/Qwen3-8B", {"name": "Liminal", "base_url": HTTP + "gpu-box.example.test:8000/v1",
                                   "wire_api": "responses"}, 32768),
}
PATHS = {"windows": "C:\\Windows\\System32;C:\\tools", "linux": "/usr/local/bin:/usr/bin"}


def program(p) -> str:
    return str(p.home / "app" / "0.170.0" / "bin" / ("codex.exe" if p.system == "windows" else "codex"))


def started(p, folder, key: str = ""):
    """The launch of a start in `folder` against what Use… keeps."""
    use = p.use_kept()
    return p._launch(str(folder), use, p.serving_of(use.server), key)


def config(p) -> dict:
    return tomllib.loads((p.codex_home() / "config.toml").read_text(encoding="utf-8"))


# -- each model server ------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("system", ["windows", "linux"])
@pytest.mark.parametrize("server", list(SERVED))
def test_each_start_is_told_its_server_its_model_and_its_sandbox(tmp_path, project, system, server):
    p = made(tmp_path, system)
    installed(p)
    model, provider, context = SERVED[server]
    chosen(p, server, model)
    launch = started(p, project, PLACEHOLDER if server == "llamacpp/gpu" else "")
    assert launch.argv[:2] == (program(p), "--no-daemon")
    said = overridden(launch.argv)
    expected = {"approval_policy": "on-request", "sandbox_mode": "workspace-write",
                "sandbox_workspace_write": {"network_access": False}, "model_provider": "liminal",
                "model_providers": {"liminal": provider}, "model": model, "model_context_window": context}
    if system == "windows":
        expected["windows"] = {"sandbox": "mxc"}
    assert said == expected
    assert launch.cwd == str(project) and launch.env["CODEX_HOME"] == str(p.codex_home())
    parsed = config(p)
    assert list(parsed["projects"]) == [os.path.abspath(project)]
    assert parsed["projects"][os.path.abspath(project)] == {"trust_level": "untrusted"}


def test_lmdeploy_and_a_server_that_does_not_say_it_are_refused_before_anything(windows, project):
    p = windows
    installed(p)
    p.app.serving["ollama"]["instances"][0].pop("speaks")  # (a plugin on a library before 1.66.0 says nothing)
    for server, model, speaks in (("lmdeploy/turbo", "internlm3-8b", "chat and completions"),
                                  ("ollama/default", "qwen3:8b", "nothing")):
        chosen(p, server, model)
        at = p.serving_of(server, fresh=True)
        words = refused(lambda: p.command(str(project)))
        assert words == (f"{at['plugin_title']} / {server.split('/')[1]} offers no Responses API (its plugin says it "
                         f"speaks {speaks}): Codex CLI asks a model server for nothing else")
        assert p.fits(at) == words
    assert not (p.codex_home() / "config.toml").exists()  # a refusal writes nothing


def test_a_window_on_windows_is_started_with_its_command_its_folder_and_its_environment(windows, project):
    p = windows
    installed(p)
    chosen(p, "llamacpp/gpu", CODER)
    answer = p.open(str(project))
    [start] = p.out.popen.made
    words = started(p, project, KEY).argv
    assert start["argv"] == console.hold_command(list(words))
    assert start["cwd"] == str(project) and start["creationflags"] == NEW_CONSOLE | BREAKAWAY
    home = str(Path(p.out.env["USERPROFILE"]))
    assert start["env"] == {"PATH": PATHS["windows"], "USERPROFILE": home, "CODEX_HOME": str(p.codex_home()),
                            "LIMINAL_SERVER_KEY": KEY}  # no pair of Liminal's, no OPENAI_* or CODEX_* of yours
    assert answer["ok"] is True and answer["said"] == (f"Codex CLI opened in a window of its own in {project}, started "
                                                       f"against llama.cpp / gpu with {CODER}")
    assert not any(KEY in word for word in start["argv"]) and KEY not in str(answer)
    assert KEY not in (p.codex_home() / "config.toml").read_text(encoding="utf-8")


@pytest.mark.parametrize("system", ["windows", "linux"])
def test_the_lines_to_paste_hold_no_key_and_end_in_its_command(tmp_path, project, system):
    p = made(tmp_path, system, interactive=False)
    installed(p)
    chosen(p, "llamacpp/gpu", CODER)
    answer = p.command(str(project))
    lines = answer["lines"]
    assert answer["ok"] is True and answer["said"] == RUN_IT
    assert p.open(str(project)) == answer  # no window here: the same lines
    assert p.out.popen.made == [] and not any(KEY in line for line in lines)
    assert sum(PLACEHOLDER in line for line in lines) == 1
    assert any("LIMINAL_SERVER_KEY" in line and PLACEHOLDER in line for line in lines)
    for name in ("OPENAI_API_KEY", "CODEX_HOME", "CODEX_SQLITE_HOME", KEY_VARIABLE, "MASSIVE_API_KEY"):
        unset = f"Remove-Item Env:{name} -ErrorAction SilentlyContinue" if system == "windows" else f"unset {name}"
        assert unset in lines, name
    last = lines[-1]
    assert program(p) in last and "--no-daemon" in last and "model_provider=liminal" in last
    assert ("windows.sandbox=mxc" in last) is (system == "windows")


def test_what_codex_inherits_drops_every_hosted_key_every_codex_and_openai_variable_and_every_pair_of_liminals(
        windows, project):
    p = windows
    installed(p)
    chosen(p)
    launch = started(p, project)
    assert launch.drop == (*constants.DROP, *DECLARED, "LIMINAL_*") and launch.secret == ()
    for pattern in ("OPENAI_*", "CODEX_*", "ANTHROPIC_*", "OLLAMA_*", "OTEL_*", "GOOSE_*", "OPENCODE_*"):
        assert pattern in constants.DROP, pattern
    keyed = started(p, project, KEY)
    assert keyed.secret == ("LIMINAL_SERVER_KEY",) and keyed.env["LIMINAL_SERVER_KEY"] == KEY
    assert not any(KEY in word for word in keyed.argv)


# -- its options ------------------------------------------------------------------------------------------------------
def test_its_sandbox_and_its_network_reach_codex_and_elevated_never(windows, project):
    p = windows
    installed(p)
    for given, sandbox in ((None, "mxc"), ("mxc", "mxc"), ("unelevated", "mxc"), ("elevated", "mxc")):
        chosen(p, **({"sandbox": given} if given else {}))
        said = overridden(started(p, project).argv)
        assert said["windows"] == {"sandbox": sandbox} and config(p)["windows"] == {"sandbox": sandbox}
    chosen(p, network="on")
    assert overridden(started(p, project).argv)["sandbox_workspace_write"] == {"network_access": True}
    assert config(p)["sandbox_workspace_write"] == {"network_access": True}
    assert "elevated" not in [w.partition("=")[2] for w in started(p, project).argv]
    assert not any("sandbox setup" in w or w == "sandbox" for w in started(p, project).argv)


def test_use_refuses_a_sandbox_it_does_not_offer(windows):
    installed(windows)
    assert "elevated" in refused(lambda: windows.use("ollama/default", "qwen3:8b", None, "elevated"))
    assert "unelevated" in refused(lambda: windows.use("ollama/default", "qwen3:8b", None, "unelevated"))


def test_on_linux_no_windows_sandbox_is_written(linux, project):
    installed(linux)
    chosen(linux, sandbox="unelevated")
    assert "windows" not in overridden(started(linux, project).argv) and "windows" not in config(linux)


def test_a_context_not_said_or_too_small_is_refused_and_a_typed_one_is_used(windows, project):
    p = windows
    installed(p)
    p.app.serving["llamacpp"]["instances"][0]["context"] = None
    chosen(p, "llamacpp/gpu", CODER)
    assert refused(lambda: p.command(str(project))) == (f"llama.cpp / gpu does not say {CODER}'s context: give it "
                                                         "under Use… (Context)")
    p.app.serving["llamacpp"]["instances"][0]["context"] = 4096
    p.serving_of("llamacpp/gpu", fresh=True)
    assert "8,192 tokens at the least, and 4,096" in refused(lambda: p.command(str(project)))
    chosen(p, "llamacpp/gpu", CODER, context=100000)
    assert overridden(started(p, project).argv)["model_context_window"] == 100000


def test_what_codex_cannot_be_given_is_refused_in_words(windows, project):
    p = windows
    installed(p)
    p.app.serving["ollama"]["instances"][0]["models"].append({"id": "it's", "context": 40960, "tools": True})
    chosen(p, "ollama/default", "it's")
    words = refused(lambda: p.command(str(project)))
    assert words.startswith("Codex cannot be given what this start needs: the model's id holds a single quote")
    assert words.endswith("Nothing was started")


# -- config.toml ------------------------------------------------------------------------------------------------------
def test_config_toml_keeps_every_folder_untrusted_and_marks_a_trusted_one_again(windows, project, tmp_path):
    p = windows
    installed(p)
    chosen(p)
    other = tmp_path / "other"
    other.mkdir()
    started(p, other)
    path = p.codex_home() / "config.toml"
    text = path.read_text(encoding="utf-8").replace('trust_level = "untrusted"', 'trust_level = "trusted"')
    path.write_text(text + '\nmodel = "chosen in Codex"\n', encoding="utf-8")  # (Codex's own edits)
    started(p, project)
    parsed = config(p)
    assert list(parsed["projects"]) == [os.path.abspath(project), os.path.abspath(other)]
    assert all(v == {"trust_level": "untrusted"} for v in parsed["projects"].values())
    assert "model" not in parsed  # written whole again


def test_config_toml_marks_the_newest_folders_alone(windows, project, monkeypatch):
    p = windows
    installed(p)
    chosen(p)
    monkeypatch.setattr(constants, "PROJECTS_KEPT", 3)
    folders = []
    for n in range(5):
        folder = project / f"f{n}"
        folder.mkdir()
        folders.append(os.path.abspath(folder))
        started(p, folder)
    assert list(config(p)["projects"]) == folders[::-1][:3]


def test_a_dot_env_beside_it_is_removed_and_one_that_cannot_be_refuses(windows, project, monkeypatch):
    p = windows
    installed(p)
    chosen(p)
    env_file = p.codex_home() / ".env"
    env_file.parent.mkdir(parents=True)
    env_file.write_text("OPENAI_API_KEY=planted\n", encoding="utf-8")
    started(p, project)
    assert not env_file.exists()
    env_file.write_text("OPENAI_API_KEY=planted\n", encoding="utf-8")
    real = Path.unlink

    def stuck(self, *a, **k):
        if self.name == ".env":
            raise PermissionError("in use")
        return real(self, *a, **k)
    monkeypatch.setattr(Path, "unlink", stuck)
    assert "which Codex would read into its environment, could not be removed (in use)" in refused(
        lambda: p.command(str(project)))


def test_a_config_toml_that_cannot_be_read_back_is_written_whole_all_the_same(windows, project):
    p = windows
    installed(p)
    chosen(p)
    path = p.codex_home() / "config.toml"
    path.parent.mkdir(parents=True)
    path.write_text("this is [not toml", encoding="utf-8")
    started(p, project)
    assert list(config(p)["projects"]) == [os.path.abspath(project)]


# -- the PATH it is given ---------------------------------------------------------------------------------------------
@pytest.mark.parametrize("system, given, whole", [
    ("windows", "C:\\Windows\\System32;;.;tools;C:\\tools;\\\\server\\share", "C:\\Windows\\System32;C:\\tools;"
                                                                              "\\\\server\\share"),
    ("windows", "\"C:\\Program Files\\x\";bin", "\"C:\\Program Files\\x\""),
    ("linux", "/usr/bin::.:bin:/usr/local/bin", "/usr/bin:/usr/local/bin"),
])
def test_a_path_entry_that_means_the_folder_is_left_out(tmp_path, project, system, given, whole):
    p = made(tmp_path, system)
    installed(p)
    chosen(p)
    p.out.env["PATH"] = given
    assert started(p, project).env["PATH"] == whole
    p.out.env["PATH"] = PATHS[system]
    assert "PATH" not in started(p, project).env  # (nothing to leave out: its own stays)


# -- Liminal's MCP ----------------------------------------------------------------------------------------------------
def test_liminals_mcp_over_http_with_a_token_for_the_window_alone(tmp_path, project):
    p = made(tmp_path, "windows", mcp=True)
    installed(p)
    chosen(p, mcp="on")
    answer = p.open(str(project))
    [start] = p.out.popen.made
    [token] = p.app.minted
    assert answer["ok"] is True and start["env"]["LIMINAL_MCP_TOKEN"] == token
    assert not any(token in w for w in start["argv"]) and token not in (p.codex_home() / "config.toml").read_text(
        encoding="utf-8")
    said = overridden(start["argv"][start["argv"].index(program(p)):])
    assert said["mcp_servers"]["liminal"] == {
        "url": ENDPOINT, "bearer_token_env_var": "LIMINAL_MCP_TOKEN", "http_headers": {"X-Liminal-Charts": "1"},
        "startup_timeout_sec": 30, "tool_timeout_sec": 110, "enabled": True}
    lines = p.command(str(project))["lines"]
    assert not any(token in line for line in lines) and len(p.app.minted) == 1  # Command… asks no token
    p.out.popen.windows[0].code = 0
    p.running()
    assert p.app.ended == [token]  # the window gone: its token ended


def test_liminals_mcp_through_the_bridge_where_the_route_is_not_served(tmp_path, project):
    p = made(tmp_path, "linux", mcp=True, interactive=False)
    bridge = ["/usr/bin/python3", "-I", "-S", "/home/you/plugins/plugin-platform-mcp/bridge.py", "--port", "9775"]
    p.app.offer = {**p.app.offer, "wires": ["stdio"], "endpoint": "", "bridge": bridge}
    installed(p)
    chosen(p, mcp="on")
    lines = p.command(str(project))["lines"]
    said = overridden(started(p, project).argv)
    assert said["mcp_servers"]["liminal"] == {
        "command": bridge[0], "args": bridge[1:], "env_vars": ["LIMINAL_MCP_TOKEN"], "startup_timeout_sec": 30,
        "tool_timeout_sec": 110, "enabled": True}
    assert all(not children.not_passed(w) for w in started(p, project).argv)
    assert lines[-1].count("mcp_servers.liminal.command") == 1


@pytest.mark.parametrize("system, bridge", [("windows", ["python.exe", *BRIDGE[1:]]),
                                            ("linux", ["python3", "-I", "/x/bridge.py"]),
                                            ("linux", BRIDGE)])  # (a Windows path is no whole path on Linux)
def test_a_bridge_not_named_by_a_whole_path_is_refused(tmp_path, project, system, bridge):
    p = made(tmp_path, system, mcp=True, interactive=False)
    p.app.offer = {**p.app.offer, "wires": ["stdio"], "endpoint": "", "bridge": bridge}
    installed(p)
    chosen(p, mcp="on")
    assert refused(lambda: p.command(str(project))) == ("Codex cannot be given what this start needs: the MCP "
                                                        "plugin's bridge is not named by a whole path. Nothing was "
                                                        "started")
    on_windows = made(tmp_path / "w", "windows", mcp=True, interactive=False)
    on_windows.app.offer = {**on_windows.app.offer, "wires": ["stdio"], "endpoint": ""}
    installed(on_windows)
    chosen(on_windows, mcp="on")
    assert overridden(started(on_windows, project).argv)["mcp_servers"]["liminal"]["command"] == BRIDGE[0]


def test_liminals_mcp_off_is_in_no_word(windows, project):
    installed(windows)
    chosen(windows)
    assert "mcp_servers" not in overridden(started(windows, project).argv)
    assert "mcp_servers" not in config(windows)


# -- its transcripts --------------------------------------------------------------------------------------------------
def transcripts(p, count: int, size: int = 10, folder: str = "sessions") -> list[Path]:
    """`count` stand-in transcripts, the oldest first, laid out as Codex lays them out (sessions/YYYY/MM/DD), each
    written days before the clock's now (which it moves on to 10,000,000 s): none is too fresh to prune."""
    p.out.clock.now = max(p.out.clock.now, 10_000_000.0)
    made_ = []
    for n in range(count):
        path = p.codex_home() / folder / "2026" / "11" / f"{n % 28 + 1:02d}" / f"rollout-{n:04d}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x" * size)
        os.utime(path, (1_000_000 + n, 1_000_000 + n))
        made_.append(path)
    return made_


def test_an_open_that_opens_a_window_keeps_the_newest_fifty_transcripts(windows, project):
    p = windows
    installed(p)
    chosen(p)
    kept = transcripts(p, 60)
    other = p.codex_home() / "sessions" / "notes.txt"
    other.write_text("not a transcript", encoding="utf-8")
    answer = p.open(str(project))
    assert answer["ok"] is True and answer["lines"][-1] == "10 older transcripts removed"
    assert [x.exists() for x in kept] == [False] * 10 + [True] * 50 and other.exists()


def test_transcripts_past_their_bytes_go_too_and_archived_ones_count(windows, project, monkeypatch):
    p = windows
    installed(p)
    chosen(p)
    monkeypatch.setattr(constants, "TRANSCRIPTS_BYTES", 250)
    older = transcripts(p, 3, size=100, folder="archived_sessions")
    newer = transcripts(p, 0)
    path = p.codex_home() / "sessions" / "2026" / "11" / "26" / "rollout-new.jsonl.zst"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"z" * 100)
    os.utime(path, (2_000_000, 2_000_000))
    assert p.prune_transcripts() == 2 and newer == []
    assert path.exists() and [x.exists() for x in older] == [False, False, True]
    assert not (p.codex_home() / "archived_sessions" / "2026" / "11" / "01").exists()  # (its empty folder gone)


@pytest.mark.parametrize("system", ["windows", "linux"])
def test_a_transcript_written_lately_is_never_pruned_though_past_what_is_kept(tmp_path, monkeypatch, system):
    """A Codex started from Command…'s lines is no window of the plugin's: its transcript, written a minute ago and
    alone past the bytes kept, stays (on Linux it would be unlinked while Codex holds it open); the old ones go."""
    p = made(tmp_path, system)
    installed(p)
    chosen(p)
    old = transcripts(p, 3, size=100)
    live = p.codex_home() / "sessions" / "2026" / "11" / "27" / "rollout-live.jsonl"
    live.parent.mkdir(parents=True, exist_ok=True)
    live.write_bytes(b"x" * 500)
    os.utime(live, (p.out.clock() - 60, p.out.clock() - 60))
    monkeypatch.setattr(constants, "TRANSCRIPTS_BYTES", 250)
    assert not p.running()
    assert p.prune_transcripts() == 3 and live.exists() and not any(x.exists() for x in old)


def test_no_transcript_is_removed_by_command_or_while_a_window_is_open(windows, project):
    p = windows
    installed(p)
    chosen(p)
    kept = transcripts(p, 55)
    p.command(str(project))
    assert all(x.exists() for x in kept)  # Command… is a read
    assert p.open(str(project))["ok"] is True and sum(x.exists() for x in kept) == 50
    more = [x for x in kept if x.exists()]
    for n in range(5):  # five newer while the window is open
        path = p.codex_home() / "sessions" / "late" / f"rollout-late{n}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"y")
        os.utime(path, (3_000_000 + n, 3_000_000 + n))
    answer = p.open(str(project))
    assert answer["ok"] is True and "older transcripts removed" not in " ".join(answer["lines"])
    assert all(x.exists() for x in more)


def test_the_launch_is_told_whole_paths_and_config_toml_is_what_files_writes(tmp_path, project, monkeypatch):
    p = made(tmp_path, "windows")
    installed(p)
    chosen(p)
    monkeypatch.chdir(tmp_path)
    launch = started(p, project)
    assert Path(launch.argv[0]).is_absolute() and Path(launch.env["CODEX_HOME"]).is_absolute()
    text = (p.codex_home() / "config.toml").read_text(encoding="utf-8")
    assert text == files.config_toml(system="windows", folders=[os.path.abspath(project)])
