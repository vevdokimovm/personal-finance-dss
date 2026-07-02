# docs/diagrams/ — диаграммы архитектуры и модели

Технические диаграммы проекта в формате **draw.io** (`.drawio`) с превью (`.png`/`.svg`).
Мастер-файл со всеми диаграммами — `all_diagrams.drawio`.

## Состав (по ГОСТ и нотациям)
- Пайплайн и модель: `01_main_pipeline_GOST`, `02_avalanche_GOST`, `03_goals_si_GOST`, `15_forecast_GOST`.
- Архитектура C4: `04_c4_context`, `05_c4_container`, `06_c4_component`.
- Поведение: `07_sequence_planning`, `08_sequence_import`, `09_state_machine`, `13_usecase`.
- Данные: `10_er_database`, `11_uml_class`, `14_dependency_graph`.
- Процессы/нотации: `12_idef0`, `16_pdca`, `17_bpmn`, `18_epc`, `19_vsm`, `20_dmaic`.

Историческая ВКР-редакция описаний диаграмм (модель v2.0.2) удалена как **legacy** — каноничная
модель проекта v3.0.0. Исходники диаграмм — `all_diagrams.drawio`, рендеры — `*.drawio.png` в этой папке.

> Бизнес-диаграммы (canvas, journey, SWOT, monetization, roadmap) — отдельно в
> `knowledge/business/diagrams/`.

Правило для draw.io: не использовать символы `∈ ≠ ∅` в значениях атрибутов (краш WebKit).

## Превью (PNG)

Источник истины — `.drawio` (XML); PNG — производный артефакт. Рендер в песочнице невозможен
(CDN Chromium заблокирован), поэтому после правки источника протухшее превью **удаляется**,
а регенерация делается на Mac (drawio desktop → File → Export as → PNG, масштаб 1.5).

**Ждут регенерации на Mac (источник изменён v5.12.0–v5.14.0):**
`05_c4_container` · `06_c4_component` (+ ingestion/MFA) · `07_sequence_planning` ·
`10_er_database` (полная регенерация: 28 таблиц) · `17_bpmn` · `18_epc` · `20_dmaic` ·
`01_main_pipeline_GOST` и `02_avalanche_GOST` (превью не было изначально).

Мастер `all_diagrams.drawio` синхронизирован постранично (страницы ER и C4 L3 обновлены v5.14.0).
