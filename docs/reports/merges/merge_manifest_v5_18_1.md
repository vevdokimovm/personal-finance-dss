# Merge-манифест — вахта M, линия v5.11.0 → v5.18.1 (2026-07-02/03)

> Для аккаунта-приёмника (V/J/S). **Канон = это дерево (v5.18.1).** Мержить по дисциплине
> `merge_and_fork_guide.md`: база — каноничная линия, дифф РЕАЛЬНЫХ деревьев (не журналов),
> union реестров, WATCHLOG-хирургия assert-guarded заменами, гейт смёрженного дерева на обеих БД.

## Батчи линии (все — 2026-07-02/03, аккаунт M)

| Версия | Суть |
|---|---|
| v5.12.0 | Методичка живого роадмапа → `knowledge/guides/roadmap_methodology.md` + механизм в шапке ROADMAP |
| v5.13.0 | (чужая вахта, принято по вотчлогу) §5.8 п.3+п.4-список, PIT-008 |
| v5.14.0 | Диаграммы: ER-drawio 28 таблиц программно, C4+ingestion/mfa, §9 деплой в diagrams.md, **7 stale PNG удалены** |
| v5.15.0 | 7 доков базы знаний (onboarding/glossary/api_contract+`docs/api/openapi.json` 106 путей/backup_restore/pdn_data_map/slo) + `tools/api_snapshot/` + INC-DELIVERY-STUB v2 + PIT-009 |
| v5.16.0 | `knowledge/science/` (научный трек, 42 файла) + инцидент доставки ЗАКРЫТ (корень: Tor Browser) |
| v5.17.0 | `tools/portrait_testing/` + `tests/test_portrait_property.py` (7 тестов) + свип 12 000 = 0 нарушений + отчёт |
| v5.18.0 | **Закрытие вехи 5**: диета −9.6 МБ, **перестановка вех**, LEGAL.md, конспект курса, `docs/roadmap_archive/` |
| v5.18.1 | Этот манифест (PATCH) |

## ⚠️ Опасные зоны мержа (читать до диффа)

1. **Перестановка вех (v5.18.0):** канон нумерации — **6=Тестирование, 7=Юридическое, 8=Фронтенд,
   9=Деплой** (было: 6=фронт, 7=тест, 8=юр). Если твоя линия правила ROADMAP/доки по СТАРОЙ
   нумерации — мержить по СМЫСЛУ, не по номеру; перекрёстные «веха N» в этой линии уже поправлены
   в 10 файлах. Снимок старого порядка — `docs/roadmap_archive/roadmap_2026_07_02_v5_17_0_pre_reorder.md`.
2. **Диета (v5.18.0) — НЕ ВОСКРЕШАТЬ удалённое.** Полный протокол путей —
   `docs/reports/releases/archive_diet_v5_18_0.md` (29 позиций: 13 .docx статей → только .pdf,
   6 фигур КИМ — дубли replication_package.zip, 4 бинарника ответов редакций → `responses_digest.md`,
   4 pitch-PDF — регенерируемы, `logo_reference_hq.png` → сжатый `logo_reference.png`).
   Отсутствие этих файлов в каноне — намеренное; при union «есть у тебя, нет здесь» для этих путей = НЕ добавлять.
   То же: 7 stale PNG диаграмм (v5.14.0) и `.mypy_cache` (исключён из zip навсегда).
3. **Версии при коллизии:** если твоя линия тоже ушла в 5.1x — консолидация под НОВОЙ версией
   без переписывания канонической истории (правило мерж-дисциплины); CHANGELOG — union записей по датам.
4. **WATCHLOG §3:** окно ровно 10 (сейчас 5.18.1→5.9.0); чужие версии вставлять хирургией, старьё — вниз за борт.
5. **ROADMAP-галки к union:** §5.5 [x] (банки), §5.8 полностью [x], §5.9 [x] (наука, private-only),
   §6.2 суб-[x] (портретная инфраструктура), веха 5 в таблице — «Завершена (v5.18.0)»,
   механизм п.6 — «Предложения Claude» как ворота закрытия вехи.

## Файловая карта линии (для диффа деревьев)

**Добавлено:** `LEGAL.md` · `docs/api/openapi.json` · `docs/onboarding.md` · `docs/glossary.md` ·
`docs/api_contract.md` · `docs/backup_restore.md` · `docs/pdn_data_map.md` · `docs/slo.md` ·
`docs/roadmap_archive/{README.md, roadmap_…pre_reorder.md}` ·
`docs/reports/incidents/inc_chat_file_delivery_dead_stub.md` ·
`docs/reports/releases/archive_diet_v5_18_0.md` · `docs/reports/testing/portrait_sweep_2026_07.md` ·
`docs/reports/merges/merge_manifest_v5_18_1.md` · `knowledge/science/**` (после диеты ~28 файлов,
вкл. `articles/manuscripts_index.md`, `articles/journal_responses/responses_digest.md`) ·
`knowledge/business/solution_factory_course.md` · `knowledge/business/pitch/README.md` ·
`knowledge/guides/roadmap_methodology.md` · `tools/api_snapshot/dump_openapi.py` ·
`tools/portrait_testing/{__init__,generator,invariants,runner}.py` · `tests/test_portrait_property.py`.

**Изменено (ключевое):** `docs/ROADMAP.md` (механизм, §5.9, перестановка вех, таблица, указатель) ·
`docs/WATCHLOG.md` (шапка/§0/§3/§4) · `CHANGELOG.md` (+8 записей) · `app/config.py` (5.18.1) ·
`docs/diagrams.md` (§1/§2/§5/§7 переписаны + §9) · `docs/diagrams/{06_c4_component,10_er_database,all_diagrams}.drawio` ·
`docs/pitfalls.md` (PIT-008, PIT-009 v2-закрыт) · `docs/session_continuity.md` (правило доставки) ·
`docs/reports/incidents_summary.md` (+строка, закрыт) · `docs/naming_convention.md` (лого) ·
`knowledge/science/{README,kim_submission_checklist}.md` · 10 доков — правка ссылок «веха N».

**Удалено:** см. зону 2 (диета + stale PNG). **Переименовано/заменено:**
`knowledge/brand/logo_reference_hq.png` → `logo_reference.png` (800px, 489K).

## Гейты приёмки смёрженного дерева

flake8 по всему репо = 0 · mypy (как минимум `tools/`, `tests/test_portrait_property.py`) ·
`pytest tests/test_portrait_property.py` + смежные ядра — зелёные · матрица SQLite+PostgreSQL ·
контроль: `python -m tools.portrait_testing.runner --n 25` → violations=0, crashes=0 ·
WATCHLOG §3 = 10 строк · `unzip`-архив ≤ 12 МБ.

## Pending на момент манифеста

Манифест публикации public-зеркала — на подтверждении владельца (пуш НЕ делан) ·
веха 6 (тестирование, v6.0.0) — старт по команде · PNG-превью диаграмм — Mac («Ожидается») ·
предложения по бэку (8 шт) выданы владельцу — решения не приняты.
