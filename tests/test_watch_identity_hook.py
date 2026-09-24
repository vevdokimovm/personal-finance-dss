"""Гейт вахты: какая вахта (аккаунт) идёт сейчас — механизмом, а не памятью.

**Жалоба владельца 16.09.2026, дословно:** «у тебя опять не работает гейт на чек какая
вахта сейчас». Вахта в тот же день записала в WATCHLOG «V → S → M» по догадке.

**Причина — две дыры сразу.**
1. `watch-identity.sh` зарегистрирован только в `base-repo`; в этом проекте его не было
   вовсе, а искать реестр вахт он умел только относительно `CLAUDE_PROJECT_DIR`.
2. Он висел только на `SessionStart`, а `/login` меняет аккаунт ПОСРЕДИ сессии
   (16.09.2026 — три смены за день). Теперь он же стоит на `UserPromptSubmit`
   с `--on-change`: молчит, пока почта та же, и говорит в первый же ход после смены.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from tests.support.workstation import requires_base_repo_hooks

# 🔴 Хук живёт в каноне `base-repo`, а не в этом репозитории: на раннере CI его нет
# по построению, и красный там означал «нет машины владельца», а не «гейт сломан».
# Пропуск ИМЕНОВАННЫЙ — `pytest -rs` печатает причину (см. `tests/support/workstation.py`).
pytestmark = requires_base_repo_hooks

HOOK = Path.home() / "repos" / "base-repo" / ".claude" / "hooks" / "watch-identity.sh"
SETTINGS = Path(__file__).resolve().parents[1] / ".claude" / "settings.json"

REGISTRY = """| Вахта | Имя | Почта |
|---|---|---|
| **V** | **Vasilii** | `vevdokimovm@gmail.com` |
| **J** | **Jesus** | `vevdokimovm3@proton.me` |
| **M** | Michael | `gertab95@proton.me` — см. ниже |
| 🟢 **A** | **Adam** | `finpilot.support@proton.me` |
"""


def run(tmp: Path, email: str, *args: str) -> str:
    home = tmp / "home"
    home.mkdir(exist_ok=True)
    (home / ".claude.json").write_text(json.dumps({"oauthAccount": {"emailAddress": email}}))
    registry = tmp / "84-claude-accounts.md"
    registry.write_text(REGISTRY)
    result = subprocess.run(
        ["bash", str(HOOK), *args],
        capture_output=True,
        text=True,
        env={
            "PATH": "/usr/bin:/bin:/usr/local/bin",
            "HOME": str(home),
            "CLAUDE_PROJECT_DIR": str(tmp / "some-project"),
            "WATCH_MAP_FILE": str(registry),
            "WATCH_STATE_DIR": str(tmp / "state"),
        },
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def test_letter_found_outside_base_repo(tmp_path):
    assert "Вахта этой сессии: V (vevdokimovm@gmail.com)" in run(tmp_path, "vevdokimovm@gmail.com")


def test_every_registry_letter_resolves(tmp_path):
    cases = {"vevdokimovm3@proton.me": "J", "gertab95@proton.me": "M",
             "finpilot.support@proton.me": "A"}
    for email, letter in cases.items():
        assert f"Вахта этой сессии: {letter}" in run(tmp_path, email)


def test_unknown_email_is_not_guessed(tmp_path):
    out = run(tmp_path, "stranger@example.com")
    assert "НЕ ОПОЗНАНА" in out


def test_on_change_silent_when_same_account(tmp_path):
    run(tmp_path, "vevdokimovm@gmail.com")
    assert run(tmp_path, "vevdokimovm@gmail.com", "--on-change") == ""


def test_on_change_speaks_after_login(tmp_path):
    run(tmp_path, "gertab95@proton.me")
    out = run(tmp_path, "vevdokimovm@gmail.com", "--on-change")
    assert "Вахта этой сессии: V" in out
    assert "СМЕНИЛАСЬ" in out
    assert "gertab95@proton.me" in out


def test_on_change_speaks_on_first_prompt(tmp_path):
    assert "Вахта этой сессии: A" in run(tmp_path, "finpilot.support@proton.me", "--on-change")


def test_registered_on_session_start_and_every_prompt():
    hooks = json.loads(SETTINGS.read_text())["hooks"]

    def commands(event: str) -> list[str]:
        return [h["command"] for entry in hooks.get(event, []) for h in entry["hooks"]]

    assert any("watch-identity.sh" in c for c in commands("SessionStart"))
    assert any("watch-identity.sh" in c and "--on-change" in c
               for c in commands("UserPromptSubmit"))
