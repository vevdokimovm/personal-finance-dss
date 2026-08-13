# Проверка: ROUND_HALF_UP — объективно правильный выбор для этого продукта, или произвол?

**Тип материала:** внешний веб-ресёрч (WebSearch), подпадает под правило §18 в полном
смысле — получено извне, не гарантированно воспроизводимо дословно повторным поиском.

**Дата:** 2026-08-13. **Повод:** владелец усомнился в ходе батча v8.19.2 (Decimal в
`amortization.py`), правильно ли применять ROUND_HALF_UP, увидев конкретный кейс
(0.125₽ → 0.13₽ по канону против 0.12₽ у `round()` из stdlib) — не хочет слепо повторять
то, что уже написано в скилле `finpilot-money-format`, без проверки.

**Разметка уверенности:** [Ф] = подтверждено первоисточником в выдаче, [О] = вывод из
нескольких источников поиска.

---

## Запрос 1 — российская налоговая практика

Query: `НК РФ округление копеек до рубля правило 50 копеек округляется`

[Ф] Согласно п. 6 ст. 52 НК РФ: сумма налога исчисляется в полных рублях. Сумма налога
менее 50 копеек отбрасывается, сумма 50 копеек и более округляется до полного рубля —
классическое арифметическое округление (round half up / round half away from zero для
положительных чисел), не банковское round-half-even.

[Ф] Оговорка из выдачи: правило п. 6 ст. 52 НК НЕ применяется к НДС в счетах-фактурах и
не универсально для всех налогов/взносов — т.е. это не абсолютный закон для любых
денежных расчётов в РФ, а конкретная норма для конкретного контекста (исчисление суммы
налога к уплате).

Источники:
- [Порядок округления копеек до целых рублей при исчислении НДС — ФНС России](https://www.nalog.gov.ru/rn73/news/tax_doc_news/4801518/)
- [Как правильно округлять суммы налогов и взносов? — Бухгалтерия.ru](https://www.buhgalteria.ru/article/kak-pravilno-okruglyat-summy-nalogov-i-vznosov-)
- [Округление НДС до копеек — КонсультантПлюс](https://www.consultant.ru/law/podborki/okruglenie_nds_do_kopeek/)
- [О порядке округления... НДС — ФНС России, г. Москва](https://www.nalog.gov.ru/rn77/taxation/taxes/nds/4615493/)
- [Декларация УСН: в рублях или копейках — reg.ppt.ru](https://reg.ppt.ru/deklaratsiya-usn-v-rublyakh.do)
- [Как правильно округлять суммы налогов и взносов — Клерк.ру](https://www.klerk.ru/buh/articles/586677/)
- [Округление НДФЛ — калькулятор — calc.ru](https://www.calc.ru/Okrugleniye-Ndfl.html)

## Запрос 2 — международная практика банковского/финансового округления

Query: `банковское округление half-even vs round half up financial calculations best practice`

[О] Round-half-to-even (banker's rounding) минимизирует систематическое смещение суммы
ВВЕРХ при округлении большого количества независимых значений — это причина, по которой
это дефолтный режим IEEE 754 (стандарт арифметики с плавающей точкой) и стандарт ASTM E29
(аналитическая химия), а также одобренный метод для налоговых расчётов IRS (США).

[О] При этом «традиционная финансовая отчётность часто по умолчанию использует round
half up» ("traditional financial reporting often defaulting to round half up") —
выбор метода зависит от контекста и регуляторных требований, а не универсален.

Источники:
- [Banker's Rounding Rule — Python in Plain English](https://python.plainenglish.io/bankers-rounding-rule-29629e44a17a)
- [Banker's Rounding (Round Half to Even) in Dart — Medium](https://medium.com/@firunath/bankers-rounding-round-half-to-even-in-dart-9526479002ef)
- [Beyond the 5: Why Scientists Use Banker's Rounding — Chem.Academy](https://chem.academy/notes/bankers-rounding.html)
- [SQL SERVER — Banker's Rounding — SQL Authority](https://blog.sqlauthority.com/2023/08/15/sql-server-bankers-rounding/)
- [Rounding: Half-Up vs. Bankers — calcufacil.com](https://calcufacil.com/en/rounding-half-up-bankers/)
- [Banker's Rounding Calculator — roundingcalculators.com](https://www.roundingcalculators.com/calculators/bankers-rounding)
- [Rounding Calculator — microapp.io](https://microapp.io/rounding-calculator/)
- [Bankers Rounding | Round Half to Even Explained — roundingcalculators.com](https://www.roundingcalculators.com/guides/bankers-rounding)
- [What is Banker's Rounding and Why Does It Matter? — roundingsolver.com](https://www.roundingsolver.com/blog/bankers-rounding/)

## Синтез (для батча v8.19.2)

Правило не универсально — выбор зависит от того, что оптимизируется:

- **Round-half-even** оправдан, когда суммируются МНОГО независимых округлений и важна
  статистическая точность суммы (научные расчёты, агрегированная бухгалтерская
  отчётность на больших объёмах, поэтому и дефолт в IEEE 754/железе).
- **Round-half-up** оправдан, когда пользователь должен свести КОНКРЕТНУЮ строку с тем,
  что посчитает вручную/калькулятором/банковской выпиской — это ровно контекст
  `docs/api/openapi.json`-строки графика погашения долга в FINPILOT: пользователь видит
  цифру и может сверить с реальной выпиской. Round-half-even там даст цифру, которая не
  совпадёт с тем, что покажет обычный калькулятор или банк — подрыв доверия важнее
  теоретической статистической беспристрастности.

Для FINPILOT ROUND_HALF_UP — не произвольный выбор: (1) совпадает с прецедентом
российской фискальной практики (п. 6 ст. 52 НК РФ — та же логика «≥50 копеек вверх»,
хоть и не буквально применимая норма к этому конкретному расчёту), (2) совпадает с тем,
что ожидает и может проверить вручную пользователь, (3) уже был решением проекта ДО
этого батча (`app/core/money.py`, скилл `finpilot-money-format`) — батч v8.19.2 не
вводит новое правило, а устраняет место (`amortization.py`), которое использовало
`round()` из stdlib (round-half-even) в обход уже принятого канона.
