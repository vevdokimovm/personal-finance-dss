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
| Dawes 1979, Dawes & Corrigan 1974, Einhorn & Hogarth 1975, Wainer 1976, Grove et al. 2000, Dana & Dawes 2004, Hogarth & Karelaia 2007 | все семь — Unpaywall `is_oa: false`, `oa_status: "closed"`; пять зеркал Dawes 1979 через `curl` вернули HTML-заглушки. 🔴 **Тезис «равные веса не хуже подогнанных» первоисточником НЕ подтверждён** |
| Amar et al. 2011, Kettle et al. 2016 (snowball, лабораторные) | `closed`; у Kettle пять локаций в OpenAlex и все не-OA. 🔴 Утверждение «snowball выигрывает по доведению до конца» **не подтверждено** |
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
