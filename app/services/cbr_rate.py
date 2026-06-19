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

# Память о недавней неудаче: при недоступности cbr.ru (зарубежный IP/блокировка)
# не ходим в сеть на каждом запросе рекомендации — иначе каждый расчёт ждёт ответ.
# Повторная попытка не чаще, чем раз в 15 минут.
_FAIL_RETRY_SECONDS = 900
_fail_until: dict[str, object] = {"ts": None, "detail": ""}


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
    now = datetime.now(timezone.utc)

    if _cache["rate"] is not None and _cache["fetched_on"] == today:
        return {"key_rate": _cache["rate"], "source": "cache", "as_of": today.isoformat()}

    # Недавняя неудача — не бьёмся в сеть на каждом запросе.
    if _fail_until["ts"] is not None and now < _fail_until["ts"]:
        return {
            "key_rate": fallback, "source": "fallback",
            "as_of": today.isoformat(), "detail": _fail_until["detail"],
        }

    detail = ""
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
            _fail_until.update(ts=None, detail="")
            return {"key_rate": rate, "source": "cbr", "as_of": today.isoformat(), "detail": ""}
        detail = "cbr.ru ответил, но ключевую ставку не удалось извлечь из ответа"
        _log.warning("CBR key rate: %s", detail)
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            detail = ("Банк России отклонил запрос (403). Частая причина — запрос идёт "
                      "с зарубежного IP или из дата-центра: cbr.ru блокирует такие обращения. "
                      "Решается запуском с российского IP/хостинга.")
        else:
            detail = f"cbr.ru вернул код {exc.code}"
        _log.warning("CBR key rate HTTP error: %s", detail)
    except (TimeoutError, urllib.error.URLError) as exc:
        reason = getattr(exc, "reason", exc)
        detail = f"нет связи с cbr.ru ({reason}) — проверьте интернет и доступ контейнера в сеть"
        _log.warning("CBR key rate network error: %s", detail)
    except (ET.ParseError, ValueError, OSError) as exc:
        detail = f"ответ cbr.ru не распознан ({exc})"
        _log.warning("CBR key rate parse error: %s", detail)

    _fail_until.update(ts=now + timedelta(seconds=_FAIL_RETRY_SECONDS), detail=detail)
    return {"key_rate": fallback, "source": "fallback", "as_of": today.isoformat(), "detail": detail}


def get_opportunity_cost_rate(fallback: float = 0.14, tax_rate: float = 0.13) -> dict[str, object]:
    """Альтернативная доходность рубля (OCR / r_bench) — порог фильтра Avalanche.

    Накопительные счета и короткие ОФЗ держатся рядом с ключевой ставкой ЦБ, но с
    процентного дохода удерживается НДФЛ. Поэтому посленалоговая доходность
    безрисковой альтернативы ≈ ключевая × (1 − НДФЛ). Гасить кредит выгодно только
    если его ставка выше этого ориентира.

    При ключевой 16% и НДФЛ 13% → r_bench ≈ 0.139, что совпадает с историческим
    дефолтом 0.14. Если ключевую получить нельзя (нет связи с cbr.ru / зарубежный
    IP), возвращается fallback (обычно prefs.r_bench). Функция никогда не падает.

    Возвращает {"r_bench": float, "source": "cbr_keyrate_post_tax"|"fallback", ...}.
    """
    kr = get_key_rate()
    rate = kr.get("key_rate")
    if kr.get("source") in ("cbr", "cache") and isinstance(rate, (int, float)) and 0 < rate < 1:
        ocr = round(float(rate) * (1 - tax_rate), 4)
        return {
            "r_bench": ocr,
            "source": "cbr_keyrate_post_tax",
            "key_rate": float(rate),
            "tax_rate": tax_rate,
            "as_of": kr.get("as_of"),
        }
    return {
        "r_bench": round(fallback, 4),
        "source": "fallback",
        "as_of": kr.get("as_of"),
        "detail": kr.get("detail", ""),
    }
