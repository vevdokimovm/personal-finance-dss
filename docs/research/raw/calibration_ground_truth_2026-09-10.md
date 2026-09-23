# Тема 35. Чем заменить экспертный консенсус как эталон + микроданные для правдоподобной популяции

Дата: 10.09.2026. Статус: ЗАВЕРШЕНО.
Агент: один, подагентов — ноль.

Зачем: калибровка модели FINPILOT идёт пятый раунд, 12 000 синтетических портретов против
консенсуса четырёх экспертных движков (согласие 51,9% → 87,4% → 78,63%). Две структурные дыры:
(1) портреты синтетические, происхождение распределений не показано; (2) эталон — МНЕНИЕ, а не ИСХОД.

Опора (не переискивается): тема 27 `raw/prescriptive_quality_metrics_2026-09-10.md`,
тема 34 (веса профилей статистикой РФ не калибруются), темы 32–33 (ставка и инфляция — совместно).

---

## Участок 1. Микроданные для правдоподобной популяции РФ

### 1.1 RLMS-HSE

**Что это.** Российский мониторинг экономического положения и здоровья населения НИУ ВШЭ —
панельное обследование домохозяйств, ведётся с 1994 г., зеркала: `hse.ru/rlms` и
`rlms-hse.cpc.unc.edu` (Carolina Population Center, UNC Chapel Hill).

**Условия доступа [ПРОЧИТАНО, rlms-hse.cpc.unc.edu/data/availability/, 10.09.2026]:**

- Публичные данные — **без заявки и без соглашения**: "available to download without any
  application process from the CPC Dataverses". Регистрация/плата на странице доступа
  не заявлены; на странице `hse.ru/en/rlms/` формулировка мягче — «users are asked to
  register online and accept Data Use agreement» (это со сниппета поиска, страница сама
  не открывалась — помечаю как НЕ ПРОЧИТАННОЕ).
- Публичны: **«Household & Individual» 1994–2024**, «Community» 1994–2018,
  Family Planning and Reproductive Health (2010, 2012).
- Чувствительны (нужно соглашение): **цены по населённым пунктам** 1994–2024 (Data Use
  Agreement) и **день и месяц рождения** 1994–2024 (соглашение + security plan).
  Запрос — на `sveta@demoscope.ru`.
- Форматы: Stata (.dta), SPSS (.sav / portable), S-Plus, R, tab-delimited; zip.
  Глубина панели: домохозяйства **1994–2024**, индивиды **1994–2025**
  [ПРОЧИТАНО, hse.ru/en/rlms/downloads].
- Ограничений на **публикацию результатов** на странице доступа НЕ УКАЗАНО
  ("Publishing Restrictions: Not specified"); есть отдельная страница "Citing the Data" —
  цитирование обязательно, её текст в этой сессии не читался.

**Вывод по RLMS для нас:** публичный слой — тот самый, что нужен (доходы, расходы,
занятость, состав домохозяйства), берётся свободно, панель 30 лет. Порождать из него
синтетическую популяцию и публиковать результаты — препятствий в условиях доступа
не обнаружено (публичные файлы, application process отсутствует). 🔴 Слабое место RLMS
именно для FINPILOT — блок задолженности в нём тонкий (см. 1.3): RLMS сильнее по доходам
и потреблению, чем по кредитному портфелю домохозяйства.

### 1.2 Микроданные Росстата (ВНДН, ОБДХ) и ЦБ (ОДПФ)

🔴 **ГЛАВНАЯ НАХОДКА УЧАСТКА 1.** Обезличенные микроданные выборочных обследований
Росстата **и ЦБ** выложены единым каталогом на портале «Если быть точным»
[ПРОЧИТАНО, tochno.st/datasets/surveys, обновление каталога 03.09.2026]:

- период **2011–2025**, форматы **CSV (UTF-8, разделитель «;»), XLSX, SAV**;
- лицензия — **Creative Commons BY 4.0** (то есть свободное использование и публикация
  производных при указании источника);
- скачивание — архивом по каждому обследованию, хранилище
  `https://storage.yandexcloud.net/tochno-st-catalog/Rosstat/...`;
- 12 обследований, из них нам прямо релевантны:
  - **ВНДН** — «Выборочное наблюдение доходов населения и участия в социальных
    программах», **2012–2025, 13 волн**;
  - **ОДПФ** — «Обследование домохозяйств по потребительским финансам» (ЦБ РФ),
    **2013, 2015, 2018, 2020, 2022, 2024**;
  - **КОУЖ** — «Комплексное наблюдение условий жизни населения», 2011, 2014, 2016,
    2018, 2020, 2022, 2024.

Объём ВНДН (со сниппета Росстата, НЕ прочитано в первоисточнике): ежегодно с 2016 г.
во всех субъектах РФ, **60 тыс. домохозяйств**, раз в три года — **160 тыс.**

**Собственный портал ОБДХ Росстата** `https://obdx.gks.ru/` — HTTP 200, но это
«Система доступа к результатам обследований» с формой входа («Обычный пользователь»,
«Вход в систему»), то есть агрегатор витрин, а не выгрузка микрофайлов без авторизации.
`https://rosstat.gov.ru/microdata` — **404**. `gks.ru/free_doc/new_site/vndn-2024/` — **403**.
Вывод: официальный канал Росстата к микроданным в этой сессии не открылся; рабочий канал —
зеркало tochno.st под CC BY 4.0.

### 1.3 🔴 ОДПФ ЦБ РФ — микроданные СКАЧАНЫ И ПОСЧИТАНЫ В ЭТОЙ СЕССИИ

Это главный результат темы. Банк России выкладывает **деперсонифицированные микроданные
на своём сайте, без регистрации, без заявки, без соглашения**.

Страница: `https://www.cbr.ru/ec_research/vserossiyskoe-obsledovanie-domokhozyaystv-po-potrebitel-skim-finansam/`
(HTTP 200, 65 798 байт) [ПРОЧИТАНО целиком, 10.09.2026].
🔴 Адрес с `-skoe-...-skim-` (латиница «y»): вариант `vserossiiskoe-...-potrebitelskim-` даёт **404**.

**Дословно со страницы ЦБ:**

> «Проект стартовал в 2013 году, обследование проводится раз в два года. Четыре первые волны
> были организованы Минфином России. Пятую волну в 2022 году и шестую волну в 2024 году
> Всероссийского обследования домохозяйств по потребительским финансам провел Банк России.
> Координацию и реализацию всех волн обследования, включая полевые работы, осуществляет
> ООО «Демоскоп».»

> «В 2024 году было опрошено 6079 домохозяйств, включая 11835 респондента, проживающих
> в 32 субъектах Российской Федерации. 99% итогового количества респондентов было опрошено
> в марте – августе 2024 года»

> «Данные опроса представлены в двух форматах .csv и .RData и не являются очищенными
> от выбросов и пропусков.»

Условие использования (дословно, раздел «Доступ к данным»):

> «Банк России приветствует проведение экономических исследований академическим сообществом
> на актуальные темы с использованием гранулярных данных Всероссийского обследования
> домохозяйств по потребительским финансам. Ссылка на источник: Официальный сайт Банка России
> (2025), «Всероссийское обследование домохозяйств по потребительским финансам», доступен:
> https://cbr.ru/ec_research/vserossiyskoe-obsledovanie-domokhozyaystv-po-potrebitel-skim-finansam/»

То есть **единственное условие — ссылка на источник**. Запрета на производные и публикацию нет.

**Прямые ссылки на файлы (все проверены, HTTP 200, 10.09.2026):**

| Файл | URL | Размер |
|---|---|---|
| Данные, анкета домохозяйства, 6-я волна 2024 | `https://www.cbr.ru/Content/Document/File/174715/anketa_6.zip` | 5 147 023 Б |
| Данные, индивидуальная анкета, 6-я волна 2024 | `https://www.cbr.ru/Content/Document/File/174716/anketa_6_1.zip` | 17 191 480 Б |
| Вопросники 6-й волны с кодами вопросов | `https://www.cbr.ru/Content/Document/File/174712/quet_6_2024.zip` | 1 957 504 Б |
| Readme (код перевода форматов) | `https://www.cbr.ru/Content/Document/File/174713/readme_n.zip` | 1 004 Б |
| Методология 6-й волны 2024 | `https://www.cbr.ru/Content/Document/File/174710/method_6_2024.pdf` | 588 340 Б |
| Вопросники 1–4 волн (2013, 2015, 2018, 2020) | `https://www.cbr.ru/Content/Document/File/146140/questin_1_4.zip` | — |
| Данные 5-й волны 2022 (дх / инд.) | `.../145697/anketa_5.zip`, `.../145698/in_anketa_5.zip` | — |

🔴 **Имя файла в архиве кириллицей в кодировке CP866** — `unzip` падает с «Illegal byte sequence».
Обход, проверен: распаковка через `zipfile` в Python с переименованием
(`n.encode('cp437').decode('cp866')`).

**Структура файла домохозяйств (проверена лично, файл распакован и прочитан):**
`12/database_FB_household_261224s_6wave.csv`, 65 497 007 байт, **2 680 столбцов × 6 079 строк**
(строк ровно столько, сколько домохозяйств в волне).
Первые столбцы: `id_w, id_h, oldhh, aid_h, bid_h, cid_h, did_h, eid_h, fid_h, redidh, psu,
sett_typ, hhwgt, size, hh_size, тип_дх, h_h1, h_h2, …`
Есть **вес домохозяйства `hhwgt`** и **PSU (`psu` = субъект РФ)** — то есть выборка
пересчитывается в население корректно. Панель склеивается: `id_w` — год волны,
`aid_h…fid_h` — код домохозяйства в соответствующей волне (a — 2013 … f — 2024),
`idind` — сквозной идентификатор индивида по всем волнам.

**Что в анкетах (со страницы ЦБ, дословный перечень блоков):**
анкета домохозяйства — «социо-демографических характеристиках», «жилищных условиях…
финансовых источниках их приобретения», «кредитах на покупку объектов недвижимости»,
«доходах и расходах домозяйства и их структуре», «стабильности получения доходов»,
«сбережениях из доходов, их структуре и **горизонте финансового планирования**».
Индивидуальная анкета — «объеме и структуре финансовых активов», «объеме и структуре
финансовых обязательств, в том числе фактическом и планируемом спросе на кредиты»,
«предпочтениях относительно суммы сбережений из доходов (сберегательное поведение)
или суммы принимаемых финансовых обязательств», «уровне финансовой грамотности»,
«финансовом самочувствии», «финансовой доступности».

**Долг измеряется ПОКРЕДИТНО** — это структура нашего портрета один в один
[вопросник, `Индивидуальный вопросник_2024.pdf`, ПРОЧИТАНО]:
- С4.1 наличие невыплаченных потребительских кредитов; С4.2 цель кредита; С4.3 год выдачи;
  **С4.4 сумма кредита; С4.5 срок; С4.6 «Сколько Вам осталось» выплатить (остаток);
  С4.7 «Какой ежемесячный платеж»**; С4.8 ставка; С4.10 — повтор блока по СЛЕДУЮЩЕМУ кредиту;
- С2.* — кредитные карты: число карт, общий лимит (С2.4), лимит по карте (С2.9),
  **годовая ставка (С2.10)**, средний ежемесячный платёж (С2.13), задолженность (С2.14/С2.15);
- С3.* — займы в ломбардах и МФО: число, сумма, **ставка (С3.4)**, срок (С3.5);
- К15–К19 — кредиты на развитие бизнеса: остаток, ежемесячный платёж, срок, цели;
- С1.* — кредитная история спроса: отказы, одобрение на меньшую сумму / по большей ставке,
  опыт с нелегальными кредиторами.

**🔴 И блок, который прямо бьёт по выводу темы 34.** В анкете домохозяйства есть
вопросы о ЦЕЛЯХ и НОРМАТИВЕ подушки:

> «Н15. …Пожалуйста, представьте себе не очень приятную картину: все члены Вашего
> домохозяйства лишились всех источников дохода. Как долго Ваше домохозяйство сможет
> материально жить так же, как Вы живёте сейчас, то есть, не уменьшая расходов, только
> за счёт денежных сбережений, ничего не продавая из имущества?» (переменная `h28`)

> «О24. …на ближайшие 5 - 10 лет у Вашего домохозяйства запланированы какие-нибудь крупные
> расходы, например, приобретение недвижимости или транспорта, крупный ремонт, оплата
> образования или медицинских услуг?» (`o27`) → «О25. Вы уже начали делать сбережения
> для оплаты этих запланированных расходов?» (`o28`)

> «О26. Иногда расходы бывают связаны с незапланированными ситуациями. **Как Вы считаете,
> сколько денег домохозяйство должно иметь в сбережениях** для оплаты таких непредвиденных
> расходов, которые могут случиться в будущем? ___ РУБЛЕЙ» (`o29`)

> «О27. В случае острой необходимости Ваше домохозяйство могло бы одолжить у родственников
> или знакомых сумму в 50 000 рублей?» (`o30`) «О28. А 500 000 рублей?»

#### 1.3.1 Посчитано мной на скачанном файле (не из публикации)

Расчёт: 6-я волна 2024, `database_FB_household_261224s_6wave.csv`, n = 6 079.

**Автономия на сбережениях (`h28`), взвешено по `hhwgt`, отказы и «затрудняюсь» исключены:**

| Ответ | Доля, % |
|---|---|
| Не больше месяца | 32,9 |
| Несколько месяцев | 27,1 |
| Не больше недели | 14,0 |
| Ни одного дня | 9,3 |
| Не больше двух недель | 8,8 |
| Полгода и больше | **7,9** |

Итого «месяц и меньше» = **65,0 %**; «полгода и больше» = 7,9 %.
(Невзвешенные частоты: полгода+ 443, несколько месяцев 1 568, ≤месяц 1 881, ≤2 недели 485,
≤недели 768, ни одного дня 493; «затрудняюсь» 393, «нет ответа» 13, «отказ» 35.)
🟡 Сверка с темой 34: там «у 73 % подушка 0–1 мес» — по ОДПФ-2024 получается **65,0 %**.
Расхождение объясняется базой (там, вероятно, другой опрос/год); наше число теперь
получено из первичного файла и воспроизводимо.

**Нормативная подушка «сколько ДОЛЖНО быть» (`o29`), n = 5 469 валидных ответов, ₽:**

| p10 | p25 | медиана | p75 | p90 | среднее |
|---|---|---|---|---|---|
| 45 000 | 50 000 | **100 000** | 200 000 | 500 000 | 212 665 |

**Цели (`o27`/`o28`):** крупные расходы на 5–10 лет запланированы у 1 426 из 5 824
ответивших «да/нет» = **24,5 %**; из них **уже копят — 795 из 1 417 = 56,1 %**
(«Да» 795, «Нет» 622).

🔴 **Следствие: вывод темы 34 «веса профилей статистикой РФ не калибруются» требует
поправки.** Прямых весов «резерв/долг/цели» действительно никто не спрашивает, но ОДПФ
измеряет три их наблюдаемые проекции: желаемый размер подушки в рублях (`o29`),
фактическая автономия (`h28`), наличие цели и факт накопления под неё (`o27`,`o28`),
плюс горизонт финансового планирования. Это не веса SAW напрямую, но это **эмпирическое
ограничение на них**: набор весов, порождающий популяцию с медианной желаемой подушкой
не 100 тыс. ₽ и долей целевых накопителей не ~25 %, противоречит данным.

### 1.4 Прочие источники микроданных

- **tochno.st** (см. 1.2) — зеркало ВНДН/КОУЖ/ОДПФ под **CC BY 4.0**, форматы CSV/XLSX/SAV,
  единый каталог. Полезно тем, что ВНДН (60–160 тыс. домохозяйств) даёт **распределение
  доходов** гораздо большего объёма, чем ОДПФ (6 тыс.).
- **RLMS-HSE** (1.1) — панель 1994–2025, публичный слой без заявки; сильна доходами,
  занятостью, потреблением; слаба покредитной детализацией долга.
- **`obdx.gks.ru`** — витрина ОБДХ Росстата за логином, микрофайлы без авторизации не отдаёт.
- **`dano.hse.ru`** — зеркало публикаций ВШЭ по ОДПФ (встретилось в выдаче, не открывалось).

### 1.5 🔴 ПРЯМОЙ ОТВЕТ УЧАСТКА 1

**Да, 12 000 портретов можно породить из РЕАЛЬНОГО распределения, и данные для этого уже
лежат на диске.** Комбинация трёх источников, по убыванию приоритета:

1. **ОДПФ-2024 (ЦБ) — базовый каркас портрета.** 6 079 домохозяйств × 2 680 переменных,
   веса `hhwgt`, регион `psu`. Даёт: доход и его структуру, расходы, сбережения,
   **покредитный список долгов с остатком, платежом, ставкой и сроком** — то есть ровно
   те поля, которые потребляет модель v3.0.0. Плюс панель 6 волн 2013–2024 для проверки
   устойчивости распределений во времени.
2. **ВНДН (Росстат, через tochno.st, CC BY 4.0)** — калибровка маргиналов дохода на
   выборке в 10–25 раз большей; ОДПФ по доходу тонок в хвостах.
3. **RLMS-HSE** — контрольная сверка и, при необходимости, расширение по составу
   домохозяйства и занятости.

**Порядок работ (исполнимо):**
1. Скачать ОДПФ 6-й волны (household + individual) и 5-й волны; распаковать через
   `zipfile`+cp866 (не `unzip`).
2. Собрать «портрет» = склейка household (доход, расходы, подушка, цели) + individual
   (покредитный долг) по `id_h` внутри волны.
3. Почистить: файлы, по прямому предупреждению ЦБ, **«не являются очищенными от выбросов
   и пропусков»**; кодировать 97/98/997/998 как пропуск, править нефинансируемые портреты
   (платежи > дохода) явным правилом и логировать долю отброшенных.
4. Ре-сэмплировать 12 000 портретов **с весами `hhwgt`** (взвешенный бутстрап) — это уже
   даёт реальную популяцию без всякой генеративной модели. Сглаживание непрерывных величин —
   ядерное, чтобы не было 6 079 повторяющихся точек.
5. Только если нужно больше разнообразия или регионального разреза — синтетическая
   генерация поверх (участок 2) с обязательной проверкой правдоподобия.

**Что делать, если бы микроданные были недоступны** (сценарий отпал, но фиксирую как
запасной): копулы по опубликованным маргиналам + корреляционная матрица из публикаций;
качество такой популяции проверяется только по маргиналам и заявленным корреляциям,
совместные хвосты остаются недоказуемыми. Этот путь теперь НЕ нужен.

---

## Участок 2. Синтетические популяции — метод

### 2.1 IPF и synthetic reconstruction — классика, и её три известные болезни

IPF (iterative proportional fitting) — «traditionally used in many commercial and
non-commercial microsimulation systems for creating the joint distribution of individuals
when combining a reference joint distribution with target marginal distributions».
Смысл: есть выборка-донор с совместным распределением и известные маргиналы генеральной
совокупности; IPF итеративно домножает ячейки таблицы, пока маргиналы не сойдутся к целевым.

Три ограничения, названные в первоисточнике
[Jeong B., Lee W., Kim D.-S., Shin H. «Copula-Based Approach to Synthetic Population
Generation», PLoS ONE, 2016, 11(8):e0159496, ПРОЧИТАНО через pmc.ncbi.nlm.nih.gov/articles/PMC4973930/]:

1. **Несходимость:** «IPF procedure may not converge» при блочно-диагональной структуре
   референсной матрицы.
2. **Проблема нулевой ячейки:** «If any of a_{i,+} vanishes to zero while r_i is not,
   the IPF procedure fails».
3. **Зависимости:** «It is unclear whether IPF well preserves the dependence structure of
   the reference joint table sufficiently when fitting it to target margins».

Плюс отдельная известная беда — **округление до целых**: в сравнении IPF и simulated
annealing «IPF coupled with a marginal distributions-controlled rounding outperforms
populations generated with simulated annealing in all scenarios, while simulated annealing
generally outperforms IPF coupled with the commonly used Monte Carlo rounding»
(Choupani & Mamdoohi, Computers, Environment and Urban Systems, 2016 —
🟡 со сниппета, полный текст за пейволлом ScienceDirect, НЕ ПРОЧИТАН).

🔴 **Для нас IPF по большому счёту не нужен.** IPF решает задачу «донор есть, а маргиналы
генсовокупности другие». У нас донор (ОДПФ) уже репрезентативен и снабжён весами `hhwgt` —
достаточно взвешенного ре-сэмплинга. IPF понадобится, только если захотим региональный
разрез тоньше, чем даёт `psu`, или подгонку под маргиналы ВНДН.

### 2.2 Копулы — сохранение зависимостей при подмене маргиналов

**Копульный подход (CBJF)**, Jeong et al. 2016, четыре шага [ПРОЧИТАНО]:
1) накопленные распределения из референсных данных; 2) целевые накопленные распределения
из маргинальных ограничений; 3) билинейно интерполированная **эмпирическая** копула
«C(u,v) is computed using a bilinear interpolation»; 4) извлечение масс вероятности
    b_{k,l} = B_{k,l} − B_{k−1,l} − B_{k,l−1} + B_{k−1,l−1}
Метод не итеративный, поэтому не имеет проблем сходимости и нулевой ячейки.
Проверка сохранения зависимости — Пирсон, ρ Спирмена, τ Кендалла, MIC.
Вывод авторов: CBJF превосходит IPF «in almost all combinations», особенно
при «larger modifications» маргиналов.

**Современное развитие — «копульная нормализация» поверх генеративной модели**
[Jutras-Dubé P., Al-Khasawneh M.B., Yang Z., Bas J., Bastin F., Cirillo C.
«Copula-based transferable models for synthetic population generation»,
arXiv:2302.09193v3, 22.08.2024, PDF СКАЧАН И ПРОЧИТАН]:

> «the process involves normalizing the data and treating it as realizations of a given
> copula, and then training a generative model before incorporating the information on the
> marginals of the target population»

> «Results show that the copula enhances machine learning methods in matching the marginals
> of the reference data. Furthermore, it consistently surpasses Iterative Proportional Fitting
> in terms of SRMSE in the transferability experiments, while introducing unique observations
> not found in the original training sample.»

Сравнивались Bayesian Networks, VAE и GAN, каждая с копульной нормализацией и без,
плюс IPF и независимый бейзлайн. Про IPF прямо: «IPF shows notable limitations in terms of
sampling zeros, recall, and F1 score, as it fails to generalize».

### 2.3 🔴 Как доказать, что синтетическая популяция правдоподобна — рабочий набор метрик

Это и есть ответ на главный вопрос участка. Метрики делятся на три слоя.

**Слой A. Соответствие распределению — SRMSE.**
Стандарт микросимуляции, определение Sun & Erath, дословная формула
[arXiv:2302.09193, §4.2, ПРОЧИТАНО]:

```
                ┌───────────────────────────────────────────────┐
SRMSE = sqrt( M · Σ_{m1=1..M1} … Σ_{md=1..Md} (π_{m1…md} − π̂_{m1…md})² )
```
где d — число переменных, M_i — число категорий переменной i,
π и π̂ — относительные частоты конкретной комбинации в референсных и в синтетических
данных, M = Π_{i=1..d} M_i.

> «SRMSE captures whether a combination of synthetic data appears in the actual data in
> similar proportions. A SRMSE value of 0 indicates a perfect match, whereas larger values
> signify a growing disparity between the reference and synthetic data.»

🔴 Ключевой приём (по Borysov et al.): **SRMSE считается не одним числом, а проекциями
на подмножества из n переменных, n = 1…5.** «For n = 1, the SRMSE evaluates the fit of the
marginals, whereas for n > 1, it assesses the fit of the multivariate dependencies.»
Это ровно то, что нам нужно: SRMSE₁ проверяет маргиналы (доход, возраст, долг по
отдельности), SRMSE₂₊ — что связки «доход × долг × возраст» встречаются в тех же долях.

**Слой B. Разнообразие и допустимость — sampled zeros и structural zeros.**
[там же, ПРОЧИТАНО]:

> «SZ is the count of the generated combinations of variables that exist in the reference
> data but are unobserved in the training set. Lower SZ indicates lower diversity.
> In particular, a SZ count of 0 implies that the model failed to produce unseen realistic
> examples, while larger SZ values indicate the model's capability to generate out-of-sample
> examples. Similarly, we consider structural zeros (STZ), which are **infeasible combinations
> of attributes that do not exist in the population**. Lower counts of STZ suggest higher
> feasibility of the generated data.»

Плюс precision / recall / F1: «Precision reflects the proportion of generated data that are
feasible, recall measures how well the synthetic data covers the attribute combinations
present in the population».

🔴 Для FINPILOT STZ переводится в проверяемое правило: портрет с платежом по долгу больше
дохода, с отрицательным свободным потоком при нулевом долге, с ПДН > 1 — это structural zero.
Их доля в синтетической популяции обязана быть измерена и обоснована (в реальных данных
такие комбинации редки, но НЕ нулевы).

**Слой C. Sample-level метрики генеративной модели — α-Precision, β-Recall, Authenticity.**
[Alaa A.M., van Breugel B., Saveliev E., van der Schaar M. «How Faithful is your Synthetic
Data? Sample-level Metrics for Evaluating and Auditing Generative Models»,
Proceedings of the 39th ICML, PMLR 162:290–306, 2022. PDF СКАЧАН И ПРОЧИТАН]

Тройка: `E ≜ (α-Precision, β-Recall, Authenticity)` = (Fidelity, Diversity, Generalization).

α-support — минимальный по объёму подмножество носителя с массой α:
```
S^α ≜ min_{s⊆S} V(s),  s.t. P(s) = α
```
> «One can think of an α-support as dividing the full support of P into "normal" samples
> concentrated in S^α, and "outliers" residing in S̄^α.»

```
P_α ≜ P( X̃_g ∈ S_r^α ),  α ∈ [0,1]
```
> «α-Precision is the fraction of synthetic samples that resemble the "most typical"
> fraction α of real samples, whereas β-Recall is the fraction of real samples covered by
> the most typical fraction β of synthetic samples.»

🔴 **Теорема 1 (дословно):** «The α-Precision and β-Recall satisfy the condition
P_α/α = R_β/β = 1, ∀ α, β, iff the generative and real densities are equal, i.e., P_g = P_r.»
> «Theorem 1 says that a model is optimal if and only if both its P_α and R_β are straight
> lines with unity slopes.»

Это даёт **проверяемый критерий правдоподобия популяции**: строится кривая P_α по α ∈ [0,1],
и отклонение от прямой с единичным наклоном — количественная мера неправдоподобия.

**Authenticity** — доля образцов, «invented by the model and not copied from the training
data», через формальную проверку на копирование с d(X, D_real) = min_i d(X, X_{r,i}).
Для нас это ещё и защита по 152-ФЗ: низкая Authenticity = популяция содержит копии реальных
респондентов ОДПФ.

Отдельно: «our new metric definitions solve many of the drawbacks of standard precision-recall
analysis, such as lack of robustness to outliers and failure to detect distributional
mismatches (Naeem et al., 2020)» — то есть α/β-версии заменяют density/coverage Naeem.

**Слой D. Полезность — TSTR.**
[Frontiers in Digital Health, 2025, «Comprehensive evaluation framework for synthetic tabular
data in health: fidelity, utility and privacy analysis…», doi 10.3389/fdgth.2025.1576290,
ПРОЧИТАНО]. Единый конвейер из трёх слоёв: fidelity — Hellinger distance, Pairwise
Correlation Difference (PCD), R² DD-plot, **AUC-ROC различителя реального и синтетического
(значение ≈ 0,5 = данные неразличимы)**; utility — **TSTR (Train on Synthetic, Test on Real)
против TRTR (Train Real, Test Real)**, разрыв TSTR−TRTR и есть метрика; privacy — singling
out, linkability, membership inference, attribute inference.

🔴 **Замечание по применимости TSTR к нам.** TSTR требует задачи предсказания с меткой.
У портрета FINPILOT естественной метки нет. Законная подстановка: обучать на синтетике
предсказание наблюдаемой в ОДПФ величины (например `h28` — автономия домохозяйства на
сбережениях, или факт наличия просроченного долга) и тестировать на реальном hold-out
ОДПФ. Если модель, обученная на синтетике, предсказывает реальную автономию почти так же
хорошо, как обученная на реальных, — популяция несёт ту же структуру зависимостей.

### 2.4 Что из этого брать нам

| Метрика | Нужна? | Почему |
|---|---|---|
| SRMSE₁ (маргиналы) | 🟢 да | дёшево, прямо проверяет доход/возраст/долг |
| SRMSE₂…SRMSE₄ | 🟢 да | это и есть проверка связок; главный аргумент против «портреты выдуманы» |
| STZ (доля недопустимых портретов) | 🟢 да | у нас формулируется через инварианты модели |
| SZ (sampled zeros) | 🟡 да, если генерируем | если ре-сэмплинг с весами — SZ ≡ 0 по построению, метрика бессмысленна |
| α-Precision / β-Recall | 🟢 да | единственная метрика с теоремой «оптимум ⟺ распределения совпадают» |
| Authenticity | 🟢 да | двойная роль: не переобучение + не утечка реальных респондентов |
| TSTR | 🟡 да, в подстановке | нужна выбранная целевая переменная из ОДПФ |
| CTGAN / TVAE | 🟠 не сейчас | нужны, когда донора мало; у нас донор есть и он взвешен |

---

## Участок 3. Retrospective backtesting — законная форма

Тема 27 (§4.3) забраковала наивную формулировку и переформулировала в три приёма.
Здесь — методология каждого.

### 3.1 Regret против оракула с look-ahead: готовый аппарат из финпланирования — WER

🔴 **Изобретать метрику не нужно, она есть и называется Withdrawal Efficiency Rate.**
Введена Blanchett, Kowara & Chen (2012), изложение с определением —
Blanchett D.M. «Simple Formulas to Implement Complex Withdrawal Strategies»,
Journal of Financial Planning, сентябрь 2013 [ПРОЧИТАНО через `r.jina.ai`, доступ прямым
`WebFetch` дал **403**]:

> «Two key unknowns exist when determining how much a retiree can afford to withdraw from
> a portfolio: (1) how long the retiree is going to live and (2) the returns the retiree is
> going to experience. If a retiree knew these two values, he or she could determine the exact
> amount that could be withdrawn from the portfolio each year (or month) so that the ending
> value of the account would be exactly $0 on the day he or she (or they) pass away.
> While it is not possible to know these values in real life, **within a simulation framework
> it is possible to compare the actual income generated by a withdrawal strategy versus the
> amount of income that could have been withdrawn had the retiree had perfect information.**
> This is the key concept of the WER.»

> «The WER is calculated by dividing the amount of **utility adjusted income received** during
> retirement by the amount of **constant income the retiree could have received had he or she
> had perfect information** at the beginning of retirement (that is, they knew the returns that
> would be experienced and the length of the retirement period). The WER for each run is
> determined by multiplying the probability of living to that retirement year, subsequent on
> surviving the previous year, by the WER value for each year of the simulation.»

> «A WER value of 100 percent would imply the portfolio was able to capture all the potential
> available income over the period and implies the retiree had perfect foresight. Therefore,
> the goal is to select the strategy with the highest WER value.»

Что здесь важно методологически и переносится на нас дословно:
1. Знаменатель — **оракул с полным знанием будущего**, и это признаётся открыто, а не
   выдаётся за «правильный ответ».
2. Числитель — **скорректированный на полезность** результат, а не сырые рубли.
   То есть regret считается в единицах полезности, а не денег.
3. Сравниваются **стратегии между собой по одной шкале**, и именно это делает метрику
   полезной без ground truth (ровно критерий Миллера из темы 27, §1.2).
4. У Blanchett WER считался не на истории, а **в Монте-Карло**: 10 000 прогонов, каждый
   со своей траекторией. 🔴 Это снимает главную претензию темы 27 к бэктесту («траектория
   одна, n=1»): оракул можно считать **внутри каждого сценария Монте-Карло**, где траектория
   своя, и тогда независимых наблюдений столько, сколько прогонов.
5. Порядок величины «цены упрощения» у Blanchett: формульный подход дал
   «99.89 percent of the WER values of the DC model, on average», то есть потеря
   эффективности 0,1 п.п. Это ориентир, насколько мелкими бывают осмысленные различия.

**Перевод в FINPILOT.**
```
Regret(p) = 1 − U_model(p) / U_oracle(p)
U_oracle(p) = max по всем 66 альтернативам при ИЗВЕСТНОЙ реализации ставки и инфляции
U_model(p) = полезность альтернативы, выбранной моделью по информации на дату старта
```
Считается: (а) на реальной траектории РФ 2014–2026 — одна оценка, интервалов не даёт;
(б) внутри Монте-Карло по совместному генератору «ставка × инфляция» тем 32–33 — даёт
распределение Regret и честные интервалы, потому что прогоны независимы.
Отчитывать медиану и 90-й перцентиль Regret, и обязательно — Regret наивных бейзлайнов
на тех же прогонах.

### 3.2 Выживаемость ограничений по когортам

Прямого канонического источника «cohort survival of constraints» в этой сессии не найдено —
приём собирается из двух готовых:
- **cohort/rolling-period анализ** финпланирования (Bengen и наследники; зафиксирован
  в теме 27, §4.1) — стартовать план в каждый год t, вести до конца горизонта, считать
  долю успешных стартов;
- **определение «успеха» через ограничение, а не через оптимум**, — как у DeVaney (участок 4):
  бинарный исход «инвариант удержан / нарушен».

Операционально: для когорты старта t ∈ {2014-01 … 2020-12} инвариант Rt≥0 и ПДН≤0.40
проверяется на всём горизонте; survival(t) = 1, если ни разу не нарушен.
Метрика — доля выживших когорт и **кривая выживаемости по длине горизонта** (аналог
Каплана–Мейера: доля когорт, доживших до месяца h без нарушения).

### 3.3 Доверительные интервалы при перекрывающихся окнах

Проблема названа в теме 27 прямо: «12 когорт — это НЕ 12 независимых наблюдений».
Два стандартных лекарства, оба добыты.

**(а) HAC / Newey–West.** Newey W.K., West K.D. «A Simple, Positive Semi-Definite,
Heteroskedasticity and Autocorrelation Consistent Covariance Matrix», *Econometrica*,
1987, 55(3), 703–708. Формула в операционном виде
[Stata Reference Manual, `[TS] newey`, §Methods and formulas, PDF ПРОЧИТАН]:

```
X'Ω̂X = X'Ω̂₀X + (n/(n−k)) · Σ_{l=1..m} (1 − l/(m+1)) · Σ_{t=l+1..n} ê_t ê_{t−l} (x'_t x_{t−l} + x'_{t−l} x_t)
```
Ядро `(1 − l/(m+1))` (ядро Бартлетта) — то, что гарантирует положительную полуопределённость.
`m` — лаг усечения; 🔴 при перекрывающихся окнах длины `h` **минимально разумное `m = h − 1`**,
иначе часть общей информации между соседними окнами не учтена.

Выбор `m` не произволен: Andrews D.W.K. «Heteroskedasticity and Autocorrelation Consistent
Covariance Matrix Estimation», Cowles Foundation Discussion Paper № 877, июль 1988
(опубликовано Econometrica 1991) [PDF СКАЧАН И ПРОЧИТАН, аннотация]:

> «Currently available estimators that are designed for this context depend upon the choice
> of a lag truncation parameter and a weighting scheme. Results in the literature provide
> a condition on the growth rate of the lag truncation parameter as T → ∞ that is sufficient
> for consistency. **No results are available, however, regarding the choice of lag truncation
> parameter for a fixed sample size**… In consequence, available estimators are not entirely
> operational…»
> «Asymptotically optimal kernel/weighting scheme and bandwidth/lag truncation parameters are
> obtained using a minimax asymptotic mean squared error criterion… data-dependent automatic
> bandwidth/lag truncation parameters are defined…»

То есть: правило выбора `m` — автоматический data-driven бандвидт Эндрюса, а не «на глаз».

**(б) Блочный бутстрап.** Обычный бутстрап на перекрывающихся окнах занижает
неопределённость, потому что разрушает зависимость. Правило (🟡 формулировка со сводки
поиска, первоисточник в этой сессии не открывался):
«practitioners employ a block bootstrap with blocks sufficiently long to span the overlap
in the rolling window construction», и «the block length must increase with increasing sample
size to make bootstrap estimators … consistent, and must also increase to enable the block
bootstrap to achieve asymptotically correct coverage probabilities for confidence intervals».
Варианты: неперекрывающийся (NOBB) и перекрывающийся (MBB, Künsch 1989);
«the rates of convergence of the error made with overlapping and non-overlapping blocks
are the same».

🔴 **Честная оценка применимости к нам.** У нас 12 лет месячных данных, горизонт плана —
годы. Число независимых блоков длиной в горизонт получается однозначным (2–4).
Блочный бутстрап на таком ряде даёт интервалы, но ОЧЕНЬ широкие, и это правильный ответ:
**широкий интервал — не дефект метода, а честная мера того, сколько истории у нас есть.**
Вывод: интервалы по историческим когортам публиковать обязательно, но основную статистическую
силу брать из Монте-Карло (§3.1, п.4), где независимость обеспечена конструкцией.

---

## Участок 4. Нормативные эталоны как замена мнению

### 4.1 Greninger et al. (1996) — первоисточник добыт целиком

Greninger S.A., Hampton V.L., Kitt K.A., Achacoso J.A. «Ratios and Benchmarks for Measuring
the Financial Well-Being of Families and Individuals», *Financial Services Review*, 1996,
5(1), 57–70, ISSN 1057-0810.
🔴 **PDF полного текста добыт по открытому адресу** `openjournals.libs.uga.edu/fsr/article/download/3790/3237/10814`
(HTTP 200, 1 107 275 Б) — ScienceDirect и там же зеркало отдают пейволл и капчу
(даже через `r.jina.ai`: «Are you a robot?»).

**Метод — Delphi, дословно из аннотации:**

> «Financial planners and educators comprised a panel of 156 experts in this Delphi study
> designed to identify and refine ratios and benchmarks for measuring financial wellbeing.
> Consensus between the two groups existed for benchmarks on 20 of 22 ratios in the areas of
> liquidity, savings, asset allocation, inflation protection, tax burden, housing expenses,
> and insolvency/credit.»

**Полный набор нормативов — Table 2 «Financial Well-Being Profile», дословно
(с исправлением очевидных ошибок OCR: «2» = «≥», «5»/«S»/«s» = «≤»):**

| Область | Коэффициент | Норматив |
|---|---|---|
| Liquidity | liquid assets / monthly expenses | **≥ 250 %** (≥ 2,5 месячных расходов) |
| Savings | savings / gross income | **≥ 10 %** |
| Asset Allocation | liquid assets / net worth | ≥ 15 % |
| Asset Allocation | net investment assets / net worth | ≥ 50 % |
| Asset Allocation | foreign investments / total investments | ≥ 10 % |
| Inflation Protection | %Δ net worth / rate of inflation | ≥ 2 |
| Inflation Protection | %Δ investment assets / rate of inflation | ≥ 2 |
| Tax Burden | payroll taxes / gross income | ≤ 20 % (доход $31 000); ≤ 30 % ($100 000) |
| Tax Burden | (payroll + property taxes) / gross income | ≤ 25 % ($31 000); ≤ 35 % ($100 000) |
| Housing | renter's expenses / gross income | ≤ 30 % |
| Housing | homeowner's expenses / gross income | ≤ 35 % |
| Insolvency/Credit | nonmortgage debt payments / after-tax income | **≤ 15 % — разумно; ≥ 20 % — danger-point** |
| Insolvency/Credit | total debt payments / after-tax income | **≤ 35 % — разумно; ≥ 45 % — danger-point** |

Уточнение по подушке (§A «Liquidity», дословно):

> «The median value for the ratio involving expenses was 300% suggesting a 3:1 ratio of liquid
> assets to monthly expenses. The mean values, which ranged from 246% for the educators to
> 270% for the planners, were somewhat lower than the overall median. However, these findings
> support a general view that liquid assets should provide a minimum of 2,5 to 3 months of
> living expenses.»

🔴 Честно про норму 10 % сбережений — авторы САМИ сомневаются в ней (§B «Savings»):

> «When respondents were asked to specify the percentages of income that should be saved,
> **identical values were recommended for both gross and net income** by planners and educators
> alike. **These results are problematic** since it would be impossible for the same level of
> savings to comprise similar percentages of both before- and after-tax income levels. Since
> the median recommended savings ratio for both incomes was 10% the research team felt that
> **these responses might have been influenced by widely-held savings norms.**»

То есть авторы прямо пишут: эксперты, скорее всего, повторили общеизвестное правило,
а не вывели число. Это документальное подтверждение опасения владельца.

И как сами авторы понимают статус своих нормативов:

> «the primary function of ratios should be to act as **red flags**…» (DeVaney & Lytton, 1995,
> цит. по Greninger et al.)
> «**Finding values that lie outside the recommended parameters does not necessarily indicate
> a lack of financial health** but instead points to an area worthy of further introspective
> thought and analysis.»

> «this research dealt with benchmarks that are **generally appropriate for families and
> individuals, not considering differences in life-cycle stages, income levels (except the tax
> burden measure), risk tolerances, and economic conditions**. However, financial experts are
> all too aware that a "typical" family/individual does not really exist.»

🔴 **Правило 50/30/20 в этом первоисточнике ОТСУТСТВУЕТ.** Его источник другой
(Warren & Warren Tyagi, «All Your Worth», 2005) и в этой сессии не проверялся.
Не приписывать 50/30/20 работе Greninger.

### 4.2 🔴 Честный вопрос: есть ли норматив, выведенный из ИСХОДОВ, а не из консенсуса?

**Короткий ответ: да, один — и он ровно один найден.**

DeVaney S.A. «The Usefulness of Financial Ratios as Predictors of Household Insolvency:
Two Perspectives», *Financial Counseling and Planning*, 1994, том 5, с. 5–24.
🔴 **PDF добыт целиком**: `https://www.afcpe.org/wp-content/uploads/2018/10/vol-51.pdf`
(HTTP 200, 160 005 Б). Путь к нему — через индекс `afcpe.org/news-and-publications/
journal-of-financial-counseling-and-planning/volume-5/`; угадывание имени файла (`vol51.pdf`
и др.) давало 404, SSRN — 403.

**Почему это ИСХОД, а не мнение** [ПРОЧИТАНО]:

> «The dependent variable was insolvency which was defined as the household having net worth
> less than one month's income. If net worth was less than one month's income in 1986,
> the variable was coded as 1.0 for insolvency, else the variable was coded as 0.0 for solvency.»

Данные — SCF, **1 934 домохозяйства, ратио на 1983 г., исход на 1986 г.** То есть настоящий
проспективный дизайн: норматив измеряется на дату t, факт наступает в t+3.

**Результат логистической регрессии** [дословно]:

> «The predictive power of the model as indicated by the concordant pairs was 75% … which
> suggests that 1986 insolvency status can be accurately predicted for 75% of the households,
> just based on information on whether each household met the three guidelines in 1983.»

> «All other things equal, **not meeting the guideline for the Liquidity ratio was associated
> with a five-fold increase in the probability of being insolvent (16% compared to 3%).**
> For families who met the guideline for Gross Annual Debt Payments compared to Disposable
> Income, the probability of insolvency was **5% compared to 18%** (more than a three-fold
> increase) for those who did not meet the guideline… The effect of the Total Assets/Total
> Liability guideline was a three-fold increase in the risk of becoming insolvent
> (20% compared to 6%).»

Нормативы, которые проверялись:

> «The guideline used in this research was that **if the Liquidity ratio yielded a value greater
> than 0.25 (1/4 of a year or 3 months), the household was reasonably prepared for emergencies**
> such as a temporary job loss.»

**И главное — CART вывел порог ИЗ ДАННЫХ, а не взял из консенсуса** [дословно]:

> «Node 1 of the classification tree splits on **Gross Annual Debts/Disposable Income > .35**.
> This means that households with annual debt payments larger than 35% of disposable income
> were directed to the left…»

> «The analysis yielded a classification tree which had an estimated misclassification rate of
> **16.8% for the learning sample and 15.5% for the test sample**. This value … suggests that
> the classification tree will correctly predict the propensity for insolvency of a new
> observation **about 83% of the time**.»

Относительная важность переменных в дереве: Total Assets/Total Liabilities — 100,
Annual Debt Payments — 96, Shelter Cost — 79, Liquidity — 71.

🔴 **Точный статус этого источника, без приукрашивания.**
DeVaney не выводила из исходов ВСЕ нормативы: пороги (0,25 по ликвидности и др.) она взяла
из обзора Lytton et al. 1991 — то есть из той же экспертной традиции — и **проверила их
предсказательную силу против факта**. Это не «норматив из исхода», это **норматив,
валидированный исходом**, и разница существенна. Единственный порог, действительно
порождённый данными, — **0,35 по отношению годовых платежей по долгу к располагаемому
доходу** (сплит CART).
Показательно, что сама DeVaney отмечает про предшественников:
> «Although Lytton et al. (1991) strongly recommended the use of guidelines with financial
> ratios, **they did not provide empirical evidence of their usefulness.**»

**Вывод участка 4.** Опасение владельца подтверждается документально: нормативы личных
финансов — это в подавляющем большинстве записанное экспертное мнение (Delphi, 156 человек,
1996 год), причём авторы сами предупреждают, что часть ответов повторяет «widely-held norms».
Единственный найденный путь превратить их в эталон из исходов — **дизайн DeVaney: взять
норматив как бинарный признак на дату t и проверить против наблюдаемого исхода в t+k**.
🟢 И это у нас теперь ВЫПОЛНИМО: ОДПФ — панель шести волн 2013–2024 со сквозным
`idind` и повалновыми `aid_h…fid_h`, то есть тот же проспективный дизайн воспроизводится
на российских данных.

🟡 Отдельно: «несколько десятков нормативов личного финансового здоровья США» в виде
единого канонического списка в этой сессии НЕ найдены — найден набор Greninger (22 ratio,
20 с консенсусом) и трёхкоэффициентный набор, используемый как отраслевой стандарт
(liquidity ratio, investment ratio, debt-to-asset ratio) с порогами: подушка «3 to 6 months»
(Keown 2015; Winger & Frasca 2006), investment ratio > 25 % (Baek & DeVaney 2004),
диапазон 25–50 % (Lytton, Garman & Porter 1991), debt-to-asset ≤ 50 % (Winger & Frasca 2002)
[всё — по обзору «Financial Ratios and Financial Satisfaction», ERIC EJ1241055, PDF ПРОЧИТАН].

---

## ПРЯМОЙ ОТВЕТ: план замены эталона для раунда 6

**Одной фразой: эталоном перестаёт быть «что сказали четыре движка» и становится набор
из четырёх независимых опор — реальная популяция ОДПФ, инварианты на реальной траектории,
regret против оракула в Монте-Карло и нормативы, валидированные исходом по DeVaney.
Экспертный консенсус остаётся, но понижается до одной метрики согласованности из восьми.**

Порядок исполнения — по возрастанию стоимости; каждый шаг даёт результат сам по себе.

### Шаг 1 (1–2 дня). Реальная популяция вместо синтетической
Что делать: скачать ОДПФ 6-й и 5-й волн (household + individual, ссылки в §1.3), собрать
портрет склейкой по `id_h`, ре-сэмплировать 12 000 наблюдений с весами `hhwgt`.
Метрика приёмки: **SRMSE₁ ≤ порога на маргиналах дохода, возраста, суммарного долга,
платежа; SRMSE₂ и SRMSE₃ на тройках (доход × долг × возраст)** — считаются против самого
ОДПФ как референса. Доля structural zeros (портреты, нарушающие инварианты модели) —
измеряется и объясняется, не подгоняется.
Что это закрывает: дыру «происхождение распределений не показано». Ответ становится
проверяемым одной строкой: распределения происходят из 6 079 реальных домохозяйств
Банка России, волна 2024.

### Шаг 2 (1 день). Нормативный эталон вместо мнения — в двух ипостасях
(а) **Нормативы Greninger 1996** (полная таблица в §4.1) — как ЖЁСТКИЕ КОРИДОРЫ,
не как правильный ответ: `total debt payments / after-tax income ≤ 35 %` (danger ≥ 45 %),
`nonmortgage ≤ 15 %` (danger ≥ 20 %), подушка ≥ 2,5–3 месячных расходов, сбережения ≥ 10 %.
Метрика: доля рекомендаций модели, выводящих портрет ЗА danger-point, — должна быть 0
там, где выход не вынужден исходным состоянием портрета.
(б) **Российский норматив вместо американского — из ОДПФ.** Медиана желаемой подушки
100 000 ₽ (`o29`), фактическая автономия (`h28`). Проверка: рекомендуемый моделью целевой
размер резерва для портрета с медианными характеристиками не должен расходиться с
медианой `o29` в разы.

### Шаг 3 (2–3 дня). Эталон из ИСХОДА — воспроизвести дизайн DeVaney на ОДПФ
🔴 **Это и есть содержательная замена мнения на исход, и она стала возможна только сегодня.**
Панель ОДПФ склеивается: волна 2022 (`e`) → волна 2024 (`f`), 5 325 домохозяйств есть
в обеих.
- Признаки на 2022: наши инварианты и нормативы как бинарные (ПДН ≤ 0,40; автономия ≥ 3 мес;
  платежи/доход ≤ 0,35).
- Исход на 2024: наблюдаемое ухудшение — падение автономии `h28` до «не больше недели/ни
  одного дня», появление просрочки, рост числа кредитов, обращение в МФО (блок С3).
- Модель: логистическая регрессия + CART, ровно как у DeVaney; метрики — доля конкордантных
  пар (у DeVaney 75 %) и misclassification rate (у неё 15,5 % на тестовой выборке).
Что это даёт: **пороги FINPILOT получают предсказательную валидность против реального
российского исхода**, а не согласие с движками. Если порог 0,40 по ПДН не разделяет
исходы — это находка, а не провал, и её надо принять.

### Шаг 4 (2–3 дня). Regret против оракула — по WER
Реализовать `Regret(p) = 1 − U_model(p)/U_oracle(p)` (§3.1), считать в Монте-Карло на
совместном генераторе «ставка × инфляция» из тем 32–33. Обязательно на тех же прогонах —
Regret четырёх наивных бейзлайнов (пропорция, всё-в-долг, всё-в-резерв, snowball).
Приёмка: медиана Regret модели строго ниже медианы Regret каждого бейзлайна;
разрыв — заявляемая ценность продукта в числах.

### Шаг 5 (1–2 дня). Выживаемость инвариантов на реальной траектории РФ
Когорты старта помесячно 2014–2020, ставка — реальный ряд ЦБ (тема 27 подтвердила HTTP 200).
Метрика: кривая выживаемости (доля когорт без нарушения Rt≥0 и ПДН≤0,40 к месяцу h).
Интервалы — блочный бутстрап с длиной блока ≥ горизонта плюс HAC/Newey–West с `m ≥ h−1`
и автоматическим бандвидтом Эндрюса (§3.3). 🔴 В отчёте прямо написать, что интервалы
широкие, потому что независимой истории 12 лет, а не потому что метод плох.

### Шаг 6. Экспертный консенсус — оставить, но понизить в статусе
Согласие с четырьмя движками остаётся метрикой **M5 из темы 27** (расстояние d(a,e),
ICC(2,k) с нижней границей ДИ), и в отчёте называется согласованностью, а не точностью.
Зона отсутствия консенсуса (амплитуда 66 п.п. в раунде 5) — метрика **M6**: портреты
из неё исключаются из M5 и получают в продукте режим «несколько допустимых планов».
Основание — Grove et al. 2000 из темы 27: механические методы точнее клинических, так что
подгонка под мнение экспертов может уводить ОТ точности.

### Итоговая приёмка вехи 6 — по слабейшему звену
К восьми метрикам темы 27 добавляются пять новых. Веха проходится, когда пройдены все,
а не когда среднее хорошее.

| № | Метрика | Источник | Порог |
|---|---|---|---|
| P1 | SRMSE₁ (маргиналы популяции) | Sun & Erath; arXiv:2302.09193 | публикуется; сравнение с независимым бейзлайном (независимая выборка маргиналов) обязательно |
| P2 | SRMSE₂₋₃ (связки) | там же | строго ниже независимого бейзлайна |
| P3 | STZ-rate (доля недопустимых портретов) | там же | измеряется; каждый класс объяснён |
| P4 | α-Precision / β-Recall (кривые) | Alaa et al., ICML 2022 | отклонение от прямой единичного наклона публикуется |
| P5 | Authenticity | там же | высокая: портреты не копии реальных респондентов ОДПФ (это ещё и 152-ФЗ) |
| O1 | Concordant pairs логистической модели «норматив-2022 → исход-2024» | DeVaney 1994 | > 50 % (порог Amemiya); ориентир DeVaney — 75 % |
| O2 | Misclassification rate CART на тестовой трети | там же | ориентир DeVaney — 15,5 % |
| R1 | Regret против оракула, медиана и p90 | Blanchett 2013 (WER) | строго ниже, чем у каждого из 4 бейзлайнов |
| S1 | Кривая выживаемости инвариантов по когортам | тема 27 §4.3 | публикуется с интервалами; провал когорт объяснён шоком, а не багом |
| N1 | Доля рекомендаций за danger-point Greninger | Greninger et al. 1996 | 0 при невынужденном выходе |

---

## Что делать с 12 000 портретов

🔴 **Перегенерировать. Не оставлять как есть и не дополнять.**

Почему не «оставить»: главная претензия к раунду 5 — не число портретов и не их качество,
а **непоказанное происхождение распределений**. Никакая метрика поверх нынешних портретов
эту претензию не снимает, потому что снимать её должен источник, а не проверка.

Почему не «дополнить»: смесь «часть из ОДПФ, часть выдуманная» делает невозможными
SRMSE и α-Precision — референс перестаёт быть чистым, и любое число становится
неинтерпретируемым.

**Как перегенерировать (без генеративных моделей, это важно):**
1. База — взвешенный ре-сэмплинг 12 000 из 6 079 домохозяйств ОДПФ-2024 по `hhwgt`.
   Никакого CTGAN/TVAE: донор репрезентативен и снабжён весами, генеративная модель здесь
   добавила бы только новый источник ошибки и новую вещь, которую надо доказывать.
2. Сглаживание непрерывных величин (доход, остаток долга, платёж) — ядерное, чтобы
   в популяции не было 6 079 повторяющихся точек; ширина ядра подбирается по SRMSE₁.
3. Очистка — по прямому предупреждению ЦБ («не являются очищенными от выбросов и
   пропусков»): коды 97/98/997/998 → пропуск; импутация только явная и логируемая;
   доля отброшенных портретов — в отчёт.
4. Ставка и инфляция портрету НЕ приписываются из ОДПФ — они генерируются совместно
   по темам 32–33; из ОДПФ берётся ставка по конкретному кредиту (С4.8, С2.10, С3.4)
   как характеристика уже существующего долга.
5. Старые 12 000 не выбрасывать: сохранить как **набор регрессии** и прогнать на нём
   метаморфические отношения M1–M4 темы 27. Расхождение M1–M4 между старой и новой
   популяцией — сигнал, что метрика зависела от популяции, а не от модели.

**Побочный выигрыш:** после перегенерации фраза «12 000 синтетических портретов»
в описании продукта заменяется на «12 000 портретов, ре-сэмплированных из Всероссийского
обследования домохозяйств по потребительским финансам Банка России, волна 2024
(6 079 домохозяйств, 32 субъекта РФ)». Это защитимо на защите, перед регулятором
и перед банком-партнёром; «синтетические» — не защитимо.

---

## Что не добыто и почему (коды ответа)

1. **Greninger et al. 1996 через ScienceDirect** — пейволл + антибот. `r.jina.ai` вернул
   страницу капчи Cloudflare («Are you a robot?», reference a38e5f84787e1585).
   🟢 Обойдено: полный PDF взят с `openjournals.libs.uga.edu` (HTTP 200).
2. **DeVaney 1994 через SSRN** — `curl` с браузерным UA дал **403**; `r.jina.ai` вернул
   пустую оболочку без текста.
   🟢 Обойдено: полный PDF `afcpe.org/wp-content/uploads/2018/10/vol-51.pdf` (HTTP 200).
   Угадывание имени (`vol51.pdf`, `vol52.pdf`, `vol511.pdf`, `vol5-1.pdf`) дало 404 —
   адрес взят со страницы-индекса, как и предписано.
3. **Официальный канал микроданных Росстата** — `rosstat.gov.ru/microdata` **404**,
   `gks.ru/free_doc/new_site/vndn-2024/` **403**, `obdx.gks.ru` — HTTP 200, но за формой
   входа. Микроданные ВНДН/КОУЖ взяты через зеркало tochno.st (CC BY 4.0).
   🟡 Не проверено лично: реальная выгрузка ВНДН с `storage.yandexcloud.net` (не качал,
   участок 1 закрыт данными ЦБ). Объём выборки ВНДН (60/160 тыс.) — со сниппета,
   первоисточник Росстата не открывался.
4. **Страница `hse.ru/en/rlms/` и «Citing the Data»** — не читались; формулировка про
   «register online and accept Data Use agreement» взята со сниппета поиска и помечена
   как непрочитанная. Условие «публичные данные без application process» — прочитано
   на зеркале UNC. Расхождение между двумя зеркалами не разрешено.
5. **Индивидуальный файл ОДПФ (`anketa_6_1.zip`, 17,2 МБ)** — доступность подтверждена
   (HTTP 200, точный размер), но файл НЕ скачивался и структура покредитного блока
   проверена **по вопроснику**, а не по колонкам CSV. Проверено по CSV только домохозяйство.
6. **Choupani & Mamdoohi (IPF vs simulated annealing)** — ScienceDirect, пейволл,
   полный текст не читан; цитата про округление — со сводки поиска.
7. **Первоисточники по блочному бутстрапу** (Künsch 1989; Politis & Romano 1994) —
   не открывались; §3.3(б) опирается на сводку поиска, а не на прочитанный текст.
   Это самое слабое место отчёта по цитированию.
8. **Blanchett, Kowara & Chen (2012)** — оригинал WER не читан; определение взято
   из изложения Blanchett 2013, где оно дано дословно и с указанием на первоисточник.
9. **50/30/20** — первоисточник (Warren & Warren Tyagi, 2005) не проверялся.
   Установлено отрицательное: в Greninger et al. 1996 этого правила НЕТ.
10. **Канонический список «нескольких десятков» нормативов финансового здоровья США** —
    не найден как единый документ (см. §4.2, 🟡).

---

## Метод поиска

**WebSearch был доступен весь прогон** (в отличие от предыдущего агента) — 14 вызовов.
`WebFetch` — 6 вызовов, из них 1 отдал 403 (FPA) и 1 потребовал ручного следования редиректу
(PMC). Остальное — `curl`/`pdftotext`/`python3` через Bash.

**Что сработало, по каналам:**
- 🟢 `curl -sk --http1.1` по cbr.ru — весь ОДПФ, включая 5 МБ данных. Ключ: адрес взят
  с работающей страницы, не угадан (угаданный вариант дал 404).
- 🟢 `WebFetch` — RLMS (оба зеркала), tochno.st, PMC (после ручного редиректа), Frontiers.
- 🟢 `r.jina.ai` — пробил `financialplanningassociation.org` (прямой `WebFetch` — 403).
  🔴 НЕ пробил ScienceDirect: вернул страницу капчи, а не текст. Граница канала уточнена:
  антибот Cloudflare с интерактивной капчей ему не поддаётся.
- 🟢 `pdftotext` — все шесть PDF (Alaa/PMLR, Jutras-Dubé/arXiv, Andrews/Cowles, Stata manual,
  Greninger/UGA, DeVaney/AFCPE) разобраны без единой осечки.
- 🟢 **Приём, добавленный этой сессией:** архивы cbr.ru содержат имена файлов кириллицей
  в CP866, и системный `unzip` падает с «Illegal byte sequence». Обход —
  `zipfile` в Python с `n.encode('cp437').decode('cp866')`. Записать в базу приёмов.
- 🟢 **Второй приём:** индекс журнала вместо угадывания имени PDF. Четыре угаданных имени
  дали 404, страница-индекс тома дала точный адрес с первого раза.

**Чего НЕ делалось:** подагентов — ноль, как предписано. Сырьё писалось в файл четырьмя
дописываниями по ходу (скелет → участок 1 → участок 2 → участки 3–4 → финал), не одним
`Write` в конце.

**Главное отличие этого прогона от предыдущих по теме калибровки:** отчёт содержит числа,
посчитанные мной на скачанном первичном файле (§1.3.1), а не пересказ публикаций.
Файл `database_FB_household_261224s_6wave.csv` лежит распакованным в скретчпаде сессии
(65 497 007 Б); при новой сессии качается заново по ссылке из §1.3 за один `curl`.

---

## ДОБОР 11.09.2026

Дата: 11.09.2026. Основание: при первом прогоне 10.09.2026 агенту запретили подагентов,
часть работы осталась недобытой (раздел «Что не добыто и почему», 10 пунктов).
Владелец: довести до полноты.

🔴 **Ограничение инструментов этого прогона.** `WebSearch` исчерпан на сессию окончательно
(400/400, бюджет общий с подагентами) — не использовался ни разу. Exa недоступна (404).
`r.jina.ai` отвечает 401 — канал, который спас Blanchett 2013 в первой редакции, в этом
прогоне мёртв. Замена, применённая фактически: **OpenAlex** (поиск работ),
**Crossref** (реквизиты), **Unpaywall** (отличает «не нашли» от «открытого доступа нет вовсе»),
**Semantic Scholar**, институтские репозитории (DSpace 7: `/server/api/core/bitstreams/<uuid>/content`,
а не `/bitstreams/<uuid>/download` — тот отдаёт 405), `curl -sk --http1.1` для госсайтов РФ.

### Шаг 0. Разбор задачи

**Главные сущности:** (а) микроданные ОДПФ ЦБ как источник правдоподобной популяции;
(б) альтернативные обследования (RLMS, КОУЖ, ОБДХ, ВНДН, НБКИ/ОКБ, SCF/HFCS/PSID);
(в) веса SAW-свёртки и вопрос, откуда их брать — из нормативов или из наблюдаемого поведения;
(г) нормировка как условие осмысленности любого веса (тема 39, Тофаллис 2014).

**Какие факты нужны:** точная структура файлов ОДПФ (имена переменных дохода, платежей,
остатков, ставок, сбережений), лицензия, сопоставимость волн; по альтернативам — что каждая
даёт и чего не даёт для калибровки; по контрпримерам — есть ли доказанные случаи, когда
калибровка по наблюдаемому поведению хуже нормативных весов.

**Границы:** РФ, данные 2013–2024; зарубежные обследования — только как методологический
образец, не как источник для калибровки под РФ.

**Что важнее всего владельцу:** не библиография, а исполнимость. Вопрос звучит как
«можно ли из ОДПФ построить распределение „свободный поток → фактическое распределение
между долгами/резервом/целями“» — то есть можно ли учиться весам у данных.

**Форма ответа:** дописанный раздел с фактическими выгрузками (не пересказом) + явный блок
«ИЗМЕНЕНИЯ ВЫВОДОВ».

**Три способа ответить, выбран один.**
1. *Только литература* (искать статьи про калибровку весов по поведению) — отвергнут:
   первая редакция уже показала, что решающий ресурс лежит на диске, а не в статьях.
2. *Только данные* (скачать всё и посчитать) — отвергнут: не отвечает на п. 4 задания
   (контрпримеры) и на п. 5 (следствие Тофаллиса), а именно они решают, стоит ли вообще
   калибровать веса по данным.
3. 🟢 **Выбран: данные первыми, литература вторыми, и литература как ФИЛЬТР на данные.**
   Сначала фактически вскрыть индивидуальный файл ОДПФ (в первой редакции он не качался —
   пункт 5 списка недобытого), установить, какие переменные реально есть; затем проверить
   литературой, законно ли из этих переменных выводить веса. Порядок важен: если
   контрпримеры покажут, что учиться у данных вредно, вся работа с файлами всё равно
   нужна — для популяции, а не для весов; обратный порядок сделал бы её условной.

### Шаг 1. Классификация запроса

**Breadth-first.** Четыре независимых под-вопроса, почти не пересекающихся по источникам:
(1) практика ОДПФ — файлы; (2) альтернативы ОДПФ — обследования; (3) контрпримеры —
литература по поведенческой калибровке; (4) следствие Тофаллиса — чтение своего же файла
темы 39. Это не «один вопрос многими ракурсами» (не depth-first) и заведомо не straightforward.

### Шаг 2. План и число подагентов

**Два подагента, последовательно, не веером** (потолок задан владельцем).
- Участок 1 (файлы ОДПФ) и участок 4 (Тофаллис) — делаю сам: первый требует Bash и локальной
  работы с персональными по форме данными, второй — чтения файла нашей же базы.
- Подагент A — контрпримеры: калибровка весов по поведению против нормативных весов.
  Это главный содержательный риск задания, отдаётся отдельному контексту.
- Подагент B — альтернативы ОДПФ: RLMS, КОУЖ, ОБДХ, ВНДН, НБКИ/ОКБ, SCF/HFCS/PSID.

Дальше — по ходу, дописыванием.

### Д.1. Микроданные ОДПФ — ПРАКТИКА: файлы вскрыты, оба, структура описана фактически

Закрывает пункт 5 списка недобытого («индивидуальный файл не скачивался, структура покредитного
блока проверена по вопроснику, а не по колонкам CSV»).

#### Д.1.1 Что скачано и распаковано (11.09.2026, `curl -sk --http1.1` + браузерный UA)

Все пять адресов из §1.3 живы, размеры совпали с замером 10.09.2026 байт в байт:

| Файл | HTTP | Байт |
|---|---|---|
| `174715/anketa_6.zip` (ДХ, 6-я волна) | 200 | 5 147 023 |
| `174716/anketa_6_1.zip` (индивиды, 6-я волна) | 200 | 17 191 480 |
| `174712/quet_6_2024.zip` (вопросники) | 200 | 1 957 504 |
| `174713/readme_n.zip` | 200 | 1 004 |
| `174710/method_6_2024.pdf` | 200 | 588 340 |

Содержимое архивов (распаковка `zipfile`+cp866, `unzip` по-прежнему падает):

| Внутреннее имя | Байт |
|---|---|
| `12/database_FB_household_261224s_6wave.csv` | 65 497 007 |
| `12/database_FB_household_261224s_6wave.RData` | 2 570 906 |
| `34/database_FB_individual_28112024_6wave.csv` | **159 903 677** |
| `34/database_FB_individual_28112024_6wave.RData` | 3 539 496 |
| `Вопросники 6ая волна/Вопросник домохозяйства_2024.pdf` | 1 013 604 |
| `Вопросники 6ая волна/Индивидуальный вопросник_2024.pdf` | 1 418 983 |

**Индивидуальный файл, замерено:** **11 835 строк × 1 859 столбцов**, разделитель — **запятая**,
не «;»; кодировка UTF-8; значения — **текстовые метки, а не коды** («Да», «Нет»,
«ЗАТРУДНЯЮСЬ ОТВЕТИТЬ», «ОТКАЗ ОТ ОТВЕТА», «НЕТ ОТВЕТА», `NA` для незаданных по фильтру).
Число строк ровно совпало с заявленным ЦБ («11835 респондента»).
Ключи: `id_w, idind, id_i, redidi, id_h, psu, gr_vozr, gr_educ, sett_typ, size, inwgt` —
🔴 **вес индивида называется `inwgt`, а не `hhwgt`**; у индивидов 16 различных значений веса,
у ДХ — своё поле `hhwgt`. Склейка с домохозяйством — по `id_h` (6 079 уникальных значений
в индивидуальном файле, ровно как ДХ в household).

🔴 **Практическое следствие формата.** Файлы `.csv` от ЦБ получены из `.RData` через
`haven::as_factor(data)` — это прямо написано в `readme.txt` архива `readme_n.zip`:
> «#Вариант 3. данные в формате .csv (Excel): значения в ячейках - текстовые
> # Преобразуйте данные, чтобы сохранить лейблы
> data <- haven::as_factor(data)»
То есть CSV — **лейблы**, а не коды. Совет §1.5 первой редакции «кодировать 97/98/997/998
как пропуск» **к CSV неприменим**: в CSV на этих местах уже стоят текстовые
«ЗАТРУДНЯЮСЬ ОТВЕТИТЬ» / «ОТКАЗ ОТ ОТВЕТА». Числовые коды живут в `.RData`. Фильтровать надо
по строкам-меткам (список выше), и это заметно надёжнее.
🟡 Побочный дефект того же преобразования: крупные суммы записаны в R-нотации — в поле
суммы кредита встречается `3e+05`, `1e+05`, `2e+05`. Парсер обязан быть float-парсером,
а не `int(str)`.

#### Д.1.2 Соответствие «вопрос → переменная» установлено точно

Вопросники несут имена переменных прямо в вёрстке, с префиксом `PF`/`PF_`; в CSV префикс
снят и имя опущено в нижний регистр (`PFC47_1` → `c47_1`, `PF_H28` → `h28`, `PFO61_R` → `o61_r`).
Это снимает всю прежнюю неопределённость с именами.

🔴 **И это же выявило ошибку первой редакции. В §1.3 написано «С4.8 ставка» — НЕВЕРНО.**
Дословно из вопросника (`Индивидуальный вопросник_2024.pdf`, с. 63):

> «С4.8. Посмотрите, пожалуйста, на карточку и скажите, **где Вы брали этот кредит**?
> [ИНТЕРВЬЮЕР! ПЕРЕДАЙТЕ КАРТОЧКУ В_43] В ОФИСЕ БАНКА … 1 … В МИКРОФИНАНСОВОЙ
> ОРГАНИЗАЦИИ … 3» (переменные `c48_1`, `c48_2`, `c48_3`)

Значения в данных это подтверждают: `c48_1` принимает ровно шесть значений, из них
«В ОФИСЕ БАНКА» (526), «В БАНКЕ ВНЕ ОФИСА… ОНЛАЙН» (144), «В МИКРОФИНАНСОВОЙ ОРГАНИЗАЦИИ» (5).
Это **канал выдачи, а не процент**.

**Фактический блок потребительского кредита С4 (до трёх крупнейших кредитов):**

| Вопрос | Что спрашивают | Переменные |
|---|---|---|
| С4.1 | есть ли невыплаченные потребкредиты | `p9_1` |
| С4.2 | цель кредита (11 вариантов, мультивыбор) | `p95_11…p95311` |
| С4.3 | год и месяц оформления | `p93_1y`,`p93_1m` … |
| С4.4 | **сумма кредита, ₽** | `c44_1,c44_2,c44_3` |
| С4.4а | интервал суммы с карточки (если трудно назвать) | `c44a_1…` |
| С4.5 | **срок, месяцев** | `p96_1,p96_2,p96_3` |
| С4.6 | **остаток к выплате, ₽** | `p911_1,p911_2,p911_3` |
| С4.6а | интервал остатка | `p911a1…` |
| С4.7 | **ежемесячный платёж, ₽** | `c47_1,c47_2,c47_3` |
| С4.7а | интервал платежа | `c47a_1…` |
| С4.8 | **где брали кредит** (канал) | `c48_1…` |
| С4.9 | почему именно там (до двух ответов) | `c49_11,c49_12,…` |

🔴 **Ставки в блоке С4 НЕТ ВООБЩЕ.** Утверждение первой редакции и задания
(«ставка по каждому кредиту») **опровергнуто на первоисточнике**. Ставка спрашивается
только в четырёх других местах:

| Где | Вопрос, дословно | Переменные | Заполнено, n |
|---|---|---|---|
| Кредитные карты | «С2.10. Какова годовая процентная ставка по этой кредитной карте?» | `p611_1..3` | 891 |
| МФО/ломбарды | «С3.4. Под какой процент взят этот займ? **Если невыплаченных займов несколько, то назовите минимальную ставку.**» | `c3_4` | **23** |
| Автокредиты (блок Е) | «Е18. Какова (была) годовая процентная ставка по этому кредиту?» | `e22_1..3` | 646 |
| Ипотека (анкета ДХ) | «А26. Какова годовая процентная ставка по этому кредиту?» | `a64` | — |

🔴 И второй пробел, прямо бьющий по Шагу 3 первой редакции: **по потребительскому кредиту
(блок С4) просрочка НЕ спрашивается.** Слово «просрочка» в вопросниках не встречается ни разу;
формулировка анкеты — «задержка платежей … сроком 3 месяца и более», и она есть **везде,
кроме блока С4**:

| Тип долга | Вопрос | Переменные |
|---|---|---|
| Кредитная карта | С2.15 (сейчас) / С2.16 (раньше) | `p616_1..3` / `p617_1..3` |
| Автокредит | Е22 | блок `e` |
| Кредит на основную недвижимость | А30 / А31 | `a69` / `a70` |
| Кредит на дом, иную недвижимость | В1.21 / В2.22 / В3.21 | `b1_49` и аналоги |
| **Потребительский кредит (С4)** | **отсутствует** | **—** |

То есть исход «появление просрочки» измерим для карт, авто и недвижимости, но **не для того
класса долга, который в популяции самый частый**. Досрочное погашение спрашивается ещё уже —
**только по рефинансированному ипотечному**: «А35. Ваше домохозяйство планируете погашать
этот новый кредит досрочно или нет?» (`a73`), и это **намерение**, а не факт.

**Ключевые переменные анкеты домохозяйства (установлены точно):**

| Вопрос | Смысл | Переменная |
|---|---|---|
| Н12 | устойчивый регулярный ежемесячный доход ДХ | `h47_r` |
| Н13 | весь средний ежемесячный суммарный доход ДХ | `h48_r` |
| Н14 | сколько ДХ тратит ежемесячно | `h49_r` |
| Н15 | автономия на сбережениях | `h28` |
| А26 / А28 / А29 | ставка / остаток / платёж по ипотеке | `a64` / `a66` / `a67` |
| А30 / А31 | текущая и прошлая задержка по ипотеке | `a69` / `a70` |
| О24 / О25 | крупные расходы на 5–10 лет / уже копят | `o27` / `o28` |
| О26 | сколько ДОЛЖНО быть в резерве, ₽ | `o29` |
| О29 / О30 | есть ли сбережения / их сумма | `h33` / `h34_r` |
| О35 / О36 / О37 | **откладывали ли за последний месяц / сколько ₽ / обычно так же?** | `o60` / `o61_r` / `o62` |

🟢 Находка, которой в первой редакции не было: **О35–О36 (`o60`, `o61_r`) — это прямая
месячная величина «сколько ушло в сбережения»**, то есть наблюдаемый поток, а не остаток.
Именно она — единственный кандидат на «фактическое распределение» в терминах задания.

#### Д.1.3 Посчитано на скачанных файлах 11.09.2026 (взвешено `hhwgt` / `inwgt`)

**Домохозяйства, суммы в ₽:**

| Переменная | n | p10 | p25 | медиана | p75 | p90 | среднее |
|---|---|---|---|---|---|---|---|
| `h47_r` Н12 устойчивый доход | 5 034 | 20 000 | 29 200 | **50 000** | 85 000 | 132 500 | 66 839 |
| `h48_r` Н13 весь доход | 4 889 | 20 450 | 30 000 | **50 000** | 90 000 | 140 000 | 69 362 |
| `h49_r` Н14 расходы | 4 560 | 18 000 | 25 000 | **40 000** | 70 000 | 100 000 | 53 201 |
| `o29` О26 «должно быть в резерве» | 5 469 | 30 000 | 50 000 | **100 000** | 200 000 | 500 000 | 206 659 |
| `h34_r` О30 все сбережения | 1 552 | 50 000 | 100 000 | 180 000 | 300 000 | 700 000 | 340 117 |
| `o61_r` О36 отложено за месяц | 1 213 | 3 000 | 5 000 | **10 000** | 20 000 | 40 000 | 17 364 |

🟢 Медиана `o29` = **100 000 ₽** воспроизвелась в точности (первая редакция дала то же).
Средняя разошлась: 206 659 против 212 665 — 🟡 причина в цензуре выбросов: здесь отброшены
значения ≥ 50 млн ₽; расхождение 2,8 % и не влияет на выводы. p10 разошёлся сильнее
(30 000 против 45 000) — вероятно, разная обработка отказов; для канона брать медиану,
она устойчива.

**Свободный поток = Н13 − Н14** (посчитан впервые):
n = 4 384, p10 = 0, p25 = 0, **медиана 5 000 ₽**, p75 = 19 950, p90 = 40 000, среднее 16 128.
🔴 Доля домохозяйств с **отрицательным** свободным потоком — **0,4 %**. Это не реальность,
а артефакт метода: Н13 и Н14 — две независимые самооценки «на глаз», и респондент почти
никогда не называет расход выше дохода. Для калибровки инварианта Rt ≥ 0 эта пара
непригодна; у четверти выборки поток ровно 0 (p25 = 0), то есть названы равные числа.

**Норма сбережения за месяц** среди тех, кто откладывал: `o61_r`/`h48_r`,
n = 1 130, p10 = 6 %, p25 = 10 %, **медиана 15 %**, p75 = 23 %, p90 = 34 %, среднее 19 %.
🟢 Это прямое эмпирическое сопоставление с нормативом Greninger «savings / gross income ≥ 10 %»
(§4.1): у откладывающих российских ДХ медиана **выше** норматива — 15 %. Но откладывают
не все (см. ниже), так что по всей популяции норма сбережения существенно ниже 10 %.

**Категориальные, взвешенные % (база — все 6 079 ДХ, отказы НЕ исключены):**

| Вопрос | Распределение |
|---|---|
| О35 (`o60`) откладывали ли за месяц | **NA 51,7** · Да 27,6 · Нет 20,0 · отказ/ЗО 0,6 |
| О29 (`h33`) есть ли сбережения вообще | Да **48,3** · Нет 46,5 · отказ 5,1 |
| О24 (`o27`) крупные расходы на 5–10 лет | Нет 74,3 · **Да 21,9** · ЗО 3,6 |
| О25 (`o28`) уже начали копить | NA 78,1 · **Да 12,5** · Нет 9,3 |
| Н15 (`h28`) автономия | ≤месяца 30,6 · несколько мес. 25,1 · ≤недели 13,0 · ни дня 8,6 · ≤2 недель 8,2 · **полгода+ 7,3** · ЗО 6,4 |

🔴 **NA 51,7 % в О35 — важнее, чем кажется.** Вопрос задаётся по фильтру, и половина
выборки его не получила. Любая статистика «сколько откладывают россияне», посчитанная
по `o61_r` без учёта этого фильтра, завышена вдвое.

**Индивиды (n = 11 835, взвешено `inwgt`):**

| Продукт | Доля «Да», % |
|---|---|
| С4.1 потребительский кредит (`p9_1`) | **5,85** |
| С2.1 кредитная карта (`c2_1`) | **7,35** |
| С3.1 займ в МФО/ломбарде (`c3_1`) | **0,34** |

| Переменная | n | p10 | p25 | медиана | p75 | p90 |
|---|---|---|---|---|---|---|
| `c44_1` сумма 1-го кредита, ₽ | 645 | 50 000 | 100 000 | **200 000** | 500 000 | 1 000 000 |
| `p911_1` остаток, ₽ | 515 | 15 000 | 35 000 | **100 000** | 300 000 | 605 000 |
| `c47_1` платёж, ₽/мес | 646 | 2 300 | 4 500 | **7 900** | 14 000 | 23 000 |
| `p96_1` срок, мес | 650 | 12 | 36 | **60** | 60 | 60 |
| `p611_1` ставка по карте, % | 891 | 10 | 18 | **23** | 27 | 30 |
| `c3_4` ставка МФО, % | **23** | 1 | 5 | 12 | 25 | 50 |
| `e22_1` ставка автокредита, % | 646 | 9 | 12 | **16** | 18 | 22 |

Полнота покредитного кортежа: из 683 человек с потребкредитом **полный кортеж
(сумма + остаток + платёж + срок) есть у 492**, неполный — у 191 (28 %).

**Долговая нагрузка на уровне ДХ:** хотя бы один член с потребкредитом / картой / МФО —
**17,7 %** взвешенно (1 177 ДХ из 6 079). Платёж по ипотеке заполнен у **3,9 %** ДХ.

#### Д.1.4 🔴 ПРЯМОЙ ОТВЕТ на главный вопрос задания

**Вопрос:** можно ли из ОДПФ построить распределение «свободный поток → фактическое
распределение между долгами, резервом и целями»?

**Ответ: НЕТ. И это не вопрос усилий — ячейка данных физически пуста.** Посчитано
пересечение трёх условий на 6 079 домохозяйствах:

| есть долг | свободный поток > 0 | откладывал за месяц | n | взвеш. % |
|---|---|---|---|---|
| нет | нет | нет | 2 191 | 36,9 |
| нет | да | нет | 1 528 | 25,8 |
| нет | да | да | 1 126 | 18,5 |
| нет | нет | да | 426 | 6,8 |
| **да** | нет | нет | 389 | 5,9 |
| **да** | да | нет | 260 | 3,8 |
| **да** | **да** | **да** | **106** | **1,6** |
| да | нет | да | 53 | 0,7 |

🔴 **Домохозяйств, у которых одновременно есть долг, положительный свободный поток,
факт откладывания И названная сумма отложенного, — 95 из 6 079.** Это и есть весь
эмпирический материал, на котором в принципе наблюдается решение «поток делится между
долгом и резервом». Девяносто пять наблюдений.

Для этих 95 посчитано отношение «отложено / свободный поток»:
p10 = 0,18 · p25 = 0,28 · **медиана 0,50** · p75 = 1,00 · p90 = 1,11;
у **13,7 %** отношение **больше единицы** — отложено больше, чем «свободно» по разнице
Н13−Н14, то есть две самооценки внутренне противоречивы.

**Три причины, почему даже эти 95 не дают весов модели — и каждая смертельна по отдельности:**

1. **«В долг» у нас — это ДОСРОЧНОЕ погашение, то есть выбор. В ОДПФ наблюдается только
   `c47_*` — договорный платёж, то есть обязанность.** Вопроса «сколько вы внесли сверх
   графика» в анкете нет; ближайшее — намерение по ипотеке (`a73`, А35), да и то бинарное
   и только для рефинансированного кредита. Модель FINPILOT распределяет **свободный**
   поток; ОДПФ измеряет **связанный**. Это разные величины, и никакая обработка одну
   в другую не превращает.
2. **«В цели» не измерено суммой вовсе.** Есть только бинарное «начали копить под цель»
   (`o28`, 12,5 % ДХ); сумма, идущая на цель, отдельно от общей `o61_r` не спрашивается.
   Третьей доли SAW-свёртки в данных просто нет.
3. **Числитель и знаменатель несопоставимы по природе.** `o61_r` — прямой вопрос о факте;
   Н13−Н14 — разность двух округлённых самооценок. Отсюда и 13,7 % отношений > 1, и 0,4 %
   отрицательных потоков.

**Что ОДПФ всё-таки даёт, и это по-прежнему много:**
🟢 Порождение **правдоподобной популяции портретов** (участок 1 первой редакции) —
подтверждается полностью и теперь стоит на вскрытых файлах: доход, расходы, сбережения,
автономия, цель, покредитный долг с суммой/остатком/платежом/сроком, веса, регион.
🟢 **Эмпирические ограничения на веса** (не сами веса): медиана желаемого резерва 100 000 ₽,
доля целевых накопителей 21,9 %, медианная норма сбережения у откладывающих 15 %,
медианный платёж по потребкредиту 7 900 ₽ при медианном доходе ДХ 50 000 ₽.
🔴 **Не даёт: ставку по потребкредиту, просрочку по потребкредиту, факт досрочного
погашения, сумму на цель.** Четыре из них — ровно те, что нужны для Avalanche-фильтра
и для эталона из исхода.

#### Д.1.5 Лицензия и условия — перепроверено, изменений нет

Условие со страницы ЦБ — единственное («Ссылка на источник…», §1.3, цитата приведена
дословно ещё 10.09.2026). Никакого клик-соглашения, регистрации или заявки при скачивании
файлов 11.09.2026 не потребовалось: пять прямых `curl` дали 200 без кук и без редиректов
на форму. 🔴 Оговорка ЦБ, которую нельзя терять: **«Данные опроса представлены в двух
форматах .csv и .RData и не являются очищенными от выбросов и пропусков.»**
Работа с файлами велась только локально, в скретчпаде сессии; наружу не выгружалось ничего.

### Д.2. Волны ОДПФ: какие есть и какие СОПОСТАВИМЫ — измерено, а не предположено

#### Д.2.1 Найдены объединённые файлы всех волн (в первой редакции их не было)

Разбор HTML страницы ЦБ дал два адреса, отсутствовавшие в §1.3, — **объединённые данные
по всем шести волнам**:

| Файл | URL | Байт |
|---|---|---|
| Объединённые данные, анкета ДХ, все волны | `https://www.cbr.ru/Content/Document/File/145700/t_ankea.rar` | **15 789 758** |
| Объединённые данные, индивидуальная анкета, все волны | `https://www.cbr.ru/Content/Document/File/145701/t_anketa_1.rar` | **28 176 954** |
| Итоговый технический отчёт, 6-я волна | `https://www.cbr.ru/Content/Document/File/174711/inf.pdf` | 1 004 558 |

🔴 **Формат — RAR5, не ZIP.** `unrar`, `unar`, `7z` в системе отсутствуют; **`bsdtar` (штатный,
`/usr/bin/bsdtar`) RAR5 читает и распаковывает без ошибок**, включая кириллические имена
(`ЭП11_Объединенные данные по анкете для домохозяйства_все волны/`). Приём в базу приёмов.

Внутри: `database1-6_FB_household_261224s.csv` — **387 843 721 байт**, 2 680 столбцов,
**36 322 строки** (все волны в одной таблице).

#### Д.2.2 Строк по волнам

| Волна | 2013 | 2015 | 2018 | 2020 | 2022 | 2024 |
|---|---|---|---|---|---|---|
| Домохозяйств | 6 103 | 6 027 | 6 012 | 6 020 | 6 081 | **6 079** |

Панельные ключи заполняются накопительно и корректно: в строках волны 2024 заполнены все
шесть `aid_h…fid_h`, в строках 2013 — только `aid_h`. Панель склеивается, как и заявлено.

#### Д.2.3 🔴 Но сопоставимы волны НЕ ПО ВСЕМУ. Измеренная картина

Заполненность ключевых переменных по волнам (число непропущенных значений):

| Переменная | 2013 | 2015 | 2018 | 2020 | 2022 | 2024 |
|---|---|---|---|---|---|---|
| `h28` автономия | 5 916 | 5 860 | 5 809 | 5 789 | 5 685 | 5 638 |
| `o27` цель на 5–10 лет | 5 824 | 5 797 | 5 785 | 5 791 | 5 820 | 5 824 |
| `o28` уже копят | 2 335 | 1 956 | 1 804 | 1 543 | 1 487 | 1 417 |
| `o29` желаемый резерв | 5 346 | 5 448 | 5 398 | 5 328 | 5 646 | 5 469 |
| `h33` есть сбережения | 5 986 | 5 937 | 5 891 | 5 878 | 5 783 | 5 729 |
| `h34_r` сумма сбережений | 1 334 | 1 433 | 1 322 | 1 334 | 1 389 | 1 552 |
| **`h47_r` доход устойчивый** | **0** | **0** | **0** | **0** | 5 030 | 5 034 |
| **`h48_r` доход весь** | **0** | **0** | **0** | **0** | 4 834 | 4 889 |
| **`h49_r` расходы** | **0** | **0** | **0** | **0** | 4 549 | 4 560 |
| **`o60` откладывали за месяц** | **0** | **0** | **0** | **0** | 2 680 | 2 897 |
| **`o61_r` сколько отложили** | **0** | **0** | **0** | **0** | 1 055 | 1 213 |
| **`a64` ставка по ипотеке** | **0** | **0** | **0** | **0** | 261 | 260 |
| **`a66/a67` остаток/платёж ипотеки** | **0** | **0** | **0** | **0** | 192/267 | 193/270 |
| **`a69/a70` задержки по ипотеке** | **0** | **0** | **0** | **0** | 277 | 278 |

🔴 **Доход, расходы, месячный поток сбережений и ВЕСЬ ипотечный блок существуют только
в волнах 2022 и 2024** — тех двух, что провёл Банк России. Четыре волны Минфина (2013–2020)
в объединённом файле по этим полям пусты полностью (ровно 0, не «мало»).

Общая картина сопоставимости, посчитанная по всем 2 680 столбцам (порог — заполнение
≥ 20 % строк волны):

| Волна | 2013 | 2015 | 2018 | 2020 | 2022 | 2024 |
|---|---|---|---|---|---|---|
| Реально заполненных столбцов | 268 | 272 | 273 | 275 | 291 | **296** |

- **Сквозных столбцов (заполнены ≥ 20 % во ВСЕХ шести волнах) — 96.**
- Столбцов, заполненных и в 2022, и в 2024, — 281; из них **185 отсутствуют в 2013**.

**Что это меняет в плане первой редакции.** §1.5 обещал «панель 6 волн 2013–2024 для проверки
устойчивости распределений во времени», а §«Шаг 3» строил дизайн DeVaney на связке
2022 (`e`) → 2024 (`f`). 🟢 Шаг 3 уцелел: он опирается ровно на те две волны, где данные есть.
🔴 А обещание «шести волн» надо снять: по доходу, расходам и долгу ОДПФ — **двухволновая
панель**, 2022 и 2024, один межволновой интервал. По автономии, целям и желаемому резерву —
да, полные шесть волн, и это ценный длинный ряд (`h28`, `o27`, `o29`, `h33` заполнены
в каждой волне).

🔴 **И это добивает идею калибровки весов по поведению.** Дизайн «признак на t → исход на t+k»
имеет ровно **одну** реализацию (2022→2024), то есть одно наблюдение шока на когорту,
а не шесть. Доверительные интервалы по такому дизайну строятся только внутри выборки
домохозяйств, но не по времени.

#### Д.2.4 Панель 2022→2024: сколько домохозяйств реально дожили

Посчитано на файле волны 6 (`database_FB_household_261224s_6wave.csv`, 6 079 строк) —
сколько строк волны 2024 несут заполненный идентификатор предыдущей волны:

| поле | `aid_h` 2013 | `bid_h` 2015 | `cid_h` 2018 | `did_h` 2020 | `eid_h` 2022 | `fid_h` 2024 |
|---|---|---|---|---|---|---|
| ДХ волны 2024 с этим id | 3 283 | 3 589 | 4 012 | 4 518 | **5 326** | 6 079 |

🟢 Число первой редакции подтверждено с точностью до единицы: **5 326** (там было 5 325 —
расхождение на одно домохозяйство, вероятно округление счёта при другом фильтре).
То есть панель 2022→2024 — **5 326 домохозяйств, 87,6 % волны 2024**. Это много, дизайн
DeVaney на ней исполним. Сквозная глубина до 2013 — 3 283 ДХ (54 %), но по доходу
и долгу она бесполезна (Д.2.3).

### Д.3. Связка с добором темы 39: что Тофаллис делает с ЛЮБОЙ калибровкой весов

Прочитан раздел Д.3.2 файла `docs/research/raw/approach_validity_2026-09-10.md` (строки
1095–1194). Источник там добыт полностью и процитирован дословно: Tofallis C. «Add or multiply?
A tutorial on ranking and choosing with multiple criteria», *INFORMS Transactions in Education*,
14(3), 2014, 109–119, DOI 10.1287/ited.2013.0124; добытая копия — working paper Hertfordshire
Business School, `https://uhra.herts.ac.uk/id/eprint/11986/1/s153.pdf`.

Три установленных там факта, которые здесь работают как ограничение:

1. Четыре стандартные нормировки одних и тех же данных дают четыре разных ранжирования
   (с. 5 WP, дословно: «The key point is that the four normalizations do not agree with each
   other… Candidate B's rank ranges from third down to last»).
2. 🔴 **Вес не инвариантен.** Тот же вес задаёт разный обменный курс между критериями при
   разной нормировке: у Тофаллиса один и тот же вес даёт то $1,7 тыс., то $1,36 тыс. за год
   опыта (с. 7 WP).
3. Вывод автора (с. 7 WP, дословно): «It is not sufficient to ask people for weights in
   isolation; the elicitation procedure needs to take account of how they will subsequently
   be applied.»

#### 🔴 ПРЯМОЙ ОТВЕТ: что это означает для калибровки весов ПО ДАННЫМ

**Тофаллис бьёт по калибровке по данным ровно так же, как по экспертной, и по той же
причине — а в одном отношении сильнее.**

**(а) Симметрия. Данные не дают весам смысла, которого им не даёт эксперт.** Цитата про
elicitation читается как «спрашивать вес в отрыве от применения нельзя» — но это утверждение
не про людей, а про **идентифицируемость**. Вес в SAW — коэффициент при НОРМИРОВАННОМ
критерии; пока нормировка не зафиксирована, величина «вес» не определена. Любая процедура
оценивания — хоть опрос экспертов, хоть регрессия по наблюдаемому поведению, хоть обратная
задача «подобрать веса, при которых модель воспроизводит выбор домохозяйств» — оценивает
не «важность критерия», а **пару (важность, нормировка)**. Заменив эксперта данными,
мы меняем источник числа, но не устраняем неидентифицируемость. Соблазн «данные объективнее»
здесь ложный: объективен замер, а не шкала, в которой он выражен.

**(б) Асимметрия, и она НЕ в пользу данных.** Экспертная калибровка идёт при ОДНОЙ
нормировке, заданной разработчиком для всех портретов сразу. Калибровка по поведению идёт
по популяции домохозяйств, и если нормировка **зависит от выборки** (делим на max или на sum
внутри конкретного пользователя — то, что помечено в теме 39 как «диапазонная зависимость»,
п. 4 практических следствий), то у домохозяйства с одним дешёвым долгом и у домохозяйства
с пятью дорогими **один и тот же оценённый вес означает разный обменный курс**. Тогда
оценка, усреднённая по популяции, — это среднее несоизмеримых величин. 🔴 Это не шум,
который лечится объёмом выборки: это ошибка спецификации. Больше домохозяйств делает
такую оценку **точнее вокруг бессмысленного числа**.

**(в) Порядок работ жёстко задан, и он обратный интуиции.** Нельзя «сначала откалибровать
веса по ОДПФ, потом решить вопрос нормировки». Нормировка — **предусловие**, а не шаг
конвейера. Пока в `docs/math_model.md` не записано, какая нормировка канон, любая
калибровка — и пятый экспертный раунд с согласием 78,63 %, и будущая по данным — калибрует
величину без определения.

**(г) Конструктивный выход, и он единственный чистый.** Если веса элиситируются
и калибруются **сразу в форме обменного курса** («сколько рублей переплаты домохозяйство
готово отдать за один месяц резерва»), нормировка перестаёт быть свободным параметром:
курс задан в физических единицах (₽/месяц), и его величина не меняется от того, делим мы
на max или на sum. Это ровно то, чего требует цитата Тофаллиса про elicitation. Второй
вариант из темы 39 — **нормировка по абсолютной шкале с фиксированными якорями**
(ПДН 0…0,40; резерв 0…6 месяцев) — эквивалентен по эффекту: шкала задаётся каноном,
а не выборкой, и веса становятся сопоставимыми между пользователями.

**(д) И сложение с находкой Д.1.4.** Даже если бы нормировку канонизировали сегодня,
калибровать веса по наблюдаемому распределению потока не на чем: ячейка — **95
домохозяйств**, и «доля в долг» в ней измеряет обязательный платёж, а не выбор. То есть
против калибровки весов по данным работают две независимые причины — **неидентифицируемость
(Тофаллис) и отсутствие данных (Д.1.4)**. Устранение любой одной из них другую не снимает.

🟢 **Что при этом остаётся законным и не задевается ни одной из двух причин:**
использование ОДПФ для **порождения популяции портретов** и для **проверки следствий**
(медиана желаемого резерва, доля целевых накопителей, норма сбережения). Это операции
над наблюдаемыми величинами в их собственных единицах — рублях, месяцах, долях, —
где нормировка вообще не участвует. Ограничение Тофаллиса касается **весов свёртки**,
а не данных как таковых.

### Д.4. Недобытая литература первой редакции — закрыта по пунктам

Каналом служили OpenAlex / Crossref / Unpaywall / Semantic Scholar. 🔴 Unpaywall здесь не
украшение: он превращает «не смог открыть» в проверяемое «открытого доступа не существует».

#### Д.4.1 🟢 Пункт 7 (блочный бутстрап) — ПЕРВОИСТОЧНИК ДОБЫТ

Первая редакция называла §3.3(б) «самым слабым местом отчёта по цитированию»: правило выбора
длины блока было взято со сводки поиска.

**Künsch H.R. «The Jackknife and the Bootstrap for General Stationary Observations»,
*The Annals of Statistics*, 1989, Vol. 17, No. 3, pp. 1217–1241.**
DOI 10.1214/aos/1176347265. Unpaywall/OpenAlex: `oa_status = bronze`.
PDF взят с Project Euclid (HTTP 200, 2 065 604 Б).
🔴 Скан без текстового слоя — `pdftotext` вернул 378 байт (обложку JSTOR). Прочитан через
`Read` с параметром `pages` (постраничный рендер), с. 1217–1218.

Аннотация, дословно (с. 1217):

> «We extend the jackknife and the bootstrap method of estimating standard errors to the case
> where the observations form a general stationary sequence. We do not attempt to reduction to
> i.i.d. values. The jackknife calculates the sample variance of replicates of the statistic
> obtained by omitting each block of *l* consecutive data once. In the case of the arithmetic
> mean this is shown to be equivalent to a weighted covariance estimate of the observations.
> **Under appropriate conditions consistency is obtained if l = l(n) → ∞ and l(n)/n → 0.**
> … Bootstrap replicates are constructed by selecting blocks of length *l* randomly with
> replacement among the blocks of observations.»

И конструкция MBB дословно (с. 1218):

> «choose n/l blocks of length l with replacement from the n − l + 1 blocks of observed data.»

И явное сопоставление с неперекрывающимися блоками Карлстайна (с. 1218):

> «Carlstein (1986) has proposed a variance estimator which selects nonoverlapping blocks.
> For the arithmetic mean, deletion of blocks is the same as selecting blocks. So in this case
> our jackknife differs only by using overlapping blocks and tapering. However, for general
> statistics, deletion is better than selection, both in theory (see Remark 4.1) and in the
> simulations of Sections 5.1 and 5.2.2.»

🟢 **Условие «l → ∞ и l/n → 0» теперь стоит на первоисточнике**, а не на сводке. Для нас
оно и есть приговор историческим когортам: при n ≈ 144 месяцах и длине блока порядка горизонта
плана условие «l/n → 0» выполняется формально, но численно l/n ≈ 0,1–0,2 — то есть
асимптотика не наступила. Широкие интервалы §3.3 — следствие именно этого, и вывод первой
редакции («широкий интервал — честная мера того, сколько истории у нас есть») подтверждён.

**Politis D.N., Romano J.P. «The Stationary Bootstrap», *Journal of the American Statistical
Association*, 1994, 89(428), DOI 10.1080/01621459.1994.10476870.**
🔴 Unpaywall, дословно: `"is_oa": false, "oa_status": "closed"`, `best_oa_location: None`.
То есть это не «я не нашёл» — **открытого доступа к этой работе не существует**. Запись
в §3.3(б) о стационарном бутстрапе остаётся несверенной с первоисточником, и теперь известно,
что сверить её бесплатно нельзя.

#### Д.4.2 🔴 Пункт 6 (Choupani & Mamdoohi) — исправлены РЕКВИЗИТЫ, доступ подтверждён закрытым

Первая редакция ссылалась на «Choupani & Mamdoohi, Computers, Environment and Urban Systems,
2016». Найдены **две разные работы этих авторов**, и цитата принадлежит второй:

1. **Choupani A.-A., Mamdoohi A.R. «Population Synthesis Using Iterative Proportional Fitting
   (IPF): A Review and Future Research», *Transportation Research Procedia*, 2016,
   DOI 10.1016/j.trpro.2016.11.078.** Unpaywall: `is_oa = true, oa_status = "gold"`,
   лицензия CC BY-NC-ND. 🔴 Но PDF за антиботом ScienceDirect: `curl` с браузерным UA дал
   **403** (1 208 167 байт HTML-заглушки). Аннотация получена полностью через Semantic Scholar.
   Из неё, дословно:
   > «Our review shows that **integer conversion and zero-cell are among the most important
   > problems** necessitating empirical investigation. Unbiased tabular (controlled) rounding
   > methods should be developed to integerize the fractional numbers estimated by IPF for the
   > frequency of household types. Zero-cell problem, although already dealt with, still lacks
   > unbiased solutions.»
   🟢 Это независимо подтверждает две из трёх «болезней IPF» §2.1 (нулевая ячейка, округление).

2. **Choupani A.-A., Mamdoohi A.R. «Comparison of Iterative Proportional Fitting and Simulated
   Annealing as synthetic population generation techniques: Importance of the rounding method»,
   *Computers, Environment and Urban Systems*, 2017, vol. 68, pp. 78–88,
   DOI 10.1016/j.compenvurbsys.2017.11.001, опубликовано 07.12.2017.**
   🔴 Unpaywall, дословно: `"is_oa": false, "oa_status": "closed"`, число OA-локаций — **0**.
   Именно к ней относится цитата про «marginal distributions-controlled rounding».
   **Год в первой редакции (2016) неверен — это 2017**; название там отсутствовало вовсе.
   Полный текст недоступен бесплатно нигде — проверено, а не предположено.

#### Д.4.3 🔴 Пункт 8 (Blanchett, Kowara & Chen 2012, первоисточник WER) — отрицательный результат установлен

Поиск по OpenAlex `title.search:optimal withdrawal strategy retirement income portfolios`
вернул **count = 0**. Crossref по тому же названию не дал ни одного совпадения (выдача —
другие работы по safe withdrawal rates). 🔴 Вывод: у работы **нет DOI и её нет ни в OpenAlex,
ни в Crossref**, поэтому Unpaywall по ней запросить физически невозможно. Это практикующее
издание (Morningstar / Retirement Management Journal), а не индексируемая статья.
🟢 Практического ущерба нет: определение WER взято из Blanchett 2013, где оно дано дословно
и со ссылкой на первоисточник (§3.1, цитаты добыты и остаются в силе). Но статус пункта
меняется с «не читан» на **«не индексирован; проверить невозможно средствами открытых API»**.

#### Д.4.4 Пункты 9 и 10 — не добирались сознательно

Правило 50/30/20 (Warren & Warren Tyagi, «All Your Worth», 2005) — книга, не статья; для
наших целей достаточно уже установленного отрицательного факта: **в Greninger et al. 1996
этого правила нет**. Проверка книги не проходит тест «строго ли необходим этот шаг»
(шаг 3б): 50/30/20 в модели FINPILOT не используется.
Пункт 10 (единый канонический список нормативов США) остаётся отрицательным результатом
первой редакции: такого документа не существует, есть набор Greninger (22 коэффициента)
и отраслевая тройка. Переискивание без `WebSearch` не даст нового.

### Д.5. Альтернативы ОДПФ — часть 1: каналы РФ, проверенные лично

Закрывает пункт 3 списка недобытого («реальная выгрузка ВНДН не проверялась, объём выборки —
со сниппета»).

#### Д.5.1 Официальный канал Росстата — статус подтверждён, без изменений

| Адрес | 11.09.2026 |
|---|---|
| `https://rosstat.gov.ru/microdata` | **404** (отдаёт страницу-заглушку 680 635 Б) |
| `https://obdx.gks.ru/` | **200**, 10 815 Б — форма входа, микрофайлы без авторизации не отдаёт |
| `https://tochno.st/datasets/surveys` | **200**, 376 088 Б |

Вывод первой редакции подтверждён: рабочий канал к микроданным Росстата — зеркало tochno.st.

#### Д.5.2 🟢 Каталог tochno.st вскрыт: 14 прямых ссылок, лицензия прочитана в первоисточнике

Со страницы извлечены **14 прямых URL** на `storage.yandexcloud.net`, включая отдельный
архив по каждому обследованию и **паспорт набора**
`description_surveys_135_v20260903.pdf` (HTTP 200, 254 967 Б, ПРОЧИТАН).

Дословно из паспорта:

> «Микроданные федеральных статистических наблюдений Росстата по социально-демографическим
> проблемам и обследования домохозяйств по потребительским финансам Центрального банка.
> В набор данных входят **58 файлов микроданных 12 обследований**, проведенных в период
> с 2011 по 2025 годы.»
> «Данные опубликованы в том виде, в котором их хранит Росстат.»
> «Набор доступен для работы в форматах CSV (кодировка: «UTF-8», разделитель: «;»), XLSX и SAV.»

🔴 **Лицензия — прочитана в паспорте, а не со страницы:** поле «Лицензия, под которой
публикуется набор данных» = **«Creative Commons BY»**. Обязательная форма цитирования, дословно:

> «Микроданные выборочных обследований Росстата и Центрального банка; обработка:
> «Если быть точным», 2025. URL: https://tochno.st/datasets/surveys»

История версий каталога (важна для воспроизводимости): 11.12.2024 v1.0 → 29.09.2025 v1.1
(добавлены КОУЖ-2024, ВНДН-2024, СЗН-2024) → **21.11.2025 v1.2 (добавлены микроданные
ОДПФ-2013–2024)** → 17.12.2025 v1.3 → 29.12.2025 v1.4 → **03.09.2026 v1.5 (ВНДН-2025,
НО-2025, КДУ-2025)**.

#### Д.5.3 ВНДН — выгрузка проверена лично

Прямой URL (декодированный):
`storage.yandexcloud.net/tochno-st-catalog/Rosstat/data_surveys_135_v20260903/ВНДН (Выборочное наблюдение доходов населения и участия в социальных программах).zip`
🟢 `curl -sIL` → **HTTP/2 200, `content-type: application/zip`, `content-length: 1 196 783 419`**
(≈ 1,2 ГБ). Файл живой и берётся без авторизации. 🔴 Не скачивался: 1,2 ГБ ради проверки
маргиналов дохода не проходит тест «строго ли необходим шаг» — ОДПФ-2024 уже даёт доход
на 6 079 ДХ, а ВНДН понадобится только на этапе калибровки хвостов.

**Годы ВНДН по паспорту (не по сниппету):** 2012, 2014, 2015, 2016, 2017, 2018, 2019, 2020,
2021, 2022, 2023, 2024, **2025** — тринадцать волн.
🟡 Объём выборки ВНДН (60/160 тыс. домохозяйств) в паспорте каталога **не указан** —
это число остаётся со сниппета Росстата и по-прежнему не сверено с первоисточником.

**КОУЖ** — годы 2011, 2014, 2016, 2018, 2020, 2022, 2024 (семь волн), тот же архив, та же
лицензия. **ОДПФ на tochno.st** лежит копией (`data_surveys_135_v20251121/ОДПФ…zip`);
🔴 для нас копия избыточна — оригинал у ЦБ свежее и содержит объединённые файлы всех волн
(Д.2.1), которых в зеркале нет.

#### Д.5.4 RLMS-HSE — расхождение между зеркалами РАЗРЕШЕНО

Закрывает пункт 4 списка недобытого.

**Зеркало UNC** `rlms-hse.cpc.unc.edu/data/availability/` (HTTP 200, 38 387 Б, ПРОЧИТАНО).
Таблица доступа, дословно:

> «Public Data | Rounds | Data Use Agreement | Data Security Plan | IRB Approval | Data Access
> **Household & Individual | 1994-2024 | No | No | No** | HSE, Dataverse
> Community | 1994-2018 | No | No | No | HSE, Dataverse
> Family Planning and Reproductive Health | 2010, 2012 | No | No | …»

> «These files are available to download **without any application process** from the CPC
> Dataverses hosted by the Odum Institute.»

> «Some data remain Sensitive and are available with the restrictions indicated in the table
> below… If you require birth date and community prices, please Contact Us and request assistance.»

**Зеркало ВШЭ** `hse.ru/en/rlms/` (HTTP 200, 123 484 Б) и `hse.ru/en/rlms/downloads`
(HTTP 200, 44 085 Б) — обе страницы вычитаны машинно по ключам `register`, `regist`,
`agreement`, `free of charge`, `restriction`, `Dataverse`.
🔴 **Слова «register» на них НЕТ ни разу**; на странице загрузок нет ни одного из шести ключей.
Формулировка «users are asked to register online and accept Data Use agreement», занесённая
в §1.1 первой редакции со сниппета поиска, **на самих страницах ВШЭ не подтверждена**.

🟢 **Разрешение расхождения:** противоречия между зеркалами нет — есть ошибка сниппета.
Публичный слой RLMS (Household & Individual, 1994–2024) берётся **без заявки, без соглашения
и без IRB**, что прямо записано в таблице UNC тремя «No». Условие одно — цитирование
(страница «Citing the Data» существует в навигации обоих зеркал; 🟡 по адресу
`rlms-hse.cpc.unc.edu/citing-the-data` отдаётся **404**, точный текст требования
в этой сессии не прочитан).

### Д.6. 🔴 КОНТРПРИМЕРЫ: вредно ли учиться весам у наблюдаемого поведения

Работал подагент A (один, последовательно; сырьё в `scratchpad/subagent_A.md`, 238 строк).
Вопрос ставился намеренно на опровержение: «покажи, что калибровка по поведению ХУЖЕ
нормативных весов».

#### Д.6.1 Главный контрпример добыт целиком и бьёт ровно в наш класс решений

**Gathergood J., Mahoney N., Stewart N., Weber J. «How Do Individuals Repay Their Debt?
The Balance-Matching Heuristic». *American Economic Review*, 2019, 109(3), pp. 844–875.
DOI 10.1257/aer.20180288.**
Статус доступа: Unpaywall по журнальному DOI — `is_oa: true`, `oa_status: "bronze"`,
`best_oa_location.url_for_pdf = aeaweb.org/articles/pdf/doi/10.1257/aer.20180288`;
🔴 но `aeaweb.org` на `curl` с браузерным UA отдал HTML-заглушку 5,8 КБ вместо PDF.
🟢 **ПРОЧИТАН ПОЛНЫЙ ТЕКСТ** по идентичному препринту **NBER Working Paper № 24161
(December 2017, revised August 2018)**, `nber.org/system/files/working_papers/w24161/w24161.pdf`
(993 745 Б, 3 467 строк после `pdftotext -layout`).

**Дословно, аннотация (NBER WP 24161, с. 2):**

> «We study how individuals repay their debt using linked data on multiple credit cards.
> **Repayments are not allocated to the higher interest rate card, which would minimize the
> cost of borrowing.** Moreover, **the degree of misallocation is invariant to the economic
> stakes, which is inconsistent with optimization frictions.** Instead, we show that repayments
> are consistent with a balance-matching heuristic under which the share of repayments on each
> card is matched to the share of balances on each card. Balance matching captures more than
> half of the predictable variation in repayments and is highly persistent within individuals
> over time.»

**Дословно, раздел 1 — численный размер ошибки:**

> «To minimize interest charges, we calculate that individuals should allocate **97.1%** of the
> payments in excess of the minimum to the high APR card. We show that individuals allocate only
> **51.5%** of their excess payments to the high APR card, behavior that is virtually
> indistinguishable from the completely non-responsive baseline. In other words, **85% of
> individuals should put 100% of their excess payments on the high interest rate card but only
> 10% do so.**»

**Дословно, раздел 3.1 «Costs of Misallocation» — цена ошибки не мелкая:**

> «Average interest savings are increasing across the number of cards, rising from £65 in the
> two-card sample to £248 in the five-card sample… with the 90th percentile rising from £167
> in the two-card sample to **£927** in the five-card sample.»

**И кросс-культурная устойчивость (раздел 1):**

> «the share of payments in excess of the minimum misallocated to the high APR card is 50% among
> Mexican credit card holders and 46% among U.K. credit card holders… providing a striking
> example of **uniformity of a behavioral bias across very different cultures and financial
> settings**.»

#### Д.6.2 🔴 Эксперимент «а давайте выучим веса у данных» авторы уже поставили — и он провалился

Это самая ценная часть находки. Авторы обучили ML-модель максимального качества на реальных
данных о погашении, чтобы получить верхнюю границу предсказуемости. Дословно (раздел 1):

> «To provide an upper benchmark, we use machine learning techniques to find the repayment model
> that maximizes out-of-sample fit using a rich set of explanatory variables… We find that
> balance matching captures more than half of the "predictable variation" in repayment behavior.»

> «Consistent with the poor fit of the optimal repayment rule, we find that **interest rates have
> low variable importance** (i.e., proportional increase in R²) in our machine learning models.
> Consistent with the balance matching results, we find that **balances have the highest variable
> importance**…»

**Перевод на FINPILOT.** Если бы мы подобрали веса SAW так, чтобы модель максимально
воспроизводила наблюдаемое распределение платежей, мы получили бы **вес ставки по кредиту,
близкий к нулю, и вес остатка — максимальный**. Это ровно та ошибка, которую исправляет
Avalanche-фильтр. Обучение по поведению здесь не улучшает СППР — оно **её отключает**.

И отдельно — довод против оправдания «это скрытые предпочтения, а не ошибка»: у авторов прямо
сказано, что misallocation **не убывает** там, где цена ошибки высока («invariant to the
economic stakes, which is inconsistent with optimization frictions»). Рациональная экономия
внимания убывала бы. Значит поведение нельзя легализовать как обучающий сигнал.

#### Д.6.3 Эвристика 1/N — буквальный сценарий вырождения наших весов

Из того же полного текста, разделы 5.2–5.4:

> «Repay the card with the lowest balance ("debt snowball method")… Proponents argue that paying
> off a card with a low balance generates a "win" that motivates further repayment behavior…
> See also Amar et al. (2011) and Brown and Lahey (2015) for laboratory evidence…»

> «All the heuristics have median savings close to zero, but have wide dispersion in savings
> or losses…»

> «Under the 1/N heuristic, payments are equal across cards, and **the steady state balances are
> unchanged relative to the status quo**.» (и «the 1/N rule [captures] 11.7% [of individuals]»)

🔴 Для SAW это прямое предупреждение: равные веса по долгам — не «нейтральный бейзлайн»,
а стратегия с **нулевой экономией**. Бейзлайн «пропорция» из Шага 4 (§ «Шаг 4») теперь имеет
первоисточник и известную цену: ноль.

🟡 Про snowball: у Gathergood et al. это **пересказ позиции финансовых советников**
(сноска 36 цитирует Дэйва Рэмси дословно), а не измеренный ими эффект. Утверждение «snowball
проигрывает по деньгам, но выигрывает по доведению до конца» первоисточником в этой сессии
**не подтверждено** — Amar et al. 2011, Kettle et al. 2016, Brown & Lahey 2015 закрыты
(см. Д.6.5).

#### Д.6.4 Co-holding — подтверждение из второго источника, но только по аннотации

**Gathergood J., Weber J. «Self-control, financial literacy & the co-holding puzzle».
*Journal of Economic Behavior & Organization*, 2014, vol. 107 (part B), pp. 455–469.
DOI 10.1016/j.jebo.2014.04.018.** Unpaywall: `is_oa: true`, `oa_status: "hybrid"`.
🔴 Полный текст добыть не удалось тремя каналами: ScienceDirect — **403** (HTML-заглушка
1 207 946 Б); Nottingham ePrints `eprints.nottingham.ac.uk/29811/` — **404**;
Repository@Nottingham (Worktribe) — **403 с челленджем Cloudflare**. Аннотация получена
полностью из OpenAlex, дословно:

> «Approximately **12% of households** in our sample co-hold, on average, **£3800 of revolving
> consumer credit** on which they incur interest charges, **even though they could immediately
> pay down all this debt using their liquid assets**. Co-holders are typically more financially
> literate, with above average income and education.»

🔴 **Для нас это прямой удар по одной конкретной идее:** «посмотрим, какое соотношение
резерв/долг люди держат по факту, и возьмём его за целевое». Двенадцать процентов домохозяйств
держат соотношение, при котором резерв дороже долга — то есть заведомо убыточное. Причём это
**не бедные и не безграмотные**: «more financially literate, with above average income and
education». Финансовая грамотность от этой ошибки не защищает, значит и фильтрация выборки
«по грамотным» не спасёт калибровку.

#### Д.6.5 🔴 Что подагент НЕ добыл, и чего из-за этого нельзя утверждать

Весь блок «improper linear models» (тезис «равные веса не хуже подогнанных») остался
**без единого прочитанного текста**. Вердикты Unpaywall дословно — все семь работ `is_oa: false`,
`oa_status: "closed"`:

| Работа | DOI | Unpaywall |
|---|---|---|
| Dawes R.M. «The robust beauty of improper linear models in decision making», *American Psychologist*, 1979, 34(7), 571–582 | 10.1037/0003-066X.34.7.571 | `closed`, `best_oa_location: null` |
| Dawes & Corrigan «Linear models in decision making», *Psych. Bulletin*, 1974, 81(2), 95–106 | 10.1037/h0037613 | `closed` |
| Einhorn & Hogarth «Unit weighting schemes for decision making», *OBHP*, 1975, 13(2), 171–192 | 10.1016/0030-5073(75)90044-6 | `closed` |
| Wainer H. «Estimating coefficients in linear models: It don't make no nevermind», *Psych. Bulletin*, 1976, 83(2), 213–217 | 10.1037/0033-2909.83.2.213 | `closed` |
| Grove et al. «Clinical versus mechanical prediction: A meta-analysis», *Psych. Assessment*, 2000, 12(1), 19–30 | 10.1037/1040-3590.12.1.19 | `closed` |
| Dana & Dawes «The superiority of simple alternatives to regression…», *JEBS*, 2004, 29(3), 317–331 | 10.3102/10769986029003317 | `closed` |
| Hogarth & Karelaia «Heuristic and linear models of judgment», *Psych. Review*, 2007, 114(3), 733–758 | 10.1037/0033-295X.114.3.733 | `closed` |

🔴 **Практическое следствие:** ссылка на Grove et al. 2000 в §«Шаг 6» («механические методы
точнее клинических») стоит на теме 27, а не на прочитанном первоисточнике, и теперь известно,
что первоисточник закрыт. Не выдавать за прочитанное.

Также закрыты: Amar et al. 2011 *JMR* 48(SPL):S38–S50 (10.1509/jmkr.48.SPL.S38) — `closed`,
единственная локация — сам DOI; Kettle et al. 2016 *JCR* 43(3):460–477 (10.1093/jcr/ucw037) —
`closed`, пять локаций в OpenAlex и все не-OA.
🟡 Любопытный случай: Besharat, Carrillat, Ladik 2014 *JPP&M* 33(2):143–158 (10.1509/jppm.13.007)
— Unpaywall говорит `is_oa: true, oa_status: "green"`, локация — DSpace Griffith; при разборе
item через DSpace 7 API там **только бандлы LICENSE, бандла ORIGINAL с файлом нет**.
То есть бывает «зелёная» запись без файла — Unpaywall это не проверяет.

🔴 **Честно про причину.** В этом прогоне были закрыты сразу три канала обнаружения
(`WebSearch` исчерпан, Exa 404, `r.jina.ai` 401). API метаданных находят работу **по известному
названию**, но не находят её **зеркала**. Зеркала Dawes 1979 в вебе почти наверняка есть —
их не нашли потому, что нечем было искать. Это ограничение прогона, а не вывод об отсутствии
литературы.

#### Д.6.6 🔴 ПРЯМОЙ ОТВЕТ по контрпримерам

**Да, для нашей задачи «учиться весам у наблюдаемого поведения» ВРЕДНО — в той форме,
в какой идея сформулирована.** Стоит это на одном источнике, но прочитанном целиком
и бьющем ровно в наш класс решений (Gathergood et al., AER 2019 / NBER WP 24161).

Условия, при которых калибровка по поведению всё же законна — три роли, и только они:

1. **Приёмистость, а не оптимальность.** Поведенческие данные годятся, чтобы калибровать,
   ЧТО человек согласится исполнить (какую долю потока реально направит, доведёт ли план
   до конца), и не годятся, чтобы калибровать, что оптимально. Смешивать эти два объекта
   в одной SAW-свёртке нельзя.
2. **Только там, где нормативного оптимума нет.** Деление между «резервом» и «целями»
   нормативно недоопределено — тут поведение информативно. Деление между долгами по ставке
   определено однозначно — тут не информативно вообще.
3. **Никогда как единственная целевая функция фита.** Максимизация соответствия наблюдаемому
   поведению буквально награждает воспроизведение balance matching. Нужен внешний нормативный
   гейт (переплата, срок выхода из долга) как обязательное условие приёмки.

### Д.7. Сверка моих расчётов с официальной публикацией ЦБ по той же волне

Добыт аналитический доклад ЦБ **«Финансы российских домохозяйств в 2024 году»** (2025),
`https://www.cbr.ru/Content/Document/File/177096/analytic_note_20250609_dip.pdf`
(HTTP 200, 2 736 819 Б, разобран `pdftotext -layout`). Источник данных в нём — та же 6-я волна
ОДПФ, что я считал сам. Это внешняя проверка моей арифметики.

| Показатель | ЦБ (публикация) | Мой расчёт на файле | Сходится? |
|---|---|---|---|
| ДХ, сообщающих о наличии сбережений | **51 %** (было 47 % в 2022) | `h33`=«Да» **48,3 %** при 5,1 % отказов | 🟢 да: 48,3/(100−5,2) = **50,9 %** |
| ДХ с какими-либо финансовыми обязательствами | **20 %** (23 % в 2022) | мои 17,7 % — без ипотеки и без прочей недвижимости | 🟢 согласуется по порядку |
| ДХ с потребительскими кредитами | **8 %** (10 % в 2022) | 5,85 % **индивидов** (не ДХ) | 🟢 разные единицы, не противоречат |
| ДХ, плативших по кредитам и займам ежемесячно | **25 %** | — | — |
| Медиана обязательств у медианного ДХ | **200 тыс. ₽** | `c44_1` медиана суммы 1-го кредита 200 000 ₽ | 🟢 совпало |

🟢 **Вывод сверки: взвешивание по `hhwgt` и обработка отказов у меня верны** — расхождение
с ЦБ объясняется целиком тем, включён ли отказ в знаменатель.

**Числа ЦБ, которых у меня не было и которые прямо нужны модели (дословно):**

> «В 2024 г. 25% домохозяйств осуществляли ежемесячные платежи по кредитам и займам.
> **Медиана отношения регулярных платежей по кредитам к доходам составила 16,7% в 2024 г.
> после 17,5% в 2022 году.** В 2024 г. для всех доходных групп этот уровень относительно
> 2022 г. практически не изменился.»

🔴 **Это эмпирический якорь для инварианта ПДН ≤ 0,40.** Фактическая медиана долговой нагрузки
среди платящих — **16,7 %**, то есть порог 0,40 лежит примерно на 2,4 медианы. Доля ДХ
за порогом 80 % — «не превышает в 2024 г. 3,1 % в 1-й квинтильной группе по доходу».

> «Наиболее распространенный вид обязательств – потребительские кредиты – есть у 8%
> домохозяйств в 2024 г. (у 10% в 2022 г.)… Объем невыплаченной задолженности у медианного
> домохозяйства в 2024 г. составил 200 тыс. руб. (против 140 тыс. руб. в 2022 г.).»

> «Медиана отношения суммы обязательств к финансовым активам (за исключением наличности)
> для домохозяйств с обязательствами существенно выше (**от 6 до 9 раз**). Это может
> свидетельствовать об отсутствии у домохозяйств ресурсов для быстрого погашения
> задолженности при необходимости.»

Просрочка (дословно) — подтверждает Д.1.2 о том, где она измеряется:

> «Доля домохозяйств в рассматриваемой выборке, которые подтверждали факт наличия просроченных
> платежей, наибольшая по **кредитным картам (2,5% в 2024 г.)** и наименьшая по кредитам
> на основную недвижимость (0,9% в 2024 г.)… За всю историю платежей по обязательствам
> в 2024 г. только 1,3% домохозяйств… сообщают об имевшемся просроченном платеже по кредиту
> на основную недвижимость и 5,9% – по кредитным картам.»

🔴 **Следствие для Шага 3 (дизайн DeVaney на ОДПФ).** Исход «просрочка» имеет базовую частоту
**0,9–2,5 %**. При n = 5 326 панельных ДХ и доле с соответствующим типом долга в единицы
процентов число событий в ячейке — десятки, а не сотни. Логистическая регрессия и CART
на таком числе событий дадут широчайшие интервалы. Порог «> 50 % конкордантных пар» будет
достигнут тривиально, а его содержательность — нулевой. **Метрики O1 и O2 из итоговой
таблицы приёмки надо либо переформулировать на более частый исход (падение автономии `h28`,
рост числа кредитов), либо снять.**

#### 🔴 И самое неприятное: ЦБ сам зафиксировал ту же внутреннюю несогласованность, что нашёл я

Сноска 18 доклада, дословно:

> «Тем домохозяйствам, у которых доходы оказывались меньше или равны расходам, мы присваивали
> нулевую норму сбережений. **Во всех доходных группах доли домохозяйств, для которых доходы
> превышают расходы, оказываются значительно больше, чем доли домохозяйств, дающих
> утвердительный ответ о наличии сбережений. Получаемая существенная разница в долях
> составляет 17–32 п.п.**»

То есть разность «доход минус расход» (`h48_r` − `h49_r`) и самоотчёт о сбережениях расходятся
на 17–32 процентных пункта — по признанию самого Банка России. Это независимое подтверждение
моей находки Д.1.3 (0,4 % отрицательных потоков; 13,7 % отношений «отложено/поток» > 1).
🔴 **Вывод, который отсюда следует прямо: «свободный поток», вычисленный как Н13 − Н14,
не является наблюдаемой величиной.** Он — разность двух несогласованных самооценок.
Строить на нём калибровку весов нельзя, и ЦБ, определяя норму сбережений, вынужден был
затыкать дыру присвоением нулей.

Для справки, норма сбережений по ЦБ (та же сноска и текст): «в 2024 г. в низкой, средних
и высокой доходных группах медианная норма сбережений составила соответственно **0, 18–19
и 34 %**».

### Д.8. Технический отчёт 6-й волны — дизайн выборки и достижимость (добыт впервые)

`https://www.cbr.ru/Content/Document/File/174711/inf.pdf` (HTTP 200, 1 004 558 Б) и
`174710/method_6_2024.pdf` (588 340 Б) — оба разобраны `pdftotext -layout`.

**Дизайн (методология, дословно):** «используется дизайн (модель) **стратифицированной,
многоступенчатой, вероятностной, территориальной адресной выборки**»; тип обследования —
«сплит-панель (Split panel)… обследование с пересекающимися (перекрывающимися) выборками
(overlapping survey)». То есть веса `hhwgt` и `psu` не декоративны — без них выборка смещена
по построению.

**Достижимость, дословно (технический отчёт, с. 16):**

> «По результатам проведения интервью репрезентативная выборка составила 6079 домохозяйство.
> Из 6081 домохозяйства, опрошенных в 2022 г. повторно опрошены в 2024 г. были **5225**
> домохозяйств. Таким образом, **достижимость ранее опрошенных в 2022 г. домохозяйств
> составила 85,9%**.»

> «для достижения того же самого объема опрошенных домохозяйств (6081 в 2022 году и 6079
> в 2024 году) интервьюерам пришлось обойти существенно большее количество адресов
> (**8502 адреса в 2022 году и 8940 в 2024**)… растет недостижимость (в основном **отказы
> участвовать в опросе**) среди новых домохозяйств, ранее не участвовавших в опросе.»

🟡 **Внутреннее расхождение в самом отчёте, зафиксировать.** В одном месте сказано «повторно
опрошены 5225», в другом — «87,6% всех семей, опрошенных в 2024 г.» являются панельными;
87,6 % от 6 079 = 5 325. Мой счёт заполненных `eid_h` по файлу — **5 326**. Три числа
(5 225 / 5 325 / 5 326) не сходятся; разница около сотни ДХ, ~1,9 % волны. Для наших целей
безразлично, но при публикации брать **5 326 — оно посчитано на данных**, а не переписано
из текста.

**Практическое следствие для «правдоподобной популяции»:** доля обойдённых адресов,
давших интервью, — 6 079 / 8 940 = **68 %**, и неответ смещён в сторону новых домохозяйств,
то есть в сторону тех, кто отказывается говорить о финансах. Веса корректируют известные
маргиналы, но не корректируют отказ по причине самой темы. 🔴 В отчёте о популяции это надо
назвать прямо: наши 12 000 портретов наследуют смещение неответа ОДПФ, и оценивать его
метриками SRMSE невозможно — референс сам смещён.

### Д.9. Сколько в популяции портретов, где Avalanche вообще применим

Посчитано на обоих файлах: число различимых долговых позиций на домохозяйство
(потребкредиты 1–3 + кредитные карты 1–3 + займ МФО + ипотека/кредит на недвижимость),
взвешено `hhwgt`:

| Позиций | 0 | 1 | 2 | 3 | 4 | 5+ |
|---|---|---|---|---|---|---|
| Доля ДХ, % | **80,2** | 13,1 | 4,4 | 1,5 | 0,6 | 0,3 |

🔴 **Домохозяйств с двумя и более долговыми позициями — 6,7 %.** Avalanche-фильтр
(«гасим сначала самый дорогой») имеет смысл только там: при одной позиции выбор
вырождается. То есть ядро продукта адресовано **одной четырнадцатой** генеральной
совокупности российских домохозяйств.

И поверх этого — 🔴 **ставка по потребительскому кредиту в ОДПФ не спрашивается вовсе**
(Д.1.2): из 645 человек, назвавших сумму потребкредита, ставку не назвал **никто**, потому
что вопроса нет. Значит для 6,7 % портретов, где Avalanche применим, **сам критерий
упорядочивания долгов из ОДПФ не восстанавливается** — только по картам (`p611_*`),
авто (`e22_*`), ипотеке (`a64`) и МФО (`c3_4`, всего 23 ответа).

**Что с этим делать (два законных пути, оба без калибровки весов):**
1. Ставку по потребкредиту **вменять** из внешнего источника — публикуемая ЦБ ПСК
   (полная стоимость кредита) по категориям и срокам, привязка по `p96_*` (срок) и
   `c48_*` (канал выдачи: офис банка / онлайн / МФО). Это вменение по наблюдаемым признакам,
   а не выдумка; долю вменённых значений публиковать.
2. Проверить долю применимости честно и **сказать её вслух в описании продукта**: Avalanche
   релевантен 6,7 % домохозяйств, остальным продукт полезен другой частью (резерв, цели,
   инвариант ПДН). Это не слабость модели, а измеренная граница применимости — и её лучше
   назвать самому, чем услышать от рецензента.

### Д.10. 🟢 Норматив подушки Greninger 1996 независимо подтверждён на российских данных 2024

Это самая неожиданная находка добора. Желаемый резерв `o29` («О26. Как Вы считаете, сколько
денег домохозяйство должно иметь в сбережениях для оплаты… непредвиденных расходов?»)
переведён в **месяцы расходов** делением на `h49_r` (Н14, ежемесячные расходы ДХ).
Взвешено `hhwgt`.

| Показатель | n | p10 | p25 | **медиана** | p75 | p90 |
|---|---|---|---|---|---|---|
| ЖЕЛАЕМЫЙ резерв `o29` / расходы, месяцев | 4 245 | 0,67 | 1,25 | **2,50** | 5,00 | 11,11 |
| ФАКТИЧЕСКИЕ сбережения `h34_r` / расходы, месяцев | 1 448 | 0,89 | 2,00 | **4,00** | 8,33 | 16,67 |

**Медиана желаемой подушки российских домохозяйств в 2024 году — ровно 2,50 месяца расходов.**

Сопоставление с нормативом, добытым в §4.1 (Greninger et al. 1996, Delphi, 156 экспертов США),
дословно оттуда:

> «these findings support a general view that **liquid assets should provide a minimum of
> 2,5 to 3 months of living expenses**.»

🟢 **Совпадение точное и независимое:** американский экспертный консенсус 1996 года и медиана
самостоятельного суждения 4 245 российских домохозяйств 2024 года дают **одно и то же число**.
Это первое в теме 35 свидетельство того, что хотя бы один норматив нашей модели не является
ни артефактом Delphi, ни культурной особенностью.

Доли относительно порогов:

| Порог | ЖЕЛАЕМЫЙ ≥ порога | ФАКТИЧЕСКИЙ ≥ порога (среди назвавших сумму) |
|---|---|---|
| ≥ 2,5 мес (Greninger, минимум) | **51,6 %** | 69,7 % |
| ≥ 3 мес (Greninger, верх диапазона; DeVaney 1994) | **42,5 %** | 62,6 % |
| ≥ 6 мес (отраслевое «3 to 6 months») | 21,7 % | 36,3 % |

🔴 **Осторожно с прочтением второй строки.** «Фактические сбережения ≥ 3 мес у 62,6 %» —
это доля среди **1 448 домохозяйств, назвавших сумму сбережений**, то есть среди тех, у кого
сбережения вообще есть и кто готов их назвать. По всей популяции сбережения есть у 48,3 %
(`h33`), и сумму назвали 1 552 из 6 079 = 25,5 %. Так что «62,6 % россиян имеют подушку
на 3 месяца» — **неверное утверждение**, и оно легко получается из этой таблицы по невнимательности.
Корректная оценка по всей популяции: 0,255 × 0,626 ≈ **16 %** имеют подтверждённую подушку
≥ 3 месяцев расходов. Это сходится с `h28` (Н15): «полгода и больше» назвали 7,3 %,
«несколько месяцев» — 25,1 %.

**Что это даёт вехе 6, практически:**
🟢 Метрика **N1** («доля рекомендаций за danger-point Greninger») получает российское
подтверждение по подушке — порог 2,5–3 месяца можно защищать не ссылкой на Delphi 1996,
а медианой ОДПФ-2024.
🟢 Шаг 2(б) («российский норматив вместо американского») выполняется и в рублях
(медиана `o29` = 100 000 ₽), и в месяцах расходов (медиана 2,50), и второе устойчивее:
рублёвая величина стареет с инфляцией, а месяцы — нет.

### Д.11. Воспроизводимость расчётов первой редакции — проверена и подтверждена

Расчёт §1.3.1 повторён с нуля на заново скачанном файле, через другой код, другим способом
обработки пропусков. Таблица `h28`, пересчитанная на базу без «затрудняюсь»/отказов
(база = 92,8 % взвешенной массы):

| Ответ | Первая редакция, 10.09 | Добор, 11.09 |
|---|---|---|
| Не больше месяца | 32,9 | **33,0** |
| Несколько месяцев | 27,1 | **27,0** |
| Не больше недели | 14,0 | **14,0** |
| Ни одного дня | 9,3 | **9,3** |
| Не больше двух недель | 8,8 | **8,8** |
| Полгода и больше | 7,9 | **7,9** |

🟢 Совпадение по всем шести строкам с точностью до 0,1 п.п. Медиана `o29` = 100 000 ₽
воспроизведена точно. Панель `eid_h` = 5 326 против 5 325. **Числа §1.3.1 воспроизводимы
и годны к публикации.** Единственное расхождение — среднее `o29` (206 659 против 212 665),
и оно объяснено цензурой выбросов (Д.1.3).

### Д.12. ПДН по ОДПФ-2024 — распределение посчитано, порог 0,40 получил эмпирический якорь

ПДН = (сумма платежей по потребкредитам `c47_1..3` всех членов ДХ + платёж по ипотеке `a67`)
/ доход `h48_r`. Только ДХ с ненулевым платежом. Взвешено `hhwgt`.

| n | p10 | p25 | **медиана** | p75 | p90 |
|---|---|---|---|---|---|
| 652 | 0,046 | 0,080 | **0,150** | 0,250 | 0,357 |

| Порог | Доля ДХ за порогом |
|---|---|
| ПДН > **0,40** (наш инвариант) | **6,8 %** |
| ПДН > 0,50 | 3,2 % |
| ПДН > 0,80 | 0,7 % |

🟢 **Сверка с ЦБ:** публикация даёт «медиана отношения регулярных платежей по кредитам
к доходам составила **16,7 %** в 2024 г.» — у меня **15,0 %**. Расхождение 1,7 п.п.
объясняется составом платежей (ЦБ включает и те типы, для которых в анкете нет переменной
платежа). Доля ДХ с нагрузкой > 80 % у меня 0,7 %, у ЦБ «не превышает 3,1 % в 1-й квинтильной
группе» — сходится.

🔴 **Следствие для инварианта ПДН ≤ 0,40.** Порог отсекает **6,8 %** домохозяйств
с платежами, то есть примерно 1,4 % всей популяции. Он лежит между p90 (0,357) и p95 —
это не «жёсткое ограничение, обрубающее половину пользователей», а верхний хвост.
🟢 Для защиты это сильный аргумент: **порог 0,40 не выдуман — он совпадает с 90–92-м
перцентилем фактической долговой нагрузки российских домохозяйств.**

#### 🔴 Ошибка, допущенная и исправленная по ходу — записать, чтобы не повторить

Первый вариант этого расчёта дал медиану ПДН 0,206 и «14,9 % с нагрузкой > 80 %», что
противоречило ЦБ втрое. Причина: в сумму платежей были включены переменные `p615_1..3`,
которые я по имени принял за платёж по кредитной карте. Проверка вопросника показала:

> «С2.13. Сколько в среднем в месяц Вы обычно **тратите** по этой карте?» → `p614_1..3`
> «С2.14. Сколько рублей в настоящий момент составляет Ваша **задолженность** по этой
> кредитной карте?» → `p615_1..3`

То есть `p615` — **остаток долга**, а `p614` — **оборот трат**, и ни то, ни другое не является
платежом. 🔴 **Минимального платежа по кредитной карте в анкете ОДПФ нет вообще.**
Это третья дыра покрытия после отсутствия ставки по потребкредиту и просрочки по нему.
🔴 И это же исправляет §1.3 первой редакции, где `С2.13` названа «средний ежемесячный платёж» —
неверно, это траты по карте.

**Урок метода:** имя переменной в ОДПФ угадывать нельзя, даже когда угадывается «очевидно».
Единственный надёжный путь — вопросник с кодами (`quet_6_2024.zip`), где имя стоит рядом
с текстом вопроса. Ошибка была поймана только потому, что результат сверялся с независимой
публикацией ЦБ; без сверки она ушла бы в отчёт.

### Д.13. Файлы 5-й волны и вопросники 1–4 волн — размеры доставлены (в §1.3 стояли прочерки)

| Файл | URL | HTTP | Байт |
|---|---|---|---|
| Данные ДХ, 5-я волна 2022 | `.../145697/anketa_5.zip` | 200 | **1 866 262** |
| Данные индивидов, 5-я волна 2022 | `.../145698/in_anketa_5.zip` | 200 | **7 499 355** |
| Вопросники 5-й волны с кодами | `.../145685/questin.zip` | 200 | **2 626 802** |
| Вопросники 1–4 волн (2013–2020) | `.../146140/questin_1_4.zip` | 200 | **14 157 575** |
| Итоговый технический отчёт 5-й волны | `.../145684/method_t.pdf` | — | не запрашивался |

🟢 Шаг 3 (дизайн DeVaney на связке 2022→2024) обеспечен файлами полностью. 🟡 Но брать
их отдельными архивами не нужно: объединённые файлы всех волн (Д.2.1) содержат обе волны
в одной таблице с унифицированными именами столбцов, что снимает задачу гармонизации.

### Д.14. Альтернативы ОДПФ — часть 2: закрывает ли кто-нибудь дыру с досрочным погашением

Работал подагент B (второй и последний, запущен ПОСЛЕ завершения A, не веером; сырьё —
`scratchpad/subagent_B.md`, 31 176 Б). Вопрос к каждому источнику ставился один и тот же:
есть ли (1) досрочное/сверхминимальное погашение, (2) сбережения по целям в суммах,
(3) ставка по каждому потребкредиту, (4) просрочка по потребкредиту.

#### Д.14.1 SCF 2022 (ФРС США) — единственный источник, где решение наблюдается прямо

Проверено: `federalreserve.gov/econres/files/codebk2022.txt` — **HTTP 200, 2 819 548 Б**,
скачан анонимно, без регистрации и соглашения; `econres/scfindex.htm` — 200, 102 594 Б.

🟢 **Досрочное погашение спрашивается ПРЯМЫМ вопросом по каждому кредиту**, дословно из кодбука:

> `X7534(#1)  Is this loan being paid off ahead of schedule, behind schedule, or are the
> payments about on schedule?`
> `     1.  *On schedule     2.  *Ahead of schedule     3.  *Behind schedule`

Серия повторяется по типам долга (`X7529`, `X7521`, `X7554`, `X7564`, `X7566`,
`X7821/X7844/X7867/X7921/X7944/X7967` — образовательные, до шести).
🔴 **Суммы переплаты сверх графика нет** — только категория; сумма вычисляется косвенно
(фактический платёж против аннуитета из остатка/ставки/срока, есть `X2216/X2217` —
ожидаемые месяц и год погашения).

Ставка — по каждому долгу: `X2219/X2319/X2419/X7170  What is the current annual rate of
interest being charged on this loan?  PERCENT * 100`; плюс `X816` (ипотека), `X7132`
(кредитная карта), `X7822` (образовательный).

Просрочка — на уровне ДХ, две градации:
> `X3004  …were all the payments made the way they were scheduled, or were payments on any
> of the loans sometimes made later or missed?`
> `X3005  Were you ever behind in your payments by two months or more?`

Цели сбережения — ранжированный список до шести (`X3006 X3007 X7513 X7514 X7515 X6848`):
> `People have different reasons for saving… What are your most important reasons for saving?`
🔴 **Сумм по целям нет и здесь.**

#### Д.14.2 HFCS (ЕЦБ) — дыру НЕ закрывает, и доступ платный по формальностям

Проверено: главная HFCS — 200, 137 608 Б; каталог переменных волны 2021 (PDF, 1 124 660 Б)
и анкета волны 2023 (PDF, 937 327 Б) — оба разобраны.

🔴 **Досрочного погашения в HFCS НЕТ.** Поиск по анкете 2023 и каталогу 2021 по ключам
`early repayment`, `repay early`, `extra payment`, `ahead of schedule`, `more than required`
дал **ноль совпадений**.

🔴 **Доступ требует заявки — подтверждено дословно** (секция «Access to the data»):

> «The HFCS datasets are available to researchers for research purposes. Please add the
> following information to your access request: a copy of your **government-issued photo
> identification document**… a **Resume or Curriculum Vitae** in English… completed **access
> request form**»

То есть паспорт + CV + форма; имя файла формы (`access_form_leadresearchersurname_…`)
показывает, что предполагается ведущий исследователь, то есть аффилиация де-факто.
Для нас HFCS практически недоступен.

🟢 **Но одна находка HFCS для продукта важнее данных.** Переменная `HI0400x purpose of saving`
— двенадцать бинарных целей, и среди них:

> `e - Provision for unexpected events`
> **`f - Paying off debts`**
> `g - Old-age provision`

🔴 **Погашение долга стоит в европейской гармонизированной анкете ОТДЕЛЬНОЙ целью сбережения,
наравне с резервом на непредвиденное.** Это внешнее подтверждение самой постановки FINPILOT:
трёхчастное деление свободного потока «долг / резерв / цели» — не наша конструкция,
а признанная в методологии ЕЦБ. Для защиты продукта это аргумент сильнее любого веса.

Ставка — `HC090$x non-collateralised loan $x: current interest rate of loan`, просрочка —
`HC1250` + `HC1270 Any overdue payments by more than 90 days`. Формулировка `HC1250` почти
дословно повторяет SCF `X3004` — обследования намеренно сопоставимы.

#### Д.14.3 PSID — НЕ ДОБЫТ, отрицательный результат с точным кодом

`psidonline.isr.umich.edu/Guide/Overview.aspx` — **HTTP 403, 43 101 Б**, тело ответа дословно:
> «Security Challenge. Enable JavaScript and cookies to continue. We're reviewing the security
> of your connection before proceeding.»

Это JS-антибот. Обходные каналы в этом прогоне мертвы все три (`WebSearch` исчерпан,
Exa 404, `r.jina.ai` 401), `curl` с браузерным UA — это и есть тот канал, что получил 403.
🔴 **О содержании долгового блока PSID в этом отчёте не утверждается ничего.**

#### Д.14.4 Кредитные бюро РФ — публичных микроданных не найдено

| Адрес | Код | Что отдал |
|---|---|---|
| `nbki.ru/company/news/` | 200, 251 227 Б | только меню и навигация; лента новостей рендерится JS |
| `bki-okb.ru/press/news` | 200, **2 149 Б** | пустая SPA-оболочка, текста ноль |
| `bki-okb.ru/press/research` | 200, **2 153 Б** | то же |
| Скоринг Бюро | не запрашивалось | бюджет подагента исчерпан |

Раздела «данные для исследователей» в навигации НБКИ нет; меню целиком построено вокруг
платных и персональных сервисов. 🔴 Дословной формулировки условий доступа добыть не удалось —
записывается как **непроверенное**, а не как «данные закрыты».

**Рассуждение (не цитата), которое всё равно решает вопрос:** кредитная история по 218-ФЗ
содержит фактические платежи по каждому договору, график и остаток — значит досрочное
погашение в данных бюро наблюдается **по определению**, как разность факта и графика,
без вопроса респонденту. Но у бюро **принципиально нет** доходов, расходов, сбережений и целей
домохозяйства, то есть **нет левой части нашего уравнения — самого свободного денежного
потока**. Бюро закрывает (1), (3), (4) и не закрывает (2) и знаменатель. Для калибровки
весов SAW этого недостаточно ни при каких условиях доступа.

#### Д.14.5 КОУЖ и ВНДН по содержанию — НЕ УСТАНОВЛЕНО, и это честный ответ

`rosstat.gov.ru/free_doc/new_site/vndn-2024/index.html` — HTTP 200, но **10 473 Б**: SPA-оболочка,
в которой видно только оглавление («Вопросники», «Политика доступа», «Микроданные», «Файлы
данных»), а содержимое разделов рендерится JS и ссылок на файлы в HTML нет.
`.../KOUZ22/` и `.../KOUZ-2024/` — **404** (шаблон адреса не угадан).

🟢 Найден способ добыть вопросники, не качая гигабайты, — со страницы tochno.st, дословно:

> «Микроданные многих волн не опубликованы даже на сайте Росстата. Мы их получили через
> официальный запрос и опубликовали в удобном для работы формате… **К микроданным прилагаются
> вопросники и кодбуки с описанием обследования и переменных.**»
> «Для того, чтобы не скачивать весь массив данных, можно выбрать интересующее вас обследование
> и скачать архив с данными только по нему.»

🔴 **Но сам вопрос — есть ли в КОУЖ/ВНДН долговой блок и сбережения по целям — остаётся
без ответа.** Вопросники лежат внутри архивов (ВНДН — 1,2 ГБ), качать их ради проверки
запрещено бюджетом. Никаких утверждений о содержании КОУЖ/ВНДН в этой теме нет и делать
их нельзя.

#### Д.14.6 🔴 ИТОГ по альтернативам

| Источник | (1) досрочное погашение | (2) суммы по целям | (3) ставка по потребкредиту | (4) просрочка по потребкредиту | доступ |
|---|---|---|---|---|---|
| **ОДПФ ЦБ (РФ)** | **НЕТ** | **НЕТ** (только бинарное `o28`) | **НЕТ** | **НЕТ** (есть по картам/авто/недвижимости) | открыт, условие — ссылка |
| **SCF 2022 (США)** | **ДА**, категория по каждому кредиту | нет (цели ранжированы) | **ДА** | **ДА** | публичный, без заявки |
| **HFCS (ЕС)** | **НЕТ** | нет (12 бинарных целей, вкл. «Paying off debts») | **ДА** | **ДА** (>90 дней) | паспорт + CV + форма |
| **PSID** | не установлено | не установлено | не установлено | не установлено | **403**, антибот |
| **Бюро РФ** | по природе ДА | **НЕТ принципиально** | по природе ДА | по природе ДА | публичных микроданных не найдено |
| **КОУЖ / ВНДН** | не установлено | не установлено | не установлено | не установлено | открыт, CC BY 4.0 |

**Прямой ответ: ни один ДОСТУПНЫЙ российский источник дыру не закрывает.** ОДПФ её не
содержит, бюро публично данных не дают, КОУЖ/ВНДН не проверены. Оценивать веса SAW
«по наблюдаемому российскому поведению» **нечем** — и это свойство поля, а не недоработка
поиска.

**Что из этого всё-таки берём:**
1. 🟢 **Формулировку вопроса.** `ahead of schedule / on schedule / behind schedule` по каждому
   кредиту — одна кнопка в интерфейсе FINPILOT. Если продукт когда-нибудь соберёт собственные
   данные пользователей, он будет измерять ровно ту величину, которой нет ни в одном
   российском обследовании. Это не «когда-нибудь», а конкурентное преимущество: такой
   переменной по РФ не существует ни у кого.
2. 🟢 **Внешнюю опору постановки задачи** — `f - Paying off debts` как цель сбережения
   в анкете ЕЦБ (Д.14.2).
3. 🟡 **SCF как площадку для пилота метода**, но не для весов: на нём можно численно проверить,
   что связка (ставка, остаток, цель, доход) → «плачу сверх графика» вообще оценима. Перенос
   коэффициентов на РФ потребовал бы отдельного обоснования, а с учётом Д.6 (люди гасят
   неоптимально) он и не нужен.

---

## ИЗМЕНЕНИЯ ВЫВОДОВ ПО ИТОГАМ ДОБОРА 11.09.2026

### 1. Что ПОДТВЕРДИЛОСЬ

| Вывод первой редакции | Чем подтверждён в доборе |
|---|---|
| ОДПФ — открытые микроданные, единственное условие — ссылка на источник | пять прямых `curl` дали 200 без кук, регистрации и соглашения; размеры совпали байт в байт (Д.1.1) |
| Числа §1.3.1 (`h28`, `o29`, цели) | пересчитаны с нуля другим кодом — совпадение по всем шести строкам `h28` до 0,1 п.п., медиана `o29` = 100 000 ₽ точно (Д.11) |
| Панель 2022→2024 склеивается | посчитано: **5 326** ДХ (было 5 325), 87,6 % волны (Д.2.4) |
| Взвешивание по `hhwgt` корректно | сверено с публикацией ЦБ: сбережения 48,3 %/(100−5,2) = 50,9 % против официальных 51 % (Д.7) |
| Порог ПДН ≤ 0,40 осмыслен | впервые посчитано распределение: медиана 0,150, порог отсекает 6,8 % платящих ДХ, лежит на p90–p92 (Д.12) |
| Норматив подушки Greninger (2,5–3 мес) | 🟢 **независимо подтверждён**: медиана желаемого резерва россиян в 2024 г. = **2,50 месяца расходов** (Д.10) |
| RLMS берётся без заявки | подтверждено дословной таблицей UNC (три «No») — Д.5.4 |
| Микроданные Росстата только через tochno.st | `rosstat.gov.ru/microdata` = 404, `obdx.gks.ru` за логином; лицензия **CC BY 4.0** прочитана в паспорте набора (Д.5.1–Д.5.2) |
| Широкие интервалы по историческим когортам — честная мера | 🟢 первоисточник Künsch 1989 добыт: «consistency is obtained if l = l(n) → ∞ and **l(n)/n → 0**» (Д.4.1) |

### 2. Что УТОЧНИЛОСЬ

- **Панель ОДПФ — не шесть волн, а две.** Доход, расходы, месячный поток сбережений и весь
  ипотечный блок заполнены **только в 2022 и 2024**; в волнах Минфина 2013–2020 — ровно ноль.
  Сквозных столбцов во всех шести волнах — **96 из 2 680** (Д.2.3).
- **Найдены объединённые файлы всех волн** (`t_ankea.rar` 15,8 МБ, `t_anketa_1.rar` 28,2 МБ),
  которых не было в §1.3. Формат RAR5; распаковывает штатный **`bsdtar`** (Д.2.1).
- **CSV от ЦБ — это ЛЕЙБЛЫ, а не коды.** Совет «кодировать 97/98/997/998 как пропуск»
  к CSV неприменим; фильтровать надо по строкам «ЗАТРУДНЯЮСЬ ОТВЕТИТЬ» / «ОТКАЗ ОТ ОТВЕТА» /
  `NA`. Плюс R-нотация в суммах (`3e+05`) — нужен float-парсер (Д.1.1).
- **Индивидуальный файл вскрыт:** 11 835 × 1 859, разделитель **запятая**, вес индивида —
  **`inwgt`**, не `hhwgt` (Д.1.1).
- **Choupani & Mamdoohi** — две разные работы, цитата принадлежит **2017**, а не 2016:
  *Computers, Environment and Urban Systems*, vol. 68, 78–88; Unpaywall `closed`, 0 OA-локаций
  (Д.4.2).
- **Blanchett, Kowara & Chen 2012** — не «не читан», а **не индексирован**: OpenAlex `count = 0`,
  в Crossref нет; DOI отсутствует, Unpaywall неприменим (Д.4.3).
- **Politis & Romano 1994** — Unpaywall `is_oa: false, oa_status: "closed"`, `best_oa_location: None`.
  Проверено, что открытого доступа не существует (Д.4.1).
- **Расхождение зеркал RLMS оказалось ошибкой сниппета**, а не противоречием: слова «register»
  на страницах ВШЭ нет ни разу (Д.5.4).
- **Смещение неответа** названо числом: 6 079 интервью на 8 940 обойдённых адресов = 68 %,
  и неответ растёт среди новых ДХ, то есть среди отказывающихся говорить о финансах (Д.8).

### 3. 🔴 Что ОПРОВЕРГНУТО

1. **«ОДПФ даёт ставку по каждому кредиту» — НЕВЕРНО.** В блоке потребительских кредитов
   (С4) ставки нет вовсе. `С4.8` — это «где Вы брали этот кредит» (канал выдачи), а не процент.
   Ставка есть только по картам (`p611_*`), авто (`e22_*`), ипотеке (`a64`) и МФО (`c3_4`,
   всего 23 ответа). Из 645 человек, назвавших сумму потребкредита, ставку не назвал никто —
   вопроса нет (Д.1.2, Д.9).
2. **«С2.13 — средний ежемесячный платёж по карте» — НЕВЕРНО.** `p614_*` — это «сколько
   тратите по карте», `p615_*` — остаток задолженности. **Минимального платежа по карте
   в анкете нет вообще** (Д.12).
3. **«Просрочка измерима» — только частично.** По потребительскому кредиту, самому частому
   классу долга, вопроса о задержке платежей НЕТ; он есть по картам, авто и недвижимости
   (Д.1.2). Базовая частота исхода по публикации ЦБ — **0,9–2,5 %**, то есть десятки событий
   на панели (Д.7).
4. 🔴 **ГЛАВНОЕ. «Из ОДПФ можно построить распределение „свободный поток → фактическое
   распределение между долгами, резервом и целями“» — НЕТ, НЕЛЬЗЯ.** Три независимых причины,
   каждая смертельна по отдельности (Д.1.4):
   - домохозяйств с одновременно долгом, положительным потоком и названной суммой
     отложенного — **95 из 6 079**;
   - «в долг» в ОДПФ — это `c47_*`, договорный платёж, то есть **обязанность**, а модель
     распределяет **свободный** поток; вопроса о сверхграфиковом взносе нет;
   - «в цели» суммой не измерено вовсе — только бинарное `o28`.
5. **«Свободный поток = Н13 − Н14» — не наблюдаемая величина.** Отрицательный поток
   у 0,4 % ДХ, у 13,7 % из 95 отложено больше, чем «свободно». 🔴 Это **признаёт сам ЦБ**
   (сноска 18 доклада): доли ДХ, у которых доход превышает расход, больше долей сообщающих
   о сбережениях **на 17–32 п.п.** (Д.7).
6. **«Учиться весам у наблюдаемого поведения» — ВРЕДНО.** Gathergood et al., AER 2019
   (прочитан целиком по NBER WP 24161): люди направляют на дорогую карту 51,5 % избыточного
   платежа при нормативных 97,1 %; ошибка **не убывает** с ростом ставок; ML-модель
   максимального фита даёт ставке **низкую** variable importance, а балансам — наивысшую.
   Обучение по поведению воспроизводит balance matching, то есть ровно ту ошибку, которую
   исправляет Avalanche (Д.6.1–Д.6.2).
7. **Тофаллис бьёт по калибровке по данным так же, как по экспертной.** Вес без
   канонизированной нормировки не определён; при выборочно-зависимой нормировке оценка
   по популяции есть **среднее несоизмеримых величин**, и рост объёма выборки её не чинит,
   а только сужает интервал вокруг бессмысленного числа (Д.3).

### 4. Что ИЗМЕНИТЬ В ПЛАНЕ (конкретно)

| Пункт первой редакции | Решение |
|---|---|
| §1.5 «панель 6 волн для проверки устойчивости» | заменить на «две волны по доходу/долгу (2022, 2024); шесть волн по `h28`, `o27`, `o29`, `h33`» |
| §1.3 «ставка по каждому кредиту», «С2.13 платёж» | 🔴 удалить как ошибочные; ставку по потребкредиту **вменять** из публикуемой ЦБ ПСК по сроку (`p96_*`) и каналу выдачи (`c48_*`), долю вменённых публиковать (Д.9) |
| Шаг 3, исход «появление просрочки» | 🔴 снять: по потребкредиту переменной нет, по остальным базовая частота 0,9–2,5 % → метрики **O1 и O2 переформулировать** на частый исход (падение `h28`, рост числа кредитов) либо снять совсем (Д.7) |
| Шаг 1 «ре-сэмплинг 12 000 с весами» | 🟢 остаётся в силе и усиливается; добавить обязательную оговорку о смещении неответа 32 % (Д.8) |
| Шаг 2(б) «российский норматив» | 🟢 остаётся; **брать в месяцах расходов (медиана 2,50), а не в рублях** — месяцы не стареют с инфляцией (Д.10) |
| Идея калибровать веса по данным | 🔴 закрыть. Сначала канонизировать нормировку в `docs/math_model.md` (Тофаллис), и даже после этого данных нет (95 ДХ) |
| Ссылка на Grove et al. 2000 в Шаге 6 | пометить как непрочитанный первоисточник: Unpaywall `closed` (Д.6.5) |
| Описание продукта | добавить измеренную границу: Avalanche применим к **6,7 %** домохозяйств (≥2 долговые позиции), и сказать это самим (Д.9) |
| Интерфейс FINPILOT | 🟢 добавить вопрос SCF `ahead of schedule / on schedule / behind schedule` по каждому долгу — переменной, которой нет ни в одном российском обследовании, продукт начнёт владеть сам (Д.14.6) |

### 5. Что ОСТАЛОСЬ НЕИЗВЕСТНЫМ и что именно вернул отказ

| Что | Код отказа / статус |
|---|---|
| Polits & Romano 1994 «The Stationary Bootstrap» | Unpaywall `is_oa: false`, `oa_status: "closed"`, `best_oa_location: None` — **открытого доступа не существует** |
| Choupani & Mamdoohi 2017 (CEUS 68:78–88), полный текст | Unpaywall `closed`, **0 OA-локаций**; цитата про округление остаётся со сводки |
| Choupani & Mamdoohi 2016 (TRP), PDF | `oa_status: "gold"`, но ScienceDirect отдал **403** (HTML-заглушка 1 208 167 Б); прочитана только аннотация |
| Blanchett, Kowara & Chen 2012 (первоисточник WER) | OpenAlex `count = 0`, Crossref — нет; **DOI отсутствует**, проверить открытыми API невозможно |
| Dawes 1979, Dawes & Corrigan 1974, Einhorn & Hogarth 1975, Wainer 1976, Grove et al. 2000, Dana & Dawes 2004, Hogarth & Karelaia 2007 | все семь — Unpaywall `is_oa: false`, `oa_status: "closed"`; пять зеркал Dawes 1979 через `curl` вернули HTML-заглушки. 🔴 **ОБНОВЛЕНО 11.09.2026 перепроверкой Д3:** тезис «равные веса не хуже подогнанных» в сильной форме **ОПРОВЕРГНУТ** собственной таблицей Дауэса (1979, с. 576) — на 861 наблюдении и 11 признаках регрессия с кросс-валидацией бьёт равные веса .46 против .34, порог 15–20 наблюдений на признак. И хуже для нас: веса, выведенные из поведения экспертов, проиграли равным во всех пяти исследованиях (с. 576–577). Полные тексты Dawes 1979, Dawes & Corrigan 1974, Grove et al. 2000, Meehl 1978, Hogarth 2006 — в `approach_validity_2026-09-10.md`, разделы «ПЕРЕПРОВЕРКА Д3 С ПОИСКОМ». Dana & Dawes 2004 и Hogarth & Karelaia 2007 (Psych Review) по-прежнему `closed`; рабочий документ Hogarth & Karelaia (UPF WP 974, 2006) добыт полным текстом — см. П5.3.2 |
| Amar et al. 2011, Kettle et al. 2016 (snowball, лабораторные) | `closed`; у Kettle пять локаций в OpenAlex и все не-OA. 🔴 **ОБНОВЛЕНО 11.09.2026 добором Д11** (`behavioral_execution_gap_2026-09-10.md`, разделы «ДОБОР Д11»): Amar et al. 2011 добыт и работает **ПРОТИВ** snowball, а не за — в теме 26 она стояла в лагере «за» по ошибке. Gal & McShane добыты и **не доказывают**, что snowball доводит погашение до конца: порядок закрытия счетов выбирала фирма, ставок в данных нет вовсе. Kettle et al. 2016 остаётся `closed`, все пять локаций не-OA (в перепроверке Д5 не пробовался — бюджет). Итог: утверждение «snowball выигрывает по доведению до конца» **опровергнуто**, а не просто не подтверждено |
| Besharat et al. 2014 | Unpaywall `is_oa: true, oa_status: "green"`, но в DSpace Griffith у item **только бандлы LICENSE, файла нет** — «зелёная» запись без файла |
| Gathergood & Weber 2014 (co-holding), полный текст | ScienceDirect **403**; Nottingham ePrints **404**; Repository@Nottingham **403 (Cloudflare)**. Прочитана аннотация: 12 % ДХ co-hold, £3 800 |
| PSID — содержание долгового блока | `psidonline.isr.umich.edu` — **HTTP 403**, «Security Challenge. Enable JavaScript and cookies to continue» |
| КОУЖ / ВНДН — есть ли долговой блок и цели сбережений | страницы Росстата — SPA, разделы «Вопросники»/«Политика доступа» пустые в HTML; угаданные адреса КОУЖ — **404**; вопросники лежат внутри архивов (ВНДН 1,2 ГБ), качать не стали |
| НБКИ / ОКБ — условия доступа исследователей | `nbki.ru` — лента за JS; `bki-okb.ru/press/news` и `/press/research` — **2 149 и 2 153 байта** пустой SPA-оболочки. Скоринг Бюро не запрашивалось |
| Объём выборки ВНДН (60/160 тыс.) | в паспорте каталога **не указан**, остаётся со сниппета Росстата |
| RLMS «Citing the Data», точный текст | `rlms-hse.cpc.unc.edu/citing-the-data` — **404** |
| «Flat maximum principle» в многокритериальном выборе | поиск по OpenAlex релевантного не дал; отрицательный **результат поиска**, не отсутствие литературы |

### 6. 🔴 Честно про инструменты этого прогона

В доборе были закрыты **три канала обнаружения одновременно**: `WebSearch` исчерпан (400/400),
Exa отдаёт 404, `r.jina.ai` — 401. Осталось два: API метаданных (OpenAlex / Crossref /
Unpaywall / Semantic Scholar) и прямой `curl`.

**Чем это обернулось конкретно.** API метаданных находят работу **по известному названию**,
но не находят её **зеркала**. Поэтому весь блок «improper linear models» остался без единого
прочитанного текста: зеркала Dawes 1979 в вебе почти наверняка есть — их нечем было искать.
🔴 Это ограничение прогона, а не вывод о литературе, и оно прямо повлияло на результат:
раздел «контрпримеры» держится на **одном** полностью прочитанном источнике вместо восьми.

**Что при этом сработало лучше, чем раньше:**
- 🟢 **Unpaywall как инструмент честности.** Он превратил девять «не смог открыть» в проверяемые
  «открытого доступа не существует» с дословным вердиктом. Это не добыча, но это знание.
  И он же поймал ложноположительный случай (Besharat: `green` без файла).
- 🟢 **`bsdtar` берёт RAR5** — новый приём, открывший объединённые файлы всех волн ОДПФ.
- 🟢 **`Read` с `pages` по сканированному PDF** — Künsch 1989 не имеет текстового слоя
  (`pdftotext` вернул 378 байт обложки JSTOR), постраничный рендер прочитался целиком.
- 🟢 **Сверка своих расчётов с независимой публикацией того же ведомства** — именно она поймала
  мою ошибку с `p615` (Д.12). Без неё ошибочная медиана ПДН 0,206 ушла бы в отчёт.

**Подагентов — два, последовательно, не веером.** Оба записали сырьё в файл ДО итогового
ответа (`scratchpad/subagent_A.md` 238 строк, `subagent_B.md` 31 176 Б). Ни один не оборвался.
Вызовов `WebSearch` — **ноль**.

### 7. Одной фразой

**Добор не расширил план — он его сузил, и это главный его результат:** ОДПФ остаётся
превосходным источником **популяции** (и подтвердил норматив подушки с точностью до сотой),
но идея откалибровать веса SAW по наблюдаемому поведению россиян закрыта тремя независимыми
ударами — данных нет (95 домохозяйств), измеряемая величина не та (обязанность вместо выбора),
а даже при идеальных данных веса неидентифицируемы без канонизированной нормировки и вредны,
потому что воспроизводят задокументированную ошибку людей.

---

## ПЕРЕПРОВЕРКА Д5 С ПОИСКОМ — шапка и метод

Дата: 11.09.2026. Основание: добор Д5 (раздел «ДОБОР 11.09.2026» выше) шёл с тремя
мёртвыми каналами обнаружения одновременно — `WebSearch` исчерпан (400/400 в нашем же
`~/.claude/settings.json`, теперь поднят), Exa 404, `r.jina.ai` 401. Сам добор назвал
последствие: «API метаданных находят работу по известному названию, но не находят её
зеркала… раздел контрпримеров держится на одном полностью прочитанном источнике вместо
восьми». Перепроверка — с работающим `WebSearch`.

**Что НЕ перепроверялось (закрыто соседними доборами этой сессии):** блок improper linear
models — перепроверка Д3 в `approach_validity_2026-09-10.md`; Amar et al. 2011, Gal &
McShane, Hamilton 2023 — добор Д11 в `behavioral_execution_gap_2026-09-10.md`; co-holding
на российских данных и условия RLMS — добор Д9.

**Порядок каналов этого прогона:** `WebSearch` → `WebFetch` → `curl -sk --http1.1` с
браузерным UA → `r.jina.ai` → API метаданных → Wayback с суффиксом `id_`.

**Первая проверка канала (11.09.2026):** `WebSearch` отдаёт выдачу — два запроса
(`PSID codebook "paid ahead of schedule"`, `SCF "ahead of schedule" "behind schedule"`)
вернули по 9 ссылок каждый. Бюджет не отказал.

### ПЕРЕПРОВЕРКА Д5 С ПОИСКОМ — П5.1(а) SCF: дословный текст вопроса и коды переменных 🟢 ДОБЫТО

**Канал:** `WebSearch` (запрос `Survey of Consumer Finances question "ahead of schedule"
"behind schedule" loan payments variable`, 9 ссылок, релевантного прямого ответа НЕ дал —
поиск дал только выход на federalreserve.gov) → **прямой `curl -sk --http1.1`** с браузерным
UA по кодбуку SCF.

- `https://www.federalreserve.gov/econres/files/codebk2022.txt` — **HTTP 200, 2 819 548 Б**
- `https://www.federalreserve.gov/econres/files/codebk2019.txt` — **HTTP 200, 2 764 991 Б**

Это машинно читаемый кодбук SCF 2022 целиком, а не сниппет. Все цитаты ниже — из
полностью прочитанного файла (grep + sed по локальной копии).

**Дословный текст вопроса (кодбук SCF 2022, блок первой/второй/третьей ипотеки, строки 7991–7999):**

```
X7571(#1)       Are you paying off this (land contract/loan) ahead of
X7570(#2)       schedule, behind schedule, or are the payments about
X7569(#3)       on schedule?

                IF R EXITED FORBEARANCE VIA A MODIFIED LOAN,
                CHOOSE "ON SCHEDULE".

                     1.    *On schedule
                     2.    *Ahead of schedule
                     3.    *Behind schedule
```

Вариант для нессудных блоков (строки 8817–8822), формулировка чуть иная —
пассив вместо активного залога:

```
X7566           Are you paying off this loan ahead of schedule, behind
                schedule, or are the payments about on schedule?
```
и
```
X7554(#1)       Is this loan being paid off ahead of schedule, behind
X7553(#2)       schedule, or are the payments about on schedule?
```

**Коды переменных.** Вопрос задаётся **по каждому долгу отдельно** — восемь блоков анкеты,
18 уникальных кодов переменных (по слотам кредитов внутри блока):
`X7519 X7520 X7521 X7528 X7529 X7532 X7533 X7534 X7553 X7554 X7564 X7566 X7569 X7570 X7571
X7821 X7844 X7867`. То есть предписание плана темы 35 «вопрос SCF по КАЖДОМУ долгу»
воспроизведено верно — это действительно per-loan переменная.

🔴 **ГЛАВНАЯ ПОПРАВКА, которой не было в первом доборе: SCF спрашивает НАПРАВЛЕНИЕ,
но НЕ СУММУ переопережения.** Проверено по полному кодбуку:
- Единственный follow-up при ответе «не по графику» — **ожидаемый месяц/год погашения**
  (`X1042` месяц, `X1043` год, `X815/X915/X1015` год; skip-логика прямо гласит
  `Inap. … payments on schedule: X7566=1`, то есть вопрос задаётся ТОЛЬКО тем,
  кто ответил не «on schedule»). Никакого «сколько рублей/долларов сверх графика» нет.
- Формулировки «more than the minimum», «extra payment», «pay more than» в кодбуке
  **отсутствуют вовсе** (grep по 2,8 МБ: 0 совпадений по «extra payment» и «pay more than»;
  «minimum payment» встречается дважды и оба раза — как инструкция интервьюеру
  «WE WANT THE TOTAL AMOUNT OWED, NOT THE MINIMUM PAYMENT», строки 5110 и 5337).
- По кредитным картам SCF спрашивает `X413`/`X443`/`X7575` «After the last payment(s)
  (was/were) made, what was the total amount…» — то есть **остаток после платежа**,
  а не размер платежа сверх минимума.

**Что это меняет для темы 35.** Два следствия, противоположных по знаку:
1. 🟢 Строка плана «Интерфейс FINPILOT: добавить вопрос SCF `ahead / on / behind schedule`
   по каждому долгу» — **подтверждена дословно и уточнена**: это ординальная переменная
   из трёх категорий, задаваемая per-loan, с единственным продолжением про ожидаемый срок
   погашения. Формулировку можно брать в интерфейс как есть (перевод трёх категорий +
   вопрос об ожидаемом годе закрытия).
2. 🔴 Но она **не даёт эталона для калибровки весов**: даже эталонное обследование США,
   из которого формулировка взята, **не наблюдает величину** сверхграфикового взноса.
   То есть центральная величина темы 35 («сколько свободного потока ушло на досрочное
   погашение») не наблюдаема не только в российских анкетах — она не наблюдаема
   и в SCF. Прежний неявный подтекст плана («в SCF это есть, а у нас нет») **неверен**:
   в SCF есть только знак, и по нему веса свёртки не откалибровать.

### ПЕРЕПРОВЕРКА Д5 С ПОИСКОМ — П5.1(б) PSID: долговой блок 🟢 ДОБЫТО ПОЛНОСТЬЮ

**Что изменил поиск против первого добора.** Первый добор записал: «`psidonline.isr.umich.edu`
— HTTP 403, „Security Challenge. Enable JavaScript and cookies to continue“». Перепроверка
подтверждает 403 на самом сайте (`/data/Documentation/UserGuide2015.pdf` — **403, 43 152 Б**
тела-заглушки; `/CDS/CuratedPSIDVariables.pdf` — **403, 43 107 Б**), но **обошла его двумя
каналами, которых у первого добора не было**:

1. 🟢 **Wayback с суффиксом `id_`** — полные кодбуки PSID:
   `https://web.archive.org/web/20250715005351id_/https://psidonline.isr.umich.edu/documents/psid/codebook/FAM2023ER_codebook.pdf`
   — **HTTP 200, 3 439 538 Б**, `pdftotext -layout` → 3 548 639 Б текста, 1 358 страниц.
   `…/20210630021544id_/…/FAM2019ER_codebook.pdf` — **HTTP 200, 5 096 192 Б** → 5 668 591 Б текста.
   Адреса получены не угадыванием, а из **CDX API Wayback**
   (`http://web.archive.org/cdx/search/cdx?url=psidonline.isr.umich.edu/documents/psid/codebook*`) —
   там перечислены снимки всех волн 2001–2023.
   🔴 Замечание по каналу: попытка взять тот же файл через `web/2023id_/…UserGuide2015.pdf`
   (без точного таймстампа из CDX) дала **ровно 1 048 576 Б** — усечённый файл, `pdftotext`
   упал с «Invalid XRef entry 0». Ровный 1 МБ — признак обрезки, а не успеха; таймстамп
   надо брать из CDX.
2. 🟢 **Внешнее зеркало документации** — `PSID Main Interview User Manual` лежит на сайте
   Университета штата Орегон:
   `https://health.oregonstate.edu/sites/health.oregonstate.edu/files/char/military-life-course/study-documents/PSID-DOCUMENTS/psid_userguide2009.pdf`
   — **HTTP 200, 722 923 Б** → 324 351 Б текста. Найдено `WebSearch`-ом
   (запрос `PSID wealth questionnaire "how much do you have in savings" mortgage prepayment question text`).

**Ответ на три вопроса участка, по полностью прочитанному кодбуку PSID 2023 (Family File):**

**(1) Вопрос о досрочном или сверхграфиковом погашении долга — 🔴 В PSID ОТСУТСТВУЕТ.**
Отрицательный результат машинный, а не «не нашёл»: grep по 3,5 МБ текста кодбука 2023 —
**0 совпадений** по `ahead of schedule`, `behind schedule`, `prepay`, `extra payment`,
`more than … required`, `minimum payment`. По кодбуку 2019 — **0 совпадений** по
`ahead of schedule`. То, что PSID спрашивает про отклонение от графика, — **только
в сторону просрочки**:

```
A27a. Some people have had difficulties recently making their mortgage or loan payments.
Are you (or anyone in your family living there) currently behind on your (mortgage/loan)
payments?--FIRST MORTGAGE          [ER82064; Yes 74 (0,81 %), No 2 703 (29,53 %)]
ER82065  "A27B MONTHS BEHIND ON MTGE # 1"
A27b. How many months are you behind?--FIRST MORTGAGE
```

Что PSID про долг спрашивает (блок A, по каждой из двух ипотек отдельно):
`A23` наличие кредита → `A23a` тип (mortgage / land contract / home equity loan) →
`A23b` первичный или рефинансированный → **`A24` остаток основного долга** →
**`A25` размер месячного платежа** → `A25a3` фиксированная или переменная ставка →
**`A25a4` текущая ставка** (целая часть `ER82060` + дробная, отдельными переменными) →
`A26` год получения/рефинансирования → **`A27` сколько ещё лет платить** → `A27a/A27b`
просрочка → `A27d/A27e` месяц и год начала обращения взыскания.

**(2) Вопрос о сумме сбережений — 🟢 ЕСТЬ, дословно (кодбук 2023, с. 646):**

```
ER83939  "W27A WTR CHECKING/SAVING ACCT"
W27a. Do you (or anyone in your family living there) have checking or savings accounts,
including money market accounts?
    6,484  70.85%  1 Yes, one or more
    2,568  28.06%  5 No, none

ER83940  "W28A AMT CK/SAVING ACCT"
W28a. If you added up all of your checking, saving, and money market accounts (for all of
your family living there), about how much would they amount to altogether right now?
    5,559  60.74%  Actual amount
       74   0.81%  DK
      588   6.42%  NA; refused
    2,863  31.28%  Inap.: amount is zero / no account
```
Плюс **unfolding brackets** (`W30a. Would they amount to $15,000 or more?` и т. д.) —
приём восстановления суммы у тех, кто отказался назвать её напрямую. Это прямой
методический образец для FINPILOT: 6,42 % отказов по сумме лечится вопросом
«больше или меньше порога», а не вменением.

**(3) Вопрос типа SCF `ahead / on / behind schedule` — 🔴 В PSID ЕГО НЕТ** (см. п. 1).
То есть предписание плана «взять вопрос SCF» — верно именно как **SCF**, а не «как
в западных панелях вообще»: эталонная панель PSID этой переменной не содержит.

**(4) Ближайший аналог «распределения потока» в PSID — блок W43–W46 «active saving».**
Дословно: «W43. These next questions are about changes in your wealth during the last two
years… Since January 2021, did you (or anyone in your family living there) put aside money
in any private annuities or I.R.A.s?» → `W44. How much did that amount to?`
(`ER84009`, actual amount у 854 ДХ = 9,33 %; `Inap.` у 8 161 = 89,17 %).
🔴 **Это и есть та же проблема, что в ОДПФ, только в эталонной панели:** даже PSID
измеряет «сколько отложил» лишь по одному каналу (пенсионные счета), за два года,
и заполненность — **9,33 % домохозяйств**. Разложения «свободный поток → доли между
долгом, резервом и целями» нет и в PSID.

**Что это меняет для темы 35.** 🔴 **Центральный вывод УКРЕПЛЁН, а не поколеблен.**
Прежняя формулировка добора Д5 звучала как «в российских анкетах этого нет»; после
перепроверки корректная формулировка сильнее: **переменной „сколько свободного потока
ушло сверх графика на досрочное погашение“ нет ни в ОДПФ, ни в ВНДН, ни в PSID, ни в SCF.**
Это не дефект российской статистики — это отсутствие такой переменной в мировой практике
панельных обследований домохозяйств. Соответственно эталон для калибровки весов SAW
нельзя построить не только из российских данных, но и импортом зарубежных.

### ПЕРЕПРОВЕРКА Д5 С ПОИСКОМ — П5.2 ВНДН против плана темы 35 🟢 ДОБЫТО, находка Д9 ПОДТВЕРЖДЕНА и УТОЧНЕНА

**Канал:** `WebSearch` (`вопросник ВНДН форма 1-доходы кредиты займы "остаток задолженности"
"процентная ставка" домохозяйство Росстат`) → прямой `curl -sk --http1.1`.
- «Указания по заполнению форм федерального статистического наблюдения», приложение № 3
  к приказу Росстата от 13.08.2024 № 360 (НДН-2025):
  `https://03.rosstat.gov.ru/storage/mediabank/ndn-2025_pr_ros_360_20240813_ukaz.pdf`
  — **HTTP 200, 6 938 289 Б**; `pdftotext -layout` → **523 201 Б** текста, разобрано целиком
  (одно предупреждение `Invalid number of shared object groups`, на текст не повлияло).
- `https://27.rosstat.gov.ru/impotant/document/150257` (Хабаровскстат) — **HTTP 200, 728 222 Б**.
- Не сработало: `rosstat.gov.ru/free_doc/new_site/usp/survey0/technicalInformation/dataCollection.html`
  — **404, 1 245 Б**; `gks.ru/free_doc/new_site/vndn-2020/index.html` — **403, 548 Б**
  (то же поведение госсайтов, что в первом доборе).

**Дословно, Указания к НДН-2025, «Раздел 7. Финансовое положение домохозяйства», п. 133
(вопрос 5):**

> «Уточняются условия займа, установленные договором с банком. По первой строке «Каковы цели
> займа» (код 1) переносятся коды из вопроса 4. Если задолженностей было несколько, ответы
> проставляются во всех предусмотренных для этого графах. Если на одну и ту же цель было взято
> несколько кредитов, коды в строке 1 могут повторяться. Далее указывается год заключения
> договора (код 2), **процентная ставка в год (код 3), ежемесячная сумма погашения (код 4),
> остаток долга по кредиту по состоянию на конец года**.
> **Если домохозяйство имеет несколько задолженностей на покупку товаров и неотложные нужды,
> указываются наиболее крупные из них.**»

Плюс п. 130 (вопрос 3) — факт наличия остатка долга; п. 132 (вопрос 4) — цели займа,
несколько вариантов; п. 134 (вопрос 5.1) — участие в программе льготной ипотеки с господдержкой;
п. 140 (вопрос 10) — **число раз возникновения задолженности** из-за недостатка денег по трём
графам: аренда/ипотека основного жилья, ЖКУ, товары в кредит; п. 137–138 (вопросы 7–8) —
«свести концы с концами» и минимальный необходимый доход.

**🟢 Находка Д9 подтверждена первоисточником:** покредитный блок в ВНДН действительно есть,
и в нём есть ровно те четыре величины, ради которых план темы 35 завёл вменение —
цель, год договора, **ставка в год**, ежемесячный платёж, остаток долга.

**🔴 Три оговорки, которых у Д9 не было — и каждая ограничивает пригодность ВНДН:**

1. 🔴 **Покредитный блок НЕ исчерпывающий.** Прямая цитата: «Если домохозяйство имеет
   несколько задолженностей на покупку товаров и неотложные нужды, указываются **наиболее
   крупные из них**». То есть по самому массовому классу долгов (потребительские и на
   неотложные нужды) фиксируются не все позиции, а крупнейшие. Для Avalanche это
   критично: алгоритм сортирует **все** долги по ставке, а данные гарантированно
   усечены по числу позиций именно там, где долгов много. Измеренная в Д.9 граница
   «Avalanche применим к 6,7 % домохозяйств (≥2 долговые позиции)» на ВНДН
   воспроизведена быть не может — усечение даёт смещение вниз по числу позиций.
2. 🔴 **Остаток долга — «по состоянию на конец года», ежемесячный платёж — договорный.**
   Это годовой срез обязательств, а не месячный поток решений. Та же подмена, что
   в ОДПФ (`c47_*` — обязанность, не выбор), только в другом обследовании.
3. 🔴 **Ставка спрашивается у респондента, а не берётся из договора.** «Процентная ставка
   в год» — самоотчёт домохозяйства. Это не эквивалент ПСК и не банковская отчётность;
   для подстановки в Avalanche качество такой ставки надо публиковать как ограничение.

**🟡 Подтверждено отрицательное (совпадает с Д9, проверено grep-ом по 523 КБ Указаний):**
вопроса о **досрочном / сверхграфиковом погашении** в ВНДН **нет** (0 совпадений
по «досрочн» в кредитном контексте — все 6 совпадений относятся к досрочной пенсии);
вопроса о **сумме сбережений** — **нет** (единственные совпадения «сбережения» — в
определении оплаты труда «направлялась на личные нужды и сбережения»); слова
«процентная ставка» вне п. 133 в Указаниях не встречается вовсе.

**🟢 Объём выборки ВНДН — закрыт первоисточником, строка раздела 5 снимается.**
Хабаровскстат, HTTP 200: «данное обследование проводится **ежегодно**… В 2022 г. предстоит
проведение широкомасштабного наблюдения с охватом **160 тысяч домашних хозяйств** во всех
субъектах Российской Федерации, из них в Хабаровском крае — 1 608». То есть 160 тыс. —
это широкомасштабная волна (2022), а ежегодные — меньшего охвата; прежняя запись
«60/160 тыс. со сниппета» уточнена: **оба числа верны и относятся к разным типам волн**,
160 тыс. — широкомасштабная.

**ЧТО КОНКРЕТНО МОЖНО ПЕРЕПИСАТЬ В ПЛАНЕ, А ЧТО НЕЛЬЗЯ:**

| Строка плана (раздел 4) | Решение после перепроверки |
|---|---|
| «ставку по потребкредиту **вменять** из публикуемой ЦБ ПСК по сроку (`p96_*`) и каналу (`c48_*`), долю вменённых публиковать» | 🟡 **остаётся в силе для ОДПФ**, но добавить строку: ставка есть напрямую в ВНДН (вопрос 5, код 3) как **самоотчёт**, и её можно использовать для **валидации вменения** — сверить распределение вменённых ставок с распределением самоотчётных. Убирать вменение нельзя: в ОДПФ, откуда берётся популяция, ставки по потребкредиту по-прежнему нет |
| «шаг 3, исход „появление просрочки“ снять: по потребкредиту переменной нет» | 🟡 **частично отменяется**: в ВНДН вопрос 10 даёт **число раз** возникновения задолженности из-за недостатка денег по трём графам, включая «за товары, приобретённые в кредит». Это не просрочка по кредитному договору, но это частый наблюдаемый исход. Метрики O1/O2 можно переформулировать на него — на ВНДН, не на ОДПФ |
| «строить эталон на ОДПФ» | 🔴 **на ВНДН вместо ОДПФ строить эталон НЕЛЬЗЯ** — причина не в ставках, а в том, что центральная величина (сверхграфиковый взнос) и сумма сбережений в ВНДН отсутствуют так же, как в ОДПФ. Плюс усечение покредитного блока «наиболее крупными» |
| Источник **популяции** для ре-сэмплинга 12 000 | 🟢 **ОДПФ остаётся** (6 079 ДХ, покредитный блок без усечения, есть суммы отложенного). ВНДН пригоден как **второй, независимый источник для сверки маргиналов** — 160 тыс. ДХ против 6 079 дают несравнимо более точные краевые распределения дохода и долговой нагрузки |

**Доступность микроданных ВНДН исследователю — 🟡 частично.**
`WebSearch` дал: обезличенные микроданные ВНДН 2012–2024 существуют и опубликованы
зеркалом `tochno.st/datasets/surveys` (тот же канал, которым первый добор взял ВНДН/КОУЖ,
CC BY 4.0); формулировка зеркала — файлы «получены по официальному запросу» в Росстат.
🔴 **Это сниппет, первоисточник условий доступа не открыт:** официальная страница
`rosstat.gov.ru/microdata` в первом доборе дала **404**, в этой перепроверке
`free_doc/new_site/usp/.../dataCollection.html` — **404**, `gks.ru/.../vndn-2020/` — **403**.
Точный регламент («кому, на каких условиях, по какой форме заявки») **НЕ ДОБЫТ**.
Практический вывод для плана: рабочий путь к микроданным ВНДН — зеркало tochno.st под
CC BY 4.0, официальный канал — через запрос в Росстат, регламент которого документально
не подтверждён.

### ПЕРЕПРОВЕРКА Д5 С ПОИСКОМ — П5.3 методические первоисточники

**П5.3.1 🔴 Gathergood & Weber (co-holding) — ДОБЫТ ПОЛНЫМ ТЕКСТОМ, и он ОПРОВЕРГАЕТ
числа, записанные в разделе 5 файла.**

Канал: `WebSearch` (`Gathergood Weber 2014 "self-control" "financial literacy" co-holding…`)
→ рабочая ссылка не SSRN и не Nottingham ePrints (первый добор упирался в них: ScienceDirect
403, ePrints 404, Repository@Nottingham 403), а **серия рабочих документов CFCM**:
`https://www.nottingham.ac.uk/cfcm/documents/papers/12-04.pdf` — **HTTP 200, 644 445 Б**,
PDF v1.4, `pdftotext -layout` разобрал целиком. Это Working Paper 12/04, версия
**20 февраля 2013**.
(SSRN тем же прогоном: `papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2005031…` — **403, 5 981 Б**;
`core.ac.uk/download/291305276.pdf` — **404, 215 Б**.)

Дословно, абстракт WP 12/04:

> «Approximately **14%** of households in our sample co-hold, on average, **£3,400** of
> revolving consumer credit on which they incur interest charges, even though they could
> immediately pay down all this debt using their liquid assets. Co-holders are typically
> more financially literate, with above average income and education. However, we show
> co-holding is also associated with impulsive spending behavior on the part of the household.»

И во введении, числа, которых в файле не было вовсе:

> «We show that in a sample of UK households 14% hold, on average, £3,400 of revolving
> consumer credit… By co-holding credit and assets, these households incur on average
> **£600 in unnecessary interest charges per annum**. A subset of these, **4% of the sample,
> incur £1,300** in unnecessary interest charges per annum.»

🔴 **Расхождение с записью в файле.** Раздел 5 первого добора содержит: «Прочитана
аннотация: 12 % ДХ co-hold, £3 800». Полностью прочитанный рабочий документ даёт
**14 % и £3 400**. Оба числа, судя по всему, верны — но относятся к **разным версиям
работы**: 12 % / £3 800 — аннотация опубликованной версии (JEBO 2014, т. 107, с. 455–469),
14 % / £3 400 — рабочий документ 2013 года. Вывод для файла: **число из аннотации нельзя
цитировать как «результат Gathergood & Weber» без указания версии**; между WP и публикацией
выборка или определение co-holding менялись. Опубликованная версия полным текстом
по-прежнему НЕ добыта (ScienceDirect закрыт).

**Что добавляет содержательно (и чего в теме 35 не было):** co-holding — это прямая
количественная оценка цены той самой ошибки, которую снимает FINPILOT. Домохозяйство,
держащее резерв при дорогом долге, платит **£600 в год впустую** (в подвыборке 4 % —
£1 300). Это защитимая величина «ценности рекомендации» для описания продукта, и она
измерена, а не оценена. 🟡 Оговорка: Великобритания, данные Debt Tracker, средний доход
выборки £35 300 — переносить на РФ нельзя, только как методический образец постановки
задачи.

**П5.3.2 🟢 Hogarth & Karelaia — ДОБЫТ ПОЛНЫМ ТЕКСТОМ (66 страниц), но это ДРУГАЯ работа,
чем указано в плане.**

Канал: `WebSearch` → `https://econ-papers.upf.edu/papers/974.pdf` — **HTTP 200, 430 728 Б**,
PDF v1.3, **66 страниц**, разобран `pdftotext -layout` целиком.

🔴 **Важное уточнение реквизитов.** В разделе 5 файла работа записана как
«Hogarth & Karelaia 2007» — то есть *Psychological Review* 114(3): 733, «Heuristic and
linear models of judgment: **Matching rules and environments**». Добытый документ —
рабочий документ UPF № 974 от **18 июня 2006**, «On heuristic and linear models of
judgment: **Mapping the demand for knowledge**». Это **предшествующая работа тех же
авторов с той же аналитической рамкой**, а не препринт статьи 2007 года (заголовок иной).
Публикация 2007 года полным текстом НЕ добыта. Всё ниже — из WP 974, и так и надо
цитировать.

Что в нём измерено (мета-анализ lens-model исследований, **255 исследований**: 59 с
экспертами, 192 с новичками, 4 неклассифицированных):

Таблица 5, «Type of weighting function» — точность линейной модели судьи (LC accuracy):
равновесная среда 75 %, компенсаторная 71 %, некомпенсаторная 67 %.

Таблица 6, трёхпризнаковые среды — процент верных бинарных выборов:

| Среда | Максимум возможного | LC (модель судьи) | EW (равные веса) | TTB | Число сред |
|---|---|---|---|---|---|
| Равновесная | 81 | 72 | **80** | 71 | 9 |
| **Компенсаторная** | 81 | 68 | **77** | 73 | 19 |
| Некомпенсаторная | 82 | 67 | 74 | **77** | 26 |

Двухпризнаковые: равновесная — максимум 94, LC 79, **EW 92**; некомпенсаторная —
максимум 84, LC 69, SV 76, TTB 75, EW 73.

Дословно (с. 29): «As would be expected, the EW strategy performs best in equal weighting
environments (80%) and the TTB strategy best in the non-compensatory environments (77%).
Interestingly, **in these compensatory environments, it is the EW model that performs best
(77%). The mean LC model never has the best performance.**»

🔴 **Это независимое подтверждение вывода перепроверки Д3, и оно бьёт по FINPILOT точнее.**
SAW — **компенсаторная** свёртка. Именно в компенсаторных средах равные веса (77 %)
обгоняют линейную модель, подогнанную под суждения человека (68 %), при теоретическом
максимуме 81 %. То есть: (а) веса, выведенные из поведения эксперта, проигрывают равным
весам — ровно как у Дауэса (Д3); (б) разрыв между равными весами и оптимумом мал
(77 против 81) — это и есть эффект «плоского максимума» в числах.
🟡 Оговорка, которую нельзя опускать: колонка LC — это модель **человека-судьи**,
а не регрессия, оптимально подогнанная к исходу. Работа не утверждает, что равные веса
бьют оптимальную регрессию; она утверждает, что они бьют модель человека. Для темы 35
это ровно нужный случай, потому что наши веса откалиброваны по согласию с экспертами.

**П5.3.3 🔴 Politis & Romano 1994 «The Stationary Bootstrap» — НЕ ДОБЫТ.**
Канал: два запроса `WebSearch` (в т. ч. с номерами страниц и словом `lecture notes`).
Все выдачи ведут в три места: `tandfonline.com/doi/abs/10.1080/01621459.1994.10476870`
(абстракт), `jstor.org/stable/2290993`, `scribd.com` (не источник). 🔴 Проверена
персональная страница автора: `https://mathweb.ucsd.edu/~politis/` — **HTTP 200, 4 063 Б**,
и каталог препринтов `https://mathweb.ucsd.edu/~politis/PAPER/` — **HTTP 200, 36 636 Б**;
в каталоге 1994 года нет вовсе, самые ранние выложенные работы — 1999
(`locbootJSPI99.pdf`). Реквизиты подтверждены (JASA 89(428): 1303–1313), открытого доступа
нет, **автор сам его не выкладывает**. Это совпадает с вердиктом Unpaywall первого добора
(`is_oa: false`, `oa_status: "closed"`) — перепроверка с работающим поиском его
**подтвердила, а не опровергла**. §3.3(б) остаётся на сводке.

**П5.3.4 🟡 Choupani & Mamdoohi — реквизиты исправлены, полный текст не добыт.**
🔴 **Первая правка: работы 2017 года в CEUS, по-видимому, НЕТ.** `WebSearch` по
`Choupani Mamdoohi 2017 "iterative proportional fitting" … "Computers Environment and Urban
Systems"` вернул только: (а) *Transportation Research Procedia* 17 (2016): 223–233,
«Population Synthesis Using Iterative Proportional Fitting (IPF): A Review and Future
Research»; (б) *Transportation Research Record* 2493 (2015), `doi:10.3141/2493-01`,
«Population Synthesis in Activity-Based Models». Запись раздела 5 «Choupani & Mamdoohi
2017 (CEUS 68:78–88)» поиском **не подтверждается**; вероятнее, в плане перепутаны
реквизиты и речь о TRP 2016 либо TRR 2015.
Полный текст TRP 2016: подтверждено, что работа **golden OA** — Unpaywall
`oa_status: "gold"`, единственная OA-локация — `sciencedirect.com/…/S2352146516306925/pdf`;
страница статьи, снятая через Wayback (`web/2020id_/…` — **HTTP 200, 87 090 Б**), дословно
содержит «Under a Creative Commons license — open access», DOI `10.1016/j.trpro.2016.11.078`,
с. 223–233. 🔴 Но самого PDF добыть не удалось: `r.jina.ai` по ScienceDirect отдал
**403, 5 878 Б** страницу Cloudflare «Just a moment…» (канал жив, но антибот издателя
его не пускает — та же граница, что зафиксирована в первом прогоне); Wayback по
`…/pdf` дал **HTTP 200, 43 369 Б**, но это **HTML-страница-редирект ScienceDirect,
а не PDF** (`file` → «HTML document text»); CDX показывает, что все снимки этого адреса
— 10–29 КБ HTML, самого PDF в архиве нет. **Цитата про округление в ре-сэмплинге
остаётся со сводки поиска, первоисточник не открыт.**
🟢 Побочно: это второй замеренный случай правила «большой размер ответа не значит успех» —
43 369 Б выглядят как PDF по размеру и не являются им.

**П5.3.5 🔴 Blanchett, Kowara & Chen 2012 — НЕ ДОБЫТ, но статус уточнён.**
Канал: `WebSearch` → **персональный сайт первого автора**
`https://www.davidmblanchett.com/research` — **HTTP 200, 345 108 Б**, разобран.
Реквизиты по странице автора дословно: «Blanchett, David, Maciej Kowara, and Peng Chen.
2012. “Optimal Withdrawal Strategy for Retirement Income Portfolios.” *Retirement Management
Journal*, vol. 2, no. 3 (Fall): **7-18**. ~ this paper was awarded RIIA's 2012 Thought
Leadership Award».
🔴 Два новых факта: (1) **автор сам не выкладывает PDF этой работы**, тогда как рядом
у большинства его публикаций стоят рабочие ссылки «View» на morningstar.com и
davidmblanchett.com — значит отсутствие OA не случайность канала;
(2) 🔴 **расхождение в пагинации**: страница автора даёт «7-18», сводка поиска —
«7–20». Первоисточник не открыт, поэтому в файле правильно писать диапазон
как неподтверждённый. Проба `davidmblanchett.com/Credit%20Cards%2008.16.12%20FINAL.pdf`
(соседняя ссылка с его же страницы) — **404, 117 437 Б** (тело — HTML-страница ошибки,
опять же большой размер при отказе). Запись первого добора «DOI отсутствует, проверить
открытыми API невозможно» **подтверждена**: реквизиты добыты с авторской страницы, текст — нет.

### ПЕРЕПРОВЕРКА Д5 С ПОИСКОМ — П5.3 (окончание): что осталось закрытым

**П5.3.6 🔴 Dana & Dawes 2004 — НЕ ДОБЫТ.** Реквизиты уточнены: *Journal of Educational
and Behavioral Statistics*, 29(3), Autumn 2004, `doi:10.3102/10769986029003317`
(JSTOR 3701356). Пробы: Wayback `web/2020id_/journals.sagepub.com/doi/pdf/10.3102/…`
— **404, 4 684 Б**; `r.jina.ai` по странице SAGE — **403, 5 830 Б** (Cloudflare).
Единственный канал в выдаче — ResearchGate, который не является источником и требует
входа. Совпадает с вердиктом Unpaywall (`closed`).

**П5.3.7 🔴 Besharat et al. 2014 — НЕ ДОБЫТ, но реквизиты в файле, вероятно, ОШИБОЧНЫ.**
Поиск показал, что под «Besharat et al. 2014» скрываются **две разные работы**:
- Besharat, Carrillat & Ladik (2014), «When Motivation is Against Debtors' Best Interest:
  The Illusion of Goal Progress in Credit Card Debt Repayment», *Journal of Public Policy
  & Marketing* 33: 143–158, `doi:10.1509/jppm.13.007`;
- Besharat, Varki & Craig (**2015**), «Keeping consumers in the red: Hedonic debt
  prioritization within multiple debt accounts», *Journal of Consumer Psychology* 25: 311–316,
  `doi:10.1016/j.jcps.2014.08.005`.
Вторая по содержанию ближе к теме («долги за гедонические покупки и долги давние
**усиливают** склонность гасить меньшие остатки вместо остатков с более высокой ставкой» —
🟡 это сниппет, первоисточник не открыт). «Зелёная» запись без файла в DSpace Griffith,
найденная первым добором, относится к одной из двух, к какой — не установлено.
Проба Wayback `…/doi/pdf/10.1509/jppm.13.007` — **404, 4 661 Б**.
**Практический вывод:** в файле нельзя ссылаться на «Besharat et al. 2014» без разведения
этих двух работ; и содержательно интересна та, которая **2015**, а не 2014.

### ПЕРЕПРОВЕРКА Д5 С ПОИСКОМ — П5.4 доступ к данным БКИ 🟡 ЧАСТИЧНО ДОБЫТО

**Что изменил поиск.** Первый добор получил от `nbki.ru` «ленту за JS», а от
`bki-okb.ru/press/*` — пустые SPA-оболочки 2 149 и 2 153 Б. Перепроверка подтверждает,
что живой сайт не читается (`nbki.ru/corp/bank/analitics/` — **404, 42 584 Б** тела-навигации;
`nbki.ru/analytics/` и `/services/analytics/` — **404, по ~169 КБ** SPA-заглушки;
`bki-okb.ru/corp/services/transmit/` — **HTTP 200, 2 165 Б**, текста после снятия тегов
**1 символ**, то есть та же пустая оболочка). 🟢 **Обойдено через Wayback с `id_`
и `--compressed`:**
`https://web.archive.org/web/20251208025950id_/https://nbki.ru/corp/bank/analitics/`
— **HTTP 200, 107 157 Б**, после снятия тегов 7 740 символов читаемого текста.
Без флага `--compressed` тот же запрос отдал 21 874 Б неразжатого gzip и выглядел как мусор —
**новый приём для базы: снимки Wayback надо брать с `--compressed`.**

**Что НБКИ реально предлагает (дословно со снятой страницы):**
- **«BI аналитика НБКИ»:** «Статистические данные из базы НБКИ за последние **13 месяцев**
  сгруппированы по разделам: кредитные заявки, выдача кредитов, портфельные характеристики,
  качество обслуживания обязательств (винтажи). Предоставляемая информация сформирована
  в графическом виде (диаграммы, таблицы) с применением различных срезов и фильтров,
  и ранжируется как по федеральным данным, так и по регионам кредитования, типам кредитов,
  возрастам заемщиков и т.п. **Доступ заказчиков к базовой версии предоставляется
  по запросу в НБКИ.**»
- **«Нестандартизированные отчеты»:** «НБКИ предоставляет различные отчеты и **выборки
  по запросам заказчиков** исходя из текущих потребностей с необходимой детализацией
  и периодичностью.»
- Стандартизированные отчёты: «Бенчмаркинг», «Бенчмаркинг.Взыскание», «Винтажный анализ»,
  **«Анализ долговой нагрузки частных заемщиков»**, «Поведенческий анализ заемщика после
  получения отказа», **«Модельная песочница»**.
- «Бенчмаркинг» содержит «более **2 000 переменных** в виде динамических рядов
  с 12-месячной ретроспективой»; сравнение идёт с «**деперсонализированного референтного
  списка кредиторов**».

🔴 **Опровержение сводки поиска.** Сводка `WebSearch` утверждала, что «НБКИ предоставляет
обезличенные выборки из своей базы или обогащает выборки клиента данными НБКИ». На снятой
странице слова «обезличен» **нет вовсе** (0 совпадений), равно как «исследовател» и
«агрегир». Деперсонализация в тексте относится к **списку кредиторов-контрагентов**,
а не к заёмщикам. То есть формулировка «обезличенные выборки для исследователей»
первоисточником **не подтверждается** — её нельзя вносить в файл.

**Ответ на вопрос участка.** Публичных агрегированных срезов у НБКИ **нет**: всё —
«по запросу заказчика», а форма заявки на сайте требует обязательных полей
**«Организация», «ИНН компании», «Код участника»**, то есть канал устроен как B2B
для кредиторов и страховщиков (перечень аудиторий на сайте: банки и МФИ, страховые,
поставщики ЖКУ и связи, лизинг, брокеры). Отдельного канала «исследователю /
университету» на сайте не заявлено. 🔴 Условия (цена, форма договора, что именно
отдают — агрегаты или микроданные) **НЕ ДОБЫТЫ**: их на публичных страницах нет.
По ОКБ не добыто ничего: сайт целиком SPA, снимок не снимался (бюджет).

🟡 **Рабочий вывод для темы 35:** данные БКИ для эталона калибровки бесполезны даже
при идеальном доступе — по той же причине, что ОДПФ и ВНДН. БКИ видит **платежи по
договору и просрочки**, а не решение «куда направить свободный поток»; вопроса о
сбережениях у БКИ нет по определению (это не их предмет). Ценность БКИ для FINPILOT
в другом — в валидации **распределения ставок и долговой нагрузки**, и здесь достаточно
публикуемых ЦБ агрегатов, а не доступа к бюро.
🟡 Публикационная серия ЦБ по данным БКИ (найденная добором темы 34-v2) этим прогоном
**не перепроверялась** — сошлись на неё как на закрывающий источник по агрегатам.

### ПЕРЕПРОВЕРКА Д5 С ПОИСКОМ — П5.5 остаток раздела 5

**П5.5.1 🟢 Объём выборки ВНДН — ЗАКРЫТ** (см. П5.2: 160 тыс. ДХ, широкомасштабная
волна 2022, первоисточник Хабаровскстат, HTTP 200).

**П5.5.2 🔴 «Flat maximum principle» в многокритериальном выборе — отрицательный
результат ПОДТВЕРЖДЁН, и теперь он объяснён.** Первый добор получил пустоту от OpenAlex
и записал это как «отрицательный результат поиска, не отсутствие литературы».
Перепроверка `WebSearch`-ом (`"flat maximum" principle multicriteria decision weights
insensitivity "multi-attribute" utility equal weights robustness`) дала **ту же пустоту
по термину** и одновременно объяснила её: в литературе по MCDM этот же эффект живёт
**под другими названиями** — «weight stability intervals», «weight sensitivity analysis»,
«scale dependence in weight-rate methods», «full-range weight sensitivity analysis».
Найденная релевантная работа — «Weight stability intervals for multi-criteria decision
analysis using the **weighted sum model**» (*Expert Systems with Applications*,
`sciencedirect.com/science/article/pii/S0957417425020792`) — 🟡 сниппет, первоисточник
не открыт (ScienceDirect). Это прямо про **WSM, то есть про нашу SAW**.
**Вывод:** термин «flat maximum» принадлежит психологии суждений (Дауэс, Лавстед,
Hogarth & Karelaia — см. П5.3.2), а не MCDM; искать его в MCDM бессмысленно, а искать
надо «weight stability interval». 🔴 Это меняет формулировку строки раздела 5: не
«литературы нет», а «литература есть под другим термином, и её надо добыть отдельной
темой».

**П5.5.3 🟡 RLMS «Citing the Data» — НЕ ДОБЫТО, дублировать не стали.**
Первый добор: `rlms-hse.cpc.unc.edu/citing-the-data` — 404. Условия RLMS добыты добором Д9
в UNC Dataverse; согласно указанию, повторно не проверялись. Расхождение между зеркалами
(HSE «register online and accept Data Use agreement» со сниппета против UNC «публичные
данные без application process») **остаётся неразрешённым**.

**П5.5.4 🔴 Kettle et al. 2016 — не пробовался** (бюджет ушёл на П5.1–П5.4). Остаётся
в статусе первого добора: Unpaywall `closed`, пять локаций в OpenAlex, все не-OA.

### ПЕРЕПРОВЕРКА Д5 С ПОИСКОМ — ИЗМЕНЕНИЯ ВЫВОДОВ ПОСЛЕ ПЕРЕПРОВЕРКИ С ПОИСКОМ

**Прямой ответ на главный вопрос: центральный вывод темы 35 УСТОЯЛ и УСИЛИЛСЯ.**
Источника данных, который позволил бы построить эталон «свободный поток → фактическое
распределение между долгами, резервом и целями», поиск **не нашёл** — и, что важнее,
нашёл причину, по которой его и не могло быть: **переменной «сколько внесено сверх
графика» не содержит ни одно из четырёх проверенных обследований — ОДПФ, ВНДН, PSID, SCF.**
До этой перепроверки вывод звучал как утверждение о российской статистике; теперь он
проверен на эталонных зарубежных инструментах и оказался утверждением о панельных
обследованиях домохозяйств в целом. Идея «калибровать веса по наблюдаемому поведению»
остаётся закрытой, и не только за отсутствием данных: она вредна (Gathergood et al.,
AER 2019 — Д.6) и неидентифицируема без канонизированной нормировки (Тофаллис — Д.3).

**ПОДТВЕРДИЛОСЬ (перепроверка не изменила):**
1. 🟢 Формулировка SCF `ahead of schedule / on schedule / behind schedule` существует
   дословно, задаётся **по каждому долгу** (8 блоков анкеты, 18 кодов переменных),
   и её можно брать в интерфейс FINPILOT как есть — П5.1(а).
2. 🟢 Покредитный блок ВНДН со ставкой, платежом, остатком, годом договора и целью —
   находка Д9 **подтверждена первоисточником** (Указания Росстата к НДН-2025, п. 133) — П5.2.
3. 🟢 Вопросов о досрочном погашении и о сумме сбережений в ВНДН **нет** — П5.2,
   машинная проверка по 523 КБ Указаний.
4. 🔴 Politis & Romano 1994 открытого доступа не имеет — подтверждено уже не только
   Unpaywall, но и **каталогом препринтов самого автора** (там нет работ до 1999) — П5.3.3.
5. 🔴 Dana & Dawes 2004 недоступен; `r.jina.ai` по SAGE и ScienceDirect — 403 Cloudflare.
   Граница канала `r.jina.ai`, зафиксированная в первом прогоне («не пробивает интерактивную
   капчу»), подтверждена трижды — П5.3.4, П5.3.6.

**ОПРОВЕРГНУТО или СУЩЕСТВЕННО ИСПРАВЛЕНО:**
1. 🔴 **Неявный подтекст плана «в SCF величина досрочного погашения есть» — НЕВЕРЕН.**
   SCF спрашивает только **направление** отклонения от графика; единственное продолжение —
   ожидаемый месяц/год погашения. Формулировок «extra payment», «more than the minimum»
   в кодбуке SCF 2022 **нет вовсе** (0 совпадений по 2,8 МБ). Суммы сверхграфикового
   взноса не наблюдает и SCF — П5.1(а).
2. 🔴 **В PSID вопроса `ahead of schedule` НЕТ.** 0 совпадений по кодбукам 2023 (3,5 МБ)
   и 2019 (5,7 МБ). PSID спрашивает отклонение от графика **только в сторону просрочки**
   (`A27a`, `A27b` «How many months are you behind?»). Ссылаться на «западные панели»
   как на носителя этой переменной нельзя — носитель ровно один, SCF — П5.1(б).
3. 🔴 **Числа Gathergood & Weber в разделе 5 файла требуют оговорки о версии.**
   Записано «12 % ДХ, £3 800» (из аннотации). Полностью прочитанный рабочий документ
   CFCM 12/04 (HTTP 200, 644 445 Б) даёт **14 % и £3 400**, плюс числа, которых в файле
   не было: **£600 напрасных процентов в год** в среднем и **£1 300 у 4 % выборки** — П5.3.1.
4. 🔴 **Реквизиты «Choupani & Mamdoohi 2017 (CEUS 68:78–88)» поиском НЕ подтверждаются.**
   Существуют TRP 17 (2016): 223–233 и TRR 2493 (2015). Работа 2017 года в CEUS
   в выдаче отсутствует — вероятна ошибка в ссылке плана — П5.3.4.
5. 🔴 **«Besharat et al. 2014» — две разные работы**, и содержательно нужная из них
   вышла в **2015** (Besharat, Varki & Craig, JCP 25: 311–316) — П5.3.7.
6. 🔴 **Сводка поиска про «обезличенные выборки НБКИ для исследователей» НЕ подтверждается
   первоисточником.** На снятой странице НБКИ слова «обезличен», «исследовател», «агрегир»
   отсутствуют; деперсонализация относится к **референтному списку кредиторов**. Канал
   устроен как B2B (обязательные «Организация», «ИНН», «Код участника») — П5.4.
7. 🔴 **Строка «flat maximum principle — литературы нет» неверна по формулировке.**
   Литература есть, но под терминами «weight stability intervals» / «weight sensitivity
   analysis»; нашлась работа прямо про **weighted sum model** (= наша SAW) — П5.5.2.
8. 🔴 **Объём выборки ВНДН больше не «со сниппета»:** 160 тыс. ДХ, широкомасштабная
   волна 2022, первоисточник Росстата (HTTP 200) — П5.2.
9. 🟡 **Blanchett, Kowara & Chen 2012:** реквизиты добыты с авторской страницы
   (RMJ 2(3), Fall: **7-18**, награда RIIA 2012), при этом автор **сам не выкладывает PDF**,
   а сводка поиска давала пагинацию «7–20» — расхождение записать как неразрешённое — П5.3.5.
10. 🟢 **Новое, чего в теме не было вовсе: PSID даёт готовый приём против отказов
    по сумме** — unfolding brackets (`W30a. Would they amount to $15,000 or more?`)
    при 6,42 % отказов по прямому вопросу о сумме счетов. Это применимо к анкете FINPILOT
    напрямую — П5.1(б).
11. 🔴 **Оговорка ВНДН, которой не было у Д9:** «Если домохозяйство имеет несколько
    задолженностей на покупку товаров и неотложные нужды, **указываются наиболее крупные
    из них**». Покредитный блок ВНДН усечён именно там, где долгов много — значит границу
    применимости Avalanche (6,7 % ДХ с ≥2 позициями) на ВНДН воспроизвести нельзя — П5.2.
12. 🟢 **Независимое подтверждение вывода Д3 в числах, на компенсаторных задачах** (а SAW —
    компенсаторная свёртка): Hogarth & Karelaia, UPF WP 974, добыт полным текстом (66 с.,
    HTTP 200, 430 728 Б), мета-анализ 255 исследований. В компенсаторных трёхпризнаковых
    средах равные веса дают **77 %** верных выборов против **68 %** у линейной модели,
    подогнанной под суждения человека, при теоретическом максимуме **81 %** — П5.3.2.
    🔴 Но это **не** «равные веса бьют оптимальную регрессию»: колонка LC — модель
    человека-судьи. Для темы 35 случай ровно нужный, потому что наши веса откалиброваны
    по согласию с экспертами.

### ПЕРЕПРОВЕРКА Д5 С ПОИСКОМ — честно про инструменты

`WebSearch` работал весь прогон — **17 вызовов**, отказа по бюджету не было ни раз.
Подагентов — **ноль** (участки оказались последовательно зависимыми: каждый следующий
адрес брался из выдачи предыдущего шага). Сырьё писалось в файл **шестью дописываниями
по ходу** (шапка → П5.1а → П5.1б → П5.2 → П5.3 → П5.4/П5.5 → финал), `Write` не применялся.

**Что решило дело — два канала, которых у Д5 не было:**
- 🟢 **Wayback с суффиксом `id_` + адрес из CDX API.** Так пробиты `psidonline.isr.umich.edu`
  (403 на живом сайте) и `nbki.ru` (SPA). 🔴 Два условия, без которых приём не работает:
  таймстамп берётся **из CDX**, а не придумывается (придуманный `web/2023id_/` дал
  ровно **1 048 576 Б** усечённого PDF), и запрос идёт **с `--compressed`** (без него
  снимок nbki.ru пришёл как 21 874 Б неразжатого gzip и выглядел мусором).
- 🟢 **`WebSearch` как искатель ЗЕРКАЛ, а не работ.** Именно этого не хватало Д5, и он
  это предсказал верно. Практические попадания: документация PSID на сайте Университета
  штата Орегон; рабочий документ Gathergood & Weber в серии CFCM Ноттингема (после того
  как SSRN дал 403, а ePrints — 404); Hogarth & Karelaia на `econ-papers.upf.edu`;
  машинно читаемый кодбук SCF на `federalreserve.gov` в виде plain text.

**Границы, замеренные заново:** `r.jina.ai` **жив** (не 401, как в Д5), но
ScienceDirect и SAGE отдают ему **403 Cloudflare «Just a moment…»** — три пробы, три раза.
Правило «большой размер ответа не значит успех» подтвердилось дважды: 43 369 Б «PDF»
с ScienceDirect оказались HTML-редиректом, 117 437 Б с сайта Blanchett — страницей 404.

### ПЕРЕПРОВЕРКА Д5 С ПОИСКОМ — одной фразой

Перепроверка с работающим поиском **не нашла источника, меняющего вывод темы 35, зато
нашла, почему его нет:** переменной «свободный поток → доли между долгом, резервом
и целями» не содержит ни ОДПФ, ни ВНДН, ни PSID, ни SCF, и «эталон» для калибровки весов
нельзя ни построить в РФ, ни импортировать; при этом сама перепроверка исправила
шесть числовых и библиографических записей файла и добыла три первоисточника,
считавшихся недоступными.

---

# ДОБОР Г5 (11.09.2026) — российские публикации и норма 353-ФЗ

Пункт Г5.6 очереди `docs/research/queue/GAP_QUEUE.md`. Пункт «кластеризация RLMS 2015–2019»
из этого же списка **уже закрыт** добором Д9.5 (первоисточник Рыжикова–Скуратова открыт
и разобран в `rf_household_finance_stats_v2_2026-09-10.md`) — здесь не дублируется.

## ДОБОР Г5 — Г5.6.1. Шульгин, Новак, Вихарев (2025) — полный текст добыт

Реквизиты подтверждены **Crossref API без ключа** (`api.crossref.org/works/10.31737/22212264_2025_3_78-111`,
HTTP 200, 10 513 байт): Шульгин, Новак, Вихарев, «DSGE-модель с тремя группами домохозяйств»,
*Journal of the New Economic Association* (Журнал НЭА), № 3(68), 2025, с. 78–111,
опубликовано 29.09.2025.

**Полный текст добыт прямым PDF** мимо сайта журнала:
`http://www.econorus.org/repec/journl/2025-68-78-111r.pdf` → `curl -sk --http1.1`,
**HTTP 200, 346 385 байт, `application/pdf`**, `pdftotext -layout` → 2 345 строк.
Аффилиация всех троих авторов, дословно с титула: **Волго-Вятское ГУ Банка России,
Нижний Новгород** — то есть это работа сотрудников ЦБ, а не сторонних академиков.

### Метод разбиения домохозяйств (дословно, п. 2.1)

Калибровка «проведена на данных **RLMS-HSE по домохозяйствам за 2014–2020 гг.** и данных
Росстата за 2014–2021 гг.». Три группы по Kaplan, Violante, Weidner (2014): **n** — есть
ликвидные активы; **w** — есть неликвидные активы (недвижимость) как потенциальный залог;
**p** — нет неликвидных активов либо их стоимость сопоставима со стоимостью кредита.

🔴 **Главная находка этого пункта — формулировка вопроса RLMS, по которому авторы относят
домохозяйство к группе n. Дословно:**

> «Представьте себе не очень приятную картину: все члены вашей семьи лишились всех
> источников дохода. Как долго ваша семья сможет материально жить так же, как вы живете
> сейчас, т.е. не уменьшая расходов, только за счет денежных сбережений, ничего
> не продавая из имущества?»

К группе n относят ответивших **«Несколько месяцев»** или **«Полгода и больше»**.
Комментарий авторов дословно: «Это означает, что у домохозяйства есть ликвидные сбережения,
позволяющие сглаживать потребление во времени.»

🔴 **Это прямой российский аналог вопроса о резерве на непредвиденное — в микроданных,
с панелью и в порядковой шкале «сколько месяцев продержитесь».** Наш показатель «резерв
в месяцах расходов» имеет в RLMS-HSE операционализированный близнец, причём с оговоркой
«не уменьшая расходов» — то есть без поведенческой адаптации, ровно как считаем мы.
Ограничение: шкала грубая (категории, а не месяцы) и меряет **фактическую способность**,
а не **желаемый размер** резерва; медиана желаемого резерва 2,50 месяца (установлена ранее)
этим не подтверждается и не опровергается — это разные величины. ⚠️ Сама формулировка взята
из статьи, **анкету RLMS-HSE в этом доборе я не открывал**; номер вопроса неизвестен.

### Доли групп и таблица 1 (дословно)

Доли усреднены за 2014–2020 гг. по RLMS-HSE: **группа n — 0,247; группа w — 0,359;
группа p — 0,394**.

Таблица 1 «Ключевые показатели межгрупповой гетерогенности домохозяйств в **2020 г.**»,
дословно:

| Показатель | Группа n | Группа w | Группа p |
|---|---:|---:|---:|
| Число домохозяйств в группе, человек | 1 133 | 1 548 | 1 745 |
| Доля в выборке | 0,25 | 0,36 | 0,39 |
| Доля текущего потребления в доходах | 0,35 | 0,41 | 0,44 |
| Доля общего потребления в доходах | 0,73 | 0,81 | 0,78 |
| Текущее потребление, руб. | 8 897 | 8 271 | 7 609 |
| Общее потребление, руб. | 18 398 | 16 844 | 14 099 |

Источник строкой под таблицей: «расчеты авторов на основе данных RLMS-HSE».
Сноска 8, дословно: «При расчетах долей из выборки исключаются наблюдения, в которых
расходы домохозяйств на текущее потребление превышают доход более чем в два раза
(Khvostova, Larin, Novak, 2016)».

### ⚠️ Сопоставление с типологией Рыжиковой–Скуратовой (добор Д9.5) — расхождение

| Источник | Данные | «Благополучная» группа | «Стеснённая» группа |
|---|---|---:|---:|
| Рыжикова–Скуратова 2023 (k-means по доле еды и сбережениям) | RLMS 2015–2019 | non-HtM **3,8 %** | HtM 48,7 % |
| Шульгин и др. 2025 (по ликвидным/неликвидным активам) | RLMS 2014–2020 | группа n **24,7 %** | группа p 39,4 % |

🔴 **Разница шестикратная (3,8 % против 24,7 %) на почти одних и тех же данных.**
Это не ошибка ни у кого из них, а следствие разных определений: Рыжикова–Скуратова режут
по **факту наличия сбережений и доле еды в расходах** (жёсткий критерий), Шульгин и др. —
по **самооценке «продержимся несколько месяцев»** (мягкий, самоотчёт). Практический вывод
для калибровки: **доля «домохозяйств с подушкой» в России не определена — она равна
от 4 % до 25 % в зависимости от того, спрашиваем мы про факт или про самооценку.**
Любое наше число по этому поводу обязано называть, какое из двух определений взято.
Записывать в канон ни одно из двух нельзя.

### Прочее из работы, что стоит знать

Дословно: «Практика использования недвижимости в качестве залога при кредитовании
физических лиц слабо распространена в России (за исключением ипотеки)»; учёт недвижимости
в модели нужен «в большей степени для обеспечения процикличности кредитования,
а не для отражения фактического механизма кредитования в России». Индекс Джини
по трёхгрупповому разбиению коррелирует с фактическим «около 0,9».

## ДОБОР Г5 — Г5.6.2. «Вопросы экономики» / «Экономическая социология» — частично

🟡 Прицельный WebSearch дал одну прямо релевантную работу: **Мамедли М., Синяков А.,
«Финансы домохозяйств в России: шоки дохода и сглаживание потребления»** (карточка HSE,
https://publications.hse.ru/articles/219829731). Из сводки выдачи, 🔴 **полный текст
не открывался**: домохозяйства сглаживают **около 50 % шоков дохода**; сглаживание ниже
у сельских жителей, у домохозяйств с более высокой долговой нагрузкой на момент кризиса
и у низкодоходных; российские домохозяйства неохотно тратят накопленные сбережения
и неохотно наращивают долг в ответ на изменение дохода — исключение составили
домохозяйства с высокой долговой нагрузкой в кризис 2014 г.

Попутно зафиксированы адреса рабочих материалов ЦБ по теме (не открывались):
`https://www.cbr.ru/content/document/file/16736/wps_5.pdf` («Индикаторы долговой нагрузки»,
серия докладов об экономических исследованиях) и
`https://www.cbr.ru/Content/Document/File/23500/analytic_note_170928.pdf`
(«Потребительское кредитование в России: перспективы и риски», 28.09.2017).
Диссертация «Стратегии долгового поведения населения в современной России»
(dissercat) — не открывалась.

🔴 Систематического прохода по архивам «Вопросов экономики» и «Экономической социологии»
в этом доборе **не было** — один поисковый запрос, а не разбор журналов. Считать пункт
закрытым нельзя.

## ДОБОР Г5 — Г5.6.3. 🟢 Пороги 200× и 1000×: дословная норма и число Росстата

### Норма — ст. 9 ч. 1.1 353-ФЗ, дословно

Текст добыт `curl -s "https://r.jina.ai/https://www.consultant.ru/document/cons_doc_LAW_155986/8010678fe385f06b25a48465610d110690a6d609/"`
→ **HTTP 200, 12 757 байт** (прямой `curl` к consultant.ru антибот не пропускает).
Пометка в тексте: «(часть 1.1 введена Федеральным законом от **22.06.2024 N 151-ФЗ**)».

> «1.1. Применение переменных процентных ставок в порядке, установленном настоящим
> Федеральным законом, допускается только к следующим договорам:
> 1) кредитному договору, договору займа, которые заключены с физическим лицом в целях,
> не связанных с осуществлением им предпринимательской деятельности, и обязательства
> заемщика по которым обеспечены ипотекой, срок возврата кредита (займа) по которым
> не превышает на дату заключения соответствующего договора **двадцати лет** и сумма кредита
> (займа) по которым **превышает увеличенную в двести раз и не превышает увеличенную
> в тысячу раз** величину среднемесячной номинальной начисленной заработной платы работников
> по полному кругу организаций в целом по экономике Российской Федерации в среднем
> за календарный год, предшествующий году выдачи кредита (займа), опубликованную
> на официальном сайте [Росстата] …, а при отсутствии такой информации — величину
> среднемесячной номинальной начисленной заработной платы работников по полному кругу
> организаций в целом по экономике Российской Федерации в среднем за двенадцать месяцев
> на основе последних данных, опубликованных на официальном сайте уполномоченного органа;
> 2) кредитному договору, договору займа, которые заключены с физическим лицом …
> и обязательства заемщика по которым обеспечены ипотекой, **и договору потребительского
> кредита (займа)**, если сумма кредита (займа) по таким договорам **превышает увеличенную
> в тысячу раз** величину среднемесячной номинальной начисленной заработной платы …»

🔴 Точная механика, которую легко прочитать неверно: базой служит **среднемесячная
номинальная начисленная зарплата по полному кругу организаций в целом по экономике РФ
за календарный год, ПРЕДШЕСТВУЮЩИЙ году выдачи** кредита.

### Число Росстата и расчёт порогов

**Среднемесячная начисленная заработная плата в РФ за 2025 год — 100 360 ₽** (+13,5 %
к 2024 г.). 🔴 Провенанс: **сводка выдачи WebSearch по публикациям «Коммерсанта» и ТАСС
со ссылкой на Росстат**; прямой файл Росстата с этим годовым числом в доборе не открыт.
Косвенное подтверждение порядка величины — справочная таблица КонсультантПлюс по данным
Росстата (`r.jina.ai`, HTTP 200, 15 630 байт): помесячный ряд 2025 г. лежит в диапазоне
**88 981 – 139 727 ₽** (декабрь — 139 727), ряд 2024 г. — 75 034 – 128 665 ₽,
ряд 2023 г. — 63 260 – 103 815 ₽. Среднее по двенадцати месяцам 2025 г. согласуется
с 100 тыс. ₽.

⚠️ Отдельно замерено и отброшено: PDF «Срочная информация, 29 апреля 2026, ЗАРАБОТНАЯ ПЛАТА
ОРГАНИЗАЦИЙ» (`https://37.rosstat.gov.ru/storage/mediabank/zar_0426_2_2.pdf`,
`curl`, HTTP 200, 437 218 байт, 3 страницы) даёт за 2025 г. **57 122,0 ₽** — это
**Ивановская область**, а не РФ. Такие региональные файлы Росстата легко принять
за федеральные: они лежат по одинаковым путям и одинаково называются.

**Пороги для кредитов, выдаваемых в 2026 году** (база — 2025 г., 100 360 ₽), мой расчёт:

| Порог | Формула | Значение |
|---|---|---:|
| 200× (нижняя граница «ипотечного окна») | 100 360 × 200 | **20 072 000 ₽** |
| 1000× (верхняя граница окна / нижняя для п. 2) | 100 360 × 1 000 | **100 360 000 ₽** |

🔴 **Что это значит для FINPILOT.** Плавающая ставка по ипотеке физлица законна только
в коридоре примерно **20,1 – 100,4 млн ₽ и на срок до 20 лет**; по потребительскому кредиту —
только свыше **≈100,4 млн ₽**. То есть **для всей нашей целевой аудитории плавающих ставок
по закону быть не может**: обычная ипотека 3–15 млн ₽ ниже нижнего порога, потребкредиты —
на два порядка ниже. Допущение модели «ставка по кредиту фиксирована на весь срок»
не упрощение, а **воспроизведение нормы права** — и это сильный аргумент в пользу
текущего устройства прогноза. ⚠️ Пороги пересчитываются каждый год: база меняется
с публикацией годовой зарплаты Росстата, значит число в коде/доках должно быть
параметром с годом, а не константой. При росте зарплаты ~13 % в год порог 200×
в 2027 г. будет уже около 22,7 млн ₽.

---

## ДОБОР Г8 — Г8.2 Правило 50/30/20: первоисточник Warren & Warren Tyagi (11.09.2026)

**Реквизиты:** Elizabeth Warren, Amelia Warren Tyagi. *All Your Worth: The Ultimate Lifetime Money
Plan*. New York: Free Press, 2005. У авторов правило называется **«The Balanced Money Formula»**;
«50/30/20» в тексте встречается как второе название («Is it ever all right to deviate from the
50/30/20 formula?»).

**Канал и 🔴 происхождение текста (читать до цитат).** Полный текст книги получен со страницы
`dokumen.pub/all-your-worth-the-ultimate-lifetime-money-plan-elizabeth-warrenn-amelia-warren-tyagi.html`
(curl, HTTP 200, 531 952 байта HTML, после снятия разметки ~487 000 символов). В тексте 67 водяных
знаков `OceanofPDF.com`: это **неофициальная электронная копия**, не издательский файл.
Следствия: (1) **номеров страниц нет**, ссылки ниже — на главу и раздел; (2) внутренние ссылки
самой книги («Step Three, which starts on page 70», «list of Steal-from-Tomorrow debt on page 137»)
дают привязку к пагинации издания; (3) сверки с бумажным изданием не было, но текст связный,
главы и рабочие листы (Worksheets 3, 9) на месте, и формула совпадает с пересказами (Shortform,
Ironclad Finances — **сниппеты выдачи**, не открывались). Выдержек с сайта Гарварда искать не
пришлось.

### 1. Формулировка дословно (раздел «The Balanced Money Formula», гл. 1 / Step One)

> «So what's the formula? Here it is: **Must-Haves: 50% · Wants: 30% · Savings: 20%**»
> «Testing yourself against the Balanced Money Formula is a little like checking your cholesterol
> against the recommended levels. It helps you flag when something is wrong»

База — **доход после налогов**: в рабочем листе дохода отдельно оговорено, что взносы в пенсионный
план из зарплаты «aren't part of your take-home paycheck, but they build toward your lifetime Savings,
so we want to be sure to count them now» — то есть они возвращаются в базу и попадают в Savings.

🔴 **50 % — потолок, а не норма расхода:** «We're saying you should limit the hard-core commitments
to **at most** half of your income.»

### 2. Что входит в каждую долю — и куда идут долги

**Must-Haves (не «needs»)**, дословно:
> «A place to live, utilities, medical care, insurance, transportation, and **minimum payments on your
> can't-escape legal obligations**. This is the core, the amount that you must pay every month, in good
> times and in bad.»
Три критерия отбора: «1. Could you live in safety and dignity without this purchase (at least for a
while)? 2. If you lost your job, would you keep spending money on this? 3. Could you live without
this purchase for six months?» Продукты питания и одежда входят только в базовой части (разбор
на примере одежды: «you "must have" clothes… But the odds are you have a closet fu[ll]»).
🔴 Пересказ «needs / wants / savings» **неточен**: у авторов «Must-Haves» — узкая категория
«платишь при любых обстоятельствах», а не «потребности» вообще.

**Wants** — «a totally open field», всё остальное; список примеров включает кабельное ТВ, уборку,
стрижку, подарки, спортивный лагерь, благотворительный взнос.

**Savings — 🔴 включает погашение долга**, дословно:
> «The Savings category actually includes two kinds of money. The first is … money for a retirement
> account or a regular bank account. **The second kind of Savings is debt repayment.** … Every time you
> pay down principal on a loan you are building your Savings for the future.»

**Итоговая раскладка долговых платежей у первоисточника:**

| Что | Куда |
|---|---|
| Минимальные обязательные платежи (ипотека, авто, прочие «can't-escape legal obligations») | **Must-Haves (50 %)** |
| Любые платежи **сверх минимума**, т.е. досрочное погашение | **Savings (20 %)** |
| Рост остатка по кредитной карте | **вычитается** из Savings (Worksheet 3, Part 2: баланс $900 → $1 500 за год = −$50/мес) |
| Рефинансирование карты в home equity | **не** Savings: «You still owe the money… So your debt is still the same» |

Чтение: 20 % — это **весь** поток на будущее, и досрочное погашение с резервом и целями конкурируют
внутри одной доли. Это ровно та постановка, которую решает FINPILOT, — у авторов она не
оптимизируется, а задаётся: при наличии «Steal-from-Tomorrow» долга весь 20 % идёт на долг
(«Earmark 20% for Debt Payment … Just 20% of each and every paycheck for paying off your debts»,
Step Five).
«Steal-from-Tomorrow debt» — кредитные карты и подобные долги; ипотека, автокредит и студенческие
займы в эту группу **не входят** («You took these loans so you could…» — долги под актив).

### 3. На чём основано — эмпирика или эвристика

Авторы дают **три обоснования только для 50 %** (раздел «Why 50% for Must-Haves?»):
1. «It is sustainable» — довод без чисел.
2. «It is safe» — единственный количественный довод: «In most states, unemployment insurance covers
   roughly 50% of your previous salary… most disability policies would cover about half of your
   salary», плюс «if you are married… you could get by on only one paycheck for a while».
3. «It has been tested over time» — «that number worked for Americans for a long time. A generation
   or so ago, most families spent half (or less) of their incomes on the Must-Haves… We go over the
   details in *The Two-Income Trap*». То есть ссылка на их же книгу 2003 г., а не на расчёт в этой.
**Для 30 % обоснования нет вовсе**: «Why 30% for Wants? Because you deserve some space where you can
relax and enjoy yourself!» Раздела «Why 20%» в тексте нет (поиск по строке — 0 совпадений);
20 % получается как остаток: «Since your Must-Haves and Wants claim only 80%… you have 20% left over».
В благодарностях: исследователи Consumer Bankruptcy Project «helped develop the data…, which provided
important empirical underpinning for this work» — но в самой книге **нет таблицы, выборки или
расчёта**, из которых следовали бы доли 50/30/20.

🔴 **Вывод: 50/30/20 — эвристика с одним количественным ориентиром** (пособие по безработице ≈ 50 %
заработка в США 2005 г.) и отсылкой к исторической структуре расходов американских семей. Как
«норматив, выведенный из данных» его подавать нельзя. Перенос в РФ требует отдельного
обоснования: опорный довод («пособие ≈ половина зарплаты») к российскому пособию по безработице
не применим — проверять отдельно, в этом доборе не проверялось.

### 4. Оговорки самих авторов

- Отклонение допустимо: «If your income dips… nearly all your money would go to Must-Haves, while you
  would cut back on Wants and Savings until things got back to normal»; постоянный сдвиг — у
  самозанятого («put even more into Savings») или у пенсионеров без ипотеки («go light on the
  Must-Haves… heavier on the Wants»). Итоговая формулировка: «**the right place for most people most
  of the time**».
- Порог кризиса: «If you owe more than a year's income in Steal-from-Tomorrow debt or if your minimum
  monthly payments claim significantly more than 20% of your income, then you may be in need of some
  Financial CPR» — раздел о банкротстве в конце книги.
- Шкала «Monthly Savings Score»: «20% +: Super Big Saver», «12–20%: Strong Sav[er]» — то есть 20 % —
  верх шкалы, а не минимум.

### 5. 🔴 Попутная находка, прямо про avalanche/snowball

Первоисточник 50/30/20 **сам предписывает порядок погашения — и это не avalanche**. Step Five,
раздел «Pay the Debts That Bother You Most», дословно:
> «What should you pay first? Whatever you want. … If you owe any back-payments on your rent or
> mortgage, pay those first. … if you owe back-payments on your car or child support, pay those next.
> … But once those are covered, it really is up to you whether Visa comes before MasterCard… Pay the
> debt that bothers you most. … Would it feel good to get just one thing crossed off? If so, start by
> paying off the smallest debt. … **So don't get too caught up in comparing interest rates.** …
> it just doesn't matter very much which debt you pay off first.»
Механика у них — «снежный ком» в чистом виде: «Tackle Your Debts One at a Time… keep making the bare
minimum monthly payments on your other debts… The amount that you save each month on minimum monthly
payments will be plowed right back into paying off the other debts».
Чтение для продукта: если FINPILOT ссылается на 50/30/20 как на ориентир, он ссылается на
источник, который **явно отвергает сортировку по ставке** внутри группы потребительских долгов.
Приоритет у авторов — не ставка, а **последствия неплатежа** (жильё → авто/алименты → остальное).
Это не доказательство (в книге нет данных), но расхождение с каноном нужно знать при цитировании.

**Статус Г8.2: 🟢 добыт** (полный текст, неофициальная копия без пагинации — см. оговорку выше).

---

# ДОБОР Г30.1 — Exa (16.09.2026)

**Состояние каналов (свои замеры 16.09.2026):** `mcp__exa__web_search_exa` — работает;
`mcp__exa__web_fetch_exa` — работает, но **на ScienceDirect отдал `CRAWL_LIVECRAWL_TIMEOUT`**
(то есть издатель не пробит и этим каналом — замер, а не предположение). Wayback — **HTTP 302**.
OpenAlex, Unpaywall — HTTP 200. `curl -skL` по `acrwebsite.org/volumes/v42/acr_v42_17515.pdf` —
**HTTP 404, 172 345 байт HTML** (очередной случай «большой размер тела при отказе», как и
зафиксировано в П5.3.4/П5.3.5).

Взяты пункты, остававшиеся открытыми по последнему упоминанию: П5.3.3–П5.3.7. Закрытое ранее
(ВНДН, КОУЖ, PSID-кодбуки, объём выборки ВНДН, пороги 200×/1000×, 50/30/20, Шульгин и др.)
не переоткрывалось.

## Г30.1-17. 🔴 Besharat, Varki & Craig (2015) — ДОБЫТ ФАКТИЧЕСКИЙ МАТЕРИАЛ ТРЁХ ЭКСПЕРИМЕНТОВ (было: «сниппет, первоисточник не открыт»)

Было (П5.3.7): «НЕ ДОБЫТ… содержательно интересна та, которая **2015**, а не 2014… 🟡 это сниппет,
первоисточник не открыт».

Реквизиты подтверждены по карточке репозитория Университета Кентукки
(`https://scholars.uky.edu/en/publications/keeping-consumers-in-the-red-hedonic-debt-prioritization-within-m/`,
через Exa 16.09.2026), дословно: **Journal of Consumer Psychology, том 25, выпуск 2, с. 311–316,
6 страниц, DOI 10.1016/j.jcps.2014.08.005, State: Published — 2015.** То есть правка П5.3.7
(«год 2015, а не 2014») подтверждена официальной карточкой.

**Через Exa добыто тело статьи — дословно.**

Постановка и главный эффект:
> «we demonstrate that **when debt is incurred for a hedonic purchase (as opposed to a utilitarian
> purchase) and it is realized in the distant past (as opposed to the proximal past), customers with
> multiple credit card debts are more likely to reduce the NUMBER of credit card debts rather than
> decrease the TOTAL COST of debt across all accounts**, thus amplifying the effects reported by
> Amar et al. (2011). … For example, **between a $300 loan with a 6% interest rate and a $3000 loan
> with a 12% interest rate, a person would pay off the $300 loan faster if it were incurred for a
> hedonic purchase compared to a utilitarian purchase.**»

🔴 **Числа эксперимента 2 (то, чего не было в файле вовсе) — дословно:**
> «An ANOVA was performed with the proportion of smaller debt repaid as the dependent variable and
> debt type, timing, and APR as the independent factors. The three-way interaction was significant
> (**F(1, 272) = 4.56, p < .05**) revealing that the interaction between debt type and timing was
> dependent on whether the APR was 12% or 18%. … **when APR was 18%** … **irrespective of proximal
> past (M hedonic-18% = .54 vs. M utilitarian-18% = .49; F(1, 272) = 1.09, p > .10) or distant past
> timing (M hedonic-18% = .47 vs. M utilitarian-18% = .48) — individuals allocated most of their
> money towards the smaller debt, regardless of the debt nature.** However, **when the smaller debt
> APR was 12%**, the main effect of debt type (**F(1, 272) = 22.20**), debt timing
> (**F(1, 272) = 5.36**), and the interaction (**F(1, 272) = 12.63**) were significant …
> **M hedonic-12% = .45 vs. M utilitarian-12% = .31** (проксимальное прошлое) и
> **M hedonic-12% = .59 vs. M utilitarian-12% = .27** (дальнее прошлое).»

Выводы авторов — дословно:
> «Experiment 1a shows that consumers prefer to repay hedonic debt faster than utilitarian debt…
> Experiment 1b demonstrates that **even in the presence of cost information and real financial
> incentives, participants still prioritize hedonic, low APR debts.** Although the decreased
> enjoyment of the hedonic purchase leads consumers to reduce the hedonic debt faster when it has
> low APR, **consumers act rationally when the interest rate is high regardless of the type of
> debt.**»
> «**The temptation to pay off past, hedonic debts may override optimal allocation intentions and
> keep debtors in debt longer than necessary.**»

Выборка (дословный фрагмент описания эксперимента 2): «…**seventeen mTurk workers participated**…
SD = 6.73; **151 men**; **M credit cards = 5.22**; 37 responses were excluded…» (число участников в
выдаче обрезано слева — привожу как есть, не достраиваю).

🔴 **Что это даёт продукту — важная и неудобная деталь для Avalanche-фильтра.** (1) Отклонение от
оптимального порядка погашения **не универсально: при высокой ставке (18 %) тип долга перестаёт
влиять — люди и так гасят меньший остаток**; эффект «гедонического» долга проявляется на **умеренной
ставке (12 %)**. (2) 🔴 **Сообщение полной стоимости долга и денежный стимул НЕ устранили
искажение** (эксперимент 1b) — это прямой довод против того, что достаточно «показать переплату»,
и в пользу того, что рекомендация должна быть действием, а не информированием. Именно этот пункт
раньше держался у нас на пересказе. (3) Механизм — ожидаемое удовольствие от покупки, а не
финансовая логика; значит объяснение пользователю, почему Avalanche выгоднее, должно бить не
в арифметику, а в этот мотив.

## Г30.1-18. Dana & Dawes 2004 — ДОБЫТ (в этом файле значился «НЕ ДОБЫТ»)

Было (П5.3.6): «НЕ ДОБЫТ… Wayback 404, r.jina.ai по SAGE — 403 (Cloudflare)… совпадает с вердиктом
Unpaywall (`closed`)».

**Полный текст остаётся закрытым, но абстракт с числовыми порогами добыт дословно и сверен по трём
независимым площадкам** (SAGE, ERIC `EJ727514`, RePEc `sae:jedbes:v:29:y:2004:i:3:p:317-331`) —
через Exa 16.09.2026. Подробности и цитата — в соседнем файле темы,
`approach_validity_2026-09-10.md`, блок **Г30.1-3** (чтобы не дублировать материал между файлами).

Короткое существо для этого файла: **при adjusted R < .6 корреляционные веса превосходят
регрессионные даже при 100 наблюдениях на предиктор; при adjusted R < .4 единичные веса
превосходят все методы; регрессия выигрывала только при adjusted R² > .9.** Для калибровки весов
нашей модели это означает: **эталон для сравнения — не «подогнанные веса», а равные и
корреляционные**, и при нашем объёме данных подгонка весов не окупается.

## Г30.1-19. Politis & Romano 1994, Blanchett et al. 2012, Choupani & Mamdoohi — перепроверены, статус НЕ изменился

Все три прогнаны через Exa 16.09.2026; ни один не открылся. Это **подтверждённые отрицательные
результаты**, а не непроверенные пункты.

- **Politis & Romano 1994 «The Stationary Bootstrap», JASA 89(428): 1303–1313** — Exa-поиск даёт те
  же три адреса (Taylor & Francis abs, JSTOR 2290993, агрегаторы); открытой копии нет. Совпадает с
  прошлым замером: автор сам работу не выкладывает, каталог препринтов начинается с 1999 г.
  §3.3(б) остаётся на сводке.
- **Blanchett, Kowara & Chen 2012, Retirement Management Journal 2(3): 7–18** — журнальной копии
  нет; расхождение пагинации «7–18» (страница автора) против «7–20» (сводка поиска) остаётся
  неразрешённым, в файле писать как неподтверждённое.
- **Choupani & Mamdoohi, Transportation Research Procedia 17 (2016): 223–233 (gold OA)** — 🔴
  **`mcp__exa__web_fetch_exa` по ScienceDirect вернул `CRAWL_LIVECRAWL_TIMEOUT`**, то есть и Exa
  этот PDF не берёт. Ранее: `r.jina.ai` — 403 Cloudflare, Wayback — HTML-редирект вместо PDF.
  Парадокс сохраняется: статья юридически открыта (CC-лицензия), фактически недоступна ни одним
  из четырёх каналов. Цитата про округление в ре-сэмплинге остаётся со сводки.

## ИТОГ Г30.1 — calibration_ground_truth

| Пункт | Был статус | Стал | Чем взят |
|---|---|---|---|
| Besharat et al. — какая из двух работ и её содержание | НЕ ДОБЫТ, реквизиты под вопросом, только сниппет | 🔴 **ДОБЫТО**: год 2015 подтверждён карточкой UKY, добыты три эксперимента с F-статистиками и средними | Exa (тело статьи в индексе) + репозиторий Университета Кентукки |
| Dana & Dawes 2004 | НЕ ДОБЫТ | **частично добыт** — абстракт с порогами дословно, тремя совпадающими копиями | Exa → SAGE + ERIC + RePEc (материал записан в `approach_validity`, Г30.1-3) |
| Politis & Romano 1994 | НЕ ДОБЫТ | **не добыт — подтверждено закрытым** | Exa: открытых копий нет |
| Blanchett, Kowara & Chen 2012 | НЕ ДОБЫТ | **не добыт — подтверждено**; расхождение пагинации не разрешено | Exa |
| Choupani & Mamdoohi (TRP 2016, gold OA) | НЕ ДОБЫТ (r.jina.ai 403, Wayback — HTML) | **не добыт**; 🔴 новый замер: Exa по ScienceDirect — `CRAWL_LIVECRAWL_TIMEOUT` | Exa |
| ВНДН: регламент доступа к микроданным | НЕ ДОБЫТ | **не переоткрывался** (вне списка Г30.1, путь через зеркало tochno.st уже зафиксирован) | — |
| ОКБ (SPA-сайт) | не добыто ничего | **не переоткрывался** (бюджет) | — |
| RLMS «Citing the Data» | НЕ ДОБЫТО, дублировать не стали | **не переоткрывался** | — |

**Главное число по файлу `calibration_ground_truth`: из 5 проверенных пунктов «не добыто» Exa
перевела в «добыто»/«частично добыто» — 2** (Besharat 2015 — полностью по существу, Dana & Dawes —
абстракт с числами). Три (Politis & Romano, Blanchett, Choupani) подтверждены как закрытые всеми
доступными каналами, включая Exa. 🔴 **Отдельный результат батча: издательский ScienceDirect Exa
НЕ пробивает** (`CRAWL_LIVECRAWL_TIMEOUT`) — в отличие от репозиториев и агрегаторов, где она
работает; это граница канала, которую стоит помнить в остальных подбатчах Г30.

---

## ДОБОР Г31.2 — прокси (16.09.2026)

**Каналы на начало работы (парный замер):** `r.jina.ai` **без UA** → `www.monarchmoney.com/pricing`
**HTTP 200, 5 509 байт** содержимого; тот же адрес через прокси **с UA Chrome/127** → **HTTP 403,
5 743 байта** `Just a moment...`. Ошибка вызова прокси с UA подтверждена. Exa — 🟢;
Wayback **replay** — 🟢; Unpaywall и Crossref — 🟢 (200).

### Г31.2-7. 🟡 Choupani & Mamdoohi 2016 (TRP 17: 223–233, gold OA) — АБСТРАКТ ДОБЫТ; статус меняется с «не добыт ничем» на «частично»

**Прежний статус** (§Д.4.2, таблица П5.3.4 и Г30.1-19): «`r.jina.ai` — 403 Cloudflare, Wayback —
HTML-редирект вместо PDF, `mcp__exa__web_fetch_exa` по ScienceDirect — `CRAWL_LIVECRAWL_TIMEOUT`.
Парадокс: статья юридически открыта (CC), фактически недоступна ни одним из четырёх каналов».

**Реквизиты уточнены через Crossref (HTTP 200):** Choupani A.-A., Mamdoohi A.R. **«Population
Synthesis Using Iterative Proportional Fitting (IPF): A Review and Future Research»**,
*Transportation Research Procedia* **17** (2016) **223–233**, **DOI 10.1016/j.trpro.2016.11.078**,
pii **S2352146516306925**. Unpaywall (200): `is_oa: true`, `oa_status: **gold**`, единственная
OA-локация — `sciencedirect.com/science/article/pii/S2352146516306925/pdf`, host_type `publisher`.

**Каналы 16.09.2026:**

| Канал | Адрес | Код | Размер | Итог |
|---|---|---|---|---|
| `r.jina.ai` **без UA** | `…/S2352146516306925/pdf` | 200 у прокси | 113 054 б | тело — оболочка `Just a moment...` + `Target URL returned error 403`; 🔴 **без UA результат тот же — не наша ошибка вызова** |
| `r.jina.ai` **без UA** | `…/pii/S0895717708002860` (Wang & Luo, для контроля) | 200 | 112 999 б | та же оболочка Cloudflare. **ScienceDirect закрыт для прокси как класс** |
| Wayback replay | `web/2018/…/S2352146516306925/pdf` | **200** | 46 603 б **HTML** | снимок **05.06.2022 05:37:21 UTC** — страница-пересылка Elsevier «Preparing your download… Request ID: 71668e503fee90b5», PDF в архив не попал. Подтверждает прежнюю запись «HTML вместо PDF» |
| Wayback replay | `web/2019/…/pii/S2352146516306925` (страница статьи, без `/pdf`) | **200** | 92 226 б | 🟢 **абстракт целиком** |

#### Первичный материал — абстракт дословно (Wayback, страница статьи)

> «Activity-Based travel demand modeling requires the detailed socioeconomic data of the study area
> population. Since the collection of such detailed data for the whole population is too expensive,
> if not infeasible, population synthesis has been proposed to predict the data and produce them
> synthetically based on a sample. This much cheaper alternative for forecasting population
> characteristics is based on iterative proportional fitting (IPF)… This paper seeks to critically
> review the state of the art of IPF, classify the peer-reviewed literature, investigate the major
> problems of IPF, and identify gaps for future research… **Our review shows that integer conversion
> and zero-cell are among the most important problems necessitating empirical investigation.
> Unbiased tabular (controlled) rounding methods should be developed to integerize the fractional
> numbers estimated by IPF for the frequency of household types. Zero-cell problem, although already
> dealt with, still lacks unbiased solutions. Simulation-based synthesis can help to avoid zero-cell
> problem while it has many other advantages.**»
> Ключевые слова: «population synthesis · iterative proportional fitting (IPF) · integer conversion ·
> zero-cell problem · validation framework». Рецензирование: «Peer-review under responsibility of
> the Department of Civil Engineering, Indian Institute of Technology Bombay», © 2016 The Author(s),
> Elsevier B.V.

#### Что это меняет для участка 2 (синтетические популяции)

1. 🔴 **Тезис про округление больше не держится на сниппете.** Раньше цитата о «marginal
   distributions-controlled rounding» была снята с поисковой сводки и приписана работе 2017 г.
   Теперь **сами авторы в абстракте 2016 г.** говорят: «**Unbiased tabular (controlled) rounding
   methods should be developed** to integerize the fractional numbers estimated by IPF» — то есть
   на 2016 г. несмещённого метода округления, по их обзору, **не существует**, это открытая
   проблема, а не готовый рецепт. Нашу формулировку в §участок 2 надо привести к этому: целочисление
   после IPF — известная нерешённая проблема, а не деталь реализации.
2. 🔴 **Вторая проблема, которой у нас не было вовсе: zero-cell.** «Zero-cell problem, although
   already dealt with, still lacks unbiased solutions». Для наших 12 000 портретов это прямой риск:
   комбинации признаков, отсутствующие в выборке-основе, IPF воспроизвести не может.
3. 🟢 **Авторская рекомендация в нашу сторону:** «**Simulation-based synthesis can help to avoid
   zero-cell problem** while it has many other advantages» — довод в пользу симуляционного
   порождения популяции вместо чистого IPF.
4. 🟡 **Полный текст по-прежнему не добыт** (в архив попала страница-пересылка, а не PDF), и цитата
   про округление из работы **2017** г. (CEUS 68: 78–88, Unpaywall `closed`, 0 OA-локаций) остаётся
   не подтверждённой первоисточником. Но статус пункта меняется с «не добыто ничем» на
   **«абстракт первоисточника добыт, содержательное утверждение подтверждено авторами»**.

### Г31.2-8. Перепроверенные и НЕ сдвинувшиеся пункты

| Пункт | Замер 16.09.2026 | Итог |
|---|---|---|
| Choupani & Mamdoohi **2017** (CEUS 68:78–88) | не переоткрывался отдельно; Unpaywall ранее `closed`, 0 OA-локаций | ❌ пейволл; прокси пейволл не обходит — подтверждено на Wiley/SSRN/ScienceDirect в этом же подбатче |
| Politis & Romano 1994 | не переоткрывался | подтверждённый отрицательный результат (Г30.1-19), не класс антибота |
| Blanchett, Kowara & Chen 2012 | не переоткрывался | работы нет в OpenAlex и Crossref — проверить нечем, не вопрос канала |
| ВНДН (регламент микроданных), ОКБ, RLMS | не переоткрывались | ОКБ — SPA, нужен headless-браузер; остальные — не класс прокси |

## ИТОГ Г31.2 — calibration_ground_truth

- **Частично закрыт 1 пункт** (Choupani & Mamdoohi 2016: абстракт дословно, две проблемы IPF
  названы авторами), каналом **Wayback replay страницы статьи** — после того как прокси без UA
  и Exa по ScienceDirect отказали.
- 🔴 **Нашей ошибкой вызова прокси не оказался ни один пункт.** Замерено прямо: ScienceDirect
  отдаёт прокси оболочку Cloudflare **и с UA, и без него** — это защита издателя, класс закрыт
  как таковой.
- 🔴 **Ошибка «отказ инструмента = отсутствие источника» — 1 раз:** Wayback раньше проверялся
  только по адресу `/pdf` (где лежит страница-пересылка Elsevier) и не проверялся по адресу
  **страницы статьи**, где абстракт был всё это время.
- Канон модели, прогноз, новизна, юрблок — **не меняются**; меняется формулировка §участок 2
  (округление и zero-cell как открытые проблемы IPF, довод за симуляционный синтез).

---

## ДОБОР Г31.4 — Semantic Scholar и долги Г31.2 (16.09.2026)

**Каналы на начало работы (замер 16.09.2026, `curl -skL --http1.1`, коды дословно):**
Unpaywall **200** (1 126 б) · Crossref **200** (7 853 б) · OpenAlex **200** (23 652 б) ·
EuropePMC **200** (995 б) · `r.jina.ai` **200** (367 б, без браузерного UA) ·
Wayback replay **200** (54 059 б, 5,2 с) · `curl`/`pdftotext`/`tesseract` — все три в системе.
🔴 **Semantic Scholar расщеплён по эндпоинтам:** `/graph/v1/paper/search` — **429 на 4 из 4
попыток** (174 б, паузы 6–8 с); `/paper/search/bulk` — **200**; `/paper/DOI:<doi>` —
**200 на 3 из 3**; `/paper/DOI:<doi>/citations` — **200**. Запись «S2 = 429» в Д3–Д6 и Г18
описывала ОДИН эндпоинт из четырёх.

### Г31.4-D3. 🟢 Gathergood & Weber — ДОБЫТА ОПУБЛИКОВАННАЯ ВЕРСИЯ (JEBO 107 (2014) 455–469). Расхождение версий ЗАКРЫТО

Задолженность Г31.2 №3. Предписанные каналы (SSRN Delivery.cfm, CORE, OpenAIRE) отработаны
и **не понадобились** — сработала профилактика Г31.5: сначала спросить у Unpaywall ТОЧНЫЙ
адрес открытой копии.

| Шаг | Адрес | Код / размер | Итог |
|---|---|---|---|
| Crossref, поиск по библиографии | api.crossref.org | 200 | DOI опубликованной версии **`10.1016/j.jebo.2014.04.018`**, JEBO **т. 107, с. 455–469**; отдельно SSRN-препринт `10.2139/ssrn.2005031` |
| Unpaywall по DOI | api.unpaywall.org | **200, 3 525 б** | 🔴 **`is_oa: true`, `oa_status: "hybrid"`**; три локации: издательская `sciencedirect.com/…/S0167268114001231/pdf` + **репозитории `eprints.nottingham.ac.uk/29811/` и `nottingham-repository.worktribe.com/output/726053`** |
| Semantic Scholar по DOI | api.semanticscholar.org | **200** | `openAccessPdf.status: "HYBRID"`, 🔴 **`license: "CCBY"`**; `citationCount: 99`; **абстракт отдан ПОЛНОСТЬЮ** (в отличие от Elsevier-записей выше) |
| eprints, прямой | `eprints.nottingham.ac.uk/29811/` | **404, 466 893 б** | страница-заглушка |
| worktribe, прямой | `…/output/726053` | **403, 5 486 б** | антибот |
| worktribe через `r.jina.ai` без UA | — | **200, 549 б** | «Just a moment… Performing security verification» — капча, тела нет |
| 🟢 **Wayback replay, страница eprints** | `web.archive.org/web/2018/http://eprints.nottingham.ac.uk/29811/` | **200, 32 821 б** | **выдал точное имя файла PDF: `1-s2.0-S0167268114001231-main.pdf`** |
| 🟢 **Wayback replay, PDF** | `web.archive.org/web/20190105221234/http://eprints.nottingham.ac.uk/29811/1/1-s2.0-S0167268114001231-main.pdf` | **HTTP 200, 529 778 б, `application/pdf`** | **PDF 1.4, 16 страниц, опубликованная вёрстка Elsevier**, sha256 `329ef389d35c0b5d0f9037fea9d3267d8e078c9141d9022390a7c683ca79c1aa` |

Правовой статус чист: на первой странице PDF — «This article is made available under the
Creative Commons Attribution licence», в подвале статьи — «© 2014 The Authors. Published by
Elsevier B.V. This is an open access article under the CC BY license». Пиратские каналы
не задействованы.

**Абстракт опубликованной версии ДОСЛОВНО (с. 455):**

> «We use UK survey data to analyze the puzzling co-existence of high cost revolving consumer
> credit alongside low yield liquid savings in household balance sheets, which we name the
> 'co-holding puzzle'. Approximately **12% of households in our sample co-hold, on average,
> £3800 of revolving consumer credit** on which they incur interest charges, even though they
> could immediately pay down all this debt using their liquid assets. Co-holders are typically
> more financially literate, with above average income and education. **In most estimates**
> co-holding is also associated with impulsive spending behavior on the part of the household.
> Our results provide empirical support to theoretical models in which households co-hold
> as a means of managing self-control problems.»

**Введение, дословно (с. 456):**

> «using UK data, we find that 12% of UK households hold, on average, £3800 of revolving credit
> on multiple credit products for which they incur interest charges even though they could
> immediately pay down all this debt using their liquid assets (and with a month's income in
> liquid assets to spare). By 'co-holding' credit and assets, these households incur on average
> approximately **£650 () in unnecessary interest charges per annum. One-in-five
> 'co-holders' incur £1000 () in interest charges per annum due to co-holding.**»

**Ещё дословно, эконометрический результат (с. 457):**

> «a household which exhibits impulsiveness in spending decisions is approximately **70% more
> likely to co-hold at least £1000** of consumer credit. Estimates also imply that among
> co-holders impulsiveness is associated with co-holding approximately £3100, on average,
> equivalent to foregoing **£550 in interest payments per annum**.»

**Выборка (с. 457–458, раздел 2):** опрос **октября 2010**, **2 584 домохозяйства**; средний
доход ДХ **£35 600**, медианный **£30 000**; 70 % — собственники жилья. Среди ко-холдеров
**199 ДХ** могли погасить долг полностью, **100 ДХ** — частично; среднее ко-холдинга
**£3 800**, медианное **£2 500**. Заёмщики: средний потребдолг £6 900, медиана £3 100.
Сберегатели: средние сбережения £21 500, медиана £10 000.

### 🔴 Разрешение расхождения версий (П5.3.1 закрывается)

Раздел П5.3.1 оставил открытым: 12 % / £3 800 (аннотация публикации) против 14 % / £3 400
(рабочий документ CFCM 12/04 от 20.02.2013), и запретил цитировать числа без указания версии.
Теперь обе версии прочитаны целиком, и картина такая:

| Показатель | WP CFCM 12/04 (20.02.2013) | 🟢 **JEBO 107 (2014) 455–469 — версия записи** |
|---|---|---|
| Доля ко-холдеров | 14 % | **12 %** |
| Средний объём ко-холдинга | £3 400 | **£3 800** |
| Лишние проценты в год, в среднем | £600 | **£650 ()** |
| «Хвост» | 4 % **выборки** несут £1 300 | **каждый пятый КО-ХОЛДЕР несёт £1 000 ()** |
| Связь с импульсивностью | «is also associated» | **«In most estimates** is also associated» — формулировка ОСЛАБЛЕНА |

🔴 **Практический вывод для нас — правило цитирования, а не правка канона.** (1) Цитировать
следует **опубликованные** числа: **12 %, £3 800, £650 в год**. (2) Хвост переформулирован
не косметически: WP говорил о 4 % ВЫБОРКИ, публикация — о 20 % КО-ХОЛДЕРОВ (то есть
≈2,4 % выборки при доле ко-холдеров 12 %), и сумма снижена с £1 300 до £1 000. Наша прежняя
запись «4 % несут £1 300» опиралась на снятую авторами версию и **подлежит замене**.
(3) Ослабление «In most estimates» означает, что связь ко-холдинга с импульсивностью
в публикации подана осторожнее, чем в WP, — при ссылке на неё как на поведенческое основание
это надо воспроизводить.

**Что это меняет в продукте.** Величина «цена ошибки, которую снимает FINPILOT» остаётся
защитимой и измеренной, но её правильное значение — **£650 в год на ко-холдящее ДХ**
(не £600), а 12 % — доля таких ДХ в британской выборке 2010 года. 🟡 Перенос на РФ
по-прежнему запрещён: другая страна, другой год, другой набор кредитных продуктов;
годится только как методический образец постановки задачи. **Канон модели, формулировка
новизны и код не затрагиваются.**

## ИТОГ Г31.4

По этому файлу: **1 пункт закрыт** — Gathergood & Weber добыты **опубликованной версией
JEBO 107 (2014) 455–469** (CC BY, через Wayback по странице репозитория Ноттингема, адрес
которой дал Unpaywall). Расхождение версий из П5.3.1 **разрешено**: версия записи —
**12 %, £3 800, £650/год, каждый пятый ко-холдер £1 000**; прежняя запись «4 % выборки несут
£1 300» взята из снятого рабочего документа и подлежит замене. Формулировка связи
с импульсивностью в публикации **ослаблена** («In most estimates»).
**Вклад Semantic Scholar:** дал полный абстракт и, главное, **лицензию `CCBY`** — то есть
основание брать текст легально; но адрес открытой копии дал Unpaywall, а файл — Wayback.
Частичный вклад, не решающий.
Не добыто по файлу: ничего нового не открылось. Задолженности нет.
🔴 Канон, новизна, код — не затронуты; меняется **правило цитирования чисел**.

**Сводный итог всего подбатча Г31.4** — в `approach_validity_2026-09-10.md`, блок «ИТОГ Г31.4 (СВОДНЫЙ)».
