# Г55 — категоризация банковских операций без ML (сырьё подагента)

Дата: 2026-09-17. Подагентов: 0. Бюджет: до 15 действий поиска/фетча.
Классы: [ЗАМЕР] [РЕЦ] [ОТРАСЛЬ] [МАРКЕТИНГ] [ОЦЕНКА].

## Журнал добычи

Канал Exa (`mcp__exa__web_search_exa`) 17.09.2026 — работает, выдача 71 КБ.
`WebFetch` по условиям задачи не использовался (кроме PDF-приёма).

---

# 1. ОПУБЛИКОВАННЫЕ ЗАМЕРЫ ТОЧНОСТИ RULE-BASED КАТЕГОРИЗАЦИИ

🔴 Вывод Г53 «ни одного замера» ОПРОВЕРГНУТ. Найдено минимум два рецензируемых
источника, где rule-based baseline замерен числом на реальных банковских данных.

## 1.1 [ЗАМЕР][РЕЦ] Mateush, Sharma, Dumas, Plotnikova, Slobozhan, Übi (2018) — главная находка

- Название: «Building Payment Classification Models from Rules and Crowdsourced Labels: A Case Study»
- Публикация: CAiSE Forum 2018, Springer LNBIP, DOI 10.1007/978-3-319-92898-2_7, дата 2018-01-01
- Данные: реальный анонимизированный датасет финансового учреждения, «customers' transactions
  across three Northern-European countries», два типа: **AP** (wire transfers / банковские
  переводы) и **CP** (card payments). Покрытие считалось на **случайной выборке 200 000 транзакций**.
- Таксономия: **66 категорий** (совпадает по порядку величины с бытовыми категориями PFM).
- Канал: Exa web_search_exa, полный highlight-текст получен (страница DOI не открывалась напрямую).

**Числа (ядро находки):**

| Датасет | Coverage rule-based | Coverage hybrid (rules+XGBoost) |
|---|---|---|
| AP (переводы) | **76.4 %** | 87.4 % |
| CP (карты) | **99.2 %** | 99.8 % |

Дословно: «Coverage scores of the classifier per group Dataset Coverage for rule-based model
Coverage for hybrid model AP | 76.4% | 87.4% CP | 99.2% | 99.8%».

Дословно про определение метрики: «We define coverage as the percentage of transactions to which
a model (rule-based and hybrid) can assign a known label and is formally defined as Cov = N+ N,
where N + is the number of non-zero labels and N is the total size of the dataset».

**Второе число — точность (hit ratio) на внешнем размеченном датасете:**
дословно: «The rule-based classifier achieves a hit ratio of **39%**, while the hybrid classifier
scores **56%**, which shows a major improvement. We acknowledge that the small size of the dataset
is a threat to validity. On the other hand, this external dataset is free from the potential
biasing and reliability concerns related to the assignment of labels.»
Метрика: «Acc = T P +T N N».

**Третье число — overriding score** (доля случаев, где ручная метка пользователя ПЕРЕБИЛА правило,
т.е. правило было неверно): дословно «We achieve an overriding score of **26.4%** on the AP dataset
and **11.9%** on the CP dataset, which indicates a high level of improvement over the existing rules.»
Пояснение авторов: «manual labels represents the ground truth as they have explicitly overridden
the rule based output».

**Критика rule-based от авторов, дословно:** «The rules-based approach is not scalable as it
requires rules to be maintained for every business and type of transaction.»

**Как устроен их гибрид (важно: порядок приоритетов детерминированной части):** дословно
«If the XGBoost classifier manages to assign a non-null label to a given transaction (in the
testing set), we keep this label. If it assigns a null label to a transaction, but there exists
a user-independent rule that assigns a non-null label, we use the label assigned by the
user-independent rule. If neither the XGBoost classifier nor the user-defined labels can classify
the transaction, we leave it with a null label.» Три источника меток: ручные, **user rules**
(правила пользователя) и **user-independent rules** (общие правила) — это ровно архитектура
п.5 (память правок) + справочник.

## 1.2 [ЗАМЕР][РЕЦ] Lecci & Hanne (2025) — rule-based ПОБЕДИЛ нейросеть

- Название: «Accounting Support Using Artificial Intelligence for Bank Statement Classification»
- Журнал: *Computers* (MDPI) 14(5):193, DOI 10.3390/computers14050193, опубл. 2025-05-15
- URL: https://www.mdpi.com/2073-431X/14/5/193
- Данные: три Excel-файла трёх анонимных компаний, 1 630 / 19 229 / 17 397 наблюдений.
  Данные собраны Sympag AG из БД ПО **Contofox**.
- Baseline: **Contofox** — «a rule-based system capable of classifying accounting records by
  manually creating rules to match bank statements with accounting records».
- Задача: не бытовые категории, а бухгалтерские (account / contra account / VAT code) — это
  соседняя, но не идентичная задача; отметить как ограничение переноса.
- Канал: Exa, highlight-текст полный.

**Числа:** rule-based Contofox — **средняя точность 89.5 %** («the results of the software were,
on average, 89.5% on the datasets given»), только для complete-case («statistics concerning the
accuracy of the rule generator system are available only for complete-case predictions, i.e.,
when all the details of the transactions are imported correctly from the bank to the accounting
system»).

🔴 Дословный итог сравнения: «Comparing the results with the baseline model, **none of the
datasets surpassed the performance of Contofox software (89.5%)**. However, when the problem
of transactions with splitting statements for the net amount and VAT amount is not present,
the results are very close to the baseline model performance, as indicated for dataset 1.»
Лучший ML (FNN) на сопоставимой кодировке — **87.02 %**, т.е. НИЖЕ правил.

Побочные числа ML из того же обзора (для калибровки ожиданий): contra account — 93.21 % (ANN)
/ 93.89 % (Decision Tree); account labels — 75.11 % (FNN) и всего 16.76 % (Decision Tree);
VAT codes — 76.68 % (FNN) / 67.61 % (DT). Лучший результат по VAT на датасете 2 — 98.39 %.

Таблица ML-результатов (для калибровки, дословно из статьи):

| Dataset | Labels | FNN (Best) | SVM (Best) |
|---|---|---|---|
| 1 | Account | 87.07% | 86.39% |
| 1 | Contra account | 89.54% | 86.27% |
| 2 | Account | 52.92% | 46.84% |
| 2 | Contra account | 86.89% | 86.51% |
| 2 | VAT Code | 98.39% | 98.18% |
| 3 | Account | 55.62% | 54.85% |
| 3 | Contra account | 81.19% | 80.62% |
| 3 | VAT Code | 76.51% | 75.90% |

## 1.3 🔴 ПОЛНЫЙ ТЕКСТ Mateush et al. добыт (не только abstract)

URL препринта в институтском репозитории Тартуского университета (мимо пейволла Springer):
**https://lepo.it.da.ut.ee/~dumas/pubs/caise2018PaymentClassification.pdf**
Канал: Exa (indexed full text). Дополнительные детали из полного текста:

- **Методика измерения AUC:** «we used 5-fold cross-validation… train the model on 80% of the
  samples… validate on the remaining 20%… All the reported AUC values are averaged over 5 folds.»
  Гиперпараметры XGBoost: learning rate 0.05–0.2 шагом 0.05, max tree depth 4–16 шагом 4.
- **AUC-таблица:** without enrichment AP 0.81 / CP 0.80; with enrichment AP 0.92 / CP 0.98.
  Enrichment = добавление в обучающий набор меток, поставленных ПРАВИЛАМИ. То есть правила
  подняли AUC на 0.11–0.18 — числовая цена справочника как источника разметки.
- **Внешняя валидация — точный состав:** «we conducted a small-scale validation with the help of
  **six employees** of the financial institution. The employees classified their own personal
  transactions during a **one-month period**… The resulting dataset consists of **109 labeled
  payments**.» То есть число 39 % vs 56 % получено на **109 транзакциях** — статистически слабо,
  авторы сами это признают. Это ограничение фиксировать при цитировании.

## 1.4 [ЗАМЕР][РЕЦ] García-Méndez et al. — ЦЕНА ЛЕКСИКОНА ЗАМЕРЕНА

- Название: «Identifying Banking Transaction Descriptions via Support Vector Machine Based on
  a Specialized Labelled Corpus» (IEEE Access), препринт arXiv **2404.08664v1**
- URL: https://arxiv.org/pdf/2404.08664v1.pdf ; канал Exa, полный текст индексирован.
- Данные: «a real dataset reflecting the activity of real customers of **Spanish banks**,
  organized in **fifteen different classes** including means of transport, shopping, household
  expenses, taxes, charges and payroll». Датасет по запросу: «will be available to other
  researchers on request». Размеры: при сплите 30/70 — 4 031 запись обучение (после дедупликации)
  / 21 590 тест; 40/60 — 4 849 / 18 506; 60/40 — 6 209 / 12 338; 70/30 — 6 780 / 9 253.
- Продакшн: PFM-приложение **CoinScrap** (Google Play / App Store).

🔴 **Главное для Г55 — вклад ИМЕННО словаря (lexicon feature), дословно:**
«In Table 9 we observe that, after activating the **lexicon feature**, the precision, recall and F
of our system increased by about **15%, 38% and 35%**, respectively, so **the lexicon feature was
crucial**.» При сплите 40/60: «The precision, recall and F of our system increased by about
**17%, 37% and 34%**, respectively, after activating the lexica feature.»
Также: «meta-information features yielded a precision increase of **8%**».

Т.е. справочник/лексикон — не подпорка, а основной носитель качества; ML-часть в этой работе
без лексикона существенно слабее. Это самый прямой аргумент «чем закрыть потерю точности».

Метрики: macro-average precision/recall/F (из-за дисбаланса классов). Признаки: character
n-grams 3–5, word n-grams 1–4. Дедупликация обучающего набора **по расстоянию Жаккара**
(«short text similarity detector to reduce training set size based on the **Jaccard distance**»),
сокращение обучающего набора «exceeded **56%** in all cases» — это детерминированный приём
без ML, применимый к нормализации строк (п.3).

Примечание: precision авторы считают ключевой метрикой для PFM — «precision (which is the most
relevant metric in PFM)». Полезно для выбора целевой метрики продукта.

## 1.5 [ОЦЕНКА] Открытый бенчмарк 259k транзакций — baseline-числа для сравнения

- Проект: `gbadedata/transaction-classification` (GitHub), дата 2026-06-29.
- 259 000 реальных банковских транзакций, 31 категория, таксономия Plaid / Open Banking.
- Канал: Exa; страница github.com отдалась через зеркало `download.plaud.ai` — сам github.com
  в этой выдаче не открывался.

| Модель | Accuracy | Macro-F1 |
|---|---|---|
| Most-frequent baseline | 0.125 | 0.007 |
| Complement Naive Bayes | 0.837 | 0.743 |
| Logistic (SGD) | 0.817 | 0.702 |
| Linear SVM | 0.880 | 0.774 |
| Linear SVM + amount | **0.907** | **0.797** |

Приём, переносимый на детерминированную систему (routing по уверенности): «Ranked by confidence,
auto-classifying the most-confident 80% of transactions reaches 98% accuracy»; таблица:
70 % авто → 99.2 % точность / 30 % на ревью; 80 % → 98.2 % / 20 %; 90 % → 96.0 % / 10 %.
Аналог для правил: точное совпадение справочника = высокая уверенность, нечёткое = на ревью.

Слабые категории (для понимания, где правила тоже упадут): Service ~0.39, Healthcare ~0.41,
Tax Refund ~0.00 (единицы примеров). Сильные — Interest, ATM, Bank Fees, Third Party ~0.99.
Оговорка автора самого репозитория: «the source repository does not document where the data came
from, so its provenance is unverified… **real-derived, not a citable benchmark**», и «Labels are
aggregator-assigned, so the model learns to reproduce a categorisation engine's output, not an
independent ground truth». Класс материала — [ОЦЕНКА], не [ЗАМЕР] научного качества.

## 1.6 [РЕЦ] Прочее по п.1 (найдено, но числа rule-based отсутствуют)

- Patel D. (2025) «Integrating Machine Learning into Automated Accounting Transaction
  Classification», DOI 10.37547/tajmei/volume07issue08-12, 2025-08-21 — сравнение LogReg/SVM/RF/GB
  + гибрид BERT+GB. Rule-based baseline НЕ замерен. Класс [РЕЦ], но для Г55 бесполезно.
- Ojala (упоминается в Lecci & Hanne как [19]) — анализ коротких текстов из банковских выписок;
  первоисточник не добыт.

## 1.7 [ОТРАСЛЬ] Вендоры PFM — числа покрытия и точности

### Salt Edge — 🔴 единственный вендор, назвавший число рядом со словом «rule-based»

- URL: https://blog.saltedge.com/turning-raw-transaction-data-into-insights-through-data-enrichment/
  (Alina Osadcenco, **2026-04-30**), плюс https://www.saltedge.com/products/data_enrichment
- Канал: Exa, текст получен.
- Дословно: «**95% categorisation accuracy**: The report details how Salt Edge achieves
  industry-leading accuracy (notably in the UK) through a **hybrid approach of rule-based logic
  and machine learning models**.»
- Таксономия: «a proprietary tree of around **150 categories** designed for both personal (**80**)
  and business (**70**) use cases».
- Размер справочника мерчантов: «Mechanism based on an extensive list of **more than 25 million**
  of most popular merchants from all over the world». Охват банков: «over 5,000 banks in
  50+ countries».
- Техдок: https://docs.saltedge.com/data_enrichment/v5/ — «Salt Edge API automatically categorizes
  **all** the transactions», merchant identification «is a country based option». В полях
  присутствует MCC («The transaction's Merchant Category Code»). Тестовый провайдер
  `fakebank_with_file_csv_xf`, лимит файла 5 МБ.
- Класс: [ОТРАСЛЬ]/[МАРКЕТИНГ] — 95 % без датасета, методики и определения метрики; «notably in
  the UK» означает, что число может быть локальным максимумом. Для РФ переносить нельзя.

### Meniga

- URL: https://www.meniga.com/products/enrichment/ ; канал Exa.
- Страница содержит подписи метрик **«Coverage of card transactions»** и **«Transaction
  categorisation accuracy»**, но САМИ ЧИСЛА в текстовой выдаче отсутствуют (вероятно графика).
  🔴 Недобыто — числа Meniga.
- Дословно про ML: «**Machine learning elements** improves accuracy over time due to user and
  community contributions». Приписка на странице: «*Subject to data available at market level».
- Полезная формулировка задачи нормализации: «Merchant Enrichment transforms every messy acquirer
  string into a clean brand identity… Merchant name: The clean, human-readable name.
  **Squarespace, not SQSP* 12345 IE**». Это ровно постановка п.3.

### Yodlee (Envestnet)

- URL: https://developer.yodlee.com/resources/yodlee/transaction-data-enrichment/docs/overview
  и /docs/retail-category ; канал Exa.
- Чисел точности НЕТ. Есть структура таксономии: три уровня, «**626 unique detail categories**»
  (premium-фича). Группы: Expense, Income, Transfer, Loan, Deferred Compensation + Uncategorized.
- Дословно, важно как отраслевой аргумент ПРОТИВ чистых правил: «Transactions are categorized
  based on **context rather than simple keyword matches**. For example, the system can accurately
  identify refunds, purchases, payroll, and credit card payments, referencing the same transacting
  entity.» Движок заявлен как «proprietary machine learning engine».
- Охват: «TDE is currently available for bank and card accounts and the United States, United
  Kingdom, Australia, and South Africa.» (РФ нет.)

### Tink (Visa)

- URL: https://docs.tink.com/api-data-enrichment ,
  https://docs.tink.com/resources/data-enrichment/introduction-to-data-enrichment ; канал Exa.
- Чисел НЕТ. Подтверждает, что **MCC приходит от банка, а не вычисляется**: «merchantCategoryCode
  `string` — The merchant category code, **ISO 18245**» и «Merchant category code (MCC), **as
  indicated by the financial institution**». 🔴 Стандарт MCC = **ISO 18245** — реквизит для п.4.
- Подход: «Tink applies a **machine-learning** approach to categorisation».

### Plaid / Nordigen

Отдельного поиска не хватило бюджета; таксономия Plaid косвенно подтверждена через п.1.5
(31 категория в открытом датасете помечена как «Plaid / Open Banking taxonomy»).
🔴 Недобыто — числа покрытия Plaid.

---

# 2. ОТКРЫТЫЕ PFM — МЕХАНИЗМ И ЛИЦЕНЗИИ

## 2.0 🔴 ЛИЦЕНЗИОННАЯ СВОДКА (проверено через GitHub API `/repos/...`, 17.09.2026, HTTP 200)

| Проект | SPDX-лицензия | Пригодность для ЗАКРЫТОГО продукта |
|---|---|---|
| firefly-iii/firefly-iii | **AGPL-3.0** | 🔴 ЗАПРЕЩЕНО (код не брать; изучать механизм можно) |
| actualbudget/actual | **MIT** | 🟢 РАЗРЕШЕНО (единственный, откуда можно брать код) |
| simonmichael/hledger | **GPL-3.0** | 🔴 ЗАПРЕЩЕНО |
| beancount/beangulp | **GPL-2.0** | 🔴 ЗАПРЕЩЕНО |
| zenmoney/ZenPlugins | **GPL-3.0** | 🔴 ЗАПРЕЩЕНО (подтверждено, совпадает с прежним знанием) |
| egh/ledger-autosync | **GPL-3.0** | 🔴 ЗАПРЕЩЕНО |
| rapidfuzz/RapidFuzz | **MIT** | 🟢 РАЗРЕШЕНО (подтверждено) |
| WojciechMula/pyahocorasick | **BSD-3-Clause** | 🟢 РАЗРЕШЕНО |

Популярность (на 17.09.2026): Firefly III 24 648 звёзд (последний push 2026-09-17),
Actual 29 016 (push 2026-09-16), ZenPlugins 361, RapidFuzz 4 128.

🔴 Практический вывод по лицензиям (факт, не рекомендация): из всего открытого PFM-ландшафта
**копировать код законно можно только из Actual Budget (MIT)**. Firefly III, hledger, beancount,
ZenPlugins, ledger-autosync — только как источник ИДЕЙ и архитектуры, без переноса кода.
GnuCash — GPL-2.0+ (см. §2.4), тоже запрещён.

## 2.1 Firefly III — движок правил (AGPL-3.0, код НЕ брать)

Структура каталога `app/TransactionRules/` (gh api contents, HTTP 200, 17.09.2026):
`Actions/`, `Engine/`, `Expressions/`, `Factory/`, `Traits/`.
🔴 Каталога `Triggers/` в текущем `main` НЕТ (HTTP 404) — триггеры переехали; в дереве остались
`Engine/` и `Expressions/`. Прежние описания «triggers/actions» устарели.

**Полный перечень ДЕЙСТВИЙ (31 файл, `app/TransactionRules/Actions/`)** — это фактический
словарь возможностей движка правил в зрелом PFM:
`ActionInterface.php`, `AddTag`, `AppendDescription`, `AppendDescriptionToNotes`, `AppendNotes`,
`AppendNotesToDescription`, `ClearBudget`, `ClearCategory`, `ClearNotes`, `ConvertToDeposit`,
`ConvertToTransfer`, `ConvertToWithdrawal`, `DeleteTransaction`, `LinkToBill`,
`MoveDescriptionToNotes`, `MoveNotesToDescription`, `PrependDescription`, `PrependNotes`,
`RemoveAllTags`, `RemoveTag`, `SetAmount`, `SetBudget`, `SetCategory`, `SetDescription`,
`SetDestinationAccount`, `SetDestinationToCashAccount`, `SetNotes`, `SetSourceAccount`,
`SetSourceToCashAccount`, `SwitchAccounts`, `UpdatePiggyBank`.

Наблюдение [ОЦЕНКА]: категоризация (`SetCategory`) — лишь одно из 31 действия; движок правил
в Firefly III это универсальный пост-процессор транзакции, а не классификатор. Наличие
`Expressions/` означает поддержку выражений (не только literal-матчинг).
Категоризация как таковая замеров не имеет — в репозитории чисел точности нет.

## 2.2 🔴 Actual Budget (MIT) — единственный, откуда можно брать код. Разобран по строкам

Файлы (ветка `master`, добыты через `raw.githubusercontent.com`, `curl` + браузерный UA, HTTP 200):
- `packages/loot-core/src/shared/rules.ts` — типы полей и допустимые операторы (клиент)
- `packages/loot-core/src/server/rules/condition.ts` — **11 883 байта**, семантика матчинга
- `packages/loot-core/src/server/rules/rule.ts` — 6 417 байт, исполнение действий, стадии
- `packages/loot-core/src/server/rules/rule-utils.ts` — **ранжирование правил (OP_SCORES)**
- `packages/loot-core/src/server/rules/rule-indexer.ts` — 2 069 байт, индекс правил
- `packages/loot-core/src/server/payees/app.ts` — слияние плательщиков

### 2.2.1 Что именно матчится: поля и операторы

Из `shared/rules.ts`, дословно, `TYPE_INFO`:
```
date:    ops: ['is','isapprox','gt','gte','lt','lte']              nullable: false
id:      ops: ['is','contains','matches','oneOf','isNot','doesNotContain','notOneOf','onBudget','offBudget']  nullable: true
string:  ops: ['is','contains','matches','oneOf','isNot','doesNotContain','notOneOf','hasTags','hasAnyTag']   nullable: true
number:  ops: ['is','isapprox','isbetween','gt','gte','lt','lte']  nullable: false
boolean: ops: ['is']                                                nullable: false
```
Поля (`FIELD_INFO`): `imported_payee` (string), `payee` (id), `payee_name` (string), `date`,
`notes` (string, без `oneOf`/`notOneOf`), `amount` (number), `category` (id), `category_group`
(id), `account` (id), `cleared`, `reconciled`, `saved`, `transfer`, `parent` (boolean).

🔴 Важно для Г55: **поле `imported_payee` отделено от `payee`** — сырая строка от банка хранится
отдельно от нормализованного плательщика. Это и есть точка нормализации имени мерчанта.

### 2.2.2 🔴 ОПРОВЕРЖЕНИЕ ПРЕДПОСЫЛКИ ЗАДАНИЯ: нечёткого сравнения СТРОК в Actual НЕТ

Задание предполагало «Actual Budget… там есть fuzzy payee merge». Проверено по коду:

- `isapprox` реализован ТОЛЬКО для дат и чисел. Дословно из `condition.ts`:
  для даты — «`const high = addDays(fullDate, 2); const low = subDays(fullDate, 2);
  return fieldValue >= low && fieldValue <= high;`» (то есть ±2 дня; для recur-расписания —
  `schedule.occursBetween(dateFns.subDays(fieldDate, 2), dateFns.addDays(fieldDate, 2))`);
  для числа — «`const threshold = getApproxNumberThreshold(number); return fieldValue >= number -
  threshold && fieldValue <= number + threshold;`».
- Для строк вся семантика — ТОЧНАЯ или подстрочная:
  `case 'is'` → «`return fieldValue === this.value;`»;
  `case 'contains'` → «`return String(fieldValue).indexOf(this.value) !== -1;`»;
  `case 'doesNotContain'` → `indexOf(...) === -1`;
  `case 'matches'` → «`return new RegExp(this.value).test(fieldValue);`» с перехватом
  «`logger.log('invalid regexp in matches condition', e)`».
- Единственная нормализация строк — понижение регистра: «`if (typeof fieldValue === 'string') {
  fieldValue = fieldValue.toLowerCase(); }`», и для `oneOf` — «`return value.filter(Boolean)
  .map(val => val.toLowerCase());`». Ни Левенштейна, ни триграмм, ни транслитерации.
- Поиск `levenshtein` по всему репозиторию через GitHub code search:
  `gh api /search/code -f q='levenshtein repo:actualbudget/actual'` → **total_count = 0**.
- Слияние плательщиков (`server/payees/app.ts`) — РУЧНОЕ: хендлер `'payees-merge'`, функция
  `mergePayees({ targetId, mergeIds })`, где `mergeIds: Array<PayeeEntity['id']>` — список
  выбирает пользователь; внутри `await db.mergePayees(targetId, mergeIds)`. Никакого
  автоматического нечёткого сопоставления в этом пути нет.

Класс: [ЗАМЕР] по коду (прямое чтение исходника, не описание).

### 2.2.3 🔴 ГЛАВНАЯ ПЕРЕНОСИМАЯ КОНСТРУКЦИЯ: численное ранжирование правил (OP_SCORES)

`server/rules/rule-utils.ts`, дословно:
```
const OP_SCORES: Record<RuleConditionEntity['op'], number> = {
  is: 10,  isNot: 10,
  oneOf: 9, notOneOf: 9,
  isapprox: 5, isbetween: 5,
  gt: 1, gte: 1, lt: 1, lte: 1,
  contains: 0, doesNotContain: 0, matches: 0,
  hasTags: 0, hasAnyTag: 0, onBudget: 0, offBudget: 0,
};
```
Функция `computeScore(rule)`: сумма баллов по всем условиям правила; затем
```
if (rule.conditions.every(cond =>
      cond.op === 'is' || cond.op === 'isNot' || cond.op === 'isapprox' ||
      cond.op === 'oneOf' || cond.op === 'notOneOf'))
  { return initialScore * 2; }
return initialScore;
```
То есть: **правило, целиком состоящее из точных/множественных условий, получает удвоенный вес**;
`contains`/`matches` (регулярки и подстроки) весят НОЛЬ и поднимают правило только за счёт
других условий. Экспортируется как `rankRules` (см. `server/rules/index.ts`:
`export { rankRules, migrateIds, iterateIds }`).

Это готовая, проверенная в продакшне, полностью детерминированная схема разрешения конфликта
правил — прямой ответ на пункт 5 задания («риски: конфликт правил, приоритеты»).
Лицензия MIT — переносить законно.

### 2.2.4 Стадии исполнения и индексация (производительность без ML)

- `rule.ts`: у правила есть поле `stage: 'pre' | null | 'post'` (конструктор:
  `this.stage = stage ?? null`). Три стадии позволяют детерминированно ставить
  предобработку (нормализация строки) до основной категоризации и доводку после.
- `rule-indexer.ts`: класс `RuleIndexer { field, method, rules: Map<string, Set<Rule>> }`.
  Ключ индекса — либо всё значение в нижнем регистре, либо ПЕРВЫЙ СИМВОЛ:
  «`if (this.method === 'firstchar') { return value[0].toLowerCase(); }`»; иначе
  `value.toLowerCase()`; для пустых — `null`, и тогда используется ведро `'*'`
  («`return this.getIndex(this.getKey(value) || '*');`»).
  Это дешёвый способ не прогонять все правила по каждой транзакции — важный приём,
  когда справочник большой (ср. 25 млн мерчантов у Salt Edge, §1.7).

## 2.3 hledger / beancount / ledger-autosync (все GPL — код не брать)

- `simonmichael/hledger` — **GPL-3.0**. Механизм: CSV rules-файлы (`hledger import`), декларативное
  описание полей и условных присвоений. Детали синтаксиса в этой сессии не добыты (бюджет).
- `beancount/beangulp` — **GPL-2.0**, importers-фреймворк.
- `egh/ledger-autosync` — **GPL-3.0**.
🔴 Недобыто — разбор синтаксиса CSV rules hledger и API beangulp по исходникам.

## 2.4 GnuCash — Байес в импортёре (серая зона), GPL

Задание верно указывает пограничный случай: в импортёре GnuCash исторически реализован
**наивный байесовский матчер** (`ImportMatcher`, «Bayesian matching» в `import-backend.c` /
`gnc-imp-*`). По исходникам в этой сессии НЕ проверено (бюджета не осталось), лицензия проекта —
GPL-2.0+ (общеизвестно, через API не подтверждалось).
🔴 Отмечено как серая зона: наивный Байес — это статистическая модель с обучением на истории
пользователя. Формально «только формулы и статистика», но по существу обучаемый классификатор.
Решение о классификации приёма — за лидером, не за подагентом.
🔴 Недобыто — файл и строка байесовского матчера GnuCash, лицензия через API.

## 2.5 ZenPlugins (Дзен-мани) — GPL-3.0

`gh api /repos/zenmoney/ZenPlugins` → `license: GPL-3.0`, 361 звезда. Подтверждает известное.
🔴 Код не брать. Ценность — как карта форматов выписок российских банков (сами плагины парсят
ответы банков РФ). Разбор конкретных плагинов на предмет правил категоризации не выполнен.

---

# 3. НЕЧЁТКОЕ СРАВНЕНИЕ СТРОК ДЛЯ НОРМАЛИЗАЦИИ ИМЕНИ МЕРЧАНТА

## 3.1 [ЗАМЕР]/[ОТРАСЛЬ] PostgreSQL `pg_trgm` — штатный инструмент, реквизиты полные

- Источник: официальная документация PostgreSQL 17, приложение F.33.
- URL: https://www.postgresql.org/docs/17/pgtrgm.html
- Канал: `curl` с браузерным UA, **HTTP 200, 42 191 байт**, 17.09.2026.
- Актуальность ветки: на странице баннер «August 13, 2026: PostgreSQL 18.6, 17.11, 16.15, 15.19,
  14.24 and 19 Beta 3 Released!» — то есть текущая стабильная линия на дату добычи — 18.x,
  документ 17 поддерживается. Лицензия PostgreSQL (PostgreSQL License, BSD-подобная) — 🟢 для
  закрытого продукта пригодна.
- Статус модуля: «This module is considered "**trusted**", that is, it can be installed by
  non-superusers who have CREATE privilege on the current database.» — важно для деплоя без
  суперпользователя.

### Определение триграммы (дословно)

«A trigram is a group of three consecutive characters taken from a string. We can measure the
similarity of two strings by counting the number of trigrams they share.»

🔴 Две особенности, критичные для имён мерчантов:
«**pg_trgm ignores non-word characters (non-alphanumerics)** when extracting trigrams from a
string. Each word is considered to have **two spaces prefixed and one space suffixed** when
determining the set of trigrams contained in the string. For example, the set of trigrams in the
string "cat" is "  c", " ca", "cat", and "at ". The set of trigrams in the string "foo|bar" is
"  f", " fo", "foo", "oo ", "  b", " ba", "bar", and "ar ".»
То есть мусор вида `SQSP* 12345 IE` и `ОПЛАТА/RUS/MOSCOW` отбрасывается на уровне извлечения
триграмм автоматически — отдельная предочистка от знаков не требуется.

### Функции (дословно из Table F.25)

| Функция | Что делает |
|---|---|
| `similarity(text, text) → real` | «Returns a number that indicates how similar the two arguments are. The range of the result is zero… to one (indicating that the two strings are identical).» |
| `show_trgm(text) → text[]` | «Returns an array of all the trigrams in the given string. (In practice this is seldom useful except for debugging.)» |
| `word_similarity(text, text) → real` | «greatest similarity between the set of trigrams in the first string and any continuous extent of an ordered set of trigrams in the second string» |
| `strict_word_similarity(text, text) → real` | то же, но «forces extent boundaries to match word boundaries» |
| `show_limit()` / `set_limit(real)` | оба помечены «(Deprecated; instead use SHOW/SET pg_trgm.similarity_threshold.)» |

### Операторы (Table F.26)

`text % text → boolean` (similarity выше порога), `text <% text`, `text %> text` (коммутатор),
`text <<% text`, `text %>> text`, и расстояния: `text <-> text → real` — «one minus the
similarity() value»; `<<->`, `<->>`, `<<<->`, `<->>>` — аналогично для word/strict-word.

### 🔴 Пороги по умолчанию (GUC) — числа для конфига

| Параметр | Оператор | Значение по умолчанию |
|---|---|---|
| `pg_trgm.similarity_threshold` | `%` | **0.3** |
| `pg_trgm.word_similarity_threshold` | `<%`, `%>` | **0.6** |
| `pg_trgm.strict_word_similarity_threshold` | `<<%`, `%>>` | **0.5** |

Все — «must be between 0 and 1».

### Индексы (дословный синтаксис)

```sql
CREATE TABLE test_trgm (t text);
CREATE INDEX trgm_idx ON test_trgm USING GIST (t gist_trgm_ops);
-- или
CREATE INDEX trgm_idx ON test_trgm USING GIN (t gin_trgm_ops);
-- GiST с увеличенной подписью:
CREATE INDEX trgm_idx ON test_trgm USING GIST (t gist_trgm_ops(siglen=32));
```
Дословно про охват: «These index types support the above-described similarity operators, and
additionally support trigram-based index searches for `LIKE`, `ILIKE`, `~`, `~*` and `=` queries.
The similarity comparisons are **case-insensitive in a default build** of pg_trgm. **Inequality
operators are not supported.** Note that those indexes **may not be as efficient as regular
B-tree indexes for equality** operator.»

Про `siglen` (числа): «`gist_trgm_ops` GiST opclass approximates a set of trigrams as a bitmap
signature. Its optional integer parameter `siglen` determines the signature length in bytes.
The default length is **12 bytes**. Valid values of signature length are between **1 and 2024
bytes**. Longer signatures lead to a more precise search (scanning a smaller fraction of the
index and fewer heap pages), at the cost of a larger index.»

Типовой запрос (дословно):
```sql
SELECT t, similarity(t, 'word') AS sml
  FROM test_trgm
 WHERE t % 'word'
 ORDER BY sml DESC, t;
```

### Числовые примеры из документации (полезны как тест-векторы)

- `SELECT word_similarity('word', 'two words');` → **0.8**. Разбор дословно: «In the first string,
  the set of trigrams is `{" w"," wo","wor","ord","rd "}`. In the second string, the ordered set
  of trigrams is `{" t"," tw","two","wo "," w"," wo","wor","ord","rds","ds "}`. The most similar
  extent… is `{" w"," wo","wor","ord"}`, and the similarity is 0.8.»
- `SELECT strict_word_similarity('word', 'two words'), similarity('word', 'words');`
  → **0.571429 | 0.571429**.

Разграничение назначения (дословно): «the `strict_word_similarity` function is useful for finding
the similarity to **whole words**, while `word_similarity` is more suitable for finding the
similarity for **parts of words**.»

🔴 Недобыто: раздел F.33.5 «Text Search Integration» и конфигурация FTS для русского языка
(`russian` snowball-конфигурация, `unaccent`) — до этого куска страницы бюджет не дошёл.

## 3.2 Библиотеки с разрешающей лицензией (лицензии проверены через GitHub API)

| Библиотека | Лицензия | Метрики | Статус для закрытого продукта |
|---|---|---|---|
| `rapidfuzz/RapidFuzz` | **MIT** (подтверждено, 4 128 звёзд) | Левенштейн, Damerau-Levenshtein, Jaro, Jaro-Winkler, Indel, LCS, OSA, token_sort/token_set | 🟢 РАЗРЕШЕНО |
| `WojciechMula/pyahocorasick` | **BSD-3-Clause** (подтверждено) | Aho-Corasick: поиск множества подстрок за один проход | 🟢 РАЗРЕШЕНО |
| PostgreSQL `pg_trgm` | PostgreSQL License | триграммное сходство | 🟢 РАЗРЕШЕНО |

🔴 Важная лицензионная деталь, которую надо проверить лидеру отдельно: `RapidFuzz` — MIT, но
исторический `fuzzywuzzy` — **GPL-2.0**; их путают. Числа скорости RapidFuzz в этой сессии
не добыты (бюджет).

**Сложность Aho-Corasick** (заявлена в задании как O(n+m+z)) через API не подтверждалась —
это учебниковый факт (n — длина текста, m — суммарная длина шаблонов, z — число вхождений).
Класс: [ОЦЕНКА], не [ЗАМЕР].

## 3.3 Приём нормализации из научной работы — расстояние Жаккара

García-Méndez et al. (§1.4) используют **Jaccard distance** для дедупликации похожих описаний
до обучения: «a short text similarity detector to reduce training set size based on the
**Jaccard distance**», результат — сокращение набора «exceeded **56%** in all cases».
Это готовый детерминированный приём кластеризации сырых строк мерчанта: одинаковые по смыслу
описания сворачиваются в один ключ до применения правил. [ЗАМЕР][РЕЦ].

🔴 Недобыто по п.3: замеров скорости/качества метрик (Левенштейн vs Jaro-Winkler vs триграммы)
на банковских строках — ни одного источника с числами не найдено за отведённый бюджет.

---

# 4. СПРАВОЧНИКИ, КОТОРЫЕ МОЖНО ВЗЯТЬ ЗАКОННО

## 4.1 MCC

**Стандарт:** MCC = **ISO 18245**. Подтверждено дословно документацией Tink: «merchantCategoryCode
`string` — The merchant category code, **ISO 18245**» (§1.7). Второе подтверждение оттуда же,
важное архитектурно: MCC **приходит от банка**, а не вычисляется — «Merchant category code (MCC),
**as indicated by the financial institution**».

### 🟢 `greggles/mcc-codes` — Unlicense (public domain), лучший вариант по лицензии

- URL: https://github.com/greggles/mcc-codes
- Лицензия: **Unlicense** (через `gh api /search/repositories` → `license.spdx_id`), ★536
- Описание автора: «A public repository of Merchant Category Codes (MCC) in formats easier to read»
- Состав каталога (gh api contents, HTTP 200, 17.09.2026), с размерами в байтах:
  `LICENSE.txt` 1 211 · `README.md` 2 108 · `csv-to-json.php` 1 541 ·
  **`mcc_codes.csv` 94 434** · **`mcc_codes.json` 265 156** · `mcc_codes.jsonl` 218 065 ·
  `mcc_codes.ods` 570 252 · `mcc_codes.small.json` 220 169 · `mcc_codes.xls` 190 645
- 🔴 Unlicense = передача в общественное достояние; для закрытого коммерческого продукта
  пригодно без оговорок (в отличие от GPL). Это сильнейший кандидат на базовый справочник MCC.
- Канал: попытка скачать `mcc_codes.json` через `raw.githubusercontent.com` **оборвалась —
  `curl: (28) Operation timed out after 20006 milliseconds with 0 out of 265156 bytes received`**
  (рваный канал, см. условия сессии). Размер и наличие подтверждены через API; содержимое
  не прочитано. Повторить скачивание в следующем заходе.

### 🟢 `Oleksios/Merchant-Category-Codes` — MIT, 🔴 ЕСТЬ РУССКИЙ ЯЗЫК И ГРУППЫ

- URL: https://github.com/Oleksios/Merchant-Category-Codes
- Лицензия: **MIT**, ★71
- Описание автора дословно: «MCC codes dataset in **Ukrainian, English and Russian** (with groups
  and without groups)»
- Состав каталога (gh api contents): `LICENSE` 1 073 · `README.md` 4 987 · каталог **`With groups`**
  · каталог **`Without groups`**
- 🔴 Это ровно то, что требовалось в задании — «перечень с соответствием MCC→бытовая категория»,
  причём с русскими наименованиями и уже сгруппированный. Файлы внутри каталогов не перечислены
  (бюджет исчерпан).

### Официальные списки (НСПК/Мир, ЦБ РФ, Visa/Mastercard)

🔴 **НЕДОБЫТО.** До этих источников бюджет вызовов не дошёл. Ни один официальный PDF/страница
в этой сессии не запрашивались — записывать как «нет» нельзя.

## 4.2 🔴 БИК — справочник ЦБ РФ. ДОБЫТО ПОЛНОСТЬЮ, реквизиты точные

- **Точный URL шаблона (ежедневный):**
  `https://www.cbr.ru/vfs/mcirabis/BIKNew/YYYYMMDDED01OSBR.zip`
  Проверено на дату сессии: `https://www.cbr.ru/vfs/mcirabis/BIKNew/20260917ED01OSBR.zip`
- Канал: `curl` с браузерным UA. **HTTP 200**, `content-type: application/zip`,
  `content-length: 108334` (108 КБ), скачан целиком 17.09.2026.
- 🔴 Особенность доступа: домен под **ddos-guard** (`server: ddos-guard`, ставит cookie
  `__ddg1_/__ddg8_/__ddg9_/__ddg10_`). ZIP при этом отдаётся без капчи. Страница
  `https://www.cbr.ru/s/newbik` — **HTTP 301** на `/Queries/XsltBlock/File/101478?fileId=0`
  (то есть `newbik` это редирект-обёртка, не прямой файл).
- **Содержимое архива (unzip -l):** ровно один файл — **`20260917_ED807_full.xml`, 719 579 байт**,
  дата в архиве `09-16-2026 21:01`. Имя внутри = `YYYYMMDD_ED807_full.xml`.
- **Формат — ED807, кодировка WINDOWS-1251.** Корневой элемент дословно:
  `<ED807 xmlns="urn:cbr-ru:ed:v2.0" EDNo="707458709" EDDate="2026-09-16" EDAuthor="4583001999"
  CreationReason="FCBD" CreationDateTime="2026-09-16T18:00:52Z" InfoTypeCode="FIRR"
  BusinessDay="2026-09-17" DirectoryVersion="1">`
  🔴 Обратить внимание: `EDDate` = 2026-09-16, а `BusinessDay` = 2026-09-17 — файл публикуется
  накануне операционного дня, к которому относится. Это влияет на логику ежедневного обновления.
- **Структура записи** (дословно первая запись):
  `<BICDirectoryEntry BIC="040397100"><ParticipantInfo NameP="..." CntrCd="RU" Rgn="03"
  Ind="350000" Tnp="г" Nnp="Краснодар" Adr="ул Орджоникидзе, 155" DateIn="2011-01-11"
  PtType="52" Srvcs="3" XchType="1" UID="0397002001" ParticipantStatus="PSAC"></ParticipantInfo>
  <Accounts Account="40116810900000010001" RegulationAccountType="TRSA" CK="99"
  AccountCBRBIC="040397002" DateIn="2013-02-25" AccountStatus="ACAC"></Accounts>…`
  Вторая запись содержит дополнительно `RegN="3553-Б"` (регистрационный номер кредитной
  организации) — то есть у коммерческих банков есть `RegN`, у подразделений Банка России нет.
- Лицензия: отдельного лицензионного текста у выгрузки нет; это официальная публикация Банка
  России (справочник БИК публикуется в силу нормативных требований). Формально-юридическую
  оценку права на использование должен дать лидер/юрблок — подагент её не выносит.

## 4.3 ИНН → ОКВЭД (ФНС / ЕГРЮЛ)

### 🔴 Проверка локального диска: НУЖНЫХ ДАННЫХ ТАМ НЕТ

Каталог `/Users/vasyaevdokimov/raw-originals/finpilot-data/datagov/` осмотрен (`ls`, `head`),
содержимое на 17.09.2026:

| Файл | Размер | Что это на самом деле |
|---|---|---|
| `datagov_registry_2026-09-17.csv` | 2.9 МБ | реестр наборов данных (метаданные) |
| `datagov_registry_2026-09-17.json` | 12 МБ | то же в JSON |
| `fns_1ddk_data-20260101-structure-20260101.csv` | 30 КБ | **форма 1-ДДК** — агрегированная налоговая статистика по субъектам РФ |
| `fns_1ddk_structure-20260101.csv` | 28 КБ | описание полей 1-ДДК |
| `minek_mecdata_data-2026-04-10.csv` | 15 КБ | месячные показатели Минэка по районам |
| `minek_mecdata_structure-2026-04-10.csv` | 919 Б | описание полей |

Содержимое `fns_1ddk` дословно (первая строка структуры):
`"GA","Subjects of the Russian Federation","Субъекты Российской Федерации","text"`;
`"GB", … "Общая сумма дохода, заявленная налогоплательщиками-физическими лицами … (тыс.руб.)"`.
Строка данных: `"Белгородская область","231396035","54","4053",…`

🔴 **Вывод по факту: это агрегаты по регионам, а НЕ реестр организаций. Соответствия ИНН→ОКВЭД
на диске НЕТ ни в каком виде.** Прежнее предположение задания («на диске уже частично лежит»)
не подтвердилось — лежат данные другой природы.

### Внешние источники ИНН→ОКВЭД

🔴 **НЕДОБЫТО.** `data.nalog.ru` / выгрузки ЕГРЮЛ / `bus.gov.ru` в этой сессии не запрашивались —
бюджет вызовов закончился на BIK и MCC. Формат, лицензия, объём и порядок обновления неизвестны.
Запрет на установку российского корневого сертификата (условие сессии) может отдельно осложнить
доступ к `nalog.ru` — это надо проверить замером, а не предполагать.

---

# 5. ДЕТЕРМИНИРОВАННАЯ «ПАМЯТЬ ПРАВОК» ПОЛЬЗОВАТЕЛЯ

## 5.1 Как реализовано в открытых проектах

**Actual Budget (MIT).** Механизм — не отдельная таблица переопределений, а **правило как
объект данных**: правка пользователя превращается в правило с условием по `imported_payee`
и действием `SetCategory`-аналогом. Разрешение конфликтов — `rankRules`/`OP_SCORES` (§2.2.3):
точное совпадение (`is`, 10 баллов, ×2 за однородность) всегда перебивает эвристику
(`contains`/`matches`, 0 баллов). Раздельные поля `imported_payee` / `payee` дают опору
для правила «эта сырая строка банка → всегда эта категория».

**Mateush et al. 2018 (§1.1)** — три уровня меток в продакшне финансового учреждения, дословно:
«samples labeled manually, samples labeled by **user rules**, samples labeled by
**user-independent rules**, and samples that could not be labeled by any rule». Порядок
приоритета в их системе (дословно): сначала модель, при null-метке — user-independent rule,
иначе null. В детерминированной системе тот же порядок читается наоборот: ручная метка →
правило пользователя → общее правило → «не определено».

**Salt Edge** заявляет поддержку в API: «Supports user-defined categories» (§1.7).

## 5.2 Почему это НЕ обучение — аргументы, найденные в материале

1. **Нет функции потерь и нет обобщения.** Запись «строка X → категория Y» применяется только
   к точному совпадению X. Сравнить с Mateush: их overriding score **26.4 % (AP)** и
   **11.9 % (CP)** — это доля случаев, где ML ОБОБЩИЛ ручную правку на другие транзакции.
   Детерминированная память правок по определению даёт overriding 0 % за пределами точного ключа.
   Числовая цена отказа от обучения, таким образом, замерена именно этой метрикой.
2. **Результат воспроизводим и объясним.** Каждая метка трассируется до конкретной записи;
   у Actual это буквально правило, которое пользователь видит и может удалить.
3. **Нет параметров, подбираемых по данным.** `OP_SCORES` — константы, заданные разработчиком,
   а не обученные веса.

## 5.3 Риски (из кода и статей, не из головы)

- **Конфликт правил.** Решается численным приоритетом: Actual складывает баллы условий и
  удваивает за однородно-точные правила; регулярка весит 0. Без такой схемы порядок применения
  правил становится неопределённым.
- **Нулевой вес `contains`/`matches`** означает: правило на подстроке «MAGNIT» не перебьёт
  правило на точной строке — то есть широкие правила надо считать слабыми ПО ПОСТРОЕНИЮ.
- **Стадии `pre`/`null`/`post`** нужны, чтобы нормализация не конкурировала с категоризацией
  за приоритет — иначе правило нормализации и правило категоризации попадут в одну очередь.
- **Непокрытый остаток.** Mateush: rule-based coverage **76.4 %** на переводах — то есть ~24 %
  транзакций правила не закрывают вообще (для карт 99.2 %, разница между каналами огромна).
  Salt Edge/Yodlee вводят явное ведро `Uncategorized` — дословно у Yodlee: «Any transaction
  that is not categorized is marked as **Uncategorized**».
- **Масштабируемость правил** — критика авторов дословно: «The rules-based approach is not
  scalable as it requires rules to be maintained for every business and type of transaction.»
- **Непоследовательность ручных меток** — «The crowdsourcing approach leads to inconsistencies»;
  у Mateush метки шести сотрудников на 109 транзакциях уже дали противоречия
  («despite inconsistencies between crowdsourced labels»).

---

# НЕДОБЫТОЕ (со причиной по каждому пункту)

## По п.1 (замеры)
1. **Числа Meniga** (Coverage of card transactions / Transaction categorisation accuracy).
   Причина: подписи метрик на странице есть, сами значения отрендерены графикой и в текстовую
   выдачу Exa не попали. Канал: Exa. Лечится скриншотом страницы либо их PDF-отчётом.
2. **Числа покрытия Plaid и Nordigen.** Причина: бюджет вызовов исчерпан, отдельный поиск
   не запускался. Не «нет», а «не искали».
3. **Полный текст Lecci & Hanne с MDPI.** Причина: не запрашивался прямо; по условиям сессии
   MDPI отдаёт 403 на `curl`, штатный обход — `r.jina.ai` (не пробовался, бюджет).
   Highlight-текст Exa покрыл ключевые числа, но таблицы 3–5 целиком не видны.
4. **Ojala** (цит. как [19] у Lecci & Hanne) — реквизиты и числа. Причина: не искался.
5. **Датасет García-Méndez** — доступен «on request», то есть недобываем автоматически в принципе.

## По п.2 (исходники)
6. **Синтаксис CSV rules hledger** (`hledger import`) и API `beangulp`. Причина: бюджет.
   Лицензии выяснены (GPL-3.0 / GPL-2.0), код всё равно непригоден к переносу — приоритет низкий.
7. **Байесовский матчер GnuCash** — файл, строка, лицензия через API. Причина: бюджет.
   🔴 Это единственная незакрытая «серая зона» из задания и по существу важна: если приём
   классифицируется как обучение, он под запретом владельца.
8. **Правила категоризации внутри плагинов ZenPlugins.** Причина: бюджет; лицензия GPL-3.0
   делает код непригодным, ценность только как карта форматов банков РФ.
9. **Текущее расположение триггеров Firefly III** — каталог `Triggers/` даёт HTTP 404,
   куда переехали условия (в `Engine/` или `Expressions/`) не выяснено. Причина: бюджет.

## По п.3 (нечёткое сравнение)
10. **Раздел F.33.5 pg_trgm «Text Search Integration»** и конфигурация FTS для **русского языка**
    (`russian` snowball, `unaccent`, словари). Причина: страница добыта целиком (42 191 байт),
    но до этого раздела чтение не дошло — текст на диске в `/tmp/pgtrgm.html` уже есть,
    добирается без сети.
11. **Числа скорости RapidFuzz** и любые замеры «Левенштейн vs Jaro-Winkler vs триграммы
    на банковских строках». Причина: не найдено ни одного источника с числами за отведённый
    бюджет. Это честный отрицательный результат по узкому вопросу, но поиск был неглубокий.
12. **Подтверждение сложности Aho-Corasick O(n+m+z)** первоисточником. Причина: принято как
    учебниковый факт, помечено [ОЦЕНКА].

## По п.4 (справочники)
13. **Официальные списки MCC** — НСПК/Мир, ЦБ РФ, публичные PDF Visa/Mastercard.
    Причина: не запрашивались вовсе (бюджет ушёл на BIK и GitHub-датасеты). 🔴 Самый крупный
    непокрытый пункт задания.
14. **Содержимое `greggles/mcc-codes`** (`mcc_codes.json`, 265 156 Б).
    Причина: канал оборвался — `curl: (28) Operation timed out after 20006 ms with 0 out of
    265156 bytes received`. Файл существует (подтверждено API), просто не скачан.
15. **Перечень файлов внутри `Oleksios/Merchant-Category-Codes`** (каталоги `With groups` /
    `Without groups`) и сами русские наименования категорий. Причина: бюджет.
16. **ИНН → ОКВЭД: формат, лицензия, объём, регламент обновления** (`data.nalog.ru`, выгрузки
    ЕГРЮЛ, `bus.gov.ru`). Причина: бюджет исчерпан. Дополнительный риск: запрет на российский
    корневой сертификат может закрыть доступ к `nalog.ru` — это надо ЗАМЕРИТЬ, не предполагать.
17. **Юридическая оценка права на использование справочника БИК** в коммерческом закрытом
    продукте. Причина: вне компетенции подагента, данные для оценки собраны (§4.2).

## Ограничения канала за сессию (замер)
- `WebFetch` не использовался по указанию лидера.
- `curl` с браузерным UA: `postgresql.org` 200, `cbr.ru` 200 (под ddos-guard),
  `raw.githubusercontent.com` — 3 успеха и **1 таймаут 20 с**; канал действительно рваный.
- `gh api`: 8 успешных вызовов, 1 HTTP 404 (несуществующий путь Firefly), 1 пустая выдача
  (`/search/repositories` с длинной фразой `merchant category code mcc list` вернул ноль —
  короткий запрос `mcc codes` сработал; это особенность GitHub search, не отказ канала).
- Exa: 2 вызова, оба успешны, суммарно ~93 КБ текста, включая полные тексты статей мимо пейволла
  Springer (институтский препринт Тартуского университета) и arXiv.
- `r.jina.ai` — не потребовался, не пробовался.
- OpenAlex / Crossref / Semantic Scholar — не потребовались, не пробовались.

Инструментальных вызовов израсходовано: 22 из 25.

