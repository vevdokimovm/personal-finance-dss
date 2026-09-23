# Г62 — Подробное индивидуальное объяснение совета текстом без LLM — сырьё

Дата: 2026-09-19. Исполнитель: lead research agent (одна сессия, подагентов 0–1).
Правило: дописывается после каждого вызова инструмента.

## Журнал вызовов

1. Создан файл-сырьё.
2. Прочитана постановка `queue/prompts/g62_prompt.md` и раздел Г62 в GAP_QUEUE (стр. 3733–3781).
   Строки Г62 в сводной таблице GAP_QUEUE НЕТ (последняя — Г61, стр. 62) — добавить при закрытии.
3. Канон `docs/math_model.md` — версия **3.9.0** (не 3.0.0, как в глобальных инструкциях). Ключевое для объяснений:
   - §7: min-max нормализация В РАМКАХ текущего множества A; при max=min — «константа для всех».
     Для D в свёртку идёт (1 − D̂). Для L — насыщение L^sat = min(L, L*(u)).
   - §8: U(a) = w_R R̂ + w_L L̂ + w_D (1−D̂) + w_S Ŝ. 🔴 Выбор ЛЕКСИКОГРАФИЧЕСКИЙ:
     a* = argmax (min(L(a), F), U(a)); F = 2 мес / 1 мес при токсичном долге (ставка ≥ max(30 %, r_bench+15 п.п.)) /
     2 + min(1, max(0, CV−0,3)) при волатильном доходе. То есть «почему А» — НЕ всегда разложение U:
     первым решает уровень floor, SAW — только среди floor-равных.
   - §6: жёсткие R(a) ≥ 0 и D(a) ≤ max(0,40; D_t) («план не увеличивает ПДН»); при D_t > 0,40 — флаг Dt_alert + нота рефинансирования.
   - §9: веса 5 профилей (0,20/0,45/0,25/0,10 … 0,35/0,10/0,15/0,40), L* = 6/5/4,5/3,5/3 мес.
   - §10: r_bench = key·0,87 (фолбэк 0,14); O_target = {r_k ≥ r_bench}; каскад долг → цели → резерв; x_obl_unused, x_goals_unused.
   - §11: веса категорий целей 3/2/1/0,5, срочность u_s = max(1, 12/τ), индексация 4 % для τ > 36.
   - §12: кризисный режим R_t < 0 — план из 4 ходов, runway, severity, summary «без формул» (FR-01/UX-02).
   - §13–14: инвест-транш (полка по профилю 0/20/40/60/80 % акций), ноты АСВ 1,4 млн и ИИС; слой излишка.
   - §15: SES α=0,3 + MC N=1000, σ(h)=σ0·√(1+0,5h), выход — медиана и CI 80 % [Q10; Q90], h=3 мес.
4. Код текстового слоя, который УЖЕ есть (`app/core/recommendation.py`, 370 строк; `app/core/ranking.py`):
   - `build_recommendation_text` (диагноз), `explain_alternative` → gains / costs / insight / dominant_criterion / counterfactual / delta.
   - `ranking.py:194` пишет `weighted_scores` = w·x_norm; `normalize_value` при max == min возвращает **1.0**.
   - `_dominant_criterion` = argmax АБСОЛЮТНОГО вклада победителя (не контрастного).
   - `_counterfactual` = разность вкладов с СЛЕДУЮЩИМ в отсортированном по (floor_level, utility) списке.
   Гипотезы о неверности (проверю синтетикой):
   Г-а: у пользователя без долга критерий D константен → вклад w_D·1 = 0,25 у ВСЕХ альтернатив → «решающим оказалось
        снижение долговой нагрузки» у человека без долга.
   Г-б: если победитель выигрывает по floor, utility следующего может быть ВЫШЕ → «отстаёт на N баллов» ложно.
   Г-в: `build_recommendation_text` пишет «безопасный минимум — 3 месяца», а канон: floor 2 мес, L* 3–6 по профилю —
        число не из расчёта.
5. 🔴 ЗАМЕР на реальном конвейере `app.services.planning.run_planning` (скрипт в scratchpad `g62_probe.py`, синтетика, код НЕ правился).
   **Случай A** — без долга, доход 120 000, расходы 80 000, подушка 60 000, цель «Отпуск», профиль 3:
   все три топ-варианта имеют ws Rt = 0,25 и Dt = 0,25 (критерии константны, `normalize_value` → 1,0).
   Вариант #2: `dominant_criterion = Rt` → текст «Решающим для оценки оказалось то, сколько свободных денег остаётся
   каждый месяц» — у человека, у которого этот показатель одинаков во всех вариантах. **Г-а подтверждена.**
   Победитель выбран floor-уровнем (1,25 против 1,20 мес), а текст: «оптимальный баланс для профиля „Сбалансированный“».
   **Случай B** — кредитка 35 % (токсичная → floor 1 мес), подушка 20 000, расходы 70 000, профиль 5 «Агрессивный»:
   победитель a0100 (100 % в резерв) U = **0,10**; второй a190 U = **0,1399** — по SAW второй ЛУЧШЕ, победил floor
   (0,857 против 0,80). Текст победителя: «Следующий по оценке вариант отстаёт примерно на 4 из 100 баллов» (знак неверен)
   и «этот набрал наивысшую оценку» (неверно). **Г-б подтверждена.**
   **Счёт по сетке** 162 синтетических портретов (доход × расходы × подушка × ставка × платёж × профиль, один кредит + одна цель):
   у **47 из 162 (29 %)** контрфактуал победителя имеет ОТРИЦАТЕЛЬНЫЙ utility_gap, то есть текст «отстаёт на N баллов» ложен.
   Пример: доход 90 000, расходы 60 000, подушка 0, кредит 12 %, профиль 5: U победителя 0,60, второго 0,6298, floor 0,4167 vs 0,375.
   **Случай C** — дешёвая ипотека 6 %, без целей, подушка 700 000 (7 мес > L* 4,5): все варианты U = 1,0 (все критерии константны),
   топ схлопнулся в 1 вариант, текст «набрал наивысшую оценку… решающим — рост подушки», хотя никакой критерий не различал варианты.
   Вывод для спецификации: (1) вклад считать КОНТРАСТНО Δⱼ = wⱼ(r̂ⱼ(a*) − r̂ⱼ(b)), константные критерии (max = min) исключать
   из прозы; (2) первым проверять, ЧЕМ решён выбор — floor-уровнем или SAW — и писать разный текст; (3) при полной ничьей —
   честный блок «варианты равноценны, выбран по правилу X».
6. **Regulation B, 12 CFR 1002.9 + Official Interpretation (Supplement I)** — eCFR versioner API,
   `https://www.ecfr.gov/api/versioner/v1/full/2026-08-01/title-12.xml?part=1002`, HTTP 200, 109 391 B (сжатие обязательно:
   без `--compressed` — 406 «This endpoint requires response compression»; первая попытка renderer API — 302). Дословно:
   > §1002.9(b)(2) «Statement of specific reasons. The statement of reasons for adverse action required by paragraph (a)(2)(i)
   > of this section must be specific and indicate the principal reason(s) for the adverse action. Statements that the adverse
   > action was based on the creditor's internal standards or policies or that the applicant… failed to achieve a qualifying
   > score on the creditor's credit scoring system are insufficient.»
   Комментарии к Paragraph 9(b)(2):
   > «1. Number of specific reasons. … The regulation does not mandate that a specific number of reasons be disclosed, but
   > disclosure of more than four reasons is not likely to be helpful to the applicant.»
   > «2. Source of specific reasons. The specific reasons disclosed … must relate to and accurately describe the factors
   > actually considered or scored by a creditor.»
   > «4. Credit scoring system. … the reasons disclosed must relate only to those factors actually scored in the system.
   > Moreover, no factor that was a principal reason for adverse action may be excluded from disclosure.»
   > «5. Credit scoring — method for selecting reasons. … One method is to identify the factors for which the applicant's score
   > fell furthest below the average score for each of those factors achieved by applicants whose total score was at or slightly
   > above the minimum passing score. Another method is to identify the factors for which the applicant's score fell furthest
   > below the average score for each of those factors achieved by all applicants. … Any other method that produces results
   > substantially similar to either of these methods is also acceptable.»
   > «7. Combined credit scoring and judgmental system. … the reasons for the denial must come from the component of the system
   > that the applicant failed. … If the application passes the credit scoring stage but the creditor then denies … based on a
   > judgmental assessment …, the reasons disclosed must relate to the factors reviewed judgmentally, even if the factors were
   > also considered in the credit scoring component. … disclosure of more than a combined total of four reasons is not likely
   > to be helpful.»
   > «8. Automatic denial. … When a creditor denies the credit request because of an automatic-denial factor, the creditor must
   > disclose that specific factor.»
   **Перенос на нас (решение вахты):** (к.2/4) причина = только фактор, реально вошедший в расчёт → ни одного числа не из расчёта
   (Г-в «3 месяца» нарушает); (к.5) отбор причин — КОНТРАСТОМ против эталона (у нас эталон = второе место или «средний по A»),
   а не абсолютной величиной вклада → ровно дефект Г-а; (к.7) причина берётся из ТОЙ СТУПЕНИ, которая решила: floor-ступень или
   SAW-ступень → ровно дефект Г-б; (к.8) жёсткие инварианты (R ≥ 0, ПДН, Avalanche-отсев) называются как «автоматический» фактор;
   (к.1) не больше 4 причин.
7. **CFPB Circular 2022-03** «Adverse action notification requirements in connection with credit decisions based on complex
   algorithms» — curl с браузерным UA **403** → `r.jina.ai` **200, 15 224 B**. Пометки «Archived» на странице нет. Дословно:
   > «Question: When creditors make credit decisions based on complex algorithms that prevent creditors from accurately identifying
   > the specific reasons for denying credit…, do these creditors need to comply with the … requirement to provide a statement of
   > specific reasons…? — Yes. … The adverse action notice requirements of ECOA and Regulation B, however, apply equally to all credit
   > decisions, regardless of the technology used to make them. Thus, ECOA and Regulation B do not permit creditors to use complex
   > algorithms when doing so means they cannot provide the specific [and accurate reasons]…»
   **CFPB Circular 2023-03** (про образцы-чеклисты причин): curl 403 → r.jina.ai 200, 10 768 B, но это страница-заглушка
   «**Archived content** … Content has been archived … Page last modified Apr. 11, 2025» → Exa fetch — та же заглушка →
   архив `wayback.archive-it.org/23481/20250327014847/...` — 200, 4 430 B, текста нет (JS-оболочка). 4 попытки, лимит.
   🟢 Не пройден браузер. Статус документа: **снят в архив CFPB в 2025 г.** — цитировать как действующую позицию нельзя;
   для спецификации он не нужен: норма «причины должны отражать фактические факторы» стоит в самом Official Interpretation
   (к. 9(b)(2)-2 и -4, п. 6 выше), это первоисточник уровнем выше.
8. **152-ФЗ ст. 16** — `consultant.ru/document/cons_doc_LAW_61801/22e884a41450dcb5cb62d956583ad32abe2bbbe9/`, `curl -sk --http1.1` +
   браузерный UA, **200, 46 783 B**. Редакция на дату: «Федеральный закон от 27.07.2006 N 152-ФЗ (ред. от 26.07.2026)»; помета
   «Подготовлена редакция документа с изменениями, не вступившими в силу». Текст статьи дословно:
   > «Статья 16. Права субъектов персональных данных при принятии решений на основании исключительно автоматизированной обработки
   > их персональных данных
   > 1. Запрещается принятие на основании исключительно автоматизированной обработки персональных данных решений, порождающих
   > юридические последствия в отношении субъекта персональных данных или иным образом затрагивающих его права и законные интересы,
   > за исключением случаев, предусмотренных частью 2 настоящей статьи.
   > 2. Решение, порождающее юридические последствия в отношении субъекта персональных данных или иным образом затрагивающее его
   > права и законные интересы, может быть принято на основании исключительно автоматизированной обработки его персональных данных
   > только при наличии согласия в письменной форме субъекта персональных данных или в случаях, предусмотренных федеральными законами,
   > устанавливающими также меры по обеспечению соблюдения прав и законных интересов субъекта персональных данных.
   > 3. Оператор обязан разъяснить субъекту персональных данных порядок принятия решения на основании исключительно автоматизированной
   > обработки его персональных данных и возможные юридические последствия такого решения, предоставить возможность заявить
   > возражение против такого решения, а также разъяснить порядок защиты субъектом персональных данных своих прав и законных интересов.
   > 4. Оператор обязан рассмотреть возражение, указанное в части 3 настоящей статьи, в течение тридцати дней со дня его получения и
   > уведомить субъекта персональных данных о результатах рассмотрения такого возражения.
   > (в ред. Федерального закона от 25.07.2011 N 261-ФЗ)»
   Текст ст. 16 не менялся с 2011 г. (последняя правка — 261-ФЗ).
9. **243-ФЗ от 26.07.2026 «О поддержке развития технологий искусственного интеллекта в Российской Федерации»** — ПЕРВОИСТОЧНИК ДОБЫТ.
   Официальное опубликование: `publication.pravo.gov.ru/document/0001202607260003` (Exa-поиск, дата опубликования 26.07.2026).
   Каналы: consultant.ru `cons_doc_LAW_540336` через `curl -sk --http1.1` — 200, 37 228 B, но только оглавление (полный текст
   за кнопкой «Открыть полный текст»); полный текст — Exa fetch `lawnotes.ru/laws/federalnyy-zakon-ot-26.07.2026-n-243-fz`
   (перепечатка КонсультантПлюс; совпадает с фрагментами garant.ru `base.garant.ru/414652934/` и spinform в выдаче Exa).
   Принят ГД 08.07.2026, одобрен СФ 17.07.2026. Дословно значимое:
   > Ст. 1 ч. 1: «Настоящий Федеральный закон регулирует отношения в сфере разработки, внедрения и применения **больших
   > фундаментальных моделей** искусственного интеллекта.»
   > Ст. 3 п. 1: «искусственный интеллект - комплекс технологических решений, позволяющий имитировать когнитивные функции человека
   > (включая способность самостоятельно совершенствовать свои функции, повышать точность решений за счет анализа новых данных и
   > выполнять поиск решений **без заранее заданного алгоритма**) и получать при выполнении конкретных задач результаты, сопоставимые
   > с результатами интеллектуальной деятельности человека или превосходящие их…»
   > Ст. 3 п. 2: «большая фундаментальная модель искусственного интеллекта - программа для ЭВМ…, использующая алгоритмы и
   > обучающаяся (ранее обученная) на составах данных…, содержащая **не менее 1 миллиарда параметров** и применяемая для выполнения
   > большого количества различных задач;»
   > Ст. 4 п. 4: «уважение автономии и свободы воли человека»; п. 5 — риск-ориентированный подход.
   > Ст. 9 ч. 1: маркировка — «Лицу, применяющему большую фундаментальную модель… в целях создания информационного материала в аудио-
   > и (или) визуальной форме, обеспечивается возможность размещения информационного предупреждения…» (с 01.03.2027, ст. 13 ч. 2).
   > Ст. 13: вступает в силу с 01.09.2026; п. 3–5 ч. 2 ст. 5, ч. 2–5 ст. 6, ст. 8–10 — с 01.03.2027.
   **Вывод:** требования объяснимости решений в законе НЕТ ни одной статьи; предмет — только БФМ ≥ 1 млрд параметров. Продукт без
   ML и без LLM, с заранее заданным алгоритмом, под закон не попадает ни по ст. 1, ни по определению ст. 3 п. 1. Вторичный обзор Б1
   (Г59) подтверждён первоисточником. Если в будущем появится LLM-слой — ст. 9 и 10 (маркировка, уведомление о правах на результат)
   станут применимы с 01.03.2027.
10. **Письмо/разъяснение РКН № 08-118602 (2024)** — Exa-поиск (8 результатов): упоминание ТОЛЬКО в блоге
    `net.zaurisakov.com` (06.08.2026): «В 2024 году Роскомнадзор выпустил разъяснение № 08-118602 о том, что обработка запросов через
    нейросети является частным случаем автоматизированной обработки персональных данных» — без реквизитов, даты, адресата, ссылки.
    Остальные выдачи (cloud.ru, habr 1082750, workspace.ru, forpes.ru, marsgpt.ru, vfs.consulting) номер не упоминают.
    `WebSearch "08-118602" Роскомнадзор` — только страницы контактов территориальных управлений РКН; номер не найден нигде.
    Попыток на этом шаге 2, плюс предыдущие в Г59/`rkn_ai_search`. 🟢 Не пройден: pd.rkn.gov.ru поиск по документам, браузер.
    **Статус для спецификации:** цитировать нельзя; и НЕ НУЖНО — по пересказу оно про обработку запросов НЕЙРОСЕТЯМИ, у нас нейросети
    нет. Норма, которая реально касается нас, — ст. 16 152-ФЗ (п. 8), а она добыта первоисточником.
    Попутно из habr 1082750 (16.09.2026, вторичное): «В первой версии законопроекта об ИИ было понятие „трансграничные технологии
    искусственного интеллекта“… из принятого 26 июля 2026 закона 243-ФЗ его убрали, про персональные данные там ничего» — сходится
    с первоисточником (п. 9).
11. Своя база (не повторять): `raw/ml_vs_rules_validity_2026-09-17.md` §4.1 и `raw/causal_effect_measurement_2026-09-10.md` —
    ст. 16 уже разобрана: «рекомендация — не решение, пользователь её принимает или правит сам»; граница — АВТОИСПОЛНЕНИЕ
    (автоплатёж, автоперевод в резерв) попадает под ч. 1 и требует письменного согласия. `raw/regulation_rf_investment_advice_2026-09-09.md`
    §2: FINPILOT не ИИР по предмету (нет ценной бумаги / сделки / договора об ИК); 🔴 ограничение для ГЕНЕРАТОРА ТЕКСТА:
    «признак а) — указание на соответствие инструмента финансовому положению/целям/риску» срабатывает, как только в тексте появится
    **определённый финансовый инструмент**. Значит шаблоны объяснения не имеют права подставлять тикер, эмитента, название фонда,
    банк или конкретный вклад в одну фразу с «подходит вашему профилю». Классы («индексный портфель», «облигации, например ОФЗ»,
    «накопительный счёт») — как сейчас.
12. **Tintarev N., Masthoff J. «Evaluating the effectiveness of explanations for recommender systems»**, *User Modeling and
    User-Adapted Interaction* 22, 399–439 (2012), DOI 10.1007/s11257-011-9117-5; авторская копия `aura.abdn.ac.uk/bitstream/handle/2164/2690/USER700.pdf`.
    Канал: Exa-поиск (выдержки из полного текста авторской копии и Springer). Дословно:
    > Abstract: «Such explanations can serve seven aims: effectiveness, satisfaction, transparency, scrutability, trust, persuasiveness,
    > and efficiency. These aims can be incompatible, so any evaluation needs to state which aim is being investigated and use appropriate
    > metrics. … Contrary to expectation, personalization was detrimental to effectiveness, though it may improve user satisfaction.»
    > Table 1: «Transparency — Explain how the system works; Scrutability — Allow users to tell the system it is wrong; Trust — Increase
    > users' confidence in the system; Effectiveness — Help users make good decisions; Persuasiveness — Convince users to try or buy;
    > Efficiency — Help users make decisions faster; Satisfaction — Increase the ease of use or enjoyment».
    > «These aims can be complementary (e.g. effectiveness may increase trust) or contradictory (e.g. **persuasiveness may decrease
    > effectiveness**).»
    > Метрика (по Bilgic & Mooney 2005): «1. (Rating1) The user rates the item on the basis of the explanation 2. The user tries the item
    > 3. (Rating2) The user re-rates the item. Effectiveness can then be measured by the discrepancy between steps 1 and 3 (Rating1 − Rating2).
    > … an effective explanation is one which minimizes the gap between these two ratings.»
    > Результат (камеры): «effectiveness was significantly better in the non-personalized condition than the personalized condition
    > (Bonferroni corrected, p < 0.05)… almost 45% of explanations in this condition lead to perfect effectiveness… participants were
    > significantly more satisfied with personalized explanations than non-personalized (Bonferroni corrected, p<0.01).»
    > «The lower opt-out rates in the personalized condition indicate that the personalized explanations did help participants form an
    > opinion, though **not necessarily an accurate one**.»
    **Перенос:** «понравилось объяснение» (satisfaction) и «помогло решить верно» (effectiveness) расходятся ИЗМЕРЕННО, в обратные стороны.
    Метрика нашей проверки — effectiveness, а не satisfaction. Оговорка: домен — фильмы/камеры, персонализация там = подбор признаков
    под вкус, а не подстановка собственных чисел пользователя; переносим принцип метрики, а не знак эффекта.
13. **Bansal G., Wu T., Zhou J., Fok R., Nushi B., Kamar E., Ribeiro M. T., Weld D. S. «Does the Whole Exceed its Parts? The Effect
    of AI Explanations on Complementary Team Performance»**, CHI 2021; полный текст `aiweb.cs.washington.edu/ai/pubs/bansal-chi21.pdf`
    (Exa-поиск, выдержки из PDF). >1 500 участников, три набора (Beer, Amzbook, LSAT). Дословно:
    > «While we observed complementary improvements from AI augmentation, they were not increased by explanations. Rather,
    > **explanations increased the chance that humans will accept the AI's recommendation, regardless of its correctness.**»
    > «Explanations often increased accuracy when the AI system was correct but, worryingly, decreased it when the AI erred, resulting in
    > a minimal net change — even for our adaptive explanations.»
    > «For Beer, Team (Conf) and Team (Explain-Top-1, AI) achieved similar performance, with the accuracy being 0.89 ± 0.05 vs.
    > 0.88 ± 0.06 respectively; the difference was insignificant (z=-1.18, p=.24).»
    > «This is consistent with Psychology literature [39], which has shown that human explanations cause listeners to agree even when
    > the explanation is wrong…»
    > Вывод авторов: «communicate explanations to increase understanding rather than just to persuade.»
    **Перенос:** ловушка убедительности ИЗМЕРЕНА на большом N: объяснение поднимает принятие совета независимо от его правильности.
    Значит (1) метрика проверки обязана делить случаи на «совет верен» / «совет неверен» (у нас: синтетика с известным верным ответом
    и подсаженными ошибками), (2) простой показ уверенности — сильный базовый уровень, объяснение должно его ПОБИТЬ, иначе не нужно.
14. **McDowell M., Jacobs P. «Meta-analysis of the effect of natural frequencies on Bayesian reasoning»**, *Psychological Bulletin*
    143(12), 1273–1312 (2017), DOI 10.1037/bul0000126 (PubMed 29048176). Канал: Exa; числа — из диссертации Jacobs P. «On the Significance
    of Information» (HU Berlin 2021, DOI 10.18452/22919, глава = та же статья) и Weber, Binder, Krauß, *Frontiers in Psychology* 2018,
    DOI 10.3389/fpsyg.2018.01833. Дословно (Jacobs 2021):
    > «35 articles representing 226 performance estimates» (абстракт статьи).
    > «We find that, in its simplest form we would, on average, expect **24 percent** of those presented with natural frequencies and
    > **4 percent** of those presented with conditional probabilities to solve such problems correctly. This implies an odds ratio of 7.10…»
    > «The strongest moderator, overall and conceptually, was the presentation of a **visual aid**, which increased performance under both
    > formats by 22 and 23 percentage points, on average.»
    > «Gerd Gigerenzer and Ulrich Hoffrage (1995) reported that only 16 percent of their participants were able to solve a problem when given
    > information in conditional probabilities… under this format [natural frequencies], 46 percent…»
    Weber et al. 2018: «on average three quarters of participants in their meta-analysis failed to obtain the correct solution … in frequency
    format»; и ~49 % получивших частоты переводили их обратно в вероятности.
    **Перенос и граница переноса:** эффект измерен на БАЙЕСОВСКИХ задачах (условные вероятности). У нас вывод Монте-Карло —
    вероятность одиночного исхода («подушка кончится до …») и квантильный коридор. Прямо переносится: (1) формат «N из 100 вариантов
    будущего» вместо «P = 0,13», потому что он несёт класс отсчёта; (2) визуальная опора (+22–23 п.п.) — самый сильный модератор,
    сильнее формата. Не переносится автоматически: величина эффекта (24 % против 4 %) — она про условный вывод, которого мы
    от пользователя не требуем.
15. **Gigerenzer G., Hertwig R., van den Broek E., Fasolo B., Katsikopoulos K. V. «"A 30% Chance of Rain Tomorrow": How Does the
    Public Understand Probabilistic Weather Forecasts?»**, *Risk Analysis* 25(3), 623–629 (2005), DOI 10.1111/j.1539-6924.2005.00608.x;
    полный текст — `library.mpib-berlin.mpg.de/ft/gg/GG_30_Chance_2005.pdf`, реквизиты — `researchonline.lse.ac.uk/id/eprint/16975/`
    (Exa; Wiley — только оболочка). Дословно:
    > «Because the forecast is expressed as a single-event probability, however, it does not specify the class of events it refers to.
    > Therefore, even numerical probabilities can be interpreted by members of the public in multiple, mutually contradictory ways.»
    > «Only in New York did a majority of them supply the standard meteorological interpretation… In each of the European cities, this
    > alternative was judged as the least appropriate. The preferred interpretation in Europe was that it will rain tomorrow "30% of the
    > time," followed by "in 30% of the area."»
    > Рецепт: «There is a 30% probability of rain tomorrow. This percentage does not refer to how long, in what area, or how much it rains.
    > It means that in 3 out of 10 times when meteorologists make this prediction, there will be at least a trace of rain the next day.»
    > «Quantitative probabilities will continue to confuse the public as long as [the reference class is not specified]…»
    **Перенос (прямой, это именно наш случай — вероятность одиночного исхода):** каждое вероятностное число Монте-Карло в тексте
    обязано нести КЛАСС ОТСЧЁТА: «из 1 000 вариантов того, как могут сложиться ваши доходы и расходы в ближайшие 3 месяца, в 130
    подушка заканчивается раньше». Без класса — «13 % риск» будет прочитан как «13 % денег» или «13 % времени».
16. **Вербальные шкалы вероятности — школа Budescu.** Канал: Exa (три документа).
    (а) Budescu D. V., Broomell S. B., Por H.-H. «Improving communication of uncertainty in the reports of the IPCC», *Psychological
    Science* 20, 299–308 (2009) — пересказ New Scientist 10.02.2009 (223 участника): «Three quarters of respondents thought "very likely"
    meant less than 90% certain, and nearly half thought "very likely" meant less than 66% certain.»
    (б) Budescu, Por, Broomell «Effective communication of uncertainty in the IPCC reports», *Climatic Change* (2012), репрезентативная
    выборка США (Knowledge Networks/TESS), PDF `paos.colorado.edu/.../Effective_communication_of_unc.pdf`. Дословно:
    > «The mean estimates for the four words are 41 for Very Unlikely, 44 for Unlikely, 54 for Likely, and 62 for Very Likely.
    > The most striking result is how regressive these estimates are…»
    > «the dual (verbal—numerical) scale (1) increases the level of differentiation between the various terms, (2) increases the consistency
    > of interpretation of these terms, and (3) increases the level of consistency with the IPCC guidelines. Most importantly, (4) these
    > positive effects are independent of the respondents' ideological and environmental views.»
    > «Access to the translation table (Table 1) improved consistency slightly, but the addition of numerical probability ranges to the
    > verbal probabilistic terms in the statements themselves was more effective…»
    > «Authors should exercise caution when considering the use of negatively worded terms (e.g., Unlikely) … the negatively-worded terms
    > resulted in greater variability in the responses than the positively-worded terms.»
    > «Probabilistic pronouncement should be used exclusively for precise and unambiguous events…»
    > «the vast majority of these studies were done in English and there is no research on the universality of these boundaries across
    > languages.»
    (в) Budescu et al. «The interpretation of IPCC probabilistic statements around the world», *Nature Climate Change* 4 (2014),
    nature.com/articles/nclimate2194 + отчёт NSF (ADS 2011nsf....1125879B): «25 samples and 17 languages … 10,792 valid responses …
    laypeople interpret IPCC statements as conveying probabilities closer to 50% than intended … the Dual presentation format makes the meaning
    of the terms across languages more similar». Был ли русский среди 17 языков — из выдержек не видно (🟢 не проверено).
    **Перенос:** слово без числа читается регрессивно к 50 % («очень вероятно» → в среднем 62) и с большим разбросом; словарь на одном
    языке не переносится на другой. Правило для нас: НИКОГДА только слово; всегда «слово + число с классом отсчёта в той же фразе»
    (двойной формат, число внутри предложения, а не в сноске/легенде); избегать отрицательных формулировок («маловероятно»)
    — у них разброс выше; вероятностное слово применять только к точно определённому событию («подушка опустится ниже 1 месяца
    расходов», а не «будут трудности»).
17. **Коммуникация финансового риска непрофессионалам — измерено именно на финансовых решениях.** Канал: Exa.
    (а) Bradbury M., Hens T., Zeisberger S. «Improving Investment Decisions with Simulated Experience», *Review of Finance* 19(3),
    1019–1052 (2015), DOI 10.1093/rof/rfu021; SSRN 2179276. Дословно (выдержки полного текста):
    > «participants are able to gain "simulated experience" by random sampling of a previously described return distribution.»
    > «After gaining experience 51.4% of subjects changed their product choice. … 35.2% increased risk taking while only 16.2% switched into
    > a less risky product (paired two-sided Wilcoxon signed-rank test: p<0.01).»
    > «After SE, loss probabilities are less overestimated, gain probabilities less underestimated… subjects do not show greater regret or
    > dissatisfaction with the returns achieved by the riskier decisions.»
    > «the simulated experience essentially repeated information already provided to the subjects» — то есть эффект даёт ФОРМА, не новая
    > информация. «probability estimates after SE are based on the observation of only 30 random returns».
    (б) Kaufmann C., Weber M., Haisley E. «The Role of Experience Sampling and Graphical Displays on One's Investment Risk Appetite»,
    *Management Science* 59(2), 323–340 (2013) — аннотация (RePEc):
    > «We analyze four different ways of communicating risk: (i) numerical descriptions, (ii) experience sampling, (iii) graphical displays,
    > and (iv) a combination of these formats in the "risk tool." … participants in the risk tool condition are more accurate on recall
    > questions regarding the expected return and the probability of a loss. We find no evidence of greater dissatisfaction with returns…»
    **Перенос:** у нас 1 000 путей Монте-Карло уже посчитаны (§15 канона) — «симулированный опыт» почти бесплатен: показать 10–20
    случайных путей («так может сложиться месяц: …»). 🔴 Но оба исследования показывают, что ФОРМАТ сам сдвигает выбор риска
    (51,4 % сменили продукт без новой информации) — это ровно ловушка из п. 13 с другой стороны: формат объяснения — не нейтральная
    упаковка, его влияние на выбор надо мерить против верного ответа, а не против «понравилось». Критерий «лучше» у авторов — точность
    оценок вероятности и отсутствие сожаления, не доля принявших.
18. **Kulesza T., Stumpf S., Burnett M., Yang S., Kwan I., Wong W.-K. «Too much, too little, or just right? Ways explanations impact
    end users' mental models»**, IEEE VL/HCC 2013, pp. 3–10, DOI 10.1109/VLHCC.2013.6645235; открытый PDF
    `openaccess.city.ac.uk/id/eprint/6344/3/VLHCC2013.pdf` (Exa). Качественное исследование, музыкальный рекомендатель. Дословно:
    > «soundness (how truthful each element in an explanation is with respect to the underlying system) and completeness (the extent to which
    > an explanation describes all of the underlying system)»
    > «Our findings suggest that completeness is more important than soundness… We also found that oversimplification, as per many commercial
    > agents, can be a problem: when soundness was very low, participants experienced more mental demand and lost trust in the explanations»
    > «Our most complete explanations (HH and LSHC) were associated with the best mental models… Participants placed the most trust in HH
    > explanations.» «Participants had more difficulty understanding the agent's reasoning process than the features it used, but abstract
    > explanations of the model intelligibility type helped overcome this obstacle. However, participants appeared to prefer more concrete
    > explanations.»
    **Перенос:** у нас soundness = 1 по построению ДОСТУПНА (SAW — точное разложение), значит спор «полнота против верности» для нас
    снят: делаем HH (верно и полно), а краткость достигаем ОТБОРОМ (топ-причины), не упрощением-искажением. Замер п. 5 показывает,
    что текущий слой как раз нарушает soundness (Г-а, Г-б) — это худший угол таблицы Kulesza (доверие падает).
    Отдельный блок «как это работает вообще» (model intelligibility) — нужен, он закрывает «процесс», который понимают хуже признаков.
19. **Miller T. «Explanation in artificial intelligence: Insights from the social sciences»**, *Artificial Intelligence* 267 (2019)
    1–38, DOI 10.1016/j.artint.2018.07.007; arXiv 1706.07269v3 (Exa, выдержки полного текста). Дословно четыре вывода:
    > «1. Explanations are contrastive — … people do not ask why event P happened, but rather why event P happened instead of some event Q.»
    > «2. Explanation are selected (in a biased manner) — people rarely, if ever, expect an explanation that consists of an actual and complete
    > cause of an event. Humans are adept at selecting one or two causes…»
    > «3. Probabilities probably don't matter — … referring to probabilities or statistical relationships in explanation is not as effective as
    > referring to causes.»
    > «4. Explanations are social — they are a transfer of knowledge, presented as part of a conversation or interaction…»
    > «the answer "Because she was hot" is a good answer if the foil is Elizabeth leaving the door closed, but not a good answer if the foil is
    > "rather than turning on the air conditioning", because the fact that Elizabeth is hot explains both the fact and the foil.»
    > «explaining a contrastive question is often easier than giving a full causal attribution because one only needs to understand what is
    > different between the two cases» · «Lim and Dey found … that "Why not …?" questions were common questions that people asked.»
    **Перенос:** (1) причина обязана РАЗЛИЧАТЬ факт и фольгу — критерий, одинаковый у обоих вариантов, причиной быть не может (это
    ровно формальная запись дефекта Г-а: Rt = 0,25 у всех — «жарко» объясняет и дверь, и кондиционер); (2) выбирать 1–2 причины;
    (3) фольга по умолчанию — второе место, но пользователь спрашивает «почему не …» про СВОЙ вариант — у нас 66 посчитанных
    альтернатив, значит на любую фольгу из решётки ответ точный, без приближений; самые частые фольги — три угла («всё в долг»,
    «всё в подушку», «всё в цели»); (4) вероятность — не причина: риск-блок отдельно от блока «почему».
20. **Wachter S., Mittelstadt B., Russell C. «Counterfactual Explanations Without Opening the Black Box: Automated Decisions and the
    GDPR»**, *Harvard Journal of Law & Technology* 31(2) (2018); SSRN 3063289; PDF `jolt.law.harvard.edu/.../Counterfactual-Explanations-
    without-Opening-the-Black-Box-Sandra-Wachter-et-al.pdf` (Exa). Дословно:
    > «We propose three aims for explanations to assist data subjects: (1) to inform and help the subject understand why a particular decision
    > was reached, (2) to provide grounds to contest adverse decisions, and (3) to understand what could be changed to receive a desired result
    > in the future, based on the current decision-making model.»
    > «These counterfactual explanations describe the smallest change to the world that can be made to obtain a desirable outcome, or to arrive
    > at the "closest possible world." As multiple variables or sets of variables can lead to one or more desirable outcomes, multiple
    > counterfactual explanations can be provided…»
    > «Unconditional counterfactual explanations should be given for positive and negative automated decisions, regardless of whether the
    > decisions are solely (as opposed to predominantly) automated or produce legal or other significant effects.»
    **Перенос:** три цели Wachter ложатся на ч. 3 ст. 16 152-ФЗ почти дословно («разъяснить порядок принятия решения… возможность заявить
    возражение») — понять / оспорить / изменить. Наш контрфактуал обязан быть по ВХОДАМ пользователя (доход, расходы, подушка, ставка,
    профиль), а не «если бы у второго варианта было выше» (текущий `_counterfactual` — это не контрфактуал, а контраст, и подпись в
    коде вводит в заблуждение). У детерминированной модели «ближайший мир» находится точно: перезапуск расчёта на изменённом входе.
21. 🔴 ЗАМЕР-2 (скрипт `g62_cf.py` в scratchpad, случай B: доход 120 000, расходы 70 000, кредитка 35 %, подушка 20 000, профиль 5).
    `uptime` load average 3,27 / 4,11 / 4,22 (ниже 8) — замер времени валиден.
    - `run_planning`: **медиана 3,5 мс**, максимум 6,2 мс на 20 прогонах.
    - Победитель a0100 (100 % в подушку): floor_level 0,8571, U = 0,10. **Лучший по SAW — a1000 (100 % в досрочку кредитки), U = 0,50**,
      floor 0,2857. То есть выбор решила floor-ступень, SAW-ступень выбрала бы ПРОТИВОПОЛОЖНОЕ. Разность вкладов победитель − a1000:
      Rt −0,35, Lt +0,10, Dt −0,15, Si 0 (сумма −0,40).
    - Контрфактуал по подушке (бисекция, 10 прогонов ≈ 35 мс): при подушке **≈ 34 218 ₽** победитель меняется на a190 (4 000 в долг,
      36 000 в подушку). Проверка смысла: 34 218 + 36 000 ≈ 70 218 ≈ **1 месяц расходов** = floor при токсичном долге. Контрфактуал
      совпадает с каноном §8 — это и есть честная причина, выраженная в рублях.
    - Контрфактуал по доходу: при доходе **≈ 135 585 ₽** победитель → a190 (5 558,5 в долг, 50 026,5 в подушку).
    **Что это даёт спецификации:** правильный текст для B — не «оптимальный баланс для профиля „Агрессивный“», а
    «Сначала — запас на 1 месяц расходов (70 000 ₽): у вас кредит под 35 %, и без запаса любой сбой дохода превратится в новый долг
    под такую же ставку. Сейчас в подушке 20 000 ₽, после этого месяца будет 60 000 ₽ — всё ещё меньше. Как только запас дойдёт до
    70 000 ₽, свободные деньги пойдут на досрочное погашение кредитки: для вашего профиля это было бы лучшим вариантом без правила запаса.»
    Контрфактуал по входу стоит ~10 перерасчётов × 3,5 мс — дёшево, считать на сервере по запросу «подробнее», не на каждый показ.
22. Своя база: **Д-09** в `raw/math_core_verification_plan_2026-09-17.md` (стр. ~3132, Г39, 17.09.2026) — УЖЕ измерено: фраза
    «решающим оказалось…» неверна в **67,9 %** советов (40,4 % — выиграл floor; 27,5 % — выиграл SAW, но назван не тот критерий);
    предложено: ветка floor + критерий по разнице с соперником, цена 2–4 ч + тест верности 1–2 ч, корзина «до запуска».
    Мой замер (п. 5, 21) Д-09 НЕ повторяет, а добавляет три НОВЫХ дефекта того же класса:
    (Д-09а) контраст-текст «следующий отстаёт на N баллов» имеет неверный знак в 47 из 162 (29 %) портретов сетки — там, где решил floor;
    (Д-09б) константный критерий (max = min → 1,0 у всех) попадает в «решающий» (случай A, человек без долга);
    (Д-09в) полная ничья (все U = 1,0, случай C) подаётся как «набрал наивысшую оценку».
    Плюс (Д-09г) `build_recommendation_text` называет «безопасный минимум — 3 месяца», канон — floor 2 мес. / 1 мес. / 2–3 мес. и L* 3–6.
    Все четыре закрываются одним правилом спецификации: текст строится из трассы решения (какая ступень решила, с каким соперником,
    какие критерии различают), а не из абсолютных полей победителя.
23. **Millecamp M., Htun N. N., Conati C., Verbert K. «To explain or not to explain: the effects of personal characteristics when
    explaining music recommendations»**, IUI 2019, pp. 397–407, DOI 10.1145/3301275.3302313 (Exa, аннотация). Дословно:
    > «Results indicate that personal characteristics have significant influence on the interaction and perception of recommender systems,
    > and that this influence changes by adding explanations. For people with a low need for cognition are the explained recommendations the
    > most beneficial. For people with a high need for cognition, we observed that explanations could create a lack of confidence.»
    Смежное (Exa, аннотация главы Springer 2025, ITS-подсказки, Conati и др.): «students with low levels of two traits, Need for Cognition and
    Conscientiousness … generally do not ask for the explanations although they would benefit from them… personalization increases our target
    users' interaction with the hint explanations, their understanding of the hints, and their learning.»
    Ain et al. 2026 (DOI 10.1145/3774935.3806179, n = 54): простая интерактивная визуализация связи «предпочтения → рекомендация» работала
    «for most users, independent of their PCs».
    **Перенос:** тем, кому объяснение нужнее всего, свойственно его НЕ открывать → главная причина обязана стоять в уровне по умолчанию,
    а не за «подробнее». Адаптировать можно объём и порядок, но не факты (Tintarev п. 12: персонализация содержания ухудшила effectiveness).
    Меры need for cognition у нас нет и спрашивать её — трение; признаки уровня — поведенческие счётчики (см. спецификацию, ч. 4).
    Браузер и вкладки в этой теме не открывались; подагентов — 0.
24. Код прогноза (`app/core/forecast.py`, `app/services/forecasting.py:136`) против канона §15 и «Обновления прогнозирования (v3.3.0)»:
    - Монте-Карло строится ТОЛЬКО вокруг точечного прогноза ресурса `point_rt`; σ_abs = |point| · 0,05 · √(1 + 0,5h) (`MC_SIGMA_BASE = 0.05`),
      то есть ширина коридора — **принятое допущение ±5 %**, а не разброс, измеренный по истории пользователя.
    - Наружу отдаются только квантили `{"p10","p50","p90"}` на каждый шаг горизонта; сами пути (1 000 выборок) выбрасываются →
      **вероятность события** («подушка опустится ниже 1 мес. расходов») сейчас НЕ вычисляется, её нечем подставить в текст.
    - При отсутствии истории `build_history_from_current` строит СИНТЕТИЧЕСКУЮ историю из 6 точек (шум 5 %).
    **Следствия для спецификации (ч. 3):** (1) пока σ не оценена по истории, текст риска обязан говорить «коридор построен на типовом
    разбросе ±5 %, а не на ваших данных» — иначе нарушение soundness (п. 18); (2) формулировки «в N из 100 вариантов» допустимы только
    после того, как бэкенд начнёт сохранять счёт путей по событию (дёшево: счётчик в том же цикле, O(N)); до этого — только коридор
    p10–p90 с классом отсчёта; (3) при синтетической истории — никаких вероятностных слов, только «истории пока мало».

---

# СПЕЦИФИКАЦИЯ генератора объяснений (Г62, 19.09.2026)

Канон — `docs/math_model.md` v3.9.0. Движок уже решён (Г55 §7: Jinja2 + своя таблица форм из pymorphy3/OpenCorpora, Г59).
Здесь — ЧТО говорить, откуда числа, как про риск, какой глубины, как проверять, какой правовой минимум.
Все решения приняты вахтой по замерам; владельцу из этой темы не уходит ничего.

## Ч. 0. Сквозной принцип: текст — функция ТРАССЫ решения, а не полей победителя

Корень всех четырёх дефектов (Д-09 67,9 % + Д-09а…г, п. 5, 21, 22) один: слой текста берёт абсолютные поля победителя
(`weighted_scores`, `utility`) и сочиняет, почему он победил. Лечение — ранжирование само отдаёт **трассу решения**
`DecisionTrace` (чистые данные, без текста), генератор только переводит её в слова. Поля трассы:

| Поле | Что | Откуда (канон / код) |
|---|---|---|
| `mode` | `crisis` (R_t < 0) · `regular` | §12; `planning.py: is_deficit` |
| `decided_by` | `floor` · `saw` · `tie` · `single_admissible` | §8 лексикографический выбор; вычисляется в `rank_alternatives` |
| `floor_target` F и `floor_reason` | 2 мес · 1 мес (токсичный долг: имя, ставка, порог max(30 %, r_bench+15 п.п.)) · 2+Δ (CV дохода) | §8, `effective_floor_months` |
| `foil_default` | лучший вариант с ТЕМ ЖЕ floor_level, иначе лучший по U среди всех | §8 |
| `saw_best` | argmax U по всему A′ (что выбрала бы свёртка без правила запаса) | §8 |
| `delta_contrib[j]` | wⱼ·(r̂ⱼ(a*) − r̂ⱼ(foil)); сумма = U(a*) − U(foil) ТОЧНО (одна нормировка на A) | §7–8 |
| `constant_criteria` | j, где max = min на A (нормировка вырождена, `normalize_value` → 1,0) | §7 «защита от вырожденности» |
| `saturated_L` | L(a*) ≥ L*(u) → рост подушки выше цели не учитывается | §7 насыщение |
| `rejected` | число отсеянных по R(a) < 0 и по ПДН > max(0,40; D_t) | §6; `filter_alternatives` |
| `avalanche` | целевые кредиты (r_k ≥ r_bench) и НЕцелевые с их ставками; r_bench и его источник (ключевая·0,87 / фолбэк 0,14) | §10.2–10.3 |
| `cascade` | x_obl_unused → цели; x_goals_unused → подушка | §10.4 |
| `dt_alert` | D_t > 0,40 | §6 |
| `risk` | p10/p50/p90 по шагам; `sigma_source` = `assumed_5pct` · `fitted`; `history_kind` = `real` · `synthetic`; позже — счётчики событий | §15; п. 24 |

Правило `decided_by`: `floor`, если существует допустимая b с U(b) > U(a*) и floor_level(b) < floor_level(a*);
`tie`, если |U(a*) − U(foil)| < 1·10⁻⁴ при равном floor_level; `single_admissible`, если |A′| = 1 после дедупликации; иначе `saw`.
**Проверено на синтетике:** случай B (п. 21) → `floor`, saw_best = a1000 (всё в досрочку, U 0,50 против 0,10 у победителя).

## Ч. 1. Состав блоков текста и порядок

Обычный режим (R_t ≥ 0):

| # | Блок | Когда показывается | Содержание |
|---|---|---|---|
| Б1 | **Что делать** | всегда | сплит в ₽ и %: досрочка (какой кредит), подушка, цели (какие). Сумма = R⁺ (инвариант сохранения §10.4) |
| Б2 | **Почему так** (главная причина) | всегда, 1–2 причины | ветка по `decided_by` (ниже) |
| Б3 | **Что исключено правилами** | если `rejected` > 0, есть нецелевые кредиты, `dt_alert` | «кредит «X» под 8,5 % досрочно не гасим: ставка ниже 13,9 % — столько приносит накопительный счёт при ключевой 16 % после налога»; «N вариантов отсеяны: увели бы бюджет в минус»; «доля платежей 47 % — выше 40 %, план её не увеличит; стоит рефинансировать» |
| Б4 | **Чем платите** | если у a* есть критерий с Δⱼ < 0 против фольги, или каскад | главная уступка в натуральных единицах + существующие `costs` каскада |
| Б5 | **Риск** | если есть прогноз | правила ч. 3 |
| Б6 | **Что изменило бы совет** | уровень 2 | контрфактуалы по входам (ч. 4) |
| Б7 | **Как это устроено и как не согласиться** | уровень 3, постоянная ссылка | статичный текст: 66 вариантов, два жёстких правила, правило запаса, веса ВАШЕГО профиля; кнопка «не согласен» (ч. 6) |

Б2 по веткам (шаблоны — смысл, не финальная редактура):
- `floor`: «Сначала — запас на {F} мес. расходов ({F·E} ₽){причина F}. Сейчас в подушке {B_liq} ₽, после этого месяца будет {B_liq+x_r_eff} ₽.
  {Если floor не достигнут:} Как только запас дойдёт до {F·E} ₽, свободные деньги пойдут {куда saw_best}: для вашего профиля это было бы
  лучшим вариантом без правила запаса.» Причина F: токсичный долг → «у вас кредит «X» под 35 %: без запаса любой сбой дохода станет
  новым долгом под такую же ставку, поэтому запас сокращён до 1 месяца»; волатильный доход → «доход за последние {n} мес. колебался
  сильнее обычного, поэтому запас увеличен до {F} мес.». (Reg B комм. 9(b)(2)-7: причина берётся из ступени, которая решила.)
- `saw`: до 2 критериев с наибольшим Δⱼ > 0 против фольги; константные критерии исключены; каждый — в натуральных единицах
  (таблица ч. 2), не в «баллах». Фольга называется: «по сравнению с вариантом «{сплит фольги}» этот…».
- `tie`: «Варианты «{A}» и «{B}» для вас практически равноценны (разница оценок меньше 0,01 %). Выбран «{A}» по правилу: {правило
  разрешения ничьей}.» Правило ничьей должно стать явным в коде (сейчас — порядок генерации; решение вахты: при ничьей предпочитать
  больший floor_level, затем больший x_d_eff, затем меньший номер — закрепить тестом).
- `single_admissible`: «Подходит только один вариант: остальные {n₁} увели бы бюджет в минус, {n₂} подняли бы долю платежей выше 40 %.»

Кризисный режим (R_t < 0): Б1 = план ходов `crisis_plan.actions` по порядку §12; Б2 = дефицит |R_t| ₽ и запас хода
`runway_months`; Б3 = тяжесть `severity` словами; Б5 не показывается (прогноз в кризисе — не главное); Б6 = «сколько сократить,
чтобы выйти в ноль» (`max_affordable_expenses`) — это уже контрфактуал по построению. Существующее `summary` без формул сохраняется.
Слой излишка (§14) и инвест-транш (§13) — отдельные блоки после Б1 с их нотами (АСВ 1,4 млн, ИИС), без изменений.

Ограничения на весь текст: не больше 4 причин суммарно (Reg B комм. 9(b)(2)-1); ни одного критерия, не различающего факт и фольгу
(Miller п. 19); ни одного определённого финансового инструмента рядом со словами о пригодности (39-ФЗ, п. 11); никаких «баллов
из 100» — min-max нормировка относительна множеству A, число баллов не сравнимо ни между людьми, ни между месяцами.

## Ч. 2. Откуда каждое число

Правило: в шаблоне нет числовых литералов. Каждое число — подстановка из трассы или из таблицы констант канона (0,40; 2 / 1 мес;
L* по профилю; 1,4 млн АСВ; 400 000 ИИС; 4 % инфляции целей). Проверяется автоматически (ч. 5, тест T2).

| Подстановка в тексте | Поле | Канон |
|---|---|---|
| сумма к распределению | R⁺ = max(R_t, 0) | §4.2 |
| досрочка / в подушку / в цели, ₽ | `x_obl_effective`, `x_reserve_effective`, Σ`goal_allocation` | §10.4, §5.2, §11.4 |
| какой кредит и его ставка | `obligation_allocation[].name`, `.interest_rate` | §10.4 |
| порог «выгодно гасить» | r_bench = r_key·0,87 (и r_key, и источник) | §10.2 |
| «станет свободнее на … ₽/мес» (критерий R) | `Rt_new − Rt` | §5.1 |
| «подушка на … мес.» (критерий L) | `Lt_new`, при `saturated_L` — L*(u) | §5.2, §7 |
| «доля платежей в доходе с …% до …%» (критерий D) | `Dt`, `Dt_new` ×100, целые проценты | §3.4, §5.3 |
| «в цели … ₽, из них в «{цель}» …» (критерий S) | `goal_allocation[goal]`; приоритет — w_cat·u_s | §11.1–11.4 |
| запас F и его причина | `floor_target`, `floor_reason` (кредит, ставка, CV) | §8 |
| «сколько месяцев проживёте без дохода» | `Lt` (текущее), `Lt_new` | §3.3 |
| риск (коридор) | `p10`, `p50`, `p90` на шаге h | §15 |
| дефицит, запас хода | |R_t|, `runway_months` | §12 |
| потолок трат в кризисе | `max_affordable_expenses` | §12 |

Перевод Δⱼ в натуральные единицы: Δ_R → разница `Rt_new` a* и фольги в ₽/мес; Δ_L → разница `Lt_new` (с насыщением) в мес.;
Δ_D → разница `Dt_new` в п.п. дохода; Δ_S → разница Σ`goal_allocation` в ₽. Сами Δⱼ (веса × нормированные) — только для
ОТБОРА причин, в текст не выводятся. Округление: деньги — целые рубли с неразрывным пробелом (скилл money-format), месяцы — до
0,1, проценты дохода — целые.

## Ч. 3. Правила формулировок риска

1. **Класс отсчёта в каждой вероятностной фразе** (Gigerenzer 2005, п. 15): «из 1 000 смоделированных вариантов ваших доходов и
   расходов на ближайшие {h} мес.». Никогда «риск 13 %» без класса.
2. **Двойной формат, число внутри фразы** (Budescu 2009/2012/2014, п. 16): слово + число в одном предложении, не в легенде.
   Только слово — запрещено (читается регрессивно к 50 %: «очень вероятно» → в среднем 62).
3. **Шкала слов (своя, положительный корень, без отрицаний):** ≥ 90 из 100 — «почти всегда»; 66–89 — «в большинстве вариантов»;
   34–65 — «примерно в половине вариантов»; 10–33 — «в меньшинстве вариантов»; 1–9 — «редко»; 0 из 1 000 — «ни в одном из 1 000
   вариантов (это не значит, что невозможно)». 🟡 Русская шкала не валидирована ни одним источником (Budescu: «no research on the
   universality of these boundaries across languages») — поэтому слово всегда при числе, а проверка прочтения — вопрос в опросе (ч. 5).
4. **Коридор словами:** «в 8 из 10 вариантов свободный остаток через {h} мес. будет между {p10} и {p90} ₽; в 1 из 10 — ниже {p10} ₽».
   Нижний хвост называется всегда: 80 % интервал оставляет 20 % снаружи.
5. **Событие должно быть точным** (Budescu 2012): «подушка опустится ниже 1 месяца расходов ({E} ₽)», а не «возникнут трудности».
6. **Честность источника разброса** (п. 24): пока σ = типовые ±5 %, фраза «коридор построен на типовом разбросе, а не на вашей
   истории»; при синтетической истории — вероятностных слов нет вовсе, только «истории пока мало, прогноз ориентировочный».
7. **Вероятность события («в N из 1 000») — только после того, как бэкенд начнёт считать события по путям** (счётчик в цикле
   `monte_carlo_intervals`, O(N)). До этого Б5 = только коридор (правило 4).
8. **Риск — отдельно от «почему»** (Miller п. 19: вероятности — не причина). Б5 не объясняет выбор, он описывает последствия.
9. **Симулированный опыт** (Bradbury 2015, Kaufmann 2013, п. 17) — уровень 2: 5–10 случайных путей из тех же 1 000 («так может сложиться:
   …»). 🔴 Включать только после A/B-проверки ч. 5: формат сам сдвигает выбор (51,4 % сменили продукт без новой информации).

## Ч. 4. Уровни глубины

| Уровень | Что | Показ |
|---|---|---|
| 0 — карточка | Б1 + Б2 одной фразой (главная причина) + Б5 одной фразой, если нижний хвост уводит R или подушку ниже нуля / floor | по умолчанию |
| 1 — «почему так» | Б2 полностью (≤ 4 причин), Б3, Б4, Б5 полностью | раскрытие |
| 2 — «а если…» | Б6: контрфактуалы по входам + ответ на выбранную фольгу | по запросу |
| 3 — «как устроено» | Б7 | постоянная ссылка |

Решения вахты:
- **Главная причина обязана быть в уровне 0** (Millecamp п. 23: те, кому объяснение нужнее, его не раскрывают).
- **Глубина меняет объём и порядок, но не факты и не числа** (Tintarev п. 12: персонализация содержания ухудшила effectiveness).
- **Фольги уровня 2**: второе место; три угла («всё в досрочку», «всё в подушку», «всё в цели»); **совет прошлого месяца** — для
  вернувшегося пользователя это естественная ожидаемая фольга (Miller: фольга = ожидаемое событие). Любая фольга из 66 отвечается
  точно из уже посчитанного `ranked`, без перерасчёта.
- **Контрфактуалы по входам** (Wachter п. 20): ближайшее изменение одной величины, меняющее победителя — подушка, доход, расходы,
  ставка самого дорогого кредита, профиль риска. Бисекция по одной переменной ≈ 10 перерасчётов × 3,5 мс (п. 21) — на сервере, по
  запросу, не на каждый показ. Текст: «Если бы в подушке было не 20 000, а 34 218 ₽, часть денег уже пошла бы на кредитку».
  Проверка смысла обязательна: контрфактуал случая B совпал с порогом floor (1 мес. расходов) — если бисекция даёт число, которое
  не объясняется ни одним правилом канона, это сигнал дефекта модели, а не текст для пользователя.
- **Признаки уровня без ML** (правила-счётчики, не обучение): (а) явный переключатель «всегда подробно» — запоминается;
  (б) пользователь раскрыл уровень 1 в ≥ 3 из последних 5 визитов → уровень 1 по умолчанию; (в) первый совет или смена победителя
  против прошлого месяца → Б2 раскрыт с фольгой «прошлый месяц»; (г) кризисный режим, `dt_alert`, `decided_by = floor` с
  недостигнутым запасом → уровень 1 по умолчанию; (д) профиль риска (анкета) — меняет только порядок блоков Б4/Б5, не текст.
  Тест финансовой грамотности не вводится (трение; сигнал (б) измеряет интерес поведением).

## Ч. 5. Метрика проверки

Главная метрика — **«помогло решить верно»**, не «понравилось». Основание: Tintarev & Masthoff 2012 (п. 12) — satisfaction и
effectiveness расходятся измеренно; Bansal 2021 (п. 13) — объяснение поднимает принятие совета независимо от его правильности.

**А. Автоматические тесты (CI, без людей, блокирующие):**
| Тест | Что проверяет | Порог |
|---|---|---|
| T1 верность ступени | `decided_by` в тексте = фактической ступени; при `saw` названный критерий = argmax Δⱼ против фольги | 100 % (сейчас 32,1 %, Д-09) |
| T2 происхождение чисел | каждое число, извлечённое из текста, совпадает с полем трассы/константой канона после форматирования | 100 % |
| T3 нет константных критериев | ни один j из `constant_criteria` не назван причиной | 100 % (Д-09б) |
| T4 знак контраста | если текст говорит «лучше фольги», U(a*) ≥ U(фольги) в той же ступени | 100 % (сейчас 71 % по сетке 162, Д-09а) |
| T5 истинность контрфактуала | перерасчёт на изменённом входе даёт заявленного победителя | 100 % |
| T6 детерминизм | один вход → побайтно один текст | 100 % |
| T7 без формул и без «баллов» | нет Rt, Lt, U(a), «баллов», «п.п.» (FR-01/UX-02) | 100 % |
| T8 согласование | «1 месяц / 2 месяца / 5 месяцев», «1 рубль / 3 рубля» по таблице форм | 100 % |
| T9 нет инструмента рядом с пригодностью | словарь запрещённых сущностей (тикеры, эмитенты, банки) в одной фразе с «подходит/соответствует» | 0 совпадений |
Прогон — на сетке синтетических портретов (как п. 5: доход × расходы × подушка × ставка × платёж × профиль) и на 12 000 портретах стенда.

**Б. Проверка с людьми (опрос/лаборатория, только синтетические сценарии — правило 7 CLAUDE.md):**
1. **Калиброванное доверие** (Bansal): участнику показывают сценарий и совет; в части сценариев совет заведомо НЕВЕРЕН (подсаженная
   ошибка: снят floor, перепутан порядок кредитов). Метрика = P(принял | совет верен) − P(принял | совет неверен). Условия: без
   объяснения · только числа/коридор (сильный базовый уровень Bansal) · наш уровень 0 · наш уровень 1. Объяснение оправдано, только
   если его метрика выше, чем у «только числа».
2. **Предсказание модели** (forward simulation): «что посоветует система, если подушка станет 70 000 ₽?» — доля верных ответов после
   уровня 1 против контроля. Это прямая мера понимания, без самооценки.
3. **Effectiveness по Bilgic & Mooney** (п. 12): оценка совета после уровня 0 и после полного раскрытия с ценой; меньший разрыв — лучше.
4. **Прочтение шкалы риска**: «что значит „в меньшинстве вариантов (20 из 100)“?» — доля ответов с правильным классом отсчёта; ответ
   на 🟡 из ч. 3 п. 3.
5. Satisfaction записывается, но **не является критерием решения**.
Размер и дизайн опроса — в синтез («анализ волны 2»), не здесь.

## Ч. 6. Правовой минимум

1. **152-ФЗ ст. 16** (ред. от 26.07.2026, текст статьи не менялся с 261-ФЗ 2011 г.; п. 8). Совет, который пользователь исполняет сам,
   — не «решение, порождающее юридические последствия»: под ч. 1–2 не попадаем (своя база, п. 11). Граница — **автоисполнение**
   (автоплатёж, автоперевод): тогда нужно письменное согласие (ч. 2) и всё ч. 3–4. **Решение вахты:** выполнять ч. 3 добровольно уже
   сейчас — она дешёвая и совпадает с Б7: (а) разъяснить порядок принятия решения (уровень 3), (б) последствия (совет необязателен,
   ничего не исполняется автоматически), (в) дать возможность заявить возражение — кнопка «не согласен с советом» с полем причины,
   (г) порядок защиты прав — ссылка на политику ПДн. Возражение — логируемое событие; при переходе к автоисполнению срок ответа
   30 дней (ч. 4) становится обязательным. Это же — сигнал качества модели (фольга, которую выбрал человек).
2. **243-ФЗ от 26.07.2026** (первоисточник добыт, п. 9): предмет — только БФМ ≥ 1 млрд параметров; определение ИИ требует «поиска
   решений без заранее заданного алгоритма». Продукт без ML/LLM **не попадает**. Требований объяснимости в законе нет. Если в будущем
   появится LLM-слой — ст. 9 (маркировка аудио/видео) и ст. 10 (уведомление о правах на результат) с 01.03.2027.
3. **Письмо РКН № 08-118602 (2024)**: первоисточника нет нигде, только блог (п. 10) — не цитировать; по пересказу оно про нейросети,
   к нам не относится.
4. **39-ФЗ ст. 6.1** (своя база, п. 11): шаблон не имеет права ставить определённый финансовый инструмент рядом со словами о
   пригодности профилю/целям (признак а) ИИР). Тест T9. Существующий дисклеймер 39-ФЗ (поле L5) не трогается.
5. **Отраслевой образец, не применимое право — Regulation B 12 CFR 1002.9(b)(2) и Official Interpretation** (первоисточник, п. 6):
   причины — только из реально посчитанных факторов (комм. 2, 4); отбор причин — контрастом к эталону (комм. 5); при составной системе
   причина из ступени, которая решила (комм. 7); факторы автоматического отсева раскрываются (комм. 8); не больше 4 причин (комм. 1);
   «не набрали балл» — недостаточная причина (§1002.9(b)(2)) — поэтому «этот вариант набрал наивысшую оценку» причиной не является.
   CFPB Circular 2022-03 — «технология не освобождает от конкретных и точных причин»; Circular 2023-03 снята в архив в 2025 г.,
   не цитировать как действующую.

## Что идёт в синтез по сферам
- **Математическое ядро:** `DecisionTrace` из `rank_alternatives` (decided_by, foil, saw_best, delta_contrib, constant_criteria);
  явное правило ничьей; счётчики событий в Монте-Карло; честный `sigma_source`.
- **Бэкенд:** генератор по блокам Б1–Б7 на Jinja2 + таблица форм; эндпоинт контрфактуалов по запросу; событие «не согласен».
- **Фронтенд:** уровни 0–3, выбор фольги (второе место / три угла / прошлый месяц), визуальная опора для коридора риска
  (McDowell & Jacobs: визуальная опора +22–23 п.п. — сильнейший модератор).
- **Правовой контур:** добровольная ч. 3 ст. 16; граница автоисполнения; тест T9.
- **Приоритет:** Д-09 + Д-09а…г — «до запуска» (неверное объяснение хуже отсутствующего, Kulesza: низкая soundness роняет доверие).

## Осталось неизвестным / не добыто
- 🟢 не сделано (наша работа): письмо РКН 08-118602 — не пройдены pd.rkn.gov.ru и браузер; CFPB 2023-03 — оригинал в архиве не
  пройден браузером (для спецификации не нужен); был ли русский среди 17 языков Budescu 2014 — не проверено.
- Нет ни одного исследования вербальной шкалы вероятности на РУССКОМ языке в финансовом контексте — шкала ч. 3 п. 3 гипотеза,
  проверяется опросом (ч. 5 Б4).
- Величины эффектов перенесены из других доменов (фильмы/камеры, музыка, погода, байесовские задачи, инвест-продукты); прямых
  измерений «объяснение распределения собственного потока» в литературе не найдено — поэтому ч. 5 Б обязательна до выводов.

---
Закрытие: GAP_QUEUE — строка таблицы Г62 добавлена (её не было), статус раздела Г62 → ✅. `list_pages` в браузере: одна вкладка
`about:blank` (не наша) — своих вкладок не открывалось. Тяжёлых процессов не запускалось (скрипты замера ≤ 1 с). Подагентов 0;
Exa-поисков 10, Exa fetch 2, WebSearch 1, curl 8. Версия, CHANGELOG, WATCHLOG, канон и код не тронуты.
