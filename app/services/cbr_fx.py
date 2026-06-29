"""Живые курсы валют от Банка России (P2.3).

Источник: https://www.cbr.ru/scripts/XML_daily.asp — официальные курсы валют к рублю.
Пересчитываются в USD-пивот (FxRate.rate_to_usd = стоимость 1 единицы валюты в USD).

Как и cbr_rate: сеть к cbr.ru может быть недоступна (песочница/зарубежный IP) —
тогда возвращается кэш или None, а БД-курсы не затираются. Сервис не падает.
Реальный fetch проверяется на российском хостинге/Docker.
"""
from __future__ import annotations

import logging
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from xml.etree import ElementTree as ET

from sqlalchemy.orm import Session

from app.database.models import FxRate

_log = logging.getLogger(__name__)

_CBR_FX_URL = "https://www.cbr.ru/scripts/XML_daily.asp"
_TIMEOUT_SECONDS = 6
# Реалистичный User-Agent: cbr.ru отклоняет дефолтный Python-urllib UA.
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Кэш на процесс: курсы на сутки.
_cache: dict[str, object] = {"rates": None, "fetched_on": None}
# Память о недавней неудаче: не бьёмся в сеть на каждом запросе.
_FAIL_RETRY_SECONDS = 900
_fail_until: dict[str, object] = {"ts": None}


def parse_cbr_fx_xml(xml_text: str) -> dict[str, float]:
    """ЦБ XML_daily → {currency: rate_to_usd}. USD-пивот.

    ЦБ даёт рубли за Nominal единиц валюты; rate_to_usd = USD за 1 единицу:
    rate(X) = (рублей за 1 X) / (рублей за 1 USD). Для RUB добавляется 1/rub_per_usd.
    """
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return {}

    rub_per_unit: dict[str, float] = {}
    for val in root.iter("Valute"):
        code_el = val.find("CharCode")
        nom_el = val.find("Nominal")
        value_el = val.find("Value")
        if code_el is None or nom_el is None or value_el is None:
            continue
        code = (code_el.text or "").strip().upper()
        try:
            nominal = float((nom_el.text or "1").replace(",", "."))
            value = float((value_el.text or "0").replace(",", "."))
        except ValueError:
            continue
        if code and nominal > 0 and value > 0:
            rub_per_unit[code] = value / nominal

    if "USD" not in rub_per_unit:
        return {}

    rub_per_usd = rub_per_unit["USD"]
    rates: dict[str, float] = {"USD": 1.0, "RUB": round(1.0 / rub_per_usd, 8)}
    for code, rub in rub_per_unit.items():
        rates[code] = round(rub / rub_per_usd, 8)
    return rates


def fetch_cbr_fx_rates(use_cache: bool = True) -> dict[str, float] | None:
    """Курсы валют с cbr.ru в USD-пивоте. Кэш на сутки; при недоступности — None."""
    today = datetime.now(timezone.utc).date()
    now = datetime.now(timezone.utc)

    if use_cache and _cache["rates"] is not None and _cache["fetched_on"] == today:
        return _cache["rates"]  # type: ignore[return-value]

    fail_ts = _fail_until["ts"]
    if use_cache and isinstance(fail_ts, datetime) and now < fail_ts:
        return None

    try:
        req = urllib.request.Request(
            _CBR_FX_URL,
            headers={"User-Agent": _USER_AGENT, "Accept": "application/xml, text/xml, */*"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=_TIMEOUT_SECONDS) as resp:
            raw = resp.read()
        try:
            xml_text = raw.decode("windows-1251")  # ЦБ отдаёт cp1251
        except UnicodeDecodeError:
            xml_text = raw.decode("utf-8", errors="replace")
        rates = parse_cbr_fx_xml(xml_text)
        if rates:
            _cache.update(rates=rates, fetched_on=today)
            _fail_until.update(ts=None)
            return rates
        _log.warning("CBR FX: ответ получен, но курсы не извлечены")
    except urllib.error.HTTPError as exc:
        _log.warning("CBR FX HTTP error: %s", exc.code)
    except (TimeoutError, urllib.error.URLError, OSError) as exc:
        _log.warning("CBR FX network error: %s", getattr(exc, "reason", exc))

    _fail_until.update(ts=now + timedelta(seconds=_FAIL_RETRY_SECONDS))
    return None


def update_fx_rates(db: Session) -> dict[str, object]:
    """Обновляет таблицу fx_rates с ЦБ. При недоступности БД не затирается.

    Возвращает {"updated": int, "source": "cbr"|"fallback"}.
    """
    rates = fetch_cbr_fx_rates()
    if not rates:
        return {"updated": 0, "source": "fallback"}

    updated = 0
    now = datetime.utcnow()
    for currency, rate in rates.items():
        row = db.query(FxRate).filter(FxRate.currency == currency).first()
        if row is None:
            db.add(FxRate(currency=currency, rate_to_usd=rate, updated_at=now))
        else:
            row.rate_to_usd = rate
            row.updated_at = now
        updated += 1
    db.commit()
    return {"updated": updated, "source": "cbr"}
