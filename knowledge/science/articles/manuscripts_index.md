# Индекс рукописей — где что лежит (v5.18.2, после мёржа линий M+J)

> **Обновление v5.18.2 (консолидация вахт M+J).** Диета вахты M (v5.18.0) держала в репо только
> .pdf статей, а .md/.docx-исходники выносила к владельцу. Вахта J держала полное дерево
> .md-рукописей в репо. При мёрже .md-исходники **восстановлены в репо** (diff-friendly, greppable) —
> см. колонку «Исходник .md (в репо)». .docx-версии по-прежнему у владельца в `Наука.zip`.
> Суть и статусы публикаций — `../publications_status.md`.

| Статья | В репо (.pdf) | Исходник .md (в репо) | .docx у владельца (`Наука.zip`) |
|---|---|---|---|
| КИМ RU («Объяснимая гибридная СППР…») | `kim/Evdokimov_KIM_RU.pdf` | — | `Статьи/Статья журнал КИМ/Материалы/Evdokimov_KIM_RU.docx` |
| КИМ EN | `kim/Evdokimov_KIM_EN.pdf` | — | `…/Evdokimov_KIM_EN.docx` |
| Статья 1 (e-Informatica, requirements + эмпирика 322) | `submitted/Article_EISEJ_EvdokimovVM.pdf` (вёрстка подачи) | `submitted/article1_eisej_final.md` | `Статьи/Отправленные в журнал/Article1_EISEJ_FINAL.docx` |
| Статья 2 (Информатика и автоматизация, категоризация) | — | `submitted/article2_informatics_automation_final.md` | `…/Article2_InformaticsAutomation_FINAL.docx` |
| Статья 3 (Программирование ИСП РАН, архитектура) | — | `submitted/article3_programming_final.md` | `…/Article3_Programming_FINAL.docx` |
| Manuscript RU/EN (универсальная рукопись) | — | `submitted/manuscript_ru.md`, `submitted/manuscript_en.md` | `…/Evdokimov_manuscript_RU.docx`, `…_EN.docx` |
| Article 0 (версия для БИ ВШЭ, отказ по scope) | — | `other/article0_dss_model_crm_ru.md` | `Статьи/Article0_DSS_Model_CRM_RU_FINAL.docx` |
| An Explainable Hybrid DSS (EN-ветка) | — | `other/explainable_hybrid_dss.md` | `Статьи/An Explainable Hybrid Decision Support System for Personal Finance.docx` |
| Соавторская ветка (Бондаренко) ×2 | — | `other/coauthored_bondarenko/…` | `Статьи/В соавторстве с Бондаренко/…` |
| Cover letter (EISEJ) | — | `submitted/cover_letter.md` | `Статьи/Соло от организации/Cover_letter_Evdokimov.docx` |
| Научный метод (методичка) | суть в `../guides/` | `../guides/scientific_method.docx` (docx-методичка J) | `Научный_метод.docx` |

Фигуры статьи КИМ (6 png): канонично живут внутри `kim/replication_package.zip` (10 fig-вхождений,
распаковывается при подаче) **и** дополнительно распакованы в `kim/figures/` + `kim/replication_package/`
(browsable-копия из вахты J). Дубль намеренный: zip — замороженный сабмишен-артефакт, распакованное — рабочая копия.
