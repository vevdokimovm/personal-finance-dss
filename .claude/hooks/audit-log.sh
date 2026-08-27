#!/bin/bash
# PostToolUse: аудит действий агента (152-ФЗ).
set -uo pipefail
H="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="${CLAUDE_PROJECT_DIR:-.}"
mkdir -p "$root/logs"
cat | python3 -c '
import json, sys, datetime
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
ti = d.get("tool_input") or {}
rec = {
    "ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "session": d.get("session_id"),
    "event": d.get("hook_event_name"),
    "tool": d.get("tool_name"),
    "path": ti.get("file_path") or ti.get("notebook_path"),
    "cmd": ti.get("command"),
}
print(json.dumps(rec, ensure_ascii=False))
' >> "$root/logs/agent-audit.jsonl" 2>/dev/null
exit 0
