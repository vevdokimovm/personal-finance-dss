# Тема 19. Регуляторика мира: граница «совет» / «информация-инструмент»

**Дата работы:** 09.09.2026. **Статус:** ЗАВЕРШЕНО. Разделы 1–8 закрыты, недобытое перечислено в конце файла с кодами ответов.

**Тип запроса (классификация lead agent):** breadth-first — восемь слабо связанных
под-вопросов по четырём юрисдикциям. Ограничение канона FINPILOT (правило 11): не более
двух подагентов, по одному, не веером. Основную добычу ведёт вахта сама.

**Метод:** дословная норма + реквизиты + дата проверки. Пересказ по памяти модели не
используется; если источник не открылся — записан код ответа.

---

## 1. ЕС: граница «investment advice» в MiFID II — дословно

### 1.1. Directive 2014/65/EU, Article 4(1)(4) — определение

Источник: консолидированный текст EUR-Lex `02014L0065 — EN — 28.03.2024 — 012.001`
(URL `https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02014L0065-20240328`,
HTTP 200, 952 081 байт, скачано 09.09.2026). Консолидация на 28.03.2024 — последняя доступная
на дату проверки.

> **Article 4(1)(4)**
> ‘investment advice’ means the provision of personal recommendations to a client, either upon
> its request or at the initiative of the investment firm, in respect of one or more transactions
> relating to financial instruments;

Три кумулятивных элемента прямо в тексте: (а) **personal recommendation**, (б) **клиенту**,
(в) **в отношении одной или нескольких СДЕЛОК, относящихся к ФИНАНСОВЫМ ИНСТРУМЕНТАМ**.
Отсутствие любого — деятельность не является investment advice.

### 1.2. Что такое «финансовый инструмент» — закрытый перечень

> **Article 4(1)(15)**
> ‘financial instrument’ means those instruments specified in Section C of Annex I, including such
> instruments issued by means of distributed ledger technology;

> **ANNEX I, SECTION C — Financial instruments**
> (1) Transferable securities;
> (2) Money-market instruments;
> (3) Units in collective investment undertakings;
> (4) Options, futures, swaps, forward rate agreements and any other derivative contracts relating
> to securities, currencies, interest rates or yields, emission allowances or other derivatives
> instruments, financial indices or financial measures which may be settled physically or in cash;
> (5) [деривативы на товары с денежным расчётом] … (6) … (7) …
> (8) Derivative instruments for the transfer of credit risk;
> (9) Financial contracts for differences;
> (10) [деривативы на климатические переменные, фрахт, инфляцию и пр.];
> (11) Emission allowances consisting of any units recognised for compliance with the requirements
> of Directive 2003/87/EC (Emissions Trading Scheme).

🔴 **Ключевое для FINPILOT.** Перечень Section C **закрытый** и в нём НЕТ:
банковского вклада/депозита, счёта накоплений, потребительского кредита, ипотеки,
кредитной карты, наличных денег, подушки безопасности. Следовательно, рекомендация
«направить X% свободного потока на досрочное погашение кредита, Y% в резерв, Z% в цели»
**по предмету вне** Section C — ровно как и в РФ по ст. 6.1 39-ФЗ (тема 18). Совпадение
конструкции полное: обе юрисдикции цепляют регулирование к ПРЕДМЕТУ (ценная бумага /
финансовый инструмент), а не к факту персонализации.

Оговорка: депозиты структурные («structured deposits») в MiFID II охвачены отдельно —
не через Section C, а через отдельные ссылки в ст. 1(4). Обычный срочный вклад — нет.
Для FINPILOT это не создаёт проблемы: конкретные вклады мы не называем.

### 1.3. Delegated Regulation (EU) 2017/565, Article 9 — что такое personal recommendation

Источник: консолидированный текст `32017R0565 — EN — 02.08.2022`. 🔴 Прямой `curl`
и `WebFetch` по EUR-Lex вернули **HTTP 202 с нулевым телом** (асинхронный рендер/троттлинг),
взято через текстовый прокси `https://r.jina.ai/…` — **HTTP 200, 239 403 байта**, 09.09.2026.

> **Article 9 — Investment advice** *(Article 4(1)(4) of Directive 2014/65/EU)*
>
> For the purposes of the definition of ‘investment advice’ in Article 4(1)(4) of Directive
> 2014/65/EU, a personal recommendation shall be considered a recommendation that is made to a
> person in his capacity as an investor or potential investor, or in his capacity as an agent for
> an investor or potential investor.
>
> That recommendation shall be presented as suitable for that person, or shall be based on a
> consideration of the circumstances of that person, and shall constitute a recommendation to take
> one of the following sets of steps:
>
> (a) to buy, sell, subscribe for, exchange, redeem, hold or underwrite **a particular financial
> instrument**;
>
> (b) to exercise or not to exercise any right conferred by **a particular financial instrument**
> to buy, sell, subscribe for, exchange, or redeem a financial instrument.
>
> A recommendation shall not be considered a personal recommendation if it is issued exclusively
> to the public.

**Пять признаков personal recommendation, вычитываемые из Article 9 дословно** (это и есть
канонический «пятиэлементный тест», который CESR/ESMA и FCA раскладывают в Q&A):

| № | Признак | Есть ли у FINPILOT |
|---|---|---|
| 1 | это **рекомендация** (а не только информация) | 🔴 ДА — выдаём одну альтернативу как рекомендованную |
| 2 | адресована **лицу в качестве инвестора или потенциального инвестора** (либо его агента) | 🟡 спорно — адресована лицу как заёмщику/сберегателю; инвест-транш размечен |
| 3 | **подана как подходящая ЭТОМУ лицу либо основана на учёте его обстоятельств** | 🔴 ДА — доходы, расходы, обязательства, цели, риск-профиль |
| 4 | это рекомендация совершить действие из перечня (buy/sell/subscribe/exchange/redeem/hold/underwrite) | 🟢 НЕТ — мы не рекомендуем ни одно из этих действий |
| 5 | действие относится к **КОНКРЕТНОМУ («a particular») финансовому инструменту** | 🟢 НЕТ — инструмент не назван вовсе |
| 6* | не адресована исключительно публике (not issued exclusively to the public) | 🔴 не помогает — наш вывод индивидуален |

🔴 **Решающий элемент в ЕС — слово «particular».** Article 9 требует не просто «финансовый
инструмент», а **конкретный** финансовый инструмент. Это ровно та же красная линия, что и
в теме 18 по РФ (ст. 6.2 п. 5 39-ФЗ: обязательное «описание ценной бумаги и планируемой с ней
сделки»). **Линии совпадают.** Персонализация (признак 3) у нас есть и это ничего не меняет:
признаки Article 9 **кумулятивны** — «shall be presented as suitable … **and** shall constitute
a recommendation to take one of the following sets of steps».

### 1.4. Article 25(2) Directive — suitability (на случай, если бы попадали)

> **Article 25(2)** When providing investment advice or portfolio management the investment firm
> shall obtain the necessary information regarding the client’s or potential client’s knowledge and
> experience in the investment field relevant to the specific type of product or service, that
> person’s financial situation including his ability to bear losses, and his investment objectives
> including his risk tolerance so as to enable the investment firm to recommend to the client or
> potential client the investment services and financial instruments that are suitable for him and,
> in particular, are in accordance with his risk tolerance and ability to bear losses.

Обратим внимание: набор данных, который MiFID II требует собирать для suitability
(финансовое положение + способность нести убытки + цели + риск-толерантность), FINPILOT уже
собирает целиком. То есть **по глубине профилирования мы на уровне регулируемого
инвестсоветника, а вне периметра держимся только за счёт предмета.** Это то же наблюдение,
что и находка (3) темы 18 — «мы в одном элементе от полного состава».

### 1.5. Article 54(1) DR 2017/565 — робо-советник не снижает ответственность

> **Article 54(1), второй абзац** Where investment advice or portfolio management services are
> provided in whole or in part **through an automated or semi-automated system**, the responsibility
> to undertake the suitability assessment shall lie with the investment firm providing the service
> and **shall not be reduced by the use of an electronic system** in making the personal
> recommendation or decision to trade.

Прямая проекция на нас: **«это алгоритм, а не человек» в ЕС не является ни смягчающим
обстоятельством, ни основанием для вывода из периметра.** Тот же по духу вывод, что и
находка (2) темы 18 про дисклеймер.

### 1.6. Annex I Section B(5) — «general recommendation» это ancillary service

> **ANNEX I, SECTION B — Ancillary services**
> (5) Investment research and financial analysis or other forms of **general recommendation**
> relating to transactions in financial instruments;

Важная деталь конструкции: общая (неперсональная) рекомендация по сделкам с финансовыми
инструментами — это **ancillary service**, а не investment service. Сама по себе она
**не даёт права** на лицензию и не требует её самостоятельно (ancillary-услуги
лицензируются только в связке с основной). То есть в ЕС generic advice выведен из основного
периметра сознательно и на уровне приложения к директиве.

---

## 2. «Generic advice» vs «personal recommendation»: что разрешено без лицензии

### 2.1. ЕС — конструкция уже показана в §1.6

В ЕС generic advice (в терминах Annex I Section B(5) — «other forms of general recommendation
relating to transactions in financial instruments») вынесена в **ancillary services** и не
образует самостоятельного лицензируемого состава.

🔴 CESR/10-293 «Questions and Answers — Understanding the definition of advice under MiFID»
(октябрь 2010) **не добыт**: `esma.europa.eu/sites/default/files/library/2015/11/10_293.pdf`
и `esma.europa.eu/document/questions-answers-understanding-definition-advice-under-mifid`
вернули **HTTP 404** (09.09.2026) — старая библиотека CESR при миграции сайта ESMA
переехала. Функциональный эквивалент по содержанию (те же пограничные случаи: калькуляторы,
фильтры, скрипты вопросов, generic advice) добыт из FCA PERG 8.28–8.30A — см. §3, — который
разбирает ровно эти сценарии дословно и подробнее.

### 2.2. UK — «generic advice» названа прямо и с примерами

Источник: FCA Handbook, **PERG 8.26 «Advice must relate to a particular investment»**
(handbook.fca.org.uk/handbook/PERG/8/26.html, HTTP 200, 09.09.2026; дата версии гайденса
в тексте — 06/04/2016 и 23/02/2018).

> **PERG 8.26.1 G** For the purposes of article 53(1), advice must relate to a particular
> investment – generic or general advice is not covered.
>
> **PERG 8.26.2 G** Generic advice will not be caught by article 53(1). Examples of generic
> advice may include: (1) **financial planning**; (2) advice on the merits of investing in Japan
> rather than Europe; (3) advice on the merits of investing in investment trusts as opposed to
> unit trusts or unit-linked insurance; and (4) advice on the merits of investing offshore, or
> in fixed income rather than floating rate bonds.

🔴 **«Financial planning» назван регулятором как пример НЕрегулируемого generic advice** —
это самый прямой из добытых текстов в пользу нашей позиции по инвестиционному контуру.

Ограничитель того же гайденса, который надо держать в голове:

> **PERG 8.26.5 G** (1) Although giving generic advice is generally not a regulated activity,
> if it is given **in the course of or in preparation for a regulated activity** it can form part
> of that regulated activity. (2) For example, if a firm gives generic advice (for instance about
> the merits of investing in Japan rather than Europe) and then goes on to identify a particular
> Japanese share, the generic advice will form part of the regulated activity…

Проекция на нас: пока в продукте нет ни витрины инструментов, ни перехода «а вот сюда положить»,
generic-статус держится. **Любая будущая интеграция «купить здесь» затягивает в периметр
и ретроспективно — весь предшествующий расчёт.**

### 2.3. Прямой ответ на центральный вопрос: «погасите дорогой кредит прежде, чем инвестировать»

- **ЕС (MiFID II):** НЕТ, это не investment advice — не выполняются признаки (a)/(b) Article 9
  DR 2017/565 (нет рекомендации buy/sell/hold в отношении «a particular financial instrument»).
- **UK, инвестиционный периметр (art. 53 RAO):** НЕТ по той же причине — PERG 8.24.2G(2)
  «that investment must be **a particular** investment».
- 🔴 **UK, долговой периметр (art. 39E RAO, debt counselling): ДА, это регулируемая
  деятельность.** Здесь красная линия проходит СОВЕРШЕННО ИНАЧЕ. Разбор — §5.

---

## 3. UK: regulated activity и Perimeter Guidance

### 3.1. RAO Article 53 — advising on investments (дословно)

Источник: **The Financial Services and Markets Act 2000 (Regulated Activities) Order 2001,
S.I. 2001/544, article 53**, legislation.gov.uk (HTTP 200, 65 755 байт, скачано 09.09.2026;
текст «latest available (revised)» с отметками поправок F1–F9).

> **53.—(1)** Advising a person is a specified kind of activity if the advice is—
> (a) given to the person in his capacity as an investor or potential investor, or in his capacity
> as agent for an investor or a potential investor; and
> (b) advice on the merits of his doing any of the following (whether as principal or agent)—
> (i) buying, selling, subscribing for, exchanging, redeeming, holding or underwriting **a
> particular investment which is a security, structured deposit or a relevant investment**, or
> (ii) exercising or not exercising any right conferred by such an investment to buy, sell,
> subscribe for, exchange or redeem such an investment.
>
> **(1A)** Paragraph (1) does not apply to a person who is appropriately authorised except to the
> extent that they are providing a personal recommendation.
> **(1C)** … a personal recommendation is a recommendation— (a) made to a person in their capacity
> as an investor or potential investor…; (b) which constitutes a recommendation to them to do any
> of the following…: (i) buy, sell, subscribe for, exchange, redeem, hold or underwrite **a
> particular investment** which is a security, structured deposit or a relevant investment; …
> and (c) that is— (i) presented as suitable for the person to whom it is made; or (ii) based on
> a consideration of the circumstances of that person.
> **(1D)** A recommendation is not a personal recommendation if it is issued exclusively to
> the public.

🔴 **Важная асимметрия UK против ЕС.** Для **неавторизованного** лица (наш случай, если бы мы
вышли на рынок UK без лицензии) применяется art. 53(1) — он **шире** MiFID-овского personal
recommendation: он **не требует персонализации вообще**. Достаточно «advice on the merits»
о конкретном инструменте. FCA формулирует это прямо:

> **PERG 8.24.1D G** … The definition of advising on investments … that applies to a person in (1)
> is the one in PERG 8.24.1G. **It is not relevant to such a person whether or not the advice is
> a personal recommendation.**

> **PERG 8.24.1B G** (1) A firm that is not appropriately authorised … will need permission for
> advising on investments … whether it wants: (a) to give non-personalised advice…

Значит: в UK «мы же не персонализируем» **не работает как защита** в инвестиционном контуре.
Работает только «инструмент не назван». Для нас это то же самое ограничение, что в РФ и ЕС,
но добытое по другому основанию, и это важно: наша единственная линия защиты держится
на предмете во всех трёх юрисдикциях, но в UK она — **единственная возможная**.

### 3.2. Пятиэлементный тест FCA (PERG 8.24.2 G) — дословно

> **PERG 8.24.2 G** For advice to be covered by PERG 8.24.1 G:
> (1) it must relate to an investment which is a security, structured deposit or a relevant
> investment;
> (2) that investment must be **a particular investment**;
> (3) it must be given to persons **in their capacity as investors or potential investors**;
> (4) it must be **advice (that is, not just information)**; and
> (5) it must relate to **the merits** of investors or potential investors (or their agents)
> buying, selling, subscribing for or underwriting … the investment.

Прогон FINPILOT: (1) НЕТ · (2) НЕТ · (3) спорно · (4) ДА · (5) НЕТ. Два независимых
провала теста ⇒ **art. 53 RAO не применяется**.

### 3.3. Граница «advice vs information» — PERG 8.28 (дословно, ключевое)

> **PERG 8.28.1 G** In the FCA's view, **advice requires an element of opinion on the part of the
> adviser. In effect, it is a recommendation as to a course of action. Information, on the other
> hand, involves statements of fact or figures.**
>
> **PERG 8.28.2 G** (1) In general terms, simply giving information without making any comment or
> value judgment on its relevance to decisions which an investor may make is not advice.
> (2) The provision of purely factual information does not become regulated advice merely because
> it feeds into the customer's own decision-making process and is taken into account by them.
> (3) Regulated advice includes **any communication with the customer which, in the particular
> context in which it is given, goes beyond the mere provision of information and is objectively
> likely to influence the customer's decision** whether or not to buy or sell.
> (4) A key to the giving of advice is that the information: (a) is either accompanied by comment
> or value judgment on the relevance of that information to the customer's investment decision;
> **or (b) is itself the product of a process of selection involving a value judgment so that the
> information will tend to influence the decision.**
> (5) Advice can still be regulated advice if the person receiving the advice: (a) is free to
> follow or disregard the advice; or (b) may receive further advice from another person…
>
> **PERG 8.28.5 G** A key question is whether **an impartial observer**, having due regard to the
> regulatory regime and guidance, context, timing and what passed between the parties, would
> conclude that what the adviser says could reasonably have been understood by the customer as
> being advice.
>
> **PERG 8.28.6 G** … **Any significant element of evaluation, value judgment or persuasion is
> likely to mean that advice is being given.**

🔴 **PERG 8.28.2(4)(b) и 8.28.5 закрывают для нас всякую надежду сойти за «информацию».**
SAW-свёртка с весами по риск-профилю — это буквально «a process of selection involving a value
judgment». Отсечение 66 альтернатив до одной — это «evaluation». А 8.28.2(5)(a) («клиент волен
не следовать») снимает и защиту «мы же только предлагаем». **FINPILOT — это advice, а не
information, по любому из этих критериев.** Вопрос только в том, ПРО ЧТО этот advice.

### 3.4. Скриптованные опросники, деревья решений и фильтры — PERG 8.30A

> **PERG 8.30A.4 G** (2) The pre-purchase questioning process may involve identifying one or more
> particular investments. If so, to avoid advising on investments…, the critical factor is likely
> to be whether the process is limited to, and likely to be perceived by the person as, **assisting
> the person to make their own choice** of product which has particular features which the person
> regards as important. The questioner will need to **avoid providing any judgment on the
> suitability** of one or more products for that person.
>
> 🟢 **PERG 8.30A.7 G** (3) One scenario is that the scripted questioning **may not lead to the
> identification of any particular investment; in this case, the questioner has provided advice,
> but it is generic advice and does not amount to advising on investments** (except P2P agreements).
>
> **PERG 8.30A.15 G** (1) If the input from the customer is much more extensive than, and the way
> that those inputs interact on the website is much more complicated than, the processes described
> in PERG 8.30A.12G and PERG 8.30A.13G, the website is not simply displaying factual information
> about the design of the product. (2) In that case **the production of a list of results uses an
> element of opinion and skill (albeit automated)** in translating the customer's input into a
> display of a particular product or products.

🟢 **PERG 8.30A.7G(3) — прямое попадание в наш случай и лучшая цитата всей темы для
инвестиционного контура.** «Опросник дал советующий вывод, но не назвал конкретного
инструмента ⇒ это generic advice ⇒ вне регулируемой деятельности». Это ровно FINPILOT:
опрос обширный, вывод оценочный, инструмент не назван.

🔴 И встречный сигнал: **PERG 8.30A.15G(2) — «element of opinion and skill (albeit automated)»**.
FCA прямо отвергает аргумент «это же автомат, а не мнение». Автоматизация оценочного суждения
остаётся оценочным суждением, как и в Art. 54(1) DR 2017/565 (§1.5). Три юрисдикции сошлись
на одном: **алгоритмичность не выводит из периметра.**

---

## 5. 🔴 UK debt counselling — ближайший к нам контур в мире, и он нас ЛОВИТ

> Раздел вынесен вперёд раздела 4, потому что это главная находка темы.

### 5.1. Норма — RAO article 39E (дословно)

Источник: legislation.gov.uk, S.I. 2001/544, art. 39E (HTTP 200, скачано 09.09.2026).
Введена: The FSMA 2000 (Regulated Activities) (Amendment) (No.2) Order 2013,
**S.I. 2013/1881, art. 1(2)(6), 5** — «inserted (26.7.2013 for specified purposes, **1.4.2014**
in so far as not already in force)». То есть норма действует с передачи потребкредита
от OFT к FCA 01.04.2014.

> **39E.—(1)** **Giving advice to a borrower about the liquidation of a debt due under a credit
> agreement is a specified kind of activity.**
> **(2)** Giving advice to a hirer about the liquidation of a debt due under a consumer hire
> agreement is a specified kind of activity.

Соседняя норма — **art. 39D (debt adjusting)**, дословно:

> **39D.—(1)** When carried on in relation to debts due under a credit agreement—
> (a) negotiating with the lender, on behalf of the borrower, terms for the discharge of a debt,
> (b) taking over, in return for payments by the borrower, that person's obligation to discharge
> a debt, or (c) any similar activity concerned with the liquidation of a debt, is a specified kind
> of activity.

Debt adjusting (39D) нас не касается — мы ни с кем не ведём переговоры от имени пользователя
и не принимаем на себя его обязательств. **Debt counselling (39E) касается прямо.**

### 5.2. Состав debt counselling — PERG 17.2 (дословно)

> **PERG 17.2, Q2.1** What is the basic definition of debt counselling? It involves the following
> elements: (1) It is **advice** given to: (a) a borrower about **the liquidation of a debt** due
> under a credit agreement… (2) The advice must relate to **a particular debt and debtor**…
> (3) It covers the giving of advice. **It does not cover just giving mere information.**
> (4) If an exclusion applies, the activity is not a regulated activity.

🔴 **Обратите внимание, чего в составе НЕТ: требования назвать финансовый инструмент,
продукт, банк или кредитора.** Достаточно «конкретного долга конкретного должника».
Именно здесь наша российская красная линия («не называть финансовый инструмент») **не
работает вовсе** — она защищает от art. 53, но не от art. 39E.

### 5.3. «Liquidation of a debt» — максимально широко, включая штатное погашение

> **PERG 17.3, Q3.1** What does liquidation of a debt mean? **It has a wide meaning.** For example,
> it would cover the following:
> • **paying off the debt in full and in time**;
> • agreeing a rescheduling or a temporary halt to paying off the debt;
> • the debtor being released from the debt;
> • agreeing a reduced repayment amount (including the creditor agreeing to accept token
> repayments);
> • a third party taking over the debtor's obligation to discharge the debt;
> • discharging the debt or making it irrecoverable through personal insolvency procedures such as
> bankruptcy, a voluntary arrangement or a debt relief order.
>
> **Q3.2** … **Debt counselling is not limited to debts that are overdue. It also covers debts that
> are not overdue.** … it would cover present obligations to make payments in the future.

🔴 Два убийственных для нас пункта: (а) «**paying off the debt in full and in time**» —
то есть даже совет о нормальном, не проблемном погашении; (б) **долг не обязан быть
просроченным**. FINPILOT работает именно с непросроченными кредитами и советует их досрочное
погашение — это ядро продукта, и оно целиком внутри определения «liquidation».

### 5.4. Прямые примеры FCA, попадающие в FINPILOT один в один — PERG 17.7

> **Пример (14).** Adviser: “I recommend you prioritise the repayment of your electricity bill over
> all other debts” — **This is likely to constitute debt counselling** if, having considered all of
> a debtor's outstanding debts, an adviser advises the debtor to prioritise the repayment of a
> utility bill … over his other outstanding debts … This constitutes advising on the liquidation of
> debts due, since there is an implied recommendation that the debtor should postpone repaying his
> consumer credit related debts until he has repaid another debt or debts.

🔴 Это **буквально Avalanche-фильтр**: «сначала гасим дорогой кредит, остальные — минимальным
платежом». Приоритизация одного долга над другими = debt counselling.

> **Пример (16).** An adviser gives budgetary advice — **This is debt counselling** if the adviser
> goes beyond the services in example (15) and advises the debtor on **how to match income and
> debts**. For example, the adviser may advise the debtor to reduce discretionary spending to a set
> amount each month to enable him to pay off a certain amount of a large credit card bill each
> month. **It does not matter if the result of the advice is that the debtor should pay off his
> debts in full**, rather than by instalments over a period of time or by entering into some sort
> of repayment plan, as debt counselling is not limited to advice about being released from paying
> the debt in full or rescheduling.

🔴 «Advises the debtor on **how to match income and debts**» — это определение FINPILOT
одной строкой.

Граница, за которой ещё безопасно (**пример (15)** — то, чем мы НЕ являемся):

> **Пример (15).** A person … helps a debtor to draw up a budget, e.g. providing a budget planner
> to see how much disposable income the client has each month or how long the client's money could
> last over a particular period. **This is not debt counselling if all the adviser does is to
> provide a debtor with information about his budget and the process is limited to, and likely to
> be perceived by the debtor as, assisting him to make his own choice** as to a course of action he
> might take in liquidating his consumer credit-related debts. It may not be advice at all, in that
> **it just puts into a convenient form information that the consumer has himself supplied**. …
> as long as the adviser gives the information in a balanced and neutral way, the adviser should
> be seen as providing information rather than advice.

> **Пример (5).** Adviser: “I would recommend that you explore the pros and cons of all the
> different debt solutions that may be available to you” — **This is not debt counselling. It is
> unregulated generic advice** because it does not steer the debtor to any particular course of
> action in liquidating his debts.

> **Пример (4).** Adviser: “I recommend you do not borrow more than you can comfortably afford” —
> **This is not debt counselling as it is about incurring debts, not liquidating them.**

Итого разграничитель UK: **бюджетный планировщик, показывающий цифры = информация (можно);
система, выбирающая за пользователя, сколько и какому долгу направить = debt counselling
(нельзя без лицензии).**

### 5.5. Дерево решений и «interactive software system» — прямо названы

> **PERG 17.5, Q5.5** … If the process involves identifying one or more particular courses of
> action then, in the FCA's view, to avoid debt counselling, the critical factor is likely to be
> whether the process is limited to, and likely to be perceived by the debtor as, assisting the
> debtor to make his own choice of how to liquidate his debts. **The questioner will need to avoid
> making any judgement on the suitability of one or more courses of action for the debtor.**
> …
> (1) The questioner may go on to identify several courses of action which match features
> identified by the scripted questioning; **provided these are presented in a balanced and neutral
> way (for example, they identify all the possible courses of action, without making a
> recommendation as to a particular one) this need not, of itself, involve debt counselling.**
> (2) The questioner may go on to advise the debtor on the merits of one particular course of
> action over another. **This would be debt counselling.**
> …
> (5) The scripted questioning may lead to the identification of one or more particular courses of
> action. **This is likely to be debt counselling.**
>
> **Q5.7** Does the medium used to give advice matter? The medium … should make no material
> difference … Advice can be provided in many ways including: … **• through the provision of an
> interactive software system.**

> **Q5.1** … **advice to opt for one of a number of identified possible debt solutions without
> advising which one of those the client should adopt may, depending on the circumstances, be debt
> counselling.**

> **Q5.4** … the concept of generic advice is potentially relevant to debt counselling. … However,
> as explained in the answer to Q5.1, **advice may be debt counselling even though the advice does
> not identify a course of action with any precision. This narrows the types of advice that will be
> excluded from being debt counselling on the grounds of being generic advice.**

> **Q5.5 (4)** The scripted questioning may not lead to the identification of any particular course
> of action; in this case, the questioner has provided advice, but it is generic advice and does
> not amount to debt counselling. **As explained in the answer to Q5.4 this will be an uncommon
> scenario.**

🔴 Сравните с §3.4: в инвестиционном контуре «опросник без называния инструмента» — **безопасная
generic advice** (PERG 8.30A.7G(3)); в долговом — FCA сама говорит, что аналогичный выход
«**uncommon**», потому что generic-лазейка там сужена. **Симметрии нет.**

### 5.6. Публичность и исключения

> **PERG 17.4, Q4.1** … debt counselling covers giving advice about "a" debt. This means that the
> advice must relate to the debts of a particular debtor or debtors. Advice will normally not be
> covered if it is not given to any particular debtor. So for example, it would not generally cover
> advice in a newspaper… **General advice open to everyone on a website is unlikely to be debt
> counselling for the same reason. On the other hand advice given to a particular debtor over the
> Internet may be regulated.**

Это единственная реальная развилка: обезличенная статья на сайте — можно; персонализированный
вывод конкретному залогиненному пользователю — нельзя. FINPILOT по построению во второй половине.

Перечень исключений (**PERG 17.6, Q6.1**), ни одно из которых нам не подходит:
art. 39H (лицо связано с самим кредитным договором — кредитор/его агент), 39I (энергоснабжающие
организации), 39J (в связи с regulated mortgage contract), 39K (адвокаты и члены юрпрофессии),
72A (**information society services**), 72G (местные власти), 72H (арбитражные управляющие).

🟡 **Article 72A «Information society services» — единственное, что теоретически стоило бы
проверить** для чисто онлайнового продукта, но по существу это реализация принципа страны
происхождения из e-Commerce Directive 2000/31/EC для поставщиков, учреждённых в другом
государстве EEA; после выхода UK из ЕС его применимость к третьим странам сомнительна.
🔴 **Текст art. 72A и PERG 2.9.18G в этой сессии не открывался** — вывод помечен как гипотеза,
не как проверенная норма.

### 5.7. Бесплатный сектор долговых консультаций UK — контекст

Регулируемая деятельность 39E не означает «только за деньги»: бесплатные консультанты
(StepChange, Citizens Advice, National Debtline) тоже авторизованы FCA — либо напрямую,
либо через групповую лицензию. MoneyHelper — бренд государственного Money and Pensions
Service (MaPS). 🔴 **Конкретные реквизиты авторизаций и данные о финансировании бесплатного
сектора в этой сессии не проверялись** — оставлено как контекст, не как факт с реквизитами.

### 3.5. 🔴 Advice Guidance Boundary Review — статус на 09.09.2026: РЕЖИМ УЖЕ ДЕЙСТВУЕТ

Источники: страница FCA «Advice Guidance Boundary Review»
(fca.org.uk/firms/advice-guidance-boundary-review, HTTP 200, «First published: 28/06/2025,
Last updated: 02/03/2026») и **PS25/22 «Supporting consumers' pensions and investment
decisions: rules for targeted support»** (PDF, fca.org.uk/publication/policy/ps25-22.pdf,
HTTP 200, 1 853 149 байт, скачано 09.09.2026).

**Хронология, дословно со страницы FCA:**

> We published our policy statement setting out the near-final rules for targeted support on
> **11 December 2025**. The FCA Board decided to confirm the near-final rules as final on
> **26 February 2026**. … We are now accepting applications for targeted support permissions via
> Connect. … **We expect the targeted support rules to take effect from 6 April 2026.**
> We plan to consult on **simplifying and consolidating our investment advice rules and guidance
> in early 2026.**

Отметка об обновлении страницы: «**02/03/2026: Information changed** Firms can apply for
targeted support permission».

Правовой инструмент: **FCA 2026/5 / FOS 2026/04 «Advice Guidance Boundary Review (Targeted
Support) Instrument»**, дата в имени файла на api-handbook.fca.org.uk — **2026-03-02**.
Новые правила поведения — **COBS 9B**.

**Что такое targeted support — дословно из PS25/22:**

> **§2.6** While targeted support will be **less personalised than individualised advice**, it will
> be capable of reaching a significantly greater number of consumers than current forms of advice.
> We estimate that at least **18 million people** could be offered targeted support within a decade.
>
> **§2.7** … Our framework sets requirements including: • To identify **consumer segments** with
> shared financial support needs or objectives and, where relevant, common characteristics, in
> order to deliver suitable **ready-made suggestions**. …
>
> **§3.14** … firms will have to **pre-define consumer segments**, based on common situations and,
> where relevant, common characteristics. **Pre-defining these elements removes the need for firms
> to assess suitability in real time.** Instead, targeted support is about aligning a consumer with
> a consumer segment.
>
> **§1.7** The Government has confirmed that targeted support will be a **new specified activity**.
> This means that firms will only be able to provide it if they are **authorised** to do so.

🔴 **Три вывода, важных для FINPILOT, и все три неприятные.**

**(1) UK не расширил нелицензируемую зону — он создал ТРЕТИЙ лицензируемый уровень.**
Реформа, задуманная как «закрыть advice gap», кончилась новым specified activity с
собственной авторизацией, собственными правилами COBS 9B и **минимальным капиталом
£500 000** («for a firm with permission to provide targeted support: £500,000», PS25/22).
Ожидание «в зрелых юрисдикциях такие штуки как наша уже разрешили» — **не подтверждается**.

**(2) Направление персонализации в UK ровно ОБРАТНОЕ нашему.** Targeted support легален
потому, что он **менее** персонализирован: сегменты вместо индивидуальной оценки,
преднастроенные «ready-made suggestions» вместо расчёта в реальном времени. FINPILOT —
полностью индивидуальный расчёт в реальном времени. По оси, вдоль которой UK строил
послабление, мы находимся на **дальнем от послабления конце**.

**(3) Предмет targeted support — pensions и retail investments**, то есть тот же
инвестиционный периметр. **На debt counselling (art. 39E) реформа не распространяется**,
и, следовательно, наш долговой блок она никак не облегчает.

Зафиксированное напряжение, прямо названное FCA (PS25/22 §3.13, отзывы на консультацию):

> Eight respondents also noted there was an **inherent tension between artificial intelligence (AI),
> which enables a high degree of personalisation, and the targeted support regime which is based on
> consumer segments with common characteristics.**

Это ровно наш класс продуктов. Регулятор ответил «нам комфортно, режим outcomes-focused»,
то есть **вопрос оставлен открытым**, а не решён в пользу персонализированных алгоритмов.

---

## 4. Advice gap — числа

Все числа ниже — дословно из **PS25/22** (FCA, 11.12.2025 / финальные правила 26.02.2026),
если не указано иное.

> **§1.1** We estimate around **23 million consumers are currently underserved** by the markets
> for advice and guidance.
>
> **§1.2** The 'advice gap' is real. **Less than 1 in 10 people obtain regulated financial advice**
> – many turn to family and friends or social media instead for help. … we also know that consumers
> need more help with their pension decisions with **12.5 million under-saving for retirement**
> (Department for Work and Pensions, 2023)…
>
> **§2.2** Only **9% of adults received regulated financial advice in the 12 months to May 2024**
> about investments, saving into a pension or retirement planning (**Financial Lives 2024 survey**).
> **40% of consumers who don't invest say that a lack of knowledge is a key barrier to investing**
> (Thinks Insight & Strategy, 2025), and **75% of DC pension-holders aged 45+ do not have a clear
> plan** for how to take their money (FLS 2024). … Among **investors aged 18-34, 45% used social
> media to research investing** (FLS 2024).
>
> **§1.3** While there are good sources of free and impartial guidance available, **firms are wary
> of giving consumers specific help or guidance in case it crosses the boundary into advice.
> Many consumers cannot afford comprehensive financial advice and free guidance provides limited
> support.**
>
> **§1.5** In the three years to 2023, UK households allocated on average just **19%** of their
> household financial assets to retail investments…, compared to **EU (38%)** and **US (56%)**
> households (New Financial, 2025).
>
> **§2.6** We estimate that at least **18 million people** could be offered targeted support within
> a decade.

**Стоимость консультации.** По данным государственного MoneyHelper (Money and Pensions Service),
почасовые ставки финансовых консультантов в UK **начинаются от £75/час и доходят до £350+**;
типичная модель — первоначальная комиссия 1–2% от инвестируемой суммы плюс 0,5–1,5% годовых от
AUM. 🟡 Это вторичный источник (сводка MoneyHelper через поисковую выдачу, 09.09.2026);
первичная страница MoneyHelper в этой сессии постранично не открывалась —
число помечено как ориентир, а не как проверенная цифра с реквизитами.

**Что из этого — топливо для продукта, а не для комплаенса:**
§1.3 PS25/22 — это официальное признание регулятора, что **сама нечёткость границы
подавляет предложение**: фирмы не дают помощь из страха перейти границу. Экономический
смысл FINPILOT — занять именно эту пустоту. Но UK показывает, что пустота там не потому,
что никто не догадался, а потому что **вход в неё стоит лицензии и £500 тыс. капитала**.
Российский контур (тема 18) в этом смысле мягче: у нас граница проведена по предмету
и в неё можно войти без лицензии — но только пока мы не назвали инструмент.

---

## 6. Robo-advice: что регуляторы требуют от алгоритма как такового

### 6.1. ЕС — ESMA Guidelines on suitability, редакция 2022

Источник: **ESMA35-43-3172, «Final Report — Guidelines on certain aspects of the MiFID II
suitability requirements», 23 September 2022**, 73 страницы, PDF получен прямым `curl`
(HTTP 200, 627 559 байт, 09.09.2026), разобран `pdftotext`.

Определение робо-совета, дословно (Annex, таблица терминов):

> **Robo-advice** — The provision of investment advice or portfolio management services
> (in whole or in part) **through an automated or semi-automated system used as a client-facing
> tool.**

Статус документа (важно для оценки веса): это **guidelines по ст. 16 ESMA Regulation**, а не
регламент:

> **§7** … In accordance with Article 16(3) of the ESMA Regulation, competent authorities and
> financial market participants shall **make every effort to comply** with guidelines.

🔴 **Guideline 90 — требования к самому алгоритму. Это самое ценное в разделе, потому что
применимо к нам как инженерный стандарт независимо от того, попадаем ли мы под лицензию.**

> **90.** In order to ensure the consistency of the suitability assessment conducted through
> automated tools (even if the interaction with clients does not occur through automated systems),
> firms should **regularly monitor and test the algorithms** that underpin the suitability of the
> transactions recommended… In particular, firms should at least:
> • establish an appropriate **system-design documentation** that clearly sets out the purpose,
> scope and design of the algorithms. **Decision trees or decision rules should form part of this
> documentation**, where relevant;
> • have a **documented test strategy** that explains the scope of testing of algorithms. This
> should include test plans, test cases, test results, defect resolution (if relevant), and final
> test results;
> • have in place appropriate **policies and procedures for managing any changes to an algorithm**,
> including monitoring and keeping records of any such changes. This includes having security
> arrangements in place to monitor and prevent **unauthorised access to the algorithm**;
> • **review and update algorithms** to ensure that they reflect any relevant changes (e.g. market
> changes and changes in the applicable law) that may affect their effectiveness;
> • have in place policies and procedures enabling to **detect any error within the algorithm** and
> deal with it appropriately, including, for example, **suspending the provision of advice** if that
> error is likely to result in an unsuitable advice…;
> • have in place adequate resources, including human and technological resources, to monitor and
> supervise the performance of algorithms…; and
> • have in place an appropriate **internal sign-off process** to ensure that the steps above have
> been followed.

🟢 **Прямая проекция на FINPILOT: значительная часть Guideline 90 у нас уже выполнена** —
документация модели как канона (`docs/math_model.md`), версионирование матмодели по SemVer,
история калибровок (`docs/model/model_history.md`), TDD и CI-гейты (coverage ≥90%,
revision-gate), preflight как внутренний sign-off. **То, чего нет: (а) политики обнаружения
ошибки алгоритма с автоматической приостановкой выдачи рекомендации; (б) политики контроля
несанкционированного доступа к алгоритму как отдельного контура.** Это готовый чеклист
на будущее — независимо от юрисдикции.

**Guideline 108 — требование к людям, а не к коду:**

> **108.** Where relevant, when employing automated tools (including hybrid tools), investment
> firms should ensure that their staff involved in the activities related to the definition of these
> tools: (a) have an appropriate understanding of the technology and algorithms used to provide
> digital advice (particularly they are able to **understand the rationale, risks and rules behind
> the algorithms** underpinning the digital advice); and (b) are able to **understand and review
> the digital/automated advice generated by the algorithms**.

То есть требование объяснимости в ЕС сформулировано не как «объясни пользователю», а как
«**твои сотрудники обязаны понимать и уметь проверить** то, что выдал алгоритм». Для
однопользовательского проекта это переводится в требование к внутренней документации модели.

**Guideline 17 — что раскрывать пользователю робо-советника:**

> **17.** In order to address potential gaps in clients' understanding of the services provided
> through robo-advice, firms should inform clients… on the following:
> • **a very clear explanation of the exact degree and extent of human involvement** and if and how
> the client can ask for human interaction;
> • an explanation that **the answers clients provide will have a direct impact** in determining the
> suitability of the investment decisions recommended…;
> • a description of the **sources of information** used to generate an investment advice… (e.g.,
> if an online questionnaire is used, firms should explain that the responses to the questionnaire
> **may be the sole basis** for the robo-advice or whether the firm has access to other client
> information or accounts);
> • an explanation of **how and when the client's information will be updated**…

🟢 Это отличный **дизайн-чеклист для нашего экрана объяснения рекомендации**, применимый
добровольно: степень участия человека (у нас — ноль), что вход целиком определяет выход,
что источник данных — только введённая пользователем анкета, и когда данные надо обновлять.
Взять целиком в UX-стандарт стоит независимо от регулирования.

### 6.2. Article 54(1) DR 2017/565 и PERG 8.30A.15 — уже приведены выше

Оба регулятора (ЕС и UK) сказали одно и то же двумя формулировками:
«**shall not be reduced by the use of an electronic system**» (§1.5) и «**an element of opinion
and skill (albeit automated)**» (§3.4). 🔴 Это независимое подтверждение находки (2) темы 18
про дисклеймер, но по другой оси: **не только дисклеймер не защищает — автоматизация тоже.**
Трёх юрисдикций достаточно, чтобы считать это устойчивым принципом, а не особенностью
российского регулятора.

### 5.8. 🔴 ЕС: у долгового совета ЕСТЬ свой периметр, и он строже британского по субъекту

Это не было в вопросах темы, но найдено при проверке и меняет вывод по ЕС.
Источник: **Directive (EU) 2023/2225 of 18 October 2023 on credit agreements for consumers
and repealing Directive 2008/48/EC** («CCD II»), текст CELEX 32023L2225, получен через
текстовый прокси `r.jina.ai` (HTTP 200, 207 412 байт, 09.09.2026; прямой `curl` по EUR-Lex
давал 202/0 — см. §1.3).

**Определение, Article 3, point (17):**

> (17) **‘advisory services’ means personal recommendations to a consumer in respect of one or
> more transactions relating to credit agreements** and that constitute a separate activity from
> the granting of a credit and from the credit intermediation activities as set out in point (12);

Обратите внимание на конструкцию: это **дословный клон** Article 4(1)(4) MiFID II, где
«financial instruments» заменено на «**credit agreements**». То есть в ЕС предмет-триггер
для потребкредита прописан отдельным актом, ровно тем же приёмом.

**Определение, Article 3, point (22):**

> (22) **‘debt advisory services’ means personalised assistance of a technical, legal or
> psychological nature provided by independent professional operators** which are not, in
> particular, creditors or credit intermediaries…, in favour of consumers who experience or might
> experience **difficulties in meeting their financial commitments**.

🔴 **Article 16(6) — резервирование деятельности. Это самая жёсткая норма из всех найденных
в теме:**

> **6.** Member States shall ensure that **advisory services may only be provided by creditors and,
> where applicable, credit intermediaries.**
>
> Member States may, by way of derogation from the first subparagraph, allow other persons than
> those referred to in the first subparagraph to provide advisory services where one of the
> following conditions is fulfilled:
> (a) the advisory services are provided **in an incidental manner** in the course of a professional
> activity that is regulated…;
> (b) … by insolvency practitioners…;
> (c) … by **public or voluntary providers of debt advisory services** as referred to in Article 36
> **which do not operate on a commercial basis**;
> (d) the advisory services are provided by persons that are **authorised and supervised by
> competent authorities**.

Что это значит для нас буквально: в ЕС «advisory services» по кредитным договорам — это
**зарезервированная за кредиторами и кредитными посредниками деятельность**. Независимый
коммерческий продукт может её вести только через дерогацию (d) — то есть **будучи
авторизованным и поднадзорным**. Дерогация (c) прямо исключает коммерческую основу,
то есть под неё FINPILOT не подпадает по определению («which do not operate on a commercial
basis»), а мы — коммерческий запуск.

**Требования при оказании advisory services (Article 16(3))** — для сравнения с тем, что
мы уже делаем:

> (a) obtain the necessary information regarding the consumer's **financial situation, preferences
> and objectives** related to the credit agreement, in order … to recommend credit agreements that
> are suitable to the consumer;
> (b) assess the financial situation and the needs of the consumer …, **taking into account
> reasonable assumptions as to the risks to the consumer's financial situation over the term of the
> recommended credit agreement**;
> (c) consider a sufficiently large number of credit agreements in their product range…;
> (d) **act in the best interests of the consumer**; and
> (e) give the consumer a **record of the recommendation** provided, on paper or on another durable
> medium…

**Article 36 — Debt advisory services (обязанность государства, не запрет):**

> **1.** Member States shall ensure that **independent debt advisory services are made available**
> to consumers who experience or might experience difficulties in meeting their financial
> commitments, **with only limited charges payable** for such services.
> **2.** … creditors shall have processes and policies in place for the **early detection** of
> consumers experiencing financial difficulties.
> **3.** Member States shall ensure that creditors **refer** consumers who experience difficulties …
> to debt advisory services easily accessible to the consumer.

**Даты — критично, потому что это ближайший горизонт, а не история. Article 48:**

> **1.** Member States shall adopt and publish, **by 20 November 2025**, the laws, regulations and
> administrative provisions necessary to comply with this Directive. …
> **They shall apply those measures from 20 November 2026.**

И Article 47: «Directive 2008/48/EC is repealed **with effect from 20 November 2026**.»

🔴 **Вывод по датам:** на 09.09.2026 CCD II **транспонирована, но ещё не применяется** —
национальные меры включаются **20.11.2026**, то есть примерно через два месяца после
планового коммерческого запуска FINPILOT. Для внутреннего рынка РФ это безразлично; для
любого сценария выхода в ЕС это означает, что **режим, в который мы бы приходили, — новый
и ужесточающий**, а не старый CCD 2008/48/EC.

🟡 **Существенная неопределённость, которую честнее назвать, чем закрыть.** Является ли
рекомендация «направить свободные деньги на досрочное погашение кредита» «personal
recommendation **in respect of a transaction relating to a credit agreement**» в смысле
Article 3(17)? Досрочное погашение — это исполнение существующего договора, а не заключение
нового; при этом Article 16(3)(c) говорит о рекомендации «credit agreements … from among that
product range», что склоняет к прочтению «советы о ВЫБОРЕ кредита», а не «о погашении
имеющегося». **Толкований национальных регуляторов и разъяснений Комиссии по этому вопросу
в данной сессии не искалось** — вопрос помечен как открытый и как первый кандидат на добор,
если тема выхода в ЕС станет реальной.

🔴 **Не проверялось в этой сессии (и должно быть проверено перед любым выходом на ЕС/UK):**
Directive 2014/17/EU (Mortgage Credit Directive), Article 4(21) — определение «advisory
services» для ипотечного кредита и Article 22 — стандарты для них. Ипотека у нас в контуре
обязательств пользователя присутствует, и MCD, вероятно, содержит аналогичную конструкцию.

---

## 2-бис. ЕС: действующая замена CESR/10-293 — supervisory briefing ESMA 2023

🔴 Заказанный в теме документ **CESR/10-293 не открылся (HTTP 404, три URL, §2.1)**, но найден
и добыт его **действующий преемник, покрывающий ровно те же пограничные случаи**:

**ESMA35-43-3861, «Supervisory briefing on understanding the definition of advice under
MiFID II», 11 July 2023** (PDF, esma.europa.eu, HTTP 200, 864 274 байта, скачано 09.09.2026,
разобрано `pdftotext`).

Связь с CESR/10-293 указана самим ESMA дословно:

> **§2.** In April 2010, CESR (ESMA's predecessor) published a Q&A entitled "Understanding the
> definition of advice under MiFID" [сноска: CESR/10-293] … The CESR document has proven to be a
> useful and valuable supervisory convergence tool over these years and **is still applied by firms
> and national competent authorities (NCAs)**. Considering that the legal definition of investment
> advice has substantially remained unchanged from the MiFID I to the MiFID II framework, ESMA has
> deemed beneficial to **update the content of the CESR document**, in particular in light of the
> evolution of business models and technology (for example, increased use of social media and
> **mobile apps** by firms). … **The content of the above-mentioned CESR document remains largely
> unchanged but is supplemented or further specified on certain aspects by this briefing.**

Статус документа (ниже, чем guidelines):

> **§9.** The content of this supervisory briefing is **not subject to any 'comply or explain'
> mechanism for NCAs and it is not binding**, though it provides a clear indication of the
> expectations around the understanding of investment advice by firms.

**Структура — те самые «пять признаков» из вопроса 1 темы**, официально названные ESMA
«the five key tests for investment advice» (§2, оглавление, диаграмма на стр. 9):
3.1 Does the service constitute a **recommendation**? · 3.2 Is it in relation to one or more
**transactions in financial instruments**? · 3.3 Is it **presented as suitable**? · 3.4 Is it
**based on a consideration of the person's circumstances**? · 3.5 Is it issued **otherwise than
exclusively to the public**? (плюс 3.6 «in his/her capacity as an investor» и 3.7 «as an agent»).

### Что такое generic advice — дословно (§§48–51, 57–58)

> **48.** In contrast, **generic advice about a type of financial instrument and general
> recommendations are not investment advice** under the Directive, **unless they are a part of the
> whole investment advice process** (e.g., information on an **asset allocation** preceding the
> investment advice concerning a portfolio). Acts that are preparatory to the provision of an
> investment service … should be considered as an integral part of that service or activity.
>
> **49.** **Advice that does not relate to a particular investment or investments should be regarded
> as generic advice.** Examples of generic advice may include: • advice on the merits of investing
> in one geographical zone rather than another…; or • advice on the merits of investing in certain
> **asset classes** rather than in others (for example, bonds rather than shares).
>
> **50.** **Recital 15 of the MiFID II Delegated Regulation** states that generic advice about a
> type of financial instrument is generally not considered investment advice for the purposes of
> MiFID II. *(🟡 Текст самого Recital 15 в этой сессии отдельно не сверялся — консолидированная
> выгрузка 02017R0565 через прокси пришла без преамбулы; ссылка приводится по цитате ESMA.)*
>
> **57.** It is possible for a client to ask for and receive information about **different types of
> financial instruments** without advice being given on one or more specific financial instruments.
> …
> **58.** **Advice covering which asset class would be better for an investor would normally qualify
> as generic advice** rather than as investment advice. **If, further to advice regarding an asset
> class being given, the firm also indicates a particular instrument within that asset class then
> this would be regarded as investment advice.**

🟢 **§58 — прямой и лучший ответ ЕС на наш вопрос 2.** «Какой класс активов лучше» = generic
advice = вне периметра. «И вот конкретно этот инструмент внутри класса» = investment advice.
Наша разметка инвестиционного транша (сумма и назначение, без указания во что) стоит
**ровно на разрешённой стороне § 58**, но в одном шаге от запрещённой.

🔴 И встречное ограничение **§48**: generic advice становится частью регулируемой услуги,
если она — подготовительный этап к ней («**unless they are a part of the whole investment
advice process**»). Это близнец британского PERG 8.26.5G. Инженерный вывод один и тот же:
**никаких «а теперь купите вот тут» в продукте, ни своими руками, ни партнёрской ссылкой.**

### Фильтры и сравнивалки — §§36–39

> **36.** The fact that a firm enables a client to **filter** the information that they receive about
> different financial instruments — for example, by choosing from a set of options on a website or
> on an app — **does not automatically mean that a recommendation is being given**…
>
> **38.** **A critical factor would be whether the process is limited to assisting the person to
> make their own choice** of product which has particular features which the person regards as
> important: if this is the case then it is unlikely that the process will involve a personal
> recommendation.
>
> **39.** As an example, **price comparison websites** commonly collect information from clients and
> about their circumstances and allow them to filter the information that they view as a result,
> **without necessarily giving investment advice**… In such cases, **the ability of the client to
> make their own choices about the features they are looking for, and the absence of apparent
> judgement about which features or products they should choose**, would make it unlikely that the
> service offered would be viewed as investment advice.

🔴 Тест §38–39 («клиент делает выбор сам», «отсутствие видимого суждения о том, что ему
следует выбрать») FINPILOT **не проходит**: мы делаем выбор за пользователя и выдаём одну
альтернативу. Совпадает слово в слово с британскими PERG 8.30A.4G и PERG 17.5 Q5.5.
Три регулятора независимо сформулировали один и тот же разграничитель:
**«помогаем выбрать самому» — можно, «выбираем за него» — нельзя.**

---

## 7. США

> Раздел добыт отдельным подагентом (единственный запущенный в теме; потолок канона — два,
> веером не запускались). Материал приводится целиком, без переписывания, как первичный
> по правилу §9 канона FINPILOT. Нумерация внутри раздела — авторская нумерация подагента.


Дата сбора: 09.09.2026. Все нормы проверены на эту дату по источникам, указанным под цитатами.
Правило файла: если источник не открылся — пишем «не открыто, HTTP <код>», пересказ по памяти не допускается.

---

### 1. Investment Advisers Act of 1940, Section 202(a)(11) — определение "investment adviser"

Кодификация: **15 U.S.C. § 80b-2(a)(11)**.
Источник: Legal Information Institute, Cornell Law School, https://www.law.cornell.edu/uscode/text/15/80b-2 (открыто 09.09.2026, HTTP 200).

Дословно (первая, определяющая часть):

> "Investment adviser" means any person who, for compensation, engages in the business of advising others, either directly or through publications or writings, as to the value of securities or as to the advisability of investing in, purchasing, or selling securities, or who, for compensation and as part of a regular business, issues or promulgates analyses or reports concerning securities;

### Трёхэлементный тест (структура нормы)

Из текста прямо вычитываются три кумулятивных элемента:

| Элемент | Формулировка нормы | Проекция на FINPILOT |
|---|---|---|
| (a) compensation | "for compensation" | Выполняется при платной подписке SaaS. Компенсация не обязана быть отдельной платой за совет. |
| (b) engaged in the business | "engages in the business of advising others" / "as part of a regular business" | Выполняется: рекомендация — основная функция продукта, а не побочная. |
| (c) предмет совета | "**as to the value of securities or as to the advisability of investing in, purchasing, or selling securities**" | 🔴 Ключевой элемент. Предмет жёстко ограничен **securities**. |

### Разбор ключевого вопроса: обязателен ли предмет «securities»

Да — обязателен, и это видно из самого текста. Норма не говорит «advising as to financial matters» или «as to personal finances»; оба альтернативных плеча определения (совет и «analyses or reports») привязаны к слову *securities*. Совет о том, как распределить свободный денежный поток между досрочным погашением долга, резервом и целями, **без называния ценных бумаг**, буквальным текстом § 80b-2(a)(11) не покрывается: ни «value of securities», ни «advisability of investing in, purchasing, or selling securities» здесь не затрагиваются.

Оговорка, которую надо держать: SEC исторически трактует элемент (c) расширительно — в частности, совет об **asset allocation** между классами активов SEC рассматривала как совет о ценных бумагах даже без называния конкретных бумаг. Пока не подтверждено дословным источником в этом файле — см. §6 и раздел «Что не добыто».

Практический вывод по FINPILOT: элементы (a) и (b) у нас выполняются, весь периметр держится на элементе (c). Разметка «инвестиционного транша» (сумма и назначение без указания, во что) — это ровно та зона, где элемент (c) может начать выполняться, если появится хоть какое-то указание на классы инструментов. Правило продукта «конкретные бумаги, фонды, банки, вклады, брокеры не называются никогда» — это и есть контроль элемента (c), и он должен быть зафиксирован не как маркетинговое обещание, а как инвариант.

---

### 2. Исключения из 202(a)(11) — дословно

Источник тот же (Cornell LII, 09.09.2026, HTTP 200).
🔴 Внимание: **буквенная нумерация исключений в действующей редакции иная, чем в задании.** Банки — (A), «solely incidental» профессии — (B), брокеры-дилеры — (C), publisher's exclusion — (D). Ниже — как в законе.

> **(A)** a bank, or any bank holding company as defined in the Bank Holding Company Act of 1956 which is not an investment company, except that the term "investment adviser" includes any bank or bank holding company to the extent that such bank or bank holding company serves or acts as an investment adviser to a registered investment company, but if, in the case of a bank, such services or actions are performed through a separately identifiable department or division, the department or division, and not the bank itself, shall be deemed to be the investment adviser;

> **(B)** any lawyer, accountant, engineer, or teacher whose performance of such services is solely incidental to the practice of his profession;

> **(C)** any broker or dealer whose performance of such services is solely incidental to the conduct of his business as a broker or dealer and who receives no special compensation therefor;

> **(D)** the publisher of any bona fide newspaper, news magazine or business or financial publication of general and regular circulation;

> **(E)** any person whose advice, analyses or reports relate to no securities other than securities which are direct obligations of or obligations guaranteed as to principal or interest by the United States, or securities issued or guaranteed by corporations in which the United States has a direct or indirect interest which shall have been designated by the Secretary of the Treasury, pursuant to section 3(a)(12) of the Securities Exchange Act of 1934, as exempted securities for the purposes of that Act;

> **(F)** any nationally recognized statistical rating organization, as that term is defined in section 3(a)(62) of the Securities Exchange Act of 1934, unless such organization engages in issuing recommendations as to purchasing, selling, or holding securities or in managing assets, consisting in whole or in part of securities, on behalf of others;

> **(G)** any family office, as defined by rule, regulation, or order of the Commission, in accordance with the purposes of this subchapter; or

> **(H)** such other persons not within the intent of this paragraph, as the Commission may designate by rules and regulations or order.

### Проекция на FINPILOT

- **(A) банки** — не наш случай, продавца/банка в контуре нет.
- **(B) solely incidental** — не наш случай: мы не юрфирма/бухгалтерия/вуз, для которых совет побочен. Заметить: перечень закрытый (lawyer, accountant, engineer, teacher), «software vendor» в нём нет.
- **(C) broker-dealer** — не применимо, дистрибьютора и комиссий от третьих лиц нет.
- **(D) publisher's exclusion** — единственное исключение, теоретически релевантное софту-«изданию». Но условия жёсткие: *bona fide*, *of general and regular circulation*. Персонализированный расчёт под конкретного пользователя эту дверь закрывает — см. §3 (Lowe).
- **(E)** — не наш случай (мы не про госбумаги США).

Вывод: **ни одно исключение не является для FINPILOT надёжной опорой.** Периметр надо держать на элементе (c) самого определения (нет совета о securities), а не на исключениях.

---

### 3. Lowe v. SEC, 472 U.S. 181 (1985) — где Верховный суд провёл границу

Источник: Legal Information Institute, Cornell Law School, https://www.law.cornell.edu/supremecourt/text/472/181 (открыто 09.09.2026, HTTP 200).
Justia (supreme.justia.com/cases/federal/us/472/181/) — **не открыто, HTTP 403**, и через текстовый прокси r.jina.ai тоже пусто; цитаты взяты у Cornell.

Дословно, из мнения большинства:

> "The Act was designed to apply to those persons engaged in the investment-advisory profession—those who provide personalized advice attuned to a client's concerns" — 472 U.S. at 211.

> "The mere fact that a publication contains advice and comment about specific securities does not give it the personalized character that identifies a professional investment adviser" — 472 U.S. at 211.

> "petitioners' publications do not fit within the central purpose of the Act because they do not offer individualized advice attuned to any specific portfolio or to any client's particular needs. On the contrary, they circulate for sale to the public at large in a free, open market" — 472 U.S. at 211.

> "those words describe the publication rather than the character of the publisher; hence Lowe's unsavory history does not prevent his newsletters from being 'bona fide'" — 472 U.S. at 212.

> Publications with "general and regular" circulation "would not include 'people who send out bulletins from time to time on the advisability of buying and selling stocks,' or 'hit and run tipsters'" — 472 U.S. at 209.

> Holding: "petitioners' publications fall within the statutory exclusion for bona fide publications and that none of the petitioners is an 'investment adviser' as defined in the Act" — 472 U.S. at 213.

### Разбор — 🔴 это самый важный пункт файла для FINPILOT

Линия Lowe проведена **по персонализации, а не по предмету**. Суд не говорит «это не про ценные бумаги, значит не советник»; он говорит: издание не персонализировано, не привязано к конкретному портфелю и конкретным нуждам клиента — значит publisher's exclusion работает.

Отсюда прямое следствие для нас: **FINPILOT — ровно противоположный полюс шкалы Lowe.** Мы принимаем доходы, расходы, кредиты со ставками, активы и цели конкретного человека и выдаём ОДНУ рекомендацию, рассчитанную под него. Это буквально "individualized advice attuned to any specific portfolio or to any client's particular needs" и "personalized advice attuned to a client's concerns". Значит:

1. **Publisher's exclusion (D) для FINPILOT недоступен в принципе.** Ни «наш продукт — это калькулятор/публикация», ни «алгоритм, а не человек» его не открывают: Lowe разграничивает не по автоматизации, а по персонализации, и мы на «плохой» стороне линии.
2. Единственная защита США-периметра остаётся прежней и единственной: **предмет совета не securities** (элемент (c) §80b-2(a)(11)). То есть периметр держится на product-инварианте, а не на юридическом исключении.
3. Практический риск-вектор: любое движение продукта в сторону «во что вложить инвестиционный транш» одновременно (а) включает элемент (c) и (б) не может быть погашено исключением (D), потому что совет персонализирован. Это делает инвариант «не называем инструменты» единственной точкой отказа в США — и её надо тестировать как жёсткое ограничение модели, а не как редакционную политику.

---

### 5. SEC IM Guidance Update No. 2017-02 "Robo-Advisers" (Division of Investment Management, February 2017)

Источник: https://www.sec.gov/investment/im-guidance-2017-02.pdf — прямой `curl` с браузерным UA дал **HTTP 403**; взято через текстовый прокси `https://r.jina.ai/...` (HTTP 200, 09.09.2026), 15 страниц.

### Кому адресовано — дословно

> "Robo-advisers, which are typically **registered investment advisers**, use innovative technologies to provide discretionary asset management services to their clients through online algorithmic-based programs. A client that wishes to utilize a robo-adviser enters personal information and other data into an interactive, digital platform (e.g., a website and/or mobile application). Based on such information, the robo-adviser generates a portfolio for the client and subsequently manages the client's account." (стр. 1)

> "Robo-advisers, like all registered investment advisers, are subject to the substantive and fiduciary obligations of the Advisers Act. Because robo-advisers rely on algorithms, provide advisory services over the internet, and may offer limited, if any, direct human interaction to their clients, their unique business models may raise certain considerations when seeking to comply with the Advisers Act."

### Три области — дословно

> "This guidance focuses on three distinct areas identified by the Staff, listed below, and provides suggestions on how robo-advisers may address them:
> 1. The substance and presentation of **disclosures** to clients about the robo-adviser and the investment advisory services it offers;
> 2. The **obligation to obtain information from clients** to support the robo-adviser's duty to provide suitable advice; and
> 3. The adoption and implementation of **effective compliance programs** reasonably designed to address particular concerns relevant to providing automated advice."

### Suitability — дословно

> "An investment adviser's fiduciary duty includes an obligation to act in the best interests of its clients and to provide only suitable investment advice. Consistent with these obligations, an investment adviser must make a reasonable determination that the investment advice provided is suitable for the client based on the client's financial situation and investment objectives."

> Робо-советник должен рассмотреть: "Whether the questions elicit sufficient information to allow the robo-adviser to conclude that its initial recommendations and ongoing investment advice are suitable and appropriate for that client based on his or her financial situation and investment objectives"; "Whether the questions in the questionnaire are sufficiently clear..."; "Whether steps have been taken to address inconsistent client responses, such as: — Incorporating into the questionnaire design features to alert a client when his or her responses appear internally inconsistent and suggest that the client may wish to reconsider such responses; or — Implementing systems to automatically flag apparently inconsistent information provided by a client for review or follow-up by the robo-adviser."

### Требования к раскрытию алгоритма — дословно (выборка, релевантная нам)

> "• A description of the particular risks inherent in the use of an algorithm to manage client accounts (e.g., that the algorithm might rebalance client accounts without regard to market conditions...);
> • A description of any circumstances that might cause the robo-adviser to override the algorithm used to manage client accounts...;
> • A description of any involvement by a third party in the development, management, or ownership of the algorithm..., including an explanation of any conflicts of interest such an arrangement may create...;
> • An explanation of the degree of human involvement in the oversight and management of individual client accounts...;
> • A description of **how the robo-adviser uses the information gathered from a client to generate a recommended portfolio and any limitations** (e.g., if a questionnaire is used, that the responses to the questionnaire may be the sole basis for the robo-adviser's advice...); and
> • An explanation of how and when a client should update information he or she has provided to the robo-adviser."

### 🔴 Прямое попадание в наш продукт — предупреждение о введении в заблуждение

> "Robo-advisers should be careful not to mislead clients by implying, for example, that: • The robo-adviser is providing a **comprehensive financial plan if it is not in fact doing so** (e.g., if the robo-adviser does not take into consideration a client's tax situation or **debt obligations**, or if the investment advice is only targeted to meet a **specific goal — such as paying for a large purchase or college tuition — without regard to the client's broader financial situation**);"

### Разбор для FINPILOT

1. Guidance Update 2017-02 адресован **зарегистрированным** советникам: он не расширяет определение из §202(a)(11), а объясняет, как ему соответствовать. Формально он к нам не применяется, пока мы не подпадаем под определение. Но как **инженерный стандарт качества алгоритмического совета** он релевантен целиком, и планка «Т-Банк/Сбер/Альфа» ему соответствует по смыслу.
2. Прямо переносимо на FINPILOT без всякой регистрации:
   - раскрывать, **как** входные данные превращаются в рекомендацию и каковы ограничения (у нас — 66 альтернатив, шаг 10%, четыре критерия, веса риск-профиля; это и есть требуемое "how ... uses the information gathered ... and any limitations");
   - раскрывать, что ответы анкеты — единственная основа совета;
   - раскрывать обстоятельства, при которых алгоритм переопределяется (у нас — кризисный режим и жёсткие ограничения Rt≥0, ПДН≤0.40);
   - ловить **внутренне противоречивые ответы** пользователя и подсвечивать их, а не молча считать;
   - говорить пользователю, когда обновлять входные данные.
3. Обратной стороной: наш продукт как раз **учитывает debt obligations** и широкую картину — то есть по этому абзацу мы на «хорошей» стороне. Но зеркальный риск для нас — обещать «comprehensive financial plan», не учитывая налоги; формулировки маркетинга должны быть уже фактического охвата модели.

---

### 4. Regulation Best Interest (Release No. 34-86031, June 5, 2019) и Form CRS

Источник: SEC Small Entity Compliance Guide, https://www.sec.gov/info/smallbus/secg/regulation-best-interest (открыто 09.09.2026, HTTP 200).

Дословно о сфере действия:

> "Regulation Best Interest ... establishes a new standard of conduct under the Securities Exchange Act of 1934 ... for **broker-dealers and natural persons who are associated persons of a broker-dealer** ... when making a recommendation of **any securities transaction or investment strategy involving securities** (including account recommendations) to a **retail customer**."

> "Regulation Best Interest does not apply to investment advice provided to a retail customer by a dual-registrant when acting in the capacity of an investment adviser."

Дата принятия — June 5, 2019.

### Разбор для FINPILOT

Reg BI навешивается на **статус** (broker-dealer / его associated person) плюс **предмет** (securities transaction or investment strategy involving securities). У FINPILOT нет ни того, ни другого: мы не брокер-дилер, дистрибьютора и комиссий от третьих лиц в контуре нет, ценные бумаги не называются.

Вывод: **Reg BI к тому, кто не является ни брокером-дилером, ни зарегистрированным советником, не применяется.** Form CRS — производная обязанность тех же зарегистрированных лиц (Form ADV Part 3 / Form CRS сдают зарегистрированные BD и RIA), и без регистрации обязанности её подавать не возникает.

🔴 Но заметить механизм: Reg BI ловит не только сделку, но и "**investment strategy involving securities**", то есть стратегию, а не конкретную бумагу. Это тот же вектор риска, что и в §1: если продукт когда-нибудь начнёт советовать не «сколько», а «во что» — даже на уровне классов активов, без имён — «стратегия, включающая ценные бумаги» становится вероятной квалификацией.

---

### 6. Практический вопрос: советник ли приложение, которое не называет бумаг; и регулирование совета о погашении долга

### 6.1. Федеральный уровень (SEC): совет о погашении долга

Совет «направь свободные деньги на досрочное погашение кредита / в резерв» не затрагивает ни "value of securities", ни "advisability of investing in, purchasing, or selling securities" (§80b-2(a)(11), цитата в §1). Федерального регулятора персональных финансовых советов как таковых в США нет — SEC регулирует только инвестиционную часть.

⚠️ **Не добыто дословно:** SEC no-action letters и staff guidance конкретно про budgeting / financial-wellness приложения, а также публикации Morrison Foerster / Ropes & Gray / Davis Polk / Skadden / Sidley по вопросу "is a financial planning tool an investment adviser". Бюджет действий исчерпан раньше. Это открытая позиция — см. финальный раздел.

### 6.2. 🔴 Уровень штатов: debt adjusting / debt-management services — вот ближайший аналог британского art. 39E

Это **не** SEC-периметр, а лицензирование штатов, и именно оно, а не Advisers Act, — реальный американский аналог британского art. 39E (debt counselling).

**(1) Юта — Uniform Debt-Management Services Act (UDMSA), кодифицирован как Utah Code Title 13, Chapter 42.**
Источник: Justia, 2025 Utah Code, UT Code § 13-42-102 (2025), https://law.justia.com/codes/utah/title-13/chapter-42/section-102/ (открыто 09.09.2026, HTTP 200 через r.jina.ai).

Дословно, определение из UDMSA:

> "(9) **'Debt-management services' means services as an intermediary between an individual and one or more creditors of the individual for the purpose of obtaining concessions**, but does not include: (a) legal services provided in an attorney-client relationship if: (i) the services are provided by an attorney who: (A) is licensed or otherwise authorized to practice law in this state; and (B) provides legal services in representing the individual in the individual's relationship with a creditor; and (ii) there is no intermediary between the individual and the creditor other than the attorney...; (b) accounting services provided in an accountant-client relationship..."

> "(7) **'Concessions' means assent to repayment of a debt on terms more favorable to an individual than the terms of the contract** between the individual and a creditor."

> "(14) **'Plan' means a program or strategy in which a provider furnishes debt-management services to an individual and which includes a schedule of payments** to be made by or on behalf of the individual and used to pay debts owed by the individual."

> "(16) **'Provider' means a person that provides, offers to provide, or agrees to provide debt-management services directly or through others.**"

**Разбор:** UDMSA-определение построено на двух признаках — (а) быть **посредником между человеком и кредитором** и (б) добиваться **уступок** (concessions) от кредитора. FINPILOT не является посредником: с кредиторами мы не контактируем, уступок не добиваемся, платежи через себя не проводим. По UDMSA-редакции штата типа Юты **мы вне периметра**, и это устойчивый вывод, потому что оба признака отсутствуют, а не один.

**(2) 🔴 Вашингтон — RCW 18.28.010, редакция БЕЗ признака посредничества, и это опасная редакция.**
Источник: Washington State Legislature, RCW 18.28.010, https://app.leg.wa.gov/rcw/default.aspx?cite=18.28.010 (открыто 09.09.2026, HTTP 200 через r.jina.ai).

Дословно:

> "(2) **'Debt adjusting' means the managing, counseling, settling, adjusting, prorating, or liquidating of the indebtedness of a debtor, or receiving funds for the purpose of distributing said funds among creditors in payment or partial payment of obligations of a debtor.**"

> "(1) **'Debt adjuster'**, which includes any person known as a debt pooler, debt manager, debt consolidator, debt prorater, or credit counselor, **is any person engaging in or holding himself or herself out as engaging in the business of debt adjusting for compensation.** The term shall not include: (a) Attorneys-at-law, escrow agents, accountants, broker-dealers in securities, or investment advisors in securities, while performing services solely incidental to the practice of their professions; (b) Any person, partnership, association, or corporation doing business under and as permitted by any law of this state or of the United States relating to banks, consumer finance businesses...; (c) Persons who, as employees on a regular salary or wage of an employer not engaged in the business of debt adjusting, perform credit services for their employer; (d) Public officers while acting in their official capacities and persons acting under court order; (e) Any person while performing services incidental to the dissolution, winding up or liquidation of a partnership, corporation, or other business enterprise; (f) Nonprofit organizations dealing exclusively with debts owing from commercial enterprises to business creditors; (g) Nonprofit organizations engaged in debt adjusting and which do not assess against the debtor a service charge in excess of fifteen dollars per month."

> "(3) 'Debt adjusting agency' is any partnership, corporation, or association engaging in or holding itself out as engaging in the business of debt adjusting."

**Разбор — это главный операционный риск США по FINPILOT, и он НЕ в SEC.**
Вашингтонское определение шире UDMSA сразу по двум осям:
- признака «посредник между должником и кредитором» **нет**: достаточно "managing, **counseling**, ... **prorating** ... of the indebtedness of a debtor";
- «получение средств для распределения кредиторам» — это **альтернативное** плечо через "or", а не обязательный элемент.

Наш Avalanche-фильтр долгов, который берёт список кредитов со ставками и выдаёт, какой гасить досрочно и на какую сумму, буквально ложится на "counseling ... or prorating ... of the indebtedness of a debtor", а подписка даёт "for compensation". Ни одно из исключений (a)–(g) нам не подходит: мы не адвокаты и не бухгалтеры (и услуга у нас не "solely incidental"), не банк, не работодатель должника, не некоммерческая организация.

Практический вывод: **при выходе на рынок США периметр закрывается не одним анализом Advisers Act, а поштатным обзором debt adjusting / debt-management licensing.** Штаты сильно расходятся: часть приняла UDMSA (узкое определение через посредничество и concessions), часть держит старые широкие законы типа вашингтонского, часть вообще запрещает коммерческий debt adjusting. Это тот же тип риска, что и art. 39E в UK, но помноженный на 50 юрисдикций.

**(3) Третий штат — не добыто.** Бюджет действий. Кандидаты для добора: Georgia (O.C.G.A. § 18-5-1 и след., исторически запрет коммерческого debt adjusting), Delaware (принял UDMSA), Rhode Island, Colorado (принял UDMSA).

---

### 5-бис. SEC и AI / predictive data analytics в советах — судьба предложения 2023 года

Проверено 09.09.2026.

- **Предложение:** "Conflicts of Interest Associated with the Use of Predictive Data Analytics by Broker-Dealers and Investment Advisers", опубликовано в Federal Register **09.08.2023** (файл рулмейкинга S7-12-23, RIN 3235-AN14). Источник: https://www.federalregister.gov/documents/2023/08/09/2023-16377/conflicts-of-interest-associated-with-the-use-of-predictive-data-analytics-by-broker-dealers-and
- **Судьба:** 🔴 **ОТОЗВАНО.** "Notice of Withdrawal of Proposed Regulatory Actions", Release No. 33-11377, опубликовано в Federal Register **17.06.2025**: Комиссия отзывает уведомления о предлагаемом нормотворчестве и **не намерена принимать по ним финальные правила**; если решит вернуться к теме — выпустит новое предложение. Источники: https://www.sec.gov/files/rules/final/2025/33-11377.pdf и https://www.federalregister.gov/documents/2025/06/17/2025-11110/withdrawal-of-proposed-regulatory-actions
- **Статус на 09.09.2026:** нового предложения по PDA не обнаружено в рамках этого бюджета поиска; дословный текст релиза 33-11377 в этом файле не воспроизведён (см. «Что не добыто»).

**Разбор:** специального федерального режима для «ИИ/алгоритма в финансовом совете» в США на сегодня **нет**. Даже если бы правило приняли, оно распространялось бы на broker-dealers и investment advisers — то есть на статус, которого у FINPILOT нет. Для нас это значит: американский периметр по-прежнему определяется §202(a)(11) плюс лицензированием штатов, а не «регулированием ИИ».

---

### 7. "Investment adviser" против "financial planner"

Позиция по добытым в этом файле источникам:

1. §80b-2(a)(11) (дословно в §1) определяет регулируемое лицо **через предмет — securities**. Термина "financial planner" в определении нет вовсе.
2. Reg BI (дословно в §4) навешивается на broker-dealers и их associated persons при рекомендации securities transaction or investment strategy involving securities. Термина "financial planner" нет.
3. Guidance Update 2017-02 (§5) прямо предупреждает робо-советников не создавать впечатление, что они дают "**a comprehensive financial plan if it is not in fact doing so**" — то есть SEC регулирует их как советников по ценным бумагам, а «финансовый план» рассматривает как **маркетинговое утверждение, требующее правдивости**, а не как отдельный лицензируемый вид деятельности.

Отсюда следует вывод, стандартно принятый в отрасли: **федерального лицензирования «финансовых планировщиков» как профессии в США нет; регулируется только инвестиционная (securities) составляющая их работы, а CFP — частная сертификация CFP Board, а не государственная лицензия.**

⚠️ Часть про CFP Board дословным источником в этом файле **не подтверждена** — не хватило бюджета действий. Утверждения (1)–(3) подтверждены дословно, вывод про отсутствие федеральной лицензии планировщика следует из них логически, но прямой цитаты «financial planners are not federally licensed» здесь нет.

---

### Итоговая рамка периметра США для FINPILOT

1. **Advisers Act — вероятнее всего мимо, но по одной-единственной причине:** элемент (c) определения требует предмета *securities*, а мы бумаг не называем. Компенсация и «engaged in the business» у нас выполняются.
2. **Publisher's exclusion (D) нам недоступен** — Lowe провёл линию по персонализации, а мы максимально персонализированы.
3. **Reg BI и Form CRS не применяются** — нет статуса BD/RIA и нет securities.
4. **Guidance 2017-02 формально не наш**, но это готовый чек-лист качества: раскрыть логику алгоритма, его ограничения, случаи переопределения, ловить противоречивые ответы, говорить, когда обновлять данные.
5. **Специального AI-режима нет** — предложение по predictive data analytics отозвано 17.06.2025.
6. 🔴 **Настоящий американский риск лежит не в SEC, а в лицензировании штатов по debt adjusting.** Вашингтонское "debt adjusting" = "managing, **counseling** ... or **prorating** ... of the indebtedness of a debtor" **for compensation**, без требования посредничества — это прямое попадание нашего Avalanche-фильтра. UDMSA-штаты (Юта) безопаснее: там нужен признак посредничества между должником и кредитором и добывание concessions, чего у нас нет.
7. **Точка отказа продукта одна и та же во всех разделах:** инвариант «конкретные инструменты не называются». Он должен быть тестируемым ограничением модели и текстов, а не редакционной привычкой.

---

### Что не добыто и почему

| Пункт | Что именно | Причина |
|---|---|---|
| 3 | Lowe v. SEC на supreme.justia.com | **HTTP 403** при WebFetch; через `r.jina.ai` пустой ответ (288 байт). Цитаты взяты у Cornell LII (HTTP 200), поэтому пункт закрыт. |
| 3 | Точная формулировка про "person-to-person" отношения в Lowe | Не найдена в выдаче Cornell в пределах бюджета. Формулировки про "personalized" / "individualized advice" добыты дословно и линию проводят. |
| 5 | Прямая загрузка im-guidance-2017-02.pdf с sec.gov | `curl` с браузерным UA — **HTTP 403**. Обойдено через `r.jina.ai` (HTTP 200), содержимое добыто. |
| 5-бис | Дословный текст Release No. 33-11377 (отзыв PDA-предложения) | Не открывался — исчерпан бюджет действий (15). Факт и дата (17.06.2025) подтверждены выдачей поиска по sec.gov / federalregister.gov, но не дословной цитатой из релиза. |
| 6.1 | SEC no-action letters и staff guidance по budgeting / financial-wellness приложениям; публикации Morrison Foerster, Ropes & Gray, Davis Polk, Skadden, Sidley по вопросу "is a financial planning tool an investment adviser" | Не искались — исчерпан бюджет действий. **Самая существенная лакуна:** именно здесь лежит отраслевая практика применения элемента (c) к asset allocation без называния бумаг. |
| 6.2 | Третий штат с нормой о debt adjusting | Бюджет. Добыты два: Utah (UDMSA) и Washington. Кандидаты: Georgia, Delaware, Rhode Island, Colorado. |
| 6.2 | Официальный текст UDMSA (2005/2011) с uniformlaws.org | Не открывался; вместо него — кодификация UDMSA в праве штата Юта (Justia, HTTP 200), что для проекции нормы равноценно. |
| 7 | Дословное подтверждение статуса CFP Board как частной сертификации | Бюджет. Вывод сделан из добытых источников логически, прямой цитаты нет. |
---

## 8. Итог для FINPILOT

### 8.1. Сравнительная таблица: где попадаем, где нет, и какое свойство решающее

| Юрисдикция и контур | Норма-триггер (реквизиты) | Решающее свойство | FINPILOT |
|---|---|---|---|
| **РФ, инвестсоветник** | ст. 6.1 п. 1, ст. 6.2 п. 5 39-ФЗ (ред. 04.08.2026); Базовый стандарт, протокол ЦБ КФНП-37 от 16.11.2023 | **Предмет**: названная ценная бумага / ПФИ + планируемая сделка (тема 18) | 🟢 **ВНЕ** |
| **РФ, долговой контур** | отдельного лицензируемого состава «совет о погашении долга» не выявлено (тема 18) | — | 🟢 **ВНЕ** |
| **ЕС, investment advice** | Art. 4(1)(4) Dir. 2014/65/EU (конс. 28.03.2024) + Art. 9 DR (EU) 2017/565 (конс. 02.08.2022) | **Предмет**: «**a particular** financial instrument» из закрытого перечня Annex I Section C | 🟢 **ВНЕ** |
| **ЕС, advisory services по кредиту** | Art. 3(17) + **Art. 16(6)** Dir. (EU) 2023/2225 (CCD II); применяется **с 20.11.2026** | **Персонализация + предмет «credit agreements»**; деятельность **зарезервирована** за кредиторами и кредитными посредниками | 🔴 **ВЕРОЯТНО ВНУТРИ** (см. 8.3) |
| **UK, advising on investments** | art. 53(1) RAO, S.I. 2001/544; PERG 8.24.2G | **Предмет**: «**a particular** investment». Персонализация **нерелевантна** для неавторизованного лица (PERG 8.24.1D G) | 🟢 **ВНЕ** |
| **UK, debt counselling** | **art. 39E RAO** (введена S.I. 2013/1881, в силе с 01.04.2014); PERG 17 | **Персонализация + конкретный долг конкретного должника**. Инструмент называть **не требуется**. «Liquidation» включает «paying off the debt in full and in time» | 🔴 **ВНУТРИ** |
| **UK, targeted support** | новая specified activity; PS25/22, FCA 2026/5, правила COBS 9B, **в силе с 06.04.2026** | Сегменты вместо индивидуальной оценки; отдельная авторизация + **£500 000** мин. капитала | ⚫ **не наш путь** — режим строится на МЕНЬШЕЙ персонализации |
| **US, Advisers Act** | 15 U.S.C. § 80b-2(a)(11) | **Предмет**: *securities*. Publisher's exclusion (D) закрыт по **Lowe v. SEC, 472 U.S. 181 (1985)** — линия по персонализации | 🟢 **ВНЕ** (на одном элементе) |
| **US, Reg BI** | Release 34-86031 (05.06.2019) | **Статус** BD/associated person + предмет securities | 🟢 **ВНЕ** |
| **US, debt adjusting штатов** | напр. **RCW 18.28.010 (Washington)**: «managing, **counseling**, settling, adjusting, **prorating**, or liquidating of the indebtedness of a debtor» for compensation | **Действие над долгами за вознаграждение**; посредничество с кредитором **не требуется** | 🔴 **ВЕРОЯТНО ВНУТРИ** в широких штатах; 🟢 вне в UDMSA-штатах (Utah: нужны посредничество + concessions) |

### 8.2. 🔴 Прямой ответ: совпадает ли красная линия темы 18 с мировой

**Совпадает ровно наполовину, и не совпадающая половина — та, на которой стоит ядро продукта.**

**Совпадает — в инвестиционном контуре, и совпадает поразительно точно.** Четыре юрисдикции
независимо провели одну и ту же линию по ПРЕДМЕТУ:
РФ — «описание ценной бумаги и планируемой с ней сделки» (39-ФЗ ст. 6.2 п. 5);
ЕС — «**a particular** financial instrument» (Art. 9 DR 2017/565);
UK — «**a particular** investment» (art. 53(1)(b)(i) RAO, PERG 8.24.2G(2));
США — «*securities*» (§ 80b-2(a)(11)).
Наш инвариант «конкретные бумаги, фонды, банки, брокеры не называются» защищает нас
во всех четырёх. Более того, **ESMA прямо благословила ровно нашу конструкцию**:
«Advice covering which asset class would be better for an investor would normally qualify as
**generic advice**» (ESMA35-43-3861, §58), а FCA прямо назвала «**financial planning**» примером
нерегулируемого generic advice (PERG 8.26.2G(1)).

**НЕ совпадает — в долговом контуре, и там линия ГОРАЗДО строже.** В РФ (тема 18) отдельного
периметра для совета о погашении долга нет, поэтому «предметная» красная линия закрывает всё.
За рубежом такой периметр есть, он **отдельный от инвестиционного**, и триггер у него другой:

> **не «названный инструмент», а «персонализированный совет по конкретному долгу конкретного
> должника».**

UK art. 39E + PERG 17: «liquidation» включает штатное досрочное погашение непросроченного
кредита (Q3.1, Q3.2); приоритизация одного долга над другими — debt counselling (пример 14);
«advises the debtor on **how to match income and debts**» — debt counselling (пример 16);
«**through the provision of an interactive software system**» — тоже способ дать совет (Q5.7).
ЕС CCD II Art. 16(6) — деятельность зарезервирована за кредиторами. США — лицензирование
штатов (WA: «counseling ... or prorating ... of the indebtedness ... for compensation»).

**Практический вывод, который нужно знать заранее (это и просила тема):**
🔴 **Наша российская красная линия достаточна для РФ и для инвестиционного контура всего мира,
но НЕ достаточна для выхода за рубеж.** При выходе на UK, ЕС или США долговой блок FINPILOT —
Avalanche-фильтр, приоритизация досрочного погашения, расчёт «сколько на какой кредит» —
требует **отдельного основания**, которого «мы не называем инструменты» не даёт.
Варианты, если такой выход когда-нибудь встанет: (а) авторизация по art. 39E / дерогация
Art. 16(6)(d) CCD II — то есть лицензия; (б) выключение долгового движка в зарубежной сборке
и превращение его в «budget planner» уровня примера (15) PERG 17.7 — балансированная нейтральная
подача всех вариантов без выбора одного; (в) отказ от рынка. Третьего пути «дисклеймером»
или «алгоритмичностью» нет — см. 8.4.

### 8.3. Открытый вопрос, который честнее назвать, чем закрыть

Является ли «направить X ₽ на досрочное погашение кредита» «personal recommendation **in respect
of one or more transactions relating to credit agreements**» (Art. 3(17) CCD II)? Текст читается
двояко: досрочное погашение — исполнение существующего договора, а Art. 16(3)(c) говорит о
рекомендации «credit agreements … from among that product range», то есть о выборе кредита.
Британский регулятор в аналогичной ситуации ответил однозначно «да, включая штатное погашение»
(PERG 17.3 Q3.1). Разъяснений Комиссии и национальных регуляторов по CCD II в этой сессии
не искалось. **Помечено как открытое, приоритет добора — только если появится сценарий ЕС.**

### 8.4. Три принципа, подтверждённые независимо в трёх-четырёх юрисдикциях

**(1) Дисклеймер не защищает.** РФ — признак ИИР работает «независимо от наличия дисклеймера»
(тема 18); ЕС — ESMA §§14–15 (тема 18); UK — PERG 8.28.2G(5)(a) «Advice can still be regulated
advice if the person receiving the advice is free to follow or disregard the advice».

**(2) Автоматизация не защищает.** ЕС — Art. 54(1) DR 2017/565: «shall **not be reduced by the
use of an electronic system**»; UK — PERG 8.30A.15G(2): «an element of opinion and skill
(**albeit automated**)» и PERG 17.5 Q5.7 «through the provision of an interactive software
system»; США — Lowe провёл линию по персонализации, не по способу производства совета.
🔴 **Это независимое подтверждение находки (2) темы 18 по другой оси и делает её общим
принципом, а не особенностью ЦБ РФ.**

**(3) Разграничитель везде один и тот же и формулируется почти дословно одинаково:
«помогаем выбрать самому» — можно, «выбираем за него» — нельзя.**
ESMA §38: «whether the process is limited to **assisting the person to make their own choice**»;
FCA PERG 8.30A.4G(2): «limited to … **assisting the person to make their own choice** …
The questioner will need to **avoid providing any judgment on the suitability**»;
FCA PERG 17.5 Q5.5: «limited to … **assisting the debtor to make his own choice** …
avoid making any judgement on the **suitability** of one or more courses of action».
🔴 **FINPILOT по построению стоит на запрещённой стороне этой формулировки во всех трёх
редакциях: мы отсекаем 65 альтернатив из 66 и выдаём одну.** Это не дефект реализации, это
и есть продукт. Значит, единственная защита — предметная, и её границы описаны выше.

### 8.5. Что взять в работу независимо от юрисдикции (это не комплаенс, это качество)

- **ESMA Guideline 90** как чеклист инженерной зрелости алгоритма советующей системы:
  system-design documentation с decision rules · документированная стратегия тестирования ·
  управление изменениями алгоритма с записями · контроль несанкционированного доступа ·
  **детекция ошибки алгоритма с приостановкой выдачи рекомендации** · внутренний sign-off.
  🟢 У нас закрыто: канон модели, SemVer, model_history, TDD, CI-гейты, preflight.
  🔴 Не закрыто: политика «обнаружили ошибку модели → выдача рекомендаций приостановлена»
  и контур защиты алгоритма от несанкционированного изменения.
- **ESMA Guideline 17 + SEC Guidance 2017-02** как чеклист экрана объяснения рекомендации:
  степень участия человека (у нас — ноль) · что ответы пользователя напрямую определяют вывод ·
  что анкета — единственный источник данных · когда данные надо обновить · при каких
  обстоятельствах алгоритм переопределяется (у нас — жёсткие инварианты Rt≥0 и ПДН≤0.40) ·
  **подсветка внутренне противоречивых ответов пользователя вместо молчаливого расчёта**.
- **SEC Guidance 2017-02** о честности охвата: не заявлять «comprehensive financial plan»,
  если налоги в модели не учтены. Формулировки маркетинга должны быть **уже** фактического
  охвата модели.

---

## Что не добыто и почему

| № вопроса | Что именно | Код ответа / причина |
|---|---|---|
| 1, 2 | **CESR/10-293** «Understanding the definition of advice under MiFID» (апрель 2010) | **HTTP 404** по трём URL на esma.europa.eu (`/sites/default/files/library/2015/11/10_293.pdf`, `/system/files/10_293.pdf`, `/sites/default/files/library/10_293.pdf`) и **404** на странице документа. Библиотека CESR при миграции сайта ESMA утрачена по этим адресам. 🟢 **Компенсировано полностью**: добыт официальный преемник **ESMA35-43-3861 (11.07.2023)**, который сам заявляет, что «content of the above-mentioned CESR document remains largely unchanged» (§2). |
| 1 | Прямая выгрузка EUR-Lex по `curl`/`WebFetch` для DR 2017/565 и CCD II | **HTTP 202 с нулевым телом** (асинхронный рендер EUR-Lex). Обойдено текстовым прокси `r.jina.ai` — HTTP 200. Для MiFID II прямой `curl` сработал (200, 952 КБ). |
| 1 | Текст **Recital 15 DR 2017/565** (generic advice about a type of financial instrument) | Консолидированная выгрузка через прокси пришла **без преамбулы**. Ссылка приводится по цитате ESMA35-43-3861 §50, дословно рецитал не сверялся. |
| 5 | Текст **art. 72A RAO** (information society services) и **PERG 2.9.18G** | Не открывались — не запрашивались в пределах бюджета. Вывод о неприменимости к третьим странам после Brexit помечен как **гипотеза**, а не проверенная норма. |
| 5 | Реквизиты авторизации StepChange / Citizens Advice / National Debtline, данные о финансировании бесплатного сектора UK | Не проверялись. Приведены как контекст. |
| 5-бис | **Directive 2014/17/EU (MCD)**, Art. 4(21) и Art. 22 — «advisory services» по ипотечному кредиту | Не открывалась. 🔴 **Значимая лакуна**: ипотека присутствует в контуре обязательств пользователя, конструкция MCD, вероятно, аналогична CCD II. Первый кандидат на добор. |
| 5-бис | Толкования Комиссии / национальных регуляторов: покрывает ли Art. 3(17) CCD II совет о **досрочном погашении** существующего кредита | Не искались. Ключевая открытая неопределённость по ЕС (см. 8.3). |
| 4 | Первичная страница MoneyHelper о стоимости консультации | Постранично не открывалась; числа (£75–£350+/час) взяты из сводки поисковой выдачи 09.09.2026. Помечены как ориентир. |
| 7 | SEC no-action letters и staff guidance по budgeting / financial-wellness приложениям; публикации крупных юрфирм по «is a financial planning tool an investment adviser» | Не искались — исчерпан бюджет подагента (15 действий). 🔴 **Самая существенная лакуна по США**: именно там отраслевая практика применения элемента «securities» к asset allocation без называния бумаг. |
| 7 | Дословный текст Release 33-11377 (отзыв PDA-предложения SEC); формулировка «person-to-person» в Lowe; третий штат по debt adjusting; статус CFP Board | Бюджет подагента. Детали — в таблице конца §7. |
| 7 | `supreme.justia.com` (Lowe v. SEC) | **HTTP 403**, через `r.jina.ai` пустой ответ (288 байт). Обойдено: цитаты взяты у Cornell LII (HTTP 200). |
| 7 | `sec.gov` PDF (IM Guidance 2017-02) | **HTTP 403** и на `WebFetch`, и на `curl` с браузерным UA. Обойдено через `r.jina.ai` — **HTTP 200**. |

**Процесс, для прозрачности.** Тип запроса — **breadth-first** (восемь слабо связанных
под-вопросов по четырём юрисдикциям). Подагентов запущен **один** (США), при потолке канона
в два и запрете веерного запуска; остальные семь разделов вахта добыла сама. Вызовов
`WebSearch` — 4. Основной канал добычи — `curl` с браузерным UA (сработал на legislation.gov.uk,
handbook.fca.org.uk, fca.org.uk, esma.europa.eu, EUR-Lex по MiFID II) и текстовый прокси
`r.jina.ai` там, где EUR-Lex отдавал 202/0, а `sec.gov` и `justia` — 403. PDF разбирались
`pdftotext`.


---

## ДОБОР Г2 — Г2.1 Mortgage Credit Directive 2014/17/EU (дословно)

Добыто 11.09.2026. Источник: Directive 2014/17/EU of the European Parliament and of the Council of 4 February 2014 on credit agreements for consumers relating to residential immovable property (CELEX 32014L0017), https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32014L0017 .
Каналы: прямой `curl -sk --http1.1` с браузерным UA — HTTP 200, 544 103 байта (HTML); текстовый прокси `r.jina.ai` — HTTP 200, 258 284 байта (цитаты ниже сняты из него). Редакция — исходная (as adopted); консолидированные поправки не сверялись.

**Article 4, point (21) — определение:**

> (21) ‘Advisory services’ means the provision of personal recommendations to a consumer in respect of one or more transactions relating to credit agreements and constitutes a separate activity from the granting of a credit and from the credit intermediation activities set out in point 5.

Проверочная формулировка вахты подтверждена дословно.

**Article 4, point (5) — credit intermediary (нужно для понимания, кто «допущен»):**

> (5) ‘Credit intermediary’ means a natural or legal person who is not acting as a creditor or notary and not merely introducing, either directly or indirectly, a consumer to a creditor or credit intermediary, and who, in the course of his trade, business or profession, for remuneration …: (a) presents or offers credit agreements to consumers; (b) assists consumers by undertaking preparatory work or other pre-contractual administration in respect of credit agreements other than as referred to in point (a); or (c) concludes credit agreements with consumers on behalf of the creditor.

**Article 3(1) — сфера:** «(a) credit agreements which are secured either by a mortgage or by another comparable security … on residential immovable property …; and (b) credit agreements the purpose of which is to acquire or retain property rights in land or in an existing or projected building.»

**Article 22 — Standards for advisory services (ключевые части дословно):**

> 1. Member States shall ensure that the creditor, credit intermediary or appointed representative explicitly informs the consumer, in the context of a given transaction, whether advisory services are being or can be provided to the consumer.
>
> 2. … before the provision of advisory services … provides the consumer with the following information on paper or another durable medium:
> (a) **whether the recommendation will be based on considering only their own product range** in accordance with point (b) of paragraph 3 **or a wide range of products from across the market** in accordance with point (c) of paragraph 3 so that the consumer can understand the basis on which the recommendation is made;
> (b) where applicable, the fee payable by the consumer for the advisory services or … the method used for its calculation.
>
> 3. Where advisory services are provided to consumers, Member States shall ensure, in addition to the requirements set out in Articles 7 and 9, that:
> (a) … obtain the necessary information regarding the consumer’s personal and financial situation, his preferences and objectives so as to enable the recommendation of suitable credit agreements. Such an assessment shall be based on information that is up to date … and shall take into account reasonable assumptions as to risks to the consumer’s situation over the term of the proposed credit agreement;
> (b) creditors, tied credit intermediaries … consider a sufficiently large number of credit agreements in their product range and recommend a suitable credit agreements or several suitable credit agreements from among their product range …;
> (c) non-tied credit intermediaries … consider a sufficiently large number of credit agreements available on the market and recommend a suitable credit agreement or several … available on the market …;
> (d) … act in the best interests of the consumer …; and
> (e) … give the consumer a record on paper or on another durable medium of the recommendation provided.
>
> 4. Member States may prohibit the use of the term ‘advice’ and ‘advisor’ … [условия на ‘independent advice’: sufficiently large number of credit agreements available on the market; не вознаграждение от кредиторов] … Member States may impose more stringent requirements in relation to the use of the terms ‘independent advice’ or ‘independent advisor’ …, including a ban on receiving remuneration from a creditor.
>
> 5. Member States may provide for an obligation … to warn a consumer when, considering the consumer’s financial situation, a credit agreement may induce a specific risk for the consumer.
>
> 🔴 **6. Member States shall ensure that advisory services are only provided by creditors, credit intermediaries or appointed representatives.**
>
> Member States may decide not to apply the first subparagraph to persons:
> (a) carrying out the credit intermediation activities … or providing advisory services where those activities are carried out or services are provided **in an incidental manner** in the course of a professional activity and that activity is regulated …;
> (b) **providing advisory services in the context of managing existing debt** which are insolvency practitioners where that activity is regulated by legal or regulatory provisions **or public or voluntary debt advisory services which do not operate on a commercial basis**; or
> (c) providing advisory services who are not creditors, credit intermediaries or appointed representatives where such persons are **admitted and supervised by competent authorities in accordance with the requirements for credit intermediaries under this Directive**.
>
> Persons benefiting from the waiver in the second subparagraph shall not benefit from the right referred to in Article 32(1) to provide services for the entire territory of the Union.
>
> 🟢 **7. This Article shall be without prejudice to Article 16 and to Member States’ competence to ensure that services are made available to consumers to help them understand their financial needs and which types of products are likely to meet those needs.**

**Article 29(1) — допуск (admission):**

> 1. Credit intermediaries shall be duly admitted to carry out all or part of the credit intermediation activities set out in point 5 of Article 4 **or to provide advisory services** by a competent authority in their home Member State. …

Art. 29(2): требования допуска — (a) professional indemnity insurance (минимальная сумма — RTS EBA), (b) good repute (чистая судимость по имущественным/финансовым преступлениям, не банкрот), (c) knowledge and competence по Annex III.

**Article 7(1)** — conduct of business: при оказании advisory services «the activity shall in addition be based on the information required under point (a) of Article 22(3)». **Art. 7(4)**: при advisory services вознаграждение персонала «is not contingent on sales targets».

**Article 25 — Early repayment (право потребителя):** «1. Member States shall ensure that the consumer has a right to discharge fully or partially his obligations under a credit agreement prior to the expiry of that agreement. …» **Art. 25(4)**: «Where a consumer seeks to discharge his obligations … prior to the expiry of the agreement, **the creditor shall provide the consumer** without delay … with the information necessary to consider that option. That information shall at least **quantify the implications for the consumer** of discharging his obligations prior to the expiry of the credit agreement and clearly set out any assumptions used.»

**Article 43(1) — переходное:** «This Directive shall not apply to credit agreements existing before 21 March 2016.» **Art. 42**: транспозиция до 21.03.2016, применение с 21.03.2016.

**Преамбула, дословно, что НЕ является personal recommendation:**
- Recital (48): кредиторы должны объяснять характеристики продуктов «in a personalised manner … **Such explanations should not in itself constitute a personal recommendation.**»
- Recital (63): «Providing advice in the form of a personalised recommendation is a distinct activity which may but need not be combined with other aspects of granting or intermediating credit.»
- Recital (64): «Those providing advisory services should be able to specialise in certain ‘niche’ products such as bridging finance …»

### Разбор Г2.1 (исследовательский, не юридическое заключение)

1. **Режим MCD — резервирование + допуск, как в CCD II.** Art. 22(6) — ровно та же конструкция, что Art. 16(6) CCD II (найдена ранее в §5.8): оказывать advisory services могут только кредиторы, кредитные посредники и их представители; третье лицо — только через допуск «in accordance with the requirements for credit intermediaries» (Art. 22(6)(c) + Art. 29). В отличие от CCD II, MCD **оставляет государству выбор** («Member States may decide not to apply»), то есть независимый ипотечный советник возможен лишь там, где государство открыло дерогацию (c), и паспорта на весь ЕС у него нет (последний абзац Art. 22(6)).
2. 🔴 **Главный вопрос — «покрывает ли совет о досрочном погашении уже существующей ипотеки»: текст директивы даёт косвенный аргумент ЗА.** Дерогация (b) говорит о лицах, «providing advisory services **in the context of managing existing debt**». Если бы советы в контексте управления существующим долгом вообще не были «advisory services», изымать их из резервирования было бы не нужно. Это аргумент систематического толкования, а не прямая норма; противоположный аргумент — стандарты Art. 22(3)(b)–(c) целиком описывают **выбор кредитного договора** («recommend a suitable credit agreement … available on the market»), и для совета «гасить досрочно» они неисполнимы по смыслу. Официального толкования Комиссии/EBA по этому вопросу в этом доборе не найдено (см. ниже).
3. 🟢 **Нейтральная зона прямо названа в тексте — Art. 22(7):** государства вправе обеспечивать услуги, которые помогают потребителю «understand their financial needs and **which types of products** are likely to meet those needs». Это та же линия, что generic advice в MiFID (тип, а не конкретный продукт). Для FINPILOT она покрывает объяснение «тип: досрочное погашение/рефинансирование/резерв», но не «гасите ипотеку X ₽ сейчас» — последнее ближе к personal recommendation.
4. **Art. 25(4) важен продуктово:** количественные последствия досрочного погашения ипотеки обязан раскрыть **кредитор** по запросу потребителя. То есть в ЕС сам расчёт «что будет, если погасить досрочно» — нормированная обязанность банка, а не зона независимого советника. В B2B-сценарии встраивания FINPILOT в банк именно этот расчёт — законная функция банка.
5. **Art. 43(1):** директива не применяется к договорам, существующим до 21.03.2016 — старые ипотеки вне её режима (национальное право могло распространить).


### Г2.1 — транспозиция MCD: Германия и Ирландия (дословно)

**Германия — § 34i GewO (Gewerbeordnung).** https://www.gesetze-im-internet.de/gewo/__34i.html — прямой `curl` дал код 000 (таймаут соединения, 0 байт); через `r.jina.ai` — HTTP 200, 6 642 байта, текст нормы полностью.

> (1) Wer gewerbsmäßig den Abschluss von Immobiliar-Verbraucherdarlehensverträgen im Sinne des § 491 Absatz 3 des Bürgerlichen Gesetzbuchs … vermitteln will **oder Dritte zu solchen Verträgen beraten will** (Immobiliardarlehensvermittler), **bedarf der Erlaubnis der zuständigen Behörde.** …
>
> (2) Die Erlaubnis ist zu versagen, wenn … 3. der Antragsteller den Nachweis einer Berufshaftpflichtversicherung … nicht erbringen kann, 4. der Antragsteller nicht durch eine vor der Industrie- und Handelskammer erfolgreich abgelegte Prüfung nachweist, dass er die Sachkunde … besitzt …, oder 🔴 **5. der Antragsteller seine Hauptniederlassung oder seinen Hauptsitz nicht im Inland hat oder seine Tätigkeit als Immobiliardarlehensvermittler nicht im Inland ausübt.**
>
> (3) Keiner Erlaubnis … bedürfen Kreditinstitute, für die eine Erlaubnis nach § 32 Absatz 1 des Kreditwesengesetzes erteilt wurde, …
>
> (4) Keiner Erlaubnis … bedarf ein Immobiliardarlehensvermittler, der … im Umfang seiner Erlaubnis handelt, die nach Artikel 29 der Richtlinie 2014/17/EU … durch einen anderen Mitgliedstaat … erteilt worden ist. …
>
> (5) Gewerbetreibende nach den Absätzen 1 und 4, die eine unabhängige Beratung anbieten oder als unabhängiger Berater auftreten (**Honorar-Immobiliardarlehensberater**), 1. müssen für ihre Empfehlung **für oder gegen einen Immobiliar-Verbraucherdarlehensvertrag** … eine hinreichende Anzahl von entsprechenden auf dem Markt angebotenen Verträgen heranziehen und 2. dürfen vom Darlehensgeber keine Zuwendungen annehmen und von ihm in keiner Weise abhängig sein. Honorar-Immobiliardarlehensberater dürfen keine Tätigkeit als Immobiliardarlehensvermittler und Immobiliardarlehensvermittler dürfen keine Tätigkeit als Honorar-Immobiliardarlehensberater ausüben.
>
> (8) … sich unverzüglich nach Aufnahme ihrer Tätigkeit in das Register nach § 11a Absatz 1 eintragen zu lassen …

**Германия — § 511 BGB «Beratungsleistungen bei Immobiliar-Verbraucherdarlehensverträgen».** https://www.gesetze-im-internet.de/bgb/__511.html — `curl`, HTTP 200, 4 916 байт.

> (1) Bevor der Darlehensgeber dem Darlehensnehmer **individuelle Empfehlungen zu einem oder mehreren Geschäften erteilt, die im Zusammenhang mit einem Immobiliar-Verbraucherdarlehensvertrag stehen (Beratungsleistungen)**, hat er den Darlehensnehmer über die sich aus Artikel 247 § 18 des Einführungsgesetzes zum Bürgerlichen Gesetzbuche ergebenden Einzelheiten … zu informieren.
> (2) … hat der Darlehensgeber eine ausreichende Zahl an Darlehensverträgen zumindest aus seiner Produktpalette auf ihre Geeignetheit zu prüfen.
> (3) Der Darlehensgeber hat dem Darlehensnehmer … ein geeignetes oder mehrere geeignete Produkte zu empfehlen **oder ihn darauf hinzuweisen, dass er kein Produkt empfehlen kann.** …

§ 655a(3) BGB (https://www.gesetze-im-internet.de/bgb/__655a.html, `curl`, HTTP 200, 6 028 байт): для Darlehensvermittler, оказывающего Beratungsleistungen, «so gilt § 511 entsprechend … mit der Maßgabe, dass der Darlehensvermittler eine ausreichende Zahl von am Markt verfügbaren Darlehensverträgen zu prüfen hat».

**Разбор Германии.** (1) Германия воспользовалась дерогацией Art. 22(6)(c) MCD: независимый советник по ипотеке **допустим, но только с Erlaubnis** по § 34i(1) и под именем Honorar-Immobiliardarlehensberater (§ 34i(5)). (2) Предмет немецкой нормы сформулирован **уже**, чем в директиве: «Dritte **zu solchen Verträgen** beraten» и «Empfehlung **für oder gegen einen** Immobiliar-Verbraucherdarlehensvertrag» — речь о заключении/выборе договора. Совет о досрочном погашении существующего договора текстом § 34i прямо не назван; § 511(1) BGB шире («Geschäften … im Zusammenhang mit» договором), но адресован Darlehensgeber, то есть банку. Толкование BaFin/IHK на вопрос «покрывает ли досрочное погашение» — не найдено. (3) 🔴 **§ 34i(2) Nr. 5: разрешение не выдаётся, если головной офис не в Германии** — для FINPILOT, оказывающего услугу из-за пределов ЕС, немецкая лицензия недоступна в принципе (кроме пути § 34i(4) — паспорт другого государства-члена ЕС/ЕЭЗ по Art. 29 MCD, но у советника по дерогации Art. 22(6) паспорта нет, см. последний абзац Art. 22(6)).

**Ирландия — S.I. No. 142 of 2016, European Union (Consumer Mortgage Credit Agreements) Regulations 2016.** https://www.irishstatutebook.ie/eli/2016/si/142/made/en/print — `curl`, HTTP 200, 320 389 байт. Редакция — as made (поправки не сверялись).

> Reg. 3(1): “advisory services” means the provision of personal recommendations to a consumer in respect of one or more transactions relating to credit agreements and constitutes a separate activity from the granting of a credit and from credit intermediation activities;
>
> Reg. 23(7): **Advisory services shall only be provided by**— (a) a creditor; (b) a mortgage credit intermediary; (c) a barrister, solicitor or accountant providing advisory services if— (i) he or she is subject to regulation by a professional body, and (ii) those services are provided in an incidental manner in the course of a professional activity; (d) any of the following (**but only in the context of managing existing debt**)— (i) an approved intermediary authorised under section 47 of the Personal Insolvency Act 2012 … or a personal insolvency practitioner …; (ii) **a debt management firm authorised by the Central Bank**; (iii) a charitable organisation within the meaning of section 2(1) of the Charities Act 2009 …; (iv) **the Money Advice and Budgeting Service**; (v) a person who is a party to the “Protocol for Independent Advice to Borrowers Availing of Long Term Mortgage Forbearance” made on 2 August 2012 … .
>
> Reg. 23(10): A creditor or mortgage credit intermediary **or other person who contravenes a provision of this Regulation commits an offence.**

**Разбор Ирландии.** (1) Ирландия, в отличие от Германии, дерогацию (c) — «любое допущенное лицо» — **не открыла**: список закрытый. Коммерческий независимый советник по ипотеке может работать только как mortgage credit intermediary либо — «only in the context of managing existing debt» — как **debt management firm authorised by the Central Bank**. (2) 🔴 Ирландский законодатель прямо выделил категорию «советы в контексте управления существующим долгом» внутри режима advisory services и допустил туда лицензированные debt management firms — **это прямое подтверждение, что национальный законодатель читает «advisory services» MCD как включающие советы по уже существующему ипотечному долгу**, иначе категория (d) была бы лишней. (3) Нарушение Reg. 23 — уголовное правонарушение (offence) для «other person» (Reg. 23(10)), то есть норма адресована и нелицензированным третьим лицам.


## ДОБОР Г2 — Г2.4 SEC Release No. 33-11377 (дословно)

Добыто 11.09.2026. https://www.sec.gov/files/rules/final/2025/33-11377.pdf — `curl -sk --http1.1` с UA, содержащим контакт, HTTP 200, 182 621 байт PDF; `pdftotext` — 14 955 байт текста. (Браузерный UA на sec.gov ранее давал 403 — подтверждено правило вахты: нужен UA с контактом.) Страница Federal Register https://www.federalregister.gov/documents/2025/06/17/2025-11110/withdrawal-of-proposed-regulatory-actions — HTTP 200, 92 260 байт (не разбиралась, PDF — первоисточник).

Реквизиты: «[Release Nos. **33-11377; 34-103247; IA-6885; IC-35635**; File Nos. S7-20-22; **S7-12-23**; …] RINs … **3235-AN14** … **Withdrawal of Proposed Regulatory Actions** … ACTION: Notice of withdrawal of proposed rules.» Подписано: «By the Commission. **Dated: June 12, 2025.** Sherry R. Haywood». В силе «as of June 17, 2025».

> SUMMARY: The Securities and Exchange Commission (“Commission”) is formally withdrawing certain notices of proposed rulemaking issued between March 2022 and November 2023. **The Commission does not intend to issue final rules with respect to these proposals.** If the Commission decides to pursue future regulatory action in any of these areas, it will issue a new proposed rule.

Что отозвано по нашей теме:

> Conflicts of Interest Associated with the Use of Predictive Data Analytics by Broker-Dealers and Investment Advisers
> On August 9, 2023, the Commission published proposed new rules under the Securities Exchange Act of 1934 (“Exchange Act”) and the Investment Advisers Act of 1940 (“Advisers Act”) to, among other things, address certain interactions between broker-dealers or investment advisers and investors through these firms’ use of predictive data analytics. [сноска: 88 FR 53960 (August 9, 2023)]

Почему — единственная мотивировка в тексте:

> Withdrawal of Proposed Rules
> **We are withdrawing these proposals because, as noted above, we no longer intend to issue final rules with respect to these proposals.** If the Commission decides to pursue future regulatory action in any of these areas, it will do so by publishing a new proposed rule or other issuance consistent with the requirements of the Administrative Procedure Act, as applicable.

**Разбор.** (1) Прежняя запись файла (§5-бис) подтверждена дословно. (2) Содержательной мотивировки («правило ошибочно», «рынок сам») в релизе **нет** — только «no longer intend». Утверждать, что SEC «сочла регулирование ИИ ненужным», по этому тексту нельзя. (3) Отзыв пакетный: 14 предложений 2020–2023 гг. одним актом, среди них также safeguarding (custody) и cybersecurity для advisers — это смена повестки Комиссии, а не решение по PDA по существу. (4) Для FINPILOT вывод прежний: специального федерального режима «алгоритм в совете» нет, и отозванное правило в любом случае адресовалось BD/IA.


## ДОБОР Г2 — Г2.3 art. 72A RAO и PERG 2.9.18G (UK, исключение для information society services)

Добыто 11.09.2026.

**(1) art. 72A RAO — текущее состояние.** https://www.legislation.gov.uk/uksi/2001/544/article/72A — `curl`, HTTP 200, 41 878 байт. Страница «up to date with all changes known to be in force on or before 11 September 2026». Текст статьи на сайте — дословно:

> Information society services
> F1 72A. . . . . . . . . . . . . . . . . . . . . . . . . .
> Textual Amendments
> F1 **Art. 72A omitted (31.12.2020)** by virtue of The Electronic Commerce and Solvency 2 (Amendment etc.) (EU Exit) Regulations 2019 (**S.I. 2019/1361**), regs. 1(2), 5(2) (with regs. 11-28) (as amended by S.I. 2019/1390, regs. 1(2), 6); 2020 c. 1, Sch. 5 para. 1(1)

История версий на той же странице: 21/08/2002 · 11/01/2005 · 24/03/2015 · 01/01/2016 · 29/11/2018 · 01/04/2019 · **31/12/2020**. Отметки outstanding: «Order revoked by 2023 c. 29 Sch. 1 Pt. 5» (Financial Services and Markets Act 2023 — отмена RAO целиком ещё не введена в силу; RAO пока действует).

**(2) PERG 2.9.18G — редакция до Brexit.** Текущий handbook.fca.org.uk отдаёт 301 на себя же (`curl`, 167 байт), `r.jina.ai` возвращает страницу PERG 2.10 (26 766 байт, 2.9.18 не найдено). Добыто через Wayback: CDX API вернул 26 снимков 2015–2025; снимок `https://web.archive.org/web/20190718233738id_/https://www.handbook.fca.org.uk/handbook/PERG/2/9.html` — HTTP 200, 145 155 байт. Дословно:

> Incoming ECA providers
> **PERG 2.9.18 G** 01/01/2016
> (1) In accordance with article 3(2) of the E-Commerce Directive, all requirements on persons providing electronic commerce activities into the United Kingdom **from the EEA** are lifted, where these fall within the co-ordinated field and would restrict the freedom of such a firm to provide services. The coordinated field includes any requirement of a general or specific nature concerning the taking up or pursuit of electronic commerce activities. Authorisation requirements fall within the coordinated field. The services affected are generally those provided electronically, for example through the Internet or solicited e-mail.
> (2) The Regulated Activities Order was amended by the Financial Services and Markets Act 2000 (Regulated Activities) (Amendment) (Electronic Commerce Directive) Order 2002 (SI 2002/2157). This Order creates a general exclusion from regulated activities (except for the regulated activities of effecting or carrying out contracts of insurance). Where activities consist of electronic commerce activities, **an incoming ECA provider will not require authorisation for such activities in the United Kingdom**. … However, services provided off-line in the United Kingdom … by such a firm which amount to regulated activities still require authorisation.
> (3) Incoming ECA providers should note that notification requirements under the Single Market Directives still apply (see SUP 13A).

И в той же главе (PERG 2.9.1G(2) того же снимка): «The exclusion described in PERG 2.9.18 G relates to electronic commerce activities provided by an **incoming ECA provider**. This exclusion applies to all regulated activities except effecting or carrying out contracts of insurance.»

**(3) PERG 2.9 — текущая редакция.** Снимок `…/web/20251207183722id_/…/PERG/2/9.html` — HTTP 200, 35 753 байта; строк «2.9.18» и «Information society» в нём **нет** (0 совпадений) — раздел удалён вместе с art. 72A.

### Разбор Г2.3

🔴 **Гипотеза файла (строка «art. 72A … вывод о неприменимости к третьим странам после Brexit помечен как гипотеза») — подтверждена в сильной форме: исключения больше не существует вовсе, а не только для третьих стран.** С 31.12.2020 art. 72A исключена из RAO (S.I. 2019/1361), PERG 2.9.18G из Perimeter Guidance удалён. Даже в период действия исключение работало только для **incoming ECA provider** — поставщика, учреждённого **в ЕЭЗ** (механизм article 3(2) E-Commerce Directive, «country of origin»). Российский или любой иной не-ЕЭЗ поставщик под него не подпадал никогда. **Вывод: путь «оказываем онлайн из-за рубежа — значит вне британского debt counselling» закрыт; остаётся только общий вопрос территориальности («by way of business in the UK», s. 19 и s. 418 FSMA) и исключение для overseas persons (art. 72 RAO), которое для debt counselling не проверялось в этом доборе.**


## ДОБОР Г2 — Г2.5 UDMSA — официальный текст (дословно)

Добыто 11.09.2026. «UNIFORM DEBT-MANAGEMENT SERVICES ACT (Last Revised or Amended in 2008)», National Conference of Commissioners on Uniform State Laws — https://www.ftc.gov/sites/default/files/documents/public_events/consumer-protection-and-debt-settlement-industry/udmsafinal.pdf (копия официального текста NCCUSL в материалах FTC; ссылка найдена через WebSearch; сайт uniformlaws.org PDF в выдаче не дал — библиотека сообщества за входом). `curl` — HTTP 200, 422 105 байт, PDF 44 страницы; `pdftotext` — 271 935 байт.

**Section 2 — определения:**

> (7) “Concessions” means assent to repayment of a debt on terms more favorable to an individual than the terms of the contract between the individual and a creditor.
>
> (9) **“Debt-management services” means services as an intermediary between an individual and one or more creditors of the individual for the purpose of obtaining concessions**, but does not include:
> (A) legal services provided in an attorney-client relationship by an attorney licensed …;
> (B) accounting services provided in an accountant-client relationship by a certified public accountant …; or
> (C) **financial-planning services provided in a financial planner-client relationship by a member of a financial-planning profession** whose members the administrator, by rule, determines are (i) licensed by this state; (ii) subject to a disciplinary mechanism; (iii) subject to a code of professional responsibility; and (iv) subject to a continuing-education requirement.
>
> (13) “Plan” means a program or strategy in which a provider furnishes debt-management services to an individual and which includes a schedule of payments to be made by or on behalf of the individual and used to pay debts owed by the individual.
>
> (15) “Provider” means a person that provides, offers to provide, or agrees to provide debt-management services directly or through others.

**Section 3 — изъятия (выборка):**

> (a) This [act] does not apply to an agreement with an individual who the provider has no reason to know resides in this state at the time of the agreement.
> (b) This [act] does not apply to a provider to the extent that the provider: (1) provides or agrees to provide debt-management, educational, or counseling services to an individual who the provider has no reason to know resides in this state …; or (2) **receives no compensation for debt-management services** from or on behalf of the individuals … or from their creditors.
> (c) … (2) a bank; (3) an affiliate … of a bank if the affiliate is regulated by a federal or state banking regulatory authority; or (4) a title insurer, escrow company, or other person that provides bill-paying services if the provision of debt-management services is incidental to the bill-paying services.

Официальный Comment к Section 3, п. 1: «Under section 2(15) a person may be a provider **even if the person has no physical presence in this state.**» П. 5: «A provider whose ads reach, or whose website is accessible to, individuals who reside in this state but who does not enter agreements with or provide services to those individuals is not offering to provide debt-management services to residents of this state.»

**Section 4(a):** «a provider may not provide debt-management services to an individual who it reasonably should know resides in this state at the time it agrees to provide the services, **unless the provider is registered** under this [act].» Section 4(d) [в скобках, опция штата] — регистрация только not-for-profit 501(c); Legislative Note: «This section implements the state’s decision concerning whether for-profit entities are permitted to provide debt-management services.»

**Какие штаты приняли** — сниппет выдачи WebSearch 11.09.2026 (первоисточник — карта принятий uniformlaws.org — не открыт): «adopted in Colorado, Delaware, Missouri, Nevada, Rhode Island, Tennessee, and Utah … the Virgin Islands have also adopted the UDMSA with modifications»; Utah — первый штат, 2006. Косвенные подтверждения по выдаче: Nevada NRS Chapter 676A (https://www.leg.state.nv.us/nrs/nrs-676a.html), Delaware AG «Debt Management Services Act» (https://attorneygeneral.delaware.gov/fraud/cpu/debtmanadvisory/), Utah Code Title 13 Ch. 42 (добыт ранее). Wikipedia (API, HTTP 200, 7 979 байт) пишет лишь «more than 20 states are executed to introduce the act in 2009» — число принявших не называет.

### Разбор Г2.5

1. **Прежний вывод файла по UDMSA подтверждён по официальному тексту модели, а не только по кодификации Юты:** триггер — «intermediary between an individual and … creditors **for the purpose of obtaining concessions**». Совет без контакта с кредиторами и без переговоров об уступках (FINPILOT: гасить досрочно по договору, без изменения условий) под определение не подпадает; план с графиком платежей (2(13)) — производное понятие, «in which a provider furnishes debt-management services», то есть без посредничества планом в смысле акта не является.
2. Отдельно: даже планировщик внутри определения мог бы быть изъят по 2(9)(C), но только если он член **лицензируемой штатом** профессии планировщиков — такой профессии в большинстве штатов нет, так что для нас это изъятие мёртвое и не нужно.
3. **Экстерриториальность:** отсутствие физического присутствия в штате не спасает (Comment 1). Для нас это безразлично, пока мы вне определения.
4. 🔴 **UDMSA — лишь 7 штатов + Виргинские острова (по сниппету).** Остальные штаты держат собственные законы о debt adjusting / credit counseling, и часть из них построена широко, как вашингтонский RCW 18.28.010 («managing, counseling … prorating … of the indebtedness») — ранее найденный риск это не снимает, а подтверждает: безопасная UDMSA-модель — меньшинство.


## ДОБОР Г2 — Г2.2 CCD II (Directive (EU) 2023/2225): досрочное погашение и debt advisory services

Добыто 11.09.2026. Текст — CELEX 32023L2225 через `r.jina.ai`, HTTP 200, 207 412 байт (тот же размер, что при добыче 09.09.2026 — текст не менялся). Art. 3(17), 3(22), 16(3), 16(6), 36, 48 уже процитированы в §5.8; ниже — только новое.

**Art. 3(21) — определение досрочного погашения:**
> (21) ‘early repayment’ means the full or partial discharge of the consumer’s obligations under a credit agreement, before the date agreed in the credit agreement;

**Art. 16(6)(b) и (c) — полные формулировки дерогаций (в §5.8 были сокращены):**
> (b) the advisory services are provided **in the context of management of existing debt** by insolvency practitioners and where that management activity is regulated by legal or regulatory provisions;
> (c) the advisory services are provided **in the context of management of existing debt** by public or voluntary providers of debt advisory services as referred to in Article 36 which do not operate on a commercial basis;

**Art. 2(2)(l) — сфера, переходное:**
> 2. This Directive does not apply to the following: … (l) **credit agreements existing on 20 November 2026**; however, Articles 23 and 24, Article 25(1), second sentence, Article 25(2) and Articles 28 and 39 shall apply to all open-end credit agreements existing on 20 November 2026.

Art. 47, второй абзац: «Notwithstanding the first paragraph, Directive 2008/48/EC shall continue to apply to credit agreements existing on 20 November 2026 until their termination.»

**Art. 2(2)(a) — ипотека вне CCD II:** «credit agreements which are secured either by a mortgage, or by another comparable security … on immovable property …» — то есть ипотечный кредит FINPILOT-пользователя в ЕС — это MCD (Г2.1), потребкредит и карты — CCD II.

**Art. 29(1)–(2) — право на досрочное погашение**: «the consumer is at any time entitled to early repayment …»; компенсация кредитору только в период фиксированной ставки, потолок **1 %** (при сроке до окончания больше года) и **0,5 %** (до года) от досрочно погашаемой суммы; Art. 29(4)(a) — государство может установить порог, не выше **EUR 10 000** за 12 месяцев, ниже которого компенсации нет.

**Recital (63)** — кредитор при регулярном овердрафте «should offer the consumer advisory services, where available, to help the consumer identify less expensive alternatives, and redirect the consumer towards debt advisory services». (Норма — Art. 25(2)-подобное положение: «in the case of regular overrunning, the creditor shall offer the consumer advisory services, where available, and redirect the consumer at no cost towards debt advisory services».)

**Recital (81) — debt advisory services, дословно ключевые части:**
> … Financial difficulties cover a wide variety of situations, for example among many others, having delayed the repayment of debt for more than 90 days. The objective of debt advisory services is to help consumers facing financial difficulties and guide them to repay, as far as possible, their outstanding debts, while maintaining a decent level of life and preserving their dignity. That personalised and independent assistance may include legal counselling, **money and debt management** as well as social and psychological assistance. The assistance should be provided by professional operators which are **not creditors, credit intermediaries, providers of crowdfunding credit services, credit purchasers or credit servicers, and are independent from them.** Member States should ensure that debt advisory services provided by independent professional operators are made available, directly or indirectly and **with only limited charges**, to consumers. **Those charges should in principle only cover operating expenses** … **Member States remain free to maintain or introduce specific requirements for debt advisory services.** …

Art. 36(4): «Member States shall, by 20 November 2026, and every year thereafter, report to the Commission on available debt advisory services»; Комиссия — обзор к 20.11.2028.

**Толкования по вопросу «досрочное погашение = advisory services?»** — поиск WebSearch (запрос «CCD2 "advisory services" early repayment existing credit agreement interpretation», 11.09.2026): **официальных разъяснений Комиссии или EBA не найдено**. Найдено:

(а) **Ирландия, CCPC — Submission to the Department of Finance CCD 2 Consultation (2024).** https://www.ccpc.ie/business/wp-content/uploads/sites/3/2024/10/Consumer-Credit-Directive-CCD-2.pdf → 301 → https://assets.ccpc.ie/data/docs/default-source/about-us/submissions/submissions-2024/submission-to-consumer-credit-directive-cc2.pdf, `curl -L`, HTTP 200, 485 146 байт, `pdftotext` 33 944 байта. Дословно:
> Question 10 – **Should Ireland continue to allow persons to provide advisory services** on condition that they are provided under a regulated professional framework; provided by regulated insolvency practitioners; provided by non-commercial public or voluntary debt advisory services or provided by persons authorised and supervised by the competent authority?
> **Yes.** Independent advice by regulated, recognised and authorised services will ensure that consumers continue to avail of protections and impartial assistance, if required, with credit agreements. It is important that any advice received is holistically in the best interest of the consumer and considers their overall financial wellbeing. … A regulated independent professional will impartially review the overall financial health of the consumer and offer comprehensive support.

Это позиция ирландского регулятора по защите потребителей в консультации Минфина (не норма). Итоговый ирландский акт транспозиции CCD II в этом доборе не искался.

(б) **Италия — транспозиция** по Legal500 «Navigating the New Consumer Credit Landscape with CCD II» (https://www.legal500.com/guides/hot-topic/navigating-the-new-consumer-credit-landscape-with-ccd-ii/, `r.jina.ai`, HTTP 200, 16 100 байт; вторичный источник, первоисточник — Decreto legislativo — не открыт): «Italy implemented CCD II through **Legislative Decree No. 212 of December 31, 2025** … Introducing a formal definition of “advisory services” (Article 121 TUB); Regulating advisory activity by lenders and intermediaries (Article 124.2 TUB); **Clarifying that only specific registered intermediaries may provide independent advice**; Distinguishing this from debt counseling services under Article 125-terdecies TUB.»

### Разбор Г2.2

1. 🔴 **Дерогации (b)–(c) Art. 16(6) прямо говорят о «advisory services … in the context of management of existing debt».** Та же логика, что в MCD (Г2.1, п. 2): законодатель ЕС в обоих актах исходит из того, что советы по управлению **уже существующим** долгом **входят** в понятие advisory services — иначе их не нужно было бы изымать из резервирования. Это текстуальный аргумент, а не разъяснение; но он **ослабляет** прежнюю оговорку §8.3 («Art. 16(3)(c) склоняет к прочтению "советы о выборе кредита"»). Корректнее: стандарты Art. 16(3) написаны под выбор кредита, но **периметр** Art. 3(17) + резервирование Art. 16(6) по систематике охватывает и управление существующим долгом.
2. 🟢 **Смягчающее — Art. 2(2)(l):** CCD II не применяется к кредитным договорам, существующим на 20.11.2026; к ним продолжает применяться CCD 2008/48/EC до их прекращения (Art. 47). В CCD 2008/48/EC режима advisory services и резервирования **нет** (в тексте 2008/48 определения advisory services нет — это новелла CCD II; сверено косвенно: в §5.8 указано, что CCD II «новый и ужесточающий»; первоисточник 2008/48 в этом доборе не открывался — 🟡). Следствие: на переходный период совет по уже существующим на 20.11.2026 кредитам, по буквальному тексту, в периметр Art. 16(6) CCD II не попадает; по кредитам, заключённым после 20.11.2026, — попадает, если это «personal recommendation in respect of … transactions relating to credit agreements». Для продукта с горизонтом в годы это временная, а не структурная ниша.
3. **Легальная ниша debt advisory services (Art. 36) для FINPILOT как коммерческого продукта — узкая.** Recital (81): операторы должны быть **независимы** от кредиторов, плата — «only limited charges», «in principle only cover operating expenses». Дерогация (c) Art. 16(6) — только для «public or voluntary providers … which do not operate on a commercial basis». То есть подписочная модель FINPILOT под Art. 36 не встаёт. Реалистичные роли: (а) **поставщик ПО для** независимых debt advisory services (некоммерческих организаций, которых государства обязаны обеспечить к 20.11.2026) — B2B2C, где советует оператор, а не мы; (б) **поставщик ПО для кредитора** в рамках Art. 36(2) — «processes and policies in place for the early detection of consumers experiencing financial difficulties» и направление к debt advice. Оба варианта — не норма, а вывод исследователя из текста.
4. **B2B со встраиванием в банк:** кредитор входит в список тех, кому advisory services **разрешены** по умолчанию (Art. 16(6) первый абзац), но несёт стандарты Art. 16(2)–(5): раскрыть, на какой линейке основан совет; собрать информацию о финансовом положении; best interests; **record of the recommendation on a durable medium**. FINPILOT, встроенный в банк, должен уметь выдавать эту запись — продуктовое требование, а не лицензионное.


## ДОБОР Г2 — Г2.4 SEC: staff guidance по финансовому планированию (IA-1092) и практика юрфирм

**SEC Release No. IA-1092 (October 8, 1987), «Applicability of the Investment Advisers Act to Financial Planners, Pension Consultants, and Other Persons Who Provide Investment Advisory Services as a Component of Other Financial Services»** — позиция staff Division of Investment Management, выпущенная совместно с NASAA; заменила IA-770. Адрес `https://www.sec.gov/rules/interp/ia-1092.pdf` → 301 → `/files/rules/interp/ia-1092.pdf` → **HTTP 404** (53 435 байт HTML-заглушки). Правильный адрес найден WebSearch: https://www.sec.gov/files/rules/interp/1987/ia-1092.pdf — `curl` с UA-контактом, HTTP 200, 1 167 175 байт, PDF-скан; `pdftotext` — 41 800 байт, **OCR местами искажён**.

Дословно (читаемые места скана):

> Financial planning typically involves providing a variety of services, principally advisory in nature, to individuals or families regarding the management of their financial resources based upon an analysis of individual client needs. … This information normally would cover present and anticipated **assets and liabilities**, including insurance, savings, investments … The program developed for the client usually includes general recommendations for a course of activity or specific actions, to be taken by the client. For example, recommendations may be made that the client obtain insurance or revise existing coverage, establish an individual retirement account, **increase or decrease funds held in savings accounts, or invest funds in securities**.

> Whether a person providing financially related services of the type discussed in this release is an investment adviser within the meaning of the Advisers Act **depends upon all the relevant facts and circumstances.** … A determination … will depend upon whether such person: (1) provides advice, or issues reports or analyses, **regarding securities**; (2) is in the business of providing such services; and (3) provides such services for compensation.

> … if a financial planner structures his planning so as to give only generic, non-specific investment advice as a financial planner, but then gives specific securities advice in his capacity as a registered representative of a dealer or as agent of an insurance company, the person would not be able to assert that he was not "in the business" of giving investment advice.

🔴 **Ключевой абзац о «securities» — в скане не читается** (OCR выдал мусор в районе стр. 6–7). Приводится по дословной цитате в Kitces.com (гостевой пост Chris Stanley, Beach Street Legal, «When Does A Financial Coach Need To Register As An Investment Adviser? The “ABCS” Test», https://www.kitces.com/blog/abcs-financial-coach-register-investment-adviser-status-sec-series-65-66-nasaa/ — прямой канал kitces.com отдаёт 403 по прежним замерам; через `r.jina.ai` HTTP 200, 36 858 байт). **Вторичная цитата первоисточника, со скана не сверена:**

> The staff believes that a person who provides advice, or issues or promulgates reports or analyses, which concern securities, but which do not relate to specific securities, generally is an investment adviser … **The staff has interpreted the definition of investment adviser to include persons who advise clients concerning the relative advantages and disadvantages of investing in securities in general as compared to other investments. A person who, in the course of developing a financial program for a client, advises a client as to the desirability of investing in, purchasing or selling securities, as opposed to, or in relation to, any non-securities investment or financial vehicle would also be "advising" others within the meaning of Section 202(a)(11).**

Та же статья, позиция юриста (не SEC) — список областей, которые «would also not be captured by the "securities" hook»: «Goal setting · **Debt reduction** · **Budgeting** · **Establishing appropriate savings** · College aid strategies · Property & casualty insurance needs analysis · Optimization of credit card benefits · Employer salary negotiation · Vehicle lease versus buy decisions · Rent versus own decisions · **Mortgage refinancing**». И: «Thus, even the mere comparison of investing in securities in general as opposed to real estate, for example, is enough to trigger the securities element of the ABCS test.» Автор отдельно указывает, что «business» по IA-1092 требует «specific investment advice» о «specific securities or specific categories of securities»: «a general recommendation to allocate assets to securities is not enough … A recommendation to allocate assets to stocks, bonds, mutual funds, or exchange-traded funds … would seem to be specific enough».

**Рынок — пример того, что делают конкуренты в США:** Origin (useorigin.com, `r.jina.ai`, HTTP 200, 10 039 байт) называет свой ИИ-продукт «The first full-spectrum AI financial advisor **regulated by the SEC**» — то есть при переходе к инвестиционным советам американский игрок пошёл в регистрацию RIA, а не в обход. Маркетинговый текст, факт регистрации по Form ADV в этом доборе не проверялся.

**Не найдено:** SEC no-action letters конкретно про budgeting / financial-wellness приложения; публикации Morrison Foerster, Ropes & Gray, Davis Polk, Skadden, Sidley по вопросу «is a financial planning tool an investment adviser». Два WebSearch-запроса («budgeting app "investment adviser" SEC financial planning tool law firm», «financial wellness app Investment Advisers Act registration law firm analysis») вернули маркетинг приложений, NASAA, Cornell LII и Kitces/Beach Street Legal; страниц названных пяти фирм в выдаче не было. Отрицательный результат, а не исчерпание канала.

### Разбор Г2.4

1. 🟢 **Совет о долгах и резерве без ценных бумаг — вне Advisers Act.** Подтверждено по IA-1092 (трёхэлементный тест, элемент (1) «regarding securities») и по практике юриста-специалиста: debt reduction, budgeting, establishing savings, mortgage refinancing — вне «securities hook».
2. 🔴 **Уточнение прежнего вывода §7 «Advisers Act — мимо, потому что мы бумаг не называем»: этого условия НЕДОСТАТОЧНО.** По позиции staff в IA-1092 (во вторичной цитате) советником является и тот, кто советует о «relative advantages and disadvantages of investing in securities **in general** as compared to other investments» и о желательности инвестиций в ценные бумаги «as opposed to, or in relation to, **any non-securities investment or financial vehicle**». Если в распределении свободного потока FINPILOT есть направление «инвестировать» (в любой форме: «цель — инвестиции», «вложить в фондовый рынок») и модель рекомендует долю между ним и досрочным погашением/резервом, это ложится на формулировку staff **без называния конкретной бумаги**. Защищённая конструкция для США — направления «погашение долга / резерв (депозит, накопительный счёт) / цель-покупка», без направления «инвестиции в ценные бумаги». Проверить, есть ли такое направление в каноне модели, — задача не этого добора (канон не правится).
3. Отзыв PDA (33-11377) на этот вывод не влияет: IA-1092 — действующая staff-позиция 1987 года, её отзыв в этом доборе не встречен.

## ДОБОР Г2 — Г2.6 Бесплатный долговой совет в UK: авторизация, финансирование, цены

**StepChange.** https://www.stepchange.org/about-us/governance/regulatory-information.aspx — `curl`, HTTP 200, 57 534 байта. Дословно: «Foundation for Credit Counselling, 123 Albion Street, Leeds, LS2 8ER trading as StepChange Debt Charity and StepChange Debt Charity Scotland. A registered charity no.1016630 and SC046263. It is a limited company registered in England and Wales (company no:2757055). **Authorised and regulated by the Financial Conduct Authority (Firm Registration Number 729047)**».

**National Debtline (Money Advice Trust).** https://moneyadvicetrust.org/advice-services/makingsureitsus/ — `r.jina.ai`, HTTP 200, 12 089 байт. Дословно: «**Authorised and regulated by the Financial Conduct Authority - 618928**».

**Citizens Advice.** Единого FRN нет: в FCA Register **каждое местное бюро — отдельная авторизованная фирма** (выдача WebSearch 11.09.2026: Birmingham, Basingstoke, Wiltshire, New Forest, Liverpool, Braintree & South Essex, St Helens, Arun and Chichester, Blackpool, Bath & District — все на register.fca.org.uk; в сниппете — «authorised by the FCA since 01/04/2014»). Страницы реестра (Salesforce, JS-рендер) не открывались — **сниппет, первоисточник не открыт**. Дата 01.04.2014 совпадает с переходом потребкредита от OFT к FCA и вступлением art. 39E (§5.1).

**Финансирование.** Money Advice Trust, «Our funding» (https://moneyadvicetrust.org/partnerships/our-funding/, `r.jina.ai`, HTTP 200, 3 135 байт), дословно: «**Commissioned services** – Specific funding to help support the provision of **free-to-client debt advice** via our front-line services, **largely from the debt advice levy administered by the Money and Pensions Service**». Сниппеты выдачи (первоисточники не открыты): «The Financial Conduct Authority imposes a levy on all regulated financial services companies to pay for such support, and that includes funding the Money and Pensions Service» (Hansard, Commons, Debt Advice Services, 09.01.2025, https://hansard.parliament.uk/commons/2025-01-09/debates/6D09A5E2-5CE7-46E7-B272-03328ED1C36F/DebtAdviceServices); у MaPS есть грантовые программы Debt Advice Modernisation Fund 2025/26 и Debt Advice Modernisation and Transformation Fund 2026/27 для «not-for-profit organisations» (find-government-grants.service.gov.uk). Сумма levy на 2025/26 не добыта.

**MoneyHelper — цена платной консультации.** Страница «Financial adviser fees» https://www.moneyhelper.org.uk/en/getting-help-and-advice/financial-advisers/guide-to-financial-adviser-fees — прямой `curl` к moneyhelper.org.uk отдаёт **403** (5 909 байт), `r.jina.ai` — HTTP 200, но **561 байт заглушки**. Добыто через Wayback: CDX — снимки 2025-03…2025-11; `https://web.archive.org/web/20251119023745id_/…` — HTTP 200, 27 441 байт gzip, после распаковки 24 657 байт текста. Дословно:

> An hourly rate — this will vary from **£75 an hour to £350**, although the UK average rate is about **£150 an hour**. A set fee for a piece of work — this might be several hundred or several thousand pounds. … (i.e. a pension transfer will cost more in advice fees than simply arranging an ISA). A monthly fee …

🔴 **Поправка к прежней записи файла (§5.7 и строка «4» в «Что не добыто»):** числа £75–£350/час подтверждены, но это цена **регулируемого финансового (инвестиционного, пенсионного) советника**, а не консультации по долгам — страница лежит в разделе «financial-advisers» и в примерах — pension transfer и ISA. Использовать эти числа как «цену долгового совета» нельзя. Долговой совет в UK для потребителя в массе **бесплатен** (StepChange, National Debtline, Citizens Advice — все авторизованы по debt counselling и финансируются через levy MaPS); платный сектор — debt management plans с комиссиями (страница MoneyHelper о DMP через `r.jina.ai` дала заглушку 550 байт, прямой `curl` — 403; сниппет выдачи: «if you choose a fee-paying provider, all DMP providers must be authorised by the Financial Conduct Authority» — первоисточник не открыт).

### Разбор Г2.6

Бесплатный сектор UK занимает именно ту нишу, где FINPILOT попал бы под art. 39E: персонализированный совет по долгам. Он **авторизован** (не вне периметра, а внутри, с FRN), финансируется **принудительным сбором с отрасли** через MaPS и нацелен на людей в трудностях. Места для платного продукта с тем же содержанием нет по двум причинам сразу: нужна та же авторизация, и потребитель получает аналог бесплатно. Место остаётся у (а) нейтрального планировщика без выбора (пример (15) PERG 17.7, Д14), (б) людей **без** финансовых трудностей, которым бесплатный сектор не адресован (оптимизация досрочного погашения при нормальной платёжеспособности) — но art. 39E охватывает и их (Q3.1–3.2), так что авторизация нужна и тут; (в) B2B — поставщик ПО для авторизованных фирм и благотворительных организаций (конкурентное поле — у MaPS есть гранты на digital transformation для not-for-profit).


**Сверка к Г2.2, п. 2 (снимает 🟡):** Directive 2008/48/EC, CELEX 32008L0048, `r.jina.ai`, HTTP 200, 91 415 байт — строка «advis» в тексте встречается **0 раз**. Режима advisory services и резервирования деятельности в CCD 2008 нет; это новелла CCD II. Переходная ниша по договорам, существующим на 20.11.2026, подтверждена по тексту обеих директив.

---

## ИТОГ ДОБОРА Г2 (11.09.2026)

### По пунктам

| Пункт | Статус | Что добыто / причина недобора |
|---|---|---|
| Г2.1 MCD 2014/17/EU | ✅ добыт | Art. 4(21), 22 (вкл. 22(6)–(7)), 29, 7, 25, 43 — дословно; транспозиция: Германия (§ 34i GewO, § 511, § 655a BGB), Ирландия (S.I. 142/2016, Reg. 3, 23). Толкование Комиссии/EBA/BaFin по досрочному погашению **не найдено**. |
| Г2.2 CCD II 2023/2225 | ✅ добыт (кроме толкований) | Art. 3(21), 16(6)(b)–(c) полностью, 2(2)(l), 29, 36(4), 47, recitals 63, 81; позиция CCPC (Ирландия); транспозиция Италии — по вторичному (Legal500). **Официальных толкований Комиссии/EBA о досрочном погашении не найдено.** Итоговые акты транспозиции Германии и Ирландии не искались. |
| Г2.3 art. 72A RAO / PERG 2.9.18G | ✅ добыт | Статья исключена с 31.12.2020 (S.I. 2019/1361); PERG 2.9.18G — дословно по Wayback 2019; в снимке 2025 раздела нет. Overseas persons exclusion (art. 72 RAO) для debt counselling **не проверялся**. |
| Г2.4 SEC | 🟡 частично | 33-11377 — дословно; IA-1092 — первоисточник добыт, ключевой абзац о «securities in general» — **только по вторичной цитате** (OCR скана нечитаем). **No-action letters по budgeting/wellness-приложениям и публикации пяти названных юрфирм не найдены** (два запроса, в выдаче их нет). |
| Г2.5 UDMSA | ✅ добыт | Официальный текст 2008 (копия на ftc.gov): §§ 2(7), 2(9), 2(13), 2(15), 3, 4 + Comment. Список принявших штатов — **по сниппету** (7 + Виргинские о-ва), карта uniformlaws.org не открыта. |
| Г2.6 UK бесплатный сектор + MoneyHelper | ✅ добыт (кроме суммы levy) | FRN StepChange 729047, Money Advice Trust (National Debtline) 618928 — первоисточники; Citizens Advice — по бюро, по сниппету; финансирование через levy MaPS — первоисточник MAT; MoneyHelper £75–£350/час, среднее £150 — первоисточник через Wayback. Сумма levy 2025/26 **не добыта**. |

### Опровержения и уточнения прежних выводов файла

- 🔴 **§8.3 / §5.8 («Art. 16(3)(c) склоняет к прочтению "советы о выборе кредита"»)** — ослаблено. И MCD (Art. 22(6)(b)), и CCD II (Art. 16(6)(b)–(c)) изымают из резервирования «advisory services **in the context of managing existing debt**»; Ирландия в Reg. 23(7)(d) S.I. 142/2016 выделила ту же категорию и допустила туда «debt management firm authorised by the Central Bank». Систематическое толкование — советы по существующему долгу **внутри** периметра advisory services.
- 🔴 **§«Что не добыто», строка про art. 72A («гипотеза о неприменимости к третьим странам»)** — подтверждено сильнее гипотезы: исключения **нет вовсе** с 31.12.2020, а для не-ЕЭЗ поставщиков его не было никогда.
- 🔴 **§7 / «Итоговая рамка США», п. 1 («Advisers Act — мимо, потому что бумаг не называем»)** — условие недостаточно: по staff-позиции IA-1092 (во вторичной цитате) совет о «securities in general as compared to other investments» уже триггер. Мимо — только если среди направлений распределения нет инвестиций в ценные бумаги.
- 🔴 **§5.7 / «Что не добыто» п. 4 (MoneyHelper £75–£350+/час как цена консультации)** — числа верны, но это цена **финансового советника** (пенсии, ISA), а не долгового совета. Долговой совет в UK массово бесплатен.
- 🟢 **Новое смягчение по ЕС:** CCD II не применяется к договорам, существующим на 20.11.2026 (Art. 2(2)(l)), а в CCD 2008 режима advisory services нет. MCD не применяется к ипотекам до 21.03.2016 (Art. 43(1)).
- 🟢 **Новая нейтральная зона по ЕС:** MCD Art. 22(7) и Irish Reg. 23(9) — услуги, помогающие потребителю «understand their financial needs and **which types of products** are likely to meet those needs», прямо выведены из-под резервирования.

### Сводная таблица (материал исследователя, не юридическое заключение)

| Юрисдикция | Норма | Ловит FINPILOT в B2C? | Ловит в B2B со встраиванием в банк? | Что нужно, чтобы работать легально |
|---|---|---|---|---|
| **ЕС — ипотека** | MCD Art. 4(21), 22(6), 29; DE § 34i GewO; IE Reg. 23(7) S.I. 142/2016 | 🔴 Вероятно да, по ипотекам после 21.03.2016: персональный совет «гасить ипотеку досрочно» — advisory services по систематике Art. 22(6)(b). Коммерческая дерогация есть не везде: DE — Erlaubnis по § 34i, **только с головным офисом в Германии** (§ 34i(2) Nr. 5); IE — закрытый список, коммерческому советнику только через статус intermediary или debt management firm. | 🟢 Банк-кредитор вправе оказывать advisory services (Art. 22(6), первый абзац), но несёт стандарты Art. 22(1)–(3): раскрыть охват линейки, собрать данные, best interests, **record on durable medium**. Расчёт последствий досрочного погашения — обязанность кредитора (Art. 25(4)). | B2C: допуск как credit intermediary / Honorar-Immobiliardarlehensberater в конкретной стране с местным учреждением, без паспорта ЕС; либо нейтральный инструмент «какие **типы** решений подходят» (Art. 22(7)) без выбора за пользователя. B2B: FINPILOT — ПО банка, советует банк. |
| **ЕС — потребкредит** | CCD II Art. 3(17), 16(6), 36; применяется с 20.11.2026 | 🔴 Вероятно да, по договорам после 20.11.2026 (Art. 16(6) — резервирование; коммерческий путь только через (d) «authorised and supervised»). 🟢 По договорам, существующим на 20.11.2026, — вне CCD II (Art. 2(2)(l)), а в CCD 2008 режима нет. Ниша Art. 36 — только некоммерческая и с «limited charges». | 🟢 Кредитор — разрешённый субъект; стандарты Art. 16(2)–(5), обязанности Art. 36(2)–(3) (раннее выявление трудностей, направление к debt advice) — функция, которую FINPILOT может закрывать как ПО. | B2C: авторизация по национальному акту транспозиции (Италия — только зарегистрированные посредники); B2B: ПО банка или ПО для некоммерческих debt advisory services. |
| **UK** | art. 39E RAO, PERG 17; art. 72A **исключена** 31.12.2020 | 🔴 Да (Д14, подтверждено): debt counselling. Онлайн из-за рубежа не спасает — исключения для information society services больше нет. Бесплатный авторизованный сектор (StepChange 729047, MAT 618928, бюро Citizens Advice) занимает эту нишу за счёт levy MaPS. | 🟡 Банк, авторизованный на debt counselling, может давать совет сам; FINPILOT как его ПО — вне периметра, если совет даёт банк (не проверялось отдельно — PERG об аутсорсинге не открывался). | B2C: авторизация FCA на debt counselling либо нейтральный планировщик (пример (15) PERG 17.7). B2B: ПО для авторизованных фирм и благотворительных организаций. |
| **США — федеральный** | Advisers Act § 202(a)(11); IA-1092; 33-11377 | 🟢 Нет, если совет только о долгах, бюджете, резерве, рефинансировании ипотеки. 🔴 Да, если модель сравнивает инвестиции в ценные бумаги **в целом** с другими направлениями (IA-1092, вторичная цитата). Спецрежима ИИ нет (PDA отозвано). | 🟢 Банк исключён из определения; FINPILOT как ПО банка — вне. | Не иметь направления «инвестиции в ценные бумаги» в распределении для американской сборки; иначе регистрация RIA (так сделал Origin). |
| **США — штаты** | UDMSA (7 штатов + Виргинские о-ва, по сниппету); широкие законы типа RCW 18.28.010 (WA) | 🟢 В UDMSA-штатах — нет (нужны посредничество с кредитором и concessions). 🔴 В штатах с широкими законами — вероятно да («counseling … prorating … of the indebtedness … for compensation»). Отсутствие присутствия в штате не спасает (Comment 1 к § 3 UDMSA). | 🟢 Банки изъяты и в UDMSA (§ 3(c)(2)–(3)), и в WA (RCW 18.28.010(1)(b)). | Поштатный обзор; вне UDMSA-штатов — лицензия debt adjuster/credit counselor (часть штатов допускает только nonprofit) или B2B через банк. |

**Общий вывод добора (материал, не заключение).** Во всех трёх западных юрисдикциях ядро FINPILOT — персональная рекомендация по существующему долгу — **внутри** регулируемого периметра, кроме UDMSA-штатов США и переходной ниши ЕС по старым договорам. Единственный сценарий, где продукт работает без собственной лицензии во всех юрисдикциях таблицы, — **B2B-встраивание в банк**: кредитор везде разрешённый субъект (ЕС), изъят из определения (США) или может авторизоваться сам (UK). Цена — стандарты банка ложатся на продукт: раскрытие охвата, best interests, запись рекомендации на durable medium.

**Процесс.** Тип — breadth-first (шесть независимых пунктов по четырём юрисдикциям). Подагентов — **0** (потолок два; пункты закрывались дешевле напрямую через `curl`/`r.jina.ai`). Вызовов `WebSearch` — 13, отказа бюджета не было. Каналы: прямой `curl` (EUR-Lex MCD, gesetze-im-internet § 511/§ 655a, irishstatutebook, legislation.gov.uk, sec.gov с UA-контактом, ftc.gov, stepchange.org, ccpc.ie с `-L`); `r.jina.ai` (EUR-Lex CCD II/CCD 2008, § 34i GewO после таймаута прямого, Money Advice Trust, Legal500, Kitces, Origin); Wayback `id_` + CDX (PERG 2.9 в редакциях 2019 и 2025, MoneyHelper — gzip). Заглушки, отсеянные по размеру: handbook.fca.org.uk 301/167 байт, moneyhelper через jina 561 и 550 байт, sec.gov старый адрес IA-1092 404/53 435 байт.

---

## ДОБОР Г16 — П. Режимы для советующих финсервисов: Казахстан, Армения, Сербия, ОАЭ, Грузия

Добор 12.09.2026, исполнитель без подагентов. Метод: нормы дословно на языке оригинала; у каждого источника URL, канал, HTTP-код, размер. Заключений юриста нет — только буквальное содержание норм.

### П.Казахстан

#### П.КЗ-1. Республиканский режим (АРРФР) — Закон РК «О рынке ценных бумаг» от 02.07.2003 № 461-II

**Источник.** `https://old.adilet.zan.kz/rus/docs/Z030000461_` — канал `curl -sk --http1.1` с браузерным UA, **HTTP 200, 1 029 829 байт**. Перечень изменений в тексте доведён до **Закона РК от 16.01.2026 № 259-VIII**.
Отрицательный канал, для протокола: новый `https://adilet.zan.kz/rus/docs/Z030000461_` — HTTP 200, **2 191 байт** (SPA-заглушка, в разметке комментарий «ИИ-краулеры … видят только эту разметку»); через `r.jina.ai` — HTTP 200, 2 281 байт (только шапка). Старая версия ИПС отдаёт полный текст.

Дословно, **статья 53-2 «Особенности предоставления услуг по инвестиционному консультированию»**:

> «1. Под инвестиционным консультированием понимаются услуги по предоставлению индивидуальным инвесторам инвестиционных рекомендаций по заключению сделок с ценными бумагами и иными финансовыми инструментами (далее – инвестиционная рекомендация).
> Оказывать услуги по инвестиционному консультированию вправе организации, осуществляющие брокерскую и (или) дилерскую деятельность на рынке ценных бумаг и (или) деятельность по управлению инвестиционным портфелем.
> 2. Инвестиционная рекомендация предоставляется индивидуальному инвестору в порядке, определенном нормативным правовым актом уполномоченного органа.
> 3. Инвестиционную рекомендацию вправе предоставлять только [работник лицензиата, осуществляющего] брокерскую и (или) дилерскую деятельность на рынке ценных бумаг и (или) деятельность по управлению инвестиционным портфелем, соответствующий квалификационным требованиям, установленным нормативным правовым актом уполномоченного органа и внутренними документами лицензиата.
> 4. При оказании услуг по инвестиционному консультированию брокер и (или) дилер, управляющий инвестиционным портфелем и их работники обязаны действовать добросовестно с должной осмотрительностью и исключительно в интересах клиента. …»

(Квадратные скобки в п. 3 — фрагмент, выпавший на границе выдержки при извлечении; смысл восстановлен по соседнему окну того же текста, дословная середина фразы не сверена.)

Там же, статья о запрете непрофильной деятельности лицензиата (номер статьи в выдержке не захвачен): «Лицензиат не вправе осуществлять предпринимательскую деятельность, не относящуюся к деятельности на финансовом рынке, за исключением следующих случаев: … 2) предоставления консультационных и информационных услуг по вопросам, связанным с деятельностью на рынке ценных бумаг, с учетом особенностей, установленных статьей 53-2 настоящего Закона; … 4) организации обучения в области деятельности на рынке ценных бумаг».

**Что норма покрывает / не покрывает (буквально).** Предмет ст. 53-2 — рекомендации «по заключению сделок с ценными бумагами и иными финансовыми инструментами». Совет по погашению займа, резерву, бюджету под этот предмет буквально не подпадает (вывод по тексту, не толкование юриста). Отдельного лицензируемого вида «финансовый консультант физлиц / долговой консультант» в выдержках не найдено.

#### П.КЗ-2. Закон РК «О банках и банковской деятельности» от 31.08.1995 № 2444

**Источник.** `https://old.adilet.zan.kz/rus/docs/Z950002444_` — `curl`, **HTTP 200, 1 688 936 байт**.
Дословно (перечень разрешённой банкам неосновной деятельности, подпункт 8): «8) предоставлением консультационных услуг по вопросам, связанным с финансовой деятельностью». То же для банковских холдингов (п. 10 той же статьи): «2) предоставлением консультационных услуг по вопросам, связанным с финансовой деятельностью».
**Буквальное значение:** норма РАЗРЕШАЕТ такие услуги банкам (снимает с них запрет непрофильной деятельности), но не делает их лицензируемой банковской операцией и не резервирует за банками. Нормы, запрещающей нелицензиатам консультировать физлиц по долгам, в законе не найдено (поиск по «консультацион» — 3 вхождения, все приведены или касаются омбудсмана).

#### П.КЗ-3. МФЦА / AIFC — AFSA (отдельный режим, для деятельности «в или из» МФЦА)

**Источник 1.** AIFC General Rules (GEN), Schedule 1 — `https://orderly.myafsa.com/entiresection/a0001000200020007/general-rules` через `r.jina.ai`, **HTTP 200, 126 799 байт** (прямой `curl` на orderly.myafsa.com — **403, 5 878 байт**, антибот). Дата редакции в выдержке не видна.

GEN 1.1.1 (фрагмент): «… a Regulated Activity that may be carried on by an Authorised Firm, subject to the terms of its Licence, if that activity: (a) is specified in the list of activities in Schedule 1; and (b) is carried on by way of business as described in GEN 1.1.9; and (c) is not otherwise excluded in accordance with any other provision in GEN 1.1.»

GEN 1.1.9: «A Person carries on an activity by way of business for the purposes of GEN 1.1.1 if that Person: (a) engages in the activity in a manner which in itself constitutes the carrying on of a business; (b) holds himself out as willing and able to engage in that activity; or (c) regularly solicits other Persons to engage with him in transactions constituting that activity.»

Schedule 1, п. 10: «**10. Advising on Investments** (1) Advising on Investments means giving advice to a Person in his capacity as an investor or potential investor, or in his capacity as agent for an investor or a potential investor, on the merits of his buying, selling, holding, subscribing for or underwriting a particular Investment (whether as principal or agent). (2) In sub‐paragraph (1), "advice" includes a statement, opinion or report: (a) where the intention is to influence a Person, in making a decision, to select a particular Investment or an interest in a particular Investment; or (b) which could reasonably be regarded as being intended to have such an influence.»

Schedule 1, п. 19: «**19. Advising on a Credit Facility** (1) Advising on a Credit Facility means giving advice to a Person in his capacity as a borrower or a potential borrower, or as an agent for a borrower or a potential borrower, on the merits of his entering into a particular Credit Facility. (2) In sub‐paragraph (1), "advice" includes a statement, opinion or report: (a) where the intention is to influence a Person, in making a decision, to enter into a particular Credit Facility; or (b) which could reasonably be regarded as being intended to have such an influence.»

Schedule 1, п. 20 (для контраста): «(1) Arranging a Credit Facility means making arrangements for the provision of a Credit Facility by one or more Persons. (2) A Person does not carry on the Regulated Activity of Arranging a Credit Facility if (a) he is to be a party to the Provision of Credit Facilities in question; or (b) he merely provides the means by which a Person providing a Credit Facility communicates with the Person to whom the Credit Facility is or is to be provided. …»

**Буквально:** п. 19 привязан к «entering into a particular Credit Facility» — к ВСТУПЛЕНИЮ в конкретный кредит. Совет по порядку погашения УЖЕ существующих долгов в формулировку «entering into» буквально не входит (вывод по тексту). Исключения для «generic advice / publications / software» в выданном тексте GEN не найдено: поиск по «newspaper», «Advice given in» — 0 вхождений.

**Источник 2.** AFSA, страницы видов деятельности: `https://afsa.aifc.kz/regulated-activities/advising-on-investments/` (`curl`, **200, 80 096 байт**) и `https://afsa.aifc.kz/regulated-activities/advising-on-a-credit-facility/` (`curl`, **200, 79 320 байт**). Определения совпадают с GEN дословно. Цифры с официальной страницы (Advising on Investments): «Authorisation Fee (paid once) 7 000 USD»; «Registration fee is 500 USD (paid once) if you apply via the self-service portal»; «Supervision Fee (annually) 1 400 USD»; «The Minimum Capital Requirement of Advising on Investments Firms is equal to its Base Capital Requirement (10 000 USD)»; «Liquid Assets whose value is at least equal to 25% of the firm's Annual Operating Expenditure». По Advising on a Credit Facility — «Authorisation Fee (paid once) 7 000 USD».

**Не добыто по КЗ.** (1) Акт АРРФР о «порядке» предоставления инвестиционной рекомендации (п. 2 ст. 53-2) — не искался, бюджет. (2) Прямой нормы о роботизированном совете в РК не найдено ни в законе о РЦБ, ни в законе о банках — отрицательный результат по двум текстам. (3) Номер статьи о запрете непрофильной деятельности лицензиата РЦБ не зафиксирован. (4) AIFC: исключения для генерической/программной рекомендации в GEN не найдены; Guidance AFSA по «advice» vs «information» — не искалась.

### П.Армения

Регулятор — **Центральный банк Республики Армения (ЦБА)**, мегарегулятор (банки, кредитные организации, рынок ценных бумаг).

#### П.АМ-1. Закон РА «О рынке ценных бумаг» от 11.10.2007 HO-195-N

**Источник.** `https://www.arlis.am/hy/acts/182318` — `curl`, **HTTP 200, 546 630 байт**. Официальный перевод на английский («Text of the Official Translation»), шапка: «With changes and additions as of 09.06.2022»; перевод опубликован «on a joint site 12 september 2023».

Дословно, **Article 25. Investment services**: «1. Within the meaning of this Law, the investment services shall mean services where the person: (1) receives and communicates assignments regarding securities transactions from clients; (2) executes securities transactions on its behalf or on behalf of the client and at the expense of the client; (3) **provides consultation to clients regarding the investments in securities**; (4) executes securities transaction at its expense and on its behalf; (5) manages the pool of securities; (6) carries out guaranteed or non-guaranteed placement of securities. …»

**Article 26. Non-basic services**: «Within the meaning of this Law non-basic services shall mean: … (4) provision of consultations to companies on structure of capital, corporate strategy issues … (7) **development and dissemination of researches, financial analyses and other general investment proposals related to securities transactions.** (Article 26 … edited by HO-183-N of 25 March 2020)»

**Article 27. Persons providing investment services**: «2. Investment services and non-basic service specified in point 1 of Article 26 of this Law may be provided only by: (1) the persons providing investment services; (2) persons and bodies specified in Articles 30 and 31 of this Law. 3. **Non-basic services prescribed by points (3), (4) and (7) of Article 26 of this Law may be provided by other persons as well.** …»

**Article 28** (фрагмент): «1. The investment company shall mean a joint-stock or limited liability company that has been issued a licence for providing investment services …»

**Буквально:** граница «регулируемый совет / общая информация» проведена самим законом: консультация клиента по инвестициям в ценные бумаги — инвестиционная услуга (ст. 25(1)(3)), только для лицензиатов (ст. 27(2)); «general investment proposals», исследования и финансовый анализ (ст. 26(7)) — разрешены любым лицам (ст. 27(3)). Долги, бюджет, резерв в предмет закона (ценные бумаги) не входят.

#### П.АМ-2. Официальное разъяснение ЦБА от 22.02.2022 № 1 (иностранный провайдер)

**Источник.** `https://old.cba.am/EN/laregulations/clarification_22022022_eng.pdf` — `curl`, **HTTP 200, 37 276 байт**, `pdftotext` → 6 172 байта. (В тексте разъяснения закон ошибочно датирован «October 11, 2017» в первом абзаце и «October 11, 2007» в резолютивной части.)

Дословно, резолютивная часть: «1. Investment services provided by a foreign financial institution to RA-resident individuals or legal entities are not subject to the provisions of the October 11, 2007 HO-195-N Law on the Securities Market, if the services are carried out in compliance with the following conditions: 1) The offer of investment services by the foreign financial institution is not presented in the form of a public offer (including through advertising carried out via various information and telecommunication platforms, such as on television, radio, the internet, or other mass media, as well as in any other way), the content of which makes it clear that the offer is targeted toward RA residents. 2) The individual offer … does not indicate that the institution intends to gradually disseminate information about its services to a wide audience of RA residents and to regularly provide such services to many RA residents. 2. The provisions of the Law on the Securities Market additionally do not apply to investment services provided by foreign financial institutions to RA-resident individuals or legal entities when the offer of investment services is made or the services are provided at the initiative of the RA resident, regardless of the type or frequency of services provided thereafter.»
Подписано: «Governor of the Central Bank of Armenia Martin Galstyan, February 25, 2022».

#### П.АМ-3. Закон РА «О кредитных организациях» от 29.05.2002 HO-176-N

**Источник.** `https://www.arlis.am/hy/acts/182327` — `curl`, **HTTP 200, 122 056 байт**, официальный перевод, «With changes and additions as of 09.06.2022».
Дословно (перечень того, что вправе делать кредитная организация; номер статьи в выдержке не захвачен): «… (h) provide leasing; (i) accept in deposit precious metals … (j) **provide financial consultation**; (k) establish and maintain customer creditworthiness database, carry out the activities of collection of debts; …»
**Буквально:** финансовая консультация — разрешённая кредитной организации деятельность, а не операция, зарезервированная за лицензиатами.

#### П.АМ-4. Закон РА «О потребительском кредитовании» от 17.06.2008 HO-141-N

**Источник.** `https://www.arlis.am/hy/acts/182395` — `curl`, **HTTP 200, 86 282 байт**, официальный перевод, «With changes and additions as of 24.03.2021».
Дословно, Article 1(1): «This Law shall regulate the relations arising from contracts on crediting, the peculiarities of and mandatory conditions for the types thereof, the procedure and the conditions for calculation of Annual Percentage Rate under contracts on crediting, the liability of the creditor, the rights of consumers under contracts on crediting and other relations pertaining to these contracts.» Article 2(1)(2): «creditor — a bank, branch of foreign bank, credit organisation or pawn shop providing credit».
**Отрицательный результат:** поиск по «ntermediar», «advice», «consult» в тексте закона — **0 вхождений**. Режима кредитного посредника/консультанта по долгам в этом законе нет (в редакции перевода на 24.03.2021).

**Не добыто по Армении.** (1) Нормативные акты ЦБА о правилах оказания инвестиционных услуг (ст. 27(4)) — не искались. (2) Новейшие поправки после 09.06.2022 к закону о РЦБ (включая возможную гармонизацию с MiFID) — английский перевод на arlis их не содержит; армянский текст не сверялся. (3) Отдельной нормы о роботизированном совете — не найдено.

### П.Сербия

Регуляторы — **Komisija za hartije od vrednosti** (рынок капитала, инвестиционные услуги) и **Narodna banka Srbije** (банковские и кредитные услуги, защита пользователей финуслуг).

#### П.RS-1. Zakon o tržištu kapitala («Sl. glasnik RS», br. 129/2021 i 109/2025)

**Источник.** `https://www.paragraf.rs/propisi/zakon_o_trzistu_kapitala.html` — `curl`, **HTTP 200, 905 580 байт**; редакция по шапке: «Sl. glasnik RS", br. 129/2021 i 109/2025». Paragraf.rs — частная правовая база (консолидированный текст), не официальный вестник; официальный ПИС (pravno-informacioni-sistem.rs) не сверялся.

Дословно, **Član 2, stav 1, tačka 2)**: «investicione usluge i aktivnosti koje se odnose na finansijske instrumente iz tačke 19) ovog stava su: (1) prijem i prenos naloga koji se odnose na jedan ili više finansijskih instrumenata; (2) izvršenje naloga za račun klijenata; (3) trgovanje za sopstveni račun; (4) upravljanje portfoliom; (5) **investiciono savetovanje**; …»

**Član 2, tačka 7)**: «**investicioni savet je pružanje lične preporuke klijentu, bilo na zahtev klijenta ili na inicijativu investicionog društva, u pogledu jedne ili više transakcija u vezi sa finansijskim instrumentima**».

**Član 2, tačka 1)**: «investiciono društvo je pravno lice u čije redovne aktivnosti ili poslovanje spada pružanje jedne ili više investicionih usluga trećim licima, odnosno profesionalno obavljanje jedne ili više investicionih aktivnosti».

**Član 3 (Izuzeci)**: «Odredbe Glave VI i Glave VIII ovog zakona ne primenjuju se na: … 3) lica koja pružaju investicione usluge kada se ta usluga pruža povremeno u okviru obavljanja njihove pretežne profesionalne delatnosti, a sama delatnost je uređena zakonskim ili podzakonskim odredbama ili pravilima poslovne etike koji uređuje samu profesiju i kojima se ne zabranjuje pružanje te usluge; … 10) **lica koja pružaju investicione savete u okviru obavljanja druge delatnosti, na koju se ne primenjuju odredbe ovog zakona, pod uslovom da se za pružanje takvih saveta ne naplaćuje posebna naknada.**»

Граница «общая рекомендация» — отдельный режим «investiciona preporuka» (Glava о злоупотреблениях рынком, чл. 291–294): «… preporučuje ili predlaže strategija ulaganja u pogledu jednog ili više finansijskih instrumenata … namenjenih distribucionom kanalu ili javnosti. … Distribucioni kanal je kanal putem kojeg informacija postaje javno dostupna ili će pristup informaciji imati veliki broj lica.» Для таких рекомендаций — требования к содержанию и раскрытию (чл. 292–294), а не лицензия («Davalac investicione preporuke dužan je da u preporuci osigura: 1) da se činjenice jasno razlikuju od tumačenja, procena, mišljenja …», чл. 293).

Лицензирование: «Zahtev za davanje dozvole za obavljanje delatnosti investicionog društva Član 150 …»; «Član 151 Komisija odlučuje o zahtevu … u roku od šest meseci od dana prijema urednog zahteva.»

**Буквально:** лицензируемо — «lična preporuka» по «transakcijama u vezi sa finansijskim instrumentima». Совет по долгам/бюджету в предмет не входит (кредит — не финансовый инструмент по тексту закона; вывод по тексту, не толкование). Исключение чл. 3(10) снимает режим с попутного бесплатного инвест-совета; у FINPILOT совет — основная платная деятельность (подписка), под буквальный текст исключения не подходит.

#### П.RS-2. Zakon o zaštiti korisnika finansijskih usluga («Sl. glasnik RS», br. 19/2025)

**Источник.** `https://www.paragraf.rs/propisi/zakon_o_zastiti_korisnika_finansijskih_usluga.html` — `curl`, **HTTP 200, 198 206 байт**; шапка: «Sl. glasnik RS", br. 19/2025» (новый закон 2025 г.).

Дословно, **Član 2, tačka 41)**: «**savetodavne usluge označavaju lične preporuke u pogledu jedne ili više bankarskih usluga koje korisnik koji se obratio banci zahteva, a koje predstavljaju odvojenu aktivnost u odnosu na bankarske usluge.**»
Član 2, tač. 1), 2), 4): «1) kreditne usluge su usluge koje banka, platna institucija i institucija elektronskog novca pružaju korisnicima ovih usluga po osnovu ugovora o kreditu … 2) bankarske usluge su kreditne usluge i usluge koje pruža banka po osnovu ugovora o depozitu; … 4) finansijske usluge su bankarske usluge, kreditne usluge i usluge finansijskog lizinga».
Член о квалификации (чл. 15): «Zaposleni koji su angažovani na poslovima prodaje finansijskih usluga, odnosno sporednih usluga ili pružanju savetodavnih usluga dužni su da poseduju odgovarajuće kvalifikacije, znanje i iskustvo …»
Там же, об обязанности учитывать положение клиента: «Pri zaključivanju ugovora o finansijskim uslugama i pružanju savetodavnih usluga, davalac usluga dužan je da uzme u obzir sve informacije o okolnostima u kojima se korisnik nalazi …»
Član 3, tač. 1): «Odredbe ovog zakona ne primenjuju se na: 1) ugovore o finansijskim uslugama koji imaju za cilj investiranje u finansijske instrumente, izuzev ugovora o depozitu; …»

**Буквально:** «savetodavne usluge» определены как услуга, которую клиент запрашивает **у банка**; обязанности адресованы «davalac usluga» (банк, платёжная институция и т. п.). Лицензионного режима для небанковского независимого консультанта по кредитам в выдержках не найдено; отдельного вида «kreditni posrednik» в тексте нет (поиск по «posrednik» дал только посредничество НБС в спорах).

**Не добыто по Сербии.** (1) Официальный текст на pravno-informacioni-sistem.rs не сверялся — использован консолидированный текст paragraf.rs. (2) Акты Комиссии о «povremeno» (чл. 3 ст. 1 т. 3) — не искались. (3) Норма о роботизированном совете — не найдена.

### П.ОАЭ

Четыре раздельных периметра: onshore — **ЦБ ОАЭ (CBUAE)** по банковским и кредитным услугам и **SCA** по ценным бумагам (по выдаче поиска SCA переименована в **Capital Market Authority**, домен `uaecma.gov.ae`; в этом добое не проверялось); свободные финансовые зоны — **DIFC/DFSA** и **ADGM/FSRA**. VARA (виртуальные активы, Дубай) к продукту без криптоактивов не относится и не исследовалась.

#### П.AE-DIFC. DFSA Rulebook, General Module (GEN)

Все тексты взяты с `dfsaen.thomsonreuters.com` (официальный хостинг Rulebook DFSA) через `r.jina.ai`.

**GEN 2.11.1 Advising on Financial Products** — `https://dfsaen.thomsonreuters.com/rulebook/gen-2111`, jina **200, 40 409 байт**; действующая редакция «Nov 01 2022», последняя поправка «DFSA RMI328/2022 (Made 29th June 2022). [VER56/11-22]». Дословно:
«(1) In GEN Rule 2.2.2, Advising on Financial Products means giving advice to a Person in his capacity as an investor or potential investor, or in his capacity as agent for an investor or a potential investor, on the merits of his buying, selling, holding, subscribing for or underwriting a particular financial product (whether as principal or agent). (2) Advice in (1) includes a statement, opinion or report: (a) where the intention is to influence a Person, in making a decision, to select a particular financial product or an interest in a particular financial product; or (b) which could reasonably be regarded as being intended to have such an influence. (3) Giving advice to a Person under (1) includes operating an Insurance Aggregation Site relating to contracts of Long-Term Insurance, other than contracts of reinsurance. (4) For the purposes of this Rule and GEN Rule 2.11.2, a "financial product" is: (a) an Investment; (b) a Deposit; (c) a Profit Sharing Investment Account; (d) a right under a contract of Long-Term Insurance, that is not a contract of reinsurance; (e) a right under an Employee Money Purchase Scheme; (f) a right or interest in a pension, superannuation, retirement or gratuity scheme or arrangement, or a broadly similar scheme or arrangement; or (g) a Crypto Token.»

**GEN 2.11.2 (исключение для публикаций)** — `https://dfsaen.thomsonreuters.com/rulebook/gen-2112`, jina **200, 37 558 байт**; редакция «Feb 01 2017». Дословно:
«A Person does not Advise on Financial Products by giving advice in any newspaper, journal, magazine, broadcast service or similar service in any medium if the principal purpose of the publication or service, taken as a whole, is neither: (a) that of giving advice of the kind mentioned in GEN Rule 2.11.1; nor (b) that of leading or enabling Persons to buy, sell, subscribe for or underwrite a particular financial product of the kind in GEN Rule 2.11.1(4).»

**GEN 2.28.1 Arranging Credit and Advising on Credit** — `https://dfsaen.thomsonreuters.com/rulebook/gen-2281`, jina **200, 38 127 байт**; редакция «Feb 01 2017», «[Added] DFSA RM131/2014 … [Amended] DFSA RM184/2016». Дословно:
«(1) In GEN Rule 2.2.2, Arranging Credit and Advising on Credit means: (a) making arrangements for another Person, whether as principal or agent, to borrow money by way of a Credit Facility; or (b) giving advice to a Person in his capacity as a borrower or potential borrower or as agent for a borrower or potential borrower on the merits of his entering into a particular Credit Facility. (2) Advice in (1)(b) includes a statement, opinion or report: (a) where the intention is to influence a Person, in making a decision, to enter into a particular Credit Facility; or (b) which could reasonably be regarded as being intended to have such an influence.»

**GEN 2.28.2** — `https://dfsaen.thomsonreuters.com/rulebook/gen-2282`, jina **200, 37 863 байт**. Дословно: «A Person does not carry on the activity of Arranging Credit under GEN Rule 2.28.1(1)(a) if that Person enters, or is to enter, into the transaction to Provide Credit. …» (исключения GEN 2.28.3–2.28.8 существуют по оглавлению, тексты не добыты).

**Буквально (DIFC):** «financial product» по GEN 2.11.1(4) — инвестиции, депозиты, долгосрочное страхование, пенсии, крипто-токены; кредит в список не входит. Совет по кредиту — отдельная деятельность GEN 2.28.1(1)(b), привязанная к «entering into a particular Credit Facility». Порядок погашения существующих долгов в эту формулировку буквально не входит; совет «положить в депозит / резерв в конкретном продукте» — входит в GEN 2.11.1, если продукт конкретный («a particular financial product»). Исключение GEN 2.11.2 касается изданий, чья основная цель — НЕ совет; сервис, чья основная цель — совет, под него буквально не подпадает.

#### П.AE-ADGM. Financial Services and Markets Regulations 2015 (FSMR), Schedule 1

**Источник.** `https://en.adgm.thomsonreuters.com/node/12877` (официальный хостинг ADGM Rulebook) через `r.jina.ai`, **200, 22 304 байт**; действующая редакция «Dec 18 2023», пометка «Amended on (04 May, 2023)». Глоссарий: `https://en.adgm.thomsonreuters.com/entiresection/11100`, jina **200, 50 768 байт** — «Advising on Investments or Credit Means the Regulated Activity specified in paragraph 28 of Schedule 1 of the FSMR».

Дословно, **Schedule 1, paragraph 28. Advising on Investments or Credit**:
«(1) Advising a person is a specified kind of activity if the advice is — (a) advice on the merits of his doing any of the following (whether as principal or agent) — (i) Buying or Selling a Specified Investment (other than a Credit Facility), a Virtual Asset or a Spot Commodity or subscribing for or underwriting a particular investment which is a Specified Investment (other than a Credit Facility) or a Profit Sharing Investment Account; (ii) exercising any right conferred by such an investment to Buy, Sell, subscribe for or underwrite such an investment; or (iii) **entering into a Credit Facility**; and (b) given to the person in his capacity as (i) an investor or potential investor; (ii) agent for an investor or a potential investor; (iii) Borrower or potential Borrower; or (iv) agent for a Borrower or potential Borrower. (2) In sub-paragraph (1), "advice" includes a statement, opinion or report — (a) where the intention is to influence a person, in making a decision, to select a particular financial product or an interest in a particular investment; or (b) which could reasonably be regarded as being intended to have such an influence.»

Оглавление раздела исключений (`https://en.adgm.thomsonreuters.com/node/12878`, jina **200, 21 200 байт**): «29. Advice given in newspapers etc.»; «30. Other exclusions» — тексты добираются ниже.

**Робо-совет в ADGM (только заголовок и сниппет поиска, документ не открывался):** FSRA «Supplementary Guidance – Digital Investment Management (VER02.061125)», `https://assets.adgm.com/download/assets/supplementary-guidance-authorisation-of-digital-investment-management-robo-advisory-activities.pdf/…`. По сниппету выдачи (пересказ, не норма): Advising on Investments or Credit включает «recommending that a client invest in a portfolio of Financial Instruments», а Digital Investment Manager с разрешением на Managing Assets «will not require separate permissions for Advising on Investments or Credit if it undertakes those Regulated Activities incidentally».

ADGM FSMR Schedule 1, **paragraph 29. Advice given in newspapers etc.** — `https://en.adgm.thomsonreuters.com/node/12879`, jina **200, 22 536 байт**, редакция «Oct 20 2015». Дословно:
«(1) There is excluded from paragraph 28 the giving of advice in writing or other legible form if the advice is contained in a newspaper, journal, magazine, or other periodical Publication, or is given by way of a service comprising regularly updated news or information, if the principal purpose of the Publication or service, taken as a whole and including any advertisements or other promotional material contained in it, is neither — (a) that of giving advice of a kind mentioned in paragraph 28; nor (b) that of leading or enabling persons to Buy, Sell, subscribe for or underwrite Specified Investments. (2) There is also excluded from paragraph 28 the giving of advice in any service consisting of the broadcast or transmission of television or radio programmes, if the principal purpose of the service … is neither of those mentioned in sub-paragraph (1)(a) and (b). (3) The Regulator may, on the application of the proprietor of any such Publication or service as is mentioned in sub-paragraph (1) or (2), certify that it is of the nature described in that paragraph, and may revoke any such certificate if it considers that it is no longer justified. (4) A certificate given under sub-paragraph (3) and not revoked is conclusive evidence of the matters certified.»
Paragraph 30 «Other exclusions» — не добыт.

**Буквально (ADGM):** п. 28(1)(a)(iii) — «entering into a Credit Facility»: как в DIFC и AIFC, привязка к вступлению в кредит. Исключение п. 29 — для периодических изданий и новостных сервисов, чья основная цель не совет; сервис, чья основная цель — совет, буквально под него не подпадает.

#### П.AE-onshore-SCA. Правила SCA о лицензировании финансовой деятельности (Rulebook of Financial Activities, Section 2)

**Источник.** `https://www.sca.gov.ae/assets/7949008c/en-licensing-of-the-financial-activities-and-jobs-approval.aspx` — `curl` без `-L`: **301, 228 байт**; с `-L`: **200, 728 961 байт**, конечный адрес `https://www.uaecma.gov.ae/assets/7949008c/…` (переадресация SCA → CMA подтверждена на уровне HTTP), PDF 1.7, 64 страницы. Документ — «Section (2): The financial activities and jobs approval»; в тексте поправки до «Resolution No. (35/Chairman) of 2023 issued on 3/8/2023 enforced on 16/8/2023».

Дословно, Chapter 1, **Article (2): Scope of application**: «1- The provisions of this section shall apply to any person who practices any of the financial activities or professional jobs specified in this section inside the state. … 2- **No financial activity may be practiced unless after obtaining a license and /or approval on practicing the financial activity from the Authority.** Furthermore, no approved job shall be practiced unless after obtaining an approval from it.»

Перечень финансовой деятельности (Article (1), фрагмент): «1- Trading broker. … 5- Financial Products dealer *. **6- Financial Consultations.** 7- Financial advisor (issuance manager). 8- Listing advisor. 9- Promotion. 10- Introducing. … 12- Portfolios management* …»
Категории лицензий (Chapter 2, Article (2)): «… Fifth category: Arrangement and advice. …»
Среди признаваемых квалификаций сотрудников — «Registered Financial Planner», «Chartered Financial Consultant (ChFC)» (с. 51).

**Чего в этом документе нет:** определения «Financial Consultations» (поиск по «Consultation» — 1 вхождение, только перечень; «Definitions» — 0). Предмет категории по сниппету поиска (Mondaq/Lexology, **пересказ, не норма**): «providing financial consultation and financial analysis on securities for a fee as a regular business». По тексту документа предмет — финансовая деятельность в отношении ценных бумаг; долгов и бюджета он не касается.

#### П.AE-onshore-CBUAE — не исследовано

Режим ЦБ ОАЭ для консультаций по кредитам и личным финансам (Consumer Protection Regulation, Finance Companies Regulation) в этом добое **не открывался** — бюджет вызовов исчерпан на SCA/DFSA/ADGM. Отрицательного результата нет: вопрос остаётся открытым.

**Не добыто по ОАЭ.** (1) CBUAE — целиком, см. выше. (2) Определение «Financial Consultations» из Decision No. 13/RM/2021 (Rulebook, Section 1 «Definitions») — не найдено в скачанной Section 2. (3) DFSA GEN 2.28.3–2.28.8 и ADGM Schedule 1 п. 30 — не открывались. (4) FSRA Supplementary Guidance по робо-совету — известен только сниппет.

### П.Грузия

Регулятор — **Национальный банк Грузии (НБГ)**.

**Источник 1 (актуальный).** `https://matsne.gov.ge/en/document/view/18196` через `r.jina.ai`, **200, 204 947 байт** — английский перевод Закона Грузии «О рынке ценных бумаг» от 24.12.1998 № 1745-IIს; последние поправки в выдержках — «Law of Georgia No 3714 of 16 November 2023 – website, 7.12.2023»; есть вставки с пометкой «Shall become effective from 1 January 2027».
**Источник 2 (устаревший, для протокола).** `https://www.matsne.gov.ge/en/document/download/18196/22/en/pdf` — `curl`, **200, 224 870 байт**, PDF 30 страниц; это публикация № 22 с поправками до 2015 г. Использован только для сверки, нормы процитированы из источника 1.

Дословно, **Article 23 – Activities of a brokerage company**: «A brokerage licence authorises a brokerage company to engage in operations and services related to equity share, shares, bonds, certificates, bills of exchange, cheques and other securities, and as such a brokerage company may: a) **direct consultations to investors on investments, including the price of securities, investment in securities, trading in securities and related foreign exchange transactions**; b) conduct research related to financial instruments and their issuers and ensure the dissemination of the research results and/or recommendations on investments strategies; c) provide consultations to issuers on the issuance of securities and the attractiveness of investments; … f) manage clients' investment portfolios …»

Лицензионная оговорка (номер статьи и её п. 1 с перечнем деятельности в выдержку не попали): «2. An appropriate activity may not be carried out without a licence specified in paragraph 1 of this article and issued by the National Bank of Georgia, except as otherwise provided for by the legislation of Georgia.»

Article 23¹(4) (фрагмент): «Brokerage companies shall not be engaged in activities that are not stipulated by Article 23 of this Law, except …»
Об обязанностях при рекомендациях (статья не зафиксирована): «4. A broker shall be prohibited from giving knowingly misleading recommendations and information to clients on behalf of the brokerage company. A brokerage company shall provide information on the suitability of investments …»

**Отрицательный результат.** В актуальном английском тексте закона поиск по «adviser», «advisor», «investment advice» — **0 вхождений**; отдельного лицензируемого вида «инвестиционный советник» в законе нет. Консультирование инвесторов — вид деятельности в рамках брокерской лицензии (ст. 23(a)); из выдержек не видно, распространяется ли лицензионная оговорка на консультации, которые отдельно от брокерских операций оказывает нелицензиат.
**Пересказ, не норма:** `https://legal.ge/en/service/licensing-and-regulatory-permits-en/investment-advisor-license-georgia` (юрфирма, по сниппету поиска) — «Investment advisor licensing in Georgia is regulated by the National Bank of Georgia … mandatory … for individuals planning to provide individual recommendations on securities»; основание — «the Order of the President of the National Bank "On Approval of the Rule for Licensing Brokerage Companies and Recognizing Investment Advisors"». Сам приказ НБГ не открывался.

**Не добыто по Грузии.** (1) Приказ президента НБГ о лицензировании брокерских компаний и признании инвестиционных советников — не открывался, бюджет. (2) Номер статьи с оговоркой «may not be carried out without a licence» и её п. 1. (3) Нормы о консультациях по потребительскому кредиту и долгам (Органический закон о НБГ, акты НБГ о защите прав потребителей) — не искались. (4) Грузинский оригинал не сверялся, только официальный английский перевод matsne.

### П — итог по странам

Обозначения: (а) персональный совет по долгам и личным финансам без продажи продуктов; (б) то же, выдаётся программой; (в) инвестиционный совет. «Нормы не найдено» — в прочитанных актах нет нормы, требующей лицензии; это не значит, что её нет во всей правовой системе. Выводы в колонках — буквальное содержание прочитанных норм, не юридическое заключение.

| Юрисдикция | Регулятор | (а) | (б) | (в) | Норма-основание | Уверенность | Что не добыто и почему |
|---|---|---|---|---|---|---|---|
| Казахстан (республиканский режим) | АРРФР | нормы не найдено | нормы не найдено (о робо-совете ничего нет) | **да** — только брокер/дилер/управляющий портфелем | Закон о РЦБ № 461-II, ст. 53-2 п. 1 (ред. до 16.01.2026 № 259-VIII); Закон о банках, ст. 8 пп. 8) — разрешение банкам, не резерв | ст. 53-2 прочитана дословно (в п. 3 разрыв на границе выдержки) | акт АРРФР о порядке рекомендации; номер статьи о непрофильной деятельности — не хватило бюджета |
| Казахстан — МФЦА | AFSA | совет по порядку погашения существующих долгов — буквально вне п. 19; совет о вступлении в конкретный кредит — **да** | то же; исключения для ПО не найдено | **да** | AIFC GEN Sch. 1 п. 10, п. 19; GEN 1.1.1, 1.1.9 | прочитано дословно (jina), дата редакции не видна | Guidance AFSA по advice/information — не искалась |
| Армения | ЦБА | нормы не найдено | нормы не найдено | **да** (консультация по инвестициям в ЦБ — инвестиционная услуга); «general investment proposals» — свободны | Закон о РЦБ HO-195-N ст. 25(1)(3), 26(7), 27(2)–(3) (ред. 09.06.2022); Закон о потребкредите — посредников нет; Закон о кредитных организациях — «provide financial consultation» разрешена, не зарезервирована | прочитано дословно (официальный английский перевод) | акты ЦБА по ст. 27(4); поправки после 06.2022 не сверены |
| Сербия | Komisija za HoV; НБС | для небанковского консультанта нормы не найдено; «savetodavne usluge» определены как услуги банка | нормы не найдено | **да** («lična preporuka» по финансовым инструментам); исключение ч. 3 т. 10 — только для попутного бесплатного совета | ZTK (СГ 129/2021, 109/2025) чл. 2 т. 2)(5), т. 7), чл. 3 т. 10; ZZKFU (СГ 19/2025) чл. 2 т. 41 | дословно, но по консолидированному тексту paragraf.rs, не по официальному ПИС | официальный текст ПИС; акты Комиссии о «povremeno» |
| ОАЭ onshore — SCA/CMA | SCA (CMA) | не относится (предмет — ценные бумаги) | не относится | **да** — категория «Financial Consultations», без лицензии деятельность запрещена | Rulebook Section 2, Article (2) Scope, п. 2; перечень, п. 6 | прочитано дословно; определения категории в документе нет — по пересказу юрфирмы | определение «Financial Consultations» (Section 1 Rulebook) |
| ОАЭ onshore — CBUAE | CBUAE | **неясно** | **неясно** | — | — | не исследовано | весь режим CBUAE — бюджет вызовов кончился |
| ОАЭ — DIFC | DFSA | совет о вступлении в конкретный кредит — **да** (GEN 2.28.1(1)(b)); порядок погашения существующих долгов — буквально вне; совет по конкретному депозиту — **да** (GEN 2.11.1(4)(b)) | то же; исключение GEN 2.11.2 — только для изданий, чья основная цель не совет | **да** | GEN 2.11.1 (ред. 01.11.2022), 2.11.2, 2.28.1 (ред. 01.02.2017) | прочитано дословно | GEN 2.28.3–2.28.8 не открывались |
| ОАЭ — ADGM | FSRA | вступление в кредит — **да**; существующий долг — буквально вне | то же; исключение п. 29 — для периодики и новостей, чья основная цель не совет | **да** | FSMR 2015 Sch. 1 п. 28 (ред. 18.12.2023), п. 29 | прочитано дословно | п. 30 Other exclusions; Guidance по робо-совету — только сниппет |
| Грузия | НБГ | нормы не найдено | нормы не найдено | **да** — в рамках брокерской лицензии (ст. 23(a)); отдельного «советника» в законе нет; по пересказу юрфирмы есть приказ НБГ о «признании инвестиционных советников» | Закон о РЦБ № 1745-IIს ст. 23(a), 23¹(4), оговорка «may not be carried out without a licence» (статья не зафиксирована); ред. до 16.11.2023 | закон — дословно (английский перевод); приказ НБГ — пересказ | приказ НБГ; номер статьи лицензионной оговорки; режим для консультаций по потребкредиту |

**Процесс.** Подагентов — 0. Вызовов `WebSearch` — 10, отказа бюджета не было. Всего вызовов инструментов — около 40 (потолок задания). Каналы: прямой `curl` (old.adilet.zan.kz, afsa.aifc.kz, arlis.am, old.cba.am PDF, paragraf.rs, matsne PDF, sca.gov.ae → uaecma.gov.ae с `-L`); `r.jina.ai` (orderly.myafsa.com после 403 прямого, dfsaen.thomsonreuters.com, en.adgm.thomsonreuters.com, matsne view). Отсеянные заглушки: новый adilet.zan.kz — 200/2 191 байт (SPA), тот же через jina — 200/2 281; orderly.myafsa.com прямой — 403/5 878; sca.gov.ae без `-L` — 301/228. Exa и Wayback не понадобились.



## ДОБОР Г16 — О. UK RAO (SI 2001/544) art. 72 «Overseas persons» и art. 39E «Debt-counselling» (дословно)

- Источник: https://www.legislation.gov.uk/uksi/2001/544/article/72 (latest available revised version) — curl, HTTP 200, 137 910 байт; https://www.legislation.gov.uk/uksi/2001/544/article/39E — curl, HTTP 200, 41 259 байт; снято 12.09.2026 ~22:05 МСК.
- Буквальное содержание, без толкования: пункт (5) art. 72 исключает для overseas person по legitimate approach только activities по articles 53 и 55A («giving of advice or the provision of targeted support»). Строки «39E» в тексте art. 72 НЕТ (проверено поиском по снятому тексту: `'39E' in text` → False). Единственное совпадение по шаблону «39[A-Z]» — «39A» в п. (6), который исключает из article 64 соглашения по legitimate approach; к debt-counselling (39E) не относится.
- Пп. (1)–(5F) art. 72 — полностью; хвост (6)–(14) — в полном тексте, снятом в /private/tmp/g16/rao72.txt, тоже переносится ниже.

```text
Overseas persons U.K. 72. —(1) An overseas person does not carry on an activity of the kind specified by article 14 [ F1 , 25D or 25DA ] by— (a) entering into a transaction as principal with or though an authorised person, or an exempt person acting in the course of a business comprising a regulated activity in relation to which he is exempt; or (b) entering into a transaction as principal with a person in the United Kingdom, if the transaction is the result of a legitimate approach. (2) An overseas person does not carry on an activity of the kind specified by article 21 [ F2 , 25D or 25DA ] by— (a) entering into a transaction as agent for any person with or through an authorised person or an exempt person acting in the course of a business comprising a regulated activity in relation to which he is exempt; or (b) entering into a transaction with another party (“X") as agent for any person (“Y"), other than with or through an authorised person or such an exempt person, unless— (i) either X or Y is in the United Kingdom; and (ii) the transaction is the result of an approach (other than a legitimate approach) made by or on behalf of, or to, whichever of X or Y is in the United Kingdom. (3) There are excluded from article 25(1) [ F3 , 25D or 25DA ] arrangements made by an overseas person with an authorised person, or an exempt person acting in the course of a business comprising a regulated activity in relation to which he is exempt. (4) There are excluded from article 25(2) [ F4 , 25D or 25DA ] arrangements made by an overseas person with a view to transactions which are, as respects transactions in the United Kingdom, confined to— (a) transactions entered into by authorised persons as principal or agent; and (b) transactions entered into by exempt persons, as principal or agent, in the course of business comprising regulated activities in relation to which they are exempt. (5) [ F5 There is excluded from articles 53 and 55A the giving of advice or the provision of targeted support by an overseas person ] as a result of a legitimate approach. [ F6 (5A) An overseas person does not carry on an activity of the kind specified by article 25A(1)(a), [ F7 25A(2A), ] 25B(1)(a) [ F8 , 25C(1)(a) or 25E(1)(a) ] if each person who may be contemplating entering into the relevant type of agreement in the relevant capacity is non-resident. (5B) There are excluded from articles 25A(1)(b), 25B(1)(b) [ F9 , 25C(1)(b) and 25E(1)(b) ] arrangements made by an overseas person to vary the terms of a qualifying agreement. (5C) There are excluded from articles 25A(2), 25B(2) [ F10 , 25C(2) and 25E(2) ] , arrangements made by an overseas person which are made solely with a view to non-resident persons who participate in those arrangements entering, in the relevant capacity, into the relevant type of agreement. (5D) An overseas person does not carry on an activity of the kind specified in article 61(1), 63B(1) [ F11 , 63F(1) or 63J(1) ] by entering into a qualifying agreement. (5E) An overseas person does not carry on an activity of the kind specified in article 61(2), 63B(2) [ F12 , 63F(2) or 63J(2) ] where he administers a qualifying agreement. (5F) In paragraphs (5A) to (5E)— (a) “ non-resident ” means not normally resident in the United Kingdom; (b) “ qualifying agreement ” means— (i) in relation to articles 25A and 61, a regulated mortgage contract where the borrower (or each borrower) is non-resident when he enters into it; (ii) in relation to articles 25B and 63B, a regulated home reversion plan where the reversion seller (or each reversion seller) is non-resident when he enters into it; (iii) in relation to articles 25C and 63F, a regulated home purchase plan where the home purchaser (or each home purchaser) is non-resident when he enters into it; [ F13 (iv) in relation to articles 25E and 63J, a regulated sale and rent back agreement where the agreement seller (or each agreement seller) is non-resident when the agreement seller enters into it; ] (c) “ the relevant capacity ” means— (i) in the case of a regulated mortgage contract, as borrower; (ii) in the case of a regulated home reversion plan, as reversion seller or plan provider; (iii) in the case of a regulated home purchase plan, as home purchaser; [ F14 (iv) in the case of a regulated sale and rent back agreement, as agreement seller or agreement provider; ] (d) “ the relevant type of agreement ” means— (i) in relation to article 25A, a regulated mortgage contract; (ii) in relation to article 25B, a regulated home reversion plan; (iii) in relation to article 25C, a regulated home purchase plan [ F15 ; (iv) in relation to article 25E, a regulated sale and rent back agreement ] . ] [ F16 (5G) An overseas person (“ P ”) does not carry on the activity specified by article 63U by providing an ESG rating to a person who is located in the United Kingdom (“ Q ”) where P receives no remuneration in respect of the ESG rating from any person. (5H) In paragraph (5G)— (a) “ ESG rating ” and “ located in the United Kingdom ” have the meanings given in article 63Z7; (b) the reference to P making the rating available is to be interpreted in accordance with the definition of “making available” in article 63Z7; (c) “ remuneration ” means any commission, fee, charge or other payment, including an economic benefit of any kind or any other financial or non-financial advantage or incentive offered or given. ] (6) There is excluded from article 64 any agreement made by an overseas person to carry on an activity of the kind specified by article 25(1) or (2), 37 [ F17 , 39A ] , 40 or 45 if the agreement is the result of a legitimate approach. (7) In this article, “ legitimate approach " means— (a) an approach made to the overseas person which has not been solicited by him in any way, or has been solicited by him in a way which does not contravene section 21 of the Act; or (b) an approach made by or on behalf of the overseas person in a way which does not contravene that section. [ F18 (8) Paragraphs (1) to (5) do not apply where the overseas person is an investment firm or [ F19 qualifying credit institution ] — (a) who is providing or performing investment services and activities on a professional basis; and (b) whose home F20 ... State is the United Kingdom. ] [ F21 (9) Paragraphs (1) to (5) do not apply where the overseas person is providing clearing services as a central counterparty (within the meaning of section 313(1) of the Act). ] [ F22 (9A) Paragraphs (1) to (5) do not apply— (a) where the overseas person is a central securities depository which provides the services referred to in Article F23 ... 25(2) of the CSD regulation in the United Kingdom (including through a branch in the United Kingdom); F24 ... F24 (b) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . ] [ F25 (10) Paragraphs (5A) and (5C) do not apply where the overseas person is a mortgage intermediary whose home F26 ... State is the United Kingdom. ] [ F27 (10A) This article does not apply in the following two cases. ] [ F28 (11) [ F29 The first case is ] where the overseas person is— (a) a third-country firm, as defined by Article 4.1.57 (“definitions”) of the markets in financial instruments directive (“third country firm”); (b) established in a country subject to an equivalence decision; and (c) carrying on an activity a third country firm established in that third country may carry on by virtue of the equivalence decision under— (i) Article 46.1 of the markets in financial instruments regulation (general provisions) if it is registered by ESMA in the register of third country firms established in accordance with Article 48 of that Regulation (register); (ii) Article 47.3 of the markets in financial instruments regulation (equivalence decision) if it has a branch in an EEA State other than the United Kingdom and is authorised in that State in accordance with Article 39 of the markets in financial instruments directive (establishment of a branch); or (iii) Article 46.5 of the markets in financial instruments regulation. [ F30 (11A) The second case is where the overseas person is— (a) a third-country firm, as defined by Article 2.1.42 of the markets in financial instruments regulation; (b) established in a county that is the subject of an equivalence determination; and (c) carrying on an activity a third country firm established in that third country may carry on, by virtue of the equivalence determination, under— (i) Article 46.1 of the markets in financial instruments regulation, if it is registered by the FCA in the register of third country firms established in accordance with Article 48 of that regulation, or (ii) Article 46.5 of that regulation. ] (12) For the purposes of [ F31 paragraphs (11) and (11A) ] — (a) “ equivalence decision ” means a decision adopted by the Commission [ F32 before IP completion day ] in relation to a country under Article 47.1 of the markets in financial instruments regulation which has not been withdrawn by a subsequent decision adopted by the Commission [ F32 before IP completion day ] under that Article; F33 ... (b) a country is subject to an equivalence decision if a period of more than three years has elapsed since the adoption of the decision by the Commission, beginning on the day after the date of the adoption of the decision. ] [ F34 (c) “ equivalence determination ” means a determination made by the Treasury— (i) in regulations under Article 47.1 of the markets in financial instruments regulation and not revoked; or (ii) by direction under regulation 2 of the Equivalence Determinations for Financial Services and Miscellaneous Provisions (Amendment etc) (EU Exit) Regulations 2019 and not revoked; (d) a country is the subject of an equivalence determination if a period of more than three years has elapsed since— (i) the date on which the equivalence determination came into force, or (ii) where two or more equivalence determinations have been made in succession in relation to the country concerned, the date on which the first equivalence determination came into force; (e) for the purposes of sub-paragraph (d), an equivalence determination is not made in succession to an earlier determination if the earlier determination ceased to have effect before the later determination came into force. ] [ F35 (13) This article does not apply to the carrying on of an activity of any of the kinds specified in this article (“the RAO activity”) by an overseas person where— (a) the overseas person is registered in the register in respect of a description of— (i) relevant services, (ii) a category of relevant clients, and (iii) one or more relevant financial instruments, and (b) the activity which the overseas person may carry on by virtue of their registration in the register is in substance the same as the RAO activity, taking account of the financial instruments in relation to which, and the clients in relation to whom, the RAO activity may be carried out. (14) In paragraph (13)— “ register ” is the register maintained by the FCA in accordance with regulation 8 of the Financial Services and Markets Act 2023 (Mutual Recognition Agreement) (Switzerland) Regulations 2025 (the “ Switzerland Regulations ”); “ relevant client ” has the same meaning as in Part 4 of the Switzerland Regulations; “ relevant financial instrument ” has the same meaning as in Part 4 of the Switzerland Regulations; “ relevant service ” has the same meaning as in Part 4 of the Switzerland Regulations. ]
```

Поправки к art. 72 (первые записи блока Textual Amendments; F5 — S.I. 2026/74 о targeted support, в силе 06.04.2026):

```text
Textual Amendments F1 Words in art. 72(1) substituted (1.4.2017 for specified purposes, 3.1.2018 in so far as not already in force) by The Financial Services and Markets Act 2000 (Regulated Activities) (Amendment) Order 2017 (S.I. 2017/488) , arts. 1(2) , 5(2) F2 Words in art. 72(2) substituted (1.4.2017 for specified purposes, 3.1.2018 in so far as not already in force) by The Financial Services and Markets Act 2000 (Regulated Activities) (Amendment) Order 2017 (S.I. 2017/488) , arts. 1(2) , 5(2) F3 Words in art. 72(3) substituted (1.4.2017 for specified purposes, 3.1.2018 in so far as not already in force) by The Financial Services and Markets Act 2000 (Regulated Activities) (Amendment) Order 2017 (S.I. 2017/488) , arts. 1(2) , 5(2) F4 Words in art. 72(4) substituted (1.4.2017 for specified purposes, 3.1.2018 in so far as not already in force) by The Financial Services and Markets Act 2000 (Regulated Activities) (Amendment) Order 2017 (S.I. 2017/488) , arts. 1(2) , 5(2) F5 Words in art. 72(5) substituted (23.2.2026 for specified purposes, 6.4.2026 in so far as not already in force) by The Financial Services and Markets Act 2000 (Regulated Activities) (Providing Targeted Support) (Amendment) Order 2026 (S.I. 2026/74) , art. 1(2) (3) , Sch. para. 1(10) F6 Art. 72(5A)-(5F) substituted (6.11.2006 for specified purposes, 6.4.2007 in so far as not already in force) by The Financial Services and Markets Act 2000 (Regulated Activities) (Amendment) (No.2) Order 2006 (S.I. 2006/2383) , arts. 1(2) , 21 F7 Word in art. 72(5A) inserted (20.4.2015 for specified purposes, 21.12.2015 for specified purposes, 21.3.2016 in so far as not already in force) by The Mortgage Credit Directive Order 2015 (S.I. 2015/910) , art. 1(5) , Sch. 1 para. 4(26)(a) (with Pt. 4 ) F8 Words in art. 72(5A) substituted (1.7.2009 for specified purposes, 30.6.2010 in so far as not already in force) by The Financial Services and Markets Act 2000 (Regulated Activities) (Amendment) Order 2009 (S.I. 2009/1342) , arts. 1(2) , 20(a) F9 Words in art. 72(5B) substituted (1.7.2009 for specified purposes, 30.6.2010 in so far as not already in force) by The Financial Services and Markets Act 2000 (Regulated Activities) (Amendment) Order 2009 (S.I. 2009/1342) , arts. 1(2) , 20(b) F10 Words in art. 72(5C) substituted (1.7.2009 for specified purposes, 30.6.2010 in so far as not already in force) by The Financial Services and Markets Act 2000 (Regulated Activities) (Amendment) Order 2009 (S.I. 2009/1342) , arts. 1(2) , 20(c) F11 Words in art. 72(5D) substituted (1.7.2009 for specified purposes, 30.6.2010 in so far as not already in force) by The Financial Services and Markets Act 2000 (Regulated Activities) (Amendment) Order 2009 (S.I. 2009/1342) , arts. 1(2) , 20(d) F12 Words in art. 72(5E) substituted (1.7.2009 for specified purposes, 30.6.2010 in so far as not already in force) by The Financial Services and Markets Act 2000 (Regulated Activities) (Amendment) Order 2009 (S.I. 2009/1342) , arts. 1(2) , 20(e) F13 Art. 72(5F)(b)(iv) inserted (1.7.2009 for specified purposes, 30.6.2010 in so far as not already in force) by The Financial Services and Markets Act 2000 (Regulated Activities) (Amendment) Order 2009 (S.I. 2009/1342) , arts. 1(2) , 20(f) F14 Art. 72(5F)(c)(iv) inserted (1.7.2009 for specified purposes, 30.6.2010 in so far as not already in force) by The Financial Services and Markets Act 2000 (Regulated Activities) (Amendment) Order 2009 (S.I. 2009/1342) , arts. 1(2) , 20(g) F15 Art. 72(5F)(d)(iv) and semi-colon inserted (1.7.2009 for specified purposes, 30.6.2010 in so far as not already in force) by The Financial Services and Markets Act 2000 (Regulated Activities) (Amendment) Order 2009 (S.I. 2009/1342) , arts. 1(2) , 20(h) F16 Art. 72(5G)(5H) inserted (16.12.2025 for specified purposes) by The Financial Services and Markets Act 2000 (Regulated Activities) (ESG Ratings) Order 2025 (S.I. 2025/1349) , arts. 2 , 7 (with arts. 8-22 ) F17 Word in art. 72(6) inserted (31.10.2004 for specified purposes, 14.1.2005 in so far as not already in force) by The Financial Services and Markets Act 2000 (Regulated Activities) (Amendment) (No. 2) Order 2003 (S.I. 2003/1476) , arts. 1(3) , 10(6) F18 Art. 72(8) inserted (1.4.2007 for specified purposes, 1.11.2007 in so far as not already in force) by The Financial Services and Markets Act 2000 (Regulated Activities) (Amendment No. 3) Order 2006 (S.I. 2006/3384) , arts. 1(2) , 24(e) F19 Words in art. 72(8) substituted (31.12.2020) by The Financial Services and Markets Act 2000 (Amendment) (EU Exit) Regulations 2019 (S.I. 2019/632) , regs. 1(3) , 147(2) (with savings in S.I. 2019/680 , reg. 11 (as amended by S.I. 2019/1212 , regs. 1(3) , 22(3) ); 2020 c. 1 , Sch. 5 para. 1(1) F20 Word in art. 72(8)(b) omitted (31.12.2020) by virtue of The Financial Services and Markets Act 2000 (Amendment) (EU Exit) Regulations 2019 (S.I. 2019/632) , regs. 1(3) , 147(3) (with savings in S.I. 2019/680 , reg. 11 (as amended by S.I. 2019/1212 , regs. 1(3) , 22(3) ); 2020 c. 1 , Sch. 5 para. 1(1) F21 Art. 72(9) inserted (1.4.2013) by The Financial Services and Markets Act 2000 (Over the Counter Derivatives, Central Counterparties and Trade Repositories) Regulations 2013 (S.I. 2013/504) , regs. 1(2) , 33(5) (with regs. 52-58 ) F22 Art. 72(9A) inserted (28.11.2017) by The Central Securities Depositories Regulations 2017 (S.I. 2017/1064) , reg. 1 , Sch. para. 23(3) (with regs. 7(4) , 8(4) , 9(1) ) F23 Words in art. 72(9A)(a) omitted (31.12.2020) by virtue of The Financial Services and Markets Act 2000 (Amendment) (EU Exit) Regulations 2019 (S.I. 2019/632) , regs. 1(3) , 147(4)(a) (with savings in S.I. 2019/680 , reg. 11 (as amended by S.I. 2019/1212 , regs. 1(3) , 22(3) ); 2020 c. 1 , Sch. 5 para. 1(1) F24 Art. 72(9A)(b) and word omitted (31.12.2020) by virtue of The Financial Services and Markets Act 2000 (Amendment) (EU Exit) Regulations 2019 (S.I. 2019/632) , regs. 1(3) , 147(4)(b) (with savings in S.I. 2019/680 , reg. 11
```

art. 39E:

```text
[ F1 Debt-counselling U.K. 39E. — (1) Giving advice to a borrower about the liquidation of a debt due under a credit agreement is a specified kind of activity. (2) Giving advice to a hirer about the liquidation of a debt due under a consumer hire agreement is a specified kind of activity. ] Textual Amendments F1 Pt. II Ch. 7B inserted (26.7.2013 for specified purposes, 1.4.2014 in so far as not already in force) by The Financial Services and Markets Act 2000 (Regulated Activities) (Amendment) (No.2) Order 2013 (S.I. 2013/1881) , art. 1(2) (6) , 5
```


## ДОБОР Г16 — Н. Транспозиция CCD II (Directive (EU) 2023/2225): Германия и Ирландия

### Германия — итоговый акт принят и опубликован

- Акт: «Gesetz zur Umsetzung der Richtlinie (EU) 2023/2225 über Verbraucherkreditverträge und zur Regelung der Förderung klimaneutraler Mobilität» vom 12. Mai 2026, BGBl. 2026 I Nr. 139 vom 18.05.2026; ELI https://www.recht.bund.de/eli/bund/bgbl-1/2026/139
- Источники: карточка https://www.recht.bund.de/bgbl/1/2026/139/VO.html (curl, HTTP 200, 37 948 байт); официальный PDF https://www.recht.bund.de/bgbl/1/2026/139/regelungstext.pdf?__blob=publicationFile&v=1 (curl, HTTP 200, 921 242 байт; pdftotext 193 391 знак). Снято 12.09.2026 ~22:15 МСК.
- Структура (заголовки статей из PDF): Art. 1 BGB; Art. 2 EGBGB (Art. 247 — информация); Art. 3 BDSG; Art. 4 UKlaG; Art. 5 EU-VSchDG; Art. 6 UWG; Art. 7 GewO; Art. 8 PAngV; Art. 9 KWG; Art. 10 InstitutsVergV; Art. 11 FinDAG; Art. 12 FinDAGebV; Art. 13 VVG; Art. 14 новый Absatzfinanzierungsaufsichtsgesetz (AbsFinAG); Art. 15 KliNeMFöG; Art. 16 Inkrafttreten.
- В тексте есть отсылка к отдельному закону «Gesetz über den Zugang zu Schuldnerberatungsdiensten für Verbraucher» (обязанность кредитора направлять заёмщика в трудностях к службам долгового консультирования, ст. 36 CCD II) — сам этот закон в Nr. 139 не содержится; его реквизиты не добыты.

Art. 16 Inkrafttreten — дословно:

```text
Artikel 16
Inkrafttreten
(1) Dieses Gesetz tritt vorbehaltlich des Absatzes 2 am 20. November 2026 in Kraft.
(2) Am Tag nach der Verkündung treten in Kraft:
1. Artikel 1 Nummer 6 Buchstabe c und Nummer 19,
2. in Artikel 7 Nummer 6 § 34l der Gewerbeordnung sowie
3. Artikel 15.

Die verfassungsmäßigen Rechte des Bundesrates sind gewahrt.
Das vorstehende Gesetz wird hiermit ausgefertigt. Es ist im Bundesgesetzblatt zu verkünden.

Berlin, den 12. Mai 2026
Der Bundespräsident
Steinmeier
Der Bundeskanzler
Merz
Die Bundesministerin
d e r J u s t i z u n d f ü r Ve r b r a u c h e r s c h u t z
Stefanie Hubig

Seite 37 von 51

Bundesgesetzblatt Jahrgang 2026 Teil I Nr. 139, ausgegeben zu Bonn am 18. Mai 2026

Seite 38 von 51

EU-Rechtsakte:
1. Richtlinie 93/13/EWG des Rates vom 5. April 1993 über missbräuchliche Klauseln in Verbraucherverträgen
(ABl. L 95 vom 21.4.1993, S. 29), die zuletzt durch die Richtlinie (EU) 2019/2161 vom 27. November 2019
(ABl. L 328 vom 18.12.2019, S. 7) geändert worden ist
2. Empfehlung 2003/361/EG der Kommission vom 6. Mai 2003 betreffend die Definition der Kleinstunternehmen
sowie der kleinen und mittleren Unternehmen (ABl. L 124 vom 20.5.2003, S. 36)
3. Richtlinie 2005/36/EG des Europäischen Parlaments und des Rates vom 7. September 2005 über die
Anerkennung von Berufsqualifikationen (ABl. L 255 vom 30.9.2005, S. 22; L 271 vom 16.10.2007, S. 18; L 93
vom 4.4.2008, S. 28; L 33 vom 3.2.2009, S. 49; L 305 vom 24.10.2014, S. 115), die zuletzt durch die Delegierte
Richtlinie (EU) 2024/782 vom 4. März 2024 (ABl. L, 2024/782, 31.5.2024) geändert worden ist
4. Verordnung (EU) Nr. 260/2012 des Europäischen Parlaments und des Rates vom 14. März 2012 zur Festlegung
der technischen Vorschriften und der Geschäftsanforderungen für Überweisungen und Lastschriften in Euro und
zur Änderung der Verordnung (EG) Nr. 924/2009 (ABl. L 94 vom 30.3.2012, S. 22), die zuletzt durch die
Verordnung (EU) 2024/886 vom 13. März 2024 (ABl. L, 2024/886, 19.3.2024) geändert worden ist
5. Verordnung (EU) 2015/751 des Europäischen Parlaments und des Rates vom 29. April 2015 über
Interbankenentgelte für kartengebundene Zahlungsvorgänge (ABl. L 123 vom 19.5.2015, S. 1), die durch die
Delegierte Verordnung (EU) 2018/72 vom 4. Oktober 2017 (ABl. L 13 vom 18.1.2018, S. 1) geändert worden ist
6. Richtlinie (EU) 2015/1535 des Europäischen Parlaments und des Rates vom 9. September 2015 über ein
Informationsverfahren auf dem Gebiet der technischen Vorschriften und der Vorschriften für die Dienste der
Informationsgesellschaft (ABl. L 241 vom 17.9.2015, S. 1)
```

Отсылка к Schuldnerberatungsdienste (Art. 1, изменения BGB) — дословно, строки PDF:

```text
Abschnitten 3, 4 und 13 des in Artikel 247 § 1 Absatz 2 Satz 2 des Einführungsgesetzes zum Bürgerlichen
Gesetzbuche genannten Musters und entsprechend Artikel 246b § 1 Absatz 1 Nummer 16 des Einführungs­
gesetzes zum Bürgerlichen Gesetzbuche unterrichtet hat.“
16. In § 496 Absatz 2 Satz 1 wird nach der Angabe „unverzüglich“ die Angabe „vom bisherigen Darlehensgeber“
eingefügt.
17. Nach § 497 wird der folgende § 497a eingefügt:
„§ 497a
Zahlungsrückstände und Nachsichtsmaßnahmen bei Allgemein-Verbraucherdarlehen
(1) Der Darlehensgeber ist verpflichtet, den Darlehensnehmer eines Allgemein-Verbraucherdarlehens­
vertrags, der Schwierigkeiten bei der Erfüllung seiner finanziellen Verpflichtungen hat, an Schuldnerberatungs­
dienste nach dem Gesetz über den Zugang zu Schuldnerberatungsdiensten für Verbraucher zu verweisen, die
für den Darlehensnehmer leicht zugänglich sind.
(2) Der Darlehensgeber muss, sofern angebracht, angemessene Nachsicht walten lassen, bevor er ein
Zwangsvollstreckungsverfahren zur Durchsetzung seiner Ansprüche im Zusammenhang mit einem AllgemeinVerbraucherdarlehensvertrag einleitet. Die gegebenenfalls zu ergreifenden Maßnahmen der Nachsicht müssen
unter anderem den individuellen Umständen des jeweiligen Darlehensnehmers Rechnung tragen. Sie können
unter anderem aus einer vollständigen oder anteiligen Umschuldung des Darlehens bestehen und umfassen
eine Änderung der Bedingungen des Darlehensvertrags, die unter anderem Folgendes umfassen kann:
1. eine Verlängerung der Laufzeit des Darlehensvertrags,
2. eine Änderung der Art des Darlehensvertrags,
3. einen Zahlungsaufschub für alle oder einen Teil der Rückzahlungsraten in einem bestimmten Zeitraum,

Bundesgesetzblatt Jahrgang 2026 Teil I Nr. 139, ausgegeben zu Bonn am 18. Mai 2026
```

Новый § 511 BGB «Beratungsleistungen» (Art. 1 Nr. 32) — дословно:

```text
Beratungsleistungen bei Verbraucherdarlehensverträgen“.
32. § 511 wird wie folgt geändert:
a) Die Überschrift wird durch die folgende Überschrift ersetzt:
„§ 511
Beratungsleistungen bei Verbraucherdarlehensverträgen“.

Bundesgesetzblatt Jahrgang 2026 Teil I Nr. 139, ausgegeben zu Bonn am 18. Mai 2026

Seite 9 von 51

b) Absatz 1 wird durch den folgenden Absatz 1 ersetzt:
„(1) Der Darlehensgeber hat den Darlehensnehmer zu informieren, ob für ihn individuelle Empfehlungen
zu einem oder mehreren Geschäften, die im Zusammenhang mit einem Verbraucherdarlehensvertrag stehen
(Beratungsleistungen), erbracht werden oder erbracht werden können. Bevor der Darlehensgeber für den
Darlehensnehmer solche Beratungsleistungen erbringt, hat er den Darlehensnehmer über die sich aus
Artikel 247 § 18 des Einführungsgesetzes zum Bürgerlichen Gesetzbuche ergebenden Einzelheiten in der
dort vorgesehenen Form zu informieren.“
c) Absatz 3 wird durch die folgenden Absätze 3 und 4 ersetzt:
„(3) Der Darlehensgeber hat dem Darlehensnehmer auf Grund der Prüfung gemäß Absatz 2 in dessen
bestem Interesse ein geeignetes oder mehrere geeignete Produkte zu empfehlen oder ihn darauf
hinzuweisen, dass er kein Produkt empfehlen kann. Die Empfehlung oder der Hinweis ist dem
Darlehensnehmer bei einem Immobiliar-Verbraucherdarlehensvertrag auf einem dauerhaften Datenträger
und bei einem Allgemein-Verbraucherdarlehensvertrag auf Papier oder auf einem anderen im Vertrag über
die Erbringung der Beratungsleistung benannten dauerhaften Datenträger nach Wahl des Darlehensnehmers
zur Verfügung zu stellen.
(4) Der Darlehensgeber ist verpflichtet, den Darlehensnehmer zu warnen, wenn ein Verbraucher­
darlehensvertrag unter Berücksichtigung der finanziellen Situation des Darlehensnehmers möglicherweise
ein spezifisches Risiko für ihn birgt.“
33. § 512 Satz 1 wird durch den folgenden Satz ersetzt:
„Von den Vorschriften der §§ 491 bis 511 darf, soweit nicht etwas anderes bestimmt ist, nicht zum Nachteil des
Verbrauchers abgewichen werden.“
34. Buch 2 Abschnitt 8 Titel 3 Untertitel 6 wird gestrichen.
35. Die Überschrift des Buchs 2 Abschnitt 8 Titel 10 Untertitel 2 wird durch die folgende Überschrift ersetzt:
„Untertitel 2
Vermittlung von Verbraucherdarlehensverträgen und Finanzierungshilfen“.
36. § 655a wird wie folgt geändert:
a) Absatz 1 wird wie folgt geändert:
aa) In Satz 1 Nummer 1 wird die Angabe „entgeltliche Finanzierungshilfe“ durch die Angabe „Finanzierungs­
hilfe nach § 506“ ersetzt.
bb) Satz 2 wird durch den folgenden Satz ersetzt:
„Bei Finanzierungshilfen nach § 506, die den Ausnahmen des § 491 Absatz 2 Satz 2 Nummer 1 bis 3 und
Absatz 3 Satz 2 entsprechen, gelten die Vorschriften dieses Untertitels nicht.“
b) Absatz 2 wird durch den folgenden Absatz 2 ersetzt:
„(2) Der Darlehensvermittler ist verpflichtet, den Verbraucher nach Maßgabe des Artikels 247 § 13
Absatz 2 und § 13b Absatz 1 und des Artikels 247a § 2 des Einführungsgesetzes zum Bürgerlichen
Gesetzbuche zu informieren. Der Darlehensvermittler ist gegenüber dem Verbraucher zusätzlich wie ein
Darlehensgeber gemäß § 491a verpflichtet. Satz 2 gilt hinsichtlich § 491a Absatz 1 und 2 nicht für
Warenlieferanten oder Dienstleistungserbringer, die in lediglich untergeordneter Funktion als Darlehens­
vermittler von Allgemein-Verbraucherdarlehen oder von entsprechenden Finanzierungshilfen tätig werden,
etwa indem sie als Nebenleistung den Abschluss eines verbundenen Verbraucherdarlehensvertrags
vermitteln.“
c) Absatz 3 Satz 1 und 2 wird durch die folgenden Sätze ersetzt:
„Bietet der Darlehensvermittler im Zusammenhang mit der Vermittlung eines Verbraucherdarlehensvertrags
oder einer entsprechenden Finanzierungshilfe nach § 506 Beratungsleistungen gemäß § 511 Absatz 1 an, so
gilt § 511 entsprechend. § 511 Absatz 2 Satz 2 gilt bei der Vermittlung eines Immobiliar-Verbraucher­
darlehensvertrages oder einer entsprechenden Finanzierungshilfe entsprechend mit der Maßgabe, dass
der Darlehensvermittler eine ausreichende Zahl von am Markt verfügbaren Darlehensverträgen zu prüfen
hat.“
37. § 655b wird durch den folgenden § 655b ersetzt:
„§ 655b
Textform bei einem Vertrag mit einem Verbraucher
(1) Der Darlehensvermittlungsvertrag mit einem Verbraucher bedarf der Textform. Der Vertrag darf nicht mit
dem Antrag auf Hingabe des Darlehens oder der Finanzierungshilfe gemäß § 506 verbunden werden. § 492
Absatz 1a gilt entsprechend. Der Darlehensvermittler hat dem Verbraucher den Vertragsinhalt in Textform
mitzuteilen.
(2) Ein Darlehensvermittlungsvertrag mit einem Verbraucher, der den Anforderungen des Absatzes 1 Satz 1
und 2 nicht genügt oder vor dessen Abschluss die Pflichten aus Artikel 247 § 13 Absatz 2, § 13b Absatz 1 sowie
§ 18 des Einführungsgesetzes zum Bürgerlichen Gesetzbuche nicht erfüllt worden sind, ist nichtig.“

Bundesgesetzblatt Jahrgang 2026 Teil I Nr. 139, ausgegeben zu Bonn am 18. Mai 2026

```

### Ирландия — итоговый акт НЕ найден

- Три поиска 12.09.2026 (WebSearch: «Ireland transposition … S.I. 2025», «"European Union (Consumer Credit" Regulations 2026 Ireland», «Ireland Consumer Credit Bill 2026 general scheme») не нашли ни S.I., ни законопроекта о транспозиции. Юрфирмы (A&L Goodbody https://www.algoodbody.com/insights-publications/consumer-credit-directive-2-ccd2-what-consumer-lenders-in-ireland-need-to-know ; Mason Hayes Curran https://www.mhc.ie/latest/insights/new-rules-on-consumer-credit-and-distance-marketing) по пересказу выдачи пишут: транспонирующий акт не опубликован, несмотря на срок 20.11.2025; применение CCD II — с 20.11.2026. Консультация Минфина по 23 национальным дискрециям закрылась 16.10.2024: https://www.gov.ie/en/department-of-finance/consultations/public-consultation-on-the-implementation-of-the-consumer-credit-directive-2/
- В irishstatutebook найден «Credit Review Act 2026» (Number 1 of 2026) — по названию это закон о Credit Review Office, к транспозиции CCD II по выдаче не относится; не открывался.
- Статус: неизвестно, принят ли акт между июлем и сентябрём 2026 — первоисточник (irishstatutebook.ie, перечень S.I. 2026) целиком не просматривался.

## ДОБОР Г16 — Р (часть 1). Stripe: условия о запрещённых бизнесах и санкциях

- Источник: https://stripe.com/legal/restricted-businesses — curl HTTP 200, 214 495 байт (текст в JS); через r.jina.ai HTTP 200, 28 425 байт. Снято 12.09.2026 ~22:15 МСК.
- Выдержки дословно (строки markdown прокси; пропуски [...]):

```text

## High-Risk Jurisdictions and Persons

Use of Stripe's services for any dealings, engagement, or sale of goods or services either directly or indirectly with the following are prohibited:

#### High-risk jurisdictions

Persons located in, resident in, or a citizen of, or products or services originating from jurisdictions that Stripe has determined for various reasons, including legal, contractual, and commercial reasons, to be prohibited, including, Cuba, Iran, North Korea, and Syria, and the Crimea, Donetsk, and Luhansk regions.

#### High-risk persons

Persons Stripe has determined for various reasons, including legal, contractual, and commercial reasons, to be prohibited, such as those individuals or entities named to a restricted person or party list of, or otherwise restricted by, the United States, United Kingdom, European Union, or United Nations, including the sanctions maintained by the US Office of Foreign Assets Control or the Denied Persons List or Entity List maintained by the US Department of Commerce.

Additionally, it's prohibited to use Stripe's products and services to directly or indirectly:

#### Prohibited services

Export, re-export, sell, or supply accounting services; trust and corporate formation services; management consulting services; architecture services; engineering services; quantum computing services; information technology (IT) consultancy and design services; and IT-support services and cloud-based services for enterprise management software and design and manufacturing software to any person located in Russia. In the European Union and the United Kingdom, it is prohibited to use Stripe's products and services, directly or indirectly, to provide credit-rating services, market research and public relations services, advertising services, auditing services, or legal advisory services to any person located in Russia.

#### Prohibited goods

Deal in any goods prohibited by law for export to or import from Russia (for example, luxury goods, sensitive goods included in the Common High Priority Items List, enterprise management software and design software).

You must not use Stripe's services for any illegal activities or for the businesses or product types listed below. The types of businesses listed here are representative of prohibited categories, but this is not an exhaustive list.

#### Any illegal products and services
[...]

*    Any artificial-intelligence generated content that meets the above criteria

#### Debt relief companies

*    Debt settlement, debt negotiation, and debt consolidation

#### The following financial products and services

*    ATMs

*    Check cashing

*    Debt collection agencies

*    Funded prop trading

*    Money orders and traveler's checks

*    Payable-through accounts
[...]

#### Lending and credit

*    Loan repayments with credit cards

*    Credit monitoring, credit repair, and counseling services

#### Marijuana(see the[FAQ](https://support.stripe.com/questions/prohibited-and-restricted-businesses-list-faqs)s for additional details)

*    Cannabis products
```

- https://support.stripe.com/questions/uae-account-activation-requirements — curl и r.jina.ai отдали пустую страницу (174–209 байт), текста нет. Пересказ поисковой выдачи (не Stripe): для счёта Stripe UAE нужна торговая лицензия ОАЭ (mainland или free zone); для представителей и владельцев ≥25 % — паспорт, Emirates ID и резидентская виза, если они не граждане ОАЭ/GCC и живут в ОАЭ.
- https://stripe.com/legal/ssa (HTTP 200, 289 353 байт): ОАЭ и Кипр обслуживает контрагент «Stripe Payments Europe, Limited» (таблица Stripe Contracting Entity, дословно: «United Arab Emirates Stripe Payments Europe, Limited»; Кипр — в списке стран ЕЭЗ того же контрагента). Слово «sanction» в тексте SSA, снятом curl, не найдено — вероятно, санкционный пункт в подгружаемой части; не проверено.
- https://support.stripe.com/questions/stripe-and-sanctions — HTTP 404.


### Германия — отдельный закон о службах долгового консультирования (SchuBerDG): НЕ вступил, в согласительной процедуре

- Акт: «Gesetz über den Zugang zu Schuldnerberatungsdiensten für Verbraucher (Schuldnerberatungsdienstegesetz – SchuBerDG)», Drucksache Bundestag 21/1847, Bundesrat 701/25; реализует ст. 36 CCD II (доступ к независимым службам долгового консультирования).
- Карточка Бундесрата https://www.bundesrat.de/SharedDocs/beratungsvorgaenge/2025/0701-0800/0701-25.html (r.jina.ai HTTP 200, 16 812 байт) — дословно ход дела:

```text
    *   [Reden](https://www.bundesrat.de/DE/service/archiv/reden-archiv/reden-archiv-node.html)
    *   [Themenarchiv](https://www.bundesrat.de/DE/service/archiv/themenarchiv/themenarchiv-node.html)
    *   [Fotos](https://www.bundesrat.de/DE/service/archiv/fotoarchiv/fotoarchiv-node.html)
*   [Mediathek Videoarchiv zu Plenarsitzungen und Veranstaltungen](https://www.bundesrat.de/DE/service/mediathek/mediathek-node.html)
*   [Livestream Streamingangebote des Bundesrates während der Plenarsitzungen](https://www.bundesrat.de/DE/service/livestream/livestream-node.html)
*   [App des Bundesrates Alles Wesentliche zum Bundesrat - zu jeder Zeit, an jedem Ort](https://www.bundesrat.de/DE/service/app/app-node.html)
*   [Social Media Der Bundesrat in den sozialen Netzwerken](https://www.bundesrat.de/DE/service/socialmedia/socialmedia-node.html)
*   [Stellenangebote Stellenausschreibungen des Sekretariats des Bundesrates](https://www.bundesrat.de/DE/service/stellen/stellen-node.html)
*   [Öffentliche Ausschreibungen Lieferleistungen und Dienstleistungen](https://www.bundesrat.de/DE/service/ausschreibungen/ausschreibungen-node.html)
*   [Glossar](https://www.bundesrat.de/DE/service/glossar/glossar_node.html)
*   [Abkürzungen](https://www.bundesrat.de/DE/service/abkuerzungen/abkuerzungen-node.html)
# Sie sind hier:
1.   [Startseite](https://www.bundesrat.de/DE/homepage/homepage-node.html)
2.   [Service](https://www.bundesrat.de/DE/service/service-node.html)
3.   [Archiv](https://www.bundesrat.de/DE/service/archiv/archiv-node.html)
4.   [Drucksachen](https://www.bundesrat.de/DE/service/archiv/bv-archiv/bv-archiv-node.html)
5.   **Gesetz über den Zugang zu Schuldnerberatungsdiensten für Verbraucher (Schuldnerberatungsdienstegesetz - SchuBerDG)**
[](https://www.bundesrat.de/)
## 701/25
## [Gesetz über den Zugang zu Schuldnerberatungsdiensten für Verbraucher (Schuldnerberatungsdienstegesetz - SchuBerDG)](https://www.bundesrat.de/SharedDocs/beratungsvorgaenge/2025/0701-0800/0701-25.html?topNr=701%2F25#top-701/25)
28.11.2025
```

- Бундестаг, текстовый архив 2026 kw20 «Gesetz zu Schuldnerberatungsdiensten im Vermittlungsausschuss» https://www.bundestag.de/dokumente/textarchiv/2026/kw20-vermittlungsausschuss-1178424 (curl HTTP 200, 721 233 байт) — дословно фрагмент:

```text
) zu dem Gesetzentwurf. Neben den Grünen stimmte nur Die Linke dafür, Union, AfD und SPD lehnten ihn ab.
Mit den Stimmen von CDU/CSU, SPD und Bündnis 90/Die Grünen beschloss das Parlament eine Entschließung zu dem Gesetz. Dagegen stimmten die AfD und Die Linke.
Der Bundesrat hat am 
Freitag, 8. Mai 2026
, beschlossen dem Gesetz nicht zuzustimmen (
21/5883
(Dokument, öffnet ein neues Fenster)
).
Gesetzentwurf der Bundesregierung
Mit dem Gesetz über den Zugang zu Schuldnerberatungsdiensten für Verbraucher (
21/1847
(Dokument, öffnet ein neues Fenster)
) werden Vorgaben der EU-Verbraucherkreditrichtlinie 2023 / 2225 in deutsches Recht umgesetzt. Danach haben die Mitgliedstaaten sicherzustellen, dass Verbraucherinnen und Verbraucher, die Schwierigkeiten bei der Erfüllung ihrer finanziellen Verpflichtungen haben oder haben könnten, Zugang zu unabhängigen Schuldnerberatungsdiensten erhalten, für die nur begrenzte Entgelte zu entrichten sind. Die Richtlinie verpflichtet die Mitgliedstaaten, die entsprechenden Rechts- und Verwaltungsvorschriften bis spätestens 20. November 2025 umzusetzen.
Vorgesehen ist, dass die Länder die Verfügbarkeit unabhängiger Schuldnerberatungsdienste sicherstellen. Diese Dienste sollen für Verbraucherinnen und Verbraucher „grundsätzlich kostenlos“ sein. Die Erhebung eines begrenzten Entgelts ist demnach möglich, sofern es höchstens die Betriebskosten deckt und keine unangemessene Belastung für die Verbraucher darstellt. Vorgesehen sind zudem jährliche Berichtspflichten der Länder an das Bundesministerium der Justiz sowie des Ministeriums an die Europäische Kommission über die Zahl der vorhandenen Beratungsstellen.
In Deutschland gibt es laut Bundesregierung rund 1.380 Schuldnerberatungsstellen. Verlässliche Daten zu deren geografischer Verteilung, Ausstattung oder Wartezeiten lägen jedoch nicht vor, „auf deren Grundlage sich die Notwendigkeit oder der Umfang eines Ausbaus der Beratungskapazitäten prognostizieren ließe“. Daher lasse sich der finanzielle Mehraufwand auf Seiten der Länder nicht im Vorhinein quantifizieren.
Änderungen im Rechtsausschuss
Der Rechtsausschuss hatte am 12. November auf Änderungsantrag der Koalitionsfraktionen CDU/CSU und SPD noch zwei Änderungen am Regierungsentwurf vorgenommen. Zum einen wird im Schuldnerberatungsdienstegesetz festgeschrieben, dass die Dienste für Verbraucher „kostenlos angeboten werden“. Ein „begrenztes“ Entgelt ist demnach nur in „besonders begründeten Ausnahmefällen“ zulässig. 
Ursprünglich hatte der Entwurf vorgesehen, dass die Beratung „grundsätzlich kostenlos“ anzubieten ist und die Möglichkeit für ein „begrenztes Entgelt“ eingeräumt. Dies war in den parlamentarischen Beratungen zu dem Gesetzentwurf sowohl von Abgeordneten als auch von Sachverständigen kritisiert worden.
Zum anderen wird durch die Änderungen nun ausführlicher im Normtext dargelegt, wer Schuldnerberatungsdienste im Sinne des Gesetzes erbringen darf. Dazu wird definiert, was unter einem unabhängigen professionellen Anbieter zu verstehen ist. Auch diese Forderung war im parlamentarischen Verfahren erhoben worden.
Entschließung verabschiedet
Die Bundesregierung wird in der verabschiedeten Entschließung aufgefordert, gemeinsam mit den Ländern einen Vorschlag zu entwickeln, der dazu führt, eine auskömmliche Finanzierung und damit die Zukunftsfähigkeit der Schuldnerberatung in Deutschland – auch im Hinblick auf die Kostenfreiheit – zu sichern. Die Entwicklung dieses Vorschlags soll eine Prüfung der verpflichtenden Beteiligung privater Gläubiger an der Finanzierung der Schuldnerberatung einschließen.
Die Prüfung soll auch umfassen, wie es durch Verfahrensverschlankungen, Änderungen im Verbraucherinsolvenzrecht und die Digitalisierung von Schuldnerberatungsprozessen und Verbraucherinsolvenzverfahren zu besseren und schnelleren Ergebnissen und gleichzeitig zu Kosteneinsparungen kommen kann. Dies soll ermöglichen, dass die Länder dadurch frei werdende Mittel der Schuldnerberatung zur Verfügung stellen können. Der Rechtsausschuss des Bundestages erwartet zu den Forderungen der Entschließung einen Bericht bis zum 31. Januar 2027.
Änderungs- und Entschließungsantrag
Die Linke hatte in ihrem Änderungsantrag (
21/2788
(Dokument, öffnet ein neues Fenster)
```

- По пересказу выдачи (bundestag kw46/2025): службы должны быть «grundsätzlich kostenfrei» для потребителя, обязанность обеспечить их — на землях. Режима лицензирования коммерческих советующих сервисов в этом законе по пересказу нет; текст закона не добыт (PDF Бундесрата 1060/erl/21.pdf — curl вернул 000/0 байт).

## ДОБОР Г16 — Р (часть 2). Публичные свидетельства по Stripe и гражданам РФ

- Privatily helpdesk (сервис регистрации компаний; вторичный источник, не Stripe) https://helpdesk.privatily.com/?article=which-nationalities-are-fully-blacklisted-by-stripe — r.jina.ai HTTP 200, 5 152 байт; дословно:

```text

```

- vc.ru, 16.05.2024 (коммерческий блог посредника, маркетинговый тон) https://vc.ru/money/1177254-platezhnye-sistemy-paypal-i-stripe-nedostupny-grazhdanam-rossii-pochemu-eto-mif — r.jina.ai HTTP 200, 19 375 байт; дословно: «известные платежные системы Stripe и PayPal или не позволяли создать аккаунт в принципе, поскольку в списке выпадающих стран не было России, или уже после успешной регистрации учетной записи из РФ первые транзакции могли привести к мгновенной блокировке». Рецепт статьи — зарубежное юрлицо; конкретных кейсов с датами нет.
- Поиск по «Stripe ОАЭ гражданин РФ … отказ» и «Stripe Кипр … россиянин блокировка» (12.09.2026): задокументированных кейсов отказа/успеха в 2025–2026 с проверяемыми деталями не найдено; выдача — посредники (pikabu, awx.pro, relocation2armenia), утверждающие, что при зарубежной компании «можно», и что «российский паспорт может потребовать дополнительных документов» при KYC. Пересказ, не свидетельство.
- Контекст по Кипру (пересказ выдачи, mind.ua; residentpravo.com): массовые закрытия счетов россиян в кипрских банках; с конца октября 2025 EMI (Revolut) замораживали счета граждан РФ со ссылкой на 19-й пакет санкций ЕС; 13.03.2026 Еврокомиссия опубликовала разъяснение, что гражданство РФ само по себе не основание для закрытия счёта. Первоисточник разъяснения ЕК не открывался.
- Exa (`web_search_exa`, `web_fetch_exa`) в наборе инструментов этого агента отсутствует: вызов вернул «No such tool available». Канал не использован.

- Итог по SchuBerDG на 12.09.2026 (пересказ выдачи: hib-Kurzmeldung Бундестага https://www.bundestag.de/presse/hib/kurzmeldungen-1178472 ; gegen-hartz.de): Бундесрат отказал в согласии 08.05.2026, правительство созвало Vermittlungsausschuss 13.05.2026; сведений о договорённости в выдаче нет; действуют прежние земельные службы. Первоисточник о результате (vermittlungsausschuss.de) не открывался.


## ИТОГ ДОБОРА Г16 (regulation_world_advice_boundary) — 12.09.2026

| Пункт | Статус | Что именно |
|---|---|---|
| Н. CCD II — Германия | добыт | итоговый акт BGBl. 2026 I Nr. 139 от 18.05.2026 (официальный PDF), Art. 16 — вступление в силу 20.11.2026; новый § 511 BGB. Отдельный SchuBerDG (службы долгового консультирования) не вступил: Бундесрат отказал в согласии 08.05.2026, правительство 13.05.2026 созвало Vermittlungsausschuss, об исходе известно только по пересказу |
| Н. CCD II — Ирландия | НЕ добыт | транспонирующий акт не найден тремя поисками; юрфирмы по пересказу пишут, что он не опубликован; irishstatutebook сплошь не просматривался |
| О. UK RAO art. 72 | добыт | art. 72 целиком (latest revised, с поправкой S.I. 2026/74) + art. 39E |
| П. KZ / AM / RS / UAE / GE | добыт в основном (подагент, 1 запуск) | см. «П — итог по странам» выше; ОАЭ onshore CBUAE — не исследован, кончился бюджет вызовов |
| Р. Stripe | добыт частично | restricted-businesses дословно, SSA (контрагент для ОАЭ и Кипра); страница требований Stripe UAE — пустая (174–209 байт), sanctions FAQ — 404; проверяемых кейсов отказа или открытия в 2025–2026 не найдено. Exa в инструментах агента отсутствует |

Буквальное содержание:
- RAO art. 72(5): «There is excluded from articles 53 and 55A the giving of advice or the provision of targeted support by an overseas person … as a result of a legitimate approach». Строки «39E» в art. 72 нет вовсе (проверено по снятому тексту).
- Stripe, список запрещённых (блок перед заголовком «Restricted Businesses»): «Debt relief companies — Debt settlement, debt negotiation, and debt consolidation»; «Lending and credit — … Credit monitoring, credit repair, and counseling services». В разметке прокси заголовка «Prohibited businesses» над блоком не видно, принадлежность разделу определена по оглавлению страницы — сверить глазами.
- Stripe, «High-risk jurisdictions»: запрещены лица, «located in, resident in, or a citizen of» Кубы, Ирана, КНДР, Сирии, Крыма, Донецкой и Луганской областей. Россия в этом перечне по гражданству НЕ названа. «Prohibited services» по России перечисляют бухгалтерию, trust/corporate formation, консалтинг, IT-консалтинг и IT-поддержку, облачные сервисы для корпоративного ПО; в ЕС и UK — ещё рекламу, маркетинговые исследования, юридические услуги «to any person located in Russia».
- SSA: контрагент для ОАЭ и для Кипра (ЕЭЗ) — «Stripe Payments Europe, Limited».

Противоречие между источниками (не сглаживаю): Privatily (посредник) пишет «Stripe fully restricts accounts from … Russia», а собственная страница Stripe среди запрещённых по гражданству Россию не называет. Первичным считаю текст Stripe. Что Stripe делает на практике при KYC бенефициара с паспортом РФ — неизвестно.

🔴 Что меняет выводы `legal_final.md`:
1. 🔴 **§2.1 (UK) усиливается: у иностранного поставщика нет выхода через overseas persons exclusion.** Art. 72(5) снимает с overseas person только articles 53 и 55A (инвестиционный совет, targeted support), а debt-counselling (39E) в art. 72 не упоминается. То есть британский режим debt counselling через art. 72 с иностранного поставщика не снимается. Оговорка: территориальный вопрос — «carrying on in the UK», s. 418 FSMA — не исследовался.
2. 🔴 **Stripe может отказать нам по ПРЕДМЕТУ, а не из-за основателя.** В списке запрещённых стоят «credit … counseling services» и «debt relief companies». Советующий по долгам сервис рискует попасть в категорию «credit counseling» при любой юрисдикции компании — в ОАЭ, на Кипре, в США. В L9 это надо поставить рядом с UK: платёжный провайдер — отдельный барьер для выхода за рубеж. Что Stripe сделает с FINPILOT на практике, не проверялось.
3. 🔴 **Для L9 появилась карта «мягких» юрисдикций.** В МФЦА, DIFC и ADGM регулируется совет о ВСТУПЛЕНИИ в конкретный кредит, а совет о порядке погашения существующих долгов под буквальные определения не подпадает (AIFC GEN Sch. 1 п. 19; DFSA GEN 2.28.1(1)(b); ADGM FSMR Sch. 1 п. 28). В прочитанных актах республиканского Казахстана, Армении, Сербии и Грузии нормы о лицензии на (а) и (б) не найдено. Это полярно UK (PERG 17 покрывает и не просроченный долг). Оговорка подагента: «нормы не найдено» ≠ «нормы нет», а ОАЭ onshore (CBUAE) не исследован.
4. §2.2 (ЕС): для DE транспозиция CCD II теперь реквизирована (BGBl. 2026 I Nr. 139, с 20.11.2026). Новый § 511 BGB («Beratungsleistungen») адресован кредиторам и посредникам, к нам как к несоветующему-по-продукту сервису его адресность не проверялась.
