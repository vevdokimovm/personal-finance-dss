# Sub-17: Доверие/принятие рекомендаций в финансах + вред и этика RS в финансах

Дата прогона: 2026-09-09
Статус: ЗАВЕРШЕНО (в пределах бюджета; часть пунктов см. "Что не добыто")

Бюджет: WebSearch ≤10, WebFetch/curl ≤15.

---

## ВОПРОС A: доверие, принятие, алгоритм-аверсия в финансах

### 1. Dietvorst, Simmons, Massey (2018) «Overcoming Algorithm Aversion: People Will Use Imperfect Algorithms If They Can (Even Slightly) Modify Them», Management Science 64(3):1155-1170

🟢 Источник открыт: working-paper версия (идентична по тексту опубликованной, DOI 10.1287/mnsc.2016.2643) —
https://marketing.wharton.upenn.edu/wp-content/uploads/2016/10/Dietvorst-Overcoming-Algorithm-Aversion.pdf
(параллельно скачан и опубликованный PDF: https://faculty.wharton.upenn.edu/wp-content/uploads/2016/08/Dietvorst-Simmons-Massey-2018.pdf).
Извлечение через `pdftotext`.

**Abstract (дословно):**
> «Although evidence-based algorithms consistently outperform human forecasters, people consistently fail
> to use them, especially after learning that they are imperfect. In this paper, we investigate how algorithm
> aversion might be overcome. In incentivized forecasting tasks, we find that people are considerably more
> likely to choose to use an algorithm, and thus perform better, when they can modify its forecasts.
> Importantly, this is true even when they are severely restricted in the modifications they can make. In fact,
> people's decision to use an algorithm is insensitive to the magnitude of the modifications they are able to
> make.»
(с. 2 препринта / соответствует Abstract опубликованной версии)

**Study 1 (числа), с. 8-9 препринта:**
> «Whereas only 32% of participants in the can't-change condition chose to use the model's forecasts, 73%
> of participants in the change-10 condition, χ2(1, N = 145) = 24.19, p < .001, and 76% of participants in the
> adjust-by-10 condition, χ2(1, N = 146) = 28.40, p < .001, chose to use the model.»
Участники, выбравшие использовать модель, отклонялись от неё существенно меньше разрешённого:
«provided forecasts that were 4.71 percentiles away from the model's forecasts» (adjust-by-10, лимит был 10),
«changed the model 8.54 times on average, and only 39% used all 10 of their changes» (change-10).

**Study 2 (репликация), с. 13-14:**
> «47% of participants in the can't-change condition chose to use the model's forecasts, 77% of participants
> in the change-10 condition, χ2(1, N = 542) = 49.37, p < .001, and 75% of participants in the adjust-by-5
> condition, χ2(1, N = 530) = 44.33, p < .001, chose to use the model.»

**Study 3 (эффект НЕ зависит от величины разрешённой корректировки), с. ~16-17:**
> «Whereas only 47% of participants in the can't-change condition chose to use the model, 70% of
> participants in the adjust-by-X conditions chose to the model» — при этом внутри adjust-by-X разбивка
> почти не отличается по величине допуска: «71%, 71%, and 68% chose to the model in the adjust-by-10,
> adjust-by-5, and adjust-by-2 conditions» (χ2(1, N=...) значимо против can't-change; различия МЕЖДУ
> тремя adjust-условиями незначимы). Ключевой вывод статьи: готовность пользоваться алгоритмом не
> зависит от того, НАСКОЛЬКО сильно разрешена корректировка — важен сам факт наличия контроля.

**Study 4 (downstream: доверие и повторный выбор после ошибки), с. 25-26, 31-32:**
Дизайн: model-only (принудительно только модель) vs use-freely (неограниченная корректировка) vs
adjust-by-10 (ограниченная). Все участники видели, что их процесс прогнозирования ошибается: «All
participants saw their forecasting process err. The best performing participant had an average absolute
error of 9.2.»
После ошибки, при выборе процесса для СЛЕДУЮЩЕЙ серии прогнозов:
> «participants who could (restrictively or freely) modify the model's forecasts in Stage 1 were much more
> likely to choose the "model-only" option (30%) than participants who could not modify the model's
> forecasts in Stage 1 (12%), χ2(1, N = 823) = 38.45, p < .001.»
То есть даже возможность в прошлом корректировать алгоритм делает людей значимо более готовыми
затем довериться ему ПОЛНОСТЬЮ (30% против 12% — рост в 2.5 раза), несмотря на то что модель
на их глазах ошибалась.
Дополнительно (доверие): участники условия use-freely после ошибки «had more confidence in the
model's forecasts than their own, t(203) = 2.77, p = .006, and thought that their average absolute error was
similar to the model's, t(203) = 0.51, p = .612» (с. 31).

**Практический вывод статьи (для наших RS):** алгоритм-аверсию снижает не точность и не объяснение
как таковое, а ПРЕДОСТАВЛЕНИЕ ХОТЬ КАКОГО-ТО КОНТРОЛЯ над выводом — «people's decision to
use an algorithm is insensitive to the magnitude of the modifications they are able to make» — то есть даже
символическая (severely restricted) возможность скорректировать рекомендацию системы резко поднимает
готовность её принять и затем ей доверять после ошибки.

### 2. Dietvorst, Simmons, Massey (2015) «Algorithm Aversion: People Erroneously Avoid Algorithms After Seeing Them Err», Journal of Experimental Psychology: General, 144(1), 114-126

🟢 Источник открыт дословно. PDF получен через DSpace REST API репозитория UPenn (обычный `/download`
эндпоинт отдаёт JS-обвязку без содержимого; рабочий URL —
`https://repository.upenn.edu/server/api/core/bitstreams/4d24c079-228b-47bd-ba8c-166eeddee8de/content`,
найден через Semantic Scholar API `openAccessPdf`, DOI 10.1037/xge0000033). Извлечение через `pdftotext`.

**Определение алгоритм-аверсии — дословно из абстракта (с. 1):**
> «Research shows that evidence-based algorithms more accurately predict the future than do human
> forecasters. Yet when forecasters are deciding whether to use a human forecaster or a statistical
> algorithm, they often choose the human forecaster. This phenomenon, which we call algorithm aversion,
> is costly, and it is important to understand its causes. We show that people are especially averse to
> algorithmic forecasters after seeing them perform, even when they see them outperform a human
> forecaster. This is because people more quickly lose confidence in algorithmic than human forecasters
> after seeing them make the same mistake.»

**Мета-контекст (с. 1):** «Grove, Zald, Lebow, Snitz, and Nelson (2000) meta-analyzed 136 studies
investigating the prediction of human health and behavior. They found that algorithms outperformed
human forecasters by 10% on average and that it was far more common for algorithms to outperform human
judges than the opposite.»

**Дизайн (5 исследований):** участники в разных условиях либо видели работу алгоритма, либо человека,
либо обоих, либо ни одного («both, or neither»), затем решали, привязать ли свой бонус к будущим
прогнозам алгоритма или человека («tie their incentives to the future predictions of the algorithm or the
human»). Задачи: прогноз успеваемости MBA-студентов (Studies 1, 2, 4) и прогноз ранга штатов по числу
вылетающих авиапассажиров (Studies 3a, 3b).

**Ключевой количественный результат — модель видели ошибающейся, но она объективно превосходила
человека (с. 6):**
> «participants in the model-and-human conditions, most of whom saw the model outperform the human in
> the first stage of the experiment (610 of 741 [83%] across the five studies), were, across all studies, among
> those least likely to choose the model.»
То есть в 83% случаев участники САМИ наблюдали превосходство модели над человеком — и тем не менее
именно в этой группе (видевших работу модели) готовность довериться модели была НИЖЕ, чем у тех, кто
работу модели не видел вовсе.

**Статистика значимости эффекта по исследованиям (сноска 7, с. 6-7), участники model-and-human
условия, выбор модель vs. человек:**
> «Study 1, χ2(1, N = 271) = 39.94, p < .001; Study 3a, χ2(1, N = 309) = 4.72, p = .030; Study 3b, χ2(1,
> N = 783) = 16.83, p < .001; Study 4, χ2(1, N = 264) = 13.84, p < .001.»
Даже если ограничить выборку только теми, кто видел ПРЕВОСХОДСТВО модели над человеком, эффект
остаётся значимым: «Study 1, χ2(1, N = 242) = 20.07, p < .001; Study 3a, χ2(1, N = 302) = 2.54, p = .111;
Study 3b, χ2(1, N = 758) = 9.92, p = .002; Study 4, χ2(1, N = 235) = 5.24, p = .022.»

**Величина ошибки моделей относительно людей (с. 6, Table 3):** модель ошибалась на «15–29% more error
than the model» меньше в задаче MBA (т.е. люди ошибались на 15-29% больше модели) и «90–97% more
error than the model» в задаче про авиапассажиров — то есть в Studies 3a/3b модель делала примерно вдвое
меньше ошибок, чем человек, и даже такое драматическое превосходство не переломило аверсию.

**Асимметрия доверия (confidence), Table 4 + текст с. 7:** «seeing the model perform significantly decreased
participants' confidence in the model's forecasts in all four studies», тогда как «seeing the human perform did
not consistently decrease confidence in the human's forecasts—it did so significantly only in Study 4».
Вывод авторов: «seeing a model make relatively small mistakes consistently decreased confidence in the
model, whereas seeing a human make relatively large mistakes did not consistently decrease confidence in the
human» — асимметричный стандарт прощения ошибок.

**Ограничение доступности числовых процентов выбора по условиям:** сами проценты выбора «модель vs.
человек» по каждому условию (Did-Not-See-Model / Saw-Model / Saw-Human / Model-and-Human) поданы в
статье только графически (Figure 3, bar chart) — pdftotext не извлекает данные из растровых столбцов,
текст даёт только χ2/N/p и означенные структуры confidence (Table 4), не сырые %. Помечаю это прямо,
без реконструкции цифр по памяти.

### 3. Logg, Minson, Moore (2019) «Algorithm Appreciation: People Prefer Algorithmic to Human Judgment», Organizational Behavior and Human Decision Processes 151:90-103 (контраст к алгоритм-аверсии)

🟢 Источник открыт дословно. PDF — авторская страница (открытый доступ):
https://www.jennlogg.com/uploads/2/8/9/2/2892148/algorithm_appreciation__logg_minson_moore_2019_.pdf
(DOI 10.1016/j.obhdp.2018.12.005; OpenAlex/SemanticScholar числят статью closed-access, но PDF на
сайте автора доступен напрямую). Извлечение через `pdftotext`.

**Abstract (дословно, из метаданных Semantic Scholar, сверено с текстом PDF):**
> «Even though computational algorithms often outperform human judgment, received wisdom suggests that
> people may be skeptical of relying on them (Dawes, 1979). Counter to this notion, results from six
> experiments show that lay people adhere more to advice when they think it comes from an algorithm than
> from a person... Yet, researchers predicted the opposite result... Paradoxically, experienced professionals,
> who make forecasts on a regular basis, relied less on algorithmic advice than lay people did, which hurt
> their accuracy.»

**Метрика — Weight on Advice (WOA), определение дословно (с. ~7):**
> «Weight on Advice (WOA), is the difference between the initial and revised judgment divided by the
> difference between the initial judgment and the advice. WOA of 0% occurs when a participant ignores
> advice and WOA of 100% occurs when a participant abandons his or her prior judgment with the advice.»

**Experiment 1A (визуальная оценка веса человека по фото), числа:**
> «Participants showed an appreciation of algorithms, relying more on the same advice when they thought it
> came from an algorithm (M = 0.45, SD = 0.37), than when they thought it came from other people
> (M = 0.30, SD = 0.35), F(1, 200) = 8.86, p = .003, d = 0.42.»
Т.е. идентичный совет (число 163 фунта) при ярлыке «алгоритм» получал WOA=45%, при ярлыке
«другие люди» — WOA=30%. Реальный вес был 164 фунта — совет был почти идеальным.

**Experiment 4 (выбор алгоритм vs другой участник vs собственная оценка), с. ~15, Fig. 2:**
> «The majority of participants chose to determine their bonus pay based on the algorithm's estimate rather
> than another participant's estimate (88%), χ2(1, N = 206) = 118.14, p < .001, r = 0.76... participants even
> chose the algorithm's estimate over their own estimate (66%), χ2(1, N = 197) = 20.15, p < .001, r = 0.32.»
Fig. 2 caption: «More than 50% of participants chose the algorithm in both conditions, ps < 0.001.»

**Experiment 2 (совместное vs раздельное предъявление советов), с. ~13:**
> «evaluating the two advisors jointly did not reverse the preference for algorithmic advice; 75% of
> participants in the joint condition also preferred the algorithm (N = 39) over the other participant.»

**Experiment 5 — КЛЮЧЕВОЙ КОНТРАСТ с алгоритм-аверсией: эксперты (нацбезопасность) vs миряне, с. ~19-20:**
> «Controlling for familiarity, we observed a main effect of advisor, F(1, 338) = 9.46, p = .002, η2 = 0.02,
> d = 0.29. As in earlier experiments, our participants placed more weight on algorithmic than human advice.
> Furthermore, experienced judges (the national security experts) took less advice than lay people, F(1, 338)
> = 32.39, p < .001, η2 = 0.08, d = 0.60. Importantly, we also observed a significant interaction between
> judge expertise and the source of advice: whereas lay judges placed more weight on algorithmic than
> human advice, the experts heavily discounted all advice sources, F(1, 338) = 5.05, p = .025, η2 = 0.01,
> d = 0.23.»
Т.е. эффект «algorithm appreciation» держится на МИРЯНАХ; опытные профессиональные прогнозисты
одинаково скептичны и к алгоритму, и к человеку — обесценивают ЛЮБОЙ внешний совет («heavily
discounted all advice sources»), что и вредит их точности («which hurt their accuracy» — abstract).

**Как определяли «алгоритм» для участников (с. ~10-11):** «we conceptualize an algorithm as a series of
mathematical calculations... 42% of responses fell into the first category» — большинство участников
самостоятельно дали определение, близкое к экспертному («procedure for computing a function», Rogers
1987), т.е. эффект не объясняется непониманием термина.

**Прямой методологический контраст с Dietvorst et al. (2015):** Logg et al. предъявляли «black box»-совет
БЕЗ демонстрации ошибок алгоритма на глазах участника («Updating to algorithmic advice without access
to its equations or processes»); Dietvorst et al. специально показывали ошибку алгоритма перед выбором.
Это прямо указывает на граничное условие: appreciation держится, пока участник не видел, как алгоритм
ошибается лично на его глазах — увидев ошибку, срабатывает aversion (Dietvorst 2015), не appreciation.

### 4. Доверие к робо-эдвайзеру vs человеку-консультанту — эмпирика с реальными данными и лабораторными числами

#### 4.1 Greig, Ramadorai, Rossi, Utkus, Walther (2023) «Algorithm Aversion: Theory and Evidence from Robo-Advice», рабочая версия апрель 2023 (Vanguard + Georgetown + Imperial College)

🟢 Источник открыт дословно. PDF: https://finance.unibocconi.eu/sites/default/files/files/media/attachments/paperramadorai20230418120509.pdf
(SSRN зеркало: https://ssrn.com/abstract=4301514). Извлечение через `pdftotext`. ЭТО РЕАЛЬНЫЕ ПОВЕДЕНЧЕСКИЕ
ДАННЫЕ (не лабораторный эксперимент): клиенты Vanguard Personal Advisor Services (PAS) — гибридный
робо-эдвайзинг, где портфель ведёт алгоритм, но клиент квазислучайно закреплён за человеком-советником
разного типа поддержки («high-retention» vs «low-retention» advisor).

**Abstract (дословно):**
> «We build a structural model of psychological "algorithm aversion," which features ongoing disutility of
> dealing with an algorithm, pessimism about the algorithm's ability, and uncertainty about the algorithm's
> performance; all three components can be assuaged by human interaction. We estimate model parameters
> using unique data from a "hybrid" robo-advising service in which portfolio management is automated, but
> clients are randomly matched with human advisors who provide different standards of support. Algorithm
> aversion is mainly driven by ongoing disutility and uncertainty, and human advice is especially important
> in retaining investors in robo-advice during market downturns.»

**Ключевые числа (с. 5, Introduction):**
> «our estimates are consistent with a model in which a high-retention human advisor removes over 90% of
> the effect of investors' prior about the expected returns generated by the algorithm.»
> «high-retention human advisors reduce clients' propensity to quit in benign market conditions by around
> 23%.»
> «Repeating our baseline empirical estimation in a sample of experienced clients, we find that high-retention
> human advisors still reduce the baseline propensity to quit by about 21%.»

**Аттриция и просадки рынка (с. 17-18):**
> «investors assigned to type-1 advisors are still with robo-advice [at 3 years]: 90.6%... The corresponding
> value for type-0 advisors is 86.8%.» (survival/удержание за 3 года)
> «those assigned to [high-retention] type-1 human advisors have a 25.4% lower hazard [of attrition] than
> those assigned to type-0 human advisors» (Cox proportional hazard).
> «attrition from robo-advising increases by 0.136 percentage points in poor market conditions, i.e., a
> 0.136/0.369=37% increase in attrition in such times» — то есть отток из робо-эдвайзинга на плохом рынке
> растёт на 37% относительно базовой ставки, и это именно тот момент, где человек-советник
> максимально снижает отток.
> Итоговый расчёт удержания: «mL = 0.369*12 = 4.43%» (годовая аттриция без сильной поддержки) против
> «mH = (0.369-0.086)*12 = 3.40%» (с сильной поддержкой) — «reduction by 1 − 3.4/4.43 = 23.25%».

**Практический вывод для финансовых RS:** человек «в контуре» не повышает точность алгоритма — он
снижает субъективную неопределённость и психологический дискомфорт пользователя («ongoing
disutility»), и это статистически измеримо влияет на удержание клиентов, ОСОБЕННО в кризис (просадка
рынка = момент максимального риска ухода пользователя от алгоритмической рекомендации).

#### 4.2 Niszczota & Kaszás (2020) «Robo-investment aversion», PLOS ONE 15(9):e0239277

🟢 Источник открыт дословно (open access). PDF:
https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0239277&type=printable.
DOI 10.1371/journal.pone.0239277. Извлечение через `pdftotext`. 5 экспериментов, N=3828 суммарно.

**Abstract/итог (с. 1, 20):**
> «In five experiments (N = 3,828), we investigate whether people prefer investment decisions to be made by
> human investment managers rather than algorithms... Computer algorithms run funds that account for 35%
> of the US stock market, and are responsible for 60% of the trading that happens on it.»
> «across five experiments (N = 3,828)—summarized in Table 2—we document a considerable robo-investment
> aversion (d = –0.39 [–0.45, –0.32] in internal meta-analysis).»

**Study 4, числа выбора человек vs алгоритм (с. ~17):**
> «Participants showed a preference for human advice, choosing them in 57.3% of cases, which was
> significantly different from 50% (χ2(1) = 16.0, p < .001). This is consistent with robo-investment aversion
> (d = –0.30).»
Разбивка по типу акций: «controversial stocks (human advice was preferred by 57.0% of participants) and
non-controversial stocks (human advice was preferred by 57.6% of participants; χ2(1) = 0.03, p = .87)» —
то есть моральная спорность актива НЕ усиливала аверсию в этом исследовании (вопреки исходной
гипотезе про ESG/моральные домены).

**Study 3 (иное направление — контрпример) (с. ~14):**
> «A similar proportion of participants chose human (48%) over algorithm (52%) advice» — при этом на
> спорных акциях «47.8% chose the algorithm» (d=-0.09, слабо), на неспорных «56.5% chose the algorithm»
> (d=0.26) — «showing a greater reliance on human [advice for controversial stocks]» — здесь моральная
> спорность актива ДЕЙСТВИТЕЛЬНО сдвигала выбор к человеку.

**Объединённый анализ Studies 4+5 (с. ~18):**
> «Overall, 47.0% of participants in these studies preferred the algorithm over humans, which is consistent
> with robo-investment aversion (χ2(1) = 4.42, p = .036). This aversion was not different across controversial
> and non-controversial stocks (χ2(1) = 1.95, p = .16).»

**Вывод авторов:** качественный анализ открытых ответов показал, что предпочитающие человека
объясняли выбор через «emotions» (N=19 упоминаний) и способность учитывать контекст, тогда как
предпочитающие алгоритм чаще ссылались на «bias»/«biases» как свойство человека (N=8) — то есть
ключевая ось решения — не мораль конкретно, а общее восприятие «эмоции vs предвзятость» для каждого
типа советника.

### 5. Влияние объяснения (XAI) на принятие финансового совета + human-in-the-loop

#### Ben David, Resheff, Tron (2021) «Explainable AI and Adoption of Financial Algorithmic Advisors: an Experimental Study», arXiv:2101.02555 (принято/цитируется как рабочая статья, veb-based game с реальными денежными ставками)

🟢 Источник открыт дословно. PDF: https://arxiv.org/pdf/2101.02555. Извлечение через `pdftotext`.

**Abstract (дословно):**
> «We study whether receiving advice from either a human or algorithmic advisor, accompanied by five types
> of Local and Global explanation labelings, has an effect on the readiness to adopt, willingness to pay, and
> trust in a financial AI consultant... We observed that accuracy-based explanations of the model in initial
> phases leads to higher adoption rates. When the performance of the model is immaculate, there is less
> importance associated with the kind of explanation for adoption. Using more elaborate feature-based or
> accuracy-based explanations helps substantially in reducing the adoption drop upon model failure.
> Furthermore, using an autopilot increases adoption significantly. Participants assigned to the AI-labeled
> advice with explanations were willing to pay more for the advice than the AI-labeled advice with a
> No-explanation alternative.»

**Метрика:** Readiness To Adopt (RTA) — «simply defined as the fraction» участников, принявших совет
советника в данный день (с. ~5).

**Ключевые числа по дням эксперимента (с. ~13-14):**
> «Figure 2 summarizes the overall adoption rate (RTA) for different experimental conditions. The overall
> model adoption changed... an average of 60% adoption when averaging over all participants.»
> «which the algorithmic performance was good, overall adoption increased leading to an average adoption
> of 85.5% on day 7. Following the model failure on day 7, adoption plummeted, returning approximately to
> the initial level with 61% on day 8, this was followed by a slow recovery up until day 10 (66%). With the
> introduction of [явное разъяснение по автопилоту], value of 94%. Finally, when participants were told
> advice will no [longer be given]... overall decrease in adoption on the final day (77%).»
> «the initial adoption of the Human Advisor (RTA of 56%) as opposed to... [algorithmic advisor without
> explanation, RTA of 57.7%]. However, over the first few days, the algorithmic advice with No Explanation
> showed significant gains in adoption as compared to the Human Advisor leading to a 16.3 percent gap on
> day 7 (P-value = 0.0129, t = 2.5114). However, following model failure on day 7, adoption and RTA levels
> fell back to around the initial values in both cases (54% and 56% for No explanation and Human Advisor,
> respectively).»
> «Using more elaborate feature-based or accuracy-based explanations helps substantially in reducing the
> adoption drop upon model failure... [recovery] not significantly more favorable for the AI-based advisor
> (65% compared to 58% by day 10).»

**Практический вывод:** и человек, и «безмолвный» алгоритм стартуют с почти одинакового уровня доверия
(RTA ~56-58%), алгоритм БЕЗ объяснений какое-то время обгоняет человека при хорошей работе (до +16.3
п.п.), но после первой заметной ошибки происходит резкое падение доверия («adoption plummeted») —
согласуется с Dietvorst et al. (2015): демонстрация ошибки алгоритма бьёт по доверию сильнее, чем
демонстрация ошибки человека. Объяснения (accuracy-based / feature-based) смягчают именно ЭТОТ провал
после ошибки, а не сам факт первичного принятия — перекликается с Dietvorst et al. (2018): не точность и
не объяснение как таковое решают дело, а инструмент, который помогает пользователю пережить
демонстрацию ошибки без полного отказа от системы.

---

## ВОПРОС B: вред и этика рекомендации финансовых действий

### 1-2. Регуляторный контур ответственности за совет: MiFID II suitability (ESMA Guidelines) — дословно

🟢 Источник открыт дословно, официальный документ ESMA. PDF:
https://www.esma.europa.eu/sites/default/files/2023-04/ESMA35-43-3172_Guidelines_on_certain_aspects_of_the_MiFID_II_suitability_requirements.pdf
(ESMA35-43-3172, дата документа 23.09.2022, опубликован 03.04.2023 — актуальная версия Guidelines on
certain aspects of the MiFID II suitability requirements, применяется к Article 25(2) MiFID II и Articles 54-55
MiFID II Delegated Regulation). Извлечение через `pdftotext`.

**Область применения (§2, с. 2):**
> «These guidelines apply in relation to Article 25(2) of MiFID II and Articles 54 and 55 of MiFID II Delegated
> Regulation and apply to the provision of the following investment services... investment advice; portfolio
> management.»

**Определение robo-advice — дословно из глоссария документа (с. 3):**
> «Robo-advice: The provision of investment advice or portfolio management services (in whole or in part)
> through an automated or semi-automated system used as a client-facing tool.»

**КЛЮЧЕВОЙ пункт для проектирования RS — ответственность НЕ передаётся клиенту (§14, с. 5):**
> «Firms should avoid stating, or giving the impression, that it is the client who decides on the suitability of
> the investment, or that it is the client who establishes which financial instruments fit his own risk profile.
> For example, firms should avoid indicating to the client that a certain financial instrument is the one that
> the client chose as being suitable, or requiring the client to confirm that an instrument or service is
> suitable.»

**Дисклеймеры не снимают ответственность (§15, с. 5):**
> «Any disclaimers (or other similar types of statements) aimed at limiting the firm's responsibility for the
> suitability assessment would not in any way impact the characterisation of the service provided in practice
> to clients nor the assessment of the firm's compliance to the corresponding requirements... firms should
> not claim that they do not assess the suitability.»
Прямое следствие для дизайна RS: формулировка «это не финансовый совет, решение за вами» юридически
не освобождает систему от ответственности за пригодность (suitability) рекомендации, если по факту
система выполняет функцию персональной рекомендации.

**Специфические требования к раскрытию информации именно для robo-advice (§17, с. 5-6):**
> «In order to address potential gaps in clients' understanding of the services provided through robo-advice,
> firms should inform clients, in addition to other required information, on the following: a very clear
> explanation of the exact degree and extent of human involvement and if and how the client can ask for
> human interaction; an explanation that the answers clients provide will have a direct impact in determining
> the suitability of the investment decisions recommended or undertaken on their behalf; a description of the
> sources of information used to generate an investment advice or to provide the portfolio management
> service (e.g., if an online questionnaire is used, firms should explain that the responses to the questionnaire
> may be the sole basis for the robo-advice or whether the firm has access to other client information or
> accounts)...»

**Требования к мониторингу и тестированию алгоритма suitability (§90, с. 26) — фактически технический
стандарт для RS в финансах:**
> «In order to ensure the consistency of the suitability assessment conducted through automated tools (even
> if the interaction with clients does not occur through automated systems), firms should regularly monitor
> and test the algorithms that underpin the suitability of the transactions recommended or undertaken on
> behalf of clients... firms should at least: establish an appropriate system-design documentation that clearly
> sets out the purpose, scope and design of the algorithms. Decision trees or decision rules should form part
> of this documentation, where relevant; have a documented test strategy that explains the scope of testing
> of algorithms... have in place appropriate policies and procedures for managing any changes to an
> algorithm, including monitoring and keeping records of any such changes... have in place policies and
> procedures enabling to detect any error within the algorithm and deal with it appropriately, including, for
> example, suspending the provision of advice if that error is likely to result in an unsuitable advice and/or a
> breach of relevant law/regulation; have in place adequate resources, including human and technological
> resources, to monitor and supervise the performance of algorithms through an adequate and timely review
> of the advice provided; and have in place an appropriate internal sign-off process to ensure that the steps
> above have been followed.»

Это прямое регуляторное требование к архитектуре RS в финансах (EU/MiFID II контур): версионирование
и документация правил, тестовый план с прогонами и результатами, процедура отслеживания изменений
алгоритма, детекция ошибок с возможностью ПРИОСТАНОВИТЬ выдачу совета, регулярный человеческий
надзор за производительностью. Прямо переносимо на архитектуру и changelog-дисциплину любой RS,
дающей персональные финансовые рекомендации.

### 2b. SEC Regulation Best Interest (Reg BI) — США, дословно с официальной страницы SEC

🟢 Источник открыт дословно через WebFetch (прямой доступ к sec.gov по curl заблокирован rate-limit'ом
403, r.jina.ai прокси заблокирован по репутации сети — оба задокументированы как «не открыт» ниже;
содержимое получено штатным WebFetch-инструментом с той же страницы sec.gov, что делает цитату
первичной, не пересказом). URL:
https://www.sec.gov/resources-small-businesses/small-business-compliance-guides/regulation-best-interest.
Принято 05.06.2019, вступило в силу 30.06.2020.

**Основной стандарт (дословно):**
> «act in the best interest of the retail customer at the time the recommendation is made, without placing
> your financial or other interest ahead of the retail customer's interests.»

**Четыре компонентных обязательства (дословно по разделам страницы SEC):**
1. Disclosure Obligation — раскрытие конфликтов интересов и характера отношений ДО или В МОМЕНТ
   рекомендации;
2. Care Obligation — «exercise reasonable diligence, care, and skill in making the recommendation»;
3. Conflict of Interest Obligation — письменные политики и процедуры по выявлению и устранению
   конфликтов интересов;
4. Compliance Obligation — письменные политики и процедуры, обеспечивающие соблюдение самого
   Reg BI.

Ключевое для дизайна RS: Reg BI явно НЕ требует единственной «лучшей» рекомендации из всех
возможных, но требует документируемого процесса заботы (Care) и раскрытия конфликтов ДО выдачи
рекомендации — то есть аудиторский след и timing раскрытия имеют такое же регуляторное значение,
как сама точность рекомендации.

### 2c. FCA (Великобритания): граница «совет vs guidance» — частично закрыто

🟡 Не дословно, реконструкция по сниппетам поисковой выдачи (WebFetch на
https://www.fca.org.uk/firms/advice-guidance-boundary-review не дал определения «personal recommendation» —
страница описывает только текущий Advice Guidance Boundary Review 2023+ и концепции «targeted support» /
«simplified advice», без цитаты первоисточника). По сниппетам поиска: граница проходит через понятие
«personal recommendation» — рекомендация по ценной бумаге/структурированному депозиту/релевантной
инвестиции, представленная как подходящая («suitable») для конкретного лица либо основанная на учёте
обстоятельств этого лица; всё, что не дотягивает до personal recommendation, регулируется как guidance
(более лёгкий режим). FCA опубликовала в августе 2023 разъясняющий документ с примерами границы.
Точная формулировка из FCA Handbook (COBS/PERG) НЕ открыта дословно в этом прогоне — источник не
проверен, цитировать нельзя. Если для проектирования RS нужна именно точная формулировка "personal
recommendation" из FCA Handbook — это отдельная задача добычи (PERG 8.28, COBS 9), не закрыта здесь.

### 3. Dark patterns / sludge в финансовых приложениях — регуляторное эмпирическое исследование

🟢 Источник открыт дословно. Ontario Securities Commission (OSC), «Digital Engagement Practices: Dark
Patterns in Retail Investing», research report, PDF:
https://www.osc.ca/sites/default/files/2024-02/inv-research_20240223_dark-patterns.pdf (публикация
23.02.2024). Извлечение через `pdftotext`. Это официальное регуляторное исследование (не академическая
статья) — environmental scan реальных торговых/инвестиционных приложений + обзор эмпирической
литературы по эффектам.

**Классификация (Contents, с. 2):** Dark Patterns (Prompts and reminders, Intermediate currency, Ranking,
Sensory manipulations, Social norms/interactions, Scarcity claims, Hidden fees/information) отдельно от
«Dark Nudges», «Sludge» и «Targeted Advertising» — четыре разных механизма вреда, не синонимы.

**Push-уведомления и объём торгов — дословно (с. ~13):**
> «a US trading platform sends push notifications... when the intraday return of a stock in their portfolio
> reaches +/- 5%. This type of push notification has been shown to increase the number of retail investor
> trades by approximately 25% in the minutes following a notification and to exacerbate the disposition
> effect... trades executed within 24 hours of receiving a push notification bore 19-percentage-point higher
> leverage. The impact was stronger for male, younger, and less experienced investors.»

**Ranking/списки лидеров и «herding» (стадный эффект) (с. ~14-15):**
> «These types of stock lists are also significantly associated with increased "herding" behaviour, where
> retail investor choices are positively correlated with each other... one study found an average 20-day
> abnormal return of -4.7% for top stocks purchased each day.»
Контрпример из другого исследования (важно для честности вывода): «a "Top Movers" list did not impact
investor returns» на данных двух немецких розничных банков, где инвесторы были в среднем 45 лет с 9
годами опыта — то есть эффект зависит от опыта/возраста аудитории продукта, не универсален.

**Скрытая экономика бонусных программ (referral bonus), пример sludge/dark pattern (с. ~44):**
> «one platform advertises a large bonus if a user refers their friends (up to several thousand dollars) - in
> reality, 99% of users will receive less than $50. This information is not mentioned in the offer but can be
> found if a user searches for it in the platform's help centre.»

**Sludge — определение через противопоставление dark pattern (с. ~44):** намеренное усложнение доступа
к информации о комиссиях («This additional step makes it difficult to access this information when a user
needs it, and qualifies as sludge») — в отличие от dark pattern, который активно подталкивает к действию,
sludge — это трение, мешающее защитному действию пользователя (посмотреть комиссию, отписаться,
вывести средства).

### 4. Chen, J. (2018) «Fair lending needs explainable models for responsible recommendation», Workshop on Responsible Recommendation (RecSys 2018 workshop), Vancouver

🟢 Источник открыт дословно. Автор — Jiahao Chen, Capital One. HTML-версия через ar5iv (зеркало arXiv):
https://ar5iv.labs.arxiv.org/html/1809.04684 (arXiv:1809.04684). Это ПРЯМОЕ попадание в тему: сама секция
конференции называется «Responsible Recommendation», и статья именно про RS в кредитовании.

**Тема/контекст (abstract, дословно):**
> «The financial services industry has unique explainability and fairness challenges arising from compliance
> and ethical considerations in credit decisioning. These challenges complicate the use of model machine
> learning and artificial intelligence methods in business decision processes.»

**Правовой контур США (перечислены дословно):** ECOA (Equal Credit Opportunity Act), FCRA (Fair Credit
Reporting Act), FACTA, FHA (Fair Housing Act), FEHA, CCPA (Consumer Credit Protection Act) — с таблицей
защищённых классов (age, color, disability, familial status, gender identity, marital status, national origin,
race, recipient of public assistance, religion, sex) по FHA и ECOA раздельно.

**Два теста дискриминации — определения дословно:**
> «disparate treatment: informally, intentionally treating people differently on the basis on a protected class,
> and disparate impact: informally, discriminating against any protected class as a resulting from
> implementing of a facially neutral policy.»

**Redlining через прокси-признаки — прямое предупреждение для фичей RS (дословно):**
> «a model for credit risk has to avoid features like zip code, which is highly correlated with race, a
> protected class. Using zip code in a model therefore runs the risk of redlining, the denial of services in
> neighborhoods populated mainly by racial minorities.»
> «Other variables that may be predictive of credit risk, such as length of credit history, correlate with age of
> customer, another prohibited class, and may require remediation in automated scoring systems.»
> «Even seemingly innocuous policies like a minimum principal amount for a loan may introduce bias against
> one or more protected classes.»

**Маркетинговые предложения кредита = юридически то же самое, что кредитное решение (важно для RS,
которая «просто рекомендует» продукт):**
> «marketing campaigns for credit have compliance considerations similar to credit decisioning models... each
> marketing offer to a prescreened customer is a firm offer of credit; all a customer needs to do is accept the
> offer to obtain credit» (FCRA). Т.е. рекомендация кредитного продукта юридически приравнивается к
> самому кредитному решению, а не к нейтральной подсказке — грань между «просто советуем» и «выдаём
> решение» в кредитном домене институционально стёрта.

**Adverse action notice — обязательное объяснение отказа (дословно):**
> «An adverse action notice is required by ECOA and FCRA if a customer is denied credit based on
> information in a credit report... such a notice must provide specific reasons for denying credit... AI/ML
> systems used to extend credit must also be able to provide the explanations necessary for adverse action.»

**Число, обосновывающее необходимость «отлаживаемости» модели (дословно):**
> «5% of Americans have errors in their credit reports that adversely affect their creditworthiness» (со ссылкой
> на Federal Trade Commission).

**Проблема измерения дискриминации без меток протестных классов:** «Credit card companies do not
generally collect information about an applicant's race, but may have a compliance need to demonstrate the
lack of disparate impact with regard to race. Regulators like the CFPB have published assessment
methodologies that describe the use of proxy models to impute race labels... However, the resulting
assessment seems to overestimate the amount of disparate impact.»

### 5. «Harm-aware recommendation» как термин RS-литературы — есть, но НЕ применительно к финансам

🟡 Не открыто дословно (проверены только сниппеты ACM DL/researchgate/academia.edu через WebSearch,
полный текст не зафетчен — бюджет исчерпан к этому пункту). Термин существует: workshop-серия «OHARS —
(Second) Workshop on Online Misinformation- and Harm-Aware Recommender Systems», co-located с ACM
RecSys в 2020 и 2021, DOI 10.1145/3383313.3411537 и 10.1145/3460231.3470941. По сниппету: «Harm-aware
recommender systems are designed to mitigate the negative effects of multiple forms of online harms...
fostering the recommendation of safe content and trustworthy users.»

**Важный вывод по объёму: предметная область OHARS — дезинформация, hate speech, вредоносный
контент в соцсетях, НЕ финансовые продукты.** Прямого пересечения «harm-aware recommendation» как
устоявшегося термина именно с финансовым доменом (кредиты, инвестпродукты) в этом прогоне НЕ
обнаружено — ближайшие по духу работы, реально закрывающие тему вреда в финансовых RS, идут не
под ярлыком «harm-aware», а под fairness-aware recommendation (см. п.4, Chen 2018) и под dark
patterns/sludge (см. п.3, OSC 2024). Это стоит явно зафиксировать как терминологический разрыв: индустрия
финансов регулирует вред через suitability/appropriateness и fair lending, а не через RS-специфичный термин
«harm-aware».

---

## Что не добыто и почему

1. **FCA Handbook точная формулировка «personal recommendation» (PERG 8.28 / COBS 9.2)** — НЕ открыта
   дословно. WebFetch на https://www.fca.org.uk/firms/advice-guidance-boundary-review вернул страницу без
   определения (только описание текущего Advice Guidance Boundary Review). Дальнейшая добыча (Handbook
   напрямую) не предпринята — бюджет.
2. **SEC.gov напрямую через curl** — HTTP 403 «Request Rate Threshold Exceeded» (автоматический доступ
   заблокирован anti-bot). Обойдено через штатный WebFetch-инструмент на ту же страницу — успешно,
   содержимое дословное.
3. **r.jina.ai прокси для sec.gov** — HTTP 401 «blocked from performing anonymous queries due to bad network
   reputation (AS9009)» — прокси не сработал в этот раз, в отличие от инструкции про MDPI (приём не
   универсален, зависит от репутации исходящего IP в моменте).
4. **DSpace UPenn `/download` эндпоинт** — отдаёт JS SPA-обвязку без содержимого (HTTP 200, но 827 байт
   HTML вместо PDF). Обойдено через прямой REST API `/server/api/core/bitstreams/<uuid>/content` — рабочий
   приём для институциональных DSpace-репозиториев, стоит занести в общий список приёмов очереди.
5. **opim.wharton.upenn.edu прямой PDF (2015 paper)** — curl упал с exit 6 (DNS resolution failure), URL
   недействителен/устарел. Заменено на репозиторий UPenn через Semantic Scholar `openAccessPdf` — сработало.
6. **Hodge, Mendoza, Sinha (2021) «The Effect of Humanizing Robo-Advisors on Investor Judgments», Contemporary
   Accounting Research 38(1):770-792** — НЕ открыт дословно. Semantic Scholar API дважды вернул HTTP 429
   (rate limit), полный текст не добыт; есть только пересказ из WebSearch-сниппета (см. текст ответа ниже,
   помечен 🟡, не вставлен в тело файла как дословная цитата, чтобы не смешивать с 🟢-материалом).
7. **«Harm-aware recommendation» + финансы напрямую** — не найдено пересечения (см. раздел 5 выше);
   это, вероятно, реальный терминологический пробел в литературе, а не недоработка поиска — подтверждено
   отсутствием совместных результатов по прямому запросу.
8. **openalex.org / semanticscholar.org API** — несколько запросов упали по rate-limit (429/"Rate limit exceeded")
   в процессе прогона; обойдено через WebSearch и прямые curl на издательские/авторские PDF.

## Незачтённый пересказ (🟡, вне выборки основного файла — для полноты)

**Hodge, Mendoza, Sinha (2021), Contemporary Accounting Research 38(1):770-792** — по сниппету WebSearch
(не по первоисточнику): исследование эффекта «очеловечивания» (присвоения имени) робо-эдвайзера на
суждения инвесторов. Находка по пересказу: инвесторы больше полагаются на рекомендацию БЕЗЫМЯННОГО
робо-эдвайзера, но больше полагаются на рекомендацию ИМЕНОВАННОГО человека-советника; именованному
робо-эдвайзеру доверяют МЕНЬШЕ на относительно сложных задачах и БОЛЬШЕ на простых. Это интересный
потенциальный контраргумент к общей идее «очеловечивания интерфейса RS повышает доверие» — эффект
зависит от воспринимаемой сложности задачи. Требует проверки по первоисточнику до использования как
факта.

