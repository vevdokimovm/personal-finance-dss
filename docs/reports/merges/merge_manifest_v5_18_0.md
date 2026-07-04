# Merge-манифест линии v5.18.0 — похудение архива + перенумерация вех 6↔7

> Инстанс процедуры `merge_and_fork_guide.md` для ЭТОЙ линии. Читает аккаунт,
> который будет сливать v5.18.0 с любой параллельной линией (V/J/M/S).

## 1. TL;DR для мёржера

Линия **docs-only** (код `app/` не тронут, кроме `config.py` bump). Три опасности:
(1) **перенумерация вех**: теперь 6=тестирование, 7=фронт — любая параллельная
линия со «веха 6/7» в старом смысле семантически конфликтует, текстовый diff это
НЕ ловит; (2) **массовые удаления/переименования** в `knowledge/` — параллельная
правка удалённого файла = потерянная работа, сверяй реестр §2.3; (3) WATCHLOG/
ROADMAP/CHANGELOG переписаны крупно — append-конфликты будут, это норма.

## 2. Surface — что именно изменено

### 2.1. Код

- `app/config.py` — только `APP_VERSION` 5.17.0 → 5.18.0. Больше НИЧЕГО в `app/`.

### 2.2. Изменённые файлы (контент)

- `docs/ROADMAP.md` — таблица вех (статусы 4/5 = Завершена; 6=тестирование
  «Следующая», 7=фронт), порядок «тест → фронт», свап тел вех с перенумерацией
  §6.x↔§7.x, §5.9 перенесён внутрь вехи 5, новый указатель «СЛЕДУЮЩАЯ ЗАДАЧА»
  (веха 6 §6.3 + §6.1), «Ожидается» + пункт манифеста зеркала, ссылка на реестр.
- Свип «веха 6/7» (7→6 тестирование, 6→7 фронт): `docs/api_contract.md`,
  `docs/glossary.md`, `docs/slo.md`, `docs/universal_statement_parser_strategy.md`,
  `docs/reports/testing/portrait_sweep_2026_07.md`,
  `docs/reports/adr/adr_001_frontend_stack.md`,
  `knowledge/guides/roadmap_methodology.md`, `knowledge/product/banks_registry.md`,
  `knowledge/product/banks_statements_reference.md`.
- `tools/publish/finpilot_publish_public.sh` — `sanitize_tree()` (README-бейдж и
  футер, LICENSE-холдер, DEPLOY clone-URL) + GUARD 3/3 (скан личных имён) + `SED=`.
- `docs/sandbox_runbook.md` — новый раздел «Сборка чистого архива» (exclude-канон,
  добавлен `.mypy_cache`).
- Правки ссылок после удалений: `knowledge/science/README.md`,
  `publications_status.md`, `kim_submission_checklist.md`,
  `knowledge/survey_auditory/product_additions_from_research.md`.
- `README.md` — бейдж версии (5.13.0 → 5.18.0; был протухшим), строка про LEGAL.md.
- `CHANGELOG.md`, `docs/WATCHLOG.md` — записи батча (append-зона).

### 2.3. Удалено / переименовано (не восстанавливать при мёрже!)

Полный реестр с обоснованиями — `docs/reports/audits/archive_slimming_2026_07.md`.
Классы: `.mypy_cache/`; 3 md-дубля; `pitch_en.pdf`+`pitch_intl_en.pdf`;
KIM docx-близнецы; `replication_package.zip`→распакован в `replication_package/`;
2 PNG-скрина писем→`journal_responses/notes.md`; survey `finpilot_report.html`+14 PNG;
10 научных docx→md (таблица переименований в отчёте);
`Evdokimov_KIM_*.pdf`→`kim_ru/en.pdf`, `Article_EISEJ_*.pdf`→`eisej_submission.pdf`;
лого 4096px→1200px/256цв.

### 2.4. Новые файлы

`LEGAL.md` (корень) · `docs/roadmap_registry.md` · `docs/public_mirror_manifest.md` ·
`docs/reports/audits/archive_slimming_2026_07.md` ·
`knowledge/business/pitch/solution_factory_methodology.md` ·
`knowledge/business/pitch/eventify_channel_analysis.md` ·
`knowledge/survey_auditory/results/README.md` (указатель) ·
`knowledge/science/articles/journal_responses/notes.md` ·
`knowledge/science/articles/kim/replication_package/` (7 файлов) ·
10 md-конвертаций научных статей · этот манифест.

### 2.5. НЕ тронуто — исключить из мёрджа сразу

`app/` (кроме config-бампа), `tests/`, `alembic/`, `frontend/`, `deploy/`,
`nginx/`, `.github/`, все диаграммы `docs/diagrams/`, шрифты.

## 3. Зоны риска конфликта с другими вахтами

1. **Семантика номеров вех** — параллельный текст «веха 6 (фронт)» после мёрджа
   станет ложью. Правило: при слиянии прогнать
   `grep -rn "вех[аиеу] [67]" --include="*.md"` и выровнять по R3
   (6=тестирование, 7=фронт), карта — `docs/roadmap_registry.md`.
2. **ROADMAP.md** — структурный rewrite; чужие правки старой структуры вливать
   вручную в новую (не наоборот).
3. **Удалённые файлы** — если параллельная линия их правила, перенести правку в
   канон-преемник (таблицы соответствия в отчёте похудения), файл не воскрешать.
4. **WATCHLOG §3** — обе линии добавят версию сверху; после слияния окно снова
   РОВНО 10 (лишнее старое — удалить).
5. **`finpilot_publish_public.sh`** — если другая линия трогала allow-list,
   слить списки; `sanitize_tree`/GUARD 3/3 сохранить обязательно.

## 4. Инварианты-контракты — НЕ сломать при слиянии

- **I1.** Веха 6 = тестирование, веха 7 = фронт (редакция R3) — во ВСЕХ доках
  после мёрджа единообразно.
- **I2.** Архив ≤ 15 МБ zip; exclude-канон runbook применяется при каждой сборке.
- **I3.** Удалённые бинарники не возвращаются в архив (страховка — release assets).
- **I4.** `results/` держит только невоспроизводимое (raw остаётся, производные — нет).
- **I5.** Санитайзер + три GUARD-слоя в публикаторе не ослабляются; зеркало не
  пушится до подтверждения манифеста владельцем.
- **I6.** WATCHLOG §3 — ровно 10 версий.

## 5. Чек-лист слияния этой линии

1. Сверить `APP_VERSION` обеих линий; целевая = максимальная, CHANGELOG — обе записи.
2. ROADMAP: за базу берётся версия ЭТОЙ линии (R3-структура), чужие чекбоксы/
   тексты вливаются поверх.
3. Прогнать grep-свип номеров вех (п.3.1) по итоговому дереву.
4. Проверить, что ни один файл из §2.3 не вернулся (diff по списку отчёта).
5. WATCHLOG: объединить §0/§4, окно §3 = 10.
6. `bash -n tools/publish/finpilot_publish_public.sh` + глазами: санитайзер и
   GUARD 3/3 на месте.
7. Гейты: fast-тесты зелёные (docs-линия их не трогала — регресс значит конфликт
  мёрджа), `flake8 .` = 0, свежий zip по exclude-канону ≤ 15 МБ.

## 6. Семантические конфликты — особое внимание

Текстовый diff НЕ покажет: (а) чужой док, ссылающийся на `finpilot_report.html`
или старые имена docx — ссылка станет битой, чинить по таблицам отчёта похудения;
(б) чужой текст «фронт — следующая веха» — переписать под R3; (в) чужая инструкция
сборки архива без exclude-канона — заменить ссылкой на runbook-раздел.
