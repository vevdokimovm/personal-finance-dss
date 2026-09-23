"""Гейт Exa: ни один агент не стартует, если Exa в этой сессии не работает.

**Решение владельца 16.09.2026, дословно:** «вообще никакой агент не запускаем если exa
не работает. это также важно как вебсерч. когда ты даже без вебсерча запускал
исследования... что просто бесполезно».

**Чем оплачено.** Сплошной `grep` по `docs/research/raw/` 16.09.2026: Exa была недоступна
агентам в 16 файлах начиная с 08.09.2026, а вахта узнавала об этом из отчётов постфактум
и продолжала запускать. Коннектор `claude.ai Exa` после `/login` на другой аккаунт отвечал
`404 Server not found` — от самого claude.ai, при живом `mcp.exa.ai`.

**Три способа умереть, и гейт ловит каждый.**
1. Сессия стартовала, когда Exa не была настроена. Инструменты читаются один раз
   на старте процесса (PIT-035) — настройка посреди сессии ничего не даёт. Метка
   ставится на SessionStart и привязана к ПРОЦЕССУ claude (pid + время старта), поэтому
   `/clear` и компакция её не подделают: процесс тот же, инструменты те же.
2. Инструмент есть, но отвечает «not connected» / «Server not found» — метка «мертва»
   до перезапуска.
3. Сам сервис лежит — живая проба `initialize` перед каждым запуском агента.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "exa-gate.py"

EXA_CONFIG = {"mcpServers": {"exa": {"type": "http", "url": "https://mcp.exa.ai/mcp"}}}
NO_EXA_CONFIG = {"mcpServers": {"other": {"type": "http", "url": "https://x.example/mcp"}}}
LIVE_INIT = (
    'event: message\ndata: {"result":{"protocolVersion":"2025-06-18",'
    '"serverInfo":{"name":"exa-search-server","title":"Exa"}},"jsonrpc":"2.0","id":1}'
)


@pytest.fixture(scope="module")
def hook():
    spec = importlib.util.spec_from_file_location("exa_gate", HOOK)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_hook(payload: dict, tmp: Path, config: dict, probe: str = "alive",
             key: str = "proc-1") -> subprocess.CompletedProcess:
    config_path = tmp / "claude.json"
    config_path.write_text(json.dumps(config))
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={
            "PATH": "/usr/bin:/bin",
            "FINPILOT_EXA_STATE_DIR": str(tmp / "state"),
            "FINPILOT_EXA_CONFIG": str(config_path),
            "FINPILOT_EXA_PROBE": probe,
            "FINPILOT_EXA_PROCESS_KEY": key,
        },
    )


START = {"hook_event_name": "SessionStart", "session_id": "s1", "source": "startup"}
CLEAR = {"hook_event_name": "SessionStart", "session_id": "s2", "source": "clear"}
AGENT = {
    "hook_event_name": "PreToolUse",
    "session_id": "s1",
    "tool_name": "Agent",
    "tool_input": {"prompt": "исследуй тему"},
}


def exa_call(response: object) -> dict:
    return {
        "hook_event_name": "PostToolUse",
        "session_id": "s1",
        "tool_name": "mcp__exa__web_search_exa",
        "tool_response": response,
    }


# --- чистая логика -----------------------------------------------------------


def test_exa_configured_by_url_not_by_name(hook):
    renamed = {"mcpServers": {"search": {"url": "https://mcp.exa.ai/mcp"}}}
    assert hook.exa_configured(renamed)
    assert hook.exa_configured(EXA_CONFIG)
    assert not hook.exa_configured(NO_EXA_CONFIG)
    assert not hook.exa_configured({})


def test_exa_configured_in_project_scope(hook):
    config = {"projects": {"/any/dir": {"mcpServers": {"exa": {
        "url": "https://mcp.exa.ai/mcp"}}}}}
    assert hook.exa_configured(config)


def test_probe_alive_requires_exa_server_info(hook):
    assert hook.probe_alive(200, LIVE_INIT)
    assert not hook.probe_alive(404, LIVE_INIT)
    assert not hook.probe_alive(200, '{"error":{"message":"Server not found"}}')
    assert not hook.probe_alive(0, "")


@pytest.mark.parametrize("text", [
    'MCP server "claude.ai Exa" is not connected',
    '{"type":"not_found_error","message":"Server not found"}',
    "Failed to reconnect to exa: HTTP 404",
])
def test_dead_reason_on_disconnect(hook, text):
    assert hook.dead_reason(text)


def test_dead_reason_silent_on_live_results_that_mention_errors(hook):
    live = json.dumps({"results": [{"title": "Server not found errors in MCP",
                                    "url": "https://example.com"}]})
    assert hook.dead_reason(live) == ""
    assert hook.dead_reason("") == ""


def test_verdict_blocks_without_marker(hook):
    allowed, reason = hook.agent_verdict(None, alive=True)
    assert not allowed
    assert "ПЕРЕЗАПУ" in reason


def test_verdict_blocks_when_session_started_without_exa(hook):
    allowed, reason = hook.agent_verdict({"loaded": False, "dead": False}, alive=True)
    assert not allowed
    assert "ПЕРЕЗАПУ" in reason


def test_verdict_blocks_dead_channel(hook):
    marker = {"loaded": True, "dead": True, "reason": "not connected"}
    allowed, reason = hook.agent_verdict(marker, alive=True)
    assert not allowed
    assert "not connected" in reason


def test_verdict_blocks_when_service_down(hook):
    allowed, reason = hook.agent_verdict({"loaded": True, "dead": False}, alive=False)
    assert not allowed
    assert "не отвечает" in reason


def test_verdict_allows_healthy(hook):
    assert hook.agent_verdict({"loaded": True, "dead": False}, alive=True) == (True, "")


# --- поведение процесса-хука ------------------------------------------------------


def test_agent_blocked_when_no_session_start_seen(tmp_path):
    result = run_hook(AGENT, tmp_path, EXA_CONFIG)
    assert result.returncode == 2
    assert "Exa" in result.stderr


def test_agent_allowed_after_start_with_exa(tmp_path):
    assert run_hook(START, tmp_path, EXA_CONFIG).returncode == 0
    assert run_hook(AGENT, tmp_path, EXA_CONFIG).returncode == 0


def test_agent_blocked_after_start_without_exa(tmp_path):
    run_hook(START, tmp_path, NO_EXA_CONFIG)
    assert run_hook(AGENT, tmp_path, NO_EXA_CONFIG).returncode == 2


def test_config_added_mid_session_does_not_unblock(tmp_path):
    """Настроили Exa посреди сессии — инструменты от этого не появились."""
    run_hook(START, tmp_path, NO_EXA_CONFIG)
    run_hook(CLEAR, tmp_path, EXA_CONFIG)
    assert run_hook(AGENT, tmp_path, EXA_CONFIG).returncode == 2


def test_new_process_gets_fresh_marker(tmp_path):
    run_hook(START, tmp_path, NO_EXA_CONFIG, key="proc-old")
    run_hook(START, tmp_path, EXA_CONFIG, key="proc-new")
    assert run_hook(AGENT, tmp_path, EXA_CONFIG, key="proc-new").returncode == 0


def test_agent_blocked_when_service_down(tmp_path):
    run_hook(START, tmp_path, EXA_CONFIG)
    result = run_hook(AGENT, tmp_path, EXA_CONFIG, probe="dead")
    assert result.returncode == 2
    assert "не отвечает" in result.stderr


def test_disconnect_marks_dead_loudly_and_blocks(tmp_path):
    run_hook(START, tmp_path, EXA_CONFIG)
    shout = run_hook(exa_call('MCP server "exa" is not connected'), tmp_path, EXA_CONFIG)
    assert shout.returncode == 2
    assert "ПЕРЕЗАПУ" in shout.stderr
    assert run_hook(AGENT, tmp_path, EXA_CONFIG).returncode == 2


def test_live_exa_call_keeps_gate_open(tmp_path):
    run_hook(START, tmp_path, EXA_CONFIG)
    live = {"results": [{"title": "t", "url": "https://example.com"}]}
    assert run_hook(exa_call(live), tmp_path, EXA_CONFIG).returncode == 0
    assert run_hook(AGENT, tmp_path, EXA_CONFIG).returncode == 0


def test_other_tools_ignored(tmp_path):
    payload = {"hook_event_name": "PreToolUse", "tool_name": "Bash",
               "session_id": "s1", "tool_input": {"command": "ls"}}
    assert run_hook(payload, tmp_path, NO_EXA_CONFIG).returncode == 0


def test_garbage_stdin_does_not_crash(tmp_path):
    result = subprocess.run([sys.executable, str(HOOK)], input="not json",
                            capture_output=True, text=True,
                            env={"PATH": "/usr/bin:/bin",
                                 "FINPILOT_EXA_STATE_DIR": str(tmp_path)})
    assert result.returncode == 0


def test_hook_registered_for_agent_session_start_and_exa_tools():
    settings = json.loads((HOOK.parents[1] / "settings.json").read_text())
    hooks = settings["hooks"]

    def registered(event: str, matcher: str | None) -> bool:
        for entry in hooks.get(event, []):
            if matcher is not None and entry.get("matcher") != matcher:
                continue
            if any("exa-gate.py" in h.get("command", "") for h in entry["hooks"]):
                return True
        return False

    assert registered("PreToolUse", "Agent")
    assert registered("SessionStart", None)
    assert registered("PostToolUse", "mcp__exa__.*")
