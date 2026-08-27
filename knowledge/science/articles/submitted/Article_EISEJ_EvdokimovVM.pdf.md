# Article_EISEJ_EvdokimovVM — выжимка

| | |
|---|---|
| оригинал | `Article_EISEJ_EvdokimovVM.pdf` (рядом, не тронут) |
| тип | PDF |
| размер | 0.4 МБ |
| страниц | 9 |
| извлечено знаков | 23991 |

## Извлечённый текст

> Ниже — **текстовый слой файла**, а не пересказ. Извлечено машинно; смысл, структура
> и то, что было картинкой, здесь не появятся. Оригинал остаётся эталоном.

Eliciting and Prioritising Requirements for an Explainable Personal-
   Finance Decision-Support System: An Empirical Study of Stated
                  versus Revealed Decision Behaviour
                                        Vasilii M. Evdokimov
           National University of Science and Technology MISIS (NUST MISIS), Moscow, Russia
                        ORCID: 0009-0004-8821-8414 · m2201058@edu.misis.ru

Abstract
Background: Personal-finance decision-support systems (DSS) are proliferating, yet adoption depends
less on algorithmic sophistication than on whether a system matches how people actually decide and
whether it earns their trust; requirements for such systems are often derived from domain assumptions
rather than from empirical evidence of user behaviour.
Aim: We derive and prioritise functional and non-functional requirements for an explainable personal-
finance DSS from empirical evidence of user behaviour and acceptance conditions.
Method: We conducted a quantitative survey of 385 respondents (322 valid after attention-check
filtering), combining descriptive statistics, hypothesis testing with effect sizes and Holm correction for
multiplicity, a stated-versus-revealed behavioural probe, a Cronbach's-alpha diagnostic of a four-
criteria decision battery, and thematic coding of open responses; findings were mapped to requirements
and prioritised with RICE and MoSCoW.
Results: We observed a pronounced intention–action gap: 46% of respondents report rational
calculation, but in a concrete task only 10% computed a trade-off while 63% decided emotionally.
Demand for an automated advisor is high (84%) but conditional on transparency (67% require a numeric
explanation; 61% a transparent algorithm), and trust collapses from explanation (74–79%) to
autonomous money movement (16%). Debt presence is strongly associated with the repay-versus-save
dilemma (Cramér's V = 0.62).
Conclusion: The evidence reframes the system as a transparency-first 'external System 2' that computes
the allocation and explains it at the moment of decision. We present a prioritised requirement set in
which explainability and bounded autonomy are non-functional preconditions, and we report lessons
for instrument design.
Keywords: requirements engineering; empirical software engineering; decision-support systems;
personal finance; explainability; user study; RICE; MoSCoW.

1. Introduction
Decisions about how to allocate disposable income — between repaying debt, building a liquidity
reserve and funding goals — are made repeatedly by almost every adult, and their cumulative effect
over years is large. These decisions are also unusually sensitive to error: a misallocation can leave a
household short of liquidity or deepen its debt burden. A growing class of personal-finance applications
and fintech services aims to support such decisions, but in practice most of them display retrospective
statistics rather than recommend a next step, and the recommendations they do offer are rarely
explained.
The difficulty is only partly technical. Two non-technical factors dominate adoption. First, behaviour:
people frequently intend to decide rationally yet fall back on intuition at the moment of choice. Second,
trust: a recommendation that cannot be inspected is easily dismissed, especially when it concerns
money. Requirements for such systems, however, are often derived top-down from domain assumptions
rather than from evidence about how users actually behave and what would make them rely on an
automated advisor.
This paper addresses that gap. We treat the construction of a personal-finance DSS as a requirements-
engineering problem and derive its requirements empirically, from a survey of 385 respondents (322
valid). The study has two distinctive features for software engineering. First, it pairs stated preferences
with a revealed-behaviour probe, exposing an intention–action gap that reframes the system's core
purpose. Second, it treats explainability not as a feature but as a non-functional precondition for
adoption, and shows quantitatively how user trust depends on it. The target system is kept anonymous
throughout; this is a study of method and evidence, not a product description.
We investigate four research questions:
   — RQ1. How do individuals currently manage personal-finance allocation, and which tools and
     methods do they use?
   — RQ2. Is there a gap between stated (intended) rational decision-making and revealed behaviour
     in a concrete task?
   — RQ3. Which functional and non-functional requirements for a DSS can be derived from user
     pains and expectations, and how should they be prioritised?
   — RQ4. What conditions govern user acceptance of an automated financial advisor, in particular
     regarding explainability and autonomy?
The remainder of the paper is organised as follows. Section 2 reviews background and related work.
Section 3 describes the study design. Section 4 reports results by research question. Section 5 derives
and prioritises the requirements. Section 6 discusses threats to validity, and Section 7 concludes.

2. Background and Related Work
Requirements elicitation through surveys and questionnaires is a standard technique in requirements
engineering, valued for reach and comparability, and limited by self-report bias and shallow coverage
[7, 8, 16]. Our design follows the empirical-software-engineering tradition of pairing elicitation with
explicit validity analysis [16, 17], and augments self-report with a behavioural probe to mitigate the
best-known weakness of surveys.
The behavioural framing draws on dual-process theory, which distinguishes fast, intuitive judgement
from slow, deliberate reasoning [1], and on the intention–behaviour gap documented in social
psychology, whereby stated intentions translate only weakly into action [2, 3]. In the financial domain,
this gap motivates interventions that lower the effort of the deliberate path [15]. We use these ideas not
to model users but to interpret an observed discrepancy and to motivate a design that performs the
computation on the user's behalf.
Acceptance and trust are treated through the technology-acceptance literature [6] and research on trust
in automation, which shows that appropriate reliance depends on transparency and on the match
between perceived and actual system capability [4]. Work on explanation in artificial intelligence
stresses that useful explanations are contrastive and audience-appropriate [5]. These results justify our
decision to elevate explainability to a non-functional requirement and to bound the system's autonomy.
For prioritisation we use two widely adopted schemes: MoSCoW categorisation [10] and RICE scoring,
complementing the qualitative ordering with a reach–impact–confidence–effort estimate.

3. Study Design
3.1. Objectives and research questions
The objective was to obtain an evidence base for the requirements of a personal-finance DSS, covering
current practice (RQ1), the stated–revealed behaviour gap (RQ2), derived and prioritised requirements
(RQ3), and acceptance conditions (RQ4). The study is observational and cross-sectional.

3.2. Instrument
Data were collected with an online questionnaire of 77 items (62 substantive questions; the remainder
matrix sub-items and service fields). The instrument comprised blocks on current financial
management; perceived pains and expectations; a four-criteria importance battery (disposable resource,
liquidity, debt burden, safety); a behavioural case task contrasting stated and revealed decision-making;
attitudes towards an automated advisor and its acceptable degree of autonomy; willingness to pay; and
demographics. An attention check ('select seven stars') was embedded to identify inattentive
submissions.

3.3. Sample and data cleaning
The questionnaire received 385 responses. After removing 63 submissions that failed the attention
check, 322 valid responses remained; submissions collected before the attention check was introduced
and otherwise consistent were retained. Because the instrument was extended during data collection
and the closed questions were mandatory, the valid base size varies by item rather than reflecting
dropout; the representativeness of the later cohort was checked against the earlier one. Three sub-blocks
(the criteria battery, the behavioural case and the AI-trust items) rest on approximately 19 responses
and are reported as preliminary.

3.4. Analysis
Descriptive statistics summarise practice, pains and expectations. Associations were tested with the chi-
square test and reported with Cramér's V as an effect size [11, 14]; no p-value is reported without an
accompanying effect size, and the Holm step-down procedure was applied to control the family-wise
error rate across multiple comparisons [12]. The stated–revealed comparison contrasts the proportion
claiming rational calculation with the proportion that actually computed in the case task. The internal
structure of the four-criteria battery was examined with Cronbach's alpha [13]. Open responses were
coded thematically. Finally, findings were mapped to candidate requirements, which were prioritised
with RICE and MoSCoW [10]. One planned block — a drag-and-drop ranking of criteria — produced
only five valid permutations out of nineteen because of the form's interaction mechanics and was
excluded from analysis; we return to this as a methodological lesson in Section 6.

4. Results
4.1. RQ1 — Current practice
Most respondents rely on passive, retrospective tools: 70.1% use the statistics built into their banking
application, 23.1% keep notes on their phone, 20.3% use a spreadsheet and 18.7% use a dedicated
budgeting application; 11.4% use nothing at all and 7% use AI assistants (Figure 1). The dominant
theme in open responses about abandoning previous tools was that they 'only show statistics' and
provide no next step. Current practice is therefore oriented towards looking back at spending rather than
deciding what to do with money that remains.
                     Figure 1. Tools used to manage personal finances (multiple choice).

4.2. RQ2 — The intention–action gap
When asked how they decide where to direct money, 46% described a rational, calculated approach. In
a concrete case task — answered by a smaller behavioural sub-sample — only 10% actually performed
a calculation, while 63% reported deciding on emotion, a gap of 36 percentage points between stated
and revealed behaviour (Figure 2). The pattern is consistent with dual-process accounts [1]: deliberate
reasoning is claimed in the abstract but is displaced by fast, intuitive judgement at the moment of
decision. This is the study's central finding, and although the revealed-behaviour probe is indicative
rather than definitive, it is corroborated by the large-sample demand for transparency (Section 4.4) and
reframes the system's purpose: the value of a DSS here is less to inform a calculation the user would
otherwise perform than to perform the calculation on the user's behalf and present the result at the
moment of hesitation — an 'external System 2'.




     Figure 2. The intention–action gap: a rational approach is claimed far more often than it is enacted.

4.3. RQ3 — Pains and expectations
The single strongest expectation was visibility of disposable cash flow: how much money remains after
all obligatory payments was the top must-have (61%) and ranked highest under RICE scoring. Beyond
it, 62% wanted to compare alternatives, 48% wanted to see the consequences of a choice in advance,
and 38% wanted a predictive warning of an impending shortfall. The most cited pains were an
overloaded interface and not knowing where to start, a predictive 'funds will be insufficient' concern
(32%), and the absence of any explanation of the advice given (22%). On the preferred form of advice,
59% favoured a visualisation or comparison, 45% wanted concrete numbers, and 19% wanted a single
short action — a split that argues for layering rather than choosing one format.

4.4. RQ4 — Acceptance conditions
Demand for an automated advisor was high (84%) but explicitly conditional: 67% said they would trust
it only if it explained its reasoning with numbers, and 61% only if the algorithm were transparent.
Acceptance also depended sharply on autonomy. Trust was high for an advisor that computes or
explains (74–79%) but collapsed to 16% for one that decides and moves money by itself (Figure 3),
implying a recommend-and-confirm interaction rather than an autopilot.




    Figure 3. Acceptance is conditional on transparency and collapses when the system acts autonomously.

Two debt-related results are notable. The presence of debt was strongly associated with experiencing
the repay-versus-save dilemma (Cramér's V = 0.62), and 40% of respondents with debt reported facing
it; debtors were also significantly more anxious about missing a payment. Finally, the four-criteria
importance battery returned a low Cronbach's alpha (0.632). Rather than indicating an unreliable scale,
this is consistent with the criteria measuring largely independent constructs — empirical support for
treating them as separate, independently weighted dimensions rather than collapsing them into one
score. Willingness to pay was modest: 54% would pay no more than 200 RUB per month, a constraint
with direct consequences for the business model.

5. From Findings to Requirements
Three design principles follow directly from the evidence and govern the requirements below. First,
transparency is a precondition, not an embellishment: demand for an advisor is high but conditional on
numeric, inspectable explanations (Section 4.4). Second, the system should act as an external System 2
— it should perform the computation and present the result at the moment of decision, because users
intend to calculate but do not (Section 4.2). Third, it should advise and wait for confirmation rather than
act autonomously, because trust in autonomous money movement is very low (Section 4.4).
Table 1 lists the functional (FR) and non-functional (NFR) requirements derived from the findings, each
traced to its supporting evidence and prioritised with MoSCoW. RICE scoring was applied in parallel;
the requirement to surface disposable cash flow scored highest (RICE 1.83) and, together with the
explainability requirement, anchors the minimum viable product. The catalogue is deliberately
transparency-first: the explanation of a recommendation is itself a Must-have requirement, not an
optional addition to a recommender.
        Table 1. Requirements derived from the study, with supporting evidence and MoSCoW priority.
 Requirement                           Type     Key empirical evidence                        Priority
 Compute and surface disposable        FR       Top expectation (61% must-have); highest-     Must
 cash flow (income − expenses −                 ranked item under RICE (1.83)
 obligatory payments) as the
 primary screen
 Generate an allocation                FR       Core unmet need: 'does not tell me where to   Must
 recommendation across debt                     put the money' (open responses)
 repayment, reserve and goals
 Explain each recommendation: the      FR/NFR   'Does not explain the logic of advice' —      Must
 underlying calculation, the                    pain for 22%; 67% trust only with a
 compared alternatives, and why                 numeric explanation; 61% require a
 others were rejected                           transparent algorithm
 Let the user compare the top          FR       62% want to compare alternatives              Should
 alternatives, not only the best one
 Provide 'what-if' scenarios with      FR       48% want to see consequences of a choice      Should
 instant recomputation of indicators            in advance
 Raise a predictive 'funds will be     FR       Pain for 32%; expectation for 38%             Should
 insufficient' alert before a due
 payment
 Give a direct, explained 'repay-vs-   FR       Strongest association in the data (debt ↔     Should
 save' verdict                                  dilemma, V = 0.62); 40% of debtors faced it
 Trigger a recommendation at the       FR       Intention–action gap: computation is needed   Should
 moment income arrives                          at the moment of hesitation
 Segmented onboarding with             FR       Format preferences split: 59% visual, 45%     Should
 layered advice (verdict → numbers              numeric, 19% short action
 → visual)
 Risk-based payment reminders          FR       Debtors fear missed payments (H4); but        Could
 (only on real risk)                            notifications are the 3rd irritant (25%)
 Minimal cognitive load: one key       NFR      'Overloaded interface' and 'do not know       Must
 indicator and one action per screen            where to start' are top irritants
 Human-in-the-loop: never move         NFR      Trust collapses from explain/compute (74–     Must
 money autonomously                             79%) to autonomous transfer (16%)
 Reproducibility and determinism       NFR      Transparency precondition; auditability of    Must
 of every recommendation                        advice
 Affordability / freemium model        NFR      54% willing to pay ≤ 200 RUB per month        Could
 Autonomous financial actions          —        Lowest trust (16%); out of scope by design    Won't (now)

The prioritisation makes the dependency structure explicit. The Must-have set establishes the trust
foundation — a single, clearly explained disposable-cash-flow figure, an explained recommendation,
low cognitive load and a human-in-the-loop guarantee — and consists largely of exposing computation
the engine can already perform rather than of new algorithms. The Should-have set addresses the
strongest specific pains: the repay-versus-save verdict (the largest effect in the data), the predictive
shortfall alert, what-if scenarios and the moment-of-decision trigger. Could-have and Won't-have items
reflect either weak demand under a tight willingness-to-pay ceiling or the explicit autonomy boundary.
6. Validity and Scope
The design controls the principal validity concerns. The central finding — the intention–action gap —
is established not by self-report alone but by contrasting stated approach with revealed behaviour in a
concrete task, with inattentive respondents removed by an attention check; any residual desirability bias
would inflate the stated-rational figure and thus widen rather than create the gap. The behavioural probe
is answered by a smaller sub-sample and is therefore indicative, but it converges with the large-sample
demand for transparency. Associations are reported with effect sizes and the family-wise error rate is
controlled with the Holm procedure, so the reported relationships are conservative.
The four-criteria battery returned a low Cronbach's alpha (0.632), which we read as evidence that the
criteria capture largely independent constructs rather than as low reliability; confirming this with a
confirmatory factor analysis on a larger sample is a natural next step. The study draws on a longitudinal
real-world evidence base and on a focused first segment of respondents — younger, capital-city users
with modest income and small debts — for whom the design is directly applicable; extending the
evidence to debt-bearing households is the main aim of the planned second wave. A drag-and-drop
ranking block was excluded after its interaction mechanics produced inconsistent permutations, which
motivates the instrument-design recommendation to favour pairwise comparison or fixed-budget point
allocation.

7. Conclusion
We derived and prioritised requirements for an explainable personal-finance decision-support system
from an empirical study of 385 respondents (322 valid), combining descriptive and inferential statistics
with a stated-versus-revealed behavioural probe. The central result is an intention–action gap — 46%
claim to calculate, 10% actually do — which reframes the system as an external System 2 that performs
the computation and presents the result at the moment of decision. Acceptance of such a system is high
but conditional on transparency and on bounded autonomy, which we therefore encode as non-
functional preconditions. The resulting transparency-first requirement set, prioritised with RICE and
MoSCoW, places an explained disposable-cash-flow recommendation at the centre of the minimum
viable product.
For software engineering practice, the study illustrates the value of pairing requirements elicitation with
a behavioural probe and of treating explainability as a first-class requirement in decision-support
systems. Future work includes a second survey wave that broadens the sample to debt-bearing
households, enlarges the under-powered sub-blocks, replaces the invalidated ranking instrument, and
confirms the independence of the four decision criteria through confirmatory factor analysis.

Acknowledgements
The author thanks I. S. Bondarenko for scientific supervision.

Declarations
Author contributions (CRediT): V. M. Evdokimov — Conceptualisation, Methodology, Software,
Formal analysis, Investigation, Data curation, Writing – original draft, Writing – review and editing,
Visualisation.
Declaration of generative AI: During the preparation of this work the author used a generative AI
assistant to support data analysis, drafting and language editing. The author reviewed and edited the
content and takes full responsibility for it.
Funding: none. Conflicts of interest: the author declares no conflict of interest. Data availability: the
anonymised survey data are available from the author on reasonable request.

References
 1. Kahneman D. Thinking, Fast and Slow. New York: Farrar, Straus and Giroux, 2011.
 2. Sheeran P. Intention–behavior relations: A conceptual and empirical review. European Review of Social
     Psychology, 2002, vol. 12, no. 1, pp. 1–36.
 3. Sheeran P., Webb T. L. The intention–behavior gap. Social and Personality Psychology Compass, 2016,
     vol. 10, no. 9, pp. 503–518.
 4. Lee J. D., See K. A. Trust in automation: Designing for appropriate reliance. Human Factors, 2004, vol. 46,
     no. 1, pp. 50–80.
 5. Miller T. Explanation in artificial intelligence: Insights from the social sciences. Artificial Intelligence,
     2019, vol. 267, pp. 1–38.
 6. Davis F. D. Perceived usefulness, perceived ease of use, and user acceptance of information technology.
     MIS Quarterly, 1989, vol. 13, no. 3, pp. 319–340.
 7. Sommerville I. Software Engineering. 10th ed. Harlow: Pearson, 2015.
 8. Pohl K. Requirements Engineering: Fundamentals, Principles, and Techniques. Berlin: Springer, 2010.
 9. Glinz M. On non-functional requirements. Proc. 15th IEEE International Requirements Engineering
     Conference (RE'07), 2007, pp. 21–26.
 10. Clegg D., Barker R. Case Method Fast-Track: A RAD Approach. Wokingham: Addison-Wesley, 1994.
 11. Cohen J. Statistical Power Analysis for the Behavioral Sciences. 2nd ed. Hillsdale: Lawrence Erlbaum,
     1988.
 12. Holm S. A simple sequentially rejective multiple test procedure. Scandinavian Journal of Statistics, 1979,
     vol. 6, no. 2, pp. 65–70.
 13. Cronbach L. J. Coefficient alpha and the internal structure of tests. Psychometrika, 1951, vol. 16, no. 3, pp.
     297–334.
 14. Cramér H. Mathematical Methods of Statistics. Princeton: Princeton University Press, 1946.
 15. Thaler R. H., Benartzi S. Save More Tomorrow: Using behavioral economics to increase employee saving.
     Journal of Political Economy, 2004, vol. 112, no. S1, pp. S164–S187.
 16. Hofmann H. F., Lehner F. Requirements engineering as a success factor in software projects. IEEE Software,
     2001, vol. 18, no. 4, pp. 58–66.
 17. Wohlin C., Runeson P., Höst M., Ohlsson M. C., Regnell B., Wesslén A. Experimentation in Software
     Engineering. Berlin: Springer, 2012.
