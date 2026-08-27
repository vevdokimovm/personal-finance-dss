# e_informatica_draft_proof — выжимка

| | |
|---|---|
| оригинал | `e_informatica_draft_proof.pdf` (рядом, не тронут) |
| тип | PDF |
| размер | 0.5 МБ |
| страниц | 10 |
| извлечено знаков | 33727 |

## Извлечённый текст

> Ниже — **текстовый слой файла**, а не пересказ. Извлечено машинно; смысл, структура
> и то, что было картинкой, здесь не появятся. Оригинал остаётся эталоном.

e-Informatica Software Engineering Journal




      Eliciting and Prioritising Requirements for an Explainable
      Personal-Finance Decision-Support System: An Empirical
         Study of Stated versus Revealed Decision Behaviour

                 Journal:   e-Informatica Software Engineering Journal

           Manuscript ID    Draft



                  Fo
        Manuscript Type:

  Date Submitted by the
                Author:
                            Research article

                            n/a

Complete List of Authors:
                            rR
                            Evdokimov, Vasilii; NUST MISIS, ACS

                            Software requirements engineering and modeling, Internet software
              Keywords:

                                    ev
                            systems development, Empirical and experimental studies in software
                            engineering (incl., Formal methods in software engineering.




                                         iew
                                                     On
                                                             ly




                       https://mc.manuscriptcentral.com/e-informaticasej
Page 1 of 8                                  e-Informatica Software Engineering Journal


1
2
3
4              Eliciting and Prioritising Requirements for an Explainable Personal-
5                Finance Decision-Support System: An Empirical Study of Stated
6
7
                                versus Revealed Decision Behaviour
8                                                     Vasilii M. Evdokimov
9
                         National University of Science and Technology MISIS (NUST MISIS), Moscow, Russia
10
11                                    ORCID: 0009-0004-8821-8414 · m2201058@edu.misis.ru
12
13            Abstract
14
15            Background: Personal-finance decision-support systems (DSS) are proliferating, yet adoption depends
16            less on algorithmic sophistication than on whether a system matches how people actually decide and
17            whether it earns their trust; requirements for such systems are often derived from domain assumptions
18            rather than from empirical evidence of user behaviour.
19
20            Aim: We derive and prioritise functional and non-functional requirements for an explainable personal-
21            finance DSS from empirical evidence of user behaviour and acceptance conditions.
22
23
24
                                      Fo
              Method: We conducted a quantitative survey of 385 respondents (322 valid after attention-check
              filtering), combining descriptive statistics, hypothesis testing with effect sizes and Holm correction for
25
26
27
28
                                             rR
              multiplicity, a stated-versus-revealed behavioural probe, a Cronbach's-alpha diagnostic of a four-
              criteria decision battery, and thematic coding of open responses; findings were mapped to requirements
              and prioritised with RICE and MoSCoW.
29
30
31
                                                    ev
              Results: We observed a pronounced intention–action gap: 46% of respondents report rational
              calculation, but in a concrete task only 10% computed a trade-off while 63% decided emotionally.



                                                           iew
32            Demand for an automated advisor is high (84%) but conditional on transparency (67% require a numeric
33            explanation; 61% a transparent algorithm), and trust collapses from explanation (74–79%) to
34
35
              autonomous money movement (16%). Debt presence is strongly associated with the repay-versus-save
36            dilemma (Cramér's V = 0.62).


                                                                      On
37
38
              Conclusion: The evidence reframes the system as a transparency-first 'external System 2' that computes
39            the allocation and explains it at the moment of decision. We present a prioritised requirement set in
40            which explainability and bounded autonomy are non-functional preconditions, and we report lessons
41
42
43
              for instrument design.
                                                                              ly
              Keywords: requirements engineering; empirical software engineering; decision-support systems;
44            personal finance; explainability; user study; RICE; MoSCoW.
45
46
47            1. Introduction
48
              Decisions about how to allocate disposable income — between repaying debt, building a liquidity
49
50            reserve and funding goals — are made repeatedly by almost every adult, and their cumulative effect
51            over years is large. These decisions are also unusually sensitive to error: a misallocation can leave a
52            household short of liquidity or deepen its debt burden. A growing class of personal-finance applications
53            and fintech services aims to support such decisions, but in practice most of them display retrospective
54
              statistics rather than recommend a next step, and the recommendations they do offer are rarely
55
56            explained.
57
              The difficulty is only partly technical. Two non-technical factors dominate adoption. First, behaviour:
58
59            people frequently intend to decide rationally yet fall back on intuition at the moment of choice. Second,
60            trust: a recommendation that cannot be inspected is easily dismissed, especially when it concerns



                                          https://mc.manuscriptcentral.com/e-informaticasej
                                     e-Informatica Software Engineering Journal                                    Page 2 of 8


1
2
3    money. Requirements for such systems, however, are often derived top-down from domain assumptions
4
     rather than from evidence about how users actually behave and what would make them rely on an
5
6    automated advisor.
7
     This paper addresses that gap. We treat the construction of a personal-finance DSS as a requirements-
8
9    engineering problem and derive its requirements empirically, from a survey of 385 respondents (322
10   valid). The study has two distinctive features for software engineering. First, it pairs stated preferences
11   with a revealed-behaviour probe, exposing an intention–action gap that reframes the system's core
12   purpose. Second, it treats explainability not as a feature but as a non-functional precondition for
13
14
     adoption, and shows quantitatively how user trust depends on it. The target system is kept anonymous
15   throughout; this is a study of method and evidence, not a product description.
16
17
     We investigate four research questions:
18      — RQ1. How do individuals currently manage personal-finance allocation, and which tools and
19
          methods do they use?
20
21      — RQ2. Is there a gap between stated (intended) rational decision-making and revealed behaviour
22
23
24
          in a concrete task?
                              Fo
        — RQ3. Which functional and non-functional requirements for a DSS can be derived from user
          pains and expectations, and how should they be prioritised?
25
26
27
28
                                    rR
        — RQ4. What conditions govern user acceptance of an automated financial advisor, in particular
          regarding explainability and autonomy?
     The remainder of the paper is organised as follows. Section 2 reviews background and related work.
29
30
31
                                            ev
     Section 3 describes the study design. Section 4 reports results by research question. Section 5 derives
     and prioritises the requirements. Section 6 discusses threats to validity, and Section 7 concludes.



                                                  iew
32
33   2. Background and Related Work
34
35   Requirements elicitation through surveys and questionnaires is a standard technique in requirements
36   engineering, valued for reach and comparability, and limited by self-report bias and shallow coverage


                                                             On
37   [7, 8, 16]. Our design follows the empirical-software-engineering tradition of pairing elicitation with
38
     explicit validity analysis [16, 17], and augments self-report with a behavioural probe to mitigate the
39
40   best-known weakness of surveys.
41
42
43
                                                                      ly
     The behavioural framing draws on dual-process theory, which distinguishes fast, intuitive judgement
     from slow, deliberate reasoning [1], and on the intention–behaviour gap documented in social
     psychology, whereby stated intentions translate only weakly into action [2, 3]. In the financial domain,
44
45   this gap motivates interventions that lower the effort of the deliberate path [15]. We use these ideas not
46   to model users but to interpret an observed discrepancy and to motivate a design that performs the
47
     computation on the user's behalf.
48
49   Acceptance and trust are treated through the technology-acceptance literature [6] and research on trust
50
     in automation, which shows that appropriate reliance depends on transparency and on the match
51
52   between perceived and actual system capability [4]. Work on explanation in artificial intelligence
53   stresses that useful explanations are contrastive and audience-appropriate [5]. These results justify our
54   decision to elevate explainability to a non-functional requirement and to bound the system's autonomy.
55   For prioritisation we use two widely adopted schemes: MoSCoW categorisation [10] and RICE scoring,
56
57
     complementing the qualitative ordering with a reach–impact–confidence–effort estimate.
58
59   3. Study Design
60



                                 https://mc.manuscriptcentral.com/e-informaticasej
Page 3 of 8                                  e-Informatica Software Engineering Journal


1
2
3             3.1. Objectives and research questions
4
5             The objective was to obtain an evidence base for the requirements of a personal-finance DSS, covering
6             current practice (RQ1), the stated–revealed behaviour gap (RQ2), derived and prioritised requirements
7             (RQ3), and acceptance conditions (RQ4). The study is observational and cross-sectional.
8
9
              3.2. Instrument
10
11            Data were collected with an online questionnaire of 77 items (62 substantive questions; the remainder
12            matrix sub-items and service fields). The instrument comprised blocks on current financial
13
              management; perceived pains and expectations; a four-criteria importance battery (disposable resource,
14
15            liquidity, debt burden, safety); a behavioural case task contrasting stated and revealed decision-making;
16            attitudes towards an automated advisor and its acceptable degree of autonomy; willingness to pay; and
17            demographics. An attention check ('select seven stars') was embedded to identify inattentive
18            submissions.
19
20
              3.3. Sample and data cleaning
21
22
23
24
                                      Fo
              The questionnaire received 385 responses. After removing 63 submissions that failed the attention
              check, 322 valid responses remained; submissions collected before the attention check was introduced
              and otherwise consistent were retained. Because the instrument was extended during data collection
25
26
27
28
                                             rR
              and the closed questions were mandatory, the valid base size varies by item rather than reflecting
              dropout; the representativeness of the later cohort was checked against the earlier one. Three sub-blocks
              (the criteria battery, the behavioural case and the AI-trust items) rest on approximately 19 responses
29
30
31
              and are reported as preliminary.

              3.4. Analysis
                                                    ev
                                                          iew
32
33            Descriptive statistics summarise practice, pains and expectations. Associations were tested with the chi-
34            square test and reported with Cramér's V as an effect size [11, 14]; no p-value is reported without an
35
              accompanying effect size, and the Holm step-down procedure was applied to control the family-wise
36
              error rate across multiple comparisons [12]. The stated–revealed comparison contrasts the proportion


                                                                     On
37
38            claiming rational calculation with the proportion that actually computed in the case task. The internal
39            structure of the four-criteria battery was examined with Cronbach's alpha [13]. Open responses were
40            coded thematically. Finally, findings were mapped to candidate requirements, which were prioritised
41
42
43
                                                                              ly
              with RICE and MoSCoW [10]. One planned block — a drag-and-drop ranking of criteria — produced
              only five valid permutations out of nineteen because of the form's interaction mechanics and was
              excluded from analysis; we return to this as a methodological lesson in Section 6.
44
45
46
              4. Results
47
48
              4.1. RQ1 — Current practice
49
50            Most respondents rely on passive, retrospective tools: 70.1% use the statistics built into their banking
51            application, 23.1% keep notes on their phone, 20.3% use a spreadsheet and 18.7% use a dedicated
52
              budgeting application; 11.4% use nothing at all and 7% use AI assistants (Figure 1). The dominant
53
54            theme in open responses about abandoning previous tools was that they 'only show statistics' and
55            provide no next step. Current practice is therefore oriented towards looking back at spending rather than
56            deciding what to do with money that remains.
57
58
59
60



                                         https://mc.manuscriptcentral.com/e-informaticasej
                                     e-Informatica Software Engineering Journal                                   Page 4 of 8


1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20                        Figure 1. Tools used to manage personal finances (multiple choice).
21
22
23
24
                              Fo
     4.2. RQ2 — The intention–action gap
     When asked how they decide where to direct money, 46% described a rational, calculated approach. In


                                     rR
25   a concrete case task — answered by a smaller behavioural sub-sample — only 10% actually performed
26   a calculation, while 63% reported deciding on emotion, a gap of 36 percentage points between stated
27   and revealed behaviour (Figure 2). The pattern is consistent with dual-process accounts [1]: deliberate
28
29
30
31
                                             ev
     reasoning is claimed in the abstract but is displaced by fast, intuitive judgement at the moment of
     decision. This is the study's central finding, and although the revealed-behaviour probe is indicative
     rather than definitive, it is corroborated by the large-sample demand for transparency (Section 4.4) and



                                                    iew
32   reframes the system's purpose: the value of a DSS here is less to inform a calculation the user would
33   otherwise perform than to perform the calculation on the user's behalf and present the result at the
34
     moment of hesitation — an 'external System 2'.
35
36



                                                                On
37
38
39
40
41
42
43
                                                                        ly
44
45
46
47
48
49
50
51
52
53
54        Figure 2. The intention–action gap: a rational approach is claimed far more often than it is enacted.
55
56   4.3. RQ3 — Pains and expectations
57
     The single strongest expectation was visibility of disposable cash flow: how much money remains after
58
59   all obligatory payments was the top must-have (61%) and ranked highest under RICE scoring. Beyond
60   it, 62% wanted to compare alternatives, 48% wanted to see the consequences of a choice in advance,



                                 https://mc.manuscriptcentral.com/e-informaticasej
Page 5 of 8                                   e-Informatica Software Engineering Journal


1
2
3             and 38% wanted a predictive warning of an impending shortfall. The most cited pains were an
4
              overloaded interface and not knowing where to start, a predictive 'funds will be insufficient' concern
5
6             (32%), and the absence of any explanation of the advice given (22%). On the preferred form of advice,
7             59% favoured a visualisation or comparison, 45% wanted concrete numbers, and 19% wanted a single
8             short action — a split that argues for layering rather than choosing one format.
9
10            4.4. RQ4 — Acceptance conditions
11
12            Demand for an automated advisor was high (84%) but explicitly conditional: 67% said they would trust
13            it only if it explained its reasoning with numbers, and 61% only if the algorithm were transparent.
14            Acceptance also depended sharply on autonomy. Trust was high for an advisor that computes or
15
              explains (74–79%) but collapsed to 16% for one that decides and moves money by itself (Figure 3),
16
17            implying a recommend-and-confirm interaction rather than an autopilot.
18
19
20
21
22
23
24
                                       Fo
25
26
27
28
                                              rR
29
30
31
                                                     ev
                                                            iew
32
33
34
35
36                Figure 3. Acceptance is conditional on transparency and collapses when the system acts autonomously.


                                                                       On
37
38            Two debt-related results are notable. The presence of debt was strongly associated with experiencing
39            the repay-versus-save dilemma (Cramér's V = 0.62), and 40% of respondents with debt reported facing
40            it; debtors were also significantly more anxious about missing a payment. Finally, the four-criteria
41
42
43
                                                                               ly
              importance battery returned a low Cronbach's alpha (0.632). Rather than indicating an unreliable scale,
              this is consistent with the criteria measuring largely independent constructs — empirical support for
44            treating them as separate, independently weighted dimensions rather than collapsing them into one
45            score. Willingness to pay was modest: 54% would pay no more than 200 RUB per month, a constraint
46            with direct consequences for the business model.
47
48
49            5. From Findings to Requirements
50
51            Three design principles follow directly from the evidence and govern the requirements below. First,
52            transparency is a precondition, not an embellishment: demand for an advisor is high but conditional on
53            numeric, inspectable explanations (Section 4.4). Second, the system should act as an external System 2
54            — it should perform the computation and present the result at the moment of decision, because users
55
              intend to calculate but do not (Section 4.2). Third, it should advise and wait for confirmation rather than
56
57            act autonomously, because trust in autonomous money movement is very low (Section 4.4).
58
              Table 1 lists the functional (FR) and non-functional (NFR) requirements derived from the findings, each
59
60            traced to its supporting evidence and prioritised with MoSCoW. RICE scoring was applied in parallel;



                                          https://mc.manuscriptcentral.com/e-informaticasej
                                          e-Informatica Software Engineering Journal                                 Page 6 of 8


1
2
3    the requirement to surface disposable cash flow scored highest (RICE 1.83) and, together with the
4
     explainability requirement, anchors the minimum viable product. The catalogue is deliberately
5
6    transparency-first: the explanation of a recommendation is itself a Must-have requirement, not an
7    optional addition to a recommender.
8
9            Table 1. Requirements derived from the study, with supporting evidence and MoSCoW priority.
10    Requirement                              Type      Key empirical evidence                        Priority
11
12    Compute and surface disposable           FR        Top expectation (61% must-have); highest-     Must
13    cash flow (income − expenses −                     ranked item under RICE (1.83)
      obligatory payments) as the
14
      primary screen
15
16    Generate an allocation                   FR        Core unmet need: 'does not tell me where to   Must
17    recommendation across debt                         put the money' (open responses)
18    repayment, reserve and goals
19    Explain each recommendation: the         FR/NFR    'Does not explain the logic of advice' —      Must
20    underlying calculation, the                        pain for 22%; 67% trust only with a
21    compared alternatives, and why                     numeric explanation; 61% require a
22
23
24
      others were rejected
                                Fo
      Let the user compare the top             FR
                                                         transparent algorithm
                                                         62% want to compare alternatives              Should


                                          rR
25    alternatives, not only the best one
26    Provide 'what-if' scenarios with         FR        48% want to see consequences of a choice      Should
27    instant recomputation of indicators                in advance
28
29
30
31
      Raise a predictive 'funds will be
      insufficient' alert before a due
      payment
                                                ev
                                               FR        Pain for 32%; expectation for 38%             Should




                                                        iew
32    Give a direct, explained 'repay-vs-      FR        Strongest association in the data (debt ↔     Should
33    save' verdict                                      dilemma, V = 0.62); 40% of debtors faced it
34    Trigger a recommendation at the          FR        Intention–action gap: computation is needed   Should
35    moment income arrives                              at the moment of hesitation
36



                                                                  On
37    Segmented onboarding with                FR        Format preferences split: 59% visual, 45%     Should
38    layered advice (verdict → numbers                  numeric, 19% short action
39    → visual)
40    Risk-based payment reminders             FR        Debtors fear missed payments (H4); but        Could
41
42
43
      (only on real risk)
      Minimal cognitive load: one key
      indicator and one action per screen
                                               NFR
                                                                           ly
                                                         notifications are the 3rd irritant (25%)
                                                         'Overloaded interface' and 'do not know
                                                         where to start' are top irritants
                                                                                                       Must
44
45    Human-in-the-loop: never move            NFR       Trust collapses from explain/compute (74–     Must
46    money autonomously                                 79%) to autonomous transfer (16%)
47
      Reproducibility and determinism          NFR       Transparency precondition; auditability of    Must
48
      of every recommendation                            advice
49
50    Affordability / freemium model           NFR       54% willing to pay ≤ 200 RUB per month        Could
51    Autonomous financial actions             —         Lowest trust (16%); out of scope by design    Won't (now)
52
53   The prioritisation makes the dependency structure explicit. The Must-have set establishes the trust
54   foundation — a single, clearly explained disposable-cash-flow figure, an explained recommendation,
55   low cognitive load and a human-in-the-loop guarantee — and consists largely of exposing computation
56   the engine can already perform rather than of new algorithms. The Should-have set addresses the
57
     strongest specific pains: the repay-versus-save verdict (the largest effect in the data), the predictive
58
     shortfall alert, what-if scenarios and the moment-of-decision trigger. Could-have and Won't-have items
59
60
     reflect either weak demand under a tight willingness-to-pay ceiling or the explicit autonomy boundary.



                                   https://mc.manuscriptcentral.com/e-informaticasej
Page 7 of 8                                   e-Informatica Software Engineering Journal


1
2
3
              6. Validity and Scope
4
5             The design controls the principal validity concerns. The central finding — the intention–action gap —
6             is established not by self-report alone but by contrasting stated approach with revealed behaviour in a
7
8
              concrete task, with inattentive respondents removed by an attention check; any residual desirability bias
9             would inflate the stated-rational figure and thus widen rather than create the gap. The behavioural probe
10            is answered by a smaller sub-sample and is therefore indicative, but it converges with the large-sample
11            demand for transparency. Associations are reported with effect sizes and the family-wise error rate is
12            controlled with the Holm procedure, so the reported relationships are conservative.
13
14            The four-criteria battery returned a low Cronbach's alpha (0.632), which we read as evidence that the
15            criteria capture largely independent constructs rather than as low reliability; confirming this with a
16
17            confirmatory factor analysis on a larger sample is a natural next step. The study draws on a longitudinal
18            real-world evidence base and on a focused first segment of respondents — younger, capital-city users
19            with modest income and small debts — for whom the design is directly applicable; extending the
20            evidence to debt-bearing households is the main aim of the planned second wave. A drag-and-drop
21
22
23
24
                                       Fo
              ranking block was excluded after its interaction mechanics produced inconsistent permutations, which
              motivates the instrument-design recommendation to favour pairwise comparison or fixed-budget point
              allocation.
25
26
27
28
              7. Conclusion                  rR
              We derived and prioritised requirements for an explainable personal-finance decision-support system
29
30
31
                                                     ev
              from an empirical study of 385 respondents (322 valid), combining descriptive and inferential statistics
              with a stated-versus-revealed behavioural probe. The central result is an intention–action gap — 46%



                                                           iew
32            claim to calculate, 10% actually do — which reframes the system as an external System 2 that performs
33            the computation and presents the result at the moment of decision. Acceptance of such a system is high
34            but conditional on transparency and on bounded autonomy, which we therefore encode as non-
35            functional preconditions. The resulting transparency-first requirement set, prioritised with RICE and
36
              MoSCoW, places an explained disposable-cash-flow recommendation at the centre of the minimum


                                                                      On
37
38            viable product.
39
40            For software engineering practice, the study illustrates the value of pairing requirements elicitation with
              a behavioural probe and of treating explainability as a first-class requirement in decision-support
41
42
43
                                                                               ly
              systems. Future work includes a second survey wave that broadens the sample to debt-bearing
              households, enlarges the under-powered sub-blocks, replaces the invalidated ranking instrument, and
44
              confirms the independence of the four decision criteria through confirmatory factor analysis.
45
46
47            Acknowledgements
48
49            The author thanks I. S. Bondarenko for scientific supervision.
50
51            Declarations
52
53            Author contributions (CRediT): V. M. Evdokimov — Conceptualisation, Methodology, Software,
54            Formal analysis, Investigation, Data curation, Writing – original draft, Writing – review and editing,
55            Visualisation.
56
57            Declaration of generative AI: During the preparation of this work the author used a generative AI
58            assistant to support data analysis, drafting and language editing. The author reviewed and edited the
59
              content and takes full responsibility for it.
60



                                          https://mc.manuscriptcentral.com/e-informaticasej
                                         e-Informatica Software Engineering Journal                                        Page 8 of 8


1
2
3    Funding: none. Conflicts of interest: the author declares no conflict of interest. Data availability: the
4
     anonymised survey data are available from the author on reasonable request.
5
6
7    References
8
9     1. Kahneman D. Thinking, Fast and Slow. New York: Farrar, Straus and Giroux, 2011.
10    2. Sheeran P. Intention–behavior relations: A conceptual and empirical review. European Review of Social
11        Psychology, 2002, vol. 12, no. 1, pp. 1–36.
12
      3. Sheeran P., Webb T. L. The intention–behavior gap. Social and Personality Psychology Compass, 2016,
13        vol. 10, no. 9, pp. 503–518.
14
15    4. Lee J. D., See K. A. Trust in automation: Designing for appropriate reliance. Human Factors, 2004, vol. 46,
16        no. 1, pp. 50–80.
17    5. Miller T. Explanation in artificial intelligence: Insights from the social sciences. Artificial Intelligence,
18        2019, vol. 267, pp. 1–38.
19    6. Davis F. D. Perceived usefulness, perceived ease of use, and user acceptance of information technology.
20        MIS Quarterly, 1989, vol. 13, no. 3, pp. 319–340.
21
22
23
24
                               Fo
      7. Sommerville I. Software Engineering. 10th ed. Harlow: Pearson, 2015.
      8. Pohl K. Requirements Engineering: Fundamentals, Principles, and Techniques. Berlin: Springer, 2010.
      9. Glinz M. On non-functional requirements. Proc. 15th IEEE International Requirements Engineering
25
26
27
28
                                         rR
          Conference (RE'07), 2007, pp. 21–26.
      10. Clegg D., Barker R. Case Method Fast-Track: A RAD Approach. Wokingham: Addison-Wesley, 1994.
      11. Cohen J. Statistical Power Analysis for the Behavioral Sciences. 2nd ed. Hillsdale: Lawrence Erlbaum,
29
30
31
          1988.
                                                ev
      12. Holm S. A simple sequentially rejective multiple test procedure. Scandinavian Journal of Statistics, 1979,



                                                      iew
          vol. 6, no. 2, pp. 65–70.
32
33    13. Cronbach L. J. Coefficient alpha and the internal structure of tests. Psychometrika, 1951, vol. 16, no. 3, pp.
34        297–334.
35    14. Cramér H. Mathematical Methods of Statistics. Princeton: Princeton University Press, 1946.
36
      15. Thaler R. H., Benartzi S. Save More Tomorrow: Using behavioral economics to increase employee saving.


                                                                  On
37
          Journal of Political Economy, 2004, vol. 112, no. S1, pp. S164–S187.
38
39    16. Hofmann H. F., Lehner F. Requirements engineering as a success factor in software projects. IEEE Software,
40        2001, vol. 18, no. 4, pp. 58–66.
41
42
43
                                                                           ly
      17. Wohlin C., Runeson P., Höst M., Ohlsson M. C., Regnell B., Wesslén A. Experimentation in Software
          Engineering. Berlin: Springer, 2012.

44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60



                                      https://mc.manuscriptcentral.com/e-informaticasej
