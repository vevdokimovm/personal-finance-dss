# Диета архива — v5.18.0 (приказ владельца: ≤15 МБ, цель ≤12)

> Критерий №1 — сохранить интеллектуальную составляющую; №2 — вес.
> Каждая позиция: что убрано → куда делась суть / где оригинал.

| Файл | КБ | Суть/оригинал |
|---|---|---|
| `knowledge/science/articles/kim/Evdokimov_KIM_RU.docx` | 353 | manuscripts_index.md → Наука.zip владельца |
| `knowledge/science/articles/kim/Evdokimov_KIM_EN.docx` | 354 | manuscripts_index.md → Наука.zip владельца |
| `knowledge/science/articles/submitted/Evdokimov_manuscript_RU.docx` | 352 | manuscripts_index.md → Наука.zip владельца |
| `knowledge/science/articles/submitted/Evdokimov_manuscript_EN.docx` | 347 | manuscripts_index.md → Наука.zip владельца |
| `knowledge/science/articles/submitted/Article1_EISEJ_FINAL.docx` | 155 | manuscripts_index.md → Наука.zip владельца |
| `knowledge/science/articles/submitted/Article2_InformaticsAutomation_FINAL.docx` | 199 | manuscripts_index.md → Наука.zip владельца |
| `knowledge/science/articles/submitted/Article3_Programming_FINAL.docx` | 303 | manuscripts_index.md → Наука.zip владельца |
| `knowledge/science/articles/submitted/Cover_letter_Evdokimov.docx` | 9 | manuscripts_index.md → Наука.zip владельца |
| `knowledge/science/articles/other/Article0_DSS_Model_CRM_RU_FINAL.docx` | 351 | manuscripts_index.md → Наука.zip владельца |
| `knowledge/science/articles/other/An_Explainable_Hybrid_DSS_Personal_Finance.docx` | 357 | manuscripts_index.md → Наука.zip владельца |
| `knowledge/science/articles/other/coauthored_bondarenko/Statya_RU_SPPR_personalnye_finansy.docx` | 351 | manuscripts_index.md → Наука.zip владельца |
| `knowledge/science/articles/other/coauthored_bondarenko/Evdokimov_DSS_personal_finance_article.docx` | 346 | manuscripts_index.md → Наука.zip владельца |
| `knowledge/science/guides/scientific_method.docx` | 47 | manuscripts_index.md → Наука.zip владельца |
| `knowledge/science/articles/kim/figures/fig3_forecast_en.png` | 137 | дубль replication_package.zip |
| `knowledge/science/articles/kim/figures/fig2_heatmap.png` | 109 | дубль replication_package.zip |
| `knowledge/science/articles/kim/figures/fig1_pipeline_en.png` | 130 | дубль replication_package.zip |
| `knowledge/science/articles/kim/figures/fig1_pipeline.png` | 130 | дубль replication_package.zip |
| `knowledge/science/articles/kim/figures/fig2_heatmap_en.png` | 115 | дубль replication_package.zip |
| `knowledge/science/articles/kim/figures/fig3_forecast.png` | 136 | дубль replication_package.zip |
| `knowledge/science/articles/other/fig_function_tree_en.png` | 232 | фигура есть в текстах статей; оригинал у владельца |
| `knowledge/science/articles/journal_responses/business_informatics_hse_response.pdf` | 382 | responses_digest.md |
| `knowledge/science/articles/journal_responses/e_informatica_response.png` | 261 | responses_digest.md |
| `knowledge/science/articles/journal_responses/programming_ispran_response.png` | 223 | responses_digest.md |
| `knowledge/science/articles/journal_responses/e_informatica_draft_proof.pdf` | 461 | responses_digest.md |
| `knowledge/business/pitch/pitch_ru.pdf` | 621 | регенерация p013_render.py; README в папке |
| `knowledge/business/pitch/pitch_en.pdf` | 608 | регенерация p013_render.py; README в папке |
| `knowledge/business/pitch/pitch_intl_ru.pdf` | 607 | регенерация p013_render.py; README в папке |
| `knowledge/business/pitch/pitch_intl_en.pdf` | 591 | регенерация p013_render.py; README в папке |
| `knowledge/brand/logo_reference_hq.png` | 1550 | сжат до logo_reference.png (489K, 800px); HQ-исходник у владельца |

**Итого высвобождено: ~9.6 МБ.** Плюс из zip исключён `.mypy_cache/`
(кэш mypy, регенерируемый — раньше протекал в архив).

Не тронуто осознанно: `survey_questionnaire_62q.pdf` (первичный артефакт исследования,
нужен статье 1), `finpilot_report.html` (витринный результат опроса), `axe.min.js`
(вендор a11y-CI), шрифты `app/assets/fonts` (прод-функционал PDF-экспорта),
`replication_package.zip` (научная воспроизводимость КИМ).
