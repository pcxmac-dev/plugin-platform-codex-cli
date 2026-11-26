"""What the README and the CHANGELOG tell the user, where the plugin's behaviour rests on their words (the behaviour
itself is tested beside the code): what only a real run confirms is listed; its start-up fetch, its transcripts and
its ports said plainly (the user's answers 6 and 8); the sandbox on each system and the elevated one never; the
install's pin and its hosts. Read as text, nothing run."""
from __future__ import annotations

import re
from pathlib import Path

from plugin_platform_codex_cli import constants

HERE = Path(__file__).resolve().parent.parent


def words(name: str) -> str:
    """A file's text with its line breaks and runs of spaces as one space, as it reads."""
    return re.sub(r"\s+", " ", (HERE / name).read_text(encoding="utf-8"))


def section(name: str, title: str) -> str:
    """One section of a file (from its "## title" to the next "## "), as it reads."""
    text = (HERE / name).read_text(encoding="utf-8")
    start = text.index(f"\n## {title}\n")
    end = text.find("\n## ", start + 1)
    return re.sub(r"\s+", " ", text[start:end if end > 0 else None])


def test_the_readme_lists_what_only_a_real_run_confirms():
    said = section("README.md", "Not yet confirmed by a real run")
    for item in ("The package's layout as it unpacks", "MXC on this PC's build", "cannot reach 127.0.0.1:8775",
                 "under `[projects]`", "no shared background server starts", "a window still open keeps",
                 "TOML literal string", "Liminal's MCP with Codex", "The bundled `bwrap` in the user's WSL Ubuntu",
                 "/v1/responses"):
        assert item in said, item


def test_the_readme_says_its_fetch_its_transcripts_and_its_ports_plainly():
    said = words("README.md")
    assert constants.ANNOUNCEMENT in said and "No setting of Codex 0.170.0 turns it off" in said
    assert "no setting of its terminal screen turns this off" in said
    assert "keeps the newest 50 (200 MB at the most)" in said and "Command… removes nothing" in said
    assert "`127.0.0.1:1455`" in said and "none opened by itself here" in said


def test_the_readme_says_each_sandbox_and_never_the_elevated_one():
    said = words("README.md")
    for item in ("**Windows, MXC** (the default)", "**Never the unelevated sandbox**",
                 "**Never the elevated sandbox**", "**Linux, bubblewrap**", "apparmor_restrict_unprivileged_userns",
                 "26100.9278", "26200.9278"):
        assert item in said, item


def test_the_readme_says_how_the_install_is_pinned_and_from_where():
    said = words("README.md")
    assert all(name in said for name, _, _ in constants.TARGETS.values())
    assert all(host in said for host in constants.HOSTS)
    assert "GitHub's record of the release" in said and "not marked immutable" in said
    assert "ARM64's packages are not pinned in this release" in said


def test_the_changelog_names_its_release_and_the_users_words():
    changelog = words("CHANGELOG.md")
    assert changelog.startswith("# Changelog ## 0.1.0 (2026-11-26)")
    assert '"mxc, never elevated"' in changelog and "Needs liminal-libs>=1.99.0," in changelog


def test_no_line_is_longer_than_120_characters():
    for path in sorted([*HERE.rglob("*.py"), *HERE.rglob("*.md"), *HERE.rglob("*.toml"), *HERE.rglob("*.yml")]):
        if any(part in (".git", "__pycache__") for part in path.parts):
            continue
        long = [n for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1) if len(line) > 120]
        assert long == [], f"{path.relative_to(HERE)}: lines {long}"


def test_no_module_imports_what_it_does_not_use():
    for path in sorted([*(HERE / "src" / "plugin_platform_codex_cli").glob("*.py"), *(HERE / "tests").glob("*.py")]):
        text = path.read_text(encoding="utf-8")
        names = re.findall(r"^from \S+ import \(?([^)]+?)\)?$", text, re.M | re.S)
        imported = [n.strip().split(" as ")[-1] for line in names for n in line.split(",") if n.strip()]
        imported += re.findall(r"^import (\w+)$", text, re.M)
        body = re.sub(r"^(from \S+ import \([^)]*\)|from .*|import .*)$", "", text, flags=re.M)
        unused = [n for n in imported if n != "annotations" and not re.search(rf"\b{re.escape(n)}\b", body)]
        assert unused == [], f"{path.name}: {unused}"
