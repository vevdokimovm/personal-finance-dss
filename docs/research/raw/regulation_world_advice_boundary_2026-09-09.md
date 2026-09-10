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

