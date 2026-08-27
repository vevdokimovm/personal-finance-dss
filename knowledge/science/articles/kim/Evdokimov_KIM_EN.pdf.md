# Evdokimov_KIM_EN — выжимка

| | |
|---|---|
| оригинал | `Evdokimov_KIM_EN.pdf` (рядом, не тронут) |
| тип | PDF |
| размер | 0.5 МБ |
| страниц | 11 |
| извлечено знаков | 37649 |

## Извлечённый текст

> Ниже — **текстовый слой файла**, а не пересказ. Извлечено машинно; смысл, структура
> и то, что было картинкой, здесь не появятся. Оригинал остаётся эталоном.

UDC 519.816:004.94

A multi-criteria model for allocating free cash flow in personal
financial planning: a computational study and norm-anchored
                     criteria normalization
                                             V. M. Evdokimov
                             National University of Science and Technology MISIS,
                                  4 Leninskiy Prospekt, Moscow, 119049, Russia
                         E-mail: m2201058@edu.misis.ru, ORCID: 0009-0004-8821-8414

Abstract. This paper proposes and studies a multi-criteria model that supports a recurring household decision:
how to split free monthly cash flow between early debt repayment, a liquidity reserve, and savings goals. The
model combines several components into a single decision cycle. It generates allocation alternatives by
discretizing the available resource into fixed shares, screens loans for early repayment against an opportunity-
cost rate threshold, scores goal attainment with category and urgency weights, enforces a feasibility cascade
based on liquidity and debt-load constraints, forecasts cash flows with simple exponential smoothing
accompanied by Monte-Carlo interval estimation, and ranks the feasible alternatives by an additive utility
function whose weights encode the user's risk profile. A computational study runs the model on three
demonstration profiles — over-indebted, typical, and comfortable — under three liquidity-threshold regimes.
The study reveals a degeneracy in the original criteria specification: the resource and liquidity criteria, both
computed from the unallocated remainder, are nearly collinear (their correlation across alternatives exceeds
0.999), so the ranking collapses toward reserve-only allocations regardless of the risk profile, while sample-
range min-max normalization inflates economically negligible criterion differences to the full unit interval. The
paper then introduces a refinement: the resource criterion becomes a forecast of next-period free cash flow,
which embeds the forecasting block directly into the utility function; the liquidity criterion switches to a stock-
based measure; and normalization is anchored to financial norms — the regulatory debt-service-to-income
ceiling and liquidity-stock benchmarks — instead of the sample range. Under the refined model,
recommendations differentiate monotonically across risk profiles: conservative profiles build the reserve,
active profiles fund goals, and the aggressive profile additionally prepays expensive debt. Rankings remain
stable under small weight perturbations, the protective cascade still produces corrective output on the over-
indebted profile, and a full decision cycle completes in under two milliseconds, which supports interactive use.
Keywords: multi-criteria decision making, decision support, simple additive weighting, criteria normalization,
cash-flow forecasting, Monte-Carlo method, personal finance, computational experiment

Introduction
       The quality of everyday financial decisions directly affects household resilience, savings, and the ability
to reach long-term goals [Lusardi, Mitchell, 2014]. A growing range of financial products and digital channels
multiplies the alternatives that must be compared by rates, terms, and risks, while most users keep their
information about income, expenses, and obligations fragmented [Blokhina et al., 2025; Malyonkina,
Ponyaeva, 2024]. Digital personal-finance services are developing rapidly [Gomber et al., 2017; Kachanova,
Plaksa, 2025], yet their functionality mostly reduces to transaction tracking and expense visualization: a
formalized procedure for choosing an action — where to direct this month's free funds — is typically absent
from mass-market products.
       The need for such a procedure has empirical support. An anonymous online survey conducted by the
author (385 responses collected, 322 valid after an attention check) showed that, despite a declared inclination
toward rational calculation, only 10% of respondents actually relied on computation in a concrete allocation
situation, 63% decided based on emotional comfort or anxiety, and 84% viewed the idea of an algorithmic
advisor positively on the condition that its logic is transparent. The condition matters: in high-stakes settings,
interpretable models are preferable to post-hoc explanations of black boxes [Rudin, 2019], and the quality of an
explanation determines user trust in a recommendation [Miller, 2019; Arrieta et al., 2020].
    Multi-criteria decision analysis, systematically applied in finance [Hwang, Yoon, 1981; Zopounidis,
Doumpos, 2002], provides the methodological basis for formalizing such problems. Among ranking methods,
simple additive weighting (SAW), rooted in additive utility theory [Fishburn, 1967], stands out for combining
simplicity, computational efficiency, and — critically for this domain — full transparency: the contribution of
each criterion to an alternative's score is explicit [Velasquez, Hester, 2013]. Ratio-based diagnostics of
household financial state were developed in [Lytton et al., 1991] and consolidated into consensus benchmarks
in [Greninger et al., 1996]; the regulatory ceiling on debt load is set by the central bank [Bank of Russia, 2018].
Exponential smoothing [Hyndman et al., 2002] and Monte-Carlo simulation [Metropolis, Ulam, 1949] serve to
assess the stability of future states. At the same time, multi-criteria rankings are known to be sensitive to the
choice of normalization procedure [Jain et al., 2005; Vafaei et al., 2018] — an aspect that, as shown below,
turns out to be decisive for the class of models considered here.
       The novelty of this work lies not in the individual methods, each of which is known, but in their
integration into a single free-cash-flow allocation model and in the results of its computational study. The
contributions are: (1) a complete multi-criteria model comprising alternative generation, an opportunity-cost
screening filter for early repayment, weighted goal scoring, and a feasibility cascade; (2) a computational
demonstration that the natural criteria specification is degenerate — the resource and liquidity criteria are
collinear and min-max normalization is pathological, which biases the ranking toward reserve allocations
regardless of user preferences; (3) a refinement — a forecast-based resource criterion that embeds the
forecasting block into the utility function, a stock-based liquidity criterion, and norm-anchored normalization
— that restores meaningful differentiation of recommendations across risk profiles; (4) evidence that the
protective constraints retain their behavior and that the ranking is stable under weight perturbations. Personal
finance serves as the application domain; the scheme itself — detected criteria collinearity followed by norm-
based anchoring of scales — transfers to other resource-allocation problems.

1. Classes of algorithmic approaches and method selection
       Algorithmic cores of digital personal-finance tools fall into six classes that differ in the balance of
adaptivity and explainability (Table 1). Rules and heuristics are transparent but express trade-offs between
competing directions poorly; scoring models reduce a multidimensional situation to a single number;
forecasting models improve justification but do not by themselves choose an action; optimization formulations
are rigorous, yet their solutions are hard to explain to users without special training. A hybrid scheme — rules
as feasibility constraints, a forecast as a criterion source, and multi-criteria ranking as the choice mechanism —
combines the strengths of these classes at the cost of higher demands on module coordination; as Section 3
shows, coordinating the criteria is precisely the non-trivial part of the problem.
Table 1. Classes of algorithmic approaches to decision support in personal finance
        Approach class                          Strengths                                 Limitations
 Rules and heuristics            Transparent logic, low complexity          Weak adaptivity, poor handling of
                                                                            multiple criteria
 Scoring models                  Compactness, easy monitoring               Reduction to a single number, debatable
                                                                            weights
 Cash-flow forecasting           Captures dynamics and uncertainty          Does not choose an action, needs history
 Multi-criteria choice           Formalizes trade-offs, tunable             Sensitive to scales and normalization
                                 preferences
 Optimization models             Rigor, reproducibility                     Hard to explain, assumption-dependent
 Hybrid (rules + forecast +      Balance of explainability and quality      Module coordination, demanding testing
 ranking)



2. Mathematical model
2.1. Input data and state metrics
       Input data are aligned to a monthly time step. In period t, let income transactions ik, expense transactions
ej, and the current balance Bt be given. The set of credit obligations O = {(Pl, rl, Tl, Blloan)} specifies, for each
loan l, the monthly annuity payment, the annual rate, the remaining term, and the principal balance. The set of
goals G = {(Tstgt, Cs, τs, cs)} specifies, for each goal s, the target amount, the current savings, the months to
deadline, and the category. User parameters include the liquidity threshold Lmin, the debt-load ceiling Dmax, the
benchmark rate rbench, and the risk profile. The net cash flow and the free resource of the period are
                                                CFt = ∑ ik − ∑ ej,                                             (1)
                                                 Rt = CFt − ∑ Pl.                                              (2)
      The current state is characterized by the liquidity ratio and the debt load:
                                              Lt = Rt / (∑ ej + ∑ Pl),                                         (3)
                                                 Dt = ∑ Pl / ∑ ik.                                             (4)
       Metric (3) expresses what share of the month's total mandatory payments is covered by the free resource
and is interpreted as the operational safety margin of the budget; the norm Lmin = 0.30 follows the ratio system
of [Greninger et al., 1996]. Metric (4) is the debt-service-to-income ratio; the ceiling Dmax = 0.40 corresponds to
the regulatory threshold [Bank of Russia, 2018]. The conditions CFt > 0 and Rt > 0 are necessary for the model
to apply: when they fail, the model does not pick the “least bad” allocation but issues a corrective
recommendation about structural budget revision (fail-loud principle).

2.2. Cash-flow forecasting
      Income and expense series are forecast with simple exponential smoothing [Hyndman et al., 2002]:
                                        ŷt+1 = α yt + (1 − α) ŷt, 0 < α < 1,                                   (5)
       where α = 0.3 places moderate trust in the latest observation, which is typical for monthly financial
series. Forecast uncertainty is assessed by Monte-Carlo simulation [Metropolis, Ulam, 1949]: N = 1000
scenarios are generated around the point forecast with noise whose variance equals the sample variance of
smoothing residuals; the scenarios yield the median and the 95% interval over horizons h = 1, …, 3 months. In
the original model specification, the forecasting block is purely diagnostic — it estimates the risk of a resource
deficit; Section 3.3 integrates it directly into the utility function.

2.3. Alternative generation and the early-repayment rate filter
       An allocation alternative is a triple a = (xd, xr, xg) of amounts directed, respectively, to early debt
repayment, to the liquidity reserve, and to goals, subject to xd + xr + xg = max(Rt, 0) and non-negativity. The set
of alternatives is generated by discretizing the shares with step 0.2, which by the stars-and-bars scheme yields
21 variants — from “all to early repayment” to “all to goals”. The discretization step balances coverage against
cognitive load: every alternative remains explainable to the user in terms of shares.
       The amount xd is distributed across loans by the highest-rate-first strategy [Bach, 2004; Amar et al.,
2011] with an additional economic filter: early repayment applies only to obligations whose rate is no lower
than the opportunity cost of placing the funds
                                            Otgt = {l ∈ O : rl ≥ rbench},                                      (6)
      where rbench = 0.14 is a benchmark return on savings instruments (the parameter is revised as market
conditions change). If all loans are cheaper than the threshold, the xd component is redirected to goals: a ruble
placed at a higher rate is economically more productive than a ruble that repays cheap debt. After partial
repayment, the annuity payment is recomputed for the unchanged term, which reduces the total payment by
δP(a) and consequently lowers the debt load Dt(a).

2.4. Goal attainment with categories and urgency
      Goals carry category weights: investment in income growth — 3.0 (the priority of human-capital
investment [Becker, 1964]), safety — 2.0, material goals — 1.0, emotional goals — 0.5. Goal urgency grows as
the deadline approaches:
                                          us = max(1, 12 / max(τs, 1)).                                        (7)
      The amount xg is distributed across active goals in proportion to the product of category weight and
urgency, with the constraint of not saving beyond the target amount; any surplus is redistributed by the same
proportion. The weighted goal attainment for alternative a is
                                      St(a) = ∑s (Cs + ΔCs(a)) ws us / ∑s Tstgt ws us,                                   (8)
      where ΔCs(a) is the contribution to goal s under the alternative. Metric (8) lies in the unit interval by
construction and is interpreted as the share of the weighted goal total already covered by savings.

2.5. Feasibility constraints
       An alternative is feasible if the state remains in the safe zone after applying it:
                                         Lt(a) ≥ Lmin, Dt(a) ≤ Dmax, Rt(a) ≥ 0,                                          (9)
       where the metrics are recomputed for the allocation: the liquidity numerator decreases by the amounts
directed out of the resource, and the denominator decreases by δP(a). Constraint checking is prioritized as a
cascade — debt load first, then liquidity, then non-negativity of the remainder — so critical constraints are
resolved before any discretionary choice. An empty feasible set is treated as a diagnosis: the model reports
which constraint is violated and why, instead of returning the formally “best” infeasible alternative.

2.6. Normalization, aggregation, and risk profiles
      Before aggregation, the heterogeneous criteria are mapped to the unit interval. The natural and widely
used choice is min-max normalization over the current feasible set [Jain et al., 2005]:
                                        x̂ (a) = (x(a) − min x) / (max x − min x).                                      (10)
       The integral utility of an alternative is the additive aggregation [Fishburn, 1967] with the debt-load term
inverted, since its reduction is preferred:
             U(a) = wR R̂ (a) + wL L̂ (a) + wD (1 − D̂ (a)) + wS Ŝ(a), ∑ w = 1; a = arg max U(a*).             (11)
       The weights encode the user's financial strategy and are set by one of five risk profiles (Table 2); the
balanced profile is the default. The explicit utility function makes the model tunable without changing the
algorithm and explainable: for any recommendation, the contribution of each criterion can be shown.
Table 2. Risk profiles and criterion weights
            Profile                wR (resource)           wL (liquidity)            wD (debt)             wS (goals)
 Conservative                  0.20                    0.45                   0.25                  0.10
 Moderate                      0.20                    0.35                   0.25                  0.20
 Balanced                      0.25                    0.30                   0.25                  0.20
 Active                        0.30                    0.20                   0.20                  0.30
 Aggressive                    0.35                    0.10                   0.15                  0.40




Fig. 1. The decision cycle. The dashed arrow marks the integration of the forecasting block into the utility function (the
                                              refinement of Section 3.3)

3. Computational study
3.1. Experimental design and demonstration profiles
       The model is implemented in Python (the experiment source code is available on request; see Additional
information). The study uses three demonstration profiles covering qualitatively different state zones (Table 3):
profile A — over-indebted (debt load above the regulatory ceiling), profile B — typical (liquidity near the Lmin
threshold), profile C — comfortable (substantial free resource). Profiles B and C each include three goals of
different categories (a safety reserve, professional retraining, a vacation) and loans with different rates, of
which the mortgage (8.5%) fails filter (6) at rbench = 0.14, while the consumer loans (19–27%) pass. For each
profile, three liquidity-threshold regimes Lmin ∈ {0; 0.15; 0.30} and five risk profiles were examined; ranking
stability was tested by perturbing each weight of the balanced profile by ±0.05 with renormalization (eight
perturbations).
Table 3. Demonstration profiles (amounts in rubles per month)
                Metric                    A (over-indebted)                  B (typical)             C (comfortable)
 Income ∑ ik                           90,000                     135,000                    167,000
 Expenses ∑ ej                         40,000                     60,000                     36,500
 Payments ∑ Pl                         38,299                     33,622                     30,327
 Loans (rate)                          card (27%), consumer       card (27%), consumer       consumer (19%), mortgage
                                       (22%)                      (22%), mortgage (8.5%)     (8.5%)
 Free resource Rt                      11,701                     41,378                     100,173
 Liquidity Lt                          0.149                      0.442                      1.499
 Debt load Dt                          0.426                      0.249                      0.182
 Balance Bt                            30,000                     90,000                     150,000


3.2. Behavior of the original criteria specification
      On profile A, the feasible set is empty under every threshold regime: the debt load exceeds Dmax = 0.40,
and even directing the entire resource to early repayment lowers it only to 0.413. The model correctly refuses to
choose and issues a corrective recommendation to reduce the debt load — the protective cascade works as
designed.
      On profiles B and C, the ranking degenerates (Table 4). Tightening the liquidity threshold monotonically
shrinks the feasible set (from 19 to 3 alternatives on profile B), yet the optimal alternative is the same for all five
risk profiles: “the entire resource to the reserve”. The only exception is the aggressive profile on the
comfortable profile C at Lmin = 0.30. The ranking is formally stable — all eight weight perturbations preserve
the optimum — but here stability is a symptom rather than a virtue: the ranking is insensitive to user
preferences as well.
Table 4. Original specification: feasible-set size and the number of distinct optima across the five risk profiles
      Profile                        Lmin = 0                            Lmin = 0.15                    Lmin = 0.30
 A                       infeasible (fail-loud diagnosis)   infeasible                     infeasible
 B                       19 alternatives; 1 optimum         10; 1 optimum (0/100/0)        3; 1 optimum (0/100/0)
                         (0/100/0)
 C                       17; 1 optimum (0/100/0)            15; 1 optimum (0/100/0)        14; 2 optima


       The causes of the degeneracy follow from criterion analysis. First, the resource and liquidity criteria in
the original specification are computed from the same quantity — the unallocated remainder: the numerator of
Lt(a) coincides with Rt(a), while the denominator is nearly constant across alternatives. Their sample
correlation over the 21 alternatives is 0.9998 (profile B) and 0.99979 (profile C): two of the four criteria are
effectively one, and the combined weight of “keeping the funds” reaches 0.45–0.65 depending on the risk
profile. Second, min-max normalization (10) stretches any criterion range — including an economically
negligible one — to the full unit interval: early repayment changes profile C's debt load only from 0.182 to
0.157, yet after normalization this difference weighs as much as the full resource range. The sensitivity of
multi-criteria rankings to the normalization procedure is known in the literature [Vafaei et al., 2018]; here it is
amplified by criteria collinearity and produces a systematic bias.

3.3. Refinement: a forecast-based resource criterion, stock liquidity, and norm-anchored normalization
       The proposed refinement preserves the model structure — the alternative set, the rate filter, the weighted
goals, and the constraint cascade (9) remain unchanged — and modifies only the criteria specification in
aggregation (11). Three changes remove the identified defects.
       First, the resource criterion is replaced by a forecast of next-period free cash flow:
                                         R̂ t+1(a) = Ît+1 − Êt+1 − (∑ Pl − δP(a)),                                    (12)
      where Ît+1 and Êt+1 are the forecasts (5) of the income and expense series. The criterion stops rewarding
fund retention: the current balance does not enter (12), and early repayment raises the future resource through
lower payments. The forecasting block, which served only a diagnostic function in the original model, thereby
becomes part of the utility function.
       Second, the liquidity criterion switches from flow to stock:
                                      Lstk(a) = (Bt + xr) / (∑ ej + ∑ Pl − δP(a)),                                    (13)
       i.e., it measures the number of months of mandatory payments covered by the accumulated stock of
funds — an alternative-dependent analogue of the basic liquidity ratio [Greninger et al., 1996]. Now the reserve
component xr — and only it — improves this criterion, which removes the collinearity: each allocation
direction primarily improves its own criterion (early repayment — the future resource and the debt load, the
reserve — the liquidity stock, goals — goal attainment).
       Third, normalization is anchored not to the sample range but to meaningful scale anchors: the forecast
resource (12) is normalized by the forecast net flow Ît+1 − Êt+1 (the share of the future flow that remains free); the
stock (13) — by the upper liquidity-stock norm of six months [Greninger et al., 1996]; the debt load — by the
regulatory ceiling Dmax [Bank of Russia, 2018]; goal attainment (8) already lies in the unit interval. All
normalized values are clipped to the unit interval. Norm-anchored normalization has three consequences:
economically small criterion differences remain small after normalization; the scales do not depend on the
composition of the alternative set, which rules out rank reversal when it changes; and every normalized value is
interpretable to the user in terms of accepted financial norms, which directly supports the explainability
requirement.

3.4. Results of the refined model
       On the same profiles and at the same threshold Lmin = 0.30, the refined model behaves qualitatively
differently (Table 5, Fig. 2). On the comfortable profile C, recommendations differentiate monotonically with
risk appetite: the conservative, moderate, and balanced profiles build the reserve; the active profile directs 60%
of the resource to goals; the aggressive profile additionally prepays the consumer loan (19% per annum) — the
only obligation that passes filter (6) — while the mortgage (8.5%) is correctly excluded from early repayment
as cheaper than the alternative placement of funds. On the typical profile B, where only three feasible
alternatives survive the constraint cascade, differentiation is expectedly weaker: the conservative profile
chooses the pure reserve, the others — the reserve with partial goal funding. This illustrates a general property
of the model: in the constrained zone, the decision is driven mostly by the protective constraints; in the
comfortable zone — by user preferences. Profile A still receives a corrective recommendation.
Table 5. Refined model: optimal alternatives (early repayment / reserve / goals, % of the resource) at L min = 0.30
              Risk profile                              B (typical)                                C (comfortable)
 Conservative                             0 / 100 / 0                                0 / 100 / 0
 Moderate                                 0 / 80 / 20                                0 / 100 / 0
 Balanced                                 0 / 80 / 20                                0 / 100 / 0
 Active                                   0 / 80 / 20                                0 / 40 / 60
 Aggressive                               0 / 80 / 20                                20 / 20 / 60
 Fig. 2. Utility U(a) of profile C's feasible alternatives across the five risk profiles (refined model). The star marks the
                profile's optimal alternative. The viridis colormap remains monotone in monochrome print

       Ranking stability was tested by perturbing the balanced profile's weights by ±0.05. On profile B, the
optimum survives all eight perturbations. On profile C, it survives six of eight; in two cases (lowering the
liquidity weight or raising the goal weight by 0.05), the optimum switches to the structurally adjacent
alternative “0/40/60” with a utility difference below 0.007. This behavior is boundary-like rather than chaotic:
the balanced profile of a comfortable user sits near the border between the “reserve” and “goals” zones, and a
small preference shift moves the recommendation into the neighboring zone. For practice this implies showing
the user not only the optimum but also the alternatives closest in utility.

3.5. The forecasting block and computational efficiency




 Fig. 3. Forecast of profile C's free resource: the smoothed series, the median forecast, and the 95% interval over 1000
                                                   Monte-Carlo scenarios

       Figure 3 illustrates the stochastic forecast of profile C's free resource on a synthetic 18-month series: the
three-month median is 101.0 thousand rubles with a 95% interval from 88.4 to 114.6 thousand rubles. The
interval estimate serves two purposes: in criterion (12) — through the point forecast, and in the explanation of a
recommendation — as an honest characterization of uncertainty (“with 95% probability, your free resource in
three months will be between … and …”). The computational complexity of the cycle is linear in the numbers
of alternatives, obligations, and scenarios; in the Python implementation, a full cycle — generating and
evaluating 21 alternatives, the filters, normalization, and ranking for five profiles — takes 0.7 ms, and the
stochastic forecast (1000 scenarios, three-month horizon) takes 0.9 ms. The total is under two milliseconds per
decision, which comfortably supports interactive use, including instant recomputation when the user changes
weights or inputs.
4. Discussion
       The main methodological result is that the “natural” criteria specification — resource and liquidity
computed from the unallocated remainder plus min-max normalization — looks correct and passes functional
testing on typical scenarios, yet systematically degenerates the ranking. The defect is invisible at the level of
individual formulas and is revealed only by a computational study of the model as a whole: criteria collinearity
(correlation above 0.999) and the normalization-driven stretching of negligible ranges jointly reduce the multi-
criteria problem to a single-criterion one. This argues for mandatory computational studies of decision-support
models before deployment — functional correctness is not enough.
       The proposed norm-based anchoring of scales appears transferable beyond this problem: wherever
meaningful norms exist for the criteria (regulatory thresholds, industry benchmarks), normalizing to them is
preferable to the sample range — it preserves the economic scale of differences, removes the dependence on
the composition of alternatives, and makes normalized values interpretable. The latter property connects
directly to the explainability requirement [Rudin, 2019; Miller, 2019]: the user sees scores as “shares of a
norm” rather than arbitrary units.
       The limitations of this work define its development directions. First, the study uses demonstration
profiles that systematically cover qualitatively different state zones; longitudinal validation on real user data is
a separate study. Second, the risk-profile weights are set expertly; eliciting them from user preferences (for
example, via pairwise comparisons) and calibrating the boundaries of recommendation-switching zones
require a controlled user experiment. Third, the forecasting block is limited to simple exponential smoothing;
series with seasonality and structural shifts call for more expressive models, while keeping interval uncertainty
estimates. Fourth, the threshold rate of the early-repayment filter is a constant and should be updated from
market data. Finally, the model is deterministic with respect to goal categories; automatic transaction
categorization and the architectural organization of the software implementation are separate problems and are
not considered here.

Conclusion
       This paper formulated a multi-criteria model for allocating a user's free cash flow between early debt
repayment, a liquidity reserve, and savings goals: alternative generation by share discretization, an early-
repayment filter based on an opportunity-cost rate threshold, weighted goal scoring with categories and
urgency, a feasibility cascade over liquidity and debt load, stochastic cash-flow forecasting, and additive
criteria aggregation by risk profile.
       A computational study on three demonstration profiles under three liquidity-threshold regimes revealed
the degeneracy of the original criteria specification: the collinearity of the resource and liquidity criteria
(correlation above 0.999) combined with min-max normalization biases the ranking toward reserve allocations
regardless of the risk profile. The proposed refinement — a forecast-based resource criterion that embeds the
forecasting block into the utility function, a stock-based liquidity criterion, and norm-anchored normalization
— restores meaningful differentiation: conservative profiles build the reserve, active profiles fund goals, and
the aggressive profile additionally prepays expensive debt, with the opportunity-cost filter correctly excluding
the cheap mortgage from early repayment. The ranking is stable under small weight perturbations, the
protective cascade retains its corrective behavior on the over-indebted profile, and a full computation cycle
takes under two milliseconds.
       Comparison with known results confirms the general finding in the literature that the normalization
procedure substantially affects multi-criteria rankings [Jain et al., 2005; Vafaei et al., 2018] and sharpens it for
resource-allocation problems: with collinear criteria, sample-based normalization does not merely reorder
alternatives — it systematically degenerates the problem. Future work includes eliciting weights from user
preferences, longitudinal validation on real data, extending the forecasting block, and calibrating the norm
anchors of the scales from market data.

Additional information
      Acknowledgements. The author thanks I. S. Bondarenko (NUST MISIS) for supervising the work
within which this study was carried out.
      Funding. This research received no external funding.
      Conflict of interest. The author declares no conflict of interest.
      Data and code availability. The source code of the model and of the computational experiment,
reproducing all tables and figures, as well as the anonymized data of the survey mentioned in the Introduction,
are available from the author on reasonable request.

References
Amar M., Ariely D., Ayal S., Cryder C. E., Rick S. I. Winning the battle but losing the war: the psychology of
debt management // Journal of Marketing Research. — 2011. — Vol. 48, SPL. — P. S38–S50. DOI:
10.1509/jmkr.48.SPL.S38.
Arrieta A. B., Díaz-Rodríguez N., Del Ser J. et al. Explainable artificial intelligence (XAI): concepts,
taxonomies, opportunities and challenges toward responsible AI // Information Fusion. — 2020. — Vol. 58. —
P. 82–115. DOI: 10.1016/j.inffus.2019.12.012.
Bach D. The Automatic Millionaire: a powerful one-step plan to live and finish rich. — New York: Broadway
Books, 2004. — 272 p.
Bank of Russia. Ordinance No. 4892-U of 31 August 2018 on types of assets and risk-weight add-ons. —
Moscow: Bank of Russia, 2018 (in Russian).
Becker G. S. Human capital: a theoretical and empirical analysis, with special reference to education. — New
York: Columbia University Press, 1964. — 187 p.
Blokhina I. M., Ayvazyan N. S., Kazakova L. V., Fedosova Yu. V. Features of personal finance management in
modern conditions // Estestvenno-gumanitarnye issledovaniya. — 2025. — No. 3 (59). — P. 624–629 (in
Russian).
Fishburn P. C. Methods of estimating additive utilities // Management Science. — 1967. — Vol. 13, No. 7. —
P. 435–453. DOI: 10.1287/mnsc.13.7.435.
Gomber P., Koch J.-A., Siering M. Digital finance and FinTech: current research and future research
directions // Journal of Business Economics. — 2017. — Vol. 87. — P. 537–580. DOI: 10.1007/s11573-017-
0852-x.
Greninger S. A., Hampton V. L., Kitt K. A., Achacoso J. A. Ratios and benchmarks for measuring the financial
well-being of families and individuals // Financial Services Review. — 1996. — Vol. 5, No. 1. — P. 57–70.
DOI: 10.1016/S1057-0810(96)90027-X.
Hwang C. L., Yoon K. Multiple attribute decision making: methods and applications. — Berlin: Springer-
Verlag, 1981. — 259 p.
Hyndman R. J., Koehler A. B., Snyder R. D., Grose S. A state space framework for automatic forecasting using
exponential smoothing methods // International Journal of Forecasting. — 2002. — Vol. 18, No. 3. — P. 439–
454. DOI: 10.1016/S0169-2070(01)00110-8.
Jain A., Nandakumar K., Ross A. Score normalization in multimodal biometric systems // Pattern Recognition.
— 2005. — Vol. 38, No. 12. — P. 2270–2285. DOI: 10.1016/j.patcog.2005.01.012.
Kachanova L. S., Plaksa M. A. Customization of personal finance information products as a means of
household economic security // Ekonomika i predprinimatelstvo. — 2025. — No. 6 (179). — P. 1417–1425 (in
Russian).
Lusardi A., Mitchell O. S. The economic importance of financial literacy: theory and evidence // Journal of
Economic Literature. — 2014. — Vol. 52, No. 1. — P. 5–44. DOI: 10.1257/jel.52.1.5.
Lytton R. H., Garman E. T., Porter N. M. How to use financial ratios when advising clients // Financial
Counseling and Planning. — 1991. — Vol. 2. — P. 3–23.
Malyonkina T. M., Ponyaeva E. V. Digitalization of personal finance management // Mnogourovnevoe
obshchestvennoe vosproizvodstvo: voprosy teorii i praktiki. — 2024. — No. 1 (42). — P. 77–81 (in Russian).
Metropolis N., Ulam S. The Monte Carlo method // Journal of the American Statistical Association. — 1949. —
Vol. 44, No. 247. — P. 335–341. DOI: 10.1080/01621459.1949.10483310.
Miller T. Explanation in artificial intelligence: insights from the social sciences // Artificial Intelligence. —
2019. — Vol. 267. — P. 1–38. DOI: 10.1016/j.artint.2018.07.007.
Rudin C. Stop explaining black box machine learning models for high stakes decisions and use interpretable
models instead // Nature Machine Intelligence. — 2019. — Vol. 1. — P. 206–215. DOI: 10.1038/s42256-019-
0048-x.
Vafaei N., Ribeiro R. A., Camarinha-Matos L. M. Data normalisation techniques in decision making: case study
with TOPSIS method // International Journal of Information and Decision Sciences. — 2018. — Vol. 10, No. 1.
— P. 19–38. DOI: 10.1504/IJIDS.2018.090667.
Velasquez M., Hester P. T. An analysis of multi-criteria decision making methods // International Journal of
Operations Research. — 2013. — Vol. 10, No. 2. — P. 56–66.
Zopounidis C., Doumpos M. Multi-criteria decision aid in financial decision making: methodologies and
literature review // Journal of Multi-Criteria Decision Analysis. — 2002. — Vol. 11, No. 4–5. — P. 167–186.
DOI: 10.1002/mcda.333.

Author information
     Vasilii M. Evdokimov — Department of Automated Control Systems, National University of Science
and Technology MISIS, 4 Leninskiy Prospekt, Moscow, 119049, Russia; e-mail: m2201058@edu.misis.ru;
ORCID: 0009-0004-8821-8414.
