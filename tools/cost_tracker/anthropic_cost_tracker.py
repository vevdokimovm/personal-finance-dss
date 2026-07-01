"""FINPILOT — сводка расхода Claude по нескольким аккаунтам (V/J/S/M).

Заглушка-каркас: без ключей завершается чисто с подсказкой.
Как только 4 admin-ключа вписаны в .env — тянет usage/cost через Admin API
и печатает единую таблицу по аккаунтам.
"""

import argparse
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Iterator

import requests
from dotenv import load_dotenv

API_BASE = "https://api.anthropic.com/v1/organizations"
API_VERSION = "2023-06-01"
KEY_PREFIX = "sk-ant-admin01-"
PLACEHOLDER = "sk-ant-admin01-REPLACE_ME"
ACCOUNTS = ("V", "J", "S", "M")
MAX_DAILY_BUCKETS = 31


@dataclass
class AccountConfig:
    label: str
    admin_key: str

    @property
    def is_ready(self) -> bool:
        return (
            bool(self.admin_key)
            and self.admin_key != PLACEHOLDER
            and self.admin_key.startswith(KEY_PREFIX)
        )


@dataclass
class AccountReport:
    label: str
    tokens: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    cost_cents: float = 0.0
    error: str | None = None

    @property
    def cost_usd(self) -> float:
        return self.cost_cents / 100.0

    @property
    def total_tokens(self) -> int:
        return sum(self.tokens.values())


def iter_results(buckets: list) -> Iterator[dict]:
    for bucket in buckets:
        if not isinstance(bucket, dict):
            continue
        results = bucket.get("results")
        if isinstance(results, list):
            yield from (r for r in results if isinstance(r, dict))
        else:
            yield bucket


def date_windows(start: datetime, end: datetime, max_days: int) -> Iterator[tuple[str, str]]:
    cursor = start
    step = timedelta(days=max_days)
    while cursor < end:
        chunk_end = min(cursor + step, end)
        yield _iso(cursor), _iso(chunk_end)
        cursor = chunk_end


def _iso(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


class AdminAPIClient:
    def __init__(self, admin_key: str, timeout: int = 30) -> None:
        self._key = admin_key
        self._timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": self._key,
            "anthropic-version": API_VERSION,
            "User-Agent": "finpilot-cost-tracker/1.0 (+https://github.com/vevdokimovm)",
        }

    def _paginated(self, endpoint: str, params: dict) -> list:
        buckets: list = []
        page: str | None = None
        while True:
            query = dict(params)
            if page:
                query["page"] = page
            resp = requests.get(
                f"{API_BASE}/{endpoint}",
                headers=self._headers(),
                params=query,
                timeout=self._timeout,
            )
            resp.raise_for_status()
            payload = resp.json()
            buckets.extend(payload.get("data", []))
            if not payload.get("has_more"):
                break
            page = payload.get("next_page")
            if not page:
                break
        return buckets

    def fetch_cost_cents(self, start: str, end: str) -> float:
        buckets = self._paginated("cost_report", {"starting_at": start, "ending_at": end})
        total = 0.0
        for row in iter_results(buckets):
            amount = row.get("amount")
            if amount is not None:
                total += float(amount)
        return total

    def fetch_tokens(self, start: str, end: str) -> dict[str, int]:
        buckets = self._paginated(
            "usage_report/messages",
            {"starting_at": start, "ending_at": end, "bucket_width": "1d"},
        )
        totals: dict[str, int] = defaultdict(int)
        for row in iter_results(buckets):
            for key, value in row.items():
                if key.endswith("_tokens") and isinstance(value, int):
                    totals[key] += value
        return totals


class CostTracker:
    def __init__(self, accounts: list[AccountConfig], days: int) -> None:
        self._accounts = accounts
        end = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        self._start = end - timedelta(days=days)
        self._end = end

    def run(self) -> list[AccountReport]:
        reports: list[AccountReport] = []
        for account in self._accounts:
            reports.append(self._collect(account))
        return reports

    def _collect(self, account: AccountConfig) -> AccountReport:
        report = AccountReport(label=account.label)
        client = AdminAPIClient(account.admin_key)
        try:
            for start, end in date_windows(self._start, self._end, MAX_DAILY_BUCKETS):
                report.cost_cents += client.fetch_cost_cents(start, end)
                for key, value in client.fetch_tokens(start, end).items():
                    report.tokens[key] += value
        except requests.HTTPError as exc:
            report.error = _http_error(exc)
        except requests.RequestException as exc:
            report.error = f"сеть: {exc}"
        return report


def _http_error(exc: requests.HTTPError) -> str:
    status = exc.response.status_code if exc.response is not None else "?"
    if status == 401:
        return "401 — ключ невалиден или отозван"
    if status == 403:
        return "403 — у ключа нет прав Admin API (не тот тип ключа?)"
    if status == 429:
        return "429 — превышен лимит запросов, повтори позже"
    return f"HTTP {status}"


def _fmt_tokens(value: int) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


def load_accounts() -> tuple[list[AccountConfig], list[AccountConfig]]:
    load_dotenv()
    ready: list[AccountConfig] = []
    missing: list[AccountConfig] = []
    for label in ACCOUNTS:
        key = os.getenv(f"ANTHROPIC_ADMIN_KEY_{label}", "").strip()
        config = AccountConfig(label=label, admin_key=key)
        (ready if config.is_ready else missing).append(config)
    return ready, missing


def _print_env_hint() -> None:
    print("Формат .env (положи рядом со скриптом, в .gitignore):")
    print("-" * 60)
    for label in ACCOUNTS:
        print(f"ANTHROPIC_ADMIN_KEY_{label}={PLACEHOLDER}")
    print("-" * 60)
    print("Ключи создаются в Консоли: platform.claude.com/settings/admin-keys\n")


def _print_table(reports: list[AccountReport], days: int) -> None:
    print(f"\nРасход Claude за последние {days} дн. (UTC)")
    print("=" * 62)
    header = f"{'Акк':<5}{'Токены':>14}{'Стоимость':>14}   Статус"
    print(header)
    print("-" * 62)
    total_cost = 0.0
    total_tokens = 0
    for report in reports:
        if report.error:
            print(f"{report.label:<5}{'—':>14}{'—':>14}   {report.error}")
            continue
        total_cost += report.cost_usd
        total_tokens += report.total_tokens
        print(
            f"{report.label:<5}"
            f"{_fmt_tokens(report.total_tokens):>14}"
            f"{'$' + format(report.cost_usd, '.2f'):>14}"
            f"   ok"
        )
    print("-" * 62)
    print(f"{'ИТОГО':<5}{_fmt_tokens(total_tokens):>14}{'$' + format(total_cost, '.2f'):>14}")
    print("=" * 62)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="FINPILOT — сводка расхода Claude по аккаунтам V/J/S/M"
    )
    parser.add_argument("--days", type=int, default=30, help="период в днях (по умолчанию 30)")
    args = parser.parse_args()

    ready, missing = load_accounts()
    if missing:
        labels = ", ".join(config.label for config in missing)
        print(f"[stub] Нет готовых admin-ключей для: {labels}\n")
        _print_env_hint()

    if not ready:
        print("Ни одного готового аккаунта — заглушка завершает работу.")
        return 0

    tracker = CostTracker(ready, args.days)
    reports = tracker.run()
    _print_table(reports, args.days)
    return 0


if __name__ == "__main__":
    sys.exit(main())
