"""Живые курсы валют от ЦБ РФ (P2.3 / P0.3).

Парсинг тестируется и на синтетике, и на реальной фикстуре ответа ЦБ (XML_daily,
снята с боевого формата — научная нотация, крупные номиналы, VunitRate). Сетевой fetch
с cbr.ru из песочницы напрямую недоступен: cbr.ru отдаёт 403 на IP дата-центров — этот
кейс покрыт тестом fallback. Живой сетевой fetch проверяется на проде с подходящим IP.
"""
from __future__ import annotations

import urllib.error
from pathlib import Path
from unittest.mock import patch

import pytest

from app.services.cbr_fx import fetch_cbr_fx_rates, parse_cbr_fx_xml, update_fx_rates

# Фрагмент формата ЦБ XML_daily.asp: рубли за Nominal единиц валюты.
_CBR_XML = """<?xml version="1.0" encoding="windows-1251"?>
<ValCurs Date="20.06.2026" name="Foreign Currency Market">
<Valute ID="R01235"><NumCode>840</NumCode><CharCode>USD</CharCode>
<Nominal>1</Nominal><Name>Доллар США</Name><Value>90,00</Value></Valute>
<Valute ID="R01239"><NumCode>978</NumCode><CharCode>EUR</CharCode>
<Nominal>1</Nominal><Name>Евро</Name><Value>100,00</Value></Valute>
<Valute ID="R01375"><NumCode>156</NumCode><CharCode>CNY</CharCode>
<Nominal>10</Nominal><Name>Юань</Name><Value>120,00</Value></Valute>
</ValCurs>"""


class TestParseCbrXml:
    def test_usd_pivot_is_one(self) -> None:
        rates = parse_cbr_fx_xml(_CBR_XML)
        assert rates["USD"] == 1.0

    def test_eur_to_usd(self) -> None:
        rates = parse_cbr_fx_xml(_CBR_XML)
        assert rates["EUR"] == pytest.approx(100 / 90, abs=1e-6)  # 1.1111

    def test_rub_to_usd(self) -> None:
        rates = parse_cbr_fx_xml(_CBR_XML)
        assert rates["RUB"] == pytest.approx(1 / 90, abs=1e-6)  # 0.0111

    def test_nominal_handled(self) -> None:
        # CNY: 120 руб за 10 → 12 руб/CNY → 12/90 USD
        rates = parse_cbr_fx_xml(_CBR_XML)
        assert rates["CNY"] == pytest.approx(12 / 90, abs=1e-6)

    def test_empty_without_usd(self) -> None:
        xml = '<ValCurs><Valute><CharCode>EUR</CharCode><Nominal>1</Nominal><Value>100,00</Value></Valute></ValCurs>'  # noqa: E501
        assert parse_cbr_fx_xml(xml) == {}

    def test_garbage_returns_empty(self) -> None:
        assert parse_cbr_fx_xml("не xml вовсе") == {}


_REAL_FIXTURE = Path(__file__).parent / "fixtures" / "cbr_daily_sample.xml"


class TestParseRealCbrResponse:
    """Парсинг на реальном ответе ЦБ (XML_daily, 23.06.2026): научная нотация,
    крупные номиналы, поле VunitRate. Фикстура снята с боевого формата."""

    @pytest.fixture
    def rates(self) -> dict[str, float]:
        return parse_cbr_fx_xml(_REAL_FIXTURE.read_text(encoding="utf-8"))

    def test_usd_pivot(self, rates: dict[str, float]) -> None:
        assert rates["USD"] == 1.0

    def test_major_currencies(self, rates: dict[str, float]) -> None:
        assert rates["EUR"] == pytest.approx(84.5863 / 73.765, abs=1e-6)
        assert rates["CNY"] == pytest.approx(10.8847 / 73.765, abs=1e-6)

    def test_nominal_100_normalized(self, rates: dict[str, float]) -> None:
        # JPY: 45.6551 руб за 100 единиц → 0.456551 руб/JPY (парсер округляет до 8 знаков)
        assert rates["JPY"] == round((45.6551 / 100) / 73.765, 8)

    def test_scientific_notation_value(self, rates: dict[str, float]) -> None:
        # IRR: 50.7659 руб за 1_000_000 — крошечный курс парсится без падения
        assert rates["IRR"] > 0
        assert rates["IRR"] == round((50.7659 / 1_000_000) / 73.765, 8)

    def test_large_nominal(self, rates: dict[str, float]) -> None:
        # VND: 29.2916 руб за 10000 единиц
        assert rates["VND"] == round((29.2916 / 10000) / 73.765, 8)


class TestFetchFallback:
    def test_fetch_returns_none_on_network_error(self) -> None:
        with patch("app.services.cbr_fx.urllib.request.urlopen", side_effect=OSError("blocked")):
            assert fetch_cbr_fx_rates(use_cache=False) is None

    def test_fetch_returns_none_on_http_403(self) -> None:
        # cbr.ru отвечает 403 на IP дата-центров (DDoS-защита) — реальный прод-кейс.
        err = urllib.error.HTTPError(
            "https://www.cbr.ru/scripts/XML_daily.asp", 403, "Forbidden", {}, None
        )
        with patch("app.services.cbr_fx.urllib.request.urlopen", side_effect=err):
            assert fetch_cbr_fx_rates(use_cache=False) is None


class TestUpdateFxRates:
    def test_update_does_not_wipe_db_on_failure(self, client) -> None:
        from app.database.db import SessionLocal

        db = SessionLocal()
        try:
            with patch("app.services.cbr_fx.fetch_cbr_fx_rates", return_value=None):
                result = update_fx_rates(db)
            assert result["source"] == "fallback"
            assert result["updated"] == 0
        finally:
            db.close()

    def test_update_upserts_on_success(self, client) -> None:
        from app.database.db import SessionLocal
        from app.database.models import FxRate

        db = SessionLocal()
        try:
            fake = {"USD": 1.0, "EUR": 1.1111, "RUB": 0.0111}
            with patch("app.services.cbr_fx.fetch_cbr_fx_rates", return_value=fake):
                result = update_fx_rates(db)
            assert result["source"] == "cbr"
            assert result["updated"] == 3
            eur = db.query(FxRate).filter(FxRate.currency == "EUR").first()
            assert eur is not None
            assert float(eur.rate_to_usd) == pytest.approx(1.1111, abs=1e-4)
        finally:
            db.close()

    def test_refresh_endpoint_returns_source(self, client) -> None:
        with patch("app.services.cbr_fx.fetch_cbr_fx_rates", return_value=None):
            r = client.post("/api/fx/refresh")
        assert r.status_code == 200
        assert r.json()["source"] == "fallback"
