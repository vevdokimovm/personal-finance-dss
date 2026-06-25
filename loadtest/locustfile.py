"""
Нагрузочный сценарий FINPILOT (P0.4).

Гоняет реалистичную смесь запросов гостя по демо-данным: дашборд, быстрая
рекомендация (кэш) и полный расчёт СППР (Monte Carlo — самый дорогой путь).

Запуск (headless):
    locust -f loadtest/locustfile.py --host http://127.0.0.1:8000 \
        --headless -u 100 -r 20 -t 30s --csv /tmp/finpilot_load

Демо-данные привязаны к гостю (user_id=None) и общие для всех виртуальных
пользователей, поэтому грузятся один раз на старте теста.
"""
import os

from locust import HttpUser, between, events, task

API = os.getenv("API_PREFIX", "/api")
DEMO_CASE = os.getenv("DEMO_CASE", "anna")


@events.test_start.add_listener
def _preload_demo(environment, **_kwargs) -> None:
    """Один раз заливает демо-кейс гостю до начала нагрузки."""
    import requests

    url = f"{environment.host}{API}/demo/load?case={DEMO_CASE}"
    try:
        resp = requests.post(url, timeout=15)
        print(f"[setup] demo/load case={DEMO_CASE}: HTTP {resp.status_code}")
    except Exception as exc:  # noqa: BLE001
        print(f"[setup] demo preload failed: {exc}")


class FinpilotGuest(HttpUser):
    wait_time = between(0.1, 0.6)

    @task(1)
    def health(self) -> None:
        self.client.get("/health", name="GET /health")

    @task(3)
    def dashboard(self) -> None:
        self.client.get("/dashboard", name="GET /dashboard")

    @task(4)
    def recommendation(self) -> None:
        self.client.post(f"{API}/recommendation", json={}, name="POST /api/recommendation")

    @task(2)
    def calculate(self) -> None:
        self.client.post(f"{API}/planning/calculate", json={}, name="POST /api/planning/calculate")
