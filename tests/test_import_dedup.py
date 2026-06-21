"""Надёжность импорта выписок (P2.1).

Повторная загрузка той же выписки не должна задваивать транзакции (иначе аналитика
искажается). Также: дубли внутри одного файла отсекаются, размер файла ограничен,
отчёт показывает сколько добавлено и сколько пропущено.
"""
from __future__ import annotations

import io

from fastapi.testclient import TestClient

_CSV = "Дата;Сумма;Описание\n01.06.2026;-1000;Кофе\n02.06.2026;5000;Зарплата\n"


def _upload(client: TestClient, content: str, bank: str = "universal"):
    files = {"file": ("statement.csv", io.BytesIO(content.encode("utf-8")), "text/csv")}
    return client.post("/api/banks/upload", files=files, data={"bank_id": bank})


class TestImportDeduplication:
    def test_reimport_skips_duplicates(self, client: TestClient) -> None:
        first = _upload(client, _CSV)
        assert first.json()["added_count"] == 2

        second = _upload(client, _CSV)
        body = second.json()
        assert body["added_count"] == 0
        assert body["skipped_duplicates"] == 2

    def test_duplicates_within_file_skipped(self, client: TestClient) -> None:
        dup = "Дата;Сумма;Описание\n01.06.2026;-1000;Кофе\n01.06.2026;-1000;Кофе\n"
        body = _upload(client, dup).json()
        assert body["added_count"] == 1
        assert body["skipped_duplicates"] == 1

    def test_report_includes_skipped(self, client: TestClient) -> None:
        body = _upload(client, _CSV).json()
        assert "skipped_duplicates" in body

    def test_new_rows_still_added_after_reimport(self, client: TestClient) -> None:
        _upload(client, _CSV)
        extended = _CSV + "03.06.2026;-2000;Такси\n"
        body = _upload(client, extended).json()
        assert body["added_count"] == 1          # только новая строка
        assert body["skipped_duplicates"] == 2   # две прежние


class TestUploadSizeLimit:
    def test_oversized_file_rejected(self, client: TestClient) -> None:
        big = "x" * (11 * 1024 * 1024)  # 11 MB — больше лимита
        body = _upload(client, big).json()
        assert body["status"] == "error"
