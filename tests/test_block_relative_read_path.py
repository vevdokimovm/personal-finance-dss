"""Хук против диалогов разрешения работает и не мешает работе (PIT-018, v8.43.0).

Хук `.claude/hooks/block-relative-read-path.py` блокирует команду, в которой читающая
утилита получает относительный путь-аргумент: харнесс не может сопоставить такой путь
с `deny`-правилами `Read()` и эскалирует вопрос владельцу, а диалог внешне неотличим
от вопроса, заданного вахтой.

🔴 Тест нужен не «для покрытия». Первая редакция хука резала команду по `&&` регуляркой
ДО разбора кавычек — и блокировала `echo '{"command":"... && grep -n x docs/f.md"}'`,
то есть собственную проверочную команду. Дефект нашёлся ровно в тот момент, когда хук
впервые применили к живой строке; здесь он зафиксирован, чтобы не вернулся.

Ложное срабатывание здесь дороже пропуска: пропущенная команда стоит одного диалога,
а хук, блокирующий исправные команды, делает работу невозможной и будет снят.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "block-relative-read-path.py"


@pytest.fixture(scope="module")
def hook():
    spec = importlib.util.spec_from_file_location("block_relative_read_path", HOOK)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


BLOCKED = [
    ('cd /abs && grep -n "x" docs/pitfalls.md', "относительный путь после абсолютного cd"),
    ("grep -rn pattern src/pages", "относительный каталог"),
    ("cat CHANGELOG.md", "относительный файл без слэша, опознан по расширению"),
    ("uptime && tail -20 out.log", "второй сегмент цепочки"),
]

ALLOWED = [
    ("grep -n x /abs/docs/pitfalls.md", "абсолютный путь"),
    ("cd frontend && npx vitest run", "npx не читающая утилита"),
    ('grep -n "docs/x.md" /abs/f.md', "путь внутри кавычек — это шаблон, не файл"),
    ("uptime", "нет путей вовсе"),
    ('echo \'{"command":"cd /abs && grep -n x docs/f.md"}\'', "оператор внутри кавычек"),
    ("grep -rn pattern $CLAUDE_PROJECT_DIR/docs", "путь через переменную окружения"),
    ("grep -rn x /abs/f.md 2>/dev/null", "перенаправление stderr, а не аргумент"),
    ("grep -rn x /abs/f.md > out.log", "перенаправление stdout"),
    (
        "cat > /abs/f.css <<'EOF'\n/* ритм */\n.a { margin: 0 }\nEOF",
        "тело heredoc — данные, а не команда",
    ),
    (
        "cat > /abs/f.sh <<'EOF'\ngrep -n x docs/pitfalls.md\nEOF",
        "команда ВНУТРИ heredoc не выполняется сейчас",
    ),
]


@pytest.mark.parametrize("command,why", BLOCKED, ids=[w for _, w in BLOCKED])
def test_blocks(hook, command, why) -> None:
    assert hook.offending_paths(command), f"пропущено, хотя {why}: {command}"


@pytest.mark.parametrize("command,why", ALLOWED, ids=[w for _, w in ALLOWED])
def test_allows(hook, command, why) -> None:
    """Ложное срабатывание делает хук неработоспособным — он будет снят целиком."""
    assert not hook.offending_paths(command), f"ложно заблокировано ({why}): {command}"


def test_hook_is_executable() -> None:
    """🔴 Без бита `+x` хук не исполняется — и падения при этом НЕ будет.

    Худший вид отказа: код на месте, регистрация на месте, вердикт «зелено» означает
    «не проверялось». Бит слетел на этой же неделе, когда файл перезаписали целиком
    после `chmod` — нашла соседняя вахта по своему `system_status.py`, не этот гейт.
    Родня PIT-017 (гейт, заявленный как проверяющий X, обязан фактически проверять X).
    """
    assert os.access(HOOK, os.X_OK), (
        f"{HOOK.name} без бита исполнения: PreToolUse его не запустит, "
        f"и защита будет молча отсутствовать. Починка: chmod +x"
    )


def test_hook_is_registered() -> None:
    """Файл на диске без записи в settings.json не выполняется ВООБЩЕ.

    Гейт, существующий только файлом, — это обещание, а не механизм (PIT-017: гейт,
    заявленный как проверяющий X, обязан фактически проверять X).
    """
    import json

    settings = json.loads(
        (Path(__file__).resolve().parents[1] / ".claude" / "settings.json").read_text(
            encoding="utf-8"
        )
    )
    commands = [
        hook["command"]
        for group in settings["hooks"]["PreToolUse"]
        if group.get("matcher") == "Bash"
        for hook in group["hooks"]
    ]
    assert any("block-relative-read-path.py" in c for c in commands), (
        "хук не зарегистрирован в PreToolUse/Bash — на диске лежит, но не работает"
    )
