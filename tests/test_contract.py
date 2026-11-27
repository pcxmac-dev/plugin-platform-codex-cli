"""The plugin conforms to the class contract (plugin API 2.2): liminal_libs.sources.conformance, read from the plugin
alone (nothing runs). A harness of the platform's AI plugins, drawn under AI plugins, Harnesses, at 523; its icon
Codex's own mark, drawn by the library; its hooks the harness base's and no other; Liminal's MCP offered over HTTP and
by the bridge; what it says of the interface it shares; one run state for the registry's copies; its versions and its
floor as pyproject says them."""
from __future__ import annotations

import re
import tomllib
from pathlib import Path

import liminal_libs
import plugin_platform_codex_cli as module
from liminal_libs.machines import harness
from liminal_libs.machines.ai import AiPlugin
from liminal_libs.machines.harness import Harness
from liminal_libs.sources.conformance import assert_module_conforms
from liminal_libs.ui import STATIC

HERE = Path(__file__).resolve().parent.parent
PYPROJECT = tomllib.loads((HERE / "pyproject.toml").read_text(encoding="utf-8"))


def release(version: str) -> tuple[int, ...]:
    """A release's number as a tuple ("1.66.0" -> (1, 66, 0)), what follows its digits left out."""
    return tuple(int(re.match(r"\d*", part).group() or 0) for part in str(version).split(".")[:3])


def test_it_conforms_to_the_class_contract():
    found = assert_module_conforms(module)
    assert [p.name for p in found] == ["codex-cli"] and all(p.api == "2.2" and not p.is_record for p in found)
    assert {p.SYSTEM for p in found} == {"platform"} and {p.KIND for p in found} == {"machine"}
    assert all(p.apis and p.interface()["apis"] == [a.name for a in p.apis] for p in found)
    p = module.MACHINE
    assert isinstance(p, Harness) and isinstance(p, AiPlugin) and p.title == "Codex CLI"
    assert p.about.startswith("OpenAI's open-source Codex CLI") and len(p.about) <= 120


def test_it_is_drawn_under_ai_plugins_harnesses_at_523():
    """Its section and group (liminal-libs 1.62.0): AI plugins, Harnesses, at 523, after OpenCode 520, Aider 521 and
    Continue 522, before Pi 524 and goose 525 (the plan of 2026-11-18)."""
    p = module.MACHINE
    assert (p.SECTION, p.GROUP, p.order) == ("ai", "harness", 523)


def test_its_icon_is_codexs_own_mark_drawn_by_the_library():
    """Codex's own mark (not the OpenAI knot of the Codex plugin), in liminal-libs 1.66.0's icons.js: a mark missing,
    or drawn under another name, fails it."""
    assert module.MACHINE.ICON == "codexcli"
    drawn = set(re.findall(r"^\s*([a-z]+):\s*'", (STATIC / "icons.js").read_text(encoding="utf-8"), re.M))
    assert "codexcli" in drawn, f"liminal-libs {liminal_libs.__version__} draws no codexcli mark"


def test_its_hooks_are_the_harness_bases_and_no_other():
    p = module.MACHINE
    hooks = p.interface()["hooks"]
    assert set(hooks) == {"present", "status", "refresh", "install", "uninstall", "use", "open", "command",
                          "ask_models"}
    assert p.HOOKS == Harness.HOOKS and "terminal" not in hooks
    assert p.JOB_HOOKS == ("install",) and p.CANCEL_HOOKS == ("install",)
    assert not p.gives("check") and p.STEPS == () and not p.gives("setup")  # the page asks Install at once
    assert hooks["open"] == "(folder=None) -> 'dict'"
    assert hooks["use"] == "(server, model, *values) -> 'dict'" and hooks["command"] == "(folder=None) -> 'dict'"
    assert getattr(module.CodexCliPlugin.open, "held", False)  # waits for no install: AiPlugin's START_HOOKS


def test_its_changes_are_asked_from_the_page_alone():
    """liminal-libs 1.99.0: a harness's changes are page-only, the base's four; it adds no change hook of its own, so
    it names none (PAGE_ONLY_HOOKS)."""
    assert "PAGE_ONLY_HOOKS" not in module.CodexCliPlugin.__dict__
    assert set(module.MACHINE.PAGE_ONLY_HOOKS) >= {"install", "uninstall", "use", "open"}


def test_its_options_and_liminals_mcp():
    p = module.MACHINE
    assert [s.name for s in p.OPTIONS] == ["context", "sandbox", "network", "mcp"]
    assert p.OPTIONS[-1] is harness.MCP_OPTION and p.MCP_WIRES == ("http", "stdio")
    sandbox = p.OPTIONS[1]
    assert sandbox.default == "mxc" and [c[0] for c in sandbox.choices] == ["mxc"]
    assert "elevated" not in [c[0] for c in sandbox.choices]  # needs administrator rights, changes the system
    assert "unelevated" not in [c[0] for c in sandbox.choices]  # its commands reach the platform (answer 5: mxc)
    assert "the platform's API among it" in sandbox.note and "neither is offered" in sandbox.note
    network = p.OPTIONS[2]
    assert network.default == "off" and [c[0] for c in network.choices] == ["off", "on"]
    assert not any(s.name in ("approvals", "approval_policy") for s in p.OPTIONS)  # on-request, always written
    context = p.OPTIONS[0]
    assert (context.min, context.max) == (8192, 2_000_000)


def test_what_it_says_of_the_interface_it_shares():
    """The Internal API tab's words (read by name; every plugin is middleware): a harness with no hook of its own, so
    no read of its own and no service; what it asks of the other plugins (the model servers and the MCP plugin) and
    what it keeps through the login are the base's."""
    p = module.MACHINE
    assert module.CodexCliPlugin.__dict__["READ_HOOKS"] == () and module.CodexCliPlugin.__dict__["SERVICE_HOOKS"] == ()
    assert "KEEPS" not in module.CodexCliPlugin.__dict__
    assert [ask[:2] for ask in p.ASKS] == [("", "serving"), ("", "models_of"), ("mcp", "client_offer"),
                                           ("mcp", "ensure_client"), ("mcp", "launch_token"), ("mcp", "end_launch")]
    assert p.KEEPS == ((p.variable("use"), "what it is started against: the model server, the model, the folder last "
                                           "opened and its options"),)
    assert p.variable("use") == "LIMINAL_AI_CODEX_CLI_USE"
    assert all(isinstance(n, str) and 0 < len(n) <= 400 for n in p.INTERNAL_NOTES)
    assert set(harness.MCP_NOTES) <= set(p.INTERNAL_NOTES)
    for hook in ("use", "open", "command", "status"):  # each says what it is in its first sentence
        assert (getattr(module.CodexCliPlugin, hook).__doc__ or "").strip(), hook


def test_a_copy_the_registry_hands_out_shares_what_the_plugin_keeps():
    p = module.CodexCliPlugin()
    copy = p.with_(origin="the plugin directory's checkout")
    assert copy is not p and copy._rt is p._rt and copy.out is p.out
    assert type(p._rt).__name__ == "CodexCliRun"


def test_its_versions_and_its_floor_are_pyprojects():
    project = PYPROJECT["project"]
    assert module.__version__ == project["version"] == "0.1.1"
    assert project["dependencies"] == ["liminal-libs>=1.99.0"]
    assert module.LIBS_FLOOR == module.MACHINE.LIBS_FLOOR == "1.99.0"  # the base's changes page-only
    assert project["entry-points"]["liminal.providers"] == {"codex-cli": "plugin_platform_codex_cli"}
    assert release(liminal_libs.__version__) >= release(module.LIBS_FLOOR)
    assert module.MACHINE.too_old() == ""
    changelog = (HERE / "CHANGELOG.md").read_text(encoding="utf-8")
    assert re.search(r"^## (\S+) \((\S+)\)", changelog, re.M).groups() == (module.__version__, "2026-11-27")


def test_a_library_older_than_its_floor_is_said_and_refuses_every_hook(monkeypatch, tmp_path):
    """Below 1.99.0 its base's changes (install, uninstall, use, open) can be asked by any program, as it names none
    of its own (below 1.66.0 there is no serving row saying what it speaks either): the page says so, and nothing
    runs."""
    from conftest import made, refused

    p = made(tmp_path)
    monkeypatch.setattr(liminal_libs, "__version__", "1.98.2")
    assert p.too_old() == "Codex CLI needs liminal-libs 1.99.0 or newer, and this is 1.98.2: update the library"
    status = p.status()
    assert status["valid"] is False and status["why"] == p.too_old()
    assert refused(lambda: p.ask("install", True)) == p.too_old()
