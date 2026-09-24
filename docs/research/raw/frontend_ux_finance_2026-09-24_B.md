# Тема 42, подагент B — сырьё (снято 24.09.2026)

Углы: (1) как показывают РЕКОМЕНДАЦИЮ, а не отчёт, включая ОТКАЗ; (5) тёмные паттерны
в финансовом интерфейсе и их запрет (включая право РФ).

Формат: дословная цитата > источник URL, дата снятия. Пересказ помечен «[пересказ]».

---

## Угол 1. Показ рекомендации, обоснования, альтернатив и отказа

### 1.1. 🔴 ПРЕЦЕДЕНТ ДЛЯ РЕЖИМА ОТКАЗА: Regulation B / ECOA, 12 CFR 1002.9 — интерфейс обязан назвать ПРИЧИНЫ отказа

Ключевая норма (п. (b)(2), дословно):

> "(2) _Statement of specific reasons._ The statement of reasons for adverse action required by
> paragraph (a)(2)(i) of this section **must be specific and indicate the principal reason(s)**
> for the adverse action. **Statements that the adverse action was based on the creditor's
> internal standards or policies or that the applicant, joint applicant, or similar party
> failed to achieve a qualifying score on the creditor's credit scoring system are
> insufficient.**"

— источник: https://www.ecfr.gov/current/title-12/chapter-X/part-1002/section-1002.9, снято 24.09.2026

Состав уведомления (п. (a)(2), дословно):

> "(2) _Content of notification when adverse action is taken._ A notification given to an
> applicant when adverse action is taken shall be in writing and shall contain a statement
> of the action taken; the name and address of the creditor; a statement of the provisions
> of section 701(a) of the Act; the name and address of the Federal agency that administers
> compliance with respect to the creditor; and either: (i) A statement of specific reasons
> for the action taken; or (ii) A disclosure of the applicant's right to a statement of
> specific reasons within 30 days, if the statement is requested within 60 days of the
> creditor's notification."

— источник: там же, снято 24.09.2026

Отдельная норма про НЕПОЛНЫЕ данные (п. (c)(2), дословно) — прямой аналог состояния
«недостаточно данных для рекомендации»:

> "(2) _Notice of incompleteness._ If additional information is needed from an applicant,
> the creditor shall send a written notice to the applicant **specifying the information
> needed**, designating a reasonable period of time for the applicant to provide the
> information, and informing the applicant that **failure to provide the information requested
> will result in no further consideration being given** to the application."

— источник: там же, снято 24.09.2026

**Что из этого прямо берётся в FINPILOT (режим «безопасного распределения нет»).**
Регулятор США формализовал ровно тот интерфейсный класс, который у нас есть: отказ
алгоритма человеку. Три требования, переносимых дословно:
1. отказ называет **конкретные главные причины**, а не факт срабатывания правила;
2. ссылка на «внутреннюю политику» или «вы не набрали баллов по нашей скоринговой модели»
   объявлена НЕДОСТАТОЧНОЙ — то есть экран вида «нарушен инвариант ПДН ≤ 0.40» без указания,
   ЧТО именно и НАСКОЛЬКО его нарушает, был бы по этой логике неприемлем;
3. состояние «данных не хватает» — отдельное от отказа, и оно обязано **перечислить
   недостающее** и сказать, что будет, если данные не дать.

### 1.2. Примет ли человек предписание машины: Dietvorst, Simmons & Massey, «Algorithm Aversion» (JEP:General 2015, 144(1), 114–126)

Абстракт дословно:

> "Research shows that evidence-based algorithms more accurately predict the future than do
> human forecasters. Yet when forecasters are deciding whether to use a human forecaster or
> a statistical algorithm, they often choose the human forecaster. This phenomenon, which we
> call algorithm aversion, is costly, and it is important to understand its causes. We show
> that people are especially averse to algorithmic forecasters after seeing them perform,
> even when they see them outperform a human forecaster. This is because people more quickly
> lose confidence in algorithmic than human forecasters after seeing them make the same
> mistake. In 5 studies, participants either saw an algorithm make forecasts, a human make
> forecasts, both, or neither. They then decided whether to tie their incentives to the future
> predictions of the algorithm or the human. Participants who saw the algorithm perform were
> less confident in it, and less likely to choose it over an inferior human forecaster. This
> was true even among those who saw the algorithm outperform the human."

— источник: https://marketing.wharton.upenn.edu/wp-content/uploads/2016/10/Dietvorst-Simmons-Massey-2014.pdf (DOI 10.1037/xge0000033), снято 24.09.2026

Числа из полного текста (дословно):

> "15–29% more error than the model in the MBA student forecasting task of Studies 1, 2, and 4
> and 90–97% more error than the model in the airline passenger forecasting task of Studies
> 3a and 3b" — то есть человек-прогнозист был хуже модели везде.

> "participants in the model-and-human conditions, most of whom saw the model outperform the
> human in the first stage of the experiment (**610 of 741 [83%] across the five studies**),
> were, across all studies, among those least likely to choose the model. In every experiment,
> participants in the model-and-human condition were significantly less likely to tie their
> bonuses to the model than were participants who did not see the model perform."

> "participants were significantly more likely to use humans that produced **13–97% more error
> than algorithms** after seeing those algorithms err."

> "Whereas seeing the human perform did not consistently decrease confidence in the human's
> forecasts — it did so significantly only in Study 4, seeing the model perform significantly
> decreased participants' confidence in the model's forecasts in all four studies."

Таблица 5 (оценка точности модели участниками, «% оценок модели в пределах 5 перцентилей»,
средние по условиям Control / Human / Model / Model-and-human):

> Study 1: 46.52 / 47.63 / **28.24** / 36.73
> Study 4: 52.89 / 50.64 / **37.51** / 43.47

— то есть достаточно ОДИН РАЗ показать человеку, как модель ошибается, чтобы его оценка
её точности упала с ~47 % до ~28 % (Study 1), при том что модель объективно точнее человека.

— источник: тот же PDF, снято 24.09.2026

Ещё одно число про калибровку ожиданий (Study 3b, дословно):

> "These participants expected a superhuman performance from the human — to perfectly predict
> 16.7 of 50 (33%) ranks — and a supermodel performance from the model — to perfectly predict
> 30.4 of 50 (61%) ranks. In reality, the humans and the model perfectly predicted 2.2 (4%)
> and 6.0 (12%) ranks."

**Прямой вывод для FINPILOT.** Продукт выдаёт ПРЕДПИСАНИЕ, и по этим данным доверие к нему
рухнет с первой же видимой ошибки прогноза — быстрее, чем к человеку-консультанту с теми же
ошибками. Два интерфейсных следствия:
(а) ожидания точности надо сбивать ЗАРАНЕЕ (прогноз SES+Монте-Карло показывать как диапазон
с явной частотой промаха, а не как одно число) — иначе человек ждёт 61 % точных попаданий
и получает 12 %;
(б) первая встреча с ошибкой модели должна происходить внутри интерфейса, где ошибка заранее
объявлена ожидаемой, а не как сюрприз.

### 1.3. 🔴🔴 САМОЕ ПРИКЛАДНОЕ: Dietvorst, Simmons & Massey, «Overcoming Algorithm Aversion» (Management Science 2018, 64(3), 1155–1170)

Абстракт дословно:

> "Although evidence-based algorithms consistently outperform human forecasters, people often
> fail to use them after learning that they are imperfect, a phenomenon known as algorithm
> aversion. In this paper, we present three studies investigating how to reduce algorithm
> aversion. In incentivized forecasting tasks, participants chose between using their own
> forecasts or those of an algorithm that was built by experts. **Participants were considerably
> more likely to choose to use an imperfect algorithm when they could modify its forecasts,
> and they performed better as a result. Notably, the preference for modifiable algorithms held
> even when participants were severely restricted in the modifications they could make**
> (Studies 1–3). In fact, our results suggest that participants' preference for modifiable
> algorithms was indicative of a desire for some control over the forecasting outcome, and not
> for a desire for greater control over the forecasting outcome, as participants' preference
> for modifiable algorithms was **relatively insensitive to the magnitude of the modifications**
> they were able to make (Study 2). Additionally, we found that giving participants the freedom
> to modify an imperfect algorithm made them feel more satisfied with the forecasting process,
> more likely to believe that the algorithm was superior, and more likely to choose to use an
> algorithm to make subsequent forecasts (Study 3). This research suggests that one can reduce
> algorithm aversion by giving people some control — even a slight amount — over an imperfect
> algorithm's forecast."

— источник: https://faculty.wharton.upenn.edu/wp-content/uploads/2016/08/Dietvorst-Simmons-Massey-2018.pdf (DOI 10.1287/mnsc.2016.2643), снято 24.09.2026

🔴 **ЦИФРЫ ИЗ ПОЛНОГО ТЕКСТА (дословно, самые важные во всей теме):**

> "Whereas only **32% of participants in the can't-change condition chose to use the model's
> forecasts, 73% of participants in the change-10 condition** (χ²(1, N = 145) = 24.19,
> p < 0.001) **and 76% of participants in the adjust-by-10 condition** (χ²(1, N = 146) = …)"

> "only **47% of participants in the can't-change condition chose to use the model's forecasts,
> 70% of participants in the adjust-by-X conditions** chose to [use] the model"

> "**71%, 71%, and 68% chose to [use] the model**" — доли выбравших модель при трёх разных
> величинах допустимой правки, включая случай, когда допустимая правка была урезана на 80 %:
> "by imposing an **80% reduction** of the amount by which [participants could adjust]".

> "Participants chose [to use the model, fully or partially] **over 80% of the time**."

— источник: тот же PDF (строки 340–342, 797, 811, 818, 1564 текстового слоя), снято 24.09.2026

Выводы авторов для практики (дословно):

> "framing the decision of whether or not to use an algorithm as an **all-or-nothing decision
> is likely to be counterproductive**. People are unlikely to commit to using an algorithm's
> forecasts exclusively after getting performance feedback or learning that it is imperfect.
> … However, asking people to commit to an algorithm's forecasts that they can modify by
> a limited amount seems much more palatable."

> "restricting the amount by which people can modify an algorithm's forecasts leads them to
> deviate from the algorithm less and thus to perform better."

> "Participants in our studies did often worsen the algorithm's forecasts when given the ability
> to adjust them. However, we may have to accept this error so that, overall, people make less
> error."

— источник: тот же PDF, снято 24.09.2026

🔴 **Что это значит для FINPILOT ровно.** Продукт УЖЕ построен как «66 альтернатив, шаг 10 %» —
то есть как **ограниченная правка предписания**, и это ровно та конструкция, которая в эксперименте
подняла долю принявших алгоритм с 32 % до 73–76 % (Study 1) и с 47 % до 70 % (Study 2). Три
интерфейсных следствия, которые из этого вытекают буквально:
1. **Экран предписания не должен быть «принять / отклонить».** Бинарный экран — та самая
   all-or-nothing рамка, которая названа контрпродуктивной. Нужен один рекомендованный
   вариант ПЛЮС видимый механизм сдвига (слайдер/шаг 10 %), даже если пользователь им
   не воспользуется.
2. **Диапазон правки можно и НУЖНО ограничивать** — согласие пользователя нечувствительно
   к величине допустимого сдвига (71 % / 71 % / 68 % при трёх ширинах, включая урезание на 80 %),
   а узкий коридор даёт лучший результат. Инварианты Rt ≥ 0 и ПДН ≤ 0.40 как границы слайдера
   не снижают принятие — это подтверждено экспериментально.
3. **Ухудшение решения пользователем — приемлемая цена.** Авторы прямо пишут, что участники
   часто портили прогноз правкой, и это всё равно выгодно в сумме. То есть «пользователь сдвинул
   ползунок и выбрал не оптимум» не повод запрещать сдвиг.

---

## Угол 5. Тёмные паттерны в финансовом интерфейсе и их запрет

### 5.1. Таксономия Harry Brignull — deceptive.design/types (18 типов, дословно)

> 1. **Sneaking** — "The user is drawn into a transaction on false pretences, because pertinent information is hidden or delayed from being presented to them."
> 2. **Forced action** — "The user wants to do something, but they are required to do something else undesirable in return."
> 3. **Hard to cancel** — "The user finds it easy to sign up or subscribe, but when they want to cancel they find it very hard."
> 4. **Preselection** — "The user is presented with a default option that has already been selected for them, in order to influence their decision-making."
> 5. **Obstruction** — "The user is faced with barriers or hurdles, making it hard for them to complete their task or access information."
> 6. **Hidden subscription** — "The user is unknowingly enrolled in a recurring subscription or payment plan without clear disclosure or their explicit consent."
> 7. **Hidden costs** — "The user is enticed with a low advertised price. After investing time and effort, they discover unexpected fees and charges when they reach the checkout."
> 8. **Trick wording** — "The user is misled into taking an action, due to the presentation of confusing or misleading language."
> 9. **Visual interference** — "The user expects to see information presented in a clear and predictable way on the page, but it is hidden, obscured or disguised."
> 10. **Fake social proof** — "The user is misled into believing a product is more popular or credible than it really is, because they were shown fake reviews, testimonials, or activity messages."
> 11. **Fake urgency** — "The user is pressured into completing an action because they are presented with a fake time limitation."
> 12. **Nagging** — "The user tries to do something, but they are persistently interrupted by requests to do something else that may not be in their best interests."
> 13. **Fake scarcity** — "The user is pressured into completing an action because they are presented with a fake indication of limited supply or popularity."
> 14. **Disguised ads** — "The user mistakenly believes they are clicking on an interface element or native content, but it's actually a disguised advertisment."
> 15. **Confirmshaming** — "The user is emotionally manipulated into doing something that they would not otherwise have done."
> 16. **Comparison prevention** — "The user struggles to compare products because features and prices are combined in a complex manner, or because essential information is hard to find."
> 17. **Addictive Design** — "The user interacts excessively with products designed to exploit psychological vulnerabilities and foster compulsive behavior."
> 18. **Currency Confusion** — "The user is misled about how much they are really spending, because real money is converted into a virtual currency that obscures the true cost."

— источник: https://www.deceptive.design/types, снято 24.09.2026

**Прямое приложение к FINPILOT:** из 18 типов к продукту-советнику применимы прежде всего
**Preselection** (какая из 66 альтернатив предвыбрана по умолчанию — это и есть предписание,
и оно должно быть обосновано расчётом, а не выгодой), **Comparison prevention** (альтернативы
обязаны сравниваться на одном экране в одних единицах), **Visual interference** (обоснование
и ограничения не прячутся за «подробнее»), **Trick wording** (формулировка предписания),
**Confirmshaming** (тон отказа: «нет безопасного распределения» нельзя подавать как укор),
**Nagging** (повторные приглашения пересчитать/довнести данные).

### 5.2. FTC «Bringing Dark Patterns to Light» (сентябрь 2022) — четыре группы тактик

[пересказ с дословными фрагментами] Отчёт выделяет четыре распространённые тактики:
> 1. **Misleading Consumers and Disguising Ads** — включая "advertisements designed to look like independent, editorial content" и таймеры обратного отсчёта, создающие ложную срочность.
> 2. **Making Subscription Cancellation Difficult**
> 3. **Burying Key Terms and Junk Fees** — "hiding material information in dense documents", сокрытие обязательных платежей до поздних шагов покупки.
> 4. **Tricking Consumers into Sharing Data** — настройки приватности, "designed to intentionally steer consumers toward the option that gives away the most personal information."

Ключевой вывод отчёта: dark patterns "have grown in scale and sophistication", компании
"develop complex analytical techniques, collect more personal data, and experiment with dark
patterns to exploit the most effective ones."

— источник: https://www.ftc.gov/news-events/news/press-releases/2022/09/ftc-report-shows-rise-sophisticated-dark-patterns-designed-trick-trap-consumers, снято 24.09.2026

### 5.3. Mathur et al. «Dark Patterns at Scale» (CSCW 2019) — числа

> approximately **11,000 shopping websites** and **53,000 product pages**;
> **1,818 dark pattern instances**; **15 distinct types**; **7 broader categories**;
> **183 websites** engaging in deceptive practices; **22 third-party entities** offering
> dark patterns as commercial solutions.

— источник: https://arxiv.org/abs/1907.07032 (Proc. ACM Human-Computer Interaction, ноябрь 2019, CSCW), снято 24.09.2026

### 5.4. 🔴 РФ: 353-ФЗ ст. 6 ч. 1 — требование к ВЁРСТКЕ полной стоимости кредита (дословно)

> «1. Полная стоимость потребительского кредита (займа) определяется как в процентах годовых,
> так и в денежном выражении и рассчитывается в порядке, установленном настоящим Федеральным
> законом. Полная стоимость потребительского кредита (займа) размещается **в квадратных рамках
> в правом верхнем углу первой страницы договора** потребительского кредита (займа) перед
> таблицей, содержащей индивидуальные условия договора потребительского кредита (займа),
> и наносится цифрами и **прописными буквами черного цвета на белом фоне четким, хорошо
> читаемым шрифтом максимального размера из используемых на этой странице размеров шрифта**.
> Полная стоимость потребительского кредита (займа) в денежном выражении размещается справа
> от полной стоимости потребительского кредита (займа), определяемой в процентах годовых.
> **Площадь каждой квадратной рамки должна составлять не менее чем 5 процентов площади первой
> страницы** договора потребительского кредита (займа). Полная стоимость потребительского
> кредита (займа) в процентах годовых указывается **с точностью до третьего знака после
> запятой**.»

— источник: https://www.consultant.ru/document/cons_doc_LAW_155986/e52bee2d092465172cd750d5a23927f45bb3d017/, снято 24.09.2026
— подтверждение тем же текстом на сайте Генпрокуратуры: https://epp.genproc.gov.ru/ru/proc_11/activity/legal-education/explain/e146820/, снято 24.09.2026

[пересказ] Историческая правка: точность «до третьего знака после запятой» добавлена
ФЗ от 02.07.2021 N 329-ФЗ, вступила в силу 03.07.2022 — прежняя редакция такого требования
не содержала (сравнительная таблица редакций КонсультантПлюс,
https://www.consultant.ru/document/cons_doc_LAW_167376/6bfe55e5bbf65ec6e7962cd4ac842e1a142be98f/).

**Почему это прямой прецедент для FINPILOT.** Российский законодатель уже один раз перевёл
требование «человек должен увидеть главное число» в проверяемые параметры ВЁРСТКИ: место
на экране (правый верхний угол первой страницы), цвет (чёрным по белому), размер (максимальный
из используемых на странице), площадь (не менее 5 % страницы), точность (3 знака). Это готовый
шаблон нормы для главного числа экрана предписания: место, контраст, кегль относительно
остальной страницы, доля площади, точность. Норма на FINPILOT формально не распространяется
(продукт не кредитор и не заключает договор потребительского кредита), но является образцом
уровня строгости, который регулятор РФ считает нормальным для финансового интерфейса.

### 5.5. 🔴 Требование одинакового шрифта при совместном показе ставки и диапазона ПСК (353-ФЗ, ч. 4.1 ст. 5)

> «Размещение в местах оказания услуг и на официальном сайте кредитора в информационно-
> телекоммуникационной сети "Интернет" (при наличии) информации о процентных ставках
> в процентах годовых, указанной в пункте 8 части 4 настоящей статьи, допускается при
> совместном размещении с указанной в пункте 10 части 4 настоящей статьи информацией
> о диапазоне значений полной стоимости потребительского кредита (займа) **одинаковым
> по размеру шрифтом**. Любая информация, доводимая кредитором до заемщика, должна
> соответствовать информации, указанной в части 4 настоящей статьи.» (дополнение внесено
> Федеральным законом от 24.07.2023 № 359-ФЗ)

— источник: http://www.kremlin.ru/acts/bank/37939, снято 24.09.2026

**Приложение:** прямой запрет визуального неравенства двух чисел, одно из которых выгодно
показывать крупнее. Для FINPILOT это переводится в норму: рекомендуемая альтернатива
и её отвергнутые конкуренты показываются одним кеглем; «выгодная» цифра не крупнее «невыгодной».

---

## Не добыто (подагент B)

(наполняется по ходу)
