# Рукопись EN (подача)

> Текст извлечён из `Evdokimov_manuscript_EN.docx` при похудении архива v5.18.0.
> Формулы/рисунки/вёрстка не переносились — здесь суть для контекста.
> Оригинальный docx: у владельца локально + в assets GitHub-релизов приватного репо (v5.16.0+).

---

An Explainable Hybrid Decision Support System for Personal Finance: Multi-Criteria Ranking of Fund-Allocation Alternatives under Liquidity and Debt Constraints

Vasilii M. Evdokimov

National University of Science and Technology MISIS, Moscow, Russian Federation

Author: m2201058@edu.misis.ru   |   ORCID: 0009-0004-8821-8414

Abstract

Decision-making in personal finance increasingly takes place in a data-rich digital environment, yet the choice of how to allocate free funds is still made intuitively and without any formal comparison of alternatives. This study addresses the absence of a transparent, reproducible instrument that allows a non-expert user to select among competing financial actions under liquidity constraints, cash-flow uncertainty, and conflicting long-term goals. A survey of 385 respondents conducted for this work showed that 76% allocate their free funds intuitively, without calculation, while 83% would be willing to use a decision support system (DSS) provided that its logic is transparent. We propose an explainable hybrid algorithmic core that combines rule-based feasibility constraints, cash-flow forecasting by simple exponential smoothing with Monte-Carlo interval estimation, and multi-criteria ranking of allocation alternatives by the simple additive weighting (SAW) method. Alternatives are evaluated through an integral utility function defined over a vector of financial-state metrics — available resource, liquidity, debt load, and goal-funding adequacy {Rt, Lt, Dt, St}. The model is implemented as a web application on a Python 3.12 / FastAPI / SQLAlchemy / SQLite stack. Functional testing on five representative user scenarios and four boundary conditions confirmed correct behaviour in all cases, and the time required to produce a justified recommendation was reduced from 30–60 minutes of manual analysis to under five seconds. The approach is applicable to FinTech services, personal-finance assistants, and financial-literacy tools.

Keywords: decision support system; personal finance; multi-criteria decision making; simple additive weighting; cash-flow forecasting; explainable recommendations; FinTech.

Introduction

Personal finance is increasingly managed on the basis of data and digital services, and the quality of everyday financial decisions directly affects the stability of households, the level of saving activity, and people’s ability to reach long-term goals. The continued expansion of financial products and the channels through which they are consumed increases the number of alternatives that a user must weigh, comparing interest rates, fees, tax consequences, terms, and risks. At the same time, the underlying information about incomes, expenses, and obligations remains fragmented for most users, and analysis is performed episodically and with approximate estimates. This produces a persistent gap between the availability of digital tools and the actual manageability of a personal budget, debt load, and savings [1, 2].

Even when digital applications are used, users frequently limit themselves to recording expenses or reviewing aggregated dashboards. The absence of a formalized action-selection procedure means that decisions are made intuitively, without accounting for liquidity constraints and without evaluating the trade-offs between current consumption, a financial reserve, and long-term goals. As a result, the probability of financial errors rises; the most common are an unbalanced expenditure structure, an insufficient reserve, an irrational debt-repayment order, and the selection of saving instruments without reference to an acceptable level of risk [3]. Although digital services and fintech products for personal finance are developing rapidly [4–8], their algorithmic core rarely provides a transparent, formal procedure for choosing among alternative allocations.

To quantify this demand, an anonymous online survey of 385 respondents was conducted within the framework of this study. It showed that 76% of participants allocate their free funds intuitively, without any calculation, while 83% expressed a willingness to use a decision support system (DSS) on the condition that its logic is transparent. These findings substantiate the practical need for an instrument that is not a “black box”: in personal finance, users tend to reject recommendations that appear opaque, even when those recommendations are computationally justified.

The aim of this work is to improve the validity of allocating a user’s free funds by automating the multi-criteria ranking of alternatives that maximizes an integral utility indicator U(a) over a vector of financial-state metrics {Rt, Lt, Dt, St} subject to model constraints. The object of the study is the set of decision-making processes in personal finance; the subject is the automation of a DSS intended to process a user’s financial data and to generate recommendations on formalized criteria.

The contributions of the paper are the following:

a formalized model of a user’s financial state expressed through a compact set of interpretable metrics — available resource, liquidity, debt load, and goal-funding adequacy;

an explainable hybrid algorithmic core that integrates rule-based feasibility constraints, cash-flow forecasting (simple exponential smoothing with Monte-Carlo interval estimation), and multi-criteria ranking by the simple additive weighting method, while preserving the interpretability of every recommendation;

a working software prototype implemented on a modern Python web stack (FastAPI, SQLAlchemy, Pydantic, SQLite);

an experimental validation of the prototype on five representative user scenarios and four boundary conditions, together with a measurement of the reduction in recommendation-formation time.

The remainder of the paper is organized as follows. Section 1 reviews the classes of algorithmic approaches used in personal-finance DSS and motivates the chosen method. Section 2 formalizes the input data, the financial-state metrics, the forecasting and ranking models, the resulting algorithm, and the implementation. Section 3 reports the experimental results. Section 4 discusses the implications, limitations, and directions for future work.

1. Related Work and Choice of Approach

Digital solutions for personal-finance management develop at the intersection of FinTech practice and decision-support methods. At the application level, systems oriented toward the collection and categorization of transactions, the visualization of expenditure structure, goal setting, and reminders dominate. At the level of the algorithmic core, however, the approaches differ markedly: some solutions are limited to rules and heuristics, some use forecasting and recommendation ranking, and the most advanced rely on optimization models and elements of intelligent data analysis [9].

Six broad classes of approaches can be distinguished, each with characteristic strengths and limitations (Table 1). Rule-based systems offer transparent logic and low computational cost but adapt poorly to changing behaviour and struggle with multi-criteria problems. Scoring models and indices compress a complex situation into a single number, which is convenient for monitoring but methodologically contestable. Cash-flow forecasting based on time series or machine-learning models improves the substantiation of decisions and supports the estimation of liquidity-shortfall probability, but it requires history and degrades under structural shifts. Multi-criteria decision-making (MCDM) [10, 11] formalizes the “return–risk–liquidity” trade-off but is sensitive to the specification of preferences and scales. Optimization models provide a rigorous, reproducible choice subject to constraints, yet their quality depends on the realism of the assumptions and may be less explainable in a mass-user context. Hybrid approaches combine these components and offer the most favourable balance of recommendation quality, robustness, and explainability, at the cost of higher architectural and testing complexity.

Table 1. Classes of algorithmic approaches to personal-finance DSS.

Approach class

Strengths

Limitations and risks

Rules and heuristics

Transparent logic; low complexity; easy to explain

Weak adaptivity; poor with many criteria; quality depends on rule completeness

Scoring models and indices

Compact result; convenient for tracking dynamics; suitable for ranking

Reduces a complex situation to one number; sensitive to data quality; weights are contestable

Cash-flow forecasting

Better substantiation; captures seasonality; allows uncertainty estimation

Overfitting risk; needs history; degrades under structural shifts

Multi-criteria ranking (MCDM)

Formalizes trade-offs; tunable preferences

Hard to set preferences; needs correct scales; risk of unstable rankings

Optimization models

Rigorous, reproducible; explicit constraints

Computational cost; dependence on assumptions and input quality

Hybrid (rules + forecast + ranking)

Balance of explainability and quality; robust to partial data

Higher architectural complexity; more demanding testing; module coordination

Among MCDM methods, the analytic hierarchy process (AHP), the technique for order preference by similarity to ideal solution (TOPSIS), and simple additive weighting (SAW) are the most developed [12, 13]. SAW is applicable when the criteria are independent and additive, and it provides the most favourable balance of simplicity, transparency, and computational efficiency relative to AHP and TOPSIS. Because explainability is decisive in the personal-finance domain — users rarely accept opaque advice — SAW is adopted here as the ranking method, with min-max normalization to reconcile the differing dimensions of the criteria; the additive convolution itself rests on multi-attribute utility theory [14, 15].

The diagnostic use of liquidity and debt-burden ratios to characterize a household’s financial position has a long methodological history, originating in the work of Lytton, Garman, and Porter [16] and developed in the consensus benchmarks of the Delphi study by Greninger and colleagues [17]. In the present work, these basic ratios are adapted to the decision-support task rather than used purely for ex-post diagnostics. The applied literature on personal-finance tools typically describes functionality and user scenarios in detail, while the selection procedure and the formal justification of recommendations remain under-developed at the methodological level. This gap — a formalized, explainable utility-based selection over interpretable financial metrics — is what the proposed model targets.

2. Materials and Methods

2.1 Problem statement and input data

The input of the system is a set of parameters describing the user’s current financial state, obligations, goals, and constraints. The data are divided into cash flows, obligations, user parameters, and goals, and are reduced to a common time step (one month) and normalized in structure, following established practice in system modelling and information-system design [21, 22]. Let It and Et denote the set of incomes and the set of expenses in period t, respectively. The net cash flow is then defined as the difference between total income and total expenditure over the period:

			CFt = ∑ ik − ∑ ej	(1)

The set of obligations O = {o1, …, op} is characterized for each obligation by a triple (Al, rl, Tl) — amount, interest rate, and term — from which the scheduled payment Pl,t in period t is obtained. The user parameter vector U = (Lmin, R, H) collects the minimum admissible liquidity, the acceptable risk level, and the planning horizon. Each financial goal gs is described by a required amount Ss, a target term Ts, and a priority ws. The complete input vector is X = {It, Et, O, U, G, Bt}, where Bt is the current cash balance.

2.2 Financial-state metrics

The current state is described by three interpretable indicators. The available resource is the amount the user can direct to additional goals after mandatory payments:

			Rt = Bt + CFt − ∑ Pl,t	(2)

The liquidity ratio expresses how many periods of current expenditure the available balance can cover:

			Lt = Bt / ∑ ej	(3)

The debt-load ratio measures the share of mandatory payments in income; the higher its value, the stronger the user’s dependence on obligations:

			Dt = ∑ Pl,t / ∑ ik	(4)

The goal-funding adequacy relates the available resource to the required saving rate aggregated over all active goals:

			St = Rt / ∑ (Ss / Ts)	(5)

These metrics are interpreted jointly rather than in isolation. For example, a high available resource combined with low liquidity may signal risk caused by uneven cash flows, while a low debt load does not guarantee stability in the absence of an adequate reserve.

2.3 Cash-flow forecasting

To assess the robustness of the future state, the income and expense components are forecast by simple exponential smoothing (SES) [18, 19], which assigns geometrically decaying weights to past observations. For a generic series y, the one-step forecast is

			ŷt+1 = α yt + (1 − α) ŷt,   0 < α < 1	(6)

where the smoothing coefficient α controls the trade-off between responsiveness and stability. SES is applied independently to the income and expense components, and the h-step forecast of the available resource Rt+h follows by substituting the smoothed components into (2). To quantify uncertainty, an empirical predictive interval for Rt+h is obtained by Monte-Carlo resampling of the forecast residuals [20], which yields a distribution of plausible future resources rather than a single point estimate and supports the assessment of liquidity-shortfall risk.

2.4 Alternative generation, feasibility, and ranking

A set of candidate decisions A = {a1, …, an} is generated by discretizing the available resource into fixed shares and enumerating admissible allocations of those shares between three directions — repayment of obligations, formation of a reserve fund, and progress toward goals — subject to the budget constraint that the total allocation does not exceed Rt. For each allocation, the metrics are recomputed, so that every alternative is described by the vector ai = (Ri, Li, Di, Si).

Before ranking, a feasibility filter retains only the alternatives that satisfy the rule-based constraints:

			Ri ≥ Lmin,    Li ≥ Lcrit,    Di ≤ Dmax	(7)

which yields the feasible set A′ ⊆ A. If A′ is empty, the system instead issues corrective recommendations aimed at stabilizing the financial state. Because the metrics differ in dimension, each criterion is brought to the unit interval by min-max normalization:

			xinorm = (xi − xmin) / (xmax − xmin)	(8)

Denote by ri, li, di, si the normalized values of Ri, Li, Di, Si. The integral utility of an alternative is the additive convolution of the criteria (the SAW method), with the debt-load term inverted because its reduction is preferable:

			U(ai) = w1 ri + w2 li + w3 (1 − di) + w4 si,   ∑ wk = 1	(9)

where the weights w1…w4 encode the user’s financial strategy and can be adjusted; when inputs or weights change, the system recomputes the utilities and updates the ranking automatically. The recommended decision is the feasible alternative with the highest utility:

			a* = arg max over ai ∈ A′ of U(ai)	(10)

2.5 Quality and effectiveness indicators

Three indicators characterize the system, consistent with standard software-quality models [24]. Forecast accuracy is the mean absolute percentage error (MAPE) between forecast and actual values of the cash-flow series over T periods:

			E = (1 / T) ∑ |yt − ŷt| / |yt|	(11)

The robustness of decisions is captured by an admissibility coefficient — the share of generated alternatives that satisfy the constraints:

			Ks = Nvalid / Ntotal	(12)

Finally, the practical benefit of a chosen decision is summarized by an effectiveness indicator that aggregates the changes in the available resource, liquidity, and debt load:

			Eff = α ΔR + β ΔL − γ ΔD	(13)

with weights α, β, γ. The three indicators are mutually reinforcing: higher forecast accuracy raises decision robustness, and robust decisions in turn increase effectiveness.

2.6 Algorithm

The functioning of the DSS is cyclic and transforms the input vector X into a justified decision through the following stages: (i) preparation and validation of the input data; (ii) computation of the current-state metrics CFt, Rt, Lt, Dt; (iii) forecasting of future cash flows over the horizon; (iv) generation of the alternative set; (v) feasibility filtering; (vi) normalization and utility-based ranking; (vii) formation of the recommendation together with a textual explanation that reports the driving metric values; and (viii) parameter updating based on user feedback. The selection logic is priority-ordered: the debt load is checked first, then liquidity, then the availability of free resource against active goals, so that critical constraints are always resolved before discretionary allocation. The corresponding control flow is shown in Figure 2 using standard flowchart notation [26].

Figure 1. Functional structure (function tree) of the decision support system.

Figure 2. Process of recommendation formation (BPMN).

2.7 Implementation

The prototype is implemented as a web application in Python 3.12. FastAPI provides the REST interface between the client and the computational core, served by the Uvicorn ASGI server; SQLAlchemy supplies object-relational mapping that abstracts the underlying database (SQLite in the prototype, with PostgreSQL as an alternative); Pydantic and pydantic-settings handle input validation and configuration; and Jinja2 renders the HTML interface. The code follows a layered design — a data-storage layer for transactions, obligations, and goals; a business-logic layer implementing the metric computation, forecasting, and ranking; the REST API; and the user interface for data entry, indicator visualization, and recommendation delivery. The interface includes an operations journal, panels for obligations and goals, a key-indicators panel, a recommendation block with explanations, and a scenario mode in which the user can vary incomes and expenses to evaluate alternative developments and then restore the actual values, separating real-situation analysis from what-if modelling. The system was developed in line with standard software life-cycle and automated-system creation guidelines [23, 25].

3. Results

Testing verified the correctness of the computations, the robustness of the system to varied inputs, and the consistency of the generated recommendations with the decision logic. Five scenarios were constructed to reflect typical financial situations — a balanced state, a high debt load, insufficient liquidity, a free resource without critical constraints, and the presence of active saving goals. For each scenario the metrics Rt, Lt, Dt were computed and the generated recommendation was compared with the expected one (Table 2). The actual recommendation matched the expected recommendation in all five cases.

Table 2. Functional testing of the system across five representative scenarios (amounts in RUB).

#

Income

Expenses

Obligations

Rt

Lt

Dt

Recommendation (expected = actual)

1

150 000

90 000

20 000

40 000

0.36

0.13

Reduce debt load

2

120 000

100 000

10 000

10 000

0.09

0.08

Increase liquidity

3

200 000

100 000

20 000

80 000

0.67

0.10

Allocate free funds

4

180 000

120 000

15 000

45 000

0.33

0.08

Increase liquidity

5

170 000

80 000

10 000

80 000

0.89

0.06

Direct funds to goals

A separate set of boundary and malformed inputs was used to confirm robustness, in particular the absence of division errors when income or obligations are zero, and the generation of a warning recommendation when the available resource becomes negative (Table 3). All boundary cases passed.

Table 3. Boundary-condition checks.

#

Condition

Expected result

Outcome

1

No income

Dt = 0; no division-by-zero error

Passed

2

Zero expenses

Correct computation of Rt

Passed

3

No obligations

Dt = 0

Passed

4

Negative Rt

Warning recommendation generated

Passed

A worked example illustrates the computation on a representative demo profile with income 167 000, expenses 36 500, and obligations 23 500 RUB. The net cash flow is CFt = 167 000 − 36 500 = 130 500 RUB; the available resource is Rt = 130 500 − 23 500 = 107 000 RUB; the liquidity ratio is Lt = 107 000 / 60 000 ≈ 1.78; and the debt load is Dt = 23 500 / 167 000 ≈ 0.14. A positive resource, a liquidity ratio above one, and a debt load well below the 0.4 threshold are interpreted as a stable state, and the system accordingly recommends allocating the free funds or directing them toward goals, with an explanation that cites the underlying values.

Finally, the practical effect on the decision process was assessed by comparing the end-to-end time required to produce a justified recommendation. Manual analysis of the same situation — consolidating data, computing the ratios, and weighing alternatives — takes an estimated 30–60 minutes, whereas the prototype produces a ranked, explained recommendation in under five seconds, while removing the inconsistency inherent in ad-hoc manual assessment.

4. Discussion

The results indicate that a compact set of interpretable metrics, combined with rule-based constraints and SAW ranking, is sufficient to reproduce expert-consistent recommendations across a range of typical situations while keeping every output explainable. The priority-ordered selection logic guarantees that liquidity and debt constraints are never violated for the sake of a higher utility score, which is essential for user trust in the personal-finance domain. The explicit utility function also makes the system tunable: by adjusting the criterion weights, the same engine expresses different financial strategies without any change to the algorithm.

Several limitations should be acknowledged. The present version uses a simplified representation of the financial state: accumulated funds and the evolution of cash flows over time are only partially accounted for, and the set of stability indicators is comparatively narrow. The prototype does not yet integrate with external financial services such as banking platforms or electronic-payment systems, so the correctness of the computations depends on the completeness and accuracy of user-entered data, and recommendation quality may decline under substantial structural changes in incomes and expenses. The criterion weights are currently set heuristically rather than elicited through a formal preference-acquisition procedure, and the validation, while confirming functional correctness, was conducted on representative scenarios rather than on a longitudinal real-user dataset.

These limitations define the directions for further development. The mathematical model can be extended to account for the structure of savings, balance dynamics, and longer-term parameters. The point-forecast SES module can be complemented or replaced by machine-learning forecasters that capture seasonality and non-linear patterns, in line with recent work on personal-finance forecasting [7] and the broader digital transformation of finance [27]. Integration with banking APIs would automate data acquisition and improve reliability, and a sensitivity analysis of the ranking with respect to the weights, together with a controlled user study, would strengthen the evidence on real-world usefulness and on the elicitation of preferences.

Conclusion

This paper presented an explainable hybrid decision support system for the allocation of personal free funds. Motivated by a survey of 385 respondents that revealed both the prevalence of intuitive allocation and a strong demand for transparent automation, the work formalized a user’s financial state through four interpretable metrics — available resource, liquidity, debt load, and goal-funding adequacy — and combined rule-based feasibility constraints, cash-flow forecasting by simple exponential smoothing with Monte-Carlo interval estimation, and multi-criteria ranking by the simple additive weighting method into a single integral utility function. A working prototype on a Python / FastAPI / SQLAlchemy / SQLite stack was implemented and validated: across five representative scenarios and four boundary conditions the generated recommendations were correct in every case, and the time to produce a justified, explained recommendation was reduced from 30–60 minutes of manual analysis to under five seconds. The approach is directly applicable to FinTech services, personal-finance assistants, and financial-literacy tools, and it provides a foundation for further development toward richer financial models, machine-learning forecasting, and automated data integration.

Declarations

Author contributions. The manuscript was prepared by the sole author, who carried out the conceptualization, methodology, software implementation, validation, and writing.

Acknowledgements. The author thanks I.S. Bondarenko (NUST MISIS) for scientific supervision of the thesis on which this paper is based.

Funding. This research received no external funding.

Conflicts of interest. The authors declare no conflict of interest.

Data availability. The anonymized survey dataset (385 respondents) and the prototype source code are available from the corresponding author on reasonable request.

Ethics. The survey was anonymous and voluntary; participation implied informed consent, and no personally identifying information was collected.

References

Blokhina I.M., Aivazyan N.S., Kazakova L.V., Fedosova Yu.V. (2025) Features of personal finance management in modern conditions. Estestvenno-Gumanitarnye Issledovaniya, no. 3 (59), pp. 624–629 (in Russian).

Malenkina T.M., Ponyaeva E.V. (2024) Digitalization of personal finance management. Mnogourovnevoe Obshchestvennoe Vosproizvodstvo: Voprosy Teorii i Praktiki, no. 1 (42), pp. 77–81 (in Russian).

Lusardi A., Mitchell O.S. (2014) The economic importance of financial literacy: Theory and evidence. Journal of Economic Literature, vol. 52, no. 1, pp. 5–44.

Kachanova L.S., Plaksa M.A. (2025) Customization of information products for managing citizens’ personal finances as a means of ensuring the economic security of households. Ekonomika i Predprinimatelstvo, no. 6 (179), pp. 1417–1425 (in Russian).

Kutenkov D.A., Gorobinskiy L.V. (2025) Architecture and implementation of personal finance management systems. Ekonomika Stroitelstva, no. 4, pp. 626–629 (in Russian).

Okhotskaya M.A. (2025) Improvement of a fintech product in the field of personal finance management. Vestnik REU im. G.V. Plekhanova. Vstuplenie. Put v Nauku, vol. 15, no. 2 (50), pp. 69–85 (in Russian).

Ivanova M.A. (2025) A mobile application for accounting and forecasting personal finances using the CatBoost model. Nauchno-Tekhnicheskiy Vestnik Povolzhya, no. 12, pp. 147–151 (in Russian).

Materova E.S., Khamityanova R.Ya., Gasanov E.A.O., Romanovskiy D.V. (2025) On the category of ‘personal finance’ in the investment process. Voprosy Ekonomiki i Prava, no. 204, pp. 69–75 (in Russian).

Power D.J. (2002) Decision support systems: Concepts and resources for managers. Westport: Quorum Books.

Zavadskas E.K., Turskis Z. (2011) Multiple criteria decision making (MCDM) methods in economics: An overview. Technological and Economic Development of Economy, vol. 17, no. 2, pp. 397–427.

Triantaphyllou E. (2000) Multi-criteria decision making methods: A comparative study. Dordrecht: Kluwer Academic Publishers.

Hwang C.L., Yoon K. (1981) Multiple attribute decision making: Methods and applications. Berlin: Springer-Verlag.

Saaty T.L. (1980) The analytic hierarchy process. New York: McGraw-Hill.

Fishburn P.C. (1970) Utility theory for decision making. New York: John Wiley & Sons.

Keeney R.L., Raiffa H. (1976) Decisions with multiple objectives: Preferences and value tradeoffs. New York: John Wiley & Sons.

Lytton R.H., Garman E.T., Porter N.M. (1991) How to use financial ratios when advising clients. Financial Counseling and Planning, vol. 2, pp. 3–23.

Greninger S.A., Hampton V.L., Kitt K.A., Achacoso J.A. (1996) Ratios and benchmarks for measuring the financial well-being of families and individuals. Financial Services Review, vol. 5, no. 1, pp. 57–70.

Hyndman R.J., Athanasopoulos G. (2021) Forecasting: Principles and practice. 3rd ed. Melbourne: OTexts.

Gardner E.S. (2006) Exponential smoothing: The state of the art — Part II. International Journal of Forecasting, vol. 22, no. 4, pp. 637–666.

Metropolis N., Ulam S. (1949) The Monte Carlo method. Journal of the American Statistical Association, vol. 44, no. 247, pp. 335–341.

Sovetov B.Ya., Yakovlev S.A. (2021) Modeling of systems. 7th ed. Moscow: Yurait (in Russian).

Ipatova E.R., Ipatov Yu.V. (2021) Methodologies and technologies of system design of information systems. 3rd ed. Moscow: FLINTA (in Russian).

ISO/IEC/IEEE 12207:2017. Systems and software engineering — Software life cycle processes. Geneva: ISO.

ISO/IEC 25010:2011. Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models. Geneva: ISO.

GOST 34.601-90. Information technology. Set of standards for automated systems. Automated systems. Stages of creation. Moscow: Standartinform (in Russian).

GOST 19.701-90. Unified system of program documentation. Schemes of algorithms, programs, data and systems. Notation and rules. Moscow: Standartinform (in Russian).

Abramov A.E., Abramova M.A., Bezsmertnaya E.R. et al. (2024) Digital trajectories of economy and finance in the 21st century: A monograph. K.V. Krinichanskiy, B.B. Rubtsov (eds.). Moscow: Knorus (in Russian).

About the authors

Vasilii M. Evdokimov

Department of Automated Control Systems, National University of Science and Technology MISIS, 4 Leninsky Prospect, Moscow 119049, Russia;

E-mail: m2201058@edu.misis.ru

ORCID: 0009-0004-8821-8414
