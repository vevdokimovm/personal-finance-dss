"""Живые курсы валют от ЦБ РФ (P2.3).

Парсинг тестируется на фикстуре XML_daily. Реальный fetch с cbr.ru из песочницы
недоступен (только fallback) — живая проверка fetch выполняется на Docker.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest

from app.services.cbr_fx import fetch_cbr_fx_rates, parse_cbr_fx_xml, update_fx_rates

# Фрагмент формата ЦБ XML_daily.asp: рубли за Nominal единиц валюты.
_CBR_XML = """<?xml version="1.0" encoding="windows-1251"?>
<ValCurs Date="20.06.2026" name="Foreign Currency Market">
<Valute ID="R01235"><NumCode>840</NumCode><CharCode>USD</CharCode><Nominal>1</Nominal><Name>Доллар США</Name><Value>90,00</Value></Valute>
<Valute ID="R01239"><NumCode>978</NumCode><CharCode>EUR</CharCode><Nominal>1</Nominal><Name>Евро</Name><Value>100,00</Value></Valute>
<Valute ID="R01375"><NumCode>156</NumCode><CharCode>CNY</CharCode><Nominal>10</Nominal><Name>Юань</Name><Value>120,00</Value></Valute>
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
        xml = '<ValCurs><Valute><CharCode>EUR</CharCode><Nominal>1</Nominal><Value>100,00</Value></Valute></ValCurs>'
        assert parse_cbr_fx_xml(xml) == {}

    def test_garbage_returns_empty(self) -> None:
        assert parse_cbr_fx_xml("не xml вовсе") == {}


class TestFetchFallback:
    def test_fetch_returns_none_on_network_error(self) -> None:
        with patch("app.services.cbr_fx.urllib.request.urlopen", side_effect=OSError("blocked")):
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
