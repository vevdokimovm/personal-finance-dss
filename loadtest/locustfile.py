"""
Нагрузочный сценарий FINPILOT (P0.4) — прод-уровень.

Гоняет реалистичную смесь запросов, приближённую к продакшену: преобладание
READ-операций (просмотр дашборда, списков, истории) над тяжёлыми расчётами СППР
(Monte-Carlo). Два класса пользователей:

  - FinpilotGuest               — гость по общим демо-данным (анонимный режим);
  - FinpilotAuthenticatedUser   — зарегистрированный пользователь со своим JWT,
                                   изолированными данными и полным CRUD-флоу.

В проде смесь смещена в read-heavy: на каждый дорогой `calculate` приходится
много дешёвых просмотров. Веса @task ниже это отражают.

────────────────────────────────────────────────────────────────────────────
ЗАПУСК

Smoke (песочница, базовая проверка):
    locust -f loadtest/locustfile.py --host http://127.0.0.1:8000 \
        --headless -u 50 -r 10 -t 30s --csv /tmp/finpilot_load

Прод-профиль (характеризация пропускной способности на VPS):
    # rate-limit отключается, иначе тест меряет ЗАЩИТУ, а не throughput:
    RATE_LIMIT_REQUESTS=100000000 (в .env приложения на стенде)
    locust -f loadtest/locustfile.py --host https://<vps> \
        --headless -u 500 -r 50 -t 5m --csv /tmp/finpilot_prod

Веб-UI (интерактивно, для ступенчатого ramp):
    locust -f loadtest/locustfile.py --host http://127.0.0.1:8000

────────────────────────────────────────────────────────────────────────────
RATE-LIMIT И ТРАКТОВКА 429

Чувствительные эндпоинты под `RateLimitMiddleware` (по умолчанию 30 req / 60s на
IP+путь). При нагрузке с ОДНОГО IP лимит срабатывает закономерно и отдаёт 429 —
это корректная работа защиты, НЕ сбой. Поэтому запросы к лимитируемым путям
помечают 429 как ожидаемый ответ (`catch_response`), и он не засчитывается в
failures. Для чистого замера пропускной способности лимит на стенде поднимают
переменной `RATE_LIMIT_REQUESTS` (см. прод-профиль) — тогда 429 не возникает.

────────────────────────────────────────────────────────────────────────────
SLA-ОРИЕНТИРЫ (цель для прод-стенда, сверяются боевым прогоном)

  GET-страницы / списки:   p95 < 200 мс
  POST /recommendation:    p95 < 300 мс (кэш TTL по отпечатку входа)
  POST /calculate:         p95 < 900 мс (Monte-Carlo — самый дорогой путь)
  failures (вне 429):      < 0.5%

Базовый baseline в песочнице (smoke): ~110 RPS @ 60u, бутылочное горло —
`calculate`; боевые числа снимаются на VPS тем же сценарием.
"""
import os
import uuid

from locust import HttpUser, between, events, task

API = os.getenv("API_PREFIX", "/api")
DEMO_CASE = os.getenv("DEMO_CASE", "anna")

# Пути под rate-limit (см. RATE_LIMITED_PREFIXES в app/main.py): 429 на них —
# ожидаемое поведение защиты, а не сбой.
RATE_LIMITED = (f"{API}/recommendation", f"{API}/planning/calculate",
                f"{API}/planning/forecast", f"{API}/auth/")


def _is_rate_limited_path(path: str) -> bool:
    return any(path.startswith(p) for p in RATE_LIMITED)


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


class _Tolerant429Mixin:
    """Хелперы запросов, трактующие 429 на лимитируемых путях как успех."""

    def _get(self, path: str, **kw) -> None:
        with self.client.get(path, name=kw.pop("name", path),
                             catch_response=True, **kw) as resp:
            if resp.status_code == 429 and _is_rate_limited_path(path):
                resp.success()
            elif resp.status_code >= 400:
                resp.failure(f"HTTP {resp.status_code}")
            else:
                resp.success()

    def _post(self, path: str, json: dict | None = None, **kw) -> None:
        with self.client.post(path, json=json or {}, name=kw.pop("name", path),
                              catch_response=True, **kw) as resp:
            if resp.status_code == 429 and _is_rate_limited_path(path):
                resp.success()
            elif resp.status_code >= 400:
                resp.failure(f"HTTP {resp.status_code}")
            else:
                resp.success()


class FinpilotGuest(_Tolerant429Mixin, HttpUser):
    """Анонимный пользователь по общим демо-данным. Read-heavy смесь."""

    weight = 3
    wait_time = between(0.1, 0.6)

    # ── READ (преобладают) ──────────────────────────────────────────────
    @task(8)
    def dashboard(self) -> None:
        self._get("/dashboard", name="GET /dashboard")

    @task(5)
    def transactions(self) -> None:
        self._get(f"{API}/transactions", name="GET /api/transactions")

    @task(4)
    def goals(self) -> None:
        self._get(f"{API}/goals", name="GET /api/goals")

    @task(4)
    def obligations(self) -> None:
        self._get(f"{API}/obligations", name="GET /api/obligations")

    @task(3)
    def liquid_assets(self) -> None:
        self._get(f"{API}/liquid-assets", name="GET /api/liquid-assets")

    @task(3)
    def history(self) -> None:
        self._get(f"{API}/planning/history", name="GET /api/planning/history")

    @task(2)
    def budgets(self) -> None:
        self._get(f"{API}/budgets", name="GET /api/budgets")

    @task(2)
    def fx_rates(self) -> None:
        self._get(f"{API}/fx/rates", name="GET /api/fx/rates")

    @task(2)
    def spending_advice(self) -> None:
        self._get(f"{API}/planning/spending-advice", name="GET /api/planning/spending-advice")

    @task(1)
    def health(self) -> None:
        self._get("/health", name="GET /health")

    # ── WRITE / расчёты (дороже, реже) ──────────────────────────────────
    @task(4)
    def recommendation(self) -> None:
        self._post(f"{API}/recommendation", name="POST /api/recommendation")

    @task(2)
    def calculate(self) -> None:
        self._post(f"{API}/planning/calculate", name="POST /api/planning/calculate")

    @task(1)
    def forecast(self) -> None:
        self._post(f"{API}/planning/forecast", name="POST /api/planning/forecast")


class FinpilotAuthenticatedUser(_Tolerant429Mixin, HttpUser):
    """Зарегистрированный пользователь: свой JWT, изолированные данные.

    Каждый виртуальный пользователь на старте регистрируется уникальным email,
    получает токен и дальше ходит с `Authorization: Bearer`. Это прод-реалистичный
    профиль (большинство активных пользователей авторизованы).
    """

    weight = 1
    wait_time = between(0.2, 0.8)

    def on_start(self) -> None:
        email = f"load_{uuid.uuid4().hex[:12]}@example.com"
        payload = {"email": email, "password": "loadtest-pass-1", "display_name": "Load"}
        with self.client.post(f"{API}/auth/register", json=payload,
                              name="POST /api/auth/register", catch_response=True) as resp:
            if resp.status_code == 429:
                resp.success()  # лимит на auth — ожидаемо при массовой регистрации
                self.headers = {}
                return
            if resp.status_code >= 400:
                resp.failure(f"register HTTP {resp.status_code}")
                self.headers = {}
                return
            resp.success()
            token = (resp.json() or {}).get("access_token")
            self.headers = {"Authorization": f"Bearer {token}"} if token else {}

    @task(6)
    def my_dashboard(self) -> None:
        self._get("/dashboard", name="GET /dashboard [auth]", headers=self.headers)

    @task(4)
    def my_transactions(self) -> None:
        self._get(f"{API}/transactions", name="GET /api/transactions [auth]", headers=self.headers)

    @task(3)
    def my_goals(self) -> None:
        self._get(f"{API}/goals", name="GET /api/goals [auth]", headers=self.headers)

    @task(3)
    def my_obligations(self) -> None:
        self._get(f"{API}/obligations", name="GET /api/obligations [auth]", headers=self.headers)

    @task(2)
    def my_history(self) -> None:
        self._get(f"{API}/planning/history",
                  name="GET /api/planning/history [auth]", headers=self.headers)

    @task(3)
    def my_recommendation(self) -> None:
        self._post(f"{API}/recommendation",
                   name="POST /api/recommendation [auth]", headers=self.headers)

    @task(1)
    def my_calculate(self) -> None:
        self._post(f"{API}/planning/calculate",
                   name="POST /api/planning/calculate [auth]", headers=self.headers)
