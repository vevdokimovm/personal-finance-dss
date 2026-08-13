# Канон и история решений по Decimal — сверка перед батчем

**Тип материала:** внутренний код/докс-ресёрч (Explore-агент читал docs/ и git log),
НЕ внешний источник в смысле README этого каталога — сохранено по прямому указанию
владельца, для непрерывности между сессиями/аккаунтами.

**Дата:** 2026-08-13. **Контекст:** тот же батч v8.19.2, что и файлы 08-09 в этом каталоге.

**Задание агенту:** прочитать всё, что уже записано про Decimal в
`model_completion_plan.md` §2.5, `WATCHLOG.md`, `math_model.md`, скилл
`finpilot-money-format`, `ROADMAP.md`, и историю git для `app/core/money.py` — чтобы
план не противоречил и не дублировал более раннее решение.

---

## Отчёт агента (дословно)

I now have full context. Note: git history for this repo only goes back to a single restore commit (v8.7.0 snapshot) — there is no earlier commit that "introduced" `FLOW_EPS`/`to_money`; the design rationale lives only in the code comments/docstring, not in commit history.

Report:

**1. docs/model/model_completion_plan.md (item 2.5, lines 186–190)**

Item **2.5** sits in **"Волна 2 — живые данные"** (§6, live-data wave, planned 6–18 months post-launch), table rows 2.1–2.6, axis column "3", effect "+0.3", cost "2 батча (плюс регресс всех golden)". Full text (⚠ flagged):

> "**Decimal в денежном ядре** вместо float с эпсилоном — **НЕ требует ни эксперта, ни живых данных** (найдено при ревизии 2026-08-13: сидит в волне 2 по хронологии батчей, не по типу ресурса — `model_quality_scorecard.md` §4 подтверждает, что ограничение чисто инженерное). Технически можно начинать в любой момент, не дожидаясь 6–12 мес. после запуска; не сделано в этой сессии из-за размера/риска (**регресс ВСЕХ golden-снапшотов**) — решение по срокам за владельцем"

So the plan explicitly says it's misfiled (present by batch chronology, not by resource type), has no expert/data blocker, and can start any time — but was deliberately **not started** because of its size/risk, specifically **regression risk to all golden snapshots**. Decision on timing is left to the owner (Василий). §7 resource summary counts wave 2 total as 8 sessions / 12 batches → integral ≈91.3 (not yet recalculated after 2.6 closed separately).

**2. docs/WATCHLOG.md**

- Header (line 39–45, v8.19.1): "Decimal в денежном ядре — найден как реальная незаблокированная задача, НЕ взят (крупный рефакторинг, решение за владельцем); фронт-скелет... следующая задача" — i.e. after this revision, Decimal migration + frontend are the only two things left.
- §0 resume point (lines 217–221): confirms the same finding — item 2.5 was misfiled in Wave 2, "**НЕ реализовано в этом батче** — крупный рефакторинг (регресс ВСЕХ golden-снапшотов), решение по срокам оставлено владельцу, не взято с ходу без подтверждения."
- §3 version history (lines 1168–1174, v8.19.1 entry): same summary, plus "Матмодель без экспертов/данных исчерпана — остался только Decimal (решение владельца) и фронт."

No session actually attempted the migration; it's flagged three times as owner-decision-pending, not started, primary blocker = golden-snapshot regression risk.

**3. docs/math_model.md**

Canon header: **"версия 3.9.0 (calibrated+)"**, status "соответствует коду приложения версии 6.17.0 и далее (проверено на v8.18.0)". Searched for Decimal/float/округлен/ROUND_HALF_UP/эпсилон/epsilon — **no matches for money rounding policy**. The only "эпсилон"-family hit is `\varepsilon^{(i)}` (line 525), a Monte-Carlo noise term in forecasting, unrelated to money precision. **math_model.md currently specifies no canon rounding/precision policy for money** — that content lives only in code (`app/core/money.py`) and the skill file, not in the authoritative canon doc.

**4. `.claude/skills/finpilot-money-format/SKILL.md`** (full content read)

Key conventions already documented:
- "Деньги хранятся в **копейках, целым числом**. `Numeric(18, 2)` в БД, `int` в домене. `float` для денег запрещён"
- "Где нужна дробь при расчёте (проценты, доли распределения) — `decimal.Decimal` с явным контекстом, округление в конце операции, а не по пути."
- Rounding: "**`ROUND_HALF_UP`** — как считает бухгалтерия... Не `ROUND_HALF_EVEN`"
- Largest-remainder allocation rule: "считать все части вниз, остаток раздать по единице копейки в порядке приоритета"
- "Не форматировать деньги в бизнес-логике — только на границе представления"; "Не сравнивать суммы через `==` после арифметики с процентами"

(Примечание при синтезе плана батча v8.19.2: этот скилл описывает int-копейки-домен,
который не совпадает с фактической БД — `Numeric(14,2)` Decimal-рубли, не
`Numeric(18,2)` int-копейки. Расхождение не разбиралось в рамках этого батча — вне
периметра, отмечено как отдельная находка, не задача.)

**5. docs/ROADMAP.md** — no "Decimal" mentions found (grep returned nothing). The Decimal migration is **not tracked as a checkbox item in ROADMAP.md**; it only exists in `model_completion_plan.md` §6 item 2.5 and WATCHLOG mentions.

**6. Git history for `app/core/money.py`**

`git log --oneline -- app/core/money.py` returns exactly one commit, `05f819b`, "chore: восстановить git-историю проекта на состоянии v8.7.0" — the whole repo history was reset/reinitialized as a single snapshot commit (message: "Репозиторий был случайно инициализирован в $HOME прошлой сессией... Инициализирован заново внутри finpilot/, снимок текущего дерева зафиксирован как есть на v8.7.0"). There is **no earlier commit with original design rationale** — it was lost in the history reset. The rationale instead lives in the file's own docstring/comments (`app/core/money.py`): money-boundary rounding is P1.4 policy, `to_money()`/`money()` round via `ROUND_HALF_UP` at input/output boundaries (source of truth = DB `Numeric(14,2)`), while "Безразмерное ядро выбора (нормализация, веса, U(a)) сознательно остаётся float" (dimensionless scoring core intentionally stays float). `FLOW_EPS = 0.005` (half a kopeck) is documented as the float-arithmetic tolerance for flow `|Rt|`, tied to finding **R3-F1** from round 3 of certification — crisis mode must not trigger from rounding residue.
