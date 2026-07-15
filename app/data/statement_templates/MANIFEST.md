# Эталонные шаблоны банковских выписок

Синтетические образцы (не реальные выписки) в формате каждого банка. Golden-фикстуры
для `tests/test_statement_templates.py`, эталон формата и образец для пользователя.
Регенерация: `python -m tools.statement_templates.build_templates`.

| Файл | Формат | Парсер | bank_id | Операций |
|---|---|---|---|---|
| `tinkoff.csv` | CSV (`;`, BOM) | `parse_tinkoff_csv` | tinkoff | 2 (+1 FAILED отсеяна) |
| `sber.csv` | CSV (`;`) | `parse_sber_csv` | sber | 2 |
| `universal_single.csv` | CSV знаковая | `parse_universal_csv` | universal | 2 |
| `universal_split.csv` | CSV (split Приход/Расход) | `parse_universal_csv` | universal | 2 |
| `universal.xlsx` | XLSX | `parse_xlsx` | universal | 2 |
| `tinkoff.pdf` | PDF (текст) | `parse_tinkoff_pdf` | tinkoff | 2 |
| `sber.pdf` | PDF (текст, описание на след. строке) | `parse_sber_pdf` | sber | 2 |
| `vtb.pdf` | PDF (таблица, знаковая сумма) | `parse_vtb_pdf` | vtb | 2 |
| `raiffeisen.pdf` | PDF таблица (Поступления/Расходы) | `parse_raiffeisen_pdf` | raiffeisen | 2 |
| `sberbank_1c.txt` | 1CClientBankExchange | `parse_1c_exchange` | — | 2 |

Стратегия покрытия ~200 банков — `docs/universal_statement_parser_strategy.md`:
5 выделенных парсеров под крупные банки + универсальный (CSV/XLSX по эвристикам
колонок) + 1C-обмен покрывают длинный хвост без парсера на каждый банк.
