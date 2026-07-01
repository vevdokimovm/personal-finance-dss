"""Тесты сервиса ключевой ставки ЦБ и расчёта r_bench (OCR).

Сеть к cbr.ru не дёргается — get_key_rate / _fetch_from_cbr мокаются.
"""
import datetime as _dt
import urllib.error

import pytest

from app.database.models import CbrKeyRate
from app.services import cbr_rate


def _reset_module_state() -> None:
    cbr_rate._cache.update(rate=None, source=None, fetched_on=None)
    cbr_rate._fail_until.update(ts=None, detail="")


class TestOpportunityCostRate:
    def test_post_tax_rate_when_cbr_available(self, monkeypatch):
        # ключевая 16% получена с cbr → r_bench = 0.16 × (1 − 0.13) = 0.1392
        monkeypatch.setattr(
            cbr_rate, "get_key_rate",
            lambda *a, **k: {"key_rate": 0.16, "source": "cbr", "as_of": "2026-06-18"},
        )
        result = cbr_rate.get_opportunity_cost_rate(fallback=0.14)
        assert result["source"] == "cbr_keyrate_post_tax"
        assert result["r_bench"] == pytest.approx(0.1392)

    def test_uses_cache_source(self, monkeypatch):
        monkeypatch.setattr(
            cbr_rate, "get_key_rate",
            lambda *a, **k: {"key_rate": 0.20, "source": "cache", "as_of": "2026-06-18"},
        )
        result = cbr_rate.get_opportunity_cost_rate(fallback=0.14, tax_rate=0.13)
        assert result["r_bench"] == pytest.approx(round(0.20 * 0.87, 4))

    def test_accepts_db_cache_source(self, monkeypatch):
        # last-known-good из БД — тоже реальная ставка, r_bench считаем из неё
        monkeypatch.setattr(
            cbr_rate, "get_key_rate",
            lambda *a, **k: {"key_rate": 0.1425, "source": "cache_db", "as_of": "2026-06-22"},
        )
        result = cbr_rate.get_opportunity_cost_rate(fallback=0.14)
        assert result["source"] == "cbr_keyrate_post_tax"
        assert result["r_bench"] == pytest.approx(round(0.1425 * 0.87, 4))

    def test_fallback_when_cbr_unavailable(self, monkeypatch):
        # cbr недоступен (зарубежный IP) → отдаём fallback, не вычисляем из фейка
        monkeypatch.setattr(
            cbr_rate, "get_key_rate",
            lambda *a, **k: {"key_rate": 0.16, "source": "fallback", "as_of": "2026-06-18", "detail": "403"},  # noqa: E501
        )
        result = cbr_rate.get_opportunity_cost_rate(fallback=0.14)
        assert result["source"] == "fallback"
        assert result["r_bench"] == pytest.approx(0.14)

    def test_custom_fallback_propagates(self, monkeypatch):
        monkeypatch.setattr(
            cbr_rate, "get_key_rate",
            lambda *a, **k: {"key_rate": None, "source": "fallback", "as_of": "x", "detail": ""},
        )
        result = cbr_rate.get_opportunity_cost_rate(fallback=0.11)
        assert result["r_bench"] == pytest.approx(0.11)


class TestSoapBody:
    def test_uses_capital_todate(self):
        # Регрессия корня инцидента: cbr.ru ждёт <ToDate> с заглавной (как <fromDate>).
        # Строчная <toDate> игнорировалась ASMX → ToDate=MinValue → пустой диапазон.
        body = cbr_rate._build_soap_body(_dt.date(2026, 1, 1), _dt.date(2026, 6, 22)).decode("utf-8")  # noqa: E501
        assert "<fromDate>2026-01-01</fromDate>" in body
        assert "<ToDate>2026-06-22</ToDate>" in body
        assert "<toDate>" not in body


class TestParseLatest:
    def test_picks_most_recent_with_date(self):
        xml = (
            '<KeyRate><KR><DT>2026-06-09T00:00:00+03:00</DT><Rate>20,00</Rate></KR>'
            '<KR><DT>2026-06-22T00:00:00+03:00</DT><Rate>14,25</Rate></KR></KeyRate>'
        )
        eff, rate = cbr_rate._parse_latest(xml)
        assert eff == _dt.date(2026, 6, 22)
        assert rate == pytest.approx(0.1425)

    def test_namespaced_and_mixed_case(self):
        xml = (
            '<diffgram xmlns:d="urn:x"><KeyRate xmlns="">'
            '<kr><dt>2026-06-22</dt><rate>14.25</rate></kr></KeyRate></diffgram>'
        )
        eff, rate = cbr_rate._parse_latest(xml)
        assert rate == pytest.approx(0.1425)
        assert eff == _dt.date(2026, 6, 22)

    def test_empty_returns_none_pair(self):
        assert cbr_rate._parse_latest("<KeyRate></KeyRate>") == (None, None)

    def test_soap_fault_returns_none_pair(self):
        # SOAP-fault с кодом 200 (валидный XML, но без KR) — корень инцидента
        fault = (
            '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
            '<soap:Body><soap:Fault><faultstring>err</faultstring></soap:Fault>'
            "</soap:Body></soap:Envelope>"
        )
        assert cbr_rate._parse_latest(fault) == (None, None)

    def test_legacy_parse_rate_wrapper(self):
        # обратная совместимость старого _parse_latest_rate
        xml = "<KeyRate><KR><DT>2026-06-15</DT><Rate>16,00</Rate></KR></KeyRate>"
        assert cbr_rate._parse_latest_rate(xml) == pytest.approx(0.16)
        assert cbr_rate._parse_latest_rate("<KeyRate></KeyRate>") is None


class TestDbCache:
    def test_successful_fetch_persists(self, db_session, monkeypatch):
        _reset_module_state()
        monkeypatch.setattr(
            cbr_rate, "_fetch_from_cbr",
            lambda: {"ok": True, "rate": 0.1425,
                     "effective_date": _dt.date(2026, 6, 22), "detail": ""},
        )
        res = cbr_rate.get_key_rate(fallback=0.16)
        assert res["source"] == "cbr"
        assert res["key_rate"] == pytest.approx(0.1425)
        assert res["as_of"] == "2026-06-22"

        row = (
            db_session.query(CbrKeyRate)
            .order_by(CbrKeyRate.effective_date.desc())
            .first()
        )
        assert row is not None
        assert row.rate == pytest.approx(0.1425)
        assert row.effective_date == _dt.date(2026, 6, 22)

    def test_db_cache_served_when_cbr_down(self, db_session, monkeypatch):
        _reset_module_state()
        cbr_rate._db_store(_dt.date(2026, 6, 22), 0.1425)
        monkeypatch.setattr(
            cbr_rate, "_fetch_from_cbr",
            lambda: {"ok": False, "rate": None, "effective_date": None, "detail": "403"},
        )
        res = cbr_rate.get_key_rate(fallback=0.16)
        assert res["source"] == "cache_db"
        assert res["key_rate"] == pytest.approx(0.1425)
        assert res["as_of"] == "2026-06-22"

    def test_fallback_when_no_cbr_and_no_cache(self, db_session, monkeypatch):
        _reset_module_state()
        monkeypatch.setattr(
            cbr_rate, "_fetch_from_cbr",
            lambda: {"ok": False, "rate": None, "effective_date": None, "detail": "403"},
        )
        res = cbr_rate.get_key_rate(fallback=0.16)
        assert res["source"] == "fallback"
        assert res["key_rate"] == pytest.approx(0.16)

    def test_upsert_idempotent(self, db_session):
        cbr_rate._db_store(_dt.date(2026, 6, 22), 0.1425)
        cbr_rate._db_store(_dt.date(2026, 6, 22), 0.1300)  # та же дата → обновление
        rows = (
            db_session.query(CbrKeyRate)
            .filter_by(effective_date=_dt.date(2026, 6, 22))
            .all()
        )
        assert len(rows) == 1
        assert rows[0].rate == pytest.approx(0.1300)

    def test_db_lookup_safe_without_table(self, monkeypatch):
        # если таблицы нет / сессия падает — тихо None, не валимся
        def _boom(*a, **k):
            raise RuntimeError("no table")
        monkeypatch.setattr(cbr_rate, "SessionLocal", _boom)
        assert cbr_rate._db_lookup() is None


class TestFailureMemo:
    def test_failure_short_circuits_next_call(self, db_session, monkeypatch):
        _reset_module_state()

        calls = {"n": 0}

        def _boom(*a, **k):
            calls["n"] += 1
            raise urllib.error.URLError("blocked")

        monkeypatch.setattr(cbr_rate.urllib.request, "urlopen", _boom)

        first = cbr_rate.get_key_rate(fallback=0.16)
        assert first["source"] == "fallback"  # сеть упала, БД-кэш пуст
        assert cbr_rate._fail_until["ts"] is not None
        assert calls["n"] == 1

        # второй вызов в окне ретрая не должен идти в сеть
        second = cbr_rate.get_key_rate(fallback=0.16)
        assert second["source"] == "fallback"
        assert calls["n"] == 1  # urlopen больше не вызывался

        _reset_module_state()


class _FakeResp:
    def __init__(self, body: bytes):
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class TestFetchFromCbr:
    def test_parses_real_shaped_response(self, monkeypatch):
        body = (
            '<?xml version="1.0"?>'
            '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
            '<soap:Body><KeyRateResponse xmlns="http://web.cbr.ru/"><KeyRateResult>'
            '<diffgr:diffgram xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">'
            '<KeyRate xmlns=""><KR><DT>2026-06-09T00:00:00+03:00</DT><Rate>20.00</Rate></KR>'
            '<KR><DT>2026-06-22T00:00:00+03:00</DT><Rate>14.25</Rate></KR>'
            "</KeyRate></diffgr:diffgram></KeyRateResult></KeyRateResponse>"
            "</soap:Body></soap:Envelope>"
        ).encode("utf-8")
        monkeypatch.setattr(cbr_rate.urllib.request, "urlopen", lambda *a, **k: _FakeResp(body))
        res = cbr_rate._fetch_from_cbr()
        assert res["ok"] is True
        assert res["rate"] == pytest.approx(0.1425)
        assert res["effective_date"] == _dt.date(2026, 6, 22)

    def test_200_but_unparseable_puts_snippet_in_detail(self, monkeypatch):
        # корень инцидента: 200, но нет строк KR (пустой диапазон / SOAP-fault)
        fault = (
            b'<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
            b'<soap:Body><KeyRateResponse xmlns="http://web.cbr.ru/">'
            b"<KeyRateResult/></KeyRateResponse></soap:Body></soap:Envelope>"
        )
        monkeypatch.setattr(cbr_rate.urllib.request, "urlopen", lambda *a, **k: _FakeResp(fault))
        res = cbr_rate._fetch_from_cbr()
        assert res["ok"] is False
        assert "не удалось извлечь" in res["detail"]
        assert "Начало ответа" in res["detail"]  # самодиагностика

    def test_http_403_detail(self, monkeypatch):
        def _raise(*a, **k):
            raise urllib.error.HTTPError("u", 403, "Forbidden", {}, None)
        monkeypatch.setattr(cbr_rate.urllib.request, "urlopen", _raise)
        res = cbr_rate._fetch_from_cbr()
        assert res["ok"] is False
        assert "403" in res["detail"]

    def test_http_other_code_detail(self, monkeypatch):
        def _raise(*a, **k):
            raise urllib.error.HTTPError("u", 500, "ISE", {}, None)
        monkeypatch.setattr(cbr_rate.urllib.request, "urlopen", _raise)
        res = cbr_rate._fetch_from_cbr()
        assert res["ok"] is False
        assert "500" in res["detail"]

    def test_network_error_detail(self, monkeypatch):
        def _raise(*a, **k):
            raise urllib.error.URLError("blocked")
        monkeypatch.setattr(cbr_rate.urllib.request, "urlopen", _raise)
        res = cbr_rate._fetch_from_cbr()
        assert res["ok"] is False
        assert "нет связи" in res["detail"]


class TestRefresh:
    def test_refresh_ok_persists(self, db_session, monkeypatch):
        _reset_module_state()
        monkeypatch.setattr(
            cbr_rate, "_fetch_from_cbr",
            lambda: {"ok": True, "rate": 0.1425,
                     "effective_date": _dt.date(2026, 6, 22), "detail": ""},
        )
        res = cbr_rate.refresh_key_rate()
        assert res["ok"] is True and res["stored"] is True
        assert res["key_rate"] == pytest.approx(0.1425)
        row = (
            db_session.query(CbrKeyRate)
            .filter_by(effective_date=_dt.date(2026, 6, 22))
            .first()
        )
        assert row is not None and row.rate == pytest.approx(0.1425)

    def test_refresh_fail(self, monkeypatch):
        _reset_module_state()
        monkeypatch.setattr(
            cbr_rate, "_fetch_from_cbr",
            lambda: {"ok": False, "rate": None, "effective_date": None, "detail": "403"},
        )
        res = cbr_rate.refresh_key_rate()
        assert res["ok"] is False and res["stored"] is False
