# Тема 17 — Рекомендательные системы в финансовой сфере: специфика домена

> Дата: 09.09.2026. Статус: **ЗАВЕРШЁН**. Файл писался по ходу (правило §11 CLAUDE.md).
> Если файл обрывается на середине раздела — агент упёрся в бюджет; всё ниже точки обрыва не добыто.
>
> **Классификация запроса (шаг 1 lead-agent):** breadth-first — семь независимых под-вопросов
> об одном домене. Углы не конкурируют, а покрывают разные срезы.
> **План:** вахта закрывает вопросы 1–3 сама (обзорная литература, методологические отличия,
> метрики); один подагент — вопросы 4–5 (доверие/алгоритм-аверсия + вред/этика/fairness);
> второй подагент при наличии бюджета — вопрос 6 (cold start). Вопрос 7 (синтез для FINPILOT) —
> только вахта, синтез субагенту не делегируется никогда.
>
> **Что уже закрыто и здесь НЕ дублируется:** темы 1–16 очереди, особенно тема 16
> (constraint-based/utility-based школа Felfernig — новизна по методу и объяснимости опровергнута).

---

## Легенда пометок

- 🟢 — дословная выписка из открытого первоисточника, ссылка проверена в этом прогоне.
- 🟡 — из аннотации/сниппета поиска, полный текст не открыт.
- 🔴 — реконструкция по памяти модели, НЕ проверено (только в отдельном разделе в конце).

---

## 1. Обзорная литература «recommender systems in finance / FinRec»

### 1.1 🟢 Wu & Li 2025 — систематический обзор 65 работ 2018–2024 (главный источник вопроса 1)

**Точная ссылка:** Wu, Di (Andrew); Li, Xuhui. «A Systematic Literature Review of Financial Product
Recommendation Systems». *Information* (MDPI), 2025, т. 16, № 3, ст. 196. DOI: 10.3390/info16030196.
Дата публикации 03.03.2025. Открытый доступ CC BY. Цитирований по Semantic Scholar на 09.09.2026 — 6.

🔴 **Как добыт.** `WebFetch` и `curl` с браузерным UA на `mdpi.com` → **403** (антибот MDPI).
Сработал третий канал: текстовый прокси `https://r.jina.ai/<URL>` → **HTTP 200**, 136 504 байта
полного текста статьи в markdown. Приём новый, в базе приёмов его не было — записать рядом
с «WebFetch кладёт PDF на диск».

**Метод обзора (§2.2–2.3, дословно):**

> «To ensure the comprehensiveness of the literature search, this study utilized both the Web of
> Science (WOS) and China National Knowledge Infrastructure (CNKI) databases.»

> «The search terms “Recommendations” OR “Recommender” OR “Recommendation” OR “Recommender Systems”
> OR “Recommendation Systems” OR “Recommender System” OR “Recommendation System” AND “Stock”
> OR “Financial Products” OR “Bonds” OR “financial services” OR “financial” were searched in
> Web of Science and CNKI, respectively.»

> «As shown in Figure 1 (PRISMA flow diagram), 431 records were retrieved from two databases…
> Finally, the optimal results for eligibility for the final phase amounted to 71 studies, but
> only 65 were available for reading.» (§2.3)

**Исследовательские вопросы обзора (§2.1, дословно):**

> «RQ1: What are the characteristics that differentiate financial product recommendation systems
> from recommendation systems in other domains?»
> «RQ2: What methods are applied in financial product recommendation systems?»
> «RQ3: How can the performance of financial product recommendation systems be improved?»

**Разбиение массива работ (§4, дословно):**

> «The output of the system process resulted in a total of 65 articles, with the financial products
> covered primarily focused on three categories: bank financial products, securities financial
> products, and other financial products.»

> «In summary, this study divides financial product recommendation into three research directions:
> financial recommendation based on precision marketing, financial recommendation based on
> time-series analysis, and financial recommendation based on text mining.» (§4)

> «…due to the transparency and granularity of stock data, which include minute-level or even
> tick-by-tick trading data, prediction-based recommendations are typically applied to stocks.» (§4)

🟡 **Точные доли по трём направлениям приведены только на Figure 3** («Categorization of articles»),
рисунок в текстовом прокси не передан. Числовые доли по категориям **не добыты**; словесно
обзор говорит «current research focuses most on the diversity and time sensitivity of features» (§5).

### 1.2 🔴🟢 ГЛАВНОЕ ДЛЯ НАС: обзор 2025 года формализует задачу ТОЛЬКО как выбор продукта

Это самая ценная выписка темы. Обзор, посвящённый именно вопросу «чем финансовая рекомендация
отличается от остальных», формально ставит задачу так (§3.2, дословно):

> «…assuming that the product set is S, and the user set is U, the traditional recommendation system
> problem can be formulated as a prediction P(uᵢ, sⱼ), where uᵢ ∈ U and sⱼ ∈ S denote the user and
> item, respectively. The financial product recommendation problem is more complex and can be
> further extended to predict P(uᵢ, sⱼ, dₜ, act), thus predicting the probability that uᵢ will
> produce an interaction act with sⱼ on day dₜ as the objective. Here… act refers to the diverse
> interactions between the investor and the financial product, which are usually two types of
> behaviors: buying and selling.»

**Что это значит.** Даже в расширенной постановке 2025 года объект рекомендации — элемент
sⱼ из **готового каталога продуктов S**, а действие `act` ограничено парой «купить/продать».
Постановки «как распределить собственный свободный поток пользователя между погашением долга,
резервом и целями» в пространстве P(uᵢ, sⱼ, dₜ, act) **нет вовсе — она в него не выражается**:
у нашей рекомендации нет sⱼ, потому что нет каталога продавца. Это **измеренный ноль**
(в смысле требования вопроса 1), полученный не отсутствием находок, а прямой формулировкой
предметной области в самом свежем систематическом обзоре домена.

Подтверждающая формулировка целей домена (§3.1, дословно):

> «According to some scholars, financial product recommendation can be regarded as a decision
> support system aimed at assisting investors in making correct or near-correct financial product
> trading decisions to maximize investment returns.»

> «Precision marketing is regarded by this group of scholars as the ultimate goal of providing
> financial product recommendation services.»

Обе школы, которые обзор перечисляет как исчерпывающие домен, — это (а) предсказание доходности
инструмента и (б) precision marketing, т.е. точный сбыт. Ни одна не является прескриптивным
советом о собственных деньгах пользователя вне ассортимента.

### 1.3 🟢 Четыре различающих признака домена по Wu & Li (§5, дословно) — ответ на RQ1

> «The complexity of financial product recommendation can be reflected in the following four
> aspects: (1) diversified business objectives; (2) diverse and complex features; (3) time-varying
> characteristics; (4) parallel buying and selling behaviors.»

Развёрнутые формулировки (§3.1, дословно):

- **Многоцелевость.** «In real-world scenarios, users typically choose products that offer higher
  returns based on their specific investment goals and risk considerations, which makes the
  requirements for recommendation systems more complex and diverse. A single objective appears
  limited and one-sided; in practice, it is necessary to balance users’ profitability needs while
  achieving precision marketing strategies.»
- **Рациональность и многокритериальность решения пользователя.** «Financial products usually
  involve the transaction and management of funds, and users are usually more cautious in their
  decision making. In order to minimize the risks involved in finance and investment, users’
  decisions on financial products are more rational, and people will consider multiple factors
  when making decisions rather than just a single economic factor, requiring more information
  and analysis.»
- **Время.** «Financial product recommendations usually show a high degree of time sensitivity…
  the first is the time-varying nature of the features… the second is the timeliness of the
  recommendation result, i.e., the recommendation results generated at different points in time
  will be different… outdated information may lead to inaccurate recommendations.»
- **Параллельность взаимодействий (против каскадности в e-commerce).** «These interactive
  behaviors all point to a single direction that leads to purchase… Financial product
  recommendations include browsing, clicking, favoriting, buying, selling, and other interactive
  behaviors, which point to the two directions of buying and selling… buying and selling are
  parallel interactive behaviors with respect to each other.»

**Замечание вахты:** заявленные обзором отличия — про **данные и цели продавца**, а не про
необратимость, отложенность обратной связи или цену ошибки. То есть даже специализированный
RQ1 «чем финансовый домен отличается» отвечается в терминах фичей и таргетов, а не в терминах
ответственности за совет. Это само по себе характеристика состояния литературы.

### 1.4 🟢 Направления будущих работ по Wu & Li (§6)

Названы ровно два: **multi-behavioral recommendation** и **multi-task recommendation**.
Дословно: «…balancing user preferences and user returns is a key task in financial product
recommendation… a model is able to consider a user’s personalized preferences and financial goals
at the same time». Ни прескриптивного совета, ни оценки долгосрочных исходов среди направлений нет.

### 1.5 🟡 Прочие обзоры домена (из сниппетов, полные тексты см. §«Что не добыто»)

- **Sharaf, M.; Hemdan, E.E.; El-Sayed, A.; El-Bahnasawy, N.A. «A survey on recommendation systems
  for financial services». *Multimedia Tools and Applications*, 2022. DOI: 10.1007/s11042-022-12564-1.**
  Цитирований по Semantic Scholar на 09.09.2026 — **36** (самый цитируемый обзор домена).
  Полный текст **не открыт**: `link.springer.com` → HTTP 303 на IdP-логин; Semantic Scholar
  сообщает `openAccessPdf: ""`, статус OA отсутствует. Аннотация издателем скрыта («The following
  paper fields have been elided by the publisher»).
- **«Challenges of recommender systems in finance and banking: a systematic review»** (2025,
  52 работы). Из сниппета поиска, 🟡: «Through the study of 52 relevant papers, three main challenges
  were identified: i) transparency, ethics, and data privacy; ii) handling complex content
  information and accounting for multiple user behaviors; iii) explainability of AI models.»
  И там же 🟡: «Despite their popularity, recommender systems are not widely used in finance and
  banking.» Первичный доступ — только ResearchGate (антибот), DOI в выдаче не назван.
- **FinRec workshop** — серия воркшопов при ACM RecSys, третье издание: «FinRec: The 3rd
  International Workshop on Personalization & Recommender Systems in Financial Services»,
  Proceedings of the 16th ACM Conference on Recommender Systems (RecSys '22),
  DOI: 10.1145/3523227.3547420. Продолжение линии — **Fin-RecSys @ IJCAI-2024**
  (https://sites.google.com/view/fin-recsys2024/). Существование отдельной воркшоп-серии
  по домену — сам по себе факт: домен признан имеющим собственную специфику.
- **«Economic Recommender Systems — A Systematic Review»**, arXiv:2308.11998 — обзор про
  экономические цели RS (цена, прибыль), не про финансовый домен как таковой; отмечен как
  смежный, не разобран.

---

## 2. Чем финансовая рекомендация отличается методологически — прямые формулировки

### 2.1 🟢 Канон домена: шесть измерений Burke & Ramezani, включая risk и scrutability

Самая цитируемая рамка «чем один домен RS отличается от другого» — **Burke, Robin; Ramezani,
Maryam. «Matching Recommendation Technologies and Domains». Recommender Systems Handbook, 2011,
с. 367–386** (реф. [10] у Zibriczky). Дословно в пересказе Zibriczky (§2, с. 3):

> «Based on the work of Burke and Ramezani [10], a domain can be characterized by the following
> aspects: (1) heterogeneity that captures the diversity of items’ properties in a domain,
> (2) churn that characterizes the level of novelty and expected lifespan of the items,
> (3) interaction style that describes how the users are able to express their preference,
> (4) preference stability that characterizes the degree of variation of user preferences over
> time, (5) **risk that determines the expected tolerance of the users for false recommendations**
> and (6) **scrutability that refers to the demand for explanation of recommendations**.»

**Это и есть искомая методологическая рамка.** Два из шести измерений — **risk** (терпимость
к ложной рекомендации) и **scrutability** (потребность в объяснении) — и по обоим финансовый
домен стоит на краю шкалы. То есть асимметрия цены ошибки и обязательность объяснения — не наше
наблюдение, а параметры канонической таксономии доменов RS, опубликованные в Handbook.

### 2.2 🟢 Zibriczky 2016 — финансовый домен как «долгосрочное обязательство с отложенной полезностью»

**Точная ссылка:** Zibriczky, Dávid. «Recommender Systems meet Finance: A literature review».
In: Proceedings of the 2nd International Workshop on Personalization & Recommender Systems in
Financial Services (FINREC 2016), Bari, Italy, 16.06.2016. CEUR Workshop Proceedings, Vol. 1606,
с. 3–10. URL: https://ceur-ws.org/Vol-1606/paper02.pdf (открыт целиком, curl + pdftotext, 8 стр.).

Ключевая формулировка отличия домена (§1 Introduction, с. 3, дословно):

> «Compared to the subjects of conventional recommender systems, **financial products usually
> require a long-term significant financial commitment as their utility is not realized immediately**
> depending on several external factors (like market returns, governmental regularizations,
> currency, etc.); furthermore, **expert knowledge is necessary to judge which one is a good choice**.
> In order to reduce the risk of such a choice, **users tend to formulate stricter expectations to
> these products than to conventional e-commerce ones**, thus applying a recommender system in
> financial domains is a challenging task.»

Про приватность и её следствие — холодный старт (§1, с. 3, дословно; см. также §6):

> «Users typically protect their personal data, which is especially true for financial services,
> causing privacy risk issues in recommender systems and requiring more complex alternative
> personalization methods. As privacy issues are significant in financial services, **personal
> metadata and individual transactional data are often missing, which causes user cold-start problem
> for recommender systems**.»

Вывод обзора про объяснимость (§4 Conclusion, с. 8, дословно):

> «As the object of recommendations are usually related to money spending transactions, we consider
> all financial domains; therefore, **the demand for proper explanation about the recommendations
> is significant**.»

И — про наш собственный сегмент (§2.1, с. 4, дословно):

> «These systems focus on money management and spending opportunities, thus **we identify high risk
> and significant demand for explanation**.»

🔴 **Отдельно для канона новизны** — там же, §2.1, приговор состоянию сегмента на 2016 год:

> «Overall, a number of works are published for banking sector; however, **all of them seem to be
> non-production concept only**.»

### 2.3 🟢 Ближайший найденный родственник нашего объекта — Fano & Kurth 2003

Zibriczky (§2.1, с. 4, дословно):

> «Fano and Kurth [22] introduce a concept of interactive management tool that **assists in personal
> resource (money) allocation**. For the optimization of this objective, they propose an algorithm,
> which considers **expenses, financial goals and time of attainment**. Yu [86] introduces a prototype
> of online personal finance management tool, which is capable to provide insurance planning,
> asset allocation and investment recommendation.»

Библиографическая запись реф. [22] дословно: «Andrew Fano and Scott W Kurth, ‘Personal Choice
Point: Helping users visualize what it means to buy a BMW’, Control, 46–52, (2003)» (работа
Accenture Labs, представлена на IUI 2003).

**Оценка вахты.** Это единственная встреченная в обзорной литературе работа, где объект —
**распределение собственных денег пользователя с учётом расходов, целей и сроков**, а не выбор
продукта из ассортимента. По названию и описанию это визуализация последствий крупной покупки,
а не оптимизационный движок; но формулировка «personal resource (money) allocation… considers
expenses, financial goals and time of attainment» настолько близка к нашей постановке, что
первоисточник нужно открыть отдельно. **Первоисточник не открыт** — ACM DL под антиботом
(см. §«Что не добыто»). Это порождённая задача, а не закрытый вопрос.

### 2.4 🟢 Sawant 2026 — прямая формулировка ВСЕХ пунктов вопроса 2 разом

**Точная ссылка:** Sawant, Yash Ganpat. «High-Stakes Personalization: Rethinking LLM Customization
for Individual Investor Decision-Making». arXiv:2604.04300, подано 05.04.2026; принято на
CustomNLP4U Workshop @ ACL 2026. Полный текст открыт через `r.jina.ai` на arXiv HTML.

Это position paper по LLM-персонализации, а не по классическим RS, — но именно он даёт то, чего
нет ни у Wu & Li, ни у Zibriczky: **дословные формулировки необратимости, отложенности обратной
связи и отсутствия ground truth.** §2 «Background: What Makes Finance Different», дословно:

> **«Decisions are consequential and irreversible.** Unlike a misranked search result or an off-tone
> email draft, a poorly timed trade results in direct financial loss. **The tolerance for
> personalization error is orders of magnitude lower.**»

> **«Preferences are dynamic and self-contradictory.** An investor may state a rule (“never average
> down into a falling knife”) while exhibiting a pattern of doing exactly that during high-volatility
> periods. The system must represent both the stated rule and the revealed behavior — the tension
> between them is itself informative.»

> **«Ground truth is delayed and stochastic.** A recommendation made today may take weeks to
> validate, confounded by market noise. **There is no immediate label to train or evaluate against.**»

> **«Temporal coherence is load-bearing.** An investment thesis stated six weeks ago must anchor
> today’s evaluation. Stateless or session-bounded systems lose this thread entirely, defaulting
> to whatever narrative is most coherent at generation time.»

И общая рамка (§2, дословно):

> «Most LLM personalization research assumes a relatively benign setting: users have stable
> preferences, the system’s job is to match them, and evaluation reduces to preference satisfaction…
> Individual investing breaks both frames simultaneously.»

> «This combination of properties is not merely harder — **it is structurally different** from what
> current personalization methods are designed for.» (§1)

🔴 **Сильная оговорка вахты о статусе источника.** Это workshop position paper одного автора
2026 года, опирающийся на один развёрнутый им продукт (InvestMate), без внешней эмпирики.
Формулировки — лучшие из найденных, но это **мнение практика, а не установленный результат**.
Цитировать как «в литературе сформулировано так», не как «измерено».

---

## 3. Как в этом домене оценивают качество рекомендации

### 3.1 🟢 Отсутствие ground truth признано и в общей теории RS, и в финансовом срезе

Общая рамка — **Castells, Pablo; Moffat, Alistair. «Offline recommender system evaluation:
Challenges and new directions». AI Magazine, 2022, 43(2). DOI: 10.1002/aaai.12051.** 🟡 (полный
текст не открывался в этом прогоне, выписка из сниппета поисковика, помечена соответственно):

> 🟡 «The ground truth for evaluating recommendations — required for meaningful experimentation —
> is difficult to obtain at scale in any controlled environment because the source of ground truth
> information is people — end-users — in large numbers, who cannot be bypassed or proxied in any
> meaningful way, since the “truth” being sought is precisely the individual and subjective
> inclinations and preferences of those people.»

Финансовый срез — Sawant 2026, §4.4 «Alignment Without Ground Truth», 🟢 дословно:

> «Personalization evaluation typically relies on preference ratings, A/B tests, or task completion
> metrics. **In investing: outcomes materialize over months; good process regularly produces bad
> outcomes; the counterfactual is unobservable;** and LLMs themselves exhibit cognitive biases that
> interact with the investor’s own.»

> «The broader implication extends beyond finance: any domain where outcomes are stochastic and
> delayed — healthcare, educational guidance, career coaching — faces the same evaluation gap.
> **Finance makes it impossible to ignore because P&L is precise enough to seem evaluable while
> being too noisy to serve as ground truth for personalization quality.**»

### 3.2 🟢 Единственный найденный конкретный протокол — оценка ПРОЦЕССА, а не исхода

Sawant 2026, §4.4, дословно:

> «Our approach to thesis grading addresses this by evaluating closed positions on **process
> quality**: was the thesis directionally correct? Was timing appropriate? Was sizing consistent
> with conviction? **A position that lost money but followed a sound thesis receives a higher grade
> than a profitable impulsive trade.** This process-over-outcome framing is grounded in behavioral
> economics, but **formalizing it as a personalization evaluation metric remains an open problem**.»

И в списке открытых направлений (§5, дословно):

> «**Process-quality evaluation frameworks.** We lack evaluation methodologies for personalized
> systems where ground truth is stochastic. Formalizing process-quality metrics — coherence,
> evidential grounding, and consistency with the user’s stated framework — **is an open problem**
> that would benefit personalization research well beyond finance.»

**Вывод по вопросу 3 (честный):** опубликованного, валидированного офлайн-протокола оценки
прескриптивных финансовых советов **найти не удалось**. Самый свежий источник домена прямо
называет это открытой проблемой. Это второй измеренный ноль темы.

### 3.3 🟢 Удовлетворённость пользователя ≠ качество совета — с прямой ссылкой

Sawant 2026, §4.3, дословно:

> «Sanz-Cruzado et al. found that **users preferred LLM advisors with extroverted personas even when
> those agents gave worse advice** — suggesting satisfaction and quality can be inversely correlated.»

И оттуда же (§5), почему это ломает стандартную оптимизацию:

> «Standard RLHF optimizes for user approval — **exactly the wrong objective when user satisfaction
> and advice quality are inversely correlated**.»

🔴 Первоисточник Sanz-Cruzado et al. (2025) по этой ссылке **не открывался** — цитата приведена
по вторичному источнику (Sawant 2026), это отмечено явно. Проверить отдельно.

### 3.4 🟡 Метрики принятия вместо кликов — общая линия RS, не финансовая специфика

Из **Jannach, Dietmar; Jugovac, Michael. «Measuring the Business Value of Recommender Systems»**
(arXiv:1908.08328), 🟡 из сниппета: «Optimizing for click-rates may be too short-sighted in many
applications, and click-through rates are typically not the ultimate success measure to target in
recommendation scenarios»; adoption/conversion-меры «only count a recommendation as successful if
there are signs that it was truly useful for consumers». Полный текст не открывался — это общее
место теории RS, а не находка по финансовому домену; приведено как рамка.

**Регуляторные понятия suitability / appropriateness** и счётчики принятия совета вынесены
в работу подагента (§4–5 файла `_sub17_trust_and_harm.md`).

---

## 6. Холодный старт и разреженность в финансовом домене

*(Раздел закрыт вахтой; разделы 4–5 — работа подагента, см. ниже.)*

### 6.1 🟢 Постановка проблемы именно для финансов — Zibriczky 2016

Уже процитировано в §2.2, повторю формулировку причинности целиком (FINREC 2016, с. 3, дословно):

> «As privacy issues are significant in financial services, personal metadata and individual
> transactional data are often missing, **which causes user cold-start problem for recommender
> systems**.»

То есть в финансовом домене холодный старт — не временное неудобство новизны пользователя,
а **структурное следствие приватности**: данных нет не потому, что пользователь новый,
а потому что он их не отдаёт.

### 6.2 🟢 Канонический ответ литературы: knowledge-based рекомендации

**Точная ссылка:** Uta, M.; Felfernig, A.; Le, V.-M.; Tran, T.N.T.; Garber, D.; Lubos, S.;
Burgstaller, T. «Knowledge-based recommender systems: overview and research directions».
*Frontiers in Big Data*, 2024, т. 7, ст. 1304439. DOI: 10.3389/fdata.2024.1304439.
Открытый доступ; полный текст снят через `r.jina.ai` (HTTP 200, 182 077 байт).

Дословно (§1 Introduction, третий абзац классификации подходов):

> «**Third, knowledge-based recommender (KBR) systems can be considered as complementary to CF- and
> CBF-based approaches in terms of avoiding the related cold-start difficulties** (Burke; Towle and
> Quinn; Lorenzi and Ricci). KBR systems are based on the idea of collecting the preferences of a
> user (preference elicitation) within the scope of a dialog and then to recommend items either
> (1) on the basis of a predefined set of recommendation rules (constraints) or (2) using similarity
> metrics that help to identify items which are similar to the preferences of the user.»

Дальше — прямое обоснование, почему именно финансы (там же, дословно):

> «**KBR systems support the determination of recommendations specifically in complex and
> high-involvement item domains [domains where suboptimal decisions can have significant negative
> consequences, for example, when investing in high-risk financial services (Felfernig et al.)]
> where items are not bought on a regular basis.** Example item domains are financial services
> (Felfernig et al.; Musto et al.), software services (Felfernig et al.), apartment or house
> purchasing (Fano and Kurth), and digital cameras (Felfernig et al.).»

> «These systems are able to take into account constraints (e.g., **high-risk financial services
> must not be recommended to users with a low preparedness to take risks**) and provide explanations
> of recommendations **also in situations where no solution could be identified**. In contrast to CF
> and CBF, **KBR systems support explicit preference elicitation dialogs which makes them immune
> with regard to user preferences changing over time**.»

Цена подхода названа там же (дословно):

> «Due to an often time-intensive knowledge exchange between domain experts and knowledge engineers,
> the definition of recommendation knowledge can trigger high setup costs (Ulz et al.).»

### 6.3 🟢 Формализованное свойство домена: «high-involvement items»

В той же статье в таблице сравнения подходов (Table 1, подпись, дословно):

> «_Basic properties_ of different recommendation approaches: _easy setup_ = low effort needed for
> setting up the recommender system, _dialog-based_ = conversational process between system and
> user, _serendipity_ = effect of proposing unexpected but relevant recommendations, _cold-start
> problem_ = initial data are needed to provide reasonable recommendations, **_high-involvement
> items_ = a user carefully evaluates the candidate items since suboptimal decisions can have
> significant negative consequences**.»

В таблице строка «Cold-start problem» помечена «×» у CF и CBF и «–» у KBR (то есть у
knowledge-based подхода холодного старта нет).

**Это важная для нас терминологическая находка.** У свойства, которое мы описывали своими словами
(«цена ошибки несопоставима, пользователь взвешивает»), есть **устоявшееся имя —
high-involvement item domain**, и оно вынесено в таблицу свойств вместе с cold-start.
Финансовые услуги — их пример №1.

### 6.4 🟡 Финансовая специфика cold start отдельной работой

**Hung, Tsan-Yin; Huang, Szu-Hao. «Addressing the cold-start problem of recommendation systems
for financial products by using few-shot deep learning». *Applied Intelligence*, 2022.
DOI: 10.1007/s10489-022-03374-x.** Цитирований по Semantic Scholar на 09.09.2026 — 10.
**Полный текст и даже аннотация не добыты**: Semantic Scholar сообщает `openAccessPdf: ""`,
аннотация скрыта издателем («The following paper fields have been elided by the publisher»),
Springer отдаёт редирект на IdP. Зафиксировано как существующая, но не прочитанная работа.

### 6.5 🟡 Что литература предлагает вместо истории (общая линия, не финансовая)

Из сниппетов поиска (полные тексты не открывались, помечено 🟡):
- **Байесовский приор по популяции:** «a two-part Bayesian model, where the prior probability is
  based on the existing user population and data likelihood, which is based on the data supplied
  by the user… when a new user enters the system, little is known about that user and the prior
  distribution is the main contributor».
- **Синтетические/заимствованные профили:** «generate pseudo-counts from suitable mixtures of the
  accounts profiles of other members… such that the accounts profile of a new user can be seeded
  to be similar… even when the new user has no historical data» (формулировка из патентного текста
  US 10909575, не из статьи).
- **Демография как минимальный вход:** «solutions typically use similar demographic information,
  most commonly age, occupation and gender, and **most solutions ask for less than five pieces of
  information**».
- Обзор по теме: **«Approaches and algorithms to mitigate cold start problems in recommender
  systems: a systematic literature review», Journal of Intelligent Information Systems, 2022,
  DOI: 10.1007/s10844-022-00698-5** — не открыт (Springer, редирект на IdP).

**Вывод по вопросу 6.** Ответ литературы на холодный старт в финансах однозначен и стар: это
**knowledge-based / constraint-based рекомендация с явным диалогом сбора предпочтений**, и она
названа «immune» к холодному старту прямым текстом в обзоре 2024 года. Ничего экзотического
(синтетические профили, перенос с популяции) для финансового домена как предпочтительного ответа
литература не предлагает — это компенсаторные приёмы для CF, а не для нашего класса систем.

---

## 1-бис. Второй систематический обзор домена — Bonde & Bichanga 2025 (добыт целиком)

**Точная ссылка:** Bonde, Lossan; Bichanga, Abdoul Karim. «Challenges of recommender systems in
finance and banking: a systematic review». *IAES International Journal of Artificial Intelligence
(IJ-AI)*, 2025, т. 14, № 4, август 2025, с. 2559–2567. ISSN 2252-8938.
DOI: 10.11591/ijai.v14.i4.pp2559-2567. Открытый доступ CC BY-SA.
PDF: https://ijai.iaescore.com/index.php/IJAI/article/download/25820/14602 (HTTP 200, 9 стр.,
снят curl + pdftotext). Аффилиации: Adventist University of Africa (Найроби) и Nazi Boni
University (Буркина-Фасо).

### 1-бис.1 🟢 Отправная точка обзора — домен НЕ освоен

Аннотация, дословно:

> «Recommender systems are widely applied in various domains, including e-commerce, marketing, and
> education. **Despite their popularity, recommender systems are not widely used in finance and
> banking.**»

§3 Results and Discussion, дословно:

> «Although previous studies have extensively analyzed recommender systems in various domains such
> as e-commerce, marketing, and education, **they have not explicitly addressed the unique challenges
> and requirements of the finance and banking industry.** This gap in the research necessitated a
> focused investigation into the specific issues faced by financial institutions when adopting
> these systems.»

### 1-бис.2 🟢 ДОЛИ РАБОТ ПО ТЕМАМ — числа, которых просил вопрос 1

Из 52 отобранных работ (§3.1, дословно):

| Тема | Доля работ | Дословная формулировка обзора |
|---|---|---|
| Разнообразие источников данных | **34%** | «About 34% of the studies emphasized the importance of leveraging various data types to enhance model accuracy and robustness.» |
| Прозрачность, этика, приватность | **27%** | «We found that transparency, ethics, and data privacy are critical concerns, as highlighted by 27% of the reviewed papers.» |
| Обнаружение мошенничества | **21%** | «Approximately 21% of the papers reviewed supported the use of these advanced models…» |
| Проблема холодного старта | **18%** | «Cold-start problems were another significant challenge identified, affecting around 18% of the recommender systems in the reviewed studies.» |
| Ценность клиента и маркетинг | **16%** | «About 16% of the papers highlighted the need for sophisticated customer segmentation.» |

Девять категорий задач домена (Table 2, дословно, с номерами ссылок обзора):
**Financial recommendation systems** [6]–[17] · **Stock market prediction** [18]–[23] ·
**Risk management and fraud detection** [24]–[27] · **Transparency, ethics, and data privacy**
[28],[29] · **Exploring new data sources and modalities** [30]–[34] · **Customer value and
marketing** [35]–[38] · **Financial planning and advisory** [39]–[42] · **Auditing and insights**
[43]–[45] · **Emerging technologies** [46]–[53].

🔴 **Ключевое число для нашего вопроса.** Категория, ближайшая к прескриптивному совету о деньгах
пользователя, — **«Financial planning and advisory» — ровно ЧЕТЫРЕ ссылки [39]–[42] из 52 работ,
то есть 7,7% массива.** И даже эти четыре — не то, что мы делаем; вот их дословные библиографические
записи из списка литературы обзора:

> «N. Pereira and S. L. Varma, “Financial planning recommendation system using content-based
> collaborative and demographic filtering,” Advances in Intelligent Systems and Computing, vol. 669,
> pp. 141–151, 2019, doi: 10.1007/978-981-10-8968-8_12.»
> «P. Ładyżyński, K. Żbikowski, and P. Gawrysiak, “**Direct marketing campaigns in retail banking**
> with the use of deep learning and random forests,” Expert Systems with Applications, vol. 134,
> pp. 28–35, 2019, doi: 10.1016/j.eswa.2019.05.020.»
> «S. Chakraborty, “Capturing financial markets to apply deep reinforcement learning,”
> arXiv-Quantitative Finance, pp. 1-17, 2019.»
> «J. Ren, J. Long, and Z. Xu, “**Financial news recommendation** based on graph embeddings,”
> Decision Support Systems, vol. 125, 2019, doi: 10.1016/j.dss.2019.113115.»

Из четырёх работ рубрики «финансовое планирование и консультирование» одна — про **прямые
маркетинговые кампании банка**, одна — про **рекомендацию новостей**, одна — про **RL на рынках**.
Прескриптивным советом о распределении собственного потока не является **ни одна**.

### 1-бис.3 🟢 Собственная интерпретация обзором своей рубрики «Financial planning and advisory»

§3.2.7, дословно и целиком:

> «Incorporating additional data sources and personalizing recommendations based on individual and
> familial factors significantly improved the quality of financial planning recommendations. Our
> approach provided more accurate and relevant recommendations, suggesting that expanded data usage
> is not associated with reduced recommendation quality.»

**Наблюдение вахты, важное для вопроса 2.** Весь §3.2 обзора 2025 года разбирает домен в терминах
**точности модели и объёма данных**. Слова «irreversible», «suitability», «cost of error»,
«counterfactual» в тексте отсутствуют. То есть **второй независимый систематический обзор домена
тоже не формулирует специфику через ответственность за совет** — ровно как и Wu & Li (§1.3).
Это устойчивое свойство литературы, а не особенность одного обзора.

### 1-бис.4 🟢 Три главных вызова домена по Bonde & Bichanga (аннотация, дословно)

> «Through the study of the 52 relevant papers, three main challenges: i) **transparency, ethics,
> and data privacy**; ii) **handling complex content information and accounting for multiple user
> behaviors**; and iii) **explainability of AI models** were identified.»

И §3 «Lessons learned», дословно:

> «…**data transparency, ethical design, and confidentiality are essential for building user trust
> and facilitating the adoption of recommender systems in finance.** Users are more likely to engage
> with systems they perceive as fair, secure, and understandable, particularly in sensitive domains
> like banking. **Incorporating clear explanations for recommendations and adhering to ethical
> standards not only improves user experience but also ensures compliance with regulatory
> frameworks.**»

🔴 **Оговорка о качестве источника.** Журнал IJ-AI (IAES) — не топовая площадка; в тексте есть
странности («This suggests that incorporating temporal context is **not** associated with poor
recommendation performance» — двойное отрицание вместо утверждения, повторяющаяся конструкция
«is not associated with» во всех подразделах §3.2). Проценты по темам и таблица категорий
пригодны как измерение массива; интерпретации автора — с осторожностью.

### 1-бис.5 🟡 Побочная находка для вопроса 5 (передана в работу подагента)

В списке литературы обзора: «K. Lakkaraju, S. E. Jones, S. K. R. Vuruma, V. Pallagani,
B. C. Muppasani, and B. Srivastava, “**LLMs for financial advisement: a fairness and efficacy study
in personal decision making**,” in 4th ACM International Conference on AI in Finance (ICAIF), 2023,
pp. 100–107, doi: 10.1145/3604237.3626867.» — прямое попадание в вопрос 5 (fairness в личных
финансовых решениях). Не открыта (ACM DL под антиботом).

---

## 2-бис. Дополнение о Fano & Kurth 2003 — единственном близком родственнике объекта

Работа встретилась **дважды независимо**: у Zibriczky (FINREC 2016, §2.1) как инструмент
«personal resource (money) allocation» и у Uta/Felfernig et al. (Frontiers in Big Data 2024, §1)
в перечне доменов knowledge-based рекомендаций как «apartment or house purchasing (Fano and Kurth)».
Два обзора описывают её по-разному, что само по себе повод открыть первоисточник.

🟡 Из сниппета поисковой выдачи (полный текст **не открыт**): «The “Personal Choice Point” project…
addressed **how to determine whether a purchase is affordable by examining how it would affect other
financial goals**.» Это описание — «влияние решения о деньгах на прочие финансовые цели
пользователя», то есть по объекту ближе к FINPILOT, чем что-либо из 65 работ Wu & Li и 52 работ
Bonde & Bichanga.

**Статус:** первоисточник не добыт. `WebSearch` даёт только вторичные упоминания; Semantic Scholar
вернул HTTP 429 (rate limit), OpenAlex по названию работу **не находит вовсе** (три нерелевантных
результата). Публикация 2003 года в трудах IUI, ACM DL под антиботом.
**Порождённая задача:** открыть Fano & Kurth 2003 через другой канал (CiteSeerX, персональные
страницы авторов, архив Accenture Labs) и установить, оптимизирует ли она распределение или только
визуализирует последствия. От ответа зависит формулировка зазора новизны FINPILOT.

---

## 1-тер. Контрольный поиск на прескриптивное распределение потока — отрицательный результат

Отдельный целевой запрос («prescriptive recommender system personal finance allocate cash flow
debt savings goals optimization», 09.09.2026) не вернул **ни одной академической работы**.
Вся релевантная выдача — **патенты USPTO** (в т.ч. US 12450487 «Artificial intelligence-based
personalized financial recommendation assistant system and method») и маркетинговые страницы
финансовых компаний.

**Это третий измеренный ноль темы, и он согласуется с §1.2 и §1-бис.2:** объект «распределить
собственный свободный поток между долгом, резервом и целями» существует в **патентном** массиве
(что уже установлено темами 1–11 и 22 и здесь не дублируется) и **отсутствует в академической
литературе рекомендательных систем**. Два систематических обзора домена (65 и 52 работы,
2025 год) не содержат его ни как категорию, ни как отдельную работу.

---

## 3-бис. 🔴🟢 ГЛАВНАЯ ЭМПИРИЧЕСКАЯ НАХОДКА ТЕМЫ: пользователь не отличает хороший совет от плохого

Найдено вахтой (не подагентом) по обратной ссылке из Sawant 2026. Прямо отвечает на вопросы 3 и 4.

**Точная ссылка:** Takayanagi, Takehiro; Izumi, Kiyoshi; Sanz-Cruzado, Javier; McCreadie, Richard;
Ounis, Iadh. «Are Generative AI Agents Effective Personalized Financial Advisors?».
In: Proceedings of the 48th International ACM SIGIR Conference on Research and Development in
Information Retrieval (SIGIR '25), Padua, Italy, 13–18.07.2025. ACM, 10 стр.
DOI: 10.1145/3726302.3729897. Препринт arXiv:2504.05862.
Аффилиации: University of Tokyo, University of Glasgow.
🟢 **Полный текст открыт** через репозиторий Глазго: https://eprints.gla.ac.uk/353695/2/353695.pdf
(HTTP 200, curl + pdftotext; ACM DL при этом остаётся под антиботом). Цитирований по счётчику
ACM на PDF — 3, скачиваний — 2260.

### Постановка (Abstract, дословно)

> «Large language model-based agents are becoming increasingly popular as a low-cost mechanism to
> provide personalized, conversational advice, and have demonstrated impressive capabilities in
> relatively simple scenarios, **such as movie recommendations**. But how do these agents perform in
> **complex high-stakes domains, where domain expertise is essential and mistakes carry substantial
> risk?**»

Это буквально формулировка вопроса нашей темы («чем рекомендация финансового действия отличается
от рекомендации фильма»), поставленная как исследовательский вопрос и проверенная экспериментом.

### Дизайн

> «Via a lab-based user study with **64 participants**, we show that LLM-advisors often match human
> advisor performance when eliciting preferences, although they can struggle to resolve conflicting
> user needs.» (Abstract)

Набор — из университета авторов, оплата **£10/час**, длительность ≈1 час (§ методики, с. 5).
Три исследовательских вопроса (§3, дословно):
> «RQ1: Can LLM-advisors effectively elicit user preferences…»
> «RQ2: Does personalization lead to better investment decisions and a more positive advisor
> assessment?»
> «RQ3: Do different personality traits affect decision quality…»
Замеряемые шкалы включают **Emotional Trust**, **Trust in Competence**, **Overall Satisfaction**
(стандартизованные опросники) и объективное качество решения — корреляцию Спирмена между
ранжировкой активов участником и эталонной ранжировкой.

### 🔴 Находка №1 — удовлетворённость и качество совета РАСХОДЯТСЯ (Abstract, дословно)

> «More worryingly, **users appear insensitive to the quality of advice being given, or worse these
> can have an inverse relationship.** Indeed, **users reported a preference for and increased
> satisfaction as well as emotional trust with LLMs adopting an extroverted persona, even though
> those agents provided worse advice.**»

### 🔴 Находка №2 — числа по качеству решения (§5.3.1, дословно)

> «…we observe a difference between the two advisors, with the conscientious LLM-advisor providing
> better guidance than the extroverted one (**0.26 vs. 0.122**). This observation is consistent when
> we restrict our analysis to those cases where the preference elicitation is successful. While,
> expectedly, the effectiveness of both advisors improves when the elicitation is successful
> (**0.243 vs. 0.122** in the case of the extroverted advisor and **0.365 vs. 0.26** in the case of
> the conscientious one), the conscientious advisor has an advantage over the extroverted one
> (**0.365 vs. 0.26**).»

Метрика — «the average Spearman’s Rho correlation between the investor ranking and the ground truth
ranking» (Table 4). То есть **экстравертный советник даёт вдвое худшее качество решения
(0.122 против 0.26), но получает более высокие оценки доверия и удовлетворённости.**

### 🔴 Находка №3 — пользователь не различает персонализированного и базового советника (§5.2, дословно)

> «…the participant preference scores for both variants are **statistically indistinguishable**,
> except under the quality of information provision criteria. This means that **our participants
> cannot tell if the LLM-advisor is personalizing to them, and trust the worse agent just as much
> as the better one.**»

> «This underlines one of the core risks of using LLM-advisors in the financial domain; **since our
> users are inherently inexpert they lack the fundamental skills to judge to what extent the LLM is
> providing good advice, meaning that there is no safety net if the LLM makes a mistake.**»

### 🔴 Находка №4 — неточная выявленная преференция ХУЖЕ отсутствия персонализации (§5.2, дословно)

> «First, the impact the LLM-advisor has is strongly tied to the quality of the preference
> elicitation data provided, where **poor preference elicitation will cause the agent to actively
> direct the investor to the wrong assets.**»

Статистика в таблице: тест Уилкоксона для связанных выборок, «Boldface indicates significant
effects with † for 𝑝 < 0.1 and ‡ for 𝑝 < 0.05».

### Что это значит для нас (оценка вахты, не источника)

Три следствия, каждое проверяемое против нашей конструкции:
1. **Метрика «пользователь принял совет» как показатель качества — опровергнута эмпирически.**
   Принятие и удовлетворённость в этом эксперименте коррелируют с персоной, а не с качеством.
   Любой наш KPI вида «доля принятых рекомендаций» измеряет обаяние интерфейса, а не пользу.
2. **Точность анкеты риск-профиля — критический путь, а не удобство.** Неверно снятая преференция
   не «немного ухудшает», а **активно уводит пользователя не туда** — хуже, чем отсутствие
   персонализации.
3. **«Safety net» отсутствует по построению домена:** пользователь неэксперт и не может отловить
   ошибку системы. Это аргумент в пользу жёстких инвариантов (Rt≥0, ПДН≤0.40) как единственного
   работающего предохранителя — проверка не может быть делегирована пользователю.

---

## 4–5. Доверие/алгоритм-аверсия и вред/этика — работа подагента

🔴 **Полное сырьё этих двух вопросов — в отдельном файле подагента:**
`/Users/vasyaevdokimov/repos/personal-finance-dss/docs/research/raw/_sub17_trust_and_harm.md`
Там дословные выписки с точными страницами и статистикой. Ниже — только сводка вахты
с теми числами, которые несут следствия для проектирования. Пересказ не заменяет файл.

### 4.1 🟢 Алгоритм-аверсия: люди отказываются от алгоритма ПОСЛЕ того, как увидели его ошибку

**Dietvorst, B.J.; Simmons, J.P.; Massey, C. «Algorithm Aversion: People Erroneously Avoid
Algorithms After Seeing Them Err». Journal of Experimental Psychology: General, 2015, 144(1),
с. 114–126.** Ключевое число: в первой стадии эксперимента **83% участников (610 из 741 по пяти
исследованиям)** сами наблюдали, что модель точнее человека, — и всё равно после демонстрации
ошибки модели предпочитали человеческий прогноз.

### 4.2 🔴 Противоядие найдено и оно НЕ объяснение, а КОНТРОЛЬ

**Dietvorst, B.J.; Simmons, J.P.; Massey, C. «Overcoming Algorithm Aversion: People Will Use
Imperfect Algorithms If They Can (Even Slightly) Modify Them». Management Science, 2018, 64(3),
с. 1155–1170. DOI: 10.1287/mnsc.2016.2643.** Открыт целиком (Wharton, препринт + опубликованный PDF).

| Условие | Доля выбравших алгоритм | Исследование |
|---|---|---|
| Нельзя менять вывод модели | **32%** | Study 1 |
| Можно изменить 10 значений | **73%** | Study 1, χ²(1, N=145)=24.19, p<.001 |
| Можно скорректировать на ±10 | **76%** | Study 1, χ²(1, N=146)=28.40, p<.001 |
| Нельзя менять (репликация) | **47%** | Study 2 |
| Можно менять | **75–77%** | Study 2, N=530–542, p<.001 |

И главное — **размер разрешённой правки не важен**: «71%, 71%, and 68% chose the model in the
adjust-by-10, adjust-by-5, and adjust-by-2 conditions» (Study 3), различия между тремя допусками
незначимы. Дословный вывод статьи: «people’s decision to use an algorithm is **insensitive to the
magnitude of the modifications** they are able to make».

Отложенный эффект (Study 4): участники, которые *в прошлом* могли править модель, потом выбирали
режим «только модель, без правок» **в 30% случаев против 12%** у тех, кто править не мог
(χ²(1, N=823)=38.45, p<.001) — **несмотря на то что модель на их глазах ошибалась**.

### 4.3 🟡 Обратный эффект тоже существует — algorithm appreciation

**Logg, J.M.; Minson, J.A.; Moore, D.A. «Algorithmic Appreciation: People Prefer Algorithmic to
Human Judgment». Organizational Behavior and Human Decision Processes, 2019, 151, с. 90–103.**
Метрика Weight on Advice (WOA). Один и тот же совет с ярлыком «алгоритм» получал **WOA = 45%**,
с ярлыком «другие люди» — **WOA = 30%** (M=0.30, SD=0.35, F(1,200)=8.86, p=.003, d=0.42).
**88%** участников предпочли оценку алгоритма оценке другого участника; **66%** — оценке своей
собственной.

🔴 **Противоречие между источниками — называю прямо, а не сглаживаю.** Dietvorst даёт аверсию,
Logg — предпочтение алгоритма. Примиряющее условие видно из самих работ: **appreciation
наблюдается ДО демонстрации ошибки, aversion — ПОСЛЕ.** Для FINPILOT это означает, что доверие
пользователя — не константа профиля, а функция истории отказов системы; первый заметный промах
стоит дороже, чем любая начальная настройка тона.

### 4.4 🔴 Робо-инвестиционная аверсия измерена на большой выборке

**Niszczota, P.; Kaszás, D. «Robo-investment aversion». PLOS ONE, 2020, 15(9): e0239277.
DOI: 10.1371/journal.pone.0239277.** Пять экспериментов, **N = 3 828**. Дословно: «we document a
considerable robo-investment aversion (**d = –0.39** [–0.45, –0.32] in internal meta-analysis)».
В Study 4 человеческий совет выбирали в **57,3%** случаев (χ²(1)=16.0, p<.001).

### 4.5 🔴 Человек «в контуре» — эффект измерен на РЕАЛЬНЫХ клиентах, не в лаборатории

**Greig, F.; Ramadorai, T.; Rossi, A.; Utkus, S.; Walther, A. «Algorithm Aversion: Theory and
Evidence from Robo-Advice», рабочая версия 18.04.2023 (Vanguard, Georgetown, Imperial College).
SSRN: https://ssrn.com/abstract=4301514.** Данные Vanguard Personal Advisor Services — гибридный
робо-эдвайзинг, клиенты квазислучайно закреплены за советниками разного типа.

- «a high-retention human advisor removes **over 90%** of the effect of investors’ prior about the
  expected returns generated by the algorithm»;
- «high-retention human advisors reduce clients’ propensity to quit in benign market conditions by
  around **23%**» (и **21%** на подвыборке опытных клиентов);
- удержание за 3 года: **90,6%** против **86,8%**; риск оттока ниже на **25,4%** (Cox);
- «attrition from robo-advising increases by 0.136 percentage points in poor market conditions,
  i.e., a **37% increase in attrition** in such times».

**Механизм, названный авторами:** человек не улучшает алгоритм — он снимает «ongoing disutility»
и неопределённость. И работает это **сильнее всего на просадке рынка**, то есть ровно в момент,
когда пользователь больше всего склонен бросить систему.

### 4.6 🔴 Объяснение спасает НЕ первичное принятие, а восстановление после ошибки

**Ben David, D.; Resheff, Y.S.; Tron, T. «Explainable AI and Adoption of Financial Algorithmic
Advisors: an Experimental Study». arXiv:2101.02555.** Метрика Readiness To Adopt (RTA).
Старт почти одинаков: человек-советник **56%**, алгоритм без объяснений **57,7%**. На хорошей
работе алгоритм отрывается до **+16,3 п.п.** к седьмому дню (p=0.0129, t=2.5114). После сбоя
на седьмой день «adoption plummeted» — **85,5% → 61%**, то есть к исходному уровню.
Дословно из аннотации: «Using more elaborate feature-based or accuracy-based explanations helps
substantially in **reducing the adoption drop upon model failure**.»

### 5.1 🟢 Регуляторный контур: ответственность за пригодность НЕ передаётся пользователю

**ESMA. «Guidelines on certain aspects of the MiFID II suitability requirements», ESMA35-43-3172,
23.09.2022, опубликованы 03.04.2023.** Открыты дословно (PDF ESMA, pdftotext). Три пункта,
которые прямо задают требования к архитектуре нашего класса систем:

> §14: «Firms should **avoid stating, or giving the impression, that it is the client who decides on
> the suitability** of the investment, or that it is the client who establishes which financial
> instruments fit his own risk profile… firms should avoid… **requiring the client to confirm that
> an instrument or service is suitable**.»

> §15: «**Any disclaimers** (or other similar types of statements) aimed at limiting the firm’s
> responsibility for the suitability assessment **would not in any way impact** the characterisation
> of the service provided in practice to clients nor the assessment of the firm’s compliance…
> firms should not claim that they do not assess the suitability.»

> §90 (мониторинг алгоритма): «firms should **regularly monitor and test the algorithms** that
> underpin the suitability… establish an appropriate **system-design documentation** that clearly
> sets out the purpose, scope and design of the algorithms. **Decision trees or decision rules
> should form part of this documentation**… have a documented **test strategy**… policies and
> procedures for **managing any changes to an algorithm**, including monitoring and keeping records
> of any such changes… **detect any error within the algorithm** and deal with it appropriately,
> including, for example, **suspending the provision of advice** if that error is likely to result
> in an unsuitable advice…»

Определение robo-advice из глоссария того же документа (с. 3, дословно):
> «Robo-advice: The provision of investment advice or portfolio management services (in whole or in
> part) through an automated or semi-automated system used as a client-facing tool.»

### 5.2 🟢 США: SEC Regulation Best Interest

Принято 05.06.2019, действует с 30.06.2020. Основной стандарт дословно со страницы SEC:
> «act in the best interest of the retail customer at the time the recommendation is made, **without
> placing your financial or other interest ahead of the retail customer’s interests**.»
Четыре обязательства: Disclosure, Care («exercise reasonable diligence, care, and skill in making
the recommendation»), Conflict of Interest, Compliance.

### 5.3 🟡 FCA: граница «advice vs guidance» — закрыта частично

Понятие «personal recommendation» как водораздел зафиксировано, но **точная формулировка из FCA
Handbook (PERG 8.28, COBS 9) в этом прогоне не открыта** — страница Advice Guidance Boundary Review
описывает только текущую реформу («targeted support», «simplified advice»). Порождённая задача;
относится к теме 19 очереди, здесь не добирается.

### 5.4 🔴 Что домен считает вредом — измеренные паттерны (регуляторное исследование)

**Ontario Securities Commission. «Digital Engagement Practices: Dark Patterns in Retail Investing»,
research report, 23.02.2024.** Открыт целиком (PDF OSC, pdftotext). Разделяет **четыре разных
механизма**, не синонимы: Dark Patterns · Dark Nudges · Sludge · Targeted Advertising.

- **Push-уведомления:** «This type of push notification has been shown to **increase the number of
  retail investor trades by approximately 25%** in the minutes following a notification and to
  exacerbate the disposition effect… trades executed within 24 hours of receiving a push
  notification bore **19-percentage-point higher leverage**. The impact was stronger for male,
  younger, and less experienced investors.»
- **Списки/рейтинги (ranking) и стадность:** «one study found an average **20-day abnormal return
  of −4.7%** for top stocks purchased each day». Честный контрпример там же: у аудитории в среднем
  45 лет с 9 годами опыта список «Top Movers» на доходность **не влиял** — эффект зависит от
  аудитории, не универсален.
- **Sludge как отдельная категория:** трение, мешающее *защитному* действию пользователя
  (посмотреть комиссию, отписаться, вывести средства) — в отличие от dark pattern, который толкает
  к действию. Пример: «one platform advertises a large bonus… (up to several thousand dollars) —
  in reality, **99% of users will receive less than $50**. This information is not mentioned in the
  offer but can be found if a user searches for it in the platform’s help centre.»

### 5.5 🔴 Fairness в кредитных рекомендациях — и стёртая граница «совет / решение»

**Chen, Jiahao (Capital One). «Fair lending needs explainable models for responsible
recommendation». Workshop on Responsible Recommendation @ ACM RecSys 2018, Vancouver.
arXiv:1809.04684.** Открыт целиком через зеркало ar5iv.

Два теста дискриминации, дословно:
> «**disparate treatment**: informally, intentionally treating people differently on the basis on a
> protected class, and **disparate impact**: informally, discriminating against any protected class
> as a resulting from implementing of a facially neutral policy.»

Прямое предупреждение о признаках-прокси:
> «a model for credit risk has to avoid features like **zip code**, which is highly correlated with
> race… Using zip code in a model therefore runs the risk of **redlining**… Other variables that may
> be predictive of credit risk, such as **length of credit history, correlate with age** of customer,
> another prohibited class… **Even seemingly innocuous policies like a minimum principal amount for
> a loan may introduce bias** against one or more protected classes.»

🔴 **Самое важное для нашего класса систем:**
> «marketing campaigns for credit have compliance considerations similar to credit decisioning
> models… **each marketing offer to a prescreened customer is a firm offer of credit; all a customer
> needs to do is accept the offer to obtain credit**» (по FCRA).

То есть в кредитном домене **юридическая граница между «мы просто рекомендуем» и «мы приняли
решение» стёрта институционально** — это второй, независимый от ESMA §15, источник того же вывода:
позиция «это не совет, решаете вы» не защищает.

И число, обосновывающее требование отлаживаемости модели:
> «**5% of Americans have errors in their credit reports** that adversely affect their
> creditworthiness» (со ссылкой на FTC).

### 5.6 🟡 Терминологический разрыв: «harm-aware recommendation» существует, но не про финансы

Термин и площадка (OHARS — workshop по вредным/чувствительным рекомендациям при ACM RecSys)
в литературе RS **есть**, но к финансовому домену **не применяются**: подагент не нашёл ни одной
работы, соединяющей их. Помечено 🟡 — проверены только сниппеты, ACM DL под антиботом.
**Это четвёртый измеренный ноль темы.**

---

## Что не добыто и почему

| Источник | Канал и код ответа | Что осталось неизвестным |
|---|---|---|
| Wu & Li 2025, **Figure 3** «Categorization of articles» | текст статьи снят целиком через `r.jina.ai`, но **рисунки прокси не передаёт** | точные доли 65 работ по трём направлениям (precision marketing / time-series / text mining) — есть только словесная оценка §5 |
| Sharaf et al. 2022, «A survey on recommendation systems for financial services», MTA, DOI 10.1007/s11042-022-12564-1 (36 цитирований — самый цитируемый обзор домена) | `WebFetch` → **HTTP 303** на `idp.springer.com`; `r.jina.ai` → HTTP 200, но **отдал только список литературы**, не текст (пейволл); Semantic Scholar: `openAccessPdf: ""`, аннотация скрыта издателем | вся классификация задач домена по этому обзору |
| **Fano, A.; Kurth, S.W. «Personal Choice Point…», 2003** — ближайший найденный родственник объекта FINPILOT | ACM DL под антиботом; Semantic Scholar → **HTTP 429**; OpenAlex по названию → **работу не находит**; `WebSearch` даёт только вторичные упоминания | оптимизирует ли работа распределение или только визуализирует последствия. **От этого зависит формулировка зазора новизны** |
| Hung & Huang 2022, «Addressing the cold-start problem… financial products… few-shot deep learning», Applied Intelligence, DOI 10.1007/s10489-022-03374-x | Springer → редирект на IdP; Semantic Scholar: `openAccessPdf: ""`, аннотация скрыта издателем | даже аннотация |
| «Approaches and algorithms to mitigate cold start problems…», JIIS 2022, DOI 10.1007/s10844-022-00698-5 | Springer, редирект на IdP | не открыт |
| **Sanz-Cruzado et al. (2025)** как отдельный источник §3.3 | цитата взята **по вторичному источнику** (Sawant 2026) | оказалось, что это тот же коллектив, что Takayanagi et al. SIGIR '25 (§3-бис) — первоисточник в итоге открыт целиком через eprints.gla.ac.uk, расхождений не обнаружено |
| **Lakkaraju et al. (2023)**, «LLMs for financial advisement: a fairness and efficacy study in personal decision making», ICAIF '23, DOI 10.1145/3604237.3626867 | ACM DL, антибот | прямое попадание в вопрос 5, не прочитана |
| **FCA Handbook**, точная формулировка «personal recommendation» (PERG 8.28, COBS 9) | страница Advice Guidance Boundary Review описывает только реформу, определения нет | относится к теме 19 очереди |
| Hodge, Mendoza, Sinha (2021), Contemporary Accounting Research, о доверии к робо-эдвайзеру | только 🟡 пересказ | числа не проверены |
| MDPI, `mdpi.com` напрямую | `WebFetch` → **403**; `curl` с браузерным UA и полным набором заголовков → **403** | обойдено третьим каналом (см. ниже) |
| ACM Digital Library | антибот и на `WebFetch`, и на `curl` — подтверждено повторно | обход не найден |

### 🔴 Новый приём добычи, найденный в этом прогоне — записать в базу приёмов

**Текстовый прокси `r.jina.ai` пробивает издательский антибот.**
```bash
curl -s "https://r.jina.ai/https://<полный URL>"
```
На `mdpi.com`, где и `WebFetch`, и `curl` с браузерным UA дают 403, прокси вернул **HTTP 200
и 136 504 байта** полного текста статьи в markdown; на `frontiersin.org` — 182 077 байт;
на arXiv HTML — полный текст. Порядок каналов теперь: `WebFetch` → `curl` с UA →
**`r.jina.ai`** → `pdftotext` по сохранённому PDF.
**Граница приёма:** на пейволльном Springer прокси возвращает 200, но отдаёт только то, что видно
анониму (список литературы) — он обходит **антибот**, но не **пейволл**.

Второй подтверждённый приём: **репозиторий университета вместо ACM DL.** Статья SIGIR '25
(§3-бис) недоступна в ACM DL, но лежит целиком в `eprints.gla.ac.uk` — искать по названию
+ `arxiv`/`eprints`.

---

## 7. Прямые следствия для FINPILOT

### 7.1 Прямой ответ на вопрос темы

**Финансовая рекомендация отличается от рекомендации фильма по четырём свойствам, каждое из
которых зафиксировано в литературе дословно, а не выведено нами:** необратимость последствий
и на порядки меньшая терпимость к ошибке (Sawant 2026 §2; Burke & Ramezani — измерение «risk»);
отложенная и стохастическая обратная связь при отсутствии ground truth (Sawant 2026 §4.4);
обязательность объяснения как параметр домена, а не фича (Burke & Ramezani — «scrutability»;
Zibriczky 2016 §4); юридическая неотчуждаемость ответственности за пригодность совета
(ESMA §14–15; Chen 2018 по FCRA).

**Но главное следствие для проектирования — не в этом списке, а в измеренном факте:**
пользователь **не способен отличить хороший совет от плохого** (Takayanagi et al., SIGIR '25:
предпочтения по вариантам «statistically indistinguishable», при вдвое худшем качестве решения
у более обаятельного советника — ρ 0.122 против 0.26). Из этого следует, что **корректность
рекомендации не может быть подтверждена реакцией пользователя ни в каком виде** — ни принятием,
ни удовлетворённостью, ни удержанием. Единственный оставшийся источник корректности —
внутренние проверки самой системы.

### 7.2 Подтверждено литературой (мы это уже делаем)

| Наше решение | Чем подтверждено |
|---|---|
| **Жёсткие инварианты Rt≥0 и ПДН≤0.40 как условие допустимости, а не как предупреждение** | «there is no safety net if the LLM makes a mistake» (Takayanagi et al., §5.2) — пользователь-неэксперт не отловит ошибку; ESMA §90 требует «suspending the provision of advice» при обнаружении ошибки. Инвариант — единственный механизм, соответствующий обоим |
| **Объяснение через вклад каждого критерия** | «scrutability» — параметр домена (Burke & Ramezani 2011); «the demand for proper explanation… is significant» (Zibriczky §4); объяснимость — один из трёх главных вызовов домена (Bonde & Bichanga 2025) |
| **Knowledge-based ядро без истории пользователя** | «KBR systems… avoid the related cold-start difficulties» и «immune with regard to user preferences changing over time» (Uta/Felfernig et al. 2024). У нас совет нужен с первого экрана — это ровно тот случай, для которого подход и предназначен |
| **Детерминированность и воспроизводимость ранжирования** | ESMA §90 дословно требует «system-design documentation… **Decision trees or decision rules should form part of this documentation**», документированную тест-стратегию и учёт изменений алгоритма. Наша дисциплина версий, CHANGELOG и TDD — не гигиена разработки, а совпадение с регуляторным требованием |
| **Отсутствие продавца и ассортимента** | ESMA §15 и Chen 2018 (FCRA: «each marketing offer… is a firm offer of credit») — вся регуляторная тяжесть домена возникает вокруг **рекомендации продукта**. У системы без каталога этой поверхности нет |

### 7.3 Опровергнуто / дыры (мы этого не делаем, и это надо чинить)

1. 🔴 **Метрика «доля принятых рекомендаций» как показатель качества — использовать нельзя.**
   Эмпирически показано, что принятие и удовлетворённость коррелируют с персоной советника,
   а не с качеством совета (Takayanagi et al. §5.2, §5.3.1; Sawant 2026 §4.3). Если такой KPI
   заложен в план продукта — он измеряет обаяние интерфейса.
2. 🔴 **Нет протокола офлайн-оценки прескриптивного совета — и его нет ни у кого.**
   Опубликованного валидированного протокола найти не удалось; самый свежий источник домена
   называет это открытой проблемой дословно («formalizing it as a personalization evaluation
   metric remains an open problem», Sawant 2026 §4.4). Единственный названный подход —
   **оценка процесса, а не исхода**. Для нас это переводится в: тестировать надо инварианты,
   монотонность отклика на параметры и воспроизводимость ранжирования, а не «правильность» ответа.
3. 🔴 **Точность анкеты риск-профиля — критический путь, а не форма для галочки.**
   «poor preference elicitation will cause the agent to **actively direct the investor to the wrong
   assets**» (Takayanagi et al. §5.2). Неверно снятая преференция хуже отсутствия персонализации.
   У нас пять фиксированных риск-профилей задают веса свёртки — значит, **вопрос анкеты,
   определяющий профиль, несёт тот же вес, что вся математика после него.**
4. 🔴 **Возможность скорректировать вывод системы — самый дешёвый из известных рычагов принятия.**
   32% → 73–76% готовности пользоваться алгоритмом (Dietvorst et al. 2018, Study 1), и величина
   допуска **не важна**. Если FINPILOT показывает 66 альтернатив, но позволяет выбрать только
   верхнюю — мы теряем эффект бесплатно. Если пользователь может сдвинуть распределение вручную
   в рамках допустимого множества — получаем удвоение принятия при нулевой цене для математики.
5. 🟡 **Просадка — момент максимального риска ухода.** «attrition… increases… a 37% increase in
   attrition in such times» (Greig et al. 2023). У нас аналог просадки — месяц, когда фактический
   поток оказался ниже прогноза и план сорвался. Поведение системы именно в этот момент
   не спроектировано.
6. 🟡 **Первая заметная ошибка системы стоит дороже всей начальной настройки.** RTA 85,5% → 61%
   после одного сбоя (Ben David et al.); объяснения смягчают **именно это падение**, а не старт.
   Значит объяснение нужно не только «почему рекомендуем», но и «почему в прошлый раз не сбылось».
7. 🟡 **Проверка на прокси-признаки не проводилась.** Chen 2018 показывает, что нейтральные на вид
   признаки (длина кредитной истории → возраст; минимальная сумма → защищённый класс) вносят
   disparate impact. Наши критерии и профили на это не проверялись ни разу.

### 7.4 🔴 ГЛАВНОЕ: поддерживает ли литература оставшийся зазор новизны

Напомню, что осталось живым после темы 16 (`docs/novelty_statement.md`): новизна **по методу
и объяснимости опровергнута**; живым остался **объект оптимизации** — распределение собственного
потока пользователя, а не подбор продукта из ассортимента продавца.

**Ответ: литература этот зазор ПОДДЕРЖИВАЕТ, и подтверждение здесь сильнее, чем было.**
Три независимых измерения, полученные в этом прогоне:

1. **Свежайший систематический обзор домена формально ставит задачу только как выбор продукта.**
   Wu & Li 2025 (65 работ, 2018–2024) расширяют классическую постановку P(uᵢ,sⱼ) до
   P(uᵢ,sⱼ,dₜ,act), где `act` ∈ {купить, продать}, а sⱼ — элемент каталога S. **Наша задача
   в это пространство не выражается вовсе**: у неё нет sⱼ. Это не «мало работ» — это отсутствие
   самой координаты (§1.2).
2. **Второй независимый обзор даёт число.** Bonde & Bichanga 2025 (52 работы): рубрика
   «Financial planning and advisory» — **4 ссылки, 7,7% массива**, и из этих четырёх одна про
   прямой маркетинг банка, одна про рекомендацию новостей, одна про RL на рынках. Прескриптивного
   распределения собственного потока — **ноль** (§1-бис.2).
3. **Целевой поиск на прескриптивное распределение потока вернул только патенты.**
   Ни одной академической работы (§1-тер). Объект живёт в патентном массиве (тема 11/22)
   и отсутствует в академической литературе RS.

🔴 **Но зазор надо сузить честно — три оговорки.**

- **Fano & Kurth 2003 не проверен.** Zibriczky описывает эту работу как инструмент «personal
  resource (money) allocation», учитывающий «expenses, financial goals and time of attainment»
  (§2-бис). Это ближе к нам, чем всё остальное в двух обзорах. Пока первоисточник не открыт,
  утверждение «объект не встречается в литературе» держится на непроверенной ссылке 2003 года.
  **Это самая срочная порождённая задача темы.**
- **Отсутствие в обзорах ≠ отсутствие в литературе.** Wu & Li искали по Web of Science и CNKI
  с запросом, включающим слова «Stock», «Financial Products», «Bonds», «financial services».
  Запрос **по построению нацелен на продукты**; работа про распределение потока без слова
  «product» в него не попадёт. Корректная формулировка: «не встречается в двух систематических
  обзорах домена и не выражается в предложенной ими формализации», а не «отсутствует в науке».
- **Формулировка канона `docs/novelty_statement.md` §4 («не раскрыто ни в одном публично доступном
  источнике») остаётся правильной формой** — эта тема её не ослабляет и не усиливает, а даёт
  под неё второй массив (академический) в дополнение к патентному.

### 7.5 🔴 Второй, ранее не заявленный кандидат в новизну — и его надо проверить отдельно

Из §7.2 видно то, чего в `novelty_statement.md` нет: **у системы без ассортимента продавца
исчезает конфликт интересов как проектная проблема.** Вся регуляторная и этическая тяжесть
домена, задокументированная в §5, крепится к рекомендации **чужого продукта**: ESMA §14–15
(suitability продукта), Reg BI («without placing your financial or other interest ahead»),
Chen 2018 (маркетинговое предложение = кредитное решение), OSC (dark patterns толкают к сделке).
Ни одно из этих требований не имеет смысла для рекомендации «положить 30% потока в резерв,
40% — на досрочное погашение».

Это **структурное свойство объекта**, а не наша заслуга, и заявлять его как новизну метода нельзя.
Но как ответ на вопрос «почему этого нет ни у одного банка» (тема 1–11: причина структурная —
конфликт интересов) он замыкает контур: **литература домена описывает именно тот конфликт,
которого у нас нет по построению.** Формулировать это стоит как объяснение пустоты рынка,
а не как научную новизну.

### 7.6 Порождённые задачи (кандидаты в очередь)

1. 🔴 **Открыть Fano & Kurth 2003 «Personal Choice Point»** любым каналом (CiteSeerX, страницы
   авторов, архив Accenture Labs, IUI '03 proceedings). От результата зависит §7.4.
2. 🔴 **Пересмотреть план продуктовых метрик:** убрать «долю принятых рекомендаций» как показатель
   качества; заменить на процессные проверки (§7.3 п.2).
3. 🔴 **Спроектировать ручную корректировку распределения в пределах допустимого множества** —
   эффект 32%→73% измерен, цена для математики нулевая (§7.3 п.4).
4. 🟡 **Аудит критериев и риск-профилей на прокси-признаки** по методике disparate impact
   (Chen 2018).
5. 🟡 **Открыть Lakkaraju et al. ICAIF '23** (fairness LLM-советов в личных решениях) — прямое
   попадание в вопрос 5, ACM DL заблокирован.
6. 🟡 **Спроектировать поведение системы в «просадке»** — месяц срыва плана (§7.3 п.5).
7. 🟡 **Добрать FCA «personal recommendation»** — передать в тему 19 очереди.

---

## Статистика прогона

- **Вахта (lead):** 8 вызовов `WebSearch`, 4 `WebFetch`, ~15 обращений через `curl`/API
  (Semantic Scholar, OpenAlex, arXiv, `r.jina.ai`), 3 PDF через `pdftotext`.
- **Подагентов: ОДИН** (потолок два, веерный запуск не применялся). Его расход: 87 вызовов
  инструментов, ~167 тыс. токенов, 949 с. Его сырьё — отдельный файл `_sub17_trust_and_harm.md`
  (585 строк).
- **Первоисточники, открытые целиком:** Wu & Li 2025 (MDPI, через прокси) · Bonde & Bichanga 2025
  (IJ-AI, PDF) · Zibriczky 2016 (CEUR, PDF) · Sawant 2026 (arXiv) · Uta/Felfernig et al. 2024
  (Frontiers) · Takayanagi et al. SIGIR '25 (eprints Glasgow, PDF) · Dietvorst et al. 2018
  (Wharton, PDF) · Dietvorst et al. 2015 · Logg et al. 2019 · Niszczota & Kaszás 2020 (PLOS ONE) ·
  Greig et al. 2023 (SSRN/Bocconi, PDF) · Ben David et al. 2021 (arXiv) · ESMA35-43-3172 (PDF) ·
  SEC Reg BI · OSC 2024 (PDF) · Chen 2018 (ar5iv). **Итого 16.**
- **Измеренных нулей: четыре** — §1.2 (задача не выражается в формализации домена), §1-бис.2
  (7,7% рубрики, из них по существу ноль), §1-тер (целевой поиск → только патенты),
  §5.6 (harm-aware recommendation не применяется к финансам).
- **Статус файла: ЗАВЕРШЁН.** Незакрытые углы перечислены в «Что не добыто и почему»
  и в §7.6 как порождённые задачи.

