#!/usr/bin/env python3
"""Блокирует команду, которая заставит харнесс СПРОСИТЬ владельца (PIT-018).

В `.claude/settings.json` настроены `deny`-правила `Read(./.env)` и подобные. Чтобы
решить, попадает ли команда под запрет, харнесс должен знать, КАКОЙ файл она откроет.
Относительный путь-аргумент он сопоставить не может: рабочий каталог команды статически
неизвестен. Разрешить не вправе, отказать молча — тоже, поэтому спрашивает владельца:

    grep on 'docs/pitfalls.md' after a cd would search a directory that cannot be
    determined here, and a Read() deny rule is configured; only you can approve
    running it anyway.  Do you want to proceed?

Снаружи диалог неотличим от вопроса, заданного вахтой, и в авто-режиме читается как
нарушение прямого приказа «не спрашивать». За сессию 04.09.2026 — больше десяти раз.

Значение имеет путь В АРГУМЕНТЕ читающей утилиты, а не путь у `cd`. Первый диагноз назвал
корнем `cd` с относительным путём; обход «делать `cd` абсолютным» соблюдался и не помогал —
следующий вопрос прилетел на команде с абсолютным `cd`. Правило, выведенное из неверного
корня, выглядит соблюдённым и не защищает, поэтому мера здесь машинная. `cd` для
не-читающих команд (`npx`, `npm`, `python -m`) вопроса не вызывает и не трогается.
"""
from __future__ import annotations

import json
import re
import shlex
import sys

READERS = {
    "grep", "egrep", "fgrep", "rg", "cat", "bat", "head", "tail", "sed", "awk",
    "less", "more", "wc", "diff", "nl", "cut", "sort", "uniq", "jq", "yq", "xxd", "od",
}
FILE_SUFFIX = re.compile(
    r"\.(md|py|ts|tsx|js|jsx|json|css|html|txt|xml|ya?ml|toml|cfg|ini|sh|sql|log)$"
)
OPERATORS = {"&&", "||", "|", ";"}


def segments(command: str) -> list[list[str]]:
    """Команда, разбитая на сегменты С УЧЁТОМ КАВЫЧЕК.

    Первая редакция резала строку регуляркой до разбора кавычек — и команда
    `echo '{"command":"cd /abs && grep -n x docs/f.md"}'` разваливалась на два
    сегмента, второй из которых выглядел вызовом `grep`. Хук блокировал `echo`
    с JSON внутри, то есть собственную проверочную команду. Разбор идёт по ТОКЕНАМ:
    оператор внутри кавычек токеном-оператором не является.
    """
    padded = re.sub(r"(\|\||&&|[|;])", r" \1 ", command)
    try:
        tokens = shlex.split(padded, posix=False)
    except ValueError:
        return []
    result: list[list[str]] = [[]]
    for token in tokens:
        if token in OPERATORS:
            result.append([])
        else:
            result[-1].append(token)
    return [seg for seg in result if seg]


def offending_paths(command: str) -> list[str]:
    """Относительные пути-аргументы у читающих утилит.

    Аргументы в кавычках пропускаются: это шаблон поиска, а не файл — в
    `grep -n "^## " docs/x.md` путь только второй.
    """
    found: list[str] = []
    for parts in segments(command):
        if parts[0].rsplit("/", 1)[-1] not in READERS:
            continue
        for arg in parts[1:]:
            if arg.startswith("-") or arg[:1] in {'"', "'", "$"}:
                continue
            if arg.startswith("/"):
                continue
            if "/" in arg or FILE_SUFFIX.search(arg):
                found.append(arg)
    return found


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    bad = offending_paths((payload.get("tool_input") or {}).get("command", ""))
    if not bad:
        return 0
    print(
        "PIT-018: relative path given to a reading utility: "
        + ", ".join(sorted(set(bad)))
        + ".\nThe harness cannot match it against Read() deny rules and WILL ASK the "
        "owner; questions are forbidden by direct order.\n"
        "Rewrite the argument as an absolute path from the repository root. "
        "An absolute `cd` does not help: what matters is the path in the ARGUMENT.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
