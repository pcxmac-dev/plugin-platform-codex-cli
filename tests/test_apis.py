"""What the plugin attaches to (plugin API 2.2): its four cards are sound; each call belongs to one of its card's parts;
every page they link is on its maker's own host; the calls they say the plugin makes are exactly the address an
install asked and the command a start ran, read from the stand-ins as the plugin sent them; nothing costs. With
LIMINAL_VENDOR_PAGES=1 alone, every address on them is asked (the only test here that reaches the network)."""
from __future__ import annotations

import os
import urllib.parse

import pytest

import plugin_platform_codex_cli as plugin
from conftest import archive, chosen, made, pin
from liminal_libs.machines.terminal import Output
from liminal_libs.sources import apis as A
from plugin_platform_codex_cli import apis as cards
from plugin_platform_codex_cli import constants


def test_its_cards_are_sound():
    assert A.problems(cards.APIS) == [] and plugin.MACHINE.apis is cards.APIS
    assert [a.name for a in cards.APIS] == ["Codex CLI", "Codex configuration (config.toml)", "Codex releases",
                                            "The Responses API as local servers speak it"]
    assert [a.kind for a in cards.APIS] == ["command", "file", "feed", "rest"]
    for api in cards.APIS:
        assert api.verified == cards.VERIFIED == "2026-11-18" and api.docs.startswith("https://")
        assert all(c.area in {x.name for x in api.areas} for c in api.calls), api.name
        assert api.used and api.covered
    codex = cards.CODEX_API
    assert len(codex.areas) > len(codex.covered) and len(codex.calls) > len(codex.used)  # more than it uses
    assert not any(c.costs for a in cards.APIS for c in a.calls)
    assert {c.name for c in codex.calls if not c.used} == {  # what it never runs, named
        f"GET {constants.ANNOUNCEMENT}", "codex exec", "codex login", "codex mcp add", "codex sandbox setup"}
    assert "LMDeploy has none" in cards.RESPONSES_API.about and "not OpenAI's service" in codex.about


def test_every_page_they_link_is_its_makers_own():
    for api in cards.APIS:
        for url in A.urls((api,)):
            assert urllib.parse.urlsplit(url).hostname in constants.MAKERS, url
    links = {x.url for x in cards.CODEX_API.links}
    for page in ("config-file/config-reference", "config-file/config-advanced", "sandboxing",
                 "windows/windows-sandbox", "agent-approvals-security", "extend/mcp?surface=cli"):
        assert "https:" + "//learn.chatgpt.com/docs/" + page in links, page
    for url in ("https:" + "//github.com/openai/codex/releases/tag/rust-v0.170.0",
                "https:" + "//github.com/openai/codex/blob/rust-v0.170.0/LICENSE",
                "https:" + "//github.com/openai/codex/blob/rust-v0.170.0/README.md"):
        assert url in links, url
    assert "https:" + "//github.com/openai/codex/releases/download/rust-v0.170.0/config-schema.json" in {
        x.url for x in cards.CONFIG_API.links}


@pytest.mark.parametrize("system", ["windows", "linux"])
def test_the_calls_it_says_it_makes_are_the_ones_it_makes(tmp_path, monkeypatch, system):
    p = made(tmp_path, system)
    p.out.opener = web = pin(monkeypatch, p.target(), archive(system))
    assert p.install(True, log=Output())["ok"] is True
    project = tmp_path / "project"
    project.mkdir()
    chosen(p)
    if system == "windows":
        assert p.open(str(project))["ok"] is True
        [start] = p.out.popen.made
        command = start["argv"][start["argv"].index("--") + 1:]
    else:  # (no display here: the lines to paste)
        launch = p._launch(str(project), p.use_kept(), p.serving_of("ollama/default"), "")
        command = list(launch.argv)
    asked = [urllib.parse.urlsplit(url) for url in web.asked]
    assert [(u.hostname, u.path.rsplit("/", 1)[0]) for u in asked] == [
        ("github.com", "/openai/codex/releases/download/rust-v0.170.0")]
    assert asked[0].path.endswith("/" + constants.TARGETS[p.target()][0])
    assert {c.name for c in cards.DOWNLOADS_API.used} == {"GET codex-package-<target>.tar.gz"}
    assert os.path.basename(command[0]) == constants.PROGRAM[system][1] and command[1] == "--no-daemon"
    assert set(command[2::2]) == {"-c"}
    assert {c.name for c in cards.CODEX_API.used} == {"codex --no-daemon -c KEY=VALUE ..."}
    assert (p.codex_home() / "config.toml").is_file() and {c.name for c in cards.CONFIG_API.used} == {
        "write config.toml"}


def test_its_hosts_are_the_ones_install_may_be_sent_to():
    hosts = {urllib.parse.urlsplit(constants.FILES).hostname, *constants.ASSET_HOSTS}
    assert hosts == set(constants.HOSTS)
    assert constants.FILES.startswith("https:" + "//github.com/openai/codex/releases/download/rust-v0.170.0/")


@pytest.mark.skipif(os.environ.get("LIMINAL_VENDOR_PAGES") != "1",
                    reason="reaches the makers' pages: LIMINAL_VENDOR_PAGES=1")
def test_every_address_on_its_cards_answers(monkeypatch):
    monkeypatch.undo()  # this test alone reaches the network (conftest refuses it to every other)
    assert A.dead_links(cards.APIS) == []
