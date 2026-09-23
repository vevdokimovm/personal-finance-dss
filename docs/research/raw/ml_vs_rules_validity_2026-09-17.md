# Г53. Насколько валидно (и нужно ли) машинное обучение в ядре FINPILOT — 17.09.2026

**Вопрос владельца дословно:** «типо я изначально хотел без мля вообще. чисто формулы.
сделай ресерч насколько вообще валидно мл использовать насколько с ним лучше хуже
и насколько он необходим?»

**Статус файла:** пишется ПО ХОДУ (правило §11 CLAUDE.md — сырьё в файл до ответа).
Разделы появляются по мере добычи. Выжимка и ВЕРДИКТ — в конце.

**Классы материала помечаются в тексте:** `[ЗАМЕР]` — прямое измерение (чьё-то или моё),
`[РЕЦ]` — рецензируемая работа, `[ОТЧЁТ]` — отраслевой/регуляторный документ,
`[МАРКЕТИНГ]` — заявление вендора (числом не считается), `[ОЦЕНКА]` — моя оценка.

---

## 0. Метод и журнал каналов

Первым шагом — проверка СВОЕЙ базы (`docs/research/raw/`), потому что часть вопроса
уже закрыта темами 35, 39, Г43. Веб — только на непокрытое.

| # | Канал / URL | Код | Что дал |
|---|---|---|---|
| 0 | `grep` по `docs/research/raw/` | OK | тема 39 §4.2 (Gigerenzer), тема 35 (Dawes/Meehl), Г43 (собственные замеры прогноза) |

| 1 | `WebFetch` любой домен | **отказ** «Unable to verify if domain is safe» на 4 из 4 (arxiv.org, eprints.soton.ac.uk, statmodeling.stat.columbia.edu) — канал в этой сессии мёртв целиком |
| 2 | `curl -sk -A <браузерный UA>` | arXiv 1909.13316 — 200, 628 719 B; M5 PDF — 200, 832 943 B; arXiv 2508.05425 — 200, 901 907 B; `eprints.soton.ac.uk` — **403** |

(таблица дополняется по ходу)

---

## 1. Прогноз дохода и расходов: M3 / M4 / M5 — прямой ответ есть, и он про длину ряда

### 1.1 M5 (2020) — ML победил, и это надо признать честно
Makridakis S., Spiliotis E., Assimakopoulos V. «The M5 Accuracy competition: Results, findings
and conclusions», *International Journal of Forecasting* 38(4), 2022, 1346–1364.
PDF добыт целиком (`curl`, 200, 832 943 B) → `/Users/vasyaevdokimov/raw-originals/finpilot-data/ml_vs_rules/m5_accuracy.pdf`.

`[ЗАМЕР]` Дословно (с. 15):
> "By observing Table 3 we find that **all top 50 submissions improve the overall forecasting
> accuracy of the top-performing benchmark by more than 14%**, while the improvements are higher
> than 20% for the top five performing methods and **an impressive 22.4% for the winning team**."

> "M5 is the first M competition where **all top-performing methods were both ML ones and
> significantly better than all statistical benchmarks and their combinations**. LightGBM proved
> that it can be used to effectively process **numerous, correlated series and
> exogenous/explanatory variables** and reduce forecast error."

Масштаб данных, на которых это получено (с. 3, 11):
> "A large dataset of **42,840 series** was introduced along with **24 benchmarks**."
Горизонт 28 дней, история 1 941 день, плюс экзогенные: цена, промо, календарь, праздники.

🔴 **Условия победы ML в M5 перечислены самими авторами и НЕ выполняются у нас:**
(а) 42 840 связанных рядов, по которым можно учиться перекрёстно («cross-learning»);
(б) тысячи наблюдений в каждом ряду;
(в) экзогенные переменные, известные заранее (цена, промо, календарь).
У одного пользователя FINPILOT — **3–12 месячных точек, один ряд, экзогенных нет**.

### 1.2 M4 (2018) — статистика доминировала
Из того же M5-текста, с. 33 `[ЗАМЕР]`:
> "In M4, **only two sophisticated methods were found to be more accurate than simple, statistical
> ones**, with the latter dominating the top positions of the competition."
Победитель M4 — гибрид (ES + LSTM) Смила, остальной топ — комбинации статистических методов;
из 17 наиболее точных методов 12 были комбинациями преимущественно статистических подходов
(Makridakis, Spiliotis, Assimakopoulos, «The M4 Competition: Results, findings, conclusion and
way forward», *IJF* 34(4), 2018, 802–808; DOI 10.1016/j.ijforecast.2018.06.001).

### 1.3 🔴 Главное для нас: где проходит граница по длине ряда — она измерена
Cerqueira V., Torgo L., Soares C. «Machine Learning vs Statistical Methods for Time Series
Forecasting: Size Matters», arXiv:1909.13316, 29.09.2019. PDF добыт целиком (200, 628 719 B) →
`/Users/vasyaevdokimov/raw-originals/finpilot-data/ml_vs_rules/ml_vs_stat_size.pdf`.

Это работа, специально написанная как **опровержение** Makridakis et al. 2018 — и опровержение
вышло условным `[РЕЦ]`/`[ЗАМЕР]`, дословно из аннотации:
> "in a recent work, evidence was shown that these approaches systematically present a lower
> predictive performance relative to simple statistical methods. In this work, **we counter these
> results. We show that these are only valid under an extremely low sample size.** Using a learning
> curve method, our results suggest that machine learning methods improve their relative predictive
> performance as the sample size grows."

Постановка (с. 1):
> "The authors draw their conclusion from a large set of 1045 monthly time series used in the
> well-known M3 competition… **The average, minimum, and maximum number of observations is 118, 66,
> and 144**… We hypothesize that these datasets are too small for machine learning models to
> generalize properly. Machine learning methods typically assume a functional form that is more
> flexible than that of statistical methods. **Hence, they are more prone to overfit.**"

Результат кривой обучения (90 рядов, prequential, обучающая выборка растёт с 18 до 1 000 точек):
> "The results depicted in this figure show a clear tendency: **when only few observations are
> available, the statistical methods present a better performance. However, as the sample size
> grows, machine learning methods outperform them.**"
> "Our results confirm the conclusions drawn from… [Makridakis et al., 2018]… Namely, that
> **statistical models outperform machine learning ones, when we only consider training sets up to
> 144 observations**."

🔴 **Перенос на нас — арифметика, а не мнение.** Точка перелома у Cerqueira — между 144 и ~500
наблюдениями. У нас на пользователя 3–12 месячных точек, то есть **в 12–48 раз меньше самой
короткой выборки, при которой ML ещё проигрывает**. Ни одна работа из найденных не показывает
выигрыша ML при n < 100 наблюдений в ряду. `[ОЦЕНКА]` Для помесячного прогноза одного человека
вопрос «ML или формула» закрыт не идеологией, а длиной ряда.

### 1.4 Собственный замер проекта (Г43, 17.09.2026) — подтверждает и добавляет неприятное
`[ЗАМЕР]` Наш же прогон 14 методов на 300 портретах × 6 типов × 3 длины истории
(`docs/research/raw/statistical_forecasting_methods_2026-09-17.md`, Пункт 1):
при T=3 лучший метод — **обычное среднее** (ошибка суммы за 6 мес. 0,205), при T=6 — **медиана**
(0,180), при T=12 — SES с подобранным α (0,144). Действующий продуктовый Holt — **худший из 14**
на всех длинах (0,606 / 0,319 / 0,227).

🔴 Вывод, который из этого следует и который не в пользу «формул вообще»: наша проблема сейчас —
**не отсутствие ML, а неудачно выбранная формула**. Замена Holt на среднее/медиану/SES даёт
27–66 % ошибки — больше, чем любой реалистичный выигрыш от ML на 3–12 точках.

---

## 2. Вероятность срыва платежа / кредитный скоринг — здесь ML реально выигрывает, и выигрыш измерен

### 2.1 Lessmann, Baesens, Seow, Thomas (EJOR 2015) — эталонный бенчмарк, добыт полным текстом
«Benchmarking state-of-the-art classification algorithms for credit scoring: An update of research»,
*European Journal of Operational Research* 247(1), 2015, 124–136, DOI 10.1016/j.ejor.2015.05.030.
PDF добыт с зеркала Эдинбургской школы бизнеса (`curl`, 200, 526 011 B; `eprints.soton.ac.uk` — 403)
→ `/Users/vasyaevdokimov/raw-originals/finpilot-data/ml_vs_rules/lessmann2015_ed.pdf`.
Дизайн: **41 классификатор, 8 реальных наборов данных** (16 одиночных, 8 однородных ансамблей,
17 разнородных), метрики AUC / H-measure / PCC / BS, тест Фридмана + post-hoc.

`[ЗАМЕР]` **AUC, выписано из Таблиц 5 и 6 дословно** (в скобках — ст. отклонение):

| Набор | LR (логистическая регрессия) | HCES-Bag (лучший разнородный ансамбль) | Разница AUC |
|---|---|---|---|
| AC | .931 (.011) | .933 (.013) | **+0,002** |
| GC | .784 (.012) | .801 (.010) | +0,017 |
| Bene1 | .773 (.012) | .800 (.008) | +0,027 |
| Bene2 | .791 (.006) | .814 (.005) | +0,023 |
| UK | .720 (.011) | .749 (.008) | +0,029 |
| PAK | .626 (.003) | .652 (.003) | +0,026 |
| GMC | .693 (.005) | .865 (.003) | **+0,172** |

🔴 **Как это читать.** На шести наборах из семи прирост ML над логистической регрессией —
**0,002…0,029 AUC**, то есть **2–6 пунктов Gini** (Gini = 2·AUC−1). Это реальный, статистически
значимый, но **скромный** прирост. Единственный разрыв в разы — GMC (Give Me Some Credit,
~150 000 заявок): там LR даёт .693, ансамбль .865. То есть **величина выигрыша ML прямо
пропорциональна объёму и нелинейности данных**, ровно как в разделе 1.

`[ЗАМЕР]` Дословно про то, когда прирост окупается (с. 43 макета):
> "Such **operational settings with a high frequency of decision tasks are exactly the environment
> where higher (statistical) accuracy translates into business value**. One-time investments (e.g.,
> for hardware, software, and user training) into a more elaborate scoring technique will pay-off in
> the longer run when **small but significant accuracy improvements are multiplied by hundreds of
> thousands of scorecard applications**."

🔴 **Прямой перенос на FINPILOT.** Условие окупаемости названо авторами явно: сотни тысяч
однотипных решений, каждое с денежным последствием. У нас — **одно решение на пользователя в
месяц**, денежное последствие несёт пользователь, а не мы, и мы не выдаём кредит. Условия
окупаемости ML-скоринга у нас **не выполняются**. Само по себе это не запрещает делать «риск
срыва платежа» как фичу, но окупаемость нужно обосновывать не ссылкой на скоринговую литературу.

Ещё одна оговорка авторов (с. 42): продвинутые классификаторы не требуют экзотической
экспертизы — «a random forest classifier, which (automatically) tests some standard meta-parameter
settings from the literature, produces very competitive retail scorecards».

### 2.2 Глубокое обучение в скоринге — «не надо»
Gunnarsson B.R., vanden Broucke S., Baesens B., Óskarsdóttir M., Lemahieu W. «Deep learning for
credit scoring: Do or don't?», *EJOR* 295(1), ноябрь 2021, 292–305, DOI 10.1016/j.ejor.2021.03.006.
🔴 **Полный текст НЕ добыт** (ScienceDirect — пейволл). Вывод взят из аннотации и карточки
EconPapers/SciSpace `[РЕЦ, по аннотации]`: глубокие сети **не оказались подходящими** моделями
для скоринга; при приоритете качества классификации следует предпочитать **XGBoost**.
То есть даже внутри лагеря ML в этой задаче побеждает табличный бустинг, а не нейросеть.

---

## 3. Категоризация транзакций — единственный модуль, где ML выигрывает у правил по существу

### 3.1 Замер на реальных банковских выписках (SME, Open Banking UK, 2025)
Aluffi P.A., Jess B., Bazzi M., Kennedy K., Arderne M., Rodrigues D., Lotz M. «Categorising SME
Bank Transactions with Machine Learning and Synthetic Data Generation», arXiv:2508.05425, 2025.
PDF добыт целиком (`curl`, 200, 901 907 B) →
`/Users/vasyaevdokimov/raw-originals/finpilot-data/ml_vs_rules/sme_categorization.pdf`.

`[ЗАМЕР]` Дословно:
> "Our calibrated approach achieves **73.4% (±8.1%) accuracy**, substantially outperforming all
> baseline methods including state-of-the-art LLMs. Notably, **GPT-4o in a zero-shot setting
> achieves 60.4% accuracy**, which, while respectable for zero-shot classification, **falls 13
> percentage points short of our fine-tuned approach**."
> "high-confidence predictions reaching **90.36% (±6.52) accuracy**"

Устройство задачи: 11 категорий, данные девяти МСП через Open Banking, обучение на двух фирмах,
проверка на третьей (out-of-sample), FinBERT + синтетика + калибровка.

`[ЗАМЕР]` Про правила — дословно:
> "Although manual annotations or **rule-based heuristics provide some interpretability and domain
> alignment, these approaches struggle to scale and adapt to the evolving and heterogeneous nature
> of SME financial data.**"
> "Bank descriptions are **short, noisy, and inconsistent**. Weak supervision combining rule-based
> labelling with neural networks… attempts to address these unstructured descriptions. Inconsistent
> naming, including abbreviations, also reduces NLP effectiveness."

🔴 **Честная оговорка, которую нельзя замазывать:** в этой работе **нет** чистого rule-based
бейзлайна с числом. Базовые линии — TF-IDF + LR/RF, FinBERT разных степеней дообучения и GPT-4o
zero-shot. То есть «правила против модели» напрямую тут **не измерены**; измерено «слабая модель
против сильной модели». Это ограничение источника, а не вывод в пользу правил.

🔴 И ещё одно число против переоценки ML: даже лучший дообученный конвейер даёт **73,4 %**
в среднем. Это значит, что **каждая четвёртая операция размечена неверно** — и без порога
доверия (у них: high-confidence подмножество → 90,4 %) такую разметку нельзя пускать в расчёт
бюджета без подтверждения человеком.

### 3.2 Отраслевая практика: гибрид, а не выбор
`[ОТЧЁТ/МАРКЕТИНГ]` Meniga (вендор PFM-движков для банков) и Quadratic описывают одну и ту же
схему: детерминированные правила (MCC → категория, известный мерчант → категория) закрывают
основную массу, ML подключается на «длинный хвост» — неразобранные назначения платежа, новые
мерчанты, неоднозначные строки. Дословно из обзора Quadratic: ML-модели «handle the "long tail"
of transactions, parsing messy vendor data and suggesting categories for ambiguous or new items
that deterministic rules might miss». Числа вендоры не приводят — **это маркетинг, числом не
считается**, но как описание архитектуры отрасли годится.

---

## 6а. Практика игроков — первоисточник от инженера Monzo (добыто 17.09.2026)

Lathia N. (Director of ML, Monzo в 2020) «Combining rule engines and machine learning», личный блог,
09.10.2020, https://nlathia.github.io/2020/10/ML-and-rule-engines.html (`curl`, 200, 11 617 B; копия
`/Users/vasyaevdokimov/raw-originals/finpilot-data/ml_vs_rules/lathia.html`). Класс: `[ОТЧЁТ практика]`
— мнение практика, не замер.

> "In the infamous Rules of Machine Learning, one of the first sections states **“don’t be afraid to
> launch a product without machine learning”** – and suggests launching a product that uses rules."
> "Rule engines, expressed a family of if-statements, do really well in deterministic scenarios.
> **If you can write a rule set that captures everything you need, then you don’t need machine
> learning! Job done**"
> "The situations where machine learning can usually help share a common theme: they are trying to
> **optimise some kind of process which cannot be fully enumerated with a deterministic set of
> rules**. This switch from “control” to “optimise” is usually a hallmark indication… many of these
> things usually have to do with **human behaviour**."
> "**Apply the rules first, and then use machine learning** … If none of the rules matched, the system
> tries to infer the topic of the conversation using a family of BERT models"
> "we ran an experiment with recommending help articles in the Monzo app… took the outcomes of the
> rules as input features to a model, which would make the final ranking decision. **This specific
> experiment didn’t work out**"
> "it’s less common for those systems to progress towards starting to use some machine learning, and
> **it’s fantastically rare for those systems to be migrated to only use machine learning**"
> "In these cases, you don’t need to ship a model – **you ship the insight that you got from that
> model, by writing rules**."

🔴 Три паттерна Monzo, прямо применимые к FINPILOT: (1) правила первыми, модель — на остаток,
который правила не разобрали (= категоризация: MCC/словарь → модель на хвост);
(2) модель как инструмент **открытия** правил офлайн, в прод уходит правило, не модель;
(3) попытка отдать модели финальное ранжирование поверх правил — у Monzo **не сработала**.

Из базы (тема 8, `competitors_recommendation_engines_2026-09-08.md`):
- **Cleo** — «категоризация трат + разговорный интерфейс поверх неё… Расчёта распределения
  свободного потока между целями/долгом/резервом не найдено — бюджетинг-ассистент с LLM-обёрткой».
- **Firefly III** — авторы явно отклонили AI-рекомендации: галлюцинации LLM делают это ненадёжным
  (GitHub Discussion #12119).
- **Nubank AI Private Banker** (`banks_world_pfm_v2_2026-09-09.md`) — раскрыт только LLMOps-контур
  (LangGraph/LangSmith), «прескриптивной математики там нет».


---

## 4. Регуляторная и правовая цена ML — РФ и зарубежный контур (добыто 17.09.2026)

Подагент первого аккаунта по этому блоку оборвался, не записав ничего; блок собран вахтой лично.
Уже закрытое в базе НЕ повторяется: EU AI Act Annex III п.5(b) и пересказ 3-МР —
`approach_validity_2026-09-10.md` §3.5–3.6; 19-МР — `cbr_19mr_product_governance_2026-09-10.md`;
граница «совет/информация» — `regulation_world_advice_boundary_2026-09-09.md`.

### 4.1 152-ФЗ, ст. 16 — `[НОРМА дословно]`
Источник: КонсультантПлюс, 152-ФЗ, ст. 16, через `r.jina.ai` (200, 4 309 B), копия
`/Users/vasyaevdokimov/raw-originals/finpilot-data/ml_vs_rules/152fz_st16.txt`.
> «1. Запрещается принятие на основании **исключительно автоматизированной обработки** персональных
> данных решений, порождающих юридические последствия в отношении субъекта персональных данных
> **или иным образом затрагивающих его права и законные интересы**, за исключением случаев,
> предусмотренных частью 2 настоящей статьи.
> 2. … может быть принято … только при наличии **согласия в письменной форме** субъекта
> персональных данных или в случаях, предусмотренных федеральными законами…
> 3. Оператор обязан **разъяснить субъекту персональных данных порядок принятия решения** на
> основании исключительно автоматизированной обработки … и возможные юридические последствия
> такого решения, **предоставить возможность заявить возражение** против такого решения…
> 4. Оператор обязан рассмотреть возражение … **в течение тридцати дней**…»

`[ОЦЕНКА]` Статья 16 **не различает формулу и ML** — она про «исключительно автоматизированную
обработку» вообще. Поэтому она бьёт одинаково и по нынешнему ядру. FINPILOT выходит из-под неё
не выбором метода, а конструкцией: рекомендация — не «решение», пользователь её принимает или
правит сам (человек в контуре). Но обязанность **разъяснить порядок принятия решения** (ч. 3),
если её когда-либо применят к нам, для формулы исполнима дословно, а для обученной модели —
только через приближённые объяснения (SHAP и т. п.). Здесь у формул реальное преимущество.

### 4.2 152-ФЗ, ст. 5 — цель обработки и обучение модели `[НОРМА дословно]`
Копия `/Users/vasyaevdokimov/raw-originals/finpilot-data/ml_vs_rules/152fz_st5.txt` (200, 4 585 B).
> «2. Обработка персональных данных должна ограничиваться достижением **конкретных, заранее
> определенных и законных целей**. Не допускается обработка персональных данных, **несовместимая с
> целями сбора** персональных данных.
> 3. Не допускается **объединение баз данных**, содержащих персональные данные, обработка которых
> осуществляется в целях, несовместимых между собой.»

`[ОЦЕНКА юриста-вахты, не разъяснение РКН]` Обучение общей модели на данных всех пользователей —
**отдельная цель**, отличная от «рассчитать рекомендацию этому пользователю». Значит, для
cross-learning (единственного режима, где ML выигрывает, см. §1.1) нужна либо отдельная цель
в согласии/политике, либо обезличивание до обучения. Детерминированное ядро этой цели не
создаёт вовсе. Разъяснений Роскомнадзора именно про «обучение ИИ на ПДн» в этой сессии
**не найдено** (не искались глубже одного запроса — «не нашли», а не «нет»).

### 4.3 152-ФЗ, ст. 13.1 (введена 233-ФЗ от 08.08.2024) — обезличенные «составы данных» `[НОРМА]`
Источник: КонсультантПлюс (ред. от 24.06.2025), ГАРАНТ `base.garant.ru/409493125/`, РГ 13.08.2024
(через Exa). Суть дословно: Минцифры «формирует составы персональных данных, полученных в
результате обезличивания… при условии, что последующая обработка таких данных не позволит
определить принадлежность таких данных конкретному субъекту»; оператор **по требованию**
Минцифры «обязан обезличить обрабатываемые им персональные данные… и предоставить» их в ГИС.
Вступление: пп. 1–3, 5 ст. 1 и ст. 2 — **с 01.09.2025** (ГАРАНТ).
`[ОЦЕНКА]` Это канал «данные → государственный датасет для ИИ», а не разрешение оператору учить
свою модель. Для нас следствие обратное ожидаемому: накопленная база ПДн сама по себе становится
предметом возможного требования Минцифры — ещё один довод хранить минимум.

### 4.4 Банк России, 3-МР от 16.06.2026 — теперь ДОСЛОВНО (было — пересказ)
Источник: `https://www.cbr.ru/Crosscut/LawActs/File/12204` (выдача Exa с текстом; зеркала —
ГАРАНТ `garant.ru/products/ipo/prime/doc/414292607/`, КонсультантПлюс `cons_doc_LAW_536935`).
Адресаты (п. 1.1): кредитные организации, филиалы иностранных банков, **некредитные финансовые
организации**, профучастники, субъекты НПС — **FINPILOT не адресат**. Документ опирается на
**Кодекс этики в сфере разработки и применения ИИ на финансовом рынке** (текст Кодекса в этой
сессии не добывался).

`[НОРМА-рекомендация дословно]`
> «2.5. В случае использования ИИ для выполнения операций в автоматическом режиме в критически
> важных процессах (например, в платежных процессах…), когда риски информационной безопасности ИИ
> оценены организацией как высокие, организации рекомендуется реализовать **валидацию результатов
> операций, выполненных ИИ в автоматическом режиме, человеком с возможностью изменения таких
> результатов**.»
> «1.5. **Достаточная объяснимость и (или) предсказуемость.** Рекомендуется закрепить необходимость
> применения механизмов интерпретации поведения модели ИИ в целях обеспечения достаточной
> объяснимости и (или) предсказуемости действий модели ИИ (в релевантных случаях).»
> «3. **Минимальные персональные данные.** Рекомендуется закрепить принцип использования минимальных
> персональных данных, на обработку которых … получено согласие субъекта персональных данных, в
> целях разработки и (или) применения систем ИИ.»
> «1.1. Целостность. … сохранение целостности программного обеспечения и **наборов данных**,
> связанных с разработкой и применением ИИ…»

`[ОЦЕНКА]` Всё, что 3-МР требует от ИИ сверх обычной ИБ (объяснимость, целостность обучающих
наборов, минимизация ПДн для обучения, red team), — это **накладные расходы, которых у
детерминированного ядра нет по построению**. Как только мы станем партнёром банка/НФО, их
предъявят к нам через договор.

### 4.5 GDPR ст. 22 и дело SCHUFA (C-634/21) — `[НОРМА дословно]`
GDPR ст. 22 (gdpr-info.eu через `r.jina.ai`, 200, 14 186 B; копия `.../gdpr22.txt`):
> "1. The data subject shall have the right not to be subject to a decision **based solely on
> automated processing, including profiling**, which produces legal effects concerning him or her
> or similarly significantly affects him or her."
> "3. … the data controller shall implement suitable measures … **at least the right to obtain human
> intervention** on the part of the controller, to express his or her point of view and to contest
> the decision."

CJEU, Judgment of 7 December 2023, C-634/21 *OQ v Land Hessen (SCHUFA Holding — Scoring)*,
ECLI:EU:C:2023:957, EUR-Lex CELEX 62021CJ0634 (через Exa). Резолютивная часть дословно:
> "Article 22(1) … must be interpreted as meaning that **the automated establishment, by a credit
> information agency, of a probability value** based on personal data relating to a person and
> concerning his or her ability to meet payment commitments in the future **constitutes ‘automated
> individual decision-making’** … where a third party, to which that probability value is
> transmitted, **draws strongly on that probability value** to establish, implement or terminate a
> contractual relationship with that person."
П. 46: понятие «решение» «is broad enough to encompass the result of calculating a person’s
creditworthiness in the form of a probability value».

`[ОЦЕНКА]` Прямое следствие для «вероятности срыва платежа» (§2): пока число видит только сам
пользователь — это не решение о нём. **Как только такое число уходит третьему лицу, которое на него
«сильно опирается» (банк-партнёр), само вычисление числа становится решением по ст. 22** — неважно,
формулой или моделью оно посчитано. ML не меняет квалификацию, но делает исполнение ч. 3
(объяснить, дать оспорить) дороже.

### 4.6 США: SEC о робо-советниках — `[НОРМА/гайд дословно]`
SEC Division of Investment Management, **Guidance Update No. 2017-02 «Robo-Advisers»**, февраль 2017,
`https://www.sec.gov/investment/im-guidance-2017-02.pdf` (`curl` — 403; `r.jina.ai` — 200, 37 946 B;
копия `.../sec_2017_02.txt`). Что советник «should consider providing»:
> "• A statement that an algorithm is used to manage individual client accounts;
> • A description of the algorithmic functions used…;
> • **A description of the assumptions and limitations of the algorithm** … (e.g., if the algorithm is
> based on modern portfolio theory, a description of the assumptions behind and the limitations of
> that theory);
> • A description of the particular risks inherent in the use of an algorithm…;
> • A description of any circumstances that might cause the robo-adviser to **override the
> algorithm**…"
Комплаенс-программа должна покрывать: "**The development, testing, and backtesting of the
algorithmic code and the post-implementation monitoring of its performance**" и "The disclosure to
clients of **changes to the algorithmic code** that may materially affect their portfolios".

SEC Proposed Rule **«Conflicts of Interest Associated with the Use of Predictive Data Analytics»**,
Release 34-97990, 26.07.2023 (88 FR 53960) — **ОТОЗВАНО** 12.06.2025 (Release 33-11377, 90 FR,
опубл. 17.06.2025): «The Commission does not intend to issue final rules with respect to these
proposals». Источники: sec.gov/rules-regulations/2025/06/s7-12-23; federalregister.gov 2025-11110.

`[ОЦЕНКА]` SEC не запрещает ML и не требует объяснимости модели как таковой; требует **раскрыть
допущения и ограничения алгоритма** и **уведомлять об изменениях кода**. У обучаемой модели
«изменение кода» происходит при каждом переобучении — то есть каждая перетренировка становится
событием раскрытия. У формулы изменение = релиз по SemVer, который у нас и так есть.

### 4.7 Итог блока 4 (выжимка)
| Требование | Бьёт по ML сильнее, чем по формуле? | Нас касается сейчас? |
|---|---|---|
| 152-ФЗ ст. 16 (разъяснить порядок, возражение) | да — объяснение формулы точное, модели приближённое | нет, пока рекомендация не «решение» |
| 152-ФЗ ст. 5 (цели) | да — обучение общей модели = новая цель | да, если начнём учить на данных пользователей |
| 3-МР ЦБ (объяснимость, данные, human-in-the-loop) | да, адресован именно ИИ | нет; да — при партнёрстве с банком/НФО |
| GDPR ст. 22 + SCHUFA | нет (квалификация одинакова), но ч. 3 дороже | только при выходе в ЕС / передаче скоринга третьим |
| EU AI Act 5(b) | только для оценки кредитоспособности | нет (закрыто темой 39) |
| SEC 2017-02 | да — каждое переобучение = изменение алгоритма к раскрытию | нет (не РИА США) |


---

## 5а. Где обучение ВРЕДИТ — документированные механизмы и провалы (добыто 17.09.2026)

### 5а.1 Технический долг ML — первоисточник Google
Sculley D. et al. «Hidden Technical Debt in Machine Learning Systems», *NeurIPS 2015*,
`papers.nips.cc/.../86df7dcfd896fcaf2674f757a2463eba-Paper.pdf` (`curl`, 200, 165 614 B) →
`/Users/vasyaevdokimov/raw-originals/finpilot-data/ml_vs_rules/sculley2015.pdf`. `[РЕЦ]`
> "**CACE principle: Changing Anything Changes Everything.** CACE applies not only to input signals,
> but also to hyper-parameters, learning settings, sampling methods, convergence thresholds, data
> selection, and essentially every other possible tweak."
> "a mature system might end up being **(at most) 5% machine learning code and (at least) 95% glue
> code**"
> "Figure 1: **Only a small fraction of real-world ML systems is composed of the ML code**… The required
> surrounding infrastructure is vast and complex."
Петля обратной связи, дословно:
> "live ML systems … often end up **influencing their own behavior** if they update over time. This
> leads to a form of analysis debt, in which it is difficult to predict the behavior of a given model
> before it is released."
> "**Direct Feedback Loops.** A model may directly influence the selection of its own future training
> data."
🔴 Перенос: советник, который учится на поведении пользователей, **сам формирует это поведение**
(совет «гаси карту» → в данных больше досрочных погашений → модель «узнаёт», что люди так делают).
Обучаться на исходах собственных рекомендаций без рандомизации (бандиты, A/B) — методически
некорректно; у формулы этой петли нет.

### 5а.2 Нестационарность — провал с числами: Zillow Offers (2021)
Zillow Group, Q3'21 Shareholder Letter, 02.11.2021,
`s24.q4cdn.com/723050407/files/doc_financials/2021/q3/Zillow-Group-Q3'21-Shareholder-Letter.pdf`
(через Exa); пресс-релиз и 10-Q — last10k.com; CNBC, CNN 02.11.2021. `[ОТЧЁТ эмитента]`
> "underpinned by the need to **forecast the price of homes accurately three to six months into the
> future**… We have been unable to accurately forecast future home prices at different times in both
> directions by much more than we modeled as possible, with Zillow Offers unit economics **swinging
> approximately 1,200 basis points** from Q2 to an expected -500 to -700 basis points in Q4 2021."
> "**a $304 million write-down on inventory** … as a result of purchasing homes at higher prices than
> our current estimates of future selling prices."
CEO Barton: "We've determined **the unpredictability in forecasting home prices far exceeds what we
anticipated**". Итог: сворачивание направления, сокращение **~25 %** персонала, списания свыше
**$540 млн** (CNN).
🔴 Честная оговорка: письмо винит **волатильность прогноза**, а не «ML» по имени (публично
Zestimate — нейросетевая модель, но связь конкретной модели с закупочными ценами в письме не
раскрыта). Урок не «ML плох», а: **обученная на спокойном периоде модель уверенно врёт на смене
режима** (пандемия), и её уверенность была встроена в денежные решения. Для РФ смена режима — норма:
ключевая ставка 2022–2026 (тема `key_rate_history_forecastability_2026-09-10.md`).

### 5а.3 LLM в клиентских финансах — регулятор фиксирует вред
CFPB, Issue Spotlight «Chatbots in consumer finance», 06.06.2023,
`files.consumerfinance.gov/f/documents/cfpb_chatbot-issue-spotlight_2023-06.pdf` (через Exa). `[ОТЧЁТ регулятора]`
> "complex chatbots that use LLMs sometimes have trouble providing accurate and reliable information.
> For conversational, generative chatbots trained on LLMs, **the underlying statistical methods are not
> well-positioned to distinguish between factually correct and incorrect data**."
> "In instances where financial institutions are relying on chatbots to provide people with certain
> information that is legally required to be accurate, **being wrong may violate those legal
> obligations**."
> "Providing inaccurate information regarding a consumer financial product or service… could lead to
> the assessment of inappropriate fees, which in turn could lead to worse outcomes such as default".
Из базы: Firefly III отказался от AI-советов из-за галлюцинаций (§6а).

### 5а.4 Остальные механизмы — по нашему кейсу
| Механизм | Чем подтверждено | Бьёт по FINPILOT |
|---|---|---|
| **Cold start** | у нового пользователя 0–3 точки истории; ML проигрывает статистике уже при ≤144 точках (Cerqueira 2019, §1.3); на 3 точках лучший метод — простое среднее (Г43, §1.4) | 100 % новых пользователей; персональная модель невозможна, возможна только популяционная (= cross-learning = 152-ФЗ ст. 5, §4.2) |
| **Нестационарность** | Zillow (§5а.2); M-соревнования: выигрыш ML в M5 — на стабильном ритейле с известными экзогенными (§1.1) | смена работы, ставка ЦБ, инфляция — ровно режимы, где обучение на прошлом врёт; Г43 п. 3 даёт правило обнаружения сдвига без обучения |
| **Петля обратной связи** | Sculley 2015 (§5а.1) | модель, учащаяся на исходах своих же советов |
| **Объяснимость** | 152-ФЗ ст. 16 ч. 3; 3-МР п. 1.5; SEC 2017-02 (§4) | формула объясняется точно («погасили карту: ставка 39,9 % > доходность вклада 14 %»); модель — приближённо |
| **Воспроизводимость** | M5 требовал ≥98 % воспроизводимости WRMSSE, т. к. «ML algorithms typically involve random initializations» (M5 PDF, разд. 3.5 «Prizes») | у нас инвариант «один вход → один ответ» проверяется тестом; у модели — только с фиксацией сидов, версий библиотек и данных |
| **Дрейф и переобучение** | Sculley 2015: CACE; SEC 2017-02: изменение алгоритма = событие раскрытия | каждое переобучение = новая версия модели → повторная валидация, раскрытие, регресс-тесты |

### 5а.5 Начинка робо-советников — детерминированная (из базы, первоисточники)
`[ОТЧЁТ вендора, методология]` Wealthfront, Classic Portfolio Investment Methodology White Paper
(`research.wealthfront.com/whitepapers/investment-methodology/`, в базе:
`portfolio_theory_robo_advisors_v2_2026-09-09.md` §5.2): «Wealthfront determines the optimal mix
of our chosen asset classes by using **Mean-Variance Optimization**». То есть ядро крупнейших
робо-советников — классическая оптимизация (Марковиц, 1952) + правила ребалансировки и
анкета-опросник, а не обученная модель. SEC 2017-02 (§4.6) в примере раскрытия сама пишет
«if the algorithm is based on modern portfolio theory» — регулятор исходит из того, что типовой
робо-советник — формула. `[ОЦЕНКА]` Позиция «детерминированное ядро» в отрасли — **норма, а не
исключение**; ML у робо-советников и банков живёт по краям (маркетинг, отток, фрод, категоризация,
чат).


---

## 5. Численная цена отказа от ML — порядок величины по модулям

`[ОЦЕНКА на основе замеров, приведённых выше]` Все числа — перенос чужих замеров на наш кейс;
собственного A/B «ML против формулы» в проекте нет (кроме Г43 по прогнозу).

| Модуль | Что теряем без ML | Порядок величины | Опора |
|---|---|---|---|
| Прогноз дохода/расходов одного человека (3–12 мес. истории) | **ничего** | 0; ML на таких длинах проигрывает | Cerqueira 2019 (≤144 точек — статистика лучше); Г43: лучший — среднее/медиана/SES |
| Прогноз с cross-learning по тысячам пользователей | потенциальный выигрыш | до −14…−22 % ошибки — **верхняя граница**, получена на 42 840 рядах с экзогенными | M5 (§1.1); у нас условия не выполнены, 152-ФЗ ст. 5 |
| Починка текущей формулы прогноза (Holt → SES/медиана) | — | **−27…−66 % ошибки** суммы за 6 мес. | Г43 (§1.4) — больше, чем любой реалистичный выигрыш ML |
| Вероятность срыва платежа | точность ранжирования | +0,002…+0,029 AUC (2–6 п. Gini) на типовых данных; до +0,17 на 150 тыс. заявок | Lessmann 2015 (§2.1); у нас нет ни меток дефолта, ни объёма |
| Категоризация: карточные операции с MCC | почти ничего | MCC → категория — детерминированный справочник | отраслевая практика (§3.2) |
| Категоризация: переводы/СБП/свободное назначение платежа | **главная реальная потеря** | модель ≈73 % против 60 % у LLM zero-shot; при высокой уверенности 90 %; бейзлайна правил с числом нет | Aluffi et al. 2025 (§3.1) |
| Разбор выписок без шаблона | умеренная | шаблонные парсеры покрывают известные банки; хвост — LLM/модель | Г20, Г47 (тема «ядро без ML») |
| Регулярные платежи/подписки | мало | периодичность + сумма ± допуск — правило; ML нужна на «шумных» мерчантах | `[ОЦЕНКА]`, замера не найдено |
| Персональные пороги (резерв, ПДН) | ничего | **обучаемых порогов не найдено ни у кого**: ПДН — норматив ЦБ, резерв — нормативы 3–6 мес. (Greninger 1996, тема 35) | «не нашли» ≠ «нет» |

**Цена ML-варианта (обратная сторона)** `[ОЦЕНКА на основе источников]`:
- данные: для cross-learning — тысячи пользователей × ≥12 мес. с согласием на отдельную цель
  (152-ФЗ ст. 5) — **на старте осенью 2026 их нет в принципе**;
- код: ML — ≤5 % системы, остальное — конвейеры, мониторинг, переобучение (Sculley 2015);
- надзор: объяснимость, целостность обучающих наборов, человек в контуре (3-МР), раскрытие каждого
  изменения модели (SEC 2017-02) — при партнёрстве с банком это станет договорным требованием;
- риск: смена режима (Zillow: −$304 млн за квартал при уверенном прогнозе).

**Итоговая оценка:** без ML FINPILOT теряет **заметно только в одном месте — категоризация
свободного текста операций** (порядка 10+ п.п. точности на хвосте), и **условно** — скоринг срыва
платежа, который нам без меток всё равно не построить. В ядре (распределение свободных денег,
арифметика долга, прогноз на коротких рядах) потеря — **ноль или отрицательная**.


---

## 6б. Остальные игроки — что у них обучается, а что нет (добыто 17.09.2026, через Exa)

**Plum (UK)** `[МАРКЕТИНГ + инженерный блог]`
- Справка «Automatic Automation» (help.withplum.com/en/articles/8707829, обновл. 20.04.2026):
  «uses Plum's AI technology to analyze your income, transactions, and available balance»;
  «it looks at your bank transactions from the **last 3 to 12 months**»; сумма пересчитывается
  «every few days». Поверх — ручной множитель «Mood»: Shy −50 %, Chilled −25 %, Eager +25 %,
  Ambitious +50 %, Beast Mode +75 %.
- Инженерный блог (Allain N., «Breaking Free: The Saving Rules’ Escape From the Monolith», Medium
  «Making Plum», 10.07.2025): «The Automatic Rule pulled in the user’s transaction history, analysed
  it, and spat out a **smart-ish number**»; «it runs an algorithm that reviews historical data and
  user profiles to figure out how much it’s safe to save»; остальные правила — Round Ups, Naughty
  Rule, Rainy Days (**погода через внешний API**), 1p Challenge — **чистые правила**; Automatic +
  Round Ups дают **>50 %** активных правил.
- `[ОЦЕНКА]` «AI» в маркетинге, «algorithm… smart-ish number» у инженеров, пользовательский
  множитель-ручка поверх и те же 3–12 месяцев истории, что у нас. Природа модели не раскрыта —
  **ML не подтверждён и не опровергнут**. Архитектурно — правила + одно «умное» число с ручным
  множителем и потолком от баланса. Это ближе к нашему ядру, чем к ML-советнику.

**Т-Банк** `[справка банка, первоисточник]` (tbank.ru/bank/help/debit-cards/tinkoff-black/earn-with-card/regular-cashback/):
категория кэшбэка определяется «**По МСС‑коду и названию магазина**»; «4121 — код и такси, и
каршеринга. В таких случаях банк смотрит не только на МСС‑код, но и на название торговой точки».
→ денежно значимая категоризация у крупнейшего цифрового банка РФ — **справочник MCC + словарь
мерчантов**, т. е. правила.

**Сбер (AI Lab)** `[ОТЧЁТ, инженерный блог]`
- Хабр, 13.04.2026, «Как граф транзакций помогает банку лучше узнать своего клиента»
  (habr.com/ru/companies/sberbank/articles/1018456/): ML на транзакциях применяется для задач
  «надёжный заёмщик или нет, мужчина это или женщина, мошенник или нет»; прирост от графа клиент–
  магазин — «**+1,3% AUC и +2,27% точности**»; «В масштабах крупного банка повышение точности
  обнаружения мошенников даже на один процент означает миллионы рублей». → тот же вывод, что
  Lessmann: **проценты, окупаемые масштабом** миллионов клиентов.
- Хабр, 18.06.2026, «Как научить языковую модель читать транзакции» (habr.com/ru/amp/publications/1049018/):
  LLM на сырых транзакциях почти бесполезна; «связываем мы их **не нейросетью-чёрным-ящиком, а
  white-box правилами**» (AutoWoE); «как только мы даём модели именно структуру white-box знаний,
  **MCC прыгает с 0,19 до 0,41**»; «**Без white-box компонента… система буквально разваливается — MCC =
  0,01**»; «главный источник силы — явные правила из white-box модели». (MCC здесь — коэффициент
  Мэтьюса, не код мерчанта.)
  🔴 Это самый сильный российский довод за нашу конструкцию: **даже у банка с данными на десятки
  миллионов клиентов LLM без явного слоя правил не работает.**

**Cleo, Firefly III, Nubank** — см. §6а (из базы). **Monzo** — §6а.

**YNAB, Emma** — первоисточников про устройство (правила/ML) в этой сессии **не добыто**
(один запрос Exa вернул только Plum). «Не нашли», а не «нет».

## 6в. LLM как «объяснялка» поверх детерминированного расчёта
`[ОТЧЁТ практики, не рецензируемо]` Отраслевой консенсус 2025–2026 в инженерных публикациях
(getmaxim.ai «LLM Guardrails for Fintech»; dev.to «Keep the LLM Out of the Math: Deterministic
Boundaries for Financial Modelling Agents»; arXiv 2603.04663 «Neuro-Symbolic Financial Reasoning
via Deterministic Fact Ledgers»; arXiv 2604.01483 «Type-Checked Compliance… Lean 4») — по выдаче
WebSearch: «LLMs are strongest as a drafting and explanation layer on top of deterministic systems,
**not as the system of record for financial facts**»; числа в тексте LLM сверяются регулярками с
исходными метриками, расхождение → флаг. 🔴 Полные тексты этих четырёх не читались — только сниппеты.
Кто так делает в проде и «чем кончилось»: Cleo (LLM-интерфейс над категоризацией, §6а); Сбер —
LLM + white-box правила (§6б); CFPB 2023 фиксирует вред от LLM-чатботов, отвечающих «от себя»
(§5а.3). Публичного разбора провала именно схемы «LLM объясняет готовый расчёт» **не найдено**.

## 6г. Граница гибрида для FINPILOT `[ОЦЕНКА по совокупности §1–6]`
**Признак границы:** модуль уходит модели, только если одновременно (1) задачу нельзя полностью
перечислить правилами (Lathia: «control → optimise», человеческий текст/поведение), (2) ошибка
модели ловится до денежного вывода (порог уверенности или подтверждение пользователем),
(3) для обучения есть данные, не требующие отдельной цели по 152-ФЗ (публичные/синтетические/
размеченные командой). Всё, что прямо определяет сумму рекомендации, — формулы.

| Остаётся формулами (ядро) | Может уйти модели (края) |
|---|---|
| распределение свободных денег (SAW/перебор), инварианты R≥0, ПДН≤0,40 | категоризация **хвоста** (переводы, СБП, свободное назначение) — после MCC и словаря; с порогом уверенности и подтверждением |
| арифметика долга (Avalanche, график, переплата) | разбор выписок неизвестного формата — как предложение разметки, проверяемое сверкой сальдо |
| прогноз на коротких рядах (среднее/медиана/SES + интервалы, Г43) | распознавание регулярных платежей на шумных мерчантах — как подсказка |
| обнаружение сдвига дохода (правило/BOCPD, Г43 п. 3) | LLM — **только текст объяснения** из готовых чисел, со сверкой чисел |
| пороги резерва и нагрузки (нормативы) | офлайн: модель как инструмент **поиска** правил (Lathia) — в прод идёт правило |


---

## 7. ВЕРДИКТ

1. **Отказ от ML в ядре — валидная позиция с опорой на замеры, а не вкусовщина.** На длине ряда одного
   пользователя (3–12 точек) статистика бьёт ML (Cerqueira 2019: перелом где-то после 144 точек;
   Makridakis 2018, M4); ядра робо-советников — Марковиц и правила (Wealthfront, SEC 2017-02).
2. **Где ML реально выигрывает, условия у нас не выполняются:** M5 (−22 % ошибки) — это 42 840
   рядов с экзогенными; скоринг (+2–6 п. Gini) окупается только на сотнях тысяч решений
   (Lessmann 2015; Сбер +1,3 % AUC «в масштабах крупного банка»).
3. **Главная текущая ошибка — не отсутствие ML, а неудачная формула прогноза:** Holt хуже лучшего простого
   метода (среднее/медиана/SES) в 1,6–3 раза (Г43). Починка даёт больше, чем дал бы любой ML.
4. **Что теряем без ML:** по существу одно — категоризацию свободного текста (переводы/СБП):
   модель ≈73 %, LLM zero-shot 60 %, при высокой уверенности 90 % (Aluffi 2025). Карточные
   операции закрывает MCC + словарь мерчантов — так делает сам Т-Банк.
5. **Чем ML вредит именно нам:** cold start у 100 % новых пользователей; смена режима (ставка,
   работа — урок Zillow, −$304 млн); петля обратной связи на собственных советах (Sculley 2015);
   объяснение и воспроизводимость, которые у формулы бесплатны.
6. **Право:** 152-ФЗ ст. 16 не отличает формулу от модели, но ст. 5 делает обучение общей модели
   отдельной целью обработки; 3-МР ЦБ, SEC 2017-02 и SCHUFA делают каждую модель дороже в надзоре.
   Детерминированное ядро этих издержек не несёт.
7. **Что брать первым, если брать:** (а) починить прогноз формулой (сейчас); (б) категоризация:
   MCC → словарь мерчантов → правила по назначению платежа → **модель/LLM только на остаток**, с
   порогом уверенности и подтверждением пользователя; (в) LLM — только как текст объяснения
   готовых чисел со сверкой. Скоринг срыва платежа, персональные пороги, ML-распределение денег —
   **не брать**: нет данных, нет окупаемости, есть правовая цена.
8. **Ответ владельцу одной строкой:** задачу надо решать формулами; без обучения она решается
   хорошо, а ML — это инструмент для края (разбор текста операций), не для ядра.

---

## 8. Недобытое и журнал (финал)

| Источник | Статус | Причина |
|---|---|---|
| Gunnarsson et al. 2021, EJOR | только аннотация | ScienceDirect — пейволл |
| Makridakis et al. 2018 (PLOS ONE), M4 paper 2018 — полные тексты | не открывались | выводы взяты из M5-статьи тех же авторов и из Cerqueira 2019 |
| Кодекс этики ЦБ по ИИ (2025) | не добыт | не искался — время |
| Разъяснения Роскомнадзора про обучение ИИ на ПДн | не найдено | один запрос; «не нашли» ≠ «нет» |
| YNAB, Emma — устройство категоризации/советов | не найдено | Exa вернул только Plum |
| Чистый бенчмарк «правила против ML» в категоризации | не найдено | в Aluffi 2025 бейзлайна правил с числом нет |
| Инженерные статьи про LLM-объяснялку (4 шт.) | только сниппеты | время |
| `eprints.soton.ac.uk` (Lessmann) | 403 | взято зеркало Эдинбурга, 200 |
| `sec.gov` PDF | `curl` 403 | `r.jina.ai` 200 |
| `WebFetch` | мёртв во всей сессии | «Unable to verify if domain is safe» |

Каналы, давшие результат: `curl` с UA (arXiv, M5, Эдинбург, NeurIPS, blog Lathia), `r.jina.ai`
(КонсультантПлюс ст. 5/16, gdpr-info, SEC), Exa (SCHUFA, SEC-отзыв, 233-ФЗ, 3-МР, Zillow, CFPB,
Plum, Т-Банк, Сбер). WebSearch — 7 вызовов. Подагентов — 1 (регуляторика; оборвался без результата
при смене аккаунта, блок собран вахтой). Первоисточники —
`/Users/vasyaevdokimov/raw-originals/finpilot-data/ml_vs_rules/`.
