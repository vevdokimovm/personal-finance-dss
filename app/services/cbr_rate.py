"""Получение ключевой ставки Банка России.

Ключевая ставка ЦБ — рыночный ориентир доходности: ставки по накопительным
счетам и краткосрочным ОФЗ обычно держатся рядом с ней. Используется как
значение по умолчанию для порога Avalanche (r_bench / OCR).

Источник: SOAP-сервис ЦБ РФ DailyInfo.asmx (метод KeyRate).
Сеть к cbr.ru может быть недоступна (песочница/файрвол) — тогда возвращается
кэшированное или дефолтное значение (CBR_KEY_RATE_FALLBACK). Сервис никогда
не падает: при любой ошибке отдаёт fallback.
"""
from __future__ import annotations

import logging
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from xml.etree import ElementTree as ET

_log = logging.getLogger(__name__)

_CBR_SOAP_URL = "https://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
_SOAP_ACTION = "http://web.cbr.ru/KeyRate"
_TIMEOUT_SECONDS = 6
# Реалистичный User-Agent: cbr.ru отклоняет запросы с дефолтным Python-urllib UA.
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Кэш на процесс: (значение, источник, дата) на сутки.
_cache: dict[str, object] = {"rate": None, "source": None, "fetched_on": None}


def _build_soap_body(from_date: date, to_date: date) -> bytes:
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
        'xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
        "<soap:Body>"
        '<KeyRate xmlns="http://web.cbr.ru/">'
        f"<fromDate>{from_date:%Y-%m-%d}</fromDate>"
        f"<toDate>{to_date:%Y-%m-%d}</toDate>"
        "</KeyRate>"
        "</soap:Body>"
        "</soap:Envelope>"
    ).encode("utf-8")


def _parse_latest_rate(xml_text: str) -> float | None:
    """Возвращает последнюю ставку (в долях, 16% → 0.16) из ответа KeyRate."""
    root = ET.fromstring(xml_text)
    rates: list[tuple[str, float]] = []
    for kr in root.iter():
        tag = kr.tag.split("}")[-1]
        if tag == "KR":
            d = r = None
            for child in kr:
                ctag = child.tag.split("}")[-1]
                if ctag == "DT":
                    d = child.text
                elif ctag == "Rate" and child.text:
                    r = float(child.text.replace(",", "."))
            if r is not None:
                rates.append((d or "", r))
    if not rates:
        return None
    rates.sort(key=lambda x: x[0])
    return rates[-1][1] / 100.0  # проценты → доли


def get_key_rate(fallback: float = 0.16) -> dict[str, object]:
    """Текущая ключевая ставка ЦБ (в долях). Кэш на сутки, иначе fallback.

    Возвращает {"key_rate": float, "source": "cbr"|"cache"|"fallback", "as_of": str}.
    """
    today = datetime.now(timezone.utc).date()

    if _cache["rate"] is not None and _cache["fetched_on"] == today:
        return {"key_rate": _cache["rate"], "source": "cache", "as_of": today.isoformat()}

    try:
        body = _build_soap_body(today - timedelta(days=30), today)
        req = urllib.request.Request(
            _CBR_SOAP_URL,
            data=body,
            headers={
                "Content-Type": "text/xml; charset=utf-8",
                # SOAP 1.1 требует SOAPAction в двойных кавычках — ASMX иначе отдаёт 500.
                "SOAPAction": f'"{_SOAP_ACTION}"',
                "User-Agent": _USER_AGENT,
                "Accept": "text/xml, application/soap+xml, */*",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=_TIMEOUT_SECONDS) as resp:
            rate = _parse_latest_rate(resp.read().decode("utf-8"))
        if rate is not None and 0 < rate < 1:
            _cache.update(rate=rate, source="cbr", fetched_on=today)
            return {"key_rate": rate, "source": "cbr", "as_of": today.isoformat()}
        _log.warning("CBR key rate: ответ получен, но ставку извлечь не удалось")
    except (urllib.error.URLError, ET.ParseError, ValueError, TimeoutError, OSError) as exc:
        # Логируем реальную причину — иначе диагностика «почему fallback» невозможна.
        _log.warning("CBR key rate fetch failed: %s", exc)

    return {"key_rate": fallback, "source": "fallback", "as_of": today.isoformat()}
