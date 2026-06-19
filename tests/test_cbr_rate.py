"""Тесты сервиса ключевой ставки ЦБ и расчёта r_bench (OCR).

Сеть к cbr.ru не дёргается — get_key_rate мокается через monkeypatch.
"""
import urllib.error
import pytest

from app.services import cbr_rate


class TestOpportunityCostRate:
    def test_post_tax_rate_when_cbr_available(self, monkeypatch):
        # ключевая 16% получена с cbr → r_bench = 0.16 × (1 − 0.13) = 0.1392
        monkeypatch.setattr(
            cbr_rate, "get_key_rate",
            lambda: {"key_rate": 0.16, "source": "cbr", "as_of": "2026-06-18"},
        )
        result = cbr_rate.get_opportunity_cost_rate(fallback=0.14)
        assert result["source"] == "cbr_keyrate_post_tax"
        assert result["r_bench"] == pytest.approx(0.1392)

    def test_uses_cache_source(self, monkeypatch):
        monkeypatch.setattr(
            cbr_rate, "get_key_rate",
            lambda: {"key_rate": 0.20, "source": "cache", "as_of": "2026-06-18"},
        )
        result = cbr_rate.get_opportunity_cost_rate(fallback=0.14, tax_rate=0.13)
        assert result["r_bench"] == pytest.approx(round(0.20 * 0.87, 4))

    def test_fallback_when_cbr_unavailable(self, monkeypatch):
        # cbr недоступен (зарубежный IP) → отдаём fallback, не вычисляем из фейка
        monkeypatch.setattr(
            cbr_rate, "get_key_rate",
            lambda: {"key_rate": 0.16, "source": "fallback", "as_of": "2026-06-18", "detail": "403"},
        )
        result = cbr_rate.get_opportunity_cost_rate(fallback=0.14)
        assert result["source"] == "fallback"
        assert result["r_bench"] == pytest.approx(0.14)

    def test_custom_fallback_propagates(self, monkeypatch):
        monkeypatch.setattr(
            cbr_rate, "get_key_rate",
            lambda: {"key_rate": None, "source": "fallback", "as_of": "x", "detail": ""},
        )
        result = cbr_rate.get_opportunity_cost_rate(fallback=0.11)
        assert result["r_bench"] == pytest.approx(0.11)


class TestKeyRateParsing:
    def test_parse_latest_rate_picks_most_recent(self):
        xml = (
            '<KeyRate><KR><DT>2026-06-01</DT><Rate>15,00</Rate></KR>'
            '<KR><DT>2026-06-15</DT><Rate>16,00</Rate></KR></KeyRate>'
        )
        assert cbr_rate._parse_latest_rate(xml) == pytest.approx(0.16)

    def test_parse_empty_returns_none(self):
        assert cbr_rate._parse_latest_rate("<KeyRate></KeyRate>") is None


class TestFailureMemo:
    def test_failure_short_circuits_next_call(self, monkeypatch):
        # сбрасываем кэш и память неудач
        cbr_rate._cache.update(rate=None, source=None, fetched_on=None)
        cbr_rate._fail_until.update(ts=None, detail="")

        calls = {"n": 0}

        def _boom(*a, **k):
            calls["n"] += 1
            raise urllib.error.URLError("blocked")

        monkeypatch.setattr(cbr_rate.urllib.request, "urlopen", _boom)

        first = cbr_rate.get_key_rate(fallback=0.16)
        assert first["source"] == "fallback"
        assert cbr_rate._fail_until["ts"] is not None
        assert calls["n"] == 1

        # второй вызов в окне ретрая не должен идти в сеть
        second = cbr_rate.get_key_rate(fallback=0.16)
        assert second["source"] == "fallback"
        assert calls["n"] == 1  # urlopen больше не вызывался

        cbr_rate._fail_until.update(ts=None, detail="")  # cleanup
