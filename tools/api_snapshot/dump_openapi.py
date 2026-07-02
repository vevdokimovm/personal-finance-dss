"""Dump the FastAPI OpenAPI schema to docs/api/openapi.json.

Run from repo root inside the project venv:
    python tools/api_snapshot/dump_openapi.py

The snapshot is a fixed contract point for the frontend (milestone 6):
regenerate it in every batch that changes routes or schemas, review the diff.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = REPO_ROOT / "docs" / "api" / "openapi.json"


def main() -> int:
    sys.path.insert(0, str(REPO_ROOT))
    from app.main import app  # noqa: PLC0415  (import after sys.path tweak)

    schema = app.openapi()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    n_paths = len(schema.get("paths", {}))
    print(f"OpenAPI snapshot: {n_paths} paths -> {OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
