# docs/diagrams/ — диаграммы архитектуры и модели

Технические диаграммы проекта в формате **draw.io** (`.drawio`) с превью (`.png`/`.svg`).
Мастер-файл со всеми диаграммами — `all_diagrams.drawio`.

## Состав (по ГОСТ и нотациям)
- Пайплайн и модель: `01_main_pipeline_GOST`, `02_avalanche_GOST`, `03_goals_si_GOST`, `15_forecast_GOST`.
- Архитектура C4: `04_c4_context`, `05_c4_container`, `06_c4_component`.
- Поведение: `07_sequence_planning`, `08_sequence_import`, `09_state_machine`, `13_usecase`.
- Данные: `10_er_database`, `11_uml_class`, `14_dependency_graph`.
- Процессы/нотации: `12_idef0`, `16_pdca`, `17_bpmn`, `18_epc`, `19_vsm`, `20_dmaic`.

Описания к диаграммам (историческая ВКР-редакция, модель v2.0.2 — **legacy**, каноничная модель
проекта — v3.0.0): `diagrams_vkr_v2_0_2.md`, `diagrams_full_set_v2_0_2.md`.

> Бизнес-диаграммы (canvas, journey, SWOT, monetization, roadmap) — отдельно в
> `knowledge/business/diagrams/`.

Правило для draw.io: не использовать символы `∈ ≠ ∅` в значениях атрибутов (краш WebKit).
