# SUB-16 — Utility-based recommendation как отдельный класс (сырьё)

> Статус: **ЗАВЕРШЁН ЧАСТИЧНО.** Подпункты 1 и 2 (важнейшие) закрыты дословно; 3–5 закрыты
> частично, пробелы перечислены в конце файла. Дата: 09.09.2026.
> Правило §9/§11 CLAUDE.md: сырьё пишется в файл ДО итогового ответа.
> Зона: utility-based RS, MAUT-основания (Keeney & Raiffa), MAUT-based RS,
> обучение весов из предпочтений, критика аддитивной полезности.
> Вне зоны (закрыто другими агентами): constraint-based recommenders, FSAdvisor/VITA,
> TOPSIS/PROMETHEE.

## Легенда
- **[ДОСЛОВНО]** — прямая цитата из открытого источника, с URL и локализацией.
- **[НЕ ОТКРЫТ]** — источник недоступен, указан код ответа.
- **РЕКОНСТРУКЦИЯ ПО ПАМЯТИ** — отдельный раздел в конце, не проверено первоисточником.

---

## 1. Burke 2002 — пять классов, utility-based

**Источник добыт.** Burke, R. «Hybrid Recommender Systems: Survey and Experiments»,
User Modeling and User-Adapted Interaction 12(4), 2002, 331–370.
Издательская версия (Springer, DOI 10.1023/A:1021240730564) — **закрытая**
(Semantic Scholar: `openAccessPdf.status = "CLOSED"`; OpenAlex: `is_oa: false`, `oa_status: closed`).
Добыта **авторская препринт-копия** (титул: «To appear in User Modeling and User-Adapted
Interaction», аффилиация «California State University, Fullerton»), через Wayback Machine:
`http://web.archive.org/web/2015id_/http://josquin.cs.depaul.edu/~rburke/pubs/burke-umuai02.pdf`
(HTTP 200, application/pdf, 1 397 702 байт). Текст извлечён `pdftotext -layout`.
🔴 Нумерация страниц в препринте СВОЯ (1–…), не совпадает с журнальной 331–370.
Ниже указаны страницы препринта и разделы.

### 1.1. Основание таксономии (препринт с. 1, §1.1 «Recommendation Techniques»)

> [ДОСЛОВНО] «Recommendation techniques have a number of possible classifications (Resnick &
> Varian 1997; Schafer, Konstan & Riedl 1999; Terveen & Hill, 2001). Of interest in this
> discussion is not the type of interface or the properties of the user's interaction with the
> recommender, but rather the sources of data on which recommendation is based and the use to
> which that data is put. Specifically, recommender systems have (i) background data, the
> information that the system has before the recommendation process begins, (ii) input data,
> the information that user must communicate to the system in order to generate a
> recommendation, and (iii) an algorithm that combines background and input data to arrive at
> its suggestions. On this basis, we can distinguish five different recommendation techniques
> as shown in Table I. Assume that I is the set of items over which recommendations might be
> made, U is the set of users whose preferences are known, u is the user for whom
> recommendations need to be generated, and i is some item for which we would like to predict
> u's preference.»

### 1.2. Table I: Recommendation Techniques (препринт с. 2) — ДОСЛОВНО, целиком

| Technique | Background | Input | Process |
|---|---|---|---|
| Collaborative | Ratings from U of items in I. | Ratings from u of items in I. | Identify users in U similar to u, and extrapolate from their ratings of i. |
| Content-based | Features of items in I | u's ratings of items in I | Generate a classifier that fits u's rating behavior and use it on i. |
| Demographic | Demographic information about U and their ratings of items in I. | Demographic information about u. | Identify users that are demographically similar to u, and extrapolate from their ratings of i. |
| Utility-based | Features of items in I. | A utility function over items in I that describes u's preferences. | Apply the function to the items and determine i's rank. |
| Knowledge-based | Features of items in I. Knowledge of how these items meet a user's needs. | A description of u's needs or interests. | Infer a match between i and u's need. |

**Ключевое для нас:** у utility-based **background = только features of items**, а
**input = сама функция полезности, поставляемая пользователем**. То есть класс определяется
тем, что предпочтения приходят в систему как ФУНКЦИЯ, а не как рейтинги и не как «описание
потребности».

### 1.3. Дословное определение utility-based recommender (препринт с. 3, §1.1)

> [ДОСЛОВНО] «Utility-based and knowledge-based recommenders do not attempt to build long-term
> generalizations about their users, but rather base their advice on an evaluation of the match
> between a user's need and the set of options available. **Utility-based recommenders make
> suggestions based on a computation of the utility of each object for the user. Of course, the
> central problem is how to create a utility function for each user.** Tête-à-Tête and the
> e-commerce site PersonaLogic each have different techniques for arriving at a user-specific
> utility function and applying it to the objects under consideration (Guttman 1998). **The user
> profile therefore is the utility function that the system has derived for the user, and the
> system employs constraint satisfaction techniques to locate the best match.** The benefit of
> utility-based recommendation is that it can factor non-product attributes, such as vendor
> reliability and product availability, into the utility computation, making it possible for
> example to trade off price against delivery schedule for a user who has an immediate need.»

(выделение полужирным моё, текст не менялся)

### 1.4. Как Burke соотносит utility-based с knowledge-based — ДОСЛОВНО

**(а) Общий абзац, препринт с. 3 (конец §1.1):**

> [ДОСЛОВНО] «Knowledge-based recommendation attempts to suggest objects based on inferences
> about a user's needs and preferences. In some sense, all recommendation techniques could be
> described as doing some kind of inference. Knowledge-based approaches are distinguished in
> that they have functional knowledge: they have knowledge about how a particular item meets a
> particular user need, and can therefore reason about the relationship between a need and a
> possible recommendation. […] **Utility-based approaches calculate a utility value for objects
> to be recommended, and in principle, such calculations could be based on functional knowledge.
> However, existing systems do not use such inference, requiring users to do their own mapping
> between their needs and the features of products, either in the form of preference functions
> for each feature in the case of Tête-à-Tête or answers to a detailed questionnaire in the case
> of PersonaLogic.**»

**(б) Прямая формула подчинения, препринт с. 10, §3 (перед Table IV):**

> [ДОСЛОВНО] «Table IV summarizes some of the most prominent research in hybrid recommender
> systems. For the sake of simplicity, the table combines knowledge-based and utility-based
> techniques (**since utility-based recommendation is a special case of knowledge-based**).»

🔴 Это ключевая для FINPILOT цитата: **у самого Burke utility-based — частный случай
knowledge-based**, отличающийся тем, что «функциональное знание» не выводится системой, а
перекладывается на пользователя в виде preference/utility-функции. Далее в статье он их
и сводит в одну колонку: «(CF = collaborative, CN = content-based, DM = demographic,
**KB = knowledge-based / utility-based**)» (подпись к таблице, препринт с. 11).

### 1.5. Table II: Tradeoffs between Recommendation Techniques (препринт с. 5) — ДОСЛОВНО

| Technique | Pluses | Minuses |
|---|---|---|
| Collaborative filtering (CF) | A. Can identify cross-genre niches. B. Domain knowledge not needed. C. Adaptive: quality improves over time. D. Implicit feedback sufficient | I. New user ramp-up problem J. New item ramp-up problem K. "Gray sheep" problem L. Quality dependent on large historical data set. M. Stability vs. plasticity problem |
| Content-based (CN) | B, C, D | I, L, M |
| Demographic (DM) | A, B, C | I, K, L, M N. Must gather demographic information |
| **Utility-based (UT)** | **E. No ramp-up required F. Sensitive to changes of preference G. Can include non-product features** | **O. User must input utility function P. Suggestion ability static (does not learn)** |
| Knowledge-based (KB) | E, F, G H. Can map from user needs to products | P Q. Knowledge engineering required. |

### 1.6. Разбор плюсов и минусов utility-based (препринт с. 4) — ДОСЛОВНО

> [ДОСЛОВНО] «Utility-based and knowledge-based recommenders do not have ramp-up or sparsity
> problems, since they do not base their recommendations on accumulated statistical evidence.
> **Utility-based techniques require that the system build a complete utility function across
> all features of the objects under consideration.** One benefit of this approach is that it can
> incorporate many different factors that contribute to the value of a product, such as delivery
> schedule, warranty terms or conceivably the user's existing portfolio, rather than just
> product-specific features. In addition, these non-product features may have extremely
> idiosyncratic utility: how soon something can be delivered may matter very much to a user
> facing a deadline. A utility-based framework thereby lets the user express all of the
> considerations that need to go into a recommendation.»

> [ДОСЛОВНО] «**The flexibility of utility-based systems is also to some degree a failing. The
> user must construct a complete preference function, and must therefore weigh the significance
> of each possible feature. Often this creates a significant burden of interaction.** Tête-à-Tête
> uses a small number of "stereotype" preference functions to get the user started, but
> ultimately the user needs to look at, weigh, and select a preference function for each feature
> that describes an item of interest. This might be feasible for items with only a few
> characteristics, such as price, quality and delivery date, **but not for more complex and
> subjective domains like movies or news articles.** PersonaLogic does not require the user to
> input a utility function, but instead derives the function through an interactive
> questionnaire. While the complete explicit utility function might be a boon to some users, for
> example, technical users with specific purchasing requirements, **it is likely to overwhelm a
> more casual user with a less-detailed knowledge. Large moves in the product space, for example,
> from "sports cars" to "family cars" require a complete re-tooling of the preference function**,
> including everything from interior space to fuel economy. This makes a utility-based system
> less appropriate for the casual browser.»

> [ДОСЛОВНО, с. 5] «Knowledge- and utility-based recommenders respond to the user's immediate
> need and do not need any kind of retraining when preferences change.»

> [ДОСЛОВНО, с. 5] «Utility- and knowledge-based systems have fewer problems in this regard
> because they do not rely on having historical data about a user's preferences. **Utility-based
> systems may present difficulties for casual users who might be unwilling to tailor a utility
> function simply to browse a catalog.**»

### 1.7. Заключение статьи (препринт с. 27, §7) — ДОСЛОВНО

> [ДОСЛОВНО] «All existing recommender systems employ one or more of a handful of basic
> techniques: content-based, collaborative, demographic, utility-based and knowledge-based.
> A survey of these techniques shows that they have complementary advantages and disadvantages.»

### 1.8. Burke 2000, «Knowledge-based Recommender Systems» (ELIS 69(32):180–200)

_(ещё не добыт на момент записи этого блока)_


## 2. Keeney & Raiffa — условия законности аддитивной свёртки

Сам учебник (Keeney, R. L. & Raiffa, H., «Decisions with Multiple Objectives: Preferences and
Value Tradeoffs», Wiley 1976 / Cambridge University Press 1993) в открытом доступе **не найден**
(Google Books — только карточка без полного текста). Поэтому дословные формулировки взяты из
открытого академического источника, который явно ведёт нумерацию рисунков и страниц по
Keeney & Raiffa (ссылки вида «Figure: 5.2 on page 225 (Keeney and Raiffa)»).

**Источник:** Panchal, J. H. «07: Multi-attribute Utility Theory» (лекционный модуль DELP,
Purdue University, School of Mechanical Engineering).
URL: `https://engineering.purdue.edu/DELP/education/decision_making_slides/Module_07___Multi_attribute_Utility_Theory.pdf`
(HTTP 200, application/pdf, 5 087 134 байта; `pdftotext -layout`).
Слайды воспроизводят аппарат гл. 5 Keeney & Raiffa; на некоторых слайдах прямые отсылки
к рисункам 5.2 (с. 225), 5.4 (с. 233), 5.7 (с. 244) учебника.
🔴 Оговорка: это **вторичный, но академический источник**. Формулировки цитируются как есть,
это НЕ дословный текст Keeney & Raiffa. Первоисточник для сверки — гл. 3 (детерминированный
случай, аддитивная value function) и гл. 5–6 (риск, MAUT) учебника.

### 2.1. Preference (preferential) independence — ДОСЛОВНО из слайдов

> [ДОСЛОВНО] «**Definition (Preference Independence (PI))**
> A subset S of attributes is preferentially independent of its complement S̄ if the preference
> order of the consequences involving only changes in levels of S does not depend on the levels
> at which attributes in S̄ are held fixed.»
>
> «Example: Attribute set: {X, Y, Z, W}; S = {X, Y}; S̄ = {Z, W}.
> Preferential independence implies that the conditional indifference curves over S do not depend
> on attributes in S̄.»

### 2.2. Utility independence — ДОСЛОВНО

Двухатрибутный случай:

> [ДОСЛОВНО] «**Definition (Utility Independence)**
> Y is utility independent of Z when conditional preferences for lotteries on Y given z do not
> depend on the particular level of z.»
>
> «If Y is utility independent of Z, all conditional utility functions along horizontal cuts
> would be positive linear transformations of each other. Therefore,
> u(y, z) = g(z) + h(z)·u(y, z′) for an arbitrarily chosen z′. In other words, the conditional
> utility function over Y given z does not strategically depend on z.»
> (со ссылкой «Figure: 5.2 on page 225 (Keeney and Raiffa)»)

Обобщение на подмножества:

> [ДОСЛОВНО] «**Definition (Utility Independence (UI))**
> A subset S of attributes is utility independent of its complement S̄ if the preference order
> of the lotteries involving only changes in levels of S does not depend on the levels at which
> attributes in S̄ are held fixed.»
>
> «**Utility independence is a stronger condition. If S is UI then S is PI. The converse is not
> true.**»

🔴 Иерархия: **UI ⇒ PI**, обратное неверно. Это важно: «предпочтения не зависят от фона» в
детерминированном смысле (PI) слабее, чем то же для лотерей (UI).

### 2.3. Mutual utility independence — ДОСЛОВНО

Двухатрибутный случай:

> [ДОСЛОВНО] «For mutual utility independence of Y and Z,
> 1. Y must be utility independent of Z, i.e., u(y, z) = c₁(z) + c₂(z)·u(y, z′) ∀y, z for an
>    arbitrarily chosen z′, and
> 2. Z must be utility independent of Y, i.e., u(y, z) = d₁(y) + d₂(y)·u(y′, z) ∀y, z for an
>    arbitrarily chosen y′.»

n атрибутов:

> [ДОСЛОВНО] «**Definition (Mutual Utility Independence: Generalization to n−attributes)**
> Attributes X₁, X₂, …, Xₙ are mutually utility independent if every subset of {X₁, X₂, …, Xₙ}
> is utility independent of its complement.»

### 2.4. Что даёт mutual utility independence — МУЛЬТИЛИНЕЙНАЯ, НЕ аддитивная форма

> [ДОСЛОВНО] «**Theorem.** If Y and Z are mutually utility independent, then the two-attribute
> utility function is **multilinear**. In particular, u can be written in the form
> u(y, z) = k_Y·u_Y(y) + k_Z·u_Z(z) + k_YZ·u_Y(y)·u_Z(z), or
> u(y, z) = u(y, z₀) + u(y₀, z) + k·u(y, z₀)·u(y₀, z), where
> 1. u(y, z) is normalized by u(y₀, z₀) = 0 and u(y₁, z₁) = 1 …
> 2. u_Y(y) is conditional utility on Y normalized by u_Y(y₀) = 0 and u_Y(y₁) = 1
> 3. u_Z(z) is conditional utility on Z normalized by u_Z(z₀) = 0 and u_Z(z₁) = 1
> 4. k_Y = u(y₁, z₀), k_Z = u(y₀, z₁), k_YZ = 1 − k_Y − k_Z, and k = k_YZ / (k_Y·k_Z)»

n атрибутов:

> [ДОСЛОВНО] «**Theorem.** Given the set of attributes {X₁, X₂, …, Xₙ} with n ≥ 2, if X_i is
> utility independent of X̄_i, i = 1, 2, …, n, then
> u(x) = Σᵢ kᵢ·uᵢ(xᵢ) + Σᵢ Σ_{j>i} k_ij·uᵢ(xᵢ)·u_j(x_j)
>      + Σᵢ Σ_{j>i} Σ_{l>j} k_ijl·uᵢ(xᵢ)·u_j(x_j)·u_l(x_l) + … + k_{123…n}·u₁(x₁)·u₂(x₂)…uₙ(xₙ)»

🔴 **Это и есть главный результат для FINPILOT.** Взаимной utility-независимости достаточно
ТОЛЬКО для мультилинейной (или, при доп. условии, мультипликативной) формы. Аддитивная свёртка
Σ kᵢuᵢ — это ЧАСТНЫЙ СЛУЧАЙ, получающийся при обнулении ВСЕХ перекрёстных коэффициентов (k = 0):

> [ДОСЛОВНО] «If two attributes are mutually utility independent, their utility function can be
> represented by either a product form, when k ≠ 0, or an additive form, when k = 0.»
>
> «For k = 0, the utility function reduces to an additive function. Additive utility function:
> u(y, z) = k_Y·u_Y(y) + k_Z·u_Z(z), where k_Y and k_Z are positive scaling constants.
> **Additive utility function implies that Y and Z are mutually utility independent. But the
> converse is not true.**»

Трёхатрибутный «мостик» PI+UI (по слайдам):

> [ДОСЛОВНО] «**Result for three attributes.** IF X is utility independent of {Y, Z}, and
> {X, Y} is preferentially independent of Z, and {X, Z} is preferentially independent of Y,
> THEN u(x, y, z) = k₁u₁(x) + k₂u₂(y) + k₃u₃(z) + k·k₁k₂·u₁(x)u₂(y) + k·k₁k₃·u₁(x)u₃(z)
> + k·k₂k₃·u₂(y)u₃(z) + k²·k₁k₂k₃·u₁(x)u₂(y)u₃(z)»
> «If k ≠ 0, we get the multiplicative form: u′(x,y,z) = u′₁(x)u′₂(y)u′₃(z).
> **If k = 0, we get the additive form: u(x, y, z) = k₁u₁(x) + k₂u₂(y) + k₃u₃(z).**»

### 2.5. Additive independence — ЕДИНСТВЕННОЕ условие, эквивалентное аддитивности

> [ДОСЛОВНО] «**Checking for Additive Independence.** For additive independence, the following
> two lotteries must be equally preferable:
> ⟨(y, z), 0.5, (y′, z′)⟩ ∼ ⟨(y, z′), 0.5, (y′, z)⟩
> for all (y, z) given arbitrarily chosen y′ and z′.»

> [ДОСЛОВНО] «**Definition (Additive Independence (AI))**
> Attributes X₁, X₂, …, Xₙ are additive independent if preferences over lotteries on
> X₁, X₂, …, Xₙ depend only on their **marginal** probability distributions and not on their
> **joint** probability distribution.»
> «In other words, the preferences for the lotteries over X₁ × X₂ × … × Xₙ can be established by
> comparing the values one attribute at a time.»

**Теорема (двухатрибутный случай) — ДОСЛОВНО:**

> [ДОСЛОВНО] «**Theorem.** Attributes Y and Z are additive independent **if and only if** the
> two-attribute utility function is additive. The additive form may be either
> u(y, z) = k_Y·u_Y(y) + k_Z·u_Z(z) or u(y, z) = u(y, zᵒ) + u(yᵒ, z), where
> 1. u(y, z) is normalized by u(yᵒ, zᵒ) = 0 and u(y¹, z¹) = 1 …
> 2. u_Y(y) is a conditional utility function on Y normalized by u_Y(yᵒ) = 0 and u_Y(y¹) = 1
> 3. u_Z(z) is a conditional utility function on Z normalized by u_Z(zᵒ) = 0 and u_Z(z¹) = 1
> 4. k_Y = u(y¹, zᵒ) and k_Z = u(yᵒ, z¹)»

**Теорема (n атрибутов) — ДОСЛОВНО:**

> [ДОСЛОВНО] «The n−attribute additive utility function
> u(x) = Σᵢ u(xᵢ, x̄ᵢᵒ) = Σᵢ kᵢ·uᵢ(xᵢ)
> **is appropriate if and only if the additive independence condition holds** among attributes
> X₁, X₂, …, Xₙ, where:
> 1. u is normalized by u(x₁ᵒ, x₂ᵒ, …, xₙᵒ) = 0 and u(x₁*, x₂*, …, xₙ*) = 1.
> 2. uᵢ is a conditional utility function of Xᵢ normalized by uᵢ(xᵢᵒ) = 0 and uᵢ(xᵢ*) = 1,
>    i = 1, 2, …, n.
> 3. kᵢ = u(xᵢ*, x̄ᵢᵒ), i = 1, 2, …, n.»

### 2.6. Смысл параметра k — компенсаторность/взаимодействие атрибутов

> [ДОСЛОВНО] «**Interpretation of Parameter k.**
> ⟨A, 0.5, C⟩ ≻ / ∼ / ≺ ⟨B, 0.5, D⟩ ⟺ k > 0 : Y and Z are complements;
> k = 0 : no interaction of preference; k < 0 : Y and Z are substitutes.»

🔴 **Прямой вывод для FINPILOT.** Аддитивная свёртка U(x) = Σ kᵢuᵢ(xᵢ) законна тогда и только
тогда, когда k = 0, то есть **между критериями НЕТ взаимодействия предпочтений** — ни
комплементарности, ни субститутности. Если, скажем, «закрытие долга» и «пополнение резерва»
для пользователя взаимодействуют (одно ценно только при определённом уровне другого) —
additive independence нарушена, и аддитивная форма неверна ПО ПОСТРОЕНИЮ, а не по калибровке.
Верная форма при mutual utility independence — мультилинейная/мультипликативная.

### 2.7. Порядок работ (assessment procedure) — ДОСЛОВНО

> [ДОСЛОВНО] «Assessment Procedure for Multiattribute Utility Functions:
> 1. Introducing the terminology and ideas. 2. Identifying relevant independence assumptions.
> 3. Assessing conditional utility functions or isopreference curves. 4. Assessing the scaling
> constants. 5. Checking for consistency and reiterating.»

Шаг 2 — «identifying relevant independence assumptions» — идёт ДО оценивания весов. В типовом
инженерном применении SAW этот шаг просто пропускается.

### 2.8. Детерминированный случай (аддитивная VALUE function) — ПРОБЕЛ

Purdue-модуль покрывает риск-версию (utility, лотереи). Классический детерминированный
результат (Debreu 1960 / Keeney & Raiffa гл. 3: **аддитивная функция ценности существует ⟺
атрибуты взаимно преференциально независимы**, при n ≥ 3) в дословном виде из первоисточника
на момент записи **не добыт**. Косвенное подтверждение — см. §6 (реконструкция) и результаты
поиска, где формулировка воспроизводится как «A preference order over a set of attributes can
be represented by an additive value function if and only if the attributes are mutually
preferential independent». 🔴 Проверять по первоисточнику.

**Что удалось подтвердить по вторичному, но проверяемому источнику** — Wikipedia,
«Debreu's representation theorems», раздел «Additivity of ordinal utility function»
(`https://en.wikipedia.org/wiki/Debreu%27s_representation_theorems`), первоисточник —
Debreu, G. «Topological methods in cardinal utility theory», 1960:

> [ДОСЛОВНО, вторичный источник] «the set of commodities (X_i)_{i∈I} is called preferentially
> independent if the preference relation ⪯ induced on (X_i)_{i∈I}, given constant quantities of
> the other commodities (X_i)_{i∉I}, does not depend on these constant quantities.»
>
> «**If all subsets of commodities are preferentially-independent AND at least three commodities
> are essential** (meaning that their quantities have an influence on the preference relation ⪯),
> **then v is additive**», то есть v(x₁,…,xₙ) = Σ kᵢ·vᵢ(xᵢ).

🔴 **Условие n ≥ 3 существенно.** При n = 2 взаимной преференциальной независимости
НЕ достаточно — нужно дополнительное условие (Thomsen condition / условие двойной отмены).
Это отдельный подводный камень: модель с двумя критериями нельзя оправдать ссылкой на Debreu.


## 3. MAUT-based recommender systems

**Основной добытый источник:** Adomavicius, G., Manouselis, N., Kwon, Y. «Multi-Criteria
Recommender Systems», глава Recommender Systems Handbook (Springer). Открытая авторская копия:
`https://www.ise.bgu.ac.il/faculty/liorr/recsyshb/chmulticriteria.pdf`
(HTTP 200, application/pdf, 999 902 байта, 36 страниц; `pdftotext -layout`).
Nikos Manouselis — соавтор Manouselis & Costopoulou 2007, и эта глава — расширенная версия
той же классификации. Сам Manouselis & Costopoulou, «Analysis and classification of
multi-criteria recommender systems», World Wide Web 10(4), 2007, 415–441
(DOI 10.1007/s11280-007-0019-8) в открытом доступе **не добыт** (Springer — платно,
ResearchGate/dl.acm.org — 403, попыток не тратилось по инструкции).

### 3.1. Где MAUT сидит в классификации MCDM-подходов к RS — ДОСЛОВНО (с. 6–7 главы)

> [ДОСЛОВНО] «According to Pardalos et al. (1995) and Jacquet-Lagrèze and Siskos (2001), the
> following categories of global preference modeling approaches can be identified:
> • **Value-Focused models**, where a value system for aggregating the user preferences on the
>   different criteria is constructed. In such approaches, marginal preferences upon each
>   criterion are synthesized into a total value function, which is usually called the utility
>   function (Keeney 1992). **These approaches are often referred to as multi-attribute utility
>   theory (MAUT) approaches.**
> • **Multi-Objective Optimization models**, where criteria are expressed in the form of multiple
>   constraints of a multi-objective optimization problem. […]
> • **Outranking Relations models**, where preferences are expressed as a system of outranking
>   relations between the items, thus allowing the expression of incomparability. […]
> • **Preference Disaggregation models**, where the preference model is derived by analyzing past
>   decisions. Such approaches are sometimes considered as a subcategory of other modeling
>   categories mentioned above, since they try to infer a preference model of a given form (e.g.,
>   value function or outranking relations) from some given preferential structures that have led
>   to particular decisions in the past. Inferred preference models aim at producing decisions
>   that are at least identical to the examined past ones (Jacquet-Lagrèze and Siskos 2001).»

### 3.2. Требование к семейству критериев (consistent family of criteria) — ДОСЛОВНО (с. 5)

> [ДОСЛОВНО] «To be able to make rational decisions using multiple criteria, it has to be ensured
> that the whole set of these functions creates a **consistent family of criteria** (Roy 1996).
> A family of criteria is said to be consistent when it has the following three properties:
> a. **Monotonic**: a family of criteria is monotonic only if, for each pair of alternatives i₁ and
>    i₂, for which g_c1(i₁) > g_c1(i₂) for one criterion c₁ and g_c(i₁) = g_c(i₂) for every other
>    criterion c ≠ c₁, it can be assumed that alternative i₁ is preferred to alternative i₂.
> b. **Exhaustive**: a family of criteria is exhaustive only if, for each pair of alternatives i₁
>    and i₂, for which g_c(i₁) = g_c(i₂) upon each criterion c, we can assume that i₁ and i₂ are
>    equivalent.
> c. **Non-redundant**: a family of criteria is non-redundant only if the removal of any one of
>    the criteria leads to the violation of one of the other two properties.»

> [ДОСЛОВНО] «**The design of a consistent family of criteria for a given recommendation
> application has been largely ignored in the recommender systems literature** and constitutes an
> interesting and important problem for future research.»

🔴 Прямо применимо к FINPILOT: набор критериев модели должен быть монотонным, исчерпывающим
и неизбыточным; неизбыточность = удаление любого критерия ломает одно из двух других свойств.

### 3.3. Utility-based формулировка задачи мультикритериальной рекомендации — ДОСЛОВНО (с. 14)

> [ДОСЛОВНО] «Some multi-criteria rating systems can choose to model a user's utility for a given
> item with an overall rating R₀ as well as the user's ratings R₁, …, R_k for each individual
> criterion c (c = 1, …, k), whereas some systems can choose not to use the overall rating and
> focus solely on individual criteria ratings. Therefore, **the utility-based formulation of the
> multi-criteria recommendation problem** can be represented either with or without overall
> ratings as follows:
> R: Users × Items → R₀ × R₁ × … × R_k  (3)   или   R: Users × Items → R₁ × … × R_k  (4)»

### 3.4. Lakiotaki и UTA в RS — ДОСЛОВНО (с. 25–26)

> [ДОСЛОВНО] «In the recommender systems literature there has been some work using
> **multi-attribute utility theories from decision science, which can be described as one way to
> take a linear combination of multiple criteria and find an optimal solution** (Lakiotaki et al.
> 2008).
> For example, the approach by Lakiotaki et al. (2008) ranks the items by adopting the **UTilités
> Additive (UTA)** method proposed by (Siskos et al. 2005). Their algorithm aims to estimate
> overall utility U of a specific item for each user by adding the marginal utilities of each
> criterion c (c = 1, …, k).
>
>     U = Σ_{c=1..k} u_c(g_c)     (18)
>
> where g_c is the rating provided on criterion c, and u_c(g_c) is a **non-decreasing real-value
> function (marginal utility function)** for a specific user. Since this model uses the ranking
> information with ordinal regression techniques, **Kendall's tau** is used as a measure of
> correlation between two ordinal-level variables to compare an actual order and the predicted
> order. The empirical results obtained by using data from Yahoo! Movies show that **20.4% of
> users obtain a Kendall's tau of 1** indicating a total agreement of the orders […]»

Ссылка из библиографии главы (дословно):
> Lakiotaki K., Tsafarakis S., Matsatsinis N., «UTA-Rec: a Recommender System Based on Multiple
> Criteria Analysis», in Proc. of 2nd ACM Conf. on Recommender Systems, 2008.
> Siskos Y., Grigoroudis E., and Matsatsinis N., «UTA Methods», Springer, 2005.

### 3.5. Другие MAUT-RS, найденные в библиографии главы (дословные ссылки)

> Schmitt C., Dengler D., Bauer M., «Multivariate Preference Models and Decision Making with the
> **MAUT Machine**», in P. Brusilovsky et al. (Eds.), User Modelling (UM 2003), LNAI 2702,
> 297–302, Berlin Heidelberg: Springer-Verlag, 2003.
>
> Schmitt C., Dengler D., Bauer M., «**The MAUT-Machine: An Adaptive Recommender System**»,
> in Proc. of ABIS Workshop 'Adaptivität und Benutzermodellierung in interaktiven
> Softwaresystemen' (ABIS'02), Hannover, Germany, October 2002.
>
> Schickel-Zuber V., Faltings B., «**Heterogeneous Attribute Utility Model**: A new approach for
> modelling user profiles for recommendation systems», in Proc. of the Workshop on Knowledge
> Discovery in the Web (WebKDD2005), Chicago, Illinois, USA, August 21, 2005.
>
> Srikumar K., Bhasker B., «Personalized Product Selection in Internet Business», Journal of
> Electronic Commerce Research, 5(4), 216–227, 2004.

### 3.6. Huang, «Designing utility-based recommender systems for e-commerce»

🔴 **НЕ ДОБЫТ.** В библиографии этой главы отсутствует; отдельный поиск по нему в рамках
бюджета не проводился. Оставлено следующему агенту.

### 3.7. Adomavicius & Kwon 2007 — aggregation function approach — ДОСЛОВНО (с. 19–21)

> [ДОСЛОВНО] «the **aggregation function approach** assumes that the overall rating serves as an
> aggregate of multi-criteria ratings (Adomavicius and Kwon 2007). Given this assumption, this
> approach finds aggregation function f that represents the relationship between overall and
> multi-criteria ratings, i.e., r₀ = f(r₁, …, r_k).  (15)»

> [ДОСЛОВНО] «The aggregation function approach consists of three steps […]. First, this approach
> estimates k individual ratings using any recommendation technique. That is, the k-dimensional
> multi-criteria rating problem is decomposed into k single-rating recommendation problems.
> Second, **aggregation function f is chosen using domain expertise, statistical techniques, or
> machine learning techniques.** For example, the domain expert may suggest a simple average
> function of the underlying multi-criteria ratings for each item based on her prior experience
> and knowledge. An aggregation function also can be obtained by using statistical techniques,
> such as **linear and non-linear regression** analysis techniques, as well as various
> sophisticated machine learning techniques, such as **artificial neural networks**. Finally, the
> overall rating of each unrated item is computed based on the k predicted individual criteria
> ratings and the chosen aggregation function f.»

> [ДОСЛОВНО] «As one example of possible aggregation functions, Adomavicius and Kwon (2007) use
> **linear regression and estimate coefficients (i.e., importance weights of each individual
> criterion) based on the known ratings**.»

> [ДОСЛОВНО] «Adomavicius and Kwon (2007) also note that the aggregation function can have
> different **scopes: total** (i.e., when a single aggregation function is learned based on the
> entire dataset), **user-based or item-based** (i.e., when a separate aggregation function is
> learned for each user or item).»

> [ДОСЛОВНО] «Empirical analysis using data from Yahoo! Movies shows that the aggregation function
> approach (using multi-criteria rating information) **outperforms a traditional single-rating
> collaborative filtering technique (using only overall ratings) by 0.3–6.3% in terms of
> precision-in-top N (N = 3, 5, and 7) metric** (Adomavicius and Kwon 2007).»

🔴 Прямой вывод для FINPILOT: даже в лучшей известной эмпирике выигрыш от мультикритериальности
над однокритериальным baseline — **единицы процентов**. Это калибр эффекта, на который стоит
рассчитывать, а не разы.


## 4. Обучение весов полезности из предпочтений пользователя

### 4.1. Преференциальная дезагрегация как класс (ДОСЛОВНО, гл. Adomavicius/Manouselis/Kwon, с. 28)

> [ДОСЛОВНО] «For a recommender system to achieve good recommendation performance, users typically
> need to provide to the system a certain amount of feedback about their preferences (e.g., in the
> form of item ratings). […] **Multi-criteria rating systems may require a more significant level
> of user involvement because each user would need to rate an item on multiple criteria.**
> Therefore, it is important to measure the costs and benefits of adopting multi-criteria ratings
> and find an optimal solution to meet the needs of both users and system designers.
> **Preference disaggregation methods could support the implicit formulation of a preference model
> based on a series of previous decisions. A characteristic example is the UTA (i.e., UTilités
> Additive) method, which can be used to extract the utility function from a user-provided ranking
> of known items** (Lakiotaki et al. 2008). Another example is the ability to obtain each user's
> preferences on several attributes of an item **implicitly from the user's written comments,
> minimizing intrusiveness** (Plantie et al. 2005; Aciar et al. 2007). There are also some
> empirical approaches with less computational complexity (Sampaio et al. 2006).»

Это ровно ответ на подпункт 4 задания: **вместо фиксированных весов — вывод функции полезности
из РАНЖИРОВКИ, которую пользователь уже дал**. UTA — ordinal regression: находим маргинальные
функции u_c и веса так, чтобы восстановленный порядок совпал с заявленным (мера согласия —
Kendall's tau, см. §3.4).

### 4.2. Первоисточник UTA

Jacquet-Lagrèze, E. & Siskos, J. «Assessing a set of additive utility functions for multicriteria
decision-making: the UTA method», European Journal of Operational Research 10(2), 1982, 151–164.
🔴 **Дословно не добыт** (Elsevier, платно; открытая копия в рамках бюджета не найдена).
В добытой главе он присутствует только через ссылки Jacquet-Lagrèze and Siskos 2001 и
Siskos, Grigoroudis, Matsatsinis «UTA Methods», Springer, 2005.

### 4.3. Conjoint analysis, Bayesian preference elicitation (Boutilier)

🔴 **НЕ ДОБЫТО** — бюджет исчерпан на подпунктах 1–3, которые в задании названы важнейшими.
Найденный, но не открытый след: «Survey of Preference Elicitation Methods» (Chen & Pu) —
ResearchGate, не открывался. Оставлено следующему агенту.


## 5. Критика аддитивной полезности в RS-контексте

### 5.1. Компенсаторность — прямо из аппарата MAUT (см. §2.6)

Формально аддитивная свёртка законна только при k = 0, «no interaction of preference».
Любая комплементарность (k > 0) или субститутность (k < 0) между критериями делает аддитивную
форму неверной по построению. Это НЕ вопрос точности калибровки весов — это вопрос
существования такого представления вообще.

### 5.2. Проблема total order без общего критерия — ДОСЛОВНО
(Adomavicius/Manouselis/Kwon, с. 24–25)

> [ДОСЛОВНО] «**However, without an overall rating the recommendation process becomes more
> complex, because it is less apparent how to establish the total order of the items.** For
> example, suppose that we have a two-criterion movie recommender system, where users judge
> movies based on their story (i.e., plot) and visual effects. Further, suppose that one movie
> needs to be chosen for recommendation among the following two alternatives: (i) movie X,
> predicted as 8 in story and 2 in visuals, and (ii) movie Y, predicted as 5 in story and 5 in
> visuals. **Since there is no overall criterion to rank the movies, it is not easy to judge which
> movie is better, unless some other modeling approach is adopted**, using some non-numerical
> (e.g., rule-based) way for expressing preferences. Several approaches have been proposed in the
> recommender systems literature to deal with this problem: some try to design a total order on
> items and obtain a single global optimal solution for each user, whereas others take the
> existing partial order of the items and **find multiple (Pareto optimal) solutions**.»

🔴 Это и есть каноническая иллюстрация компенсаторности: (8, 2) и (5, 5) при равных весах дают
одинаковую сумму, но пользователь их различает. Аддитивная свёртка эту разницу СТИРАЕТ. Прямой
аналог в FINPILOT: распределение с сильным перекосом в одну цель и сбалансированное могут
получить один SAW-балл.

### 5.3. Альтернативные, некомпенсаторные схемы агрегации — ДОСЛОВНО (с. 17)

Adomavicius & Kwon предлагают не только взвешенную сумму, но и **минимаксную** агрегацию:

> [ДОСЛОВНО] «Adomavicius and Kwon (2007) propose two aggregation approaches: an average and the
> **worst-case (i.e., smallest) similarity** […]. As a general approach, Tang and McCalla (2009)
> […] compute an aggregate similarity as a **weighted sum** of individual similarities over
> several criteria of each paper […]. In their approach, the weight of each criterion c, denoted
> by w_c, is chosen to reflect how important and useful the criterion is considered to be for the
> recommendation.»
>
> «• Average similarity: sim_avg(u, u′) = (1/(k+1)) Σ_{c=0..k} sim_c(u, u′)   (7)
> • Aggregate similarity: sim_aggregate(u, u′) = Σ_{c=0..k} w_c · sim_c(u, u′)   (8)
> • **Worst-case (smallest) similarity: sim_min(u, u′) = min_{c=0..k} sim_c(u, u′)**   (9)»

И дистанционные метрики, среди которых **Чебышёв — некомпенсаторная**:

> [ДОСЛОВНО] «• Manhattan distance: Σ_{c=0..k} |R_c(u,i) − R_c(u′,i)|   (10)
> • Euclidean distance: √(Σ_{c=0..k} |R_c(u,i) − R_c(u′,i)|²)   (11)
> • **Chebyshev (or maximal value) distance: max_{c=0..k} |R_c(u,i) − R_c(u′,i)|**   (12)»

🔴 Практический вывод: у линейной свёртки есть прямые некомпенсаторные заменители в том же
классе моделей — min / Чебышёв. Это готовый вариант «жёсткого» режима, где провал по одному
критерию нельзя откупить другим.

### 5.4. Критика фиксированных весов — ДОСЛОВНО

**(а) Веса задаются экспертным суждением, а не выводятся:**

> [ДОСЛОВНО, с. 17] «the weight of each criterion c, denoted by w_c, **is chosen to reflect how
> important and useful the criterion is considered to be** for the recommendation.»

> [ДОСЛОВНО, с. 20] «aggregation function f is chosen **using domain expertise**, statistical
> techniques, or machine learning techniques. For example, **the domain expert may suggest a
> simple average function** of the underlying multi-criteria ratings for each item **based on her
> prior experience and knowledge**.»

**(б) Одна функция на весь датасет vs персональная — прямая постановка проблемы фиксированных
профилей:**

> [ДОСЛОВНО, с. 21] «the aggregation function can have different scopes: **total** (i.e., when a
> single aggregation function is learned based on the entire dataset), **user-based or item-based**
> (i.e., when a separate aggregation function is learned for each user or item).»

**(в) Семейство критериев обычно не проверяется на состоятельность:**

> [ДОСЛОВНО, с. 5] «**The design of a consistent family of criteria for a given recommendation
> application has been largely ignored in the recommender systems literature** and constitutes an
> interesting and important problem for future research.»

**(г) Сам Burke о том же (см. §1.6):**

> [ДОСЛОВНО] «The user must construct a **complete** preference function, and must therefore weigh
> the significance of each possible feature. **Often this creates a significant burden of
> interaction.** […] Large moves in the product space […] require a **complete re-tooling of the
> preference function**.»

И минус P из Table II: «**Suggestion ability static (does not learn)**» — фиксированная функция
полезности не учится на поведении.

### 5.5. Чего в добытых источниках НЕТ

- Дословной критики **чувствительности к нормировке** шкал (min-max vs z-score vs
  utility-функция) в RS-контексте — не найдено, тема не покрыта добытыми файлами.
- Численных экспериментов «SAW против некомпенсаторной агрегации» в RS.
- Рекомендация: искать в MCDA-литературе (Roy, Bouyssou) — но это пересекается с зоной агента
  по outranking/PROMETHEE, к которой мне лезть запрещено.


## 6. РЕКОНСТРУКЦИЯ ПО ПАМЯТИ (не проверено первоисточником)

🔴 Всё ниже — память модели, а НЕ выписки. Использовать только как список гипотез для проверки,
не цитировать в докладных материалах.

1. **Keeney & Raiffa 1976, гл. 3** — детерминированный случай. Теорема 3.6 (примерно): если
   n ≥ 3 и атрибуты **взаимно преференциально независимы**, то существует аддитивная функция
   ценности v(x) = Σ λᵢ vᵢ(xᵢ). Для n = 2 требуется дополнительно **условие Томсена**
   (двойная отмена). Достаточное практическое условие в K&R: если {X₁, X_i} преференциально
   независимо от остальных для всех i = 2..n, то весь набор взаимно преференциально независим.
2. **Keeney & Raiffa 1976, гл. 6** — n-атрибутная теорема: если Xᵢ utility-независим от X̄ᵢ для
   каждого i (mutual UI), форма мультилинейная; при дополнительном условии
   Σ kᵢ = 1 получается аддитивная, при Σ kᵢ ≠ 1 — мультипликативная
   1 + k·u(x) = Π (1 + k·kᵢ·uᵢ(xᵢ)). Проверка на практике: если сумма оценённых весов
   заметно ≠ 1 — аддитивную форму применять нельзя.
3. **Дьер (Dyer 2005)** в «MCDA: State of the Art Surveys» пересказывает ровно эту иерархию
   условий и добавляет **measurable value functions** (Dyer & Sarin 1979): «difference
   independence» и «weak difference independence» — детерминированные аналоги additive
   independence и utility independence.
4. **Huang, Z. (примерно 2011), «Designing utility-based recommender systems for e-commerce:
   Evaluation of preference-elicitation methods»**, Electronic Commerce Research and
   Applications — сравнивает методы получения весов (прямое назначение, AHP/попарные сравнения,
   conjoint/SWING) для utility-based рекомендатора. Ключевой заявленный вывод: точность
   рекомендаций сильнее зависит от метода elicitation, чем от формы свёртки. **Проверять.**
5. **Adomavicius & Kwon 2007**, IEEE Intelligent Systems 22(3), 48–55 — «New recommendation
   techniques for multicriteria rating systems». Именно та работа, из которой в §3.7 приведены
   similarity-based и aggregation-function подходы (по добытой главе).
6. **Boutilier** — Bayesian preference elicitation / regret-based elicitation: веса не
   оцениваются точно, а держатся как множество допустимых; рекомендация выбирается по
   **minimax regret** над этим множеством, и запрос пользователю выбирается тот, что сильнее
   всего сузит regret. Это прямой ответ на «фиксированные веса — плохо»: вместо точечных весов
   — множество + робастный критерий. **Проверять.**
7. **Conjoint analysis** (маркетинг, Green & Srinivasan) — оценивание частичных полезностей
   (part-worths) по выбору между профилями; фактически та же аддитивная модель, оценённая
   регрессией по выборам. Ограничение — те же условия аддитивности.
8. **UTA/UTASTAR** — линейное программирование: минимизируется сумма ошибок σ⁺/σ⁻ отклонения
   восстановленного порядка от заданного пользователем; UTASTAR (Siskos & Yannacopoulos 1985)
   — улучшенная версия с двойным набором переменных ошибки. Даёт не одну функцию, а **множество**
   совместимых с ранжировкой — отсюда постоптимальный анализ.

---

## Итог по полноте

| Подпункт задания | Статус |
|---|---|
| 1. Burke 2002: определение, Table I, Table II, связь с knowledge-based | ✅ **закрыт дословно** (авторский препринт) |
| 1b. Burke 2000, «Knowledge-based Recommender Systems» (ELIS) | ❌ не добыт |
| 2. Keeney & Raiffa: PI / mutual PI / UI / AI + теоремы | 🟡 **закрыт дословно по академическому вторичному источнику** (Purdue DELP), первоисточник не открыт |
| 2b. Детерминированный случай (аддитивная value function, Debreu) | 🟡 частично, через Wikipedia + результаты поиска |
| 3. MAUT-based RS | 🟡 закрыт по главе Adomavicius/Manouselis/Kwon; Huang не добыт; Manouselis & Costopoulou 2007 сам не открыт |
| 4. Обучение весов из предпочтений (UTA) | 🟡 частично; первоисточник UTA 1982 не добыт; Boutilier/conjoint не добыты |
| 5. Критика аддитивной полезности в RS | 🟡 частично; чувствительность к нормировке не покрыта |

**Файлы на диске (временные, не в репозитории):** извлечённые тексты лежали в
scratchpad-каталоге сессии; PDF-первоисточники доступны по URL, указанным выше.

---

## ДОБОР Г31.5 — отказ адреса (17.09.2026)

**Каналы (замер 17.09.2026):** Crossref **200** · Unpaywall **200** · S2 `/paper/DOI:` **200** · 🔴 `basepub.dauphine.fr` — прямой `curl` **000, 0 б** (соединение не установлено), `r.jina.ai` **422** «Domain 'basepub.dauphine.fr' could not be resolved» — хост снят с DNS · Wayback replay **302 → 200**.

Кандидаты по файлу (последние упоминания — стр. 535–546; позже в файле ничего нет; в `constraint_based_utility_recsys` — стр. 1175 «пейвол Elsevier»):
- Jacquet-Lagrèze & Siskos 1982 (UTA) — «открытая копия в рамках бюджета не найдена» — класс «не пробовал, бюджет».
- Chen & Pu «Survey of Preference Elicitation Methods» — 🟢 **уже добыт** в `approach_validity_2026-09-10.md` (стр. 3538, EPFL). Здесь запись устарела.

### Г31.5-S1. Jacquet-Lagrèze & Siskos 1982 — 🟢 авторская аннотация ДОБЫТА; 🔴 метка «green, CC BY-SA» ложная, полного текста нет

- Crossref — **200**: `10.1016/0377-2217(82)90155-2`, *EJOR* **10(2):151–164**.
- Unpaywall — **200**: `is_oa: True`, `oa_status: "green"`, локация `basepub.dauphine.fr/handle/123456789/13111`. S2 — **200**: `openAccessPdf.status: "GREEN"`, `license: "CCBYSA"`, тот же адрес, `citationCount: 1123`.
- Адрес мёртв на уровне DNS (коды выше) — BIRD, репозиторий Université Paris-Dauphine, выведен из работы.
- Wayback по СТРАНИЦЕ репозитория: `web.archive.org/web/2020/<адрес>` — **302** на снимок **08.12.2022** (`20221208070214`); снимок — **HTTP 200, 32 754 б**. 🔴 В записи **нет ни одного файла** (ни `bitstream`, ни `citation_pdf_url`; единственный PDF на странице — справка интерфейса `AideHelp.pdf`). Запись BIRD — только метаданные и аннотация; метки Unpaywall/S2 «green» и «CC BY-SA» поставлены по наличию записи в репозитории, а не файла. Второй подряд такой случай в этом подбатче (см. Ng et al. 2012 в `dp_vs_enumeration`).

**Аннотация ДОСЛОВНО (снимок BIRD 08.12.2022, «Abstract (EN)»):**

> «The purpose of the method presented in this paper is to assess additive utility functions which aggregate multiple criteria in a composite criterion, using the information given by a subjective ranking on a set of stimuli or actions (weak-order comparison judgments) and the multicriteria evaluations of these actions. It is an ordinal regression method using linear programming to estimate the parameters of the utility function. Stability and sensitivity analysis leads to the assessment of a set of utility functions by means of post-optimality analysis techniques in linear programming. Finally, a simple illustrative example is presented and some extensions of the method are proposed.»

**Выжимка.** Подтверждает пересказ файла (§4.2) первоисточником-аннотацией: UTA — **порядковая регрессия через ЛП**, восстанавливающая аддитивную полезность по **ранжированию** набора альтернатив, и выдающая **множество** совместимых функций (пост-оптимальный анализ), а не одну. Для калибровки весов по экспертным ранжированиям это прямой, 1982 г., предшественник подхода Felfernig et al. (подгонка скоринговых правил под эталонные ранжирования, см. `constraint_based_utility_recsys` Г31.5-C2); UTA при этом честно признаёт неединственность решения — довод против публикации одного набора весов как «откалиброванного».

## ИТОГ Г31.5 — _sub16_utility_based_rs

2 кандидата: **Chen & Pu — закрыт ссылкой** (`approach_validity`); **UTA 1982 — аннотация добыта через Wayback по странице репозитория**, полный текст не существует в открытом виде (запись без файла, Elsevier — закрыт). Пройденные адреса: `api.crossref.org/works/…`, `api.unpaywall.org/v2/…`, `api.semanticscholar.org/graph/v1/paper/DOI:…`, `basepub.dauphine.fr/handle/123456789/13111` (000), `r.jina.ai/https://basepub.dauphine.fr/…` (422), `web.archive.org/web/20221208070214/…` (200, без файла).
Канон не затрагивается. Задолженности нет.
