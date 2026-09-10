"""Счётчик WebSearch: наблюдает и НИЧЕГО не запрещает (v9.9.5).

🔴 Ограничение снято по прямому решению владельца 09.09.2026: «сними нахер это
ограничение вовсе… чтобы бесконечные запросы можно было делать если это искуственный
лимит». Число 400 было нашей выдумкой, а не лимитом Anthropic.

**Чем оплачено решение.** Гейт версии 9.9.0 дважды подряд заглушил исправную работу:
09.09.2026 первый раз при 7 поисках из 400 (записано в комментарии самого хука), второй
раз в тот же день при 42 из 400 — оба раза он принял HTTP 429 от лимита АККАУНТА за
исчерпание ПОИСКА, потому что в списке маркеров стояли `429`, `rate limit`,
`too many requests`. Второй случай стоил темы 18: запуск агента был заблокирован при
живом поиске, что проверено прямым запросом из вахты.

**Почему счётчика достаточно и почему замер вообще не про то.** Публичного лимита
«N поисков за сессию» не существует: по докам платформы ограничения — это `max_uses`
на один запрос и квота организации. А наблюдаемый в Claude Code отказ описан в
`anthropics/claude-code` issue #27074 — WebSearch делает побочный запрос
(`source:"side_query"`), и тот отбивается 429 **по типу авторизации** (подписка Pro/Max
против API-ключа), а не по числу поисков. Считать поиски и объявлять их кончившимися
по такому 429 — значит измерять не ту величину.

Поэтому хук оставлен наблюдателем: считает вызовы для статистики расхода и не выносит
ни одного вердикта. Ложных срабатываний у него больше нет по построению — запрещать
нечего.
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
        "tool_input": {"prompt": prompt, "description": "тема 18"},
    }


LIVE = "1. Optimal Versus Naive Diversification — academic.oup.com — DeMiguel 2009"

# Тексты, на которых прежний гейт ложно срабатывал. Все три — признаки лимита АККАУНТА
# или транзиентной ошибки, ни один не говорит об исчерпании поискового бюджета.
ACCOUNT_LIMIT_TEXTS = [
    '429 {"type":"error","error":{"type":"rate_limit_error"}}',
    "API Error: Rate limit reached",
    "too many requests, please retry",
]


class TestCounting:
    """Счётчик считает — это всё, что он делает."""

    def test_counts_every_call(self, hook):
        state = hook.blank_state()
        for _ in range(5):
            state = hook.record_search(state, LIVE)
        assert state["used"] == 5

    def test_empty_answer_is_counted_like_any_other(self, hook):
        state = hook.record_search(hook.blank_state(), "")
        assert state["used"] == 1

    def test_counting_has_no_upper_bound(self, hook):
        """Потолка нет: 400 было выдумкой, а не лимитом Anthropic."""
        state = hook.blank_state()
        state["used"] = 10_000
        state = hook.record_search(state, LIVE)
        assert state["used"] == 10_001

    def test_state_survives_round_trip(self, hook, tmp_path):
        path = tmp_path / "s.json"
        state = hook.record_search(hook.blank_state(), LIVE)
        path.write_text(json.dumps(state, ensure_ascii=False))
        assert hook.load_state(path)["used"] == 1


class TestNoVerdicts:
    """Хук не выносит вердиктов — ни по одному входу."""

    @pytest.mark.parametrize("text", ACCOUNT_LIMIT_TEXTS)
    def test_account_limit_text_does_not_produce_exhaustion(self, hook, text):
        """🔴 Тот самый ложняк: 429 аккаунта больше не значит «поиск кончился»."""
        state = hook.record_search(hook.blank_state(), text)
        assert state.get("exhausted", False) is False

    def test_repeated_empty_answers_do_not_produce_exhaustion(self, hook):
        """Два пустых подряд — узкий запрос, а не конец бюджета."""
        state = hook.blank_state()
        state = hook.record_search(state, "")
        state = hook.record_search(state, "")
        assert state.get("exhausted", False) is False

    def test_no_limit_constant_remains(self, hook):
        """Константы потолка в модуле больше нет."""
        assert not hasattr(hook, "LIMIT")


class TestAgentNeverBlocked:
    """🔴 Ядро решения: запуск агента не блокируется никогда."""

    def test_agent_allowed_on_fresh_state(self, hook):
        allowed, reason = hook.agent_verdict(hook.blank_state(), "исследуй тему")
        assert allowed is True
        assert reason == ""

    def test_agent_allowed_after_heavy_usage(self, hook):
        state = hook.blank_state()
        state["used"] = 9_999
        allowed, _ = hook.agent_verdict(state, "исследуй тему")
        assert allowed is True

    def test_agent_allowed_after_account_limit_seen(self, hook):
        """Сессия видела 429 аккаунта — агент всё равно запускается."""
        state = hook.blank_state()
        for text in ACCOUNT_LIMIT_TEXTS:
            state = hook.record_search(state, text)
        allowed, _ = hook.agent_verdict(state, "исследуй тему")
        assert allowed is True

    def test_legacy_exhausted_flag_in_state_is_ignored(self, hook):
        """Файлы состояния прошлых сессий несут exhausted:true — он больше не действует."""
        state = hook.blank_state()
        state["exhausted"] = True
        allowed, _ = hook.agent_verdict(state, "исследуй тему")
        assert allowed is True


class TestEndToEnd:
    def test_search_event_writes_state_and_stays_silent(self, tmp_path):
        result = run_hook(search_event("s1", LIVE), tmp_path)
        assert result.returncode == 0
        assert json.loads((tmp_path / "s1.json").read_text())["used"] == 1

    @pytest.mark.parametrize("text", ACCOUNT_LIMIT_TEXTS)
    def test_agent_launch_survives_account_limit_end_to_end(self, tmp_path, text):
        """🔴 Регрессия обоих случаев 09.09.2026, сквозь процесс целиком."""
        run_hook(search_event("s2", text), tmp_path)
        result = run_hook(agent_event("s2"), tmp_path)
        assert result.returncode == 0
        if result.stdout.strip():
            payload = json.loads(result.stdout)
            decision = payload.get("hookSpecificOutput", {}).get("permissionDecision")
            assert decision != "deny"

    def test_agent_launch_never_denied_whatever_the_history(self, tmp_path):
        for _ in range(3):
            run_hook(search_event("s3", ""), tmp_path)
        result = run_hook(agent_event("s3"), tmp_path)
        assert "deny" not in result.stdout

    def test_malformed_payload_is_survived(self, tmp_path):
        result = subprocess.run(
            [sys.executable, str(HOOK)],
            input="not json",
            capture_output=True,
            text=True,
            env={"PATH": "/usr/bin:/bin", "FINPILOT_WEBSEARCH_STATE_DIR": str(tmp_path)},
        )
        assert result.returncode == 0
