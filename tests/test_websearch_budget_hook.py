"""Гейт WebSearch: считает расход, а на РЕАЛЬНОМ отказе бюджета кричит
и не пускает агента.

**Что изменилось 11.09.2026 (решение владельца, дословно): «обнови созданные гейты чтобы
они фейл лауд когда лимит в миллиарды закончится и без вебсера агенты не запусклись
а тербовали перезапустить сессию».**

Версия 9.9.5 была чистым счётчиком без вердиктов, и это оплачено двумя ложняками
09.09.2026 (при 7 и при 42 поисках): гейт принимал HTTP 429 от лимита АККАУНТА за
исчерпание ПОИСКА, потому что смотрел на маркеры `429`, `rate limit`,
`too many requests`. Второй случай стоил темы 18.

**Почему новый гейт не повторяет тот класс.** Он не считает и не угадывает. Он ищет
в ответе инструмента ДОСЛОВНЫЙ отказ харнесса, замеренный 10–11.09.2026:
«This session has used its web search budget (400 of 400 WebSearch calls)». Это
единственный вход, на котором он срабатывает. Тексты аккаунтного 429 оставлены в тестах
регрессией: на них гейт молчит, как и после снятия.

**Почему лечение — перезапуск сессии, а не ожидание.** Бюджет выдаётся на сессию и
делится с подагентами; метка живёт в файле по `session_id`, поэтому новая сессия
получает чистое состояние сама. Протухание метки по таймеру (v9.9.1) уже пробовали —
лечило следствие. Здесь лечения по времени нет вовсе: пока сессия та же, канал считается
мёртвым, и правило владельца «канал мёртв → агент НЕ ЗАПУСКАЕТСЯ» держит механизм,
а не внимательность вахты.

**Лимит на 11.09.2026** — `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION=999999999`
в `~/.claude/settings.json`. Гейт к самому числу не привязан: он ждёт отказ, каким бы
число ни было.
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


LIVE = (
    'Web search results for query: "portfolio theory"\n\n'
    'Links: [{"title":"Optimal Versus Naive Diversification",'
    '"url":"https://academic.oup.com/x"}]'
)

# Дословный отказ харнесса, замеренный 10–11.09.2026 на доборах Д3–Д6.
REFUSAL = (
    "This session has used its web search budget (400 of 400 WebSearch calls). "
    "Continue with the information already gathered instead of issuing more searches."
)
# Тот же отказ при поднятом лимите: гейт привязан к тексту, а не к числу.
REFUSAL_BILLIONS = (
    "This session has used its web search budget "
    "(999999999 of 999999999 WebSearch calls). Continue with the information "
    "already gathered instead of issuing more searches."
)

# Тексты, на которых прежний гейт ложно срабатывал. Все три — признаки лимита АККАУНТА
# или транзиентной ошибки, ни один не говорит об исчерпании поискового бюджета.
ACCOUNT_LIMIT_TEXTS = [
    '429 {"type":"error","error":{"type":"rate_limit_error"}}',
    "API Error: Rate limit reached",
    "too many requests, please retry",
]


class TestCounting:
    """Счётчик считает — расход по-прежнему замеряется."""

    def test_counts_every_call(self, hook):
        state = hook.blank_state()
        for _ in range(5):
            state = hook.record_search(state, LIVE)
        assert state["used"] == 5

    def test_empty_answer_is_counted_like_any_other(self, hook):
        state = hook.record_search(hook.blank_state(), "")
        assert state["used"] == 1

    def test_counting_has_no_upper_bound(self, hook):
        """Потолка своей выдумки нет: гейт ждёт отказ, а не считает до числа."""
        state = hook.blank_state()
        state["used"] = 10_000
        state = hook.record_search(state, LIVE)
        assert state["used"] == 10_001
        assert state["exhausted"] is False

    def test_no_limit_constant_remains(self, hook):
        """Константы собственного потолка в модуле нет."""
        assert not hasattr(hook, "LIMIT")

    def test_state_survives_round_trip(self, hook, tmp_path):
        path = tmp_path / "s.json"
        state = hook.record_search(hook.blank_state(), REFUSAL)
        path.write_text(json.dumps(state, ensure_ascii=False))
        restored = hook.load_state(path)
        assert restored["used"] == 1
        assert restored["exhausted"] is True


class TestRefusalDetection:
    """Срабатывание — только на дословный отказ бюджета."""

    @pytest.mark.parametrize("text", [REFUSAL, REFUSAL_BILLIONS])
    def test_literal_refusal_marks_exhausted(self, hook, text):
        state = hook.record_search(hook.blank_state(), text)
        assert state["exhausted"] is True
        assert "web search budget" in state["reason"].lower()

    @pytest.mark.parametrize("text", ACCOUNT_LIMIT_TEXTS)
    def test_account_limit_text_is_not_exhaustion(self, hook, text):
        """🔴 Регрессия обоих ложняков 09.09.2026."""
        state = hook.record_search(hook.blank_state(), text)
        assert state["exhausted"] is False

    def test_repeated_empty_answers_are_not_exhaustion(self, hook):
        """Два пустых подряд — узкий запрос; машинно это не отличается."""
        state = hook.blank_state()
        state = hook.record_search(state, "")
        state = hook.record_search(state, "")
        assert state["exhausted"] is False

    def test_results_merely_mentioning_the_phrase_are_not_exhaustion(self, hook):
        """Вахта ищет сам текст отказа — выдача с ним гейт не поднимает."""
        response = (
            'Web search results for query: "claude code used its web search budget"\n\n'
            'Links: [{"title":"issue #27074: This session has used its web '
            'search budget (400 of 400 WebSearch calls)",'
            '"url":"https://github.com/anthropics/claude-code"}]'
            + "\n\nПодробный разбор отказа и обходных каналов. " * 20
        )
        state = hook.record_search(hook.blank_state(), response)
        assert state["exhausted"] is False

    def test_dict_response_is_inspected_too(self, hook):
        """Ответ может прийти структурой, а не строкой."""
        state = hook.record_search(hook.blank_state(), {"result": REFUSAL})
        assert state["exhausted"] is True


class TestAgentVerdict:
    """Правило владельца: канал мёртв → агент не запускается."""

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
        state = hook.blank_state()
        for text in ACCOUNT_LIMIT_TEXTS:
            state = hook.record_search(state, text)
        allowed, _ = hook.agent_verdict(state, "исследуй тему")
        assert allowed is True

    def test_agent_blocked_after_real_refusal(self, hook):
        state = hook.record_search(hook.blank_state(), REFUSAL)
        allowed, reason = hook.agent_verdict(state, "исследуй тему")
        assert allowed is False
        assert "перезапус" in reason.lower()

    def test_block_demands_restart_not_waiting(self, hook):
        """Лечение — новая сессия. Протухание по таймеру уже пробовали, не лечит."""
        state = hook.record_search(hook.blank_state(), REFUSAL)
        _, reason = hook.agent_verdict(state, "исследуй тему")
        assert "сесси" in reason.lower()
        assert not hasattr(hook, "STALE_AFTER_SECONDS")


class TestEndToEnd:
    def test_live_search_writes_state_and_stays_silent(self, tmp_path):
        result = run_hook(search_event("s1", LIVE), tmp_path)
        assert result.returncode == 0
        assert json.loads((tmp_path / "s1.json").read_text())["used"] == 1

    def test_refusal_fails_loud_on_the_search_itself(self, tmp_path):
        """🔴 Fail loud: вахта узнаёт об отказе в тот же ход, а не потом."""
        result = run_hook(search_event("s2", REFUSAL), tmp_path)
        assert result.returncode == 2
        assert "web search budget" in result.stderr.lower()
        assert "перезапус" in result.stderr.lower()
        assert json.loads((tmp_path / "s2.json").read_text())["exhausted"] is True

    def test_agent_denied_after_refusal_end_to_end(self, tmp_path):
        run_hook(search_event("s3", REFUSAL), tmp_path)
        result = run_hook(agent_event("s3"), tmp_path)
        assert result.returncode == 2
        assert "перезапус" in result.stderr.lower()

    @pytest.mark.parametrize("text", ACCOUNT_LIMIT_TEXTS)
    def test_agent_launch_survives_account_limit_end_to_end(self, tmp_path, text):
        """🔴 Регрессия обоих случаев 09.09.2026, сквозь процесс целиком."""
        run_hook(search_event("s4", text), tmp_path)
        result = run_hook(agent_event("s4"), tmp_path)
        assert result.returncode == 0
        assert "deny" not in result.stdout

    def test_fresh_session_is_not_poisoned_by_another(self, tmp_path):
        """Метка живёт по session_id: перезапуск сессии и есть лечение."""
        run_hook(search_event("dead", REFUSAL), tmp_path)
        result = run_hook(agent_event("alive"), tmp_path)
        assert result.returncode == 0

    def test_malformed_payload_is_survived(self, tmp_path):
        result = subprocess.run(
            [sys.executable, str(HOOK)],
            input="not json",
            capture_output=True,
            text=True,
            env={
                "PATH": "/usr/bin:/bin",
                "FINPILOT_WEBSEARCH_STATE_DIR": str(tmp_path),
            },
        )
        assert result.returncode == 0
