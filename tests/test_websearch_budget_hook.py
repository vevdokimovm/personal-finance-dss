"""Гейт бюджета WebSearch: агент не уходит в исчерпанную сессию (v9.9.0).

🔴 Цена вопроса зафиксирована 08.09.2026: тема 12 очереди исследований отработала при
счётчике 400/400 ДО первого запроса. Оба подагента не получили ни одного живого
первоисточника, ход потрачен, результат — реконструкция по памяти модели. Признака
«поиск кончился» в тот момент не существовало нигде: WebSearch возвращал пустоту молча,
и это было неотличимо от узкого запроса.

Хук `.claude/hooks/websearch-budget.py` закрывает разрыв с двух сторон: считает вызовы
и распознаёт исчерпание по ответу, а затем ЗАПРЕЩАЕТ запуск `Agent` и говорит владельцу
прямым текстом, что нужен новый чат или `/clear`.

Ложное срабатывание дорого: хук, глушащий исправный запуск агента, будет снят. Поэтому
одиночный пустой ответ исчерпанием НЕ считается (узкий запрос выглядит так же) — нужны
два подряд либо явный маркер лимита в ответе.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "websearch-budget.py"


@pytest.fixture(scope="module")
def hook():
    spec = importlib.util.spec_from_file_location("websearch_budget", HOOK)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_hook(payload: dict, state_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={
            "PATH": "/usr/bin:/bin",
            "FINPILOT_WEBSEARCH_STATE_DIR": str(state_dir),
        },
    )


def search_event(session: str, response: str) -> dict:
    return {
        "session_id": session,
        "hook_event_name": "PostToolUse",
        "tool_name": "WebSearch",
        "tool_input": {"query": "portfolio theory"},
        "tool_response": response,
    }


def agent_event(session: str, prompt: str = "исследуй тему") -> dict:
    return {
        "session_id": session,
        "hook_event_name": "PreToolUse",
        "tool_name": "Agent",
        "tool_input": {"prompt": prompt, "description": "тема 12"},
    }


LIVE = "1. Optimal Versus Naive Diversification — academic.oup.com — DeMiguel 2009"


class TestClassification:
    def test_live_answer_is_ok(self, hook):
        assert hook.classify_response(LIVE) == "ok"

    def test_empty_answer_is_empty(self, hook):
        assert hook.classify_response("") == "empty"

    def test_short_noise_is_empty(self, hook):
        assert hook.classify_response("No results found.") == "empty"

    @pytest.mark.parametrize(
        "text",
        [
            "Error: rate limit exceeded for web_search",
            "You have reached your web search quota for this session",
            "web search is not available",
        ],
    )
    def test_explicit_limit_marker_is_exhausted(self, hook, text):
        assert hook.classify_response(text) == "exhausted"


class TestCounting:
    def test_counter_grows(self, hook):
        state = hook.blank_state()
        for _ in range(3):
            state = hook.record_search(state, LIVE)
        assert state["used"] == 3
        assert state["exhausted"] is False

    def test_single_empty_is_not_exhaustion(self, hook):
        state = hook.record_search(hook.blank_state(), "")
        assert state["exhausted"] is False

    def test_two_empties_in_a_row_are_exhaustion(self, hook):
        state = hook.record_search(hook.blank_state(), "")
        state = hook.record_search(state, "")
        assert state["exhausted"] is True

    def test_live_answer_resets_the_empty_streak(self, hook):
        state = hook.record_search(hook.blank_state(), "")
        state = hook.record_search(state, LIVE)
        state = hook.record_search(state, "")
        assert state["exhausted"] is False

    def test_explicit_marker_exhausts_immediately(self, hook):
        state = hook.record_search(hook.blank_state(), "rate limit exceeded")
        assert state["exhausted"] is True

    def test_hard_ceiling_exhausts(self, hook):
        state = hook.blank_state()
        state["used"] = hook.LIMIT - 1
        state = hook.record_search(state, LIVE)
        assert state["used"] == hook.LIMIT
        assert state["exhausted"] is True

    def test_warning_band_does_not_block(self, hook):
        state = hook.blank_state()
        state["used"] = hook.WARN_AT - 1
        state = hook.record_search(state, LIVE)
        assert state["exhausted"] is False
        assert hook.warning_for(state) is not None


class TestExhaustionKinds:
    """🔴 Два разных лимита, и они гасятся по-разному.

    Поймано 09.09.2026 на первом же живом применении гейта: агент упал по лимиту
    АККАУНТА (429), в ответе оказалось «rate limit», хук записал исчерпание ПОИСКОВОГО
    бюджета — и заблокировал запуск при 7 израсходованных поисках из 400. Аккаунтный
    лимит восстанавливается по часам, поисковый — только с новой сессией; смешивать их
    нельзя, иначе один 429 глушит работу до конца сессии.
    """

    def test_ceiling_exhaustion_is_marked_as_ceiling(self, hook):
        state = hook.blank_state()
        state["used"] = hook.LIMIT - 1
        state = hook.record_search(state, LIVE)
        assert state["reason"] == "ceiling"

    def test_marker_exhaustion_is_marked_as_heuristic(self, hook):
        state = hook.record_search(hook.blank_state(), "rate limit exceeded")
        assert state["reason"] == "heuristic"

    def test_heuristic_exhaustion_expires(self, hook):
        state = hook.record_search(hook.blank_state(), "rate limit exceeded")
        state["updated"] = state["updated"] - hook.HEURISTIC_TTL - 1
        assert hook.thaw(state)["exhausted"] is False

    def test_ceiling_exhaustion_never_expires(self, hook):
        state = hook.blank_state()
        state["used"] = hook.LIMIT
        state = hook.record_search(state, LIVE)
        state["updated"] = state["updated"] - hook.HEURISTIC_TTL * 100
        assert hook.thaw(state)["exhausted"] is True

    def test_fresh_heuristic_exhaustion_still_holds(self, hook):
        state = hook.record_search(hook.blank_state(), "rate limit exceeded")
        assert hook.thaw(state)["exhausted"] is True

    def test_block_message_says_how_to_reset(self, hook):
        state = hook.blank_state()
        state["exhausted"] = True
        _, reason = hook.agent_verdict(state, "исследуй")
        assert hook.RESET_HINT in reason


class TestAgentVerdict:
    def test_agent_allowed_while_search_is_alive(self, hook):
        allowed, _ = hook.agent_verdict(hook.blank_state(), "исследуй тему")
        assert allowed is True

    def test_agent_blocked_when_exhausted(self, hook):
        state = hook.blank_state()
        state["exhausted"] = True
        allowed, reason = hook.agent_verdict(state, "исследуй тему")
        assert allowed is False
        assert "/clear" in reason

    def test_nosearch_agent_passes_through(self, hook):
        state = hook.blank_state()
        state["exhausted"] = True
        allowed, _ = hook.agent_verdict(state, "NOSEARCH: прочитай код и опиши схему")
        assert allowed is True


class TestEndToEnd:
    def test_state_survives_between_calls(self, tmp_path):
        for _ in range(2):
            run_hook(search_event("s1", LIVE), tmp_path)
        state = json.loads((tmp_path / "s1.json").read_text())
        assert state["used"] == 2

    def test_sessions_are_isolated(self, tmp_path):
        run_hook(search_event("s1", LIVE), tmp_path)
        run_hook(search_event("s2", LIVE), tmp_path)
        assert json.loads((tmp_path / "s1.json").read_text())["used"] == 1
        assert json.loads((tmp_path / "s2.json").read_text())["used"] == 1

    def test_exhaustion_is_announced_to_the_owner(self, tmp_path):
        run_hook(search_event("s3", ""), tmp_path)
        result = run_hook(search_event("s3", ""), tmp_path)
        assert result.returncode == 0
        payload = json.loads(result.stdout)
        assert "/clear" in payload["systemMessage"]
        assert "WebSearch" in payload["systemMessage"]

    def test_quiet_while_budget_is_healthy(self, tmp_path):
        result = run_hook(search_event("s4", LIVE), tmp_path)
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_agent_launch_denied_after_exhaustion(self, tmp_path):
        run_hook(search_event("s5", "rate limit exceeded"), tmp_path)
        result = run_hook(agent_event("s5"), tmp_path)
        assert result.returncode == 0
        payload = json.loads(result.stdout)
        assert payload["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "/clear" in payload["hookSpecificOutput"]["permissionDecisionReason"]
        assert "/clear" in payload["systemMessage"]

    def test_agent_launch_allowed_on_fresh_session(self, tmp_path):
        result = run_hook(agent_event("s6"), tmp_path)
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_task_alias_is_gated_too(self, tmp_path):
        """Инструмент субагентов зовётся `Task` в других сборках харнесса."""
        run_hook(search_event("s8", "rate limit exceeded"), tmp_path)
        event = agent_event("s8")
        event["tool_name"] = "Task"
        payload = json.loads(run_hook(event, tmp_path).stdout)
        assert payload["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_agent_launch_warns_in_the_warning_band(self, tmp_path):
        state = {"used": 360, "empty_streak": 0, "exhausted": False, "updated": 0.0}
        (tmp_path / "s9.json").write_text(json.dumps(state))
        result = run_hook(agent_event("s9"), tmp_path)
        payload = json.loads(result.stdout)
        assert "hookSpecificOutput" in payload
        assert payload["hookSpecificOutput"].get("permissionDecision") is None
        assert "360" in payload["systemMessage"]

    def test_unrelated_tool_is_ignored(self, tmp_path):
        result = run_hook(
            {
                "session_id": "s7",
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "uptime"},
                "tool_response": "",
            },
            tmp_path,
        )
        assert result.returncode == 0
        assert result.stdout.strip() == ""
        assert not (tmp_path / "s7.json").exists()

    def test_stale_heuristic_block_lets_the_agent_through(self, tmp_path):
        """Лимит аккаунта обновился — гейт обязан отпустить сам, без вмешательства."""
        run_hook(search_event("s10", "rate limit exceeded"), tmp_path)
        path = tmp_path / "s10.json"
        state = json.loads(path.read_text())
        state["updated"] -= 100000
        path.write_text(json.dumps(state))
        result = run_hook(agent_event("s10"), tmp_path)
        assert result.stdout.strip() == ""

    def test_broken_stdin_never_blocks_work(self, tmp_path):
        result = subprocess.run(
            [sys.executable, str(HOOK)],
            input="not json at all",
            capture_output=True,
            text=True,
            env={"PATH": "/usr/bin:/bin", "FINPILOT_WEBSEARCH_STATE_DIR": str(tmp_path)},
        )
        assert result.returncode == 0
