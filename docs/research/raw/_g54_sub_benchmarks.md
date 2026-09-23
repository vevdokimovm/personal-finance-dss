# G54 sub — LLM на финансовых бенчмарках (сырьё)

Дата обращения ко всем источникам: 17.09.2026. Подагент темы «LLM вместо детерминированного калькулятора».
Числа из сниппетов поиска помечены [сниппет].

## 1 Финансовые бенчмарки

### 1.1 Vals.ai Finance Agent v2 (FAB v2) — класс: лидерборд-замер (вендор бенчмарка, не рецензируемо)
URL: https://vals.ai/benchmarks/fabv2 (текст из выдачи Exa, highlights — [сниппет]).
Методика: Bigeard, Nashold, Krishnan, Wu, «Finance Agent Benchmark: Benchmarking LLMs on Real-world
Financial Research Tasks», Vals AI, 2025, arXiv:2508.00828.
Дословно со страницы vals.ai:
> «Muse Spark 1.2 leads Finance Agent v2 with 60.60% accuracy. Claude Opus 5 follows at 58.63%, with Gemini 3.5 Flash at 57.86%.»
> «Models are able to handle simple retrieval tasks, but still struggle to perform reliably [on] harder, multi-step financial work that relies on precise numbers»
> «Muse Spark 1.2 is the only model above 60% with Partial Credit. Under stricter All-Pass scoring, it reaches 50.88%, while every other model remains below 48%.»
> «no single model leads all nine question categories, and the hardest categories remain Financial Modeling and Precedents, where the category leaders reach only 34.52% and 36.37%, respectively.»
> «General Quantitative, Earnings Analysis, General Qualitative, Market Analysis, and Disclosure Analysis all have category leaders above 70%. Adjustments tops out at 56.29%, while Comparables reaches 50.24%»
> «Muse Spark 1.2 leads at 60.60% while also being ... about a seventh the cost of Claude Opus 5»
> «One of Opus 5's 1,350 run-task results used Claude Opus 4.8 as a refusal fallback.»

Зеркало benchmarklist.com/benchmarks/vals_finance_agent_v2/ (агрегатор, импорт 2026-07-28), дословно строки:
| Модель | Score | Std.err | Latency, с | Cost/test, $ |
|---|---|---|---|---|
| Claude Opus 5 max | 58.633% | 0.077 | 598.42 | 5.12 |
| Gemini 3.5 Flash high | 57.861% | 0.231 | 322.28 | 2.51 |
| Muse Spark 1.1 x-high | 57.207% | 0.789 | 414.77 | 0.723 |
| Claude Fable 5 max | 56.314% | 0.84 | 610.95 | 8.06 |
| GPT 5.6 Luna max | 55.044% | 0.309 | 772.15 | 1.31 |
| Claude Opus 4.8 max | 53.918% | 0.159 | 547.4 | 4.22 |
| Claude Sonnet 5 max | 53.909% | 0.518 | 792.09 | 1.13 |
| GPT 5.6 Sol max | 53.756% | 0.846 | 1165.26 | 1.25 |
| GPT 5.5 x-high | 51.76% | 0.55 | 662.27 | 4.15 |
| Claude Opus 4.7 high | 51.509% | 0.49 | 360.44 | 4.03 |
| Claude Sonnet 4.6 max | 51.035% | 0.329 | 695.59 | 2.41 |
| Claude Haiku 4.5 | 31.01% | — | — | — |

Зеркало benchlm.ai/benchmarks/financeagentv2 (более свежий снимок, 58 моделей) [сниппет]:
Gemini 3.8 Flash 61.4% · Muse Spark 1.2 60.6% · Muse Spark 1.3 Max 60.0% · Gemini 3.7 Flash 59.0% ·
Claude Fable 5.1 58.9% · Claude Opus 5 58.6% · ... GPT-6 Astra 53.5% · GPT-5.5 51.8%.
llm-stats.com: среднее по 26 моделям 0.430, лидер 0.579 (обновлено август 2026) [сниппет].

### 1.2 Vals.ai Finance Agent v1.1 — лидерборд-замер
benchmarklist.com/benchmarks/vals_finance_agent/ «Results updated May 4, 2026» [сниппет]:
Claude Opus 4.7 high 64.373% (std.err 2.79) · Claude Sonnet 4.6 max 63.331% · GPT-5.4 Pro 61.5% (launch post) ·
Muse Spark 60.595% · Claude Opus 4.6 Thinking max 60.046% · GPT 5.5 x-high 59.963% ·
Claude Opus 4.5 (20251101) Thinking high 58.81% · GPT 5.2 (2025-12-11) 58.535% · GPT 5.4 57.152% ·
Claude Sonnet 4.5 (20250929) 54.5% · GPT 5 (2025-08-07) high 52.151%.
Вывод для темы: на агентских финзадачах лучшая модель мира правильно отвечает на ~6 из 10 вопросов
(All-Pass — ~5 из 10), а категория «Financial Modeling» (ближайшая к нашему расчёту) — ~1 из 3.

### 1.3 FinanceBench — Islam, Kannappan, Kiela, Qian, Scherrer, Vidgen (Patronus AI), arXiv:2311.11944, 20.11.2023 — препринт (широко цитируемый)
DOI 10.48550/arXiv.2311.11944; код/150 открытых кейсов github.com/patronus-ai/financebench. Таблица дословно (n=150 на конфигурацию):
| Модель | Конфигурация | Correct | Incorrect | Failed |
|---|---|---|---|---|
| GPT-4-Turbo | Closed Book | 14 (9%) | 5 (3%) | 126 (88%) |
| GPT-4-Turbo | Shared Vector Store | 29 (19%) | 20 (13%) | 101 (68%) |
| Llama2 | Single Vector Store | 62 (41%) | 81 (54%) | 7 (5%) |
| GPT-4-Turbo | Single Vector Store | 75 (50%) | 17 (11%) | 58 (39%) |
| Claude2 | Long Context | 114 (76%) | 32 (21%) | 4 (3%) |
| GPT-4-Turbo | Long Context | 118 (79%) | 26 (17%) | 6 (4%) |
| GPT-4-Turbo | Oracle | 128 (85%) | 22 (15%) | 0 (0%) |
> «GPT-4-Turbo used with a retrieval system incorrectly answered or refused to answer 81% of questions.»
> «Incorrect answers vary, from calculations that are off by small margins to several orders of magnitude»
> «once the right information has been extracted, they still need to reason correctly – and models still demonstrate weaknesses in this regard.»
> «many of the metrics-generated questions involve more complex numeric reasoning ... Models typically perform worst on the metrics-generated questions»
Критика (beancount.io, 12.05.2026, блог): «Even the oracle leaks. With perfect evidence, the ceiling is 85% ... n=150 ... statistically meaningless» ranking difference.

### 1.4 FinanceBench в 2026 — вторичные замеры
(а) Dewey (meetdewey.com/blog/financebench-eval, 07.04.2026; github.com/meetdewey/financebench-eval) — блог вендора (маркетинг), но с кодом:
| Система | Accuracy |
|---|---|
| GPT-4-Turbo, vector RAG (2023) | 19.0% |
| Dewey + GPT-5.4 | 62.9% (±0.3%) |
| FinSage, agentic RAG (arXiv 2504.14493, 2025) | 70.0% |
| Claude Opus 4.6, full context | 76.0%* (79.2% на 144 влезающих) |
| GPT-4-Turbo, full context (2023) | 78.0% |
| Dewey + Claude Opus 4.6 | 83.7% (±0.4%) |
| LinqAlpha (специализированная, блог 2024) | 97.2% |
Заметка: Opus 4.6 full context (76%) НЕ лучше GPT-4-Turbo 2023 (78%) на тех же 150 — рост упирается не в модель, а в обвязку.
(б) financebenchmark.ai/benchmarks/financebench — агрегатор, источник цифр не раскрыт (ссылается просто на arXiv:2311.11944) [сниппет, доверие низкое]:
GPT-5.5 91.0 (2026-04) · Claude Opus 4.7 88.0 · Gemini 3.1 Pro 86.0 · DeepSeek V4 Pro 85.0 · Grok 4.3 84.0 · Kimi K2.6 82.0 · GLM-5.1 79.0 · MiniMax M2.7 77.0.
Там же лента: «2026-09-01 Claude Fable 5.1 leads Tax Agent Bench (77.6%) and EMB (76.7%)»; «2026-09-03 GPT-6 Astra ... 63.3% on Tax Agent Bench»; «2026-09-02 Gemini 3.8 Flash takes #1 rank on Finance Agent (v2) with 61.4%».

## 2 Длина цепочки и инструменты

### 2.1 Chen, Ma, Wang, Cohen — Program of Thoughts (PoT). arXiv:2211.12588, 2022; опубл. TMLR 2023 — рецензируемое
DOI 10.48550/arXiv.2211.12588. Дословно (аннотация):
> «We evaluate PoT on five math word problem datasets and three financial-QA datasets [FinQA, ConvFinQA, TAT-QA] ... We find that PoT has an average performance gain over CoT of around 12% across all datasets.»
> «LLMs are very prone to arithmetic calculation [errors]»
Полный текст добыт (PDF v4, «Published in Transactions on Machine Learning Research (10/2023)»), копия:
/Users/vasyaevdokimov/raw-originals/finpilot-data/llm_vs_product/chen2022_program_of_thoughts_2211.12588v4.pdf
> «For financial QA datasets, PoT improves over CoT by roughly 20% on FinQA/ConvFinQA and 8% on TATQA. The larger improvements in FinQA and ConvFinQA are mainly due to miscalculations on LLMs for large numbers (e.g. in the millions). CoT adopts LLMs to perform the computation, which is highly prone to miscalculation errors, while PoT adopts a highly precise external computer to solve the problem.»
Table 2 (few-shot), дословно выборка:
| Метод | FinQA | ConvFinQA | TATQA |
|---|---|---|---|
| Published SoTA (fine-tuned) | 68.0 | 68.9 | 73.6 |
| Codex Direct | 25.6 | 40.0 | 55.0 |
| Codex CoT | 40.4 | 45.6 | 61.4 |
| PoT-Codex | 64.5 | 64.6 | 69.0 |
| Codex CoT-SC | 44.4 | 47.9 | 63.2 |
| PoT-SC-Codex | 68.1 | 67.3 | 70.2 |
| CoT-GPT4 | 58.2 | — | — |
| PoT-GPT4 | 74.0 | — | — |
(GPT-4: +15.8 п.п. от вынесения вычислений в интерпретатор на FinQA.)

### 2.2 «When LLMs Stop Following Steps: A Diagnostic Study of Arithmetic Procedural Execution», arXiv:2605.00817 (2026) — препринт
> «Average first-answer accuracy drops from 63% on 5-step procedures to 20% on 95-step procedures. ... failures often involve missing answers, premature answers, self-correction after an initial error and under-executed traces.»
Релевантность: амортизация на 60 мес. = процедура ~60+ шагов с зависимостью от промежуточных состояний.

### 2.3 Sinha et al.(?) «The Illusion of Diminishing Returns: Measuring Long Horizon Execution in LLMs», arXiv:2509.09677 (2025) — препринт (авторы по сниппету не видны)
> «the per-step accuracy of models degrades as the number of steps increases. This is not just due to long-context limitations—curiously, we observe a self-conditioning effect—models become more likely to make mistakes when the context contains their errors from prior turns. ... thinking mitigates self-conditioning, and also enables execution of much longer tasks in a single turn.»
> «even marginal gains in single-step accuracy can compound into exponential improvements in the length of tasks a model can successfully complete»
(Контраргумент против продукта: рост длины надёжно исполняемой задачи экспоненциален от точности шага.)

### 2.4 Larsen, Laurent, Rakhamsari, Turgut, Antulov-Fantulin — V-FiLLM: Verified Financial LLM Reasoning Benchmark, arXiv:2608.11047 (2026) — препринт
> «accuracy falls up to 51% as reasoning depth increases, and up to 47% points under adversarial numerical perturbations» (на открытых моделях)
> «LoRA fine-tuning on verified chain-of-thought traces improves accuracy from 81.1% to 85.6%»

### 2.5 «Bridging the Arithmetic Gap: The Cognitive Complexity Benchmark and Financial-PoT», arXiv:2601.21157 (2026) — препринт
> «model performance does not degrade linearly with task difficulty; rather, it collapses precipitously once a complexity threshold is crossed» («Cognitive Collapse»); «frequent "Arithmetic Hallucinations", where models might confidently assert that 9.11 > 9.9»
(Числа Financial-PoT до/после не извлечены — Недобытое.)

### 2.6 FINDER, arXiv:2510.13157 (2025) — препринт
> «FINDER achieves a new state-of-the-art performance on both the FinQA and ConvFinQA datasets, surpassing previous benchmarks with execution accuracy improvements of 5.98% and 4.05%»

### 2.8 He, Wang, Xiong, Chen, Hu (Ant Research) — FinMathBench, AAAI 2026 (Proc. AAAI 40(37)) — рецензируемое
DOI 10.1609/aaai.v40i37.40358; данные github.com/ant-research/FinMathBench. 946 вопросов, 4 уровня, 40 LLM, CoT и PoT.
> «Evaluation results on 40 LLMs demonstrate significant accuracy drops in multi-formula questions, e.g., 72.9% (1-Formula) to 14.0% (4-Formula) for GPT-4o under Chain-of-Thought prompting. Three critical flaws of LLMs are also observed: poor direct calculation performance, bias toward frequently solved variables in formulas, and erroneous "correction" of valid but extreme financial values.»
(Числа PoT для GPT-4o и данные по Claude не извлечены.)

### 2.9 BankMathBench, arXiv:2602.17072 (2026) — препринт
> «these models still exhibit low accuracy in core banking computations—including total payout estimation, comparison of products with varying interest rates, and interest calculation under early repayment conditions. ... existing LLMs often make systematic errors—misinterpreting product types, applying conditions incorrectly, or failing basic calculations involving exponents and geometric progressions.»
> «With tool-augmented fine-tuning, the models achieved average accuracy increases of 57.6%p (basic), 75.1%p (intermediate), and 62.9%p (advanced), representing significant gains over zero-shot baselines.» (открытые модели)
Прямо релевантно: «interest calculation under early repayment» = наш досрочный платёж.

### 2.10 Śmietańska-Nowak (Omni Calculator) — ORCA Benchmark, arXiv:2511.02589, 05.11.2025 — препринт (автор — вендор калькуляторов, конфликт интересов)
> «In 500 natural-language tasks across domains such as finance, physics, health, and statistics, the five state-of-the-art systems (ChatGPT-5, Gemini 2.5 Flash, Claude Sonnet 4.5, Grok 4, and DeepSeek V3.2) achieved only 45–63% accuracy, with errors mainly related to rounding (35%) and calculation mistakes (33%).»
> пример задачи: «If I deposit $50,000 at 5% APR, compounded weekly, what will my balance be after 18 months?»
> «models often fail together» (r≈0.40–0.65)
(Разбивка по моделям и по домену Finance не извлечена.)

### 2.11 CIFQA, arXiv:2608.26114 (2026) — препринт
> «CIFQA achieves 95.54% accuracy on calculation-intensive queries and 90.87% overall accuracy, substantially outperforming direct LLM baselines even when provided with complete formulas, rate cards, and benchmark instructions — confirming the limitation is architectural rather than informational.»
> «a 17B open-source backbone operating within CIFQA outperforms ...» (обрезано)
Архитектура: LLM — интерпретация, детерминированные Python-инструменты — начисление, сроки, досрочное изъятие. Это ровно паттерн «LLM + наш движок».

### 2.12 CreditCardQA, arXiv:2607.26952 (2026) — препринт
> «1,800 questions ... PoT yields consistent performance gains, particularly for models with weaker baseline reasoning ... failures arise less from arithmetic and more from misapplied financial rules, missed conditions, and misunderstandings of contractual terms. ... errors often arise in edge cases such as late-payment penalties or small-balance scenarios that are more likely to affect lower-income or financially vulnerable individuals.»
(Важно: с PoT арифметика перестаёт быть главной ошибкой — главной становится интерпретация условий.)

### 2.13 Hermes Plant — «Legacy no-tools LLM finance benchmark (IRR, XIRR, DCF, waterfall)», 03.07.2026 — блог вендора (маркетинг, продаёт детерминированный API)
URL: https://hermesplant.com/benchmarks/llm-finance-math
> «We asked 6 production models ... to compute IRR, XIRR, NPV, a DCF valuation, and a private-equity distribution waterfall — with no calculator»; модели: «GPT-4o mini, GPT-4o, GPT-4.1, GPT-5.1, Claude Haiku 4.5, Claude Sonnet 5», «temperature 0 where supported».
> «The GPT-4o-class models most agents call by default were wrong on 44% of attempts.»
> Periodic IRR (точно 23.38%): GPT-4o mini 50.00% wrong · GPT-4o 328.90% wrong · GPT-4.1 23.40% · GPT-5.1 23.40% · Claude Haiku 4.5 23.45% · Claude Sonnet 5 23.37% (все последние — correct в допуске)
> Оговорка самого автора: «It does not prove that deterministic finance alone is a durable moat.»
Полная страница добыта через r.jina.ai (13 371 байт). Дословно итог и СТАБИЛЬНОСТЬ (каждая задача 3 раза, мажоритарно):
| Модель | Canonical set | Fresh variants | Same answer every attempt |
|---|---|---|---|
| GPT-4o mini | 4/8 | 3/8 | 4/8 |
| GPT-4o | 5/8 | 5/8 | 2/8 |
| GPT-4.1 | 6/8 | 7/8 | 1/8 |
| GPT-5.1 | 8/8 | 5/8 | 1/8 |
| Claude Haiku 4.5 | 7/8 | 6/8 | 3/8 |
| Claude Sonnet 5 | 7/8 | 8/8 | 4/8 |
| Deterministic engine (reference) | 8/8 | 8/8 | always |
> XIRR on irregular dates (точно 37.34%): GPT-4o 2450.00% wrong; GPT-4.1 0.16% wrong; Claude Sonnet 5 «— wrong»; GPT-5.1 37.30% correct.
> «The model states each wrong number with full confidence and no error flag.»
Для темы: даже при 7–8/8 по мажоритарному голосу фронтир-модели возвращали одно и то же число во всех трёх попытках лишь в 1–4 задачах из 8 (при temperature 0, где поддерживается). GPT-5.1: 8/8 на известных задачах, 5/8 на свежих вариантах (признак контаминации или шума).

### 2.14 Блог dev.to (Renato Marinho, 05.08.2026) — мнение, не замер
> «If you have ever asked an agent to calculate a 360-month SAC amortization schedule, you've likely seen it present a perfectly formatted table that is mathematically impossible.»

### 2.7 Обзор «Numeracy in Large Language Models: Fundamental Limitations and Paths to Improvement», arXiv:2608.13129 (2026)
> «Simple magnitude comparisons, addition of large integers, basic fraction arithmetic, and operations in scientific notation routinely produce incorrect results across frontier models.»
> «Dziri et al. 2023 ... demonstrating that performance degrades systematically as reasoning chains lengthen.» (Dziri et al., «Faith and Fate», NeurIPS 2023 — рецензируемое.)

## 3 Недетерминизм

### 3.1 Atil, Aykent, Chittams, Fu, Passonneau, Radcliffe, Rajagopal, Sloan, Tudrej, Ture, Wu, Baldwin(?) — «Non-Determinism of "Deterministic" LLM Settings», arXiv:2408.04667 (v1 06.08.2024, v5 02.04.2025) — препринт
(авторы после Radcliffe по arXiv API не дочитаны; первые шесть — дословно из API.) Дословно аннотация:
> «We investigate non-determinism in five LLMs configured to be deterministic when applied to eight common tasks in across 10 runs, in both zero-shot and few-shot settings. We see accuracy variations up to 15% across naturally occurring runs with a gap of best possible performance to worst possible performance up to 70%. In fact, none of the LLMs consistently delivers repeatable accuracy across all tasks, much less identical output strings. ... non-determinism perhaps essential to the efficient use of compute resources via co-mingled data in input buffers so this issue is not going away anytime soon.»
Метрики: TARr@N (совпадение сырого вывода), TARa@N (совпадение извлечённого ответа). Код: github.com/breckbaldwin/llm-stability.

### 3.2 Horace He & Thinking Machines Lab — «Defeating Nondeterminism in LLM Inference», блог, сентябрь 2025 — блог вендора (инженерный, с воспроизводимым кодом)
URL: https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/ (через r.jina.ai, полный текст 42 773 байта).
> «We use `Qwen/Qwen3-235B-A22B-Instruct-2507` and sample 1000 completions at temperature 0 with the prompt "Tell me about Richard Feynman" (non-thinking mode), generating 1000 tokens each. Surprisingly, we generate _80_ unique completions, with the most common of these occuring 78 times.»
> «the completions are actually identical for the first 102 tokens! The first instance of diverging completions occurs at the 103rd token. ... 992 of the completions go on to generate "Queens, New York" whereas 8 of the completions generate "New York City".»
> «when we enable our batch-invariant kernels, all of our 1000 completions are identical.»
> «the primary reason nearly all LLM inference endpoints are nondeterministic is that the load (and thus batch-size) nondeterministically varies!»
Для темы: детерминизм достижим только на СВОЁМ инференс-стеке с batch-invariant ядрами; коммерческий API (Claude/GPT) этого не гарантирует. Нюанс: у рассуждающих моделей Anthropic temperature часто не настраивается вовсе (не проверено здесь).

### 3.3 «Stochastic CHAOS» (позиционная статья против детерминированного инференса), arXiv:2601.07239 (2026) — препринт
> «Atil et al. ... show that, across repeated T=0 runs of the same evaluation suite, task accuracy can fluctuate by double-digit percentages purely due to implementation-level nondeterminism.»

## 4 Ошибки в финсоветах

### 4.1 Schlosky, Karadas, Raskie — «ChatGPT, Help! I Am in Financial Trouble», J. Risk Financial Manag. 17(6):241, 2024 — рецензируемое (MDPI)
DOI 10.3390/jrfm17060241. 21 кейс личных финансов, ChatGPT-3.5. Дословно:
> «its recommendations tend to be generic, and they often overlook alternative solutions and viewpoints and priority of recommendations.»
> «It does not think outside the box ... the chatbot does not have a holistic approach. It instead provides solutions to every problem without having a holistic view and without setting clear priorities for advice seekers.»
> «in two cases where we ask ChatGPT to perform basic retirement calculations, we observe that its solutions contain errors, making them unreliable.»
> (опрос Caporal 2023) «the percentage of Americans who used ChatGPT to inquire about various financial products ... is 54%»
Для темы: отсутствие приоритизации — ровно то, что делает наш SAW-ранжинг.

### 4.2 Schlosky, Raskie — «ChatGPT as a Financial Advisor: A Re-Examination», JRFM 18(12):664, 23.11.2025 — рецензируемое (MDPI), качественная оценка без баллов
DOI 10.3390/jrfm18120664. Дословно:
> «ChatGPT-4o often produced more thorough suggestions and paid closer attention to tax implications—though it still overlooked some important details. ... Generalizations remained too broad ..., legal references were occasionally misleading»
> «the recommendations generated by ChatGPT-5 were quite similar to those generated by ChatGPT-4o, but the accuracy in the numerical problems was better under ChatGPT-5. While not a replacement for financial professionals, ChatGPT appears to be maturing into a more useful supporting tool»
(Враждебно продукту: прогресс в числах между поколениями зафиксирован.)

### 4.3 Gary N. Smith — «LLMs Can't Be Trusted for Financial Advice», Journal of Financial Planning (2024?), репозиторий Claremont (Pomona) — практико-рецензируемое (журнал FPA; год и выпуск не сверены)
URL: https://scholarship.claremont.edu/cgi/viewcontent.cgi?article=1017&context=pomona_fac_econ
> «Three prominent LLMs were tested with 11 financial-decision prompts. The LLM responses were seemingly authoritative but riddled with arithmetic and critical-thinking mistakes.»
> «I chose these two loans to see if the LLMs would compare the total payments and ignore the time value of money. All three LLMs made this mistake and recommended the one-year loan with a 9 percent APR.»
> «Bing said that it used a "loan interest calculator" and found the total interest to be $4,230.22 for the one-year loan and $5,640.00 for the 10-year loan. The first number is a simple-interest calculation; the second number is mysterious as it is neither a simple interest nor amortized interest.»
> «Bard said that it used an "online loan calculator" to determine that the one-year loan would have monthly payments of $4,083 and total interest of $3,423 while the 10-year loan would have monthly payments of $444 and total interest of $14,585. These numbers are not only incorrect but ...»
Модели: ChatGPT 3.5, Bing (GPT-4), Bard — поколение 2023, для 2026 устарело. Ценность: именно амортизационные ошибки + ложные ссылки на «калькулятор».

### 4.4 Hean, Saha, Saha — «Can AI Help with Your Personal Finances?», arXiv:2412.19784, 27.12.2024 — препринт
> «We evaluate several leading LLMs, including OpenAI's ChatGPT, Google's Gemini, Anthropic's Claude, and Meta's Llama ... on topics such as mortgages, taxes, loans, and investments. ... these models achieve an average accuracy rate of approximately 70% ... LLMs struggle to provide accurate responses for complex financial queries ... notable improvements in newer versions of these models»
(Разбивка по моделям/темам не извлечена.)

### 4.5 «Can LLMs be Good Financial Advisors?: An Initial Study in Personal Decision Making for Optimized Outcomes», FinPlan workshop @ ICAPS 2023 — воркшоп (авторы по сниппету не видны; вероятно Lakkaraju, Srivastava et al.)
URL: https://icaps23.icaps-conference.org/papers/finplan/FinPlan23_paper_7.pdf
> «We asked 13 questions representing banking products in personal finance ... in different dialects and languages (English, African American Vernacular English, and Telugu). We find that although the outputs of the chatbots are fluent and plausible, there are still critical gaps in providing accurate and reliable financial information»

## 5 Темп по поколениям

### 5.1 Finance Agent Benchmark v1 — первоисточник, Bigeard, Nashold, Krishnan, Wu (Vals AI), arXiv:2508.00828 (данные апрель–май 2025) — препринт
> «The dataset includes 537 expert-authored questions ... even the best-performing model (OpenAI's o3) achieved only 46.8% accuracy, at an average cost of $3.79 per query.»
> «even the most expensive model (o3) averages just 3.1 minutes per task and costs $3.78, compared to human experts requiring 16.8 minutes and costing $25.66»
Таблица (Acc. class-balanced / naive):
| Модель | Class-balanced | Naive | Cost/query |
|---|---|---|---|
| o3 | 46.8 ± 2.2 | 51.4 ± 2.2 | $3.7861 |
| Claude 3.7 Sonnet (Thinking) | 45.9 ± 2.2 | 52.0 ± 2.2 | $1.0168 |
| Claude 3.7 Sonnet | 44.3 ± 2.2 | 49.5 ± 2.2 | $0.9886 |
| o4 Mini | 37.3 ± 2.2 | 40.6 ± 2.1 | $0.2863 |
| Gemini 2.5 Pro Preview | 28.4 ± 2.0 | 33.0 ± 2.0 | $0.1963 |
| GPT 4.1 | 26.7 ± 2.0 | 30.7 ± 2.0 | $0.2309 |
| o1 | 21.4 ± 1.7 | 25.9 ± 1.9 | $1.4398 |
| GPT 4o (2024-08-06) | 20.0 ± 1.7 | 24.6 ± 1.9 | $0.2575 |
| Claude 3.5 Haiku | 13.1 ± 1.4 | 17.1 ± 1.6 | $0.0665 |
the-decoder.com (30.04.2025, пресса): «In the "Trends" category, ten models scored 0%, with the best result—28.6%—coming from Claude 3.7 Sonnet.»

### 5.2 Сводная траектория (собрано из 1.1, 1.2, 5.1; v1→v1.1→v2 — РАЗНЫЕ наборы, прямое сравнение v1.1 и v2 некорректно)
| Дата | Бенчмарк | Лучший Claude | Лучший вообще |
|---|---|---|---|
| апр 2025 | FAB v1 | Claude 3.7 Sonnet Thinking 45.9% | o3 46.8% |
| май 2026 (прогон 04.05.2026) | FAB v1.1 | Claude Opus 4.7 64.4% | он же |
| окт 2025 → май 2026 внутри v1.1 | FAB v1.1 | Sonnet 4.5 54.5% → Opus 4.5 58.8% → Opus 4.6 60.0% → Opus 4.7 64.4% | — |
| внутри v1.1 | FAB v1.1 | GPT-4o (2024-08) 8.1% → GPT-5 (2025-08) 52.2% → GPT-5.1 55.3% → GPT-5.2 58.5% → GPT-5.5 60.0% | — |
| июль 2026 | FAB v2 | Opus 4.7 51.5% → Opus 4.8 53.9% → Fable 5 56.3% → Opus 5 58.6% → Fable 5.1 58.9% | Gemini 3.8 Flash 61.4% (02.09.2026) |
Оценка вахты (не цитата): на v1/v1.1 прирост лидера ≈ +18 п.п. за ~12 мес.; внутри линейки Claude на v1.1 ≈ +10 п.п. за ~7 мес. (Sonnet 4.5 окт 2025 → Opus 4.7 апр 2026); на v2 ≈ +7 п.п. за ~3–4 мес. (Opus 4.7 → Fable 5.1). Бенчмарк пришлось усложнить (v2), когда v1.1 подошёл к ~64%. Потолок «Financial Modeling» на v2 — 34.5%.
Н5 («окно закрывается»): подтверждается частично — рост устойчивый, но абсолютная надёжность на многошаговых числовых задачах всё ещё ~50–60% (агентские) и далеко от 100% детерминированного движка.

### 5.3 Прочие сигналы
- Schlosky & Raskie 2025 (§4.2): ChatGPT-5 точнее ChatGPT-4o в числовых задачах тех же 21 кейсов.
- Hermes (§2.13): архив прогонов — GPT-4o mini 2/6, GPT-4o 3/6 → GPT-5.1 6/6 (22.06.2026, без инструментов).
- vals.ai Vals Index (обновлён 11.09.2026): 1 место — Claude Fable 5.1, 2 — Claude Opus 5, 3 — GPT-6 Astra [сниппет].
- vals.ai держит профильные бенчмарки CorpFin v2 (кредитные договоры), MortgageTax, TaxEval v2 — числа не извлекались.

## Итог по вопросам (выжимка вахты-подагента)
1. Бенчмарки: лучшие модели на агентских финзадачах FAB v2 — 58–61% (Claude Opus 5 58.6%, Fable 5.1 58.9%, лидер Gemini 3.8 Flash 61.4%); All-Pass <51%; «Financial Modeling» ≤34.5%. FinanceBench (простой QA) — вторичные замеры 76–91% для моделей 2026 г.
2. Длина цепочки: падение монотонное и крутое (63%→20% на 5→95 шагах; GPT-4o 72.9%→14.0% на 1→4 формулах, AAAI 2026). Вынос вычислений в код: +15–24 п.п. на FinQA (PoT, TMLR 2023); инструментальные фреймворки 90–96% (CIFQA). С кодом главная ошибка смещается к неверному толкованию условий (CreditCardQA).
3. Недетерминизм: T=0 не детерминирует — до 15% разброса точности, 70% разрыв лучший/худший (Atil et al.); 80 уникальных из 1000 (Thinking Machines); фронтир-модели дают одно и то же число во всех 3 попытках лишь в 1–4 из 8 финзадач (Hermes, 2026).
4. Ошибки в советах: generic, без приоритизации, ошибки в пенсионных расчётах (JRFM 2024); игнор стоимости денег во времени у всех трёх LLM 2023 г. (Smith); ~70% точности по ипотеке/налогам/кредитам (Hean et al. 2024); GPT-5 точнее 4o в числах (JRFM 2025).
5. Темп: +18 п.п. у лидера за год на FAB v1→v1.1; бенчмарк пришлось усложнить; на v2 +7 п.п. за ~4 месяца.

## Недобытое
- FinQA/TAT-QA/ConvFinQA — свежие (2025–2026) числа для Claude-моделей: не искались отдельно (бюджет).
- BizFinBench, FinEval — не искались (бюджет 20 действий).
- FinMathBench: числа PoT и строки для Claude — только аннотация (полный текст AAAI не открывался).
- ORCA: разбивка по моделям и домену Finance — только аннотация.
- Hean et al. 2024: разбивка точности по моделям (в т.ч. Claude) — только аннотация.
- Gary N. Smith: год и выпуск Journal of Financial Planning не сверены.
- arXiv:2509.09677: авторы не подтверждены.
- Atil et al.: полный список авторов не дочитан; числа по конкретным моделям — только аннотация.
- Finance-специфичные работы по недетерминизму (разброс именно денежных ответов) — кроме Hermes (блог вендора) не найдены; целевой поиск не делался.
- Проверка, поддерживает ли API Claude temperature=0 у рассуждающих моделей 2026 г. — не делалась.
