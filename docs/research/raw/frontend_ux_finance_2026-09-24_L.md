# Тема 42 — сырьё лида: п.2 объяснимость в интерфейсе, п.7 контур устройств

Снято 24.09.2026. Формат: дословная цитата → URL → дата.

## П.2. Объяснимость в интерфейсе (форма объяснения, доверие, решение)

### 2.1. Herlocker, Konstan, Riedl. «Explaining Collaborative Filtering Recommendations», CSCW '00, Philadelphia, pp. 241–250

Источник: https://grouplens.org/site-content/uploads/explain-CSCW-20001.pdf (PDF добыт `curl` с браузерным UA, HTTP 200, 373 754 байта; разобран `pdftotext`), снято 24.09.2026.
🔴 Это первоисточник всей линии «объяснение рекомендации в интерфейсе» — в нём измерено, КАКАЯ ФОРМА объяснения сильнее меняет готовность принять рекомендацию.

Почему тема вообще важна именно для денег (дословно):

> «While automated collaborative filtering systems have proven to be accurate enough for entertainment domains[6,9,12,13], they have yet to be successful in content domains where higher risk is associated with accepting a filtering recommendation. While a user may be willing to risk purchasing a music CD based on the recommendation of an ACF system, he will probably not risk choosing a honeymoon vacation spot or a mutual fund based on such a recommendation.»

> «ACF systems today are black boxes, computerized oracles that give advice, but cannot be questioned. A user is given no indicators to consult to determine when to trust a recommendation and when to doubt one. These problems have prevented acceptance of ACF systems in all but the low-risk content domains.»

Четыре заявленные функции объяснения (дословно): «(1) Justification… (2) User Involvement… (3) Education… (4) Acceptance. Greater acceptance of the recommender system as a decision aide, since its limits and strengths are fully visible and its suggestions are justified.»

**Эксперимент 1. Дизайн.** 78 пользователей MovieLens, randomized block design (блок — пользователь, воздействие — интерфейс объяснения), 21 разный интерфейс объяснения на ОДНУ И ТУ ЖЕ рекомендацию, порядок рандомизирован. Вопрос — «насколько вероятно, что вы пойдёте на этот фильм», шкала 1–7. Сценарий задан дословно:

> «Imagine that you have $7 and a free evening coming up. You are considering going to the theater to see a movie, but only if there is a movie worth seeing. To determine if there is a movie worth seeing, you consult MovieLens for a personalized movie recommendation. MovieLens recommends one movie, and provides some justification.»

**Таблица 1 (дословные числа: N, среднее, ст. откл.). База — строки 11 и 12 (объяснения нет).**

| # | Интерфейс объяснения | N | Mean | SD |
|---|---|---|---|---|
| 1 | Histogram with grouping | 76 | **5.25** | 1.29 |
| 2 | Past performance | 77 | **5.19** | 1.16 |
| 3 | Neighbor ratings histogram | 78 | **5.09** | 1.22 |
| 4 | Table of neighbors ratings | 78 | 4.97 | 1.29 |
| 5 | Similarity to other movies rated | 77 | 4.97 | 1.50 |
| 6 | Favorite actor or actress | 76 | 4.92 | 1.73 |
| 7 | MovieLens percent confidence in prediction | 77 | 4.71 | 1.02 |
| 8 | Won awards | 76 | 4.67 | 1.49 |
| 9 | Detailed process description | 77 | 4.64 | 1.40 |
| 10 | # neighbors | 75 | 4.60 | 1.29 |
| 11 | **No extra data – focus on system (БАЗА)** | 75 | 4.53 | 1.20 |
| 12 | **No extra data – focus on users (БАЗА)** | 78 | 4.51 | 1.35 |
| 13 | MovieLens confidence in prediction | 77 | 4.51 | 1.20 |
| 14 | Good profile | 77 | 4.45 | 1.53 |
| 15 | Overall percent rated 4+ | 75 | 4.37 | 1.26 |
| 16 | Complex graph: count, ratings, similarity | 74 | 4.36 | 1.47 |
| 17 | Recommended by movie critics | 76 | 4.21 | 1.47 |
| 18 | Rating and %agreement of closest neighbor | 77 | 4.21 | 1.20 |
| 19 | # neighbors with std. deviation | 78 | 4.19 | 1.45 |
| 20 | # neighbors with avg correlation | 76 | 4.08 | 1.46 |
| 21 | Overall average rating | 77 | **3.94** | 1.22 |

Подпись таблицы дословно: «Mean response of users to each explanation interface, based on a scale of one to seven. Explanations 11 and 12 represent the base case of no additional information. Shaded rows indicate explanations with a mean response significantly different from the base cases (two-tailed α = 0.05).»

🔴 **Главный вывод для нас, дословно:**

> «Some explanations (18–21) had significantly lower mean response than the base cases. **Poorly designed explanations can actually decrease the effectiveness of a recommender system.** This stresses the importance of good design of explanations interfaces.»

Почему победила именно простая гистограмма (дословно):

> «Explanation 1 performed better than a basic bar chart because it reduced the dimensionality of the data to a point where only one binary comparison is necessary (the good versus the bad). The hypothesis that simple graphs are more compelling is supported by observing the poor performance of Explanation 16, which presents a superset of the data shown in histograms, adding information about how close each neighbor is to the user.»

Подпись к рисунку 2 (победивший интерфейс) дословно: «A histogram of neighbors' ratings for the recommended item, with the "good" ratings clustered together and the "bad" ratings clustered together, and the ambivalent ratings separated out. The result is that the user has to do only a single binary visual comparison to understand the consequence of the explanation. This was the best performing explanation.»

Про «прошлую точность системы» как форму объяснения (2-е место, 5.19):

> «Stating positive past performance of the ACF system was just compelling as demonstrating the ratings evidence behind the recommender. The exact explanation was "MovieLens has predicted correctly for you 80% of the time in the past."… While this form of explanation is useful for setting the context, it is not valuable for distinguishing between different recommendations from the same system.»

🔴 **Прямой урок про показ статистических метрик пользователю (важно для нашего SAW-веса и корреляций):**

> «Yet explaining similarity is tricky, since the statistical similarity metrics that have been demonstrated as the most accurate such as correlation[5] are hard to understand for the average user. For example, in the recommendation explained in this study the average correlation was 0.4, which we recognize from experience as being very strong for movie rating data. However, users are not aware that correlations greater than 0.4 are rare; **they perceive 0.4 to be less than half on the scale of 0 to 1. This highlights the need to recode the similarity metric into a scale is perceptually balanced.** In this specific case, we might recode the correlations into three classes: good, average, and weak.»

**Эксперимент 2. Принятие и качество решений.** 210 пользователей, 743 мини-анкеты, месяц.

> «210 users participated in this study, filling out 743 mini-surveys. In 315 of those mini-surveys, users consulted MovieLens before seeing the movie. In 257 of those mini-surveys, MovieLens had some effect on the user's decision to see the movie. In 213 (83%) of the cases where MovieLens had an effect on the decision, the MovieLens recommendation was not the sole reason for choosing a movie.»

> «Figure 5 shows the filtering performance of each experimental group. **There was no statistically significant difference between any two experimental groups** (based on a one-way ANOVA with α = 0.05).»

> «97 experimental subjects filled out the exit survey. **86% of these users said that they would like to see their explanation interface added to the system.**»

🔴 **Расхождение внутри самой статьи, его нельзя сглаживать:** объяснение достоверно повышает ЖЕЛАНИЕ принять рекомендацию (эксп. 1) и нравится 86% (эксп. 2), но КАЧЕСТВО решений в эксп. 2 статистически не улучшило. То есть объяснение — инструмент доверия и принятия, а доказательства, что оно делает решения лучше, в первоисточнике НЕТ.

### 2.2. Zhang, Liao, Bellamy. «Effect of Confidence and Explanation on Accuracy and Trust Calibration in AI-Assisted Decision Making», ACM FAT* '20, Barcelona, DOI 10.1145/3351095.3372852

Источник: https://arxiv.org/abs/2001.02114 (метаданные) и PDF https://arxiv.org/pdf/2001.02114 (`curl` с браузерным UA, HTTP 200, 671 555 байт, разобран `pdftotext`), снято 24.09.2026.
Задача — доход выше/ниже $50K по данным Adult; человек и модель сопоставимы по силе, как у нас (пользователь про свою жизнь знает больше модели).

Аннотация дословно:

> «Through two human experiments, we show that **confidence score can help calibrate people's trust in an AI model, but trust calibration alone is not sufficient to improve AI-assisted decision making**, which may also depend on whether the human can bring in enough unique knowledge to complement the AI's errors. We also highlight the problems in using local explanation for AI-assisted decision making scenarios and invite the research community to explore new approaches to explainability for calibrating human trust in AI.»

**Эксперимент 1 — показ «уверенности модели» (confidence score).** Метрика «switch percentage» — доля проб, где человек заменил своё предсказание на предсказание ИИ.

> «A four factor ANOVA, confidence × prediction × model … effect of showing confidence scores was significant, F (1, 64) = 4.64…»

> «This calibration of trust was confirmed by a statistically significant interaction between showing confidence and the AI's confidence level, **F (4, 256) = 15.8, p < .001**.»

> «The calibration effect of confidence score on the agreement percentage, as indicated by the interaction between confidence and confidence levels, was significant, **F (4, 256) = 3.82, p = .005**. … **H1 was thus fully supported.**»

Точности, дословно: «On average, the participants' own accuracy was **65%**, with only 14 of 72 participants under 60%, while the AI accuracy was **75%**…»

🔴 Но на КАЧЕСТВО решения показ уверенности не повлиял:

> «The fact that showing confidence improved trust and trust calibration but **failed to improve the AI-assisted accuracy is puzzling, and it rejects our H2**. This phenomenon could be explained by the correlation between model decision uncertainty and human decision uncertainty, because trials where the model prediction had low confidence were also more challenging for humans.»

**Эксперимент 2 — локальное объяснение (вклад каждого атрибута, метод Шепли).** Это ровно та форма, которую естественно применить к нашей SAW-агрегации («вклад критерия»).

> «We developed a visual explanation feature like the one in Figure 7. This visualization explains a particular model prediction by **how each attribute contributes to the model's prediction**. The contribution values were generated using a state-of-the-art local explanation technique called Shapley method [19].»

🔴 Результат — **отрицательный**:

> «A Tukey's honestly significant difference (HSD) post-hoc test showed that the switch percentage in the confidence condition was significantly higher than those in the baseline condition (p=.011) and the explanation condition (p < .001), but **the explanation condition was not significantly different from the baseline (p = .66)**. … **H3 was rejected** as we found no evidence that showing explanation was more effective in trust calibration than the baseline.»

> «Similar to Experiment 1, we did not [find an effect] … F (2, 24) = 0.810, p = .457. **If anything, there was a reverse trend of decreasing the AI-assisted accuracy by showing explanation. H4 was thus also rejected.**»

> «Taken together, the results suggest **a lack of effect of local explanations on improving trust calibration and AI-assisted prediction**.»

Их же разбор противоречия с Lai & Tan — почему «объяснения помогают» в других работах:

> «But a closer look at Lai and Tan's results revealed a trend of **indiscriminatory increase in trust (willingness to accept) whether the AI made correct or incorrect predictions**, suggesting similar conclusion that explanations are ineffective for trust calibration. However, since in their study the AI outperformed human by a large margin, this indiscriminatory increase in trust improved the overall decision outcome.»

**Что это значит для FINPILOT (вывод вахты, не цитата):** показ «уверенности» рекомендации откалибровывает доверие ЧИСЛЕННО доказанно; водопад вкладов критериев в стиле Шепли — нет. Из двух форм объяснения приоритет у «насколько модель уверена именно в этом случае», а не у разложения по критериям. Разложение оставлять как раскрытие по клику, не на первом экране.

### 2.3. Poursabzi-Sangdeh, Goldstein, Hofman, Wortman Vaughan, Wallach. «Manipulating and Measuring Model Interpretability», CHI 2021 (arXiv:1802.07810)

Источник: https://arxiv.org/abs/1802.07810 (страница arXiv, `curl` с браузерным UA, HTTP 200), снято 24.09.2026. Предметная область — предсказание цены квартиры, то есть числовой прогноз про деньги.

Дословно из аннотации:

> «We present a sequence of pre-registered experiments (**N=3,800**) in which we showed participants functionally identical models that varied only in two factors commonly thought to make machine learning models more or less interpretable: the number of features and the transparency of the model (i.e., whether the model internals are clear or black box). Predictably, participants who saw a clear model with few features could better simulate the model's predictions. **However, we did not find that participants more closely followed its predictions. Furthermore, showing participants a clear model meant that they were less able to detect and correct for the model's sizable mistakes, seemingly due to information overload.** These counterintuitive findings emphasize the importance of testing over intuition when developing interpretable models.»

🔴 Прямое следствие для нас: «показать всю кухню модели» не только не повышает следование рекомендации, но и УХУДШАЕТ способность человека заметить, что модель ошиблась. Полное раскрытие формулы на первом экране — измеренный вред, а не нейтральное благо.

---

## П.7. Мобильный и десктопный контур — проверка нашего desktop-first

### 7.1. StatCounter Global Stats: доля платформ в РФ (веб-просмотры)

Источник: https://gs.statcounter.com/platform-market-share/desktop-mobile-tablet/russian-federation — снято 24.09.2026 через текстовый прокси `r.jina.ai` (WebFetch и `curl` отдавали страницу без отрендеренных чисел).

Дословно с таблицы страницы:

> «Desktop vs Mobile vs Tablet Market Share in Russian Federation - August 2026 | Desktop **74.88%** | Mobile **24.5%** | Tablet **0.62%**»

Ряд за 13 месяцев (CSV с самого StatCounter, `curl` с браузерным UA, HTTP 200; ссылка на выгрузку взята со страницы, `statType_hidden=comparison`):

```
"Date","Desktop","Mobile","Tablet"
2025-08,62.1,36.56,1.34
2025-09,55.24,43.61,1.15
2025-10,60.38,38.53,1.09
2025-11,68.02,30.79,1.19
2025-12,68.16,30.81,1.03
2026-01,69.63,29.43,0.94
2026-02,72.85,25.88,1.27
2026-03,73.07,25.61,1.32
2026-04,76.96,22.04,1
2026-05,79.05,20,0.95
2026-06,76.78,22.27,0.95
2026-07,73,26.15,0.85
2026-08,74.82,24.56,0.62
```
— источник: https://gs.statcounter.com/platform-market-share/desktop-mobile-tablet/chart.php?...&region_hidden=RU&statType_hidden=comparison&csv=1 , снято 24.09.2026.

Для контраста, мир за тот же август 2026 (та же методика, та же страница без региона):

> «Desktop vs Mobile vs Tablet Market Share Worldwide - August 2026 | Mobile **49.36%** | Desktop **49.11%** | Tablet **1.54%**»
— источник: https://gs.statcounter.com/platform-market-share/desktop-mobile-tablet , снято 24.09.2026.

🔴 **Оговорка о методике, без неё число врёт (вывод вахты, не цитата):** StatCounter считает просмотры ВЕБ-страниц с трекерами, а не время в приложениях. В РФ основные финансовые интерфейсы (Т-Банк, Сбер, ВТБ) — нативные мобильные приложения, их трафик в этот срез не попадает вовсе. Поэтому число 74,88% корректно читать как «в российском ВЕБЕ десктоп доминирует и за год его доля выросла с 62,1% до 74,8%», а не как «россияне не пользуются телефоном». Для FINPILOT, который запускается как ВЕБ-SPA, релевантен именно веб-срез — и он desktop-first подтверждает.

### 7.2. Nielsen Norman Group: комплексность контента и устройство (измерение, 1 629 наблюдений)

Источник: https://www.nngroup.com/articles/mobile-content-is-twice-as-difficult/ («Reading Content on Mobile Devices», опубликовано 11.12.2016), снято 24.09.2026 через `r.jina.ai`.

Объём: «10-participant online pilot · 30-participant online study · 40-participant in-person study · 206-participant online study», анализ — «This analysis included **1,629 cases** where a user read an article and completed the comprehension quiz for that article.»

> «Although **the effect of device was statistically significant (at p = 0.0006), the difference in comprehension scores was not practically significant**: comprehension on mobile was about **3 percentage points higher** than on a computer, with a 95% confidence interval of 1% to 5%.»

> «Our repeated-measures ANOVA yielded a significant interaction of device and difficulty (p =0.01). **Easy passages were read about as fast on both devices, but hard passages actually took longer on mobile versus computer.** (On average, participants spent about **30 milliseconds more on each word** when reading on mobile than on a computer.)»

> «In other words, **they could not sustain the higher working-memory load**… In psychology, this phenomenon is referred to as a **speed–accuracy tradeoff** — users had to slow down to achieve the same level of comprehension for difficult articles on a phone as they did on a computer.»

> «This suggests that, while reading comprehension may be comparable on a phone and a computer for easy articles, **reading on mobile becomes more difficult as the complexity of the content increases**.»

🔴 Ключевое ограничение их же вывода, дословно — и оно прямо про нас:

> «First, we know that, in general, **task performance on mobile devices is still lower** than desktops or laptops. We measured reading comprehension in this study, but most web tasks involve much more than reading. **Articles are linear content** — they don't reflect all web content or online tasks. Most online activities involve some degree of navigation and interaction. Ecommerce and other web tasks require substantial navigation and comparisons between multiple pieces of content.»

**Приложение к FINPILOT (вывод вахты):** наш первый экран — не линейный текст, а сравнение альтернатив распределения (66 вариантов, шаг 10%) с обоснованием и прогнозом. Это ровно тот класс «navigation + comparisons between multiple pieces of content», для которого NN/g фиксирует худшее исполнение на мобильном. Плюс нашли marginal-эффект: «very difficult content is harder to read on a phone than on a computer». Итого desktop-first для экрана решения обоснован замером, а не вкусом. Мобильный контур разумен для чтения ИТОГА (одно предписание, одна сумма), но не для разбора альтернатив.
