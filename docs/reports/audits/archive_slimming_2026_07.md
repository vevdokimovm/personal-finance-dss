# Ревизия: похудение архива v5.18.0 (2026-07-03)

> Приказ владельца: архив ≤ 15 МБ, желательно ≤ 12 МБ. Критерий №1 — сохранить всю
> суть/идеи/логику, вес — критерий №2. Результат: **zip 18.1 МБ → ~8.9 МБ**,
> распаковано 34 МБ → ~14.8 МБ. Ничего содержательное не потеряно: удалялись только
> кэш, байт-в-байт дубли, производные (регенерируемые) артефакты и бинарные
> близнецы при живом каноне; уникальные docx конвертированы в md с сохранением текста.

## 1. Страховочная сетка (почему удалять безопасно)

Каждый удалённый бинарник существует минимум в одном из мест: (а) локально у
владельца (Mac/почта), (б) в assets GitHub-релизов приватного репо — релизы
v5.16.0/v5.17.0 содержат полные архивы с этими файлами, история релизов не
переписывается. Архив = средство переноса контекста, не единственное хранилище.

## 2. Реестр действий

### 2.1. Утечка упаковки (−9.3 МБ распаковано)

- `.mypy_cache/` — кэш попал в архив v5.17.0 (нарушение чистой сборки). Удалён;
  канонический exclude-лист сборки закреплён в `docs/sandbox_runbook.md` §Сборка
  чистого архива (раньше жил только «в голове» — потому и утёк).

### 2.2. Байт-в-байт дубли (md5-совпадение)

| Удалено | Канон остаётся |
|---|---|
| `knowledge/survey_auditory/results/finpilot_recommendations.md` | `knowledge/survey_auditory/product_additions_from_research.md` |
| `knowledge/guides/scientific_article_gost.md` | `knowledge/science/guides/scientific_article_gost_guide.md` |
| `knowledge/survey_auditory/results/README.md` (копия анализа) | `knowledge/survey_auditory/survey_analysis.md`; в `results/` — новый короткий указатель |

### 2.3. Производные артефакты (регенерируются детерминированно)

- `knowledge/survey_auditory/results/finpilot_report.html` + 14 PNG-графиков
  (−1.1 МБ) — выход пайплайна `tools/survey_analysis/run_analysis.py` из
  `raw/survey_responses_385.xlsx`. Числа остаются в `results.json`, выводы — в md.
- Фигуры внутри `replication_package.zip` дублировали `kim/figures/` — zip
  распакован в `kim/replication_package/` (скрипты `.py` + `results*.json` +
  README), фигуры не дублируются (−0.67 МБ с учётом оставленного текста).

### 2.4. Бинарные близнецы при живом каноне

- `pitch_en.pdf`, `pitch_intl_en.pdf` (−1.2 МБ) — переводы `pitch_ru.pdf` /
  `pitch_intl_ru.pdf`; сценарии EN остаются в `pitch_script_en.md` /
  `pitch_intl_script_en.md`.
- `Evdokimov_KIM_RU.docx`, `Evdokimov_KIM_EN.docx` (−0.7 МБ) — PDF-близнецы
  остаются (правило владельца: «статьи можно оставить только .pdf»).

### 2.5. Уникальные научные docx → md-текст (−2.9 МБ → ~0.3 МБ текста)

Формулы/вёрстка не переносились — сохранена суть для контекста; финальные docx —
у владельца + в release assets. Конвертированы (новые snake_case имена):

| Было | Стало |
|---|---|
| `submitted/Article1_EISEJ_FINAL.docx` | `submitted/article1_eisej_final.md` |
| `submitted/Article2_InformaticsAutomation_FINAL.docx` | `submitted/article2_informatics_automation_final.md` |
| `submitted/Article3_Programming_FINAL.docx` | `submitted/article3_programming_final.md` |
| `submitted/Evdokimov_manuscript_RU.docx` | `submitted/manuscript_ru.md` |
| `submitted/Evdokimov_manuscript_EN.docx` | `submitted/manuscript_en.md` |
| `submitted/Cover_letter_Evdokimov.docx` | `submitted/cover_letter.md` |
| `other/An_Explainable_Hybrid_DSS_Personal_Finance.docx` | `other/explainable_hybrid_dss.md` |
| `other/Article0_DSS_Model_CRM_RU_FINAL.docx` | `other/article0_dss_model_crm_ru.md` |
| `other/coauthored_bondarenko/Statya_RU_SPPR_personalnye_finansy.docx` | `.../statya_ru_sppr_personalnye_finansy.md` |
| `other/coauthored_bondarenko/Evdokimov_DSS_personal_finance_article.docx` | `.../dss_personal_finance_article.md` |

### 2.6. Скрины писем редакций → текст (−0.5 МБ)

`e_informatica_response.png`, `programming_ispran_response.png` → суть в
`journal_responses/notes.md`. Официальные PDF-документы (отказ БИ, пруф вёрстки,
authors agreement, справка РИНЦ) — остаются как есть.

### 2.7. Нейминг (конвенция `docs/naming_convention.md`)

Оставшиеся научные PDF переименованы в snake_case; маппинг «имя подачи → имя в
репо» зафиксирован в `kim_submission_checklist.md` и `publications_status.md`:
`Evdokimov_KIM_RU.pdf → kim_ru.pdf`, `Evdokimov_KIM_EN.pdf → kim_en.pdf`,
`Article_EISEJ_EvdokimovVM.pdf → eisej_submission.pdf`. Шрифты
`LiberationSans-*.ttf` и суффикс `_GOST` у диаграмм — канонические имена,
конвенцией допущены, не трогались.

### 2.8. Лого-эталон (−1.9 МБ)

`knowledge/brand/logo_reference_hq.png`: 4096×3796 (2.0 МБ) → 1200×1112 +
квантизация 256 цветов (121 КБ). Для флэт-лого визуально без потерь; оригинал HQ —
у владельца + в release assets. Заметка — в `logo_passport.md`.

## 3. Что сознательно НЕ трогали

- `docs/diagrams/*.drawio.png` (11 превью, 1.0 МБ) — актуальные (курировались
  v5.14.0), регенерация требует Mac; бюджет позволяет.
- `app/assets/fonts/` (0.8 МБ) — runtime-актив PDF-экспорта.
- `tests/full/vendor/axe.min.js` (0.6 МБ) — детерминизм full-CI дороже веса.
- Сырьё исследований (`raw/`), официальные PDF подач/ответов, `CHANGELOG.md` —
  первоисточники и история.

## 4. Правило на будущее

Перед каждой сборкой: `md5sum`-проверка на дубли не нужна (одноразовая чистка
сделана), но exclude-лист из runbook обязателен. Новые тяжёлые бинарники (>300 КБ)
попадают в архив только если это первоисточник; производное — регенерация + заметка.
