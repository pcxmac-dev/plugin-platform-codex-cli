"""What Codex CLI is given, as text (files.py, pure): config.toml for each system against its golden text and read back
with tomllib, every key the pre-build checks name (C-X1.1) as Codex 0.170.0 reads it; the folders marked untrusted;
the -c words of a start read as Codex reads them (C-X1.1m), each one Windows PowerShell 5.1 hands over as it is; a value
-c cannot be given refused in words; Liminal's MCP over HTTP and through the bridge."""
from __future__ import annotations

import tomllib

import pytest

from conftest import BRIDGE, DATA, ENDPOINT, HTTP, overridden, read_override
from liminal_libs.machines import children
from plugin_platform_codex_cli import files


def golden(name: str) -> str:
    return (DATA / name).read_text(encoding="utf-8")


@pytest.mark.parametrize("system", ["windows", "linux"])
def test_config_toml_is_the_golden_text_for_each_system(system):
    assert files.config_toml(system=system) == golden(f"config-{system}.toml")


@pytest.mark.parametrize("system", ["windows", "linux"])
def test_config_toml_says_what_the_checks_name(system):
    """C-X1.1's overview: approvals on-request (never untrusted, which stops Codex, nor on-failure, deprecated);
    workspace-write with the network off; on Windows the sandbox always written (never unset, which prefers elevated)
    and no prefer_mxc; local only; the features that reach out off; its commands' environment narrowed (its default
    excludes on: they default off), with filters and never the legacy lists beside them."""
    parsed = tomllib.loads(files.config_toml(system=system))
    assert parsed["approval_policy"] == "on-request" and parsed["sandbox_mode"] == "workspace-write"
    assert parsed["sandbox_workspace_write"] == {"network_access": False}
    if system == "windows":
        assert parsed["windows"] == {"sandbox": "mxc"}
    else:
        assert "windows" not in parsed
    assert "prefer_mxc" not in parsed["features"] and "allow_mxc" not in parsed.get("windows", {})
    assert parsed["features"] == dict.fromkeys(("daemon_auto_start", "plugins", "remote_plugin", "apps",
                                                "tool_suggest", "skill_mcp_dependency_install"), False)
    assert (parsed["analytics"], parsed["feedback"]) == ({"enabled": False}, {"enabled": False})
    assert parsed["otel"] == {"exporter": "none", "trace_exporter": "none", "metrics_exporter": "none"}
    assert parsed["check_for_update_on_startup"] is False and parsed["web_search"] == "disabled"
    assert parsed["cli_auth_credentials_store"] == "ephemeral" and parsed["history"] == {"persistence": "none"}
    assert parsed["project_root_markers"] == [] and parsed["allow_login_shell"] is False
    policy = parsed["shell_environment_policy"]
    assert policy["inherit"] == "core" and policy["ignore_default_excludes"] is False
    assert policy["filters"] == {"LIMINAL_*": "exclude", "CODEX_*": "exclude", "OPENAI_*": "exclude"}
    assert "exclude" not in policy and "include_only" not in policy  # (cannot be mixed with filters)
    assert ("set" in policy) is (system == "windows")
    for absent in ("model", "model_provider", "model_providers", "mcp_servers", "profile", "notify", "projects"):
        assert absent not in parsed, absent  # (a start's own choice is on its command line)


def test_the_sandbox_and_the_network_chosen_are_written_and_never_another_than_mxc():
    parsed = tomllib.loads(files.config_toml(system="windows", sandbox="mxc", network=True))
    assert parsed["windows"] == {"sandbox": "mxc"} and parsed["sandbox_workspace_write"]["network_access"]
    for bad in ("unelevated", "elevated", "", "none"):
        with pytest.raises(ValueError):
            files.config_toml(system="windows", sandbox=bad)


def test_every_folder_is_marked_untrusted_whole_and_once():
    folders = ["C:\\Users\\you\\project", "C:\\Users\\you\\other \"quoted\" one", "/home/you/x",
               "C:\\Users\\you\\project"]
    parsed = tomllib.loads(files.config_toml(system="windows", folders=folders))
    assert list(parsed["projects"]) == folders[:3]
    assert all(v == {"trust_level": "untrusted"} for v in parsed["projects"].values())
    assert files.projects_of(parsed) == folders[:3]
    assert files.projects_of({"projects": {"a": {"trust_level": "trusted"}, "b": "x"}}) == ["a"]
    assert files.projects_of({}) == [] and files.projects_of({"projects": []}) == []


def start(**given) -> list[str]:
    said = dict(system="windows", sandbox="mxc", network=False, model="qwen3:8b",
                base_url=HTTP + "127.0.0.1:11434/v1", context=40960, keyed=False)
    said.update(given)
    return files.overrides(**said)


def test_a_starts_words_read_as_codex_reads_them():
    words = start()
    assert words[::2] == ["-c"] * (len(words) // 2)
    assert overridden(words) == {
        "approval_policy": "on-request", "sandbox_mode": "workspace-write",
        "sandbox_workspace_write": {"network_access": False}, "windows": {"sandbox": "mxc"},
        "model_provider": "liminal",
        "model_providers": {"liminal": {"name": "Liminal", "base_url": HTTP + "127.0.0.1:11434/v1",
                                        "wire_api": "responses"}},
        "model": "qwen3:8b", "model_context_window": 40960}
    keyed = overridden(start(keyed=True, system="linux", network=True))
    assert keyed["model_providers"]["liminal"]["env_key"] == "LIMINAL_SERVER_KEY"
    assert "windows" not in keyed and keyed["sandbox_workspace_write"] == {"network_access": True}


@pytest.mark.parametrize("model", ["1.5", "true", "qwen3:8b", "Qwen/Qwen3-8B", "gpt-oss:20b", "a b"])
def test_a_models_id_is_text_whatever_it_looks_like(model):
    """A bare 1.5 or true would be read as a number or a boolean: every text goes in single quotes."""
    assert overridden(start(model=model))["model"] == model


def test_every_word_powershell_5_1_hands_over_as_it_is():
    mcp = {"argv": ["C:\\Program Files\\Python\\python.exe", "-I", *BRIDGE[2:]], "timeout_s": 110}
    for words in (start(), start(mcp={"url": ENDPOINT, "headers": {"X-Liminal-Charts": "1"}, "timeout_s": 110}),
                  start(mcp=mcp)):
        assert [w for w in words if children.not_passed(w)] == []
        assert not any('"' in w for w in words)


@pytest.mark.parametrize("given, what", [
    ({"model": "it's"}, "the model's id"), ({"model": "a\nb"}, "the model's id"), ({"model": ""}, "the model's id"),
    ({"base_url": HTTP + "x/'v1"}, "the server's address"), ({"sandbox": "elevated"}, "never 'elevated'"),
    ({"sandbox": "unelevated"}, "never 'unelevated'"),
])
def test_a_value_its_c_cannot_be_given_is_refused_in_words(given, what):
    with pytest.raises(ValueError) as caught:
        start(**given)
    assert what in str(caught.value)


def test_liminals_mcp_over_http_names_its_token_by_its_variable():
    said = overridden(start(mcp={"url": ENDPOINT, "headers": {"X-Liminal-Charts": "1"}, "timeout_s": 110}))
    assert said["mcp_servers"] == {"liminal": {
        "url": ENDPOINT, "bearer_token_env_var": "LIMINAL_MCP_TOKEN", "http_headers": {"X-Liminal-Charts": "1"},
        "startup_timeout_sec": 30, "tool_timeout_sec": 110, "enabled": True}}


def test_liminals_mcp_through_the_bridge_hands_it_the_tokens_variable_alone():
    said = overridden(start(mcp={"argv": BRIDGE, "timeout_s": 110}))
    assert said["mcp_servers"] == {"liminal": {
        "command": BRIDGE[0], "args": BRIDGE[1:], "env_vars": ["LIMINAL_MCP_TOKEN"], "startup_timeout_sec": 30,
        "tool_timeout_sec": 110, "enabled": True}}
    assert "env" not in said["mcp_servers"]["liminal"]  # (a secret in env = {...} would be in the file)
    with pytest.raises(ValueError, match="neither an address nor a bridge"):
        start(mcp={"argv": [], "timeout_s": 110})
    with pytest.raises(ValueError, match="no timeout"):
        start(mcp={"url": ENDPOINT, "timeout_s": 0})


def test_read_override_is_codexs_reading():
    assert read_override("a=1") == ("a", 1) and read_override("a=on-request") == ("a", "on-request")
    assert read_override("a.b='x y'") == ("a.b", "x y") and read_override("a=[1, 'x']") == ("a", [1, "x"])
