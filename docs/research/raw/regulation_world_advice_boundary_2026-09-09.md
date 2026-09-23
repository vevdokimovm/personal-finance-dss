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
Gesetzbuche genannten Musters und entsprechend Artikel 246b § 1 Absatz 1 Nummer 16 des Einführungs
gesetzes zum Bürgerlichen Gesetzbuche unterrichtet hat.“
16. In § 496 Absatz 2 Satz 1 wird nach der Angabe „unverzüglich“ die Angabe „vom bisherigen Darlehensgeber“
eingefügt.
17. Nach § 497 wird der folgende § 497a eingefügt:
„§ 497a
Zahlungsrückstände und Nachsichtsmaßnahmen bei Allgemein-Verbraucherdarlehen
(1) Der Darlehensgeber ist verpflichtet, den Darlehensnehmer eines Allgemein-Verbraucherdarlehens
vertrags, der Schwierigkeiten bei der Erfüllung seiner finanziellen Verpflichtungen hat, an Schuldnerberatungs
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
(4) Der Darlehensgeber ist verpflichtet, den Darlehensnehmer zu warnen, wenn ein Verbraucher
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
aa) In Satz 1 Nummer 1 wird die Angabe „entgeltliche Finanzierungshilfe“ durch die Angabe „Finanzierungs
hilfe nach § 506“ ersetzt.
bb) Satz 2 wird durch den folgenden Satz ersetzt:
„Bei Finanzierungshilfen nach § 506, die den Ausnahmen des § 491 Absatz 2 Satz 2 Nummer 1 bis 3 und
Absatz 3 Satz 2 entsprechen, gelten die Vorschriften dieses Untertitels nicht.“
b) Absatz 2 wird durch den folgenden Absatz 2 ersetzt:
„(2) Der Darlehensvermittler ist verpflichtet, den Verbraucher nach Maßgabe des Artikels 247 § 13
Absatz 2 und § 13b Absatz 1 und des Artikels 247a § 2 des Einführungsgesetzes zum Bürgerlichen
Gesetzbuche zu informieren. Der Darlehensvermittler ist gegenüber dem Verbraucher zusätzlich wie ein
Darlehensgeber gemäß § 491a verpflichtet. Satz 2 gilt hinsichtlich § 491a Absatz 1 und 2 nicht für
Warenlieferanten oder Dienstleistungserbringer, die in lediglich untergeordneter Funktion als Darlehens
vermittler von Allgemein-Verbraucherdarlehen oder von entsprechenden Finanzierungshilfen tätig werden,
etwa indem sie als Nebenleistung den Abschluss eines verbundenen Verbraucherdarlehensvertrags
vermitteln.“
c) Absatz 3 Satz 1 und 2 wird durch die folgenden Sätze ersetzt:
„Bietet der Darlehensvermittler im Zusammenhang mit der Vermittlung eines Verbraucherdarlehensvertrags
oder einer entsprechenden Finanzierungshilfe nach § 506 Beratungsleistungen gemäß § 511 Absatz 1 an, so
gilt § 511 entsprechend. § 511 Absatz 2 Satz 2 gilt bei der Vermittlung eines Immobiliar-Verbraucher
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

---

## ДОБОР Г21 (16.09.2026)

Батч закрывает правовые лакуны, оставшиеся после Г2 и Г16. Состав и обоснование —
`docs/research/queue/COVERAGE_AUDIT_3.md`, раздел «→ Г21».

**Проверка класса 4 (сервисы, лежавшие 16.09.2026), один запрос в начале работы:**
Wayback/Internet Archive **ПОДНЯЛСЯ**. Замер 16.09.2026:
`https://web.archive.org/web/2024id_/https://www.sec.gov/rules/final.htm` →
редирект на `https://web.archive.org/web/20250117225351id_/https://www.sec.gov/rules-regulations/rulemaking-activity`,
**HTTP 200, 261 986 байт**. Канал доступен и использовался в этом батче как резервный.

### Классификация запроса и процесс

**Тип: breadth-first** — семь независимых правовых под-вопросов по четырём юрисдикциям,
пересечений между ними почти нет. Не depth-first: это не «один вопрос многими ракурсами»,
а список раздельных норм, каждая проверяется своим первоисточником.

**Основной метод — прямое снятие первоисточника вахтой**, а не делегирование.
Отвергнутые способы: (1) веер подагентов по юрисдикциям — запрещён правилом 11 CLAUDE.md
и уже стоил трёх лимитов; (2) опора на обзоры юрфирм как на основной источник —
они пересказывают, а батч требует дословных цитат с номерами статей.
Подагенты (не более двух, последовательно) — только на пункты, где нужен широкий
перебор источников, а не одна известная норма.

---

### Пункт 2. Directive 2014/17/EU (MCD), Art. 4(21) и Art. 22 — ДОБЫТО ДОСЛОВНО

**Источник.** EUR-Lex, CELEX 32014L0017, консолидированный английский текст.
Прямой `curl -sk --http1.1` с браузерным UA по
`https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32014L0017` →
**HTTP 202, 0 байт** (предсказанное батчем поведение EUR-Lex).
Обход текстовым прокси:
`https://r.jina.ai/https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32014L0017`
→ **HTTP 200, 271 929 байт**, снято 16.09.2026.

**Art. 4(21), дословно:**

> (21) 'Advisory services' means the provision of personal recommendations to a consumer
> in respect of one or more transactions relating to credit agreements and constitutes
> a separate activity from the granting of a credit and from the credit intermediation
> activities set out in point 5.

**Art. 22(6), дословно (полный текст пункта):**

> 6. Member States shall ensure that advisory services are only provided by creditors,
> credit intermediaries or appointed representatives.
>
> Member States may decide not to apply the first subparagraph to persons:
>
> (a) carrying out the credit intermediation activities set out in point 5 of Article 4
> or providing advisory services where those activities are carried out or services are
> provided in an incidental manner in the course of a professional activity and that
> activity is regulated by legal or regulatory provisions or a code of ethics governing
> the profession which do not exclude carrying out of those activities or the provision
> of those services;
>
> (b) providing advisory services **in the context of managing existing debt** which are
> insolvency practitioners where that activity is regulated by legal or regulatory
> provisions or public or voluntary debt advisory services which **do not operate on a
> commercial basis**; or
>
> (c) providing advisory services who are not creditors, credit intermediaries or
> appointed representatives where such persons are **admitted and supervised by competent
> authorities** in accordance with the requirements for credit intermediaries under this
> Directive.
>
> Persons benefiting from the waiver in the second subparagraph shall not benefit from
> the right referred to in Article 32(1) to provide services for the entire territory
> of the Union.

**Art. 22(1) и (3)(a), дословно (обязанности при оказании advisory services):**

> 1. Member States shall ensure that the creditor, credit intermediary or appointed
> representative explicitly informs the consumer, in the context of a given transaction,
> whether advisory services are being or can be provided to the consumer.

Формулировка-разграничитель из Приложения II MCD (ESIS, Part A), дословно — она же
и есть образец «мы не советуем, вы решаете сами»:

> We are not recommending a particular mortgage for you. However, based on your answers
> to some questions, we are giving you information about this mortgage so that you can
> make your own choice.

**Выжимка по пункту 2.** Гипотеза батча подтвердилась: конструкция MCD **аналогична
CCD II**, причём почти дословно. Определение Art. 4(21) MCD и Art. 3(17) CCD II
различаются только порядком слов. Монополия на advisory services (Art. 22(6) MCD =
Art. 16(6) CCD II) и набор изъятий — те же, включая изъятие «managing existing debt»
для insolvency practitioners и некоммерческих служб.
🔴 **Следствие для нас:** ипотечный контур не мягче потребительского. Если мы
советуем по порядку погашения, и в наборе обязательств пользователя есть ипотека,
то под MCD применима та же логика, что под CCD II, и то же изъятие нам недоступно
по признаку коммерческой основы.
Формулировка ESIS — прямое текстовое подтверждение уже принятого нами разграничителя
(«assisting the person to make their own choice»): европейский законодатель сам
использует «so that you can make your own choice» как маркер НЕ-совета.

---

### Пункт 3. CCD II Art. 3(17): покрывает ли «advisory services» совет о ДОСРОЧНОМ ПОГАШЕНИИ — ОТВЕТ ПОЛУЧЕН ИЗ САМОЙ НОРМЫ

**Источник.** EUR-Lex, CELEX 32023L2225 (Directive (EU) 2023/2225, CCD II).
`https://r.jina.ai/https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32023L2225`
→ **HTTP 200, 207 127 байт**, снято 16.09.2026.

**Art. 3(17), дословно:**

> (17) 'advisory services' means personal recommendations to a consumer in respect of
> one or more transactions relating to credit agreements and that constitute a separate
> activity from the granting of a credit and from the credit intermediation activities
> as set out in point (12);

**Art. 3(22), дословно (отдельное понятие — не путать с (17)):**

> (22) 'debt advisory services' means personalised assistance of a technical, legal or
> psychological nature provided by independent professional operators which are not,
> in particular, creditors or credit intermediaries as defined in this Directive, or
> credit purchasers or credit servicers as defined in Article 3, points (6) and (8),
> of Directive (EU) 2021/2167 ... in favour of consumers who experience or might
> experience difficulties in meeting their financial commitments.

**Art. 16(6), дословно (полный текст):**

> 6. Member States shall ensure that advisory services may only be provided by creditors
> and, where applicable, credit intermediaries.
>
> Member States may, by way of derogation from the first subparagraph, allow other persons
> than those referred to in the first subparagraph to provide advisory services where one
> of the following conditions is fulfilled:
>
> (a) the advisory services are provided in an incidental manner in the course of a
> professional activity that is regulated by legal or regulatory provisions or a code of
> ethics which do not exclude the provision of those services;
>
> (b) the advisory services are provided **in the context of management of existing debt**
> by insolvency practitioners and where that management activity is regulated by legal
> or regulatory provisions;
>
> (c) the advisory services are provided **in the context of management of existing debt**
> by public or voluntary providers of debt advisory services as referred to in Article 36
> which **do not operate on a commercial basis**;
>
> (d) the advisory services are provided by persons that are **authorised and supervised
> by competent authorities**.

🔴 **Это и есть ответ на пункт 3, и он выводится из структуры самой директивы,
а не из чьего-либо толкования.** Аргумент:

1. Art. 16(6) устанавливает **монополию**: advisory services вправе оказывать только
   кредиторы и кредитные посредники.
2. Изъятия (b) и (c) написаны специально для случая «advisory services **in the context
   of management of existing debt**».
3. Изъятие из запрета требуется только для того, что запретом **охвачено**. Если бы
   совет об управлении существующим долгом не подпадал под Art. 3(17), подпункты (b)
   и (c) были бы лишены предмета.
4. Следовательно, **законодатель ЕС сам исходит из того, что совет об управлении
   существующим долгом ОХВАТЫВАЕТСЯ определением «advisory services» Art. 3(17)**.

Досрочное погашение — прямо поименованная в директиве транзакция по кредитному договору
(Art. 29 CCD II, right of early repayment), то есть «transaction relating to a credit
agreement» в смысле Art. 3(17). Совет о том, какой из существующих кредитов гасить
досрочно первым, — персональная рекомендация в отношении такой транзакции.

🔴 **Ни одно из четырёх изъятий нам не подходит:**
- (a) — мы не оказываем совет «incidental» в рамках иной регулируемой профессии;
- (b) — мы не insolvency practitioners;
- (c) — 🔴 отсекает нас **прямо по признаку**: «do not operate on a commercial basis».
  Мы коммерческий сервис. Это главный отсекающий признак по ЕС;
- (d) — доступно, но это и есть «получить авторизацию», то есть попасть под регулирование.

**Соотношение с Art. 3(22) «debt advisory services».** Понятия (17) и (22) различны:
(22) — специальный институт социальной помощи людям в затруднении (Art. 36 требует от
государств обеспечить его доступность с ограниченной платой), и он тоже требует
независимости и фактически некоммерческой основы. Ни одно из двух понятий не даёт нам
безопасной гавани: (17) — монополизировано Art. 16(6), (22) — адресовано independent
professional operators для потребителей в затруднении.

**Что по этому пункту НЕ добыто.** Толкований Еврокомиссии (Q&A/guidance) именно по
Art. 3(17) и именно про досрочное погашение в этом заходе не найдено; позиции BaFin,
AMF, Banca d'Italia, Central Bank of Ireland по этому вопросу не снимались — см.
раздел о недобытом ниже. Однако **вывод от них не зависит**: он получен из текста
Art. 16(6) директивы напрямую и толкованием лишь подтверждался бы.

---

### Пункт 4. UK: art. 72A RAO — ГИПОТЕЗА СНЯТА НОРМОЙ. Статьи БОЛЬШЕ НЕ СУЩЕСТВУЕТ

**Источник.** `https://www.legislation.gov.uk/uksi/2001/544/article/72A`,
`curl -sk --http1.1` с браузерным UA → **HTTP 200, 41 878 байт**, снято 16.09.2026.

**Дословно, текущая редакция (latest revised):**

> Information society services U.K.
> F1 72A. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
>
> **Textual Amendments**
> F1 Art. 72A **omitted (31.12.2020)** by virtue of The Electronic Commerce and Solvency 2
> (Amendment etc.) (EU Exit) Regulations 2019 (**S.I. 2019/1361**), regs. 1(2), **5(2)**
> (with regs. 11-28) (as amended by S.I. 2019/1390, regs. 1(2), 6); 2020 c. 1, Sch. 5 para. 1(1)

Та же страница фиксирует ещё не применённые изменения ко всему инструменту:
«Order revoked by 2023 c. 29 Sch. 1 Pt. 5» (Financial Services and Markets Act 2023) —
отзыв RAO как ретейненного права ещё не введён в действие, то есть **RAO продолжает
действовать**, и опираться на его будущий отзыв нельзя.

🔴 **Прежний вывод Г2 был помечен как гипотеза («art. 72A неприменим к третьим странам
после Brexit») — теперь он ЗАМЕНЁН нормой, и основание оказалось другим и более
сильным.** Дело не в том, что статья не распространяется на третьи страны:
**статья изъята из RAO целиком с 31.12.2020**. Исключение для information society
services в британском праве **отсутствует как таковое** — ни для кого, включая
поставщиков из третьих стран. Ссылаться на art. 72A RAO в юрблоке нельзя вовсе.
Причина изъятия системная: art. 72A имплементировал «country of origin» принцип
Директивы об электронной коммерции 2000/31/EC, а взаимность внутреннего рынка
после выхода из ЕС прекратилась.

**PERG 2.9.18G.** `https://r.jina.ai/https://www.handbook.fca.org.uk/handbook/PERG/2/9.html`
→ **HTTP 200, 27 552 байта**, снято 16.09.2026. Раздел PERG 2.9 «Regulated activities:
exclusions applying to more than one regulated activity» в снятой версии Handbook
нормы 2.9.18G про information society services в прежнем виде не содержит —
что согласуется с изъятием art. 72A: руководство следует за отменённой нормой.
Точная нумерация в действующем Handbook по этому подразделу отдельно не сверялась,
потому что вопрос закрыт на уровне самой нормы RAO.

**Art. 72 RAO (overseas persons) применительно к debt counselling.**
`https://www.legislation.gov.uk/uksi/2001/544/article/72` → **HTTP 200, 137 910 байт**,
снято 16.09.2026. Подтверждён уже зафиксированный в этом файле результат Г16:
art. 72(5) снимает с overseas person только articles 53 и 55A; **упоминания art. 39E
(debt counselling) в art. 72 нет**. Для иностранного поставщика выхода через
overseas persons exclusion по долговому контуру НЕТ.

🔴 **Сводно по UK: обе двери, на которые была надежда, закрыты нормой.**
Art. 72A — изъят целиком с 31.12.2020; art. 72 — не покрывает 39E. Британский
долговой контур с нас не снимается ни территориально, ни по каналу оказания услуги.
Оговорка прежнего захода сохраняется: территориальный вопрос «carrying on in the UK»
(s. 418 FSMA) отдельно не исследовался — это единственная оставшаяся линия защиты
по UK, и она не про исключения, а про то, ведётся ли деятельность в UK вообще.

---

### Пункт 7. Добивка до дословных цитат — ДОБЫТО (3 из 4)

#### 7.1. SEC Release No. 33-11377 — дословно, ДОБЫТО

`curl` по `https://www.sec.gov/files/rules/final/2025/33-11377.pdf` — 403
(подтверждён замер батча: `sec.gov` отбивает и `curl`+UA, и `WebFetch`).
Обход: `https://r.jina.ai/https://www.sec.gov/files/rules/final/2025/33-11377.pdf`
→ **HTTP 200, 14 017 байт**, 7 страниц, Published Time: Tue, 17 Jun 2025 12:15:48 GMT.
Снято 16.09.2026.

Полные реквизиты (дословно с титула):

> SECURITIES AND EXCHANGE COMMISSION
> 17 CFR Parts 200, 230, 232, 239, 240, 242, 249, 270, 274, 275, and 279
> [Release Nos. **33-11377**; 34-103247; **IA-6885**; IC-35635; File Nos. S7-20-22; S7-12-23;
> S7-04-23; S7-04-22; S7-17-22; S7-25-22; S7-32-10; S7-18-23; S7-32-22; S7-31-22; S7-07-23;
> S7-06-23; S7-02-22; S7-10-20]
>
> **Withdrawal of Proposed Regulatory Actions**
> ACTION: Notice of withdrawal of proposed rules.
>
> SUMMARY: The Securities and Exchange Commission ("Commission") is formally withdrawing
> certain notices of proposed rulemaking issued between March 2022 and November 2023.
> **The Commission does not intend to issue final rules with respect to these proposals.**
> If the Commission decides to pursue future regulatory action in any of these areas,
> it will issue a new proposed rule.

Про сам PDA-проект, дословно (раздел Background):

> **Conflicts of Interest Associated with the Use of Predictive Data Analytics by
> Broker-Dealers and Investment Advisers**
> On August 9, 2023, the Commission published proposed new rules under the Securities
> Exchange Act of 1934 ("Exchange Act") and the Investment Advisers Act of 1940
> ("Advisers Act") to, among other things, address certain interactions between
> broker-dealers or investment advisers and investors through these firms' use of
> predictive data analytics.

Дата отзыва — **17.06.2025** (DATES: «...as of June 17, 2025»), исходная публикация
проекта PDA — 88 FR 53960 (August 9, 2023). Подтверждающая публикация в Federal Register:
`https://r.jina.ai/https://www.federalregister.gov/documents/2025/06/23/2025-11333/...`
→ **HTTP 200, 17 242 байта**.

**Что это значит для нас.** Проект PDA был единственной инициативой SEC, которая
прямо целилась в алгоритмические/предиктивные рекомендательные механики и могла бы
задеть сервис нашего класса по признаку «технология», а не «предмет». Он **отозван
окончательно**, с прямой формулировкой «does not intend to issue final rules».
Регуляторного крючка «вы алгоритм — значит под Advisers Act» в США сейчас нет.
Оговорка: отзыв проекта не создаёт безопасной гавани, он лишь убирает
несостоявшееся расширение; действующее определение Advisers Act не менялось.

#### 7.2. Lowe v. SEC, 472 U.S. 181 (1985) — «person-to-person», ДОБЫТО ДОСЛОВНО

`justia` → **HTTP 200, но 288 байт** (пустое тело, антибот).
Обход: `https://r.jina.ai/https://www.law.cornell.edu/supremecourt/text/472/181`
→ **HTTP 200, 145 529 байт** (Cornell LII, полный текст с особыми мнениями).
Снято 16.09.2026.

Ключевой абзац большинства (Stevens, J.), дословно:

> The Act was designed to apply to those persons engaged in the investment-advisory
> profession — **those who provide personalized advice attuned to a client's concerns**,
> whether by written or verbal communication. The mere fact that a publication contains
> advice and comment about specific securities does not give it the personalized character
> that identifies a professional investment adviser. Thus, petitioners' publications do not
> fit within the central purpose of the Act because **they do not offer individualized
> advice attuned to any specific portfolio or to any client's particular needs**.

И собственно формула «person-to-person», дословно:

> As long as the communications between petitioners and their subscribers remain
> **entirely impersonal and do not develop into the kind of fiduciary, person-to-person
> relationships** that were discussed at length in the legislative history of the Act and
> that are characteristic of investment adviser-client relationships, we believe the
> publications are, at least presumptively, within the exclusion and thus not subject
> to registration under the Act.

Из истории дела (важно, что это позиция НИЖЕСТОЯЩЕГО суда, а не ratio ВС), дословно:

> The majority first held that petitioners were engaged in business as "investment
> advisers" within the meaning of the Act. It concluded that **the Act does not distinguish
> between person-to-person advice and impersonal advice given in printed publications.**

🔴 **Осторожно с использованием Lowe в нашу пользу — и это правка к прежнему заходу.**
Lowe строит защиту на **безличности и публичности** коммуникации («entirely impersonal»,
«circulate for sale to the public at large in a free, open market»). Наш продукт —
ровно противоположное: персональная рекомендация, рассчитанная по данным конкретного
пользователя, «attuned to a client's particular needs». По критерию Lowe мы на
**«плохой» стороне линии**: мы персонализированы. Lowe защищает нас **только потому,
что мы не говорим о ценных бумагах вообще** — то есть работает предметный
разграничитель, уже зафиксированный в этом файле, а не критерий персональности.
Формулировка «person-to-person» **не является** для нас щитом и не должна цитироваться
в юрблоке как таковой.

#### 7.3. Третий штат с нормой о debt adjusting: ГРУЗИЯ (Georgia) — ДОБЫТО ДОСЛОВНО

Источники (снято 16.09.2026, все через `r.jina.ai`, прямой `justia` отдаёт пустое тело):
- перечень главы: `https://r.jina.ai/https://law.justia.com/codes/georgia/title-18/chapter-5/`
  → **HTTP 200, 13 845 байт**;
- `https://r.jina.ai/https://law.justia.com/codes/georgia/title-18/chapter-5/section-18-5-1/`
  → **HTTP 200, 14 926 байт**;
- `https://r.jina.ai/https://law.justia.com/codes/georgia/title-18/chapter-5/section-18-5-3/`
  → **HTTP 200, 14 463 байта**.

**O.C.G.A. § 18-5-1 (2025), дословно и целиком:**

> As used in this chapter, the term:
> (1) **"Debt adjusting"** means doing business in debt adjustments, **budget counseling**,
> debt management, or debt pooling service or holding oneself out, by words of similar
> import, as providing services to debtors in the management of their debts **and
> contracting with a debtor for a fee to**:
> (A) Effect the adjustment, compromise, or discharge of any account, note, or other
> indebtedness of the debtor; or
> (B) Receive from the debtor and disburse to his or her creditors any money or other
> thing of value.
> (2) "Person" means an individual, corporation, partnership, trust, association, or other
> legal entity.
> (3) "Resides" means to live in a particular place, whether on a temporary or permanent basis.

История нормы: Ga. L. 1956, p. 797, § 1; Ga. L. 2003, p. 392, § 1; Ga. L. 2015, p. 1088,
§ 18/SB 148. Наказание за ведение бизнеса debt adjusting с нарушением главы — § 18-5-4.

**O.C.G.A. § 18-5-3 (изъятия), дословно:**

> Nothing in this chapter shall apply to those situations involving debt adjusting incurred
> in the practice of law in this state. Nothing in this chapter shall apply to those persons
> or entities who incidentally engage in debt adjustment to adjust the indebtedness owed to
> said person or entity. Nothing in this chapter shall apply to the following entities or
> their subsidiaries: the Federal National Mortgage Association; the Federal Home Loan
> Mortgage Corporation; a bank, bank holding company, trust company, savings and loan
> association, credit union, credit card bank, or savings bank that is regulated and
> supervised by the Office of the Comptroller of the Currency, the Federal Reserve, the
> Federal Deposit Insurance Corporation, the National Credit Union Administration, or the
> Georgia Department of Banking and Finance; or persons as defined in Code Section 7-3-3
> operating under Chapter 3 of Title 7, the "Georgia Installment Loan Act."

🔴 **Разбор — и это главный содержательный результат по штатам.**
Определение Джорджии **называет «budget counseling» прямо** — это самый тревожный для нас
текст из трёх штатов (Utah UDMSA, RCW 18.28.010 Washington, теперь Georgia).
Но **структура определения конъюнктивная**: требуется И (а) вести бизнес в
debt adjustments / budget counseling / debt management / debt pooling либо выдавать себя
за такового, И (б) «contracting with a debtor **for a fee** to» совершить одно из двух
действий — (A) добиться adjustment, compromise или discharge задолженности, либо
(B) принимать деньги от должника и распределять их кредиторам.

Мы **не делаем ни (A), ни (B)**: мы не ведём переговоров с кредиторами, ничего не
«compromise» и не «discharge», и через нас не проходят деньги пользователя.
Поэтому по букве § 18-5-1 Джорджия нас **не ловит**, несмотря на слово
«budget counseling» в первой половине определения.

🔴 **Отличие от UK — и оно принципиально.** Джорджия строит состав вокруг
**действия с долгом и денежного потока**; UK (art. 39E RAO + PERG 17) строит его
вокруг **самого совета**. Поэтому американская модель штатов для нас мягче
британской: там, где PERG 17 ловит за рекомендацию приоритета погашения,
Джорджия требует ещё и договор на совершение действия с задолженностью.
Оговорка: конъюнктивное прочтение «and contracting with a debtor for a fee» —
прочтение по букве; судебной практики именно по разграничению «совет без действия»
в этом заходе не снималось. Единственное найденное на странице судебное решение
(Moon v. CSA—Credit Solutions of Am., Inc., 304 Ga. App. 555 (2010)) о составе
не высказывается — оно о недействительности оговорки о подсудности.

#### 7.4. Delaware / Rhode Island / Colorado — НЕ ДОБЫТО в этом заходе

Пройдено: `https://r.jina.ai/https://delcode.delaware.gov/title6/c024a/index.html`
→ **HTTP 200, 85 587 байт**, но термина «debt adjusting» в главе нет;
`.../title6/c023a/index.html` → **HTTP 200, 342 байта** (пустая заглушка, главы нет).
Rhode Island и Colorado не запрашивались — задача пункта («третий штат с дословной
нормой») закрыта Джорджией, дальнейший перебор штатов не был строго необходим
для ответа на вопрос батча. Это осознанный отказ от шага по критерию
«строго ли необходим», а не недобор.

---

### Пункт 5. Ирландия: транспозиция CCD II — ДОБЫТ ДОКАЗАННЫЙ ОТРИЦАТЕЛЬНЫЙ РЕЗУЛЬТАТ

Прежний статус (Г16): «акт не найден тремя поисками, `irishstatutebook.ie` сплошь
не просматривался». Теперь перечень просмотрен сплошь.

**Найден рабочий адрес перечня** (прежние заходы били по неверным шаблонам URL,
отсюда и «не найден»). Замеры 16.09.2026, `curl -sk --http1.1` с браузерным UA:

| URL | HTTP | Байт |
|---|---|---|
| `https://www.irishstatutebook.ie/eli/2026/en/si/` | **404** | 196 |
| `https://www.irishstatutebook.ie/eli/isbc/si/2026.html` | **404** | 196 |
| `https://www.irishstatutebook.ie/eli/ISBCSI/2026.html` | **404** | 196 |
| `https://www.irishstatutebook.ie/eli/isbc/2026.html` | 200 | 24 839 (это перечень ЗАКОНОВ, не S.I.) |
| 🟢 `https://www.irishstatutebook.ie/eli/2026/si` | **200** | **279 434** — рабочий перечень S.I. за 2026 |
| `https://www.irishstatutebook.ie/eli/2026/si/1/made/en/print` | 200 | 64 706 (подтверждает шаблон адреса отдельного S.I.) |

**Сплошной проход перечня S.I. за 2026 год (279 434 байта) по словам «credit»
и «consumer» дал полный список совпадений:**

- Credit Review Act 2026 (Commencement) Order 2026
- Credit Review Act 2026 (Establishment Day) Order 2026
- Credit Review Act 2026 (Prescribed Amounts and Fee) Regulations 2026
- Credit Review Act 2026 (Credit Review Levy) Regulations 2026
- Film (Enhanced Credit Amount for Visual Effects) (Amendment) Regulations 2026
- Statistics (Consumer Price Survey) (Amendment) Order 2026
- Central Bank (Supervision and Enforcement) Act 2013 (Section 48) (Consumer Protection) (Amendment) Regulations 2026
- European Union (Empowering Consumers for the Green Transition) Regulations 2026
- Consumer Insurance Contracts Act 2019 (Commencement) Order 2026

🔴 **Ни один из них не транспонирует Directive (EU) 2023/2225.** Credit Review Act 2026 —
про апелляции МСП на отказ в кредите, а не про CCD II.

**Подтверждение вторым, независимым источником.** A&L Goodbody, «Consumer Credit
Directive 2 (CCD2) – What consumer lenders in Ireland need to know»,
`https://r.jina.ai/https://www.algoodbody.com/insights-publications/consumer-credit-directive-2-ccd2-what-consumer-lenders-in-ireland-need-to-know`
→ **HTTP 200, 20 752 байта**, дата публикации **7 мая 2026**. Дословно:

> To date, Ireland has not published transposing legislation despite the transposition
> deadline of 20 November 2025, but we expect the transposing legislation to closely
> mirror the wording of the CCD2 text and there to be **no gold-plating**.

Найденный смежный акт (не CCD II, но по соседнему досье): **S.I. No. 309/2026 —
European Union (Distance Contracts for Financial Services) Regulations 2026**
(`https://www.irishstatutebook.ie/eli/2026/si/309/made/en/print`), транспозиция DMD II.

**Вывод по пункту 5.** Ирландия **просрочила** транспозицию CCD II (дедлайн 20.11.2025)
и по состоянию на 16.09.2026 транспонирующего акта не опубликовала. Это уже не
«не нашли», а проверенный отрицательный результат: перечень S.I. за 2026 пройден целиком.
Практическое следствие: **по Ирландии ориентироваться следует на текст самой директивы** —
и ожидание рынка (ALG) состоит в том, что ирландский акт повторит формулировки CCD II
без ужесточения. То есть разбор Art. 3(17) и Art. 16(6) выше применим к Ирландии
напрямую, когда акт выйдет. Отдельная оговорка: сама директива применяется с 20.11.2026,
и отсутствие национального акта не отменяет прямого действия за государством
в части, где нормы безусловны.

---

### Пункт 6. ОАЭ onshore (CBUAE) — ДОБЫТО. Перечень лицензируемой деятельности ИСЧЕРПЫВАЮЩИЙ, совета в нём нет

Прежний статус (Г16): «весь режим не исследован, кончился бюджет вызовов».

**Источник.** CBUAE Rulebook, консолидированный текст
«Central Bank & Organization of Financial Institutions and Activities Law»
(Decretal Federal Law No. (14) of 2018 в редакции Decretal Federal Law No. (9) of 2021).
`https://r.jina.ai/https://rulebook.centralbank.ae/en/rulebook/central-bank-organization-financial-institutions-and-activities-law`
→ **HTTP 200, 259 329 байт**, снято 16.09.2026.

Пройденные и отвергнутые каналы (замеры того же дня):
- `https://r.jina.ai/https://www.centralbank.ae/media/mnbhnyhq/decretal-federal-law-no-14-of-2018-on-the-central-bank-en.pdf` → **HTTP 422, 379 байт**;
- `https://r.jina.ai/https://rulebook.centralbank.ae/en/rulebook/article-65-licensed-financial-activities` → **HTTP 404, 3 840 байт** (неверный slug);
- `https://r.jina.ai/https://rulebook.centralbank.ae/en/rulebook/article-65-financial-activities` → **HTTP 200, 17 938 байт**, но страница помечена **«Status: Repealed»** (первоначальная редакция DFL 14/2018). 🔴 Брать её как действующую норму нельзя — взята консолидированная.

**Article (65): Financial Activities — дословно, действующая консолидированная редакция:**

> 1) The following activities shall be considered financial activities subject to Central
> Bank licensing and supervision in accordance with the provisions of this Decretal Law:
>
> a. Taking deposits of all types, including Shari'ah-compliant deposits.
> b. Providing credit facilities of all types.
> c. Providing funding facilities of all types, including Shari'ah-compliant funding facilities.
> d. Providing currency exchange and money transfer services.
> e. Providing monetary intermediating services.
> f. Providing stored values services, electronic retail payments and digital money services.
> g. Providing virtual banking services.
> h. Arranging and/or marketing for Licensed Financial Activities.
> i. Acting as a principal in financial products that affect the financial position of the
> Licensed Financial Institution, including but not limited to foreign exchange, financial
> derivatives, bonds and sukuk, equities, commodities, and any other financial products
> approved by the Central Bank.
>
> 2) The Board of Directors shall:
> a. Classify and define Licensed Financial Activities and the practices relating thereto.
> b. **Add activities or practices to the list** of Licensed Financial Activities mentioned
> in item (1) of this article, or delete activities or practices from the list, or amend them,
> following coordination and agreement with the Regulatory Authorities in the State, through
> the Financial Activities Committee referred to in Article (66) of this Decretal Law.

Определение из Article (1), дословно:

> **Licensed Financial Activities:** The financial activities subject to Central Bank
> licensing and supervision, which are specified in Article (65) of this Decretal Law.

Санкция за безлицензионную деятельность — Article (?) о проверках, дословно:

> 3) The Central Bank may, in coordination with the concerned agencies in the State, inspect
> premises of any Person **suspected of carrying on any of the financial activities referred
> to in Article (65) of this Decretal Law, without a license**.

🔴 **Вывод по ОАЭ onshore.** Перечень Art. 65(1) — **закрытый и исчерпывающий**
(«The following activities shall be considered financial activities subject to Central Bank
licensing»), и расширяется только решением Совета директоров через Financial Activities
Committee (Art. 65(2)(b), Art. 66). В перечне **нет ни «financial advice», ни «financial
consultancy», ни «debt counselling», ни «credit counselling»** — ни в одной из девяти позиций.

Наш сервис не принимает депозитов (a), не предоставляет кредитных или финансирующих
средств (b, c), не занимается обменом и переводом (d), не выступает monetary intermediary
(e), не эмитирует stored value и не проводит платежи (f), не оказывает virtual banking (g),
не действует как принципал в финансовых продуктах (i).

Единственная позиция, требующая осторожности, — **(h) «Arranging and/or marketing for
Licensed Financial Activities»**. Она ловит не совет как таковой, а организацию и
маркетинг чужой лицензируемой деятельности. Пока мы не называем конкретных продуктов
и не направляем пользователя к конкретному кредитору или банку, под (h) мы не попадаем;
🔴 **но появление в продукте любой партнёрской выдачи («вот банк, где рефинансировать»)
переводит нас под (h) и, следовательно, под лицензирование CBUAE.** Это тот же предметный
разграничитель, что и в остальных юрисдикциях, только выраженный через «arranging/marketing».

**Сопоставление с уже добытыми зонами ОАЭ.** Картина сходится: DIFC (DFSA GEN 2.28.1,
2.11.1) и ADGM (FSMR Sch. 1 п. 28) регулируют совет о ВСТУПЛЕНИИ в конкретный продукт;
CBUAE onshore вообще не относит совет к лицензируемой деятельности. То есть
**в ОАЭ — во всех трёх контурах — совет о порядке погашения существующих долгов
под лицензирование не подпадает.** Это полярно UK.

**Оговорки, честно.** (1) «Нормы в перечне нет» — вывод по исчерпывающему перечню
первичного закона, и в этом он сильнее, чем обычное «не нашли»; но подзаконные
регламенты Совета директоров (Art. 65(2)(a) «classify and define... and the practices
relating thereto») отдельно не просматривались, а именно они детализируют практики.
(2) Инвестиционный совет onshore ОАЭ относится к компетенции **SCA** (Securities and
Commodities Authority), а не CBUAE; режим SCA в этом заходе не снимался, но он
по предмету привязан к ценным бумагам, то есть к тому, чего мы не касаемся.

---

### Пункт 1. 🔴 США: Investment Advisers Act и сервис, советующий по долгам и накоплениям — ДОБЫТО

Исполнено подагентом (один запуск, `base-kit:researcher`, бюджет 14 действий, израсходовано 13,
своих подагентов не запускал). Ниже — материал подагента, сверенный вахтой, и отдельно
несколько мест, где вахта с ним расходится или уточняет.

#### 1.1. Норма: 15 U.S.C. § 80b-2(a)(11), дословно

Источник: `https://r.jina.ai/https://www.govinfo.gov/content/pkg/USCODE-2023-title15/html/USCODE-2023-title15-chap2D-subchapII-sec80b-2.htm`
→ **HTTP 200, 32 809 байт**, снято 16.09.2026.

> **(11) "Investment adviser" means any person who, for compensation, engages in the business
> of advising others, either directly or through publications or writings, as to the value of
> securities or as to the advisability of investing in, purchasing, or selling securities,
> or who, for compensation and as part of a regular business, issues or promulgates analyses
> or reports concerning securities;** but does not include (A) a bank… (B) any lawyer,
> accountant, engineer, or teacher whose performance of such services is solely incidental
> to the practice of his profession; (C) any broker or dealer… (D) the publisher of any
> bona fide newspaper, news magazine or business or financial publication of general and
> regular circulation; (E) any person whose advice, analyses or reports relate to no
> securities other than securities which are direct obligations of… the United States…;
> (F) any nationally recognized statistical rating organization…; (G) any family office…;
> or (H) such other persons not within the intent of this paragraph, as the Commission may
> designate by rules and regulations or order.

🔴 **Ключевое наблюдение, и оно — самое сильное в нашу пользу по США:** слово «securities»
стоит в **каждой** из двух альтернативных ветвей определения. Совет, не касающийся ценных
бумаг, не попадает ни в первую ветвь, ни во вторую. Мы **не входим в само определение**,
а не выводимся из него изъятием (A)–(H). Юридически это сильнее: изъятие можно потерять,
непопадание в дефиницию — нет.

**Замечание по каналу (расхождение с замером батча).** Cornell LII по
`https://r.jina.ai/https://www.law.cornell.edu/uscode/text/15/80b-2` → HTTP 200, 30 287 байт,
**но статутный текст (a)(11) на странице не отрендерен** — только примечания и история
поправок. То есть «Cornell работает» верно по коду и неверно по содержанию для страниц USC.
Для текста дела (472 U.S. 181) Cornell при этом отработал полностью (145 529 байт, см. п. 7.2).
Вывод для будущих батчей: **USC брать с `govinfo.gov`, судебные решения — с Cornell.**

#### 1.2. SEC Release IA-1092 (8 октября 1987) — добыт целиком

Источник: `https://r.jina.ai/https://www.sec.gov/rules/interp/1987/ia-1092.pdf`
→ **HTTP 200, 36 156 байт, 20 страниц**, снято 16.09.2026.
Старый адрес `https://www.sec.gov/divisions/investment/noaction/ia-1092.htm` — **404**
(страница удалена SEC; это мёртвый адрес, а не недобытый источник).

🔴 **Статус документа — и это поправка к постановке задачи батча.** Шапка релиза, дословно:

> **ACTION: Statement of staff interpretive position.** SUMMARY: The Commission is publishing
> the views of **the staff of the Division of Investment Management** on the applicability of
> the Investment Advisers Act of 1940 to financial planners… The views expressed in this
> statement were developed jointly by Division staff and the **North American Securities
> Administrators Association, Inc. ("NASAA")** to update Investment Advisers Act Release No. 770…

То есть IA-1092 — **позиция штата (сотрудников Отдела), а не Комиссии, и не норма права**.
Он не связывает ни суд, ни саму SEC. Писать в юрблоке «SEC постановила» — ошибка.

**Трёхчастный тест, дословно:**

> A determination as to whether a person providing financial planning, pension consulting,
> or other integrated advisory services is an investment adviser will depend upon whether
> such person: **(1) provides advice, or issues reports or analyses, regarding securities;
> (2) is in the business of providing such services; and (3) provides such services for
> compensation.**

Элементы **конъюнктивны** — подтверждено вторым документом SEC (Plaze, см. 1.3):
«A person must satisfy **all three** elements to fall within the definition».

**Что НЕ является specific investment advice — дословно:**

> For the purposes of (iii) above, "specific investment advice" includes a recommendation,
> analysis or report about specific securities or specific categories of securities
> (e.g., industrial development bonds, mutual funds, or medical technology stocks).
> **It includes a recommendation that a client allocate certain percentages of his assets
> to life insurance, high yielding bonds, and mutual funds or particular types of mutual
> funds such as growth stock funds or money market funds. However, specific investment
> advice does not include advice limited to a general recommendation to allocate assets
> in securities, life insurance, and tangible assets.**

🔴 **Оговорка подагента, которую вахта принимает и подчёркивает:** этот абзац относится
к элементу **«business»**, а НЕ к элементу «advice regarding securities». Он отвечает
на вопрос «достаточно ли регулярно и конкретно ты советуешь, чтобы быть *в бизнесе*»,
а не «касается ли твой совет бумаг». Вторичные источники этим злоупотребляют. Для нас
элемент (1) отпадает по более простой причине — бумаг в выдаче нет вовсе.

**🔴 Самая опасная для нас фраза IA-1092, дословно:**

> A person who, in the course of developing a financial program for a client, advises a client
> as to **the desirability of investing in, purchasing or selling securities, as opposed to,
> or in relation to, any non-securities investment or financial vehicle** would also be
> "advising" others within the meaning of Section 202(a)(11).

🔴 **Перевод на наш продукт.** Ловушка не в том, чтобы назвать бумагу, а в том, чтобы
**сопоставить вложение в бумаги с не-бумагами**. Фраза «гасить долг под 22 % выгоднее,
чем инвестировать» — классический аргумент продукта нашего класса — **прямо накрыта**
этой формулировкой и сама по себе выполняет элемент (1), хотя ни один инструмент не назван.
Это новое ограничение, которого в файле до сих пор не было.

**Антиобход — § 208(d), дословно:**

> …if a financial planner structures his planning so as to give only generic, non-specific
> investment advice as a financial planner, **but then gives specific securities advice in his
> capacity as a registered representative of a dealer**… the person would not be able to assert
> that he was not "in the business" of giving investment advice. … **Section 208(d) of the
> Advisers Act makes it illegal for someone to do indirectly under the Advisers Act what
> cannot be done directly.**

То есть «чистый» расчётный модуль не спасает, если в той же экономической связке есть
брокерская витрина или партнёрские выплаты за открытие счёта.

#### 1.3. «Regulation of Investment Advisers», SEC Division of Investment Management (Robert E. Plaze, апрель 2012)

Источник: `https://r.jina.ai/https://www.sec.gov/about/offices/oia/oia_investman/rplaze-042012.pdf`
→ **HTTP 200, 191 161 байт**, снято 16.09.2026. Документ на домене sec.gov за авторством
заместителя директора Division of Investment Management; даёт то, чего нет в IA-1092, —
поимённые no-action letters.

**Главная цитата по нашему вопросу, дословно:**

> **a. Advice about Securities.** A person clearly meets the third element of the statutory
> test if he provides advice to others about specific securities… **The SEC staff has stated
> that advice about real estate, coins, precious metals, or commodities is not advice about
> securities.**⁷ The more difficult questions arise with less specific advice… The SEC staff
> has stated in this regard: (i) advice about market trends is advice about securities;⁸
> (ii) advice about the selection and retention of other advisers is advice about securities;⁹
> (iii) advice about the advantages of investing in securities versus other types of investments
> (e.g., coins or real estate) is advice about securities;¹⁰ (iv) providing a selective list
> of securities is advice about securities even if no advice is provided as to any one
> security;¹¹ and **(v) asset allocation advice is advice about securities.**¹²

Сноски (дословно, сокращённо): ⁷ **Robert R. Champion**, SEC Staff No-Action Letter
(Sept. 22, 1986); ⁸ **Dow Theory Forecasts** (Feb. 2, 1978), **Maratta Advisory, Inc.**
(July 16, 1981); ⁹ Release 1092, **FPC Securities Corp.** (Dec. 1, 1974), см. также
**SEC v. Washington Investment Network, 475 F.3d 392 (D.C. Cir. 2007)**;
¹¹ **RDM Infodustries, Inc.** (Mar. 25, 1996); ¹² **Maratta Advisory, Inc.**

🔴 **Пункт (v) — самое опасное место во всём материале по США: «asset allocation advice
IS advice about securities».** Это позиция штата SEC, не чужая интерпретация. Формально
она опирается на Maratta Advisory (market timing) и SEC v. Bolla — оба про распределение
**инвестиционных активов**, то есть контекст узкий. Но строить защиту на узком прочтении
чужой сноски — слабая позиция в споре с регулятором.
🔴 **Терминологическое следствие, практическое:** слово «allocation» / «распределение
активов» в англоязычных публичных материалах продукта лучше не использовать;
**«cash flow prioritization»** или **«payment prioritization»** описывают ровно то же
самое и не тянут за собой сноску ¹².

**Компенсация, дословно:**

> The term "compensation" has been broadly construed. Generally, the receipt of **any
> economic benefit**… satisfies this element. The person receiving the advice **or another
> person** may pay the compensation.

🔴 «**or another person may pay**» закрывает лазейку «для пользователя бесплатно,
платит работодатель или банк-партнёр». Элемент (3) у нас выполнен всегда.

#### 1.4. Публикации юрфирм — добыты частично, вес низкий

- **Mayer Brown, «Advisers Act Outline»** (IMU 2026, черновик 21.04.2026, Adam Kanter).
  🔴 Прямым фетчем **не открывался**, текст получен через Exa highlights; HTTP-код и размер
  **не замерены**. Ключевая фраза, дословно:
  «**SEC Releases 770 and 1092 identify most financial planners as investment advisers under
  the Act who must comply with it unless they can rely on a statutory exception or exemption.**»
  🔴 **Это против нас, и замалчивать нельзя:** умолчание штата SEC — financial planner
  = investment adviser. Продукт, **называющий себя** «financial planner», стартует из
  презумпции «подпадает» и вынужден доказывать обратное. Продукт, называющий себя
  «debt payoff planner» / «cash flow tool», такой презумпции против себя не создаёт.
  Это вопрос позиционирования с прямой юридической ценой.
- **Wilson Sonsini, «Five Issues for Wealthtech Companies…»** (через JD Supra).
  🔴 Прямым фетчем не открывался, дата в выдаче отсутствует, по внутренней отсылке
  материал ~2023–2024. 🔴 **Помечаю как спекуляцию:** весь фрагмент построен на «may»,
  «can», «it is very possible», «more likely», без единой ссылки на конкретное письмо
  или дело. Существенно: текст относится к продуктам, которые «help investors allocate
  **investments**» и «provide trading signals» — там элемент «securities» и так выполнен.
  К продукту, не касающемуся инвестиций, он по предмету не относится.
- Morrison Foerster, Ropes & Gray, Davis Polk, Skadden, Sidley — **публикаций по этому
  вопросу не найдено**. В выдаче доминировал SEO-контент compliance-вендоров
  (`skills.cat`, `complycode.app`, `terms.law`), который как основание не используется.

🔴 **Непроверенное, которое НЕ переносим в выводы.** В SEO-источнике фигурировало
no-action letter под аббревиатурой «FPL» про софт для финансового планирования —
ни полного названия, ни даты, ни подтверждения существования не найдено. Не использовать,
пока не идентифицировано.

#### 1.5. Вывод по США

**Федеральный уровень: НЕ подпадаем под Advisers Act** — при условии абсолютной чистоты
по ценным бумагам. Логика: элементы (2) business и (3) compensation у подписного веб-сервиса
выполнены практически автоматически; элемент (1) — единственная линия обороны, и он
**не выполнен**, потому что «securities» стоит в обеих ветвях определения, а штат SEC
прямо признаёт классы советов вне периметра («advice about real estate, coins, precious
metals, or commodities **is not** advice about securities»). Долг, резерв и бюджет —
такой же не-security, как недвижимость. Три элемента конъюнктивны, невыполнение одного
закрывает вопрос.

🔴 **Шесть условий, при которых вывод рушится** (по убыванию риска, каждое — с нормой):

| № | Что рушит | Основание |
|---|---|---|
| 1 | Сравнение «гасить долг ИЛИ инвестировать» — даже без названия бумаг | IA-1092: «as opposed to, or in relation to, any non-securities investment or financial vehicle» |
| 2 | Конкретизация резерва: «money market fund», «short-term bond fund», брокерский счёт | IA-1092: specific investment advice **includes** рекомендацию про money market funds |
| 3 | Аффилированная монетизация через брокера/фонды/реферальные ссылки | § 208(d): «illegal… to do indirectly… what cannot be done directly» |
| 4 | Самоназвание «financial planner» | Mayer Brown по Releases 770/1092: «most financial planners are investment advisers» |
| 5 | Термин «asset allocation» в описании функции | Plaze (v): «asset allocation advice **is** advice about securities» |
| 6 | Регистрация в ШТАТАХ независимо от федерального вывода | не проверено, см. ниже |

🔴 **Главное по США одной строкой: защита — не в дисклеймере, а в СЛОВАРЕ.**
Тест функциональный, по существу, а не по ярлыку; дисклеймер «not investment advice»
не защищает никого (это третье независимое подтверждение уже зафиксированного в файле
принципа «дисклеймер не защищает»). Защищает отсутствие в выдаче: названий инструментов,
сравнений с инвестированием, слова «allocation», самоназвания «financial planner», —
и отсутствие инвестиционных партнёров в бизнес-модели.

#### 1.6. Что по США осталось неизвестным — честно

1. 🔴 **Ни одного no-action letter прямо по budgeting / debt-payoff / financial-wellness
   приложению не найдено.** Пройдены: Exa (2 целевых запроса), выдача sec.gov через прокси,
   весь реферативный аппарат § II у Plaze. Все идентифицированные письма — про смежное
   (Champion, RDM Infodustries, Maratta, FPC Securities, Dow Theory Forecasts, Kenisa Oil).
   Предположение подагента о причине («за таким письмом никто не обращался, ответ очевиден
   из статута») — правдоподобно, но это **догадка, а не установленный факт**.
2. 🔴 **Тексты самих no-action letters не добыты — ни одного**, только изложение у Plaze.
   В том числе ключевой **Robert R. Champion (22.09.1986)** — единственный источник тезиса
   «real estate, coins… is not advice about securities». Письма 1970–80-х на sec.gov
   в открытом доступе, как правило, отсутствуют.
3. 🔴 **Letter to Olena Berg (DOL), 22.02.1996** — не добыт, только изложение у Plaze.
   Ближайший к теме financial wellness документ (снимает элемент «business» с работодателя,
   но **не с вендора**, продающего софт работодателю).
4. 🔴 **Регистрация в ШТАТАХ не исследована вообще, и это самый вероятный реальный риск.**
   Есть непроверенное утверждение, что ряд штатов требует регистрации от тех, кто
   **holds himself out** как financial planner, даже без советов по бумагам. Если верно —
   это обходит всю федеральную защиту по элементу (1). Согласуется с тем, что IA-1092
   разрабатывался **совместно с NASAA**. 🔴 **Помечено как ГИПОТЕЗА**, требует отдельной
   темы: NASAA Model Rules + законы целевых штатов. В юрблок в таком виде не переносить.
5. IA-1092 добыт как OCR старого скана; два абзаца (компенсация, стр. 10; вводная часть
   стр. 6–7) в оригинале нечитаемы, восстановлены перекрёстной сверкой по Plaze
   и совпадающим фрагментам. Чистого машинного текста релиза от SEC нет.
6. Mayer Brown и Wilson Sonsini прямым фетчем не открывались (только Exa highlights),
   HTTP-коды и размеры не замерены.

---

### Пункт 7.5. Статус CFP Board — ДОБЫТО. Это ЧАСТНАЯ сертификация, а не регулятор

**Источник.** `https://r.jina.ai/https://www.cfp.net/about-cfp-board/mission-and-priorities`
→ **HTTP 200, 21 238 байт**, снято 16.09.2026. (Страница `/about-cfp-board/our-mission`
→ HTTP 200, 17 342 байта, но тело — **404 Not Found**; рабочий адрес — `/mission-and-priorities`.)

Дословно:

> CFP Board consists of two affiliated **nonprofit** organizations, both focused on achieving
> our Strategic Priorities.
>
> The mission of **CFP Board of Standards, a 501(c)(6) nonprofit organization**, is to
> credential competent and ethical financial planners, uphold CFP® certification as the
> recognized standard and advance the financial planning profession.
>
> The mission of **CFP Board Center for Financial Planning, a 501(c)(3) nonprofit
> organization**, is to advance competent and ethical financial planning and expand
> CFP® professional diversity for the benefit of the public.

Адрес: 1425 K Street NW #800, Washington, DC 20005. Основана в 1985 году.

🔴 **Вывод.** CFP Board — **частная некоммерческая сертифицирующая организация,
а НЕ государственный регулятор**. Её стандарты (в том числе фидуциарный стандарт для
владельцев марки CFP®) обязательны **только для тех, кто добровольно получил марку CFP®**,
и обеспечиваются договорным и товарно-знаковым правом, а не публичным принуждением.
Санкция за нарушение — отзыв права пользоваться маркой, а не административное наказание.

**Что это значит для нас.** CFP Board **не создаёт для нашего продукта никаких обязанностей**:
мы не претендуем на марку CFP® и не нанимаем CFP®-специалистов для оказания услуги.
🔴 Ссылаться на стандарты CFP Board в юрблоке как на регуляторное требование — ошибка;
их место — в разделе о добровольных отраслевых практиках, не в разделе о применимом праве.
Единственный практический риск — репутационно-маркетинговый: использование марки CFP®
или производных обозначений без права на них нарушало бы права на товарный знак.

---

## ИТОГ Г21

### Таблица по пунктам батча

| № | Пункт | Статус | Норма-основание (точная ссылка) | Что это меняет для красной линии |
|---|---|---|---|---|
| 1 | США: Advisers Act и сервис по долгам/накоплениям | **добыто** | 15 U.S.C. § 80b-2(a)(11) (govinfo, 200/32 809 б); SEC Release IA-1092, 08.10.1987 (sec.gov через прокси, 200/36 156 б, 20 стр.); Plaze, «Regulation of Investment Advisers», SEC DIM, апрель 2012 (200/191 161 б) | 🟢 **Федерально НЕ подпадаем**: «securities» стоит в обеих ветвях определения, мы не входим в дефиницию (а не выводимся изъятием). 🔴 Но добавились ДВА новых запрета в словаре продукта: нельзя сравнивать «гасить долг vs инвестировать» (IA-1092) и нельзя называть функцию «asset allocation» (Plaze, п. v) |
| 2 | MCD Art. 4(21) и Art. 22 | **добыто дословно** | Directive 2014/17/EU, Art. 4(21), Art. 22(1), 22(6)(a)-(c), Приложение II ESIS Part A (EUR-Lex через прокси, 200/271 929 б) | Ипотечный контур **не мягче** потребительского: определение и монополия почти дословно совпадают с CCD II. Формулировка ESIS «so that you can make your own choice» — текстовое подтверждение нашего разграничителя |
| 3 | CCD II Art. 3(17) и досрочное погашение | **добыто, ответ ПОЛОЖИТЕЛЬНЫЙ (против нас)** | Directive (EU) 2023/2225, Art. 3(17), Art. 3(22), **Art. 16(6)(b) и (c)** (EUR-Lex через прокси, 200/207 127 б) | 🔴 **Ключевой результат батча.** Изъятия 16(6)(b) и (c) написаны для «advisory services **in the context of management of existing debt**» — изъятие нужно только для охваченного, значит совет об управлении существующим долгом **входит** в Art. 3(17). Ни одно из четырёх изъятий нам не подходит; (c) отсекает прямо словами «do not operate on a commercial basis» |
| 4 | UK art. 72A RAO и PERG 2.9.18G; art. 72 | **добыто, гипотеза СНЯТА** | RAO 2001/544 art. 72A — **omitted (31.12.2020)** by S.I. 2019/1361 reg. 5(2) (legislation.gov.uk, 200/41 878 б); art. 72 (200/137 910 б) | 🔴 Прежняя гипотеза заменена нормой, и основание **сильнее и хуже для нас**: исключение для information society services в праве UK **отсутствует как таковое**, а не «не распространяется на третьи страны». Ссылаться на art. 72A нельзя вовсе |
| 5 | Ирландия: транспозиция CCD II | **добыт доказанный отрицательный результат** | Сплошной проход перечня S.I. за 2026 (`irishstatutebook.ie/eli/2026/si`, 200/279 434 б) + A&L Goodbody, 07.05.2026 (200/20 752 б) | Транспонирующего акта нет, дедлайн 20.11.2025 просрочен. По Ирландии ориентируемся на текст самой директивы; ожидание рынка — «no gold-plating» |
| 6 | ОАЭ onshore (CBUAE) | **добыто** | DFL 14/2018 в ред. DFL 9/2021, **Art. 65(1)(a)-(i)**, консолидированный текст CBUAE Rulebook (200/259 329 б) | 🟢 Перечень лицензируемой деятельности **исчерпывающий**, совета в нём нет вовсе. В ОАЭ во всех трёх контурах (CBUAE, DIFC, ADGM) мы вне лицензирования. 🔴 Осторожно с Art. 65(1)(h) «arranging and/or marketing» — партнёрская выдача переводит нас под лицензию |
| 7 | Добивка до дословных цитат | **добыто 4 из 5** | Release 33-11377 (200/14 017 б); Lowe v. SEC, 472 U.S. 181 (Cornell, 200/145 529 б); O.C.G.A. § 18-5-1 и § 18-5-3 (200/14 926 и 14 463 б); CFP Board (200/21 238 б) | Georgia — третий штат, добыт дословно. 🔴 **Lowe нас НЕ защищает** (мы персонализированы — по критерию Lowe это «плохая» сторона). CFP Board — частная сертификация, в юрблок как право не идёт. Delaware/RI/Colorado не добирались осознанно |

### 🔴 Изменилась ли граница «где мы вне регулирования» — ДА, в трёх местах

**1. ЕС: граница сдвинулась ПРОТИВ нас, и это главный результат батча.**
До Г21 статус «покрывает ли CCD II совет о досрочном погашении» был записан как
«ключевая открытая неопределённость». Теперь неопределённости нет: **Art. 16(6)(b) и (c)
CCD II доказывают охват от противного** — законодатель ЕС не стал бы писать изъятие для
«advisory services in the context of management of existing debt», если бы такой совет
не подпадал под Art. 3(17). Наш Avalanche (совет, какой из существующих кредитов гасить
первым) с 20.11.2026 в ЕС — **advisory services**, и коммерческий характер сервиса прямо
отсекает единственное подходящее по предмету изъятие (c). То же самое по ипотеке через
MCD Art. 22(6)(b). **Вывод: ЕС переходит из «вероятно вне» в «внутри, изъятия недоступны».**
Это ставит ЕС в один ряд с UK, а не с ОАЭ.

**2. UK: граница не сдвинулась, но исчезла последняя надежда на выход.**
Art. 72A изъят из RAO целиком 31.12.2020 — не «неприменим к нам», а не существует.
Вместе с подтверждённым отсутствием 39E в art. 72 (overseas persons) это значит:
**по долговому контуру UK у иностранного поставщика нет ни одного исключения.**
Единственная оставшаяся линия защиты — территориальная («carrying on in the UK»,
s. 418 FSMA), и она **не исследована**. Это теперь самая важная открытая правовая
тема по UK.

**3. США и ОАЭ: граница подтверждена в нашу пользу, но появились новые запреты в СЛОВАРЕ.**
Федерально в США мы вне Advisers Act, в ОАЭ вне лицензирования CBUAE — оба вывода
получены из первоисточника, а не из обзоров. 🔴 Но США добавили два ограничения,
которых в файле раньше не было и которые касаются **формулировок продукта**, а не
его архитектуры: (а) нельзя сравнивать досрочное погашение с инвестированием —
это само по себе делает нас «advising… as to the desirability of investing in securities»
(IA-1092); (б) нельзя называть функцию «asset allocation» — позиция штата SEC прямо
говорит «asset allocation advice **is** advice about securities» (Plaze, п. v).
Безопасные термины: **«cash flow prioritization»**, **«payment prioritization»**.

**4. Разграничитель подтверждён четвёртый раз, уже из нового источника.**
Приложение II MCD (ESIS, Part A) предписывает кредитору формулу
«**We are not recommending a particular mortgage for you… so that you can make your own
choice**». Это буквально тот разграничитель «assisting the person to make their own choice»,
который уже зафиксирован в этом файле, — теперь он подтверждён текстом европейского
законодателя, а не только руководством FCA.

**5. Принцип «дисклеймер не защищает» подтверждён независимо в третий раз** — теперь
американским материалом: тест по Advisers Act функциональный, по существу деятельности,
а ярлык на продукте его не меняет; § 208(d) прямо запрещает делать косвенно то,
что нельзя прямо.

### Общая карта на конец Г21 (по жёсткости для нас)

| Юрисдикция | Инвестиционный контур | Долговой контур |
|---|---|---|
| США (федерально) | вне (нет securities) | вне федерально; 🔴 **штаты не проверены**; Georgia не ловит (нужны действия с долгом, а не совет) |
| ЕС | вне (ESMA35-43-3861 §58) | 🔴 **ВНУТРИ с 20.11.2026** (CCD II Art. 3(17) + 16(6)); ипотека — то же через MCD |
| UK | вне (PERG 8.26.2G(1)) | 🔴 **ВНУТРИ** (art. 39E RAO + PERG 17); исключений нет — 72A изъят, 72 не покрывает 39E |
| ОАЭ (CBUAE / DIFC / ADGM) | вне | 🟢 **вне во всех трёх контурах** |
| РФ | вне | вне (по ранее зафиксированному в этом файле) |

### Что осталось неизвестным после Г21

1. 🔴 **Регистрация инвестиционных советников в ШТАТАХ США** — не исследовалась вовсе.
   Есть непроверенная гипотеза, что ряд штатов требует регистрации от тех, кто
   *holds himself out* как financial planner, даже без советов по бумагам. Если верно —
   обходит всю федеральную защиту. **Кандидат №1 в следующий правовой батч.**
2. 🔴 **Территориальность UK: s. 418 FSMA «carrying on in the UK»** — единственная
   оставшаяся линия защиты по британскому долговому контуру, не исследована.
3. Толкования Еврокомиссии и позиции нацрегуляторов (BaFin, AMF, Banca d'Italia, CBI)
   по Art. 3(17) CCD II — не найдены. Вывод по п. 3 от них **не зависит** (получен
   из текста Art. 16(6)), но подтверждение усилило бы позицию.
4. Тексты SEC no-action letters — ни одного в оригинале (только изложение у Plaze);
   ключевой Robert R. Champion (22.09.1986) не прочитан.
5. Подзаконные регламенты Совета директоров CBUAE (Art. 65(2)(a)) и режим SCA
   в ОАЭ onshore — не просматривались.
6. Delaware, Rhode Island, Colorado по debt adjusting — осознанно не добирались
   (задача «третий штат» закрыта Джорджией).

### Процесс — прозрачно

Тип запроса: **breadth-first**, 7 независимых под-вопросов. Субагентов: **ОДИН**
(`base-kit:researcher`, по пункту 1 — США; 13 действий из 14, своих подагентов не запускал),
остальные шесть пунктов вахта сняла сама прямыми запросами. Правило «по одному агенту
за раз» соблюдено: в одном ходе ни разу не было больше одного вызова `Agent`.
Собственных `WebSearch` — 4. Запись в файл велась **по ходу**, шестью отдельными
дописываниями, до формирования итогового ответа.

**Канал, решивший батч:** текстовый прокси `r.jina.ai`. Через него взято 11 из 14
источников, включая все, что отдавали 202/403/пустое тело напрямую (EUR-Lex, sec.gov,
justia, cfp.net, rulebook.centralbank.ae). Прямой `curl -sk --http1.1` с браузерным UA
сработал только на `legislation.gov.uk` и `irishstatutebook.ie`.

**Новые замеры каналов, зафиксировать для следующих батчей:**
- 🟢 **Wayback поднялся** (200, 261 986 б) — канал, лежавший 16.09 в прошлых батчах, снова жив.
- 🔴 **Cornell LII через прокси: код 200, но страницы USC отдаются БЕЗ статутного текста**
  (только примечания). Судебные решения отдаются полностью. Правило: **USC брать
  с `govinfo.gov`, судебные решения — с Cornell.**
- 🔴 **CBUAE Rulebook отдаёт отменённые редакции по «красивым» slug-адресам**
  (`article-65-financial-activities` → «Status: Repealed»). Брать только консолидированный
  текст закона целиком.
- 🔴 **`irishstatutebook.ie`: рабочий перечень S.I. — `/eli/<год>/si`** (без `/en/`,
  без `.html`). Три «естественных» варианта адреса дают 404 — именно на этом
  спотыкались прошлые заходы.

---

## ДОБОР Г26 (16.09.2026)

Второй правовой заход после Г21. Состав — `docs/research/queue/COVERAGE_AUDIT_3.md`, «→ Г26».
Пункты: (1) штаты США и financial planners; (2) s. 418 FSMA и PERG 2.4; (3) толкования CCD II
Art. 3(17); (4) SEC no-action letters в оригинале. Запись ведётся по ходу, после каждого источника.

### Г26.2 UK — s. 418 FSMA и PERG 2.4 (дословно)

**Источник 1.** FSMA 2000 s. 418, legislation.gov.uk/ukpga/2000/8/section/418 — прямой `curl -sk --http1.1`
с браузерным UA, **HTTP 200, 83 231 б** (XML-версия `/data.xml` — 200, 133 227 б), снято 16.09.2026.
Норма закона (актуальная редакция, с крипто-кейсами 6B–6F).

> **418 Carrying on regulated activities in the United Kingdom.**
> (1) [In the cases] described in this section, a person who—
> (a) is carrying on a regulated activity, but
> (b) would not otherwise be regarded as carrying it on in the United Kingdom,
> is, for the purposes of this Act, to be regarded as carrying it on in the United Kingdom.
> (2) . . . [omitted] (3) . . . [omitted]
> (4) The third case is where— (a) his registered office (or if he does not have a registered office
> his head office) is in the United Kingdom; (b) the day-to-day management of the carrying on of the
> regulated activity is the responsibility of— (i) his registered office (or head office); or
> (ii) another establishment maintained by him in the United Kingdom.
> (5) The fourth case is where— (a) his head office is not in the United Kingdom; but (b) the activity
> is carried on from an establishment maintained by him in the United Kingdom.
> (5A) . . . [omitted]
> (5AA) The sixth case … [managing an AIF] …
> **(6) [For the purposes of the preceding subsections] it is irrelevant where the person with whom the
> activity is carried on is situated.**
> (6B)–(6F) [ninth–eleventh cases: qualifying stablecoin, cryptoasset activities; «consumer» = an
> individual in the United Kingdom …]
> (7) . . . [omitted] (8) [AIF «marketed»]
> Textual Amendments: F1 Words in s. 418(1) substituted (31.12.2020) by S.I. 2019/632, regs. 1(3), 86(2).

**Источник 2.** FCA Handbook, PERG 2.4 «Link between activities and the United Kingdom»,
`r.jina.ai/https://www.handbook.fca.org.uk/handbook/PERG/2/4.html` — **HTTP 200, 16 793 б**,
снято 16.09.2026, раздел обновлён 29.07.2022. Это **guidance (G) регулятора**, не норма закона.

> **PERG 2.4.1 G** Section 19 of the Act (The general prohibition) provides that the requirement to be
> authorised under the Act only applies in relation to activities that are carried on 'in the United
> Kingdom'. … when there is a cross-border element, for example because a client is outside the United
> Kingdom or because some other element of the activity happens outside the United Kingdom, the question
> may arise as to where the activity is carried on.
>
> **PERG 2.4.3 G** Section 418 of the Act … takes this one step further. **It extends the meaning that
> 'in the United Kingdom' would ordinarily have by setting out additional cases.** …
> (3) The case is where a regulated activity is carried on by a UK-based person and the day-to-day
> management of the activity is the responsibility of an establishment in the United Kingdom.
> (4) The case is where a regulated activity is carried on by a person who is not based in the United
> Kingdom but is carried on from an establishment in the United Kingdom. …
> ((1), (2), (5) — [deleted])
>
> **PERG 2.4.5 G** A person who is based outside the United Kingdom but who sets up an establishment in
> the United Kingdom must therefore consider … Third, such a person will need to ensure that he does not
> contravene other provisions of the Act that apply to persons who are not authorised. These include the
> controls on financial promotion (section 21 …), and on giving the impression that a person is
> authorised (section 24).
>
> 🔴 **PERG 2.4.6 G** A person based outside the United Kingdom **may also be carrying on activities in
> the United Kingdom even if he does not have a place of business maintained by him in the United Kingdom
> (for example, by means of the internet or other telecommunications system or by occasional visits).**
> In that case, it will be relevant to consider whether what he is doing satisfies the business test as
> it applies in relation to the activities in question. In addition, he may be able to rely on the
> exclusions from certain regulated activities that apply in relation to overseas persons (see
> PERG 2.9.15 G).

**Выжимка.** s. 418 — норма **расширяющая**, а не ограничивающая: она добавляет случаи, когда
деятельность *считается* осуществляемой в UK, и ни одного случая, когда она *не считается*. Поэтому
«s. 418 нас защищает» — неверная постановка: защитить может только **общее значение** слов
«in the United Kingdom» в s. 19, а s. 418 для нас нейтральна (у нас нет ни UK-офиса, ни UK-заведения —
третий и четвёртый случаи не срабатывают). Общее значение FCA толкует **против** нас прямо: PERG 2.4.6G
называет интернет примером того, как иностранец без места деятельности в UK всё-таки осуществляет
деятельность в UK, и отсылает к двум фильтрам — business test и исключениям для overseas persons.
Второй фильтр для нас закрыт (Г16/Г21: art. 72 RAO не содержит 39E). Остаётся только business test —
см. следующий источник.

**Источник 3.** FCA Handbook, PERG 2.3 «The business element»,
`r.jina.ai/https://www.handbook.fca.org.uk/handbook/PERG/2/3.html` — **HTTP 200, 23 009 б**, 16.09.2026. Guidance.

> **PERG 2.3.2 G (3B)** If a not-for-profit body is carrying on debt adjusting, debt counselling or
> providing credit information services … it is to be regarded as doing so by way of business. …
> This change to the business element does not apply, however, if the not-for-profit body carries on that
> activity only on an occasional basis.
> **(4)** The business element for all other regulated activities is that the activities are carried on
> by way of business. This applies to … credit-related regulated activities …
>
> **PERG 2.3.3 G** Whether or not an activity is carried on by way of business is ultimately a question of
> judgement that takes account of several factors (none of which is likely to be conclusive). These include
> **the degree of continuity, the existence of a commercial element, the scale of the activity** and the
> proportion which the activity bears to other activities carried on by the same person but which are not
> regulated.

**Источник 4.** FCA Handbook, PERG 2.9 «Regulated activities: exclusions applicable in certain circumstances»,
`r.jina.ai/https://www.handbook.fca.org.uk/handbook/perg2/perg2s9` — **HTTP 200, 83 633 б**, 16.09.2026.
(Адрес `/handbook/PERG/2/9.html` через прокси отдал ЧУЖОЙ раздел — PERG 2.10, 26 766 б; `/PERG/2/9A.html` —
2 299 б пустышка. Правильный адрес — старая схема `perg2/perg2s9`.) Guidance.

> **PERG 2.9.15 G** This group of exclusions applies, in specified circumstances, to the regulated
> activities of: (1) dealing in investments as principal; (2) dealing in investments as agent;
> (3) arranging (bringing about) deals in investments and making arrangements with a view to transactions
> in investments; (3A) arranging a home finance transaction; (3B) operating a multilateral trading facility;
> (3C) operating an organised trading facility; (4) advising on investments; (5) entering into a home finance
> transaction; (6) administering a home finance transaction; and (7) agreeing to carry on [перечень] …
>
> **PERG 2.9.16 G** An overseas person is defined as a person who carries on what would be regulated
> activities … but who does not do so, or offer to do so, from a permanent place of business maintained by
> him in the United Kingdom. **Where a person does not have a permanent place of business in the United
> Kingdom, he will not, in any event, need to rely on these exclusions unless what he does is regarded as
> carried on in the United Kingdom (see PERG 2.4).** …
>
> **PERG 2.9.17 G** … (2) The second case is where a particular regulated activity is carried on as a
> result of what is termed a 'legitimate approach'. An approach to an overseas person that has not been
> solicited by him in any way, or has been solicited in a way that does not contravene the restrictions on
> financial promotion in section 21 of the Act, is a legitimate approach. … In such circumstances, the
> overseas person can, without requiring authorisation, … give advice in the United Kingdom …

**Выжимка по UK (Г26.2).**
1. Перечень PERG 2.9.15G подтверждает Г21 третьим независимым путём: **debt counselling (art. 39E) в
   исключениях для overseas persons нет**. Механизм «legitimate approach» (PERG 2.9.17G(2)) — тот самый,
   который спасал бы нас при обращении UK-пользователя по своей инициативе, — для долгового контура
   **недоступен**.
2. **Business test нас не спасает:** непрерывность, коммерческий элемент, масштаб (PERG 2.3.3G) — это
   ровно описание SaaS-подписки. Для credit-related activities тест «by way of business» (PERG 2.3.2G(4));
   даже некоммерческий поставщик debt counselling считается действующим by way of business (3B).
3. **Прямой ответ: s. 418 нас НЕ защищает — она вообще не про защиту.** Это норма-расширитель. Вопрос
   решается общим значением «in the United Kingdom» в s. 19, и регулятор (guidance, не закон, не суд)
   прямо называет интернет примером деятельности в UK без места деятельности в UK (PERG 2.4.6G).
   Судебного толкования этого места в заходе не добыто (см. ниже, поиск). Единственная инженерная
   защита, которая остаётся, — **не вести деятельность в UK фактически**: не принимать UK-пользователей
   для долгового модуля (геоблок/проверка резидентства при регистрации), не таргетировать UK
   (фунты, UK-кредиторы, реклама на UK). Это вывод из совокупности норм, а не цитата.
4. Независимо от авторизации, s. 21 FSMA (financial promotion) применяется к сообщениям, «capable of
   having an effect in the United Kingdom» — упомянут в PERG 2.4.5G; текст s. 21(3) в этом заходе не
   снимался.

**Источник 5.** FSMA 2000 s. 21, legislation.gov.uk/ukpga/2000/8/section/21 — прямой `curl`, **HTTP 200,
89 522 б**, 16.09.2026. Норма закона.

> **21 Restrictions on financial promotion.** (1) A person ("A") must not, in the course of business,
> communicate an invitation or inducement to (a) engage in investment activity, or (b) to engage in claims
> management activity.
> (2) But subsection (1) does not apply if— (a) A is an authorised person; or (b) the content of the
> communication is approved for the purposes of this section by an authorised person. …
> **(3) In the case of a communication originating outside the United Kingdom, subsection (1) applies only
> if the communication is capable of having an effect in the United Kingdom.**

**Источник 6.** Financial Promotion Order 2005 (SI 2005/1529), Schedule 1, legislation.gov.uk/uksi/2005/1529/schedule/1
— прямой `curl`, **HTTP 200, 498 204 б**, 16.09.2026 (адрес `/schedule/1/part/1` — 404). Норма (подзаконный акт).

> **Debt-counselling. 5B.** — (1) Advising a borrower about the liquidation of a debt due under a relevant
> credit agreement is a controlled activity. (2) Advising a hirer about the liquidation of a debt due under a
> consumer hire agreement is a controlled activity.
> [Textual Amendments F45: Sch. 1 paras. 5A, 5B inserted (26.7.2013 …, 1.4.2014 …) by S.I. 2013/1881,
> arts. 1(2)(6), 17(6)(b)]

**Выжимка.** Для UK у нас ДВА независимых территориальных крючка, и второй мягче первого не бывает:
(а) s. 19 — «carrying on in the UK» (оценочно, PERG 2.4.6G прямо против нас); (б) **s. 21(3) —
«capable of having an effect in the UK»**, и debt counselling — **controlled activity** по FPO Sch. 1
para. 5B, то есть реклама долгового модуля, доступная UK-аудитории, сама по себе — financial promotion,
даже если s. 19 бы не сработал. Baker McKenzie Resource Hub (UK, «main sources of regulatory laws»,
через `r.jina.ai`, HTTP 200, 4 699 б, 16.09.2026 — комментарий юрфирмы) формулирует то же:
«These restrictions apply separately to one another: it is possible that a particular activity is not
considered to be carrying on a regulated activity in the UK …, but sending communications to customers in
relation to that activity may still be a breach of the financial promotion restriction. A breach of either
of these restrictions is a criminal offense and may result in certain agreements being unenforceable.»
Судебной практики по интернет-случаю s. 19 не добыто: `WebSearch` (1 запрос) дал только LexisNexis
Practice Note «Territorial scope of the general prohibition» (платный, не открывался) и страницы FCA.

### Г26.1 Штаты США — financial planners без ценных бумаг

**Источник 7.** Nevada Revised Statutes, Chapter 628A «Financial Planners»,
`r.jina.ai/https://www.leg.state.nv.us/nrs/nrs-628a.html` — **HTTP 200, 5 736 б**, 16.09.2026
(ревизия на странице: «Rev. 4/15/2026 … 2025»). Норма закона штата, полный текст главы (4 секции).

> **NRS 628A.010 Definitions.** As used in this chapter, unless the context otherwise requires:
> 1. "Client" means a person who receives advice from a financial planner.
> 2. "Compensation" means a fee for services provided by a financial planner to a client or a commission or
> other remuneration derived by a financial planner from a person other than the client as the result of the
> purchase of a good or service by the client.
> 3. **"Financial planner" means a person who for compensation advises others upon the investment of money or
> upon provision for income to be needed in the future, or who holds himself or herself out as qualified to
> perform either of these functions**, but does not include: (a) An attorney …; (b) A certified public
> accountant …; or (c) A producer of insurance … or an insurance consultant …, whose advice upon investment
> or provision of future income is incidental to the practice of his or her profession or business.
> (Added 1993, 1372; A 1995, 1453, 1635; 1997, 530; 2001, 2256; 2017, 1796, 3476)
>
> **NRS 628A.020 Duties of financial planner.** A financial planner has the duty of a fiduciary toward a
> client. A financial planner shall disclose to a client, at the time advice is given, any gain the financial
> planner may receive, such as profit or commission, if the advice is followed. **A financial planner shall
> make diligent inquiry of each client to ascertain initially, and keep currently informed concerning, the
> client's financial circumstances and obligations and the client's present and anticipated obligations to
> and goals for his or her family.**
>
> **NRS 628A.030 Liability of financial planner.** 1. If loss results from following a financial planner's
> advice under any of the circumstances listed in subsection 2, the client may recover from the financial
> planner in a civil action the amount of the economic loss and all costs of litigation and attorney's fees.
> 2. … the financial planner: (a) Violated any element of his or her fiduciary duty; (b) **Was grossly
> negligent in selecting the course of action advised, in the light of all the client's circumstances known
> to the financial planner**; or (c) Violated any law of this State in recommending the investment or service.
>
> **NRS 628A.040** 1. Except as otherwise provided in subsection 2, **a financial planner shall maintain
> insurance covering liability for errors or omissions, or a surety bond to compensate clients for losses
> actionable pursuant to this chapter, in an amount of $1,000,000 or more.** 2. The provisions of
> subsection 1 do not apply to: (a) A broker-dealer or sales representative licensed pursuant to NRS 90.310
> or exempt under NRS 90.320; or (b) An investment adviser licensed pursuant to NRS 90.330 or exempt under
> NRS 90.340 or 90.345. (A 2017, 1796; 2021, 249)

**Выжимка (Невада).** 🔴 **Главная находка пункта.** Регистрации NRS 628A **не требует** — но определение
не привязано к ценным бумагам: «investment of money» (не «securities») **или** «provision for income to be
needed in the future», плюс ветка holding out. Цель накоплений / резерв / пенсионная цель FINPILOT — прямо
«provision for income to be needed in the future». Последствия при попадании: (1) фидуциарная обязанность;
(2) гражданская ответственность за убытки с судебными расходами и гонорарами адвокатов, в т.ч. за **gross
negligence в выборе рекомендованного курса**; (3) **обязательная страховка E&O или surety bond от
$1 000 000**, от которой освобождены только зарегистрированные брокеры и инвестсоветники — то есть
в Неваде «быть вне Advisers Act» делает положение **хуже**, а не лучше. Вопрос, является ли автоматический
сервис «person who advises», и применяется ли глава к иностранному поставщику без присутствия в Неваде,
текстом не решён; толкований/практики в заходе не добыто. Порядок величин: это не лицензия, а
частноправовой и страховой режим; нарушение 628A.040 глава санкцией не снабжает (санкций в тексте нет).

**Источник 8.** Uniform Securities Act (2002), NCCUSL, «without prefatory note or comments»,
uniformlaws.org/HigherLogic/System/DownloadDocumentFile.ashx?DocumentFileKey=af36852d-457e-db56-3fc2-b2485cdc47e9 —
прямой `curl`, **HTTP 200, 648 853 б, PDF 101 стр.**, `pdftotext`, 16.09.2026. (Копия на nasaa.org —
`curl` 403, 2 335 б.) Это **модельный закон**, силу имеет только в редакции, принятой штатом.

> **SECTION 102 (15)** "Investment adviser" means a person that, for compensation, engages in the business of
> advising others, either directly or through publications or writings, **as to the value of securities or the
> advisability of investing in, purchasing, or selling securities** or that, for compensation and as a part of
> a regular business, issues or promulgates analyses or reports **concerning securities**. **The term includes a
> financial planner or other person that, as an integral component of other financially related services,
> provides investment advice to others for compensation as part of a business or that holds itself out as
> providing investment advice to others for compensation.** The term does not include: (A) an investment adviser
> representative; (B) a lawyer, accountant, engineer, or teacher whose performance of investment advice is solely
> incidental …; (C) a broker-dealer …; (D) a publisher of a bona fide newspaper, news magazine, or business or
> financial publication of general and regular circulation; (E) a federal covered investment adviser; (F) a bank
> or savings institution; (G) any other person that is excluded by the Investment Advisers Act of 1940 from the
> definition of investment adviser; or (H) any other person excluded by rule or order under this [Act].
>
> **(16)** "Investment adviser representative" means an individual employed by or associated with an investment
> adviser … and who makes any recommendations or otherwise gives investment advice **regarding securities** …
>
> **SECTION 403. (a)** It is unlawful for a person to transact business in this State as an investment adviser
> unless the person is registered under this [Act] as an investment adviser or is exempt …
> **(b)** … exempt …: (1) a person without a place of business in this State that is registered under the
> securities act of the state in which the person has its principal place of business if its only clients in this
> State are: [(A)–(D) профессионалы, institutional investors, bona fide preexisting clients …]; **(2) a person
> without a place of business in this State if the person has had, during the preceding 12 months, not more than
> five clients that are residents of this State** in addition to those specified under paragraph (1); or
> (3) any other person exempted by rule or order under this [Act].

**Выжимка (модельный закон).** Гипотеза «financial planner презюмируется инвестсоветником без ценных бумаг»
по тексту USA 2002 **не подтверждается**: вторая фраза § 102(15) включает financial planner, который
«provides **investment advice**» или holds itself out as providing «**investment advice**», а весь контекст
определения и соседнего (16) — advice «regarding securities». Фраза расширяет круг ЛИЦ (планировщик, для
которого совет — «integral component of other financially related services»), но не ПРЕДМЕТ. Рыночный
смысл тот же, что федерально: без ценных бумаг — не investment adviser. 🔴 Но ветка holding out в модельном
законе есть: называть себя «providing investment advice» опасно само по себе. Де-минимис § 403(b)(2)
(≤5 клиентов-резидентов за 12 мес. без места деятельности в штате) для массового SaaS бесполезен.

**Источник 9.** Joel Seligman, «The New Uniform Securities Act», *Washington University Law Quarterly*, vol. 81,
p. 243 (2003), journals.library.wustl.edu/lawreview/article/6457/galley/23290/download/ — прямой `curl`,
**HTTP 200, 904 835 б, PDF 57 стр.**, `pdftotext`, 16.09.2026. Статья репортёра разработки USA 2002
(доктрина; текст совпадает по смыслу с Official Comment к § 102(15) — сам Comment в этом заходе НЕ снят,
версия NCCUSL «without comments»).

> The definition of "investment adviser" is in Section 102(15). This term generally follows the definition in
> Section 202(a)(11) of the Investment Advisers Act of 1940, but has been updated to take into account new media
> such as the Internet.[24]
> **The second sentence in the term addressing financial planners is new. The purpose of this sentence is to
> achieve functional regulation of financial planners who satisfy the definition of investment adviser.**[25]
> This reference is not intended to preclude persons who hold a formally recognized financial planning or
> consulting designation or certification from using this designation. **The use by a person of a title,
> designation or certification as a financial planner or other similar title, designation, or certification
> alone does not require registration as an investment adviser.**
>
> [fn. 24] **The first sentence in Section 102(15) is identical to the first sentence in the 1956 Act Section
> 401(f)** and the counterpart language in Section 202(a)(11). … These terms have been returned to Section
> 102(15) because of the intention that this definition be construed uniformly with the definition in
> Section 202(a)(11) of the Investment Advisers Act of 1940. …
> [fn. 25] Cf. … Investment Advisers Release No. IA-1,092, 39 SEC Docket 494 (Oct. 8, 1987) (similar approach
> in SEC Interpretative Release).

**Выжимка.** 🟢 Гипотеза пункта 1 **опровергнута для модельного закона прямым текстом разработчика**:
(1) в USA 1956 § 401(f) фразы о financial planner нет вовсе — первая фраза идентична федеральной;
(2) в USA 2002 фраза добавлена для «functional regulation of financial planners **who satisfy the definition
of investment adviser**», т. е. тех, кто советует о ценных бумагах; (3) сам титул «financial planner»
регистрации **не требует**; (4) толковать предписано единообразно с § 202(a)(11) Advisers Act и IA-1092 —
значит, вывод Г21 (без securities — вне) переносится на штаты модельного закона. Остаются: штаты с
собственными законами о financial planners вне securities act (Невада — см. выше) и штаты, отступившие
от модельного текста. Это проверяется ниже.

**Источник 10.** U.S. GAO, GAO-11-235 «Consumer Finance: Regulatory Coverage Generally Exists for Financial
Planners, but Consumer Protection Issues Remain», 18.01.2011, gao.gov/assets/a314689.html — прямой `curl` 403
(388 б), через `r.jina.ai` **HTTP 200, 125 846 б**, 16.09.2026. Отчёт федерального аудитора (не норма, не
позиция регулятора; внутри — пересказ позиций SEC staff и NASAA).

> Most states regulate the use of the title "financial planner," and state securities and insurance laws can
> apply to the misuse of this title and other titles. For example, **according to NASAA, at least 29 states
> specifically include financial planners in their definition of investment adviser.**[25] …
> [25] The District of Columbia and Puerto Rico also include financial [planners …]
>
> As noted earlier, the activities a financial planner normally engages in generally include advice related to
> securities--and such activities make financial planners subject to regulation under the Advisers Act. …
> **SEC staff told us that financial planners holding even broad discussions of securities--for example, what
> proportion of a portfolio should be invested in stocks--would be required to register** as investment advisers
> or investment adviser representatives. **In theory, a financial planner could offer only services that do not
> fall under existing regulatory regimes--for example, advice on household budgeting--but such an example is
> likely hypothetical and such a business model may be hard to sustain.** SEC and NASAA staff, a majority of the
> state securities regulators we spoke with, and many representatives of the financial services industry told us
> that they were not aware of any individuals serving as financial planners who were not regulated as investment
> advisers or regulated under another regulatory regime. Some regulators and industry representatives also said
> that, **to the extent that financial planners offered services that did not fall under such regulation, the new
> Bureau of Consumer Financial Protection potentially could have jurisdiction over such services.**[27]
>
> … Federal and state regulators told us **they generally focused their oversight and enforcement actions on
> financial planners' activities rather than the titles they use.** Moreover, NASAA has said that no matter what
> title financial planners use, most are required to register as investment adviser representatives …

**Выжимка.** «29 штатов включают financial planners в определение investment adviser» — это та самая фраза
модельного USA 2002 (штаты, принявшие его или аналог), и по Seligman она работает только для планировщиков,
советующих о securities. Федеральный аудитор прямо называет «advice on household budgeting» сервисом **вне
существующих режимов** (на 2011 г.) и указывает на CFPB как на возможного регулятора такого сервиса — это
новый хвост: CFPB/UDAAP, а не регистрация. Надзор, по словам регуляторов, смотрит на **деятельность, а не
титул** — это против гипотезы «holding out как financial planner сам по себе требует регистрации».

**Источник 11.** 🔴 Washington, **RCW 21.20.005(8)** (Securities Act of Washington, Definitions),
app.leg.wa.gov/RCW/default.aspx?cite=21.20.005 — прямой `curl`, **HTTP 200, 122 119 б**, 16.09.2026.
Норма закона штата, действующая редакция; история: «[2011 c 336 s 594; 2002 c 65 s 1; 1998 c 15 s 1;
1994 c 256 s 3. Prior: 1993 c 472 s 14; 1993 c 470 s 4; 1989 c 391 s 1; …]».

> **(8) "Investment adviser"** means any person who, for compensation, engages in the business of advising
> others, either directly or through publications or writings, as to the value of securities or as to the
> advisability of investing in, purchasing, or selling securities, or who, for compensation and as a part of a
> regular business, issues or promulgates analyses or reports concerning securities. "Investment adviser" also
> includes financial planners and other persons who, as an integral component of other financially related
> services, (a) provide the foregoing investment advisory services to others for compensation as part of a
> business or (b) hold themselves out as providing the foregoing investment advisory services to others for
> compensation. **Investment adviser shall also include any person who holds himself or herself out as a
> financial planner.** "Investment adviser" does not include (a) a bank, savings institution, or trust company,
> (b) a lawyer, accountant, certified public accountant …, engineer, or teacher whose performance of these
> services is solely incidental …, (c) a broker-dealer …, (d) a publisher of any bona fide newspaper, news
> magazine, news column, newsletter, or business or financial publication or service, whether communicated in
> hard copy form, by electronic means, or otherwise, **that does not consist of the rendering of advice on the
> basis of the specific investment situation of each client**, (e) a radio or television station, (f) a person
> whose advice, analyses, or reports relate only to securities exempted by RCW 21.20.310(1), (g) an investment
> adviser representative, or (h) such other persons not within the intent of this paragraph as the director may
> by rule or order designate.
>
> **(9) "Investment adviser representative"** means … individual … employed by or associated with an investment
> adviser, and who does any of the following: (a) Makes any recommendations or otherwise renders advice regarding
> securities; (b) Manages accounts or portfolios of clients; (c) Determines which recommendation or advice
> regarding securities should be given; (d) Solicits, offers, or negotiates for the sale of or sells investment
> advisory services; …

**Источник 12.** Washington DFI, Securities Act Interpretive Statement 22 (адаптирован 01.04.2002, W. M. Beatty,
General Counsel), dfi.wa.gov/industry/securities-act-interpretive-statements/securities-act-interpretive-statement-22 —
через `r.jina.ai` **HTTP 200, 9 905 б**, 16.09.2026. Позиция отдела ценных бумаг штата (толкование, не норма).
Цитирует тогдашнюю редакцию (номер пункта (6), текст про financial planner идентичен) и регистрационную норму:

> **RCW 21.20.040(3)** It is unlawful for any person to transact business in this state as an investment adviser
> or investment adviser representative unless: (a) The person is so registered or exempt from registration under
> this chapter; (b) the person has no place of business in this state and (i) the person's only clients in this
> state are [профессиональные клиенты] …, or (ii) **during the preceding twelve-month period the person has had
> fewer than six clients who are residents of this state** other than those specified in (b)(i) …; (c) … adviser
> to an investment company …; (d) the person is a federal covered adviser and … complied with … RCW 21.20.050;
> or (e) the person is excepted from the definition of investment adviser under section 202(a)(11) of the
> Investment Advisers Act of 1940.
> (Текст (3) — в редакции 2002 г. по цитате DFI; актуальная редакция RCW 21.20.040 в заходе не снималась.)

**Выжимка (Вашингтон).** 🔴 **Гипотеза пункта 1 ПОДТВЕРЖДЕНА для штата Вашингтон — текстом закона.**
Третья фраза RCW 21.20.005(8) — самостоятельная ветка определения, не связанная словами с securities:
«any person who holds himself or herself out as a financial planner». В отличие от модельного закона (где
разработчик прямо сказал, что титул сам по себе регистрации не требует), здесь законодатель штата написал
обратное. Следствие по RCW 21.20.040(3): «transact business in this state as an investment adviser» без
регистрации незаконно; де-минимис — меньше шести клиентов-резидентов за 12 мес. при отсутствии места
деятельности в штате — массовому сервису не подходит. Исключение (d) для издателей не работает: оно снято,
если издание «consist[s] of the rendering of advice on the basis of the specific investment situation of each
client», а мы персонализированы. Исключение (3)(e) отсылает к **изъятиям** из § 202(a)(11) (банки, юристы,
издатели …), а не к «не подпадающим под определение» — толкования DFI на этот счёт в заходе не найдено.
**Инженерный вывод:** в продукте, доступном резидентам Вашингтона, **нельзя называть себя «financial
planner» / «financial planning»** — ни в интерфейсе, ни в маркетинге, ни в App Store. Функция при этом не
меняется: по функции (без securities) мы вне первой и второй веток, как федерально. Попадание — только через
титул, и снимается словарём.

**Источник 13.** North Carolina, G.S. 78C-2(1) (Investment Advisers Act of North Carolina), ncleg.gov/enactedlegislation/statutes/html/bychapter/chapter_78c.html —
прямой `curl` **403** (4 545 б), через `r.jina.ai` **HTTP 200, 90 964 б**, 16.09.2026. Норма закона штата.

> **(1) "Investment adviser"** means any person who, for compensation, engages in the business of advising
> others … as to the value of securities or as to the advisability of investing in, purchasing, or selling
> securities, or who, for compensation and as part of a regular business, issues or promulgates analyses or
> reports concerning securities. "Investment adviser" also includes financial planners and other persons who,
> as an integral component of other financially related services, provide the foregoing investment advisory
> services to others for compensation and as a part of a business or who hold themselves out as providing the
> foregoing investment advisory services to others for compensation. "Investment adviser" does not include: …

**Выжимка.** Северная Каролина — типичный штат модели 1986/2002: фразы «holds himself out as a financial
planner» **нет**; планировщик попадает только через «**the foregoing** investment advisory services» (т. е.
по securities). Контрольный пример того, что Вашингтон — отступление от модели, а не норма.

**Источник 14.** Beach Street Legal LLC, «When Does a Financial Planner Need to Register as an Investment
Adviser?», 01.02.2018, beachstreetlegal.com/when-does-a-financial-planner-need-to-register-as-an-investment-adviser/ —
через `r.jina.ai` **HTTP 200, 8 475 б**, 16.09.2026. Комментарий юрфирмы; содержит цитату **Official Comment
No. 15 к USA 1956 (в ред. NASAA 1986)** — первоисточник комментария в заходе снять не удалось (см. ниже).

> NASAA adopted this clarifying amendment to include financial planners in 1986, largely in response to
> Investment Advisers Act Release No. 770 (the predecessor to Release No. 1092). However, Comment No. 15 to the
> Uniform Securities Act goes on to say that
> > The provision defining an "investment adviser" to include financial planners […] **should not be construed
> > to mean that all financial planners fall within the definition by virtue of their designation as "financial
> > planners." Financial planners rendering advice exclusively in such nonsecurities areas as insurance and budget
> > management, for example, would not be covered by the definition. However, persons offering "total financial
> > planning" would be holding themselves out as providing investment advisory services. For similar reasons, the
> > drafters thought it inappropriate to define an "investment adviser" as "a person who holds himself out as a
> > financial planner.**"

**Выжимка.** Разработчики модели **сознательно отказались** от формулы, которую затем принял Вашингтон.
Для нас две вещи: (1) «budget management» прямо назван вне определения — наш базовый функционал;
(2) 🔴 «**total financial planning**» = holding out как инвестсоветник — ещё одна запрещённая формулировка
в словарь продукта («comprehensive / holistic / total financial planning»).

**Источник 15 (первоисточник к 14).** NASAA, «Uniform Securities Act (1956), as amended» с комментариями,
PDF 57 стр., `r.jina.ai/http://www.nasaa.org/wp-content/uploads/2011/08/UniformSecuritesAct1956withcomments.pdf` —
**HTTP 200, 229 875 б**, 16.09.2026 (прямой `curl` к nasaa.org — 403). Модельный закон + официальный
комментарий разработчиков (NASAA).

> **§ 401(f)** "Investment adviser" means any person who, for compensation, engages in the business of advising
> others … as to the value of securities or as to the advisability of investing in, purchasing, or selling
> securities, or who, for compensation and as a part of a regular business, issues or promulgates analyses or
> reports concerning securities. "Investment adviser" also includes financial planners and other persons who, as
> an integral component of other financially related services, provide the foregoing investment advisory services
> to others for compensation and as part of a business or who hold themselves out as providing the foregoing
> investment advisory services to others for compensation. …
>
> **Comment .15** The clarifying amendment [in Section 401(f)] … was largely patterned after the language found in
> SEC Release No. IA-770 of August 13, 1981. The drafters feel that any person in the business of providing advice
> or issuing reports or analyses regarding securities for compensation is an investment adviser. … **The provision
> defining an "investment adviser" to include financial planners … should not be construed to mean that all
> financial planners fall within the definition by virtue of their designation as "financial planners." Financial
> planners rendering advice exclusively in such non-securities areas as insurance and budget management, for
> example, would not be covered by the definition. However, persons offering "total financial planning" would be
> holding themselves out as providing investment advisory services. For similar reasons, the drafters thought it
> inappropriate to define an "investment adviser" as "a person who holds himself out as a financial planner."** A
> definition so worded would cover persons who, while not rendering investment advice, sell insurance and other
> non-securities financial products as "financial planners." Extending the "investment adviser" definition to
> those persons would possibly involve an incursion on the regulatory jurisdiction of state regulators other than
> the state securities administrator. **It should be noted, however, that use of the term "financial planner" by a
> person engaged in product sales only without disclosing that he or she is merely a salesperson may constitute a
> deceptive practice that should be addressed by state financial services and consumer protection agencies.**
> … For purposes of the exclusions in Sections 401(f)(3) and 401(f)(4), financial planners and others who hold
> themselves out as providing investment advisory services for compensation may not claim that the services
> rendered are "solely incidental" to another activity.

**Выжимка.** Цитата Beach Street Legal сверена с первоисточником — совпадает. Вашингтон прямо принял формулу,
которую NASAA назвала неуместной. Последняя фраза комментария — второй, не-регистрационный риск: титул
«financial planner» у того, кто на деле продаёт продукты (для нас — партнёрская выдача), может быть deceptive
practice по законам штатов о защите потребителей.

**Источник 16.** 🔴 Washington, **RCW 21.20.040** (действующая редакция; история «[2016 c 61 s 1; 2002 c 65 s 3; …]»),
app.leg.wa.gov/RCW/default.aspx?cite=21.20.040 — прямой `curl`, **HTTP 200, 114 370 б**, 16.09.2026. Норма закона.

> (3) It is unlawful for any person to transact business in this state as an investment adviser or investment
> adviser representative unless: (a) The person is so registered or exempt from registration under this chapter;
> (b) the person has no place of business in this state and … (ii) during the preceding twelve-month period the
> person has had fewer than six clients who are residents of this state …; (c) …; (d) the person is a federal
> covered adviser and … complied with … RCW 21.20.050; or (e) the person is excepted from the definition of
> investment adviser under section 202(a)(11) of the Investment Advisers Act of 1940.
> **(4) It is unlawful for any person, other than a federal covered adviser, to hold himself or herself out as, or
> otherwise represent that he or she is a "financial planner," "investment counselor," or other similar term, as
> may be specified in rules adopted by the director, unless the person is registered as an investment adviser or
> investment adviser representative, is exempt from registration as an investment adviser or investment adviser
> representative under RCW 21.20.040, or is excluded from the definition of investment adviser under RCW 21.20.005.**

**Источник 17.** Washington Administrative Code **WAC 460-24A-040** «Use of certain terms deemed similar to
"financial planner" or "investment counselor"», app.leg.wa.gov/WAC/default.aspx?cite=460-24A-040 — прямой `curl`,
**HTTP 200, 111 108 б**, 16.09.2026. Правило регулятора (DFI Securities Division); ред. WSR 19-03-133, eff. 18.02.2019.

> (1) For the purposes of RCW 21.20.040(4), use of any term, or abbreviation for a term, including the word
> "financial planner" or the word "investment counselor" is considered the same as the use of either of those
> terms alone.
> (2) For the purposes of RCW 21.20.040(4), terms that are deemed similar to "financial planner" and "investment
> counselor" include, but are not limited to, the following: **(a) Financial consultant; (b) Investment consultant;
> (c) Money manager; (d) Investment manager; (e) Investment planner;** (f) Chartered financial consultant or its
> abbreviation ChFC; (g) Certified financial planner or its abbreviation CFP®; or **(h) Any combination of terms
> similar to the above if used in a manner that implies to the general public that the individual or entity using
> the terms is in the business of providing investment advisory or financial planning services.**

**Источник 18.** **WAC 460-24A-045** «Holding out as a financial planner», app.leg.wa.gov/WAC/default.aspx?cite=460-24A-045 —
прямой `curl`, **HTTP 200, 112 652 б**, 16.09.2026. Правило регулятора; ред. WSR 19-03-133, eff. 18.02.2019.

> If you use a term deemed similar to "financial planner" or "investment counselor" under WAC 460-24A-040(2), you
> will not be considered to be holding yourself out as a financial planner for purposes of RCW 21.20.005 and
> 21.20.040 under the following circumstances:
> (1) You are not in the business of providing advice relating to the purchase or sale of securities, and would
> not, but for your use of such a term, be an investment adviser required to register pursuant to RCW 21.20.040; and
> (2) You do not directly or indirectly receive a fee for providing investment advice. …; and
> (3) You deliver to every customer, **at least forty-eight hours before accepting any compensation**, including
> commissions from the sale of any investment product, a written disclosure including the following information:
> (a) You are not registered as an investment adviser or investment adviser representative in the state of
> Washington; **(b) You are not authorized to provide financial planning or investment advisory services and do not
> provide such services;** and (c) A brief description of your business which description must include a statement
> of the kind of products offered or services provided … and of the basis on which you are compensated …; and
> (4) You have each customer to whom a disclosure described in subsection (3) … is given **sign a written dated
> acknowledgment of receipt** of the disclosure; and
> (5) You retain the executed acknowledgments … but in no case for less than three years from date of execution …; and
> (6) If you received compensation from the customer on more than one occasion, you need give the customer the
> disclosure … only on the first occasion unless the information in the disclosure becomes inaccurate …

Попутно (контекст, не норма): WSR 08-09-126 (DFI, proposed rules, 22.04.2008; lawfilesext.leg.wa.gov, прямой
`curl` 200, 13 458 б) — цель поправок: «a person who uses a term or abbreviation thereof, **or engages in any
conduct, that would lead a reasonable person to believe** that the person is holding himself or herself out as a
"financial planner" … is therefore subject to registration as an investment adviser»; HB 2885-S (1999–2000,
digest, 200, 6 983 б) — законопроект о членстве в организациях с «financial planner» в названии.

**Выжимка (Вашингтон, окончательно).** Механизм двухслойный: (а) титул делает лицом «investment adviser»
(RCW 21.20.005(8), третья фраза) → нужна регистрация (21.20.040(3)); (б) отдельный запрет титула без
регистрации (21.20.040(4)). Перечень титулов — открытый и широкий: **«money manager», «financial consultant»,
«investment planner»** и любая комбинация, создающая впечатление «financial planning services». Безопасная гавань
WAC 460-24A-045 доступна тем, кто не советует о securities (это мы), но требует письменного раскрытия **за 48 часов
до любой оплаты** с подписью клиента и хранением 3 года, причём само раскрытие обязано сказать «**не оказываем
услуг финансового планирования**» — то есть гавань несовместима с маркетингом «financial planning». Для
онлайн-подписки выполнимость «written dated acknowledgment» электронной подписью текстом правила не решена.
🔴 **Ответ по штату: регистрация НЕ нужна, пока мы не используем титулы из WAC 460-24A-040 (включая «money
manager») и не создаём впечатления «financial planning services». С титулом — нужна (или гавань 045 с её
процедурой).** Толкований DFI, прямо применённых к приложениям/SaaS, в заходе не найдено.

**Источник 19.** 🔴 Maryland Securities Act, **Md. Code, Corps. & Ass'ns § 11-101(i)** (Justia, «2025 Maryland Statutes»),
`r.jina.ai/https://law.justia.com/codes/maryland/corporations-and-associations/title-11/subtitle-1/section-11-101/` —
**HTTP 200, 10 312 б**, 16.09.2026. (Официальный mgaleg.maryland.gov через прокси — 200, 17 299 б, но текст статьи
не отрендерен, только оболочка сайта.) Норма закона штата; сверка с официальным сайтом не выполнена.

> **(i)(1) "Investment adviser" means a person who, for compensation:**
> (i) Engages in the business of advising others … as to the value of securities or as to the advisability of
> investing in, purchasing, or selling securities, or who, for compensation and as a part of a regular business,
> issues or promulgates analyses or reports concerning securities; **or**
> (ii) **1. Provides or offers to provide, directly or indirectly, financial and investment counseling or advice, on
> a group or individual basis;**
> **2. Gathers information relating to investments, establishes financial goals and objectives, processes and
> analyzes the information gathered, and recommends a financial plan;** or
> **3. Holds out as an investment adviser in any way, including indicating by advertisement, card, or letterhead,
> or in any other manner indicates that the person is, a financial or investment "planner", "counselor",
> "consultant", or any other similar type of adviser or consultant.**
> (2) "Investment adviser" does not include: (i) An investment adviser representative; (ii) A bank, savings
> institution, or trust company; (iii) A lawyer, certified public accountant, engineer, insurance producer, or
> teacher whose performance of investment advisory services is solely incidental … ; (iv) A broker-dealer … ;
> **(v) A publisher of any bona fide newspaper, news column, newsletter, news magazine, or business or financial
> publication or service, whether communicated in hard copy form, or by electronic means, or otherwise, that does not
> consist of the rendering of advice on the basis of the specific investment situation of each client;**
> (vi) A federal covered adviser; or (vii) Any other person not within the intent of this subsection as the
> Commissioner by rule or order designates.

**Выжимка (Мэриленд).** 🔴 **Самый широкий из найденных штатов — и он ловит нас не только титулом, но и
функцией.** Ветка (ii) — альтернативная к securities-ветке (i) (соединитель «or») и слова «securities» не
содержит. Три самостоятельных триггера, каждый — «for compensation»:
- (ii)1 — «financial **and** investment counseling or advice». Союз «and» даёт довод, что нужен и финансовый,
  и инвестиционный совет вместе; у нас инвестиционного совета нет. Довод текстовый, толкования не добыто.
- (ii)2 — **описание процесса финпланирования почти один в один с нашим конвейером**: собрать информацию, задать
  финансовые цели, обработать и проанализировать, рекомендовать финансовый план. Единственная опора против —
  слова «information **relating to investments**». Если вклады/накопительные счета/резерв считать «investments»
  в бытовом смысле — FINPILOT попадает. Толкования Maryland Securities Division в заходе не найдено.
- (ii)3 — титул: «financial … "planner", "counselor", "consultant", **or any other similar type of adviser**».
  Шире Вашингтона: ловит и «financial adviser», и «financial coach» по «similar type».

**Источник 20.** Colorado Securities Act, **C.R.S. § 11-51-201(9.5)** (Justia),
`r.jina.ai/https://law.justia.com/codes/colorado/title-11/securities/article-51/part-2/section-11-51-201/` —
**HTTP 200, 22 732 б**, 16.09.2026. Норма закона штата (по Justia, без сверки с официальным сайтом).

> (9.5)(a)(I) "Investment adviser" means any person who, for compensation, engages in the business of advising
> others … as to the value of securities or as to the advisability of investing in, purchasing, or selling
> securities, or who, for compensation and as part of a regular business, issues or promulgates analyses or reports
> concerning securities.
> (II) "Investment adviser" includes financial planners or other persons who, as an integral component of other
> financially related services, provide investment advisory services to others for compensation and as a part of a
> business or who hold themselves out as providing investment advisory services to others for compensation.
> (b) "Investment adviser" does not include: (I) A federal covered adviser; (II) A publisher of a bona fide
> newspaper, magazine, or business or financial publication with a regular paid circulation; …

**Выжимка (Колорадо).** Модельная формула 1986 — отдельного титульного триггера нет; «investment advisory services»
по контексту (I) — о securities. Колорадо для нас по регистрации нейтрален (по тексту определения).

**Источник 21.** Maryland, **§ 11-401(b)** «Transaction of business by unregistered person unlawful» (Justia, 2025),
`r.jina.ai/https://law.justia.com/codes/maryland/corporations-and-associations/title-11/subtitle-4/section-11-401/` —
**HTTP 200, 16 761 б**, 16.09.2026. Норма закона штата.

> (b) A person may not transact business in this State as an investment adviser or as an investment adviser
> representative unless: (1) The person is registered …; (2) The person's only clients in this State are investment
> companies … or insurance companies; or (3) The person has no place of business in this State, and: (i) The
> person's only clients in this State are [институциональные] …; or **(ii) During the preceding 12-month period, the
> person has had no more than five clients who: 1. Are residents of the State; and 2. Are not the types of clients
> described in item (i) …**
> (e) By rule or order, the Commissioner may modify the requirements of this section or exempt any … investment
> adviser … if the Commissioner determines that: (1) Compliance … is not necessary or appropriate for the protection
> of investors; and (2) The exemption is consistent with the public interest …

**Выжимка.** Де-минимис — не более пяти клиентов-резидентов за 12 месяцев без места деятельности в штате;
массовый сервис его превышает с первой недели. Попадание под § 11-101(i)(1)(ii) означает **регистрацию в
Мэриленде** (федеральная регистрация недоступна: у нас нет ни securities-совета, ни активов под управлением,
а «federal covered adviser» — это лицо, зарегистрированное по § 203 Advisers Act). Выход (e) — индивидуальное
изъятие по приказу Commissioner, т. е. no-action/exemptive запрос в Maryland Securities Division.

**Источник 22.** Maryland, **COMAR 02.02.05.20** «Exemption from the Maryland Securities Act, … § 11-101(i)(2), … for
Certain Individuals», `r.jina.ai/https://www.law.cornell.edu/regulations/maryland/COMAR-02-02-05-20` — **HTTP 200,
6 422 б**, 16.09.2026. Правило регулятора (Maryland Division of Securities); принято 07.12.1992 (19:24 Md. R. 2125).
Ссылки внутри правила — на старую нумерацию § 11-101(h), ныне (i).

> A. An individual broker-dealer agent who: (1) … holds out to the public, as set forth in … § 11-101(h)(1)(ii)3 …,
> **by use of the title "financial consultant", "financial adviser", or similar title or designation**; (2) Does not
> in any other manner hold out as an investment adviser or representative; … (5) Has passed … the Series 7 examination …
> B. An individual insurance producer who: (1) **Falls within the definition of "investment adviser" … solely by
> incident of holding out to the public … by use of the registered trademark "ChFC", "Chartered Financial
> Consultant", "NAIFA" …**
> D. An individual who falls within the definition of "investment adviser" … solely by incident of holding out to the
> public … but who: (1) Uses the registered trademark "ChFC", "Chartered Financial Consultant", "CFP", or "Certified
> Financial Planner" solely in the context of: (a) Acting as a teacher or researcher …, (b) Employment in the employee
> benefits … unit of a business entity that is not an investment adviser, or (c) Employment by an agency of …
> government; …

**Выжимка.** Сам регулятор Мэриленда исходит из того, что **одного титула достаточно**, чтобы лицо «falls within the
definition of investment adviser» — иначе этих изъятий не понадобилось бы (тот же довод «от противного», что в Г21
по CCD II Art. 16(6)). Изъятия выданы узким группам лиц (агенты брокеров, страховые агенты, преподаватели); для
сервиса-приложения изъятия нет. Титул «**financial adviser**» прямо назван.
Доктрина: John A. Gray, «Accountants' Obligations under Maryland's New Investment Adviser Law», 22 U. Balt. L.F. (1991)
— закон принят весной 1989, вступал в силу 01.07.1989 и 01.10.1990 (по сниппету выдачи). Текст **не добыт**:
прямой `curl` 403, `WebFetch` 403, `r.jina.ai` 200/228 б — Cloudflare «Just a moment…».

### Г26.4 SEC no-action letters — в оригинале

**Источник 23.** SEC Division of Investment Management, **RDM Infodustries, Inc.**, no-action letter, 25.03.1996
(Our Ref. No. 96-100; Eileen M. Smiley, Senior Counsel), sec.gov/divisions/investment/noaction/1996/rfminfodustries032596.pdf —
через `r.jina.ai` **HTTP 200, 7 102 б, PDF 4 стр.** (OCR скана, опечатки оригинального распознавания сохранены
частично; исправлены только очевидные), 16.09.2026. **Позиция staff, не Комиссии.**

> … Section 202(a)(11), in pertinent part, defines the term "investment adviser" to mean any person who, for
> compensation, engages in the business of advising others as to the value of securities or as to the advisability of
> investing in, purchasing, or selling securities, or who issues or promulgates analyses or reports concerning
> securities. As we discussed in our telephone conversation on March 8, 1996, **your letter does not present
> sufficient facts upon which to make a determination whether RDM must register under the Advisers Act.** …
> The staff of the Division of Investment Management, in a number of letters, has expressed its views regarding the
> circumstances when the presentation of securities data or information constitutes an analysis or report for
> purposes of section 202(a)(11). **The staff has taken the position that information relating to securities does not
> constitute an analysis or report if: (1) the information is readily available to the public in its raw state;
> (2) the categories of information presented are not highly selective; and (3) the information is not organized or
> presented in a manner that suggests the purchase, holding, or sale of any security or securities.** See, e.g.,
> Missouri Innovation Center, Inc. (pub. avail. Oct. 17, 1995); Datastream International (pub. avail. Mar. 15, 1993);
> EJV Partners, L.P.; Univu System (pub. avail. Dec. 7, 1992). …
> Finally, the Division …, having repeatedly expressed its views …, **will no longer respond to such requests for
> interpretative or no-action letters in this area unless they present novel or unusual issues.** …
> [fn. 2] … See also Media General Financial Services, Inc. (pub. avail. July 20, 1992); Investex Investment Exchange,
> Inc. (pub. avail. Apr. 9, 1990); Charles Street Securities, Inc. (pub. avail. Feb. 27, 1987); Butcher & Singer, Inc.
> (pub. avail. Jan. 2, 1987).
> [Запрос RDM: «provide raw, unbiased financial data from Latin American corporations to stockbrokers and securities
> dealers».]

**Выжимка.** 🟡 **Письмо — не отказ в действиях, а отказ определиться** («insufficient facts») с отсылкой к
трёхэлементному тесту для **данных о ценных бумагах**. Плейз цитирует его в поддержку тезиса «selective list of
securities is advice» — в оригинале этого нет дословно, есть обратная сторона теста (не highly selective).
К нам письмо по предмету не относится (у нас нет данных о securities); годится только как иллюстрация: staff
закрыл тему для типовых запросов с 1996 г., значит новый no-action по «не-securities сервису» — возможен лишь как
«novel or unusual issue».

**Источник 24.** SEC Division of Investment Management, письмо **U.S. Department of Labor**, 22.02.1996
(Jack W. Murphy, Associate Director (Chief Counsel), адресат Olena Berg, PWBA), sec.gov/divisions/investment/noaction/1996/usdol022296.pdf —
через `r.jina.ai` **HTTP 200, 3 494 б, PDF 2 стр.** (OCR), 16.09.2026. Позиция staff.

> … In our letter to you dated December 5, 1995, …, we stated that an employer that provides investment-related
> information to its employees who participate in the employer's plan would not, as a result, be in the business of
> providing investment advice and therefore would not be an "investment adviser" as defined in the Advisers Act. …
> **our position is based on the unique nature of the employment relationship. Consequently, our position is not
> intended to address whether a third-party service provider meets the definition of investment adviser** under the
> Advisers Act. Whether such a person meets the definition … continues to depend on the application of all the factors
> set out in Section 202(a)(11), including the type of information provided.[1] We note, however, that as a general
> matter, **information that simply describes or explains the various investment options available through a plan,
> without including any analysis or recommendation with respect to those options, would not constitute "investment
> advice"** as that term is used in the Advisers Act.
> [1] Investment Advisers Act Release No. 1092 (October 8, 1987) provides the staff's views regarding the scope of
> Section 202(a)(11) …

**Выжимка.** Для нас — только подтверждение уже известного: сторонний сервис оценивается по IA-1092 и по типу
информации; «analysis or recommendation» по инвестиционным опциям — совет. Работодательский (B2B-wellness)
«щит» из письма 05.12.1995 на стороннего поставщика **не распространяется** — это важно для канала продаж через
работодателей: работодатель защищён, мы — нет.

**Индекс писем.** Страница SEC «Division of Investment Management Staff No-Action and Interpretive Letters»
(через `r.jina.ai`, **HTTP 200, 577 924 б**, 16.09.2026), разделы «Investment Advisers Act Status» (20 писем,
1993–2009) и «… – Publishers» (6 писем): **ни одного письма про budgeting, debt, credit counseling или financial
planning software** по заголовкам. **Robert R. Champion (22.09.1986) в индексе отсутствует** — письма до ~1993
на sec.gov в большинстве не выложены; текст не добыт (каналы: `WebSearch` ×1 — только цитаты у Plaze/Proskauer;
индекс SEC; PLI-глава Kirsch — `curl` 200/12 374 б, но HTML-заглушка, не PDF).

### Г26.3 CCD II Art. 3(17) — национальная транспозиция (Германия, дословно)

**Источник 25.** Gesetz zur Umsetzung der Richtlinie (EU) 2023/2225 … vom 12. Mai 2026, **BGBl. 2026 I Nr. 139**
(18.05.2026), официальный PDF recht.bund.de/bgbl/1/2026/139/regelungstext.pdf — прямой `curl`, **HTTP 200, 921 242 б**
(тот же размер, что в Г16 12.09.2026), `pdftotext`, 16.09.2026. Норма закона (вступает 20.11.2026, Art. 16(1)).
В Г16 акт найден, но статьи о Beratung не цитировались — ниже новое.

Art. 1 Nr. 32 (BGB, § 511 в новой редакции):
> „§ 511 **Beratungsleistungen bei Verbraucherdarlehensverträgen**".
> „(1) Der Darlehensgeber hat den Darlehensnehmer zu informieren, ob für ihn **individuelle Empfehlungen zu einem oder
> mehreren Geschäften, die im Zusammenhang mit einem Verbraucherdarlehensvertrag stehen (Beratungsleistungen)**,
> erbracht werden oder erbracht werden können. Bevor der Darlehensgeber für den Darlehensnehmer solche
> Beratungsleistungen erbringt, hat er den Darlehensnehmer über die sich aus Artikel 247 § 18 des
> Einführungsgesetzes zum Bürgerlichen Gesetzbuche ergebenden Einzelheiten in der dort vorgesehenen Form zu
> informieren."
> „(3) Der Darlehensgeber hat dem Darlehensnehmer auf Grund der Prüfung gemäß Absatz 2 in dessen bestem Interesse ein
> geeignetes oder mehrere geeignete Produkte zu empfehlen oder ihn darauf hinzuweisen, dass er kein Produkt empfehlen
> kann. … (4) Der Darlehensgeber ist verpflichtet, den Darlehensnehmer zu warnen, wenn ein Verbraucherdarlehensvertrag
> unter Berücksichtigung der finanziellen Situation des Darlehensnehmers möglicherweise ein spezifisches Risiko für
> ihn birgt."

Art. 7 Nr. 6 (GewO, новый § 34k «Darlehensvermittler»):
> „(1) Wer gewerbsmäßig gegen eine Vergütung, die aus einer Geldzahlung oder einem sonstigen vereinbarten
> wirtschaftlichen Vorteil bestehen kann, den Abschluss von Allgemein-Verbraucherdarlehensverträgen nach § 491
> Absatz 2 des Bürgerlichen Gesetzbuchs oder von Finanzierungshilfen nach § 506 Absatz 1 …, mit Ausnahme von Verträgen
> im Sinne des § 34i Absatz 1 Satz 1, vermitteln oder die Gelegenheit zum Abschluss solcher Verträge nachweisen **oder
> Dritte zu solchen Verträgen beraten** oder in anderer Weise beim Abschluss eines solchen Vertrages behilflich sein
> will (Darlehensvermittler), **bedarf nach Maßgabe der folgenden Bestimmungen der Erlaubnis der zuständigen
> Behörde.**"
> „(3) Die Erlaubnis nach Absatz 1 ist zu versagen, wenn … 3. der Antragsteller nicht durch eine vor der Industrie- und
> Handelskammer erfolgreich abgelegte Prüfung nachweist, dass er die für die Vermittlung von **oder Beratung zu**
> Allgemein-Verbraucherdarlehensverträgen … notwendige Sachkunde … besitzt."
> „(4) Einer Erlaubnis nach Absatz 1 bedürfen nicht: 1. Kreditinstitute …, 2. Kapitalverwaltungsgesellschaften …,
> 3. Gewerbetreibende, die als Kleinstunternehmen oder KMU … gelten und die lediglich zur Finanzierung der von ihnen
> abgeschlossenen Warenverkäufe oder zu erbringenden Dienstleistungen eine Tätigkeit nach Absatz 1 ausüben."
> „(5) Gewerbetreibende nach Absatz 1, die eine unabhängige Beratung anbieten oder als unabhängige Berater auftreten
> (**Honorar-Darlehensberater**), 1. müssen für ihre Empfehlung für oder gegen einen Allgemein-Verbraucherdarlehensvertrag
> … eine ausreichende Zahl von auf dem Markt verfügbaren Verträgen einbeziehen und 2. dürfen vom Darlehensgeber für ihre
> Beratungsleistung keine Zuwendungen annehmen …"
> „(8) … in das Register nach § 11a Absatz 1 Satz 1 eintragen zu lassen …"

**Выжимка (Германия).** 🟡 **Подтверждение Г21 частичное.** Германия переносит Art. 3(17) дословно
(«individuelle Empfehlungen zu einem oder mehreren Geschäften, die im Zusammenhang mit einem
Verbraucherdarlehensvertrag stehen»), а допуск к «Beratung» даёт через **лицензию § 34k GewO** (экзамен в IHK,
регистр, для независимых — статус Honorar-Darlehensberater). Но формулировка § 34k(1) привязана к **заключению**
договора («den Abschluss … vermitteln … oder Dritte zu solchen Verträgen beraten … beim Abschluss … behilflich
sein»). Совет «какой из уже действующих кредитов гасить первым» текстом § 34k(1) **прямо не назван**: довод «за нас» —
вся конструкция нормы про заключение; довод «против» — «Dritte zu solchen Verträgen beraten» стоит отдельным
членом перечня и не ограничен словом «Abschluss». Вывод Г21 по уровню директивы это не отменяет, а по
Германии оставляет открытым: **лицензионный крючок для «совета по существующему долгу» в немецком тексте
неоднозначен**. Разъяснений BMJV/BaFin/DIHK в заходе не найдено.

**Не добыто по п. 3:** Q&A Еврокомиссии и EBA по Art. 3(17) — не найдены (`WebSearch` ×2: выдача — текст директивы,
LEGISSUM, блоги PwC, Deloitte, recent-ecl; официальных толкований нет). Позиции AMF (Франция) и Banca d'Italia —
не искались отдельно (бюджет). Статья «Debt Counseling from the Directive No. 2023/2225 … and Perspectives for
Transposition» (ResearchGate) — не открывалась. Ирландия (CCPC) и Италия (Legal500) — уже в Г2.2 выше.

## ИТОГ Г26

### Таблица по пунктам

| № | Пункт | Статус | Норма-основание | Что меняет для красной линии |
|---|---|---|---|---|
| 1 | Штаты США: financial planner без ценных бумаг | **добыто; гипотеза подтверждена ЧАСТИЧНО — для двух штатов** | USA 1956 § 401(f) + Comment .15 (NASAA); USA 2002 § 102(15), § 403; Seligman 81 Wash. U. L.Q. 243; **RCW 21.20.005(8), 21.20.040(3)–(4); WAC 460-24A-040, -045 (Вашингтон)**; **Md. Code Corps. & Ass'ns § 11-101(i)(1)(ii), § 11-401(b); COMAR 02.02.05.20 (Мэриленд)**; NRS 628A.010–.040 (Невада); G.S. 78C-2(1) (N. Carolina); C.R.S. 11-51-201(9.5) (Colorado); GAO-11-235 | 🟢 Модельный закон (оба издания) и типовые штаты (NC, CO) титул «financial planner» без securities **не ловят** — разработчики прямо отказались от такой формулы, «budget management» назван вне определения. 🔴 **Вашингтон** ловит **одним титулом** (перечень: financial planner, financial consultant, **money manager**, investment planner и любые комбинации, намекающие на «financial planning services»). 🔴 **Мэриленд** ловит титулом («financial … planner / counselor / consultant or any other similar type of adviser») **и, вероятно, функцией** — (ii)2 описывает сбор данных → цели → анализ → «recommends a financial plan». 🟠 **Невада** регистрации не требует, но накладывает фидуциарную обязанность, ответственность за gross negligence и **E&O/bond от $1 млн** на того, кто советует «upon provision for income to be needed in the future». Новые запреты словаря: «financial planner/planning», «money manager», «financial consultant/adviser/counselor», «total/comprehensive financial planning» |
| 2 | s. 418 FSMA и PERG 2.4 | **добыто дословно** | FSMA s. 418(1), (4), (5), (6); s. 19; s. 21(1)–(3); FPO 2005 Sch. 1 para. 5B; PERG 2.3.2G–2.3.3G, 2.4.1G–2.4.6G, 2.9.15G–2.9.17G | 🔴 **s. 418 — норма-расширитель, защитой быть не может**; наш случай решается общим смыслом «in the UK» в s. 19, и FCA (guidance) прямо называет интернет примером деятельности в UK без присутствия (PERG 2.4.6G). Исключений overseas persons для debt counselling нет (PERG 2.9.15G — третье подтверждение). Business test выполняется подпиской. Сверх этого — **s. 21(3)**: debt counselling — controlled activity (FPO Sch. 1 para. 5B), реклама, «capable of having an effect in the UK», — отдельное нарушение |
| 3 | Толкования CCD II Art. 3(17) | **частично** | BGBl. 2026 I Nr. 139: § 511 BGB n.F., § 34k GewO | Германия переносит Art. 3(17) дословно и лицензирует «Beratung» через § 34k GewO, но текст лицензии привязан к **заключению** договора — для совета по **существующему** долгу немецкий крючок неоднозначен. Толкований Комиссии/EBA/BaFin/AMF/Banca d'Italia **не найдено**. Вывод Г21 (на уровне директивы — внутри) **не опровергнут** |
| 4 | SEC no-action letters в оригинале | **частично (2 письма)** | RDM Infodustries (25.03.1996); letter to U.S. DOL (22.02.1996); индекс SEC IM | Ни одного письма по budgeting/debt/planning software в индексе SEC нет. RDM — отказ определиться + тест для данных о securities (у Plaze процитирован шире оригинала). DOL-1996: «щит» работодателя **на стороннего поставщика не распространяется**. **Champion (1986) не добыт** — в индексе SEC отсутствует |

### 🔴 Прямой ответ: нужна ли нам регистрация хоть в одном штате США?

**Да — в двух штатах условно, и в одном из них, возможно, безусловно.**
- **Вашингтон — да, если мы используем титул** «financial planner» или сходный (включая «money manager»,
  «financial consultant», любую комбинацию, создающую впечатление «financial planning services»):
  RCW 21.20.005(8) делает такое лицо investment adviser, 21.20.040(3)–(4) требует регистрации, де-минимис —
  меньше шести клиентов-резидентов. **Без такого титула — нет** (функционально мы вне первой и второй веток).
  Альтернатива регистрации — гавань WAC 460-24A-045, но её обязательное раскрытие «не оказываем услуг
  финансового планирования» с подписью за 48 часов до оплаты несовместимо с позиционированием «financial planning».
- **Мэриленд — да при титуле** (§ 11-101(i)(1)(ii)3, регулятор сам исходит из «достаточно титула» — COMAR
  02.02.05.20), и **возможно — даже без титула**: ветка (ii)2 описывает процесс финпланирования без слова
  «securities», единственная опора против — «information relating to investments». Толкования Maryland Securities
  Division не найдено; при запуске на резидентов Мэриленда это **вопрос к местному юристу или exemptive-запрос
  по § 11-401(e)**, а не к словарю.
- **Невада — регистрации нет, но есть обязанности и $1 млн E&O/bond** (NRS 628A.040), если NRS 628A применима
  к автоматическому сервису и иностранному поставщику (не решено).
- Во всех остальных просмотренных (NC, CO, модельный закон 1956/2002) — **нет**. Полного прохода по 50 штатам
  **не было**: кроме Вашингтона и Мэриленда могут существовать другие отступления от модели.

### 🔴 Прямой ответ: защищает ли нас s. 418 FSMA в UK?

**Нет.** s. 418 только **добавляет** случаи, когда деятельность считается осуществляемой в UK (UK-офис, UK-заведение,
AIF, крипто), и не содержит ни одного случая «не считается» (s. 418(1); PERG 2.4.3G: «extends the meaning»).
Для нас она нейтральна, а вопрос решается общим смыслом «in the United Kingdom» в s. 19, который FCA толкует
против нас: иностранец без места деятельности в UK может осуществлять деятельность в UK «by means of the
internet» (PERG 2.4.6G, guidance, не закон и не суд). Исключений для overseas persons по debt counselling нет,
business test выполнен, а s. 21(3) независимо ловит рекламу, «capable of having an effect in the UK».
**Единственная реальная защита по британскому долговому контуру — не вести деятельность в UK фактически:**
не принимать резидентов UK в долговой модуль, не таргетировать UK (валюта, кредиторы, реклама). Это вывод
из совокупности норм; судебного толкования интернет-случая в заходе не добыто.

### Что изменилось на общей карте

| Юрисдикция | Было после Г21 | Стало после Г26 |
|---|---|---|
| США, штаты | «не проверены» | 🟢 модельные штаты — вне; 🔴 **WA — внутри при титуле**; 🔴 **MD — внутри при титуле, возможно и по функции**; 🟠 **NV — фидуциарий + $1 млн E&O без регистрации** |
| UK, территориальность | «не исследована, последняя линия» | 🔴 **линии нет**: s. 418 не защищает, PERG 2.4.6G против нас, + s. 21(3) по рекламе |
| ЕС (DE) | «внутри по директиве» | без изменений; немецкий лицензионный текст (§ 34k GewO) для существующего долга неоднозначен |

### Что осталось неизвестным

1. Полный проход по 50 штатам на отступления от модели (титульные и функциональные ветки) — сделаны только
   WA, MD, NV, NC, CO, FL (по сниппету — без фразы о planner; первоисточник не открывался).
2. Толкование Maryland Securities Division к § 11-101(i)(1)(ii)2 («information relating to investments»);
   статья Gray, 22 U. Balt. L.F. (1991) — Cloudflare на всех трёх каналах.
3. Применимость NRS 628A к автоматическому сервису и к поставщику без присутствия в Неваде; применимость
   «transact business in this state» (WA, MD) к иностранному SaaS — толкований не найдено.
4. Выполнимость подписи «written dated acknowledgment» (WAC 460-24A-045(4)) электронно.
5. Судебная практика UK по s. 19 для интернет-поставщика (LexisNexis Practice Note платный, не открывался).
6. Q&A Еврокомиссии/EBA по Art. 3(17); позиции BaFin, AMF, Banca d'Italia; разъяснения BMJV/DIHK к § 34k GewO.
7. SEC no-action Robert R. Champion (1986) — нет в индексе SEC; нужен Westlaw/Lexis.
8. 🆕 Хвост: CFPB/UDAAP как возможный регулятор «household budgeting» сервиса (GAO-11-235) — не исследовался.

### Процесс — прозрачно

Тип запроса: **breadth-first**, 4 независимых под-вопроса. **Субагентов — ноль**: все пункты сняты вахтой
прямыми запросами (отступление от метода «минимум один субагент» — осознанное, ради правила «сырьё в файл после
каждого источника» и после сегодняшних падений агентов на лимите). Собственных `WebSearch` — 11. `WebFetch` — 1
(403). Запись в файл — **16 отдельных дописываний** по ходу, до итогового ответа. Каналы: прямой `curl`
(legislation.gov.uk, app.leg.wa.gov, uniformlaws.org, wustl.edu, recht.bund.de, lawfilesext.leg.wa.gov);
`r.jina.ai` (FCA Handbook, NRS, NASAA, GAO, ncleg, Justia, Cornell COMAR, sec.gov, dfi.wa.gov, Beach Street Legal,
Baker McKenzie). Не прошли: nasaa.org и ncleg.gov напрямую (403), gao.gov напрямую (403), scholarworks.law.ubalt.edu
(403 / Cloudflare через прокси), mgaleg.maryland.gov (оболочка без текста), buzer.de через прокси (145 б).
Exa отключена, Wayback не пробовался (429/503 весь день по вводной).


## ДОБОР Г27 (16.09.2026)

Батч Г27 очереди пробелов (COVERAGE_AUDIT_4 → Г27): право США на уровне штатов, территориальность,
CFPB/UDAAP, электронная подпись WA. Метод: breadth-first; вахта снимает первоисточники сама, запись в файл
после каждой группы штатов. Установленное в Г26 (WA, MD, NV, модельный закон, NC, CO) не переоткрывается.

### П1. Штаты — группа 1 (крупные рынки), первоисточники

Ключ к чтению: в модельном законе 1956 года после поправки NASAA 1986 года стоит фраза «also includes financial
planners and other persons who, as an integral component of other financially related services, provide **the
foregoing investment advisory services** … or who hold themselves out as providing **the foregoing** investment
advisory services». «Foregoing» = совет **по ценным бумагам**. Эта формула титулом «financial planner» НЕ ловит —
она ловит планировщика, который советует по securities. Отступление (как WA, MD) — только там, где титул или
«financial planning» связан с регулированием **без** слова securities.

**California** — Corp. Code § 25009 (Justia через r.jina.ai: прямой HTTP 403, прокси HTTP 200, 3 186 б, 16.09.2026;
https://law.justia.com/codes/california/code-corp/title-4/division-1/part-1/section-25009/). Дословно:
> «(b) "Investment adviser" also includes any person who uses the title "financial planner" **and** who, for compensation,
> engages in the business, whether principally or as part of another business, of advising others, either directly or
> through publications or writings, as to the value of securities or as to the advisability of investing in, purchasing
> or selling securities, or who, for compensation and as part of a regular business, publishes analyses or reports
> concerning securities. This subdivision does not apply to: … (2) an attorney at law, accountant, engineer, or teacher
> whose performance of these services is solely incidental to the practice of his or her profession, so long as these
> individuals do not use the title "financial planner;" …» (Amended by Stats. 1996, Ch. 631, eff. 01.01.1997)
Выжимка: титул упомянут, но **конъюнктивно** с советом по securities. Сам по себе титул не ловит. → **нет**.

**Minnesota** — Minn. Stat. § 45.026 «REGULATION OF BUSINESS OF FINANCIAL PLANNING» — **отдельный закон о
планировщиках, аналог NV 628A** (прямой curl, HTTP 200, 63 740 б, 16.09.2026; https://www.revisor.mn.gov/statutes/cite/45.026). Дословно:
> «Subd. 1 … (b) "Financial planner" means a person who, on advertisements, cards, signs, circulars, letterheads, or in
> another manner, indicates that the person is a "financial planner," "financial counselor," "financial adviser,"
> "investment counselor," "investment adviser," "financial consultant," or other similar designation, title, or
> combination is considered to be representing that the person is engaged in the business of financial planning.
> (c) "Advertisement" includes: (1) printed or published material, audiovisual material, and descriptive literature of a
> financial planner used in direct mail, newspapers, magazines, other periodicals, … (4) statements, written or oral, by a
> financial planner.
> Subd. 2. Fiduciary duty. Persons who represent that they are financial planners have a fiduciary duty to persons for
> whom services are performed for compensation. In an action for breach of fiduciary duty, a person may recover actual
> damages resulting from the breach, together with costs and disbursements.
> Subd. 3. Penalty. A financial planner is subject to section 45.027, subdivision 5.» (History: 1987 c 336 s 1)
Выжимка: регистрации нет; **титул** («financial adviser», «financial counselor», «financial consultant», «или сходный»)
→ фидуциарная обязанность перед платными клиентами + гражданский иск + санкции комиссара по § 45.027 subd. 5.
Ни слова о securities. → **только при титуле** (последствие — фидуциарий, не регистрация).

**Michigan** — MCL 451.2102a(e) (legislature.mi.gov через прокси: прямой 403, прокси HTTP 200, 9 121 б;
https://www.legislature.mi.gov/printDocument.aspx?objectName=mcl-451-2102a&version=txt). Дословно:
> «(e) "Investment adviser" means a person that, for compensation, engages in the business of advising others, either
> directly or through publications or writings, as to the value of securities or the advisability of investing in,
> purchasing, or selling securities … The term includes a financial planner or other person that, as an integral
> component of other financially related services, provides investment advice to others for compensation as part of a
> business or that holds itself out as providing investment advice to others for compensation.»
Выжимка: USA 2002 § 102(15) дословно; «investment advice» = по securities. → **нет**.

**Texas** — Gov't Code § 4001.059 (statutes.capitol.texas.gov: прямой HTTP 200, но SPA-оболочка 250 874 б без текста;
через прокси HTTP 200, 23 768 б; https://statutes.capitol.texas.gov/Docs/GV/htm/GV.4001.htm). Дословно:
> «Sec. 4001.059. INVESTMENT ADVISER. "Investment adviser" includes a person who, for compensation, engages in the
> business of advising another, either directly or through publications or writings, with respect to the value of
> securities or to the advisability of investing in, purchasing, or selling securities or a person who, for compensation
> and as part of a regular business, issues or adopts analyses or a report concerning securities, **as may be further
> defined by board rule**.» (Acts 2019, 86th Leg., H.B. 4171, eff. 01.01.2022)
Выжимка: слова planner нет; «further defined by board rule» — см. ниже проверку правил TSSB. → **нет** (по закону).

**Florida** — Fla. Stat. § 517.021(20) (leg.state.fl.us прямой curl, HTTP 200, 49 917 б, 16.09.2026;
http://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0500-0599/0517/Sections/0517.021.html). Дословно:
> «(20)(a) "Investment adviser" means a person, other than an associated person of an investment adviser or a federal
> covered adviser, that receives compensation, directly or indirectly, and engages for all or part of the person's time,
> directly or indirectly, or through publications or writings, in the business of advising others as to the value of
> securities or as to the advisability of investments in, purchasing of, or selling of securities.»
Выжимка: **сниппет Г26 подтверждён первоисточником** — ни planner, ни holding out в определении нет; во всём § 517.021
слово «planner» не встречается ни разу (0 совпадений). → **нет**.

**New York** — GBL § 359-eee(1)(a) (nysenate.gov через прокси: прямой 403, прокси HTTP 200, 8 987 б;
https://www.nysenate.gov/legislation/laws/GBS/359-EEE). Дословно:
> «(a) "Investment adviser" shall mean any person who, for compensation, engages in the business of advising members of
> the public, either directly or through publications or writings within or from the state of New York, as to the value
> of securities or as to the advisability of investing in, purchasing, or selling or holding securities, or who, for
> compensation and as a part of a regular business issues or promulgates analyses or reports concerning securities to
> members of the public within or from the state of New York.»
Выжимка: planner — 0 совпадений в секции. Территориальный признак «within or from the state of New York» (к П2). → **нет**.

**Illinois** — 815 ILCS 5/2.11 (ilga.gov через прокси, HTTP 200, 3 603 б;
https://www.ilga.gov/Documents/legislation/ilcs/documents/081500050K2.11.htm). Дословно:
> «"Investment adviser" means any person who, for compensation, engages in this State in the business of advising others
> … as to the value of securities or as to the advisability of investing in, purchasing, or selling securities … or any
> financial planner or other person who, as an integral component of other financially related services, provides
> investment advisory services to others for compensation and as part of a business, or who holds himself or herself out
> as providing investment advisory services to others for compensation»
Выжимка: формула 1986 года; «investment advisory services» — по securities. Территория: «engages in this State». → **нет**.

**Ohio** — ORC § 1707.01(X)(1) (codes.ohio.gov через прокси, HTTP 200, 34 411 б; https://codes.ohio.gov/ohio-revised-code/section-1707.01).
> «(X)(1) "Investment adviser" means any person who, for compensation, engages in the business of advising others, either
> directly or through publications or writings, as to the value of securities or as to the advisability of investing in,
> purchasing, or selling securities, or who, for compensation and as a part of regular business, issues or promulgates
> analyses or reports concerning securities.»
Выжимка: чистый 1956 без поправки 1986. → **нет**.

**Virginia** — Va. Code § 13.1-501 (law.lis.virginia.gov, прямой HTTP 200, 40 171 б; https://law.lis.virginia.gov/vacode/title13.1/chapter5/section13.1-501/).
> «"Investment advisor" … also includes financial planners and other persons who, as an integral component of other
> financially related services, provide the foregoing investment advisory services to others for compensation and as a
> part of a business or who hold themselves out as providing the foregoing investment advisory services to others for
> compensation.» → формула 1986, **нет**.

**Massachusetts** — M.G.L. c. 110A § 401(m) (malegislature.gov через прокси, HTTP 200, 12 277 б;
https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXV/Chapter110A/Section401).
> «''Investment adviser'' also includes financial planners and other persons who, as an integral component of other
> financially related services, provide the foregoing investment advisory services to others for compensation and as a
> part of a business or who hold themselves out as providing the foregoing investment advisory services to others for
> compensation.» → формула 1986, **нет**.

**New Jersey** — N.J.S.A. 49:3-49(g)(1) (Justia через прокси, HTTP 200, 19 614 б; https://law.justia.com/codes/new-jersey/title-49/section-49-3-49/).
> «(ii) any financial planner and other person who provides investment advisory services to others for compensation and
> as part of a business or who holds himself out as providing investment advisory services to others for compensation.»
Выжимка: без «integral component», но «investment advisory services» отсылает к (i) — securities. → **нет**.

**Georgia** — O.C.G.A. § 10-5-2 (Justia через прокси, HTTP 200, 59 603 б; https://law.justia.com/codes/georgia/title-10/chapter-5/article-1/section-10-5-2/).
> «The term includes a financial planner or other person that, as an integral component of other financially related
> services, provides investment advice to others for compensation as part of a business or that holds itself out as
> providing investment advice to others for compensation.» → USA 2002, **нет**.

### П1. Штаты — группа 2 (25 юрисдикций), первоисточники

Все сняты 16.09.2026. Ниже — **дословно операционная фраза** каждого определения (вводная часть везде одна:
«for compensation, engages in the business of advising others … as to the value of securities or [as to] the
advisability of investing in, purchasing, or selling securities …»). Проверка на отступление: поиск по всему
снятому тексту слов «planner», «financial planning», «holds himself/itself/themselves» — счётчик в скобках.

Три типа формул:
- **Т56** — модель 1956 без поправки: только securities, planner не упомянут.
- **Т86** — поправка NASAA 1986: «also includes financial planners and other persons who, as an integral component of
  other financially related services, provide **the foregoing** investment advisory services … or who hold themselves
  out as providing **the foregoing** investment advisory services to others for compensation».
- **Т02** — USA 2002 § 102(15): «The term includes a financial planner or other person that, as an integral component of
  other financially related services, provides investment advice to others for compensation as part of a business or
  that holds itself out as providing investment advice to others for compensation» (где «investment advice» — по
  securities в смысле первой фразы; WI и SC уточняют прямо: «investment advice **regarding securities**»).

| Штат | Норма | Формула | Канал, HTTP, размер | planner/holdout в тексте | Ловит нас |
|---|---|---|---|---|---|
| Pennsylvania | 70 P.S. § 1-102(j) (Act 1972-284) | Т56 + «publications, writings **or electronic means**» | legis.state.pa.us через прокси, 200, 234 445 б | 0 | нет |
| Alabama | Code § 8-6-2 | Т86 («“Investment adviser” also includes financial planners … the foregoing investment advisory services …») | Justia через прокси (прямой 403), 200, 11 770 б | 2 (обе в Т86) | нет |
| Arizona | A.R.S. § 44-3101(5) | Т86 дословно | azleg.gov прямой, 200, 8 217 б | 3 | нет |
| Connecticut | C.G.S. § 36b-3(11) | Т56 («“Investment adviser” means any person who … concerning securities») | cga.ct.gov прямой, 200, 284 473 б (вся глава 672a) | **0 во всей главе** | нет |
| Delaware | 6 Del. C. § 73-103(10) | Т86 дословно | delcode.delaware.gov прямой, 200, 32 563 б | 2 | нет |
| District of Columbia | D.C. Code § 31-5601.01(17)(A) | Т86-вариант: «shall include financial planners or other persons who, as an integral component of other financially related services, provide investment advisory services to others for compensation, or as a part of a business, hold themselves out as providing investment advisory services …» | code.dccouncil.gov прямой, 200, 44 046 б | 2 | нет |
| Idaho | Idaho Code § 30-14-102(15) | Т02 | через прокси, 200, 20 003 б | 2 | нет |
| Indiana | IC 23-19-1-2(15) | Т02 | Justia через прокси, 200, 20 341 б | 2 | нет |
| Iowa | Iowa Code § 502.102(15) | Т02 | legis.iowa.gov PDF прямой, 200, 75 173 б (pdftotext) | 2 | нет |
| Kansas | K.S.A. 17-12a102(15) | Т02 | ksrevisor.gov прямой, 200, 35 875 б | 2 | нет |
| Kentucky | KRS 292.310(11) | Т56 | Justia через прокси, 200, 13 654 б | 0 | нет |
| Louisiana | La. R.S. 51:702(7) | Т56 | Justia через прокси, 200, 17 196 б | 0 | нет |
| Maine | 32 M.R.S. § 16102(15) | Т02 (PL 2005, c. 65) | legislature.maine.gov прямой, 200, 65 383 б | 3 (третья — в определении IAR) | нет |
| Mississippi | Miss. Code § 75-71-102(15) | Т02 | Justia через прокси, 200, 20 108 б | 2 | нет |
| Missouri | RSMo § 409.1-102(15) | Т02 | revisor.mo.gov прямой, 200, 50 589 б | 2 | нет |
| Montana | MCA § 30-10-103(12)(b) | Т86-вариант: «(ii) represents to any person that the financial planner or other person provides **the investment advisory services described in subsection (12)(a)**» | leg.mt.gov прямой, 200, 34 715 б | 2 | нет |
| Nebraska | Neb. Rev. Stat. § 8-1101(7) | Т86 дословно | nebraskalegislature.gov через прокси, 200, 17 879 б | 2 | нет |
| North Dakota | N.D.C.C. § 10-04-02(10) | Т86 («The term includes financial planners … the foregoing investment advisory services …») | ndlegis.gov PDF главы 10-04 прямой, 200, 318 722 б | 2 | нет |
| Oklahoma | 71 O.S. § 1-102(17) | Т02 | Justia через прокси, 200, 21 389 б | 2 | нет |
| Rhode Island | R.I. Gen. Laws § 7-11-101(11) | Т56 | rilegislature.gov через прокси, 200, 16 349 б | 0 | нет |
| South Carolina | S.C. Code § 35-1-102(15) | Т02 + «investment advice **regarding securities**» | scstatehouse.gov (глава 35-1) прямой, 200, 222 431 б | 2 | нет |
| Tennessee | T.C.A. § 48-1-102(13) | Т02-вариант («who holds oneself out as providing investment advice») | Justia через прокси, 200, 20 329 б | 1 | нет |
| Vermont | 9 V.S.A. § 5102(15) | Т02 | legislature.vermont.gov прямой, 200, 82 005 б | 3 (третья — IAR) | нет |
| Wisconsin | Wis. Stat. § 551.102(15)(a) | Т02 + «publications, writings, or electronic means» + «regarding securities» | docs.legis.wisconsin.gov через прокси, 200, 18 374 б | 2 | нет |
| Wyoming | Wyo. Stat. § 17-4-102(a)(xv) | Т02 | Justia через прокси, 200, 19 053 б | 3 (третья — IAR) | нет |

URL: PA https://www.legis.state.pa.us/WU01/LI/LI/US/HTM/1972/0/0284..HTM · AL https://law.justia.com/codes/alabama/title-8/chapter-6/article-1/section-8-6-2/ ·
AZ https://www.azleg.gov/ars/44/03101.htm · CT https://www.cga.ct.gov/current/pub/chap_672a.htm · DE https://delcode.delaware.gov/title6/c073/sc01/index.html ·
DC https://code.dccouncil.gov/us/dc/council/code/sections/31-5601.01 · ID https://legislature.idaho.gov/statutesrules/idstat/Title30/T30CH14/SECT30-14-102/ ·
IN https://law.justia.com/codes/indiana/title-23/article-19/chapter-1/section-23-19-1-2/ · IA https://www.legis.iowa.gov/docs/code/502.102.pdf ·
KS https://www.ksrevisor.gov/statutes/chapters/ch17/017_012a_0102.html · KY https://law.justia.com/codes/kentucky/chapter-292/section-292-310/ ·
LA https://law.justia.com/codes/louisiana/revised-statutes/title-51/rs-51-702/ · ME https://legislature.maine.gov/statutes/32/title32sec16102.html ·
MS https://law.justia.com/codes/mississippi/title-75/chapter-71/article-1/section-75-71-102/ · MO https://revisor.mo.gov/main/OneSection.aspx?section=409.1-102 ·
MT https://leg.mt.gov/bills/mca/title_0300/chapter_0100/part_0010/section_0030/0300-0100-0010-0030.html · NE https://nebraskalegislature.gov/laws/statutes.php?statute=8-1101 ·
ND https://ndlegis.gov/cencode/t10c04.pdf · OK https://law.justia.com/codes/oklahoma/title-71/section-71-1-102/ · RI https://webserver.rilegislature.gov/Statutes/TITLE7/7-11/7-11-101.htm ·
SC https://www.scstatehouse.gov/code/t35c001.php · TN https://law.justia.com/codes/tennessee/title-48/chapter-1/part-1/section-48-1-102/ ·
VT https://legislature.vermont.gov/statutes/section/09/150/05102 · WI https://docs.legis.wisconsin.gov/statutes/statutes/551/i/102 · WY https://law.justia.com/codes/wyoming/title-17/chapter-4/article-1/section-17-4-102/

Выжимка группы 2: **ни одна из 25 юрисдикций не отступает от модели** в сторону титула без securities. Во всех
формулах Т86/Т02 титул «financial planner» — только пример лица, которое советует **по securities** или выдаёт себя
за такого советника. Проверка (б) и (в) этим проходом покрыта лишь в пределах определения и соседних секций главы
о ценных бумагах; отдельные законы о планировщиках вне securities-кодексов искались отдельно (см. ниже).

### П1. Штаты — группа 3 (9 юрисдикций, добор после неверных путей), первоисточники

Первый заход дал оболочки/404: akleg.gov (JS-якорь, 14 930 б без текста), Justia с неверным подразделом для AR, HI,
NH, NM, AK (страницы без текста статьи, 0 совпадений «securit»), gc.nh.gov (прямой 403, прокси 345 б),
capitol.hawaii.gov (прокси 924 б). Правильные адреса найдены поиском, сняты через r.jina.ai 16.09.2026.

| Штат | Норма | Формула | Канал, HTTP, размер | Ловит нас |
|---|---|---|---|---|
| Alaska | AS 45.56.900(18) | Т02: «“investment adviser” includes a financial planner or other person that, as an integral component of other financially related services, provides investment advice to others for compensation as part of a business or that holds itself out as providing investment advice to others for compensation» | Justia 2018 через прокси, 200, 20 080 б; FindLaw через прокси 200, 29 894 б (текущая редакция, то же) | нет |
| Arkansas | Ark. Code § 23-42-102(9)(B) | Т02-вариант: «“Investment adviser” includes a financial planner or other person that, as an integral component of other financially related services, provides or holds himself, herself, or itself out as providing investment advice to others for compensation and as part of a business.» | Justia через прокси, 200, 24 245 б | нет |
| Hawaii | HRS § 485A-102 | Т02 | Justia через прокси, 200, 18 543 б | нет |
| New Hampshire | RSA 421-B:1-102(26) | Т02 | Justia через прокси, 200, 41 808 б | нет |
| New Mexico | NMSA § 58-13C-102 | Т02 | Justia (ред. 2021) через прокси, 200, 31 526 б | нет |
| Oregon | ORS 59.015(20)(a) | Т56-вариант, **без planner**: «“State investment adviser” means a person who, for compensation: (A) Engages all or part of the time of the person, **in this state**, in the business of advising others … as to the value of securities …; (B) … managing an investment or trading account in securities …; (C) Issues or promulgates, as part of a regular business in this state, analyses or reports concerning securities.» Во всей главе 59 — 0 совпадений «planner» | oregonlegislature.gov через прокси (прямой не соединился), 200, 171 945 б | нет |
| South Dakota | SDCL § 47-31B-102(15) | Т02 | sdlegislature.gov через прокси (прямой API — оболочка), 200, 18 461 б | нет |
| Utah | Utah Code § 61-1-13(1)(q)(ii) | Т86-вариант как у MT: «"Investment adviser" includes a financial planner or other person who: (A) as an integral component of other financially related services, provides **the investment advisory services described in Subsection (1)(q)(i)** …» | le.utah.gov через прокси (прямой — SPA), 200, 37 338 б | нет |
| West Virginia | W. Va. Code § 32-4-401(g) | Т86 дословно | code.wvlegislature.gov через прокси (прямой — без текста), 200, 13 179 б | нет |

URL: AK https://law.justia.com/codes/alaska/2018/title-45/chapter-56/article-4/section-45.56.900/ и https://codes.findlaw.com/ak/title-45-trade-and-commerce/ak-st-sect-45-56-900/ ·
AR https://law.justia.com/codes/arkansas/title-23/subtitle-2/chapter-42/subchapter-1/section-23-42-102/ · HI https://law.justia.com/codes/hawaii/title-26/chapter-485a/section-485a-102/ ·
NH https://law.justia.com/codes/new-hampshire/title-xxxviii/chapter-421-b/section-421-b-1-102/ · NM https://law.justia.com/codes/new-mexico/2021/chapter-58/article-13c/article-1/section-58-13c-102/ ·
OR https://www.oregonlegislature.gov/bills_laws/ors/ors059.html · SD https://sdlegislature.gov/Statutes/47-31B-102 · UT https://le.utah.gov/xcode/Title61/Chapter1/61-1-S13.html · WV https://code.wvlegislature.gov/32-4-401/

Промежуточный итог (а): из 45 штатов + DC **ни один** не расширяет определение investment adviser на титул или
«financial planning» без связи с ценными бумагами. Отступления от модели по-прежнему два — WA и MD (Г26).
Единственный новый крючок — **Minnesota § 45.026** (отдельный закон, вне securities-кодекса, п. (в)).

### П1(б)(в). Отдельные законы о планировщиках и ограничения титулов вне securities-кодексов

**Поиск.** Два WebSearch-запроса («state law regulating use of title financial planner…», «financial planner title
protection state legislation…»). Итог: кроме NV 628A (Г26) найдены **Minnesota § 45.026** (выше, группа 1) и
**Connecticut Public Act 17-120** — новый.

**Connecticut — Public Act No. 17-120 (sHB 6992), «AN ACT PROTECTING THE INTERESTS OF CONSUMERS DOING BUSINESS WITH
FINANCIAL PLANNERS»**. Статус (cga.ct.gov через прокси, HTTP 200, 18 627 б, 16.09.2026;
https://www.cga.ct.gov/asp/cgabillstatus/cgabillstatus.asp?selBillType=Bill&which_year=2017&bill_num=6992):
«6/6/2017 Senate Passed as Amended by House Amendment Schedule A · 6/16/2017 Public Act 17-120 · 7/5/2017 Signed by the
Governor». Текст акта (прямой curl, HTTP 200, 3 992 б; https://www.cga.ct.gov/2017/ACT/pa/2017PA-00120-R00HB-06992-PA.htm), дословно:
> «Section 1. (NEW) (Effective from passage) (a) For purposes of this section and section 2 of this act, (1) "fiduciary
> duty" means a duty to act with prudence in the best interests of a consumer with undivided loyalty to such consumer, and
> (2) **"financial planner" means a person offering individualized financial planning or investment advice to a consumer
> for compensation where such activity is not otherwise regulated by state or federal law.**
> (b) No financial planner shall, in connection with an agreement with a consumer to provide financial planning or
> investment advice for compensation, use a certificate, professional designation or form of advertising expressing or
> implying that such person has special training, education or experience in advising or serving senior citizens, unless
> such person has obtained a certificate, title or designation as described in section 36b-4 of the general statutes.
> (c) **A financial planner shall disclose to a consumer, upon request, whether or not such financial planner has a
> fiduciary duty to such consumer for each recommendation such financial planner makes to such consumer.**
> Sec. 2. (NEW) … the Banking Commissioner shall provide on the department's Internet web site links to educational
> materials on (1) financial planning and other designations … Approved July 5, 2017»
Анализ OLR к первоначальной редакции (cga.ct.gov через прокси, HTTP 200, 5 342 б;
https://cga.ct.gov/2017/BA/2017HB-06992-R000014-BA.htm) — позиция законодательного аппарата, не закон: «a "financial
planner" is a person offering individualized financial planning or investment advice to a consumer for compensation who
is not otherwise regulated by the federal Employee Retirement Income Security Act (ERISA), Investment Advisers Act, or
Securities Exchange Act». Итоговый текст шире: «not otherwise regulated by state **or federal** law».
Выжимка: **единственный найденный штат, где «financial planner» определён ПО ФУНКЦИИ и именно для тех, кого
securities-режим не ловит** — то есть ровно для нас (индивидуальный план за подписку). Обязанности лёгкие:
(1) не заявлять особой квалификации по обслуживанию пожилых («senior») без сертификата по CGS § 36b-4;
(2) **по запросу клиента раскрывать, есть ли фидуциарная обязанность по каждой рекомендации**. Регистрации,
лицензии, страховки нет. Санкция в акте не названа (вероятный канал — CUTPA, не проверено). Кодификация в
C.G.S. **не установлена**: в главе 672a (securities) слова «planner» нет вовсе (0 совпадений на 284 473 б); поиск
«P.A. 17-120, S. 1» результата не дал. → **ловит по функции, последствия минимальные**.

**GAO-11-235** (18.01.2011; gao.gov через прокси, HTTP 200, 125 846 б; https://www.gao.gov/assets/a314689.html) —
отчёт органа Конгресса, не закон. Дословно:
> «Most states regulate the use of the title "financial planner," and state securities and insurance laws can apply to
> the misuse of this title and other titles. For example, according to NASAA, at least 29 states specifically include
> financial planners in their definition of investment adviser.[Footnote 25] According to NAIC, in many states,
> regulators can use unfair trade practice laws to prohibit insurance agents from holding themselves out as financial
> planners when in fact they are only engaged…»
> «[25] The District of Columbia and Puerto Rico also include financial planners in their definitions of investment
> adviser, according to NASAA.»
> «Federal and state regulators told us they generally focused their oversight and enforcement actions on financial
> planners' activities rather than the titles they use.»
Выжимка: «29 штатов включают planners в определение» — это формулы Т86/Т02, которые наш проход прочитал дословно:
все они привязаны к совету по securities. Цифра GAO **не противоречит** нашему выводу, а объясняет его: «regulate the
title» у GAO = «planner, советующий по securities, — инвестсоветник». Страховой канал (unfair trade practices против
**insurance agents**) к нам не относится — мы не страховые агенты.

**Защита титула «financial planner»** — FPA (financialplanningassociation.org через прокси, HTTP 200, 5 645 б;
https://www.financialplanningassociation.org/advocacy/policy-center/title-protection): позиция отраслевой ассоциации —
«Currently, the term "financial planner" can be used freely and without basis for marketing purposes». Ни одного
принятого закона о защите титула на странице не названо. Поиск принятых законов после 2023 г. — не дал результатов;
**полноту по 2024–2026 не гарантирую** (сессии легислатур не просматривались поштучно).

**Страховые правила о «senior»-титулах** (NASAA/NAIC Model Rule on Use of Senior-Specific Certifications) — существуют во
многих штатах (упоминание — CGS § 36b-4(c) в анализе OLR; Conn. Agencies Regs. § 38a-432b-2), но адресованы
участникам сделок с securities и страховым агентам. Нам — только как запрет слов «senior specialist», «retirement
specialist for seniors» и т. п. без сертификата (через CT PA 17-120 § 1(b) это касается и нас).

### П4. Электронная подпись под раскрытием WAC 460-24A-045(4) — Washington UETA (RCW 1.80) и E-SIGN

**WAC 460-24A-045** (полная глава 460-24A, app.leg.wa.gov прямой curl, HTTP 200, 397 673 б, 16.09.2026;
https://app.leg.wa.gov/wac/default.aspx?cite=460-24A&full=true) — дословно, целиком (правило регулятора):
> «Holding out as a financial planner. If you use a term **deemed similar to** "financial planner" or "investment counselor"
> under WAC 460-24A-040(2), you will not be considered to be holding yourself out as a financial planner for purposes of
> RCW 21.20.005 and 21.20.040 under the following circumstances: (1) You are not in the business of providing advice
> relating to the purchase or sale of securities, and would not, but for your use of such a term, be an investment
> adviser required to register pursuant to RCW 21.20.040; and (2) You do not directly or indirectly receive a fee for
> providing investment advice. … and (3) You deliver to every customer, at least forty-eight hours before accepting any
> compensation, including commissions from the sale of any investment product, a **written disclosure** including the
> following information: (a) You are not registered as an investment adviser or investment adviser representative in the
> state of Washington; (b) You are not authorized to provide financial planning or investment advisory services and do not
> provide such services; and (c) A brief description of your business …; and (4) You have each customer to whom a
> disclosure described in subsection (3) of this section is given **sign a written dated acknowledgment of receipt** of the
> disclosure; and (5) You **retain the executed acknowledgments** … for so long as you continue to receive compensation from
> such customers, but in no case for less than three years from date of execution of the acknowledgment; and (6) If you
> received compensation from the customer on more than one occasion, you need give the customer the disclosure … only on
> the first occasion unless the information in the disclosure becomes inaccurate …» (WSR 19-03-133, eff. 18.02.2019)
Попутное уточнение к Г26: гавань буквально покрывает **«term deemed similar to "financial planner"»** (список -040(2)),
а не сам титул «financial planner». Кто называет себя дословно «financial planner», гаванью, по тексту, не пользуется.

**Washington UETA, chapter 1.80 RCW** (app.leg.wa.gov прямой curl, HTTP 200, 160 575 б, 16.09.2026;
https://app.leg.wa.gov/rcw/default.aspx?cite=1.80&full=true). Закон. Дословно:
> «RCW 1.80.010 … (10) "Electronic signature" means an electronic sound, symbol, or process attached to or logically
> associated with a record and executed or adopted by a person with the intent to sign the record. … (15) "Record" means
> information that is inscribed on a tangible medium or that is stored in an electronic or other medium and is retrievable
> in perceivable form. … "Transaction" means an action or set of actions occurring between two or more persons relating to
> the conduct of business, commercial, or governmental affairs.»
> «RCW 1.80.020 Scope. (1) … this chapter applies to electronic records and electronic signatures relating to a
> transaction. (2) This chapter does not apply to a transaction to the extent it is governed by: (a) A law governing the
> creation and execution of wills … (b) Title 62A RCW other than …» (исключения нас не касаются)
> «RCW 1.80.030 … applies to any electronic record or electronic signature created … on or after June 11, 2020.»
> «RCW 1.80.040 … (2) This chapter applies only to transactions between parties each of which has agreed to conduct
> transactions by electronic means. Whether the parties agree … is determined from the context and surrounding
> circumstances, including the parties' conduct. (3) A party that agrees to conduct a transaction by electronic means may
> refuse to conduct other transactions by electronic means. The right granted by this subsection may not be waived…»
> «RCW 1.80.060 … (3) If a law requires a record to be in writing, an electronic record satisfies the law. (4) If a law
> requires a signature, an electronic signature satisfies the law.»
> «RCW 1.80.070 (1) If parties have agreed to conduct a transaction by electronic means and a law requires a person to
> provide, send, or deliver information in writing to another person, the requirement is satisfied if the information is
> provided, sent, or delivered … in an electronic record capable of retention by the recipient at the time of receipt. An
> electronic record is not capable of retention by the recipient if the sender or its information processing system
> inhibits the ability of the recipient to print or store the electronic record.»
> «RCW 1.80.110 (1) If a law requires that a record be retained, the requirement is satisfied by retaining an electronic
> record of the information in the record which: (a) Accurately reflects the information … and (b) Remains accessible for
> later reference.»
> «RCW 1.80.190 … This chapter modifies, limits, and supersedes the electronic signatures in global and national commerce
> act, 15 U.S.C. Sec. 7001 et seq., **but does not modify, limit, or supersede section 101(c) of that act, 15 U.S.C. Sec.
> 7001(c)**, or authorize electronic delivery of any of the notices described in section 103(b) of that act…»

**E-SIGN, 15 U.S.C. § 7001(c)** (govinfo.gov прямой curl, HTTP 200, 18 380 б, 16.09.2026;
https://www.govinfo.gov/content/pkg/USCODE-2023-title15/html/USCODE-2023-title15-chap96-subchapI-sec7001.htm). Закон. Дословно:
> «(c) Consumer disclosures (1) Consent to electronic records. Notwithstanding subsection (a), if a statute, **regulation,
> or other rule of law** requires that information relating to a transaction or transactions in or affecting interstate or
> foreign commerce be provided or made available to a consumer in writing, the use of an electronic record … satisfies the
> requirement … if— (A) the consumer has affirmatively consented to such use and has not withdrawn such consent; (B) the
> consumer, prior to consenting, is provided with a clear and conspicuous statement— (i) informing the consumer of (I) any
> right or option of the consumer to have the record provided or made available on paper or in nonelectronic form, and
> (II) the right of the consumer to withdraw the consent … (ii) informing the consumer of whether the consent applies …
> (iii) describing the procedures the consumer must use to withdraw consent … and (iv) informing the consumer (I) how,
> after the consent, the consumer may, upon request, obtain a paper copy …; (C) the consumer— (i) prior to consenting, is
> provided with a statement of the hardware and software requirements for access to and retention of the electronic
> records; and (ii) consents electronically, or confirms his or her consent electronically, in a manner that reasonably
> demonstrates that the consumer can access information in the electronic form …; and (D) [при смене требований — повторно]
> (2) … (B) Verification or acknowledgment. If a law that was enacted prior to this chapter expressly requires a record to
> be provided or made available by a specified method that requires verification or acknowledgment of receipt, the record
> may be provided or made available electronically only if the method used provides verification or acknowledgment of
> receipt (whichever is required).»
Список исключений § 7003(b) (govinfo, HTTP 200, 5 180 б) — судебные документы, уведомления об отключении
коммунальных услуг, выселении/изъятии жилья, отмене страховки жизни/здоровья, отзыве товара, перевозке опасных
грузов; раскрытия инвестсоветников в нём нет.

**Выжимка П4.** Да — **электронно выполнимо**, но при трёх условиях: (1) клиент согласился вести сделку
электронно (RCW 1.80.040(2); подписка онлайн — это и есть поведение-согласие); (2) раскрытие по (3) дано записью,
которую клиент может сохранить и распечатать, не заблокированной (RCW 1.80.070(1)); (3) «written dated
acknowledgment» (4) — электронная подпись (клик «Подтверждаю получение» с меткой времени, логически связанный с
записью раскрытия) удовлетворяет требованию подписи (RCW 1.80.060(4) + определение 1.80.010(10)); хранение 3 года —
электронно (1.80.110). **Поверх — процедура согласия потребителя E-SIGN § 7001(c)**: Вашингтон прямо её сохранил
(RCW 1.80.190), а § 7001(c) распространяется и на «regulation», т. е. на WAC. Значит, перед электронным раскрытием —
отдельное явное согласие с уведомлением о праве на бумагу, отзыве, техтребованиях и «демонстрацией доступа».
Толкования DFI Washington именно к 045(4) **не найдено** (поиск по главе 460-24A: слова «internet» — 0 совпадений;
«electronic» — только про электронную подачу форм в IARD/CRD, -047). Статус вывода — **толкование из текста норм**,
не позиция регулятора. Практический смысл ограничен: гавань -045 нам всё равно неудобна (требует заявить «не оказываем
услуг финансового планирования» и не покрывает дословный титул «financial planner»).

### П2. Территориальность и интернет — часть 1 (модельный приказ NASAA 1997)

**NASAA, «Interpretive Order Concerning Broker-Dealers, Investment Advisers, Broker-Dealer Agents and Investment Adviser
Representatives Using the Internet for General Dissemination of Information on Products and Services», adopted April 27,
1997** — модельный приказ (не закон; действует в штате, только если его издал администратор штата). nasaa.org напрямую
HTTP 403 (2 341 б); через r.jina.ai HTTP 200, 7 209 б, 16.09.2026; https://www.nasaa.org/wp-content/uploads/2011/07/26-Interpretive_Order.pdf. Дословно:
> «WHEREAS the [Administrator] further acknowledges that in certain instances, by distributing information on available
> products and services through Internet Communications available to persons in this state, broker-dealers, investment
> advisers … could be construed as "transacting business" for purposes of Sections 201(a) and 201(c) of the Act so as to
> require registration in this state, since the Internet Communications would be received in this state regardless of the
> intent of the person originating such communication; …
> 1. … investment advisers … who use … the Internet … to distribute information on available products and services
> through certain communications made on the Internet directed generally to anyone having access to the Internet … shall
> not be deemed to be "transacting business" in this state … **based solely on that fact** if the following conditions are
> observed: A. The Internet Communication contains a legend in which it is clearly stated that (1) the … investment adviser
> … may only transact business in this state if first registered, excluded or exempted …; and (2) follow-up, individualized
> responses to persons in this state … that involve … **the rendering of personalized investment advice for compensation**
> … will not be made absent compliance with state … registration requirements, or an applicable exemption or exclusion;
> B. The Internet Communication contains a mechanism, including and without limitation, technical "firewalls" or other
> implemented policies and procedures, designed reasonably to ensure that prior to any subsequent, direct communication
> with prospective customers or clients in this state, said … investment adviser … is first registered in this state or
> qualifies for an exemption or exclusion from such requirement. …
> C. The Internet Communication **does not involve** either effecting or attempting to effect transactions in securities,
> or **the rendering of personalized investment advice for compensation**, as may be, in this state over the Internet,
> **but is limited to the dissemination of general information on products and services**; …
> 2. The position expressed in this Interpretive Order extends to state … registration requirements only, and does not
> excuse compliance with applicable securities registration, antifraud or related provisions»
Выжимка: «Internet Advice Exemption» в модели NASAA — **изъятие для РЕКЛАМЫ, а не для СОВЕТА**. Условие C прямо
исключает «personalized … advice for compensation … over the Internet». Наш продукт — ровно индивидуальный совет за
подписку через сайт. Если штат считает нас investment adviser (WA/MD при титуле), приказ нас **не защищает**; он
защищает только сайт-витрину, пока жителю штата не выдан ни один персональный план, и требует легенду + firewall.

### П2. Территориальность и интернет — часть 2 (WA, MD, NV, MN, федеральный уровень)

**Washington — Securities Act Policy Statement PS-20, «Internet Advertising By Broker-Dealers, Investment Advisers, And
Their Representatives», adopted 08.09.1997** (Securities Administrator Deborah R. Bortner) — **позиция регулятора**
(policy statement), не закон и не правило. dfi.wa.gov прямой curl, HTTP 200, 29 933 б, 16.09.2026;
https://dfi.wa.gov/industry/securities-act-interpretive-statements/securities-act-policy-statement-20 (реестр позиций —
https://dfi.wa.gov/industry/securities-act-interpretive-statements, HTTP 200, 56 692 б). Дословно:
> «Question presented: Is a broker-dealer, investment adviser, securities salesperson, or investment adviser
> representative "transacting business in this state" by disseminating general information over the Internet that is
> available to residents of this state? Statute: RCW 21.20.040 states that "it is unlawful for any person to transact
> business in this state" as a broker-dealer, salesperson, investment adviser, or investment adviser representative unless
> he or she is registered under this chapter. …
> Conclusion: Broker-dealers, investment advisers, and their representatives who use the Internet to distribute
> information on available products and services through communications directed generally to anyone having access to the
> Internet shall not be deemed to be "transacting business" in this state for purposes of RCW 21.20.040, based solely on
> that fact, if the following conditions are observed: A. The Internet Communication contains a legend which clearly
> states that: (1) the … investment adviser … may not transact business in Washington unless appropriately registered, or
> excluded or exempted from such registration; and (2) follow-up, individualized responses to persons in this state …
> that involve … the rendering of personalized investment advice for compensation, will not be made absent compliance with
> the appropriate registration requirements, or an applicable exemption or exclusion; B. … technical "firewalls" or other
> implemented policies and procedures, designed to reasonably ensure that prior to any direct communication with
> prospective customers or clients in this state, said … investment adviser … is first registered in this state or
> qualifies for an exemption or exclusion …; C. The Internet Communication does not involve … **the rendering of
> personalized investment advice for compensation in this state**, but is limited to the dissemination of general
> information on products and services; …»
Выжимка: WA принял модель NASAA 1997 почти дословно. Для нас — то же, что по модели: **витрина защищена, советы
жителям WA — нет**. В RCW 21.20 отдельной секции о территориальном действии (аналога § 414 модели 1956) **не
найдено**: поиск по полной главе (433 127 б, https://app.leg.wa.gov/rcw/default.aspx?cite=21.20&full=true) фраз «is made
in this state», «originates from» — 0 совпадений. Операционный критерий — «transact business in this state»
(RCW 21.20.040(3)), не определённый в законе; PS-20 — единственное найденное толкование, и оно исходит из того, что
персональный совет жителю WA через интернет = деятельность «in this state». Собственный де-минимис WA —
RCW 21.20.040(3)(b) (без места деятельности в штате и в пределах клиентского порога — установлено в Г26).

**Maryland — Corps. & Ass'ns § 11-801 «Scope of Title»** (Justia через прокси, HTTP 200, 3 369 б, 16.09.2026;
https://law.justia.com/codes/maryland/corporations-and-associations/title-11/subtitle-8/section-11-801/). Закон. Дословно:
> «(a) Sections 11-301, 11-302, 11-303, 11-304, 11-401, 11-501, and 11-703 of this title apply to any person who: …
> (2) Offers or provides investment advisory services if: (i) The contract for the investment advisory services is
> executed in this State; (ii) **The investment advisory services are rendered in this State**; or (iii) Any action
> instrumental in effecting prohibited conduct is taken in this State, **whether or not either party is then present in
> this State**. …
> (c) For the purpose of this section, an offer to sell or to buy is made in this State, whether or not either party is
> then present in this State, if the offer: (1) Originates from this State; or (2) Is directed by the offeror to this
> State and received at the place to which it is directed …
> (e) An offer to sell or to buy, or to provide investment advisory services, is not made in this State if: (1) The
> publisher circulates … any bona fide newspaper or other publication of general, regular, and paid circulation which is
> not published in this State …; or (2) A radio or television program originating outside this State is received in this
> State.
> (f) Sections 11-302 and 11-401(b) of this title, as well as § 11-304 … apply if any act instrumental in effecting
> prohibited conduct is done in this State, whether or not either party is then present in this State.»
Выжимка: § 11-401 (регистрация) распространяется на того, кто «provides investment advisory services … rendered in this
State» — **присутствие не нужно**. Изъятие (e) — только для газет и радио/ТВ; интернет туда не вписан. Аналога PS-20 в
COMAR 02.02.05 **не найдено** (полная глава, regs.maryland.gov прямой curl, HTTP 200, 176 613 б; «internet» — 0,
«electronic» — только электронная подача в IARD, .10); издавал ли Maryland Securities Commissioner отдельный приказ —
**не установлено** (один WebSearch без результата; реестр приказов не просматривался).

**Nevada — NRS 628A** (leg.state.nv.us через прокси, HTTP 200, 5 783 б, 16.09.2026; https://www.leg.state.nv.us/NRS/NRS-628A.html):
> «3. "Financial planner" means a person who for compensation advises others upon the investment of money or upon
> provision for income to be needed in the future, or who holds himself or herself out as qualified to perform either of
> these functions, but does not include: (a) An attorney … (b) A certified public accountant … (c) A producer of
> insurance …» (Added to NRS by 1993, 1372)
Выжимка: в главе нет ни территориальной нормы, ни упоминания резидентов/«in this State», кроме исключений и
«violated any law of this State». Применимость к иностранному сервису решается общими нормами о юрисдикции
(long-arm, NRCP 4.2(a)) и коллизионным правом — **толкований применительно к 628A не найдено**. Разумный вывод:
иск клиента-резидента Невады к нам по 628A.030 возможен в суде Невады, если мы целенаправленно обслуживаем жителей
штата (подписка, оплата, персональный план) — это вывод из общих принципов, не норма.

**Minnesota — § 45.026** — территориальной нормы тоже нет (текст выше, группа 1); применяется через общие полномочия
комиссара § 45.027 subd. 5 (снято 16.09.2026, прямой curl, revisor.mn.gov/statutes/cite/45.027): «Whenever it appears to
the commissioner that any person has engaged or is about to engage in any act or practice constituting a violation of
any law, rule, or order related to the duties and responsibilities entrusted to the commissioner, the commissioner may
bring an action in the name of the state … to enjoin the acts or practices and to enforce compliance … The terms of this
subdivision govern an action … including an action against a person who, for whatever reason, claims that the subject
law … does not apply to the person.»

**Федеральный уровень.**
(1) **Национальный де-минимис NSMIA, 15 U.S.C. § 80b-18a(d)** (govinfo прямой, HTTP 200, 6 186 б;
https://www.govinfo.gov/content/pkg/USCODE-2023-title15/html/USCODE-2023-title15-chap2D-subchapII-sec80b-18a.htm). Закон:
> «(d) National de minimis standard. No law of any State … requiring the registration, licensing, or qualification as an
> investment adviser shall require an investment adviser to register with the securities commissioner of the State … or
> to comply with such law (other than any provision thereof prohibiting fraudulent conduct) if the investment adviser—
> (1) does not have a place of business located within the State; and (2) during the preceding 12-month period, has had
> fewer than 6 clients who are residents of that State.»
Оговорка: «investment adviser» в федеральном акте — по 15 U.S.C. § 80b-2(a)(11), т. е. советник **по securities**.
Лицо, которое инвестсоветник только по титульному правилу штата (WA/MD), под федеральное определение не подпадает, и
распространяется ли на него § 80b-18a(d) — **спорно; толкования не найдено**. Для запуска это не щит: < 6 клиентов
— не бизнес-модель.
(2) **SEC Rule 203A-2(e) «Internet investment advisers»** (eCFR API прямой, HTTP 200, 20 119 б;
https://www.ecfr.gov/api/renderer/v1/content/enhanced/current/title-17?part=275&section=275.203A-2) — правило SEC:
> «The prohibition of section 203A(a) of the Act (15 U.S.C. 80b-3a(a)) does not apply to: … (e) Internet investment
> advisers. (1) An investment adviser that: (i) Provides investment advice to all of its clients exclusively through an
> operational interactive website at all times during which the investment adviser relies on this paragraph (e); …
> (2) … "operational interactive website" means a website, mobile application, or similar digital platform through which
> the investment adviser provides digital investment advisory services on an ongoing basis to more than one client …»
Выжимка: это **не изъятие из регистрации**, а право регистрироваться в SEC вместо штатов; доступно только
инвестсоветнику по федеральному определению (securities). Нам, не советующим по ценным бумагам, **неприменимо и не
нужно**. Термин «Internet Adviser Exemption» в отраслевой прессе относится именно к этому правилу, а не к изъятию для
персонального совета; путать их нельзя.

**Выжимка П2.** Ни одна найденная норма не выводит иностранный онлайн-сервис из-под законов WA, MD, NV, MN, если он
**оказывает персональные услуги жителям штата**. MD прямо говорит «rendered in this State … whether or not either party
is then present»; WA (PS-20) и модель NASAA освобождают только общую информацию на сайте, не персональный совет.
Защита — не изъятие, а **геоблок/отказ в обслуживании** жителей конкретных штатов (или отказ от титула в WA/MD).

### П3 (🆕). CFPB и UDAAP для бюджетно-долгового сервиса вне режимов инвестсоветника

Источник текста: **govinfo.gov по адресам `USCODE-2023-title12/...-sec54xx.htm` отдал страницу «Page Not Found»**
(HTTP 200, 43 107/44 165 б — размер ошибки одинаков для всех секций; путь `chap53-subchapV-partA-…` — 404,
`chap53-subchapV-sec…` — страница-ошибка). Рабочий канал — **uscode.house.gov через `r.jina.ai`** (без браузерного
UA; с UA прокси отдаёт капчу Cloudflare): § 5481 — HTTP 200, 36 205 б; § 5531 — 200, 4 222 б; § 5536 — 200, 2 675 б,
все 16.09.2026.

**12 U.S.C. § 5481(15)(A)(viii)** — ключевая норма (Закон; CFPA 2010 § 1002). Дословно:
> «(15) Financial product or service (A) In general. The term "financial product or service" means— … (viii) **providing
> financial advisory services** (other than services relating to securities provided by a person regulated by the
> Commission or a person regulated by a State securities Commission, but only to the extent that such person acts in a
> regulated capacity) **to consumers on individual financial matters** or relating to proprietary financial products or
> services (other than by publishing any bona fide newspaper, news magazine, or business or financial publication of
> general and regular circulation, including publishing market data, news, or data analytics or **investment information
> or recommendations that are not tailored to the individual needs of a particular consumer**), including—
> (I) **providing credit counseling to any consumer**; and (II) **providing services to assist a consumer with debt
> management or debt settlement**, modifying the terms of any extension of credit, or avoiding foreclosure; …»

**§ 5481(5)** «consumer financial product or service»:
> «means any financial product or service that is described in one or more categories under— (A) paragraph (15) and is
> **offered or provided for use by consumers primarily for personal, family, or household purposes**; or (B) clause (i),
> (iii), (ix), or (x) of paragraph (15)(A), and is delivered, offered, or provided in connection with a consumer
> financial product or service referred to in subparagraph (A).»

**§ 5481(6)** «covered person»:
> «means— (A) any person that engages in offering or providing a consumer financial product or service; and (B) any
> affiliate of a person described in subparagraph (A) if such affiliate acts as a service provider to such person.»

**§ 5531 «Prohibiting unfair, deceptive, or abusive acts or practices»** (CFPA § 1031):
> «(a) In general. The Bureau may take any action authorized under part E to prevent a covered person or service provider
> from committing or engaging in an unfair, deceptive, or abusive act or practice under Federal law in connection with any
> transaction with a consumer for a consumer financial product or service, or the offering of a consumer financial product
> or service.
> (b) … The Bureau may prescribe rules applicable to a covered person or service provider identifying as unlawful unfair,
> deceptive, or abusive acts or practices …
> (c) Unfairness (1) … unless the Bureau has a reasonable basis to conclude that— (A) the act or practice causes or is
> likely to cause substantial injury to consumers which is not reasonably avoidable by consumers; and (B) such substantial
> injury is not outweighed by countervailing benefits to consumers or to competition. …
> (d) Abusive. The Bureau shall have no authority … to declare an act or practice abusive … unless the act or practice—
> (1) **materially interferes with the ability of a consumer to understand a term or condition** of a consumer financial
> product or service; or (2) takes unreasonable advantage of— (A) **a lack of understanding on the part of the consumer of
> the material risks, costs, or conditions** of the product or service; (B) the inability of the consumer to protect the
> interests of the consumer in selecting or using a consumer financial product or service; or (C) **the reasonable
> reliance by the consumer on a covered person to act in the interests of the consumer**.»

**§ 5536 «Prohibited acts»** (CFPA § 1036):
> «(a) In general. It shall be unlawful for— (1) any covered person or service provider— (A) to offer or provide to a
> consumer any financial product or service not in conformity with Federal consumer financial law …; or (B) **to engage in
> any unfair, deceptive, or abusive act or practice**; (2) any covered person or service provider to fail or refuse, as
> required by Federal consumer financial law … (A) to permit access to or copying of records; (B) to establish or maintain
> records; or (C) to make reports or provide information to the Bureau; or (3) any person to knowingly or recklessly
> provide substantial assistance to a covered person … in violation of section 5531 …»

**GAO-11-235, сноска 27** (позиция органа Конгресса, 2011; текст снят выше):
> «[27] Section 1011 of the Dodd-Frank Act established the Bureau of Consumer Financial Protection to regulate "the
> offering and provision of consumer financial products or services under the Federal consumer financial laws." A
> financial product or service is defined in section 1002(15)(A)(viii) of the act to include financial advisory services
> to consumers on individual financial matters, with the exception of advisory services related to securities provided by
> a person regulated by SEC or a state securities commission … **Accordingly, it appears that the bureau may have
> jurisdiction over financial planners to the extent that they may offer services that would not be under the jurisdiction
> of SEC or a state securities commission.**»
> «In theory, a financial planner could offer only services that do not fall under existing regulatory regimes—for example,
> **advice on household budgeting**—but such an example is likely hypothetical…»

**Правоприменительный пример: CFPB, In re Hello Digit, LLC, 2022-CFPB-0007, consent order 10.08.2022** — акт
правоприменения, не закон (files.consumerfinance.gov: прямой curl HTTP 403, через `r.jina.ai` HTTP 200, 42 070 б;
https://files.consumerfinance.gov/f/documents/cfpb_hello-digit-llc_consent-order_2022-08.pdf; карточка дела —
https://www.consumerfinance.gov/enforcement/actions/hello-digit-llc/, через прокси HTTP 200, 2 339 б). Дословно:
> «I. Jurisdiction 1. The Bureau has jurisdiction over this matter under §§ 1053 and 1055 of the CFPA, 12 U.S.C. §§ 5563
> and 5565. … IV. Bureau Findings and Conclusions … 5. Digit is a financial-technology company with its principal place of
> business in San Francisco, California. 6. **Digit is a "covered person" under 12 U.S.C. § 5481(6).** 7. Digit has offered
> and provided a **personal-finance-management application** to consumers since February 2015. … Digit uses its own
> proprietary algorithm to analyze consumers' checking-account data to determine when and how much to save for each
> consumer.»
Санкции по делу — $2,7 млн штрафа и не менее $68 145 возмещения. Оговорка: Digit **перемещал деньги** клиентов
(автопереводы на счёт), то есть подпадал ещё и под (15)(A)(iv)-(v); наш продукт денег не двигает, и на «covered person»
у нас работает именно (15)(A)(viii).

**🔴 Прямой ответ П3: да, подпадаем.** Совет по **порядку погашения долгов** — это «services to assist a consumer with
debt management» (§ 5481(15)(A)(viii)(II)) и одновременно «financial advisory services … on individual financial
matters»; бюджетная часть — «credit counseling»/советы по личным финансам того же подпункта. Изъятие для securities
нам не помогает (мы вне SEC/штатов по ценным бумагам — именно поэтому мы **внутри** CFPA), изъятие для издателей не
применимо прямо по тексту: оно снято для рекомендаций, «tailored to the individual needs of a particular consumer», —
а наши рекомендации персональные по определению продукта. Подписка = «for compensation» здесь даже не требуется:
достаточно «offering or providing» потребителю для личных/семейных целей (§ 5481(5)).
**Что из этого следует практически.** (1) Регистрации/лицензии у CFPB **нет** — режим не разрешительный: Бюро
надзирает и наказывает. (2) Надзор (examinations) над небанками — только по § 5514 (крупные участники рынков,
определённых правилом Бюро; рынков «credit counseling»/«debt management» среди принятых правил о larger participants
нет — **проверено по списку рынков, но не по каждому правилу: считать «не установлено окончательно»**). (3) **Запрет
UDAAP (§ 5536(a)(1)(B)) действует независимо от размера и надзора**, и полномочия по § 5531(d)(2)(C) прямо ловят
«reasonable reliance by the consumer on a covered person to act in the interests of the consumer» — то есть язык
продукта («мы действуем в ваших интересах», «оптимальный план») создаёт нам абьюзивный риск, если результат
расходится с обещанием. (4) Нормы о территориальном действии CFPA в § 5481 нет; в найденных делах ответчики —
американские компании. Применимость к иностранному поставщику, обслуживающему потребителей в США, **не установлена
первоисточником** (дел против иностранного поставщика в заходе не найдено); текст «any person that engages in offering
or providing» географии не содержит.

## ИТОГ Г27

### Полная таблица: 50 штатов + DC

Колонки: **(а)** отступает ли определение investment adviser от модели в сторону «financial planner»/«holds out» БЕЗ
связи с ценными бумагами · **(б)** запрет/ограничение титулов · **(в)** отдельный закон о financial planners вне
securities-кодекса · **Ловит** — да (без титула) / титул (только при использовании титула) / нет / не установлено.
Формулы: Т56 — модель 1956 (planner не упомянут), Т86 — поправка NASAA 1986 («the foregoing … advisory services»),
Т02 — USA 2002 § 102(15). Все три формулы привязаны к совету по securities и нас не ловят.

| # | Юрисдикция | Норма | (а) | (б) | (в) | Ловит |
|---|---|---|---|---|---|---|
| 1 | Alabama | Code § 8-6-2 | Т86 | нет | нет | нет |
| 2 | Alaska | AS 45.56.900(18) | Т02 | нет | нет | нет |
| 3 | Arizona | A.R.S. § 44-3101(5) | Т86 | нет | нет | нет |
| 4 | Arkansas | § 23-42-102(9)(B) | Т02-вар. | нет | нет | нет |
| 5 | California | Corp. Code § 25009(b) | титул «financial planner» **конъюнктивно** с securities | нет самостоятельного | нет | нет |
| 6 | Colorado *(Г26)* | C.R.S. 11-51-201(9.5) | модель | нет | нет | нет |
| 7 | Connecticut | C.G.S. § 36b-3(11) (Т56) + **PA 17-120 (2017)** | нет (в securities) | senior-designations § 1(b) | **да — PA 17-120: «financial planner» по ФУНКЦИИ** | **да, без титула** (обязанности: не заявлять senior-квалификацию; по запросу раскрыть наличие фидуциарной обязанности) |
| 8 | Delaware | 6 Del. C. § 73-103(10) | Т86 | нет | нет | нет |
| 9 | District of Columbia | D.C. Code § 31-5601.01(17)(A) | Т86-вар. | нет | нет | нет |
| 10 | Florida | Fla. Stat. § 517.021(20) | Т56, слова «planner» в секции нет | нет | нет | **нет** (сниппет Г26 подтверждён первоисточником) |
| 11 | Georgia | O.C.G.A. § 10-5-2 | Т02 | нет | нет | нет |
| 12 | Hawaii | HRS § 485A-102 | Т02 | нет | нет | нет |
| 13 | Idaho | § 30-14-102(15) | Т02 | нет | нет | нет |
| 14 | Illinois | 815 ILCS 5/2.11 | Т86-вар., «in this State» | нет | нет | нет |
| 15 | Indiana | IC 23-19-1-2(15) | Т02 | нет | нет | нет |
| 16 | Iowa | § 502.102(15) | Т02 | нет | нет | нет |
| 17 | Kansas | K.S.A. 17-12a102(15) | Т02 | нет | нет | нет |
| 18 | Kentucky | KRS 292.310(11) | Т56 | нет | нет | нет |
| 19 | Louisiana | R.S. 51:702(7) | Т56 | нет | нет | нет |
| 20 | Maine | 32 M.R.S. § 16102(15) | Т02 | нет | нет | нет |
| 21 | **Maryland** *(Г26)* | Corps. & Ass'ns § 11-101(i)(1)(ii); § 11-401(b); § 11-801 | **да**: ветка (ii)2 описывает процесс планирования, (ii)3 ловит титул | **да** (§ 11-101(i)(1)(ii)3 + COMAR 02.02.05.20) | нет | **титул — да; по функции — вероятно да, не разрешено** |
| 22 | Massachusetts | M.G.L. c. 110A § 401(m) | Т86 | нет | нет | нет |
| 23 | Michigan | MCL 451.2102a(e) | Т02 | нет | нет | нет |
| 24 | **Minnesota** | Minn. Stat. § 45.026 | нет (в securities) | **да — перечень титулов** | **да — отдельный закон о business of financial planning** | **титул** (последствие: фидуциарная обязанность + иск + § 45.027 subd. 5) |
| 25 | Mississippi | § 75-71-102(15) | Т02 | нет | нет | нет |
| 26 | Missouri | § 409.1-102(15) | Т02 | нет | нет | нет |
| 27 | Montana | MCA § 30-10-103(12) | Т86-вар. | нет | нет | нет |
| 28 | Nebraska | § 8-1101(7) | Т86 | нет | нет | нет |
| 29 | **Nevada** *(Г26)* | NRS 628A.010–.040 | нет (регистрации нет) | титул «holds himself out as qualified» | **да — NRS 628A** | **да при совете «upon provision for income to be needed in the future» или при титуле**: фидуциарий, ответственность, E&O/bond от $1 млн |
| 30 | New Hampshire | RSA 421-B:1-102(26) | Т02 | нет | нет | нет |
| 31 | New Jersey | N.J.S.A. 49:3-49(g)(1) | Т86-вар. | нет | нет | нет |
| 32 | New Mexico | NMSA § 58-13C-102 | Т02 | нет | нет | нет |
| 33 | New York | GBL § 359-eee(1)(a) | Т56, «within or from the state of New York» | нет | нет | нет |
| 34 | North Carolina *(Г26)* | G.S. 78C-2(1) | Т86 | нет | нет | нет |
| 35 | North Dakota | N.D.C.C. § 10-04-02(10) | Т86 | нет | нет | нет |
| 36 | Ohio | ORC § 1707.01(X)(1) | Т56 | нет | нет | нет |
| 37 | Oklahoma | 71 O.S. § 1-102(17) | Т02 | нет | нет | нет |
| 38 | Oregon | ORS 59.015(20) | Т56-вар., «in this state», planner в главе 0 раз | нет | нет | нет |
| 39 | Pennsylvania | 70 P.S. § 1-102(j) | Т56 + «electronic means» | нет | нет | нет |
| 40 | Rhode Island | § 7-11-101(11) | Т56 | нет | нет | нет |
| 41 | South Carolina | § 35-1-102(15) | Т02 + «regarding securities» | нет | нет | нет |
| 42 | South Dakota | SDCL § 47-31B-102(15) | Т02 | нет | нет | нет |
| 43 | Tennessee | T.C.A. § 48-1-102(13) | Т02-вар. | нет | нет | нет |
| 44 | Texas | Gov't Code § 4001.059; 7 TAC 107.2, 116.1 | Т56 + «as may be further defined by board rule»; в правилах planner нет | нет | нет | нет |
| 45 | Utah | § 61-1-13(1)(q)(ii) | Т86-вар. | нет | нет | нет |
| 46 | Vermont | 9 V.S.A. § 5102(15) | Т02 | нет | нет | нет |
| 47 | Virginia | § 13.1-501 | Т86 | нет | нет | нет |
| 48 | **Washington** *(Г26)* | RCW 21.20.005(8), .040(3)–(4); WAC 460-24A-040, -045; PS-20 | **да — титул без securities** | **да — расширенный перечень титулов** (-040) | нет | **титул — да** (гавань -045 покрывает только «сходные» термины, не сам титул) |
| 49 | West Virginia | § 32-4-401(g) | Т86 | нет | нет | нет |
| 50 | Wisconsin | § 551.102(15)(a) | Т02 + «regarding securities» | нет | нет | нет |
| 51 | Wyoming | § 17-4-102(a)(xv) | Т02 | нет | нет | нет |

### 🔴 В скольких штатах нас ловит

- **Без титула — 1 штат: Connecticut** (PA 17-120: «financial planner» = кто предлагает индивидуальное финансовое
  планирование или совет за плату и **не урегулирован иначе**). Последствия минимальные: запрет заявлять
  senior-квалификацию + раскрытие по запросу о наличии фидуциарной обязанности. Регистрации нет.
- **Плюс 1 спорный без титула: Maryland** (ветка § 11-101(i)(1)(ii)2 — сбор данных → цели → анализ → «recommends a
  financial plan»; единственная опора против — «information relating to investments»). Не разрешено ни в Г26, ни в Г27;
  толкований Maryland Securities Division нет.
- **Только при титуле — 4 штата: Washington, Maryland, Minnesota, Nevada.** Вашингтон и Мэриленд — с регистрацией
  инвестсоветника; Миннесота и Невада — без регистрации, но с фидуциарной обязанностью (NV — ещё и страховка/бонд
  от $1 млн). Невада ловит и без титула, если совет касается «provision for income to be needed in the future» —
  накопительные цели под это подпадают по букве.
- **Остальные 46 юрисдикций — нет.** Сплошной проход выполнен: 51 из 51 (46 в Г27 + 5 в Г26), по каждой снят
  первоисточник, не сниппет. «Не проверено по бюджету» — **ноль** позиций по пункту (а).
- Оговорка по полноте (б)/(в): отдельные законы вне securities-кодексов искались поисковыми запросами и найдены три
  (NV, MN, CT). **Поштучный проход по кодексам всех штатов на предмет «financial planner» вне securities-раздела не
  делался** — это другая работа объёмом ещё в один батч; вероятность пропустить ещё один CT-подобный закон не нулевая.

### 🔴 Защищает ли нас Internet Advice Exemption

**Нет.** Изъятие, которое в отрасли называют «Internet Adviser Exemption», — это два разных механизма, и ни один
не наш:
1. **Модельный приказ NASAA 1997** (в WA — PS-20 от 08.09.1997) освобождает от «transacting business in this state»
   только **общую информацию на сайте**, и прямо требует, чтобы коммуникация **не включала** «the rendering of
   personalized investment advice for compensation», плюс легенду и firewall. Персональный план за подписку — ровно то,
   что условие C исключает.
2. **SEC Rule 203A-2(e)** — не изъятие от регистрации, а право интернет-советника регистрироваться в SEC вместо
   штатов; доступно только советнику по ценным бумагам. Нам неприменимо.
Территориальность против нас: MD § 11-801(a)(2)(ii) — «investment advisory services are rendered in this State …
whether or not either party is then present in this State»; изъятие (e) распространяется на газеты и радио/ТВ, интернет
в нём отсутствует. В WA территориальной нормы нет вовсе, критерий — «transact business in this state», и PS-20 читает
его против нас. Реальная защита — **не изъятие, а геоблок** (не обслуживать резидентов конкретных штатов) либо отказ
от титула там, где ловит титул. Национальный де-минимис NSMIA (15 U.S.C. § 80b-18a(d): нет места деятельности в штате
и < 6 клиентов-резидентов за 12 месяцев) как бизнес-модель не годится, и его применимость к «инвестсоветнику только по
титульному правилу штата» спорна.

### 🔴 Подпадаем ли под CFPB

**Да, по прямому тексту закона.** Совет по порядку погашения долгов и по бюджету — «financial advisory services …
to consumers on individual financial matters», включая «credit counseling» и «services to assist a consumer with debt
management» (12 U.S.C. § 5481(15)(A)(viii)); продукт для личных/семейных целей делает его «consumer financial product
or service» (§ 5481(5)), а нас — «covered person» (§ 5481(6)). Изъятие для securities-советников нам не помогает
(мы вне SEC — и именно поэтому внутри CFPA), издательское изъятие снято для рекомендаций, «tailored to the individual
needs of a particular consumer». Разрешительного режима нет: нет ни лицензии, ни регистрации — есть **запрет UDAAP**
(§ 5536(a)(1)(B)) и полномочия Бюро (§ 5531), включая «abusive» через «reasonable reliance by the consumer on a covered
person to act in the interests of the consumer» (§ 5531(d)(2)(C)). Прецедент по персональному финансовому приложению —
Hello Digit (2022-CFPB-0007): «Digit is a "covered person" under 12 U.S.C. § 5481(6)», $2,7 млн штрафа. Применимость к
**иностранному** поставщику первоисточником не подтверждена и не опровергнута — географического ограничения в тексте
нет, дел против иностранцев не найдено.

### 🔴 Электронная подпись под WAC 460-24A-045(4)

Выполнимо электронно: RCW 1.80.060(3)–(4) (электронная запись и подпись удовлетворяют требованиям «в письменной
форме» и «подпись»), 1.80.070(1) (запись, пригодная к сохранению), 1.80.110 (электронное хранение 3 года) — при
условии согласия сторон вести сделку электронно (1.80.040(2)). **Поверх — процедура согласия потребителя E-SIGN
15 U.S.C. § 7001(c)**, которую Вашингтон сохранил (RCW 1.80.190) и которая распространяется на «regulation», т. е. на
WAC. Толкования DFI именно к 045(4) нет — вывод из текста норм. Практическая ценность мала: сама гавань -045 требует
заявить «не оказываем услуг финансового планирования» и, по букве, покрывает лишь термины, «сходные» с «financial
planner», а не сам титул.

### 🔴 Запрещённые для продукта слова и формулировки (сводно по США)

Красная зона (использование = самостоятельное основание регулирования, без изменения функциональности):
- **«financial planner», «financial planning services», «financial planning»** — WA (RCW 21.20.005(8), WAC 460-24A-040),
  MD (§ 11-101(i)(1)(ii)3), MN (§ 45.026(1)(b)), CA (§ 25009(b) — вместе с советом по securities).
- **«financial consultant», «financial adviser/advisor», «financial counselor», «investment counselor», «investment
  adviser», «money manager», «investment planner»** и любые комбинации, создающие впечатление услуг финансового
  планирования — WA (перечень -040), MD («any other similar type of adviser»), MN (перечень § 45.026(1)(b)).
- **«wealth manager», «wealth management»** — прямо в перечнях не найдено, но подпадает под «similar designation,
  title, or combination» (MN) и «combinations» (WA): считать красной зоной по аналогии, не по букве.
- **«holding out as qualified to advise upon the investment of money or upon provision for income to be needed in the
  future»** — формула NRS 628A.010(3); избегать буквальных обещаний «обеспечим доход в будущем».
- **«senior specialist», «certified senior adviser», «retirement specialist for seniors»** и любые обозначения особой
  подготовки по работе с пожилыми без соответствующего сертификата — CT PA 17-120 § 1(b) (для нас как «financial
  planner» по функции), CGS § 36b-4(c), плюс аналогичные модельные правила NASAA/NAIC в других штатах.
Жёлтая зона (создаёт риск по CFPA § 5531(d)(2)(C) и по антифрод-нормам, а не отдельный режим):
- «действуем в ваших интересах», «фидуциарный», «в вашу пользу», «best interest» — порождают «reasonable reliance …
  to act in the interests of the consumer»;
- «оптимальный/лучший план», «гарантированно погасите долг за N месяцев», «guaranteed» — WAC 460-24A-140 запрещает
  «guarantees of success» для советников, а для всех прочих это классическое deceptive practice;
- «инвестиционный совет», «рекомендуем вложить», любые имена конкретных ценных бумаг/фондов — переводит нас в
  securities-режим во всех 51 юрисдикциях сразу.
Нейтральные формулировки, которые остаются доступными: «сервис расчёта распределения свободного денежного потока»,
«калькулятор/модель погашения долгов», «инструмент планирования бюджета» (**без** слова «planner» в роли титула лица),
«справочный расчёт, не является индивидуальной инвестиционной рекомендацией».

### Что осталось неизвестным по Г27

1. Кодификация CT PA 17-120 в C.G.S. (в главе 672a слова «planner» нет; поиск «P.A. 17-120, S. 1» результата не дал) и
   санкция за нарушение § 1 (вероятный канал — CUTPA, не проверено).
2. Издавал ли Maryland Securities Commissioner интернет-приказ в стиле NASAA 1997 (в COMAR 02.02.05 его нет; реестр
   приказов Division of Securities не просматривался).
3. Толкование Maryland § 11-101(i)(1)(ii)2 (функциональная ветка) — хвост из Г26, не снят.
4. Применимость CFPA к иностранному поставщику без присутствия в США — дел не найдено; норма географии не содержит.
5. Есть ли среди правил CFPB о «larger participants» рынок, покрывающий credit counseling/debt management (проверен
   перечень рынков, не каждое правило).
6. Законы штатов о financial planners **вне** securities-кодексов сверх найденных трёх (NV, MN, CT) — поштучный проход
   по всем кодексам не делался.
7. Принятые в 2024–2026 гг. законы о защите титула «financial planner» — на странице FPA ни одного не названо, поиск
   принятых актов результата не дал; поштучно сессии легислатур не просматривались.
8. Законы штатов о **debt management services / debt adjusting** (лицензирование посредников между должником и
   кредиторами) в Г27 не исследовались — отдельный класс норм, кандидат в следующий батч: по букве UDMSA они ловят
   посредничество и получение средств, а не чистый совет, но проверка не проводилась.

### Процесс — прозрачно

Тип запроса: **breadth-first** (51 независимая юрисдикция + 3 самостоятельных под-вопроса). **Субагентов — ноль**:
всё снято вахтой, ради правила «сырьё в файл после каждой группы» и после падения на лимите аккаунта в середине
батча (обрыв произошёл на переходе к П3; записанное к тому моменту — П1 целиком, П2, П4 — уцелело, работа
продолжена с этого места на другом аккаунте). Записей в файл — **8 дописываний** по ходу.
Собственных `WebSearch` — 12. Каналы: прямой `curl` (leg.state.fl.us, azleg.gov, cga.ct.gov, delcode.delaware.gov,
code.dccouncil.gov, legis.iowa.gov, ksrevisor.gov, legislature.maine.gov, revisor.mo.gov, leg.mt.gov, ndlegis.gov,
rilegislature.gov (через прокси), scstatehouse.gov, legislature.vermont.gov, law.lis.virginia.gov, app.leg.wa.gov,
dfi.wa.gov, regs.maryland.gov, govinfo.gov, ecfr.gov, revisor.mn.gov, statutes.capitol.texas.gov (оболочка),
law.cornell.edu); `r.jina.ai` (Justia — 12 штатов, nysenate.gov, malegislature.gov, ilga.gov, codes.ohio.gov,
legislature.mi.gov, legislature.idaho.gov, nebraskalegislature.gov, oregonlegislature.gov, sdlegislature.gov,
le.utah.gov, code.wvlegislature.gov, docs.legis.wisconsin.gov, legis.state.pa.us, nasaa.org, gao.gov, leg.state.nv.us,
uscode.house.gov, files.consumerfinance.gov, financialplanningassociation.org).
Не прошли: govinfo по Title 12 (страница-ошибка на всех вариантах пути — лечится uscode.house.gov через прокси);
uscode.house.gov напрямую (соединение 000); files.consumerfinance.gov и consumerfinance.gov напрямую (403);
akleg.gov (JS-якорь без текста); gc.nh.gov (403), capitol.hawaii.gov (через прокси 924 б) — обойдены через Justia;
пять адресов Justia с неверным подразделом (AK, AR, HI, NH, NM) — исправлены поиском.
🔴 Замер канала: **`r.jina.ai` нельзя звать с браузерным User-Agent** — прокси в этом случае отдаёт капчу Cloudflare;
без UA тот же адрес отвечает 200.


---

## ДОБОР Г28 (16.09.2026)

**Состояние каналов на начало работы** (замер 16.09.2026, `curl -sk --http1.1`, таймаут 25 с):
`WebSearch` — доступен. `Exa` (`mcp__exa__*`) — 🟢 работает. `r.jina.ai` (без браузерного UA) — **HTTP 200**,
367 б. OpenAlex — **200**, 16 851 б. Crossref — **200**, 2 482 б. EuropePMC — **200**, 1 190 б.
**Wayback — 429** (117 б) на старте и **429** при повторной проверке через час: лежит, вопреки пометке 🟢
в задании. `pravo.gov.ru` — **200**, 27 995 б. `consultant.ru` — **200**, 47 360 б.
`gesetze-im-internet.de` — доступен и напрямую, и через прокси; 🔴 **`/gewo/__34k.html` отдаёт HTTP 404**
(216 б) — и это оказалось содержательным фактом, а не сбоем (см. ниже). `rkn.gov.ru` — **403**.

Область добора: пункт 7 очереди Г28 — § 34k GewO и статус Schuldnerberatung в немецком праве.
Пункты 1–6 (152-ФЗ, КоАП, РКН) — в файле `pdf_statement_parsing_accuracy_2026-09-13.md`.

### Пункт 7. Германия: нужна ли лицензия § 34k GewO для совета по УЖЕ СУЩЕСТВУЮЩЕМУ долгу

**Статус: добыто, включая текст нормы и материалы законодателя. Ответ: нет, не нужна — лицензия
привязана к заключению нового договора. Но найдена вторая, более близкая к нам преграда: RDG.**

#### 7.1. 🔴 Почему § 34k не открывался в Г26: его ещё нет в действующей редакции

`https://www.gesetze-im-internet.de/gewo/__34k.html` — **HTTP 404** и напрямую, и через `r.jina.ai`.
В оглавлении GewO (`https://r.jina.ai/https://www.gesetze-im-internet.de/gewo/index.html` — **HTTP 200,
30 760 б**) идут подряд «§ 34j Verordnungsermächtigung» → «**§ 34l Verordnungsermächtigung**»: **§ 34k
в оглавлении отсутствует**, при этом § 34l уже опубликован и на § 34k прямо ссылается.

Причина: **§ 34k вступает в силу 20.11.2026**, то есть через два месяца после даты этого добора.
Портал `gesetze-im-internet.de` публикует действующую редакцию и параграф ещё не показывает.
Подтверждение — карточка NWB Gesetze: «**§ 34k [tritt am 20.11.2026 in Kraft:] Darlehensvermittler**»
(`https://datenbank.nwb.de/Dokument/136661_34k/`, найдено через Exa, дата публикации карточки 19.07.2026).
Норма о вступлении — Art. 16 закона-имплементатора, дословно из Beschlussempfehlung BT-Drs. 21/5381:
«Artikel 16 Inkrafttreten (1) **Dieses Gesetz tritt vorbehaltlich des Absatzes 2 am 20. November 2026
in Kraft.** (2) Am Tag nach der Verkündung treten in Kraft: 1. Artikel 1 Nummer 6 Buchstabe c und Nummer 19,
**2. in Artikel 7 Nummer 6 § 34l der Gewerbeordnung** sowie 3. Artikel 15.»

То есть § 34l введён в силу на день после опубликования (чтобы министерство успело издать подзаконный акт),
а сам § 34k — только с 20.11.2026. Это ровно объясняет картину «§ 34l есть, § 34k 404».

#### 7.2. Закон-имплементатор: реквизиты

**«Gesetz zur Umsetzung der Richtlinie (EU) 2023/2225 über Verbraucherkreditverträge und zur Regelung
der Förderung klimaneutraler Mobilität».** Принят Бундестагом **17.04.2026**; опубликован в
Bundesgesetzblatt Teil I: `https://www.recht.bund.de/bgbl/1/2026/139/VO.html` (BGBl. I 2026 Nr. 139).
Правительственный проект — BT-Drs. **21/1851** (текст: `dserver.bundestag.de`, копия
`inkasso.de/fileadmin/user_upload/mitgliederinformationen/2025_09_29_RegE_21_1851.pdf`);
Beschlussempfehlung und Bericht профильного комитета — BT-Drs. **21/5381**
(`https://dserver.bundestag.de/btd/21/053/2105381.pdf`); отчёт бюджетного комитета — BT-Drs. **21/5382**.
Референтский проект BMJV — `https://www.bmjv.de/SharedDocs/Gesetzgebungsverfahren/DE/2025_VerbraucherkreditRL.html`
(RegE от 03.09.2025).

Срок транспозиции по Art. 48 Abs. 1 CCD II — 20.11.2025 — **Германией пропущен**; срок применения
Art. 48 Abs. 2 — 20.11.2026 — соблюдён. Формулировка Noerr, дословно: «Die in Art. 48 Abs. 1 VK-RL 2023
vorgesehene Umsetzungsfrist (20.11.2025) konnte damit – wie auch in anderen EU-Mitgliedstaaten – nicht
eingehalten werden. Der maßgebliche Anwendungszeitpunkt des 20.11.2026 gemäß Art. 48 Abs. 2 VK-RL 2023
wird gleichwohl gewahrt.» (`https://www.noerr.com/de/insights/gesetz-zur-umsetzung-der-verbraucherkreditrichtlinie-2023-beschlossen`,
17.04.2026 — **комментарий юрфирмы, не норма**.)

#### 7.3. § 34k Abs. 1 GewO — дословно (редакция, вступающая в силу 20.11.2026)

Источник текста: NWB Gesetze, карточка § 34k (через Exa).

> «(1) Wer gewerbsmäßig **gegen eine Vergütung**, die aus einer Geldzahlung oder einem sonstigen
> vereinbarten wirtschaftlichen Vorteil bestehen kann, **den Abschluss** von Allgemein-Verbraucher­
> darlehensverträgen nach § 491 Absatz 2 des Bürgerlichen Gesetzbuchs oder von Finanzierungshilfen
> nach § 506 Absatz 1 des Bürgerlichen Gesetzbuchs, mit Ausnahme von Verträgen im Sinne des § 34i
> Absatz 1 Satz 1, **vermitteln** oder **die Gelegenheit zum Abschluss solcher Verträge nachweisen**
> oder **Dritte zu solchen Verträgen beraten** oder **in anderer Weise beim Abschluss eines solchen
> Vertrages behilflich** sein will (Darlehensvermittler), bedarf nach Maßgabe der folgenden Bestimmungen
> der Erlaubnis der zuständigen Behörde.»

🔴 **Разбор четырёх альтернатив — это и есть ответ на вопрос Г26.** Все четыре грамматически подчинены
одному дополнению — «den Abschluss … von Verträgen»:
1. `vermitteln` — посредничество при **заключении**;
2. `die Gelegenheit zum Abschluss … nachweisen` — указание на возможность **заключить**;
3. `Dritte zu solchen Verträgen beraten` — консультирование **к таким договорам**, то есть к их заключению;
4. `in anderer Weise beim Abschluss … behilflich sein` — прямо «при **заключении**».

Третья альтернатива — единственная, где формально нет слова «Abschluss», и именно она давала сомнение
в Г26. Она снимается двумя внутренними подтверждениями из того же параграфа:

- **Abs. 5 Satz 1 Nr. 1** (о Honorar-Darlehensberater), дословно: «müssen **für ihre Empfehlung für oder
  gegen einen Allgemein-Verbraucherdarlehensvertrag** oder eine Finanzierungshilfe im Sinne des Absatzes 1
  **eine ausreichende Zahl von auf dem Markt verfügbaren Verträgen einbeziehen**». Требование «перебрать
  достаточное число доступных НА РЫНКЕ договоров» имеет смысл только для выбора **нового** продукта.
  К уже взятому долгу оно неприменимо по конструкции.
- **Abs. 5 Satz 1 Nr. 2**: консультант «dürfen vom Darlehensgeber für ihre Beratungsleistung keine
  Zuwendungen annehmen» — запрет вознаграждения от кредитора, то есть регулируется ситуация продажи.

Плюс внешнее подтверждение из материалов законодателя: в Gesetzesbegründung прямо выведены из-под
лицензии «Tippgeber» — те, кто лишь сводит потенциального заёмщика с кредитором (пересказ Noerr, дословно:
«dass "Tippgeber", die lediglich Kontakte zwischen potenziellen Darlehensnehmern und Darlehensgebern
herstellen oder einen Darlehensvermittler vermitteln, nicht unter die Erlaubnispflicht fallen»).

**Второй независимый фильтр — «gegen eine Vergütung».** Noerr, дословно: «Das Gesetz präzisiert, dass
die Erlaubnispflicht **nur bei der Vermittlung gegen eine Vergütung** eingreift, die aus einer Geldzahlung
oder einem sonstigen vereinbarten wirtschaftlichen Vorteil bestehen kann <…> Ein bloß mittelbar
angestrebter wirtschaftlicher Vorteil dürfte somit künftig keine Erlaubnispflicht für die
Darlehensvermittlung auslösen.» Вознаграждение должно быть **за посредничество/консультацию по договору**;
подписка за пользование софтом, не привязанная к заключению кредитного договора, под это не подводится.

**Что ещё нового в § 34k, важного для картины:**
- Abs. 3 Satz 1 Nr. 3 — обязательный **Sachkundenachweis** (экзамен в IHK) по «fachliche und rechtliche
  Grundlagen sowie Kundenberatung»; ранее по § 34c хватало Zuverlässigkeit и geordnete Vermögensverhältnisse.
- Abs. 4 Nr. 1 — исключение для кредитных институтов с лицензией § 32 Abs. 1 KWG.
- Abs. 4 Nr. 3 — исключение для микро-, малых и средних предприятий, которые ведут такую деятельность
  **лишь для финансирования собственных продаж товаров/услуг**.
- Abs. 5 Satz 2 — 🔴 **несовместимость ролей**: «Honorar-Darlehensberater dürfen keine Tätigkeit als
  Darlehensvermittler und Darlehensvermittler dürfen keine Tätigkeit als Darlehensberater ausüben.»
- Abs. 6 — обязанность непрерывного обучения; Abs. 7 — запрет привязки вознаграждения персонала
  к планам продаж; Abs. 8 — обязательная регистрация в реестре § 11a GewO.
- Переход (§ 162 GewO): держатели разрешения по § 34c должны подать заявление на новое разрешение
  **до 31.05.2027**, иначе старое гаснет **19.11.2027**.
- Сопутствующий подзаконный акт — «Verordnung zur Umsetzung der Richtlinie (EU) 2023/2225 über
  Verbraucherkreditverträge im Gewerberecht», BR-Drs. 320/26 (`https://dserver.bundestag.de/brd/2026/0320-26.pdf`):
  детализирует Sachkundeprüfung (три блока: Kundenberatung; fachliche Kenntnisse für die Vermittlung von
  und die Beratung zu Allgemeinverbraucherdarlehen; Finanzierung und Kreditprodukte), Weiterbildung
  и порядок регистрации. Оценка нагрузки на бизнес только от обязанности обучения — **62 794 000 евро в год**.

#### 7.4. § 511 BGB: что такое Beratungsleistung

Действующая (до 20.11.2026) редакция § 511 Abs. 1 BGB — дословно
(`https://r.jina.ai/https://www.gesetze-im-internet.de/bgb/__511.html` — **HTTP 200, 1 492 б**):

> «(1) Bevor der Darlehensgeber dem Darlehensnehmer **individuelle Empfehlungen zu einem oder mehreren
> Geschäften erteilt, die im Zusammenhang mit einem Immobiliar-Verbraucherdarlehensvertrag stehen
> (Beratungsleistungen)**, hat er den Darlehensnehmer über <…> zu informieren.»

Abs. 2, дословно: «Vor Erbringung der Beratungsleistung hat sich der Darlehensgeber über den Bedarf,
die persönliche und finanzielle Situation sowie über die Präferenzen und Ziele des Darlehensnehmers
zu informieren, soweit dies **für eine passende Empfehlung eines Darlehensvertrags** erforderlich ist.»
Abs. 3: «Der Darlehensgeber hat dem Darlehensnehmer <…> **ein geeignetes oder mehrere geeignete Produkte
zu empfehlen** oder ihn darauf hinzuweisen, dass er kein Produkt empfehlen kann.»

С 20.11.2026 та же конструкция распространяется на Allgemein-Verbraucherdarlehen (Art. 1 Nr. 28 закона;
ссылка на § 511 в новой ч. 1 § 506 BGB — из BT-Drs. 21/5381). **Ключевое:** Beratungsleistung во всех
редакциях определена через **рекомендацию ПРОДУКТА** — «Empfehlung eines Darlehensvertrags», «geeignete
Produkte empfehlen». Рекомендация «в каком порядке гасить уже имеющиеся долги» продуктом не является.

#### 7.5. Schuldnerberatung: требует ли немецкое право отдельного статуса

**Да — и это преграда, более близкая к нашему продукту, чем § 34k.** Механизм не лицензионный
(не GewO), а запретительный (RDG).

**RDG § 3, дословно** (`https://r.jina.ai/https://www.gesetze-im-internet.de/rdg/__3.html` — HTTP 200, 782 б):
«Die selbständige Erbringung außergerichtlicher Rechtsdienstleistungen ist unzulässig, soweit sie nicht
erlaubt wird durch dieses Gesetz oder durch oder aufgrund anderer Gesetze.» — **общий запрет** с оговоркой
о разрешениях, а не разрешительный порядок.

**RDG § 2 Abs. 1, дословно** (HTTP 200, 1 495 б): «Rechtsdienstleistung ist **jede Tätigkeit in konkreten
fremden Angelegenheiten, sobald sie eine rechtliche Prüfung des Einzelfalls erfordert**.»
Abs. 2 отдельно относит к Rechtsdienstleistung инкассо. Abs. 3 перечисляет, что ею НЕ является
(научные заключения, третейские и примирительные органы, обсуждение с представительствами работников).

**RDG § 8 Abs. 1 Nr. 3, дословно** (HTTP 200, 1 104 б): разрешены Rechtsdienstleistungen, которые
оказывают «**nach Landesrecht als geeignet anerkannte Personen oder Stellen im Sinn des § 305 Abs. 1 Nr. 1
der Insolvenzordnung**». Там же Nr. 4 — «Verbraucherzentralen und andere mit öffentlichen Mitteln
geförderte Verbraucherverbände».

**InsO § 305 Abs. 1 Nr. 1, дословно** (HTTP 200, 3 848 б): должник обязан приложить к заявлению
«eine Bescheinigung, die von einer **geeigneten Person oder Stelle** auf der Grundlage persönlicher
Beratung und eingehender Prüfung der Einkommens- und Vermögensverhältnisse des Schuldners ausgestellt ist
und aus der sich ergibt, daß eine **außergerichtliche Einigung mit den Gläubigern über die
Schuldenbereinigung auf der Grundlage eines Plans** innerhalb der letzten sechs Monate <…> erfolglos
versucht worden ist; <…> **die Länder können bestimmen, welche Personen oder Stellen als geeignet
anzusehen sind**.»

**Конструкция целиком:** внесудебная юридическая услуга запрещена (§ 3 RDG), если не разрешена; для
Schuldnerberatung разрешение даётся через признание земельным правом «geeignete Stelle» по § 305 Abs. 1
Nr. 1 InsO (§ 8 Abs. 1 Nr. 3 RDG). То есть **отдельный статус нужен, он признаётся землёй, а не
федерацией, и критерии у каждой земли свои.**

**Спасательный клапан — RDG § 5 Abs. 1, дословно** (HTTP 200, 805 б): «Erlaubt sind Rechtsdienstleistungen
im Zusammenhang mit einer anderen Tätigkeit, **wenn sie als Nebenleistung zum Berufs- oder Tätigkeitsbild
gehören**. Ob eine Nebenleistung vorliegt, ist nach **ihrem Inhalt, Umfang und sachlichen Zusammenhang
mit der Haupttätigkeit** unter Berücksichtigung der Rechtskenntnisse zu beurteilen, die für die
Haupttätigkeit erforderlich sind.» Abs. 2 называет три закрытых случая презумпции (Testamentsvollstreckung,
Haus- und Wohnungsverwaltung, Fördermittelberatung) — нас там нет, значит для нас работает только
общий тест Abs. 1.

**Косвенное подтверждение того, что законодатель видит Schuldnerberatung отдельным институтом:**
(1) BMJV прямо пишет, дословно: «**Weitere Regelungen zur Schuldnerberatung werden durch einen separaten
Referentenentwurf geschaffen**, der ebenfalls durch das Bundesministerium der Justiz und für
Verbraucherschutz erarbeitet wird» — то есть долговое консультирование регулируется ОТДЕЛЬНЫМ законом,
не этим; (2) новый **§ 18a Abs. 8c KWG** обязывает кредитные институты «Darlehensnehmer von AVD, die in
finanzielle Schwierigkeiten geraten sind, frühzeitig zu erkennen» и «diese Darlehensnehmer **an
Schuldnerberatungsdienste zu verweisen**» — банк обязан направить к Schuldnerberatung, а не оказывать её.

#### 7.6. Прямой ответ на вопрос пункта

**Нужна ли немецкая лицензия § 34k GewO для совета по УЖЕ СУЩЕСТВУЮЩЕМУ долгу? — Нет.**
Три независимых основания:
1. **Текст нормы.** Все четыре альтернативы § 34k Abs. 1 подчинены «den Abschluss … von Verträgen».
   Существующий долг договором, который предстоит заключить, не является.
2. **Внутренняя логика параграфа.** Abs. 5 требует от Honorar-Darlehensberater перебирать «доступные
   на рынке договоры» — операция, не имеющая смысла применительно к уже выданному кредиту.
3. **Определение Beratungsleistung в § 511 BGB** — это рекомендация **продукта** («Empfehlung eines
   Darlehensvertrags», «geeignete Produkte empfehlen»). Наш вывод «гаси лавиной: сначала долг под 29 %,
   потом под 17 %» рекомендацией продукта не является.

🔴 **Но ответ на исходный вопрос Г26 неполон, если остановиться здесь: в Германии нас ловит не GewO,
а RDG.** Совет «в каком порядке гасить долги» сам по себе вне RDG — это арифметика, а не
«rechtliche Prüfung des Einzelfalls». Но соседние функции переводят продукт под § 2 Abs. 1 RDG:
разбор конкретного кредитного договора на предмет ничтожности, расчёт последствий досрочного
погашения по конкретным условиям, подготовка Schuldenbereinigungsplan, переговоры с кредиторами.
**Это ровно тот же класс границы, что мы уже проводили по другим юрисдикциям: «расчёт и раскладка» —
можно, «оценка правовых последствий конкретного договора» — нельзя без статуса.**
Для Германии статус получается не лицензией предпринимателя, а признанием земли по § 305 Abs. 1 Nr. 1 InsO.

**Ограничение добытого:** § 34k ещё не действует (20.11.2026), поэтому **судебной практики и
административных толкований по нему нет и быть не может**. Текст получен из коммерческой базы
NWB Gesetze и из материалов законодателя (BT-Drs. 21/1851, 21/5381, BR-Drs. 320/26) — это надёжно,
но это текст и намерение законодателя, а не правоприменение. К вопросу вернуться после 20.11.2026.
Комментарий Noerr — **мнение юрфирмы**, использован только как подтверждающий пересказ Gesetzesbegründung,
а не как источник нормы.

## ИТОГ Г28 (пункт 7)

| Пункт | Статус | Норма или разъяснение со ссылкой | Что меняет для продукта |
|---|---|---|---|
| 7. Лицензия § 34k GewO для совета по существующему долгу | **добыто** | § 34k Abs. 1 GewO (вступает 20.11.2026; текст — NWB `datenbank.nwb.de/Dokument/136661_34k/`): все альтернативы привязаны к «den Abschluss … von Verträgen». Закон-имплементатор — BGBl. I 2026 Nr. 139, принят 17.04.2026; Art. 16 Abs. 1: «tritt … am 20. November 2026 in Kraft» (BT-Drs. 21/5381) | **Лицензия не нужна.** Наш модуль по существующим долгам под § 34k не подпадает: нет ни посредничества, ни указания на возможность заключить договор, ни рекомендации продукта, ни вознаграждения за посредничество |
| 7а. Почему § 34k не открывался в Г26 | **добыто** | `gesetze-im-internet.de/gewo/__34k.html` — HTTP 404; в оглавлении GewO § 34j → § 34l, § 34k отсутствует, потому что ещё не в силе | Технический факт для канона добычи: **404 на `gesetze-im-internet.de` может означать «норма принята, но не вступила», а не «нормы нет»** — проверять через NWB/BGBl./BT-Drucksachen |
| 7б. Schuldnerberatung: отдельный статус | **добыто** | § 3 RDG (общий запрет внесудебных юруслуг) + § 2 Abs. 1 RDG (определение) + § 8 Abs. 1 Nr. 3 RDG (разрешено «geeignete Stellen» по § 305 Abs. 1 Nr. 1 InsO) + § 305 Abs. 1 Nr. 1 InsO («die Länder können bestimmen, welche Personen oder Stellen als geeignet anzusehen sind») | 🔴 **Да, отдельный статус нужен — но только если деятельность дотягивает до Rechtsdienstleistung.** Признание даёт земля, не федерация. Для нас: расчёт порядка погашения — вне RDG; разбор конкретного договора, Schuldenbereinigungsplan, переговоры с кредиторами — внутри. Клапан — § 5 Abs. 1 RDG (Nebenleistung), но общим тестом, без презумпции |
| 7в. Сопутствующее, добытое попутно | **добыто** | § 18a Abs. 8c KWG (новая редакция): банк обязан выявлять заёмщиков в затруднении и направлять их «an Schuldnerberatungsdienste» | Рынок B2B: с 20.11.2026 у немецких банков появляется **законная обязанность направлять** — это спрос на канал, а не только на софт |

🔴 **Прямой ответ на вопрос батча: немецкая лицензия для совета по существующему долгу НЕ нужна.**
Преграда в Германии лежит не в GewO, а в RDG, и проходит она по той же линии, которую мы уже
провели в других юрисдикциях: считать и раскладывать — можно, оценивать правовые последствия
конкретного договора — нельзя без признанного статуса.

**Каналы по пункту 7.** Собственных `WebSearch` — 0; Exa `web_search_exa` — 1 (он и дал § 34k целиком
и BT-Drucksachen). `curl` через `r.jina.ai`: `gesetze-im-internet.de` (GewO index, § 34k, § 34l,
BGB § 511, InsO § 305, RDG §§ 2, 3, 5, 8) — все HTTP 200, кроме § 34k (404). Прямой `curl -sk --http1.1`
к `gesetze-im-internet.de` — работает, `-L` не требуется. `dip.bundestag.de` отдельно не понадобился:
`dserver.bundestag.de` и `recht.bund.de` найдены через Exa. `garant.ru`/`consultant.ru` к этому пункту
не применялись.

---

## ДОБОР Г30.3 — Exa (16.09.2026)

**Каналы на начало работы (16.09.2026, ~21:30 МСК):** Exa `mcp__exa__web_search_exa` — 🟢 работает (5 результатов на пробный запрос
про SEC no-action letters); `r.jina.ai` без UA → `sec.gov` **HTTP 200**, 13 806 б; OpenAlex **200**, 18 199 б; Crossref **200**, 2 472 б;
Wayback `web/2024/https://www.sec.gov/` **302** (жив); Wayback CDX для `docs.ozon.ru` — **503**, 11 832 б (мигает). `pdftotext` — есть.

Область: разделы «осталось неизвестным» блоков Г16, Г21, Г26, Г27, Г28 этого файла. Сверка с последним упоминанием выполнена:
Г16 «Ирландия» закрыта в Г21 (п. 5), «ОАЭ onshore» — в Г21 (п. 6), «territoriality UK» — в Г26 (п. 2), «штаты США» — в Г27 (51 из 51),
«§ 34k GewO» — в Г28, «CFPB» — в Г27. Открытыми на вход Г30.3 остались: (1) SEC no-action letters в оригинале + Champion;
(2) толкования CCD II Art. 3(17); (3) законы штатов о debt management services (хвост Г27 п. 8); (4) CFPB larger participants (Г27 п. 5);
(5) CT PA 17-120 — кодификация и санкция (Г27 п. 1); (6) Stripe — практика KYC для граждан РФ (Г16-Р); (7) MD функциональная ветка,
NRS 628A к иностранцу, UK s. 19 практика, CBUAE регламенты — второстепенные, проходятся по остатку бюджета.

### Г30.3-М1. SEC no-action letters: Champion (1986) и письма о financial planning — ЧАСТИЧНО (реквизиты и содержание по вторичным, оригинала нет)

**Что сделано.** Exa `web_search_exa` — 3 запроса («Robert R. Champion SEC no-action letter 1986…»; «SEC staff no-action letter software program
generates financial plan…»; «Champion 1986 … real estate coins precious metals…»). Скачаны и разобраны:
- Plaze, «Regulation of Investment Advisers by the U.S. SEC» (SEC DIM, апрель 2012), `https://marottaonmoney.com/wp-content/uploads/2020/05/rplaze-042012.pdf` —
  прямой `curl -sL` **HTTP 200, 411 315 б**, `pdftotext`;
- 45 Wash. & Lee L. Rev. 1139 (1988), «SEC Release 1092 on the Investment Advisers Act of 1940…» (студенческая Note),
  `https://scholarlycommons.law.wlu.edu/cgi/viewcontent.cgi?article=2389&context=wlulr` — 🔴 прямой `curl` с UA **HTTP 403, 5 651 б** (HTML-заглушка),
  **`mcp__exa__web_fetch_exa` — полный текст, ~59 КБ**. Это ровно класс «отказ инструмента ≠ отсутствие источника»;
- Proskauer, «Regulation of Investment Advisers by the U.S. SEC» (обновлённый Plaze, 2019+), `https://www.proskauer.com/insights/download-pdf/2460` — сниппеты Exa;
- датасет DOJ (зеркало `tommycarstensen.com/epstein/…/EFTA01074865.html`) — сниппет Exa; использован **только ради Westlaw-цитаты**, как источник низкого доверия.

**Первичка дословно.**

Plaze (SEC DIM, 2012), разд. II.A.3.a, с текстом сноски 7:
> «The SEC staff has stated that advice about real estate, coins, precious metals, or commodities is not advice about securities. 7 … The SEC staff has stated
> in this regard: (i) advice about market trends is advice about securities; (ii) advice about the selection and retention of other advisers is advice about
> securities; (iii) advice about the advantages of investing in securities versus other types of investments (e.g., coins or real estate) is advice about
> securities; (iv) providing a selective list of securities is advice about securities even if no advice is provided as to any one security; and (v) asset
> allocation advice is advice about securities.»
> «7 Robert R. Champion, SEC Staff No-Action Letter (Sept. 22, 1986).»

Proskauer (редакция Plaze) — то же, с разнесением: «advice about real estate, 17 coins, precious metals, or commodities is not advice about securities. 18»;
«17 Brighton Pacific Realty Asset Mgmt. Co., SEC Staff Letter (Feb. 10, 1992)…»; «18 Robert R. Champion, SEC Staff No-Action Letter (Sept. 22, 1986).»;
«22 RDM Infodustries … See Media General Financial Services, SEC Staff No-Action Letter (July 20, 1992). The letter notes that the staff does not believe
that information is … presented in a manner suggesting the purchase, holding, or sale of securities, where the customer or subscriber, and not the
information provider, selects the search criteria or requests that the service provide certain select information.»

DOJ-датасет (вторичный, неизвестный автор меморандума):
> «Advice about types of assets that are not securities, such as real estate, commodities, diamonds, precious metals, coins, and stamps, would not bring
> a person within the Advisers Act.' … 2 See, e.g., Robert R. Champion, SEC No-Action Letter, 1986 WL 68317 (Sept. 22, 1986); Thomas Beard, SEC No-Action Letter …»

45 Wash. & Lee L. Rev. 1139 (1988), текст и сноски 61–68:
> «In Sinclair-deMarinis an attorney asked the SEC whether Sinclair-deMarinis, a New York corporation dealing in numismatics, needed to register under the
> Advisers Act. … The SEC responded, first, that numismatics do not qualify as securities under section 202(a)(18) of the Advisers Act. Id. The SEC advised,
> therefore, that a business that provides advice solely on numismatics need not register under the Advisers Act. Id. The SEC indicated, however, that
> Sinclair might qualify as an investment adviser if Sinclair provided advice concerning the advisability of investing in numismatics relative to securities.»
> (Sinclair-deMarinis, Inc., SEC No-Action Letter, May 1, 1981; Thomas Beard, SEC No-Action Letter, May 8, 1975 — LEXIS, Fedsec library, Noact file)
>
> «[In] a no-action letter to Linda Arnold, for example, the SEC considered whether Ms. Arnold, a licensed dealer in life and health insurance and annuities,
> needed to register as an investment adviser. Ms. Arnold was considering whether to begin providing limited financial planning services to her clients.
> Ms. Arnold emphasized that she would restrict her recommendations to categories of investments and recommend no specific investments. Although Ms. Arnold
> stressed that she would neither hold herself out to the public as an investment adviser, provide analysis or reports on securities, nor have custody of
> clients' funds, the SEC responded that Ms. Arnold might qualify as an investment adviser under the Advisers Act. The SEC warned that if Ms. Arnold offered
> clients more than a general discussion of the advisability of investing in securities in the context of a conference concerning a client's financial plan,
> Ms. Arnold's activities might qualify her as an investment adviser. Furthermore, the SEC cautioned that advice concerning specific categories of investments
> such as bonds, mutual funds, and technology stocks also could qualify as investment advice under the Advisers Act.»
> (Linda Arnold, SEC No-Action Letter, Aug. 23, 1984; Southmark … Services, SEC No-Action Letter, 1984 — LEXIS)

**Выжимка.** Реквизит Champion уточнён: **1986 WL 68317**; по содержанию письмо — опора тезиса штаба SEC «совет о НЕ-ценных бумагах
(недвижимость, монеты, драгметаллы, товары) — не совет о ценных бумагах». Это позиция регулятора (staff), не закон. Для FINPILOT:
совет «гасить долг / пополнить резерв на счёте / копить на цель» — по той же логике совет о не-ценных бумагах; **но** пара Sinclair-deMarinis
и Linda Arnold проводит ту же границу, что IA-1092 (Г21): как только сравнивается «X против ценных бумаг» или называются **категории**
инвестиций (облигации, фонды) в контексте финплана — штаб допускает статус советника. Новое к словарю продукта: категории инструментов
(«облигации», «фонды») в выдаче — тоже риск, не только конкретные бумаги. Media General (1992): если критерии выбирает **пользователь**,
а не поставщик, — это не совет; подтверждает наш разграничитель «пользователь задаёт вход».

**Письма, специально посвящённые budgeting / debt / planning software, не найдены и в Г30.3**: три запроса Exa, индекс SEC (Г26) — отрицательно;
terms.law описывает письмо «FPL» о программе финпланирования и SunAmerica, но реквизитов (дата, номер) не даёт — **консультант, реквизиты
не проверяемы, в юрблок не брать**. Оригинал Champion — только Westlaw (1986 WL 68317) / LEXIS Fedsec Noact; открытого канала нет
(письма до 2001 г. на `sec.gov` не выкладываются — вывод из индекса SEC, Г26). Статус: **частично**, класс 2 (платная база).


### Г30.3-М2. Законы штатов о debt management services (хвост Г27 п. 8) — ✅ ДОБЫТО; 🔴 ловит ли нас: модель — НЕТ, Невада — СПОРНО

**Источники (все сняты 16.09.2026):**
- UDMSA (ULC, окончательный текст с официальными комментариями), `https://www.ftc.gov/sites/default/files/documents/public_events/consumer-protection-and-debt-settlement-industry/udmsafinal.pdf` —
  прямой `curl -sL` **HTTP 200, 422 105 б**, `pdftotext -layout`. Найден через Exa. Это модельный закон + комментарий разработчиков (не закон штата).
- Venable LLP, «Reflections on Five Years of the UDMSA», 01.07.2010 — сниппет Exa (мнение юрфирмы; перечень штатов со ссылками на кодексы).
- NRS ch. 676A (Невада), `https://www.leg.state.nv.us/NRS/NRS-676A.html` через `r.jina.ai` — **HTTP 200, 125 074 б**.
- 205 ILCS 665 (Иллинойс), `https://ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1203&ChapterID=20` — **`mcp__exa__web_fetch_exa`, полный текст акта**;
  🔴 прямой `curl -sk --http1.1` к `www.ilga.gov/…/020506650K2.htm` — **000 (таймаут 120 с)**, `r.jina.ai` на `ActID=1204` и печатную версию — 200, но
  **не тот акт** (ActID 1204 ≠ 665; моя ошибка адреса, исправлена через Exa).
- C.R.S. § 12-14.5-202 (Колорадо, ред. 2016) и Del. Code tit. 6 ch. 24A (Делавэр, ред. 2010) — сниппеты Exa с Justia.
- N.D.C.C. ch. 13-11, `https://ndlegis.gov/cencode/t13c11.pdf` — прямой `curl -sL` **HTTP 200, 142 186 б**: это «DEBT-SETTLEMENT PROVIDERS», не UDMSA.

**Первичка дословно.**

UDMSA § 2(9) (модельный текст):
> «(9) “Debt-management services” means services as an intermediary between an individual and one or more creditors of the individual for the purpose
> of obtaining concessions, but does not include: (A) legal services provided in an attorney-client relationship …; (B) accounting services provided in an
> accountant-client relationship …; or (C) financial-planning services provided in a financial planner-client relationship by a member of a
> financial-planning profession whose members the administrator, by rule, determines are (i) licensed by this state; (ii) subject to a disciplinary
> mechanism; (iii) subject to a code of professional responsibility; and (iv) subject to a continuing-education requirement.»
> «(7) “Concessions” means assent to repayment of a debt on terms more favorable to an individual than the terms of the contract between the individual and a creditor.»
> «(13) “Plan” means a program or strategy in which a provider furnishes debt-management services to an individual and which includes a schedule of payments
> to be made by or on behalf of the individual and used to pay debts owed by the individual.»

UDMSA, официальный комментарий к § 2, п. 8 (позиция разработчиков — ключевая для нас):
> «8. Paragraph (9) (debt-management services): The definition encompasses the activity of entities that act as an intermediary between an individual and
> the individual's creditors, for the purpose of changing the terms of the original contract between the individual and those creditors. There is no
> requirement that the individual's money flow through the provider. … The definition includes the services of credit-counseling entities even if the
> concessions offered by creditors are not subject to negotiation. **It does not include services that consist solely of counseling or education
> concerning the management of personal finance.** Nor does it include the activity of a creditor that compromises a claim with its debtor, because the
> creditor is not operating as an intermediary.»

Перечень принявших (Venable, 2010, с кодексами): «Utah became the first state to adopt the Act in 2006. Since then, the UDMSA has been adopted in six
additional jurisdictions, Colorado, Delaware, Nevada, Rhode Island, Tennessee, and the U.S. Virgin Islands.» — Utah Code § 13-42-101 et seq.;
Colo. Rev. Stat. § 12-14.5-201 et seq. (сейчас — C.R.S. §§ 5-19-201 — 5-19-242, Justia 2024); Del. Code tit. 6 § 2401A et seq. (у Делавэра —
«1 or more **unsecured** creditors»); Nev. Rev. Stat. ch. 676A; R.I. Gen. Laws ch. 19-14.8 (действует, Justia 2025); Tenn. Code Ann. § 47-18-5401 et seq.
(🟠 по адресу Justia `47-18-5402` сейчас лежит «Foreclosure-Related Rescue Services» — номер перенесён или часть отменена; не сверено);
V.I. Code Ann. tit. 12A. **Итого 6 штатов + Виргинские о-ва.** Принятий после 2010 г. в выдаче Exa не найдено (ND в 2011 принял собственный закон
о debt-settlement providers, не UDMSA). Страница ULC с картой принятий грузится скриптом — `r.jina.ai` 200/10 266 б, карты в тексте нет.

NRS 676A.140 (Невада) — 🔴 **отступает от модели**:
> «“Debt-management services” means services as an intermediary between an individual and one or more creditors of the individual for the purpose of
> obtaining concessions **and includes credit counseling, the development and implementation of debt-management plans and debt settlement services.**
> The term does not include: 1. Legal services … 2. Accounting services … 3. Financial-planning services provided in a financial planner-client relationship
> by a member of a financial-planning profession whose members the Commissioner, by regulation, determines are: (a) Licensed by this State; (b) Subject to a
> disciplinary mechanism; (c) Subject to a code of professional responsibility; and (d) …»
NRS 676A.110: «“Credit counseling” means **providing education and assistance to an individual concerning debts owed by the individual** which may include,
without limitation, the development and implementation of a debt-management plan.»
NRS 676A.300(1): «a provider may not provide debt-management services to an individual who it reasonably should know resides in this State at the time it
agrees to provide the services, unless the provider is registered under this chapter.»
NRS 676A.270(1)–(2): «This chapter does not apply to an agreement with an individual who the provider has no reason to know resides in this State …
does not apply to a provider to the extent that the provider: (a) Provides or agrees to provide debt-management, educational or counseling services to an
individual who the provider has no reason to know resides in this State …; or (b) **Receives no compensation for debt-management services** from or on behalf
of the individuals to whom it provides the services or from their creditors.»

205 ILCS 665/2 (Иллинойс, свой закон, не UDMSA):
> «"Credit counselor" means an individual, corporation, or other entity that is not a debt management service that provides (1) guidance, educational programs,
> or advice for the purpose of addressing budgeting, personal finance, financial literacy, saving and spending practices, or the sound use of consumer credit;
> or (2) assistance or offers to assist individuals and families with financial problems by providing counseling; or (3) a combination …»
> «"Debt management service" means the planning and management of the financial affairs of a debtor for a fee **and the receiving of money from the debtor
> for the purpose of distributing it to the debtor's creditors** in payment or partial payment of the debtor's obligations or soliciting financial
> contributions from creditors. The business of debt management is conducted in this State if … the debt management business solicits or contracts with
> debtors located in this State. … This term shall not include … (g) **Credit counselors, only when providing services described in the definition of
> credit counselor in this Section.**»
205 ILCS 665/3: «It shall be unlawful for any person to operate a debt management service … without first having obtained a license»; 665/16(a):
«Any person who engages in the business of debt management service without a license shall be guilty of a Class 4 felony.»

**🔴 Прямой ответ: ловит ли нас это определение?**
- **Модель UDMSA (UT, CO, DE, RI, TN, VI) — НЕТ.** Два независимых основания: (1) по тексту — нужен посредник между человеком и кредитором
  «for the purpose of obtaining concessions»; FINPILOT с кредиторами не контактирует и уступок не добивается; (2) официальный комментарий разработчиков
  прямо исключает «services that consist solely of counseling or education concerning the management of personal finance». Оговорка: комментарий
  ULC — толковательный материал, не закон штата; суды штатов его обычно учитывают, но не обязаны.
- **Иллинойс — НЕТ, и сильнее, чем в модели.** Лицензия нужна за связку «планирование + **получение денег должника для распределения кредиторам**»
  (союз «and»), денег мы не принимаем; кроме того, совет о бюджете и личных финансах — это «credit counselor», прямо выведенный из-под лицензии (g).
- 🔴 **Невада — СПОРНО, это новый риск.** Законодатель Невады дописал «and includes credit counseling», а «credit counseling» определил как
  «education and assistance to an individual concerning debts owed by the individual» — буквально наш долговой модуль. Грамматически возможны два
  прочтения: (а) credit counseling включается только как разновидность посредничества ради уступок (тогда нас не ловит); (б) credit counseling — самостоятельный
  вид DMS (тогда ловит и требует регистрации по 676A.300 для резидентов Невады). Толкования Nevada FID в выдаче нет. Изъятие 676A.270(2)(b)
  «no compensation» нам недоступно при платной подписке. Это **тот же штат**, где Г26–Г27 нашли NRS 628A (фидуциарий + E&O $1 млн) —
  Невада теперь проблемна по двум главам.
- **Практический вывод для L9:** в США долговой модуль безопасен в модельных штатах и в Иллинойсе; для резидентов **Невады** — геоблок долгового модуля
  или бесплатный режим для них до получения толкования (вывод из текста норм, не позиция регулятора).

**Не добыто по пункту:** текущий список принявших UDMSA из первоисточника ULC (карта — JS); проверка редакций UT, RI, TN, VI поштучно (использован перечень Venable 2010
и Justia для CO, DE, RI); толкование Nevada FID к 676A.140/110.


### Г30.3-М3. Толкования CCD II Art. 3(17) — официальных толкований НЕТ (подтверждено третий раз); 🔴 НОВОЕ: немецкий SchuBerDG § 4 — монополия «независимых» на Schuldnerberatung

**Что сделано.** Exa `web_search_exa` — 3 запроса (EN: Commission/EBA guidance; DE: Begründung § 511 BGB / Schuldnerberatung; DE: статус SchuBerDG).
Скачаны: BT-Drs. 21/1847 (правительственный законопроект SchuBerDG), `https://dserver.bundestag.de/btd/21/018/2101847.pdf` — прямой `curl -sL`
**HTTP 200, 252 996 б**; BT-Drs. 21/2774 (Beschlussempfehlung Rechtsausschuss), `https://dserver.bundestag.de/btd/21/027/2102774.pdf` — **HTTP 200, 244 513 б**;
страница Vermittlungsausschuss «Laufende Vermittlungsverfahren» через `r.jina.ai` — **HTTP 200, 12 655 б**. Сниппеты Exa: EUR-Lex (текст CCD II и
резюме legissum), COM(2021) 347 (предложение Комиссии), A&L Goodbody «CCD2 Report» (юрфирма), Ireland Department of Finance consultation,
ECDN «CCD II Transposition» (НКО), CEPS explainer (аналитика), BT-Drs. 21/5883, 21/5930, hib 12.05 и 15.05.2026, BAG-SB 08.05.2026, bundestagszusammenfasser.de.

**(а) Толкование Art. 3(17) на уровне ЕС.** Ни Q&A Комиссии, ни мнения/руководства EBA по «advisory services» CCD II в выдаче нет. Единственное
официальное пояснение сути Art. 16 — пояснительная записка Комиссии к проекту (COM(2021) 347), дословно по сниппету: «Article 16 (advisory services)
establishes standards to ensure that, where advice is given by the creditor, the credit intermediary or the provider of crowdfunding credit services,
consumers are made aware of this, without introducing any obligation to provide advice.» — это позиция Комиссии о **целях** нормы, а не о её охвате.
CEPS (2023, аналитика): «In other domains of financial services, implementing standards and guidelines have become widespread, but not for consumer credit»
— уровень 2 для CCD не предусмотрен, т. е. EBA-руководств по Art. 3(17) **и не ожидается** по конструкции директивы (вывод из обзора, не из акта).
Вывод Г21 (охват доказывается от противного через Art. 16(6)(b)–(c)) остаётся единственной опорой; опровержения нет.

**(б) Национальные позиции по Art. 16(6).** Ирландия (A&L Goodbody по итогам консультации Минфина, август 2025; юрфирма): «In Ireland, credit advisory services
can be provided to consumers by solicitors and accountants, as well as by personal insolvency practitioners and ‘MABS’. The Minister has decided that this
discretion should be exercised in a manner that facilitates these professional individuals and organisations …» — дерогацию 16(6) Ирландия использует
**только** для юристов, бухгалтеров, PIP и государственной MABS; коммерческого приложения в перечне нет. Позиций BaFin, AMF, Banca d'Italia в выдаче нет;
по ECDN (НКО) Италия и Франция на 2025 г. транспозицию статьи о debt advice не завершили.

**(в) 🔴 Германия: SchuBerDG — первичка дословно (BT-Drs. 21/1847 и 21/2774).**

§ 2 (законопроект; комитет его не менял):
> «Schuldnerberatungsdienst im Sinne dieses Gesetzes ist die individuelle fachliche, rechtliche oder psychologische Unterstützung von Verbrauchern, die
> Schwierigkeiten bei der Erfüllung ihrer finanziellen Verpflichtungen haben oder haben könnten. § 3 des Rechtsdienstleistungsgesetzes bleibt unberührt.»

Обоснование «Zu § 2» (21/1847):
> «Dabei kann die fachliche Unterstützung zum Beispiel **die Analyse der finanziellen Situation der Verbraucherin oder des Verbrauchers und darauf aufbauend
> Empfehlungen für den Umgang mit den finanziellen Verpflichtungen** umfassen. … Inhaltlich folgt der Begriff dem in Deutschland bereits etablierten Ansatz
> der Schuldnerberatung und begründet deshalb keine neue Kategorie bzw. kein neues Angebot der Schuldnerberatung.»

§ 4 в редакции, принятой Бундестагом 14.11.2025 (Beschlussempfehlung 21/2774):
> «(1) Schuldnerberatungsdienste nach § 2 darf nur erbringen, wer unabhängiger professioneller Anbieter ist.
> (2) Professionelle Anbieter sind solche Anbieter, die über ausreichende fachliche Kenntnisse sowie Wissen und Sachverstand in der Erbringung von
> Schuldnerberatungsdiensten nach § 2 verfügen.
> (3) Eine Unabhängigkeit ist insbesondere dann nicht gegeben, wenn es sich um folgende Arten von Anbietern handelt: 1. einen Kreditgeber oder einen
> Kreditvermittler …, 2. einen Kreditkäufer oder einen Kreditdienstleister …, 3. einen Anbieter, der auch zu Kredit-, Finanz- oder Versicherungsdienstleistungen,
> Dienstleistungen, die der Vermögensverwertung des Verbrauchers dienen, oder zu ähnlichen Dienstleistungen gewerblich berät oder diese erbringt oder
> vermittelt, oder 4. einen Anbieter, bei dem ein anderer als einer der in den Nummern 1 bis 3 genannten Interessenkonflikte vorliegt.
> (4) Unabhängige professionelle Anbieter von Schuldnerberatungsdiensten sind insbesondere Einrichtungen in der Trägerschaft von 1. Wohlfahrtsverbänden,
> Verbraucherzentralen, kreisfreien Städten, Landkreisen oder Gemeinden, 2. eingetragenen Vereinen …, 3. sonstigen juristischen Personen …, die ausschließlich
> und unmittelbar gemeinnützige oder mildtätige Zwecke verfolgen …»

§ 3 Abs. 1 в редакции Бундестага: «Die Schuldnerberatungsdienste sollen Verbrauchern kostenlos angeboten werden. In besonders begründeten Ausnahmefällen können
Schuldnerberatungsdienste abweichend von Satz 1 höchstens gegen ein begrenztes Entgelt angeboten werden. Dieses Entgelt darf maximal die Betriebskosten des
Anbieters für den Schuldnerberatungsdienst decken …»; обоснование 21/1847: «Um Betriebskosten handelt es sich dann nicht mehr, wenn die Einrichtung des Anbieters
eines Schuldnerberatungsdienstes das Ziel verfolgt, mit dem Entgelt einen Gewinn zu erwirtschaften.»

**Статус (на 16.09.2026):** Бундестаг принял 14.11.2025; Бундесрат **отказал в согласии 08.05.2026** (BT-Drs. 21/5883: «gemäß Artikel 104a Absatz 4 des
Grundgesetzes nicht zuzustimmen»); правительство **13.05.2026 созвало Vermittlungsausschuss** (BT-Drs. 21/5930); страница Vermittlungsausschuss на 16.09.2026:
«**Es liegt noch kein Termin für die Sitzung des Vermittlungsausschusses vor.**» Закон **не вступил в силу**; предмет спора — финансирование Länder (ст. 104a GG), а не § 2/§ 4.

**🔴 Что это меняет.** Если SchuBerDG вступит в нынешней редакции, в Германии «индивидуальная фактическая поддержка» потребителя, который «имеет или **может иметь**»
трудности с обязательствами, — в том числе, по обоснованию, «анализ финансового положения и рекомендации по обращению с обязательствами» — **может оказывать
только независимый профессиональный провайдер**, по общему правилу бесплатно, максимум за покрытие издержек без прибыли. Коммерческая подписка FINPILOT
с долговым модулем для немецких пользователей попадает под § 2 по букве и не проходит § 3 (прибыль); по § 4(3) Nr. 4 коммерческий интерес как «иной
конфликт интересов» — толкование не проверено. Это **сильнее** вывода Г28 по § 34k GewO («лицензия не нужна»): там вопрос о лицензии посредника, здесь —
о монополии статуса на сам совет. Смягчающие обстоятельства: (1) закон окончательно не принят; (2) адресат § 1 — Länder, и из текста неясно, задуман ли § 4
как запрет для всех рыночных лиц или как требование к тем, кого Länder засчитывают в сеть; **санкции за нарушение § 4 в тексте нет** — проверено `grep`
по снятым 21/1847 и 21/2774: «Bußgeld» и «Ordnungswidrigkeit» — 0 вхождений; (3) граница «haben könnten» (профилактика) не определена.
**Практически для L9:** до решения Vermittlungsausschuss немецкий долговой модуль — «не запускать без местного юриста»; ЕС-вывод Г21 это только усиливает.


### Г30.3-М4. CFPB larger participants (Г27 п. 5) и CT PA 17-120 (Г27 п. 1) — ✅ ДОБЫТО

**CFPB.** Источники: 12 CFR part 1090 — eCFR (оглавление, сниппет Exa) и govinfo `CFR-2025-title12-vol9-part1090.pdf` (сниппет Exa); CFPB
«Institutions subject to CFPB supervisory authority» (сниппет Exa); Final Rule 89 FR 99582 (10.12.2024). Дословно (CFR 2025, оглавление части 1090):
«1090.104 Consumer Reporting Market. 1090.105 Consumer debt collection market. 1090.106 Student loan servicing market. 1090.107 International Money Transfer
Market. 1090.108 Automobile financing market. 1090.109 General-use digital consumer payment applications market.» Страница CFPB (позиция регулятора):
«To date, this includes larger participants in the following markets: consumer reporting, consumer debt collection, student loan servicing, international
money transfer, and automobile financing.» Final Rule 2024: «nonbank covered persons generally are subject to the CFPB's regulatory and enforcement
authority and to applicable Federal consumer financial law» — независимо от надзора.
**Ответ:** рынка «credit counseling / debt management / budgeting» среди larger-participant рынков **нет** (6 из 6 просмотрены). FINPILOT не попадает
под плановый надзор CFPB как larger participant; остаётся вывод Г27 — covered person под UDAAP и enforcement. 🟠 Расхождение источников: CFR 2025
содержит § 1090.109, а страница CFPB перечисляет только пять рынков — вероятно, правило о платёжных приложениях отменено в 2025 г.; первоисточник
отмены не снимался (к нам не относится: мы не проводим платежей).

**Коннектикут PA 17-120.** Источник: `https://www.cga.ct.gov/2017/act/pa/2017PA-00120-R00HB-06992-PA.htm` (текст акта, сниппет Exa); OLR bill analysis
2016 SB-265 (сниппет Exa); Dechert OnPoint 03.04.2018 (юрфирма). Дословно, Sec. 1:
> «(a) … (2) "financial planner" means a person offering individualized financial planning or investment advice to a consumer for compensation where such
> activity is not otherwise regulated by state or federal law. (b) No financial planner shall, in connection with an agreement with a consumer to provide
> financial planning or investment advice for compensation, use a certificate, professional designation or form of advertising expressing or implying that such
> person has special training, education or experience in advising or serving senior citizens, unless … (c) A financial planner shall disclose to a consumer,
> upon request, whether or not such financial planner has a fiduciary duty to such consumer for each recommendation such financial planner makes to such consumer.»
Sec. 2 — только обязанность Banking Commissioner разместить образовательные материалы. Оба раздела помечены «(NEW) (Effective from passage)».
**Ответ:** акт действует с 05.07.2017 (Dechert); номер кодификации в C.G.S. в выдаче не найден; **санкции в тексте акта нет** (ни штрафа, ни ссылки на CUTPA —
вероятный канал остаётся гипотезой). Для нас обязанности прежние (Г27): не заявлять «senior»-квалификацию; по запросу пользователя из CT — ответить, есть ли
у нас фидуциарная обязанность. В продукт: шаблон ответа «FINPILOT не несёт фидуциарной обязанности» для резидентов CT.

### ИТОГ Г30.3 (regulation_world_advice_boundary)

| Пункт | Был статус | Стал | Приём |
|---|---|---|---|
| SEC no-action letters в оригинале, Champion 1986 | частично (2 письма), Champion не добыт | **частично**: Champion — реквизит 1986 WL 68317 + содержание (не-securities advice); +4 письма по вторичным (Sinclair-deMarinis 1981, Linda Arnold 1984, Media General 1992, Thomas Beard 1975); оригиналы — только Westlaw/LEXIS | Exa search ×3; **Exa fetch пробил 403** на W&L Law Review; Plaze через `curl` |
| Толкования CCD II Art. 3(17) (EC, EBA, BaFin, AMF, BdI) | не найдено | **отрицательный результат подтверждён** + Ирландия (дерогация 16(6) только для юристов/бухгалтеров/PIP/MABS) | Exa search ×2 |
| 🆕 Германия: SchuBerDG § 2–4 | не было в файле (Г16 знал только статус) | **добыт дословно**: монополия «независимых» провайдеров на Schuldnerberatung, бесплатность; закон в Vermittlungsausschuss без даты | Exa search → `curl` BT-Drs. 21/1847, 21/2774; `r.jina.ai` vermittlungsausschuss.de |
| Законы штатов о debt management (UDMSA) | не исследовались | **добыто**: модель и IL не ловят; 🔴 **NV спорно** (includes credit counseling); 6 штатов + VI | Exa search ×2, Exa fetch (ILCS, после 000 у `curl`), `curl` FTC PDF, `r.jina.ai` NRS |
| CFPB larger participants | не проверено | **добыто**: 6 рынков, credit counseling нет | Exa search |
| CT PA 17-120 кодификация и санкция | не найдено | **частично**: текст акта; кодификация не найдена; санкции в акте нет | Exa search |
| Stripe: практика KYC для граждан РФ (Г16-Р) | не добыто | **не пробовалось** в Г30.3 — бюджет ушёл на право ЕС/США; остаётся | — |
| MD функциональная ветка, NRS 628A к иностранцу, UK s. 19, CBUAE регламенты | не добыто | **не пробовались** — второстепенные | — |


---

## ДОБОР Г30.3 — второй заход (16.09.2026)

**Состояние каналов на начало (16.09.2026, 22:05–22:15 МСК, после смены аккаунта):** Exa `mcp__exa__web_search_exa` — 🟢 работает;
`r.jina.ai` без UA → `sec.gov` **200**; Crossref **200**; `cbr.ru` **200**; `web.archive.org/web/2024/…` — **302**, но
🔴 **Wayback CDX — 503 «Internet Archive: Temporarily Offline»** (канал мёртв на момент работы); **OpenAlex — 429** (был 200 накануне);
`rkn.gov.ru` — **000**, `pd.rkn.gov.ru` — **403**. Предыдущий заход оборвался на лимите аккаунта (HTTP 429) до первой записи — здесь всё с нуля.

### Г30.3-В1. 🔴 Перечень штатов, принявших UDMSA, по первоисточнику ULC — НЕ ДОБЫТ (причина точная)

Пройденные каналы:
- `https://www.uniformlaws.org/committees/community-home?CommunityKey=e327d09d-edb7-4f3c-95c9-f32a5679e7c1` — `r.jina.ai` **200, 10 236 б** и
  `mcp__exa__web_fetch_exa` **200**: в HTML присутствует только заголовок раздела «### Legislative Bill Tracking» и под ним **пусто**; данные подтягивает
  скрипт платформы Higher Logic. Ни одного названия штата в выдаче нет;
- `https://www.uniformlaws.org/api/legislation/bills?communityKey=…`, `…/HigherLogic/Legislation/LegislationList.aspx?CommunityKey=…`,
  `…/acts/catalog/current/d`, `…/legislation/activity` — прямой `curl` с UA, все **HTTP 200** (70 514 / 70 659 / 160 782 / 72 016 б), но это та же
  SPA-оболочка: `grep` по «utah|colorado|rhode island|nevada|enacted» — **ноль совпадений**;
- Wayback (снимок страницы акта, где карта принятий раньше была статической) — **CDX 503**, архив офлайн;
- Exa-поиск по запросу «uniformlaws.org … legislative enactment status map enacted states list» вернул ту же страницу ULC (пустую),
  каталог актов ULC (описание акта без статуса) и обзор Venable 2010.

**Что добыто вместо этого (первоисточники штатов и легислатур, не обзор):**
- Utah Code § 13-42-101 и далее; Colo. Rev. Stat. (ныне **C.R.S. §§ 5-19-201 — 5-19-242**, Justia, ред. 2024); Del. Code tit. 6 ch. 24A;
  **NRS ch. 676A** (снят целиком через `r.jina.ai`, 125 074 б); **R.I. Gen. Laws ch. 19-14.8** — подтверждена страница самой легислатуры
  `webserver.rilegislature.gov/Statutes/TITLE19/19-14.8/INDEX.htm` («Chapter 14.8 Uniform Debt-Management Services Act»); Tenn. Code Ann. § 47-18-5401 и далее;
  V.I. Code Ann. tit. 12A.
- Отчёт Joint Legislative Council Висконсина (PRL 2007-05, `docs.legis.wisconsin.gov`) фиксирует состояние на 2007 г. дословно: «The UDMSA has been adopted
  in three other states (Delaware, Rhode Island, and Utah) and introduced in at least three others (Colorado, Hawaii, and Missouri) to date» — то есть
  Гавайи, Миссури и сам Висконсин **вносили, но в перечне принявших не значатся**.
- Северная Дакота: `ndlegis.gov/cencode/t13c11.pdf` (**200, 142 186 б**) — глава 13-11 называется «DEBT-SETTLEMENT PROVIDERS», это **не** UDMSA.

**Вывод по пункту.** Состав «6 штатов + Виргинские острова» (UT, CO, DE, NV, RI, TN, VI) подтверждён **первоисточниками самих юрисдикций**, а не обзором 2010 г.
Чего первоисточник ULC мог бы добавить — принятия после 2010 г.; их наличие **не подтверждено и не опровергнуто**: страница статуса ULC отдаётся скриптом,
Wayback офлайн. 🔴 Это «не добыто» инструментальное, не содержательное; закрывается одним открытием страницы ULC в браузере с включённым JS.

### Г30.3-В2. Мэриленд, функциональная ветка § 11-101(i)(1)(ii)2 — ✅ ДОБЫТА ПРАКТИКА (толкования как такового нет)

Первоисточники — акты самого регулятора (Securities Commissioner of Maryland, публикуются на `oag.maryland.gov`), сняты через Exa:
- Summary Order, High Point (01.02.2018), `oag.maryland.gov/i-need-to/Documents/pdfs/Securities/2018/highpoint_summary_order_020118.pdf`;
- Order to Show Cause, Richards (11.02.2026), `…/Securities/2026/20250560_OSC_Richards_021126.pdf`;
- OSC, Yost (2013); Final Judgment, Morley / The New Wealth (18.12.2018).
Во всех четырёх Комиссар цитирует определение целиком, включая нашу ветку, дословно:
> «section 11-101(i) of the Act defines “investment adviser” to mean any person who, for compensation, … provides or offers to provide financial or investment
> counseling or advice; **or gathers information relating to investments, establishes financial goals and objectives, processes and analyzes the information
> gathered, and recommends a financial plan**; or holds out as an investment adviser in any way …»
🔴 **Но ни в одном деле ветка (ii)2 не является единственным основанием:** High Point — «referring to themselves as a “financial advisor”» и «wealth management»
в названии; Richards — советы по конкретным бумагам NovaTech; Morley — «executing financial planning agreements … investing the funds in securities products,
managing the securities portfolios»; Yost — «holding out as investment advisers, providing advice regarding securities».
**Ответ:** самостоятельного применения функциональной ветки к сервису **без securities и без титула** в практике Мэриленда не найдено; отдельного толкования
Division (no-action, FAQ, интерпретирующий приказ) в выдаче нет. Опора против нас в тексте остаётся прежней («information relating to **investments**»),
и теперь к ней добавлен фактический аргумент: регулятор в известных делах всегда имел второй крючок. Риск снижается с «вероятно да» до **«не подтверждён практикой»**.
Каналы: Exa-поиск (1 запрос), первоисточники — PDF с сайта Генпрокурора штата; `mgaleg.maryland.gov` отдаёт текст § 11-101 целиком (через индекс Exa),
хотя прямой фетч страницы в Г26 давал оболочку.

### Г30.3-В3. Stripe и бенефициар-гражданин РФ — ЧАСТИЧНО (первички Stripe нет, консультанты единогласны)

Пройденные каналы: Exa-поиск (1 запрос); ранее (Г16) — сама страница Stripe о запрещённых бизнесах и высокорисковых юрисдикциях (Россия по гражданству
там **не названа**), страница требований Stripe UAE — пустая, sanctions FAQ — 404.
Что добыто сейчас (всё — консультанты и форумы, первоисточника Stripe нет):
- wyomingllc.co (2026): «Stripe suspended services for Russian-connected accounts in March 2022. This restriction applies regardless of whether you operate
  through a Wyoming LLC. Russian passport holders face automatic rejection during Stripe's identity verification process»;
- usllcglobal.com (28.04.2026): «Founders applying from Pakistan, Bangladesh, Nigeria, Iran, Russia, Vietnam … trigger heightened scrutiny», рассматривается как
  риск-вес страны, а не запрет;
- edeal.ai (15.05.2026) — разбор через право, а не практику: OFAC Determination от 08.05.2022 к EO 14071 запрещает услуги «to any person **located in** the
  Russian Federation», и вывод консультанта: вид на жительство вне РФ снимает территориальный признак, «access to fintech infrastructure: Stripe, Wise, Mercury…»;
- reddit r/stripe (12.02.2026) и r/llc (21.05.2026) — отказы в верификации у резидентов ОАЭ без связи с гражданством РФ.
**Ответ:** прямых свидетельств Stripe (правило, письмо, страница) о гражданах РФ по-прежнему нет; консультанты сходятся, что **паспорт РФ на этапе KYC
ведёт к отказу**, а рабочий путь — резидентство вне РФ. Для L9 это остаётся риском уровня «практика поставщика», не нормой. Статус: **частично**,
причина — Stripe своей политики по гражданству не публикует, а проверить эмпирически мы не можем.

### Г30.3-В4. Невада, NRS 628A к автоматическому сервису и поставщику без присутствия — ЧАСТИЧНО (норма дословно, толкований нет)

Первоисточник — `https://www.leg.state.nv.us/NRS/NRS-628A.html` (через индекс Exa; ранее гл. 676A снята через `r.jina.ai`, 200/125 074 б),
дублирование — nevada.public.law. Дословно:
> «**NRS 628A.020 Duties of financial planner.** A financial planner has the duty of a fiduciary toward a client. A financial planner shall disclose to a client,
> at the time advice is given, any gain the financial planner may receive… A financial planner shall make diligent inquiry of each client to ascertain initially,
> and keep currently informed concerning, the client's financial circumstances and obligations and the client's present and anticipated obligations to and goals
> for his or her family.»
> «**NRS 628A.030.** … The circumstances giving rise to liability … are that the financial planner: (a) Violated any element of his or her fiduciary duty;
> (b) Was grossly negligent in selecting the course of action advised, in the light of all the client's circumstances known to the financial planner; or
> (c) Violated any law of this State in recommending the investment or service.»
> «**NRS 628A.040.** … a financial planner shall maintain insurance covering liability for errors or omissions, or a surety bond … in an amount of $1,000,000 or more.»
Подтверждение отраслевой аналитикой (ICI/IDC, «2017 Changes to Nevada's Financial Planner Law…»): «The law imposes **no registration, licensure, or qualification
requirements** on financial planners»; с 01.07.2017 (SB 383) из определения убраны изъятия для брокеров-дилеров и инвестсоветников. Отчёт OLR Коннектикута
(2017-R-0142) пересказывает то же.
🔴 **Чего нет:** ни одного решения суда Невады, мнения AG или разъяснения Securities Division о применении гл. 628A к **автоматическому** сервису и к поставщику
**без присутствия в штате**; территориальной нормы сама глава не содержит. Пройденные каналы: Exa-поиск (1 запрос), leg.state.nv.us, nevada.public.law,
justia, cga.ct.gov, idc.org; `nvsos.gov` — **Incapsula-заглушка** («Request unsuccessful»). Вывод Г26 остаётся: обязанности есть, регистрации нет,
применимость к нам — открытый вопрос, решается геоблоком или местным юристом.

### Г30.3-В5. 🔴 UK, территориальность s. 19 FSMA — ДОБЫТО, и это ПРЯМОЕ ПОПАДАНИЕ В НАШ СЛУЧАЙ

Первоисточник — заявление самого регулятора: FCA, «FCA takes action against Neil Woodford and W4.0 for operating without authorisation»,
`https://www.fca.org.uk/news/statements/fca-takes-action-against-neil-woodford-and-w40-operating-without-authorisation`, 08.06.2026 (текст из индекса Exa;
подтверждён The Guardian 08.06.2026 и FTAdviser 08.06.2026). Дословно:
> «The FCA has started civil proceedings against Mr Neil Woodford and W4.0. The FCA alleges that Mr Woodford and W4.0 are providing regulated investment advice
> and making financial promotions through the **subscription-based platform, www.w4pz.com**, without authorisation. In the FCA's view, the activity breaches
> **sections 19 and 21** of the Financial Services and Markets Act 2000 (FSMA). The FCA is seeking an injunction… **W4.0 is the trading name of W Four Point Zero
> FZE LLC and is registered in the United Arab Emirates.**»
Сопутствующее (вторичное, отраслевые обзоры): по делу FCA v HTX (High Court, 2026) — «For communications originating outside the UK, the test is whether the
promotion is **capable of having an effect in the UK**. There is no requirement to demonstrate that the firm actively targeted UK consumers. Accessibility alone
can be sufficient»; индикаторы, на которые ссылался регулятор: английский язык, приём фунтов, верификация по британским документам, доступность с британских
IP; защита — «effective geo-blocking, restricting UK-issued identification documents, removing GBP functionality».
Судебная первичка по s. 19 для интернет-деятельности (BAILII, взяты реквизиты): FCA v Avacade [2020] EWHC 2175 (Ch); FCA v 24HR Trading Academy [2021] EWHC 648 (Ch);
FCA v Skinner [2020] EWHC 1097 (Ch) — все о британских лицах, поэтому вопрос «иностранец через интернет» в них не решается; ближайший живой прецедент — именно W4.0.
**Ответ на пункт:** гипотеза Г26 подтверждена практикой: **регистрация за рубежом (включая фризону ОАЭ) не защищает**, FCA идёт в суд по ss. 19 и 21 против
подписочной платформы, обслуживающей британских резидентов. Для L9: единственная рабочая защита по UK — **фактический геоблок и отказ от британских атрибутов**
(язык/валюта/идентификация), а не юридическая конструкция. Оговорка: дело W4.0 — об **инвестиционном** совете (art. 53 RAO); наш контур — долговой (art. 39E),
прямого дела по нему нет, но территориальная логика общая для s. 19.

### Г30.3-В6. 🔴 ОАЭ: закон, на который опирался вывод Г21, ЗАМЕНЁН — DFL 14/2018 → **DFL 6/2025** (в силе с 16.09.2025)

Первоисточник — CBUAE Rulebook (консолидированный текст), через `r.jina.ai`:
- `…/rulebook/article-61-licensed-financial-activities` — **200, 18 707 б**, пометка «**DFL 6/2025 Effective from 16/9/2025 Status: In-Force**». Перечень
  лицензируемой деятельности целиком: «a. Taking deposits… b. Providing credit facilities… c. Providing funding facilities… d. Providing **open finance services**.
  e. currency exchange and money transfer… f. payment services using Virtual Assets. g. stored values services, retail payments and digital money services.
  h. **Arranging, promoting, marketing for Licensed Financial Activities.** i. Acting as a principal in financial products… j. insurance, reinsurance…»;
  п. 2: Совет директоров вправе «Add, delete, or amend activities … following consultation with the ‘Financial Stability Board’».
- `…/rulebook/article-60-prohibition-carrying-or-promoting-financial-activities-without-license` — **200, 17 547 б**: «1. No Person may carry on any of the
  Licensed Financial Activities without obtaining the required license… 2. Licensed Financial Activities shall only be carried on, **in or from within the State**,
  by Persons licensed… 3. **Promotion** of any of the Licensed Financial Activities and financial products shall only be carried on in or from the State…
  The promotion … shall mean any form of communication, by any means, aimed at inviting or offering to enter into any transaction… 7. No Person shall present
  themselves as a Licensed Financial Institution if they are not.»
**Что это меняет.** Вывод Г21 п. 6 («перечень исчерпывающий, совета в нём нет → в ОАЭ onshore мы вне лицензирования») **сохраняется и в новом законе**: ни
«financial consultation», ни «advice» в перечне ст. 61 нет. Но 🔴 **реквизит в файле устарел**: ссылаться нужно на **Federal Decree-Law No. (6) of 2025, Art. 61**
(в силе с 16.09.2025), а не на DFL 14/2018 в ред. 9/2021, и держать в уме ст. 60(2)–(3) — территориальный критерий «in or from within the State» и отдельный
запрет промоушена. Осторожность по п. «h» («arranging, promoting, marketing for Licensed Financial Activities») сохраняется в прежнем виде: партнёрская выдача
кредитов переводит нас под лицензию.
**Подзаконка Совета директоров и режим SCA:** перечень лицензий SCA добыт (документ SCA «Licensing of the financial activities and jobs approval»,
`sca.gov.ae/assets/7949008c/…`, из индекса Exa): пятая категория — «Arrangement and advice», в перечне активностей значатся «**Financial Consultations**»,
«Financial advisor (issuance manager)», «Listing advisor», причём ст. 2: «No financial activity may be practiced unless after obtaining a license and/or approval…
from the Authority», а сфера — «any person who practices any of the financial activities … **inside the state**». 🟠 То есть **«финансовые консультации» в ОАЭ
лицензирует SCA, а не CBUAE** — и это ровно тот режим, который Г21 не проверял. Наш модуль не касается ценных бумаг, а перечень SCA построен вокруг рынка
капитала; но вывод «в ОАЭ во всех контурах мы вне лицензирования» теперь требует оговорки: **режим SCA «Financial Consultations» не исследован дословно**
(прямой `curl` к `uaelegislation.gov.ae` — **403**, `r.jina.ai` — 403 + капча Cloudflare; текст SCA взят из индекса Exa, постатейно не сверялся).

### Г30.3-В7. Коннектикут PA 17-120: кодификация и санкция — ✅ ОТВЕТ ПОЛУЧЕН (акт НЕ кодифицирован)

Первоисточники (Exa): текст акта `cga.ct.gov/2017/act/pa/2017PA-00120-R00HB-06992-PA.htm`; глава 672a C.G.S. `cga.ct.gov/current/pub/chap_672a.htm`;
анализ OLR к предшествующему законопроекту 2016 SB-265; страница Департамента банковского надзора `portal.ct.gov/DOB/Consumer/Consumer-Education/Choosing-A-Financial-Planner`.
Оба раздела акта помечены «**(NEW) (Effective from passage)**» и **не привязаны к статье C.G.S.**; в действующей главе 672a («Uniform Securities Act»,
§§ 36b-2 — 36b-34) норм о «financial planner» нет — § 36b-4(c) регулирует senior-обозначения только «in connection with the offer, sale or purchase of any security».
Сам акт ссылается на § 36b-4 лишь как на стандарт сертификата: «unless such person has obtained a certificate, title or designation as described in section 36b-4
of the general statutes».
**Ответ:** PA 17-120 остался **некодифицированным публичным актом** (действует с 05.07.2017 сам по себе); отдельной санкции в нём нет — ни штрафа, ни ссылки
на CUTPA. Гипотеза Г27 о CUTPA как канале ответственности **не подтверждена и не опровергнута**: в тексте акта её нет, практики не найдено.
Для продукта обязанности прежние и дешёвые: не заявлять senior-квалификацию; по запросу резидента CT отвечать, есть ли фидуциарная обязанность.

### Г30.3-В8. Пункты, по которым непройденных каналов не осталось

- **SEC no-action letter Robert R. Champion (1986 WL 68317)** — оригинал доступен только в Westlaw/LEXIS (Fedsec Noact). Пройдено: индекс SEC (Г26),
  Exa ×3 (Г30.3 первый заход), открытые репозитории. Открытых каналов больше нет; содержание письма известно из Plaze (SEC DIM) и Proskauer. **Закрываю как «частично, класс 2 (платная база)».**
- **Толкования CCD II Art. 3(17) Комиссией/EBA** — пройдено: Exa ×2, EUR-Lex, страница Комиссии по consumer protection, CEPS-обзор. Уровень 2 для CCD
  не предусмотрен (CEPS), Q&A Комиссии по директиве не публикуется. **Закрываю как доказанный отрицательный результат** с оговоркой: национальные позиции
  (DE — § 511 BGB и SchuBerDG, IE — дерогация 16(6)) добыты и заменяют отсутствующее толкование ЕС.
- **Stripe по гражданству бенефициара** — пройдено: страница Stripe (Г16), Exa ×1; политики по гражданству Stripe не публикует. **Частично, дальше — только эмпирика.**


---

## ДОБОР Г31.1 — Wayback (16.09.2026)

**Состояние каналов (замер 16.09.2026 19:32–20:50 UTC; системная дата среды — 16.09):**
`wayback/available` — 429 с редкими окнами 200; `cdx/search/cdx` — **503** «Temporarily Offline»;
🟢 replay `web/<ts>[id_]/<URL>` — **200** при паузе ≥ 18 с; `archive.ph` — 200, «No results»
по нужным адресам; Common Crawl — шлюз запросов **504**; DTIC — техобслуживание второй день.

### Г31.1-П1. Перечень штатов, принявших UDMSA — ❌ НЕ ДОБЫТО, канал исчерпан

**Что искали:** список принявших штатов на `uniformlaws.org`, который на живом сайте
подгружается скриптом (блок «Legislative Bill Tracking» / Enactment Map).

**Пройденные каналы, все с кодами:**

| Канал | Результат |
|---|---|
| Живой сайт, `curl` с браузерным UA, верный CommunityKey `e327d09d-edb7-4f3c-95c9-f32a5679e7c1` | **200, 106 856 б** — но блок «Legislative Bill Tracking» пуст, в HTML только теги `#ConsumerProtectionandLabor`, `#BusinessOrganizations`, `#UniformAct` |
| `r.jina.ai` без браузерного UA (по канону) | **200, 10 236 б** — полный отрендеренный текст страницы, **списка штатов в нём нет**; видны только «Related Versions: Debt-Management Services Act 2008 / 2005» и три документа библиотеки (Enactment Kit, Final Act, Committee Archive) |
| Разбор HTML на предмет эндпоинта данных | найден только сторонний хост `api.connectedcommunity.org` (Higher Logic); именованного эндпоинта карты принятия в разметке нет |
| Wayback replay, снимок **23.05.2024 11:21:03 UTC** (200, 143 322 б) | **тот же пустой блок** — виджет не отрабатывал и в момент съёмки |
| Wayback, легаси-адреса `uniformlaws.org/Act.aspx?title=Debt-Management+Services+Act` и `/LegislativeFactSheet.aspx?title=…` (на старом сайте карта была в HTML) | **404** — «has not archived that URL», обе формы (`+` и `%20`) |
| `archive.ph` (захватывает отрисованный JS, поэтому пробовался специально) | **404 / «No results»** — снимков этой страницы нет вовсе |

🔴 **Вывод по каналу, а не по вопросу:** список принявших штатов **не существует в виде
статического текста ни в одной сохранённой редакции страницы** — ни в архиве Wayback за 2024,
ни в archive.today, ни в легаси-адресах. Виджет Higher Logic рендерит его из стороннего API,
который архивы не сохраняют. Добор по Wayback этот пункт закрыть **не может в принципе**, и
дальнейшие попытки по этому каналу бессмысленны — пункт переводится из класса 4 («лежал чужой
сервис») в **класс 2** (нужен headless-браузер либо ручное открытие владельцем).

**Что есть взамен, чтобы пункт не остался пустым (вторичный источник с постатейными
ссылками на кодексы, найден через Exa).** Venable LLP, «Reflections on Five Years of the Uniform
Debt-Management Services Act», 21.07.2010 — по состоянию **на июль 2010 года**:

> «the UDMSA was approved by the National Conference of Commissioners on Uniform State Laws
> in 2005, and **Utah** became the first state to adopt the Act in 2006. Since then, the UDMSA
> has been adopted in six additional jurisdictions, **Colorado, Delaware, Nevada, Rhode Island,
> Tennessee, and the U.S. Virgin Islands**.»

с постатейными ссылками: Utah Code § 13-42-101 et seq. (в силе с 01.01.2007); Colo. Rev. Stat.
§ 12-14.5-201 et seq. (01.01.2008); Del Code tit. 6 § 2401A et seq. (17.01.2007);
Nev. Rev. Stat. § 676A (01.07.2010); R.I. Gen. Laws § 19-14.8 (01.07.2007);
Tenn. Code Ann § 47-18-5401 et seq. (01.07.2010); V.I. Code Ann tit. 12A (27.06.2010).

И там же — важная для нас пропорция, объясняющая, почему счёт именно по UDMSA вторичен:

> «Overall, today **49 states have what we consider to be a debt adjusting statute**, which are
> the primary state laws that regulate the industry. In 2005, out of the states that had debt
> adjusting statutes, **about 25 required licensing. That number has since risen to about 37.**»

🔴 **Содержательная поправка к постановке вопроса.** Считать «сколько штатов приняли UDMSA»
— мерить не ту величину. Единообразный акт приняли 7 юрисдикций, но **debt adjusting statutes
есть у 49 штатов**, и лицензирование требуют около 37. Риск для нас определяется вторым числом,
а не первым: попасть под лицензирование можно в штате, который UDMSA никогда не принимал.
Это согласуется с хвостом Г27 («законы штатов о debt management services / debt adjusting —
отдельный класс норм, и он к нам ближе, чем режим советников»). 🟡 Числа 49 и 37 — **по
состоянию на 2010 год и из вторичного источника**; как актуальные их брать нельзя, нужен
поштучный проход по кодексам (открытая задача Г27).

## ИТОГ Г31.1 (в этом файле)

- Пунктов класса 4, отработанных здесь: **1** (перечень штатов UDMSA).
- Закрыто снимком: **0**.
- 🔴 Переклассифицировано: **1** — из класса 4 в класс 2 (архивы этот пункт закрыть не могут
  принципиально, нужен headless-браузер).
- Побочный результат: вопрос переформулирован — считать надо debt adjusting statutes
  (≈ 49 штатов, ≈ 37 с лицензированием, данные 2010 г.), а не принятия UDMSA (7 юрисдикций).
