"""Гейт каналов добычи: агент не стартует, если умер хоть один обязательный канал.

**Решение владельца 16.09.2026, дословно:** «какие еще вещи по типу exa websearch необходимы
для высшего качества ресерча? добавь тоже гейт на них если есть такие».

**Какие каналы обязательны — по замерам, не по вкусу.**
- `r.jina.ai` — через него взято 11 из 14 источников батча Г21; 10.09.2026 он с нашей сети
  целиком отдавал 401 «bad network reputation», и агенты молча деградировали.
- OpenAlex и Crossref — поиск и реквизиты научных работ без ключа; на них держались
  доборы Д3–Д6 при мёртвом WebSearch.
- EuropePMC — дословный авторский абстракт по закрытым статьям (приём Г18).
- Локальные `curl`, `pdftotext`, `tesseract` — PDF и OCR (Г20, Г25).
- У агента-исследователя в `tools:` обязаны быть `WebFetch`, `Bash` и прямая Exa: без Bash
  агент упирался в 403 и не мог обойти их `curl`-ом (09.09.2026).
- 🔴 **Браузер** (`chrome-devtools`) — решение владельца 17.09.2026: «дай им этот инструмент
  и включи в гейт инструментов без которых агенты не запускаются». Замер того же дня:
  `data.gov.ru` отдавал 000 на `curl` и был записан мёртвым, а в браузере открылся; вердикты
  403 стоят в 55 файлах сырья, 000 — в 34, и браузером не проверялся ни один. Гейт требует
  три вещи: инструменты браузера в `tools:` исследователя, включённый плагин и установленный Chrome.
- 🔴 **Плагины исследования** — решение владельца 17.09.2026 «впиши все»: context7, serena,
  pyright-lsp, playwright, claude-security, math-olympiad, last30days, github. Гейт требует,
  чтобы все были включены; context7 — ещё и живой (пробуется `tools/list`); `gh` авторизован —
  поиск по коду GitHub без авторизации не работает вовсе, а это главный канал корпуса выписок (Г47).

**Wayback тоже обязателен** — решение владельца 16.09.2026: «сделай так чтобы гейты всегда
чекали это и агента не запускали». Послабление первой редакции оплачено: Г18 упёрся в него
по предписанному каналу, Г23 не добыл ФССП, Г24 не проверил программы PyCon.

**Semantic Scholar — только при наличии `SEMANTIC_SCHOLAR_API_KEY`:** без ключа сервис
отдаёт 429 постоянно, и жёсткий запрет по нему остановил бы работу навсегда.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = (Path(__file__).resolve().parents[1] / ".claude" / "hooks"
        / "research-channels-gate.py")

BROWSER = "mcp__plugin_chrome-devtools-mcp_chrome-devtools__"
GOOD_TOOLS = ("tools: WebSearch, WebFetch, Bash, Read, Write, Edit, Grep, Glob, Agent, "
              "mcp__exa__web_search_exa, mcp__exa__web_fetch_exa, "
              f"{BROWSER}new_page, {BROWSER}navigate_page, {BROWSER}take_snapshot, "
              f"{BROWSER}close_page, "
              "mcp__plugin_context7_context7__resolve-library-id, "
              "mcp__plugin_context7_context7__query-docs\n")
RESEARCH_PLUGINS = (
    "chrome-devtools-mcp@chrome-devtools-plugins", "context7@claude-plugins-official",
    "serena@claude-plugins-official", "pyright-lsp@claude-plugins-official",
    "playwright@claude-plugins-official", "claude-security@claude-plugins-official",
    "math-olympiad@claude-plugins-official", "last30days@last30days-skill",
    "github@claude-plugins-official",
)
PLUGIN_ON = {"enabledPlugins": {name: True for name in RESEARCH_PLUGINS}}
ALL_ALIVE = {"jina": True, "openalex": True, "crossref": True, "europepmc": True,
             "wayback": True, "semanticscholar": True, "context7": True}


@pytest.fixture(scope="module")
def hook():
    spec = importlib.util.spec_from_file_location("channels_gate", HOOK)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def agent_payload(subagent_type: str = "base-kit:researcher") -> dict:
    return {
        "hook_event_name": "PreToolUse",
        "session_id": "s1",
        "tool_name": "Agent",
        "tool_input": {"prompt": "исследуй", "subagent_type": subagent_type},
    }


def run_hook(payload: dict, tmp: Path, probes: dict, tools_line: str | None = GOOD_TOOLS,
             path_dirs: str = f"/usr/bin:/bin:/usr/local/bin:{Path.home()}/.local/bin",
             user_settings: dict | None = None,
             chrome_present: bool = True,
             gh_authed: bool = True) -> subprocess.CompletedProcess:
    agent_file = tmp / "researcher.md"
    if tools_line is None:
        agent_file.unlink(missing_ok=True)
    else:
        agent_file.write_text(f"---\nname: researcher\n{tools_line}---\nbody\n")
    settings_file = tmp / "user_settings.json"
    settings_file.write_text(json.dumps(PLUGIN_ON if user_settings is None else user_settings))
    chrome_app = tmp / "Google Chrome.app"
    if chrome_present:
        chrome_app.mkdir(exist_ok=True)
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={
            "PATH": path_dirs,
            "FINPILOT_CHANNELS_PROBE": json.dumps(probes),
            "FINPILOT_RESEARCHER_FILE": str(agent_file),
            "FINPILOT_USER_SETTINGS": str(settings_file),
            "FINPILOT_CHROME_APP": str(chrome_app),
            "FINPILOT_GH_AUTH": "1" if gh_authed else "0",
        },
    )


# --- чистая логика -----------------------------------------------------------


@pytest.mark.parametrize("name,status,body,ok", [
    ("jina", 200, "Title: Example Domain\nURL Source: https://example.com", True),
    # Прокси может отдать кэш чужой страницы — признаком служит его собственная разметка,
    # а не текст цели (ложный отрицательный, замеренный 17.09.2026).
    ("jina", 200,
     "Title: Test Document\nURL Source: https://example.com/\nMarkdown Content:", True),
    ("jina", 200, "Just a moment...", False),
    ("jina", 401, '{"message":"bad network reputation (AS9009)"}', False),
    ("jina", 200, '{"message":"blocked from performing anonymous queries"}', False),
    ("openalex", 200, '{"meta":{},"results":[{"id":"W1"}]}', True),
    ("openalex", 429, "", False),
    ("crossref", 200, '{"message":{"items":[{"DOI":"10.1"}]}}', True),
    ("crossref", 503, "", False),
    ("europepmc", 200, '{"resultList":{"result":[]}}', True),
    ("europepmc", 200, "<html>maintenance</html>", False),
    # Проба идёт по replay-эндпоинту, а не по служебному API: они падают порознь,
    # и проба по `wayback/available` дважды дала ложный отрицательный (16.09.2026).
    ("wayback", 200, "<html><title>Example Domain</title>…web.archive.org…</html>", True),
    ("wayback", 503, "Internet Archive: Temporarily Offline", False),
    ("wayback", 429, "", False),
    ("wayback", 200, "Internet Archive: Temporarily Offline", False),
    ("semanticscholar", 200, '{"total":1,"data":[{"paperId":"x"}]}', True),
    ("semanticscholar", 429, '{"message":"Too Many Requests"}', False),
    ("context7", 200, 'event: message\ndata: {"result":{"tools":[{"name":"query-docs"}]}}', True),
    ("context7", 200, '{"error":{"code":-32001,"message":"Unauthorized"}}', False),
    ("context7", 503, "", False),
])
def test_channel_alive(hook, name, status, body, ok):
    assert hook.channel_alive(name, status, body) is ok


def test_missing_researcher_tools(hook):
    assert hook.missing_tools(GOOD_TOOLS) == []
    no_bash = GOOD_TOOLS.replace("Bash, ", "")
    assert hook.missing_tools(no_bash) == ["Bash"]
    old_exa_only = "tools: WebFetch, Bash, mcp__claude_ai_Exa__web_search_exa\n"
    assert "mcp__exa__web_search_exa" in hook.missing_tools(old_exa_only)
    assert hook.missing_tools("") == list(hook.REQUIRED_TOOLS)


def test_browser_tools_required(hook):
    """Без браузера отказ `curl` записывается как смерть источника (data.gov.ru, 17.09.2026)."""
    no_browser = GOOD_TOOLS.split(f", {BROWSER}new_page")[0] + "\n"
    missing = hook.missing_tools(no_browser)
    assert f"{BROWSER}new_page" in missing
    assert f"{BROWSER}take_snapshot" in missing


@pytest.mark.parametrize("settings,missing", [
    (PLUGIN_ON, []),
    ({"enabledPlugins": dict(PLUGIN_ON["enabledPlugins"],
                             **{"serena@claude-plugins-official": False})},
     ["serena@claude-plugins-official"]),
    ({"enabledPlugins": {}}, list(RESEARCH_PLUGINS)),
    ({}, list(RESEARCH_PLUGINS)),
])
def test_disabled_research_plugins(hook, settings, missing):
    assert hook.disabled_plugins(settings) == missing


def test_context7_tools_required(hook):
    no_context7 = GOOD_TOOLS.replace("mcp__plugin_context7_context7__query-docs", "Read")
    assert "mcp__plugin_context7_context7__query-docs" in hook.missing_tools(no_context7)


def test_verdict_names_browser_problems(hook):
    allowed, reason = hook.verdict(ALL_ALIVE, missing_bins=[], missing_tools=[],
                                   browser_problems=["плагин chrome-devtools выключен"])
    assert allowed is False
    assert "chrome-devtools" in reason


def test_verdict_lists_every_dead_channel(hook):
    probes = dict(ALL_ALIVE, jina=False, crossref=False)
    allowed, reason = hook.verdict(probes, missing_bins=["tesseract"], missing_tools=[])
    assert not allowed
    for word in ("r.jina.ai", "Crossref", "tesseract"):
        assert word in reason


def test_wayback_is_required(hook):
    """Послабление по Wayback оплачено: Г18 упёрся в него, Г23 не добыл ФССП, Г24 — PyCon."""
    assert "wayback" in hook.PROBES


def test_wayback_probe_uses_replay_not_service_api(hook):
    """Служебный API архива падает отдельно от отдачи снимков — проба по нему лжёт."""
    assert "web.archive.org/web/" in hook.PROBES["wayback"]
    assert "wayback/available" not in hook.PROBES["wayback"]
    allowed, reason = hook.verdict(dict(ALL_ALIVE, wayback=False), [], [])
    assert not allowed
    assert "Wayback" in reason


def test_semantic_scholar_probed_by_bulk_not_search(hook):
    """Замер Г31.4: `/paper/search` даёт 429 всегда, `search/bulk` — 200 без ключа.

    Прежняя проба по `/paper/search` объявила бы мёртвым весь канал, которым добыты
    три решающих источника (circularity, репликация Hagger, rank reversal).
    """
    assert "semanticscholar" in hook.PROBES
    assert "search/bulk" in hook.PROBES["semanticscholar"]
    assert hook.required_probes().get("semanticscholar")
    allowed, reason = hook.verdict(dict(ALL_ALIVE, semanticscholar=False), [], [])
    assert not allowed
    assert "Semantic Scholar" in reason


def test_probe_retries_once_before_declaring_channel_dead(hook, monkeypatch):
    """Одиночный троттлинг — шум, два отказа подряд с паузой — сигнал (замер 17.09.2026)."""
    calls = []
    monkeypatch.setattr(hook, "_probe_once", lambda name: calls.append(name) or (
        hook.ALIVE if len(calls) > 1 else hook.DEAD))
    monkeypatch.setattr(hook.time, "sleep", lambda s: None)
    assert hook.probe("semanticscholar") == hook.ALIVE
    assert len(calls) == 2


def test_probe_keeps_degradation_over_death(hook, monkeypatch):
    """Попытки 429 и 000 подряд — канал деградировал, а не умер: лучшее из увиденного."""
    answers = iter([hook.DEGRADED, hook.DEAD])
    monkeypatch.setattr(hook, "_probe_once", lambda name: next(answers))
    monkeypatch.setattr(hook.time, "sleep", lambda s: None)
    assert hook.probe("wayback") == hook.DEGRADED


def test_verdict_allows_when_all_alive(hook):
    assert hook.verdict(ALL_ALIVE, missing_bins=[], missing_tools=[]) == (True, "")


# --- поведение процесса-хука ------------------------------------------------------


def test_agent_allowed_when_everything_alive(tmp_path):
    assert run_hook(agent_payload(), tmp_path, ALL_ALIVE).returncode == 0


def test_agent_blocked_when_jina_dead(tmp_path):
    result = run_hook(agent_payload(), tmp_path, dict(ALL_ALIVE, jina=False))
    assert result.returncode == 2
    assert "r.jina.ai" in result.stderr


def test_any_agent_type_is_gated_on_channels(tmp_path):
    """Правило владельца — «никакой агент», не только исследователь."""
    result = run_hook(agent_payload("general-purpose"), tmp_path,
                      dict(ALL_ALIVE, openalex=False))
    assert result.returncode == 2


def test_researcher_without_bash_blocked(tmp_path):
    result = run_hook(agent_payload(), tmp_path, ALL_ALIVE,
                      tools_line=GOOD_TOOLS.replace("Bash, ", ""))
    assert result.returncode == 2
    assert "Bash" in result.stderr


def test_researcher_without_browser_blocked(tmp_path):
    no_browser = GOOD_TOOLS.split(f", {BROWSER}new_page")[0] + "\n"
    result = run_hook(agent_payload(), tmp_path, ALL_ALIVE, tools_line=no_browser)
    assert result.returncode == 2
    assert "new_page" in result.stderr


def test_any_agent_blocked_when_browser_plugin_disabled(tmp_path):
    """Браузер — канал добычи, как r.jina.ai: без него не стартует никакой агент."""
    result = run_hook(agent_payload("general-purpose"), tmp_path, ALL_ALIVE,
                      user_settings={"enabledPlugins": {}})
    assert result.returncode == 2
    assert "chrome-devtools" in result.stderr


def test_any_agent_blocked_when_research_plugin_disabled(tmp_path):
    settings = {"enabledPlugins": dict(PLUGIN_ON["enabledPlugins"],
                                       **{"context7@claude-plugins-official": False})}
    result = run_hook(agent_payload("general-purpose"), tmp_path, ALL_ALIVE,
                      user_settings=settings)
    assert result.returncode == 2
    assert "context7" in result.stderr


def test_any_agent_blocked_when_context7_dead(tmp_path):
    result = run_hook(agent_payload(), tmp_path, dict(ALL_ALIVE, context7=False))
    assert result.returncode == 2
    assert "Context7" in result.stderr


def test_any_agent_blocked_when_gh_not_authed(tmp_path):
    result = run_hook(agent_payload("general-purpose"), tmp_path, ALL_ALIVE, gh_authed=False)
    assert result.returncode == 2
    assert "gh auth" in result.stderr


def test_any_agent_blocked_when_chrome_missing(tmp_path):
    result = run_hook(agent_payload("general-purpose"), tmp_path, ALL_ALIVE,
                      chrome_present=False)
    assert result.returncode == 2
    assert "Chrome" in result.stderr


def test_researcher_definition_missing_blocked(tmp_path):
    assert run_hook(agent_payload(), tmp_path, ALL_ALIVE, tools_line=None).returncode == 2


def test_tools_line_not_checked_for_other_agent_types(tmp_path):
    result = run_hook(agent_payload("design-critic"), tmp_path, ALL_ALIVE, tools_line=None)
    assert result.returncode == 0


def test_missing_local_binary_blocks(tmp_path):
    empty_bin = tmp_path / "bin"
    empty_bin.mkdir()
    result = run_hook(agent_payload(), tmp_path, ALL_ALIVE, path_dirs=str(empty_bin))
    assert result.returncode == 2
    assert "pdftotext" in result.stderr


def test_other_tools_ignored(tmp_path):
    payload = {"hook_event_name": "PreToolUse", "tool_name": "Bash",
               "session_id": "s1", "tool_input": {"command": "ls"}}
    dead = {key: False for key in ALL_ALIVE}
    assert run_hook(payload, tmp_path, dead).returncode == 0


def test_garbage_stdin_does_not_crash():
    result = subprocess.run([sys.executable, str(HOOK)], input="not json",
                            capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"})
    assert result.returncode == 0


def test_hook_registered_on_agent():
    settings = json.loads((HOOK.parents[1] / "settings.json").read_text())
    entries = [entry for entry in settings["hooks"]["PreToolUse"]
               if entry.get("matcher") == "Agent"]
    commands = [h["command"] for entry in entries for h in entry["hooks"]]
    assert any("research-channels-gate.py" in command for command in commands)


def test_wayback_gets_its_own_longer_timeout(hook):
    """Замер 17.09.2026: replay архива отдаёт за 8-21 с, общий таймаут 12 с его рубит.

    Четыре пробы подряд: 200/14,9 с, 302/20,7 с, 302/20,6 с, 200/8,2 с. Канал жив,
    гейт объявлял его мёртвым по калибровке, а не по факту. Остальные каналы укладываются
    в 12 с, поднимать общий порог незачем - платить ожиданием за всех ради одного нельзя.
    """
    assert hook.probe_timeout("wayback") >= 25
    assert hook.probe_timeout("openalex") == hook.PROBE_TIMEOUT


def test_probe_command_carries_per_channel_timeout(hook, monkeypatch):
    """Свой таймаут должен доехать до curl, иначе он остаётся объявлением."""
    seen = {}

    def fake_run(command, **kwargs):
        seen["command"] = command
        seen["timeout"] = kwargs.get("timeout")

        class Result:
            stdout = "Example Domain\n200"

        return Result()

    monkeypatch.setattr(hook.subprocess, "run", fake_run)
    assert hook._probe_once("wayback") == hook.ALIVE
    assert str(hook.probe_timeout("wayback")) in seen["command"]
    assert seen["timeout"] > hook.probe_timeout("wayback")


# --- деградация канала против его смерти -------------------------------------
#
# 🔴 Замер 18.09.2026 (вахта J), оплачен остановкой всей очереди на теме Г58.
# Гейт объявил мёртвыми `r.jina.ai` и Wayback и не пустил агента. Проход по лестнице
# каналов показал другое:
#   - `r.jina.ai` → 401, дословно: "You have been blocked from performing anonymous
#     queries due to bad network reputation (AS9009). Please authenticate.";
#   - `archive.org` и `web.archive.org` → 429 на всех эндпоинтах, три попытки подряд;
#   - в БРАУЗЕРЕ оба открылись с первого раза: Wayback отдал снимок `cbr.ru`
#     `20260918004518`, `r.jina.ai` — полный текст той же страницы.
# Заблокирован не канал, а ОДИН способ к нему ходить — анонимный `curl` с нашего
# выхода. Это ровно ошибка, названная аудитом № 6: «почти всё, что мы записывали
# как свойство источника, было свойством нашего канала».
#
# Послабление намеренно узкое: деградацией считаются ТОЛЬКО 401 и 429 — коды, которые
# называют репутацию и троттлинг, а не содержимое. Всё остальное (000, таймаут, 403,
# 5xx, 200 без признака) остаётся смертью и по-прежнему запрещает запуск: гейты снимали
# дважды, и оба раза это стоило суток работы.


def test_reputation_block_is_degradation_not_death(hook):
    """401 «bad network reputation» — канал жив, закрыт анонимный curl."""
    body = ('{"code":401,"name":"AuthenticationRequiredError","message":"You have been '
            'blocked from performing anonymous queries due to bad network reputation '
            '(AS9009). Please authenticate."}')
    assert hook.classify("jina", 401, body) == hook.DEGRADED


def test_rate_limit_is_degradation_not_death(hook):
    """429 архива — троттлинг нашего адреса, а не поломка Wayback."""
    assert hook.classify("wayback", 429, "") == hook.DEGRADED


@pytest.mark.parametrize("status,body", [
    (0, ""), (403, "Forbidden"), (503, ""), (200, "мимо признака"),
])
def test_everything_else_stays_death(hook, status, body):
    """Послабление узкое: смертью остаётся всё, кроме 401 и 429."""
    assert hook.classify("wayback", status, body) == hook.DEAD


def test_alive_needs_code_and_marker(hook):
    assert hook.classify("wayback", 200, "Example Domain") == hook.ALIVE


def test_degraded_channel_does_not_block_agent(tmp_path):
    """Канал, живой в браузере, не имеет права останавливать очередь."""
    result = run_hook(agent_payload(), tmp_path, dict(ALL_ALIVE, jina="degraded"))
    assert result.returncode == 0


def test_degraded_channel_is_named_loudly(tmp_path):
    """Цена молчания замерена (PIT-213): деградация обязана быть названа, не проглочена."""
    degraded = dict(ALL_ALIVE, jina="degraded", wayback="degraded")
    result = run_hook(agent_payload(), tmp_path, degraded)
    loud = result.stdout + result.stderr
    assert "r.jina.ai" in loud and "Wayback" in loud
    assert "браузер" in loud.lower()


def test_dead_channel_still_blocks_next_to_degraded(tmp_path):
    """Деградация не прикрывает смерть: мёртвый канал запрещает запуск и рядом с ней."""
    result = run_hook(agent_payload(), tmp_path,
                      dict(ALL_ALIVE, jina="degraded", openalex=False))
    assert result.returncode == 2
    assert "OpenAlex" in result.stderr


def test_all_channels_degraded_blocks(tmp_path):
    """Если анонимный доступ закрыт ВЕЗДЕ, это уже не деградация, а мёртвая сеть."""
    everywhere = {name: "degraded" for name in ALL_ALIVE}
    result = run_hook(agent_payload(), tmp_path, everywhere)
    assert result.returncode == 2


def test_boolean_probe_values_still_understood(hook):
    """Старая форма замера (True/False) читается как жив/мёртв — совместимость проб."""
    assert hook.normalize({"jina": True, "wayback": False}) == {
        "jina": hook.ALIVE, "wayback": hook.DEAD}
