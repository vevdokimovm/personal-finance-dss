# Тема 37. ПРИЧИННОСТЬ: как доказать, что продукт помог

Сырьё исследования. Дата: 2026-09-10. Статус: ЗАВЕРШЕНО.
Правило §9/§11 CLAUDE.md — первичный материал дословно, до выжимки.

Связки: тема 27 (`prescriptive_quality_metrics_2026-09-10.md`) — качество рекомендации;
тема 26 — Commonwealth Bank, нулевой эффект; тема 36 — брекетинг; тема 24 — ЦБ и наджинг.

---

## Участок 1. Что логировать с первого дня (ГЛАВНЫЙ)

### 1.1 Минимальный лог выдачи рекомендации

#### Источник A. Bottou, Peters, Quiñonero-Candela, Charles, Chickering, Portugaly, Ray, Simard, Snelson. «Counterfactual Reasoning and Learning Systems: The Example of Computational Advertising». JMLR 14 (2013) 3207–3260.
Добыт полностью: `curl` → PDF 1.4 МБ → `pdftotext -layout`, 2844 строки. Не сниппет.
URL: https://www.jmlr.org/papers/volume14/bottou13a/bottou13a.pdf

🔴 **Главное правило логирования — что именно нужно записывать (стр. 3224, §4.3):**

> «Equation (6) emphasizes the simplifications resulting from the algebraic similarities of the
> actual and counterfactual Markov factorizations. Because of these simplifications, the evaluation
> of the weights only requires the knowledge of the few factors that differ between P(ω) and P*(ω).
> **Each data sample needs to provide the value of ℓ(ωi) and the values of all variables needed to
> evaluate the factors that do not cancel in the ratio (6).**»

Перевод на наш случай: в логе должны быть (а) исход ℓ(ω) — метрика, которую мы потом считаем,
и (б) все переменные, входящие в те множители вероятностной модели, которые **различаются**
между реальной и контрфактической системой. Практически: контекст решения, само решение,
и вероятность этого решения при действовавшей политике.

🔴 **Почему без рандомизации это в принципе не работает (стр. 3224):**

> «Importance sampling relies on the assumption that all the factors appearing in the denominator
> of the reweighting ratio (6) are nonzero whenever the factors appearing in the numerator are
> nonzero. <...> this assumption means that the **data must be collected with an experiment
> involving active randomization**. We must therefore design cost-effective randomized experiments
> that yield enough information to estimate many interesting counterfactual expectations with
> sufficient accuracy.»

Это ровно тот вывод, к которому пришла тема 27 («OPE невозможен без логов с propensity»),
но здесь он у первоисточника и в форме требования к сбору данных, а не к анализу.

**Оценка контрфактического исхода (формула 7, стр. 3224):**
> Y* = ∫_ω ℓ(ω) w(ω) P(ω) ≈ (1/n) Σ_{i=1..n} ℓ(ωi) wi

**Проблема тяжёлых хвостов и клиппинг весов (стр. 3225):**
> «Unfortunately, when P(ω) is small, the reweighting ratio w(ω) takes large values with low
> probability. This heavy tailed distribution has annoying consequences because the variance of
> the integrand could be very high or infinite. When the variance is infinite, the central limit
> theorem does not hold. <...> **Importance sampling works best when the actual distribution and
> the counterfactual distribution overlap.**»

> «Let us choose the maximum weight value R deemed acceptable for the weights. **We have obtained
> very consistent results in practice with R equal to the fifth largest reweighting ratio observed
> on the empirical data.**» — сноска 7 там же: «This is in fact a slight abuse because the theory
> calls for choosing R before seeing the data.»

Клиппинг: w̄(ω) = w(ω), если P*(ω) < R·P(ω), иначе 0. Ω_R = { ω : P*(ω) < R·P(ω) }.

🔴 **Два разных доверительных интервала — диагностический приём, который стоит забрать целиком
(стр. 3226, §4.5):**
> «• The **inner confidence interval** (13) witnesses the uncertainty associated with the domain
> insufficiently explored by the actual distribution. A large inner confidence interval suggests
> that the most practical way to improve the estimate is to **adjust the data collection experiment**
> in order to obtain a better coverage of the counterfactual conditions of interest.
> • The **outer confidence interval** (12) represents the uncertainty that results from the limited
> sample size. A large outer confidence interval indicates that the sample is too small. To improve
> the result, we simply need to **continue collecting data using the same experimental setup**.»

Итог для нас: широкий внутренний интервал = «рандомизации мало, меняй схему сбора»;
широкий внешний = «просто мало пользователей, жди». Это диагностика, которой у нас сейчас нет вовсе.

**Как рандомизировали в Bing (стр. 3227, §4.6):**
> «Randomization was introduced using a modified version of the ad placement engine. Before
> determining the ad layout, a random number ε is drawn according to the standard normal
> distribution N(0,1), and all the mainline reserves are multiplied by m = ρ·e^(−σ²/2+σε). Such
> multipliers follow a log-normal distribution whose mean is ρ and whose width is controlled by σ.»

То есть рандомизировали **не выбор действия, а порог/параметр** — логнормальный множитель
с матожиданием ρ. Для нас это прямо переносимо: можно шевелить не «какую альтернативу показать»,
а числовой параметр модели (например, вес критерия в SAW), сохраняя осмысленность выдачи.

🔴 **Цена рандомизации — измерена (стр. 3229):**
> «Finally, in order to measure the cost of the randomization, we also ran the unmodified ad
> placement system on a control bucket. <...> **The randomization caused a small but statistically
> significant increase of the number of mainline ads per page. The click yield and average revenue
> differences are not significant.** <...> This experiment shows that we can obtain accurate
> counterfactual estimates with affordable randomization strategies.»

**Валидация метода (стр. 3229):** «a second traffic bucket of equal size was configured with
mainline reserves reduced by about 18%. <...> The effective measurements and the counterfactual
estimates match with high accuracy.»

**Главный аргумент «зачем вообще логировать шире, чем нужно сегодня» (стр. 3229, §4.7):**
> «The main benefit of the counterfactual estimation approach is the ability to **use the same data
> to answer a broad range of counterfactual questions**.»
Перечислены: другие уровни дисперсии рандомизации (то есть «сколько рандомизации мы можем себе
позволить в будущем» оценивается по уже собранным данным), точечные оценки без рандомизации
(Y0(ρ) ≈ 2·Yν(ρ) − Y2ν(ρ)), контекст-зависимые пороги.

**Ограничение размерности (стр. 3229):**
> «Considerably broader ranges of counterfactual questions can be answered when data is collected
> using randomization schemes that explore more dimensions. <...> However, **the more dimensions we
> randomize, the more data needs to be collected to effectively explore all these dimensions.**»

**Про выбор стратегии exploration (стр. 3241, §6.4):**
> «Meanwhile, despite their suboptimal asymptotic properties, **heuristic exploration strategies
> perform surprisingly well** during the time span in which the problem can be considered
> stationary. Even in the simple case of multi-armed bandits, excellent empirical results have been
> obtained using Thompson sampling (Chapelle and Li, 2011) or fixed strategies. **Leveraging the
> problem structure seems more important in practice than perfecting an otherwise sound exploration
> strategy.**» — и далее: «it is both expedient and practical to maximize Ŷθ at each round <...>
> subject to additional ad-hoc constraints **ensuring a minimum level of exploration**.»

Вывод для FINPILOT: не надо строить умный бандит. Надо обеспечить **минимальный уровень
исследования** и записывать вероятности. Этого достаточно.

---

### 1.2 Рандомизация в проде / exploration

#### Источник B. Alex Egg (Adyen). «Off-policy Evaluation for Payments at Adyen». arXiv:2501.10470, 15.01.2025.
Добыт полностью: `curl` → PDF 601 КБ → `pdftotext -layout`, 474 строки.
URL: https://arxiv.org/abs/2501.10470 · PDF: https://arxiv.org/pdf/2501.10470

Ценность: это **финансовая компания** (платёжный процессинг), не реклама, и там ровно наша
проблема — детерминированная продовая модель.

**Мотив отказа от чистого A/B (стр. 1):**
> «One analysis of A/B testing practices at Adyen revealed that **58% of tests were flat or
> inconclusive, resulting in over 20 weeks per year of wasted experimentation time.**»

🔴 **Дословная формулировка нашей проблемы (стр. 4, §4.1.2):**
> «There is an important and subtle implication in the reweighting scheme: it implies that the
> logging policy is stochastic or in other words you have a probability distribution across actions.
> This is important to highlight in light of the fact that **most industrial applications will be
> deterministic by default**, for example following some binomial objective click objective
> P(C|ctx, action). In this case we don't have a distribution over actions but rather a probability
> of conversion for example. This is also the case at Adyen where the existing models are based on
> a binomial objective in a **epsilon-greedy policy**.»

**Как выкрутились (стр. 4–5):**
> «To overcome this issue, the lack of action probability in the logs, we can exploit the fact that
> we are in an epsilon-greedy framework and that **for the exploration traffic we have implied
> action probabilities**. Using this intuition we can recover a stochastic logging policy which puts
> us in the reweighting framework. However, this comes w/ the tradeoff that the target and logging
> policies will be very divergent. Divergent policies will experience large weights which will
> potentially contribute to variance that we will have to mitigate. **Ideally our logging policy
> would be stochastic which would result in smaller weights and less variance and better OPE
> estimate — this is something our team are prioritizing for the future.**»

🔴 Читать так: «восстановить propensity задним числом из ε-greedy» — костыль, который работает,
но даёт огромную дисперсию. Правильно — писать propensity сразу. Adyen это признаёт прямым
текстом и ставит в план.

**Формулы четырёх оценщиков (стр. 3), дословно:**

DM: V̂_DM(π_t) = (1/n) Σ_i r̂(x_i, π_t(x_i))
> «While DM is straightforward to implement and often exhibits low variance, it is highly
> susceptible to bias if the reward model is misspecified.» (у Adyen эта регрессия на GBM
> «gets around 80% accuracy in ab tests»)

IPS: V̂_IPS(π_t) = (1/n) Σ_i [π_t(a_i|x_i) / π_o(a_i|x_i)] · r_i
> «IPS provides unbiased estimates when the logging policy has **sufficient support** (i.e., non-zero
> probability for all actions that the target policy might take). However, it can suffer from high
> variance, especially when the policies are divergent or importance weights are large or when data
> is limited.»

SNIPS: V̂_SNIPS(π_t) = [Σ_i (π_t/π_o)·r_i] / [Σ_i (π_t/π_o)]
> «SNIPS is consistent but can be biased. However, it often performs well empirically, **particularly
> in low-data regimes**, and does not require hyperparameter tuning.»
🔴 Для нас на 100–1000 пользователей это ключевая строка: SNIPS — оценщик для малых данных.

DR: V̂_DR(π_t) = (1/n) Σ_i (π_t/π_o)·(r_i − r̂(x_i,a_i)) + (1/n) Σ_i r̂(x_i, π_t(x_i))
> «DR is more robust than either DM or IPS alone. <...> and is unbiased if either r̂(x,y) = r(x,y)
> or p̂_i = π_0(y_i|x_i).» — свойство «двойной робастности»: достаточно, чтобы была верна
> **одна** из двух моделей.

🔴 **Эмпирический результат, который противоречит теоретическому ожиданию (стр. 5–6, §Результаты):**
> «IPS and SNIPS consistently maintain a **correlation above 0.8** across all weeks <...> DM and DR
> exhibited weaker performance <...> DR estimator, which combines DM and IPS, also shows **weak
> correlation, hovering around zero**.»
> «The overall outcome of these experiments is that it is indeed possible to, with over 80%
> correlation, run AB tests offline. We estimate that this is recovering an incremental **9–54
> million transactions** over a six-month period.»

То есть в реальном финансовом проде «умный» DR проиграл простому IPS/SNIPS. Учесть при выборе
оценщика: не начинать с DR только потому, что он теоретически лучший.

---

#### Источник C. Connor Douglas (NYU Stern), Joel Persson (Spotify), Foster Provost (NYU Stern). «Logging Policy Design for Off-Policy Evaluation». arXiv:2605.15108v2, май 2026.
Добыт полностью: `curl` → PDF 1.0 МБ → `pdftotext -layout`, 2384 строки.
URL: https://arxiv.org/abs/2605.15108 · PDF: https://arxiv.org/pdf/2605.15108

🔴 Это **прямо наш вопрос**: не «как оценивать», а «как проектировать логирующую политику,
чтобы потом можно было оценить». Свежая работа с соавтором из Spotify (прод).

**Постановка (Abstract):**
> «We characterize a fundamental **reward–coverage tradeoff**: concentrating probability mass on
> high-reward actions reduces variance but risks missing signal on actions the target policy may
> take. <...> We also distill practical design principles for selecting logging policies when
> operational constraints prevent implementing the theoretical optimum.»

**Почему это не академическая тонкость (стр. 3–4):**
> «In the sample limit, these estimators enjoy strong statistical guarantees <...> **In finite sample
> sizes, however, the choice of logging policy has a dramatic effect on the bias and variance of OPE
> estimates. Since all practical settings have finite samples**, this motivates studying how the
> logging policy's action probabilities should be chosen to minimize bias and variance.»

**Насколько дорого ошибиться (стр. 6, §2, иллюстрация):**
> «Uniform logging can produce highly inaccurate off-policy estimates <...> Collecting more
> informative data substantially reduces [error]: [personalized logging with] 1,000 observations
> [achieves] accuracy of 100,000 observations under uniform logging.»
🔴 Читать так: **грамотно спроектированная логирующая политика на 1 000 наблюдений даёт ту же
точность, что тупая равномерная на 100 000.** Для продукта, у которого будет 100–1000
пользователей, это разница между «измерим» и «не измерим».

**Когда равномерная рандомизация всё же оптимальна (стр. 4, §4):**
> «We show that when **neither the target policy nor the reward distribution is known, uniform
> randomization is minimax optimal.** This reflects the classical intuition that an uninformative
> prior is optimal when one assumes nothing about the estimand and wants to control worst-case error.»

🔴 **Аргумент, снимающий этическое возражение частично (стр. 4, §4, идеальный случай):**
> «We show the optimal logging policy takes the form of a **Neyman allocation** directed toward the
> target policy, weighting action probabilities by the product of target policy mass and the square
> root of the reward probability. This solution minimizes IPW variance subject to overlap, and
> yields two notable byproducts: the resulting OPE estimate based on IPW has lower MSE than the
> empirical on-policy estimate one would obtain by running the target policy directly, and **the
> logging policy accrues higher expected reward than the target policy during the logging period.**
> This confirms that OPE with an optimized logging policy can jointly attain **higher policy value
> and estimation precision** than on-policy evaluation (e.g., an A/B test).»

То есть «рандомизация = обязательно жертвуем пользователем ради науки» — не универсальная правда.
В идеальном информационном режиме логирующая политика и полезнее, и точнее A/B-теста.
Оговорка: это верно при известной модели вознаграждения, чего у нас на старте нет.

**Три реализуемых класса soft-greedy политик (стр. 26, §6.1) — дословно:**

- top-k: «Π_TK(µ̂) := { π_k : k ∈ 1,…,|A| }, is the set of policies π_k that assign **equal weight
  to the k ≤ |A| actions with the highest values of µ̂(A,X)** for each context X = x. Thus, π_{k=1}
  is the fully greedy policy and π_{k=|A|} is the fully uniform policy.»
- softmax: «π_α(a|x) = e^{α·µ̂(a,x)} / Σ_{a′∈A} e^{α·µ̂(a′,x)}, ∀α ∈ [0,∞). Here, α = 0 corresponds
  to the uniform policy while α = ∞ equates to a greedy policy. **Because this class of logging
  policies places probability mass on all actions for α ∈ [0,∞), softmax policies ensure the IPW
  estimator is unbiased for any target policy even if this mass is very small.**»
- power-normalized: «π_d(a|x) = µ̂^d(a,x) / Σ_{a′∈A} µ̂^d(a′,x), ∀d ∈ [0,∞)» — «enjoys the same
  property of ensuring weak overlap with any target policy, **as long as reward estimates are
  bounded away from 0**.»

**Результат симуляции (стр. 27, §6.2), |A| = 100 000, целевая политика top-200:**
> «In both the small-sample and large-sample settings, **well-tuned top-k policies substantially
> outperform softmax policies, with optimal values of k around 200.** This result demonstrates that
> narrowing the logging support toward high-reward actions—**intentionally incurring some bias**—can
> reduce overall MSE relative to policies that enforce overlap. As the sample size increases, the
> policies that enforce overlap perform relatively better. This is driven by the fact that **bias
> does not shrink in sample size, but variance does.**»
> «Yet, **for any finite sample size, as d and α approach ∞ (i.e. approaching greedy), MSE approaches
> infinity.**»

Числа из подписи к Figure 6 (стр. 28), дословно: «Panel (a) shows that the MSE-minimizing top-k
logging policy occurs at **k\* = 181**, yielding MSE = 3.93 × 10⁻⁵; the MSE-minimizing softmax
parameter is **α\* = 71.46**, yielding MSE = 1.94 × 10⁻³; and the [MSE]-minimizing power-normalized
degree is **d\* = .91**, yielding MSE = 5.04 × 10⁻⁵. Panel (b) shows analogous results for the large
sample-size setting, with MSE-minimizing top-k being **k\* = 249**».

🔴 **Правило выбора параметра — прямое ТЗ (стр. 28–29, §6.2):**
> «**When the target policy class is known, k can be initialized at the target policy's approximate
> support size**, as the MSE-minimizing k closely tracks this quantity across both sample-size
> regimes. For power-normalized policies, d can be tuned analogously via held-out MSE evaluation.
> For softmax policies, α lacks a direct analytical interpretation and should be selected via
> held-out MSE evaluation; however, given the consistently weaker performance of softmax relative
> to top-k and power-normalized across our simulations, **the latter two classes are generally
> preferable when the action space is large.**»
> «**When the target policy is unknown, a moderately soft-greedy policy is preferable to a fully
> greedy one, since bias from support truncation does not diminish in sample size.** In all of these
> settings, a natural approach is to treat the parameter as a hyperparameter and select it by
> computing IPW estimates of a reference policy's value on historically collected data <...> This
> requires only prior logged data and reward predictions — both available before the logging period
> begins.»

**Перенос на FINPILOT.** У нас |A| = 66 альтернатив (шаг 10%). Целевая политика — SAW-топ.
Аналог top-k при |A| = 66 и целевом «топ-1 показываем, топ-3 в списке»: логирующая политика
top-k с k порядка размера показываемой выдачи (3–5), а не k = 66. То есть **не равномерный
разброс по всем 66 альтернативам, а равновероятный выбор внутри верхушки** — и бизнесово
безопаснее, и по MSE лучше. Это самая практичная находка участка 1.

**Ограничение честно:** цитируется работа Wan et al. (2022) про «safe logging policies», где
безопасность определена как «value of the logging policy being **no less than some fixed
proportion of the value of a baseline policy**» (стр. 29, §7). Это тот формализм, который нам
нужен для регуляторного разговора: не «мы иногда показываем плохое», а «гарантируем, что
ценность логирующей политики не ниже доли λ от базовой».

---

### 1.3 Propensity score logging

Сведение трёх источников выше в одно требование.

**Что такое propensity в нашем случае.** π_o(a_i | x_i) — вероятность, с которой ДЕЙСТВОВАВШАЯ
в проде система выбрала показанное действие a_i в контексте x_i. Не «уверенность модели»,
не «оценка альтернативы по SAW», не «score». Именно вероятность выбора.

🔴 **Почему её нельзя восстановить задним числом.** Три независимых свидетельства:
1. Bottou (стр. 3224): вес требует знания множителей, различающихся между фактической и
   контрфактической моделью — эти множители существуют, только если фактическая система
   стохастическая.
2. Adyen (стр. 4): «the lack of action probability in the logs» лечится реконструкцией из
   ε-greedy, но ценой «very divergent» политик и огромной дисперсии; команда ставит переход
   на честное стохастическое логирование в план.
3. Из сниппета поиска (не открывал целиком, помечаю как непроверенный первоисточник):
   работы про «policy-based estimators where the logging propensities are **learned** from logged
   data face bias that depends directly on the true and unobserved logging propensities, which is
   **non-identifiable**». Смысл совпадает с двумя проверенными источниками: восстановленный
   propensity даёт смещение, которое невозможно оценить изнутри данных.

**Что писать (минимум, без чего IPS/SNIPS не считаются):** `propensity` — число в (0, 1],
вероятность именно показанного действия; `policy_id`/`policy_version` — какая версия политики
это породила; `action_id` — что показали; `context_hash` + сам контекст; `reward` — исход.
Полный список полей — раздел И1.

**Что ломает propensity, если про это забыть (важно, из сниппета поиска — формулировка
подтверждена смыслом источников A и B, но сама фраза из сниппета, первоисточник не открывал):**
«The correct propensity is the probability of the chosen action under the **exact decision process
that ran in production, after all rules and gating**, including hard rules (eligibility, compliance,
budgets, caps), fallbacks, tie-break rules, and any random exploration.»

🔴 Для FINPILOT это критично буквально: у нас **жёсткие инварианты Rt ≥ 0 и ПДН ≤ 0,40** режут
множество альтернатив ПОСЛЕ скоринга. Значит propensity надо считать **после** применения
инвариантов, а не до. Иначе сумма вероятностей не равна единице и все веса поедут.

### 1.4 Этика и право (ЦБ, 22-МР, 152-ФЗ)

#### Источник D. Kohavi R., Longbotham R. «Online Controlled Experiments and A/B Tests» // Encyclopedia of Machine Learning and Data Science, Springer, ред. 11.03.2023.
Добыт полностью: PDF 18 страниц → `pdftotext -layout`.
URL: https://exp-platform.com/Documents/2023-03-11EncyclopeiaMLDSABTestingFinal.pdf

**Раздел «Experimentation Ethics», стр. 10–11, дословно:**
> «Any change could potentially be an unethical change. If so, **it would also be unethical to
> experiment with that change.** The Belmont Report (1979) establishes principles for biomedical and
> behavioral studies, and the Common Rule (1991) establishes actionable review criteria based on
> these principles. One of the key points is **"risk of substantial harm"** and the concept of
> **equipoise (Freedman 1987): whether the relevant expert community is in equipoise — genuine
> uncertainty — with respect to different treatments.**»
> «Any change that harms visitors or stakeholders in any way (**physical, financial, emotional,
> psychological, social, or privacy**) may be seen as unethical. In addition, if the content is
> dishonest, untruthful, misrepresenting or does not comply with the organization's explicit or
> implied agreement with users should be considered unethical.»

🔴 **Две лакмусовые бумажки (стр. 10), дословно — забрать в регламент как есть:**
> «1. **Could you ship the change to all users without a controlled experiment, given the
> organizational standards?** If you could make the change to an algorithm, or to the look-and-feel
> of a product without an experiment, surely you should be able to run an experiment and
> scientifically evaluate the change first. **Shipping code is, in fact, an experiment.** It may not
> be a controlled experiment, but rather an inefficient sequential test where one looks at the time
> series; if key metrics are negative, the feature is rolled back.
> 2. **If the experiment were published nationwide in a newspaper or a blog, would it be a public
> relations problem?**»
Отрицательные примеры, названные в тексте: «the Facebook contagion experiment (Kramer et al. 2014)
and the OKCupid experiment (Selterman 2014)».

🔴 Ключ к нашему случаю — понятие **equipoise**. Показывать части пользователей заведомо ХУДШУЮ
рекомендацию — неэтично и, скорее всего, наказуемо. Показывать одну из нескольких альтернатив,
про которые **у экспертного сообщества нет уверенности, какая лучше**, — этично и есть
классическое основание рандомизации. Наш случай: у нас 66 альтернатив распределения свободного
потока, и разница между топ-1 и топ-3 по SAW лежит внутри погрешности модели. Это и есть
equipoise, и это единственная законная зона рандомизации.

---

#### Источник E. Polonioli A., Ghioni R., Greco C., Juneja P., Tagliabue J., Watson D., Floridi L. «The Ethics of Online Controlled Experiments (A/B Testing)». Minds and Machines (2023).
Добыт полностью: PDF 24 страницы через d-nb.info → `pdftotext -layout`, 1455 строк.
URL: https://link.springer.com/article/10.1007/s11023-023-09644-y · PDF: https://d-nb.info/1313086983/34

**Четыре принципа (по Beauchamp & Childress), стр. 5, дословно:**
> «(1) **Autonomy** — Respect the right for an individual to make their own choice.
> (2) **Fairness** — Treat individuals with fairness and equality.
> (3) **Non-maleficence** — Do not harm individuals.
> (4) **Beneficence** — Be beneficial to people and the environment.»

**Fairness, стр. 12 — прямо про наш продукт:**
> «there is a general recommendation here that experimenters should be **wary of A/B tests that
> would be deemed unfair and unethical by users should they become public**.»

**Non-maleficence и уязвимые группы, стр. 13, дословно:**
> «In the context of experimental research with human subjects, it is customary to accept that
> **additional safeguards must be included in experiments involving vulnerable subjects** <...> or
> **economically or educationally disadvantaged persons**. <...> It is critical that companies
> involved in A/B testing put in place **screening practices to help exclude from experiments
> members of a vulnerable group**, in the same way in which vulnerable subjects are screened and
> excluded from clinical RCTs (see for instance the United States Code of Federal Regulations
> Title 45, Part 46, subparts B, C and D). Protections for vulnerable populations should be put in
> place **in addition to, not in lieu of**, overall protections for all users, as vulnerability may
> be context-specific.»

🔴 **Прямой перенос на FINPILOT.** «Economically disadvantaged persons» — это буквально наша
основная аудитория в её худшем состоянии: пользователь с ПДН у границы 0,40, с просроченными
долгами, с нулевым резервом. Правило для нас: **пользователи в зоне финансового стресса
исключаются из exploration-трафика и всегда получают детерминированный топ-1.** Критерий
исключения должен быть машинным и записываться в лог (`eligible_for_exploration = false`
и причина), иначе propensity потом не восстановить.

---

#### Источник F. Методические рекомендации Банка России от 27.12.2024 № 22-МР «По предоставлению потребителям финансовых продуктов (дополнительных услуг) в дистанционных каналах».
Добыт: `WebFetch`/garant дали 403 и оглавление без текста; **сработал `r.jina.ai` на
normativ.kontur.ru — 115 957 байт полного текста.** cbr.ru по угаданному прямому URL PDF — 404.
URL: https://normativ.kontur.ru/document?documentId=485702&moduleId=1

**п. 1.1 (цель), дословно:**
> «Настоящие Методические рекомендации разработаны в целях обеспечения единства подходов
> к предоставлению финансовых продуктов (дополнительных услуг) в дистанционных каналах,
> обеспечения **прозрачного и осознанного выбора** потребителями финансовых продуктов
> (дополнительных услуг) в дистанционных каналах, улучшения качества обслуживания потребителей...»

**п. 2.6, дословно (ключевая для нас формулировка):**
> «Содержание интерфейса дистанционного канала и предлагаемых для ознакомления документов
> рекомендуется формировать таким образом, чтобы они **не приводили к множественному или неверному
> толкованию, заблуждению в отношении финансового продукта (дополнительной услуги) и связанных
> с ним потребительских рисков**.
> Учитывая изложенное, рекомендуется исключить такие приемы, как:
> **согласие с отрицанием** — проставляя отметку (галочку, передвижной переключатель), потребитель
> выражает согласие с отказом от приобретения дополнительной услуги;
> **предустановленное несогласие** — снимая отметку, потребитель соглашается на приобретение
> дополнительной услуги;
> **двойное отрицание** — проставляя отметку, потребитель выражает несогласие с отказом
> от приобретения дополнительной услуги.»

**п. 3.6, дословно:**
> «Обеспечить **равную возможность прохождения клиентского пути** и связанную с ним реализацию
> прав потребителей, предусмотренных Федеральным законом от 21.12.2013 N 353-ФЗ "О потребительском
> кредите (займе)", при предоставлении потребительского кредита (займа) в дистанционных каналах...»

**п. 2.16, дословно:**
> «Процесс регистрации в дистанционных каналах также **не рекомендуется сопровождать
> использованием малозаметных элементов интерфейса, а также допускать двусмысленности или введения
> потребителя в заблуждение**.»

🔴 **Граница, честно.** 22-МР адресован финансовым организациям (кредитные, МФО, профучастники,
страховщики) и регулирует **продажу** продукта, а не выдачу рекомендации СППР. FINPILOT
формально в перечень адресатов не входит. Но:
- п. 3.6 «равная возможность прохождения клиентского пути» — это прямой аргумент против
  A/B-теста, который **меняет доступный набор действий** у части пользователей. Против
  рандомизации внутри одинаково доступного набора — не работает.
- п. 2.6 «не приводили к неверному толкованию» — запрещает показывать рекомендацию, которую
  система сама считает хуже, **не сообщив об этом**. То есть тайный exploration в интерфейсе,
  подаваемом как «лучшая рекомендация», ложится под этот пункт по смыслу, даже если формально
  адресат другой.
- Практический выход, совместимый с обоими пунктами: **exploration не как подмена топ-1,
  а как перестановка внутри честно показанного списка альтернатив** («вот 3 варианта,
  сопоставимых по оценке; предвыбран этот»). Тогда пользователь не введён в заблуждение,
  набор действий одинаков, а propensity существует и логируема.

**152-ФЗ, статья 16, дословно** (`r.jina.ai` на consultant.ru, 4 309 байт):
> «1. **Запрещается принятие на основании исключительно автоматизированной обработки персональных
> данных решений, порождающих юридические последствия в отношении субъекта персональных данных или
> иным образом затрагивающих его права и законные интересы**, за исключением случаев,
> предусмотренных частью 2 настоящей статьи.
> 2. Решение <...> может быть принято на основании исключительно автоматизированной обработки его
> персональных данных **только при наличии согласия в письменной форме** субъекта персональных
> данных или в случаях, предусмотренных федеральными законами...
> 3. Оператор обязан **разъяснить субъекту порядок принятия решения** на основании исключительно
> автоматизированной обработки его персональных данных и возможные юридические последствия такого
> решения, **предоставить возможность заявить возражение** против такого решения...
> 4. Оператор обязан рассмотреть возражение <...> **в течение тридцати дней** со дня его получения
> и уведомить субъекта персональных данных о результатах рассмотрения такого возражения.»
URL: https://www.consultant.ru/document/cons_doc_LAW_61801/22e884a41450dcb5cb62d956583ad32abe2bbbe9/

🔴 Для FINPILOT ст. 16 скорее НЕ применяется в лоб: наша выдача — рекомендация, решение принимает
пользователь, юридических последствий сама выдача не порождает. Но это ровно та граница, которую
нельзя переходить: как только продукт начнёт **сам исполнять** распределение (автоплатёж,
автоперевод в резерв), рандомизация внутри такого автоисполнения попадает под ч. 1 ст. 16 и
требует письменного согласия. Записать это как ограничение архитектуры, а не как юридическую
сноску.

**Вывод по участку 1.4 — граница дословно.**
Можно: рандомизировать порядок/предвыбор внутри набора альтернатив, которые модель считает
сопоставимыми (equipoise), при полном раскрытии всех альтернатив и их оценок пользователю.
Нельзя: показывать альтернативу, которую модель считает хуже, выдавая её за лучшую; исключать
пользователя из части клиентского пути; рандомизировать на пользователях в финансовом стрессе;
рандомизировать автоисполняемые решения без письменного согласия.

---

## Участок 2. Квазиэксперимент без рандомизации

### 2.1 Difference-in-differences

#### Источник G. Roth J., Sant'Anna P. H. C., Bilinski A., Poe J. «What's Trending in Difference-in-Differences? A Synthesis of the Recent Econometrics Literature». arXiv:2201.01194 (опубликована в Journal of Econometrics, 2023).
Добыт полностью: `curl` → PDF 58 страниц → `pdftotext -layout`, 2431 строка.
URL: https://arxiv.org/abs/2201.01194 · PDF: https://arxiv.org/pdf/2201.01194

**Допущение 1 — параллельные тренды (стр. 6), дословно:**
> «**Assumption 1 (Parallel Trends).**
> E[Y_{i,2}(0) − Y_{i,1}(0) | D_i = 1] = E[Y_{i,2}(0) − Y_{i,1}(0) | D_i = 0].   (1)»
> «The key assumption for identifying τ₂ is the parallel trends assumption, which intuitively states
> that the average outcome for the treated and untreated populations **would have evolved in parallel
> if treatment had not occurred**.»

**Что именно оно разрешает и что запрещает (стр. 6), дословно:**
> «If Y_{i,t}(0) = α_i + φ_t + ε_{i,t}, where ε_{i,t} is mean-independent of D_i, then Assumption 1
> holds. Note that this model **allows treatment to be assigned non-randomly based on
> characteristics that affect the LEVEL of the outcome (α_i)**, but requires the treatment assignment
> to be mean-independent of variables that affect the **TREND** in the outcome (ε_{i,t}). In other
> words, **parallel trends allows for the presence of selection bias, but the bias from selecting
> into treatment must be the same in period t = 1 as it is in period t = 2.**»

🔴 Для FINPILOT это самое важное предложение всего участка 2. Люди, которые ставят приложение
по учёту финансов, отличаются от тех, кто не ставит, по УРОВНЮ финансовой дисциплины — это DiD
прощает. Но они, скорее всего, отличаются и по ТРЕНДУ (человек ставит приложение именно тогда,
когда взялся за себя) — а этого DiD не прощает, и вывод рассыпается. **Это ровно наш случай,
и он тяжёлый.** Самоотбор в момент установки коррелирован с изменением поведения по построению
(эффект «Ashenfelter's dip» наоборот).

**Допущение 2 — отсутствие антиципации (стр. 7), дословно:**
> «**Assumption 2 (No anticipatory effects).** Y_{i,1}(0) = Y_{i,1}(1) for all i with D_i = 1.»
> «...which states that the treatment has **no causal effect prior to its implementation**.»

**Идентификация ATT (формула 2, стр. 7):**
> τ₂ = E[Y_{i,2} − Y_{i,1} | D_i = 1] − E[Y_{i,2} − Y_{i,1} | D_i = 0]
> «i.e. the "difference-in-differences" of population means!»

🔴 **Четыре проблемы проверки предтрендов (стр. 29–31, §4.4) — дословно, каждая:**

1. **Параллельность до не гарантирует параллельность после.**
> «even if pre-trends are exactly parallel, this need not guarantee that the post-treatment parallel
> trends assumption is satisfied. Kahn-Lang and Lang (2020) give an intuitive example: **the average
> height of boys and girls evolves in parallel until about age 13 and then diverges, but we should
> not conclude from this that there is a causal effect of bar mitzvahs (which occur for boys at age
> 13) on children's height!**»

2. **Низкая мощность теста.**
> «even if there are pre-existing differences in trends, the tests described above **may fail to
> reject owing to low power**. <...> a linear violation of parallel trends that would be detected
> only half the time by a pre-trends test **will also lead us to spuriously find a significant
> treatment effect half the time — that is, 10 times more often than we expect to find a spurious
> effect using a nominal 95% confidence interval!**»
> «in simulations calibrated to papers published in three leading economics journals, Roth (2022)
> found that **linear violations of parallel trends that conventional tests would detect only 50% of
> the time often produce biases as large as (or larger than) the estimated treatment effect**.»
> Интуиция Bilinski & Hatfield: «pre-trends tests **reverse the traditional roles of type I and type
> II error**: they set the assumption of parallel trends as the null hypothesis and only "reject" the
> assumption if there is strong evidence against it.»

3. **Pre-test bias.**
> «conditioning the analysis on "passing" a pre-trends test induces a selection bias known as
> **pre-test bias** (Roth, 2022). <...> this additional selection bias can **exacerbate** the bias
> from a violation of parallel trends.»

4. **Что делать, если предтренд ЕСТЬ, — метод не говорит.**
> «it seems likely that with enough precision, **we will nearly always reject that the parallel
> trends assumption holds exactly** in the pre-treatment period. Nevertheless, we may still wish to
> learn something about the treatment effect <...> However, **the conventional approach does not make
> clear how to proceed in this case.**»

**Рекомендации авторов (стр. 34–36, §4.6) — дословно, это готовый чеклист:**
> «Among the different estimation procedures we discussed, we view **doubly-robust procedures as a
> natural default**, since they are valid if either the outcome model or propensity score is
> well-specified <...> A potential exception <...> arises in settings with **limited overlap**, i.e.,
> when the estimated propensity score is close to 0 or 1, in which case regression adjustment
> estimators may be preferred.»
> «we encourage researchers to continue to plot **"event-study plots"** that allow for a visual
> evaluation of pre-existing trends <...> displaying **simultaneous (rather than pointwise)
> confidence bands** for the path of the event-study coefficients.»
> «**The lack of a significant pre-trend does not necessarily imply the validity of the parallel
> trends assumption.** At minimum, we recommend that researchers **assess the power of pre-trends
> tests against economically relevant violations**.»
> «We also think it should become standard practice for researchers to **formally assess the extent
> to which their conclusions are sensitive to violations of parallel trends**. A natural statistic to
> report in many contexts is the **"breakdown" value of M̄** using the sensitivity analysis in
> Rambachan and Roth (2022b) — i.e. **how big would the post-treatment violation of parallel trends
> have to be relative to the largest pre-treatment violation to invalidate a particular
> conclusion?**»

Отдельное предупреждение по event-study при ступенчатом внедрении (стр. 29):
> «As noted by Sun and Abraham (2021), the coefficients β_r may be **contaminated by treatment
> effects at relative time r′ > 0**, so with heterogeneous treatment effects the pre-trends test may
> reject even if parallel trends holds in the pre-treatment period (or vice versa).»
🔴 Практический вывод: при поэтапной раскатке фичи по когортам НЕ использовать обычный TWFE —
использовать оценщики для staggered-настройки (Callaway–Sant'Anna и родственные).

**Что это даёт FINPILOT конкретно.** DiD у нас применим не к «поставил приложение / не поставил»
(там тренды почти наверняка не параллельны), а к **изменению внутри продукта**: включили новую
версию рекомендации одной когорте пользователей — сравниваем с когортой на старой версии,
у обеих есть история метрик ДО. Тогда самоотбор в приложение уже произошёл у всех, и допущение
становится правдоподобным. 🔴 **Требование к логам:** чтобы event-study вообще был возможен,
нужны исходные метрики **за несколько периодов ДО** изменения — то есть панель по месяцам
с первого дня, а не срез.

---

### 2.2 Regression discontinuity

#### Источник H. Lee D. S., Lemieux T. «Regression Discontinuity Designs in Economics». NBER Working Paper 14723, февраль 2009 (опубл. Journal of Economic Literature, 2010, 48(2)).
Добыт полностью: `curl` NBER → PDF → `pdftotext -layout`, 5723 строки (pdftotext ругнулся
`Invalid XRef entry 1`, но текст извлёк целиком).
URL: https://www.nber.org/papers/w14723 · PDF: https://www.nber.org/system/files/working_papers/w14723/w14723.pdf

**Условие, при нарушении которого дизайн рассыпается (стр. 2), дословно:**
> «**RD designs can be invalid if individuals can precisely manipulate the "assignment variable".**
> When there is a payoff or benefit to receiving a treatment, it is natural for an economist to
> consider how an individual may behave to obtain such benefits. <...> The important lesson here is
> that **the existence of a treatment being a discontinuous function of an assignment variable is not
> sufficient to justify the validity of an RD design. Indeed, if anything, discontinuous rules may
> generate incentives, causing behavior that would invalidate the RD approach.**»

**Почему при отсутствии точного контроля получается квазиэксперимент (стр. 2–3):**
> «If individuals – even while having some influence – are **unable to precisely manipulate** the
> assignment variable, a consequence of this is that the variation in treatment near the threshold is
> **randomized as though from a randomized experiment**. <...> every individual will have
> approximately the same probability of having an X that is just above (receiving the treatment) or
> just below (being denied the treatment) the cutoff – **similar to a coin-flip experiment**.»
> «**RD designs can be analyzed – and tested – like randomized experiments.** <...> all "baseline
> characteristics" – all those variables determined prior to the realization of the assignment
> variable – **should have the same distribution just above and just below the cutoff**. If there is
> a discontinuity in these baseline covariates, then at a minimum, the underlying identifying
> assumption of individuals' inability to precisely manipulate the assignment variable is
> unwarranted.»

**Чеклист реализации (стр. 55–57, §4.6) — дословно, сокращённо по пунктам:**
> «1. **To assess the possibility of manipulation of the assignment variable, show its distribution.**
> The most straightforward thing to do is to present a **histogram** of the assignment variable, using
> a fixed number of bins. <...> we recommend against plotting a smooth function comprised of kernel
> density estimates. **A more formal test of a discontinuity in the density can be found in McCrary
> (2008).**
> 2. **Present the main RD graph using binned local averages** <...> We recommend generally
> "undersmoothing" <...> we recommend against simply plotting the raw data without a minimal amount
> of local averaging.
> 3. **Graph a benchmark polynomial specification.**
> 4. **Explore the sensitivity of the results to a range of bandwidths, and a range of orders to the
> polynomial.** <...> report a "typical" point estimate and a range of point estimates.
> 5. **Conduct a parallel RD analysis on the baseline covariates.** <...> there should be no
> discontinuities in variables that are determined prior to the assignment.
> 6. **Explore the sensitivity of the results to the inclusion of baseline covariates.** <...> the
> inclusion of baseline covariates – no matter how highly correlated they are with the outcome –
> **should not affect the estimated discontinuity**, if the no-manipulation assumption holds.»

🔴 **Годятся ли наши пороги ПДН 0,40 и floor резерва как RDD-разрывы? Ответ: ПДН 0,40 — почти
наверняка НЕТ, floor резерва — возможно, ДА. Разбор:**

**ПДН 0,40 — нет.** Три причины, каждая ложится на процитированное выше.
1. Порог **известен и создаёт стимул** — ровно то, о чём предупреждают авторы: «discontinuous
   rules may generate incentives, causing behavior that would invalidate the RD approach».
   Пользователь, увидевший, что при ПДН 0,401 система блокирует альтернативу, может подправить
   введённый доход. Это **точная манипуляция assignment variable**, а не приблизительное влияние.
2. ПДН у нас **вычисляется из введённых пользователем данных**, а не измеряется независимо.
   Assignment variable, который подконтролен субъекту с точностью до копейки, — худший
   возможный случай для RDD.
3. ПДН 0,40 — не просто порог отсечки, а **жёсткий инвариант модели**: за ним альтернативы
   не существует вовсе. Значит по одну сторону порога нет вариации в treatment, которую можно
   сравнивать; это не разрыв в вероятности лечения, а полное отсутствие опции.
Проверка, если всё же захотим: тест McCrary (2008) на разрыв плотности ПДН у 0,40. Если увидим
скопление наблюдений прямо под 0,40 — манипуляция подтверждена и RDD закрыт.

**Floor резерва — возможно.** Если floor задаётся правилом от параметров, которые пользователь
не подгоняет прицельно (например, от медианных расходов за прошлые месяцы, посчитанных
системой), то точный контроль отсутствует и локальная рандомизация правдоподобна. Обязательно
прогнать пп. 1 и 5 чеклиста: гистограмма расстояния до floor + RD-анализ на предобработанных
ковариатах.

**Ограничение результата, о котором нельзя молчать в научном тексте:** RDD оценивает эффект
**локально у порога** («The estimated treatment effect is applicable to [units at the cutoff]»,
стр. ~9 обсуждения). Утверждение «продукт помогает» из RDD не следует — следует «продукт
помогает тем, кто у границы ПДН 0,40».

---

### 2.3 Инструментальные переменные

#### Источник I. Imbens G. W. «Instrumental Variables: An Econometrician's Perspective». NBER Working Paper 19983, 2014 (опубл. Statistical Science, 2014, 29(3)).
Добыт полностью: `curl` NBER → PDF → `pdftotext -layout`, 3047 строк.
URL: https://www.nber.org/papers/w19983

**Четыре допущения, дословно (стр. 27–30):**

1. **Случайное назначение инструмента** (или неконфаундированное при ковариатах):
> «Z_i ⊥ (Y_i(0,0), Y_i(0,1), Y_i(1,0), Y_i(1,1), X_i(0), X_i(1)) | X_i  (unconfounded assignment
> given X_i)». «This assumption is often satisfied by design: if the assignment is physically
> randomized <...> In other applications with observational data <...> this assumption is more
> controversial.»

2. **Exclusion restriction** — 🔴 названа самой критичной:
> «The second class of assumptions limits or rules out completely direct effects of the assignment
> on the outcome, other than through the effect of the assignment on the receipt of the treatment of
> interest. **This is the most critical, and typically most controversial assumption underlying
> instrumental variables methods**, sometimes viewed as the defining characteristic of instruments.
> One way of formulating this assumption is as
> **Y_i(0,x) = Y_i(1,x) for x = 0,1, for all i.   (exclusion restriction)**»
> Robins формулирует это как требование, что инструмент «is **not an independent causal risk
> factor**».

3. **Монотонность (no-defiance):**
> «A third assumption that is often used, labelled monotonicity by Imbens and Angrist (1994),
> requires that **X_i(1) ≥ X_i(0), for all i, (monotonicity)**, for all units. This assumption
> **rules out the presence of units who always do the opposite of their assignment** (units with
> X_i(0) = 1 and X_i(1) = 0), and is therefore also referred to as the **no-defiance assumption**.»

4. **Релевантность инструмента:**
> «Finally, we need the instrument to be correlated with the treatment, or the instrument to be
> **relevant** in the terminology of Staiger and Stock (1997).»

🔴 **Чего эти четыре допущения НЕ дают (стр. 31), дословно:**
> «**With only the four assumptions, random assignment, the exclusion restriction, monotonicity, and
> instrument relevance** Robins (1989), Manski (1990) and Balke and Pearl (1995) established that the
> **average treatment effect can often not be consistently estimated even in large samples**, in
> other words, that it is often **not point-identified**.»
То есть IV даёт LATE — эффект на комплаерах, а не ATE, и без дополнительных допущений средний
эффект вообще не точечно идентифицируем.

**Кандидаты в инструменты для FINPILOT — честный разбор, все слабые.**
Ищем Z, влияющий на использование рекомендации, но не на финансовое поведение напрямую.
1. **Технический сбой / плановое обслуживание, отключавшее выдачу рекомендации у части
   пользователей.** Похоже на «природный эксперимент»: назначение почти случайно.
   Exclusion restriction: сбой не влияет на поведение иначе, чем через отсутствие рекомендации —
   правдоподобно, если сбой был незаметен пользователю. Если он видел ошибку и раздражился —
   restriction нарушена (сбой действует и напрямую, через доверие). 🔴 Требование к логам:
   фиксировать факт и точное окно недоступности сервиса.
2. **Поэтапная раскатка по техническому признаку (версия ОС, регион серверов, номер шарда).**
   Random assignment — да, если шардирование по хэшу. Exclusion — да, если признак сам не связан
   с финансовым поведением. **Номер шарда по хэшу user_id — самый чистый кандидат из всех**,
   и он бесплатен: достаточно записывать `assignment_bucket` в лог с первого дня. По сути это
   рандомизация, замаскированная под инфраструктуру, — и она законна, потому что не показывает
   никому заведомо худшую рекомендацию, а лишь определяет, кто получает новую версию раньше.
3. **Push-уведомление «загляните в рекомендации» с рандомизацией отправки** — классический
   encouragement design. Random assignment — по построению. Exclusion — 🔴 **нарушена почти
   наверняка**: сам факт напоминания о финансах меняет поведение, даже если человек не открыл
   приложение. Это ровно «independent causal risk factor». Использовать нельзя, а вот как
   ITT-эксперимент (эффект самого напоминания) — можно, и это отдельный честный результат.
4. **Версия ОС / модель телефона** — отвергнуть: коррелирует с доходом, а значит с исходом
   напрямую. Exclusion restriction нарушена грубо.

**Вывод по 2.3:** единственный инструмент, который выдерживает разбор, — **технический бакет
раскатки по хэшу идентификатора**. И это, по сути, аргумент в пользу участка 1: дешевле сразу
рандомизировать явно, чем потом искать инструмент.

### 2.4 Synthetic control

🔴 **Первоисточник Abadie (2021) JEL 59(2):391–425 «Using Synthetic Controls: Feasibility, Data
Requirements, and Methodological Aspects» НЕ ДОБЫТ.** Каналы и коды: `curl` на economics.mit.edu
(два варианта пути) → HTML-заглушка/404; `curl` на aeaweb.org PDF → HTML (пейволл);
`r.jina.ai` на economics.mit.edu → HTTP 404 «Page not found | MIT Economics»; `r.jina.ai`
на страницу AEA → 1 710 байт, только аннотация без текста; nber.org версии нет.
Пейволл AEA прокси не пробивает (подтверждает известное: `r.jina.ai` обходит антибот, но НЕ пейволл).
Взято через работу, которая цитирует требования Abadie дословно.

#### Источник J. Ben-Michael E., Feller A., Rothstein J. «The Augmented Synthetic Control Method». arXiv:1811.04170 (опубл. JASA, 2021).
Добыт полностью: `curl` → PDF 3.6 МБ → `pdftotext -layout`, 193 КБ текста.
URL: https://arxiv.org/abs/1811.04170 · PDF: https://arxiv.org/pdf/1811.04170

**Область применимости (стр. 1, §1), дословно:**
> «The synthetic control method (SCM) is a popular approach for estimating the impact of a treatment
> on **a single unit in panel data settings with a modest number of control units and with many
> pre-treatment periods**. The idea is to construct a **weighted average of control units**, known
> as a synthetic control, that **matches the treated unit's pre-treatment outcomes**. The estimated
> impact is then the difference in post-treatment outcomes between the treated unit and the synthetic
> control.»

🔴 **Условие, при нарушении которого метод не применяют вообще (стр. 1 и стр. 7), дословно:**
> «**A critical feature of the original proposal, not always followed in practice, is to use SCM only
> when the synthetic control's pre-treatment outcomes closely match the pre-treatment outcomes for
> the treated unit** (Abadie et al., 2015). **When it is not possible to construct a synthetic
> control that fits pre-treatment outcomes well, the original papers advise against using SCM.**»
> «When "**the pre-treatment fit is poor or the number of pre-treatment periods is small**," Abadie
> et al. (2015) recommend against using SCM. **Even if the pre-treatment fit is excellent, Abadie et
> al. (2010, 2015) propose extensive placebo checks to ensure that SCM weights do not overfit to
> noise.** Thus, **the conditional nature of the analysis is critical to deploying SCM, excluding
> many practical settings.**»

**Про выпуклую оболочку (стр. 7):**
> «When the treated unit's vector of lagged outcomes, X₁·, is **inside the convex hull** of the
> control units' lagged outcomes, X₀·, the SCM weights achieve **perfect pre-treatment fit**, and the
> resulting estimator has many attractive properties, including a bias bound established by Abadie
> et al. (2010). **Due to the curse of dimensionality, however, achieving perfect (or nearly perfect)
> pre-treatment fit is not always feasible** with weights constrained to be on the simplex.»
Соскальзывание в обычную регрессию как решение авторы называют плохим: «This allows better (often
perfect) pre-treatment fit, but does so by **applying negative weights to some control units,
extrapolating outside the support of the data**.» ASCM предложен как средний путь.

🔴 **Годится ли synthetic control для FINPILOT? По прямому назначению — НЕТ.** SCM устроен под
«одна обработанная единица, десятки контрольных, много периодов до» — это про регионы и страны,
а не про десятки тысяч пользователей. У нас обратная геометрия: много единиц, мало периодов.
Две ситуации, где он всё же применим:
1. **Агрегированный запуск.** Если продукт выходит в одном регионе/сегменте раньше, чем
   в остальных, и мы имеем помесячные агрегаты по сегментам за год до, — SCM легален.
2. **Единичный пользователь как кейс** (N-of-1): для качественного разбора отдельного случая
   в научном тексте — «вот пользователь, вот его синтетический двойник из тех, кто не получил
   рекомендацию». Требует много месяцев истории на одного человека. Реалистично не раньше
   второго года работы продукта.
Строку «мало выборки — возьмём synthetic control» из плана вычеркнуть: метод требует не малой
выборки единиц, а **длинной предыстории**, а её у нас на старте не будет вовсе.

---

## Участок 3. Uplift / heterogeneous treatment effects

### 3.1 Зачем вместо среднего эффекта

Средний эффект (ATE/ATT) отвечает на вопрос «помогает ли продукт в среднем». Он молчит о том,
**кому** помогает и кому вредит. Если эффект +10% у одной трети и −5% у другой, средний
выглядит как +1,7% и, скорее всего, окажется статистически неотличим от нуля — ровно как
у Commonwealth Bank в теме 26 (p = 0,162). 🔴 **Нулевой средний эффект и «продукт не работает» —
не одно и то же**, и uplift-моделирование — единственный способ отличить одно от другого.

Целевая величина — CATE (conditional average treatment effect):
> τ(x) := E[D | X = x] = E[Y(1) − Y(0) | X = x]
(Künzel et al., стр. 3)

### 3.2 Мета-обучатели: S / T / X

#### Источник K. Künzel S. R., Sekhon J. S., Bickel P. J., Yu B. «Metalearners for estimating heterogeneous treatment effects using machine learning». PNAS 116(10):4156–4165, 2019 (препринт arXiv:1706.03461).
Добыт полностью: `curl` → PDF → `pdftotext -layout`, 4184 строки (с приложениями).
URL: https://arxiv.org/abs/1706.03461 · PNAS: https://doi.org/10.1073/pnas.1804597116

**Условие идентификации (Condition 1, стр. 3), дословно:**
> «To aid our ability to estimate τ, we need to assume that there are **no hidden confounders** (13):
> **Condition 1: (ε(0), ε(1)) ⊥ W | X.**»
🔴 Это то самое допущение, которое у нас без рандомизации не выполняется. Все три мета-обучателя
на него опираются; ML-мощность его не заменяет.

**T-learner (стр. 3), дословно:**
> «The T-learner takes two steps. First, the control response function, **µ₀(x) = E[Y(0)|X = x]**,
> is estimated by a base learner <...> using the observations in the control group, {(X_i, Y_i)}_{W_i=0}.
> <...> Second, we estimate the treatment response function, **µ₁(x) = E[Y(1)|X = x]**, with a
> potentially different base learner, using the treated observations <...> A T-learner is then
> obtained as
> **τ̂_T(x) = µ̂₁(x) − µ̂₀(x).   (3)**»

**S-learner (стр. 3–4), дословно:**
> «In the S-learner, the treatment indicator is included as a feature **similar to all the other
> features without the indicator being given any special role**. We thus estimate the combined
> response function, **µ(x, w) := E[Y^obs | X = x, W = w]**, using any base learner <...> The CATE
> estimator is then given by **τ̂_S(x) = µ̂(x, 1) − µ̂(x, 0).   (4)**»

**X-learner (стр. 4), три стадии, дословно:**
> «1. Estimate the response functions **µ₀(x) = E[Y(0)|X = x]** (5), and **µ₁(x) = E[Y(1)|X = x]**
> (6), using any supervised learning or regression algorithm <...>
> 2. **Impute the treatment effects** for the individuals in the treated group, based on the control
> outcome estimator, and the treatment effects for the individuals in the control group, based on
> the treatment outcome estimator, that is,
> **D̃¹_i := Y¹_i − µ̂₀(X¹_i)   (7)**, and **D̃⁰_i := µ̂₁(X⁰_i) − Y⁰_i   (8)**,
> and call these the **imputed treatment effects**. <...> Employ any supervised learning or
> regression method(s) to estimate τ(x) in two ways <...>
> 3. Define the CATE estimate by a **weighted average** of the two estimates in Stage 2:
> **τ̂(x) = g(x)·τ̂₀(x) + (1 − g(x))·τ̂₁(x),   (9)** where g ∈ [0,1] is a weight function.»
> «Based on our experience, we observe that it is **good to use an estimate of the propensity score
> for g, so that g = ê**, but it also makes sense to choose g = 1 or 0, if the number of treated
> units is very large or small compared to the number of control units.»

🔴 Здесь **propensity снова обязателен** — теперь уже как весовая функция g. Ещё один аргумент
логировать его с первого дня.

**Когда X-learner выигрывает (стр. 11, Conclusion; стр. 6, Comparison of Convergence Rates),
дословно:**
> «both theory and data examples show that it performs particularly well when **one of the treatment
> groups is much larger than the other** or when the separate parts of the X-learner are able to
> exploit the structural properties of the response and treatment effect functions. Specifically,
> **if the CATE function is linear, but the response functions in the treatment and control group
> satisfy only the Lipschitz-continuity condition, the X-learner can still achieve the parametric
> rate if one of the groups is much larger than the other (Theorem 2).** If there are no regularity
> conditions on the CATE function and the response functions are Lipschitz continuous, then **both
> the X-learner and the T-learner obtain the same minimax optimal rate (Theorem 7).**»

🔴 **Правило большого пальца авторов (стр. 5), дословно:**
> «These simulation results lead us to the conclusion that **unless one has a strong belief that the
> CATE is mostly 0, then, as a rule of thumb, one should use the X-learner with BART for small data
> sets and RF for bigger ones.**»

**Прямой перенос на FINPILOT.** Наша схема exploration неизбежно даст **сильно несбалансированный
дизайн**: 90–95% трафика получают детерминированный топ-1, 5–10% — рандомизированную выдачу.
Это ровно тот случай, под который X-learner и построен («one group is much larger than the
other»). Значит выбор мета-обучателя предрешён условиями участка 1: **X-learner, база BART на
малых данных (сотни–тысячи), RF на больших.**

### 3.3 Causal forests

#### Источник L. Wager S., Athey S. «Estimation and Inference of Heterogeneous Treatment Effects using Random Forests». JASA 113(523):1228–1242, 2018 (препринт arXiv:1510.04342).
Добыт полностью: `curl` → PDF → `pdftotext -layout`, 9274 строки.
URL: https://arxiv.org/abs/1510.04342

**Неконфаундированность (стр. 5, формула 2), дословно:**
> «A standard way to make progress is to assume **unconfoundedness** [Rosenbaum and Rubin, 1983],
> i.e., that the treatment assignment W_i is independent of the potential outcomes for Y_i
> conditional on X_i: **{Y_i(0), Y_i(1)} ⊥⊥ W_i | X_i.   (2)**»
> «The motivation behind unconfoundedness is that, given continuity assumptions, it effectively
> implies that we can **treat nearby observations in x-space as having come from a randomized
> experiment**.»

**Роль propensity (стр. 5, формула 3), дословно:**
> «E[Y_i·(W_i/e(x) − (1−W_i)/(1−e(x))) | X_i = x] = τ(x), where **e(x) = E[W_i | X_i = x]** is the
> **propensity of receiving treatment at x**. Thus, if we knew e(x), we would have access to a
> simple unbiased estimator for τ(x).»

🔴 **Условие overlap (стр. 7, формула 6), дословно — то, что у нас нарушено при детерминированной
выдаче:**
> «In addition to continuity assumptions, we also need to assume that we have **overlap**, i.e., for
> some ε > 0 and all x ∈ [0,1]^d, **ε < P[W = 1 | X = x] < 1 − ε.   (6)** This condition effectively
> guarantees that, for large enough n, **there will be enough treatment and control units near any
> test point x for local methods to work.**»

**Honesty — условие для доверительных интервалов (стр. 8), дословно:**
> «Our results do, however, require the individual trees to satisfy a fairly strong condition, which
> we call **honesty: a tree is honest if, for each training example i, it only uses the response Y_i
> to estimate the within-leaf treatment effect τ <...> or to decide where to place the splits, but
> not both.**»
> Реализация: «**double-sample tree** achieves honesty by dividing its training subsample into two
> halves I and J. Then, it uses the J-sample to place the splits, while holding out the I-sample to
> do within-leaf estimation.»
> И вариант для наблюдательных данных: «Another way to build honest trees is to **ignore the outcome
> data Y_i when placing splits, and instead first train a classification tree for the treatment
> assignments W_i (Procedure 2). Such **propensity trees** can be particularly useful in
> **observational studies**, where we want to minimize bias due to variation in e(x).»

**Что даёт causal forest сверх мета-обучателей (стр. 7, формула 7), дословно:**
> «the predictions made by a causal forest are **asymptotically Gaussian and unbiased**.
> Specifically, we show that **(τ̂(x) − τ(x)) / √Var[τ̂(x)] ⇒ N(0,1)   (7)** under the conditions
> required for consistency, provided the subsample size s scales as s ≍ n^β [for an appropriate β].»

🔴 Практический вывод: **X-learner даёт точечную оценку CATE, causal forest — оценку С
ДОВЕРИТЕЛЬНЫМ ИНТЕРВАЛОМ.** Для научного текста (ВКР/статья/магистратура) второе обязательно:
«у сегмента А эффект +Х п.п. [95% ДИ: …]» проверяемо, а «у сегмента А uplift 0,08» — нет.
План: X-learner для отбора сегментов, causal forest для инференса по отобранным.

### 3.4 🔴 Прямо наш случай: брекетеры из темы 36

Тема 36: узкий брекетинг у **74%** выборки (Ellis & Freeman, AER 2024), широкий — у ~13%.
Гипотеза, которую надо проверять uplift-моделью, а не средним: **рекомендация СППР должна
сильнее помогать узким брекетерам, потому что она делает за них ровно то, чего они сами не
делают — рассматривает распределение потока целиком, а не по одной статье.** У широких
брекетеров этот механизм уже работает своими силами, и добавленная ценность близка к нулю.
Если это так, средний эффект по всей выборке будет смещён вниз участием широких брекетеров,
и есть риск получить «неотличимо от нуля» при реальном эффекте у трёх четвертей аудитории.

**Как это измерять — конкретно:**
1. **Признак брекетинга должен быть измерен, а не спрошен.** Самоотчёт «вы планируете бюджет
   целиком?» не годится. Годятся поведенческие прокси из наших же логов: доля сессий, в которых
   пользователь смотрел сводную картину до принятия решения; правил ли он одну статью расходов
   изолированно; менял ли параметры по одному или пересобирал план. 🔴 **Это надо логировать
   с первого дня** — задним числом такой признак не восстановить.
2. Признак идёт как **ковариата X** в τ(x), а не как отдельный подвыборочный анализ. Разбиение
   выборки руками с последующим тестированием каждой части — это multiple testing и p-hacking;
   мета-обучатели и causal forest решают ту же задачу корректно.
3. Отчёт: **не «эффект есть/нет», а распределение τ̂(x) по выборке** плюс средний эффект внутри
   квантилей предсказанного uplift.

🔴 **Ограничение, которое надо назвать честно.** Тема 36 даёт долю брекетеров в популяции США
на данных Ellis & Freeman; переносимость 74% на пользователей российского финансового
приложения ничем не подтверждена. Наша задача — не подтвердить чужое число, а измерить
гетерогенность у себя. Число 74% используем как **основание для гипотезы**, не как оценку.

### 3.5 Метрики: Qini-кривая, uplift@k

🔴 **Первоисточник Radcliffe (2007) «Using control groups to target on predicted lift» НЕ ДОБЫТ**
(журнал Direct Marketing Analytics Journal, вне открытого доступа; в поиске первоисточник
не обнаружен). Определения ниже взяты из вторичных источников, **из сниппетов поисковой
выдачи, а не из прочитанных целиком статей** — помечаю как непроверенные и требующие сверки
перед использованием в научном тексте.

Из сниппетов (`WebSearch`, не открывал полностью):
> «Qini coefficients represent a natural generalization of the Gini coefficient to the case of
> uplift. The Qini curve <...> evaluates an uplift (treatment-effect) model by plotting the
> **cumulative incremental number of positive outcomes gained as units are treated in descending
> order of their predicted uplift score**.»
> Формула из сниппета: **Qini(k) = R^{T=1}_{π(k)} − R^{T=0}_{π(k)} · (N^{T=1}_{π(k)} / N^{T=0}_{π(k)})**
> — то есть накопленный отклик среди пролеченных в топ-k минус накопленный отклик среди контроля
> в том же топ-k, **отмасштабированный отношением размеров групп**.
> «The difference between the area under the actual Qini curve and that under the diagonal
> corresponding to random targeting <...> further normalized by the area between the random and the
> optimal targeting curves, [is] defined as Qini coefficient.»
Кандидаты в первоисточники для сверки (найдены, не открывались): arXiv:1911.12474
«Qini-based Uplift Regression», arXiv:2210.02152 «Improving uplift model evaluation on RCT data».

**Смысл для нас.** Qini отвечает не на вопрос «есть ли эффект», а на вопрос «умеет ли моя модель
**ранжировать** людей по величине эффекта». Это в точности та метрика, которая нужна для решения
«кому вообще показывать активную рекомендацию, а кому лучше не мешать».
🔴 **uplift@k** — доля прироста, собранная в верхних k% по предсказанному uplift; операционно
она полезнее Qini, потому что переводится в решение напрямую: «активную рекомендацию включаем
верхним 30% по uplift».

🔴 **Ограничение, снимающее половину энтузиазма.** Qini и uplift@k **считаются только на данных
с контрольной группой** — им нужны и treated, и untreated в каждом сегменте. Без участка 1
(рандомизация + propensity) весь участок 3 нереализуем. Uplift — не альтернатива логированию,
а его потребитель.

---

## Участок 4. Что считать исходом

### 4.1 Какие метрики НЕ годятся — регуляторная формулировка

#### Источник M. FCA. «Outcomes monitoring: good practice and areas for improvement». Опубликовано 27.07.2026.
Добыт полностью: `WebFetch` дал пересказ, **сверен `r.jina.ai`-выгрузкой на 71 000 байт —
формулировки совпали дословно.** (Проверка по правилу «пересказ малой моделью не доверять».)
URL: https://www.fca.org.uk/publications/good-and-poor-practice/outcomes-monitoring-good-practice-and-areas-improvement

🔴 **Ключевая цитата, дословно:**
> «**Collecting data, listing metrics or reporting management information (MI) will not, by itself,
> show whether customers are receiving good outcomes.** Firms should be able to explain:
> • What their information tells them.
> • How they use it to identify risks or issues.
> • What action they take in response.
> • **How they consider whether those actions have improved outcomes.**»

🔴 **Плохая практика — operational metrics как proxy, дословно** (раздел «Weak links between
outcomes, metrics and customer journeys»):
> «**Some firms used operational activity metrics, like conversion rates or review completion, as a
> proxy for customer outcomes – but did not define good or poor outcomes for customers at different
> stages of the journey.**»

**Плохая практика — широкое определение без привязки к этапам, дословно:**
> «Some firms had a broad definition of good customer outcomes and a list of performance indicators.
> However, they **did not clearly explain what good outcomes look like at each stage of the customer
> journey, or how each metric demonstrated those outcomes.** This can make it difficult to show
> whether outcomes are good or bad.»
> «One firm described a broad outcomes framework but **did not clearly define good and poor outcomes
> for key customer journeys, or have evidence for the thresholds it used to assess them.**»

**Плохая практика — игнорирование различий между группами, дословно:**
> «Some firms defined good customer outcomes at a broad level but did not clearly link them to key
> stages of the customer journey. **There was also limited evidence of how outcomes differ across
> customer groups, including people in vulnerable circumstances.** This can make it harder to know
> where customers may have worse outcomes or need more support.»
> «Some firms monitored outcomes for customers in vulnerable circumstances separately to other
> customers, but **did not segment those outcomes by vulnerability drivers**. For example, one firm
> aggregated its vulnerability MI rather than splitting it by drivers such as **health, financial
> resilience or life events**.»

🔴 Последняя цитата — это по сути регуляторное требование того же, что участок 3 требует
статистически: **отчёт по гетерогенности эффекта, а не только по среднему.** Uplift-моделирование
и FCA-мониторинг исходов сходятся в одной точке.

**Смягчение для маленьких фирм (важно для нас, стр. «Smaller firms»), дословно:**
> «**Smaller firms could use a focused set of indicators without complex systems or large teams.**
> What matters is that firms can explain what their information shows, how it helps them identify
> harm or poor outcomes, and what they do in response.»

**🔴 Прямой список для FINPILOT — что НЕ считать исходом.** Всё это operational metrics, каждая
из них у нас соблазнительно доступна и каждая запрещена FCA как proxy:
DAU/MAU, retention, число сессий, глубина скролла, конверсия в «принял рекомендацию»,
доля завершённых онбордингов, NPS, время в приложении, число созданных целей.
Они годятся как **диагностика того, что механизм сработал** (пользователь увидел рекомендацию),
но не как ответ на вопрос «стало ли ему лучше».

### 4.2 Прокси-метрики, которые годятся

Настоящий исход — благосостояние через 10 лет — недоступен. Практика финансовых исследований
подставляет измеримые прокси **из транзакционных данных**, а не из самоотчёта. Из двух работ
ниже (обе — реальные полевые эксперименты на банковских данных) состав таков:
- **дискреционные расходы** (развлечения, рестораны, одежда) — отдельно от недискреционных
  (бензин, продукты, ЖКУ), потому что вторые почти не поддаются краткосрочной корректировке;
- **снятия наличных** — отдельная строка, так как в них прячется расход, не попадающий
  в категории;
- **крупные редкие транзакции** — их люди систематически не закладывают в бюджет;
- **баланс сберегательного счёта**, **баланс текущего счёта**, **суммарные депозиты**;
- **факт первого в жизни сбережения** (бинарный исход для тех, у кого сбережений не было).

Для FINPILOT добавляются исходы, специфичные для СППР по распределению потока:
**остаток долга по портфелю**, **суммарная переплата по процентам к дате**, **месяцы покрытия
резервом**, **доля месяцев с Rt ≥ 0**, **ПДН** — все они считаются из тех же данных,
на которых работает модель, и все они «finance-true», а не «product-true».

### 4.3 Полевой эксперимент внутри PFM-приложения: шаблон, который можно скопировать

#### Источник N. Levi Y. «Personal Financial Information Presentation and Consumer Spending». Journal of Financial and Quantitative Analysis (принята, версия 26.10.2025).
Добыт полностью: первая закачка `curl` дала битый PDF (`Invalid XRef entry 0`), **повторная
закачка с `--retry` дала целый файл 6.6 МБ** → `pdftotext -layout`, 2857 строк. (Записываю как
приём: битый PDF — не «недоступен», а «перекачать».)
URL: https://jfqa.org/wp-content/uploads/2025/10/24988_Personal_Financial_Info.pdf

**Дизайн (Abstract), дословно:**
> «We study whether information design influences consumer behavior in a **randomized field
> experiment with users of an online account aggregation app**. Participants received a personalized
> index representing their net worth as a lifetime monthly cash flow. The presentation of this index
> varied across treatments in its framing and the salience of its display. Consumers exposed to a
> consumption-oriented frame and a salient comparison of the index with their past spending
> **reduced discretionary spending**.»

**Размер и горизонт, дословно (стр. ~16):**
> «**The final sample consists of 3,138 users.** Data on users' transactions and login activity are
> collected for a period of **25 months, starting five months before the experiment launch and
> continuing for twenty months after**.»
> «Users were randomly assigned to **seven groups**. Apart from the control group, all treated
> groups received a personalized index.»
> «Experiment materials were available on the app for a period of **eight months**.»

**Эффект и его динамика, дословно (стр. 4–5):**
> «[users exposed to the consumption frame with a] context plot **decreased their discretionary
> spending by about 15%** relative to users who received only the consumption frame with no plot or
> a context plot but with a neutral frame. **The decrease in discretionary spending started
> immediately after the launch of the experiment and persisted throughout the eight months** in
> which the experiment materials were presented on the app. These consumers increased their spending
> levels only gradually after the removal of the experiment content and **converged to the spending
> levels of consumers in unaffected groups after an additional eight months**.»
> «The decrease in spending is most pronounced in relatively "tempting" spontaneous categories such
> as **entertainment, restaurants, and clothing** <...> In contrast, **we do not find a change in
> non-discretionary spending such as gas, groceries, and utilities**, which are difficult to adjust,
> especially over a short time period.»
> «we find a **decrease in infrequent large-ticket transactions** <...> people tend to omit such
> "exceptional" transactions from their budget plan.»
> «users in the affected treatments also **decreased their cash withdrawals**, representing an
> additional decrease in spending (i.e., not included in the discretionary spending variable).»

**Спецификация оценки, дословно (стр. 17):**
> «δ_i is an **individual fixed effect**, and θ_j is an **event-month fixed effect**. **Standard
> errors are clustered at the consumer level.** <...> β_j captures the average change in the outcome
> variable between the pre-experiment months (t=−5 to t=−1) and the experiment months (t=0 to t=7)
> of consumers in treatment group j, relative to the same change in the omitted treatment group.
> Similarly, γ_j captures the average change <...> and the post-experiment months (t=8 to t=19).»
> Сноска 11: «All tests are robust to **double clustering** of the standard errors by consumer and
> year-month.»

**Критерии включения в выборку (стр. 16), дословно:**
> «had been using the app for **at least five months before the experiment**» ·
> «only users who logged into the app **at least once in the three months** [before launch]» ·
> «income and spending **above $1,000 in the five months** before the experiment launch».

🔴 **Три вывода для FINPILOT, каждый прямо переносим.**
1. **3 138 пользователей на 7 групп (≈450 на руку) хватило, чтобы поймать эффект в 15%.**
   Это реалистичный ориентир по размеру: не «нужны десятки тысяч».
2. **Горизонт: 5 месяцев ДО + 8 месяцев воздействия + 12 месяцев после.** Минимальная
   предыстория — 5 месяцев, иначе event-study не построить. 🔴 Это и есть ответ на вопрос
   «какой минимальный горизонт»: **не меньше 5 месяцев до и 6–8 месяцев после**, иначе
   эффект в финансовом поведении не отделим от сезонности.
3. **Эффект обратим и затухает за ~8 месяцев после снятия воздействия.** Значит замер надо
   вести непрерывно, а не «померили один раз и закрыли». И значит утверждение «продукт изменил
   человека» некорректно — корректно «продукт меняет поведение, пока он присутствует».

Дисциплинирующая деталь: эксперимент проведён в 2014 году и **не был предрегистрирован**
(автор указывает это прямо: «The experiment described in this paper was not pre-registered;
it was conducted in 2014, before pre-registration became common practice in economics and
finance»). Одобрение: «The study was exempt from IRB review by the Office of the Human Research
Protection Program at USC (Study ID: UP-20-00254)» и «This study does not use any personally
identifiable information».
🔴 Для нас: **предрегистрация плана анализа** — дешёвый способ снять подозрение в p-hacking
в научном тексте, и её надо делать до, а не после.

### 4.4 Второй пример: эффект PFM-инструмента на сбережения, но БЕЗ рандомизации

#### Источник O. Becker G. «Does FinTech Affect Household Saving Behavior? Findings from a Natural Field Experiment». Working Paper, Goethe University Frankfurt, 12.06.2017 (представлен на конференции ФРБ Филадельфии).
Добыт полностью: `curl` → PDF → `pdftotext -layout`, 2260 строк.
URL: https://www.philadelphiafed.org/-/media/frbp/assets/events/2017/consumer-finance/fintech-2017/day-2/does-fintech-affect-household-saving-behavior.pdf

**Дизайн и данные, дословно:**
> «We analyze a rich dataset of **65,073 German customers** obtained in a natural experiment between
> **August 2015 and March 2016**. We observe financial balances prior and after money management
> FinTech activation for a group of users and **a control group of non-users**. Also, over **2
> million current account transactions** of customers who use the tool are available.»
> «During this period **15,077 customers activated** their money management tool. 49,996 [did not].»

**Результаты, дословно:**
> «the average customer's **monthly savings balance significantly increases after tool activation by
> 268 EUR**. Average monthly current account balance significantly increases by **176 EUR** and
> total deposits held at the bank increase on average by **409 EUR** in the post-activation period.
> The latter equals an **increase of 4.2%** compared to pre-experiment deposits.»
> «customers **without any observable saving activity prior to the treatment are more likely to start
> first time saving**, after tool activation and can thus benefit from the FinTech.»
> «the increase in savings balance is driven by amplified spending on **saving plans which can easily
> be setup within the money management FinTech** <...> **active tool usage for most customers
> declines already in the first month post activation.** Together with the fact that changes in
> consumption splits are economically hardly relevant, this implies that **the tool's feature to set
> automatic default saving plans is of high relevance in changing the saving behavior**.»

🔴 **Самоотбор назван самим автором, и это главная слабость работы:**
> «customers who are **male, younger, and have a more intense banking relationship, are more likely
> to activate** the tool. We also find that customers with **low saving balances prior to the
> experiment are more likely to activate** the FinTech.»
> «the tool is **less likely to be activated by financially less educated customers** in the first
> place.»
Дисбаланс на старте подтверждён числами: «average debit balance of **9,648 EUR** in the treatment
group is significantly below the average of **12,103 EUR** in the control group»; в другом месте
«**66,189 EUR (7,939 EUR)** compared to **92,756 EUR (15,318 EUR)**».

🔴 **Это ровно тот случай, о котором предупреждает Roth et al. (участок 2.1): активировавшие
и не активировавшие различаются не только уровнем, но и, скорее всего, трендом.** Название
«natural field experiment» здесь щедрое — рандомизации нет, есть DiD на самоотобранных группах.
Работа полезна как источник **прокси-метрик и порядка величин** (268 EUR, 409 EUR, +4,2%),
но как доказательство причинности она слабее Levi. **Не копировать этот дизайн.**

Побочный, но важный для продукта вывод: эффект дала **функция автоматических сберегательных
планов** (дефолт), а не сама аналитика — активность в инструменте падает уже в первый месяц.
Для FINPILOT это гипотеза: измеримый эффект, вероятно, даст не качество рекомендации,
а то, насколько легко её **исполнить** одним действием.

---

## ИТОГ

### И1. 🔴 ПРЯМОЙ ОТВЕТ: спецификация логирования с первого релиза

Формат — ТЗ разработчику. Три таблицы: событие выдачи, событие выбора, панель исходов.
Обоснование каждого поля — ссылкой на раздел выше.

#### Таблица 1. `recommendation_impressions` — по одной строке на каждую выдачу рекомендации

| Поле | Тип | Зачем | Откуда требование |
|---|---|---|---|
| `impression_id` | UUID | ключ склейки со всем остальным | — |
| `user_id` | UUID | панель | — |
| `session_id` | UUID | группировка внутри визита | — |
| `ts` | timestamptz (UTC) | событийное время; event-study без него невозможен | §2.1 |
| `policy_id` | text | какая политика приняла решение | Adyen §1.2 |
| `policy_version` | semver | версия модели; при смене — новая логирующая политика | §1.3 |
| `model_config_hash` | text | хэш всех весов/параметров SAW и риск-профиля | §1.1 (Bottou: нужны все различающиеся множители) |
| `context_snapshot` | jsonb | ВСЕ входы модели на момент решения: доход, обязательные платежи, долги, резерв, ПДН, риск-профиль | §1.1 |
| `context_hash` | text | быстрый ключ для матчинга одинаковых контекстов | — |
| `candidate_set` | jsonb | **все 66 альтернатив с их оценками SAW после применения инвариантов** | §1.1, §1.3 |
| `feasible_set_size` | int | сколько альтернатив осталось после Rt ≥ 0 и ПДН ≤ 0,40 | 🔴 §1.3: propensity считается ПОСЛЕ гейтов |
| `shown_actions` | jsonb (упорядоченный) | что реально показали и в каком порядке | §1.1 |
| `chosen_action_id` | text | какую альтернативу система предвыбрала/поставила первой | §1.2 |
| **`propensity`** | numeric(10,9) ∈ (0,1] | 🔴 **вероятность именно этого действия при действовавшей политике.** Без неё IPS/SNIPS/X-learner не считаются никогда | §1.2, §1.3, §3.2 |
| `propensity_all` | jsonb | вероятности по всем показанным действиям (сумма = 1) | §1.3 |
| `exploration_flag` | bool | попала ли выдача в exploration-трафик | §1.2 |
| `exploration_scheme` | text | `top_k` \| `power_normalized` \| `deterministic` | §1.2 (Douglas et al.) |
| `exploration_param` | numeric | k или d — параметр «жадности» | §1.2 |
| `eligible_for_exploration` | bool | прошёл ли пользователь этический фильтр | 🔴 §1.4 (уязвимые исключаются) |
| `exclusion_reason` | text \| null | почему исключён (`financial_stress`, `pdn_near_limit`, `negative_rt`, `new_user`) | §1.4 |
| `assignment_bucket` | smallint 0..99 | стабильный бакет `hash(user_id + salt) % 100` | 🔴 §2.3: единственный выдержавший разбор инструмент |
| `ui_variant` | text | версия интерфейса выдачи | §2.1 |
| `is_deterministic_fallback` | bool | сработал ли откат на детерминированную выдачу (сбой, таймаут) | §1.3 |

#### Таблица 2. `recommendation_actions` — реакция пользователя

| Поле | Тип | Зачем |
|---|---|---|
| `impression_id` | UUID FK | склейка |
| `ts` | timestamptz | лаг реакции |
| `action_type` | enum | `viewed` \| `expanded_alternatives` \| `changed_params` \| `accepted` \| `rejected` \| `ignored` |
| `selected_action_id` | text \| null | что выбрал пользователь, если не предвыбранное |
| `deviation_from_recommended` | numeric | насколько выбор отличается от топ-1 (в п.п. распределения) |
| `time_to_decision_ms` | int | |
| `viewed_full_set` | bool | 🔴 **поведенческий прокси брекетинга** (§3.4): смотрел ли сводную картину |
| `edited_single_category` | bool | 🔴 второй прокси брекетинга: правил ли одну статью изолированно |

🔴 Два последних поля — единственный способ измерить признак брекетинга из темы 36.
**Задним числом они не восстанавливаются.** Если их не заложить сейчас, участок 3 в части
«кому помогает» останется невыполнимым навсегда.

#### Таблица 3. `user_financial_snapshots` — панель исходов, снимок раз в месяц на пользователя

| Поле | Тип | Зачем | Откуда |
|---|---|---|---|
| `user_id`, `snapshot_month` | UUID, date | ключ панели | §2.1, §4.3 |
| `total_debt` | numeric | остаток долга по портфелю | §4.2 |
| `interest_paid_cumulative` | numeric | суммарная переплата к дате | §4.2 |
| `reserve_amount`, `reserve_months_coverage` | numeric | резерв в деньгах и в месяцах покрытия | §4.2 |
| `pdn` | numeric | долговая нагрузка | §4.2 |
| `rt` | numeric | свободный поток; доля месяцев с Rt ≥ 0 | §4.2 |
| `discretionary_spending` | numeric | 🔴 **отдельно** от недискреционных | §4.3 (Levi) |
| `nondiscretionary_spending` | numeric | контрольная метрика: не должна двигаться | §4.3 |
| `cash_withdrawals` | numeric | отдельная строка | §4.3 |
| `large_ticket_count`, `large_ticket_sum` | int, numeric | редкие крупные траты | §4.3 |
| `savings_balance`, `first_time_saver_flag` | numeric, bool | сбережения и факт первого сбережения | §4.4 (Becker) |
| `active_days`, `sessions` | int | 🔴 **только как диагностика механизма, НЕ как исход** | §4.1 (FCA) |

#### Пять инженерных требований к самому логированию

1. 🔴 **`propensity` пишется в момент решения, синхронно, в той же транзакции, что и выдача.**
   Восстановление постфактум даёт неидентифицируемое смещение (§1.3).
2. 🔴 **`propensity` считается ПОСЛЕ применения жёстких инвариантов** Rt ≥ 0 и ПДН ≤ 0,40,
   а не до. Иначе `propensity_all` не суммируется в единицу (§1.3).
3. **Лог иммутабельный, append-only.** Перезапись строки убивает воспроизводимость.
4. **Снимки исходов — с первого дня жизни пользователя,** включая период до первой рекомендации.
   Без 5 месяцев предыстории event-study невозможен (§4.3).
5. **Синтетика и обезличивание.** В логи не попадают ПДн; работа с исследовательской копией
   ведётся на псевдонимизированных `user_id` (правило §7 CLAUDE.md, 152-ФЗ).

#### Схема exploration — конкретно, что включить

- Класс: **top-k soft-greedy** (не softmax, не равномерный) — §1.2, Douglas et al. стр. 27–28.
- k инициализировать размером показываемой выдачи (k = 3, при |A| = 66), затем подбирать
  как гиперпараметр по held-out IPW-MSE на уже собранных данных.
- Доля exploration-трафика: **начать с 5–10%**, только для `eligible_for_exploration = true`.
  🔴 Ориентир взят из практики (ε-greedy у Adyen, §1.2) и из измеренной цены рандомизации
  у Bottou (§1.1: значимый сдвиг только по одной служебной метрике, ключевые — нет), а НЕ из
  публикации, называющей конкретный процент. Числа «правильной доли» в добытых источниках нет —
  подбирать по внутреннему замеру.
- Интерфейс: **не подмена топ-1, а перестановка внутри честно показанного списка сопоставимых
  альтернатив с раскрытием оценок** — единственная форма, проходящая §1.4 (equipoise + 22-МР).

---

### И2. План измерения эффекта по этапам

#### ~100 пользователей — измерить эффект НЕЛЬЗЯ. Можно только подготовиться.
Что делается:
- логирование по И1 в полном объёме, включая `propensity` (стоимость нулевая, ценность
  через год — вся);
- проверки целостности: сумма `propensity_all` = 1; доля exploration соответствует заданной;
  нет пропусков в панели снимков;
- калибровка `exploration_param` в симуляции на синтетике, не на людях;
- **предрегистрация плана анализа** (§4.3) — что будет исходом, какие подгруппы, какой тест;
- описательная статистика и наивный бейзлайн по критерию Миллера из темы 27 («user plus system
  vs unaided user»).
Чего делать нельзя: объявлять любые наблюдаемые различия эффектом. На 100 пользователях
эффект в 15% при разумной дисперсии не детектируется.

#### ~1 000 пользователей — первые честные оценки
- **SNIPS как основной оценщик** (§1.2: «often performs well empirically, particularly in
  low-data regimes, and does not require hyperparameter tuning»). IPS — рядом, для сверки.
  DR — не начинать с него (§1.2: у Adyen корреляция около нуля).
- **DiD с индивидуальными и событийно-месячными фиксированными эффектами**, SE кластеризованы
  на уровне пользователя (§4.3, спецификация Levi). Событие — раскатка новой версии
  рекомендации на одну когорту `assignment_bucket`.
- **Event-study plot** с одновременными (не поточечными) доверительными полосами (§2.1).
- Обязательный отчёт: **breakdown value M̄** по Rambachan–Roth — насколько велико должно быть
  нарушение параллельных трендов, чтобы вывод развалился (§2.1).
- Контрольная метрика: недискреционные расходы **не должны двигаться** (§4.3). Если двигаются —
  дизайн загрязнён.
- Ориентир по мощности: у Levi ≈450 наблюдений на руку хватило на эффект 15% (§4.3).
  На 1 000 пользователей и 2 руках эффект меньше ~10% ловиться не будет.

#### ~10 000 пользователей — гетерогенность и инференс
- **X-learner** (база RF на таких объёмах) для оценки τ(x) — §3.2, правило большого пальца
  Künzel et al.
- **Causal forest с honesty** для доверительных интервалов по отобранным сегментам — §3.3.
  Условие overlap (ε < P[W=1|X=x] < 1−ε) выполняется ровно за счёт exploration из И1.
- **Qini-кривая и uplift@k** для решения «кому включать активную рекомендацию» — §3.5.
- Отдельный отчёт по группам, включая финансово уязвимых, **с разбивкой по драйверам
  уязвимости**, а не агрегатом — §4.1 (FCA).
- Проверка гипотезы брекетинга: τ(x) с `viewed_full_set` / `edited_single_category`
  как ковариатами — §3.4.
- Дополнительно: RDD у floor резерва с полным чеклистом Lee–Lemieux (§2.2). RDD у ПДН 0,40
  не проводить, кроме теста McCrary как диагностики манипуляции.

---

### И3. 🔴 Что измерить НЕЛЬЗЯ — и почему

1. **Эффект на благосостояние через 10 лет.** Горизонт продукта короче горизонта исхода.
   Единственный честный ход — прокси из §4.2 и явная оговорка, что это прокси.
2. **Эффект «продукта в целом» против «жизни без продукта».** Требует рандомизации доступа
   к продукту, чего у коммерческого запуска не бывает. DiD на «поставил / не поставил» ломается
   на допущении параллельных трендов: самоотбор в момент установки коррелирован с изменением
   поведения по построению (§2.1). Это ограничение неустранимо, его надо называть в научном
   тексте, а не обходить.
3. **ATE (средний эффект по всем).** С IV получаем LATE на комплаерах; ATE «often not
   point-identified» даже при всех четырёх допущениях (§2.3, Imbens).
4. **Эффект на тех, кого мы исключили из exploration.** Финансово уязвимые пользователи
   не рандомизируются по этическим основаниям (§1.4) — значит для них τ(x) не оценивается,
   только экстраполируется. Экстраполяция должна быть помечена как экстраполяция.
5. **Ретроспективный OPE по уже накопленным логам без propensity.** Подтверждено темой 27
   и тремя источниками здесь (§1.3). Реконструкция из ε-greedy даёт неоцениваемое смещение.
6. **Эффект RDD за пределами окрестности порога.** RDD у floor резерва, если получится, скажет
   про людей у порога, а не про всех (§2.2).
7. **Synthetic control на нашей геометрии данных.** Метод требует длинной предыстории на
   единицу и малого числа единиц; у нас обратное (§2.4).
8. **«Продукт изменил человека».** Levi показал: эффект затухает за ~8 месяцев после снятия
   воздействия (§4.3). Корректная формулировка — «меняет поведение, пока присутствует».
9. **Причинный вклад отдельного компонента модели** (SAW vs Avalanche vs SES+Монте-Карло)
   без отдельной факторной рандомизации по компонентам. Один общий exploration этого
   не различает; факторный дизайн увеличивает требуемую выборку кратно (§1.1: «the more
   dimensions we randomize, the more data needs to be collected»).

---

### И4. Что не добыто. Метод поиска

#### Не добыто
1. **Abadie A. (2021), JEL 59(2):391–425 «Using Synthetic Controls».** Каналы и коды:
   `curl` economics.mit.edu (2 варианта пути) → HTML-заглушка; `curl` aeaweb.org PDF → HTML
   (пейволл); `r.jina.ai` economics.mit.edu → **HTTP 404**; `r.jina.ai` aeaweb.org →
   **1 710 байт, только аннотация**; версии на NBER нет. Требования метода взяты из
   Ben-Michael, Feller, Rothstein (arXiv:1811.04170), где Abadie цитируется дословно.
   Влияние на результат: нулевое — участок 2.4 и так закрыт отрицательным выводом.
2. **Radcliffe N. (2007) «Using control groups to target on predicted lift», Direct Marketing
   Analytics Journal — первоисточник Qini.** Вне открытого доступа, в выдаче поиска
   не обнаружен. 🔴 Определения Qini в §3.5 взяты **из сниппетов поисковой выдачи**, целиком
   не читались, помечены как непроверенные. Кандидаты на сверку найдены:
   arXiv:1911.12474, arXiv:2210.02152. Влияние: формула Qini в §3.5 требует проверки
   перед использованием в научном тексте.
3. **Точная доля exploration-трафика в продакшене** (какой процент отводят Netflix / Spotify /
   Яндекс). Публикаций с конкретным числом не найдено; у Adyen сказано «exploration traffic»
   без доли. В И1 доля 5–10% названа как **инженерный ориентир, а не как найденное число** —
   отмечено там же явно.
4. **Утверждение о неидентифицируемости выученного propensity** (§1.3, п. 3) взято из сниппета
   поисковой выдачи; первоисточник не открывался. Смысл совпадает с двумя проверенными
   источниками, но сама формулировка не верифицирована.
5. **Формулировка «correct propensity is the probability under the exact decision process after
   all rules and gating»** (§1.3) — тоже из сниппета (medium-статья), первоисточник не открывался.
   Содержательно она следует из Bottou §4.3, но как цитата не подтверждена.
6. **22-МР с сайта cbr.ru.** Угаданный прямой URL PDF дал 404; garant отдал 403 и оглавление
   без текста. Текст добыт с зеркала normativ.kontur.ru через `r.jina.ai`. 🔴 Сверку
   с официальной публикацией ЦБ **не проводил** — при использовании в юридическом тексте
   сверить обязательно.
7. **Российской практики причинной оценки эффекта финтех-продуктов** не искал отдельно
   и не нашёл попутно. Пробел признаю: все полевые эксперименты в отчёте — США и Германия.

#### Метод поиска
- **WebSearch: работал. 9 вызовов**, все вернули непустую выдачу, ни одного 429.
  Запросы: Bottou counterfactual; logging propensity exploration OPE; 22-МР ЦБ;
  ethics A/B equipoise; cbr.ru 22-МР pdf; Abadie synthetic controls pdf; Qini curve;
  FCA Consumer Duty outcomes monitoring; PFM app randomized field experiment.
- **Подагентов: 0** (как предписано).
- **Основной канал добычи — `curl` с браузерным UA + `pdftotext -layout`.** Так добыты
  целиком 9 из 11 первоисточников: Bottou (JMLR), Adyen, Douglas–Persson–Provost, Roth et al.,
  Lee–Lemieux (NBER), Imbens (NBER), Künzel et al., Wager–Athey, Ben-Michael et al.,
  Levi (JFQA), Becker (Philadelphia Fed). Ни один не потребовал приёма «WebFetch кладёт PDF
  на диск».
- **`r.jina.ai` — 3 применения, 2 успеха, 1 отказ.** Успех: normativ.kontur.ru (22-МР,
  115 957 байт), consultant.ru (152-ФЗ ст. 16, 4 309 байт), fca.org.uk (71 000 байт).
  Отказ: economics.mit.edu (404) и aeaweb.org (пейволл, 1 710 байт).
  🔴 Подтверждено ещё раз: **прокси обходит антибот, но не пейволл.**
- **`WebFetch` — 2 применения.** garant.ru: вернул только оглавление без текста.
  fca.org.uk: вернул цитаты малой моделью — **сверил `r.jina.ai`-выгрузкой, формулировки
  совпали дословно** (правило «пересказ малой моделью не доверять» выполнено).
- **Новый приём, стоит записать:** первая закачка Levi (JFQA) дала файл 2.4 МБ с битым
  xref (`Invalid XRef entry 0`, `Couldn't find trailer dictionary`). Повторная закачка
  с `--retry 2` дала целый файл 6.6 МБ. 🔴 **Битый PDF — это «перекачай», а не «недоступен».**
- **Второй приём:** `pdftotext` на Lee–Lemieux ругнулся `Invalid XRef entry 1`, но извлёк
  5 723 строки корректного текста. Предупреждение парсера — не отказ, проверять по объёму
  вывода.
- **Ограничение среды:** `timeout` в zsh отсутствует; долгие `pdftotext` на больших PDF
  уходят в фон и завершаются успешно — результат забирать следующим вызовом.

#### Замечание о полноте
Первоисточники по всем четырём участкам добыты и прочитаны целиком, кроме двух отмеченных
выше (Abadie, Radcliffe). Все формулы, пороги и допущения в отчёте — из полных текстов,
кроме явно помеченных как «из сниппета» (§1.3 — два места, §3.5 — определение Qini).


---

# ДОБОР 10.09.2026

Причина добора: при первом прогоне агенту **запрещены подагенты**, часть работы осталась
недобытой (§И4, пп. 1–7) и часть утверждений помечена как «из сниппета / не сверено».
Владелец велел довести до полноты. Подагентов разрешено не более двух, последовательно.

## План добора

| № | Что | Статус |
|---|---|---|
| Д1 | **Практика OPE** (главное для продукта): поля propensity-лога, top-k soft-greedy на практике, расчёт мощности/сколько наблюдений нужно, оценщики в проде (IPS, SNIPS, DR, SWITCH) и требования к перекрытию. Первоисточники: Dudík–Langford–Li, Swaminathan–Joachims, Su et al., Open Bandit Pipeline | готово |
| Д2 | **Контрпримеры к выводу «постфактум не чинится»**: deconfounding, deficient support, IV, RDD, proximal — при каких условиях эффект восстанавливают из нерандомизированных логов | готово |
| Д3 | **Право и этика рандомизации в финпродукте РФ**: 22-МР и 19-МР (сверка с уже добытым в `raw/`), практика A/B в регулируемых отраслях | готово |
| Д4 | Закрытие §И4: Qini-первоисточник (arXiv:1911.12474, arXiv:2210.02152), неидентифицируемость выученного propensity, Abadie (2021) — либо текст, либо честная запись статуса Unpaywall | готово |
| Д5 | **ИЗМЕНЕНИЯ ВЫВОДОВ**: подтвердилось / уточнилось / опровергнуто / осталось недобытым | готово |

Инструменты: WebSearch мог быть исчерпан («400 of 400») — замена OpenAlex / Crossref /
Unpaywall / Semantic Scholar / EuropePMC. Exa недоступна (404). `r.jina.ai` отвечает 401 —
не тратить попытки (🔴 отличие от первого прогона, где прокси работал).

---

## Д1. ПРАКТИКА OFF-POLICY EVALUATION (главный участок добора)

Первая редакция дала принципы. Здесь — детали, определяющие, что логировать ДО первого релиза.

### Д1.1 Оценщики: полный ряд и что именно требует каждый

#### Источник P. Dudík M., Langford J., Li L. «Doubly Robust Policy Evaluation and Learning». ICML 2011, arXiv:1103.4601v2 (6 мая 2011).
Добыт полностью: `curl` → PDF 174 КБ → `pdftotext -layout`, 641 строка.
URL: https://arxiv.org/abs/1103.4601 · PDF: https://arxiv.org/pdf/1103.4601

🔴 **Почему IPS на практике надёжнее DM — дословно (§2.1):**
> «If p̂(a | x, h) ≈ p(a | x, h) then the IPS estimate above will be, approximately, an unbiased
> estimate of V^π. Since we typically have a good (or even accurate) understanding of the
> data-collection policy, **it is often easier to obtain a good estimate p̂, and thus IPS estimator
> is in practice less susceptible to problems with bias compared with the direct method.** However,
> IPS typically has a much larger variance, due to the range of the random variable increasing.
> **The issue becomes more severe when p(a | x, h) gets smaller.**»

**Формула DR (уравнение 1, §2.2), дословно:**
> V̂_DR^π = (1/|S|) Σ_{(x,h,a,r_a)∈S} [ (r_a − ρ̂_a(x))·I(π(x)=a) / p̂(a|x,h) + ρ̂_{π(x)}(x) ]
> «Informally, the estimator uses ρ̂ as a baseline and if there is data available, **a correction is
> applied**. We will see that our estimator is accurate **if at least one of the estimators, ρ̂ and
> p̂, is accurate**, hence the name doubly robust.»

🔴 **Точная арифметика смещения — Теорема 1 (§3), дословно.** Вводятся два отклонения:
> ∆(a,x) = ρ̂_a(x) − ρ_a(x)   — аддитивное отклонение модели вознаграждения;
> δ(a,x,h) = 1 − p(a|x,h)/p̂(a|x,h)   — 🔴 **мультипликативное отклонение оценки propensity от истинного.**

> «**Theorem 1** Let ∆ and δ be defined as above. Then, the bias of the doubly robust estimator is
> |E_S[V̂_DR^π] − V^π| = (1/|S|)·|E_S[ Σ_{(x,h)∈S} ∆δ ]|.»
> Для стационарной политики: |E[V̂_DR^π] − V^π| = |E_x[∆δ]|.
> «In contrast <...> |E[V̂_DM^π] − V^π| = |E_x[∆]| ; **|E[V̂_IPS^π] − V^π| = |E_x[ρ_{π(x)}·δ]|**,
> where the second equality is based on the observation that **IPS is a special case of DR for
> ρ̂_a(x) ≡ 0**.»
> «In general, neither of the estimators dominates the others. However, **if either ∆ ≈ 0, or δ ≈ 0,
> the expected value of the doubly robust estimator will be close to the true value, whereas DM
> requires ∆ ≈ 0 and IPS requires δ ≈ 0.**»

🔴 **Это и есть формальное доказательство главного требования темы 37.** Смещение IPS равно
E[ρ·δ], где δ — ошибка в propensity. Пишем propensity точно в момент решения → δ ≡ 0 → смещения
нет **при любой модели вознаграждения**. Восстанавливаем propensity задним числом → δ ≠ 0 и
неизвестно, а значит смещение существует и **неизмеримо изнутри данных**. Никакой «умный оценщик»
это не лечит: δ входит и в смещение DR тоже (как произведение ∆δ).

**Теорема 2 (§4) — разложение дисперсии DR на три слагаемых, дословно:**
> Var[V̂_DR^π] = (1/|S|)( E_{x,r,a}[ε²] + Var_x[ρ_{π(x)} + ∆δ] + E_x[ ((1−p)/p)·∆²(1−δ)² ] )
> «Thus, the variance can be decomposed into three terms. The first accounts for **randomness in
> rewards**. The second term is the variance of the estimator due to the **randomness in x**. And the
> last term can be viewed as the **importance weighting penalty**.»
> Для DM: «Var[V̂_DM^π] = (1/|S|)·Var_x[ρ_{π(x)} + ∆]. Thus, **the variance of the direct method does
> not have terms depending either on the past policy or the randomness in the rewards. This fact
> usually suffices to ensure that it is significantly lower than the variance of DR or IPS.**»

🔴 **Третье слагаемое — прямое ТЗ на проектирование логирующей политики.** Штраф взвешивания
растёт как (1−p)/p: при propensity p = 0,01 множитель 99, при p = 0,2 — всего 4. Отсюда вывод
участка 1.2 (top-k, а не равномерный разброс по 66 альтернативам) получает численное обоснование:
🔴 **нижняя граница propensity — проектный параметр, а не побочный эффект.** Для |A| = 66 при
равномерном логировании p = 0,015 и штраф ≈ 65; при top-3 p = 0,33 и штраф ≈ 2. Разница в 30 раз
по третьему слагаемому дисперсии.

---

#### Источник Q. Wang Y.-X., Agarwal A., Dudík M. «Optimal and Adaptive Off-policy Evaluation in Contextual Bandits». ICML 2017, arXiv:1612.01205v2 (11 ноября 2017).
Добыт полностью: `curl` → PDF 671 КБ → `pdftotext -layout`, 1631 строка.
URL: https://arxiv.org/abs/1612.01205 · PDF: https://arxiv.org/pdf/1612.01205

Это первоисточник **switch estimator**, который в задании назван отдельно.

**Идея (§4.1), дословно:**
> «Our starting point is the observation that **insistence on maintaining unbiasedness puts the DR
> estimator at one extreme end of the bias-variance tradeoff.** <...> we derive a class of estimators
> that leverage reward models to directly address this source of high variance <...> we propose to
> estimate the rewards for actions by two distinct strategies, **based on whether they have a large
> or a small importance weight in a given context. When importance weights are small, we continue to
> use our favorite unbiased estimators, but switch to directly applying the (potentially biased)
> reward model on actions with large importance weights.** Here, "small" and "large" are defined via
> a threshold parameter τ.»

**Формула (уравнение 7), дословно:**
> v̂_SWITCH = (1/n)·Σ_i [ r_i·ρ_i·1(ρ_i ≤ τ) ] + (1/n)·Σ_i Σ_{a∈A} r̂(x_i,a)·π(a|x_i)·1(ρ(x_i,a) > τ)
> где ρ_i := π(a_i|x_i)/µ(a_i|x_i).
> «When DR is used instead of IPS, we refer to the resulting estimator as **SWITCH-DR**.»

**Границы поведения (§4.1), дословно:**
> «The proposed estimator interpolates between DM and IPS. **For τ = 0, SWITCH coincides with DM,
> while τ → ∞ yields IPS.** Consequently, SWITCH estimator is **minimax optimal when τ is
> appropriately chosen.** However, unlike IPS and DR, the SWITCH and SWITCH-DR estimators are by
> design **more robust to large (or heavy-tailed) importance weights.**»

🔴 **Клиппинг Bottou — частный случай SWITCH (§4.1, сноска-перечисление), дословно:**
> «1. Bottou et al. (2013) consider a **special case of SWITCH with r̂ ≡ 0**, meaning that all the
> actions with large importance weights are **eliminated** from IPS. We refer to this method as
> **Trimmed IPS**.»
Связка с §1.1 первой редакции: приём «R = пятое по величине наблюдённое отношение» — это выбор τ
вручную. SWITCH делает то же самое, но подставляет вместо выброшенных наблюдений модель
вознаграждения вместо нуля, и выбирает τ автоматически.

🔴 **Автоматический подбор τ (§4.2) — процедура, переносимая к нам целиком, дословно:**
> «A natural criterion would be to pick τ that minimizes the MSE of the resulting estimator. Since we
> do not know the precise MSE (as v^π is unknown), an alternative is to **minimize its data-dependent
> estimate.** Recalling that the MSE can be written as the sum of variance and squared bias, we
> estimate and bound the terms individually.»
> Y_i(τ) := r_i·ρ_i·1(ρ_i ≤ τ) + Σ_a r̂(x_i,a)·π(a|x_i)·1(ρ(x_i,a) > τ);  V̂ar_τ := (1/n)Σ(Y_i(τ) − Ȳ(τ))²
> Bias²_τ := ( (1/n)·Σ_i E_π[ R_max·1(ρ > τ) | x_i ] )²
> «**τ̂ := argmin_τ ( V̂ar_τ + B̂ias²_τ )**   (9)»
> «Our upper bound on the bias is rather **conservative** <...> This has the effect of **favoring the
> use of the unbiased part in SWITCH whenever possible**, unless the variance would overwhelm even an
> arbitrarily biased DM.»
> Про MAGIC (Thomas & Brunskill 2016): «we pick only one threshold τ, while they combine the
> estimates with many different τs using a weighting function <...> **In our experiments, the
> automatic tuning using Eq. (9) generally works better than MAGIC.**»

---

#### Источник R. Su Y., Dimakopoulou M., Krishnamurthy A., Dudík M. «Doubly robust off-policy evaluation with shrinkage». ICML 2020, arXiv:1907.09623v2 (18 сентября 2020).
Добыт полностью: `curl` → PDF 14 МБ → `pdftotext -layout`, 2084 строки.
URL: https://arxiv.org/abs/1907.09623 · PDF: https://arxiv.org/pdf/1907.09623

Это «Su et al.», названный в задании. Даёт **DRos** — оценщик, который в бенчмарке на реальных
продовых данных (источник S ниже) обошёл всех остальных.

**Постановка проблемы (Abstract + §1), дословно:**
> «Our approach is based on the asymptotically optimal doubly robust estimator, but we **shrink the
> importance weights to minimize a bound on the mean squared error**, which results in a better
> bias-variance tradeoff in finite samples.»
> «[DR] is unbiased, and it is asymptotically optimal under weaker assumptions than other methods
> (Rothe, 2016). However, **its finite-sample variance can still be quite high when importance
> weights (also known as inverse propensity scores) are large.** <...> These works motivate weight
> shrinkage as a heuristic for trading off bias and variance, **but they do not provide insight into
> when and how these different methods should be used.**»

🔴 **Ядро метода — формула сжатия веса (§3.1), дословно:**
> ŵ_{o,λ}(x,a) = λ / ( w²(x,a) + λ ) · w(x,a)
> «where "o" above is a mnemonic for **optimistic shrinkage**. We refer to the DRs estimator with
> ŵ = ŵ_{o,λ} as the **doubly robust estimator with optimistic shrinkage (DRos)** <...>
> **When λ = 0, we have ŵ(x,a) = 0 corresponding to DM. As λ → ∞, the weights increase and in the
> limit become equal to w(x,a), corresponding to standard DR.**»

То есть DRos — непрерывная шкала между DM и DR по одному числу λ, тогда как SWITCH — та же шкала,
но по порогу τ и с разрывом. Обе сводятся к одной мысли: **большие веса — признак того, что
логирующая политика не покрыла нужную область, и там честнее верить модели, чем весам.**

🔴 **Процедура выбора гиперпараметра (§5 Model Selection), дословно — это то, что реально
запускается в проде:**
> «Let V̂_θ denote the estimator parameterized by θ. We consider the procedure that estimates the
> variance of V̂_θ by sample variance V̂ar(θ), and bounds the bias of V̂_θ by a data-dependent upper
> bound BiasUB(θ). The only requirement is that for all θ, Bias(θ) ≤ BiasUB(θ) (with high
> probability), and that **BiasUB(θ) = 0 whenever Bias(θ) = 0** <...>
> **θ̂ ← Minimize_{θ∈Θ} [ BiasUB(θ)² + V̂ar(θ) ]**»
> «**Theorem 3.** <...> there exists a universal constant C such that with probability at least 1−δ
> we have **MSE(θ̂) ≤ min_{θ′∈Θ₀} MSE(θ′) + C·log(|Θ|/δ)/n^{3/2}**», где Θ₀ — подмножество
> несмещённых оценщиков.
Читать так: **процедура выбора оценщика по данным не хуже лучшего несмещённого из списка** с
точностью до члена порядка n^{-3/2}. Значит выбирать оценщик руками не надо — надо прогонять
весь список и брать минимум оценённой MSE. Это снимает вопрос «какой оценщик взять» с повестки
проектирования и переносит его в код анализа.

---

### Д1.2 🔴 Сколько наблюдений нужно и какой оценщик побеждает — на РЕАЛЬНЫХ продовых данных

#### Источник S. Saito Y., Aihara S., Matsutani M., Narita Y. «Open Bandit Dataset and Pipeline: Towards Realistic and Reproducible Off-Policy Evaluation». arXiv:2008.07146 (NeurIPS 2021 Datasets and Benchmarks).
Добыт полностью: `curl` → PDF 1.6 МБ → `pdftotext -layout`, 1589 строк.
URL: https://arxiv.org/abs/2008.07146 · PDF: https://arxiv.org/pdf/2008.07146
Это и есть «библиотека Open Bandit Pipeline и её статья» из задания.

🔴 **Главное: это единственный публичный датасет, где логирующая политика РАНДОМИЗИРОВАНА
в проде и propensity записан. Замер цены рандомизации — настоящий, не оценочный.**

**Таблица 1 «Statistics of Open Bandit Dataset», дословные числа:**

| Кампания | Политика сбора | #Data | #Items | #Dim | CTR ±95% ДИ | Relative-CTR |
|---|---|---|---|---|---|---|
| ALL | Random | 1 374 327 | 80 | 84 | 0,35% ±0,010 | 1,00 |
| ALL | Bernoulli TS | 12 168 084 | 80 | 84 | 0,50% ±0,004 | 1,43 |
| Men's | Random | 452 949 | 34 | 38 | 0,51% ±0,021 | 1,48 |
| Men's | Bernoulli TS | 4 077 727 | 34 | 38 | 0,67% ±0,008 | 1,94 |
| Women's | Random | 864 585 | 46 | 50 | 0,48% ±0,014 | 1,39 |
| Women's | Bernoulli TS | 7 765 497 | 46 | 50 | 0,64% ±0,056 | 1,84 |

🔴 **ЦЕНА РАНДОМИЗАЦИИ, ИЗМЕРЕННАЯ: 0,35% против 0,50% CTR на кампании ALL — равномерно
случайная политика теряет 30% отклика относительно рабочей** (Relative-CTR 1,00 против 1,43).
Первая редакция писала «числа правильной доли в добытых источниках нет». Теперь число есть,
но это цена ПОЛНОСТЬЮ равномерной рандомизации, и она — верхняя оценка. Именно поэтому
top-k soft-greedy (§1.2, Douglas et al.) экономически осмыслен: он платит долю этой цены.

**Доля exploration-трафика — тоже измерима из таблицы:** 1 374 327 / (1 374 327 + 12 168 084)
= **10,1% трафика ZOZOTOWN отдано под равномерно случайную политику в течение 7 дней.**
🔴 Это первое найденное ЧИСЛО реальной доли exploration в проде — закрывает пробел §И4 п. 3
первой редакции («точная доля exploration-трафика в продакшене не найдена»). Ориентир И1
«начать с 5–10%» подтверждён независимо.

**Как устроен сбор (§4, дословно):**
> «We collected the data in a 7-day experiment in late November 2019 on three "campaigns" <...>
> **Each campaign randomly uses either the Random policy or the Bernoulli TS policy for each user
> impression.** These policies select three of the candidate fashion items for each user.»
🔴 Рандомизация **на уровне показа, а не пользователя**, и выбирается не действие, а ПОЛИТИКА.
Для нас это готовая схема: бросок монеты «детерминированный SAW-топ или top-k soft-greedy»
на каждую выдачу, и запись, какая политика сработала (поле `policy_id` из И1 — уже заложено).

🔴 **Приём, которого не было в первой редакции: как считать propensity, когда у политики нет
формулы (сноска 4, стр. 4), дословно:**
> «It also includes **the probability that item a is displayed at each position by the data
> collection policies.** This probability is used to calculate the importance weights.⁴»
> «⁴ We computed the action choice probabilities by **Monte Carlo simulations based on the policy
> parameters** (e.g., parameters of the beta distribution used by Bernoulli TS) used during the data
> collection process.»
Перенос на FINPILOT: если логирующая политика сложна (инварианты Rt ≥ 0 и ПДН ≤ 0,40 режут
множество, потом top-k по SAW), закрытой формулы propensity может не быть. Решение — **прогнать
сам механизм выбора N раз на зафиксированном контексте (Монте-Карло) и записать эмпирическую
частоту как propensity.** Требование к архитектуре: механизм выбора должен быть чистой
детерминированной функцией от (контекст, seed), чтобы его можно было переиграть. Это
проверяемое инженерное условие, и его надо заложить сейчас.
Оговорка честно: Монте-Карло даёт **оценку** propensity, то есть δ ≠ 0 по Теореме 1 источника P,
но δ при этом контролируемо мал (можно гонять сколько угодно итераций) и, главное, ИЗВЕСТЕН —
в отличие от реконструкции задним числом.

**Протокол оценки самих оценщиков (§5.1), дословно:**
> «We can empirically evaluate OPE estimators' performance by using **two sources of logged bandit
> data collected by running two different policies.** In the protocol, we regard one policy as
> behavior policy π_b and the other as evaluation policy π_e.»
> SE(V̂; D^(b)) := ( V̂(π_e; D^(b)) − V_on(π_e) )², где V_on — Монте-Карло-оценка по данным π_e.
> RMSE считается бутстрепом: «**200 different bootstrapped iterations**».
🔴 Это готовый рецепт нашей внутренней валидации: держать в проде ДВЕ политики, оценивать вторую
по логам первой и сверять с прямым наблюдением второй. Ровно то, что Bottou делал на Bing
(§1.1: «a second traffic bucket of equal size») — независимое подтверждение приёма.

🔴 **Результаты бенчмарка — таблица 4, n = 300 000, RMSE ×10³ (Bernoulli TS → Random):**

| Оценщик | ALL | Men's | Women's |
|---|---|---|---|
| IPW | 0,493 | 0,789 | 0,776 |
| SNIPW | 0,507 | 0,644 | 0,804 |
| DM | 1,026 | 0,773 | 0,816 |
| DR | 0,482 | 0,613 | 0,803 |
| SNDR | 0,482 | 0,659 | 0,791 |
| Switch-DR | 0,482 | 0,613 | 0,803 |
| **DRos** | **0,316** | **0,459** | **0,561** |

> «Table 4 shows that **DRos (with automatic hyperparameter tuning) performs best for the three
> campaigns, achieving about 30–60% more accurate OPE than the second-best estimators.**»

🔴 **Таблица 6 — и вот это прямо меняет вывод первой редакции. RMSE ×10³, малая выборка
n = 10 000 против большой n = 300 000:**

| Оценщик | ALL малая | ALL большая | Men's малая | Men's большая | Women's малая | Women's большая |
|---|---|---|---|---|---|---|
| IPW | 1,899 | 0,493 | 3,683 | 0,789 | 3,156 | 0,776 |
| SNIPW | 1,641 | 0,507 | 3,661 | 0,644 | 3,038 | 0,804 |
| **DM** | **0,797** | 1,026 | **3,041** | 0,773 | **2,665** | 0,816 |
| DR | 1,203 | 0,482 | 3,747 | 0,613 | 3,055 | 0,803 |
| SNDR | 1,159 | 0,482 | 3,757 | 0,659 | 3,069 | 0,791 |
| Switch-DR | 1,203 | 0,482 | 3,747 | 0,613 | 3,055 | 0,803 |
| DRos | 0,765 | **0,316** | 3,727 | **0,459** | 3,051 | **0,561** |

> «We observe in Table 6 that the estimators' performance **can change significantly depending on the
> size of the logged bandit data.** In particular, for the Men's and Women's campaigns, **the most
> accurate estimator changes with the sample size. The table shows that DM outperforms the other
> estimators in the small-sample setting, while DRos is the best for the large-sample setting.**
> These observations suggest that **practitioners have to choose an appropriate OPE estimator
> carefully for their specific application.**»

🔴 **ПРОТИВОРЕЧИЕ С ПЕРВОЙ РЕДАКЦИЕЙ, называю прямо.** §И2 («~1 000 пользователей») предписывал
**SNIPS как основной оценщик на малых данных** — на основании одной фразы из отчёта Adyen
(«particularly in low-data regimes»). Бенчмарк на реальных продовых данных ZOZO даёт обратное:
при n = 10 000 SNIPW проигрывает **DM** во всех трёх кампаниях (1,641 против 0,797; 3,661 против
3,041; 3,038 против 2,665), то есть смещённая регрессия на малой выборке точнее самонормированного
IPS. Причина видна из Теоремы 2 источника P: на малых n дисперсия давит сильнее смещения,
а у DM дисперсия не содержит ни члена логирующей политики, ни шума вознаграждений.
**Как разрешать:** ни та, ни другая рекомендация не универсальна — надо считать ВСЕ оценщики
и выбирать процедурой Su et al. (§5 источника R, `BiasUB² + V̂ar` → min). Именно так и сделано
в OBP. Вывод для И2 переформулировать: не «SNIPS основной», а **«на 1 000 наблюдений считать
весь ряд (DM, IPW, SNIPW, DR, SNDR, SWITCH-DR, DRos) и выбирать по оценённой MSE; заранее
ожидать, что победит DM или DRos, а не SNIPS»**.

**Ограничение самого бенчмарка, честно (§6), дословно:**
> «Open Bandit Dataset is currently the only public dataset allowing OPE experiments. Therefore,
> **it might lead to an overfitting issue.** Moreover, Open Bandit Dataset **includes only two
> policies.**» И допущение: «we assume that the reward of an item at a position **does not depend on
> other simultaneously presented items.** This assumption might not hold.»
🔴 Последнее прямо про нас: мы показываем **список** альтернатив, и оценка одной зависит от
соседних по списку (эффект контраста, тема 36 брекетинг). Значит стандартные оценщики у нас
работают на уровне «какая альтернатива предвыбрана», а не «какой список показан». Для списка
нужны slate-оценщики (в OBP они реализованы: «we have implemented some OPE estimators for the
**slate action setting** [29, 43]»). Записать как ограничение.

**Чувствительность DRos к λ — таблица 5 (ALL, n = 300 000), RMSE ×10³:**
λ=1 → 0,963; λ=10 → 0,770; λ=100 → 0,498; λ=1 000 → **0,245** (лучшее для Bernoulli TS → Random);
λ=10 000 → 0,323; автоподбор → 0,323.
> «First, we observe that **the choice of λ greatly affects the performance of DRos.** <...> Second,
> we observe that the automatic hyperparameter tuning procedure prefers a large value of λ. This
> means that the tuning procedure **puts emphasis on the bias of the estimator** <...> **there is room
> for improvement for Bernoulli TS → Random in terms of automatic hyperparameter tuning.**»
🔴 Отрезвляющее: автоподбор проиграл ручному λ = 1 000 в 1,3 раза (0,323 против 0,245).
Значит гиперпараметр всё равно смотреть глазами, а не доверять процедуре вслепую.

---

### Д1.3 Перекрытие (overlap / positivity): формальное требование и его цена

#### Источник T. Sachdeva N., Su Y., Joachims T. «Off-policy Bandits with Deficient Support». KDD 2020, arXiv:2006.09438.
Добыт полностью: `curl` → PDF → `pdftotext -layout`, 895 строк.
URL: https://arxiv.org/abs/2006.09438 · PDF: https://arxiv.org/pdf/2006.09438

Это первоисточник по требованию перекрытия, названному в задании (overlap/positivity).

**Определение 1 (полное перекрытие), дословно:**
> «**Definition 1 (Full support).** The logging policy π₀ is said to have **full support** for π when
> π₀(y|x) > 0 for all actions y ∈ Y and contexts x ∈ X for which π(y|x) > 0.»
> «It is known that the IPS estimator is unbiased, E_D[R̂_IPS(π)] = R(π), **if the logging policy π₀
> has full support for π.**»

🔴 **Почему это тяжелее, чем кажется (§2), дословно:**
> «For sufficiently rich policy spaces, like deep-networks <...> this means that the logging policy π₀
> needs to assign **non-zero probability to every action y in every context x. This is a strong
> condition that is not feasible in many real-world systems, especially if the action space is large
> and many actions have poor reward.**»

🔴 **Диагноз причины провала — это СМЕЩЕНИЕ, а не дисперсия (§2), дословно:**
> «If the support requirement is violated, ERM learning **can fail catastrophically.** We will show in
> the following that the underlying reason is **bias, not excessive variance that could be remedied
> through clipping or variance regularization.**»
Это прямо закрывает соблазн «а мы просто поклипуем веса и всё будет нормально». Клиппинг лечит
дисперсию; дырку в перекрытии он не лечит **в принципе**.

**Мера дефицита — множество неподдержанных действий и Propositon 1, дословно:**
> U(x, π₀) := { y ∈ Y | π₀(y|x) = 0 }
> «**Proposition 1.** <...> the bias of R̂_IPS for target policy π(Y|x) is equal to the expected
> reward on the unsupported action sets, i.e.
> **bias(R̂_IPS(π)) = E_x[ − Σ_{y∈U(x,π₀)} π(y|x)·δ(x,y) ]**.»

🔴 **Теорема 1 — цена дефицита в единицах вознаграждения, дословно:**
> «<...> there exists a reward distribution P_r with support in [r_min, r_max] such that **in the limit
> of infinite training data**, ERM using IPS over the logged data can select a policy π̂ that is at
> least **(r_max − r_min)·max_{π∈Π} D_X(π|π₀)** suboptimal.»
> Иллюстрация авторов дословно: «consider a problem with rewards r ∈ [−1, 0] <...> a good policy π_g
> with R(π_g) = −0.1 and a bad policy π_b with R(π_b) = −0.7. **If policy π_b has support divergence
> D_X(π_b|π₀) = 0.6 or larger, then ERM may return the bad π_b instead of the good π_g even with
> infinite amounts of training data.**»

🔴 **«Даже при бесконечных данных» — вот главная фраза всего добора.** Дефицит перекрытия
не лечится объёмом. Ни год ожидания, ни 100 000 пользователей не исправят политику, которая
никогда не показывала часть альтернатив. Это и есть точный технический смысл утверждения
«постфактум не чинится».

**И ещё одна ловушка (§4.1), дословно:**
> «Note that it is **sufficient to merely have ONE policy in Π that has large support deficiency** to
> achieve this suboptimality.»

**Три стратегии, когда перекрытие уже дефицитно (§3), и что победило эмпирически:**
1. **Ограничение пространства действий** (запретить неподдержанные действия): «the Action
   Restriction approach also performs poorly. While its support divergence D_X(π|π₀) is zero and
   thus bias is not the problem, we conjecture that **the best actions are often pruned** from the
   action-restricted policy space.»
2. **Экстраполяция вознаграждения** (консервативная — подставить r_min; регрессионная — подставить
   предсказание модели): «Regression Extrapolation tends to perform better than Conservative
   Extrapolation in our experiments.»
3. **Ограничение пространства ПОЛИТИК** (разрешать только политики, близкие к логирующей):
   «the methods that perform well on both datasets are **Policy Restriction and DR**.»
> Вывод авторов (§6), дословно: «We conclude that **restricting the policy space is particularly
> effective, since it provides explicit risk control, performs well in terms of learning performance,
> and it is easy and efficient to implement.**»
> Практическая приписка (§3.3): «the Policy Restriction approach is easy to implement, **does not
> require an additional regression model with unknown bias, and it does not require access to the
> logging policy during training or testing.**»

🔴 **Прямой перенос на FINPILOT.** У нас 66 альтернатив. Полное перекрытие означало бы ненулевую
вероятность каждой из 66 в каждом контексте — это несовместимо ни с этикой (§1.4), ни с
инвариантами Rt ≥ 0 и ПДН ≤ 0,40, которые режут часть множества жёстко. Значит **дефицит
перекрытия у нас есть по построению, и его надо не отрицать, а измерять.**
Требование к логам, которого в И1 не было: **писать в каждую строку `support_divergence` —
долю вероятностной массы целевой политики, пришедшуюся на действия с нулевым propensity.**
И принять как проектное решение: оценивать только политики из ограниченного класса — близкие
к логирующей (Policy Restriction), а не произвольные.

---

### Д1.4 Диагностика лога, которую можно поставить в CI

#### Источник U. Swaminathan A., Joachims T. «The Self-Normalized Estimator for Counterfactual Learning». NIPS 2015.
Добыт полностью: `curl` proceedings.neurips.cc → PDF → `pdftotext -layout`, 563 строки.
URL: https://proceedings.neurips.cc/paper_files/paper/2015/file/39027dfad5138c9ca0c474d71db915c3-Paper.pdf
Это первоисточник SNIPS, названный в задании как «Swaminathan & Joachims».

🔴 **Propensity Overfitting — отказ, о котором первая редакция не знала вовсе (§4), дословно:**
> «this risk estimator is **not equivariant**. <...> Intuitively, this type of overfitting occurs since
> the risk estimate <...> can be minimized not only by putting large probability mass h(y|x) on the
> examples with low loss δ(x,y), but **by maximizing (for negative losses) or minimizing (for positive
> losses) the sum of the weights** Ŝ(h) = (1/n)·Σ_i h(y_i|x_i)/p_i.   (4)
> For this reason, we call this type of overfitting **Propensity Overfitting**. This is in stark
> contrast to overfitting in supervised learning, which we call **Loss Overfitting**.»
> Разрушительность на примере 1: «R̂(h_overfit) ≤ (1/n)·Σ(−1)·(1/(1/k)) = **−k**. Clearly this risk
> estimate shows severe overfitting, since it can be **arbitrarily lower than the true risk
> R(h*) = −2** <...> **ERM will, hence, almost always select h_overfit over h\*.**»
> И: «this type of overfitting behavior is **not an artifact of this example.** Section 7 shows that
> **this is ubiquitous in all the datasets we explored.**»

🔴 **ГОТОВАЯ ПРОВЕРКА ЛОГА, бесплатная и однострочная (§5, формула 5), дословно:**
> «Note that for any h ∈ H, the sum of propensity weights Ŝ(h) from Equation (4) **always has
> expected value 1** under the conditions required for the unbiased estimator <...>
> E[Ŝ(h)] = (1/n)·Σ_i ∫ (h(y_i|x_i)/h₀(y_i|x_i))·h₀(y_i|x_i)·Pr(x_i) dy_i dx_i = 1.   (5)
> This means that we can **identify hypotheses that suffer from Propensity Overfitting based on how
> far Ŝ(h) deviates from its expected value of 1.** <...> **a large deviation in Ŝ(h) suggests a large
> deviation in R̂(h) and consequently a bad risk estimate.**»

🔴 **В ТЗ FINPILOT это ставится как автоматический гейт:** среднее значение импортанс-веса
по выборке должно быть близко к 1. Ушло далеко от 1 — оценка недостоверна, и это видно
БЕЗ знания истины. Дополняет проверки И1 («сумма `propensity_all` = 1»), но проверяет другое:
там — корректность записи в момент решения, здесь — пригодность выборки для оценки конкретной
целевой политики. Обе проверки дешёвые, обе надо ставить в регламент анализа.

**Формула SNIPS (уравнение 7) и её свойства, дословно:**
> R̂^SN(h) = [ Σ_i δ_i·h(y_i|x_i)/p_i ] / [ Σ_i h(y_i|x_i)/p_i ]
> «Observe that the estimate is **just a convex combination of the δ_i observed in the sample.** <...>
> Hence R̂^SN(h) is **equivariant**, unlike R̂(h). Moreover, R̂^SN(h) is **always bounded within the
> range of δ.**»
> «while the self-normalized risk estimator **is not unbiased** <...> it is **strongly consistent**
> and approaches the desired expectation when n is large.»
> «**Theorem 2.** Let D be drawn i.i.d. from a h₀ that **has full support over Y**. Then ∀h ∈ H:
> Pr( lim_{n→∞} R̂^SN(h) = R(h) ) = 1.»
🔴 Обратить внимание: состоятельность SNIPS доказана **при условии полного перекрытия**. То есть
SNIPS лечит тяжёлые хвосты и неэквивариантность, но НЕ лечит дефицит перекрытия (источник T).
Две разные болезни, и путать их нельзя.

---

## Д2. КОНТРПРИМЕРЫ: когда эффект ВОССТАНАВЛИВАЮТ из нерандомизированных логов

Задание требовало проверить вывод «логирование с рандомизацией надо заложить сейчас, постфактум
не чинится» на контрпримеры, и прямо сказано: опровержения ценнее подтверждений. Контрпримеры
нашлись, и один из них — сильный. Ниже честный разбор с условиями применимости.

### Д2.1 🔴 Сильный контрпример: обучение из логов, где рандомизации НЕ БЫЛО ВООБЩЕ

#### Источник V. Strehl A., Langford J., Li L., Kakade S. «Learning from Logged Implicit Exploration Data». NIPS 2010, arXiv:1003.0120v2 (14 июня 2010).
Добыт полностью: `curl` → PDF → `pdftotext -layout`, 529 строк.
URL: https://arxiv.org/abs/1003.0120 · PDF: https://arxiv.org/pdf/1003.0120

**Заявка, дословно (Abstract):**
> «We provide a sound and consistent foundation for the use of **nonrandom exploration data** <...>
> The primary challenge <...> is that **the exploration policy, in which "offline" data is logged, is
> not explicitly known.** Prior solutions here require either control of the actions during the
> learning process, recorded random exploration, or actions chosen obliviously in a repeated manner.
> **The techniques reported here lift these restrictions, allowing the learning of a policy for
> choosing actions given features from historical data where NO RANDOMIZATION OCCURRED OR WAS
> LOGGED.**»

🔴 **Это прямое опровержение категорической формулировки «без рандомизации нельзя».** Разбираю
механизм и условия — потому что именно в условиях вся суть.

**Механизм (§1), дословно:**
> «The essential observation is that a policy which **deterministically chooses action a on day 1 and
> then deterministically chooses action b on day 2 can be treated as randomizing between actions a
> and b with probability 0.5** when the number of events is the same each day, and the events are
> IID. Thus π̂(a|x) is an estimate of **the expected frequency with which action a would be displayed
> given features x over the timespan of the logged events.**»
> И формально (§3, перед Теоремой 3.1): «The logging policy π_t may be deterministic <...> We show
> next that this is ok **when the world is IID and the policy varies over its actions. We effectively
> substitute the standard approach of randomization in the algorithm for randomization in the
> world.**»

**Оценщик (формула 2) и роль порога τ, дословно:**
> V̂^h_π̂(S) = (1/|S|)·Σ_{(x,a,r)∈S} [ r_a·I(h(x)=a) / **max{π̂(a|x), τ}** ]
> «The purpose of τ is to **upper bound the individual terms** in the sum <...> The parameter τ may
> appear mysterious at first, but is **critical for numeric stability.**»

**Теорема 3.1, дословно:**
> «For any contextual bandit problem D with **identical draws over T rounds**, for any sequence of
> possibly stochastic policies π_t(a|x) with π derived as above [π(a|x) = E_{t∼UNIF(1..T)}[π_t(a|x)]],
> and for any predictor π̂:
> E_{S∼(D,π_t)}[ V̂^h_π̂(S) ] = E_{(x,r)∼D, a∼π(·|x)}[ r_a·I(h(x)=a) / max{π̂(a|x), τ} ].»

🔴 **УСЛОВИЯ, при которых контрпример работает — выписываю все пять, потому что именно они
определяют, применим ли он к FINPILOT:**
1. **Мир i.i.d. и «identical draws»** — распределение контекстов не меняется во времени.
2. **Логирующая политика ДОЛЖНА МЕНЯТЬСЯ во времени** («the policy varies over its actions»).
   Неизменная детерминированная политика не даёт ничего: если система всегда показывает топ-1 SAW,
   частота показа альтернативы №2 равна нулю, и восстанавливать нечего.
3. **Политики π_t не зависят от данных, на которых идёт оценка** — дословно: «we have assumed that
   they do not depend on the data used for evaluation. **Allowing for the offline evaluation of
   policies using the same data they are trained on is an important open problem.**»
4. **Смещение от порога τ существует и направлено**: «actions which are displayed with low frequency
   conditioned on x effectively have an **underestimated value**. This is exactly as expected for the
   limit where actions have no frequency.» То есть редко показываемые альтернативы систематически
   недооцениваются — метод консервативен, но не беспристрастен.
5. **Точность π̂ должна расти при малом τ**: «For very small values of τ, the estimates of π̂(a|x)
   **must be extremely accurate** to yield good performance while for larger values of τ less accuracy
   is required.»

🔴 **ВЕРДИКТ ДЛЯ FINPILOT.** Контрпример реален и подтверждён на данных рекламной компании,
но для нас он **условно применим и только как запасной путь**:
- условие 2 выполнится у нас автоматически — модель версионируется, веса SAW и риск-профили
  меняются между релизами, и разные версии показывают разное. Это и есть «randomization in the
  world». 🔴 Требование к логам: `policy_version` и `model_config_hash` (уже заложены в И1!) —
  оказывается, именно они делают этот запасной путь возможным. Их ценность выше, чем считалось;
- условие 1 (i.i.d. мир) у нас **нарушается**: состав пользователей меняется по мере роста
  продукта, макроэкономика меняется (ключевая ставка, инфляция), сезонность расходов. Значит
  «частота показа за период» смешивает изменение политики с изменением популяции;
- условие 4 означает, что редкие альтернативы будут недооценены — а у нас именно редкие
  (агрессивные стратегии погашения) и интересны.
**Итого: вывод первой редакции ослабляется, но не отменяется.** Правильная формулировка:
«без записанного propensity оценка ВОЗМОЖНА, если политика менялась во времени, мир стационарен,
и вы готовы к консервативному смещению не поддающемуся оценке; с записанным propensity оценка
несмещена по построению и стоит ноль». Разница — не «можно/нельзя», а «дёшево и точно» против
«дорого, с оговорками и только задним числом».

### Д2.2 🔴 Контрпример в ДРУГУЮ сторону: рандомизации МАЛО

#### Источник W. Bareinboim E., Forney A., Pearl J. «Bandits with Unobserved Confounders: A Causal Approach». NIPS 2015.
Добыт полностью: `curl` proceedings.neurips.cc → PDF → `pdftotext -layout`, 500 строк.
URL: https://proceedings.neurips.cc/paper_files/paper/2015/file/795c7a7a5ec6b460ec00c5841019b9e9-Paper.pdf

Пример «жадного казино» (§2) — две «однорукие машины» M1 и M2, скрытые конфаундеры: опьянение
игрока D и мигание автомата B, естественный выбор X = D ⊕ B. Выплаты подобраны так, что:
> Таблица 1b, дословные числа: **P(y|X=M1) = 0,15 и P(y|X=M2) = 0,15** (наблюдательное);
> **P(y|do(X=M1)) = 0,30 и P(y|do(X=M2)) = 0,30** (экспериментальное).
> «the casino is at the same time (1) exploiting the natural predilections of the gamblers' arm
> choices <...> (2) paying, on average, **less than the legally allowed (15% instead of 30%)**, and
> (3) **fooling state's inspectors since the randomized trial payout meets the 30% legal
> requirement.**»
> «the probability of choosing the correct action is **no better than a random coin flip** even after
> a considerable number of steps <...> cumulative regret **shows no signs of abating**» — и это для
> ε-greedy, Thompson Sampling, UCB1, EXP3 одинаково.

🔴 **Смысл: рандомизированный эксперимент даёт P(y|do(X)) — среднее по популяции — и этого
недостаточно, когда оптимальное действие зависит от ненаблюдаемого состояния, которое
проявляется в СОБСТВЕННОМ намерении пользователя.** Оба «рычага» в эксперименте выглядят
одинаково (0,30 против 0,30), при том что правильная персональная политика даёт больше.

**Решение авторов — RDC, критерий сожаления (§3), дословно:**
> «instead of using a decision rule comparing the average payouts across arms, namely
> argmax_a E(Y|do(X=a)), which was shown <...> to be insufficient <...> we should consider the rule
> using the comparison between the average payouts obtained by players **for choosing in favour or
> against their intuition**, respectively: **argmax_a E(Y_{X=a} = 1 | X = x)**,   (3)
> where **x is the player's natural predilection** and a is their final decision.»
> «**Remarkably, RDC accounts for the agent's individuality and the fact that their natural
> inclination encodes valuable information about the confounders that also affect the payout.**»
> Это ETT — «effect of the treatment on the treated».

🔴 **Как это реализуется — и это ПРЯМОЕ ТРЕБОВАНИЕ К ПРОДУКТУ, которого в И1 нет (§3), дословно:**
> «ETT will be computed in an alternative fashion, based on the idea of **intention-specific
> randomization. The main idea is to randomize intention-specific groups, namely, INTERRUPT ANY
> REASONING AGENT BEFORE THEY EXECUTE THEIR CHOICE, TREAT THIS CHOICE AS INTENTION, DELIBERATE, AND
> THEN ACT.**»

🔴 **Перенос на FINPILOT, самая продуктовая находка добора.** Надо логировать **намерение
пользователя ДО показа рекомендации** — что он собирался сделать со свободным потоком сам.
Технически: перед выдачей спросить/зафиксировать предполагаемое распределение (или взять
распределение прошлого месяца как естественный выбор) и записать его как отдельное поле.
Тогда:
- появляется контраст «пошёл по рекомендации / пошёл против неё» — это и есть ETT,
  и это ровно тот вопрос, который интересен владельцу: **помогает ли система тому,
  кто без неё сделал бы иначе**;
- закрывается дыра, которую не закрывает никакая рандомизация: ненаблюдаемое состояние
  пользователя (тревога о долге, планируемая крупная покупка) проявляется в его намерении;
- это ДЕШЕВО и НЕВОССТАНОВИМО постфактум — новое поле, ровно класс «заложить до релиза».
Оговорка честно: пример казино — синтетический, с идеальными сенсорами и бинарными переменными;
перенос на непрерывное распределение 66 альтернатив авторы не делают. Но само требование
«записывать намерение до вмешательства» от этого не слабеет — оно из другого, более старого
слоя (ETT у Pearl).

### Д2.3 Проксимальная причинность: обход конфаундинга без рандомизации, цена — две прокси-переменные

#### Источник X. Tchetgen Tchetgen E. J., Ying A., Cui Y., Shi X., Miao W. «An Introduction to Proximal Causal Learning». arXiv:2009.10982 (журнальная версия — Statistical Science).
Добыт полностью: `curl` → PDF → `pdftotext -layout`, 1434 строки.
URL: https://arxiv.org/abs/2009.10982

Идея: если обмениваемости (unconfoundedness) при наблюдаемых ковариатах нет, но измеренные
ковариаты можно разбить на **прокси** двух типов — «негативный контроль экспозиции» Z и
«негативный контроль исхода» W — эффект идентифицируем через **bridge function**.

**Ключевая оговорка авторов (Remark 1), дословно:**
> «covariates measured in an observational study in an effort to control for confounding, **may not be
> sufficient to fulfil exchangeability, but nevertheless can potentially be partitioned into proxies
> satisfying negative control conditions** (10) and (11). This observation, therefore alleviates the
> need to supplement one's observational study design by collecting additional data on potential
> negative control variables.»

🔴 **Почему это НЕ спасательный круг (Remark 3), дословно:**
> «similar to exchangeability condition (4), **Assumptions (10) and (11) are NOT EMPIRICALLY TESTABLE**
> as they presume certain null causal effects and involve conditional independence statements given
> the unmeasured variable U.»
Плюс требуется **completeness condition** — и авторы сами отмечают, что она «is not subject to an
empirical test», хотя в одном из вариантов её заменяют проверяемым аналогом.

**Вердикт для FINPILOT:** метод существует и математически честен, но переносит бремя с
«рандомизируй» на «обоснуй две непроверяемые гипотезы о прокси». Для научного текста ВКР/статьи
это законная ссылка («мы знаем про проксимальный подход и объясняем, почему не применяем»);
для продуктового решения — нет. Отдельная зацепка на будущее (Remark 2): «**even an invalid
instrumental variable** which fails to satisfy the IV independence assumption may also be included
in bucket type b» — то есть отвергнутые в §2.3 кандидаты в инструменты (push-уведомление)
не пропадают совсем, они могут работать как прокси. Как гипотеза, не как план.

### Д2.4 Свод по Д2: опровергнут ли исходный вывод

| Контрпример | Что именно опровергает | Условия, без которых не работает | Годится ли нам |
|---|---|---|---|
| Strehl et al. 2010 (implicit exploration) | «Без записанного propensity ничего нельзя» | мир i.i.d.; политика **меняется** во времени; π_t независимы от оценочных данных; смещение от τ; π̂ должен быть точен | Частично. Версионирование модели даёт вариацию, но i.i.d. нарушен. **Запасной путь, не план** |
| Sachdeva et al. 2020 (deficient support) | Ничего — **усиливает** исходный вывод | — | Дефицит перекрытия не лечится ни объёмом данных, ни клиппингом |
| Bareinboim et al. 2015 (MABUC) | «Рандомизации достаточно» | синтетический пример, бинарные переменные | 🔴 Добавляет требование: **логировать намерение ДО рекомендации** |
| Tchetgen Tchetgen et al. (proximal) | «Без рандомизации эффект не идентифицируем» | две прокси-переменные с **непроверяемыми** допущениями + completeness | Нет. Годится как ссылка, не как метод |
| DiD / RDD / IV (§2.1–2.3 первой редакции) | то же | параллельные тренды / отсутствие точной манипуляции порогом / exclusion restriction | Разобрано в первой редакции: единственный выживший инструмент — бакет по хэшу |

🔴 **ИТОГ УЧАСТКА Д2, честно.** Категорическая формулировка «постфактум не чинится» **опровергнута
как категорическая**: восстановление из нерандомизированных логов существует (Strehl et al.),
опубликовано в NIPS и проверено на реальных рекламных данных. Но все известные обходы платят
одним из трёх: непроверяемым допущением (proximal, IV), неустранимым смещением известного знака
(порог τ у Strehl), либо требуют, чтобы политика и так менялась во времени. А вот **дефицит
перекрытия** (источник T) не чинится ничем — и именно он, а не отсутствие записи propensity,
является настоящим необратимым ущербом. Правильная переформулировка вывода — в разделе
«ИЗМЕНЕНИЯ ВЫВОДОВ» ниже.

---

### Д1.5 🔴 Сколько наблюдений нужно: расчёт мощности для OPE

Задание требовало «расчёт мощности». Честный ответ по литературе: **готовой формулы мощности
для off-policy evaluation, аналогичной формуле для A/B-теста, в добытых источниках нет.**
Вместо неё в практике используется другая величина — **эффективный размер выборки**, и он
устроен так, что считается ДО и ВО ВРЕМЯ сбора, а не выводится из ожидаемого эффекта.
Ниже первоисточник и то, как из него получается проектное число.

#### Источник Y. Owen A. B. «Monte Carlo theory, methods and examples», глава 9 «Importance sampling», §9.3 (рукопись, © 2009–2013, 2018).
Добыт полностью: `curl` artowen.su.domains → PDF 658 КБ → `pdftotext -layout`, 2591 строка.
URL: https://artowen.su.domains/mc/Ch-var-is.pdf
(Рукопись помечена автором «do not distribute or post electronically without author's permission» —
здесь приводятся короткие цитаты со ссылкой, файл в репозиторий не кладётся.)

🔴 **Эффективный размер выборки, вывод и формула (9.13), дословно:**
> «Consider a hypothetical linear combination S_w = Σ w_i Z_i / Σ w_i where Z_i are independent
> random variables with a common mean and common variance σ² > 0 <...> The unweighted average of
> n_e independent random variables Z_i has variance σ²/n_e. **Setting Var(S_w) = σ²/n_e and solving
> for n_e yields the effective sample size**
> **n_e = (Σ_{i=1..n} w_i)² / Σ_{i=1..n} w_i² = n·w̄² / w̄²̄**
> <...> **If the weights are too imbalanced then the result is similar to averaging only n_e ≪ n
> observations and might therefore be unreliable. The point at which n_e becomes alarmingly small
> is hard to specify, because it is application specific.**»

**Популяционная версия (9.14), считается ДО сбора данных, дословно:**
> «For simple enough distributions, we can obtain a population version of n_e, as
> **n*_e = n·E_q(w)² / E_q(w²) = n / E_q(w²) = n / E_p(w)**. **If n*_e is too small, then we know q
> will produce imbalanced weights.**»
🔴 **Вот это и есть наш расчёт мощности.** Логирующая политика q проектируется нами, целевая p
известна приблизительно — значит E_p(w) можно посчитать **на симуляции, до единого живого
пользователя**, и получить, во сколько раз просядет эффективный размер выборки. Это ровно то,
что И2 предписывал для этапа «~100 пользователей» («калибровка `exploration_param` в симуляции
на синтетике, не на людях») — теперь у этого шага есть формула и критерий.

**Эквивалентная форма через коэффициент вариации весов (9.15), дословно:**
> «n_e = n / (1 + cv(w)²) <...> the two formulas are essentially the same.»

**Отдельный, более жёсткий порог — для оценки ДИСПЕРСИИ (9.16), дословно:**
> n_{e,σ} = (Σ w_i²)² / Σ w_i⁴
> «**If n_{e,σ} is small, then we cannot trust the variance estimate.** Estimating a variance well is
> typically a harder problem than estimating a mean well, and here we have **n_{e,σ} ≤ n_{e,µ}**.»
🔴 Практический смысл: доверительный интервал вокруг оценки требует БОЛЬШЕ данных, чем сама
оценка. Значит «мы посчитали эффект, но интервал получился широкий» — это не всегда мало
пользователей; это может быть перекос весов, и лечится он изменением схемы сбора.

🔴 **Ловушка, которую надо записать в регламент рядом с формулой (§9.3), дословно:**
> «**Effective sample sizes are imperfect diagnostics. When they are too small then we have a sign
> that the importance sampling weights are problematic. When they are large we still cannot conclude
> that importance sampling has worked. It remains possible that some important region was missed by
> all of X₁, …, X_n.**»
> И ещё: «Unfortunately **the variance estimate is itself based on the same weights that the estimate
> has used. Badly skewed weights could give a badly estimated mean along with a bad variance estimate
> that masks the problem.**»
Это тот же дефицит перекрытия (источник T), увиденный со стороны диагностики: большой n_e
не доказывает, что всё хорошо. Он доказывает только, что веса не перекошены.

**Третий диагностический признак, независимо совпавший с SNIPS (§9.3), дословно:**
> «In cases where w_i is computable, it is the observed value of a random variable with mean
> E_q(p(X)/q(X)) = 1. **If the sample mean of the weights is far from 1 then that is a sign that q was
> poorly chosen.** That is, w̄ = (1/n)·Σ w_i is another diagnostic.»
🔴 Ровно то же требование, что Ŝ(h) = 1 у Swaminathan & Joachims (§Д1.4), выведенное из другой
традиции (Монте-Карло, а не обучение из логов). **Два независимых источника дают одну проверку —
это самый надёжный пункт всего добора.** Ставить её в регламент анализа без оговорок.

#### Сборка: проектные числа для FINPILOT

Формулы мощности в «классическом» виде нет, но четыре измеренных ориентира из разных источников
складываются в шкалу. Свожу их вместе — это и есть ответ на вопрос «сколько наблюдений нужно».

| Источник | Число | Что оно означает |
|---|---|---|
| Owen, (9.14) | n*_e = n / E_p(w) | 🔴 расчётный, **считается на симуляции до релиза** |
| Douglas et al. (§1.2) | 1 000 при продуманной логирующей политике = 100 000 при равномерной | цена плохой схемы сбора — **два порядка** |
| Saito et al. (§Д1.2) | при n = 10 000 побеждает DM, при n = 300 000 — DRos | 🔴 **порядок 10⁴ — это ещё «малая выборка» для OPE** |
| Levi (§4.3 первой редакции) | ≈450 наблюдений на руку хватило на эффект 15% | это про прямой A/B, не про OPE — нижняя граница |

🔴 **Вывод, который надо занести в И2 и который первая редакция дать не могла.**
Для FINPILOT с |A| = 66 при top-k логировании с k = 3 типичный вес w = π_target/π_log ≤ 3, то есть
E_p(w) порядка 3 и n_e ≈ n/3. При равномерном логировании по всем 66 вес доходит до 66,
n_e ≈ n/66. **Разница ровно та, из-за которой стоит городить top-k: чтобы получить n_e = 1 000
эффективных наблюдений, при top-3 нужно ~3 000 выдач, при равномерном — ~66 000.**
Это арифметика, а не цитата: она выведена мной из формулы (9.14) и структуры нашей задачи,
и должна быть перепроверена симуляцией перед релизом — но порядок величины устойчив.
И отдельно: по бенчмарку ZOZO **10 000 наблюдений — это всё ещё режим, где смещённый DM точнее
несмещённых оценщиков.** Значит план И2 «~1 000 пользователей — первые честные оценки» надо
читать не как «пользователей», а как «выдач рекомендаций», и даже тогда это самая граница.

---

## Д4. ЗАКРЫТИЕ РАЗДЕЛА «НЕ ДОБЫТО» ПЕРВОЙ РЕДАКЦИИ

### Д4.1 🔴 Abadie (2021) ДОБЫТ — запись §И4 п. 1 неверна

Первая редакция: «**Abadie A. (2021), JEL 59(2):391–425 "Using Synthetic Controls" НЕ ДОБЫТ** <...>
`r.jina.ai` aeaweb.org → 1 710 байт, только аннотация; версии на NBER нет».

**Работа открыта и лежит в открытом доступе.** Как добыта — по шагам, потому что приём
переносимый:
1. `curl` Unpaywall по DOI: `https://api.unpaywall.org/v2/10.1257/jel.20191450?email=...`
   → `best_oa_location`: `host_type: repository`, `repository_institution: "Massachusetts Institute
   of Technology"`, `license: cc-by-nc`, `url: https://hdl.handle.net/1721.1/144417`,
   `url_for_pdf: null`, `version: submittedVersion`.
2. `curl` страницы DSpace → HTTP 200, 568 349 байт; из HTML выдернуты UUID битстримов.
3. 🔴 Прямой путь `/bitstreams/<uuid>/download` дал **HTTP 405 Method Not Allowed**. Рабочий путь —
   REST API DSpace 7: `https://dspace.mit.edu/server/api/core/bitstreams/<uuid>/content`
   → **HTTP 200, 882 642 байта**, PDF version 1.4, 14 страниц (вёрстка 2-up), 1 944 строки текста.

🔴 **Урок метода:** первая редакция объявила источник недобытым, испробовав aeaweb (пейволл),
economics.mit.edu (404) и NBER (нет версии) — но **не спросив Unpaywall**. Пейволл издателя
и доступность работы — разные вещи. Правило CLAUDE.md §8 («не объявлять задачу невозможной,
не исчерпав каналы») сработало бы, если бы Unpaywall был в списке каналов. Теперь он в нём есть.

**Реквизиты подтверждены по самому файлу:** Journal of Economic Literature 2021, 59(2), 391–425,
DOI 10.1257/jel.20191450, Alberto Abadie, «Using Synthetic Controls: Feasibility, Data
Requirements, and Methodological Aspects».

**Требования метода — теперь из первоисточника, а не из пересказа. Дословно.**

**Контекстное требование «Size of the Effect and Volatility of the Outcome» (§5, стр. ~409):**
> «comparative case studies typically estimate the effect of an intervention on **a single treated
> unit or on a small number of treated units**. The nature of this exercise indicates that **small
> effects will be indistinguishable from other shocks to the outcome of the affected unit, especially
> if the outcome variable of interest is highly volatile.** <...> **Even a large effect may be
> difficult to detect if the volatility of the outcome is also large. Outcome variables that include
> substantial random noise elevate the risk of over-fitting** <...> In cases where substantial
> volatility is present in the outcome of interest **it is advisable to remove it via filtering**, in
> both the exposed unit as well as in the units in the donor pool, before applying synthetic control
> techniques.»
> Тонкость, которую стоит забрать: «**the challenge posed by volatility comes only from the fraction
> of it that is generated by unit-specific factors** <...> Volatility generated by common factors
> affecting other units can be differentiated out by choosing an appropriate synthetic control.»

**Требования к донорскому пулу (§5), дословно:**
> «it is also important to **eliminate from the donor pool any units that may have suffered large
> idiosyncratic shocks to the outcome of interest during the study period** <...> Moreover, it is
> important to **restrict the donor pool to units with characteristics that are similar to the
> affected unit.** The reason is that, while the restrictions placed on the weights W do not allow
> extrapolation, **interpolation biases may still be important if the synthetic control matches the
> characteristics of the affected unit by averaging away large discrepancies.**»

🔴 **Прямой отказ от метода — формулировка, ради которой источник и нужен был (§5), дословно:**
> «More generally, **there may not exist a combination of untreated units that provide a credible
> approximation to the treated units, and the conventional synthetic control estimator SHOULD NOT BE
> USED in that case.**»

**Предупреждение против дифференцирования исхода (§5), дословно — важное и контринтуитивное:**
> «**differencing the dependent variable may result in a substantial increase in the part of the
> variance of the outcome that is attributable to noise, potentially inducing an increase in bias.**
> <...> Suppose that the idiosyncratic shocks ε_jt are independent or roughly independent in time.
> Then, **the variance of Δε_jt is larger than the variance of ε_jt** <...> a larger residual variance
> may result in **a higher risk of over-fitting and an increase in the bias** of the synthetic control
> estimator.»
🔴 Для нас: «возьмём приросты вместо уровней, так надёжнее» — в SCM это НЕ всегда так.
(В DiD дифференцирование обязательно — там оно и есть метод. Разница методов, а не опечатка.)

**Требование «Sufficient Pre-intervention Information» (§6 Data Requirements), дословно:**
> «The credibility of a synthetic control estimator depends in great part on its ability to **steadily
> track the trajectory of the outcome variable for the affected unit before the intervention** <...>
> if the data-generating process follows a linear factor model, then **the bias of the synthetic
> control estimator is bounded by a function that is inversely proportional to the number of
> pre-intervention periods** (provided that the synthetic control closely tracks the trajectory
> <...> during the pre-intervention periods). Therefore, when designing a synthetic control study,
> it is of crucial importance to collect information on [pre-intervention outcomes].»
> И: «The severity of this problem can be diminished if **powerful predictors of post-intervention
> values, aside from pre-intervention values of the outcome, are included in X_j**, reducing the
> residual variance and, as a result, the risk of over-fitting.»

**Требование «Sufficient Post-intervention Information» (§6), дословно:**
> «The evaluation data must include outcome measures that are possibly affected by the intervention
> and are relevant for the policy decision <...> **This may be problematic if the effect of an
> intervention is expected to arise gradually over time and if no forward-looking measures of the
> outcome are available.**»

**Требование «Time Horizon» (§5), дословно, и предложенный выход:**
> «The effect of some interventions may take time to emerge <...> **An obvious but unsatisfying
> approach to this problem is to wait until the effects of the intervention run their course.
> A more proactive approach is to use surrogate outcomes or leading indicators of the outcome
> variable of interest.**»
🔴 Это прямо поддерживает решение §4.2 первой редакции о прокси-метриках и переводит его
из «вынужденного упрощения» в методологически признанный приём.

🔴 **Меняется ли вывод §2.4 первой редакции («synthetic control нам не годится»)? НЕТ, вывод
устоял, и теперь он подтверждён первоисточником, а не пересказом.** Более того, первоисточник
даёт формулировку отказа сильнее («should not be used»), а требование «bias обратно
пропорционален числу предпериодов» количественно объясняет, почему на молодом продукте
метод не работает: предпериодов у нас нет.

### Д4.2 Qini: формула ПРОВЕРЕНА, снипет первой редакции оказался верным по существу

Первая редакция: «Определения Qini в §3.5 взяты **из сниппетов поисковой выдачи**, целиком
не читались, помечены как непроверенные». Сверяю по рецензируемому источнику.

#### Источник Z. Belbahri M., Murua A., Gandouet O., Partovi Nia V. «Qini-based Uplift Regression». Submitted to the Annals of Applied Statistics, arXiv:1911.12474.
Добыт полностью: `curl` → PDF → `pdftotext -layout`, 1639 строк.
URL: https://arxiv.org/abs/1911.12474 · PDF: https://arxiv.org/pdf/1911.12474

**Атрибуция первоисточника подтверждена (§1 и §2.1), дословно:**
> «Evaluating uplift models requires the construction of the Qini curve and the computation of the
> **Qini coefficient [Radcliffe, 2007]**» · «The Qini coefficient is a single statistic drawn from the
> Qini curve. This latter object is a **generalization of the Lorenz curve** [Lorenz, 1905]».

🔴 **Полное определение (§2.1), дословно — вот чего не хватало:**
> «for a given model, let û₍₁₎ ≥ û₍₂₎ ≥ … ≥ û₍ₙ₎ be the sorted predicted uplifts. Let φ ∈ [0,1] be a
> given proportion and let **N_φ = { i : û_i ≥ û₍⌈φn⌉₎ }** ⊂ {1,…,n} be the subset of individuals with
> the φn × 100% highest predicted uplifts.
> As a function of the fraction of population targeted φ, **the incremental uplift is defined as**
> **h(φ) = Σ_{i∈N_φ} y_i t_i − ( Σ_{i∈N_φ} y_i(1−t_i) ) · ( Σ_{i∈N_φ} t_i / Σ_{i∈N_φ} (1−t_i) )**,
> where Σ_{i∈N_φ}(1−t_i) ≠ 0, with h(0) = 0. **The incremental uplift has been normalized by the
> number of subjects treated in N_φ.** The relative incremental uplift g(φ) is given by
> **g(φ) = h(φ) / Σ_{i=1..n} t_i.**»
> «**The Qini curve is constructed by plotting g(φ) as a function of φ ∈ [0,1]** <...> The straight
> line between the points (0,0) and (1, g(1)) <...> represents a benchmark to compare the performance
> of the model to **a strategy that would randomly target subjects.**»
> «**The Qini coefficient q** is a single index of model performance. It is defined as the area
> between the Qini curve and the straight line:
> **q = ∫₀¹ Q(φ) dφ = ∫₀¹ { g(φ) − φ·g(1) } dφ**, where Q(φ) = g(φ) − φ·g(1).»
> Эмпирическая аппроксимация по правилу трапеций (формула 3):
> **q̂ = (1/2)·Σ_{j=1..J} (φ_{j+1} − φ_j)·{ Q(φ_{j+1}) + Q(φ_j) }**.
> «when comparing several models, the preferred model is the one with **the maximum Qini
> coefficient**.»

🔴 **ВЕРДИКТ СВЕРКИ: сниппет первой редакции был ВЕРЕН по существу.** Формула из сниппета
`Qini(k) = R^{T=1}_{π(k)} − R^{T=0}_{π(k)}·(N^{T=1}_{π(k)}/N^{T=0}_{π(k)})` — это в точности h(φ)
выше, записанное в других обозначениях. Пометку «непроверено» с §3.5 можно снимать.
Уточнение, которого в сниппете не было и которое важно: **q — это площадь между кривой и
диагональю, БЕЗ дополнительной нормировки на «оптимальную» кривую** (в сниппете упоминалась
нормировка «by the area between the random and the optimal targeting curves» — у Belbahri et al.
её в определении q нет; это, судя по всему, отдельный вариант нормировки, и при использовании
надо явно оговаривать, какой именно вариант считается).

**Бонусная находка того же источника — дополнительная метрика (§2.1), дословно:**
> «a good model should induce **a decreasing disposition of the observed uplifts** in these bins
> <...> To measure the degree to which a model does this correctly, we suggest the use of the
> **Kendall rank correlation coefficient** [Kendall, 1938].»
Полезно нам: **уплифт по бинам должен монотонно убывать** — дешёвая визуальная и числовая
проверка вменяемости uplift-модели, которой в §3.5 не было.

**Первоисточник Radcliffe (2007) сам по себе** — по-прежнему НЕ добыт (Direct Marketing Analytics
Journal, вне открытого доступа). 🔴 Но необходимость в нём отпала: определение теперь взято
из рецензируемого источника, который цитирует Radcliffe напрямую, и совпадает со снипетом.
Статус: закрыт как «не требуется».

### Д4.3 Что закрыть не удалось

1. **Первоисточник утверждения о неидентифицируемости ВЫУЧЕННОГО propensity** (§1.3 п. 3
   первой редакции, взято из сниппета) — **не найден**. Канал: OpenAlex `search=off-policy
   evaluation estimated logging propensities bias non-identifiable&per-page=6` вернул HTTP 200
   и 6 результатов, **ни один не по теме** (медицинский регистр AHRQ, InstructGPT, денежная
   политика, микроэконометрика, R&D-политика, медстрахование) — поисковое ядро OpenAlex
   по такому длинному запросу уходит в общую лексику. WebSearch исчерпан (400/400), Exa
   недоступна (сервер 404), второй заход не делал: бюджет.
   🔴 **Однако содержательно утверждение теперь подкреплено сильнее, чем было.** Теорема 1
   Дудика (§Д1.1) даёт точную величину смещения IPS: |E[V̂_IPS] − V| = |E_x[ρ·δ]|, где δ —
   мультипликативная ошибка propensity. Если propensity выучен, δ неизвестен и оценить его
   изнутри тех же данных нечем. Это не то же самое, что формальная «неидентифицируемость»,
   и я не приписываю источникам того, чего в них нет: **строгое доказательство
   неидентифицируемости в добытых текстах отсутствует**, есть точная формула смещения через
   неизвестную величину. В научный текст писать надо вторую формулировку.
2. **Формулировка «correct propensity is the probability under the exact decision process after all
   rules and gating»** (§1.3, из medium-статьи) — первоисточник не искал повторно, бюджет ушёл
   на участки Д1–Д2. Содержательно следует из Bottou §4.3 и подтверждается Definition 1 у
   Sachdeva et al. (§Д1.3: «π₀(y|x) > 0 for all actions y ∈ Y **and contexts x ∈ X**»), но как
   цитата остаётся неатрибутированной. **Рекомендация: в научном тексте не цитировать, а
   излагать своими словами со ссылкой на Bottou и Sachdeva.**
3. **Российская практика причинной оценки эффекта финтех-продуктов** (§И4 п. 7) — не искал,
   пробел из первой редакции сохраняется.
4. **22-МР со сверкой по официальной публикации cbr.ru** (§И4 п. 6) — см. участок Д3.

---

### Д1.6 Как top-k soft-greedy устроен НА ПРАКТИКЕ — из работающего кода

Первая редакция дала теорию классов логирующих политик (Douglas et al., §1.2). Задание требовало
практику. Ниже — дословно из исходного кода Open Bandit Pipeline, то есть из библиотеки,
на которой ZOZO собирал продовые данные (источник S).

#### Источник AA. Исходный код `obp/policy/offline.py`, Open Bandit Pipeline (st-tech/zr-obp, ветка master).
Добыт: `curl` raw.githubusercontent.com → HTTP 200, 73 129 байт.
URL: https://raw.githubusercontent.com/st-tech/zr-obp/master/obp/policy/offline.py

**Случай «показываем ОДНО действие» — метод `predict_proba`, докстрока дословно:**
> «Obtains action choice probabilities for new data based on scores predicted by a classifier.
> This `predict_proba` method obtains action choice probabilities for new data x ∈ X by applying
> the softmax function as follows:
> **P(A = a | x) = exp(f(x,a)/τ) / Σ_{a′∈A} exp(f(x,a′)/τ)**,
> where A is a random variable representing an action, and **τ is a temperature hyperparameter** <...>
> **As τ → ∞, the algorithm will select arms uniformly at random.**»
> Сигнатура: `predict_proba(self, context, tau: Union[int, float] = 1.0)`.
> 🔴 Ограничение прямо в коде: «**Note that this method can be used only when `len_list=1`, please use
> the `sample_action` method otherwise.**» — и `assert self.len_list == 1`.

**Случай «показываем СПИСОК» — а это ровно наш случай — метод `sample_action`, дословно:**
> «**Sample a ranking of (non-repetitive) actions from the Plackett-Luce ranking distribution.**
> This `sample_action` method samples a **non-repetitive** ranking of actions for new data x ∈ X
> via the so-called "**Gumbel Softmax trick**" as follows:
> **s(x,a) = f̂(x,a)/τ + γ_{x,a},   где γ_{x,a} ~ Gumbel(0,1)**
> τ is a temperature hyperparameter <...> When `len_list > 0`, the expected rewards estimated at
> different positions will be averaged to form f(x,a). γ_{x,a} is a random variable sampled from the
> Gumbel distribution. **By sorting the actions based on s(x,a) for each context, we can efficiently
> sample a ranking from the Plackett-Luce ranking distribution.**»
> Сигнатура: `sample_action(self, context, tau = 1.0, random_state: Optional[int] = None)`.

🔴 **Три практических вывода, которые надо занести в ТЗ FINPILOT.**

1. **«Top-k» в проде реализуется не через выбор k, а через ТЕМПЕРАТУРУ τ.** Один непрерывный
   параметр, τ → ∞ даёт равномерную политику, τ → 0 — жадную. Это удобнее top-k с целым k,
   потому что τ можно подбирать на сетке и потому что при любом конечном τ вероятность каждого
   действия строго положительна (тот самый аргумент Douglas et al. про softmax: «probability mass
   on all actions <...> ensure the IPW estimator is unbiased for any target policy even if this
   mass is very small»). Оговорка честная: Douglas et al. по MSE ставили top-k и power-normalized
   ВЫШЕ softmax при большом |A| (§1.2). У нас |A| = 66 — это не «большое» пространство действий
   вроде 100 000 из их симуляции, и преимущество top-k там доказывалось именно на |A| = 100 000.
   **Для 66 альтернатив разница между схемами, скорее всего, мала, а инженерная простота softmax
   с одним τ и гарантированной положительностью — реальное преимущество.** Это моё суждение
   из сопоставления двух источников, а не цитата; проверять симуляцией.

2. 🔴 **Показ упорядоченного СПИСКА — отдельная задача, и у неё есть готовое решение:
   Plackett–Luce через Gumbel-softmax.** Мы показываем не одну альтернативу, а список
   сопоставимых (это требование §1.4 — единственная форма, проходящая equipoise и 22-МР).
   Значит наша логирующая политика — распределение над УПОРЯДОЧЕННЫМИ СПИСКАМИ, а propensity —
   вероятность конкретного показанного списка. Реализация: посчитать SAW-оценки, разделить на τ,
   прибавить независимый шум Gumbel(0,1) к каждой, отсортировать. Просто и воспроизводимо.
   Последствие для логирования, которого в И1 не было: **поле `propensity` должно относиться
   к ПОКАЗАННОМУ СПИСКУ (или к позиции в нём), а не только к предвыбранной альтернативе**,
   и надо честно записать, какая из двух семантик выбрана. Иначе позже никто не разберёт,
   что именно измерено.

3. 🔴 **`random_state` как явный параметр — подтверждение требования воспроизводимости.**
   В коде OBP генератор случайности передаётся снаружи. У нас то же самое должно быть
   архитектурным требованием: механизм выбора — чистая функция от (контекст, конфиг, seed),
   и **seed пишется в лог**. Без этого нельзя ни переиграть решение, ни посчитать propensity
   методом Монте-Карло (приём из §Д1.2), ни доказать регулятору, что выдача не подтасована.
   Добавить поле `rng_seed` в `recommendation_impressions`.

---

### Д1.7 🔴 ДЕЛЬТА К СПЕЦИФИКАЦИИ И1: поля, которых не хватало

Первая редакция дала три таблицы (И1). Добор нашёл **шесть полей и одну сущность**, без которых
часть методов останется недоступной навсегда. Это не переписывание И1, а дополнение к нему.

**В `recommendation_impressions` добавить:**

| Поле | Тип | Зачем | Откуда требование |
|---|---|---|---|
| `rng_seed` | bigint | воспроизвести решение; без него propensity нельзя пересчитать Монте-Карло | §Д1.2 (сноска 4 Saito et al.), §Д1.6 (`random_state` в OBP) |
| `propensity_semantics` | enum (`action` \| `slate` \| `position`) | 🔴 к ЧЕМУ относится записанная вероятность: к предвыбранной альтернативе, к показанному списку целиком или к позиции | §Д1.6 (Plackett–Luce над списками) |
| `propensity_method` | enum (`closed_form` \| `monte_carlo`) | честно отметить, вероятность посчитана формулой или симуляцией | §Д1.2 |
| `propensity_mc_samples` | int \| null | сколько итераций Монте-Карло; задаёт точность δ в Теореме 1 Дудика | §Д1.1, §Д1.2 |
| `support_divergence` | numeric [0,1] | доля массы целевой политики на действиях с нулевым propensity | 🔴 §Д1.3 (Sachdeva et al., Теорема 1) |
| `logging_temperature` | numeric | τ логирующей политики в этой выдаче | §Д1.6 |

**Новая сущность — `user_intent_snapshot`.** 🔴 Самая важная находка Д2 и единственная,
которая меняет ПРОДУКТ, а не только аналитику.

| Поле | Тип | Зачем |
|---|---|---|
| `impression_id` | UUID FK | склейка с выдачей |
| `intended_allocation` | jsonb | **что пользователь собирался сделать со свободным потоком ДО показа рекомендации** |
| `intent_source` | enum (`explicit_input` \| `previous_month_actual` \| `unknown`) | спросили явно, взяли фактическое поведение прошлого месяца, или нет данных |
| `intent_captured_at` | timestamptz | строго ДО `impression.ts` — проверяемый инвариант |
| `followed_recommendation` | bool | совпало ли итоговое действие с рекомендованным |

Обоснование — Bareinboim, Forney, Pearl (§Д2.2): «**interrupt any reasoning agent before they
execute their choice, treat this choice as intention, deliberate, and then act**». Без намерения
нельзя вычислить ETT, то есть **нельзя ответить на вопрос «помогла ли система тому, кто без неё
поступил бы иначе»** — а это и есть вопрос владельца в чистом виде. Рандомизация этого не заменяет:
пример «жадного казино» показывает случай, где рандомизированный эксперимент даёт 0,30 против 0,30
(«нет разницы»), а персональная политика по намерению выигрывает.

**Две проверки лога, которые надо поставить в регламент анализа (обе бесплатные):**
1. 🔴 **w̄ ≈ 1.** Среднее импортанс-весов по выборке должно быть близко к единице. Два независимых
   источника: Swaminathan & Joachims §5 формула (5) и Owen §9.3. Отклонение — признак, что
   логирующая политика плохо покрывает целевую, и оценка недостоверна.
2. 🔴 **n_e = (Σw)²/Σw² сравнивать с n.** Эффективный размер выборки; при n_e ≪ n оценка опирается
   фактически на горстку наблюдений (Owen, формула 9.13). Дополнительно n_{e,σ} = (Σw²)²/Σw⁴ —
   для доверия интервалу, и он всегда меньше (формула 9.16).
Обе — про пригодность выборки для оценки КОНКРЕТНОЙ целевой политики, и обе дополняют, а не
заменяют проверку И1 «сумма `propensity_all` = 1» (та — про корректность записи).

---

## Д3. ПРАВО И ЭТИКА РАНДОМИЗАЦИИ В ФИНПРОДУКТЕ НА РЫНКЕ РФ

Участок добыт подагентом (один подагент, 16 вызовов инструментов, WebSearch 0, своих подагентов
0). Сырьё целиком перенесено сюда из
`scratchpad/dobor_legal.md` по правилу §9 CLAUDE.md. Ниже — дословно.

🔴 **Главная находка участка, которой в первой редакции не было вовсе: статья 10.2-2 149-ФЗ
о рекомендательных технологиях.** Первая редакция разбирала 22-МР (не наш адресат) и ст. 16
152-ФЗ (не про рекомендацию) — и пропустила норму, которая применяется к FINPILOT НАПРЯМУЮ.

- `docs/research/raw/cbr_19mr_product_governance_2026-09-10.md`: **19-МР добыт ЦЕЛИКОМ**
  (PDF cbr.ru, 39 стр., `https://www.cbr.ru/crosscut/lawacts/file/7653`) — см. п. 1 ниже.
- `docs/research/raw/tails_cbr_mr_software_registry_2026-09-10.md`: 1-МР (20.01.2025), 3-МР.

---

## 1. 19-МР Банка России — реквизиты и применимость (сверено с уже добытым файлом)

**Реквизиты** (из garant.ru, зафиксировано в добытом файле): Методические рекомендации
Банка России **№ 19-МР от 27 декабря 2023 г.** «по управлению финансовым продуктом»,
подписал первый зампред Д.В. Тулин. Опубликование: сайт Банка России 27.12.2023;
«Вестник Банка России», 29.12.2023, № 78. На 10.09.2026 отметки «утратил силу» нет;
1-МР от 20.01.2025 ссылается на 19-МР (сноска <17>).

**Адресаты — дословно, п. 1.2:** «адресованы кредитным организациям, профессиональным
участникам рынка ценных бумаг, управляющим компаниям ... микрофинансовым организациям,
а также иным финансовым организациям, принявшим решение следовать настоящим Методическим
рекомендациям ..., саморегулируемым организациям в сфере финансового рынка ... и другим
объединениям (ассоциациям, союзам) финансовых организаций.»

**Цель — дословно, п. 1.1:** «... обеспечения прозрачного и осознанного выбора потребителями
финансовых продуктов, стимулирования добросовестного клиентоориентированного поведения
поставщиков финансовых продуктов и повышения доверия на финансовом рынке.»

**Применим ли к FINPILOT — ПРЯМО: НЕТ.** Основание — п. 1.2: адресаты суть финансовые
организации и СРО. FINPILOT не является финансовой организацией и не выпускает финансовый
продукт в смысле п. 1.3 («инструмент на финансовом рынке и (или) услуга ... используется
для целей инвестирования, управления финансами или защиты активов»; сноска 1 перечисляет
облигации, ПФИ, паи, полисы, кредитные карты, кредиты, займы, вклады — СППР там нет).
Косвенная релевантность — только в B2B-сценарии (банк-заказчик, следующий 19-МР, отнесёт
встроенный модуль к своей системе управления продуктом) и как добровольно принятая планка
(«иные финансовые организации, принявшие решение следовать» — путь добровольного следования
в п. 1.2 предусмотрен прямо).

**Статус по разделу:** дословных пунктов 19-МР специально про A/B-тест или рандомизацию
в добытом тексте нет — при чтении 39 стр. таких формулировок не зафиксировано.

---

## 2. Freedman 1987, «clinical equipoise» — журнал добычи

DOI 10.1056/NEJM198707163170304, PMID 3600702, N Engl J Med 1987;317(3):141-145.

| Канал | Результат |
|---|---|
| Semantic Scholar Graph API (`paper/DOI:...`) | HTTP 200. `openAccessPdf.status = "CLOSED"`, url пустой; abstract «elided by the publisher» (null) |
| Unpaywall API (`api.unpaywall.org/v2/...`) | HTTP 200. `"is_oa": false`, `"oa_status": "closed"`, `"best_oa_location": null`, `"has_repository_copy": false`, `"oa_locations": []`. Обновлено 2026-07-28 |
| med.mcgill.ca PDF-зеркало (курс bios601) | curl вернул код **000** (соединение не установлено), 0 байт |
| pubmed.ncbi.nlm.nih.gov/3600702/ | HTTP **203**, 5565 байт HTML (антибот-заглушка, не карточка) |

| EuropePMC REST (`resultType=core`) | HTTP 200, hitCount 1. **Полный авторский abstract получен дословно** (см. ниже). `"isOpenAccess":"N"`, `"inPMC":"N"`, `"hasPDF":"N"`, `fullTextUrlList`: единственный URL — DOI, «Subscription required». citedByCount **1294** |
| OpenAlex (`works/doi:...`) | HTTP 200, cited_by_count **2352**. Ни одна из 4 locations не OA (`is_oa=False`, `pdf_url=None`): doi.org, pubmed, worldcat, `http://hdl.handle.net/10822/819907` (DigitalGeorgetown) |
| fatcat (`api.fatcat.wiki/v0/release/lookup?doi=...&expand=files`) | пустой ответ |

**Итог по полному тексту:** статья закрыта. Полный текст (5 страниц NEJM) не добыт ни одним
каналом; по Unpaywall репозиторной копии не существует вовсе. Добыт **дословный авторский
abstract**, и он содержит именно ту формулировку, ради которой статья нужна.

### 2.1 Дословная цитата — определение clinical equipoise

Источник: EuropePMC, запись MED:3600702, поле `abstractText`
(`https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%2210.1056/NEJM198707163170304%22&format=json&resultType=core`).
Это авторский abstract статьи Freedman B. «Equipoise and the ethics of clinical research»,
N Engl J Med 1987;317(3):141-145.

> «The ethics of clinical research requires equipoise--a state of genuine uncertainty on the
> part of the clinical investigator regarding the comparative therapeutic merits of each arm
> in a trial. Should the investigator discover that one treatment is of superior therapeutic
> merit, he or she is ethically obliged to offer that treatment. The current understanding of
> this requirement, which entails that the investigator have no "treatment preference"
> throughout the course of the trial, presents nearly insuperable obstacles to the ethical
> commencement or completion of a controlled trial and may also contribute to the termination
> of trials because of the failure to enroll enough patients. I suggest an alternative concept
> of equipoise, which would be based on present or imminent controversy in the clinical
> community over the preferred treatment. According to this concept of "clinical equipoise,"
> the requirement is satisfied if there is genuine uncertainty within the expert medical
> community--not necessarily on the part of the individual investigator--about the preferred
> treatment.»

**Разбор на три операционных условия (следуют прямо из текста выше):**
1. Рандомизировать этично при **genuine uncertainty** — подлинной неопределённости, какая из
   ветвей лучше.
2. Порог неопределённости — **не личное мнение исследователя**, а состояние **экспертного
   сообщества** («within the expert medical community — not necessarily on the part of the
   individual investigator»).
3. **Обязанность прекратить**: «Should the investigator discover that one treatment is of
   superior therapeutic merit, he or she is ethically obliged to offer that treatment» —
   как только преимущество установлено, рандомизация должна быть прекращена.

**Перенос на FINPILOT (вывод вахты, не цитата):** exploration-трафик допустим ровно в той
зоне, где модель сама не различает альтернативы — то есть где разрыв SAW-оценок лежит
в пределах неопределённости оценки. Показ второй по рангу альтернативы при близких оценках —
это equipoise; показ заведомо худшей (большой разрыв оценок) — нарушение условия 3, и
никакое раскрытие его не лечит, потому что нарушена обязанность предложить лучшее.

---

## 3. Прямое регулирование РФ: что ПРОВЕРЕНО и что найдено

### 3.1 ГЛАВНОЕ И ПРИМЕНИМОЕ: ст. 10.2-2 Федерального закона от 27.07.2006 № 149-ФЗ

Реквизиты: Федеральный закон от 27.07.2006 № 149-ФЗ «Об информации, информационных
технологиях и о защите информации», **статья 10.2-2 «Особенности предоставления информации
с применением рекомендательных технологий»**, введена Федеральным законом от 31.07.2023
№ 408-ФЗ. Редакция от 26.06.2026 (с изм., вступ. в силу с 01.09.2026).
Источник текста: КонсультантПлюс,
`https://www.consultant.ru/document/cons_doc_LAW_61798/2a69c627d62738291fe0a0fd4c1253385e730784/`
(HTTP 200, 67 120 байт, `curl -sk --http1.1` с браузерным UA).

Дословно:

> «1. Владелец сайта и (или) страницы сайта в сети "Интернет", и (или) информационной системы,
> и (или) программы для электронных вычислительных машин, на которых применяются информационные
> технологии предоставления информации на основе сбора, систематизации и анализа сведений,
> относящихся к предпочтениям пользователей сети "Интернет", находящихся на территории
> Российской Федерации (далее - владелец информационного ресурса, на котором применяются
> рекомендательные технологии), обязан соблюдать требования законодательства Российской
> Федерации, в частности:
> 1) не допускать применение информационных технологий предоставления информации на основе
> сбора, систематизации и анализа сведений, относящихся к предпочтениям пользователей сети
> "Интернет", находящихся на территории Российской Федерации (далее - рекомендательные
> технологии), которые нарушают права и законные интересы граждан и организаций, а также
> не допускать применение рекомендательных технологий в целях предоставления информации
> с нарушением законодательства Российской Федерации;
> 2) не допускать предоставление информации с применением рекомендательных технологий без
> информирования пользователей сети "Интернет" о применении на данном сайте ... рекомендательных
> технологий. Требования к содержанию информации о применении рекомендательных технологий
> и размещению такой информации на информационном ресурсе устанавливаются федеральным органом
> исполнительной власти, осуществляющим функции по контролю и надзору в сфере средств массовой
> информации, массовых коммуникаций, информационных технологий и связи;
> 3) разместить на информационном ресурсе, на котором применяются рекомендательные технологии,
> документ, устанавливающий правила применения рекомендательных технологий;
> 4) разместить на информационном ресурсе ... адрес электронной почты для направления ему
> юридически значимых сообщений, свои фамилию и инициалы (для физического лица) или
> наименование (для юридического лица).
>
> 2. Правила применения рекомендательных технологий должны содержать:
> 1) описание процессов и методов сбора, систематизации, анализа сведений, относящихся
> к предпочтениям пользователей сети "Интернет", предоставления информации на основе этих
> сведений, а также способов осуществления таких процессов и методов;
> 2) виды сведений, относящихся к предпочтениям пользователей сети "Интернет", которые
> используются для предоставления информации с применением рекомендательных технологий,
> источники получения таких сведений.
>
> 3. Правила применения рекомендательных технологий должны быть размещены на информационном
> ресурсе ... на русском языке. Владелец ... должен обеспечить беспрепятственный и безвозмездный
> доступ пользователей сети "Интернет" к правилам применения рекомендательных технологий.
>
> 4. В случае обнаружения в сети "Интернет" информационного ресурса, на котором рекомендательные
> технологии применяются с признаками нарушения требований, предусмотренных пунктами 1 и 2
> части 1 настоящей статьи, федеральный орган исполнительной власти [Роскомнадзор] ... вправе
> запрашивать у владельца ... информацию, связанную с применением рекомендательных технологий,
> **а также доступ к программно-техническим средствам рекомендательных технологий** для
> проведения оценки соответствия применения рекомендательных технологий требованиям настоящей
> статьи. Указанное лицо обязано предоставлять запрашиваемую информацию и доступ
> к программно-техническим средствам не позднее чем в течение десяти дней со дня получения
> запроса ...
>
> 5. В случае установления факта неисполнения ... обязанностей, предусмотренных настоящей
> статьей, [Роскомнадзор] направляет указанному лицу уведомление, содержащее требование принять
> меры по устранению выявленного нарушения. Владелец ... обязан принять меры ... не позднее чем
> через десять дней со дня получения уведомления или в иной, установленный в уведомлении срок.
>
> 6. В случае непринятия владельцем ... мер, указанных в части 5 настоящей статьи,
> [Роскомнадзор] незамедлительно направляет ...» (далее — блокировка; хвост части 6 в выгрузке
> обрезан, дословно не подтверждён).

**Что это даёт по нашему вопросу.**
- Это **ближайшее к прямому** регулирование: A/B-тест и exploration-трафик по-прежнему НЕ
  названы, но ранжирование рекомендаций попадает под статью целиком.
- Обязанность из ч. 1 п. 2 и ч. 2-3 — **опубликовать правила применения рекомендательных
  технологий** с описанием «процессов и методов ... предоставления информации на основе этих
  сведений, а также способов осуществления таких процессов и методов». Наличие exploration-ветки
  — это и есть «способ осуществления», то есть **его упоминание в правилах обязательно**, если
  рандомизация применяется. Скрытый A/B в рекомендациях — риск по ч. 1 п. 2 и ч. 2 п. 1.
- Ч. 4 — Роскомнадзор вправе требовать **доступ к программно-техническим средствам**. Практический
  вывод: конфигурация exploration должна быть воспроизводимой и предъявляемой (версия модели,
  доля трафика, seed), а не «зашита в код без следов».
- Ч. 1 п. 1 — общий запрет рекомендательных технологий, «которые нарушают права и законные
  интересы граждан». Именно сюда упирается вопрос о показе заведомо худшей альтернативы.

### 3.2 Прямого регулирования A/B-тестирования как такового НЕТ — перечень проверенного

Проверено на наличие норм именно об экспериментах/рандомизации на пользователях:
- **149-ФЗ ст. 10.2-2** — регулирует рекомендательные технологии (см. 3.1), про эксперименты
  и рандомизацию ни слова; текст статьи прочитан целиком.
- **152-ФЗ ст. 16** — уже добыто в `causal_effect_measurement_2026-09-10.md`; про запрет решений
  исключительно на автоматизированной обработке, не про эксперименты.
- **22-МР ЦБ от 27.12.2024** (пп. 1.1, 2.6, 2.16, 3.6) — уже добыто там же.
- **19-МР ЦБ от 27.12.2023** — текст 39 стр. добыт ранее целиком; формулировок про A/B-тест
  или рандомизацию в нём не зафиксировано, адресаты — финорганизации (п. 1.2), нас не обязывает.
- **1-МР ЦБ от 20.01.2025, 3-МР** — разобраны в `tails_cbr_mr_software_registry_2026-09-10.md`.

НЕ проверено в этом заходе (бюджет инструментов), честно фиксирую как пробел: 353-ФЗ
(потребкредит), 38-ФЗ «О рекламе», Закон РФ 2300-1 «О защите прав потребителей» (ст. 10 право
на информацию, ст. 16), 135-ФЗ «О защите конкуренции» / практика ФАС по недобросовестным
практикам, подзаконный акт Роскомнадзора с «требованиями к содержанию информации о применении
рекомендательных технологий» (ссылка на него есть в ч. 1 п. 2 ст. 10.2-2 — сам акт не добыт).

---

## 4. Зарубежный контур

### 4.1 DSA ЕС — дословно (добыто)

Regulation (EU) 2022/2065 (Digital Services Act), CELEX 32022R2065.
Источник: EUR-Lex, `https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32022R2065`
(HTTP 200, 840 293 байта, полный текст регламента).

**Article 25 «Online interface design and organisation» (dark patterns):**
> «1. Providers of online platforms shall not design, organise or operate their online interfaces
> in a way that deceives or manipulates the recipients of their service or in a way that otherwise
> materially distorts or impairs the ability of the recipients of their service to make free and
> informed decisions.
> 2. The prohibition in paragraph 1 shall not apply to practices covered by Directive 2005/29/EC
> or Regulation (EU) 2016/679.
> 3. The Commission may issue guidelines on how paragraph 1 applies to specific practices, notably:
> (a) giving more prominence to certain choices when asking the recipient of the service for
> a decision; (b) repeatedly requesting that the recipient of the service make a choice where that
> choice has already been made, especially by presenting pop-ups that interfere with the user
> experience; (c) making the procedure for terminating a service more difficult than subscribing
> to it.»

**Article 27 «Recommender system transparency»:**
> «1. Providers of online platforms that use recommender systems shall set out in their terms and
> conditions, in plain and intelligible language, the main parameters used in their recommender
> systems, as well as any options for the recipients of the service to modify or influence those
> main parameters.
> 2. The main parameters referred to in paragraph 1 shall explain why certain information is
> suggested to the recipient of the service. They shall include, at least: (a) the criteria which
> are most significant in determining the information suggested to the recipient of the service;
> (b) the reasons for the relative importance of those parameters.
> 3. Where several options are available pursuant to paragraph 1 for recommender systems that
> determine the relative order of information presented to recipients of the service, providers
> of online platforms shall also make available a functionality that allows the recipient of the
> service to select and to modify at any time their preferred option. That functionality shall be
> directly and easily accessible from the specific section of the online platform's online
> interface where the information is being prioritised.»

**Чтение для нашего вопроса.** DSA не запрещает рандомизацию и не упоминает A/B-тесты. Ст. 27
требует раскрытия «main parameters» и «the reasons for the relative importance of those
parameters» — то есть раскрытие ранга и его обоснования; наш сценарий (все альтернативы
и их оценки честно раскрыты) этому требованию соответствует по конструкции. Ст. 25 задаёт
границу: недопустимо «materially distorts or impairs the ability ... to make free and informed
decisions». Рандомизация, при которой пользователь видит все альтернативы с оценками и может
выбрать первую по рангу, эту способность не ухудшает; рандомизация, скрывающая ранг или
подающая exploration-вариант как «рекомендованный», — ухудшает.
Ст. 40 (доступ к данным для исследователей) и EU AI Act в этом заходе НЕ добыты — бюджет.

### 4.2 НЕ добыто (честный пробел этого захода)
- **FCA Consumer Duty** (PS22/9, FG22/5; Principle 12 / PRIN 2A) — дословных формулировок нет,
  каналы не пробовались из-за бюджета инструментов.
- **CFPB** — не пробовалось.
- **DSA ст. 40**, **EU AI Act** — не пробовались.
- **Корпоративный IRB / этические комитеты в A/B** (Facebook emotional contagion 2014 и
  последовавшая практика review boards, Jouppi/«Evolving the IRB» Polonetsky-Tene-Jerome) —
  не пробовалось.

---

## 5. Свод: что можно утверждать по добытому

1. **Прямого запрета рандомизации/A/B в РФ нет.** Ни одна из проверенных норм (149-ФЗ ст. 10.2-2,
   152-ФЗ ст. 16, 19-МР, 22-МР, 1-МР, 3-МР) не регулирует эксперименты на пользователях как
   таковые. Отрицательный результат подкреплён перечнем п. 3.2, там же — что осталось непроверенным.
2. **Применимая норма одна и она про раскрытие, а не про запрет** — ст. 10.2-2 149-ФЗ:
   информировать о применении рекомендательных технологий, опубликовать правила с описанием
   «процессов и методов ... и способов осуществления таких процессов и методов», обеспечить
   Роскомнадзору доступ к программно-техническим средствам по запросу.
3. **Этический тест — clinical equipoise Freedman 1987 (дословно добыт).** Рандомизация этична
   при genuine uncertainty на уровне экспертного сообщества, и обязана прекращаться, как только
   превосходство одной ветви установлено.
4. **Граница, которую честное раскрытие НЕ спасает:** показ альтернативы, о худшести которой
   система уже знает. Это нарушает и условие Freedman («ethically obliged to offer that
   treatment»), и ч. 1 п. 1 ст. 10.2-2 (рекомендательные технологии, «которые нарушают права
   и законные интересы граждан»), и ст. 25 DSA.
5. **Что честное раскрытие СПАСАЕТ:** exploration в зоне, где оценки альтернатив неразличимы
   в пределах неопределённости модели, при раскрытых альтернативах, оценках и самом факте
   рандомизации в правилах применения рекомендательных технологий.

---

## Д5. ИЗМЕНЕНИЯ ВЫВОДОВ ПО ИТОГАМ ДОБОРА

### Д5.1 ✅ Подтвердилось (и теперь стоит на первоисточнике, а не на пересказе)

1. **Propensity надо писать в момент решения.** Теперь есть точная арифметика, а не аргумент
   «по смыслу»: Теорема 1 Дудика (§Д1.1) — смещение IPS равно |E_x[ρ·δ]|, где δ — ошибка
   propensity. Записали точно → δ = 0 → несмещённость при любой модели вознаграждения.
2. **Экономия от продуманной логирующей политики измерена трижды независимо:** Douglas et al.
   (1 000 ≈ 100 000, §1.2), Owen (n_e = n/E_p(w), §Д1.5), третье слагаемое дисперсии DR
   (штраф (1−p)/p, §Д1.1). Все три дают один порядок выигрыша для top-k против равномерного.
3. **Synthetic control нам не годится** (§2.4) — подтверждено первоисточником Abadie (2021),
   добытым (§Д4.1), формулировка автора даже жёстче: «**should not be used in that case**».
4. **Проверка «сумма вероятностей = 1»** — подтверждена с другой стороны: E[Ŝ(h)] = 1
   у Swaminathan & Joachims и w̄ ≈ 1 у Owen. 🔴 Два независимых источника из разных традиций —
   самый надёжный пункт добора.
5. **Формула Qini из сниппета первой редакции оказалась ВЕРНОЙ** (§Д4.2). Пометку
   «непроверено» с §3.5 снимаю.
6. **Рандомизация допустима только в зоне equipoise** (§1.4) — подтверждено дословной
   формулировкой Freedman 1987 (§Д3), которая в первой редакции цитировалась через
   пересказ Kohavi.

### Д5.2 🔶 Уточнилось

1. **Доля exploration-трафика: 5–10% из «инженерного ориентира» стала измеренным числом.**
   У ZOZO 1 374 327 из 13 542 411 показов = **10,1% трафика семь дней шли под равномерно
   случайной политикой** (§Д1.2). §И4 п. 3 первой редакции («точная доля в продакшене
   не найдена») закрыт.
2. **Цена рандомизации получила число: −30% отклика** на равномерно случайной ветке
   (CTR 0,35% против 0,50%, §Д1.2). Это верхняя граница — цена ПОЛНОСТЬЮ равномерной
   политики; top-k платит долю от неё.
3. **«1 000 пользователей — первые честные оценки» (И2) надо читать строже.** По бенчмарку
   ZOZO 10 000 наблюдений — всё ещё «малая выборка» для OPE (§Д1.2). И считать надо выдачи,
   а не пользователей. Реалистичный порог первых оценок сдвигается вверх.
4. **Требование перекрытия получило формальное имя и меру:** Definition 1 (full support)
   и support divergence D_X(π|π₀) (§Д1.3). Добавлено поле `support_divergence` в лог (§Д1.7).
5. **Правовая рамка сменила основание.** Первая редакция опиралась на 22-МР (адресат — не мы)
   и ст. 16 152-ФЗ (не про рекомендацию). Теперь есть **прямо применимая норма — ст. 10.2-2
   149-ФЗ** (§Д3): рандомизацию она не запрещает, но требует опубликовать правила применения
   рекомендательных технологий с описанием «способов осуществления таких процессов и методов»,
   то есть **exploration-ветку придётся раскрыть в правилах**, и обеспечить Роскомнадзору
   доступ к программно-техническим средствам в 10 дней.
6. **top-k на практике реализуется через температуру τ, а для списка — через Plackett–Luce
   (Gumbel-softmax)** (§Д1.6). Для |A| = 66 преимущество top-k над softmax, доказанное
   Douglas et al. на |A| = 100 000, не гарантировано — проверять симуляцией.

### Д5.3 🔴 Опровергнуто или изменено

1. 🔴 **«SNIPS — основной оценщик на малых данных» (И2) — НЕВЕРНО как правило.**
   Первая редакция взяла это из одной фразы отчёта Adyen. Бенчмарк на реальных продовых данных
   ZOZO при n = 10 000: SNIPW проигрывает **DM** во всех трёх кампаниях (1,641 против 0,797;
   3,661 против 3,041; 3,038 против 2,665, §Д1.2).
   **Новая формулировка:** считать весь ряд оценщиков (DM, IPW, SNIPW, DR, SNDR, SWITCH-DR,
   DRos) и выбирать процедурой Su et al. `argmin_θ [BiasUB(θ)² + V̂ar(θ)]` (§Д1.1, Теорема 3:
   результат не хуже лучшего несмещённого из списка с точностью до C·log(|Θ|/δ)/n^{3/2}).
   Заранее ожидать победу DM на малых данных и DRos на больших, а не SNIPS.
2. 🔴 **«Постфактум не чинится» — опровергнуто КАК КАТЕГОРИЧЕСКОЕ утверждение.**
   Strehl, Langford, Li, Kakade (NIPS 2010, §Д2.1) восстанавливают эффект из логов, где
   «**no randomization occurred or was logged**», подменяя рандомизацию в алгоритме
   рандомизацией в мире (политика меняется во времени).
   **Новая формулировка, честная:** без записанного propensity оценка возможна при пяти
   условиях (мир i.i.d.; политика менялась во времени; π_t не зависят от оценочных данных;
   согласие на смещение от порога τ, занижающее ценность редких действий; высокая точность π̂).
   С записанным propensity она несмещена по построению и стоит ноль. Разница — не «можно/нельзя»,
   а «дёшево и точно» против «дорого, с оговорками и задним числом».
   🔴 **Но необратимый ущерб всё равно существует, просто он в другом месте:** дефицит
   перекрытия (Sachdeva et al., §Д1.3) даёт субоптимальность (r_max − r_min)·max D_X(π|π₀)
   **«in the limit of infinite training data»** — то есть НЕ лечится ни объёмом данных,
   ни клиппингом, ни умным оценщиком. Правильная редакция вывода темы 37:
   **«необратимо теряется не propensity, а ПЕРЕКРЫТИЕ: альтернативы, которые система никогда
   не показывала, оценить нельзя никогда».**
3. 🔴 **«Рандомизации достаточно» — опровергнуто.** Bareinboim, Forney, Pearl (§Д2.2):
   рандомизированный эксперимент даёт P(y|do(X)) = 0,30 против 0,30 («разницы нет»), тогда как
   политика по намерению пользователя выигрывает. **Следствие — новое требование к продукту:
   логировать намерение пользователя ДО показа рекомендации** (сущность `user_intent_snapshot`,
   §Д1.7). Это ровно тот класс «невосстановимо постфактум», и в первой редакции его не было.
4. 🔴 **§И4 п. 1 «Abadie (2021) НЕ ДОБЫТ» — запись неверна, работа открыта.** Она лежит
   в MIT DSpace под CC BY-NC (§Д4.1). Первая редакция не спросила Unpaywall. **Урок метода:
   пейволл издателя и доступность работы — разные вещи.** Плюс рабочий приём: DSpace 7 отдаёт
   405 на `/bitstreams/<uuid>/download` и 200 на `/server/api/core/bitstreams/<uuid>/content`.
5. **Клиппинг Bottou «R = пятое по величине отношение» (§1.1) — не отдельный приём, а частный
   случай SWITCH с r̂ ≡ 0** (§Д1.1, Wang et al.). Значит вместо ручного R правильнее сразу
   брать SWITCH-DR с автоподбором τ по `argmin (V̂ar_τ + B̂ias²_τ)`.

### Д5.4 ⬜ Осталось недобытым — и что именно вернул отказ

| Что | Канал и КОД возврата | Влияние |
|---|---|---|
| **Freedman 1987, полный текст** (5 стр. NEJM) | Unpaywall: `is_oa=false`, `oa_status=closed`, `best_oa_location=null`, `oa_locations=[]`, `has_repository_copy=false`. Semantic Scholar: `openAccessPdf.status=CLOSED`, abstract «elided by the publisher». med.mcgill.ca — код **000**. PubMed — HTTP **203** (антибот). hdl.handle.net/10822/819907 — HTTP **404**. fatcat — пустой ответ. EuropePMC `resultType=core` — HTTP 200, **полный авторский abstract дословно** | Низкое: каноническая формулировка clinical equipoise целиком содержится в добытом abstract |
| **Radcliffe 2007 (первоисточник Qini)** | Direct Marketing Analytics Journal, вне открытого доступа; в прошлой выдаче не обнаружен | Нулевое: формула проверена по Belbahri et al. (§Д4.2) и совпала |
| **Первоисточник «выученный propensity неидентифицируем»** | OpenAlex, HTTP 200, 6 результатов — **ни один по теме** (AHRQ-регистр, InstructGPT, денежная политика, микроэконометрика, R&D, медстрахование). WebSearch 400/400. Exa — сервер 404 | Среднее. 🔴 Строгого доказательства неидентифицируемости в добытых текстах НЕТ. Есть точная формула смещения через неизвестную величину (Теорема 1 Дудика). **В научный текст писать вторую формулировку, не первую** |
| **Цитата «propensity after all rules and gating»** | Повторно не искал, бюджет ушёл на Д1–Д2 | Низкое: следует из Bottou §4.3 и Definition 1 Sachdeva. Излагать своими словами, не цитировать |
| **FCA Consumer Duty (PS22/9, FG22/5, PRIN 2A), CFPB, DSA ст. 40, EU AI Act, корпоративный IRB** | Каналы не пробовались — бюджет подагента (16 из 18 вызовов) | Среднее: зарубежный контур закрыт наполовину (DSA ст. 25 и 27 добыты дословно) |
| **353-ФЗ, 38-ФЗ о рекламе, ЗоЗПП, 135-ФЗ/ФАС, подзаконный акт Роскомнадзора о содержании информации** (на него ссылается сама ст. 10.2-2 ч. 1 п. 2) | не проверялись — бюджет | Среднее: отрицательный вывод «прямого регулирования A/B в РФ нет» опирается на 6 проверенных норм, но не исчерпывающий |
| **Российская практика причинной оценки эффекта финтех-продуктов** | не искал (пробел сохраняется с первой редакции) | Среднее для научного текста: все полевые эксперименты в отчёте — США и Германия |
| **22-МР по официальной публикации cbr.ru** | garant — 403, угаданный URL PDF — 404; текст добыт с зеркала normativ.kontur.ru | Низкое, но при юридическом использовании сверить обязательно |

### Д5.5 Метод добора — точные числа

- **WebSearch: 0 вызовов.** Бюджет сессии исчерпан до начала добора (отдавал «this session has
  used its web search budget (400 of 400)»). Проверено одним вызовом, дальше не тратилось.
- **Exa: недоступна** (сервер отвечает 404) — не использовалась.
- **`r.jina.ai`: не использовался** — в этой сессии отдаёт 401 (🔴 отличие от первого прогона,
  где прокси пробивал антибот; фиксирую как изменение обстановки).
- **Подагентов: 2, последовательно, не веером.** Первый (правовой участок) упал по лимиту
  аккаунта, не успев записать файл, — **подтверждение правила «сырьё в файл ДО ответа»
  ценой одного захода**. Второй, перезапущенный с жёстким требованием писать файл после первой
  же цитаты, отработал: 16 вызовов, файл 290 строк, свои подагенты 0.
- **Основной канал: `curl` с браузерным UA + `pdftotext -layout`.** Так добыты целиком
  12 источников: Dudík–Langford–Li, Wang–Agarwal–Dudík, Su et al., Saito et al. (OBP),
  Swaminathan–Joachims (SNIPS), Swaminathan–Joachims (CRM), Sachdeva et al., Strehl et al.,
  Tchetgen Tchetgen et al., Bareinboim et al., Belbahri et al., Owen гл. 9, плюс исходный код
  `obp/policy/offline.py` и Abadie (2021).
- **Unpaywall: 1 применение, 1 успех** — и именно оно закрыло источник, полтора суток
  числившийся недобытым. 🔴 Добавить Unpaywall в штатный список каналов.
- **EuropePMC `resultType=core`: 1 применение, 1 успех** — отдал полный авторский abstract
  наглухо закрытой статьи NEJM, когда пять других каналов вернули closed/404/203/000.
  🔴 Второй канал, который надо записать в штатные.
- **DSpace 7: 405 на `/bitstreams/<uuid>/download`, 200 на `/server/api/core/bitstreams/<uuid>/content`.**
  Приём переносимый на любой репозиторий на DSpace 7.
- **Новых первоисточников добыто: 14.** Источники P–AA плюс Abadie (2021).

### Д5.6 Что менять в И1/И2 — короткий список для исполнения

1. Добавить в `recommendation_impressions` шесть полей: `rng_seed`, `propensity_semantics`,
   `propensity_method`, `propensity_mc_samples`, `support_divergence`, `logging_temperature` (§Д1.7).
2. Завести сущность **`user_intent_snapshot`** — намерение пользователя ДО показа рекомендации
   (§Д1.7, обоснование §Д2.2). Это продуктовое изменение, не только аналитическое.
3. Переписать в И2 фразу про SNIPS: считать весь ряд оценщиков, выбирать по `BiasUB² + V̂ar`.
4. Поставить в регламент анализа две проверки: **w̄ ≈ 1** и **n_e = (Σw)²/Σw² против n**
   (плюс n_{e,σ} для доверия интервалу).
5. Посчитать n*_e = n/E_p(w) на симуляции ДО релиза — это и есть наш расчёт мощности (§Д1.5).
6. Механизм выбора сделать чистой функцией от (контекст, конфиг, seed); seed писать в лог.
7. 🔴 Правовое: подготовить **документ «Правила применения рекомендательных технологий»**
   по ч. 2 ст. 10.2-2 149-ФЗ, и включить в него описание exploration-ветки как «способа
   осуществления процессов и методов». Конфигурация exploration должна быть предъявляемой
   Роскомнадзору в 10 дней (ч. 4).
8. Задать порог equipoise машинно: exploration включается **только когда разрыв SAW-оценок
   внутри показываемой верхушки лежит в пределах неопределённости модели**, и автоматически
   выключается, когда преимущество установлено (обязанность из Freedman 1987).

---

**Статус темы 37 после добора: ЗАВЕРШЕНО, добор выполнен.** Недобытое перечислено в §Д5.4
с кодами возврата. Все числа в разделах Д1–Д5 сверены с PDF/исходным текстом, не с пересказом
`WebFetch`.

---

# ПЕРЕПРОВЕРКА Д4 С ПОИСКОМ (2026-09-11)

Задание: перепроверить правовую и регуляторную часть добора Д4 (шёл с мёртвым WebSearch 400/400),
участки П4.1–П4.6. Подагентов: 0 (вся работа — лидером, последовательно). Каналы и коды — у каждой нормы.
Разделы дописываются по ходу, по одному на участок.

## ПЕРЕПРОВЕРКА Д4 С ПОИСКОМ — П4.1 EU AI Act и DSA

### Журнал добычи (11.09.2026)
| Документ | URL | Канал | HTTP | Размер |
|---|---|---|---|---|
| AI Act, Регламент (ЕС) 2024/1689, OJ-текст | `http://publications.europa.eu/resource/celex/32024R1689` (Accept: application/xhtml+xml) | curl -sk --http1.1 | 200 | 1 262 391 байт HTML → 585 354 симв. текста |
| (EUR-Lex HTML того же текста) | `eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32024R1689` | curl | **202, 0 байт** (антибот-заглушка); с `OJ:L_202401689` — 202, 2 035 байт | — |
| Digital Omnibus on AI, Регламент (ЕС) **2026/1744** от 08.07.2026, OJ L 24.7.2026 | `http://publications.europa.eu/resource/celex/32026R1744` | curl | 200 | 351 287 байт → 148 345 симв. |
| DSA, Регламент (ЕС) 2022/2065 | `http://publications.europa.eu/resource/celex/32022R2065` | curl | 200 | 838 166 байт → 416 879 симв. (EUR-Lex HTML — 202, 0 байт) |
| Руководство Комиссии по запрещённым практикам, C(2025) 5052 final (29.07.2025; первая редакция C(2025) 884, 04.02.2025) | `ai-act-service-desk.ec.europa.eu/sites/default/files/2025-08/guidelines_on_prohibited_artificial_intelligence_practices_established_by_regulation_eu_20241689_ai_act_english_ied3r5nwo50xggpcfmwckm3nuc_112367-1.PDF` | curl + pdftotext -layout | 200 | 1 204 912 байт PDF, 6 361 строка |
| Руководство Комиссии по определению «AI system» | `ai-act-service-desk.ec.europa.eu/sites/default/files/2025-08/commission_guidelines_on_the_definition_of_an_artificial_intelligence_system_established_by_regulation_eu_20241689_ai_actenglish_nf2skcqfrtjdfggjavcodopcwz4_112455.PDF` | curl + pdftotext | 200 | 333 765 байт, 591 строка |
| ПРОЕКТ руководства Комиссии по классификации high-risk, часть «Annex III» (опубл. 19.05.2026, консультация до 23.07.2026) | `https://ec.europa.eu/newsroom/dae/redirection/document/128561` (ссылка со страницы `digital-strategy.ec.europa.eu/en/library/draft-commission-guidelines-classification-high-risk-ai-systems`) | curl + pdftotext | 200 | 1 547 742 байт PDF, 148 стр., 7 669 строк |
| Сервис-деск AI Act, Annex III | `ai-act-service-desk.ec.europa.eu/en/ai-act/annex-3` | WebFetch | — | пересказ, сверен с OJ-текстом ниже |

Приём: EUR-Lex HTML отдаёт 202/0 байт (антибот), а **Publications Office `publications.europa.eu/resource/celex/<CELEX>` с `Accept: application/xhtml+xml` отдаёт тот же OJ-текст с HTTP 200** — переносимо на любой акт ЕС.
WebSearch по участку: 7 вызовов, отказов бюджета нет.

### A. AI Act — дословно

**Ст. 3 п. 1 (определение):** «‘AI system’ means a machine-based system that is designed to operate with varying levels
of autonomy and that may exhibit adaptiveness after deployment, and that, for explicit or implicit objectives, infers,
from the input it receives, how to generate outputs such as predictions, content, recommendations, or decisions that can
influence physical or virtual environments;»

**Ст. 5 п. 1 (a):** «the placing on the market, the putting into service or the use of an AI system that deploys
subliminal techniques beyond a person’s consciousness or purposefully manipulative or deceptive techniques, with the
objective, or the effect of materially distorting the behaviour of a person or a group of persons by appreciably impairing
their ability to make an informed decision, thereby causing them to take a decision that they would not have otherwise
taken in a manner that causes or is reasonably likely to cause that person, another person or group of persons
significant harm;»

**Ст. 5 п. 1 (b):** «the placing on the market, the putting into service or the use of an AI system that exploits any of
the vulnerabilities of a natural person or a specific group of persons due to their age, disability or a specific social
or economic situation, with the objective, or the effect, of materially distorting the behaviour of that person or a
person belonging to that group in a manner that causes or is reasonably likely to cause that person or another person
significant harm;»

**Ст. 5 п. 8:** «This Article shall not affect the prohibitions that apply where an AI practice infringes other Union law.»

**Сообр. 29 (выдержки):** «...whereby significant harms, in particular having sufficiently important adverse impacts on
physical, psychological health or financial interests are likely to occur, are particularly dangerous and should therefore
be prohibited.» / «...a specific social or economic situation that is likely to make those persons more vulnerable to
exploitation such as persons living in extreme poverty...» / «In any case, it is not necessary for the provider or the
deployer to have the intention to cause significant harm, provided that such harm results from the manipulative or
exploitative AI-enabled practices.» / «...common and legitimate commercial practices, for example in the field of
advertising, that comply with the applicable law should not, in themselves, be regarded as constituting harmful
manipulative AI-enabled practices.»

**Ст. 6 п. 2:** «In addition to the high-risk AI systems referred to in paragraph 1, AI systems referred to in Annex III
shall be considered to be high-risk.»
**Ст. 6 п. 3 (дерогация):** «By derogation from paragraph 2, an AI system referred to in Annex III shall not be considered
to be high-risk where it does not pose a significant risk of harm to the health, safety or fundamental rights of natural
persons, including by not materially influencing the outcome of decision making.» — при условиях (a) narrow procedural
task; (b) improve the result of a previously completed human activity; (c) detect decision-making patterns...; (d)
«perform a preparatory task to an assessment relevant for the purposes of the use cases listed in Annex III».
🔴 «Notwithstanding the first subparagraph, an AI system referred to in Annex III shall always be considered to be
high-risk where the AI system performs profiling of natural persons.»
**Ст. 6 п. 4:** провайдер, считающий систему из Annex III не высокорисковой, «shall document its assessment before that
system is placed on the market» и подлежит регистрации по ст. 49(2).

**Приложение III п. 5 (b):** «AI systems intended to be used to evaluate the creditworthiness of natural persons or
establish their credit score, with the exception of AI systems used for the purpose of detecting financial fraud»
(сверено: сервис-деск и OJ-текст совпадают).
**Сообр. 58:** «...AI systems used to evaluate the credit score or creditworthiness of natural persons should be
classified as high-risk AI systems, since they determine those persons’ access to financial resources or essential
services such as housing, electricity, and telecommunication services.»

**Ст. 10 п. 1–2 (данные):** «1. High-risk AI systems which make use of techniques involving the training of AI models
with data shall be developed on the basis of training, validation and testing data sets that meet the quality criteria
referred to in paragraphs 2 to 5 whenever such data sets are used. 2. Training, validation and testing data sets shall be
subject to data governance and management practices appropriate for the intended purpose... (a) the relevant design
choices; (b) data collection processes and the origin of data, and in the case of personal data, the original purpose of
the data collection; (c) relevant data-preparation processing operations...» (Omnibus 2026/1744, ст. 1 п. 9, заменил п. 1 —
ссылка теперь на «paragraphs 2, 3 and 4 of this Article and in Article 4a(1)».)
**Ст. 12 п. 1–2 (логи):** «1. High-risk AI systems shall technically allow for the automatic recording of events (logs)
over the lifetime of the system. 2. ... logging capabilities shall enable the recording of events relevant for: (a)
identifying situations that may result in the high-risk AI system presenting a risk ... or in a substantial modification;
(b) facilitating the post-market monitoring referred to in Article 72; and (c) monitoring the operation of high-risk AI
systems referred to in Article 26(5).»
**Ст. 14 п. 1 (надзор человека):** «High-risk AI systems shall be designed and developed in such a way, including with
appropriate human-machine interface tools, that they can be effectively overseen by natural persons during the period in
which they are in use.»

**🔴 Ст. 60–61 — «testing in real world conditions» (в своде темы 37 не упоминались вовсе).**
Ст. 60 п. 1: «Testing of high-risk AI systems in real world conditions outside AI regulatory sandboxes may be conducted by
providers or prospective providers of high-risk AI systems listed in Annex III, in accordance with this Article and the
real-world testing plan referred to in this Article, without prejudice to the prohibitions under Article 5.»
Ст. 60 п. 4 — условия (выдержки): план испытаний подан и одобрен органом рыночного надзора; срок «not longer than six
months, which may be extended for an additional period of six months»; «the subjects of the testing in real world
conditions who are persons belonging to vulnerable groups due to their age or disability, are appropriately protected»;
«the subjects of the testing in real world conditions have given informed consent in accordance with Article 61».
Ст. 60 п. 5: субъекты «may, without any resulting detriment and without having to provide any justification, withdraw
from the testing at any time». Ст. 61 п. 1: «freely-given informed consent shall be obtained from the subjects of testing
prior to their participation in such testing and after their having been duly informed...». Ст. 3: «‘informed consent’
means a subject’s freely given, specific, unambiguous and voluntary expression of his or her willingness to participate
in a particular testing in real-world conditions...».
Чтение (вывод, не цитата): это режим ДО вывода на рынок и только для high-risk; A/B после вывода на рынок этой статьёй
не описан. Но это единственная найденная в ЕС норма, где эксперимент на людях с ИИ-системой прямо требует
информированного согласия.

**Ст. 113 (даты) — в редакции Omnibus 2026/1744, ст. 1 п. 40:**
«(a) Chapters I and II shall apply from 2 February 2025, with the exception of Article 5(1), first subparagraph, points
(ba) and (bb), and Article 5(1a) and (1b) which shall apply from 2 December 2026;»
«(c) Chapter III, Sections 1, 2, and 3, with the exception of Article 6(5), shall apply from: (i) 2 December 2027 as
regards AI systems classified as high-risk pursuant to Article 6(2) and Annex III; and (ii) 2 August 2028 as regards AI
systems classified as high-risk pursuant to Article 6(1) and Annex I;»
Исходная редакция 2024 г.: общая дата — 2 August 2026; ст. 6(1) — 2 August 2027. Новые пп. (ba), (bb) ст. 5 —
про интимные дипфейки и CSAM, к нам не относятся. Ст. 5(1)(a),(b) действуют с 02.02.2025 без изменений.

### B. Руководства Комиссии (не обязательны, но это официальное толкование)

**Определение AI system:** п. 26: AI-системы отличаются от «simpler traditional software systems or programming approaches
and should not cover systems that are based on the rules defined solely by natural persons to automatically execute
operations.» П. 42: «Systems used to improve mathematical optimisation or to accelerate and approximate traditional, well
established optimisation methods, such as linear or logistic regression methods, fall outside the scope of the AI system
definition.» П. 46: «Basic data processing system refers to a system that follows predefined, explicit instructions or
operations... They operate based on fixed human-programmed rules, without using AI techniques, such as machine learning or
logic-based inference, to generate outputs.» П. 48 (classical heuristics) и п. 49 (simple prediction systems) — тоже вне
определения. (стр. 8–9 PDF)
🔶 Вывод (не цитата): детерминированное ядро SAW с фиксированными весами + Avalanche + SES/Монте-Карло с высокой
вероятностью подпадает под «rules defined solely by natural persons» / «well established optimisation methods» и
**вообще не является AI system** в смысле ст. 3(1). Это ломается в момент, когда веса/политику начнут учить по логам
(контекстный бандит, uplift-модель, обучаемая политика из темы 37) — тогда определение ст. 3(1) выполняется.
Сноска 6 там же: системы, выведенные на рынок до 02.08.2026, пользуются «grandfathering» ст. 111(2).

**Запрещённые практики (C(2025) 5052), п. 128, стр. 40–41:** «Manipulation involves, in most cases, covert techniques
undermining autonomy... By contrast, persuasion operates within the bounds of transparency and respect for individual
autonomy. It involves presenting arguments or information in a way that appeals to reason and emotions, but explains the
AI system’s objectives and functioning, provide relevant and accurate information to ensure informed decision-making...»
«For example, an AI system using personalised recommendations based on transparent algorithms and user preferences and
controls engages in persuasion.»
П. 130: «In persuasive interactions, individuals are aware of the influence attempt and can freely and autonomously choose
it. In manipulative interactions, the lack of awareness of the techniques or their impact negates the freedom of choice».
П. 133 (стр. 42): «AI systems used for providing banking services, such as mortgages and loans, that use the age or the
specific socio- economic situation of the client as an input, in compliance with Union legislation ... do not qualify as
the exploitation of vulnerabilities within the meaning of Article 5(1)(b) AI Act when they are designed to protect and
support people identified as vulnerable...» Отдельный пример там же: техники, чтобы «push people to take significantly
harmful financial decisions». Прямо про A/B-тесты — grep «A/B» по 6 361 строке: 0 вхождений.

**ПРОЕКТ руководства по high-risk, Annex III (19.05.2026):**
П. 296: «The evaluation of creditworthiness refers to the assessment of a natural person’s ability and willingness to
fulfil its contractual obligations to pay for the services provided or the credit granted.»
П. 302: из финуслуг «essential» только: bank account; payment services; «the offering of loans and credit; the offering
of extension of a credit line or of credit card limit; the offering of mortgage; and public financial services».
П. 304: не essential — «stocks and securities; ... margin trading; ... complex financial instruments; premium credit
cards; and special loans, such as leisure/travel loans».
Примеры ВНЕ п. 5(b) (стр. 88): «An AI system intended to classify customers, for example, to fulfil information
obligations, to provide tailored information to customers, to assess the suitability of a product or to make personalised
marketing offers, so long as the classification does not play a part in the assessment of the creditworthiness of a
natural person.» и «AI systems intended for customer support related to the assessment of their creditworthiness ...
may assist applicants in understanding or completing the credit application form ... or provide dynamic feedback on how
specific answers may influence the likelihood of approval. If they are not intended to be used as part of the
creditworthiness assessment or credit-scoring process ... they fall outside the use case of point 5(b).»
П. 75: «split architectures are assessed as a whole» — если выход компонента материально влияет на индивидуальное
решение, связка оценивается как одна система.
grep по 7 669 строкам: «debt» — 0 по теме, «budget» — 1 (логистика), «advice» — только voter advice. **Прямого примера
«советчик по погашению долгов / PFM» в проекте нет.**

**Ответ на вопрос П4.1 (вывод, не цитата).** Советующий по долгам сервис, адресованный самому пользователю, по тексту
п. 5(b) и проекту руководства **не является** оценкой кредитоспособности: он не оценивает «ability and willingness to
fulfil contractual obligations» в целях доступа к кредиту; ближайшие аналоги в примерах — «tailored information to
customers» и «customer support», оба ВНЕ 5(b). Высокий риск возникает в одном сценарии: **B2B, если банк использует наш
выход (ПДН, «рекомендуемый» лимит заимствования) в своём решении о выдаче/лимите** — тогда по п. 75 связка оценивается
целиком, а профилирование (ст. 6(3) последний абз.) закрывает дерогацию. Даты: с 02.12.2027 (Omnibus).

### C. DSA — сверка ссылки свода темы 37

**Ст. 3 (i):** «‘online platform’ means a hosting service that, at the request of a recipient of the service, stores and
disseminates information to the public, unless that activity is a minor and purely ancillary feature of another
service...». **Ст. 3 (s):** «‘recommender system’ means a fully or partially automated system used by an online platform to
suggest in its online interface specific information to recipients of the service...».
**Ст. 25 п. 1** (текст в §4.1 Д3 сверен — совпадает): «Providers of online platforms shall not design, organise or operate
their online interfaces in a way that deceives or manipulates ...». **Ст. 25 п. 2:** «The prohibition in paragraph 1 shall
not apply to practices covered by Directive 2005/29/EC or Regulation (EU) 2016/679.»
**Ст. 19 п. 1:** «This Section, with the exception of Article 24(3) thereof, shall not apply to providers of online
platforms that qualify as micro or small enterprises as defined in Recommendation 2003/361/EC.» (ст. 25 и 27 — в этой
секции: Глава III, Раздел 3.)
**Ст. 38:** «In addition to the requirements set out in Article 27, providers of very large online platforms and of very
large online search engines that use recommender systems shall provide at least one option for each of their recommender
systems which is not based on profiling...». **Ст. 33 п. 1:** VLOP — «equal to or higher than 45 million» среднемесячных
активных получателей в ЕС.
**Ст. 40 п. 1, 3, 4:** доступ к данным — только VLOP/VLOSE; п. 3: «explain the design, the logic, the functioning and the
testing of their algorithmic systems, including their recommender systems»; п. 4: доступ «vetted researchers ... for the
sole purpose of conducting research that contributes to the detection, identification and understanding of systemic
risks». **Ст. 93 п. 2:** DSA применяется с 17.02.2024.

🔴 **Ссылка свода темы 37 (раздел 5 п. 4: «нарушает ... ст. 25 DSA») по тексту НЕКОРРЕКТНА как утверждение
о применимости.** Ст. 25 адресована только «providers of online platforms», а платформа по ст. 3(i) — хостинг, который
хранит и распространяет информацию пользователей «to the public». FINPILOT (персональный советник без публикации
пользовательского контента) онлайн-платформой не является, и ст. 25/27 его не связывают. Даже для платформ ст. 25(2)
отсылает практики, покрытые UCPD 2005/29/EC и GDPR, к этим актам, а ст. 19 освобождает микро- и малые предприятия.
Для B2C-сервиса в ЕС рамка про манипулятивный интерфейс — **UCPD 2005/29/EC + GDPR + ст. 5(1)(a),(b) AI Act**
(последняя — если система является AI system), а не DSA. Правильная формулировка: «ст. 25 DSA — ориентир формулировки
(что считается манипулятивным дизайном), а не применимая норма». Цитата сама по себе верна (сверена дословно).
Ст. 38 и 40 — только VLOP (≥45 млн), к нам не относятся ни при каком сценарии.

## ПЕРЕПРОВЕРКА Д4 С ПОИСКОМ — П4.2 CFPB

### Журнал добычи (11.09.2026)
| Документ | URL | Канал | HTTP | Размер |
|---|---|---|---|---|
| CFPB Circular 2023-01 «Unlawful negative option marketing practices», 19.01.2023 | `files.consumerfinance.gov/f/documents/cfpb_unlawful-negative-option-marketing-practices-circular_2023-01.pdf` | WebFetch (PDF не разобран, сохранён на диск) → pdftotext -layout | — | 195,1 КБ PDF, 389 строк |
| Federal Register 90 FR 20084 (12.05.2025), FR Doc 2025-08286 «Interpretive Rules, Policy Statements, and Advisory Opinions; Withdrawal» | `federalregister.gov/documents/full_text/text/2025/05/12/2025-08286.txt` (URL из API `federalregister.gov/api/v1/documents/2025-08286.json`) | curl | 200 | 21 969 байт |
| 12 U.S.C. §5481 (определения CFPA) | `law.cornell.edu/uscode/text/12/5481` | curl | 200 | 160 811 байт |
| 12 U.S.C. §5531 (UDAAP) | `law.cornell.edu/uscode/text/12/5531` | curl | 200 | 45 718 байт |
| (uscode.house.gov — те же разделы) | `uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title12-section5481...` | curl | **000, 0 байт**, таймаут 120 с, exit 35 (TLS) | — |
| 12 CFR §1033.421 (Section 1033, обязанности третьих лиц) | `ecfr.gov/api/versioner/v1/full/2026-09-01/title-12.xml?part=1033&section=1033.421` | curl `--compressed` (без него — 406 «requires response compression») | 200 | 2 635 байт (gzip) → 8 276 симв. |
| Статус правила 1033 | `cozen.com/news-resources/publications/2026/section-1033-compliance-date-open-banking-rule-enjoined-and-under-reconsideration` (09.04.2026) | WebFetch | — | пересказ |

WebSearch по участку: 5 вызовов.

### A. 🔴 Главное: советующий по долгам сервис в США — это «consumer financial product or service»

**12 U.S.C. §5481(15)(A)(viii)** (дословно): «providing financial advisory services (other than services relating to
securities provided by a person regulated by the Commission or a person regulated by a State securities Commission, but
only to the extent that such person acts in a regulated capacity) to consumers on individual financial matters or
relating to proprietary financial products or services (other than by publishing any bona fide newspaper, news magazine,
or business or financial publication of general and regular circulation, including publishing market data, news, or data
analytics or investment information or recommendations that are not tailored to the individual needs of a particular
consumer), including— (I) providing credit counseling to any consumer; and (II) providing services to assist a consumer
with debt management or debt settlement, modifying the terms of any extension of credit, or avoiding foreclosure;»
**§5481(6):** «The term “covered person” means— (A) any person that engages in offering or providing a consumer financial
product or service; ...»

Чтение (вывод): FINPILOT в США был бы **covered person** по закону, без всякой лицензии и без продажи продукта —
«financial advisory services ... on individual financial matters ... including ... debt management». Исключение
«recommendations that are not tailored to the individual needs of a particular consumer» к нам неприменимо: наша
рекомендация персональная. Значит на нас прямо распространяется запрет UDAAP (§5531, §5536). Это прямой аналог
вывода Д14 по UK (PERG 17, debt counselling), только в США это не лицензия, а подпадание под надзорный закон.

**12 U.S.C. §5531(d) — «abusive» (дословно):** «The Bureau shall have no authority under this section to declare an act
or practice abusive in connection with the provision of a consumer financial product or service, unless the act or
practice— (1) materially interferes with the ability of a consumer to understand a term or condition of a consumer
financial product or service; or (2) takes unreasonable advantage of— (A) a lack of understanding on the part of the
consumer of the material risks, costs, or conditions of the product or service; (B) the inability of the consumer to
protect the interests of the consumer in selecting or using a consumer financial product or service; or (C) the
reasonable reliance by the consumer on a covered person to act in the interests of the consumer.»

🔴 Чтение для exploration (вывод, не цитата CFPB): п. (d)(2)(C) — **ровно та граница, которую свод темы 37 выводил
из Freedman**. Пользователь советующего сервиса по определению полагается на то, что совет — в его интересах.
Показ под видом рекомендации альтернативы, о худшести которой система знает, ради данных для оценки — кандидат
на «takes unreasonable advantage of ... the reasonable reliance by the consumer on a covered person to act in the
interests of the consumer». Это статутная норма, не отозванное руководство, и она сильнее этического аргумента.
Прямой позиции CFPB по A/B-тестам (circular, bulletin, report) не найдено — см. ниже.

### B. Dark patterns — Circular 2023-01 (дословно) и 🔴 его отзыв

Circular 2023-01, «Response»: «Yes. “Covered persons” and “service providers” must comply with the prohibition on unfair,
deceptive, or abusive acts or practices in the CFPA. Negative option marketing practices may violate that prohibition
where a seller (1) misrepresents or fails to clearly and conspicuously disclose the material terms of a negative option
program; (2) fails to obtain consumers’ informed consent; or (3) misleads consumers who want to cancel, erects
unreasonable barriers to cancellation, or fails to honor cancellation requests...» (стр. 1).
Стр. 3: «Recently, the CFPB and FTC have taken action to combat the rise of digital dark patterns, which are design
features used to deceive, steer, or manipulate users into behavior that is profitable for a company, but often harmful
to users or contrary to their intent.» Стр. 4 (Consent): «Consent will generally not be informed if, for example, a
seller mischaracterizes or conceals the negative option feature, provides contradictory or misleading information, or
otherwise interferes with the consumer’s understanding of the agreement.»

🔴 **90 FR 20084 (12.05.2025), «The withdrawals are applicable as of May 12, 2025».** В перечне отозванного
(стр. 20086, дословно по пунктам):
- Policy Statements, п. 3: «Statement of Policy Regarding Prohibition on Abusive Acts or Practices, 88 FR 21883 (Apr. 12, 2023).»
- Interpretive Rules, п. 2: «Limited Applicability of Consumer Financial Protection Act's `Time or Space' Exception to
  Digital Marketers, 87 FR 50556 (Aug. 17, 2022).»
- Circulars, п. 9: «Consumer Financial Protection Circular 2023-01: Unlawful negative option marketing practices, 88 FR
  5727 (Jan. 30, 2023).»
Всего отозвано 67 документов (8 policy statements, 7 interpretive rules, 13 advisory opinions, 39 прочих — по
пересказу Holland & Knight / Consumer Finance Monitor; сам перечень в FR сверен по трём нужным пунктам).
Вывод: **документы CFPB о dark patterns и о цифровом маркетинге как «service provider» с 12.05.2025 — не действующая
позиция агентства.** Статут (§5531, §5536) при этом не изменился и продолжает применяться (в том числе генпрокурорами
штатов по §5552 — не проверялось в этом заходе). Цитировать Circular 2023-01 можно только как историческое толкование.

### C. Section 1033 — только часть про использование данных

**12 CFR §1033.421(a)** (действующая редакция eCFR на 01.09.2026, дословно): «(1) In general. The third party will limit its
collection, use, and retention of covered data to what is reasonably necessary to provide the consumer's requested
product or service. (2) Specific purposes. For purposes of paragraph (a)(1) of this section, the following are not part
of, or reasonably necessary to provide, any other product or service: (i) Targeted advertising; (ii) Cross-selling of
other products or services; or (iii) The sale of covered data.»
**§1033.421(c)(4)** — разрешённое использование: «Uses that are reasonably necessary to improve the product or service
the consumer requested.» §1033.421(b)(2) — сбор не дольше года после последней авторизации.
Чтение: если бы FINPILOT получал данные через 1033-доступ, **оценка эффекта рекомендаций и обучение политики
подпадают под (c)(4) «improve the product or service the consumer requested»**, а монетизация через кросс-продажи
или таргетированную рекламу — прямо нет.
Статус (Cozen, 09.04.2026, пересказ WebFetch): правило enjoined федеральным судом (E.D. Ky.), CFPB «prevented from
enforcing the rule» на время пересмотра; ANPR о пересмотре — 90 FR, 22.08.2025; дата 01.04.2026 не наступила
в обязательном смысле. Текст правила в eCFR остаётся опубликованным.

### D. Отрицательные результаты участка
- **Позиция CFPB именно об A/B-тестах/экспериментах на потребителях** — не найдена: WebSearch «CFPB A/B testing consumers
  experiments» выдал только interpretive rule 2022 о digital marketers (отозван, см. B). Сам CFPB проводил
  исследования с рандомизацией (Office of Research), но нормы-позиции для поднадзорных не выпускал — по выдаче не
  видно; утверждать «позиции нет» можно только как «не найдено в 5 поисках», не как доказанное отсутствие.
- **Отдельная позиция CFPB о «советующих» инструментах по долгам** — не найдена; есть только статутное определение
  §5481(15)(A)(viii) (выше) и потребительские страницы Ask CFPB о credit counseling / debt settlement.

## ПЕРЕПРОВЕРКА Д4 С ПОИСКОМ — П4.3 Корпоративные этические комитеты для A/B

### Журнал добычи (11.09.2026)
| Документ | URL | Канал | HTTP | Размер |
|---|---|---|---|---|
| PNAS Editorial Expression of Concern (Verma), 22.07.2014, PNAS 111(29):10779, doi 10.1073/pnas.1412469111, + Correction + сама статья Kramer et al. | `socialmedialab.sites.stanford.edu/.../kramer-pnas-experimental-evidence.pdf` | curl + pdftotext | 200 | 549 866 байт PDF, 283 строки |
| Jackman M., Kanerva L. «Evolving the IRB: Building Robust Review for Industry Research», 72 Wash. & Lee L. Rev. Online 442 (2016) | прямой `scholarlycommons.law.wlu.edu/cgi/viewcontent.cgi?article=1042&context=wlulr-online` | curl → **403** (Cloudflare «Just a moment»); r.jina.ai → 200, **240 байт — пустышка** с тем же 403 | — |
|  | `https://web.archive.org/web/2022id_/<тот же URL>` | curl | **200** | 451 354 байт PDF, 6+ стр. → 723 строки |
| Polonetsky J., Tene O., Jerome J. «Beyond the Common Rule: Ethical Structures for Data Research in Non-Academic Settings», 13 Colo. Tech. L.J. 333 (2015) | см. раздел «НЕ ДОБЫТО» ниже | — | — | — |
| Meyer M.N. et al. «Objecting to experiments that compare two unobjectionable policies or treatments», PNAS 116(22):10723 (2019), doi 10.1073/pnas.1820701116, PMC6561206, CC BY-NC-ND | `ebi.ac.uk/europepmc/webservices/rest/PMC6561206/fullTextXML` | curl | 200 | 86 264 байт XML |
| Polonioli A. et al. «The Ethics of Online Controlled Experiments (A/B Testing)», Minds & Machines (2023), doi 10.1007/s11023-023-09644-y | link.springer.com (HTML и /content/pdf/) | curl → 200, **3 038 байт** (заглушка); r.jina.ai → 200, 160 691 байт, 502 строки полного текста | — |

WebSearch по участку: 6 вызовов.

### A. Facebook 2014 — что последовало (дословно, PNAS 111(29):10779)
«Questions have been raised about the principles of informed consent and opportunity to opt out in connection with the
research in this paper. The authors noted in their paper, “[The work] was consistent with Facebook’s Data Use Policy, to
which all users agree prior to creating an account on Facebook, constituting informed consent for this research.” When
the authors prepared their paper for publication in PNAS, they stated that: “Because this experiment was conducted by
Facebook, Inc. for internal purposes, the Cornell University IRB [Institutional Review Board] determined that the
project did not fall under Cornell’s Human Research Protection Program.” This statement has since been confirmed by
Cornell University. Obtaining informed consent and allowing participants to opt out are best practices in most instances
under the US Department of Health and Human Services Policy for the Protection of Human Research Subjects (the “Common
Rule”). Adherence to the Common Rule is PNAS policy, but as a private company Facebook was under no obligation to conform
to the provisions of the Common Rule when it collected the data used by the authors, and the Common Rule does not preclude
their use of the data. ... It is nevertheless a matter of concern that the collection of the data by Facebook may have
involved practices that were not fully consistent with the principles of obtaining informed consent and allowing
participants to opt out.» — Inder M. Verma, Editor-in-Chief.
Чтение: юридически частная компания Common Rule не связана (это сказал сам журнал); последствие было репутационным
и институциональным — ответом стал внутренний процесс ревью (ниже), а не норма.

### B. 🔴 Внутренний процесс Facebook — первоисточник (Jackman & Kanerva 2016, стр. 451–455)
- **Обучение (стр. 451):** «...substantive area experts and members of the research review group—complete the National
  Institute of Health’s (NIH) human subjects training. The NIH training, however, is just a starting point.»
- **Первая ступень — руководитель по предмету (стр. 451–452):** «The senior managers of each research team ... provide the
  first review of research proposals. At this point in the process, the manager determines whether an expedited review
  (“standard review”) is appropriate, or whether the proposal should be referred to the cross-functional research review
  group (“extended review”).» / «...managers may refer a project to the research review group at any stage—not just at the
  project's inception.» / 🔴 «We do not have categories of research—including product improvements—that are automatically
  approved.» / «...research that also touches on privacy is considered by a separate privacy review group».
- **Вторая ступень — группа (стр. 452):** «The research review group consists of a standing committee of five, and
  includes experts in the substantive area of the research as well as law, ethics, communications, and policy.» / «Most of
  the research Facebook conducts relates to small product tests—for example, evaluating whether the size or placement of a
  comment box affects people’s engagement. The research area expert may expedite the review of these studies...» /
  «Once extended review has been triggered, we require consensus among all members of the group before the research
  proposal is approved.»
- **Внешний член (сн. 29):** «We have considered including an external member on our review board, following the IRB
  model. To this point, however, we have instead taken the approach of engaging external stakeholders on a case-by-case
  basis».
- **Четыре критерия (стр. 454–455):** (1) «how the research will improve our society, our community, and Facebook»;
  (2) «whether there are potentially adverse consequences that could result from the study, and whether every effort has
  been taken to minimize them. ... Our review pays attention to the impact of research focused on vulnerable populations
  (e.g., teen bullying) or sensitive topics (e.g., suicide prevention)»; (3) «whether the research is consistent with
  people’s expectations»; (4) «we ensure that we have taken appropriate precautions designed to protect people’s
  information».

### C. Эмпирика «A/B illusion» (Meyer et al. 2019, PNAS, дословно из абстракта)
«...people frequently rate A/B tests designed to establish the comparative effectiveness of two policies or treatments
as inappropriate even when universally implementing either A or B, untested, is seen as appropriate. This “A/B effect” is
as strong among those with higher educational attainment and science literacy and among relevant professionals. It
persists even when there is no reason to prefer A to B...» — 16 исследований, 5 873 участника, 9 областей.
Одно из объяснений из того же абстракта: «a belief that consent is required to impose a policy on half of a population
but not on the entire population». Вывод авторов: оценка через рандомизацию «may provoke greater objection than simply
implementing» (цитата оборвана в извлечённом тексте — дальше не цитирую). В тексте статьи: примеры Facebook, OkCupid,
Pearson как один паттерн; сама идея — Meyer M.N. (2015) «Two cheers for corporate experimentation: The A/B illusion and
the virtues of data-driven innovation», Colo Tech Law J 13:273–331 (тот же номер журнала, что и Polonetsky et al.; сам текст 2015 г. не добыт).
Значение для нас: даже этичный exploration в зоне equipoise **воспринимается хуже, чем любая из ветвей по отдельности**
— аргумент за раскрытие в правилах (ст. 10.2-2) именно в формулировке «мы сравниваем равноценные варианты», а не
«мы проводим эксперименты».

### D. Обзор отрасли (Polonioli et al. 2023, Minds & Machines, через r.jina.ai)
«While participant protection protocols are considered the norm in behavioral, medical, and social research, the
situation is different when it comes to company-sponsored A/B testing.» / §3.1: «Companies such as Microsoft and Meta
have been launching internal IRBs over the past years, but it is unclear to what extent these boards can be truly
independent (Wong & Floridi, 2023). The issue is especially relevant considering that the social contagion study
mentioned above was approved by Facebook’s IRB (Kramer, 2014)». Рамка статьи — четыре принципа Beauchamp & Childress;
про equipoise: «a user should partake in an A/B test only if there is uncertainty ... about which condition is most
likely...» (обрыв в извлечении). Уязвимые группы: «additional safeguards must be included in experiments involving
vulnerable subjects such as children, prisoners, pregnant women, mentally disabled persons, or econo[mically disadvantaged]».
🔶 Замечание: утверждение «исследование эмоционального заражения было одобрено IRB Facebook» у Polonioli —
**противоречит** хронологии Jackman & Kanerva (процесс описан как созданный ПОСЛЕ, по итогам 2014) и тексту PNAS
(там говорится об IRB Корнелла, не Facebook). Полагаться на эту фразу Polonioli не следует.

### E. Практика Microsoft, LinkedIn, Booking, Airbnb — первоисточников не найдено
3 поиска («LinkedIn Microsoft experimentation ethics review board», «Kohavi ... ethics minimal risk IRB», «ethics of
A/B testing financial services»): первоисточников с описанием процесса у Microsoft/LinkedIn/Booking/Airbnb нет.
Kohavi, Tang, Xu (2020) — по пересказу обзорных сайтов (не первоисточник) рекомендуют внутренний процесс,
аналогичный IRB, с эскалацией при более чем минимальном риске; главу не открывал — книга под копирайтом Cambridge.
По финтеху найдены только отраслевой блог GrowthBook и препринт на ResearchGate (не рецензируемый) —
не цитирую.

### F. Ответ: какой минимальный внутренний процесс одобрения считается нормой отрасли (вывод)
Единственный первоисточник, где отраслевой процесс описан изнутри, — Jackman & Kanerva. Из него «минимум»:
1. обучение всех, кто одобряет, по курсу защиты участников исследований (у них — NIH human subjects training);
2. двухступенчатый отбор: руководитель по предмету решает, хватает ли ускоренного ревью или нужно расширенное;
3. **никаких автоматически одобряемых категорий**, в том числе «улучшений продукта»;
4. расширенное ревью — постоянная кросс-функциональная группа (предмет + право + этика + коммуникации + политика),
   решение консенсусом, внешние эксперты по случаю;
5. отдельное ревью приватности;
6. четыре критерия: польза; вред и его минимизация (особо — уязвимые группы и чувствительные темы); соответствие
   ожиданиям людей; защита данных.
Для FINPILOT-масштаба перенос: пп. 2, 3, 6 и журнал решений; «группа из пяти» на старте — избыточна.
Норма отрасли ≠ правовая обязанность: PNAS прямо фиксирует, что Common Rule частную компанию не связывает.

### НЕ ДОБЫТО по П4.3
- **Polonetsky, Tene, Jerome (2015), полный текст.** scholar.law.colorado.edu viewcontent (article=1195) — curl **403**
  (Cloudflare), r.jina.ai — 200, **228 байт пустышка** с «Target URL returned error 403»; Wayback
  `web/2022id_/...` — **404**; archive.org availability API — **429 Too Many Requests** (дважды); SSRN
  `Delivery.cfm?abstractid=2621559` — **403**; SSRN-зеркало из OpenAlex (`...SSRN_ID2621559_code1513383.pdf...&mirid=2`)
  — **403**. OpenAlex: doi нет, OA-URL — только SSRN. Цитат из статьи не привожу. Косвенно: Jackman & Kanerva
  ссылаются на неё (сн. 2, «13 COLO. TECH. L.J. 333, 337 (2015)») как на обоснование того, что традиционных принципов
  приватности для корпоративных исследований недостаточно.
- **Meyer 2015 «Two cheers for corporate experimentation»** — не искался отдельно (бюджет участка).

## ПЕРЕПРОВЕРКА Д4 С ПОИСКОМ — П4.5 Freedman 1987, полный текст

### Журнал добычи (11.09.2026)
| Канал | URL | HTTP | Размер | Результат |
|---|---|---|---|---|
| WebSearch «Freedman "Equipoise and the ethics of clinical research" 1987 full text ...» | — | — | — | выдача: scispace, wikipedia, researchgate, ovid, scilit, nejm (abs), studocu, taylorfrancis (2 перепечатки главой) |
| curl ovid.com fulltext | `ovid.com/journals/nejm/fulltext/10.1056/nejm198707163170304~equipoise-and-the-ethics-of-clinical-research` | 200 | 135 465 байт HTML → **2 375 симв. текста** | **только тот же авторский абстракт**, полный текст за подпиской |
| curl studocu | `studocu.com/en-gb/document/glasgow-caledonian-university/clinical-research-methods-14/nejm-1987-freedman-equipoise-and-the-ethics-of-clinical-research/109629870` | **403** | 59 394 байт | Cloudflare |
| r.jina.ai studocu | то же | 200 | **378 байт** | пустышка «Verifying you are human» |
| Wayback `web/2025id_/<studocu>` | — | **404** | 5 013 байт | снимка нет |
| curl scispace | `scispace.com/papers/equipoise-and-the-ethics-of-clinical-research-4lfnppdyqq` | **202** | 0 байт | антибот |
| WebSearch «bios601 mcgill Freedman ... pdf» | — | — | — | зеркала McGill в выдаче нет; есть перепечатки главой у Taylor & Francis (10.4324/9781315244426-17, 10.4324/9781315198231-25) — за пейволлом, не пробовались |
| curl A.J. London «Two Dogmas of Research Ethics», J Med Philos 32 (2007) — **вторичный** источник | `cmu.edu/dietrich/philosophy/docs/london/London--2DogmasResearchEthics.pdf` | 200 | 153 366 байт PDF → 976 строк | разбор позиции Freedman со страницами журнала |

**Итог по полному тексту: НЕ ДОБЫТ.** Причины по каналам — в таблице. Дословная формулировка «обязанности прекратить»
со страницей не получена; цитирую только абстракт (как в §Д3 п. 2.1) и вторичный разбор.

### 🔴 Сверка свода раздела 5 п. 3 с абстрактом и вторичным источником
Свод (раздел 5 п. 3): «Рандомизация этична при genuine uncertainty на уровне экспертного сообщества, и обязана
прекращаться, как только превосходство одной ветви установлено». §Д3 п. 2.1, условие 3, строит «обязанность прекратить»
на фразе абстракта «Should the investigator discover that one treatment is of superior therapeutic merit, he or she is
ethically obliged to offer that treatment».
**Проблема прочтения.** В абстракте эта фраза стоит в изложении ПРИНЯТОГО понимания, которое Freedman затем
критикует: следующее предложение — «The current understanding of this requirement, which entails that the investigator
have no "treatment preference" throughout the course of the trial, presents nearly insuperable obstacles...», а затем
«I suggest an alternative concept of equipoise...». Вторичный разбор это подтверждает (London 2007, стр. 104–105,
дословно): «Freedman, in contrast, argues for a robust epistemic threshold according to which uncertainty exists so long
as there is a lack of consensus in the expert medical community about the relative therapeutic benefits of the set of
interventions.» и «...the charge that Freedman’s view is insensitive to the interests of particular clinical trial
participants because it permits clinical trials to begin, or to continue, even though the individual clinician may have
formed a considered option about which of the interventions are best for him or her.» (в PDF «option»; по смыслу
«opinion» — привожу как в тексте).
🔴 **Вывод:** у Freedman условие прекращения — **исчезновение неопределённости в экспертном сообществе** (консенсус
на публично представленных данных), а **не** момент, когда у исследователя появилось предпочтение или точечная оценка
разошлась. Формулировка свода «обязана прекращаться, как только превосходство одной ветви установлено» верна только если
«установлено» понимать как «доказано по стандарту, который убедил бы сообщество». Перенос на FINPILOT в §Д3
(«показ второй по рангу при близких оценках — equipoise; показ заведомо худшей — нарушение») по существу
совместим с clinical equipoise, но ярлык «обязанность из Freedman» в Д5.6 п. 8 надо переформулировать:
«exploration выключается, когда преимущество установлено по заранее заданному статистическому критерию (интервал
разности не содержит нуля), а не по точечной оценке модели». Иначе правило жёстче Freedman и само по себе мешает
набрать данные — ровно то, против чего Freedman и писал.
Честная оговорка: без полного текста нельзя исключить, что в теле статьи есть отдельная формулировка про остановку
испытаний. Абстракт и London её не содержат.

## ПЕРЕПРОВЕРКА Д4 С ПОИСКОМ — П4.6 Перепроверка перечня Д5.4

| Пункт Д5.4 | Что сделано (канал, код, размер) | Результат |
|---|---|---|
| **Freedman 1987, полный текст** | см. П4.5 | 🔴 НЕ ДОБЫТ; но найдено расхождение прочтения абстракта (П4.5) |
| **Radcliffe 2007 (Qini)** | WebSearch: Direct Marketing Analytics Journal, 14–21; карточка Edinburgh Research Explorer `research.ed.ac.uk/en/publications/using-control-groups-to-target-on-predicted-lift-building-and-ass/` — curl 200, 37 338 байт, ссылок на PDF/«Full text» в HTML нет | НЕ ДОБЫТ (репозиторий держит только метаданные). Влияние нулевое, как и было: формула сверена по Belbahri (§Д4.2) |
| **Первоисточник «выученный propensity неидентифицируем»** | WebSearch → Hanna J.P., Niekum S., Stone P. «Importance Sampling Policy Evaluation with an Estimated Behavior Policy», ICML 2019, PMLR 97:2605–2613; PDF `cs.utexas.edu/~pstone/Papers/bib2html-links/ICML2019-Hanna.pdf` — curl 200, 2 872 104 байт, pdftotext 1 182 строки | 🔴 **Найден источник, который опровергает тезис в общем виде** (ниже) |
| **Цитата «propensity after all rules and gating»** | WebSearch → блог Somayeh Farhadi, Medium, 29.01.2026; WebFetch **403**; r.jina.ai 200, 17 764 байт, полный текст | Источник установлен: **блог, не научная работа**; научной ссылки для этой фразы в статье нет (см. ниже) |
| **Подзаконный акт Роскомнадзора по ч. 1 п. 2 ст. 10.2-2** | WebSearch → Приказ РКН от 06.10.2023 № 149; Контур.Норматив `normativ.kontur.ru/document?documentId=460885&moduleId=1` — curl 200, 373 228 байт, но разбор HTML дал пустой текст (рендер JS); r.jina.ai 200, 7 258 байт, полный текст | ✅ ДОБЫТ целиком (ниже) |
| **22-МР по официальной публикации cbr.ru** | WebSearch: документ на consultant.ru (`cons_doc_LAW_494821`), normativ.kontur.ru (documentId=485702), страница cbr.ru с ним в выдаче не появилась | НЕ ДОБЫТ с cbr.ru; вне приоритета — Д10 уже установил, что 22-МР для нас рекомендательны и не адресованы нам |
| **353-ФЗ, 38-ФЗ, 135-ФЗ/ФАС** | не проверялись в этом заходе | НЕ ДОБЫТО: бюджет ушёл на зарубежный контур (П4.1–П4.3), который по заданию приоритетнее. ЗоЗПП ст. 16 п. 3.1 — установлен добором Д10, повторно не качал |
| **FCA Consumer Duty** | не качалось по заданию — добыто Д14 (`cbr_19mr_product_governance_2026-09-10.md`, «ДОБОР Д14 — Д14.1») | Закрыто ссылкой. Для нашего вопроса из Д14 важно: FG22/5 п. 2.41 — Duty не применяется к нерегулируемому бизнесу; PERG 17 — персональный совет по погашению долгов = регулируемая деятельность debt counselling |
| **CFPB, DSA ст. 40, EU AI Act, корпоративный IRB** | П4.1–П4.3 | Закрыто, кроме Polonetsky et al. (П4.3) |
| **Российская практика** | П4.4 | см. П4.4 |

### Hanna, Niekum, Stone (ICML 2019) — дословно
Абстракт: «In this paper, we study importance sampling with an estimated behavior policy where the behavior policy estimate
comes from the same set of data used to compute the importance sampling estimate. We find that this estimator often
lowers the mean squared error of off-policy evaluation compared to importance sampling with the true behavior policy or
using a behavior policy that is estimated from a separate data set. Intuitively, estimating the behavior policy in this
way corrects for error due to sampling in the action-space.»
Введение: «It is natural to assume that such an estimator will yield worse performance since it replaces a known quantity
with an estimated quantity. However, research in the multi-armed bandit (Li et al., 2015; Narita et al., 2019), causal
inference (Hirano et al., 2003; Rosenbaum, 1987), and Monte Carlo integration (Henmi et al., 2007; Delyon & Portier,
2016) literature has demonstrated that estimating the behavior policy...» (обрыв строки в извлечении).
Предложение 1: «For all n, RIS(n) is a biased estimator, however, it is consistent provided πb ∈ Πn».
🔴 **Следствие для §1.3 п. 3 первой редакции и §Д4.3 п. 1.** Тезис «выученный propensity неидентифицируем» в общем
виде **неверен**: если логирующая политика зависит только от залогированного контекста и лежит в классе модели
(πb ∈ Πn), оценённый propensity даёт состоятельную оценку и часто МЕНЬШУЮ MSE, чем истинный. Верная граница:
восстановление ломается, когда решение зависело от **незалогированного** состояния (бюджеты, кэш, гейтинг, скрытые
признаки) — это и Farhadi пишет прямо: «you can only model what you observed. If the real decision depended on hidden
state (budgets, caps, caches), missing features, or hard-to-reconstruct gatin[g]...». Итог для И1 **не меняется**:
писать propensity в момент решения по-прежнему правильно (это единственный способ гарантировать, что скрытого
состояния нет). Меняется обоснование: не «иначе неидентифицируемо», а «иначе нет гарантии, что πb зависит только
от записанного, и нельзя проверить πb ∈ Πn».
Farhadi (Medium, 29.01.2026), строка 36 извлечения, дословно: «The correct propensity is the probability of the chosen
action under the exact decision process that ran in production, after all rules and gating, using the same inputs and
the same state reads.» — это и есть формулировка из §1.3 первой редакции. Статус: блог практика; в научный текст —
только своими словами со ссылкой на Bottou / Sachdeva, как и рекомендовал Д4.3 п. 2.

### Приказ Роскомнадзора от 06.10.2023 № 149 (зарег. в Минюсте 30.11.2023 № 76197) — дословно, все пункты
Преамбула: «В соответствии с пунктом 2 части 1 статьи 10.2-2 Федерального закона от 27 июля 2006 г. N 149-ФЗ ...
приказываю: Утвердить прилагаемые требования к содержанию информации о применении информационных технологий
предоставления информации на основе сбора, систематизации и анализа сведений, относящихся к предпочтениям пользователей
сети "Интернет" ...»
«1. На информационном ресурсе, на котором применяются ... (далее - рекомендательные технологии, информационный ресурс
соответственно), должна быть размещена следующая информация: "На информационном ресурсе применяются рекомендательные
технологии".
2. Информация, предусмотренная пунктом 1 настоящих требований, должна включать ссылку на отдельную страницу
информационного ресурса, на которой указываются следующие сведения: "На информационном ресурсе при применении
информационных технологий предоставления информации осуществляется сбор, систематизация и анализ сведений, относящихся
к предпочтениям пользователей сети "Интернет", находящихся на территории Российской Федерации".
3. Информация, предусмотренная пунктом 1 настоящих требований, размещается на русском языке в общедоступном режиме на
информационном ресурсе и (или) на персональных страницах пользователей, созданных на таком информационном ресурсе.
4. Доступ к информации о применении рекомендательных технологий должен осуществляться беспрепятственно, без
дополнительной регистрации и безвозмездно.
5. При размещении информации о применении рекомендательных технологий не допускается ее наложение на иную информацию,
размещенную на информационном ресурсе, на котором применяются рекомендательные технологии.»
Чтение: приказ регулирует только **уведомление** (ч. 1 п. 2 ст. 10.2-2) — две фиксированные фразы и ссылка.
Про содержание «правил применения» (ч. 2 ст. 10.2-2: «описание процессов и методов ... способов осуществления») приказ
ничего не добавляет. Требование описать exploration остаётся выводом из самой ч. 2 ст. 10.2-2, как в §Д3 — приказ его
не усиливает и не ослабляет.

## ПЕРЕПРОВЕРКА Д4 С ПОИСКОМ — П4.4 Российская практика причинной оценки финтех-продуктов

Пробел, сохранявшийся с первой редакции (§И4 п. 7) и с добора (§Д4.3 п. 3). Ниже — то, что реально нашлось,
и прямо названное отсутствующее.

### Журнал добычи (11.09.2026, все — curl -sk --http1.1 с браузерным UA, если не указано иное)
| Источник | URL | HTTP | Размер |
|---|---|---|---|
| Кодекс этики в сфере разработки и применения ИИ на финансовом рынке (прил. к информационному письму Банка России от 09.07.2025 № ИН-016-13/91) | `cbr.ru/content/document/file/178667/code_09072025.pdf` | 200 | 490 151 байт PDF → pdftotext 394 строки |
| Т-Банк, «Perseus: фреймворк для универсальной персонализации на основе гетерогенных событий», Хабр, 21.07.2026 | `habr.com/ru/companies/tbank/articles/1061236/` | 200 | 171 354 байт → 17 859 симв. |
| «Архитектура банковского RecSys», Хабр, 02.09.2026 (автор ToxaBes, не корпоративный блог) | `habr.com/ru/articles/1077822/` | 200 | 202 950 байт → 27 793 симв. |
| Альфа-Банк, «Волков бояться — uplift в прод не катить, или AUF 2.0», Хабр, 22.04.2026 | `habr.com/ru/companies/alfa/articles/1024090/` | 200 | 222 253 байт → 25 582 симв. |
| Альфа-Банк, отчёт о Data Science Meet Up #2, Хабр, 19.09.2022 (в т.ч. доклад «Uplift-моделирование в ценообразовании кредитных продуктов», М. Коматовский; видео — RUTUBE `rutube.ru/video/e07b39e41eecfa310886208f6a446d81/`, 02.08.2024, 00:25:06 — **видео не смотрел**) | `habr.com/ru/companies/alfa/articles/688438/` | 200 | 193 293 байт → 13 378 симв. |
| Сбер, «Causal Inference: прозрение и практика. Лекция 2. Рандомизированные контролируемые испытания», Хабр, 03.10.2024 | `habr.com/ru/companies/sberbank/articles/847406/` | 200 | 195 189 байт → 13 598 симв. |
| Сбер, «Подготовка датасета для офлайн-оценки рекомендательных моделей», Хабр, 04.09.2026 | `habr.com/ru/companies/sberbank/articles/1076666/` | 200 | 205 674 байт → 23 471 симв. |
| «Модель обещает uplift. А сколько это в рублях?», Хабр, 08.09.2026 (А. Москвин, независимый) | `habr.com/ru/articles/1079904/` | 200 | 178 776 байт → 19 142 симв. |
| Ozon Tech, «Без А/B результат ХЗ, или Как построить высоконагруженную платформу А/B-тестов», Хабр, 21.09.2022 | `habr.com/ru/companies/ozontech/articles/689052/` | 200 | 282 047 байт → 29 868 симв. |
| Ozon Tech, «Как с помощью A/B-платформы найти лучшее решение, если вариантов слишком много», Хабр, 23.03.2026 | `habr.com/ru/companies/ozontech/articles/1012750/` | 200 | 266 431 байт → 22 791 симв. |
| Сравни (финансовый маркетплейс), «Особенности и подводные камни A/B/n-тестирования», Хабр, 20.03.2023 | `habr.com/ru/companies/sravni/articles/723662/` | 200 | 202 624 байт → 22 499 симв. |
| СберЗдоровье (блог docdoc), «Платформа А/В-экспериментов», Хабр, 15.05.2024 | `habr.com/ru/companies/docdoc/articles/814415/` | 200 | 190 010 байт → 18 967 симв. |
| Kuper, «База: айсберг A/B-тестов», Хабр, 22.11.2023 | `habr.com/ru/companies/kuper/articles/774608/` | 200 | 212 895 байт → 20 089 симв. |
| АРБ / НБЖ, М. Сёмов о наджинге и «Финансовом плане», 31.12.2025 | `nbj.ru/publs/maksim_syemov_arb_vsye_chto_vy_khoteli_uzn/70334/` | 200 | 127 939 байт → 41 261 симв. |
| X5 Tech, «От A/B-тестирования к Causal Inference в офлайн ритейле» | `habr.com/ru/companies/X5Tech/articles/768008/` | **403** | 67 081 байт (антибот Хабра на этой статье; остальные статьи Хабра отдались) |

WebSearch по участку: 9 вызовов. Отказа «web search budget» не было.

### A. Какие методы применяют — по первоисточникам
1. **Uplift-моделирование — рабочая, промышленная практика в банках РФ, но применяется к МАРКЕТИНГОВОЙ коммуникации,
   а не к советам по долгам.** Альфа-Банк, AUF 2.0 (открытая библиотека, дословно из статьи): конфиг с
   `opt_metric = 'qini_auc'`, модели `SoloModel`, `TwoModels`, `AufXLearner`, `n_uplift_bins=10`; «AUF позволил обучить
   и вывести в промышленное использование уже 4 модели, при этом более 10 моделей находятся в стадии пилота. Все эти
   модели помогают избежать спама клиентов, сделать персонализированный прайсинг и привлекать новых клиентов». Про
   контрольную группу: «В бинарном случае достаточно было указать контрольную и одну целевую группу. Для мультитритмента
   нужно передать все группы, при этом ключ 'control' обязателен — именно относительно него будет считаться эффект
   каждого воздействия.» Диагностика по бакетам: «процент целевых действий (продаж, сделок, кликов) в контрольной
   и целевой группах, попавших в каждый бакет. ... Представь, что верхний бакет ... содержит 60% всех органических
   сделок — то есть тех, которые произошли бы и без коммуникации. Возможно, стоит оставить этих клиентов в покое и не
   рисковать падением маржинальности или лояльности от лишнего спама».
   🔴 Это тот же метод, что в §3 темы 37 (мета-обучатели, Qini), с тем же критерием качества — **подтверждение, что наш
   инструментарий совпадает с российской банковской практикой**, а не только с академической литературой.
2. **Uplift в ценообразовании кредитных продуктов** — доклад Альфа-Банка (М. Коматовский, Junior DS), пересказ в отчёте
   о митапе, дословно из отчёта: «Дальше берём Up-lift-модель, готовимся и проводим эксперименты. „Нужно следить за
   экспериментом от начала и до конца. Может случиться, чт[о] контрольную группу вы начали обзванивать на 2 дня раньше,
   а эксперимент через неделю закончился и в контрольной группе с позитивным воздействием Target Rate выше“». В докладе
   также «Специфические метрики под Up-lift. Сортировка скоров, подсчёт topK% и разницы Response Rate».
   Статус: **пересказ статьи о докладе; видео (25 мин) не просмотрено** — числа доклада не подтверждены.
3. **Причинный вывод как учебная программа Сбера.** Цикл «Causal Inference: прозрение и практика» (блог Сбера),
   лекция 2 — про RCT и виды рандомизации (дословно: «Простая рандомизация — каждому участнику испытания случайным
   образом назначается либо исследуемое вмешательство, либо контрольное. Стратифицированная рандомизация ...
   Кластерная рандомизация ...»). Это методический материал, не описание продовой практики.
4. **Офлайн-оценка рекомендательных моделей — есть, но не off-policy.** Сбер, статья 04.09.2026 об офлайн-оценке
   посвящена подготовке датасета: временные утечки («Самый простой случай утечки данных возникает в случае ошибок
   логирования или предобработки, когда одинаковые взаимодействия присутствуют и в обучающей выборке, и в данных для
   оценки»), сдвиги распределений, статистика Колмогорова—Смирнова, свой инструмент SplitLight. **Слов «propensity»,
   «IPS», «off-policy» в тексте нет** (grep = 0).
5. 🔴 **Единственный найденный русскоязычный текст, где IPS назван прямо** — «Архитектура банковского RecSys»
   (Хабр, 02.09.2026, автор не из банка, обзор): «Обычно используется классический метод Inverse Propensity Scoring
   (IPS) из работы Joachims с соавторами [22], где клики взвешиваются обратно пропорционально вероятности увидеть
   позицию». Там же про exploration: «Этого достаточно, чтобы обучать модель почти в реальном времени и активно
   исследовать пространство рекомендаций с помощью бандитов» (со ссылкой на промышленную работу Kuaishou). И про
   специфику банка против маркетплейса: «У банка есть лишь десятки или сотни офферов для каждого клиента. Задача поиска
   кандидатов здесь почти не возникает, поскольку практически весь каталог и без того помещается в отбор.» — прямая
   поддержка нашего случая |A| = 66 из §Д1.6.
6. **Бандиты и exploration на платформе A/B — у маркетплейса, не у банка.** Ozon Tech (23.03.2026): оптимизация
   параметров рекомендательного алгоритма поверх A/B-платформы, стратегии выбора — «Thompson Sampling (TS) из
   нормального распределения ... Стратегия семплирует для каждого возможного набора параметров аплифт метрик из оценок
   матожидания и стандартного отклонения»; для категориальных параметров — «многорукие бандиты»; и прямое
   предупреждение, дословно: **«Не используйте оптимизатор для оценки истинного эффекта от набора параметров. Для
   корректной оценки необходимо зафиксировать конкретный набор и провести отдельный А/B-тест.»** (это ровно разделение
   «exploration ≠ оценка», которое у нас в И1/И2).
7. **Глобальный холдаут против теста политик** — «Модель обещает uplift...» (08.09.2026), дословно: «Глобальный holdout
   отвечает ещё на один вопрос: какой суммарный эффект даёт оговорённая CVM-программа на выбранном горизонте. Контроль
   отдельной кампании отвечает за конкретное воздействие, а тест политик — за преимущество нового способа отбора. Эти
   конструкции нельзя незаметно подменять друг другом.» Это ровно различение «оценка политики» и «оценка воздействия»
   из §Д1.

### B. Какая доля трафика идёт на эксперименты — 🔴 В РОССИЙСКИХ ИСТОЧНИКАХ ЧИСЛА НЕТ
Проверено в 8 текстах (Ozon ×2, Сравни, СберЗдоровье, Kuper, Альфа ×2, «uplift в рублях»): описывается **механика**
сплитования, не доля. Максимум конкретики — Ozon Tech (2022): «Пользователь при запросе токена авторизации
автоматически получает А/B-группу как рандом с равномерным распределением от 0 до 99. abGroup = random % 100 ...
Бэкенд-монолит при старте читает конфиг с указанием набора фич и указанием, для какого процента пользователей»
(то есть доля задаётся конфигом и не публикуется), и Ozon Tech (2026): «Вариант №1 (50% аудитории) / Вариант №2
(50% аудитории)» — пример на два варианта.
Косвенный ориентир по CVM-контролю (не банк, маркетинговые платформы, **пересказ выдачи WebSearch, первоисточники
не открывал**): «обычно это 5-10% аудитории, иногда больше, но, как правило, не более 20-25%», срок изоляции 1–3
месяца (altcraft, mindbox, vc.ru). Как число для работы это не годится — уровень доверия «маркетинговый блог».
**Вывод: измеренное число доли exploration остаётся одно — 10,1% у ZOZO (§Д1.2), по открытому датасету.
Российского аналога нет в открытых источниках.** Отрицательный результат, не «не искал».

### C. Как решают этическую сторону — 🔴 в технических публикациях НИКАК
Ни в одном из 13 добытых технических текстов нет слов «этика», «согласие», «информирование» применительно
к эксперименту (grep по каждому = 0; единственное вхождение «этик» — в статье АРБ/НБЖ, не о A/B). Ближайшее
к этическому ограничению в отрасли — не этика, а **маржинальность и лояльность**: Альфа-Банк про «не рисковать
падением маржинальности или лояльности от лишнего спама».
Этическая рамка в РФ существует отдельно от практики экспериментов:
1. 🔴 **Кодекс этики в сфере разработки и применения ИИ на финансовом рынке** (прил. к ИН-016-13/91 от 09.07.2025) —
   документ, которого не было ни в первой редакции, ни в доборе. Дословно, п. 1.1(1): цели — «повышение доверия
   физических и юридических лиц (далее – клиенты) к применению искусственного интеллекта **кредитными организациями,
   иностранными банками ... некредитными финансовыми организациями, лицами, оказывающими профессиональные услуги на
   финансовом рынке, субъектами национальной платежной системы** (далее – организации)». П. 1.2: пять принципов —
   «человекоцентричность; справедливость; прозрачность; безопасность, надежность и эффективность; ответственное
   управление рисками». Формулировки везде «организациям **рекомендуется**».
   🔴 **Норма, которая касается нас напрямую даже без поднадзорности, п. 1.4 (дословно):** «В случае привлечения при
   разработке и применении искусственного интеллекта организациями лиц, в отношении которых Банк России не осуществляет
   контроль (надзор), организациям рекомендуется обеспечивать соблюдение такими лицами настоящего Кодекса.» То есть
   в B2B-сценарии банк-заказчик будет транслировать Кодекс на нас договором — тот же механизм, что Д14 нашёл в UK
   (FG22/5 пп. 2.22, 2.24).
   Что из Кодекса ложится на тему 37 (дословные пункты): п. 2.1(2) «предоставление клиентам возможности отказаться
   от взаимодействия с применением искусственного интеллекта» и п. 2.3 — «предоставить клиентам возможность
   взаимодействовать с сотрудником организации»; п. 2.1(3), 2.4 — пересмотр решения сотрудником по запросу клиента;
   п. 2.5 — разъяснять клиенту, «действия, которые клиенту необходимо совершить для принятия искусственным интеллектом
   решения», с оговоркой «Организация вправе не предоставлять указанные разъяснения, если имеются разумные основания
   полагать, что такое информирование может снизить эффективность применения искусственного интеллекта»; п. 2.6 —
   учитывать «факторы уязвимости клиентов (возраст, образование, ограниченные возможности и другие)»; п. 4.2 —
   «сообщать клиентам о применении искусственного интеллекта ..., если применение искусственного интеллекта неочевидно
   из обстоятельств»; п. 5.3 — показатели качества и проверка «в том числе посредством валидации, добровольной
   сертификации»; п. 5.4 — регулярный мониторинг качества; п. 6.3 — семь процессов управления рисками, включая
   «учет применяемых моделей искусственного интеллекта» и «ведение базы риск-событий»; п. 6.4 — «централизованный учет
   моделей ... с учетом присвоенного уровня риска»; п. 6.7 — факторы уровня риска, среди них «(4) количество клиентов,
   при оказании услуг которым применяется искусственный интеллект», «(5) объяснимость решений», «(6) применение
   искусственного интеллекта, разработанного третьим лицом»; п. 6.9 — «обеспечивать контроль сотрудников организации
   за решениями искусственного интеллекта, которому присвоен высокий уровень риска».
   🔴 **Про эксперименты, рандомизацию, A/B и согласие на участие в Кодексе нет ни слова** (проверено grep по всем
   394 строкам: «эксперимент» — 0, «тестир» — 0 в смысле A/B; «отказ» — только про отказ от взаимодействия с ИИ).
   Ближайший к нашей теме механизм — п. 2.1(2)/2.3 «право отказаться от взаимодействия с ИИ»: если exploration
   реализован внутри ИИ-контура, право отказа де-факто даёт пользователю выход из него.
2. **Кодекс этики в сфере ИИ от 26.10.2021** (Альянс в сфере ИИ; открыт для присоединения любых, в том числе
   небанковских, организаций) — URL текста найден (`a-ai.ru/wp-content/uploads/2021/10/Кодекс_этики_в_сфере_ИИ_финальный.pdf`,
   также base.garant.ru/406862712), **сам текст в этом заходе не качал** — бюджет ушёл на Кодекс ЦБ. НЕ ДОБЫТО.
3. **АРБ/НБЖ (31.12.2025), наджинг** — единственный найденный отраслевой текст РФ, где этика названа в одном ряду
   с воздействием на поведение клиента: «методами наджинга – набором приёмов, позволяющих, в рамках этики, существенно
   снижать риски потребителей финансовых продуктов». 🔴 Побочная находка, важная для продукта: автор (председатель
   Комитета АРБ по финансовой грамотности) строит концепцию «**Финансового плана**» — «кредитная организация предлагает
   продукт „от цели“ клиента, снабжая клиента финансовым планом – системой этапов и мероприятий», с «рекомендациями по
   размещению части свободных средств» — и прямо вешает на неё принципы 19-МР: «Распределение клиентской базы по ЦКГ
   проводится в соответствии с Методическими рекомендациями Банка России от 27.12.2023 №19-МР», «Принцип 5: Клиентская
   ценность Финансового плана». Это ближайший российский отраслевой аналог нашего продукта, описанный на языке 19-МР,
   и он подтверждает вывод Д14/Д10: в РФ такой сервис регулируется через **поднадзорную организацию**, а не напрямую.
   Статус: мнение автора в отраслевом журнале, не акт.

### D. НЕ ДОБЫТО по П4.4 — с причинами
- **Доля трафика на эксперименты в конкретном российском банке** — числа не публикуются; проверено 8 технических
  публикаций (список выше), в них только механика сплитования. Не «не искал» — отрицательный результат.
- **Видео доклада Альфа-Банка про uplift в ценообразовании** (RUTUBE, 25 мин) — не просматривалось (нет канала
  транскрипции); цитаты взяты только из текстового отчёта о митапе.
- **X5 Tech, «От A/B-тестирования к Causal Inference в офлайн ритейле»** — Хабр отдал **403** (67 081 байт) именно
  на эту статью, r.jina.ai не пробовал (ретейл, не финтех — вне приоритета).
- **Т-Банк: собственная статья про A/B-платформу или оценку эффекта** — не найдена: в блоге tbank добыт Perseus
  (инфраструктура персонализации, про офлайн-инференс и «бизнес-метрики от 3% до 17%», но без A/B-методологии),
  поиски «Т-Банк A/B платформа/CUPED» выдают статьи МТС, Otus, X5, Kuper — не Т-Банка.
- **ВТБ: публикация с методологией** — профиль `habr.com/ru/users/VTB/posts/` отдал 200/74 203 байта и «здесь пока нет
  ни одной публикации» (63 статьи лежат в другом разделе профиля, не проверял); по выдаче — только подкаст «Деньги
  любят техно», выпуск про A/B-тестирование (аудио, не транскрибировано) и вакансии с упоминанием NBO/uplift.
- **Кодекс этики ИИ 2021 (Альянс ИИ), полный текст** — URL известен, не качал (бюджет).
- **Off-policy оценка (IPS/DR) в продакшене российского банка** — **не найдено ни одного описания**. Единственное
  упоминание IPS — в обзорной статье независимого автора (п. A.5). Это существенный отрицательный результат:
  для научного текста темы 37 российских продовых кейсов OPE нет, ссылаться придётся на ZOZO/Open Bandit.

## ПЕРЕПРОВЕРКА Д4 — ИЗМЕНЕНИЯ ВЫВОДОВ ПОСЛЕ ПЕРЕПРОВЕРКИ С ПОИСКОМ

Перепроверка закрыла участки П4.1 (AI Act + DSA), П4.2 (CFPB), П4.3 (корпоративные IRB), П4.4 (практика РФ),
П4.5 (Freedman), П4.6 (перечень Д5.4). Подагентов: 0. WebSearch: 27 вызовов, отказа по бюджету не было ни разу
(в доборе Д4 было 400/400 — ограничение снято).

### ✅ Подтвердилось
1. **Цитаты DSA ст. 25 и 27 из §4.1 Д3 сверены по OJ-тексту дословно** — расхождений нет.
2. **Приложение III п. 5(b) AI Act процитировано в задании верно** (сверено с OJ и сервис-деском).
3. **Инструментарий темы 37 совпадает с российской банковской практикой** — Qini/uplift-метрики, обязательная
   контрольная группа, мета-обучатели (Альфа-Банк AUF 2.0, П4.4.A.1), различение «оценка политики / оценка
   воздействия» (П4.4.A.7), запрет использовать оптимизатор вместо честного A/B (Ozon, П4.4.A.6).
4. **Правило «exploration в зоне equipoise, без показа заведомо худшего»** — устояло и получило второе, теперь
   статутное, основание в США: 12 U.S.C. §5531(d)(2)(C), «takes unreasonable advantage of ... the reasonable reliance
   by the consumer on a covered person to act in the interests of the consumer» (П4.2.A).
5. **Ст. 10.2-2 149-ФЗ остаётся единственной прямо применимой к нам нормой в РФ**; подзаконный приказ РКН № 149
   добыт целиком и ничего к «правилам применения» не добавляет (П4.6).

### 🔴 Опровергнуто или существенно изменено
1. 🔴 **Раздел 5 п. 4 свода: «показ заведомо худшей альтернативы ... нарушает ... ст. 25 DSA» — ссылка неприменима.**
   Ст. 25 DSA адресована «providers of online platforms», а платформа по ст. 3(i) — хостинг, распространяющий
   информацию пользователей «to the public». FINPILOT ею не является. Плюс ст. 25(2) выводит из-под себя практики,
   покрытые UCPD 2005/29/EC и GDPR, а ст. 19 освобождает микро- и малые предприятия. Правильно: ст. 25 DSA —
   **формулировочный ориентир, а не применимая норма**; применимая рамка для B2C в ЕС — UCPD + GDPR + ст. 5(1)(a),(b)
   AI Act (П4.1.C).
2. 🔴 **§Д3 п. 2.1 условие 3 и Д5.6 п. 8: «обязанность прекратить, как только превосходство установлено» —
   прочтение абстракта Freedman неверно.** Фраза «ethically obliged to offer that treatment» относится к ПРИНЯТОМУ
   пониманию, которое Freedman критикует; его собственный порог — исчезновение отсутствия консенсуса в экспертном
   сообществе (вторичное подтверждение: London 2007, стр. 104–105). Нужная редакция правила: exploration выключается,
   когда преимущество установлено **по заранее заданному статистическому критерию**, а не когда разошлись точечные
   оценки (П4.5).
3. 🔴 **§1.3 п. 3 / §Д4.3 п. 1: «выученный propensity неидентифицируем» — неверно в общем виде.** Hanna, Niekum,
   Stone (ICML 2019): оценка политики поведения по тем же данным «often lowers the mean squared error of off-policy
   evaluation compared to importance sampling with the true behavior policy»; RIS(n) смещён, но состоятелен при
   πb ∈ Πn. Ломается не идентифицируемость, а случай зависимости решения от **незалогированного** состояния (П4.6).
   Вывод И1 «писать propensity в момент решения» не меняется — меняется обоснование.
4. 🔴 **§4.2 Д3 и Д5.4: «CFPB не пробовалось» закрыто, и главное — статус документов CFPB изменился.**
   Circular 2023-01 (dark patterns / negative option), interpretive rule о digital marketers и Statement of Policy
   on Abusive Acts **отозваны 12.05.2025** (90 FR 20084). Ссылаться на них как на действующую позицию нельзя;
   действует статут — §5531, §5536 (П4.2.B).
5. 🔴 **Новое обязательство, которого не было ни в одной редакции: в США советующий по долгам сервис —
   «covered person» по прямому тексту закона.** 12 U.S.C. §5481(15)(A)(viii) включает «financial advisory services ...
   to consumers on individual financial matters ... including ... (II) providing services to assist a consumer with
   debt management». То есть UDAAP применяется к нам без лицензии и без продажи продукта (П4.2.A). Это третий
   независимый режим после РФ (ст. 10.2-2) и UK (PERG 17 debt counselling, Д14).
6. 🔴 **Даты AI Act в любом прежнем пересказе устарели: Регламент (ЕС) 2026/1744 (Digital Omnibus on AI) от
   08.07.2026, OJ 24.07.2026, перенёс применение требований к high-risk из Annex III на 02.12.2027**, из Annex I —
   на 02.08.2028 (ст. 1 п. 40). Запреты ст. 5(1)(a),(b) действуют с 02.02.2025 без изменений (П4.1.A).
7. 🔴 **Вероятно, FINPILOT вообще не «AI system» в смысле AI Act** — руководство Комиссии по ст. 3(1) выводит
   из определения «systems that are based on the rules defined solely by natural persons», «well established
   optimisation methods, such as linear or logistic regression», basic data processing и classical heuristics (п. 26,
   42, 46, 48). Детерминированный SAW с фиксированными весами попадает в эти исключения; обучаемая по логам политика
   из темы 37 — уже нет. **Это делает вопрос «high risk или нет» вторичным по отношению к вопросу «учим ли мы модель
   на логах»** (П4.1.B).
8. 🔴 **Российская этическая рамка для ИИ на финрынке существует и в теме 37 отсутствовала**: Кодекс этики
   (ИН-016-13/91 от 09.07.2025). Рекомендательный и адресован организациям финрынка, но п. 1.4 прямо просит
   транслировать его на неподнадзорных исполнителей — то есть на нас в B2B (П4.4.C.1).
9. 🔶 **Практика РФ: пробел §И4 п. 7 закрыт наполовину и с отрицательным результатом.** Uplift и A/B в банках РФ —
   есть и промышленно; **off-policy оценка в продакшене российского банка не описана ни в одном найденном источнике**,
   доля трафика на эксперименты не публикуется, этическая сторона экспериментов в технических публикациях
   не обсуждается вовсе (П4.4.B, П4.4.C, П4.4.D).

### Ответ на вопрос (1): выдерживает ли вывод раздела 5 проверку зарубежными режимами
**Частично — и его надо сузить.** «Прямого запрета рандомизации нет» выдерживает: ни AI Act, ни DSA, ни CFPA не
запрещают A/B-тест как таковой; в добытых текстах слово «A/B» встречается 0 раз (AI Act, руководства Комиссии, DSA).
Единственная найденная зарубежная норма, где эксперимент на людях с ИИ-системой требует **информированного согласия
и одобрения органа**, — ст. 60–61 AI Act, но она применяется к «testing in real world conditions» **до** вывода
high-risk системы на рынок, то есть к нам в сегодняшнем виде не относится.
🔴 А вот вторая половина вывода — «применимая норма одна и она про раскрытие» — **верна только для РФ**. Зарубежные
режимы дают не раскрытие, а иную конструкцию: оценку по **последствиям для потребителя** независимо от раскрытия —
UDAAP §5531(d)(2)(C) (США, прямо применимо к debt-management-советнику), Consumer Duty/PERG 17 (UK, через
регулируемую деятельность, Д14), ст. 5(1)(a),(b) AI Act (ЕС, если система — AI system). Раскрытие в них
не оправдывает вреда. Практический итог: формулировка §5 остаётся верной как ответ «что обязательно в РФ»,
и её нельзя обобщать словами «регуляторно свободны».

### Ответ на вопрос (2): что из AI Act/DSA стало бы обязательным при выходе в ЕС или B2B с европейским банком
1. **DSA — ничего.** Ни в B2C, ни в B2B: ст. 25, 27 — только для online platforms (ст. 3(i)), ст. 38, 40 — только
   для VLOP/VLOSE (≥45 млн, ст. 33(1)), ст. 19 освобождает микро/малые. Ст. 40 «доступ исследователей» к нам
   не относится ни при каком росте, пока мы не хостинг с публичным распространением контента.
2. **AI Act, ст. 5(1)(a) и (b) — обязательны уже сейчас (с 02.02.2025) и независимо от риск-класса**, если система
   квалифицируется как AI system. Практическая граница дана руководством C(2025) 5052: «persuasion» с раскрытыми
   алгоритмами и контролем пользователя допустима, «covert techniques» с непониманием пользователем — нет (п. 128,
   130). Скрытый exploration под видом рекомендации — прямой кандидат в ст. 5(1)(a) при значимом финансовом вреде
   (сообр. 29 прямо включает «financial interests»); exploration с раскрытыми альтернативами и оценками — нет.
3. **AI Act, глава III (ст. 8–17: управление рисками, ст. 10 данные, ст. 12 логи, ст. 14 надзор человека, ст. 49
   регистрация) — обязательны ТОЛЬКО если система попадает в Annex III п. 5(b), и с 02.12.2027.** Для B2C-советника
   по нашему чтению п. 5(b) не срабатывает (проект руководства, стр. 88: «tailored information to customers»
   и «customer support» — вне 5(b)). 🔴 **Срабатывает в B2B-сценарии, если банк использует наш выход в решении
   о выдаче/лимите/цене кредита**: п. 75 проекта требует оценивать «split architectures ... as a whole», а
   профилирование физлиц закрывает дерогацию ст. 6(3). В этом случае обязательны и ст. 12 (логирование —
   совпадает с нашей И1), и ст. 14 (человеческий надзор), и ст. 10 (data governance), и ст. 6(4) —
   документированная оценка «мы не high-risk» до вывода на рынок, если мы считаем иначе.
4. **Ст. 60–61 (испытания в реальных условиях с информированным согласием, план испытаний, одобрение органа
   рыночного надзора, срок ≤6+6 мес., право выйти без последствий)** — обязательны, только если мы одновременно
   high-risk **и** тестируем до вывода на рынок. Как ориентир этичной конструкции exploration они полезны и сейчас.
5. **Практический минимум для B2B с европейским банком** (вывод, не норма): пакет как в Д14 плюс наше собственное
   решение по ст. 3(1) — письменная квалификация «AI system / не AI system» с обоснованием по п. 42/46/48 руководства
   Комиссии, и, если политика учится по логам, документированная оценка по ст. 6(3)–6(4).
