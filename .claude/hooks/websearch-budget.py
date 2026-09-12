#!/usr/bin/env python3
"""Гейт WebSearch: считает расход, а на реальном отказе бюджета кричит
и не пускает агента.

🔴 **Восстановлен 11.09.2026 по прямому решению владельца**, дословно: «обнови созданные
гейты чтобы они фейл лауд когда лимит в миллиарды закончится и без вебсера агенты
не запусклись а тербовали перезапустить сессию». Версия 9.9.5 была чистым счётчиком
без вердиктов; она молчала ровно там, где молчать нельзя — доборы Д3–Д6 прошли с мёртвым
поиском, и это выяснилось только через полтора суток (`PIT-213`).

**Чем этот гейт отличается от снятого, и почему не повторит его класс ошибки.**

1. **Он не считает и не угадывает.** Прежняя версия держала собственный потолок (400)
   и объявляла бюджет исчерпанным по числу вызовов. Здесь потолка нет вовсе: поведение
   определяет ДОСЛОВНЫЙ отказ харнесса, замеренный 10–11.09.2026 —
   «This session has used its web search budget (400 of 400 WebSearch calls)».
   Число в отказе не разбирается: при лимите `999999999` текст тот же.

2. **Аккаунтный 429 больше не признак.** Оба ложняка 09.09.2026 (при 7 и при 42 поисках)
   дал список маркеров `429`, `rate limit`, `too many requests` — признаки лимита
   АККАУНТА, а не конца поиска. Их здесь нет, и тесты держат это регрессией.

3. **Выдача, в которой лишь упомянут текст отказа, гейт не поднимает.** Вахта, читающая
   про этот самый отказ, раньше подорвала бы собственный канал. Отказ отличается
   от выдачи формой: он короткий и в нём нет ни заголовка результатов, ни ссылок.

**Лечение — перезапуск сессии, а не ожидание.** Бюджет выдаётся на сессию
и делится с подагентами, поэтому метка живёт в файле по
`session_id`, и новая сессия получает чистое состояние сама. Протухание метки
по таймеру (v9.9.1) уже пробовали — лечило следствие,
класс повторился; лечения по времени здесь нет.

**Что делать вахте при срабатывании** (порядок из CLAUDE.md, каждый канал замерен):
`WebFetch` → `curl` с браузерным UA → текстовый прокси `r.jina.ai` → Exa → научные API
без ключа (OpenAlex, Crossref, Unpaywall, Semantic Scholar, EuropePMC). Но агента
на этих каналах НЕ запускать: правило владельца — канал мёртв, значит агент не
запускается, а сессия перезапускается.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

STATE_TTL_DAYS = 7

# Дословный отказ харнесса. Двух форм достаточно: полная фраза и её «скелет» с числами.
REFUSAL_MARKERS = (
    re.compile(r"used its web search budget", re.IGNORECASE),
    re.compile(r"web search budget\s*\(\s*\d+\s+of\s+\d+", re.IGNORECASE),
)
# Признаки того, что перед нами ВЫДАЧА, а не отказ: тогда упоминание фразы не считается.
RESULT_MARKERS = (
    "web search results for query",
    "links: [",
    '"url"',
)
# Отказ короткий. Порог с запасом: замеренный текст — 190 байт.
REFUSAL_MAX_CHARS = 600

RESTART_NOTICE = (
    "КАНАЛ ПОИСКА МЁРТВ: харнесс отказал по бюджету WebSearch в этой сессии.\n"
    "Агент НЕ ЗАПУСКАЕТСЯ (правило владельца: канал добычи мёртв → агент не стартует, "
    "и в промпт НЕ дописывается «обходись без поиска»).\n"
    "Лечение — ПЕРЕЗАПУСТИТЬ СЕССИЮ: бюджет выдаётся на сессию и делится "
    "с подагентами, "
    "ожидание и ретраи его не возвращают.\n"
    "Сообщи владельцу с выводом инструмента и дождись новой сессии."
)


def blank_state() -> dict:
    """Пустое состояние счётчика для новой сессии."""
    return {"used": 0, "updated": 0.0, "exhausted": False, "reason": ""}


def response_text(response: object) -> str:
    """Привести ответ инструмента к тексту: он приходит и строкой, и структурой."""
    if isinstance(response, str):
        return response
    try:
        return json.dumps(response, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(response)


def refusal_reason(response: object) -> str:
    """Вернуть текст отказа бюджета, если это он, иначе пустую строку.

    Args:
        response: Ответ инструмента WebSearch как есть.

    Returns:
        Короткая цитата отказа для журнала, либо "" — если это живая выдача,
        аккаунтный 429, пустой ответ или выдача, лишь упоминающая текст отказа.
    """
    text = response_text(response)
    if len(text) > REFUSAL_MAX_CHARS:
        return ""
    low = text.lower()
    if any(marker in low for marker in RESULT_MARKERS):
        return ""
    if not any(marker.search(text) for marker in REFUSAL_MARKERS):
        return ""
    return " ".join(text.split())[:REFUSAL_MAX_CHARS]


def record_search(state: dict, response: object) -> dict:
    """Учесть один вызов WebSearch и поднять метку, если пришёл отказ бюджета.

    Args:
        state: Текущее состояние счётчика сессии.
        response: Ответ инструмента.

    Returns:
        Новое состояние: счётчик увеличен, метка `exhausted` выставлена только
        на дословном отказе и обратно не снимается.
    """
    updated = dict(blank_state())
    updated.update(state)
    updated["used"] = state.get("used", 0) + 1
    updated["updated"] = time.time()
    reason = refusal_reason(response)
    if reason:
        updated["exhausted"] = True
        updated["reason"] = reason
    return updated


def agent_verdict(state: dict, prompt: str) -> tuple[bool, str]:
    """Пускать ли запуск `Agent`.

    Args:
        state: Состояние счётчика сессии.
        prompt: Промпт агента; на решение не влияет — запрещает не содержание задачи,
            а мёртвый канал добычи.

    Returns:
        Пара (разрешено, причина отказа). Запрет только при поднятой метке `exhausted`.
    """
    if state.get("exhausted"):
        return False, f"{RESTART_NOTICE}\nОтказ харнесса: {state.get('reason', '')}"
    return True, ""


def state_dir() -> Path:
    override = os.environ.get("FINPILOT_WEBSEARCH_STATE_DIR")
    default = Path.home() / ".claude" / "state" / "websearch-budget"
    root = Path(override) if override else default
    root.mkdir(parents=True, exist_ok=True)
    return root


def sweep(root: Path) -> None:
    """Убрать состояния давно закрытых сессий, чтобы каталог не рос вечно."""
    deadline = time.time() - STATE_TTL_DAYS * 86400
    for stale in root.glob("*.json"):
        if stale.stat().st_mtime < deadline:
            stale.unlink(missing_ok=True)


def state_path(session_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", session_id or "unknown")
    return state_dir() / f"{safe}.json"


def load_state(path: Path) -> dict:
    """Прочитать состояние сессии; чужие и битые файлы дают пустое."""
    try:
        stored = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError, ValueError):
        return blank_state()
    state = blank_state()
    state.update({key: stored[key] for key in state if key in stored})
    return state


def handle_search(payload: dict) -> int:
    """Учесть поиск; на отказе бюджета — закричать в stderr."""
    path = state_path(payload.get("session_id", ""))
    state = record_search(load_state(path), payload.get("tool_response", ""))
    path.write_text(json.dumps(state, ensure_ascii=False))
    sweep(path.parent)
    if state["exhausted"]:
        sys.stderr.write(f"{RESTART_NOTICE}\nОтказ харнесса: {state['reason']}\n")
        return 2
    return 0


def handle_agent(payload: dict) -> int:
    """Решить судьбу запуска агента."""
    path = state_path(payload.get("session_id", ""))
    prompt = payload.get("tool_input", {}).get("prompt", "")
    allowed, reason = agent_verdict(load_state(path), prompt)
    if allowed:
        return 0
    sys.stderr.write(f"{reason}\n")
    return 2


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    event = payload.get("hook_event_name")
    tool = payload.get("tool_name")
    if tool == "WebSearch" and event == "PostToolUse":
        return handle_search(payload)
    if tool == "Agent" and event == "PreToolUse":
        return handle_agent(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
