"""Фикстуры для браузерных E2E-тестов (Playwright).

Поднимают реальный экземпляр приложения через uvicorn в отдельном процессе с
изолированной временной БД, ждут готовности и отдают base_url. pytest-playwright
сам предоставляет фикстуру `page`; `base_url` подхватывается pytest-base-url,
поэтому в тестах работает page.goto("/").

Браузер для прогона ставится отдельно: `playwright install chromium`.
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
        "SECRET_KEY": "test-secret-key-for-e2e",
        "DATABASE_URL": f"sqlite:///{db_path}",
        # Браузер E2E ходит на динамический порт — кладём его origin в CORS,
        # иначе CSRFMiddleware режет браузерные POST (recommendation и пр.) как чужой origin.
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
        raise RuntimeError("E2E live server failed to start")

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


@pytest.fixture
def seeded(base_url: str) -> str:
    """Загружает демо-данные в приложение перед тестом (через публичный API)."""
    request = urllib.request.Request(base_url + "/api/demo/load", method="POST")
    urllib.request.urlopen(request, timeout=15)
    return base_url


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, browser_type):
    """Флаги запуска chromium для контейнеров/CI, где browser-sandbox недоступен,
    а /dev/shm мал. Применяются только к chromium (webkit их не понимает)."""
    if browser_type.name == "chromium":
        return {
            **browser_type_launch_args,
            "args": ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        }
    return browser_type_launch_args
