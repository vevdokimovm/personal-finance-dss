"""Получение ключевой ставки Банка России (с durable-кэшем).

Ключевая ставка ЦБ — рыночный ориентир доходности: ставки по накопительным
счетам и краткосрочным ОФЗ обычно держатся рядом с ней. Используется как
значение по умолчанию для порога Avalanche (r_bench / OCR).

Источник: SOAP-сервис ЦБ РФ DailyInfo.asmx (метод KeyRate). Сеть к cbr.ru может
быть недоступна (песочница/файрвол), а на проде с датацентрового IP cbr.ru
отдаёт 403 (DDoS-защита). Устойчивость — три рубежа: process-кэш на сутки →
durable last-known-good в БД (таблица cbr_key_rate_cache) → статический fallback.
Сервис никогда не падает: при любой ошибке отдаёт лучшее доступное значение.
"""
from __future__ import annotations

import logging
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from typing import TypedDict
from xml.etree import ElementTree as ET

from sqlalchemy import select

from app.database.db import SessionLocal
from app.database.models import CbrKeyRate
from app.utils.time import utcnow

_log = logging.getLogger(__name__)


class CbrFetchResult(TypedDict):
    ok: bool
    rate: float | None
    effective_date: date | None
    detail: str


_CBR_SOAP_URL = "https://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
_SOAP_ACTION = "http://web.cbr.ru/KeyRate"
_TIMEOUT_SECONDS = 10
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
    # ВНИМАНИЕ: cbr.ru ASMX чувствителен к регистру имён параметров. Метод KeyRate
    # ждёт <fromDate> и <ToDate> (заглавная T). Строчная <toDate> не распознаётся,
    # ToDate уходит в DateTime.MinValue → диапазон пустой → ноль строк KR в ответе.
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
        'xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
        "<soap:Body>"
        '<KeyRate xmlns="http://web.cbr.ru/">'
        f"<fromDate>{from_date:%Y-%m-%d}</fromDate>"
        f"<ToDate>{to_date:%Y-%m-%d}</ToDate>"
        "</KeyRate>"
        "</soap:Body>"
        "</soap:Envelope>"
    ).encode("utf-8")


def _parse_effective_date(text: str | None) -> date | None:
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _parse_latest(xml_text: str) -> tuple[date | None, float | None]:
    """Последняя (по дате) ключевая ставка из ответа KeyRate: (effective_date, доли).

    Регистр тегов игнорируется (KR/DT/Rate в любом регистре, с namespace и без),
    Rate — с запятой или точкой. Пустой ответ / SOAP-fault без строк KR → (None, None).
    """
    root = ET.fromstring(xml_text)
    rows: list[tuple[str, float]] = []
    for kr in root.iter():
        if kr.tag.split("}")[-1].upper() != "KR":
            continue
        dt_text: str | None = None
        rate_val: float | None = None
        for child in kr:
            ctag = child.tag.split("}")[-1].upper()
            if ctag == "DT":
                dt_text = (child.text or "").strip()
            elif ctag == "RATE" and child.text:
                try:
                    rate_val = float(child.text.replace(",", ".").strip())
                except ValueError:
                    rate_val = None
        if rate_val is not None:
            rows.append((dt_text or "", rate_val))
    if not rows:
        return None, None
    rows.sort(key=lambda x: x[0])
    dt_text, rate_pct = rows[-1]
    return _parse_effective_date(dt_text), rate_pct / 100.0


def _parse_latest_rate(xml_text: str) -> float | None:
    """Обратная совместимость: только ставка в долях (без даты)."""
    return _parse_latest(xml_text)[1]


def _fetch_from_cbr() -> CbrFetchResult:
    """Один сетевой запрос ключевой ставки к cbr.ru (SOAP KeyRate).

    Возвращает {"ok": bool, "rate": float|None, "effective_date": date|None,
    "detail": str}. Кэши и память неудач не трогает — этим заведует get_key_rate.
    При коде 200, но неизвлекаемой ставке кладёт начало ответа в detail —
    самодиагностика без доступа к cbr.ru.
    """
    today = datetime.now(timezone.utc).date()
    detail = ""
    try:
        body = _build_soap_body(today - timedelta(days=365), today)
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
            raw = resp.read().decode("utf-8", errors="replace")
        eff_date, rate = _parse_latest(raw)
        if rate is not None and 0 < rate < 1:
            return {"ok": True, "rate": rate, "effective_date": eff_date, "detail": ""}
        snippet = " ".join(raw[:300].split())
        detail = (
            "cbr.ru ответил, но ключевую ставку не удалось извлечь из ответа. "
            f"Начало ответа: {snippet}"
        )
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

    return {"ok": False, "rate": None, "effective_date": None, "detail": detail}


def _db_lookup() -> dict[str, object] | None:
    """Последнее известное значение ставки из БД-кэша (по максимальной
    effective_date). Любой сбой (нет таблицы/сессии) → None, без падения."""
    try:
        db = SessionLocal()
    except Exception as exc:  # noqa: BLE001 — кэш не критичен
        _log.debug("key rate db cache unavailable: %s", exc)
        return None
    try:
        row = db.execute(
            select(CbrKeyRate).order_by(CbrKeyRate.effective_date.desc())
        ).scalars().first()
        if row is None:
            return None
        return {
            "key_rate": float(row.rate),
            "source": "cache_db",
            "as_of": row.effective_date.isoformat(),
            "detail": "cbr.ru недоступен; последнее известное значение ставки из кэша БД",
        }
    except Exception as exc:  # noqa: BLE001
        _log.debug("key rate db cache lookup skipped: %s", exc)
        return None
    finally:
        try:
            db.close()
        except Exception:
            pass


def _db_store(effective_date: date | None, rate: float) -> None:
    """Сохранить ставку в БД-кэш (upsert по effective_date). Любой сбой не валит
    основной ответ — кэш лучший-эффорт."""
    if effective_date is None:
        return
    try:
        db = SessionLocal()
    except Exception as exc:  # noqa: BLE001
        _log.debug("key rate db cache store unavailable: %s", exc)
        return
    try:
        existing = db.execute(
            select(CbrKeyRate).where(CbrKeyRate.effective_date == effective_date)
        ).scalar_one_or_none()
        if existing is not None:
            existing.rate = float(rate)
            existing.fetched_at = utcnow()
        else:
            db.add(CbrKeyRate(effective_date=effective_date, rate=float(rate)))
        db.commit()
    except Exception as exc:  # noqa: BLE001
        _log.warning("key rate db cache store failed: %s", exc)
        try:
            db.rollback()
        except Exception:
            pass
    finally:
        try:
            db.close()
        except Exception:
            pass


def get_key_rate(fallback: float = 0.16) -> dict[str, object]:
    """Текущая ключевая ставка ЦБ (в долях). Рубежи устойчивости:
    process-кэш на сутки → live cbr.ru → durable БД-кэш → fallback.

    Возвращает {"key_rate": float, "source": "cbr"|"cache"|"cache_db"|"fallback",
    "as_of": str, ...}.
    """
    today = datetime.now(timezone.utc).date()
    now = datetime.now(timezone.utc)

    # 1. Process-кэш на сутки.
    if _cache["rate"] is not None and _cache["fetched_on"] == today:
        return {"key_rate": _cache["rate"], "source": "cache", "as_of": today.isoformat()}

    # 2. Недавняя неудача — в сеть не идём, но отдаём БД-кэш, если он есть.
    fail_ts = _fail_until["ts"]
    if isinstance(fail_ts, datetime) and now < fail_ts:
        cached = _db_lookup()
        if cached is not None:
            return cached
        return {
            "key_rate": fallback, "source": "fallback",
            "as_of": today.isoformat(), "detail": _fail_until["detail"],
        }

    # 3. Живой запрос к cbr.ru.
    res = _fetch_from_cbr()
    rate_value = res["rate"]
    if res["ok"] and rate_value is not None:
        rate = float(rate_value)
        _cache.update(rate=rate, source="cbr", fetched_on=today)
        _fail_until.update(ts=None, detail="")
        _db_store(res["effective_date"], rate)
        eff = res["effective_date"]
        as_of = eff.isoformat() if isinstance(eff, date) else today.isoformat()
        return {"key_rate": rate, "source": "cbr", "as_of": as_of, "detail": ""}

    # 4. Сбой — запоминаем неудачу и пробуем БД-кэш.
    _fail_until.update(ts=now + timedelta(seconds=_FAIL_RETRY_SECONDS), detail=res["detail"])
    _log.warning("CBR key rate: %s", res["detail"])
    cached = _db_lookup()
    if cached is not None:
        return cached

    # 5. Конституционный fallback — последний рубеж.
    return {
        "key_rate": fallback, "source": "fallback",
        "as_of": today.isoformat(), "detail": res["detail"],
    }


def refresh_key_rate() -> dict[str, object]:
    """Принудительно тянет ставку с cbr.ru и пишет в БД-кэш, минуя process-кэш и
    backoff. Для прогрева кэша на проде (например, cron с российского IP, где
    cbr.ru доступен; на датацентровом IP cbr.ru даст 403 — прогревать с RU-IP)."""
    today = datetime.now(timezone.utc).date()
    res = _fetch_from_cbr()
    rate_value = res["rate"]
    if res["ok"] and rate_value is not None:
        rate = float(rate_value)
        _db_store(res["effective_date"], rate)
        _cache.update(rate=rate, source="cbr", fetched_on=today)
        _fail_until.update(ts=None, detail="")
        eff = res["effective_date"]
        as_of = eff.isoformat() if isinstance(eff, date) else today.isoformat()
        return {"ok": True, "key_rate": rate, "source": "cbr", "as_of": as_of, "stored": True}
    return {
        "ok": False, "key_rate": None, "source": "fallback",
        "detail": res["detail"], "stored": False,
    }


def get_opportunity_cost_rate(fallback: float = 0.14, tax_rate: float = 0.13) -> dict[str, object]:
    """Альтернативная доходность рубля (OCR / r_bench) — порог фильтра Avalanche.

    Накопительные счета и короткие ОФЗ держатся рядом с ключевой ставкой ЦБ, но с
    процентного дохода удерживается НДФЛ. Поэтому посленалоговая доходность
    безрисковой альтернативы ≈ ключевая × (1 − НДФЛ). Гасить кредит выгодно только
    если его ставка выше этого ориентира.

    При ключевой 16% и НДФЛ 13% → r_bench ≈ 0.139, что совпадает с историческим
    дефолтом 0.14. Если ключевую получить нельзя (нет связи / зарубежный IP) и
    БД-кэш пуст — возвращается fallback (обычно prefs.r_bench). Никогда не падает.

    Возвращает {"r_bench": float, "source": "cbr_keyrate_post_tax"|"fallback", ...}.
    """
    kr = get_key_rate()
    rate = kr.get("key_rate")
    if kr.get("source") in ("cbr", "cache", "cache_db") and isinstance(
            rate, (int, float)) and 0 < rate < 1:
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
