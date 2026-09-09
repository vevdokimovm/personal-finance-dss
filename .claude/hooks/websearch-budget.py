#!/usr/bin/env python3
"""Бюджет WebSearch: считает поиски и не пускает агента в исчерпанную сессию.

🔴 Оплачено ходом 08.09.2026. Тема 12 очереди исследований (портфельная теория)
отработала при счётчике 400/400 ДО первого запроса: WebSearch молча возвращал пустоту,
`Bash` у подагентов отключён, обходных каналов у них нет вовсе. Оба подагента честно
отчитались по памяти обучения — 629 строк, ни одного живого первоисточника. Ход потрачен,
тему пришлось перезапускать в новой сессии.

Разрыв был не в дисциплине, а в наблюдаемости: признака «поиск кончился» не существовало
нигде. Пустой ответ на узкий запрос и пустой ответ на исчерпанном лимите выглядят
одинаково, поэтому вахта узнавала об исчерпании постфактум, разбирая отчёт агента.

Хук закрывает это с двух сторон:
  * `PostToolUse:WebSearch` — считает вызовы и распознаёт исчерпание по ответу;
  * `PreToolUse:Agent` — при исчерпании ЗАПРЕЩАЕТ запуск и говорит владельцу прямым
    текстом, что нужен новый чат или `/clear`. Агент в исчерпанной сессии бесполезен.

Ложное срабатывание дороже пропуска: хук, глушащий исправный запуск, будет снят. Поэтому
одиночный пустой ответ исчерпанием не считается — нужны два подряд либо явный маркер
лимита. Агент, которому поиск не нужен, проходит по метке `NOSEARCH` в промпте.

Счётчик живёт на `session_id`: новая сессия (`/clear`, новый чат) — новый файл, то есть
сброс происходит ровно тогда же, когда его делает сам харнесс.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

LIMIT = 400
WARN_AT = 350
EMPTY_STREAK_FOR_EXHAUSTION = 2
MIN_LIVE_ANSWER = 40
STATE_TTL_DAYS = 7

LIMIT_MARKERS = re.compile(
    r"rate limit|quota|limit reached|limit exceeded|exceeded your|too many requests"
    r"|429|not available|unavailable|search is disabled",
    re.IGNORECASE,
)

NOSEARCH = re.compile(r"\bNOSEARCH\b")

# Инструмент запуска субагентов зовётся `Agent` здесь и `Task` в других сборках
# харнесса. Гейт обязан держать оба имени: промах по имени = молчаливо снятый гейт.
AGENT_TOOLS = {"Agent", "Task"}

ADVICE = (
    "Поиск в этой сессии кончился. Запускать агентов бессмысленно: у подагентов нет "
    "ни WebSearch, ни Bash, они вернутся с пересказом по памяти.\n"
    "Что делать: новый чат или /clear — счётчик сбрасывается только вместе с сессией.\n"
    "Если искать нужно прямо сейчас и уходить не хочется — ищи из главной сессии через "
    "curl (замерено 08.09.2026: html.duckduckgo.com отдаёт 202, arxiv.org — 200)."
)


def blank_state() -> dict:
    """Пустое состояние счётчика для новой сессии."""
    return {"used": 0, "empty_streak": 0, "exhausted": False, "updated": 0.0}


def classify_response(response: object) -> str:
    """Что ответ WebSearch говорит о живости поиска: ok, empty или exhausted."""
    text = response if isinstance(response, str) else json.dumps(response, ensure_ascii=False)
    if LIMIT_MARKERS.search(text):
        return "exhausted"
    return "ok" if len(text.strip()) >= MIN_LIVE_ANSWER else "empty"


def record_search(state: dict, response: object) -> dict:
    """Учесть один вызов WebSearch и пересчитать признак исчерпания."""
    verdict = classify_response(response)
    updated = dict(state)
    updated["used"] = state["used"] + 1
    updated["empty_streak"] = state["empty_streak"] + 1 if verdict == "empty" else 0
    updated["exhausted"] = bool(
        state["exhausted"]
        or verdict == "exhausted"
        or updated["empty_streak"] >= EMPTY_STREAK_FOR_EXHAUSTION
        or updated["used"] >= LIMIT
    )
    updated["updated"] = time.time()
    return updated


def warning_for(state: dict) -> str | None:
    """Текст владельцу, когда бюджет требует внимания; иначе None."""
    if state["exhausted"]:
        return f"🔴 WebSearch исчерпан (израсходовано {state['used']} из {LIMIT}).\n{ADVICE}"
    if state["used"] >= WARN_AT:
        return (
            f"🟡 WebSearch на исходе: {state['used']} из {LIMIT}. "
            f"Осталось {LIMIT - state['used']} запросов — тяжёлую тему в эту сессию "
            "лучше не запускать."
        )
    return None


def agent_verdict(state: dict, prompt: str) -> tuple[bool, str]:
    """Пускать ли запуск Agent при текущем состоянии бюджета."""
    if not state["exhausted"] or NOSEARCH.search(prompt):
        return True, ""
    return False, (
        f"Запуск агента заблокирован: WebSearch в этой сессии исчерпан "
        f"({state['used']} из {LIMIT}).\n{ADVICE}\n"
        "Если агенту поиск не нужен — добавь NOSEARCH в его промпт, и запуск пройдёт."
    )


def state_dir() -> Path:
    override = os.environ.get("FINPILOT_WEBSEARCH_STATE_DIR")
    root = Path(override) if override else Path.home() / ".claude" / "state" / "websearch-budget"
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
    try:
        stored = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError, ValueError):
        return blank_state()
    state = blank_state()
    state.update({key: stored[key] for key in state if key in stored})
    return state


def emit(system_message: str, deny_reason: str | None = None) -> None:
    payload: dict = {"systemMessage": system_message}
    if deny_reason is not None:
        payload["hookSpecificOutput"] = {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": deny_reason,
        }
    else:
        payload["hookSpecificOutput"] = {
            "hookEventName": "PostToolUse",
            "additionalContext": system_message,
        }
    print(json.dumps(payload, ensure_ascii=False))


def handle_search(payload: dict) -> None:
    path = state_path(payload.get("session_id", ""))
    was_exhausted = load_state(path).get("exhausted", False)
    state = record_search(load_state(path), payload.get("tool_response", ""))
    path.write_text(json.dumps(state, ensure_ascii=False))
    sweep(path.parent)
    message = warning_for(state)
    if message and not (was_exhausted and state["exhausted"]):
        emit(message)


def handle_agent(payload: dict) -> None:
    state = load_state(state_path(payload.get("session_id", "")))
    prompt = (payload.get("tool_input") or {}).get("prompt", "")
    allowed, reason = agent_verdict(state, prompt)
    if not allowed:
        emit(reason, deny_reason=reason)
    elif state["used"] >= WARN_AT:
        emit(warning_for(state) or "")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    tool = payload.get("tool_name")
    event = payload.get("hook_event_name")
    if tool == "WebSearch" and event == "PostToolUse":
        handle_search(payload)
    elif tool in AGENT_TOOLS and event == "PreToolUse":
        handle_agent(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
