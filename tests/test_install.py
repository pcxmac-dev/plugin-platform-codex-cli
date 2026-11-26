"""Install, update and uninstall: this system's package by its release's names (Windows x64, Linux x64; ARM64 not
pinned in this release), its pinned address, size, sha256 and hosts (C-X1.2b), downloaded, checked and unpacked as
the release lays it out (bin/ beside codex-resources/, which holds its sandbox's helpers; a package under a folder of
its own moved up), CURRENT written only once it is whole, a wrong sum, a cancel and a package without its helpers
each leaving nothing half-built and the install in use as it was, the uninstall leaving what it keeps, a Codex of
yours reported and never run, and none of its install scripts, npm or `codex sandbox setup` ever named in a command.

Real archives are made here in memory and unpacked by the library for real (tar.gz: Python's own); the web, the
window's process and the login are stand-ins. Nothing is downloaded, installed or started."""
from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

import plugin_platform_codex_cli as plugin
from conftest import PROGRAM_BYTES, archive, chosen, installed, made, members, pin, refused, tarred
from liminal_libs.machines.ai import CANCELLED
from liminal_libs.machines.terminal import Output
from plugin_platform_codex_cli import constants

PINNED = {  # C-X1.2b: GitHub's record of the release, rust-v0.170.0
    "windows-x64": ("codex-package-x86_64-pc-windows-msvc.tar.gz", 210098091,
                    "6ff4b22c63645ffd83aed9b722cbb0b9e5b79dc6e8916f50e362b3015fb327a9"),
    "linux-x64": ("codex-package-x86_64-unknown-linux-musl.tar.gz", 193641516,
                  "a77ff87be7ba809d715728270a78f5ce3527dc07529416d1ef8929b90b8475eb"),
}


def test_the_pins_are_the_releases_record():
    assert constants.TARGETS == PINNED
    assert constants.FILES == "https:" + "//github.com/openai/codex/releases/download/rust-v0.170.0/"
    assert not any(".zst" in a or ".zip" in a or "-gnu" in a for a, _, _ in constants.TARGETS.values())


@pytest.mark.parametrize("system, machine, target", [
    ("windows", "AMD64", "windows-x64"),
    ("linux", "x86_64", "linux-x64"),
])
def test_the_package_is_the_one_its_release_names_for_this_system(tmp_path, system, machine, target):
    p = made(tmp_path, system, machine=machine)
    assert p.target() == target and p.runs_here() == ""
    asset, size, sha = PINNED[target]
    source = p.source()
    assert (source.url, source.name, source.size, source.sha256, source.hosts) == (
        constants.FILES + asset, asset, size, sha, ("release-assets.githubusercontent.com",))
    pkg = p.package()
    assert (pkg.title, pkg.version, pkg.pin, pkg.size) == ("Codex CLI", "0.170.0", "0.170.0", size)
    assert pkg.hosts == ("github.com", "release-assets.githubusercontent.com")
    assert pkg.licence == "Codex CLI: Apache-2.0 (OpenAI)."
    assert pkg.parts == f"Codex CLI 0.170.0's package for this system ({asset}: the program and its sandbox's helpers)"


@pytest.mark.parametrize("system", ["windows", "linux"])
def test_arm64_and_an_unknown_processor_are_said_and_install_nothing(tmp_path, system):
    arm = made(tmp_path / "arm", system, machine="ARM64" if system == "windows" else "aarch64")
    where = "Windows" if system == "windows" else "Linux"
    assert arm.package() is None and arm.runs_here() == (
        f"Codex CLI 0.170.0's package for {where} on ARM64 is not pinned in this release of the plugin (x86-64 "
        "alone): it is not installed here")
    status = arm.status()
    assert status["valid"] is True and not any(f["id"] == "ai-install" for f in status["forms"])
    assert "not pinned in this release" in refused(lambda: arm.install(True))
    other = made(tmp_path / "other", system, machine="riscv64")
    assert other.target() == "" and other.runs_here() == (f"Codex CLI 0.170.0 has no package for riscv64 on {where}: "
                                                          "it is not installed here")


def test_the_target_is_worked_out_once(tmp_path):
    asked = []
    p = made(tmp_path, "linux")
    p._machine = lambda: asked.append(1) or "x86_64"
    for _ in range(3):
        p.target()
    assert asked == [1]


@pytest.mark.parametrize("system", ["windows", "linux"])
@pytest.mark.parametrize("top", ["", "codex-package"])
def test_install_downloads_checks_and_unpacks_it_as_laid_out_and_puts_it_in_use(tmp_path, monkeypatch, system, top):
    p = made(tmp_path, system)
    p.out.opener = web = pin(monkeypatch, p.target(), archive(system, top))
    out = Output()
    answer = p.install(True, log=out)
    folder = p.home / "app" / "0.170.0"
    program = folder / "bin" / ("codex.exe" if system == "windows" else "codex")
    assert answer["ok"] is True and answer["said"] == f"Codex CLI 0.170.0 installed in {program}"
    assert program.read_bytes() == PROGRAM_BYTES[system]
    laid = sorted(str(x.relative_to(folder)).replace("\\", "/") for x in folder.rglob("*") if x.is_file())
    assert laid == sorted(members(system))  # its layout kept whole: bin/ beside codex-resources/
    assert (p.home / "app" / "CURRENT").read_text(encoding="utf-8") == "0.170.0\n"
    assert web.asked == [constants.FILES + constants.TARGETS[p.target()][0]]
    assert not (p.home / "downloads").exists()  # the archive removed after a good install
    assert p.installed().path == str(program) and p.installed().version == "0.170.0"
    assert answer["lines"][0] == f"Codex CLI 0.170.0: {program}" and "nothing was started" in answer["lines"]
    assert "is the file pinned: its sha256 is" in out.read()[0]
    if os.name != "nt" and system == "linux":
        assert os.stat(program).st_mode & stat.S_IXUSR
    assert refused(lambda: p.install(True)) == "Codex CLI 0.170.0 is installed already"


@pytest.mark.skipif(os.name == "nt", reason="a file's mode is Linux's: Windows keeps none")
def test_a_program_or_a_bwrap_given_without_its_run_bit_is_made_runnable(tmp_path, monkeypatch):
    p = made(tmp_path, "linux")
    p.out.opener = pin(monkeypatch, p.target(), tarred(members("linux"), mode=0o644))
    answer = p.install(True, log=Output())
    folder = p.home / "app" / "0.170.0"
    assert answer["ok"] is True and "codex and bwrap made runnable for you" in answer["lines"]
    assert os.stat(folder / "bin" / "codex").st_mode & 0o700 == 0o700
    assert os.stat(folder / "codex-resources" / "bwrap").st_mode & 0o700 == 0o700


@pytest.mark.parametrize("system, helper", [("windows", "codex-resources/codex-command-runner.exe"),
                                            ("linux", "codex-resources/bwrap")])
def test_a_package_without_its_sandboxs_helper_installs_nothing(tmp_path, monkeypatch, system, helper):
    p = made(tmp_path, system)
    given = members(system)
    del given[helper]
    p.out.opener = pin(monkeypatch, p.target(), tarred(given))
    answer = p.install(True, log=Output())
    assert answer["ok"] is False and f"holds no {helper}, which its sandbox needs" in answer["said"]
    assert p.installed() is None and not (p.home / "app" / "0.170.0").exists()


def test_a_package_without_its_program_installs_nothing(windows, monkeypatch):
    given = {k: v for k, v in members("windows").items() if not k.startswith("bin/")}
    windows.out.opener = pin(monkeypatch, "windows-x64", tarred(given))
    answer = windows.install(True, log=Output())
    assert answer["ok"] is False and "holds no bin/codex.exe" in answer["said"] and windows.installed() is None


def test_install_asks_its_licence_first_and_refuses_in_words_before_anything(windows, monkeypatch):
    p = windows
    p.out.opener = web = pin(monkeypatch, "windows-x64", archive("windows"))
    e = pytest.raises(ValueError, p.install).value
    assert e.accept == "accept_licence" and web.asked == [] and not (p.home / "app").exists()
    form = next(f for f in p.status()["forms"] if f["id"] == "ai-install")
    assert form["job"] is True and form["fields"][0]["name"] == "accept_licence"
    assert form["confirm"]["words"].startswith(
        "Codex CLI 0.170.0's package for this system (codex-package-x86_64-pc-windows-msvc.tar.gz: the program and its "
        "sandbox's helpers) is downloaded from github.com and release-assets.githubusercontent.com (about ")
    assert form["fields"][0]["words"].startswith("Codex CLI: Apache-2.0 (OpenAI).")


def test_a_wrong_sum_installs_nothing_and_leaves_the_one_in_use(tmp_path, monkeypatch):
    p = made(tmp_path)
    installed(p, "0.169.0")
    p.out.opener = pin(monkeypatch, "windows-x64", archive("windows"))
    name, size, _ = constants.TARGETS["windows-x64"]
    monkeypatch.setitem(constants.TARGETS, "windows-x64", (name, size, "0" * 64))
    answer = p.install(True, log=Output())
    assert answer["ok"] is False and "is not the file pinned" in answer["said"]
    assert p.installed().version == "0.169.0" and not (p.home / "app" / "0.170.0").exists()


def test_a_cancel_keeps_the_part_and_answers_the_bases_cancelled_words(windows, monkeypatch):
    p = windows
    p.out.opener = web = pin(monkeypatch, "windows-x64", archive("windows") * 64)  # (any bytes: it is never unpacked)
    web.piece = 1024
    out = Output()
    web.cancel_at = constants.FILES + constants.TARGETS["windows-x64"][0]  # Cancel, clicked as Codex comes
    web.then = out.cancel
    answer = p.install(True, log=out)
    gone = f"the half-built {p.home / 'app' / '0.170.0'} was removed"
    assert answer == {"said": CANCELLED, "ok": False, "lines": [gone]}
    assert sorted(x.name for x in (p.home / "downloads").iterdir()) == [
        "codex-package-x86_64-pc-windows-msvc.tar.gz.part"]
    assert not (p.home / "app" / "CURRENT").exists() and p.installed() is None


def test_uninstall_leaves_what_it_keeps(windows):
    p = windows
    installed(p)
    home = p.codex_home()
    (home / "sessions").mkdir(parents=True)
    (home / "sessions" / "rollout-1.jsonl").write_text("{}", encoding="utf-8")
    answer = p.uninstall(True)
    assert answer["ok"] is True and p.installed() is None and not (p.home / "app").exists()
    assert (home / "sessions" / "rollout-1.jsonl").exists()
    assert p.package().keeps == (f"What it kept stays: {home}, with its transcripts (your prompts and code), its logs "
                                 "and its configuration.")


def test_a_codex_of_yours_is_a_fact_never_run(tmp_path):
    p = made(tmp_path, "windows")
    yours = tmp_path / "npm" / "codex.exe"
    yours.parent.mkdir()
    yours.write_bytes(b"yours")
    p.out.which = lambda name, *a, **k: str(yours) if name == "codex" else None
    assert p.yours() == str(yours)
    assert p.status()["yours"] == f"{yours} is yours: left as it is, not used from here"
    installed(p)
    chosen(p)
    launch = p._launch(str(tmp_path), p.use_kept(), p.serving_of("ollama/default"), "")
    assert launch.argv[0] == str(p.home / "app" / "0.170.0" / "bin" / "codex.exe") and str(yours) not in launch.argv
    mine = p.home / "app" / "0.170.0" / "bin" / "codex.exe"
    p.out.which = lambda name, *a, **k: str(mine)
    assert p.yours() == ""  # (its own on PATH is not yours)


def test_no_command_it_names_runs_its_install_scripts_npm_or_its_sandbox_setup(tmp_path):
    p = made(tmp_path, "windows")
    installed(p)
    chosen(p)
    launch = p._launch(str(tmp_path), p.use_kept(), p.serving_of("ollama/default"), "")
    text = " ".join(launch.argv)
    for word in ("sandbox setup", "setup-default-sandbox", "npm", "install.ps1", "install.sh", "login", "exec",
                 "mcp add", "elevated"):
        assert word not in text, word
    assert launch.argv[1] == "--no-daemon"
    source = Path(plugin.__file__).read_text(encoding="utf-8")
    assert '"sandbox", "setup"' not in source and "codex-windows-sandbox-service" not in str(constants.TARGETS)
