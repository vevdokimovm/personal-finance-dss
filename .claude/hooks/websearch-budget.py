#!/usr/bin/env python3
"""Счётчик WebSearch: наблюдает расход и НИЧЕГО не запрещает.

🔴 Ограничение снято 09.09.2026 по прямому решению владельца: «сними нахер это
ограничение вовсе… чтобы бесконечные запросы можно было делать если это искуственный
лимит». Прежняя версия (v9.9.0) считала поиски, объявляла бюджет исчерпанным и
запрещала запуск `Agent`.

**Почему снято — три факта, а не усталость от гейта.**

1. **Числа 400 не существует за пределами этого файла.** Оно было нашей выдумкой.
   Публичного лимита «N поисков за сессию» нет: по докам платформы ограничения — это
   `max_uses` на один запрос и квота на уровне организации.

2. **Гейт измерял не ту величину.** Наблюдаемый в Claude Code отказ описан в
   `anthropics/claude-code` issue #27074: WebSearch делает побочный запрос
   (`source:"side_query"`), и тот отбивается 429 **по типу авторизации** — на подписке
   Pro/Max падает, на API-ключе те же запросы проходят. Число сделанных поисков к этому
   отношения не имеет, поэтому счётчик в принципе не мог предсказывать отказ.

3. **Он дважды за один день заглушил исправную работу.** 09.09.2026 сначала при 7
   поисках из 400, затем при 42 из 400 — оба раза приняв 429 от лимита АККАУНТА за
   исчерпание ПОИСКА, потому что в маркерах стояли `429`, `rate limit`,
   `too many requests`. Второй случай стоил темы 18: агент был заблокирован при живом
   поиске, что тут же опровергнуто прямым запросом из вахты. Первый случай пытались
   лечить протуханием метки через 30 минут — починка не удержала, потому что лечила
   следствие, а не причину.

Собственное правило прежней версии гласило: «Ложное срабатывание дороже пропуска: хук,
глушащий исправный запуск, будет снят». Два ложных срабатывания подряд — этот случай
наступил.

**Что осталось.** Хук считает вызовы `WebSearch` в файле состояния по `session_id` —
чистое наблюдение для замеров расхода, без вердиктов и без вывода владельцу. Вердиктов
он больше не выносит вовсе, поэтому ложно сработать ему нечем.

**Признак настоящего исчерпания поиска для вахты — не счётчик, а ответ:** пустые выдачи
подряд на заведомо широких запросах. Это решение живого человека по месту, а не
автоматика: отличить исчерпание от узкого запроса машинно не удалось за две попытки.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

STATE_TTL_DAYS = 7


def blank_state() -> dict:
    """Пустое состояние счётчика для новой сессии."""
    return {"used": 0, "updated": 0.0}


def record_search(state: dict, response: object) -> dict:
    """Учесть один вызов WebSearch.

    Args:
        state: Текущее состояние счётчика сессии.
        response: Ответ инструмента; не анализируется — содержимое ни на что не влияет.

    Returns:
        Новое состояние с увеличенным счётчиком.
    """
    updated = dict(state)
    updated["used"] = state.get("used", 0) + 1
    updated["updated"] = time.time()
    return updated


def agent_verdict(state: dict, prompt: str) -> tuple[bool, str]:
    """Пускать ли запуск `Agent`.

    Всегда да. Функция сохранена, чтобы гарантия «агент не блокируется никогда»
    оставалась проверяемой тестом, а не подразумевалась отсутствием кода.

    Args:
        state: Состояние счётчика; на решение не влияет.
        prompt: Промпт агента; на решение не влияет.

    Returns:
        Пара (разрешено, причина отказа) — всегда (True, "").
    """
    return True, ""


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
    """Прочитать состояние сессии.

    Ключи прежней версии (`exhausted`, `empty_streak`, `reason`) отбрасываются:
    файлы старых сессий не должны влиять на поведение.
    """
    try:
        stored = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError, ValueError):
        return blank_state()
    state = blank_state()
    state.update({key: stored[key] for key in state if key in stored})
    return state


def handle_search(payload: dict) -> None:
    """Учесть поиск и промолчать."""
    path = state_path(payload.get("session_id", ""))
    state = record_search(load_state(path), payload.get("tool_response", ""))
    path.write_text(json.dumps(state, ensure_ascii=False))
    sweep(path.parent)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if payload.get("tool_name") == "WebSearch" and payload.get("hook_event_name") == "PostToolUse":
        handle_search(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
