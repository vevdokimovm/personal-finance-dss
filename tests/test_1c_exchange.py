"""Тесты парсера формата 1CClientBankExchange (универсальный для бизнес-счетов).

Синтетика по структуре реальных файлов «kl_to_1c» (ЕВРОМОДА со скринов). Ключевое —
знак операции по счёту владельца (РасчСчет шапки): ПлательщикСчет=владелец → расход,
ПолучательСчет=владелец → приход. Детерминированно, без LLM.
"""
from app.services.statement_parser import parse_1c_exchange, parse_bank_statement

_OWNER = "40702810001300019216"

_FILE = f"""1CClientBankExchange
ВерсияФормата=1.03
Кодировка=Windows
Отправитель=Банк
ДатаСоздания=14.06.2026
РасчСчет={_OWNER}
СекцияРасчСчет
ДатаНачала=01.06.2026
ДатаКонца=14.06.2026
РасчСчет={_OWNER}
НачальныйОстаток=100000.00
КонецРасчСчет
СекцияДокумент=Банковский ордер
Номер=49761
Дата=11.06.2026
Сумма=39.00
ПлательщикСчет={_OWNER}
ДатаСписано=11.06.2026
Плательщик=ООО "ЕВРОМОДА"
ПолучательСчет=47423810701300039072
Получатель=АО "Альфа-Банк"
НазначениеПлатежа=Размещение денежных средств во Вклад, без НДС
КонецДокумента
СекцияДокумент=Платежное поручение
Номер=100
Дата=12.06.2026
Сумма=5000.00
ПлательщикСчет=40817810000000000001
Плательщик=ООО "Контрагент"
ПолучательСчет={_OWNER}
ДатаПоступило=12.06.2026
Получатель=ООО "ЕВРОМОДА"
НазначениеПлатежа=Оплата по счёту 123
КонецДокумента
КонецФайла
"""


class TestDetection:
    def test_dispatched_by_marker(self):
        # parse_bank_statement сам распознаёт 1С по первой строке, независимо от bank_id
        txns = parse_bank_statement(_FILE, bank_id="universal")
        assert len(txns) == 2

    def test_not_1c_falls_through(self):
        csv = "Дата;Сумма;Описание\n01.06.2025;-100;X\n"
        # обычный CSV не должен уходить в 1С-парсер
        assert len(parse_bank_statement(csv, bank_id="universal")) == 1


class TestSignByOwnerAccount:
    def test_payer_is_owner_is_expense(self):
        txns = parse_1c_exchange(_FILE)
        order = next(t for t in txns if t["amount"] == 39.0)
        assert order["type"] == "expense"

    def test_payee_is_owner_is_income(self):
        txns = parse_1c_exchange(_FILE)
        pay = next(t for t in txns if t["amount"] == 5000.0)
        assert pay["type"] == "income"


class TestFieldExtraction:
    def test_amount_and_description(self):
        txns = parse_1c_exchange(_FILE)
        order = next(t for t in txns if t["amount"] == 39.0)
        assert "Размещение денежных средств" in order["description"]

    def test_date_parsed(self):
        txns = parse_1c_exchange(_FILE)
        pay = next(t for t in txns if t["amount"] == 5000.0)
        assert pay["date"].startswith("2026-06-12")

    def test_count(self):
        assert len(parse_1c_exchange(_FILE)) == 2


class TestEdgeCases:
    def test_no_owner_uses_dates_fallback(self):
        # без РасчСчет в шапке: приход — по наличию ДатаПоступило, иначе расход
        content = (
            "1CClientBankExchange\n"
            "СекцияДокумент=Платежное поручение\n"
            "Дата=01.06.2026\nСумма=1000\n"
            "ПлательщикСчет=11111111111111111111\n"
            "ПолучательСчет=22222222222222222222\n"
            "ДатаПоступило=01.06.2026\n"
            "НазначениеПлатежа=Входящий\n"
            "КонецДокумента\nКонецФайла\n"
        )
        txns = parse_1c_exchange(content)
        assert len(txns) == 1
        assert txns[0]["type"] == "income"

    def test_zero_amount_skipped(self):
        content = (
            "1CClientBankExchange\nРасчСчет=11111111111111111111\n"
            "СекцияДокумент=Ордер\nДата=01.06.2026\nСумма=0\n"
            "ПлательщикСчет=11111111111111111111\nНазначениеПлатежа=X\n"
            "КонецДокумента\nКонецФайла\n"
        )
        assert parse_1c_exchange(content) == []

    def test_no_documents_returns_empty(self):
        assert parse_1c_exchange("1CClientBankExchange\nРасчСчет=1\nКонецФайла\n") == []
