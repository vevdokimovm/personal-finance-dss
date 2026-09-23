#!/usr/bin/env python3
"""Гейт Exa: ни один агент не стартует, если Exa в этой сессии не работает.

🔴 **Решение владельца 16.09.2026, дословно:** «вообще никакой агент не запускаем если exa
не работает. это также важно как вебсерч. когда ты даже без вебсерча запускал
исследования... что просто бесполезно».

**Чем оплачено.** Exa была недоступна агентам в 16 файлах `docs/research/raw/` начиная
с 08.09.2026; вахта узнавала об этом из отчётов постфактум и продолжала запускать.
Коннектор `claude.ai Exa` после `/login` на другой аккаунт отвечал `404 Server not found`
от самого claude.ai при живом `mcp.exa.ai`. С 16.09.2026 Exa подключена напрямую
(`claude mcp add --scope user --transport http exa https://mcp.exa.ai/mcp`).

**Три способа умереть — три проверки.**

1. **Сессия стартовала без Exa.** Инструменты MCP читаются один раз при старте процесса
   (PIT-035): добавить сервер посреди сессии бесполезно. Поэтому на SessionStart ставится
   метка, привязанная к ПРОЦЕССУ claude (pid + время старта), и только при первом
   SessionStart этого процесса. `/clear` и компакция метку не переписывают: процесс тот
   же, инструменты те же.
2. **Инструмент отвечает «not connected» / «Server not found».** Метка «мертва» до нового
   процесса; хук кричит в тот же ход.
3. **Сервис лежит.** Перед каждым запуском агента — живая проба `initialize` к
   `mcp.exa.ai`. Нет сети — нет и исследования, так что запрет здесь верен.

**Лечение — перезапуск сессии** (`/exit`, затем `claude -c`), а не ретраи.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

EXA_HOST = "mcp.exa.ai"
PROBE_URL = "https://mcp.exa.ai/mcp"
PROBE_TIMEOUT = 10
STATE_TTL_DAYS = 7

DEAD_MARKERS = (
    re.compile(r"is not connected", re.IGNORECASE),
    re.compile(r"server not found", re.IGNORECASE),
    re.compile(r"failed to (re)?connect", re.IGNORECASE),
)
RESULT_MARKERS = ('"results"', '"url"', "http://", "https://")
DEAD_MAX_CHARS = 600

RESTART_NOTICE = (
    "EXA НЕ ЗАГРУЖЕНА В ЭТУ СЕССИЮ. Агент НЕ ЗАПУСКАЕТСЯ "
    "(правило владельца 16.09.2026: без Exa, как и без WebSearch, исследование бесполезно).\n"
    "ПЕРЕЗАПУСТИ СЕССИЮ: `/exit`, затем `claude -c`, и проверь `/mcp` → `exa` connected. "
    "Инструменты MCP читаются только при старте процесса.\n"
    "Если `exa` нет в `claude mcp list` — "
    "`claude mcp add --scope user --transport http exa https://mcp.exa.ai/mcp`."
)
DEAD_NOTICE = (
    "EXA ОТВАЛИЛАСЬ В ЭТОЙ СЕССИИ. Агенты НЕ ЗАПУСКАЮТСЯ до ПЕРЕЗАПУСКА сессии.\n"
    "Сообщи владельцу с выводом инструмента."
)
DOWN_NOTICE = (
    "СЕРВИС EXA не отвечает (проба initialize к mcp.exa.ai не прошла). "
    "Агент НЕ ЗАПУСКАЕТСЯ. Проверь сеть и `claude mcp get exa`, сообщи владельцу."
)


def _servers(config: dict) -> list[dict]:
    found = list((config.get("mcpServers") or {}).values())
    for project in (config.get("projects") or {}).values():
        found.extend((project.get("mcpServers") or {}).values())
    return [server for server in found if isinstance(server, dict)]


def exa_configured(config: dict) -> bool:
    """Есть ли среди серверов MCP прямое подключение к Exa (по адресу, не по имени)."""
    return any(EXA_HOST in str(server.get("url", "")) for server in _servers(config))


def probe_alive(status: int, body: str) -> bool:
    """Живой ли сервис по ответу на `initialize`."""
    return status == 200 and '"result"' in body and "exa" in body.lower()


def response_text(response: object) -> str:
    if isinstance(response, str):
        return response
    try:
        return json.dumps(response, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(response)


def dead_reason(response: object) -> str:
    """Цитата отказа подключения, либо "" для живой выдачи и пустого ответа."""
    text = response_text(response)
    if not text or len(text) > DEAD_MAX_CHARS:
        return ""
    if any(marker in text for marker in RESULT_MARKERS):
        return ""
    if not any(marker.search(text) for marker in DEAD_MARKERS):
        return ""
    return " ".join(text.split())


def agent_verdict(marker: dict | None, alive: bool) -> tuple[bool, str]:
    """Пускать ли запуск `Agent`.

    Args:
        marker: Метка процесса claude, либо None, если SessionStart не видели.
        alive: Прошла ли живая проба сервиса.

    Returns:
        Пара (разрешено, причина отказа).
    """
    if not marker or not marker.get("loaded"):
        return False, RESTART_NOTICE
    if marker.get("dead"):
        return False, f"{DEAD_NOTICE}\nОтказ: {marker.get('reason', '')}"
    if not alive:
        return False, DOWN_NOTICE
    return True, ""


def state_dir() -> Path:
    override = os.environ.get("FINPILOT_EXA_STATE_DIR")
    root = Path(override) if override else Path.home() / ".claude" / "state" / "exa-gate"
    root.mkdir(parents=True, exist_ok=True)
    return root


def process_key() -> str:
    """Ключ процесса claude: ближайший предок с именем `claude`, pid + время старта."""
    override = os.environ.get("FINPILOT_EXA_PROCESS_KEY")
    if override:
        return override
    pid = os.getppid()
    for _ in range(8):
        try:
            out = subprocess.run(
                ["ps", "-o", "ppid=,lstart=,comm=", "-p", str(pid)],
                capture_output=True, text=True, timeout=5,
            ).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            break
        if not out:
            break
        parts = out.split()
        ppid, started, comm = parts[0], " ".join(parts[1:6]), " ".join(parts[6:])
        if Path(comm).name == "claude":
            return f"{pid}-{started}"
        pid = int(ppid)
        if pid <= 1:
            break
    return f"unknown-{os.getppid()}"


def marker_path() -> Path:
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", process_key())
    return state_dir() / f"{safe}.json"


def load_marker(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def load_config() -> dict:
    override = os.environ.get("FINPILOT_EXA_CONFIG")
    path = Path(override) if override else Path.home() / ".claude.json"
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError, ValueError):
        return {}


def service_alive() -> bool:
    forced = os.environ.get("FINPILOT_EXA_PROBE")
    if forced:
        return forced == "alive"
    body = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                   "clientInfo": {"name": "finpilot-exa-gate", "version": "1"}},
    })
    try:
        out = subprocess.run(
            ["curl", "-s", "-m", str(PROBE_TIMEOUT), "-X", "POST", PROBE_URL,
             "-H", "Content-Type: application/json",
             "-H", "Accept: application/json, text/event-stream",
             "-d", body, "-w", "\n%{http_code}"],
            capture_output=True, text=True, timeout=PROBE_TIMEOUT + 5,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    text, _, code = out.rpartition("\n")
    return probe_alive(int(code) if code.isdigit() else 0, text)


def sweep(root: Path) -> None:
    deadline = time.time() - STATE_TTL_DAYS * 86400
    for stale in root.glob("*.json"):
        if stale.stat().st_mtime < deadline:
            stale.unlink(missing_ok=True)


def handle_start() -> int:
    """Первый SessionStart процесса фиксирует, загружена ли Exa."""
    path = marker_path()
    if load_marker(path) is None:
        marker = {"loaded": exa_configured(load_config()), "dead": False,
                  "reason": "", "at": time.time()}
        path.write_text(json.dumps(marker, ensure_ascii=False))
    sweep(path.parent)
    return 0


def handle_exa_call(payload: dict) -> int:
    reason = dead_reason(payload.get("tool_response", ""))
    if not reason:
        return 0
    path = marker_path()
    marker = load_marker(path) or {"loaded": True}
    marker.update({"dead": True, "reason": reason})
    path.write_text(json.dumps(marker, ensure_ascii=False))
    sys.stderr.write(f"{DEAD_NOTICE}\nПЕРЕЗАПУСТИ СЕССИЮ.\nОтказ: {reason}\n")
    return 2


def handle_agent() -> int:
    marker = load_marker(marker_path())
    alive = service_alive() if marker and marker.get("loaded") and not marker.get("dead") else True
    allowed, reason = agent_verdict(marker, alive)
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
    tool = payload.get("tool_name") or ""
    if event == "SessionStart":
        return handle_start()
    if event == "PostToolUse" and tool.startswith("mcp__exa__"):
        return handle_exa_call(payload)
    if event == "PreToolUse" and tool == "Agent":
        return handle_agent()
    return 0


if __name__ == "__main__":
    sys.exit(main())
