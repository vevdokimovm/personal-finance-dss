"""
Тесты парсера на РЕАЛЬНЫЕ форматные особенности (найдены прогоном настоящих выписок).

Проверяют то, на чём парсер спотыкался на живых данных банков:
- ВТБ PDF: движение в раздельных колонках Приход/Расход/Комиссия (реальная раскладка),
  а не знаковая сумма в одной колонке; чисто-комиссионная операция = расход.
- 1C-обмен: реальные банки шлют файл в windows-1251, не UTF-8 — декодер обязан это учесть.
- Детекция не-выписок: банк в окне «выписки» отдаёт справки об остатке/реквизиты/о
  задолженности — операций там нет, приложение не должно принять их за пустую выписку.

Фикстуры синтетические (реальные выписки содержат PII и в репозиторий не кладутся), но
воспроизводят те же форматные особенности, на которых ломались настоящие файлы.
"""
from __future__ import annotations

import unicodedata
from pathlib import Path

import pytest

from app.services.statement_parser import (
    _raif_column_map,
    _raif_table_to_transactions,
    _sber_text_to_transactions,
    _vtb_column_map,
    _vtb_table_to_transactions,
    classify_non_statement,
    decode_statement_bytes,
    detect_bank,
    detect_pdf_bank,
    parse_1c_exchange,
    parse_bank_statement,
    parse_tinkoff_csv,
    parse_universal_csv,
    pdf_non_statement_reason,
)

TPL = Path("app/data/statement_templates")


class TestVtbRealLayout:
    """Реальная раскладка ВТБ: [дата, дата2, сумма_в_валюте_операции, Приход, Расход,
    Комиссия, Описание] с двухрядной шапкой. Знаковая колонка[2] для рублёвой комиссии = 0,
    поэтому нетто считается по Приход − Расход − Комиссия. На реальном файле это давало 0."""

    def _rows(self):
        return [[
            ["Операции по счёту", "", "", "", "", "", ""],
            ["Дата и время\nоперации", "Дата обработки", "Сумма в валюте\nоперации",
             "Сумма в валюте счёта", "", "Комиссия", "Описание операции"],
            ["", "", "", "Приход", "Расход", "", ""],
            ["14.12.2025\n23:04:46", "14.12.2025", "0.00 RUB", "0\nRUB", "0\nRUB",
             "69.01\nRUB", "Комиссия за обслуживание счета."],
            ["10.12.2025\n10:00:00", "10.12.2025", "0.00 RUB", "5 000,00\nRUB", "0\nRUB",
             "0\nRUB", "Перевод СБП"],
            ["09.12.2025\n11:00:00", "09.12.2025", "0.00 RUB", "0\nRUB", "1 200,00\nRUB",
             "0\nRUB", "Оплата покупки"],
        ]]

    def test_commission_only_is_expense(self):
        # Приход=0, Расход=0, только Комиссия 69.01 → расход 69.01 (было: 0 операций).
        t = _vtb_table_to_transactions(self._rows())
        assert t[0]["type"] == "expense"
        assert t[0]["amount"] == pytest.approx(69.01)
        assert t[0]["description"] == "Комиссия за обслуживание счета."

    def test_prihod_is_income(self):
        t = _vtb_table_to_transactions(self._rows())
        assert t[1]["type"] == "income"
        assert t[1]["amount"] == pytest.approx(5000.0)

    def test_rashod_is_expense(self):
        t = _vtb_table_to_transactions(self._rows())
        assert t[2]["type"] == "expense"
        assert t[2]["amount"] == pytest.approx(1200.0)

    def test_header_and_title_rows_skipped(self):
        # Строки-заголовки (без даты в первой ячейке) не попадают в операции.
        assert len(_vtb_table_to_transactions(self._rows())) == 3

    def test_signed_single_column_variant_still_works(self):
        # Второй формат ВТБ: знаковая сумма в одной колонке, Приход/Расход пусты.
        rows = [[["30.05.2026\n19:56:44", "02.06.2026", "-741.74 RUB", None, None,
                  "0.00", "PYATEROCHKA"]]]
        t = _vtb_table_to_transactions(rows)
        assert t[0]["type"] == "expense" and t[0]["amount"] == pytest.approx(741.74)


class TestVtbTemplateB:
    """Второй реальный шаблон ВТБ: вместо «Комиссия» на индексе 5 стоит ОПИСАНИЕ, а на 6 —
    наименование получателя. Привязка к индексам брала описание из колонки контрагента
    (все расходы получали заглушку «Операция») и читала текст описания как комиссию."""

    def _rows(self):
        return [[
            ["Операции по счёту", "", "", "", "", "", ""],
            ["Дата и время\nоперации", "Дата обработки\nбанком",
             "Сумма операции в\nвалюте операции",
             "Сумма операции в валюте\nсчета/карты", "", "Описание операции",
             "Наименование\nполучателя/\nОтправителя"],
            ["", "", "", "Приход", "Расход", "", ""],
            ["29.06.2026\n11:00:00", "02.07.2026", "-186.65 RUB", "0.00 RUB", "-186.65 RUB",
             "Оплата товаров и услуг. SHOP-1. РОССИЯ. Podolsk. 991000240508.", ""],
            ["27.06.2026\n12:00:00", "27.06.2026", "3000.00 RUB", "3000.00 RUB", "0.00 RUB",
             "Переводы через СБП. Перевод денежных средств.", "Иванова Мария Петровна"],
            ["18.06.2026\n09:00:00", "18.06.2026", "-126.00 RUB", "0.00 RUB", "-126.00 RUB",
             "Оплата услуг коммерческих провайдеров. Лицевой счет: 850010068828.", "Ростелеком"],
        ]]

    def test_description_taken_from_its_own_column(self):
        t = _vtb_table_to_transactions(self._rows())
        assert t[0]["type"] == "expense" and t[0]["amount"] == pytest.approx(186.65)
        assert t[0]["description"].startswith("Оплата товаров и услуг. SHOP-1")

    def test_negative_rashod_column(self):
        # В этом шаблоне Расход идёт со знаком минус (в шаблоне A — положительный).
        t = _vtb_table_to_transactions(self._rows())
        assert [x["type"] for x in t] == ["expense", "income", "expense"]

    def test_counterparty_appended_to_description(self):
        # Контрагент — сырьё для merchant-аналитики: «Ростелеком» терять нельзя.
        t = _vtb_table_to_transactions(self._rows())
        assert t[1]["description"].endswith("Иванова Мария Петровна")
        assert "Ростелеком" in t[2]["description"]

    def test_numeric_description_not_read_as_commission(self):
        # Ландмайна: `_num('Перевод 1500') == 1500.0`. При привязке к индексам описание
        # попадало в слот «Комиссия» и молча вычиталось из суммы (200 → 1700).
        rows = self._rows()
        rows[0].append(["25.06.2026\n10:00:00", "25.06.2026", "-200.00 RUB", "0.00 RUB",
                        "-200.00 RUB", "Перевод 1500", ""])
        t = _vtb_table_to_transactions(rows)
        assert t[3]["amount"] == pytest.approx(200.00)
        assert t[3]["description"] == "Перевод 1500"

    def test_column_map_detects_both_templates(self):
        b = _vtb_column_map(self._rows()[0])
        assert (b["prihod"], b["rashod"], b["desc"], b["party"]) == (3, 4, 5, 6)
        assert "komis" not in b
        a = _vtb_column_map(TestVtbRealLayout()._rows()[0])
        assert (a["prihod"], a["rashod"], a["komis"], a["desc"]) == (3, 4, 5, 6)


class TestVtbCommissionColumn:
    """В колонку «Комиссия» ВТБ кладёт и списания, и зачисления (кешбэк) при нулевых
    Приход/Расход. Знак — только из описания: на реальной майской выписке кешбэк 656 ₽
    уходил в расход, и приход недосчитывался ровно на 656 ₽ против итогов банка."""

    def _table(self, amount, description):
        return [[
            ["Дата и время\nоперации", "Дата обработки\nбанком",
             "Сумма операции в\nвалюте операции",
             "Сумма операции в валюте\nсчета/карты", "", "Комиссия", "Описание операции"],
            ["", "", "", "Приход", "Расход", "", ""],
            ["07.05.2026\n13:41:20", "07.05.2026", "0.00 RUB", "0\nRUB", "0\nRUB",
             amount, description],
        ]]

    def test_cashback_in_commission_column_is_income(self):
        t = _vtb_table_to_transactions(self._table("656.00\nRUB",
                                                   "Зачисление кешбэка по программе лояльности."))
        assert t[0]["type"] == "income"
        assert t[0]["amount"] == pytest.approx(656.00)

    def test_commission_in_commission_column_is_expense(self):
        t = _vtb_table_to_transactions(self._table("69.01\nRUB", "Комиссия за обслуживание счета."))
        assert t[0]["type"] == "expense"
        assert t[0]["amount"] == pytest.approx(69.01)

    @pytest.mark.parametrize("desc", [
        "Зачисление кешбэка по программе лояльности.",
        "Возврат средств за отменённую покупку",
        "Начисление процентов на остаток",
    ])
    def test_credit_markers(self, desc):
        assert _vtb_table_to_transactions(self._table("100.00", desc))[0]["type"] == "income"

    @pytest.mark.parametrize("desc", [
        "Комиссия за обслуживание счета.",
        "Оплата за пролонгацию пакета Карты+.",
    ])
    def test_debit_markers(self, desc):
        assert _vtb_table_to_transactions(self._table("100.00", desc))[0]["type"] == "expense"


class TestRaiffeisenTemplates:
    """Три реальных шаблона Райффайзена. RU и EN ЗЕРКАЛЬНЫ: на месте англоязычного
    «Debit» в русском стоит «Поступления». А в шаблоне без колонки «№» движение идёт
    знаковой суммой — парсер требовал номер в первой ячейке и отбрасывал такой файл
    целиком (0 операций на двух живых выписках)."""

    RU = [[
        ["№ П/П", "Дата операции", "Номер\nдокумента", "Поступления", "Расходы",
         "Детали операции", "Номер\nкарты"],
        ["", "Выполнена банком", "", "", "", "", ""],
        ["1", "17.01.2025 17:30\n17", "ZP001", "", "- 2 670,12 ₽", "Телефон получателя", ""],
        ["2", "01.11.2024 11:36\n01", "", "+ 8 000,00 ₽", "", "Татьяна Анатольевна", ""],
        ["", "Количество операций", "", "3", "4", "", ""],
    ]]
    EN = [[
        ["№ P/P", "Posting date", "Document number", "Debit", "Credit",
         "Payment details", "Card\nnumber"],
        ["", "Executed by the bank", "", "", "", "", ""],
        ["1", "17.01.2025 17:30\n17", "ZP001", "- 2 670,12 ₽", "", "Телефон получателя", ""],
        ["8", "07.10.2024 17:44\n07", "C001", "", "+ 11,38 ₽", "Кэшбэк за сентябрь", ""],
    ]]
    NO_NUM = [[
        ["Дата операции", "Номер\nдокумента", "Сумма в валюте\nоперации",
         "Сумма в валюте\nсчета", "Детали операции", "Номер\nкарты"],
        ["Выполнена банком", "", "", "", "", ""],
        ["17.01.2025 17:30\n17", "ZP001", "- 2 670,12 ₽", "- 2 670,12 ₽", "Телефон", ""],
        ["17.01.2025 16:10\n17", "", "+ 3 000,00 ₽", "+ 3 000,00 ₽", "Игорь М.", ""],
    ]]
    NO_NUM_EN = [[
        ["Date of operation", "Document number", "Amount in currency\nof operation",
         "Amount in currency\nof account", "Description", "Card\nnumber"],
        ["Executed by the bank", "", "", "", "", ""],
        ["17.01.2025 17:30\n17", "ZP001", "- 2 670,12 ₽", "- 2 670,12 ₽", "Телефон", ""],
    ]]

    def test_ru_postuplenia_is_income(self):
        t = _raif_table_to_transactions(self.RU)
        assert [x["type"] for x in t] == ["expense", "income"]
        assert t[1]["amount"] == pytest.approx(8000.0)

    def test_en_columns_are_mirrored(self):
        t = _raif_table_to_transactions(self.EN)
        assert [x["type"] for x in t] == ["expense", "income"]
        assert t[1]["amount"] == pytest.approx(11.38)

    def test_summary_row_is_not_an_operation(self):
        # «Количество операций 3 4» — служебная строка, а не операция на 3 и 4 рубля.
        assert len(_raif_table_to_transactions(self.RU)) == 2

    def test_template_without_number_column(self):
        t = _raif_table_to_transactions(self.NO_NUM)
        assert [x["type"] for x in t] == ["expense", "income"]
        assert t[0]["amount"] == pytest.approx(2670.12)
        assert t[0]["description"] == "Телефон"

    def test_template_without_number_column_english(self):
        t = _raif_table_to_transactions(self.NO_NUM_EN)
        assert len(t) == 1 and t[0]["type"] == "expense"

    def test_column_map_differs_per_template(self):
        assert _raif_column_map(self.RU[0])["credit"] == 3
        assert _raif_column_map(self.EN[0])["credit"] == 4
        assert "account" in _raif_column_map(self.NO_NUM[0])
        assert "account" in _raif_column_map(self.NO_NUM_EN[0])


class TestBankDetection:
    """Банк определяется по содержимому файла. Ни имя файла, ни выбор в форме не
    показатель: на реальном наборе угадывание по имени трижды отправило выписку не в тот
    парсер и дало ложный ноль на исправных файлах."""

    @pytest.mark.parametrize("text,bank", [
        ("Спасибо, что Вы с нами! Всегда Ваш, Банк ВТБ (ПАО)", "vtb"),
        ("АО «Райффайзенбанк», 119002, Москва, Смоленская-Сенная", "raiffeisen"),
        ("AO Raiffeisenbank, 119002, Moscow", "raiffeisen"),
        ("ПАО Сбербанк. Выписка по платёжному счёту", "sber"),
        ("Сайт: www.gazprombank.ru", "gazprom"),
        ("АО «Альфа-Банк», Москва", "alfa"),
        ("Выписка по договору №5712737765", "tinkoff"),
    ])
    def test_detect_by_content(self, text, bank):
        assert detect_bank(text) == bank

    def test_unknown_bank_returns_none(self):
        assert detect_bank("Просто текст без реквизитов банка") is None

    def test_nfd_text_still_detected(self):
        # macOS отдаёт NFD: «й» = «и» + U+0306. Без NFC-нормализации маркер «райффайзен»
        # молча не находится — именно так реальные выписки уходили не в тот парсер.
        nfd = unicodedata.normalize("NFD", "АО «Райффайзенбанк», Москва")
        assert "райффайзен" not in nfd.lower()  # подтверждаем саму ландмайну
        assert detect_bank(nfd) == "raiffeisen"

    @pytest.mark.parametrize("template,bank", [
        ("vtb.pdf", "vtb"),
        ("raiffeisen.pdf", "raiffeisen"),
    ])
    def test_detect_pdf_bank_on_templates(self, template, bank):
        assert detect_pdf_bank((TPL / template).read_bytes()) == bank

    def test_detect_pdf_bank_on_broken_pdf(self):
        assert detect_pdf_bank(b"%PDF-broken") is None


class TestNonStatementFalsePositives:
    """Детектор справок не должен принимать настоящую выписку за справку: цена ошибки —
    отказ импортировать исправный файл."""

    @pytest.mark.parametrize("template", ["vtb.pdf", "raiffeisen.pdf", "tinkoff.pdf",
                                          "sber.pdf"])
    def test_statement_templates_are_not_certificates(self, template):
        assert pdf_non_statement_reason((TPL / template).read_bytes()) is None

    def test_statement_named_spravka_is_not_a_certificate(self):
        # Реальная выписка Тинькоффа называется «Справка о движении средств» — маркер
        # не должен цепляться за слово «справка» как таковое.
        assert classify_non_statement("Справка о движении средств\n15.01.26 Пятёрочка") is None

    def test_broken_pdf_reason_is_none(self):
        assert pdf_non_statement_reason(b"%PDF-broken") is None


class TestSberNonCashOperations:
    """Изменение кредитного лимита — не движение денег. На реальной выписке по кредитной
    карте «Установка/Увеличение кредитного лимита» проходило строкой «Прочие операции
    +110 000,00» и давало 220 000 ₽ фиктивного дохода: для СППР это отравленный вход."""

    def test_credit_limit_increase_is_not_income(self):
        lines = [
            "15.10.2025 14:43 Прочие операции +110 000,00 220 000,00",
            "15.10.2025 AUTH1 Увеличение кредитного лимита (с акцептом)",
            "13.07.2025 18:56 Перевод на карту +1 488,00 110 000,00",
            "13.07.2025 AUTH2 Перевод от П. Игорь Николаевич",
        ]
        t = _sber_text_to_transactions(lines)
        assert len(t) == 1
        assert t[0]["type"] == "income" and t[0]["amount"] == pytest.approx(1488.0)

    def test_credit_limit_setup_is_not_income(self):
        lines = [
            "25.09.2024 18:30 Прочие операции +110 000,00 110 000,00",
            "25.09.2024 AUTH0 Установка кредитного лимита. Операция по счёту",
        ]
        assert _sber_text_to_transactions(lines) == []

    def test_regular_operations_still_parsed(self):
        lines = [
            "27.09.2024 15:32 Рестораны и кафе 230,00 110 000,00",
            "27.09.2024 AUTH3 KOFEYNYA MOSCOW",
        ]
        t = _sber_text_to_transactions(lines)
        assert len(t) == 1 and t[0]["type"] == "expense"


class TestOneCEncoding:
    """1C от банков РФ — windows-1251. Декодер форсит cp1251 по магии `1CClientBankExchange`,
    не полагаясь на «utf-8 удачно упал» (на других файлах может не упасть → каша)."""

    def test_decode_forces_cp1251_for_1c(self):
        raw = (TPL / "sberbank_1c_cp1251.bin").read_bytes()
        content = decode_statement_bytes(raw)
        assert content.startswith("1CClientBankExchange")
        assert "СекцияДокумент" in content  # кириллица раскодирована верно

    def test_cp1251_1c_parses_correctly(self):
        raw = (TPL / "sberbank_1c_cp1251.bin").read_bytes()
        txns = parse_bank_statement(decode_statement_bytes(raw))
        assert len(txns) == 2
        assert txns[0]["type"] == "expense" and txns[0]["amount"] == pytest.approx(5000.0)
        assert txns[1]["type"] == "income" and txns[1]["amount"] == pytest.approx(90000.0)

    def test_utf8_1c_still_parses(self):
        raw = (TPL / "sberbank_1c.txt").read_bytes()
        assert len(parse_1c_exchange(decode_statement_bytes(raw))) == 2

    def test_decode_csv_utf8(self):
        raw = "Дата;Сумма\n01.01.2026;-100.00\n".encode("utf-8")
        assert decode_statement_bytes(raw).startswith("Дата")


class TestNonStatementDetection:
    """Справки об остатке/реквизиты/о задолженности — не выписки. Операций нет; приложение
    должно распознать тип, а не показать «пустую выписку» (silent-0 опасен)."""

    @pytest.mark.parametrize("text,expected", [
        ("СберБанк\nСправка о доступном остатке\nПетров", "справка о доступном остатке"),
        ("Реквизиты счёта\n40817...", "реквизиты счёта"),
        ("Реквизиты счета для перевода", "реквизиты счёта"),
        ("Справка о задолженности по кредитным продуктам", "справка о задолженности"),
        ("Справка о видах и размерах пенсий", "справка о выплатах/пенсиях"),
        ("Справка о состоянии вклада", "справка о состоянии вклада"),
        ("Сведения о наличии счетов и иной информации", "сведения о наличии счетов"),
        ("Заказано в СберБанк Онлайн\nСправка по арестам и взысканиям",
         "справка по арестам и взысканиям"),
        ("Для предоставления по месту требования\nС П Р А В К А", "справка банка"),
        ("CERTIFICATE\nClient: EVDOKIMOV VASILII", "справка банка (англ.)"),
        # Альфа-Банк отдаёт текст слитно, без пробелов — матчинг обязан это переживать
        ("кодподразделения500-114)имеетоткрытыйсчёт:", "справка о наличии счёта"),
    ])
    def test_certificates_detected(self, text, expected):
        assert classify_non_statement(text) == expected

    def test_real_statement_not_flagged(self):
        # Настоящая выписка операций не должна опознаваться как справка.
        text = "Выписка по платёжному счёту\n02.07.2025 13:28 Перевод 550,00 0,00"
        assert classify_non_statement(text) is None


class TestUniversalCsvRealDefects:
    """Дефекты универсального CSV-парсера, найденные контролем полноты разбора на живых
    файлах. Каждый был невидим: количество операций выглядело правдоподобно."""

    def test_postupleniya_column_is_income(self):
        # «поступление» — НЕ подстрока «Поступления» (последняя буква другая). Из-за этого
        # на реальной выписке Райффайзена терялись ВСЕ приходы: 14 строк → 8 операций,
        # и в модель попадал человек без единого дохода.
        content = (
            "Дата операции;Выполнено банком;Номер документа;Поступления;Расходы;Валюта\n"
            "17.01.2025 17:30;17.01.2025;ZP001;;2 670,12;RUB\n"
            "17.01.2025 17:29;17.01.2025;ZP002;2 670,12;;RUB\n"
        )
        parsed = parse_universal_csv(content)
        assert [t["type"] for t in parsed] == ["expense", "income"]

    def test_amount_candidate_excludes_credit_debit_columns(self):
        # «Amount in operation currency (credit)» ловится и кандидатом «amount», и «credit».
        # Побеждал «amount» — и вся выписка читалась как доход (расход = 0).
        content = (
            "Transaction date;Amount in operation currency (credit);"
            "Amount in operation currency (debit);Operation details\n"
            "17.01.2025;;2 670,12;Оплата\n"
            "18.01.2025;8 000,00;;Перевод\n"
        )
        parsed = parse_universal_csv(content)
        assert [t["type"] for t in parsed] == ["expense", "income"]

    def test_metadata_pair_is_not_a_header(self):
        # Банк печатает над таблицей пары «метка — значение». Строка
        # «Дата открытия счета | 24.12.2018 | Поступления | 224 805,37» содержит и «дату»,
        # и «поступления» — и принималась за шапку: разбор давал 0 операций.
        content = (
            "Выписка по счету\n"
            "Дата открытия счета;24.12.2018;Поступления;224 805,37 RUR\n"
            "Валюта счета;RUR;Расходы;221 195,56 RUR\n"
            "\n"
            "Дата операции;Категория;Сумма в валюте счета;Описание\n"
            "05.05.2026;Кафе;-450,00;Кофейня\n"
            "06.05.2026;Доход;30 000,00;Зарплата\n"
        )
        parsed = parse_universal_csv(content)
        assert len(parsed) == 2
        assert parsed[0]["type"] == "expense" and parsed[0]["description"] == "Кофейня"
        assert parsed[1]["type"] == "income"

    def test_report_counts_rows_and_reasons(self):
        content = (
            "Дата операции;Категория;Сумма;Описание\n"
            "05.05.2026;Кафе;-450,00;Кофейня\n"
            "Страница 1 из 1;;;\n"
        )
        report: dict = {}
        parse_universal_csv(content, report)
        assert report["rows"] == 2 and report["parsed"] == 1
        assert report["skipped"] == {"служебная строка (не операция)": 1}


class TestTinkoffCsvReport:
    def test_failed_rows_counted_as_bank_rejection(self):
        content = (
            "Дата операции;Дата платежа;Номер карты;Статус;Сумма операции;Валюта операции;"
            "Сумма платежа;Валюта платежа;Кэшбэк;Категория;MCC;Описание\n"
            "15.01.2026 12:30:00;15.01.2026;*1;OK;-100.00;RUB;-100.00;RUB;0;Еда;5411;Магнит\n"
            "16.01.2026 12:30:00;16.01.2026;*1;FAILED;-500.00;RUB;-500.00;RUB;0;Прочее;;Отмена\n"
        )
        report: dict = {}
        parsed = parse_tinkoff_csv(content, report)
        assert len(parsed) == 1
        assert report["skipped"] == {"операция отклонена банком": 1}

    def test_en_thousands_format_not_lost(self):
        # Наивный float() ломался на «1,234.56» и ронял строку в except — операция
        # исчезала молча. Теперь сумма читается через `_num`.
        content = (
            "Дата операции;Статус;Сумма платежа;Описание\n"
            "15.01.2026 12:30:00;OK;-1,234.56;Покупка\n"
        )
        report: dict = {}
        parsed = parse_tinkoff_csv(content, report)
        assert len(parsed) == 1
        assert parsed[0]["amount"] == pytest.approx(1234.56)
        assert report["skipped"] == {}
