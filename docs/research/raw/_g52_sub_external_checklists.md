# Тема Г52 — внешние чек-листы QA + боли пользователей PFM/финтех

Дата: 2026-09-18. Статус: ЗАВЕРШЕНО (бюджет 12/12 вызовов добычи использован).

Скоуп: (А) чужие чек-листы/таксономии тест-кейсов для финансовых приложений;
(Б) боли реальных пользователей PFM/банковских приложений из отзывов и форумов
(включая русскоязычные vc.ru, habr.com, klerk.ru, buh.ru).
НЕ входит: рынок, конкуренты, монетизация, ML/LLM.

## §1. Чек-листы и таксономии QA (по темам)

### 1.1 Импорт банковских выписок (дубли, повторная загрузка, битый файл, кодировка, сальдо)

[ЧЕК-ЛИСТ QA] "Bank Statement Data Validation: 10-Point Quality Checklist" — https://www.easybankconvert.com/articles/bank-statement-data-validation (обращение 2026-09-18):
> "1. Balance reconciliation: Starting + transactions = ending (±$0.01)
> 2. Transaction count: PDF count = CSV count (exact match)
> 3. Duplicate detection: Zero duplicate transactions (same date/amount/description)
> 4. Date continuity: Chronological order, no gaps, within statement period
> 5. Sample verification: 10-20 random transactions match PDF exactly
> 6. Amount format: Proper negatives, 2 decimal places, no $€£ symbols
> 7. Description completeness: No truncated or corrupted text
> 8. Running balance: Calculated balance matches statement column
> 9. Character encoding: €, £, ñ, ü display correctly (UTF-8)
> 10. Import test: CSV actually imports to accounting software"
Пороги ошибок по расхождению баланса (эвристика для диагностики):
> "Difference < $10: Check for single missing/duplicate transaction; Difference = multiple of $100: Likely misread hundreds digit; Difference = ~half of balance: Sign error; Difference > $1,000: Re-convert PDF, check for multi-page extraction failure"

[ЧЕК-ЛИСТ QA] "QBO Import Prep Checklist" — https://www.wesley-ai.co/templates/qbo-import-prep-checklist (обращение 2026-09-18):
> "1. SOURCE AND PERIOD — Correct client and bank/card account selected; Correct statement period or historical range; All required statements for the batch are included
> 2. ROW QUALITY — Dates look correct...; No obvious statement headers, totals, or non-transaction rows remain
> 3. AMOUNT AND SIGN CHECK — Deposits are positive; Payments and withdrawals are negative; No obvious sign flips remain
> 4. DUPLICATES AND TRANSFERS — Duplicate rows have been reviewed; Obvious transfers are identified
> 6. EXCEPTION CHECK — Large unusual items have support or notes; Owner transactions are flagged or resolved; Unclear deposits have been classified or escalated"
Частые причины провала импорта: "Wrong sign behavior and wrong export format... Wrong direction on deposits and withdrawals; Duplicate rows from OCR or overlapping pages; Uploading to the wrong QuickBooks Online account."

[СТАНДАРТ] Microsoft Dynamics 365 — "Reconcile bank statements (advanced bank reconciliation)" — https://github.com/MicrosoftDocs/dynamics-365-unified-operations-public/blob/main/articles/finance/cash-bank-management/reconcile-bank-statements-advanced-bank-reconciliation.md (обращение 2026-09-18). Формальные правила валидации выписки перед импортом:
> "Bank statement validation verifies: The bank statement matches the selected bank account. The bank statement currency matches the bank account currency. The opening balance of the statement equals the closing balance of the previous statement for the bank account. The date doesn't overlap the date for another bank statement for the same bank account. Dates on the statement lines are between the from-date and to-date of the bank statement. The opening balance and summarized line amounts equal the ending balance."
Дедупликация: "To prevent the import of duplicate bank statements, the system checks the combination of AccountNo, StatementID, FromDate, and ToDate. If these elements match an existing bank statement, the system considers it a duplicate and doesn't import it."
Погрешность копеек при сверке: "Penny differences might occur in your reconciliation... if the penny differences are within the tolerance amount that is defined by the Allowed penny difference field."

[БЛОГ-ВЕНДОР] "Idempotent bank statement imports: why file hash matters" — https://www.gestio.dev/blog/idempotent-bank-statement-import-file-hash (обращение 2026-09-18):
> "importing the same statement file again does not create duplicates... A file hash (e.g., SHA-256 over the file contents) gives you a deterministic identifier... Alternative keys are weaker: filename is not reliable (files get renamed); statement dates are not unique (banks reissue exports); row counts are not unique."
Кейс "тот же файл, но переэкспортированный иначе": "Banks often re-export the same period with: reordered rows; extra header rows; formatting changes. Those changes will alter the hash... treat this as a different file import."

[ЧЕК-ЛИСТ QA / СТАНДАРТ] "Bank Ingestion Procedures" (ISO 20022 CAMT.052/053) — https://cfdoc.unitedtalent.com/client-processing/foundation/procedures/bank-ingestion (обращение 2026-09-18). Дедупликация в две стадии:
> "Compute content_hash = SHA-256 of the raw XML string. Query bank_file WHERE content_hash = computed hash. If a match exists, reject — this is an exact content duplicate... If no content hash match, query bank_file WHERE source_bank_id = sourceBankId AND message_id = extracted message_id. If a match exists, reject — this is a semantic duplicate (same message from same bank)."
Обработка реверсов (сторно) отдельным потоком, не автоматически: "Because reversals carry direct financial risk, they must not be processed automatically — a cash processor must explicitly accept or reject each reversal."
Несопоставленные счета: "Log a warning for any account identifiers in the file that have no matching bank_account record; those transactions will be skipped. If no accounts match at all, reject the upload with an error listing the unmatched account identifiers."

[БЛОГ-ВЕНДОР] "Bank Statement Processing: The Complete Guide" — https://flowparse.io/bank-statement-processing-guide (обращение 2026-09-18). Пять типов ошибок на этапе валидации:
> "Balance continuity — opening + transactions must equal closing, page to page. Duplicate detection — the same transaction captured twice is caught and flagged. Missing-row detection — a gap in the running balance reveals a dropped line. Date ordering — out-of-sequence dates surface OCR or layout problems."
Частые ошибки процесса: "Skipping the balance check... Processing an incomplete set...; Using a generic CSV export when a real QBO/QFX/OFX feed would import cleanly."

### 1.2 Расчёты / амортизация / кредитные калькуляторы

[ЧЕК-ЛИСТ QA / СТАНДАРТ] "Loan Calculator Conformance Test" (Make It Exact) — https://makeitexact.com/loan-conformance (обращение 2026-09-18). Публичный корпус тест-кейсов на 2688 кредитов:
> "The corpus is the product of 12 amounts, 14 rates and 16 terms... The edges are the point: a rate of exactly zero, where the closed form divides by zero unless somebody thought about it; a loan with a single instalment; forty years, where floating point starts to matter; and amounts with pennies in them, where premature rounding shows."
Конвенции, которые часто путают с ошибками: "nominal against effective against APR — different quantities, not different answers; 30/360 against Act/365 against Act/Act day counts; rounding every month against rounding at the end; an adjusted final payment; an irregular first period."
Инвариантные свойства (метаморфное тестирование): "doubling the amount doubles the payment, a higher rate never lowers it, and a longer term lowers the payment while raising total interest."

[БЛОГ / ИНЖЕНЕРНЫЙ РАЗБОР] "Building a Deterministic Amortization Schedule Engine" — https://pratikdhanave.com/blog/posts/fintech-amortization-schedule-engine.html (обращение 2026-09-18):
> "Work in integer minor units and a Decimal for the periodic rate, and choose one rounding mode — half-even is the usual pick to avoid a systematic bias toward the lender."
Day-count конвенции как источник расхождений: "30/360... ACT/365F... ACT/360, which quietly inflates the effective annual rate... ACT/ACT... A loan booked at '12% per annum, monthly' pays a different amount under 30/360 than under ACT/365F."
Инвариант последней строки: "the last installment is forced to repay exactly the remaining balance... sum of principal components equals the original principal, and the final balance is exactly zero."
Негативная амортизация как баг, который надо отклонять: "the engine should reject that at construction time, not emit a schedule where the balance grows."
Тест-семьи: "golden fixtures... invariant property tests... event replay: apply a prepayment or rate change, then confirm the frozen prefix is unchanged and the recomputed tail still closes to zero."

[БЛОГ] "Decoding an Amortization Schedule: How to Audit a Mortgage Calculator's Output Row by Row" — https://dev.to/lizely/decoding-an-amortization-schedule-how-to-audit-a-mortgage-calculators-output-row-by-row-41c1 (обращение 2026-09-18). Три быстрых теста для аудита калькулятора:
> "Test 1 — Interest matches the monthly rate times the prior balance... Test 2 — Principal plus interest equals the scheduled payment... Test 3 — The closing balance of the final row is exactly zero. Not 'close to zero,' not '0.00000003.'"
Крайние случаи структуры кредита: "Adjustable-rate or hybrid ARM... The schedule must regenerate the payment at every reset — otherwise you get either negative amortization... Interest-only period followed by amortization... A schedule that silently extends the term instead of recalculating is a known bug pattern."
Проверка через midpoint: "At month n/2, roughly half the principal should have paid down... anything outside the [40%, 60%] band for a 30-year fixed usually indicates an off-by-one in the term input."

[СТАНДАРТ / ОЦЕНКА] "Lending Systems – Fintech Engineering Handbook" — https://handbook.fintechengineer.io/chapters/money/lending-systems.html (обращение 2026-09-18). Крайние случаи, специфичные для долгоживущих систем:
> "Payment Reversals After Interest Recalculation — A payment is applied, reducing the principal. The accrual engine runs overnight... The next day, the payment is reversed (NSF, chargeback, dispute). The principal balance goes back up – but yesterday's accrual was calculated on the wrong balance."
> "Leap Years and Day-Count Edge Cases — Under Actual/365, February 29 is a real accrual day – but the denominator is still 365, not 366. Under Actual/Actual, the denominator changes to 366 in a leap year... Test your day-count implementations with leap year boundaries, month-end boundaries, and year-end boundaries explicitly."

[ЧЕК-ЛИСТ QA / open-source] mortgagemath README + commit — https://github.com/murraystokely/mortgagemath (обращение 2026-09-18). Реальные баги, найденные при доведении покрытия до 100%:
> "annual_rate <= 0 now raises ValueError instead of letting Decimal raise InvalidOperation deep inside the closed-form formula. The 0% case is mathematically undefined for the annuity formula."
> "amortization_period_months < term_months now raises. Previously this silently produced negative balances (e.g. amort=60 / term=120 gave balance=-$128k at month 120 with no error)."
> "amortization_period_months <= 0 now raises. Previously 0 silently fell through to term_months due to Python's `or`-truthiness."
Тест на месяц-конец в леапгод: "TestActual360Invariants.test_final_balance_is_zero (with start_date in the same calendar month as a 31-day month, a 28-day month, and a 29-day leap-year February)."

[ЧЕК-ЛИСТ QA / open-source] npm `loan-amortization-calculator` README — https://registry.npmjs.org/loan-amortization-calculator (обращение 2026-09-18). Даты конца месяца:
> "Generating payment dates for month-end originations requires care: a loan originating on January 31 should produce payments on the last day of every subsequent month (Feb 28/29, Mar 31, Apr 30, …), not on a fixed day-of-month."
Финальный платёж поглощает остаток округления: "The final (nth) payment exists to absorb accumulated cent-level rounding error... Treating the last payment as a clean-up ensures the ending balance is always exactly zero."

### 1.3 Мультивалютность

[ЧЕК-ЛИСТ QA] "How to test multi-currency and cross-border payment features" (DeviQA) — https://www.deviqa.com/blog/how-to-test-multi-currency-and-cross-border-payment-features-the-complete-qa-guide/ (обращение 2026-09-18). Ключевой антипаттерн: "Currency amounts must never be stored or calculated using floating-point data types (float, double)... 0.1 + 0.2 in float doesn't equal exactly 0.3. Across millions of transactions, these imprecisions accumulate."
Точность по ISO 4217: "Test that JPY amounts display as whole numbers, ¥1,000, not ¥1,000.00... Test KWD and BHD amounts to three decimal places, a payment for KWD 10.500 and KWD 10.5 are the same value."
Протухший курс: "Simulate an exchange rate feed failure and confirm the application's defined fallback behavior... Does it block new transactions? Display a stale-rate warning? Default to a spread-protected rate?"
Кейс возврата в другой валюте: "a refund on a multi-currency transaction where the original payment was in EUR but the refund is processed in GBP. Which rate applies? The original transaction rate, the current rate, or a defined policy rate?"
Момент фиксации курса на границе суток: "a payment initiated at the close of a trading day where the rate changes between initiation and settlement the following morning. Test that the locked rate is preserved across this boundary."

[ЧЕК-ЛИСТ QA] QAPractices "Currency & Tax Calculation Testing Test Cases" — https://qapractices.com/test-cases/currency-tax-calculation-testing-test-cases/ (обращение 2026-09-18). Конкретный тест-кейс TC-07:
> "Verify behavior when exchange rates change during an active checkout session... Rate at the time of order confirmation is used. Customer is notified if the total changes. No surprise charges post-payment."
Частые ошибки: "Ignoring rounding direction: Rounding half-up vs. banker's rounding can cause cumulative discrepancies... No testing of edge currencies: Currencies with no decimal places (JPY, KRW) or three decimal places (BHD, IQD) behave differently."

[СТАНДАРТ / БЛОГ] XBOSoft "Testing Multi Currency Applications" — https://xbosoft.com/blog/testing-multi-currency-applications/ (обращение 2026-09-18). Триангуляция курсов через базовую валюту: "If a pair is unavailable, the system may triangulate through a base currency, for example convert JPY to EUR through USD. Prove that the triangulation path is deterministic, repeatable, and aligned with policy."
Граничное значение округления: "Validate amounts that sit at rounding thresholds, for example 1.005 in currencies with two decimals."
FX gain/loss за период при неизменном балансе в валюте: "Build scenarios where balances are unchanged across two periods while the EUR-USD rate changes from 1.1538 to 1.0637. Verify that the system books FX gain or loss..."

[ОЦЕНКА] frugaltesting "Testing Cross-Border Payment Systems" — https://www.frugaltesting.com/blog/testing-cross-border-payment-systems-for-compliance-and-accuracy (обращение 2026-09-18). Расхождение фронта и бэка по курсу: "Foreign exchange rate out of sync — frontend cached, backend live, customer charged a different amount than quoted... The gap per transaction is small... it becomes a reconciliation disaster." Таблица «тип отказа → тест»: "Duplicate transaction | Retry fires without checking prior completion | High | Idempotency test: submit the same transaction twice, verify a single debit."

### 1.4 Приватность / удаление аккаунта / экспорт данных (GDPR/152-ФЗ)

[ЧЕК-ЛИСТ QA] QAPractices "GDPR Web App Testing Checklist" — https://qapractices.com/checklists/gdpr-compliance-testing-checklist-web-apps/ (обращение 2026-09-18). Таблица тест-кейсов дословно:
> "A04 | Identity verification | Submit export without re-authentication | Redirect to re-enter password or 2FA
> E02 | Grace period respected | Initiate deletion | Status pending_deletion with scheduled purge date
> E03 | Permanent deletion | Trigger retention cleanup after grace period | users table email NULL; CRM contact absent; analytics user id replaced with hash
> E04 | Backup handling | Restore latest backup created before deletion | Restored user record is anonymized or excluded
> E05 | Legal hold anonymization | Flag user with open invoice, trigger deletion | Invoice retains amount, user_id replaced with anon_*
> E07 | Log cleanup | Search application logs for user email | No PII in logs or logs redacted"

[ЧЕК-ЛИСТ QA] QAPractices "GDPR Data Deletion Testing" — https://qapractices.com/test-cases/gdpr-data-deletion-testing-test-cases/ (обращение 2026-09-18):
> "TC-02: Cascade Deletion Across Tables — Verify that deleting a user record cascades correctly to all related tables... No orphaned records with user PII remain.
> TC-03: Cache and Search Index Cleanup — User data is not found in search results. Cache returns a miss or null for the user's key.
> TC-06: Third-Party Integration Notification — Third parties receive deletion request and confirm execution within SLA. Failure to notify is logged and escalated.
> TC-07: Legal Hold and Exception Handling — Deletion is blocked or deferred. User receives an explanation."
Частые ошибки: "Deleting only the primary record: Orphaned data in related tables, logs, and caches is a GDPR violation... Treating anonymization as deletion: Pseudonymized or tokenized data may still be re-identifiable."

[ЧЕК-ЛИСТ QA / методология] DEV.to "GDPR DSAR Workflow Testing Guide" — https://dev.to/beefedai/gdpr-dsar-workflow-testing-guide-2p10 (обращение 2026-09-18). Метод «маркер-приманка» для проверки полноты выгрузки: "Create a synthetic test subject with a unique marker string... and inject it into every relevant system: CRM, billing, support tickets, analytics, message queues, backups, and a third-party processor test account. Submit a DSAR for that synthetic identity and verify the export contains all seeded items (full recall)."
Реальный дефект, зафиксированный как пример: "Missing export of ticketing system entries (TC-DISC-02)... Observed: Export did not include entries from ticketing-prod between 2025-10-01 and 2025-10-14. Root cause: Indexing job failed; tickets moved to archive bucket not covered by search."
Формат для portability отдельно от обычного экспорта: "the GDPR defines a separate, but related, right to receive personal data in a structured, commonly used and machine-readable format (Article 20)... That format requirement is narrower than a generic DSAR export."

[ЧЕК-ЛИСТ QA] testmuai "GDPR Compliance Testing" — https://www.testmuai.com/blog/gdpr-compliance-testing/ (обращение 2026-09-18). Тест на soft-delete как ложное срабатывание: "The most common defect this catches is the soft-delete flag: the record vanishes from the UI but still returns through the API or a database export. Under Article 17 that state is a failure."
Проверка через повторную регистрацию: "Re-register with the same email address; recovered order history or a pre-filled profile means the deletion was a visibility flag, not an erasure."

### 1.5 Онбординг / пустые состояния

Специализированный чек-лист по этой теме не искался отдельным запросом (бюджет ушёл на приоритетные пункты задания — импорт/амортизация/мультивалюта/приватность). Ниже — только то, что нашлось попутно в других источниках; см. §4 п.6 «недобытое».

[ОТЗЫВ ПОЛЬЗОВАТЕЛЯ, RU] vraki.net, CoinKeeper, обращение 2026-09-18 — давление на подписку до понимания функционала мешает первому опыту: "Агрессивное принуждение к платной подписке не даёт мне понять подходит ли это приложение мне. Интересующие функции заблокированы. А то, что есть непонятно, как использовать. В итоге приложение становится бесполезным. Предоставьте пробный период, дайте возможность оценить полный функционал."

### 1.6 Безопасность / сессии

Специализированный чек-лист по этой теме не искался отдельным запросом (та же причина, см. §4 п.7). Единственная попутная находка — реальный сценарий потери данных при смене устройства/переустановке без завершённой синхронизации:

[ФОРУМ, RU] Форум поддержки Zenmoney (см. §2, полная цитата и URL там) — перенос приложения на новый телефон через системный перенос Android скопировал ЛОКАЛЬНЫЕ данные без переноса состояния синхронизации с сервером, что привело к расхождению баланса ~100 тыс. руб. и исчезновению счетов. Это одновременно кейс §1.6 (сессии/устройство) и §2 (боль пользователя).

## §2. Боли пользователей (дословно, с источником и языком)

### RU — Google Play / RuStore / iRecommend / Otzovik — Дзен-мани (учёт расходов)

[ОТЗЫВ ПОЛЬЗОВАТЕЛЯ, RU] Google Play, обращение 2026-09-18, https://play.google.com/store/apps/details?hl=ru&id=ru.zenmoney.androidsub:
> "Привык к нему за пару лет, но в последнее время стало лагать как не знаю что при смене разделов, просто фризится намертво, приходится быстро закрывать через список приложений и обратно открываешь уже ок. Далее - без подписки года с 2024 нельзя посмотреть даже свои доходы и дельту, сравнить базовые разделы которые были в доступе бесплатно еще с мая 2023 около года точно."
> "Сделали отличный раздел с кешбэком по каждой карте, но при распознавании скриншота добавились не все категории, а функцию ручного добавления почему-то не придумали. Буду очень рада, если исправите. Потому что без некоторых категорий эта функция вообще бесполезна."
> "Не работают авто синхронизации. Постоянные ошибки, вылеты и неучтенные транзакции. Уже два месяца приложение мертвым грузом."

[ОТЗЫВ ПОЛЬЗОВАТЕЛЯ, RU] RuStore, обращение 2026-09-18, https://www.rustore.ru/catalog/app/ru.zenmoney.androidsub/reviews:
> "С 6 июля не работает синхронизация с Вайлдберрис. Служба поддержки отвечает, что не знает когда исправят данную ошибку."
> "Проблемы с синхронизацией WB и классификацией операций не решаются в принципе. Больше не рекомендую это приложение. Разработчик приделывает бантики не обеспечивая работоспособность основных функций."
> "Перестала работать синхронизация с озон банком... Изменить автоназначение категорий операций невозможно. Постоянно расходится баланс и приходится сверять вручную."
> "Приложение на автомате дублирует перевод между своими счетами как расход, по итогу у меня расходы за 2 месяца больше чем я заработал за всю жизнь."
> "уже совершенных выбрать одну категорию, казалось бы мелочь, но у меня операции за полгода и... можно было бы за несколько кликов сделать" (жалоба на отсутствие массового переназначения категории)
> "Ранее приобрел приложение, долго не использовал. В итоге смс не распознаются, поддержка не занимается их починкой, предлагая это делать самому."

[ОТЗЫВ ПОЛЬЗОВАТЕЛЯ, RU] iRecommend, обращение 2026-09-18, https://irecommend.ru/content/ne-rabotaet-ne-rekomenduyu:
> "Синхронизация с банками или не происходит вообще или происходит после того как ты 150 раз ткнешь в экран и примерно через час очень много непонятных операций которые у меня не было, потому что я всегда сверяю с мобильным банком постоянные какие-то непонятные корректировки, постоянно сбои глюки."
> "Только эти неприятные люди молчат о том что если вы переустанавливаете или выходите из аккаунта заходите снова то у вас обновляется всё! Вообще всё... но все операции все категории все обнуляется! Получается все годы что я пользовалась этим приложением у меня обнулились."

[ОТЗЫВ ПОЛЬЗОВАТЕЛЯ, RU] iRecommend, обращение 2026-09-18, https://irecommend.ru/content/ne-tratte-dengi-oni-ne-obespechivayut-sinkhronizatsiyu-s-bankami-budete-v-ruchnuyu-traty-vno:
> "Купили год «полный дзен», но тех поддержка отсутствует - никак не помогают. Деньги возвращать отказались. Сбербанк не синхронизируется совсем! Мы не пользуемся, тк каждую операцию нужно вносить вручную."

[ОТЗЫВ ПОЛЬЗОВАТЕЛЯ, RU] Otzovik, обращение 2026-09-18, https://otzovik.com/review_18532736.html — миграция между версиями ОС ломает "пожизненную" лицензию:
> "Перенес все приложения, но Дзен-мани просто не встал. Ладно, думаю, скачаю заново из Play Market. Установилось, захожу — а там базовый бесплатный тариф!!! ... 'Та версия, которую вы купили, больше не поддерживается. Новая — это уже другая программа. Хотите старую? Скачивайте из истории покупок'... а из истории она скачивается, но не ставится на Android 14 — система просто не пускает."

[ФОРУМ, RU] Форум поддержки Zenmoney, обращение 2026-09-18, https://support.zenmoney.ru/communities/1/topics/2212-... — потеря счетов и рассинхронизация после переноса на новый телефон:
> "Сумма общего баланса в приложении на новом телефоне изменилась примерно на 100 тыс. руб., стала меньше. Стал смотреть чем это вызвано, заметил, что пропали 3 счёта или даже больше... При снятии галочек со счётов ... сумма расходов только увеличивается!!! Хотя по идее должно быть наоборот."
Ответ поддержки (объясняет модель данных — переводы на исключённый счёт превращаются в расход): "Если счёт исключается из расчёта, то все переводы на него в рамках текущего расчёта становятся расходами. Эти суммы уходят из учёта, то есть списываются в расход."

### RU — CoinKeeper — iRecommend / vraki.net

[ОТЗЫВ ПОЛЬЗОВАТЕЛЯ, RU] iRecommend, обращение 2026-09-18, https://irecommend.ru/content/coinkeeper:
> "НЕ РЕКОМЕНДУЮ В приложении масса ошибок! Синхронизация с банками работает не корректно. При повторной синхронизации дублируются операции доход и расходов."
> "Кипил подписку, сначала не мог добавить банковскую карту, удалил установил новую, и не смог войти, пишет ошибка пороля, пороль не востонавливается, удалил загрузил заново, пишет…" (обрыв, но фиксирует цикл broken-auth → reinstall → same error)

[ОТЗЫВ ПОЛЬЗОВАТЕЛЯ, RU] vraki.net, обращение 2026-09-18, https://vraki.net/otzyvy/mobilnye-prilozheniya/coinkeeper-uchet-rashodov-i-do.html:
> "Многие банки присылают сейчас пуш уведомления. А программа их не считывает, только смс. Очень не удобно."
> "При нажатии на кнопку «экспорт», приложение запрашивает разрешение на доступ к фай..." (обрыв цитаты источника — экспорт данных требует прав доступа к файлам, что пугает пользователя)
> "Приложение постоянно вылетает, редактировать уже внесённые расходы нельзя, шаг в лево, шаг в право и сразу вылетают ошибки."
> "Постоянные ошибки, невозможно внести расходы в нужную дату, всё вылетает. Таблица эксель лучше справляется."
> "После переустановки, не стали приходить и учитываться сообщения из всех трех банковских карт... в течение месяца!!!!! писала в техническую службу поддержки, но вопрос так и не помогли мне решить."
> "Много лет пользовалась премиум версией... Сегодня обнаружила, что считает неправильно. Была в шоке. Недавно завела карту, внесла все доходы и расходы. На счету показывает ровно на 1000 рублей больше. Как? Проверила другие счета, тоже неверно." — конкретная числовая ошибка баланса.
> "пользовались с супругой совместным платным аккаунтом на андроид. После подключения IOS на андроид версии перестали корректно считаться данные в наших кошельках, хотя все платежи отображаются." — расхождение между iOS/Android клиентами общего бюджета.
> "Агрессивное принуждение к платной подписке не даёт мне понять подходит ли это приложение мне. Интересующие функции заблокированы. А то, что есть непонятно, как использовать."

### RU — vc.ru — блог о собственной разработке "Контроль расходов" (косвенно фиксирует боли пользователей PFM-класса)

[БЛОГ / ФОРУМ, RU] vc.ru, обращение 2026-09-18, https://vc.ru/tribuna/59422-kak-i-zachem-ya-napisal-svoi-kontrol-rashodov (автор о существующих приложениях и обратная связь читателей):
> "они требуют слишком много внимания от пользователя" (о категоризации трат — источник процитирован в переводе агентом WebFetch, оригинал на русском не извлечён дословно, см. §4)
> "одна пропущенная трата приведёт к тому, что баланс в приложении разойдётся с реальностью" — ручной учёт и рассинхронизация баланса.
> Комментатор об упрощённом подходе автора: "it's not intuitive at all how you're supposed to update your balance" (не интуитивно, как обновлять баланс).

### EN — App marketplace review (BudgetSheet, Google Workspace Marketplace)

[ОТЗЫВ ПОЛЬЗОВАТЕЛЯ, EN] Google Workspace Marketplace, обращение 2026-09-18, https://workspace.google.com/marketplace/app/budgetsheet_budget_bank_imports/922376225939, дата отзыва март 2026:
> "Plaid bank log-in fails using credentials from password manager."

## §3. Сводный список сценариев и крайних случаев (главный выход)

**Импорт банковских выписок**
1. Загрузка одного и того же файла дважды — система обнаруживает дубль по SHA-256 контента и отклоняет повторную запись, а не создаёт дубль транзакций.
2. Банк переэкспортировал тот же период с переставленными строками/другими заголовками — хеш меняется, система должна явно спросить/зафиксировать это как НОВЫЙ импорт, а не слить с прежним молча.
3. Сальдо не сходится: открывающий баланс + сумма транзакций ≠ закрывающий баланс — блокировать импорт и показать точку расхождения, а не просто предупреждение мелким текстом.
4. Число транзакций в исходном файле (PDF/скан) не совпадает с числом распознанных строк — явный сигнал пропущенных строк.
5. Дубли внутри одного файла (одинаковые дата+сумма+описание) — предложить решение "оставить/удалить", не удалять автоматически без подтверждения.
6. Кодировка файла — не-UTF-8 символы (валюта, кириллица) отображаются как "?" или битые символы — принудительная перекодировка при импорте.
7. Разрывы дат внутри выписки (7-10+ дней без операций для активного счёта) — предупреждение "возможно пропущена страница/раздел".
8. Знак операции перепутан целиком (все дебеты стали кредитами) — расхождение баланса примерно в 2 раза от суммы операций — детектируемый паттерн, а не просто "расхождение".
9. Файл банка не в ожидаемом формате (генерический CSV вместо родного QBO/OFX/CAMT) — снижение качества импорта, предупреждать пользователя явно.
10. Реверс/сторно операции (chargeback, NSF) приходит отдельной строкой позже исходной — нельзя обрабатывать автоматически как обычную транзакцию, требуется явное подтверждение пользователя.
11. Транзакция привязана к счёту, которого нет в системе пользователя — не молча пропускать, а показать список нераспознанных счетов.
12. Округление "копеечных" расхождений при сверке — нужен явный порог допуска (tolerance), а не жёсткое равенство.
13. Повторная синхронизация с банком после сбоя создаёт дубли операций дохода/расхода (реальная жалоба CoinKeeper) — идемпотентность синхронизации, а не просто ретрай.
14. SMS-уведомления о транзакции перестают распознаваться после обновления ОС/приложения без явной причины (реальная жалоба CoinKeeper) — нужен алгоритм деградации (fallback), а не молчаливый обрыв.
15. Перевод между своими счетами по ошибке классифицируется как расход, задваивая расходы (реальная жалоба Дзен-мани) — правило "перевод между своими счетами не расход" должно быть инвариантом, проверяемым тестом.
16. Исключение счёта из расчёта бюджета превращает входящие на него переводы в "расход" по остальным счетам — контринтуитивное поведение, которое нужно явно объяснять пользователю в интерфейсе (см. цитату поддержки Zenmoney §2).

**Расчёты / амортизация / кредитные калькуляторы**
17. Ставка ровно 0% — деление на ноль в закрытой формуле аннуитета; явно валидировать вход и не давать формуле упасть в NaN/Infinity.
18. Однократный платёж (срок = 1 период) — крайний случай формулы аннуитета.
19. Очень длинный срок (30-40 лет) — накопление ошибок плавающей точки; хранить в целых минимальных единицах (копейках), не float.
20. Сумма с копейками — преждевременное округление до расчёта итога даёт неверный итог.
21. День-каунт конвенция не задана явно (30/360 vs Act/365 vs Act/Act) — один и тот же номинальный процент даёт разные платежи; должна быть явным полем ввода, не хардкодом "ставка/12".
22. Последняя строка графика не закрывает баланс ровно в ноль — индикатор бага округления, не "почти ноль".
23. Негативная амортизация (проценты за период превышают платёж, остаток растёт) — система должна отклонять построение графика на этапе валидации, а не тихо генерировать растущий баланс.
24. Дата начала кредита в конце месяца (31 января) — платежи должны идти по последнему дню каждого месяца, а не по фиксированному числу (28/29 февраля, 30 апреля...).
25. Плавающая ставка / пересчёт при рефинансировании / досрочном погашении — заморозить уже прошедшие строки графика, пересчитать только "хвост"; неизменность прошлого — инвариант, который нужно тестировать явно.
26. Разворот платежа после пересчёта процентов (NSF/чарджбэк на следующий день после того как ночной процесс уже начислил проценты на уменьшенный баланс) — нужна корректирующая проводка, ссылающаяся на исходный реверс, а не тихая правка задним числом.
27. Первый период кредита неполный/нестандартной длины (дата выдачи не совпадает с датой первого платежа на ровно один период) — отдельная формула расчёта первого периода, не универсальная.
28. Инвариантные проверки графика: удвоение суммы кредита должно удваивать платёж; повышение ставки не должно снижать платёж; увеличение срока должно снижать платёж и повышать суммарный процент — их отсутствие как класс тестов "метаморфных свойств".
29. Проверка на середине графика: к половине срока должно быть погашено 40-60% основного долга для 30-летнего аннуитета — иначе off-by-one в сроке.
30. Промежуточный/выходной период с interest-only (только проценты) — переход к стандартной амортизации должен пересчитывать платёж по остаточному сроку, а не молча продлевать срок.

**Мультивалютность**
31. Валюта с нулевым числом знаков после запятой (JPY, KRW) — отображение и хранение должно быть целым числом, не X.00.
32. Валюта с тремя знаками после запятой (KWD, BHD) — усечение/округление до двух знаков теряет значимую величину.
33. Курс обмена "протух" (фид недоступен/задержка) — явно определённое поведение (блокировать/показать предупреждение о неактуальном курсе/фолбэк с наценкой), а не тихое использование старого значения.
34. Курс на фронтенде (кэш) расходится с курсом на бэкенде (live) в момент исполнения — списание по другой сумме, чем показано пользователю (реальный паттерн реконсиляционных инцидентов).
35. Курс меняется между инициацией операции и подтверждением (например, ночью на границе торгового дня) — политика "какой курс использовать" должна быть явной и тестируемой, включая уведомление пользователя об изменении суммы.
36. Возврат средств (refund) по операции, изначально прошедшей в одной валюте, инициируется в другой — какой курс применяется (исходный/текущий/политика) должно быть явным решением, не побочным эффектом кода.
37. Округление на граничном значении (например, 1.005 при двух знаках после запятой) — банковское округление vs округление "вверх" даёт разные результаты, нужно фиксировать конвенцию.
38. Общий бюджет на двух платформах (iOS/Android) после смены одной из платформ считает по-разному при идентичных операциях (реальная жалоба CoinKeeper) — рассинхронизация клиентов должна быть невозможна архитектурно, не "почти всегда одинаково".

**Приватность / удаление аккаунта / экспорт данных (152-ФЗ/GDPR-аналог)**
39. Экспорт запрошен без повторной аутентификации — должен требовать пароль/2FA заново, не отдавать данные по одной активной сессии.
40. Экспорт не включает часть источников данных (например, архивные тикеты поддержки вне поискового индекса) — нужен тест "полноты выгрузки" через маркер-приманку, засеянный во все системы, а не доверие к тому, что "экспорт выглядит полным".
41. После удаления аккаунта данные всё ещё доступны через API/повторный экспорт (soft-delete флаг вместо реального удаления) — это провал теста, даже если в UI запись пропала.
42. Восстановление из бэкапа, сделанного до удаления, возвращает удалённые персональные данные — нужна политика анонимизации записи при восстановлении, отдельно тестируемая.
43. Пользователь с открытым обязательством (незакрытый долг/просроченный платёж) запрашивает удаление — юридическое основание хранить финансовую запись (legal hold) должно анонимизировать связанные с пользователем поля, но НЕ саму сумму операции.
44. Повторная регистрация с тем же email после удаления показывает старые данные (историю операций, профиль) — признак того, что удаление было лишь пометкой видимости, а не реальным стиранием.
45. Каскадное удаление не доходит до связанных таблиц/логов — PII остаётся в audit log, в поисковом индексе, в кэше — независимая проверка каждого хранилища по отдельности.
46. Экспортированный файл должен быть в машиночитаемом формате (JSON/CSV) отдельно от права на portability (Art. 20) — не путать с "экспортом вообще".

**Онбординг / пустые состояния**
47. Первый вход без единой добавленной транзакции/счёта — экран не должен показывать пустой график/деление на ноль по проценту исполнения бюджета.
48. Пользователь агрессивно подталкивается к платной подписке до того как понял базовый функционал — реальная жалоба (CoinKeeper): "не даёт понять подходит ли это приложение мне... то, что есть, непонятно, как использовать".

**Безопасность / сессии**
49. Смена телефона/переустановка приложения обнуляет локальные данные, если облачная синхронизация не была завершена перед удалением старого устройства (реальный кейс Дзен-мани, потеря 2+ лет истории).
50. "Пожизненная" подписка перестаёт быть валидной при смене мажорной версии ОС/приложения без миграции лицензии — не технический баг, но кейс, который стоит закрыть тестом миграции покупки при смене версии.

## §4. Недобытое (с причиной) + журнал каналов

### Журнал вызовов инструментов (12 из 12 бюджета добычи использованы)
| # | Канал | Запрос | Результат |
|---|-------|--------|-----------|
| 1 | Exa web_search_exa | bank statement QA checklist duplicate/reconciliation | Успех — 6 источников, чек-листы полные (easybankconvert, Wesley, MS Dynamics, Gestio, CFDoc, FlowParse) |
| 2 | Exa web_search_exa | loan amortization calculator edge cases rounding leap year | Успех — 8 источников (makeitexact conformance corpus, pratikdhanave, dev.to audit, mortgagemath, npm loan-amortization-calculator, fintechengineer handbook, fineract тесты) |
| 3 | WebSearch | vc.ru приложение для бюджета не смог посчитать жалоба | Частично — vc.ru не финтех-платформа, но нашёл релевантную ссылку на статью-блог с болями о PFM |
| 4 | WebSearch | habr.com банковское приложение баг выгрузка выписки отзыв | Пусто по существу — статьи не про пользовательские жалобы на выгрузку выписок, а про безопасность/уязвимости |
| 5 | Exa web_search_exa | multi-currency test cases fintech exchange rate rounding QA | Успех — 6 источников (DeviQA, shoulditestthat, QAPractices, XBOSoft, frugaltesting, testvox) |
| 6 | Exa web_search_exa | GDPR deletion request test cases account deletion export QA | Успех — 6 источников (QAPractices ×2, DEV.to DSAR guide, testmuai, qable — последний почти пустой) |
| 7 | WebSearch | klerk.ru отзыв программа учета личных финансов не смог | Пусто по существу — klerk.ru про бухгалтерию для юрлиц/ИП, не про PFM-приложения физлиц |
| 8 | WebSearch | reddit personalfinance budgeting app couldn't import bank | Почти пусто — выдало Google Workspace Marketplace вместо Reddit; извлёк один релевантный отзыв (BudgetSheet/Plaid) |
| 9 | WebFetch | vc.ru/tribuna/59422 (блог "Контроль расходов") | Успех — извлечены прямые цитаты автора и комментатора о болях ручного учёта |
| 10 | Exa web_search_exa | отзывы Дзен-мани CoinKeeper не смог жалоба Google Play | Успех, основной источник §2 — Google Play, RuStore, iRecommend, Otzovik, форум поддержки Zenmoney, vraki.net |
| 11 | WebSearch | buh.ru форум банк-клиент выписка не загрузилась жалоба | Частично — нашёл тематические ветки форума buh.ru/forum.infostart.ru, но WebSearch дал только резюме без цитат; сами ветки форума не зафетчены (бюджет исчерпан) |
| 12 | WebSearch | приложение для бюджета учет финансов отзыв не понимает не смогло форум | Слабо — общие обзорные статьи, не прямые жалобы; упомянуты Дзен-мани/CoinKeeper/Monefy, но без новых цитат сверх уже собранного |

### Недобытое (с причиной)

1. **habr.com — прямые пользовательские жалобы на PFM/банковские приложения.** WebSearch (вызов #4) не нашёл статей формата "жалоба пользователя", только материалы про уязвимости и парсинг выписок в 1С. Причина: Habr — площадка для инженерных статей, а не отзывов конечных пользователей; жанр "жалоба" там нехарактерен. Канал не мёртв, но формат запроса не тот — не проверено через прямой заход в поиск Habr по комментариям к статьям про мобильный банкинг (бюджет исчерпан).

2. **klerk.ru — жалобы пользователей PFM-приложений.** Klerk.ru оказался ресурсом для бухгалтеров/ИП (обсуждение 1С, банк-клиент для юрлиц), а не для физлиц с личными бюджетами. Тема не покрыта, потому что сама постановка "жалоба на приложение для личных финансов на klerk.ru" может быть промахом по площадке — там нет такого класса продукта в фокусе аудитории. Не проверено: есть ли на klerk.ru ветки именно про мобильный банк физлица (не исключено).

3. **buh.ru — дословные цитаты жалоб на загрузку банковской выписки.** Ветки форума найдены (buh.ru/forum/forum18375/topic87058, topic96417, topic69581 и др.), но WebSearch дал только пересказ, не цитаты, а прямой WebFetch/curl по этим URL не выполнен — бюджет 12 вызовов исчерпан на этом моменте. Это НЕДОБЫТОЕ по нехватке бюджета, не по недоступности источника: сами ссылки рабочие и содержат релевантный материал (сообщения бухгалтеров о расхождении сумм при загрузке банк-клиента), но раскрыть их не успел.

4. **Reddit r/personalfinance / r/YNAB — англоязычные жалобы на импорт банка.** WebSearch не смог адресно попасть на Reddit (выдал нерелевантные результаты по обоим заходам). Не проверены каналы Exa web_search_exa напрямую по reddit.com — не исключено, что там результат был бы лучше, но бюджет исчерпан после 12-го вызова.

5. **App Store / Google Play отзывы на англоязычные PFM-приложения (Mint, YNAB, Copilot, Monarch Money)** — не запрашивались вовсе; весь бюджет отзывов ушёл на русскоязычный сегмент по прямому требованию задания (§Б, обязательное покрытие vc.ru/habr/klerk/buh.ru). Английский сегмент §2 представлен только одним отзывом (BudgetSheet/Plaid).

6. **Тест-кейсы для онбординга/пустых состояний как отдельный класс QA-чек-листов** (не пользовательские жалобы, а именно опубликованные чек-листы вида "empty state testing checklist") — не искались отдельным запросом; §1.5 в файле фактически пуст кроме двух пунктов, выведенных из общих источников, а не из специализированного чек-листа. Причина — бюджет полностью ушёл на импорт/амортизацию/мультивалюту/приватность как более приоритетные пункты задания.

7. **Тест-кейсы безопасности/сессий как отдельный класс** (§1.6) — та же причина, не искались отдельным запросом, бюджет закончился раньше.

8. **vc.ru — статьи именно про жалобы на конкретные банковские приложения (Т-Банк/Сбер/Альфа мобильные приложения)** — не искались отдельно; найденная статья #9 про самодельный трекер расходов, не про банковские приложения крупных игроков.

### Итог по покрытию требования владельца ("русскоязычные форумы vc.ru, habr.com, klerk.ru, buh.ru — ОБЯЗАТЕЛЬНО")
- vc.ru — покрыт частично (1 статья с прямыми цитатами о болях ручного учёта, не про банковские приложения).
- habr.com — не дал прямых пользовательских жалоб данным способом запроса (см. п.1 недобытого).
- klerk.ru — не дал релевантного материала, площадка не про тот класс продукта (см. п.2).
- buh.ru — ветки форума найдены, но не зафетчены дословно из-за исчерпания бюджета (см. п.3, самое конкретное "недобытое по нехватке бюджета, а не по недоступности").
- Реальным основным источником §2 оказались iRecommend, Otzovik, RuStore, Google Play и официальный форум поддержки Zenmoney — не входили в обязательный список, но дали наиболее плотный дословный материал по болям.
