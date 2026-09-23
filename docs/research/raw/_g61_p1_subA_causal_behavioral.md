# Г61 проход 1, подагент A — causal_effect_measurement + behavioral_execution_gap

Начато 2026-09-18. Сырьё дописывается после каждого вызова.

## Шаг 1. Разбор маркеров и сверка «последнее упоминание» (без сети)

### causal_effect_measurement_2026-09-10.md (4284 строки, 64 маркера по регэкспу)
Последние итоговые блоки: «ИТОГ Г30.1» (стр. 3984), «ИТОГ Г31.2» (4163), «ИТОГ Г31.4» (4263, «Задолженности нет»).
Реально открытое по последнему упоминанию:
- C1 Freedman 1987 NEJM, полный текст — «закрыт пейволлом» (4160); частично добыт Г30.1-12.
- C2 Radcliffe 2007 (Qini) — «закрыт как не требуется» (4190), репозиторий Эдинбурга держит только метаданные (3345).
- C3 353-ФЗ, 38-ФЗ, 135-ФЗ/ФАС — «не проверялись» (3350); больше нигде в файле не закрыты.
- C4 22-МР с cbr.ru — «НЕ ДОБЫТ с cbr.ru» (3349). СВЕРКА: закрыт соседним файлом behavioral_execution_gap, Д11 стр. 1827 «cbr.ru через curl (22-МР)».
- C5 Видео Альфа-Банка RUTUBE — «нет канала транскрипции» (4160).
- C6 Доля трафика на эксперименты в РФ-банке — отрицательный результат, «числа не публикуют» (3544, 4158). Не отказ доступа.
- C7 CFPB/§5552 генпрокуроры штатов (3156) — «не проверялось в этом заходе»; вне заказа (США, продукт в РФ).
История (закрыто в самом файле): Abadie (740, 2148–2166, 2808, 4191, 4215 → Г31.4-E1); Polonetsky (3190, 3247, 3678 → Г30.1-11); Meyer 2015 (3294, 3803–3806 → Г30.1-13); Кодекс этики ИИ (3531, 3846 → Г30.1-14); X5 (3549 → Г31.2-1); ВТБ 63 статьи (3554 → Г30.1-15); РФ-практика (1385, 2323, 2826 → П4.4/Г30.1-15/16); CFPB/DSA/AI Act/IRB (2698–2707, 2824, 3597 → П4.1–П4.3); приказ РКН 149 (2648, 2825 → П4.6); «gating» (2318, 2823 → П4.6, блог Farhadi); §И4/Д5 оглавления (1356, 1358, 1426, 1437, 2816, 2846, 2875, 3286, 3543, 3672, 3988–4003, 4182); 727 и 3490 — не отказы (текст / отрицательный результат).

### behavioral_execution_gap_2026-09-10.md (2350 строк, 52 маркера)
Последние итоги: «ИТОГ ДОБОРА Г8» (2048), «ИТОГ Г30.2» (2274), «ИТОГ Г31.5» (2346, «Задолженности нет»).
🔴 Противоречие внутри файла (урок 9): Г30.2-13 (стр. 2227, 2283) пишет «Hamilton 2023 — полный текст по-прежнему НЕ добыт», тогда как Д11.1.1 (стр. 1177–1185) уже взял ПОЛНЫЙ ТЕКСТ через Wayback `id_` поверх `doi/full` (200, 394 845 б, 86 595 симв.). Правильный вердикт — ДОБЫТ (Д11). Г30.2 ошибочно переоткрыл закрытый пункт.
Сверка по соседним файлам:
- GPS Россия (943, 1003, 2279) → ЗАКРЫТ в rf_household_finance_stats_v2_2026-09-10.md «Д9.1» (стр. 470): patience −0,07528, ранг 35/76.
- Кузина–Моисеева 2024 «Экономическая социология» (897, 899) → ПОЛНЫЙ ТЕКСТ в rf_household_finance_stats_v2 «Г23.3.2» (стр. 1735).
- Кузина–Моисеева 2021 «Вопросы экономики» (842) → rf_household_finance_stats_v2 Г23.3/Г30.4-С1: «ВЭ ❌ 23/23 за подпиской», viewFile → 302 (стр. 1823, 2160+). Браузером не проверялось.
- «39 % без сбережений» (817) → rf_household_finance_stats_v2 стр. 309: ОДПФ «39 % есть сбережения» — сниппет, по-видимому, перевёрнут; первичка ОДПФ добыта там.
- Madrian & Shea 1999 (2018, 2053) → closed_forever_retry Г18.4 (стр. 327): 1999 — ошибка даты, это NBER w7682 май 2000, ДОБЫТО; + Д11.4.1.
- Brown & Lahey JMR 2015 (1864) → Г60, revived_sources.
- Hagger 2010 → подтверждён по Hagger 2016 (Г8.3а, behavioral_finance_field).
- «Correcting the Record» → Г31.5-B1 абстракт; полный текст — SSRN (капча прежних заходов). Браузером НЕ пробовался.
Реально открытое: Fernandes–Lynch–Kim полный текст (SSRN); Gollwitzer & Sheeran 2006; Росстат КОУЖ (822, 1010); NAFI методика/«67 %» сниппет (809, 814); индекс НАФИ по компонентам (873); горизонт «не дальше месяца» (902–905); RLMS-сниппет (939); leef.hse.ru RCT (913); co-holding РФ (974); дефолт в советующем продукте (исследовательский вопрос).

## Шаг 2. Добыча

### B-FLK. Fernandes, Lynch, Kim 2025 (SSRN 5385386), полный текст
- Браузер chrome-devtools `new_page` https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5385386 → страница «Just a moment… Performing security verification», Cloudflare Turnstile, чекбокс «Verify you are human» (Ray ID a3d0ff30bbf2d09b). 🟡 ВКЛАДКА ОСТАВЛЕНА ОТКРЫТОЙ (page id 50) — один клик владельца.
- Exa search (mcp__exa__web_search_exa, «Fernandes Lynch Kim publication bias financial education…») → только карточка SSRN 10.2139/ssrn.5772062 (авторы: Fernandes — Universidade Católica Portuguesa, corresponding; Lynch — CU Boulder; Kim — Cornell) + Kaiser et al. NBER w27057 и приложение; открытой копии самой работы 2025 Exa не знает.
- Попутно дословно из приложения Kaiser et al. (back.nber.org/appendix/w27057/w27057_appendix.pdf, выдача Exa): «The estimate on financial behaviors (0.0426) is statistically not different from the estimate from the unrestricted weighted least squares model» (PEESE); WAAP «of 0.0466 SD units on financial behaviors in a sample of 198 effect size estimates within 31 studies»; при MDES 0.1 — «60 effect sizes within 7 studies … 0.0395 SD units». То есть и у самих Kaiser et al. оценки с поправками (0.040–0.047) вдвое ниже заголовочной 0.10 — это согласуется с Fernandes–Lynch–Kim (0.018–0.033), расхождение меньше, чем выглядело по заголовкам.
- ВЕРДИКТ: 🟡 клик капчи владельца (SSRN Turnstile, вкладка 50). Вывод Г31.5 (0.018–0.033 SD по абстракту) стоит.

### C1. Freedman 1987 NEJM 317:141–145, полный текст
- Браузер `new_page` https://www.nejm.org/doi/full/10.1056/NEJM198707163170304 → «Just a moment… Performing security verification», Cloudflare Turnstile, «Verifying… Stuck? Troubleshoot» (Ray ID a3d10411d93a7cb6); за 35 с не прошёл сам. 🟡 ВКЛАДКА ОСТАВЛЕНА ОТКРЫТОЙ (page id 51) — один клик владельца. За капчей у NEJM вероятна ещё и регистрация/подписка (архив 1987) — это тоже 🟡.
- Вывод темы на этом источнике (Г30.1-12: три дословные цитаты тела статьи, со с. 144, включая правило остановки) не зависит от полного текста — стоит.

### C3. 353-ФЗ, 38-ФЗ, 135-ФЗ — проверка «прямого регулирования A/B в РФ нет»
Каналы и коды:
- pravo.gov.ru IPS `doc_itself&nd=102108256` (135-ФЗ) — `curl -sk --http1.1` 200, 181 717 б, НО это исходная редакция 2006 г. (нет поправок «сетевой эффект» 2023); `rdk=60` — 200, 527 650 б, редакция не ранее 2021. nd=102106226 и 102168484 — угаданы неверно (другие документы), 200 на 8 007 и 24 748 б.
- legalacts.ru `federalnyi-zakon-ot-13032006-n-38-fz-o` — 200, 432 406 б, «(ред. от 04.08.2026)».
- legalacts.ru `federalnyi-zakon-ot-21122013-n-353-fz-o` — 200, 468 589 б, «(ред. от 04.08.2026)».
- legalacts.ru `…-26072006-n-135-fz-o` — 404, 179 б (неверный слаг, не отказ сайта).
grep по «эксперимент|тестирован|рандом|персонализ|рекомендательн|алгоритм»:
- 38-ФЗ (ред. 04.08.2026): «эксперимент» — только в смысле правовых экспериментов (422-ФЗ о НПД, 417-ФЗ от 04.08.2023), об экспериментах на пользователях — 0. Дословно определение ст. 3 п. 1: «реклама - информация, распространенная любым способом, в любой форме и с использованием любых средств, адресованная неопределенному кругу лиц и направленная на привлечение внимания к объекту рекламирования…». Попутно: ст. 28.1 «Реклама услуг, связанных с процедурой банкротства» (для долгового блока — отдельная тема).
- 353-ФЗ (ред. 04.08.2026): 0 совпадений по всем шести корням.
- 135-ФЗ (редакции 2006 и ≤2021 с pravo.gov.ru): 0 совпадений.
Вывод: отрицательный вывод темы 37 «прямого регулирования A/B-тестов в РФ нет» — подтверждён по трём законам (38-ФЗ и 353-ФЗ в действующей редакции 04.08.2026; 135-ФЗ — без последних редакций). Уточнение: персональная рекомендация внутри приложения конкретному пользователю по определению ст. 3 п. 1 38-ФЗ («неопределённому кругу лиц») рекламой не является — A/B-варианты такого текста под 38-ФЗ не попадают; массовые варианты баннеров — попадают.
- 135-ФЗ в действующей редакции (после «пятого антимонопольного пакета» 2023) — НЕ проверен: legalacts.ru — два слага 404 (179 б, неверный адрес), IPS отдаёт старые редакции. 🟢 не пройдены каналы: consultant.ru/normativ.kontur.ru через r.jina.ai, браузер. Вывод от этого не зависит: антимонопольный закон регулирует рынок, не отношения сервиса с пользователем.

### C2. Radcliffe 2007 «Using Control Groups to Target on Predicted Lift» — ДОБЫТ через Exa
Канал: mcp__exa__web_search_exa → копия https://silo.tips/download/using-control-groups-to-target-on-predicted-lift (Exa отдала тело разделов 4.2–4.3). Дополнительно: Radcliffe & Surry «Real-World Uplift Modelling with Significance-Based Uplift Trees», https://stochasticsolutions.com/pdf/sig-based-up-trees.pdf, и Radcliffe «FinanceRetention», https://stochasticsolutions.com/pdf/FinanceRetention.pdf.
Дословно (Radcliffe 2007, §4.2): «we can now define the Qini value Q, for binary outcomes, in the same way as the Gini coefficient, i.e. as the ratio of the actual uplift gains curve above the diagonal to that of the optimum Qini Curve … As with the Gini coefficient, this theoretically lies in the range [-1, 1]». «it is also sometimes convenient to define the "little" q0 value as the ratio of the area of the Qini curve above the diagonal to the area above the diagonal of the "zero downlift" optimum Qini … it is possible (and not uncommon) for it to exceed 100%.» «As the overall uplift tends to zero, q0 values tend to ±∞, so "big" Q values are much more useful in these cases.» §4.3 (непрерывный исход): «dividing the area above the diagonal of our uplift gains curve (Qini curve) by half the square of the total number of customers, and we call the resulting value Qc».
Radcliffe & Surry (sig-based-up-trees, §4.2): «Q — the more general qini measure … defined simply as the area between the actual incremental gains curve in question and the diagonal corresponding to random targeting. This is scaled only to remove dependence on the population size N, dividing by N 2, where necessary.» «Uplift estimates are not strictly additive.»
Radcliffe FinanceRetention (финансовый кейс): «Properly randomised control groups of adequate size provide the only proven and reliable way of assessing the true impact of retention activity.» Числа кейса страховщика: отток в контроле 32 %, в лечении 28 %, контроль 100 000, лечение 20 000; при таргетинге 70 % по uplift — снижение оттока ≈5 п.п. вместо 4.
Сверка с файлом: §3.5 (стр. 967–969) — «area under the actual Qini curve and that under the diagonal … further normalized by the area between the random and the optimal targeting curves, [is] defined as Qini coefficient»; Д4.2 (стр. 2246) — формула проверена по Belbahri. Первоисточник совпадает: Q Радклиффа 2007 = площадь над диагональю / площадь оптимальной кривой над диагональю. 🔴 Уточнение, которого в файле не было: у Радклиффа ТРИ нормировки — Q (к оптимуму с «downlift»), q0 (к «zero-downlift», может превышать 100 % и уходит в ±∞ при нулевом общем эффекте) и Qc для денег (площадь / (N²/2), в рублях на человека); а в Radcliffe & Surry 2011 Q — уже НЕнормированная площадь / N², причём теоретический оптимум «often an order of magnitude or more larger than anything achievable». Для продукта: при почти нулевом общем эффекте рекомендаций пользоваться Q или Qc, не q0; сравнивать Qini между работами только при одной нормировке.

### B-NAFI. НАФИ: методика, субиндексы, «67 %» — ДОБЫТО первоисточником
Каналы: Exa search → https://nafi.ru/projects/finansovaya-gramotnost-rossiyan-2025/ , https://nbj.ru/publs/nafi_finansovaya_gramotnost_rossiyan_rassl/72639/ (30.03.2026), PDF-отчёт https://storage.yandexcloud.net/fingram/doc/Nafi2025.pdf → `curl -sk` 200, 1 589 324 б, `pdftotext -layout`.
Дословно (PDF НАФИ, 2025):
- «МЕТОД ОПРОСА: CAWI (интернет-опрос россиян) в возрасте 18 лет и старше. Сбор данных осуществлен методом онлайн-опроса на базе исследовательской онлайн-панели Аналитического центра НАФИ Тет-о-Твет.» «ВЫБОРКА: Основная - 1003 чел. … статистической погрешностью, не превышающей 3% на 95%-доверительном интервале.» Сбор — декабрь 2025.
- «Индекс рассчитывается как сумма значений трех частных индексов (субиндексов)» — «Финансовые знания», «Финансовые навыки», «Финансовые установки»; «Индекс принимает значения от 1 … до 21 балла».
- «Субиндекс "Финансовые знания" в 2025 году составил 4,01 балла из 7 возможных.» «Значение данного субиндекса ["Финансовые установки"] в 2025 году составило 2,91 балла из 5 возможных, без динамики». Навыки — числом в PDF не найдено; по сумме 12,61 − 4,01 − 2,91 = 5,69 из 9 (РАСЧЁТ, не цитата).
- «финансовой подушкой безопасности "правильного" размера обладает каждый третий россиянин (34% против 27% год назад)» … «две трети семей уязвимы перед внезапной потерей дохода». Вступление партнёра: «70% россиян ведут семейный бюджет, это на 7 п.п. больше, чем годом ранее … 56% … ставят долгосрочные финансовые цели … 77% совершали действия по сбережению денег»; «тех, кто хранит деньги наличными, а также тех, кто не формирует накопления совсем, по-прежнему существенна – 25% и 23%».
- nbj.ru: «финансовые знания (4,01 балла из 7) … 69% справляются с расчётом процентов по займу, … простые проценты по вкладу (41%) … влияние инфляции (44%)»; «43% нацелены на планирование жизни, 31% — на долгосрочные сбережения».
Итог: сниппет «67 % без накоплений или не более 3 мес.» (стр. 814) — это «две трети семей уязвимы» НАФИ; первоисточник установлен. 73 % (2024, стр. 802) → в замере дек. 2025 без подушки ≥3 мес. 66 %.
🔴 Расхождение источников, которое надо держать: НАФИ (онлайн-панель CAWI) — «70 % ведут семейный бюджет», ЦБ ОДПФ (микроданные, rf_household_finance_stats_v2 стр. 1652) — «ведёт учёт 13,5 %». Разница — формулировка вопроса («в уме» у НАФИ засчитан, 32 %) и онлайн-выборка. Для оценки рынка PFM брать ОДПФ, НАФИ — только динамику.

### B-GS2006. Gollwitzer & Sheeran 2006 — ОТКРЫТАЯ КОПИЯ НАЙДЕНА (была «OA-локация без url_for_pdf», Д11.4.5)
Exa search → KOPS (Konstanz) карточка https://kops.uni-konstanz.de/entities/publication/2e749bfb-8533-437c-8203-7e788c910c5f — «Open Access Green», лицензия CC BY-NC-ND 2.0; файл https://kops.uni-konstanz.de/server/api/core/bitstreams/d4f710b4-a505-49ef-a831-5b8d7675100b/content → `curl -sk` 200, 4 031 309 б, `%PDF-1.6`, 49 страниц (по r.jina.ai: 200, 298 б — только заголовок, текста нет → скан). `pdftotext`: «Invalid XRef entry / Couldn't read xref table»; pypdf в системе нет. Текстовый слой не извлечён; OCR (tesseract, англ.) не делался — бюджет.
Дословно, аннотация (карточка KOPS и первая страница файла в выдаче Exa): «Findings from 94 independent tests showed that implementation intentions had a positive effect of medium-to-large magnitude (d = .65) on goal attainment.»
Вывод темы (d = 0.65 «перекрыто мета-анализом 2024/25», где финансовой категории нет, Г31.5-B2) — стоит; число 0.65 теперь из первоисточника, не из сниппета.

### C5. Доклад Альфа-Банка «Uplift-моделирование в ценообразовании кредитных продуктов» (RUTUBE) — «нет канала транскрипции» ОПРОВЕРГНУТО
Канал транскрипции на машине есть: `/usr/local/bin/whisper-cli` + `/usr/local/bin/ffmpeg` + модели `~/.cache/whisper/ggml-large-v3-turbo-q5_0.bin`, `ggml-base.bin`. Нет только yt-dlp — не нужен: RUTUBE отдаёт поток через открытый API.
`curl https://rutube.ru/api/play/options/e07b39e41eecfa310886208f6a446d81/?no_404=true` → 200, 129 680 б; title «Uplift-моделирование в ценообразовании кредитных продуктов | Альфа-Банк», duration 1 506 100 мс (25 мин); `video_balancer.default` — m3u8 bl.rutube.ru.

### B-F2014. Fernandes, Lynch & Netemeyer 2014 (Management Science 60(8)) — АВТОРСКАЯ РУКОПИСЬ ДОБЫТА (была «SSRN/MS пейволл», стр. 490; в approach_validity стр. 2313 — 🟡 «OA-локаций нет»)
Канал: Exa search (побочная выдача по FLK) → https://budgetchallenge.com/Portals/0/Documents/FinEd_Paper_Fernandes.pdf → `curl -sk` 200, 1 449 896 б, application/pdf, `pdftotext -layout` 4 974 строки. Рукопись (препринт) с титулом «Financial Literacy, Financial Education and Downstream Financial Behaviors», Daniel Fernandes*.
Дословно:
- «We conduct a meta-analysis of the relationship of financial literacy and of financial education to financial behaviors in 168 papers covering 201 prior studies. We find that interventions to improve financial literacy explain only 0.1% of the variance in financial behaviors studied, with weaker effects in low-income samples.»
- «financial education interventions have statistically significant but miniscule effects: r2 = .0011, implying that interventions explained about 0.1% of the variance in downstream financial behaviors studied (90 effect-sizes, r = .032, CI95 = .029 to .035).»
- «33 papers reported a mean of 9.7 hours of instruction (SD = 11.9), and 29 papers reported a mean delay of 11 months between intervention and measurement of behavior (SD = 12.4).» «a positive linear simple effect of the number of hours of instruction … (B = .0032, SE = .0004, t = 8.35, p < .0001)» ; «a negative simple linear effect of delay (B = -.0033, SE = .0009, t = -3.53, p = .002) and a positive quadratic effect (B = .00014 …) – ie., effect size of interventions decayed with delay, but at a decreasing rate.»
- «We suggest a real but narrower role for "just in time" financial education tied to specific behaviors it intends to help.»
Итог: числа «0.1 % дисперсии», «168 работ / 201 исследование» (стр. 492 файла) переводятся из «сниппет» в «первоисточник, авторская рукопись». Вывод темы стоит. Для продукта полезная деталь: «just in time» — обучение, привязанное к конкретному действию, т.е. объяснение в момент рекомендации, а не курс.

### Прочие маркеры behavioral_execution_gap — закрыты соседями или вне заказа
- Росстат КОУЖ (822, 1010, 2280) → rf_household_finance_stats_v2 «Д9.4» (стр. 694–779: в КОУЖ нет ни сбережений, ни кредитов, «только бинарная способность покрыть непредвиденный расход») и «Г5.4» (стр. 1078: формы КОУЖ 2024/2026, доверие к банкам).
- Горизонт «не дальше месяца» (902–905) → rf_household_finance_stats_v2 «Г23.1» (стр. 1654, микроданные ОДПФ: «62 % планируют на горизонте ≤ нескольких месяцев, 16,6 % — не планируют»).
- RLMS-сниппет без автора (939) → rf_household_finance_stats_v2 «Д9.5» (стр. 869: кластеризация RLMS 2015–2019, первоисточник открыт).
- Co-holding в РФ (974, 1003, 2280) → rf_household_finance_stats_v2 Д9.5 (стр. 925–931): «не найдено тремя каналами» — отрицательный результат, не отказ доступа.
- Российские полевые RCT / leef.hse.ru (913–918) → отрицательный результат; leef перепроверен в behavioral_finance_field стр. 1161; Г30.2 «не найдено и Exa».
- Карточки проектов ВШЭ (848) — вне заказа: карточка подтверждает лишь существование проекта; содержательные данные мониторинга взяты из статьи ЭС 2024 (Г23.3.2).
- Кузина–Моисеева 2021, «Вопросы экономики» (842) → rf_household_finance_stats_v2 Г23.3 / Г30.4-С1: «ВЭ ❌ 23/23 за подпиской», viewFile → 302 — 🟡 подписка (браузер там не пробовался, но 302 на файл = редирект на вход, это не антибот).
- Brown & Lahey JMR 2015 (1864) → Г60 revived_sources. Madrian & Shea 1999 (2018, 2053) → closed_forever_retry Г18.4 + Д11.4.1 (N когорт 3 286 / 4 257 / 5 812). N статьи Madrian–Shea (331) → Д11.4.1.
- Sheeran 2024/25 «регуляция аффекта» (408) → Г31.5-B2. Dai–Milkman–Riis таблицы (415) → Д11 (стр. 1817). Vohs (1721) → Д11.4.4 + Г30.2-14. Hagger 2010 → Г8.3а.
- «независимой репликации не искал» (1297, лабораторный эффект ретроспективной рамки) и «журнальную версию не искал» (1575, Altmann et al. 2018 DICE DP 294) — вне заказа: не отказ доступа, выводы на рабочих версиях помечены как таковые.
- «статус репликации … не добыт в рамках бюджета, не искал целенаправленно» (352 SMarT, 367, 451) — вне заказа: мета-анализ конкретной работы в фокус темы не входил.
- «Дефолт в советующем продукте» — исследовательский вопрос, не доступ (Д11.3 «косвенные данные из 4 работ»).
- 135-ФЗ, действующая структура: `curl -s https://r.jina.ai/https://www.consultant.ru/document/cons_doc_LAW_61763/` (без UA) → 200, 54 594 б — оглавление с «Статья 10.1. Запрет на осуществление монополистической деятельности хозяйствующим субъектом, владеющим цифровой платформой» (поправки 2023 есть). Единственное совпадение «эксперимент» — новостная врезка сайта («Минцифры предложило продлить эксперимент по идентификации…»), не текст закона. Названий статей про эксперименты/тестирование на пользователях — 0. Полного текста действующей редакции 135-ФЗ по ключевым словам НЕ сделано (оглавление + редакции 2006/≤2021); вывод не зависит.
