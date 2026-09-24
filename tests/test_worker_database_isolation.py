"""Гейт: у каждого параллельного воркера своя база.

🔴 Замер 24.09.2026. `pytest -n 8` падал с `table transactions already exists`:
`conftest` кладёт адрес временной базы в `os.environ`, а воркеры `xdist` — дочерние
процессы, которые ЭТО ОКРУЖЕНИЕ НАСЛЕДУЮТ. Условие «создать базу, если `DATABASE_URL`
не задан» у них не срабатывало, и восемь воркеров одновременно создавали схему в одном
файле. Из-за этого параллельный прогон был невозможен, а полный бэкенд шёл 26 минут
вместо примерно семи.

Изоляция трогает ТОЛЬКО SQLite: адрес PostgreSQL, заданный снаружи для матрицы СУБД,
остаётся как есть — там параллель решается отдельно и не подменой пути.
"""
from __future__ import annotations

from tests.db_url import worker_database_url


class TestSqliteIsolatedPerWorker:
    """Каждому воркеру — свой файл базы."""

    def test_master_url_is_untouched(self) -> None:
        url = "sqlite:////tmp/test_abc.db"
        assert worker_database_url(url, None) == url

    def test_master_token_is_untouched(self) -> None:
        """`xdist` зовёт мастера `master` — он гоняет тесты сам, когда воркеров нет."""
        url = "sqlite:////tmp/test_abc.db"
        assert worker_database_url(url, "master") == url

    def test_each_worker_gets_its_own_file(self) -> None:
        url = "sqlite:////tmp/test_abc.db"
        first = worker_database_url(url, "gw0")
        second = worker_database_url(url, "gw1")
        assert first != second
        assert first != url and second != url
        assert first.startswith("sqlite:////tmp/test_abc") and first.endswith(".db")

    def test_same_worker_is_stable(self) -> None:
        url = "sqlite:////tmp/test_abc.db"
        assert worker_database_url(url, "gw3") == worker_database_url(url, "gw3")


class TestNonSqliteUntouched:
    """Внешняя СУБД адресом не подменяется."""

    def test_postgres_url_is_untouched(self) -> None:
        url = "postgresql+psycopg2://finpilot:pass@db:5432/finpilot"
        assert worker_database_url(url, "gw0") == url

    def test_postgres_async_url_is_untouched(self) -> None:
        url = "postgresql+asyncpg://finpilot:pass@db:5432/finpilot"
        assert worker_database_url(url, "gw2") == url
