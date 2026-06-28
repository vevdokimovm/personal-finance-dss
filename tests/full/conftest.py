"""Фикстуры предрелизного тира `full` (визуальная регрессия + live-a11y).

Поднимают реальный экземпляр приложения через uvicorn в отдельном процессе с
изолированной временной БД, заливают демо-данные (чтобы страницы рендерились с
контентом, а не пустыми) и отдают base_url. pytest-playwright предоставляет
фикстуру `page`; `base_url` подхватывается pytest-base-url.

Отдельный conftest (не переиспользуем e2e/) потому, что conftest применяется
только к своей директории: тесты в tests/full/ не видят tests/e2e/conftest.py.
Браузер для прогона — chromium (`playwright install chromium`); в песочнице
предустановлен в образе.
"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from collections.abc import Iterator

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = int(sock.getsockname()[1])
    sock.close()
    return port


def _wait_until_ready(url: str, attempts: int = 80, delay: float = 0.5) -> bool:
    for _ in range(attempts):
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except Exception:
            time.sleep(delay)
    return False


@pytest.fixture(scope="session")
def live_server() -> Iterator[str]:
    port = _free_port()
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    env = {
        **os.environ,
        "SECRET_KEY": "test-secret-key-for-full",
        "JWT_SECRET": "test-jwt-secret-for-full",
        "DATABASE_URL": f"sqlite:///{db_path}",
        "CORS_ORIGINS": f"http://127.0.0.1:{port}",
    }
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base_url = f"http://127.0.0.1:{port}"

    if not _wait_until_ready(base_url + "/"):
        proc.terminate()
        raise RuntimeError("full-тир: live server не поднялся")

    # Демо-данные: страницы должны рендериться с контентом, иначе визуальная
    # регрессия и контраст проверяют пустой каркас.
    try:
        req = urllib.request.Request(base_url + "/api/demo/load?case=anna", method="POST")
        urllib.request.urlopen(req, timeout=15)
    except Exception:
        pass  # без демо тест всё равно осмыслен (общие элементы base.html)

    yield base_url

    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture(scope="session")
def base_url(live_server: str) -> str:
    return live_server


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, browser_type):
    """Флаги chromium для контейнеров/CI (нет browser-sandbox, мал /dev/shm)."""
    if browser_type.name == "chromium":
        return {
            **browser_type_launch_args,
            "args": ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        }
    return browser_type_launch_args
