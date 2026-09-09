# Портфельная теория и математика робо-эдвайзеров — первичный материал

**Дата сборки:** 08.09.2026
**Задача:** что из академической портфельной теории реально применяется в проде робо-эдвайзеров
и что из этого применимо к распределению свободного денежного потока в FINPILOT.
Разбор МЕТОДОВ, не конкурентов.

---

## 🔴 ГЛАВНАЯ ОГОВОРКА О КАЧЕСТВЕ ЭТОГО МАТЕРИАЛА — ЧИТАТЬ ПЕРВОЙ

**В этой сессии не получено НИ ОДНОГО живого первоисточника.** `WebSearch` был исчерпан
(400/400 вызовов) ДО первого запроса обоих субагентов. Обходные каналы, предписанные
протоколом, отработаны и тоже провалились:

| Канал | Результат |
|---|---|
| `WebSearch` | исчерпан на старте сессии, 0 живых запросов у обоих субагентов |
| `curl` → DuckDuckGo Lite | anti-bot challenge («anomaly»), результатов нет |
| `WebFetch` → Google/Bing | геолокационный мусор (испаноязычная выдача, реклама аудиотехники) |
| `WebFetch` → угаданные прямые URL | частично «успех», но ТОЛЬКО через встроенный суммаризатор |
| `pdftotext` (обход §3в) | **не применён ни разу** — ни один PDF не дошёл до диска |
| Semantic Scholar API | 429 rate limit, в т.ч. после паузы |
| Ledoit site, SSRN, quantresearch.org, LBS mirror | 403 / 404 / cert error |

**Следствия, которые нельзя замазывать:**

1. Всё содержимое частей 1 и 2 — **знание моделей из обучения (cutoff ~май 2026)**, а не
   прочитанные документы. Разметка по умолчанию — [Г], не [Ф].
2. Немногие «успешные» фетчи части 2 прошли через суммаризатор `WebFetch`: субагент не видел
   сырого текста. Даты и «цитаты формул» оттуда — наиболее вероятные артефакты суммаризатора.
3. **Это ровно тот случай, когда разница между оригинальной архитектурой Anthropic и нашим
   исполнением повлияла на результат по существу**, а не косметически: метод (лид → параллельные
   субагенты → синтез лида) отработал полностью, но инструментальная база оказалась пустой.
   Честный статус исследования — **не выполнено в части внешних источников**.
4. Часть 0 (наш канон) и часть 3 (перенос) — полноценны: они опираются на файлы репозитория,
   прочитанные напрямую, а не на веб.

**Что делать дальше:** перезапустить части 1–2 в сессии с работающим `WebSearch`.
До этого — ни одну цифру из частей 1–2 не переносить в `docs/`, ВКР, README или витрину.
Совпадение двух независимых моделей на одной ссылке — слабое свидетельство, не подтверждение.

---

**Классификация запроса:** breadth-first — вопрос распадается на два независимых блока
(академическая литература / индустриальная практика), которые не нужны друг другу до синтеза.
Третий блок (перенос на нашу задачу) — depth-first, и он не поисковый: это рассуждение
лида по канону `docs/math_model.md` v3.9.0.

**Субагентов:** 2 (жёсткий потолок сессии — владелец ограничил двумя из-за трёх сожжённых
лимитов на предыдущих проходах). Углы: (1) академическая литература портфельной оптимизации;
(2) практика и раскрытие методики робо-эдвайзеров США. Второго круга не было: круг 1 упёрся
не в содержание, а в отсутствие инструмента — добор теми же тулами дал бы тот же ноль
(правило остановки шага 3а: «субагент вернул „источников не нашёл“ — синтез»).

**Реальных вызовов:** `WebSearch` — 0 успешных (исчерпан). `WebFetch`/`curl` — ~30 попыток
на двоих, из них ни одной с сырым текстом. Чтений репозитория лидом — 14.

**Разметка уверенности** — авторская конвенция `docs/research/raw/README.md`:
[Ф] подтверждено первоисточником · [О] вывод из нескольких источников ·
[Г] экстраполяция · «данных нет» — публично не существует.
Дополнительно введено для этого файла: **[П] — знание модели из обучения, живым источником
в этой сессии НЕ подтверждено.** Почти вся часть 1 и часть 2 — [П].

---

## ЧАСТЬ 0. Снимок нашей математики (внутренний код-ресёрч, канон v3.9.0)

Записано ДО внешних находок, чтобы перенос делался на факты канона, а не на память.
Источник — `docs/math_model.md` (версия 3.9.0, статус: соответствует коду v6.17.0 и далее).
**Это единственная часть файла со статусом [Ф]** — прочитано напрямую из репозитория.

### 0.1. Входы (§2)

$$ X = \{\, I_t,\; E_t,\; B_t,\; B^{\text{liq}}_t,\; O,\; G,\; u \,\} $$

- $I_t$ — совокупный месячный приток (зарплата, дивиденды, аренда, фриланс);
- $E_t = \sum e_j$ — расходы без кредитных платежей;
- $B^{\text{liq}}_t$ — ликвидная позиция вне счетов целей;
- $O = \{(P_{k,t}, r_k, T_k, B^{\text{loan}}_k)\}$ — по кредиту: аннуитетный платёж,
  **годовая ставка $r_k$ (известна точно, из договора)**, остаточный срок, остаток долга;
- $G = \{(T^{\text{tgt}}_s, C_s, d_s, c_s)\}$ — цели: сумма, накоплено, срок, категория;
- $u = (L_{\min}, D_{\max}, H, R, r_{\text{bench}})$ — параметры пользователя.

🔴 **Все входы — НАБЛЮДАЕМЫЕ величины, а не оценки случайных будущих доходностей.**
Это ключевое отличие от постановки Марковица и главный факт для раздела «урок 1/N».

### 0.2. Критерии (§3, §5)

$$ CF_t = I_t - \sum_j e_{j,t}, \qquad R_t = CF_t - \sum_k P_{k,t} $$

$$ L_t = \frac{B^{\text{liq}}_t}{\sum_j e_{j,t}} \quad \text{(ЗАПАС, месяцы автономии)},
\qquad D_t = \frac{\sum_k P_{k,t}}{I_t} \quad \text{(ПДН)} $$

Пересчёт на альтернативу $a$:
$$ R_t(a) = I_t - \textstyle\sum_j e_j - (\sum P - \delta P(a)), \qquad
L_t(a) = \frac{B^{\text{liq}}_t + x_r^{\text{eff}}}{\sum_j e_j}, \qquad
D_t(a) = \frac{\sum P - \delta P(a)}{I_t} $$

**Ортогональность критериев (§5.4).** $R_t$ и $D_t$ реагируют на $x_d$, $L_t$ — на $x_r$,
$S_n$ — на $x_g$. В прежней модели $L_t = R_t/(\sum e + \sum P)$ давала корреляцию
$R$–$L \approx 0.9998$ — из четырёх критериев работали три. Stock-based $L_t$ (v3.0.0)
эту коллинеарность устранила. [Ф, канон §3.3, §18 п.1]

### 0.3. Пространство решений (§4.3)

Stars-and-bars, шаг $\Delta = 0.10$:
$$ \lvert A \rvert = \binom{N+k-1}{k-1} = \binom{12}{2} = 66, \quad N = 10,\ k = 3 $$

Прежний шаг 20% давал 21 альтернативу и грубые советы. [Ф, канон §4.3]

### 0.4. Допустимость (§6) — только жёсткие инварианты безопасности

$$ R_t(a) \geq 0; \qquad D_t(a) \leq \max(D_{\max}, D_t),\ D_{\max} = 0.40;
\qquad L_t(a) \geq L_{\min}\ (L_{\min} = 0 \text{ по умолчанию}); \qquad x_d, x_r, x_g \geq 0 $$

Семантика ПДН-гейта: «план не увеличивает ПДН», эффективный порог $\max(D_{\max}, D_t)$.
Прежний гейт «текущий ПДН ≤ 0.40» отказывал 198 портретам из 12 000 — отказ в обслуживании
самой уязвимой группе. [Ф, канон §6, дефект G3]

### 0.5. Нормализация (§7) и свёртка (§8)

$$ \hat{x}(a) = \frac{x(a) - \min_{a'} x(a')}{\max_{a'} x(a') - \min_{a'} x(a')} $$

🔴 Min-max берётся **в рамках текущего множества $A$** — нормализация относительная,
шкала зависит от разброса реализованных значений критериев у этого пользователя.

Насыщение ликвидности (v3.1.0, дефект G1):
$$ L^{sat}_t(a) = \min\bigl(L_t(a),\; L^{*}(u)\bigr) $$
Без насыщения критерий был монотонен — модель копила подушку бесконечно: при $L_t \geq 6$ мес
отправляла в резерв 66.7% ресурса (в 64% портретов — все 100%), при консенсусе четырёх
экспертов 0.5–3.3% в резерв. Это был корень **76% всех расхождений** с консенсусом
(51.9% → 87.4% после починки). [Ф, канон §7, §18 п.7]

Свёртка SAW:
$$ U(a) = w_R \hat{R}_n(a) + w_L \hat{L}_n(a) + w_D (1 - \hat{D}_n(a)) + w_S \hat{S}_n(a),
\quad \textstyle\sum_i w_i = 1,\ U(a) \in [0,1] $$

Выбор — **лексикографический**, floor выше SAW:
$$ a^{*} = \arg\max_{a \in A'} \bigl(\min(L_t(a), F(\mathcal{O}, r_{bench}, CV_{\text{income}})),\ U(a)\bigr) $$

$$ F = \begin{cases}
1.0, & \exists o: A_o > 0 \wedge i_o \geq \max(0.30,\ r_{bench} + 0.15) \quad \text{(токсичный долг)} \\
2.0 + \min(1.0, \max(0, CV_{\text{income}} - 0.3)), & \text{иначе, доход волатилен} \\
2.0, & \text{иначе}
\end{cases} $$

$CV_{\text{income}} = \sigma/\mu$ по реальной помесячной истории, **не менее 6 содержательных
месяцев**, кап +1.0 мес. [Ф, канон §8, ADR-015]

**Красная линия ADR-015 (важна для переноса):** $R_t$, $D_t$ и кризисный детектор считаются
по фактическому потоку ТЕКУЩЕГО месяца безусловно; история дохода влияет **только на
floor-уровень**, никогда на допустимость или детектор кризиса. [Ф, канон §8]

**Измеренная чувствительность канала $CV_{\text{income}}$** (стенд 12 000 портретов, ADR-015):
затронуто **19.05%**, сменился победитель — **0.97%**, 0 портретов без волатильности сменили
победителя (локализация подтверждена). [Ф, канон, шапка v3.7.0]

### 0.6. Веса профилей (§9) — экзогенные преференции, не оценки

| Профиль | $w_R$ | $w_L$ | $w_D$ | $w_S$ | $L^{*}$, мес |
|---|---:|---:|---:|---:|---:|
| Консервативный | 0.20 | 0.45 | 0.25 | 0.10 | 6.0 |
| Умеренно-консервативный | 0.20 | 0.35 | 0.25 | 0.20 | 5.0 |
| Сбалансированный ★ | 0.25 | 0.30 | 0.25 | 0.20 | 4.5 |
| Умеренно-агрессивный | 0.30 | 0.20 | 0.20 | 0.30 | 3.5 |
| Агрессивный | 0.35 | 0.10 | 0.15 | 0.40 | 3.0 |

Монотонность весов как признак корректности: $w_L$ убывает 0.45→0.10, $w_S$ растёт 0.10→0.40,
$w_R$ растёт 0.20→0.35, $w_D$ убывает 0.25→0.15. $L^{*}$ убывает 6→3 мес (коридор 3–6:
target-константы четырёх экспертных движков + норматив Greninger 1996). Floor-резерв 2 месяца
от профиля НЕ зависит. [Ф, канон §9]

### 0.7. Avalanche и бенчмарк-ставка (§10)

$$ r_{\text{bench}} = r_{\text{key}} \cdot (1 - \text{НДФЛ}), \quad \text{НДФЛ} = 0.13
\qquad O^{\text{target}} = \{k \in O : r_k \geq r_{\text{bench}}\} $$

🔴 $r_{\text{key}}$ тянется из SOAP-сервиса ЦБ РФ — это **наблюдаемая величина**, не прогноз.
Фолбэк 0.14 при недоступности cbr.ru, кэш неудачного запроса 15 минут. [Ф, канон §10.2]

Каскад освоения ресурса долг → цели → резерв (G7-остаток, ADR-009); резерв — конечный сток.
Сохранение: $x_d^{\text{eff}} + \sum_s x_{g,s} + x_r^{\text{eff}} = R^{+}_t$. [Ф, канон §10.4]

§10.5 (помесячный график, ADR-016) — **диагностический объект**, явно не влияет на §6
допустимость, §9 SAW, §12 кризис; считается после ранжирования, гарантия по конструкции кода
+ тест `test_crisis_plan_unaffected_by_debt_schedule_adr_016`. [Ф, канон §10.5]

### 0.8. Цели (§11) — здесь ЕСТЬ оценочный параметр

$$ S_n(a) = \frac{\sum_s (C_s + \Delta C_s(a)) w_s^{\text{cat}} u_s}{\sum_s T^{\text{fut}}_s w_s^{\text{cat}} u_s},
\qquad u_s = \max\left(1, \frac{12}{\max(\tau_s, 1)}\right) $$

Категориальные веса $w^{\text{cat}}$: income_growth 3.0 / safety 2.0 / material 1.0 /
emotional 0.5 (Becker 1964, теория человеческого капитала).

🔴 Инфляционная индексация (ADR-013, v3.6.0):
$$ T^{\text{fut}}_s = \begin{cases} T^{\text{tgt}}_s, & \tau_s \leq 36\ \text{мес.} \\
T^{\text{tgt}}_s \cdot (1.04)^{\tau_s/12}, & \tau_s > 36\ \text{мес.} \end{cases} $$
Ставка 0.04 — цель Банка России по инфляции, **статичная константа**.
**Это оценочный параметр, и он ВХОДИТ в ранжирование через $S_n$.**
Измеренная чувствительность (стенд 12 000 портретов v2): затронуто **53.45%**, сменился
победитель — **0.23%**, 0 портретов без длинной цели сменили победителя. [Ф, канон §11.3, шапка]

### 0.9. Прогноз (§15) — НЕ входит в ранжирование

$$ \hat{y}_{t+1} = \alpha y_t + (1-\alpha)\hat{y}_t,\ \alpha = 0.3;
\qquad y^{(i)}_{t+h} = \hat{y}_{t+h} + \varepsilon^{(i)},\ \varepsilon^{(i)} \sim \mathcal{N}(0,\sigma^2),\ N = 1000 $$
$$ \sigma(h) = \sigma_0\sqrt{1 + 0.5h}, \qquad \text{CI}_{80\%} = [Q_{10\%}, Q_{90\%}] $$

80% вместо 95% — продуктовое решение: на горизонте 1–3 мес 95% даёт нечитаемый коридор.
[Ф, канон §15, §18 п.4]

🔴 **Ключевое для переноса:** в pipeline (§16) прогноз — этап 3, ранжирование — этап 6b.
Прогноз является выходом для отображения, а не входом критериев. [О — вывод из §16 + красной
линии ADR-015; отдельной формулировки «прогноз не входит в свёртку» в каноне нет, она следует
из того, что $R_t$/$D_t$ считаются по факту текущего месяца безусловно]

### 0.10. Где мы ДЕЙСТВИТЕЛЬНО решаем портфельную задачу (§13)

$$ x_r = \underbrace{\min(x_r, \max(0, L^{*}\textstyle\sum e - B^{\text{liq}}))}_{\text{добор подушки}}
+ \underbrace{x^{inv}}_{\text{инвестиционный транш}} $$

Полка по профилю — доля акций 0% / 20% / 40% / 60% / 80% от профиля 1 к 5, остаток поровну
депозит + ОФЗ. Горизонт: <12 мес → только депозит; 12–36 мес → депозит и ОФЗ поровну;
>36 мес → профильный микс. [Ф, канон §13]

🔴 **Это и есть ровно тот объект, к которому портфельная теория применима напрямую** —
лестница аллокации под риск-профиль, структурно тождественная тому, что делают робо-эдвайзеры.
Всё остальное в нашей модели — не портфельная задача.

Вычет ИИС типа А (ADR-017) считается ПОСЛЕ ранжирования, не входит в $utility$ — иначе граница
400 000 ₽ при шаге решётки 10% дала бы неоптимальный совет на границе лимита (ADR-008).
[Ф, канон §13]

### 0.11. Сложность (§16)

$$ T_{\text{total}} = O(Nh + \lvert A \rvert \cdot p) $$
При $N=1000$, $h=3$, $\lvert A \rvert=66$, $p \leq 10$ — единицы миллисекунд. [Ф, канон §16]

---

## ЧАСТЬ 1. Академическая литература портфельной оптимизации

> Отчёт субагента 1, ДОСЛОВНО. Статус — [П]: живых источников не получено, всё из знания модели.

## Research Report: Mean-Variance Portfolio Optimization — Theory, Estimation-Error Pathology, and Fixes

**Methodological note up front:** WebSearch was unavailable for this entire task (session-level budget exhausted before my first query fired — 0 of my ~12 calls got a live search). I then tried ~9 WebFetch/curl attempts at primary sources (Ledoit's site, DeMiguel's RFS PDF via LBS, SSRN abstract pages, Michaud's own firm site, López de Prado's quantresearch.org, Semantic Scholar API) and every one failed — 403/404, self-signed cert errors, or rate limits (429), including on retry. None of the content below was pulled from a live fetch this session. What follows is drawn from prior training knowledge of this literature, which for these specific canonical papers is generally reliable on citations/mechanisms but I flag every place where an exact number should be independently checked before being published or cited in FINPILOT docs.

---

### 1. Markowitz (1952) — original formulation

Markowitz, H. (1952). "Portfolio Selection." *Journal of Finance*, 7(1), 77–91. DOI: 10.2307/2975974.

- **Objective:** minimize portfolio variance for a given target expected return (equivalently, maximize expected return for a given variance):
  minimize σ_p² = Σᵢ Σⱼ wᵢwⱼσᵢⱼ = w'Σw
  subject to: w'μ = target return, w'1 = 1 (and w ≥ 0 in the no-short-sales case).
- **Efficient frontier:** the set of portfolios that minimize variance at each achievable expected-return level (or maximize return at each variance level); every rational risk-averse investor's optimal portfolio lies on this frontier.
- **Solution form:** with only the equality constraints (no short-sale restriction), the Lagrangian first-order conditions give a closed-form linear-algebra solution — e.g. the two-fund decomposition: minimum-variance portfolio w_mv = Σ⁻¹1 / (1'Σ⁻¹1); tangency portfolio w_tan = Σ⁻¹(μ − r_f1) / (1'Σ⁻¹(μ − r_f1)). With inequality constraints (no shorting, box constraints) it is a genuine quadratic program, solved numerically — Markowitz's own critical-line algorithm (1956) traces the whole frontier.
- **Key structural fact for everything downstream:** the closed-form weight vector is proportional to Σ⁻¹μ — i.e., it requires *inverting* the covariance matrix and multiplying it by the (noisy) mean vector. This single fact is the root of the estimation-error pathology in §2.

---

### 2. THE CENTRAL POINT — estimation error / "error maximization"

**Michaud, R. (1989).** "The Markowitz Optimization Enigma: Is 'Optimized' Optimal?" *Financial Analysts Journal*, 45(1), 31–42. DOI: 10.2469/faj.v45.n1.31.

Core argument (recalled, not a verified verbatim quote this session — flag before quoting directly): MV optimizers treat sample-estimated μ and Σ as if they were the true, certain parameters. Because the optimizer's whole job is to find the combination that most aggressively exploits *differences* between assets, it doesn't average out noise in the inputs — it hunts for and concentrates on whichever assets have the most favorable-looking (overestimated return, underestimated risk, favorably-estimated correlation) numbers. Michaud's famous characterization: MV optimizers function as **"estimation-error maximizers"** rather than diversifiers — they systematically overweight the securities whose inputs are *most* subject to estimation error, and the resulting "optimized" portfolios are typically unintuitive, concentrated in a handful of names, and unstable (small input changes → large weight changes), with poor out-of-sample performance despite in-sample optimality.

**Best, M.J. & Grauer, R.R. (1991).** "On the Sensitivity of Mean-Variance-Efficient Portfolios to Changes in Asset Means: Some Analytical and Computational Results." *Review of Financial Studies*, 4(2), 315–342. DOI: 10.1093/rfs.4.2.315. Showed analytically and computationally that small perturbations to the expected return of even a single asset can force large, discontinuous swings in the optimal weight vector — including driving many other assets' weights to zero — a direct consequence of the ill-conditioning discussed below.

**Chopra, V.K. & Ziemba, W.T. (1993).** "The Effect of Errors in Means, Variances, and Covariances on Optimal Portfolio Choice." *Journal of Portfolio Management*, 19(2), 6–11. DOI: 10.3905/jpm.1993.409440. Their widely-cited result: cash-equivalent losses from estimation error in the three input types are **wildly unequal in magnitude** — errors in *means* matter roughly an order of magnitude more than errors in variances or covariances. The number most frequently attributed to them in the literature is a ratio on the order of **~20 : ~2 : ~1** for (errors in means) : (errors in covariances) : (errors in variances), evaluated at a moderate risk-tolerance level (I recall risk tolerance ≈ 50 in their scale) — **and they explicitly caveat that this ratio is risk-tolerance-dependent**: at higher risk tolerance the relative dominance of mean errors grows further; at lower risk tolerance (more risk-averse investors) the gap narrows and variance/covariance errors matter relatively more. ⚠️ Flag: the exact ratio numbers and which of variance/covariance is "2" vs "1" should be verified against the original JPM article before being used as a hard citation — I have high confidence in the *order-of-magnitude* finding (means ≫ covariances > variances) and lower confidence in the precise digits.

**Mechanically, why the optimizer amplifies rather than averages error:** the closed-form MV solution is proportional to Σ⁻¹μ. Two things compound:
1. Averaging (e.g., estimating a single mean from many observations) reduces noise by √n. Optimization is not averaging — it's a *maximization* over noisy inputs, and by extreme-value statistics, the assets whose estimated Sharpe ratios look best are disproportionately likely to be assets where noise happened to inflate the estimate, not assets that are genuinely best. The optimizer can't distinguish signal from lucky noise, so it bets hardest on the noise.
2. Matrix inversion of Σ is numerically unstable when assets are highly correlated (Σ near-singular / ill-conditioned, small eigenvalues). Inverting amplifies whatever error exists in Σ's estimation, and that amplified error then multiplies against the equally noisy μ. The two error sources compound rather than cancel.

---

### 3. THE FIXES

**Black-Litterman.** Black, F. & Litterman, R. — internal Goldman Sachs Fixed Income Research memo (1990), "Asset Allocation: Combining Investor Views with Market Equilibrium"; Litterman & Black (1991) Goldman FI Research "Global Asset Allocation with Equities, Bonds, and Currencies"; Black, F. & Litterman, R. (1992). "Global Portfolio Optimization." *Financial Analysts Journal*, 48(5), 28–43. DOI: 10.2469/faj.v48.n5.28.
Mechanism: instead of estimating μ from noisy historical sample means, *reverse-optimize* an equilibrium prior Π from observed market-cap weights: Π = δΣw_mkt (δ = market risk-aversion coefficient) — this anchors expected returns in something economically disciplined (CAPM equilibrium) rather than sample noise. Then Bayesian-blend this prior with the investor's own subjective views, expressed via matrices P (which assets each view concerns), Q (view magnitudes), Ω (confidence/uncertainty in each view), and scalar τ (uncertainty of the prior itself):
E[R] = [(τΣ)⁻¹ + P′Ω⁻¹P]⁻¹ [(τΣ)⁻¹Π + P′Ω⁻¹Q]
Why it stabilizes weights: the optimizer starts from an already well-diversified, market-consistent portfolio and is only pulled away from it in the specific directions and to the degree the investor expresses conviction — so it can't run away to the extreme, concentrated corner solutions that raw sample-mean MV optimization produces.

**Covariance shrinkage — Ledoit & Wolf.**
- Ledoit, O. & Wolf, M. (2003). "Improved Estimation of the Covariance Matrix of Stock Returns With an Application to Portfolio Selection." *Journal of Empirical Finance*, 10(5), 603–621. DOI: 10.1016/S0927-5398(03)00007-0 (shrinkage target: single-index/market-model covariance).
- Ledoit, O. & Wolf, M. (2004). "Honey, I Shrunk the Sample Covariance Matrix." *Journal of Portfolio Management*, 30(4), 110–119. DOI: 10.3905/jpm.2004.110 (shrinkage target: constant-correlation matrix).
- Ledoit, O. & Wolf, M. (2004). "A Well-Conditioned Estimator for Large-Dimensional Covariance Matrices." *Journal of Multivariate Analysis*, 88(2), 365–411. DOI: 10.1016/S0047-259X(03)00096-4 (shrinkage target: scaled identity).
Formula: Σ_shrink = δ·F + (1−δ)·S, a convex combination of the sample covariance S and a structured, low-variance/high-bias target F. δ* (the optimal shrinkage intensity) is derived analytically to minimize expected quadratic (Frobenius) loss against the unknown true Σ — not chosen by cross-validation — using consistent estimators of the asymptotic variance/covariance of the sample-covariance entries and the target's misspecification. Result is a well-conditioned, always-invertible estimator even when the number of assets N approaches or exceeds the number of observations T. Later work: Ledoit & Wolf's *nonlinear shrinkage* (Annals of Statistics, 2012, and follow-ups ~2017–2020) applies a different shrinkage intensity to each eigenvalue individually rather than one global linear δ, improving further in high dimensions — I recall this line of work exists but did not verify the exact citation this session.

**Resampled efficiency.** Michaud, R. (1998). *Efficient Asset Management*, Harvard Business School Press (2nd ed. with R. Michaud, Oxford University Press, 2008). Method: bootstrap-resample the return history B times, compute a full MV-efficient frontier for each resampled dataset, then average weights across all B frontiers (matched by return rank) — smooths away the idiosyncratic noise that drives any single optimization to an extreme corner solution.
**Published criticism:** Scherer, B. (2002). "Portfolio Resampling: Review and Critique." *Financial Analysts Journal*, 58(6), 98–109. DOI: 10.2469/faj.v58.n6.2489. Argues the method has no rigorous decision-theoretic/Bayesian foundation (it's ad hoc statistical smoothing, not derived from expected-utility maximization), that resampled portfolios are not MV-efficient with respect to *any* coherent set of inputs, and that it still inherits the same noisy μ, Σ estimates it started from. (Michaud also patented the method — US Patent 6,003,018 — which itself drew criticism for constraining independent academic testing/adoption.)

**Robust optimization.** Goldfarb, D. & Iyengar, G. (2003). "Robust Portfolio Selection Problems." *Mathematics of Operations Research*, 28(1), 1–38. DOI: 10.1287/moor.28.1.1.14260. Defines uncertainty sets (typically ellipsoidal) around estimated parameters and solves a min-max problem — choose weights to maximize the *worst-case* objective over all parameter values in the uncertainty set — formulated as a tractable second-order cone program (SOCP). Related: Tütüncü, R.H. & Koenig, M. (2004), "Robust Asset Allocation," *Annals of Operations Research*, 132, 157–187; Fabozzi, Kolm, Pachamanova & Focardi (2007), *Robust Portfolio Optimization and Management*, Wiley (survey/synthesis).

**Risk parity.** Maillard, S., Roncalli, T. & Teiletche, J. (2010). "The Properties of Equally Weighted Risk Contribution Portfolios." *Journal of Portfolio Management*, 36(4), 60–70. DOI: 10.3905/jpm.2010.36.4.060. Equal-risk-contribution condition: wᵢ(Σw)ᵢ = wⱼ(Σw)ⱼ ∀i,j. Requires **no expected-return estimates at all** — only Σ — directly sidestepping the dominant estimation-error source identified by Chopra & Ziemba.

**Hierarchical Risk Parity.** López de Prado, M. (2016). "Building Diversified Portfolios that Outperform Out of Sample." *Journal of Portfolio Management*, 42(4), 59–69. DOI: 10.3905/jpm.2016.42.4.059 (SSRN 2708678). Three steps: (1) tree clustering — hierarchical clustering on a correlation-distance metric to build a dendrogram; (2) quasi-diagonalization — reorder the covariance matrix by dendrogram leaf order so correlated assets sit adjacently, no inversion involved; (3) recursive bisection — top-down, split the tree into two branches at each level, allocate capital between branches inversely proportional to aggregated cluster variance, recurse to individual assets. Why it improves out-of-sample stability: it never inverts the covariance matrix (inversion is the operation that catastrophically amplifies estimation error when Σ is ill-conditioned/near-singular under high correlation), it uses no return estimates, and errors are contained within local branches of the hierarchy rather than propagating globally across all assets simultaneously as in a joint one-shot optimization.
**Criticism/contested status:** I recall there being published replication work questioning whether HRP's out-of-sample edge over simpler baselines (minimum-variance, plain risk parity) holds universally, with results sensitive to the choice of distance/linkage metric — but I could not verify a specific citation this session (tool failures), so **flag this as an open item needing direct lookup**, not an asserted fact.

---

### 4. 🔴 HIGHEST PRIORITY — DeMiguel, Garlappi & Uppal (2009) and the rebuttal literature

DeMiguel, V., Garlappi, L. & Uppal, R. (2009). "Optimal Versus Naive Diversification: How Inefficient Is the 1/N Portfolio Strategy?" *Review of Financial Studies*, 22(5), 1915–1953. DOI: 10.1093/rfs/hhm075.

Recalled specifics (⚠️ **could not verify live this session — every fetch attempt on the RFS PDF, LBS mirror, and SSRN abstract page failed**; treat the exact digits below as needing a direct check before quoting in any FINPILOT document):
- They test **14** competing optimal-allocation models (sample-based MV, several Bayesian/shrinkage variants, moment-restriction and portfolio-constrained models, combination rules) against the naive **1/N** benchmark, across **7** empirical datasets of varying asset-universe composition and size.
- Headline finding: **none of the 14 sophisticated models consistently and significantly outperforms 1/N** out-of-sample on Sharpe ratio or certainty-equivalent (CEQ) return across the datasets; 1/N also has essentially zero turnover versus much higher turnover for the optimized strategies, worsening their after-cost performance further.
- Estimation-window result (the number I recall with moderate-high confidence, as it's one of the most frequently repeated factoids from this paper): the length of historical data needed for the sample-based mean-variance strategy to reliably beat 1/N is on the order of **~3,000 months (≈250 years) for a 25-asset portfolio**, and roughly **~6,000 months for a 50-asset portfolio** — i.e., far beyond any feasible real-world sample, which is the crux of their argument. **This should be double-checked against the actual paper before use** — I am not 100% certain these are the exact published figures versus a close paraphrase I've internalized from secondary discussion of the paper.
- Stated cause: the number of parameters to estimate grows with N (μ: N parameters; Σ: N(N+1)/2 parameters), and per the Best-Grauer/Chopra-Ziemba mechanism, estimation error in these gets amplified by the matrix-inversion step of MV optimization into weight instability that swamps the theoretical diversification/optimization gain achievable at realistic sample sizes (a few hundred months in practice).

**Rebuttal literature:**
- Kritzman, M., Page, S. & Turkington, D. (2010). "In Defense of Optimization: The Fallacy of 1/N." *Financial Analysts Journal*, 66(2), 31–39. DOI: 10.2469/faj.v66.n2.6. Argues DeMiguel et al.'s result is largely an artifact of testing on asset universes with fairly similar risk/return characteristics (where 1/N is a naturally strong prior) combined with short, noisy estimation windows; with more heterogeneous assets and via large-sample Monte Carlo bootstrap resampling of history, optimization reliably beats 1/N, and the breakeven sample size is much shorter than DeMiguel et al.'s headline numbers suggest.
- Tu, J. & Zhou, G. (2011). "Markowitz Meets Talmud: A Combination of Sophisticated and Naive Diversification Strategies." *Journal of Financial Economics*, 99(1), 204–215. DOI: 10.1016/j.jfineco.2010.08.013. Proposes combining 1/N and an optimized MV portfolio via an estimated convex-combination weight (itself a shrinkage-style estimator, balancing 1/N's bias against MV's estimation-error variance); shows the combination can beat both pure strategies out-of-sample.

**Balance of evidence (stated fairly, not papered over):** DeMiguel et al. (2009) is highly influential and widely replicated as a caution against *naive plug-in* sample-based MV optimization on short/realistic samples. It is not the final word — Kritzman et al. dispute the generality of the conclusion under different test designs, and the field's subsequent direction (Tu-Zhou combination rules, Ledoit-Wolf-shrunk MV, Black-Litterman, HRP, risk parity — all in §3) is essentially built on accepting DeMiguel et al.'s diagnosis (estimation error dominates naive optimization) while disputing that 1/N is therefore the right *fix* — the consensus that has emerged is that **regularized/shrunk/robust MV variants generally do recover the theoretical edge over 1/N**, so the live debate has shifted from "optimize or not" to "how much and what kind of regularization is enough."

---

### Contested / uncertain (explicit list)

1. Chopra & Ziemba (1993) exact ratio digits (20:2:1 vs. some other precise ordering/magnitude) and the exact risk-tolerance value at which it's evaluated.
2. DeMiguel, Garlappi & Uppal (2009): exact count/composition of the 7 datasets, and the precise ~3,000/~6,000-month estimation-window figures — very likely correct in order of magnitude but not independently verified this session.
3. HRP (López de Prado 2016) replication/criticism literature — I believe contested replications exist but could not locate/verify a specific citation.
4. Michaud's (1989) exact phrasing/quotable text — could not fetch the actual FAJ article or any legal mirror.
5. Ledoit-Wolf nonlinear shrinkage exact citation (I believe Annals of Statistics ~2012 plus later refinements, but did not verify the volume/year/DOI).

### Could not obtain at all

- Any live-fetched primary-source text this session (every WebSearch call failed on exhausted session budget before executing; every WebFetch attempt — Ledoit's site, DeMiguel's RFS PDF/LBS mirror, SSRN abstract pages for both DeMiguel and López de Prado, Michaud's firm site, quantresearch.org — returned 403/404/cert-error; Semantic Scholar API was rate-limited (429) on two attempts including after a wait). No DOIs or figures below were cross-checked against a live source this session — all are recalled from training knowledge with the confidence levels flagged above.

---

## ЧАСТЬ 2. Практика и раскрытие методики робо-эдвайзеров

> Отчёт субагента 2, ДОСЛОВНО. Статус — [П]/[Г]: живых подтверждённых источников нет,
> «успешные» фетчи прошли через суммаризатор `WebFetch`, сырого текста субагент не видел.

# Research Report: US Robo-Advisor Production Practices — Methodology, Risk Profiling, TLH, Rebalancing

## ⚠️ CRITICAL RELIABILITY CAVEAT — READ FIRST

This session's `WebSearch` tool was reported as **already exhausted (400/400 calls used) before my first query ran** — every search I attempted returned "session has used its web search budget," with zero actual results. I fell back to: (a) `curl` against DuckDuckGo Lite (blocked by an anti-bot "anomaly" challenge, no results extracted), (b) `WebFetch` on Google/Bing search URLs (both returned geo-locked junk — Spanish-language results, audio-equipment ads — not the query I asked for), and (c) `WebFetch` directly against **guessed** provider URLs.

The direct-URL `WebFetch` calls that "succeeded" did so via the tool's built-in summarization model, not raw text I could inspect myself. **I could not get a single PDF to a raw-text state via `pdftotext`** — the one PDF I located (Vanguard's rebalancing paper) redirected twice and then 500'd; I never obtained the file on disk to run `pdftotext` against, contrary to the prescribed workaround. This means every "quote" below passed through an opaque intermediary that could paraphrase, invent, or mis-date content, and I have **no independent corroboration**. Treat every figure/quote below as **provisional, unverified secondary reporting**, not confirmed primary-source text, until someone re-fetches and reads the raw HTML/PDF directly.

Given this, I am reporting what I got, flagged accordingly, rather than fabricating false confidence.

---

## 1. METHODOLOGY DISCLOSURE

**Betterment** — fetched `https://www.betterment.com/resources/betterment-portfolio-strategy` (WebFetch summary only, unverified). Reported claims: uses Modern Portfolio Theory + reverse optimization off CAPM (formula quoted as "μ = λ Σ ωmarket"), described as becoming "benchmark-aware" in 2024 against a custom MSCI ACWI IMI + Bloomberg U.S. Universal Bond benchmark; **101 risk levels** for the Core strategy rather than a small tier set. Page allegedly dated "Updated June 15, 2026" — this date is suspicious (unusually precise, possibly fabricated by the summarizer) and I could not verify it against raw HTML. Historically (per general industry knowledge, not this session's fetch) Betterment's whitepaper has been described elsewhere as Black-Litterman-style reverse optimization — the fetched summary is consistent with that but did not use the term "Black-Litterman" explicitly, only "reverse optimization" off CAPM equilibrium.

**Wealthfront** — fetched `https://research.wealthfront.com/whitepapers/investment-methodology/` (unverified summary). Reported: mean-variance optimization ("maximize: μ′·w subject to: w′·Σ·w = σ²"), blending CAPM-derived expected returns with a "Wealthfront Factor Model," and explicitly invoking **Black-Litterman** for capital market assumptions ("applies a technique that derives expected return parameters from market equilibrium allocations and manager 'views'"). Dated "March 9, 2026" per the summary — again unverified. This is directionally consistent with what's publicly known about Wealthfront's methodology (MVO + CAPM/Black-Litterman-informed CMAs), so plausible, but the exact sentence-level quotes are not confirmed against raw text.

**Vanguard Digital Advisor** — the direct methodology-page URL I guessed (`investor.vanguard.com/investor-resources-education/methodology/...`) 404'd. Fell back to `investor.vanguard.com/advice/digital-advisor`, which returned goals-based language ("gathers information about your investing goals... automatically build and rebalance a strategic portfolio") and a notable specific claim: **"over 300 personalized glide paths"** based on age, risk attitude/loss aversion, and marital status. No VCMM-specific quote was retrieved, and the page pointed to a separate "Digital Advisor Brochure" (ADV-style) and Form CRS rather than a standalone methodology whitepaper — I did not manage to fetch either of those documents.

**Schwab Intelligent Portfolios** — both attempts failed: the disclosures URL redirected to `schwab.com/intelligent-portfolios`, which then returned an "authorization failure" error page (likely bot-blocked), and I could not locate the ADV Part 2A brochure via Bing (results were geo-mismatched/irrelevant). **No Schwab methodology content obtained at all** — this is a clean gap, not a fabricated fallback.

---

## 2. RISK PROFILING

**Betterment**: not retrieved this session (the methodology page fetch focused on optimization, not the questionnaire). Gap.

**Wealthfront** (unverified summary): explicitly claims a deliberately short questionnaire — *"we combed behavioral economics research to simplify our risk identification process to only a few questions"* — combining subjective self-report and objective/behavioral measures, with the overall score weighted toward "whichever component is more risk averse." Output is a **continuous Risk Score from 0.5 to 10.0 in 0.5 increments**, mapping to **20 discrete asset allocations**. Recommended review annually, formal update cadence ~3 years or on major life events. This numeric range (0.5–10.0) matches what the task brief already expected, giving it somewhat higher plausibility despite the unverified sourcing.

**Vanguard Digital Advisor**: described only vaguely as a "risk attitude quiz" gathering unspecified inputs; no question count or scoring mechanic was surfaced by the fetch.

**Schwab**: not obtained (page blocked).

**Regulatory/academic criticism of questionnaires**: I did **not** manage to pull FINRA suitability guidance or the SEC's 2021 robo-adviser exam sweep / risk-alert findings — no search capability was available to locate these, and I did not have specific URLs to guess. This is a clear, acknowledged gap — flagged rather than invented.

---

## 3. TAX-LOSS HARVESTING

**Betterment** (`betterment.com/tax-loss-harvesting`, unverified summary): does **not** appear to publish a headline annual "tax alpha" percentage on this page. The retrieved claim was **"nearly 70% of customers using tax-loss harvesting covered their taxable advisory fees through estimated tax savings"** — a fee-offset statistic, not a return/alpha figure. Also references the standard $3,000/year ordinary-income offset + unlimited capital-gains offset under IRS rules. No 0.8%–2% "tax alpha" figure was found on this specific page (it may exist in a different Betterment document I didn't locate).

**Wealthfront** (`wealthfront.com/tax-loss-harvesting`, unverified summary): also did **not** yield a headline percentage on this page — only anecdotal per-user dollar examples ($42.61, $9.53) with a disclaimer that "benefits will vary." The summary flagged a separate blog post, "Tax-Loss Harvesting results 2023," as a likely source of aggregate figures, which I did not fetch.

**Independent/academic evidence (Chaudhuri, Burnham & Lo 2020; AQR/Sosner et al.; wash-sale mechanics; tax-deferral-not-elimination critique)**: **entirely unobtained**. WebSearch was dead for the whole session and I had no reliable way to locate an SSRN/journal URL by guessing. This is a hard gap — none of the requested independent literature was retrieved.

---

## 4. REBALANCING

**Vanguard's Jaconetti/Kinniry/Zilbering "Best practices for portfolio rebalancing" paper**: I located what should be the PDF (`institutional.vanguard.com/.../best_practices_rebalancing.pdf`), but it redirected to `workplace.vanguard.com/...` and then returned **HTTP 500**. I never got the file onto disk, so `pdftotext` was never run — the prescribed PDF workaround simply didn't get that far. **No content obtained.**

**Betterment / Schwab published rebalancing thresholds/bands**: **not obtained** this session — neither the specific drift-threshold percentage Betterment has published elsewhere, nor Schwab's rebalancing bands, were retrieved via any successful fetch.

**Formal no-trade-region theory (Leland; Donohue & Yip)**: not attempted given the search tool was dead and no direct URLs were available to guess.

---

## WHAT COULD NOT BE OBTAINED (explicit list)

- Schwab Intelligent Portfolios: methodology, ADV Part 2A brochure, risk questionnaire, rebalancing bands — **all failed** (blocked page + failed searches).
- Vanguard Digital Advisor: actual methodology/VCMM whitepaper text, question count, portfolio-tier count — only a marketing page was reached.
- Betterment risk questionnaire mechanics (question count, scoring).
- Any SEC ADV Part 2A / Form CRS filing for any provider (adviserinfo.sec.gov was never successfully queried or fetched).
- Chaudhuri, Burnham & Lo (2020) and all other named academic TLH literature — zero retrieval.
- Vanguard's rebalancing research paper full text (PDF chain 500'd).
- FINRA suitability guidance / SEC 2021 robo-adviser risk alert on questionnaires.
- Betterment's and Wealthfront's headline "tax alpha" percentage figures (their TLH pages didn't surface one; likely exists in a different document/blog post not located).
- Any raw-text (`pdftotext`) verification of anything — every claim above that "succeeded" passed through WebFetch's internal summarizer only.

**Bottom line for the lead agent**: this run had no functioning search capability (WebSearch pre-exhausted at session start) and no successful PDF-to-raw-text extraction. The four fragments retrieved (Betterment MPT/reverse-optimization description, Wealthfront's MVO/Black-Litterman/risk-score description, Vanguard's "300 glide paths" line, Betterment's 70%-fee-offset TLH stat) are plausible and partly consistent with general industry knowledge, but are unverified secondary paraphrase and should be re-confirmed by a session with working search/fetch before being treated as citable fact — especially the specific dates and exact quoted formulas, which are the most likely to be summarizer artifacts rather than source text.

---

## ЧАСТЬ 3. Перенос на нашу задачу — анализ лида

Синтез делает лид, не субагент (правило шага 4). Ниже — рассуждение на фактах части 0
([Ф], прочитано из репозитория) с опорой на механизмы части 1 ([П], не подтверждено).
Там, где вывод зависит от неподтверждённой цифры, это сказано явно.

### 3.0. Расхождение между субагентами

Прямых противоречий между отчётами нет — они покрывали непересекающиеся области.
Есть одно **расхождение субагента 1 с моим собственным знанием**, и его надо зафиксировать:
субагент привёл соотношение Chopra–Ziemba как means : **covariances** : variances = 20 : 2 : 1.
Наиболее распространённая в литературе форма — means : **variances** : covariances = 20 : 2 : 1,
то есть ошибки в дисперсиях весомее ошибок в ковариациях, а не наоборот. Порядок величины
(средние ≫ вторые моменты) не оспаривается ни в одной версии. **Кто прав — не проверено;
до проверки не цитировать соотношение вообще, только качественный вывод.**

### 3.1. 🔴 Урок 1/N для нас: уязвимы ли мы к error maximization

Честный ответ: **в основном нет, и не по счастливой случайности, а по устройству входов —
но с двумя конкретными исключениями, которые уже измерены.**

Разложим механизм DeMiguel/Michaud на предпосылки. Error maximization требует **всех трёх**:

| # | Предпосылка | Есть ли у нас |
|---|---|---|
| A | входы — **оценки** случайных будущих величин | **почти нет** |
| B | целевая функция **максимизируется** по этим оценкам (селекционное смещение) | **да** |
| C | отображение вход → решение **усиливает** ошибку (инверсия $\Sigma$, непрерывные веса) | **нет** |

**(A) Входы.** Это главный ответ, и интуиция в постановке задачи верна. У Марковица
**каждый** вход — оценка: $\mu$ (N параметров) и $\Sigma$ (N(N+1)/2 параметров) оцениваются
по короткой выборке. У нас $R_t$, $L_t$, $D_t$ считаются из наблюдённых доходов, расходов и
балансов текущего месяца; ставки по кредитам $r_k$ известны **точно из договора**, а не
оцениваются; $r_{\text{bench}}$ тянется из ЦБ РФ — тоже наблюдаемая. Оценивать нечего,
значит и максимизировать шум не на чем. Прогноз SES+Монте-Карло, единственный настоящий
статистический объект модели, **в ранжирование не входит** — он выход для отображения
(часть 0 §0.9). Это не косметика: именно потому, что прогноз отделён от выбора, ошибка
прогноза не может развернуть рекомендацию.

Два исключения, где оценка всё же входит в решение:

1. **$CV_{\text{income}}$ → floor-уровень.** Оценка $\sigma/\mu$ по ≥6 месяцам истории.
   Опаснее прочего тем, что floor стоит **лексикографически выше SAW** — сдвиг оценки может
   переключить дискретный ярус и тем самым подменить весь выбор, а не подвинуть его немного.
   Это структурно тот же «разрыв», что Best & Grauer описали для весов Марковица.
   **Но он измерен:** 19.05% портретов затронуто, победитель сменился в **0.97%**
   (часть 0 §0.5). Меньше процента — это не error maximization, это локальная
   чувствительность на границе яруса.
2. **Инфляция 4% → $S_n$** для целей дальше 36 мес. Единственная константа-предположение
   внутри ранжирования, и она **компаундится**: $(1.04)^{20} \approx 2.19$.
   Измерено: затронуто 53.45%, победитель сменился в **0.23%**.

Суммарно оба канала переворачивают решение примерно в 1% случаев и оба локализованы
(0 портретов без соответствующего признака сменили победителя). Сравните с Марковицем, где
возмущение среднего одного актива способно обнулить веса половины портфеля.

**(B) Максимизация есть — но она не над шумом.** Да, $\arg\max$ по 66 альтернативам формально
даёт селекционное смещение. Но смещение возникает только там, где есть чему смещаться:
extreme-value-эффект отбирает те объекты, которым «повезло с шумом». Когда критерии
детерминированы, «повезло» не бывает — argmax просто выбирает лучший исход, а не лучший шум.

**(C) Усиления ошибки нет.** Нет $\Sigma$, нет инверсии, нет плохо обусловленной матрицы.
Отображение долей в критерии — гладкое, монотонное, в размерности 2 (три доли, сумма 1).
Более того, три наших конструктивных решения работают ровно как регуляризация, изобретённая
в литературе для лечения Марковица:

- **Шаг решётки 10%.** 66 точек — крошечное пространство гипотез. В терминах статистического
  обучения это низкая ёмкость модели, то есть структурная защита от переподгонки. Отказ от
  непрерывной оптимизации здесь — не упрощение, а свойство.
- **Лексикографический floor.** Жёсткий приоритет, доминирующий над свёрткой — по функции это
  то же, что якорь равновесия в Black-Litterman: оптимизатор не может уйти в угол, потому что
  сначала обязан удовлетворить внешнее ограничение.
- **Насыщение $L^{sat}$ и жёсткие инварианты.** Прямая аналогия — Jagannathan & Ma,
  «Risk Reduction in Large Portfolios: Why Imposing the Wrong Constraints Helps»,
  *Journal of Finance* 58(4), 2003 [П, не проверено в этой сессии]: ограничения на веса
  математически эквивалентны шринкейджу ковариационной матрицы. То есть ограничение,
  введённое из соображений безопасности, попутно работает как статистическая регуляризация.
  История §7 это подтверждает эмпирически: до насыщения монотонный критерий гнал модель в
  угол «всё в резерв» (100% ресурса в 64% портретов) — ровно то же угловое поведение, за
  которое ругают чистого Марковица, и вылечено оно тем же классом средства.

🔴 **Где мы ДЕЙСТВИТЕЛЬНО уязвимы — не там, где ищут.** Риск переподгонки у нас лежит не в
per-user оптимизации, а в **калибровке весов и констант** по 12 000 портретов против
экспертного консенсуса. Веса $w$, $L^{*}$, floor 2.0, порог токсичности 30%, порог 36 мес —
всё это подобранные на выборке величины. Вот это — наш настоящий аналог критики DeMiguel:
не «оптимизатор ловит шум у пользователя», а «мы поймали шум эталонной выборки при подгонке».

И тут проект уже делает почти всё правильно, что нужно назвать вслух как силу:
предрегистрация гипотезы ДО раунда (floor 2.0 в ADR-006, G8 в WATCHLOG v6.15.0), одно правило
за раунд, split-half валидация (+1.22/+1.24 п.п. — эффект воспроизводится до сотых), сетка
альтернатив floor 0.5/1.0/1.5 с осознанным выбором предрегистрированного значения при
превышении внутри шума, и — самое сильное — **отказ менять канон в раунде 5, когда гипотеза
не подтвердилась**. Это дисциплина, которой в 2009 году не хватало половине работ,
критикуемых DeMiguel.

**Конкретное действие, которое стоит дешево и закрывает вопрос эмпирически:** ввести в
сертификационный стенд постоянные **наивные бейзлайны** в духе 1/N и мерить SAW против них
каждый раунд:
- $x_d = x_r = x_g = 1/3$ (прямой аналог 1/N);
- «всё в лавину», «всё в резерв до floor, остаток в цели»;
- «floor, потом всё в самый дорогой долг» (правило-эвристика без свёртки).

Если SAW не бьёт наивное правило по action-vector-согласию с экспертами — это красный флаг,
и он должен гореть в CI, а не выясняться на защите. Если бьёт — у вас появляется цифра,
которой нет ни у одного робо-эдвайзера: «наша оптимизация даёт +X п.п. над наивным правилом
на 12 000 портретов». Это ровно тот тест, который DeMiguel применил к отрасли, применённый
к себе добровольно. **Отрицательный результат здесь тоже ценен** — он означал бы, что решётку
можно упростить без потери качества совета.

### 3.2. Что из портфельной математики применимо, а что нет

**Применимо напрямую — ровно одно место: §13, инвестиционный транш.**
Доли акций 0/20/40/60/80% по профилю — это буквально портфельная задача и структурно
тождественна лестнице робо-эдвайзера. И главный вывод литературы здесь **защищает текущее
решение, а не требует его усложнить**: строить MVO/Black-Litterman над тремя классами активов
(акции/ОФЗ/депозит) при отсутствии надёжных оценок доходности российского рынка — это в
точности сценарий, где DeMiguel показал проигрыш наивному правилу. Фиксированная лестница по
риск-профилю есть обоснованный выбор, а не упрощение. **Рекомендация: оптимизатор сюда не
добавлять**, а в пояснении сослаться на то, почему.

**Применимо как идея, не как аппарат:**

| Метод | Что переносится |
|---|---|
| Шринкейдж (Ledoit–Wolf) | Не ковариация, а **оценка $CV_{\text{income}}$**. Сейчас порог 0/1: <6 мес → «стабилен», ≥6 → берём как есть. Это грубейшая форма шринкейджа. Непрерывный вес $\delta(T)$ к популяционному приору сгладит переключение яруса и снизит те самые 0.97% |
| Resampled efficiency (Michaud) | Не для выбора весов, а для **объяснимости**: пересэмплировать историю дохода и показать «этот совет устойчив в 99% пересэмплов». Монте-Карло у нас уже есть — не хватает применения его к устойчивости решения, а не только к коридору баланса |
| Ограничения-как-шринкейдж (Jagannathan–Ma) | Готовая рамка для ВКР/доков: наши инварианты — не только безопасность, но и регуляризация |
| Эффективная граница | Аналог — **парето-фронт** по 4 критериям среди 66. Его можно показать: «вот 5 недоминируемых вариантов, вот чем платите за каждый». Это честная «граница» для многокритериальной задачи и хороший ход в объяснимости |

**Не применимо, и важно понимать почему:**

- **Black-Litterman.** Нужен равновесный приор из рыночных капитализаций. «Рыночного портфеля»
  распределения между долгом, резервом и целями не существует — нет равновесия, из которого
  делать reverse optimization. Метод не переносится даже метафорически.
- **Шринкейдж ковариации как таковой.** У нас нет ковариационной матрицы критериев: они
  **сознательно ортогонализованы конструкцией** (§5.4), а не оценены совместно. Лечить нечего.
- **HRP.** Нужна корреляционная структура над многими активами для кластеризации.
  При $k = 3$ направлениях иерархию строить не из чего.
- **Risk parity.** «Равный вклад в риск» бессмысленно, когда направления — не рисковые активы:
  досрочное погашение кредита под 25% даёт **детерминированную** доходность 25%, у неё нет
  дисперсии, которую можно уравнивать. Это, кстати, самая глубокая причина, по которой вся
  портфельная рамка к нам применима лишь частично: у Марковица доходность случайна, у нас
  «доходность» досрочки — арифметика договора.
- **Tax-loss harvesting.** Механика опирается на реализацию убытков по бумагам, wash-sale rule
  и зачёт против прироста капитала — конструкция налогового кодекса США. Наш аналог другой по
  природе: вычет ИИС (уже реализован, ADR-017) и налог на доход по вкладам, зашитый в
  $r_{\text{bench}} = r_{\text{key}} \cdot 0.87$. Заимствовать метод нельзя, заимствовать
  **принцип** («налоговая оптимизация — самый измеримый вклад советника») уже сделано.
- **Ребалансировка.** У нас нет портфеля, дрейфующего от целевых весов: каждый месяц решение
  принимается заново от текущего состояния. Ближайший аналог — не пороги дрейфа, а вопрос
  «как часто пересматривать риск-профиль», и вот он открыт (см. 3.4).

### 3.3. Как раскрывают методику лидеры и на что ориентироваться нам

🔴 Оговорка: фактура части 2 не подтверждена, поэтому ниже — только тот уровень обобщения,
который выдерживает её ненадёжность.

Структурно в отрасли видны две модели раскрытия: **инженерная** (Betterment, Wealthfront —
публичные whitepaper с формулами и названными методами) и **регуляторная** (Vanguard, Schwab —
опора на ADV Part 2A и Form CRS, где описывается процесс и конфликты интересов, а не
математика). Обе публикуют **что** делают; ни одна, насколько известно, не публикует
**насколько её собственные параметры влияют на результат**.

Отсюда единственный вывод, который не зависит от непроверенных цифр и который стоит взять
как ориентир: **наш `docs/math_model.md` уже раскрывает больше, чем принято в отрасли** —
каждая формула, каждая константа, её источник, обоснование «почему именно столько» и
**измеренный эффект внедрения** (19.05%/0.97%, 53.45%/0.23%, 51.9%→87.4%, 78.2%→79.4%).
Публикация чувствительности собственных параметров — редкая вещь; это защитимое отличие,
и его стоит держать как продуктовое заявление, а не прятать в docs.

Важная поправка на юрисдикцию: раскрытие в США во многом вынуждено фидуциарным статусом и
формой ADV. В РФ у консультационного инструмента без лицензии такой обязанности нет — значит
наше раскрытие является **продуктовым решением о доверии**, а не комплаенсом, и подавать его
следует именно так.

### 3.4. Что осталось неизвестным

**По внешним источникам — практически всё.** Не получено ни одного живого первоисточника:

- точные цифры DeMiguel et al. (14 моделей / 7 датасетов / ~3000 и ~6000 месяцев) — не сверены;
- соотношение Chopra–Ziemba и порядок variances/covariances в нём — **прямое расхождение**
  между отчётом субагента и знанием лида, не разрешено;
- точная формулировка Michaud про «estimation-error maximizers» — цитата не подтверждена;
- существует ли published-критика HRP и какая — субагент помечает как открытый вопрос;
- методика Schwab — не получена вовсе;
- анкеты риск-профилирования: число вопросов и схема отображения ответов в веса ни у одного
  провайдера не подтверждены; заявленные 101 уровень Betterment, 0.5–10.0 / 20 аллокаций
  Wealthfront, 300+ glide paths Vanguard — [Г], возможные артефакты суммаризатора;
- независимая критика TLH (Chaudhuri, Burnham & Lo 2020 и др.) — **ноль извлечения**, при том
  что это был прямо запрошенный пункт;
- критика анкет со стороны FINRA/SEC — не получена;
- пороги ребалансировки провайдеров и работа Vanguard по ребалансировке — не получены.

**По нашей стороне — открытые вопросы, которые исследование обнажило, но не закрыло:**

1. Нигде в каноне не написано прямым текстом, что прогноз §15 не входит в ранжирование.
   Это следует из §16 и красной линии ADR-015, но держится на выводе читателя.
   Стоило бы зафиксировать явно — это ровно та инвариантная гарантия, которую в других местах
   (ADR-016, ADR-017) канон формулирует прямо и подпирает тестом.
2. Периодичность пересмотра риск-профиля пользователя у нас не определена вовсе.
3. Наивные бейзлайны в стенде отсутствуют — при том что это самый дешёвый способ ответить на
   вопрос «а нужна ли решётка вообще».

### 3.5. Итог одной строкой

Наша задача — **не портфельная**, и это не недостаток: ставки известны точно, а не
оцениваются, поэтому механизм, который ломает Марковица, у нас почти не запускается.
Измеренная доля переворотов решения от единственных двух оценочных каналов — около 1%.
Реальный риск переподгонки лежит не в решётке, а в калибровке констант по эталонной выборке,
и против него в проекте уже стоит правильная дисциплина. Единственный участок, где портфельная
теория применима буквально (§13, инвестиционный транш), литература советует **не усложнять** —
и там уже сделано так, как она советует.
