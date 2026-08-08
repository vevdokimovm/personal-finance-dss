"""Разбор stdin-конверта хука Claude Code.

Данные приходят JSON на stdin, не через env: переменные $CLAUDE_TOOL_INPUT_*
приходят пустыми (баг anthropics/claude-code#9567).

Python вместо jq намеренно: jq не гарантирован на машине, а его отсутствие
заставляло блокирующие хуки молча пропускать всё (fail-open). Python 3.12 —
и так жёсткая зависимость проекта.
"""

import json
import sys


def field(path: str, default: str = "") -> str:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(2)  # fail-closed: непонятный вход блокируется, а не пропускается
    node = data
    for key in path.split("."):
        if not isinstance(node, dict):
            return default
        node = node.get(key)
        if node is None:
            return default
    return str(node)


if __name__ == "__main__":
    sys.stdout.write(field(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ""))
