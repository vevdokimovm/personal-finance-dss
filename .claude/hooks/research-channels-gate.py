#!/usr/bin/env python3
"""Гейт каналов добычи: агент не стартует, если умер хоть один обязательный канал.

🔴 **Решение владельца 16.09.2026, дословно:** «какие еще вещи по типу exa websearch
необходимы для высшего качества ресерча? добавь тоже гейт на них если есть такие».
Живёт рядом с `websearch-budget.py` и `exa-gate.py` на том же `PreToolUse:Agent`.

**Обязательные каналы — по замерам этого проекта.**
- `r.jina.ai` — 11 из 14 источников Г21; 10.09.2026 с нашей сети целиком отдавал 401
  «bad network reputation (AS9009)», агенты молча деградировали.
- OpenAlex, Crossref — научный поиск и реквизиты без ключа (Д3–Д6 шли на них).
- EuropePMC — авторский абстракт закрытой статьи (`resultType=core`, приём Г18).
- Локальные `curl`, `pdftotext`, `tesseract` — PDF и OCR (Г20, Г25).
- У `base-kit:researcher` в `tools:` — `WebFetch`, `Bash` и прямая Exa. Без `Bash`
  агент 09.09.2026 упирался в 403 и не мог обойти их `curl`-ом.

🔴 **Wayback добавлен в обязательные 16.09.2026 по решению владельца:** «сделай так чтобы
гейты всегда чекали это и агента не запускали». Первая редакция его не гейтила, потому что
он лежал весь день; цена этого послабления измерена — Г18 упёрся в него по предписанному
каналу, Г23 не добыл ФССП, Г24 не проверил программы PyCon. Лежит — значит батч не идёт,
а ждёт, и это дешевле, чем добирать те же пункты третьим заходом.

**Semantic Scholar — условно обязателен:** без ключа он отдаёт 429 постоянно, и жёсткий
запрет по нему заблокировал бы работу навсегда. Поэтому он проверяется ТОЛЬКО когда в
окружении есть `SEMANTIC_SCHOLAR_API_KEY`; без ключа гейт молчит, а канал остаётся
запасным. Ключ бесплатный — получить его решает владелец.

🔴 **Браузер обязателен с 17.09.2026** — решение владельца: «дай им этот инструмент и включи
в гейт инструментов без которых агенты не запускаются». Замер того же дня: `data.gov.ru` давал
000 на `curl` и был записан мёртвым, а в браузере открылся (перезапуск на «ГосТех», июль 2025).
Вердикты 403 стоят в 55 файлах сырья, 000 — в 34, и браузером не проверялся ни один: антибот
узнаёт настоящий браузер по отпечатку TLS и выполнению JS, `curl` этого не подделывает.
Проверяются три вещи: инструменты `chrome-devtools` в `tools:` исследователя, включённый плагин
в `~/.claude/settings.json` и установленный Chrome. Плагин и Chrome гейтят ЛЮБОГО агента —
это канал добычи, как `r.jina.ai`.

🔴 **Плагины исследования обязательны с 17.09.2026** — решение владельца «впиши все»: context7
(документация библиотек под версию — Г33, Г34, фронт), serena и pyright-lsp (семантическая
навигация по коду вместо `grep`), playwright (второй браузерный движок), claude-security
(проверенный скан уязвимостей — продолжение Г32), math-olympiad (атака доказательств свежими
верификаторами — Г40), last30days (боли пользователей по соцсетям), github. Все должны быть
включены; context7 — ещё и живой: размещённый сервер, пробуется JSON-RPC `tools/list`.
`gh` обязан быть авторизован: поиск по коду GitHub без авторизации не работает вовсе, а он —
главный канал корпуса выписок (Г47: 22 вёрстки Сбербанка пришли из чужого репозитория).

**Коннекторы claude.ai (Drive, Notion, Claude Docs) выданы агенту на чтение, но НЕ гейтятся** —
решение владельца 17.09.2026. Они привязаны к аккаунту claude.ai и отваливаются при каждой смене
вахты (так ломался коннектор Exa); гейт по ним останавливал бы агентов после каждой смены.
Запись во внешние сервисы (Gmail, шаринг Drive, Calendar, правка Notion, Gamma, Artifact)
и `upload_file` браузера агенту не выданы: фоновый агент не действует от имени владельца наружу.

**Unpaywall не пробуется:** его запрос требует адрес почты, а слать его сторонним сервисам
без просьбы владельца нельзя.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PROBE_TIMEOUT = 12
# 🔴 Замер 17.09.2026: replay Wayback отдаёт за 8-21 с (четыре пробы подряд: 200/14,9 с,
# 302/20,7 с, 302/20,6 с, 200/8,2 с) — общий порог 12 с рубил ЖИВОЙ канал по калибровке,
# а не по факту, и гейт краснел третий запуск подряд. Остальные каналы укладываются в 12 с,
# поэтому поднят порог только у Wayback: платить ожиданием за все семь каналов ради одного
# нельзя (гейт идёт перед КАЖДЫМ запуском агента).
PROBE_TIMEOUT_OVERRIDES = {"wayback": 30}
# Один повтор с паузой: Semantic Scholar без ключа и прокси троттлят одиночный запрос,
# и одноразовая проба дважды за 17.09.2026 объявила мёртвым живой канал (соседние
# четыре запроса подряд — 200). Два отказа подряд с паузой — уже сигнал, одна — шум.
PROBE_ATTEMPTS = 2
PROBE_PAUSE_S = 6

PROBES = {
    "jina": "https://r.jina.ai/https://example.com",
    "openalex": "https://api.openalex.org/works?search=debt&per-page=1",
    "crossref": "https://api.crossref.org/works?query=debt&rows=1",
    "europepmc": ("https://www.ebi.ac.uk/europepmc/webservices/rest/search"
                  "?query=debt&format=json&pageSize=1"),
    # 🔴 Замер 16.09.2026: служебный API `wayback/available` и CDX падают ОТДЕЛЬНО
    # от отдачи снимков. Проба по ним дала ложный отрицательный дважды и стоила целого
    # класса 4 в аудитах № 3 и № 4 («Wayback лежал») — при том что снимки отдавались.
    # Поэтому пробуем именно replay-эндпоинт по «годовому» адресу: он сам редиректит
    # на ближайший снимок.
    "wayback": "https://web.archive.org/web/2020/https://example.com",
    "semanticscholar": ("https://api.semanticscholar.org/graph/v1/paper/search/bulk"
                        "?query=debt&limit=1"),
    "context7": "https://mcp.context7.com/mcp",
}
# MCP-серверы отвечают только на POST с JSON-RPC: GET на тот же адрес даёт 405.
POST_BODIES = {
    "context7": '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}',
}
# Проверяется, только если есть ключ: без ключа сервис отдаёт 429 постоянно.
# 🔴 Замер 16.09.2026 (Г31.4): у Semantic Scholar лежит ОДИН эндпоинт из четырёх —
# `/paper/search` даёт 429 всегда, а `search/bulk`, `/paper/DOI:<doi>` и `/citations`
# отвечали 200 во всех попытках без ключа. Запись «S2 = 429» в Д3–Д6 и Г18 описывала
# один эндпоинт, а не канал. Поэтому S2 переведён в ОБЯЗАТЕЛЬНЫЕ и пробуется по `bulk`;
# ключ не нужен (вывод того же замера).
OPTIONAL_PROBES: dict[str, str] = {}
ALL_PROBES = {**PROBES, **OPTIONAL_PROBES}
LABELS = {
    "jina": "r.jina.ai (текстовый прокси)",
    "openalex": "OpenAlex",
    "crossref": "Crossref",
    "europepmc": "EuropePMC",
    "wayback": "Wayback Machine (archive.org)",
    "semanticscholar": "Semantic Scholar",
    "context7": "Context7 (документация библиотек)",
}
MUST_CONTAIN = {
    # 🔴 Признак — СВОЯ разметка прокси, а не текст целевой страницы: 17.09.2026 прокси
    # начал отдавать по example.com кэш чужого «Test Document», и проба по словам
    # страницы дала ложный отрицательный при исправном канале.
    "jina": "URL Source:",
    "openalex": '"results"',
    "crossref": '"items"',
    "europepmc": '"resultList"',
    "wayback": "Example Domain",
    "semanticscholar": '"data"',
    "context7": '"query-docs"',
}
REQUIRED_BINS = ("curl", "pdftotext", "tesseract")
BROWSER_PREFIX = "mcp__plugin_chrome-devtools-mcp_chrome-devtools__"
BROWSER_TOOLS = tuple(f"{BROWSER_PREFIX}{name}" for name in
                      ("new_page", "navigate_page", "take_snapshot", "close_page"))
CONTEXT7_TOOLS = ("mcp__plugin_context7_context7__resolve-library-id",
                  "mcp__plugin_context7_context7__query-docs")
REQUIRED_TOOLS = ("WebFetch", "Bash", "mcp__exa__web_search_exa",
                  "mcp__exa__web_fetch_exa", *BROWSER_TOOLS, *CONTEXT7_TOOLS)
RESEARCH_PLUGINS = (
    "chrome-devtools-mcp@chrome-devtools-plugins", "context7@claude-plugins-official",
    "serena@claude-plugins-official", "pyright-lsp@claude-plugins-official",
    "playwright@claude-plugins-official", "claude-security@claude-plugins-official",
    "math-olympiad@claude-plugins-official", "last30days@last30days-skill",
    "github@claude-plugins-official",
)
DEFAULT_USER_SETTINGS = Path.home() / ".claude" / "settings.json"
DEFAULT_CHROME_APP = Path("/Applications/Google Chrome.app")
RESEARCHER_TYPES = ("base-kit:researcher", "researcher")
DEFAULT_RESEARCHER = Path.home() / "repos" / "base-repo" / ".claude" / "agents" / "researcher.md"


ALIVE = "alive"
DEGRADED = "degraded"
DEAD = "dead"
# 🔴 Замер 18.09.2026: 401 «bad network reputation (AS9009)» у r.jina.ai и 429 у archive.org
# держались несколько минут и сами разошлись до 200, а в БРАУЗЕРЕ оба канала открылись
# сразу. Эти два кода называют репутацию нашего выхода и троттлинг, а не содержимое, —
# значит закрыт один способ ходить в канал, а не канал. Всё остальное (000, таймаут, 403,
# 5xx, 200 без признака) остаётся смертью: гейты снимали дважды, и оба раза это стоило суток.
DEGRADED_CODES = (401, 429)


def classify(name: str, status: int, body: str) -> str:
    """Состояние канала: жив, деградировал до браузера или мёртв."""
    if status == 200 and MUST_CONTAIN[name] in body:
        return ALIVE
    if status in DEGRADED_CODES:
        return DEGRADED
    return DEAD


def normalize(probes: dict) -> dict:
    """Привести замер к состояниям: старая форма True/False читается как жив/мёртв."""
    return {name: (ALIVE if state else DEAD) if isinstance(state, bool) else state
            for name, state in probes.items()}


def channel_alive(name: str, status: int, body: str) -> bool:
    """Жив ли канал: код 200 и признак настоящего ответа в теле."""
    return classify(name, status, body) == ALIVE


def missing_tools(definition: str) -> list[str]:
    """Каких обязательных инструментов нет в строке `tools:` определения агента."""
    line = next((row for row in definition.splitlines() if row.startswith("tools:")), "")
    granted = {item.strip() for item in line.removeprefix("tools:").split(",")}
    return [tool for tool in REQUIRED_TOOLS if tool not in granted]


def disabled_plugins(settings: dict) -> list[str]:
    """Какие обязательные плагины исследования не включены в пользовательских настройках."""
    enabled = settings.get("enabledPlugins", {})
    return [name for name in RESEARCH_PLUGINS if enabled.get(name) is not True]


def verdict(probes: dict, missing_bins: list[str], missing_tools: list[str],
            browser_problems: list[str] | tuple = ()) -> tuple[bool, str]:
    """Собрать решение: запрет, если мёртв хоть один канал.

    Args:
        probes: Имя канала → жив ли.
        missing_bins: Отсутствующие локальные утилиты.
        missing_tools: Инструменты, которых нет у агента-исследователя.
        browser_problems: Что мешает инструментам агента: плагины, Chrome, `gh auth`.

    Returns:
        Пара (разрешено, причина отказа со списком всего мёртвого).
    """
    states = normalize(probes)
    problems = [f"канал {LABELS[name]} не отвечает"
                for name, state in states.items() if state == DEAD]
    # Деградация не прикрывает смерть, но и не заменяет её: если анонимный доступ закрыт
    # ВЕЗДЕ, дело уже не в репутации одного сервиса, а в нашей сети — это запрет.
    if states and all(state == DEGRADED for state in states.values()):
        problems.append("анонимный доступ закрыт по ВСЕМ каналам — это сеть, не сервисы")
    problems += [f"нет утилиты {name}" for name in missing_bins]
    problems += list(browser_problems)
    problems += [f"у base-kit:researcher нет инструмента {name}" for name in missing_tools]
    if not problems:
        return True, ""
    return False, (
        "КАНАЛЫ ДОБЫЧИ НЕПОЛНЫ. Агент НЕ ЗАПУСКАЕТСЯ "
        "(правило владельца 16.09.2026: исследование без обязательных каналов бесполезно).\n"
        + "\n".join(f"- {item}" for item in problems)
        + "\nСообщи владельцу. Сеть и прокси — проверить и повторить; инструменты агента — "
          "править `~/repos/base-repo/.claude/agents/researcher.md` и ПЕРЕЗАПУСТИТЬ сессию."
    )


def required_probes() -> dict:
    """Какие каналы обязательны сейчас: Semantic Scholar — только при наличии ключа."""
    targets = dict(PROBES)
    if os.environ.get("SEMANTIC_SCHOLAR_API_KEY"):
        targets.update(OPTIONAL_PROBES)
    return targets


def degraded_note(probes: dict) -> str:
    """Громкое предупреждение о каналах, живых только через браузер.

    Args:
        probes: Имя канала → состояние.

    Returns:
        Текст предупреждения или пустая строка, если деградировавших каналов нет.
    """
    names = [LABELS[name] for name, state in normalize(probes).items()
             if state == DEGRADED]
    if not names:
        return ""
    return (
        "КАНАЛЫ ДЕГРАДИРОВАЛИ, агент запускается: анонимный curl закрыт "
        "(401 по репутации выхода или 429 по троттлингу), сам источник жив.\n"
        + "\n".join(f"- {name}" for name in names)
        + "\nБрать эти каналы через браузер либо повторить через несколько минут. "
          "Недоступным такой источник НЕ помечать (правило владельца 18.09.2026)."
    )


def probe(name: str) -> str:
    """Состояние канала по нескольким попыткам: лучшее из полученных."""
    best = DEAD
    for attempt in range(PROBE_ATTEMPTS):
        if attempt:
            time.sleep(PROBE_PAUSE_S)
        state = _probe_once(name)
        if state == ALIVE:
            return ALIVE
        if state == DEGRADED:
            best = DEGRADED
    return best


def probe_timeout(name: str) -> int:
    """Сколько ждать этот канал: у медленных свой порог, у остальных общий."""
    return PROBE_TIMEOUT_OVERRIDES.get(name, PROBE_TIMEOUT)


def _probe_once(name: str) -> str:
    # Без браузерного UA: r.jina.ai с ним сам отдаёт капчу Cloudflare (403),
    # замерено 16.09.2026; без UA тот же адрес — 200 и текст страницы.
    limit = probe_timeout(name)
    command = ["curl", "-s", "-L", "-m", str(limit), ALL_PROBES[name],
               "-w", "\n%{http_code}"]
    if name in POST_BODIES:
        command += ["-X", "POST", "-H", "Content-Type: application/json",
                    "-H", "Accept: application/json, text/event-stream",
                    "-d", POST_BODIES[name]]
    try:
        out = subprocess.run(
            command,
            capture_output=True, text=True, timeout=limit + 5,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return DEAD
    body, _, code = out.rpartition("\n")
    return classify(name, int(code) if code.isdigit() else 0, body)


def probe_all() -> dict:
    forced = os.environ.get("FINPILOT_CHANNELS_PROBE")
    if forced:
        return normalize(json.loads(forced))
    targets = required_probes()
    with ThreadPoolExecutor(max_workers=len(targets)) as pool:
        return dict(zip(targets, pool.map(probe, targets)))


def researcher_gaps() -> list[str]:
    path = Path(os.environ.get("FINPILOT_RESEARCHER_FILE") or DEFAULT_RESEARCHER)
    try:
        return missing_tools(path.read_text())
    except OSError:
        return list(REQUIRED_TOOLS)


def browser_gaps() -> list[str]:
    """Что мешает агентам открыть источник в браузере."""
    problems = []
    path = Path(os.environ.get("FINPILOT_USER_SETTINGS") or DEFAULT_USER_SETTINGS)
    try:
        settings = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        settings = {}
    problems += [f"плагин {name} не включён" for name in disabled_plugins(settings)]
    chrome = Path(os.environ.get("FINPILOT_CHROME_APP") or DEFAULT_CHROME_APP)
    if not chrome.exists():
        problems.append(f"не установлен Google Chrome ({chrome})")
    if not gh_authed():
        problems.append("`gh auth status` не проходит — поиск по коду GitHub недоступен "
                        "(владельцу: `gh auth login`)")
    return problems


def gh_authed() -> bool:
    """Авторизован ли `gh`: без этого не работает `gh search code`."""
    forced = os.environ.get("FINPILOT_GH_AUTH")
    if forced is not None:
        return forced == "1"
    try:
        return subprocess.run(["gh", "auth", "status"], capture_output=True,
                              timeout=PROBE_TIMEOUT).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def handle_agent(payload: dict) -> int:
    subagent = payload.get("tool_input", {}).get("subagent_type", "")
    gaps = researcher_gaps() if subagent in RESEARCHER_TYPES else []
    bins = [name for name in REQUIRED_BINS if shutil.which(name) is None]
    probes = probe_all()
    allowed, reason = verdict(probes, bins, gaps, browser_gaps())
    if not allowed:
        sys.stderr.write(f"{reason}\n")
        return 2
    # Деградация не запрещает запуск, но молчать о ней нельзя (PIT-213): текст уходит
    # и в системное сообщение сессии, и в stderr — на случай, если JSON не прочтут.
    note = degraded_note(probes)
    if note:
        sys.stdout.write(json.dumps({"systemMessage": note}, ensure_ascii=False) + "\n")
        sys.stderr.write(f"{note}\n")
    return 0


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if payload.get("hook_event_name") == "PreToolUse" and payload.get("tool_name") == "Agent":
        return handle_agent(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
