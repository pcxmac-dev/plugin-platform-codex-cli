"""Its Main: a status that runs nothing and asks nothing over the network (the MXC build read from a stand-in registry,
user namespaces from stand-in /proc files); Before you use it for each model server and each sandbox (its start-up
fetch and its transcripts said plainly: the user's answer 6); Open…'s confirmation ending in what Codex must say;
how it opens on each system; its facts and its problems; its API facts asking nothing."""
from __future__ import annotations

import pytest

from conftest import CODER, Proc, Registry, chosen, form, installed, made, never, rows
from plugin_platform_codex_cli import constants, page

ANNOUNCEMENT = "https:" + "//raw.githubusercontent.com/openai/codex/main/announcement_tip.toml"


@pytest.mark.parametrize("system", ["windows", "linux"])
def test_main_runs_nothing_and_asks_nothing_over_the_network(tmp_path, system):
    p = made(tmp_path, system)
    installed(p)
    chosen(p, "llamacpp/gpu", CODER)
    p.out.popen = never("a window")  # the opener, the streamer, the runner, a port and an instance refuse already
    status = p.status()
    assert status["valid"] is True and status["summary"] == "Codex CLI 0.170.0" and "problem" not in status
    assert [t["title"] for t in status["tables"]] == ["Before you use it", "Model servers"]
    assert status["uses"] == f"llama.cpp / gpu: {CODER}"
    assert {a for _, a, _ in p.app.asked} == {"serving"}  # its model servers, through the app
    assert not p.codex_home().exists()  # a status writes nothing
    if system == "windows":
        assert set(p._registry.read) == {(constants.VERSION_KEY, "CurrentBuild"), (constants.VERSION_KEY, "UBR"),
                                         (constants.POLICY_KEY, constants.POLICY_VALUE)}
    else:
        assert set(p._proc.read) <= set(constants.USERNS.values())


def test_before_you_use_it_for_ollama_on_windows_with_mxc(windows):
    p = windows
    installed(p)
    chosen(p)
    said = rows(p.status())
    assert list(said) == ["It acts as you", "Its sandbox", "Its start-up fetch", "Its transcripts", "Local only",
                          "Its ports", "The folder's .codex", "The model", "What it shares with a Codex of yours",
                          "Its configuration"]
    assert said["It acts as you"] == page.ACTS and "asks you before going beyond that" in page.ACTS
    box = said["Its sandbox"]
    assert box.startswith("On Windows its commands run in Microsoft's MXC (Use…, Sandbox: mxc)")
    assert "they reach neither the network nor this machine's own addresses, so not the platform" in box
    assert "its elevated sandbox, which asks for administrator rights" in box and "are never chosen" in box
    assert ("This Windows (26300.9974) is later than the builds MXC came with (26100.9278, 26200.9278), so MXC is "
            "expected here, not confirmed") in box
    assert box.endswith("Its commands' network is off (Use…, Network).")
    assert said["Its start-up fetch"] == (
        f"Its terminal screen fetches {ANNOUNCEMENT} from GitHub at every start, by itself, from your address (2 s at "
        "the most): no setting of Codex 0.170.0 turns it off. It is the one call it makes on its own here.")
    kept = said["Its transcripts"]
    assert f"under {p.codex_home()}, in sessions and archived_sessions" in kept
    assert "no setting of its terminal screen turns this off" in kept
    assert "The plugin keeps the newest 50 (200 MB at the most) and removes older ones as each Open… opens a window"\
        in kept
    local = said["Local only"]
    assert local.startswith("The one model server it is given is Ollama / default")
    for words in ("analytics", "feedback", "update check", "web search", "shared background server",
                  "your keyring is never read", "the Codex plugin's OpenAI key never reaches it"):
        assert words in local, words
    assert "127.0.0.1:1455" in said["Its ports"] and said["Its ports"].startswith("It opens no port by itself here")
    assert "marked untrusted" in said["The folder's .codex"]
    model = said["The model"]
    assert model.startswith(page.MODEL) and "LMDeploy has none" in model
    assert "llama.cpp's is reported unreliable" in model
    assert "It is told 40,960 tokens of context (as Ollama / default says it). That is under the 65,536" in model
    assert "%USERPROFILE%\\.codex" in said["What it shares with a Codex of yours"]
    assert "written whole at each start" in said["Its configuration"]


def test_a_kept_unelevated_choice_starts_mxc_and_the_network_on_is_said(windows):
    p = windows
    installed(p)
    chosen(p, sandbox="unelevated", network="on")  # (kept from before: it is no longer offered)
    status = p.status()
    box = rows(status)["Its sandbox"]
    assert box.startswith("On Windows its commands run in Microsoft's MXC (Use…, Sandbox: mxc)")
    assert "Its unelevated sandbox, whose commands reach this machine's own addresses" in box
    assert "Microsoft's MXC" in page.open_words(system="windows", sandbox="unelevated", network=True, window=True)
    assert box.endswith("Its commands' network is on (Use…, Network): they reach the network and this machine's own "
                        "addresses, the platform's among them.")
    assert status["sandbox"] == page.SANDBOX_WORDS["mxc"] and "unelevated" not in page.SANDBOX_WORDS


def test_a_keyed_llama_cpp_a_remote_vllm_and_liminals_mcp(tmp_path):
    p = made(tmp_path, "linux", mcp=True)
    installed(p)
    chosen(p, "llamacpp/gpu", CODER)
    said = rows(p.status())
    assert said["Its key"] == ("llama.cpp / gpu's key reaches Codex in its environment alone (LIMINAL_SERVER_KEY, "
                               "which its provider names), never in a file or on its command line; its commands are "
                               "never given it.")
    assert "It is told 65,536 tokens of context" in said["The model"]
    chosen(p, "vllm/box", "Qwen/Qwen3-8B", mcp="on")
    said = rows(p.status())
    assert said["Plain http"] == ("vLLM / box is asked over plain http on another machine: prompts and code can be "
                                  "read on the way.")
    assert said["Liminal's MCP"] == page.MCP and "Its commands are never given the token" in page.MCP
    assert said["Its sandbox"].startswith("On Linux its commands run in bubblewrap")
    assert "Here no bwrap is on PATH: Codex uses its package's own." in said["Its sandbox"]


def test_before_a_choice_it_says_what_holds_for_any(windows):
    said = rows(windows.status())
    assert said["The model"] == page.MODEL and "Its key" not in said and "Liminal's MCP" not in said


@pytest.mark.parametrize("system", ["windows", "linux"])
def test_opens_confirmation_ends_in_what_codex_must_say(tmp_path, system):
    p = made(tmp_path, system)
    installed(p)
    chosen(p)
    words = form(p.status(), "ai-open")["confirm"]["words"]
    box = "Microsoft's MXC" if system == "windows" else "bubblewrap"
    if system == "windows":
        assert words.startswith("A terminal window opens there with Codex CLI started against Ollama / default.")
        assert words.endswith(f"Codex acts as you inside {box}, its commands' network off, and asks before going "
                              f"beyond it. It fetches {ANNOUNCEMENT} at each start, and saves each session's "
                              "transcript: the newest 50 are kept, older transcripts are removed as it opens. A "
                              "folder's .codex/ is not loaded.")
    else:  # (no display: the lines are shown)
        assert words.startswith("No window can be opened from here: the command is shown")
        assert "older transcripts are removed at the next Open… that opens a window" in words
        assert f"inside {box}" in words


def test_its_facts(windows, tmp_path):
    p = windows
    status = p.status()
    assert status["pinned"] == "0.170.0 (codex-package-x86_64-pc-windows-msvc.tar.gz)"
    assert status["sandbox"] == page.SANDBOX_WORDS["mxc"] and "yours" not in status and "problem" not in status


@pytest.mark.parametrize("build, state", [((26100, 9278), "listed"), ((26200, 9500), "listed"),
                                          ((26300, 9974), "later"), ((26100, 7000), "older"),
                                          ((22631, 4000), "older")])
def test_the_windows_build_against_the_ones_mxc_came_with(tmp_path, build, state):
    p = made(tmp_path, "windows", registry=Registry(build))
    assert p.mxc_state() == (state, f"{build[0]}.{build[1]}")
    problem = p.status().get("problem", "")
    assert ("has no MXC yet" in problem) is (state == "older")
    chosen(p, sandbox="unelevated")  # kept from before: mxc is still the one used, and said
    assert ("has no MXC yet" in p.status().get("problem", "")) is (state == "older")
    assert "unelevated" not in p.status().get("problem", "")


def test_a_build_that_cannot_be_read_says_nothing(tmp_path):
    p = made(tmp_path, "windows", registry=Registry(None))
    assert p.mxc_state() == ("", "") and "problem" not in p.status()
    assert "MXC came with" not in rows(p.status())["Its sandbox"]


def test_a_policy_naming_codexs_requirements_is_a_problem(tmp_path):
    p = made(tmp_path, "windows", registry=Registry(policy="C:\\Policies\\codex-requirements.toml"))
    assert p.status()["problem"] == ("a policy names Codex's requirements file "
                                     "(C:\\Policies\\codex-requirements.toml): what it requires comes above what a "
                                     "start is told, and can choose its sandbox")


@pytest.mark.parametrize("said, bwrap, why", [
    ({"max": "0"}, "", "this Linux allows no user namespaces (max_user_namespaces is 0)"),
    ({"max": "15000", "clone": "0"}, "", "unprivileged user namespaces are off (unprivileged_userns_clone is 0)"),
    ({"max": "15000", "apparmor": "1"}, "", "AppArmor restricts unprivileged user namespaces"),
    ({"max": "15000", "apparmor": "1"}, "/usr/bin/bwrap", ""),
    ({"max": "15000", "apparmor": "0"}, "", ""),
    ({}, "", ""),
])
def test_what_proc_says_of_user_namespaces(tmp_path, said, bwrap, why):
    p = made(tmp_path, "linux", proc=Proc(**said))
    p.out.which = lambda name, *a, **k: (bwrap or None) if name == "bwrap" else None
    problem = p.status().get("problem", "")
    if why:
        assert problem.startswith("bubblewrap cannot run Codex's commands here: ") and why in problem
        assert problem.endswith("Changing that is root's; until then every command fails")
    else:
        assert problem == ""
    if bwrap:
        assert f"Here Codex uses {bwrap}." in rows(p.status())["Its sandbox"]


def test_codexs_system_files_on_linux_are_a_problem(tmp_path, monkeypatch):
    found = tmp_path / "etc-codex" / "requirements.toml"
    found.parent.mkdir()
    found.write_text("", encoding="utf-8")
    monkeypatch.setattr(constants, "SYSTEM_FILES", (str(tmp_path / "etc-codex" / "config.toml"), str(found)))
    p = made(tmp_path, "linux")
    assert p.system_files() == (str(found),)
    assert p.status()["problem"].startswith(f"Codex's system file {found} is there")
    assert f"{found} is there: Codex reads" in rows(p.status())["Its configuration"]


def test_its_folder_inside_the_temporary_folder_is_a_problem(tmp_path):
    p = made(tmp_path, "windows")
    p._temp = lambda: str(tmp_path)
    assert p.home_in_temp() and p.status()["problem"] == page.temp_problem(str(p.codex_home()))


def test_its_api_facts_ask_nothing(windows):
    p = windows
    p.app.ask = never("the platform")
    facts = p.api_facts()
    assert facts["Codex CLI"] == {"Installed": "not installed", "Started against": "nothing yet",
                                  "Its folder": str(p.codex_home())}
    assert facts["Codex releases"] == {"This system's package": "codex-package-x86_64-pc-windows-msvc.tar.gz"}
