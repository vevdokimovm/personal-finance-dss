"""Тест импорта большой банковской выписки (батчевая вставка).

Корень бага: одиночный commit тысяч строк строит гигантский INSERT и роняет
воркер по таймауту. Тест проверяет, что импорт большого файла сохраняет все
операции (защита логики батчинга от регрессий). Написан до фикса (TDD).
"""
from __future__ import annotations

import io

from fastapi.testclient import TestClient


def _make_large_csv(rows: int) -> str:
    lines = ["Дата операции;Сумма операции;Категория;Описание;MCC"]
    for i in range(rows):
        day = (i % 28) + 1
        amount = -(100 + i % 900)  # расходы
        lines.append(f"{day:02d}.06.2025;{amount};Покупки;Магазин {i};5411")
    return "\n".join(lines)


def test_large_statement_import_saves_all(client: TestClient) -> None:
    rows = 3000
    csv_content = _make_large_csv(rows)
    files = {"file": ("statement.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    resp = client.post("/api/banks/upload", files=files, data={"bank_id": "universal"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"
    assert body["added_count"] == rows

    # Все операции реально в БД
    txns = client.get("/api/transactions").json()
    assert len(txns) >= rows
