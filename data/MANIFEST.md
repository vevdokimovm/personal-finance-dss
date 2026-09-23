# Каталог данных FINPILOT

Реальные ряды, на которых калибруется и проверяется ядро. До 17.09.2026 продукт
считал на синтетике экспертов; этот каталог её замещает.

**Что это.** 39 нормализованных CSV (35 фаз B1–B2 + 4 прогона A3), единый формат колонок:
`date, value, unit, region, breakdown`. UTF-8, десятичный разделитель — точка,
дата — ISO (`YYYY-MM-DD`), для периодов ставится **дата конца периода**
(квартал → 31 марта, год → 31 декабря), для месячных индексов — первое число
месяца. Пустая `region` не встречается: агрегат по стране помечен `RU`,
мировые ряды — кодом страны ISO-3 или `WORLD`. `breakdown` держит разрез;
вложенные разрезы разделяются `|`.

**Как обновлять.** Оригиналы лежат ВНЕ репозитория, в
`~/raw-originals/finpilot-data/<источник>/` (правило СТ-001), их реквизиты —
в `MANIFEST_sha256_2026-09-17.txt` рядом с ними. Каждый CSV получается
скриптом из `tools/data/`:

```
python -m tools.data.build_rosstat_income        # распределение дохода + логнормаль
python -m tools.data.build_cbr_rates             # курсы, ключевая ставка, RUONIA
python -m tools.data.build_moex                  # индексы MOEX
python -m tools.data.build_rosstat_prices        # ИПЦ, веса корзины, сбережение, ПМ
python -m tools.data.build_cbr_bank_rates        # ставки банков физлицам
python -m tools.data.build_rosstat_obdh          # ОБДХ по децилям (нужен unar)
python -m tools.data.build_cbr_pdn               # ПДН и NPL (нужен pdftotext)
python -m tools.data.build_rosstat_housing       # цены жилья и аренды
python -m tools.data.build_rosstat_demography    # браки, разводы, возраст
python -m tools.data.build_reference             # мир, ZCYC, МПЛ, топ-10, золото
python -m tools.data.build_a3_reference          # НПФ, цены целей, комиссии ПИФ, дожитие
```

Каталог оригиналов переопределяется `--raw-dir` или переменной
`FINPILOT_RAW_DIR`, каталог назначения — `--out-dir`. Повторный прогон на тех же
оригиналах даёт **побайтово те же файлы** (проверено 17.09.2026 сравнением
`diff -rq` полного пересбора; повторно в прогоне B2 — 35 из 35 файлов совпали
по sha256 после исправления четырёх скриптов, дублей ключа `date+unit+region+breakdown`
ни в одном файле нет).

**Чего здесь намеренно НЕТ.**
- Сырья: ни одного `.xlsx`, `.rar`, `.pdf` — только производные CSV.
  Бюджет каталога 30 МБ, занято 21 МБ (после A3: +6,6 МБ цены целей, +1,8 МБ дожитие).
- Микроданных по людям: панели домохозяйств (RLMS, «Ромир») либо платные,
  либо разрешены только для исследований — в коммерческий продукт нельзя.
- Внутридневных котировок и поминутной кривой ОФЗ: дневного шага ядру хватает,
  внутридневной поток — мегабайты на дату.
- Образцов выписок: они не данные продукта, а фикстуры тестов, лежат
  в `tests/fixtures/statements/` (см. раздел «Фикстуры парсера» ниже).
- Персональных данных: ни в каком виде и ни при каких условиях.

---

## Реестр рядов

Лицензии даны прямым ответом на вопрос «можно ли использовать в коммерческом
продукте», а не «открыты ли данные».

### Росстат — общий режим

Официальная статистическая информация Росстата общедоступна; распространение
свободное **со ссылкой на источник** (ФЗ-282 «Об официальном статистическом
учёте», ст. 4 и 5). 🔴 **В коммерческом продукте использовать можно при
указании источника.** Ниже это не повторяется в каждой строке.
Те же показатели в ЕМИСС (`fedstat.ru`, оператор — Росстат) публикуются
под **CC BY 3.0** (подвал портала, сверено 17.09.2026): коммерческое использование
разрешено с указанием источника — режим тот же, вывод не меняется.

| Файл | Оригинал и sha256 | Шаг · глубина | Уровень | Чем полезен ядру |
|---|---|---|---|---|
| `rosstat_income_distribution_year.csv` | `rosstat_ineq/NB_RD_1-2-8.xlsx`, `2a2baa09…610f3752`, снимок 17.09.2026, `rosstat.gov.ru/storage/mediabank/NB_RD_1-2-8.xlsx` | год · 1995–2025 · все субъекты | человек (душевой доход) | фактическая форма распределения дохода |
| `rosstat_income_lognormal_year.csv` | то же | год · 1995–2025 · все субъекты | человек | 🔴 σ, медиана и квантили логнормали — прямой вход генератора когорт вместо константы |
| `rosstat_cpi_month.csv` | `rosstat/rosstat_ipc_mes_08-2026.xlsx`, `4ef8b1d7…621f6ebf` | месяц · 1991–08.2026 | агрегат | инфляционный фон прогноза |
| `rosstat_cpi_kipc_year.csv` | `rosstat/rosstat_ipc-KIPC_2010-2025.xlsx`, `32b8e201…400d3dd9` | год · 2010–2025 | агрегат | 🔴 инфляция ПО КАТЕГОРИИ ЦЕЛИ, а не «средняя по больнице». ⚠️ До B2 (17.09.2026) не было 2022 года целиком — колонка подписана `20221)` (год + сноска); скрипт исправлен |
| `rosstat_cpi_basket_weights_year.csv` | `rosstat/rosstat_Vesa-tov-KIPC_2012-2026.xlsx`, `969a6921…98901ce3` | год · 2012–2026 | агрегат | структура трат условного домохозяйства. ⚠️ До B2 из сводного листа бралась только колонка 2012 года — 2013–2021 отсутствовали; скрипт исправлен. Веса 2022 «до 01.04» датированы `2022-03-31`, «с 01.04» — `2022-12-31` |
| `rosstat_income_use_quarter.csv` | `rosstat/rosstat_urov_13kv_2kv2026.xlsx`, `52a0a45d…c785d1b6` | квартал · 2013–II кв. 2026 | агрегат | 🔴 норма сбережения и её сезонность |
| `rosstat_subsistence_minimum.csv` | `rosstat/rosstat_vpm_RF_kv.xlsx` `76af72af…2c1b320a`, `rosstat_vpm-643_2021-2026.xlsx` `25a900bb…43570058` | квартал 2000–2020, год 2021–2026 | человек | нижняя граница расходов, порог «неприкосновенного» |
| `rosstat_obdh_decile_level_year.csv` | `rosstat_obdh/*.rar` (`DRP_2024` `b9934e7d…d18bd109`, `DRP_2025` `73eee9e1…7047e37e`, `dox_rasx_potreb_2022` `bb3a8091…5e07d715`, `_2023` `5786fad6…1619aecf`) | год · 2021–2025 | домохозяйство (на члена) | 🔴 сколько рублей тратит каждый дециль и на что |
| `rosstat_obdh_decile_structure_year.csv` | то же | год · 2021–2025 | домохозяйство | структура расходов в процентах по децилям |
| `rosstat_housing_price_m2_region_quarter.csv` | `rosstat_housing/sred_cen_{perv,vtor}_*.xlsx` (`b8110ffb…851d72b6`, `b6568a1f…18c4a8ce`, `5acd5c2f…15da9a51`, `f9e1659d…3789f601`, `3c4965d7…f912ee4b`, `139a12c0…6e776cde`) | квартал · 2021, 2025–II кв. 2026 · субъекты | агрегат | цена цели «квартира» по региону |
| `rosstat_commercial_rent_m2_region_quarter.csv` | `rosstat_housing/Nedvijimost_arenda_Cena_2kv-2026.xlsx`, `afdd037b…797b3d0e` | квартал · 2025–II кв. 2026 · субъекты | агрегат | ⚠️ аренда **коммерческой** недвижимости; жилой аренды в открытой статистике нет |
| `rosstat_marriages_divorces_year.csv` | `rosstat_demo/demo31_2023.xlsx` `855df528…37b7071f`, `demo32_2023.xlsx` `bc75b90d…affaf1be` | год · 1950–2021 | агрегат | частота жизненных событий, вокруг которых ставятся цели |
| `rosstat_population_age_groups.csv` | `rosstat_demo/demo14.xlsx`, `641eb733…df7d5785` | год · 1926–2021 | агрегат | возрастной профиль пользователя. `breakdown` начинается с `total`, `urban` или `rural` (разрез добавлен в B2: до него три блока сливались под одной подписью) |

### Банк России

Материалы Банка России — публичная информация; использование свободное
**со ссылкой на источник**, ограничения на коммерческое использование нет.
🔴 **В продукт можно при указании источника.**

| Файл | Оригинал и sha256 | Шаг · глубина | Уровень | Чем полезен ядру |
|---|---|---|---|---|
| `cbr_fx_usd_rub_daily.csv` | `cbr/cbr_usd_rub_daily_1992_2026.xml`, `2e1b5fc8…44af9e04` | день · 01.07.1992–17.09.2026 | агрегат | волатильность среды, валютные цели |
| `cbr_fx_eur_rub_daily.csv` | `cbr/cbr_eur_rub_daily_1999_2026.xml`, `1598e855…68890e38` | день · с 1999 | агрегат | то же по евро |
| `cbr_fx_cny_rub_daily.csv` | `cbr/cbr_cny_rub_daily_2010_2026.xml`, `40c643e9…df1c4595` | день · с 2010 | агрегат | то же по юаню |
| `cbr_fx_usd_rub_volatility_month.csv` | производный от USD/RUB | месяц · 1992–2026 | агрегат | 🔴 σ и **режим среды** (calm/stress/crisis) вместо одной константы |
| `cbr_key_rate_daily.csv` | `cbr/cbr_key_rate_daily_2013_2026.xml`, `97b38dda…705cbf8d` | день · с 13.09.2013 | агрегат | якорь ставок, ставка дисконтирования |
| `cbr_ruonia_daily.csv` | `cbr/cbr_ruonia_daily_2010_2026.xml`, `081e1e5d…be834df9` | день · с 2010 | агрегат | безрисковая ставка овернайт |
| `cbr_loan_rate_individuals_month.csv` | `cbr/cbr_int_rat_loans_ind_new.xlsx`, `f8fbaa15…4f161218` | месяц · с 01.2014, по срокам | агрегат | ставка нового долга в модуле долгов |
| `cbr_deposit_rate_individuals_month.csv` | `cbr/cbr_int_rat_deposits.xlsx`, `14a61745…535d9c04` | месяц · с 01.2014, по срокам | агрегат | доходность подушки и вкладов. 🔴 **Только вклады физлиц** — до B2 (17.09.2026) в файл попадал и соседний блок депозитов нефинансовых организаций под теми же подписями сроков; скрипт исправлен |
| `cbr_loan_rate_individuals_region_month.csv` | `cbr/cbr_int_rat_loans_ind_by_region_new.xlsx`, `803384cf…29c387de` | месяц · с 01.2019 · округа | агрегат | региональная поправка к ставке |
| `cbr_deposit_rate_individuals_region_month.csv` | `cbr/cbr_int_rat_deposits_ind_by_region.xlsx`, `b0ca8ea4…5f328e01` | месяц · с 01.2019 · округа | агрегат | то же по вкладам |
| `cbr_deposit_rate_top10_decade.csv` | `cbr_ref/avgprocstav_table.html`, `2ef5b242…ff5810e8` | декада · 2010–09.2026 | агрегат | «ставка, которую реально видит человек в топ-банке» |
| `cbr_pdn_distribution.csv` | `cbr_finstab/4q_2025_1q_2026.pdf`, `d2c6709e…216b96f7` | квартал · 2022–I кв. 2026 | агрегат | 🔴 доля выдач и портфеля по ПДН и NPL 30+ — замена экспертной вероятности дефолта |
| `cbr_mpl_limits.csv` | `cbr_mpl/Macroprudential_limits_banks_01072025.xlsx`, `0126f39b…37909cbb` | квартал · с 01.07.2025 | агрегат | регуляторные пороги ПДН как справочник рантайма |

### Московская биржа

🔴 **Осторожно с лицензией.** ISS отдаёт данные без ключа и без регистрации,
но **на распространение данных MOEX нужен договор с биржей**. Практический
вывод: считать внутри продукта (калибровка σ, бэктест) — допустимо; **показывать
котировки и индексы как сервис пользователю — только по договору**, который
не оплачен. Проверить «Правила использования информации» MOEX до релиза.

| Файл | Оригинал и sha256 | Шаг · глубина | Уровень | Чем полезен ядру |
|---|---|---|---|---|
| `moex_imoex_daily.csv` | `moex/moex_IMOEX_daily.csv`, `4c236425…f745b697` | день · с 1997 | агрегат | цена акций без дивидендов |
| `moex_mcftr_daily.csv` | `moex/moex_MCFTR_daily.csv`, `1f188554…594f35c1` | день · с 2003 | агрегат | 🔴 честная полная доходность акций (с дивидендами) |
| `moex_rtsi_daily.csv` | `moex/moex_RTSI_daily.csv`, `191ef4b1…2cb3c6f6` | день · с 1995 | агрегат | тот же рынок в долларах |
| `moex_rgbi_daily.csv` | `moex/moex_RGBI_daily.csv`, `47e94411…d8cfbdf1` | день · с 2002 | агрегат | 🔴 колонка `yield` — рыночная цена безрискового времени |
| `moex_rgbitr_daily.csv` | `moex/moex_RGBITR_daily.csv`, `68e1f3d7…835786c4` | день · с 2002 | агрегат | полная доходность ОФЗ |
| `moex_mredc_daily.csv` | `moex/moex_MREDC_daily.csv`, `568c110e…cba94f5d` | день · с 2016 | агрегат | дневная цена м² в Москве (ДомКлик × MOEX) |
| `ofz_zcyc_params.csv` | `moex_zcyc/zcyc_*.json` (8 снимков) | точечно · 2020–2026 | агрегат | параметры кривой ОФЗ (Нельсон—Сигель—Свенссон) для ставки на срок |

### Прогон A3 (17.09.2026)

Скрипт `tools/data/build_a3_reference.py`. Повторный прогон на тех же оригиналах дал
**побайтово те же 4 файла** (sha256 сверены 17.09.2026). Дубли ключа
`date+unit+region+breakdown` скрипт логирует; на снимке их нет.

| Файл | Оригинал, URL, sha256 | Шаг · глубина | Единицы | Лицензия · можно в продукт | Чем полезен ядру |
|---|---|---|---|---|---|
| `cbr_npf_returns_quarter.csv` | `npf/npf_stat.xlsx`, `https://www.cbr.ru/Content/Document/File/130741/npf_stat.xlsx` (страница `cbr.ru/RSCI/statistics/`), `b5b2014c…951072d9` | квартал · 31.12.2018–30.06.2026 | `percent_annual_gross` — доходность **до** вознаграждения фонда (внутригодовые точки — с начала года); `rub_mln`; `persons` | Банк России, со ссылкой · да | доходность пенсионных накоплений (ОПС) и резервов (НПО/ПДС) как параметр класса; рост участников ПДС |
| `rosstat_goal_prices_month.csv` | `goal_prices/sred_potreb_cen_{2022,2023,2024,2025}.xlsx`, `sred_potreb_cen_08-2026.xlsx`, `https://rosstat.gov.ru/storage/mediabank/<файл>` (страница `rosstat.gov.ru/statistics/price`); sha256 `94d58542…2d57a2c6`, `6fb42977…572359ed`, `b35330ad…2f995ef3`, `0ac8adc8…03d567ec`, `0303a5fc…94d8f96c` | месяц · 01.2022–08.2026 · РФ, федеральные округа, субъекты (города отброшены) | `rub` за единицу позиции (дата — первое число месяца, цена Росстата «на конец периода») | Росстат, ФЗ-282, со ссылкой · да | цена цели по региону: `car_domestic_new`, `car_foreign_new`, `car_imported_used` (шт.), `kasko_year`, `driving_course`, `university_state_semester`, `university_private_semester`, `college_semester` (семестр), `school_private_month`, `kindergarten_day`, `language_course_hour`, `trip_black_sea_russia`, `trip_turkey`, `trip_excursion_russia` (поездка), 🔴 `rent_flat_1room_month`, `rent_flat_2room_month` (аренда квартиры у частных лиц, месяц — **закрывает запись «аренды жилья в открытой статистике нет»**). Коды позиций Росстата — в `GOAL_ITEMS` скрипта |
| `cbr_fund_fees_class_snapshot.csv` | `pif/mutual_fund_data.xlsx`, `https://www.cbr.ru/Content/Document/File/193443/%20mutual_fund_data.xlsx` («Витрина данных ПИФ», `cbr.ru/RSCI/data_showcase/`), `370e5549…688aac1b` | срез · 31.07.2026 | `percent_of_nav_year`; `percent_12m`; `funds` | Банк России, со ссылкой · да. 🔴 **Не данные MOEX** — ограничение Г37 не касается | вознаграждение УК, инфраструктура, потолок прочих расходов и доходность 12 мес. — p25/медиана/p75 по `etf_bpif`/`open_opif` × классу. ⚠️ Класс (`money_market`, `bonds`, `equity`, `gold`, `mixed`, `other`) — **наше правило по названию и индексу**, не классификация ЦБ; «прочие расходы» — потолок из правил, не факт |
| `un_wpp_life_table_rus_year.csv` | `life_tables/WPP2024_Life_Table_Complete_Medium_{Male,Female}_1950-2023.csv.gz` (`https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/CSV_FILES/...`), `e304a776…af6358be`, `0e23ba8c…705b1458`; скрипт читает отфильтрованные по `LocID=643` копии `wpp2024_complete_{Male,Female}_RUS_1950-2023.csv` (`61056c28…16241a4e`, `c17cd23a…de485daf`) | год · 1950–2023 · возраст 0…100 · пол | `years` (`ex`), `probability` (`px`) | UN WPP 2024, CC BY 3.0 IGO, со ссылкой · да (🟡 футер страницы загрузки не открывался) | горизонт дожития для пенсионных целей. ⚠️ У мужчин e(0) WPP на 0,45–0,6 года ниже пересчёта по коэффициентам РосБРиС (сверка в сырье A3.1) |

### Мировой контекст

| Файл | Источники и лицензия | Можно в продукт |
|---|---|---|
| `world_benchmarks.csv` | FRED (`fred.stlouisfed.org`, 10 рядов США) и World Bank Open Data (8 показателей × страны, **CC BY 4.0** — со ссылкой). ⚠️ **Поправка B2 (17.09.2026, сверено по карточкам FRED):** не все ряды FRED — общественное достояние. `sp500` — © S&P Dow Jones Indices, «Reproduction … prohibited except with the prior written permission»; `vix` — © Cboe, «Copyrighted: Citation Required»; `mortgage_30y_rate` — © Freddie Mac, «Reprinted with permission», цитирование обязательно. Остальные 7 (TDSP, PSAVERT, SIPOVGINIUSA, CPIAUCSL, DGS10, HDTGPDUSQ163N, MEHOINUSA672N) — ведомства США | 🟡 **внутренние расчёты — да** (со ссылкой). **Показ пользователю:** World Bank и 7 рядов ведомств США — да со ссылкой; `vix` и `mortgage_30y_rate` — со ссылкой на правообладателя; 🔴 `sp500` — **нет без письменного разрешения S&P DJI**. Назначение — проверка «наши пороги не абсурдны на фоне мира», а НЕ перенос чисел на РФ |
| `lbma_gold_pm_daily.csv` | LBMA PM fixing через витрину `gold.org`, снимок 17.09.2026, `commodities/gold_pm.json` `77c9dc89…6eaf77e8` | 🟡 внутренние расчёты и стресс-тест долгих целей — да; перепубликация котировок как сервиса — предмет условий LBMA, не проверялось |

---

## Фикстуры парсера (не данные продукта)

| Набор | Лицензия | Где лежит | Можно в продукт |
|---|---|---|---|
| `Ev2geny/Sberbank2Excel` — текстовый слой выписки Сбербанка + 22 снимка вёрсток | **MIT** | текстовая фикстура скопирована в `tests/fixtures/statements/sberbank2excel/`; снимки вёрсток (2.4 МБ PNG/JPG) оставлены в `~/raw-originals/` — в тестах не нужны, вес не оправдан | да |
| `gerasiov/ofxstatement-russian` — 6 выписок Сбера, Альфы, ВТБ + эталоны разбора | 🔴 **файла лицензии в снимке нет, режим не подтверждён** | оставлено в `~/raw-originals/finpilot-data/statements/ofxstatement-russian/` | **до выяснения — нет**; плагины `ofxstatement` обычно GPL, а GPL в закрытом продукте несовместим с нашим режимом |
| MT940-фикстуры (`mt940_fixtures`, 161 файл) | BSD-3 (Rick van Hattem) | `~/raw-originals/.../formats_intl/` | да, но формат в дорожной карте не первый — переносить, когда дойдёт очередь |
| `camt.053` и OFX образцы | лицензии публикаторов рядом (`okane_LICENSE.txt`) | там же | проверять поимённо перед переносом |
| **Berka / PKDD'99** — 1 056 320 транзакций, 682 кредита с исходом | 🔴 **только для исследований** | `~/raw-originals/.../statements/berka/` (81 МБ) | **нет.** В репозиторий не кладётся и в продукте не используется |
| CFPB NFWBS PUF — 6 394 человека, США | общественное достояние США | `~/raw-originals/.../advice_benchmarks/` | да, но как **внешний эталон стенда**, не как данные о россиянах |

---

## Что осталось экспертным допущением

🔴 **Частота и глубина шока дохода конкретного домохозяйства** рядом не
закрывается: для этого нужна панель одних и тех же семей во времени (RLMS —
исследовательская лицензия, «Ромир» — коммерческая панель с непубличным
прайсом). В паспорте (`docs/model/rf_empirical_profile.md`) это помечено прямым
текстом как допущение, а не как измеренная величина.

Снимок: 17.09.2026. Обновление — повторным прогоном скриптов после обновления
оригиналов в `~/raw-originals/finpilot-data/`.

---

## Полные sha256 оригиналов

Сверено 17.09.2026 (прогон B2) пересчётом по файлам в `~/raw-originals/finpilot-data/`;
все значения совпадают с `MANIFEST_sha256_2026-09-17.txt`. В таблицах выше — сокращение
«8 первых…8 последних» знаков. 🔴 Шесть сокращений B1 содержали опечатку в хвосте
(`dox_rasx_potreb_2022`, `sred_cen_perv_4kv-2025`, `Nedvijimost_arenda_Cena_2kv-2026`,
`cbr_int_rat_deposits_ind_by_region`, `moex_IMOEX_daily`, `moex_RTSI_daily`) — исправлены.

| Оригинал | sha256 |
|---|---|
| `rosstat_ineq/NB_RD_1-2-8.xlsx` | `2a2baa092ef90288759ccaa8240b877b87652642825ffb07a0f12bdd610f3752` |
| `rosstat/rosstat_ipc_mes_08-2026.xlsx` | `4ef8b1d7a70d3b3e40260d4374b063a176b6fd628d7bf7289a7343ab621f6ebf` |
| `rosstat/rosstat_ipc-KIPC_2010-2025.xlsx` | `32b8e2019acb312626b8f59c18e158adbc9fb5cf09c421aa82a087a7400d3dd9` |
| `rosstat/rosstat_Vesa-tov-KIPC_2012-2026.xlsx` | `969a6921c2294e50d8032a6eafcb8c6123a19ced423c76b63a76c78098901ce3` |
| `rosstat/rosstat_urov_13kv_2kv2026.xlsx` | `52a0a45dbbe489ef0d3195da0d322a29abc2021b7b6302bf7f1ae0f9c785d1b6` |
| `rosstat/rosstat_vpm_RF_kv.xlsx` | `76af72af1626e3abaf5da582797ca01b0c5f1070361b66299e09d2b62c1b320a` |
| `rosstat/rosstat_vpm-643_2021-2026.xlsx` | `25a900bbd475f282185ec1590436df57bf1234b07ce8598e4d9a3b4443570058` |
| `rosstat_obdh/DRP_2024.rar` | `b9934e7d9affc273eabdc808a6048ef24482ec2ab4e1f89c261721b1d18bd109` |
| `rosstat_obdh/DRP_2025.rar` | `73eee9e15b342d97dc19242104dee62118cfeb40693294493ed75f677047e37e` |
| `rosstat_obdh/dox_rasx_potreb_2022.rar` | `bb3a809137a3eacbc760ec8dbb839f5b92eb40950bda7aac2c20af445e07d715` |
| `rosstat_obdh/dox_rasx_potreb_2023.rar` | `5786fad6992773ea6e86992a5f26c5461d73677833d9a4f463cfcb991619aecf` |
| `rosstat_housing/sred_cen_perv_2kv-2026.xlsx` | `b8110ffb9d717d76f9bf3520e993dbff41ee9ee77749d35e2b6b7013851d72b6` |
| `rosstat_housing/sred_cen_perv_4kv-2021.xlsx` | `b6568a1f6b431b772d32ea0f3415f7340dde75804cb1d443f839925c18c4a8ce` |
| `rosstat_housing/sred_cen_perv_4kv-2025.xlsx` | `5acd5c2f6c0a00d1cdef56adf11a14313a27e55895b95c48a9ebb9b215da9a51` |
| `rosstat_housing/sred_cen_vtor_2kv-2026.xlsx` | `f9e1659dcb40763e8affea487815bad4762159e5b30154cfbaf78b7c3789f601` |
| `rosstat_housing/sred_cen_vtor_4kv-2021.xlsx` | `3c4965d7fa560ed780af292196e99fd121cfe6ceff4c7b54fbed7745f912ee4b` |
| `rosstat_housing/sred_cen_vtor_4kv-2025.xlsx` | `139a12c08f368ae9fba6208aa79763c7aeb42db8ca39b819865de86e6e776cde` |
| `rosstat_housing/Nedvijimost_arenda_Cena_2kv-2026.xlsx` | `afdd037b40e23f53bdbd69c5219d7ddaeb31741eecc51a651e0ed8c1797b3d0e` |
| `rosstat_demo/demo31_2023.xlsx` | `855df52893e21616c0065467f493ad32bca00b337e80e09e80d438bb37b7071f` |
| `rosstat_demo/demo32_2023.xlsx` | `bc75b90d996915b4a6ebdb6027786592966f1e49818add1918dd4aefaffaf1be` |
| `rosstat_demo/demo14.xlsx` | `641eb733b819fee02adfdf2eba7aa5404804de6ebf42b0eeecbcf0d8df7d5785` |
| `cbr/cbr_usd_rub_daily_1992_2026.xml` | `2e1b5fc8e9e48eb656f63cb584fb15cbf397a1df62d8f08c457e239644af9e04` |
| `cbr/cbr_eur_rub_daily_1999_2026.xml` | `1598e8551c06ed14d0c718437378bb04feb80b16c21437a2168fe5e368890e38` |
| `cbr/cbr_cny_rub_daily_2010_2026.xml` | `40c643e9a3f7352db0beeeb64df6817562494040e988dad5a7f37575df1c4595` |
| `cbr/cbr_key_rate_daily_2013_2026.xml` | `97b38ddacfcb1aa2a0aeac413551b0d0b137eb997310e6be81032697705cbf8d` |
| `cbr/cbr_ruonia_daily_2010_2026.xml` | `081e1e5dbf4c7ddcf66809fb5cbef4d0b58584632ef0a1c83fd5659fbe834df9` |
| `cbr/cbr_int_rat_loans_ind_new.xlsx` | `f8fbaa15dd50b10602090470a0cc31aa9581e8a677447dd5a7136eb24f161218` |
| `cbr/cbr_int_rat_deposits.xlsx` | `14a61745dded4b69a35df6ea649e19eee8f13c7edd3a0c0aab26af5d535d9c04` |
| `cbr/cbr_int_rat_loans_ind_by_region_new.xlsx` | `803384cf7860674edf3b89921a4f478fef9b68382f1de6f46a28108329c387de` |
| `cbr/cbr_int_rat_deposits_ind_by_region.xlsx` | `b0ca8ea438f05d431b46b041afea9b25394f014d64bdfa253685f68e5f328e01` |
| `cbr_ref/avgprocstav_table.html` | `2ef5b2426e1ba163784aa25df7711306282e850645ade4b005a229f5ff5810e8` |
| `cbr_finstab/4q_2025_1q_2026.pdf` | `d2c6709e32cb15acd69e770eea7edf43cb8bf544dae6c487f51c4160216b96f7` |
| `cbr_mpl/Macroprudential_limits_banks_01072025.xlsx` | `0126f39bf1f06e067e90784c84c47caa27d1f4bf682b55dd8caa992937909cbb` |
| `moex/moex_IMOEX_daily.csv` | `4c236425c71392089b64f4aa1c4a045bfe6f6264eca744b39e82fecdf745b697` |
| `moex/moex_MCFTR_daily.csv` | `1f188554e49beb5c1eebca64d01394ef76cb77b36589a3bb856986ca594f35c1` |
| `moex/moex_RTSI_daily.csv` | `191ef4b1d060be840184c8359ccb0a7b310ef3afdc6fb15e633905512cb3c6f6` |
| `moex/moex_RGBI_daily.csv` | `47e944118998ea1d01ffe2ed6f4049a7a0958795acd63d307194159ed8cfbdf1` |
| `moex/moex_RGBITR_daily.csv` | `68e1f3d79a755ae1bfef13cc2764eea8c336e6cfe9942e6f756a4726835786c4` |
| `moex/moex_MREDC_daily.csv` | `568c110ea80537da0678d9c090d3468937d483cea4d20a8242ed259ccba94f5d` |
| `commodities/gold_pm.json` | `77c9dc89c5c071dafb989ff4a650abc39876dfffebe4e1b94347ea426eaf77e8` |
| `fred/fred_TDSP.csv` | `6c5ed5982a05655f5c5e47118abc325582c03b61097a38d0e858f0897a0fb3a9` |
| `fred/fred_PSAVERT.csv` | `2b41b4060a07a10ed2d7970b2656e7010ae6fac96d92c367a295fe4e78cb549b` |
| `fred/fred_SIPOVGINIUSA.csv` | `5d897c6c77730ae6f704a0eab98b33f5d1500a96d3ca09ce7b9597695a8aa585` |
| `fred/fred_MORTGAGE30US.csv` | `e2fbb4422a47ac0a7bb33dc199e9a41705154d9399c231e6d3b6476c74a57f74` |
| `fred/fred_CPIAUCSL.csv` | `f8ecddf53a9a9a74dda92c2c4204e6039466fcb744bc74171b73b5f6aac48119` |
| `fred/fred_DGS10.csv` | `c4bd527f5b92c7e536808a0189a3e038a44c6850b2cd5124ac9016be5eecaaf6` |
| `fred/fred_HDTGPDUSQ163N.csv` | `9dafbb940ffa27009cbd403b478450c3fc98d8870dcca662ea9d3fadb2cd4e35` |
| `fred/fred_MEHOINUSA672N.csv` | `71da23316ed3bb831ba4d6a5a92947fc4cf0a0793a2ff2786e914fba6d06cae4` |
| `fred/fred_VIXCLS.csv` | `e4d92c31d8c59a40e516b495eb31567ad226f50a7020e71e0450f4971ad5cb38` |
| `fred/fred_SP500.csv` | `a05c957ec824cd18b6646fa29f881f49c3f55c037b282a4711e984da10ce1255` |
| `worldbank/wb_SI.POV.GINI.json` | `1e372b4640b6533f9e7af9a23c92b18ad93f333183f25dbeaaac7fc4444c78a2` |
| `worldbank/wb_NY.GNS.ICTR.ZS.json` | `2598c1a4b944ab69a000141238763d108f7c4262fcbe58ba8b121ad07cd3c56a` |
| `worldbank/wb_FR.INR.LEND.json` | `b11c4b20ef478d3becaead5fc4242e096ce15a7d597ef31a79dc94ff98fb16b3` |
| `worldbank/wb_FR.INR.DPST.json` | `3dc7d21f26ee4ca03586768eea23128f34d8d3580ca1ac78515995bde173dbab` |
| `worldbank/wb_FP.CPI.TOTL.ZG.json` | `4adffbd12b43e3f91aed1c9e87a1df396f210648d9be9edb369dabc108ef12ed` |
| `worldbank/wb_SP.DYN.LE00.IN.json` | `478123d8ec0f1ecfb15e854c2cec27831c614ff36e743273f9d535ea2d188420` |
| `worldbank/wb_NY.GDP.PCAP.CD.json` | `0a7214b66301655c1357f06745b206f08b9a5e34ff1e79ac74c7dec671662adf` |
| `worldbank/wb_SL.UEM.TOTL.ZS.json` | `8bf12bdcd48c8808ba73c2c886eadd06bc1bcaf915b5f1170d606fafda5449c2` |
| `moex_zcyc/zcyc_2020-12-30.json` | `ceefa6836e67f0f0c76113b9d3d56c723387bc1693fa810bf4dc42616c23a7e3` |
| `moex_zcyc/zcyc_2021-12-30.json` | `937c839e3791fce292730e068d8d31d477ee59968fde805ade003fc2aa1b72f8` |
| `moex_zcyc/zcyc_2022-12-29.json` | `bbc117b3cdf7bed2615c2e59eb6a3b91c40659c673333d8eccd235536521ad12` |
| `moex_zcyc/zcyc_2023-12-28.json` | `488eba012b3fbb9f3a518ffb3ba923a4b9df21eab5a9ff02c498200eac82e94f` |
| `moex_zcyc/zcyc_2024-12-27.json` | `604d6ce0519e6949959f91a2c4830d9c2c3ed227cdd2d4f074c06edf29994897` |
| `moex_zcyc/zcyc_2025-12-30.json` | `44aee767df4d910c96e8628311c73fd3992cc8663526bed8f1eb7d1dc331ce00` |
| `moex_zcyc/zcyc_2026-06-30.json` | `7f7912a2d540d0bbbacdb12940dda30197ce60a2b9b85dfae5cd7f4335ba4ce8` |
| `moex_zcyc/zcyc_2026-09-16.json` | `db52c0ea469868107f1ccf3ee4309bc0398a544d166f3599d7ba4bb003c87197` |
| `rosstat_obdh/DRP_2026_1.rar` | `989e9b5b644e638dd24f7ca76a2060c2471da8a4f77f0724c12b7c56bead8fa2` |
| `npf/npf_stat.xlsx` | `b5b2014cda91cd37613c2db2cb62a15db15782466d921ca39c29881b951072d9` |
| `goal_prices/sred_potreb_cen_2022.xlsx` | `94d58542634ac34096bdf5261d003e57a2ee474fe54d7153daaea6d92d57a2c6` |
| `goal_prices/sred_potreb_cen_2023.xlsx` | `6fb4297765a110923566f9518aec77f6c56ae76f0f8a3b9e5d721ba3572359ed` |
| `goal_prices/sred_potreb_cen_2024.xlsx` | `b35330ad824fa4cfb85ba92718084772b8c113cb4ee7258f4ff5147e2f995ef3` |
| `goal_prices/sred_potreb_cen_2025.xlsx` | `0ac8adc81a31bd2d13018538475d1d875a74b3dae48e02c6b60e178403d567ec` |
| `goal_prices/sred_potreb_cen_08-2026.xlsx` | `0303a5fc3ed434eacf37e29c53df6f36fcf0a19e163f8ffd2cc7537994d8f96c` |
| `pif/mutual_fund_data.xlsx` | `370e5549ae20deb7dcdbfb70057ba907714447e64c93f94132839e54688aac1b` |
| `life_tables/WPP2024_Life_Table_Complete_Medium_Male_1950-2023.csv.gz` | `e304a776352e5899ff45a1e0c059bdbaa32e8a8249d36d8f4627b2afaf6358be` |
| `life_tables/WPP2024_Life_Table_Complete_Medium_Female_1950-2023.csv.gz` | `0e23ba8cc2daabd9aa40839b02e21917205f29ea45791c2b1a87bd42705b1458` |
| `life_tables/wpp2024_complete_Male_RUS_1950-2023.csv` | `61056c28079dcd8ea7579c83d7ddef7d79837f10975b8b2ad5a95bc716241a4e` |
| `life_tables/wpp2024_complete_Female_RUS_1950-2023.csv` | `c17cd23ade38db563cc938c5a1bab18dc84defa45734108ecbdb334fde485daf` |
