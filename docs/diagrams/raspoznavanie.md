# Разбор: 11 диаграмм FINPILOT (production, v3.0.0 модели)

> Дата: 2026-08-27 · метод — `07-media-to-text-lab/METHOD_IMAGES.md`.
> Источник истины — `.drawio` (см. `README.md` рядом); эти 11 `.png` — актуальный
> рендер (не входят в список «ждут регенерации» из README на момент разбора).
> Отличается от учебных диаграмм в `academic-portfolio/08-masters/vkr/diagrams/`:
> здесь — боевая версия с реальными именами модулей/функций кода, не курсовая работа.

## 0a. Дословный захват

- **`03_goals_si_GOST.drawio.png`** — «Начало: calculate_goals_si» блок-схема
  ГОСТ. Ввод: сумма на цели x_goals, список целей G, дата today → ромб
  «x_goals≤0 или G пуст?» → да: вернуть Si=0,allocation={} → …иначе для каждой цели
  s с остатком>0: urgency=max(1,12/месяцев_до_дедлайна), weight=вес категории ks,
  priority=weight·urgency → total_priority=Σpriority → ромб «total_priority≤0?»
  → да: тот же ранний выход → для каждой цели: share=priority_s/total_priority,
  x_s=min(x_goals·share,остаток_s), allocation[s]=x_s, weighted_x+=x_s·priority_s,
  weighted_total+=остаток_s·priority_s → Si=min(weighted_x/weighted_total,1.0) →
  Вывод: Si, allocation{цель→сумма} → Конец.
- **`04_c4_context.drawio.png`** — «FINPILOT — Контекст системы (C4 Level 1)».
  «Пользователь [Человек] — Физлицо, планирующее личные финансы» → «Вводит данные,
  получает рекомендации [HTTPS]» → «FINPILOT [Программная система] — СППР:
  распределение свободного денежного потока между погашением долга, резервом и
  целями». Пользователь → «Выгружает выписку» → «Банковская выписка [Внешняя
  система] — CSV/Excel из Тинькофф, Сбер, Альфа, ВТБ и др.» → «Импорт транзакций
  [CSV upload]» → FINPILOT.
- **`08_sequence_import.drawio.png`** — «FINPILOT — Импорт банковской выписки
  (POST /api/banks/import)». Дорожки: Пользователь, routes_banks, statement_parser,
  parse_bank_statement, crud. POST /banks/import{file,bank_id} → parse_bank_
  statement(content,bank_id) → «выбор парсера по bank_id (tinkoff/sber/universal)»
  → loop по строкам CSV: _get_field(row,candidates), _parse_date()+нормализация
  суммы, «тип=expense если сумма<0, иначе income» → list[transaction dict] →
  распарсенные транзакции → loop для каждой транзакции: create_transaction
  (is_synced=True) → сохранено → {imported: N, transactions}.
- **`09_state_machine.drawio.png`** — «FINPILOT — Жизненный цикл альтернативы (UML
  State Machine)». [start] → Generated --evaluate_alternative()
  Avalanche+Si+пересчёт Rt'/Lt'/Dt'--> Evaluated --нарушено ограничение--> Rejected
  [end]; Evaluated --проходит фильтр Rt'≥0∧Lt'≥Lmin∧Dt'≤Dmax--> Admissible
  --rank_alternatives() расчёт U(a) по SAW--> Ranked --U(a) максимальна (a* первая)-->
  Recommended --explain_alternative() gains/costs/insight--> Explained [end];
  Ranked --U(a) не максимальна--> NotSelected [end].
- **`11_uml_class.drawio.png`** — «FINPILOT — Диаграмма классов (UML Class)». Блок
  «ORM-модели (app/database/models.py)»: `Transaction`(id,amount,category,type,
  date,is_synced), `Obligation`(id,name,amount,interest_rate,term,monthly_payment,
  payment_day), `Goal`(id,name,target_amount,current_amount,deadline,category),
  `LiquidAsset`(id,name,amount,interest_rate,type), `UserPrefs`(id,l_min,
  risk_tolerance,horizon,r_bench). Блок «Сервисы и модули ядра (app/services,
  app/core)»: `PlanningService`(planning.py, run_planning()) «use»→ `Metrics`
  (metrics.py: calculate_rt/lt/dt/blr/cft), `Alternatives`(alternatives.py:
  generate_alternatives(),evaluate_alternative()), `Avalanche`(avalanche.py:
  allocate_obligations_avalanche()), `GoalsPriority`(goals_priority.py:
  calculate_goals_si(),preallocate_from_bliq()); дальше Alternatives→`Ranking`
  (ranking.py: RISK_PROFILES,rank_alternatives()), Avalanche→`Filtering`
  (filtering.py: filter_alternatives()).
- **`12_idef0.drawio.png`** — «FINPILOT — Функциональный контекст (IDEF0, диаграмма
  A-0)». Блок A0 «Поддержать принятие финансового решения (сгенерировать и
  ранжировать альтернативы распределения Rt)». Вход: Транзакции It,Ej;
  Обязательства O, цели G; Ликвидная позиция Bliq. Управление: Профиль риска R
  (веса U), Пороги Lmin/Dmax/r_bench, Нормы Greninger/ЦБ РФ. Механизм: Алгоритм
  SAW+Avalanche, FastAPI+SQLAlchemy. Выход: Оптимальная альтернатива a*, Top-3 +
  объяснения, Показатели Rt,Lt,Dt,BLR.
- **`13_usecase.drawio.png`** — «FINPILOT — Варианты использования (UML Use
  Case)». Актор «Пользователь» → Вести транзакции, Вести обязательства, Вести цели
  накопления, Вести ликвидные активы, Настроить профиль риска и пороги,
  Импортировать выписку (--include--> Расчитать базовые показатели, стрелка идёт
  и к актору «Банк (CSV/API)»), **«Получить рекомендацию (полный цикл СППР)»**
  (выделен зелёным) --include--> Рассчитать базовые показатели, Применить
  Avalanche+OCR-фильтр, Ранжировать по SAW; «Посмотреть borд показателей»
  --extend-- от «Получить рекомендацию»; «Построить прогноз Rt/Lt/Dt» отдельно.
  (Название фильтра на диаграмме — «OCR-фильтр»: похоже на опечатку/устаревшее
  имя для фильтра допустимости, реального OCR в системе нет — не поправлял,
  дословный захват.)
- **`14_dependency_graph.drawio.png`** — «FINPILOT — Граф зависимостей модулей
  (импорты между пакетами)». Четыре кластера: `app/api` (router→routes_planning,
  routes_recommendation; router→routes_banks), `app/services` (routes_planning→
  planning→pipeline; routes_banks→forecasting→statement_parser;
  forecasting→bank_api), `app/core` (preprocessing, metrics→filtering→
  recommendation, alternatives→avalanche, goals_priority, ranking→forecast — с
  вертикальными связями от routes_planning/routes_recommendation вниз в core),
  `app/database` (crud→models→db, ещё связь bank_api→crud).
- **`15_forecast_GOST.drawio.png`** — «FINPILOT — Прогнозирование показателей
  (SES + Monte-Carlo), ГОСТ 19.701-90». Начало: forecast_indicator(history,h) →
  Ввод: ряд history, горизонт h, α=0.3, N=1000 → ромб «len(history)≥2?» → нет:
  плоский прогноз (последнее значение×h) → да: Этап1 сглаживание Brown SES
  (Lt=α·yt+(1−α)·Lt−1) → Этап2 оценка тренда b (линейная аппроксимация) →
  Этап3 точечный прогноз ŷ(t,h)=Lt+b·h → подготовка σ_e=std(остатки),
  σ(h)=σ_e·√(1+0.5·h) → Этап4 Monte-Carlo N=1000: шум ε_h~N(0,σ(h)²) к точечному
  прогнозу → Этап5 перцентили по ансамблю p10,p50(медиана),p90=доверительный
  интервал → Вывод {point:ŷ, lower:p10, median:p50, upper:p90} → Конец.
- **`16_pdca.drawio.png`** — «FINPILOT — Управление личными финансами как цикл
  PDCA (Деминга)». Четыре блока по кругу вокруг центра «Непрерывное улучшение
  финансового состояния»: PLAN — задать цели/профиль риска/пороги Lmin-Dmax,
  запустить расчёт → DO — исполнять рекомендованное распределение Rt (платить по
  обязательствам, пополнять резерв и цели) → CHECK — импортировать новую выписку,
  сравнить факт. показатели (Rt,Lt,Dt,BLR) с планом на дашборде → ACT —
  скорректировать цели/профиль риска/пороги, перезапустить планирование → обратно
  в PLAN.
- **`19_vsm.drawio.png`** — «FINPILOT — Карта потока создания ценности (VSM): от
  данных до решения». Пользователь(вход) → Ввод/импорт данных (ручной ввод: может
  занять дни/недели, вне системы) → Расчёт показателей (VA≈5мс, метрики из
  транзакций) → Генерация+оценка альтернатив (VA≈50мс, 21 альт.×Avalanche+Si) →
  Фильтрация+ранжирование (VA≈5мс, SAW по допустимым) → Объяснение NLG (VA≈2мс,
  шаблоны Top-3) → Решение(выход). Timeline: «Lead Time ≈ дни (ручной сбор данных
  пользователем — главные потери, вне ПО)» (красным); «Processing Time (VA) ≈
  62 мс — полный расчётный цикл СППР после нажатия кнопки» (зелёным). Итог VSM
  текстом: «вычислительная ценность создаётся за десятки миллисекунд; основное
  "время потока" — ручной ввод данных. Точка улучшения — автоматизация импорта
  (банковские выписки), что и реализовано через statement_parser».

## 0b. Синтез

Полный технический паспорт продакшен-версии FINPILOT (модель v3.0.0, отличается
от учебной ВКР-версии реальными именами модулей): контекст C4, домен (классы/
IDEF0/use-case), поведение (импорт выписки — sequence, жизненный цикл альтернативы
— state machine, прогноз SES+Monte-Carlo — ГОСТ блок-схема, генерация целевого
распределения Si — ГОСТ блок-схема), инженерный граф зависимостей модулей,
и два управленческих слоя поверх системы (PDCA-цикл использования, VSM-анализ
потерь времени — вывод: узкое место не вычисления (62 мс), а ручной ввод данных
пользователем).

## 0c. Кросс-файл

Найдена вероятная опечатка/устаревшее название на `13_usecase.drawio.png`:
подпись «Применить Avalanche + **OCR**-фильтр» — в остальных 10 диаграммах и в
именах модулей (`filtering.py`, `avalanche.py`) речь везде о фильтре
**допустимости** (feasibility/allowance), не о распознавании текста; в системе
нет OCR-компонента. Не правил рисунок — читается дословно, помечено как
находка для владельца.

Источник — `.drawio` (README прямо называет его каноном); эти `.png` — рендер на
момент разбора. 9 диаграмм папки (`01,02,05,06,07,10,17,18,20`) без актуального
превью не описаны — README прямо говорит, что их картинки ждут регенерации или
никогда не рендерились; описывать по устаревшему/несуществующему изображению
означало бы гадать, а не читать.

🔴 **Уточнение 27.08.2026**: живой интерфейс FINPILOT подписывает `r_bench`
именно как **«r_bench (OCR)»** (см. `academic-portfolio/01-bachelor-thesis/
figures/product-screenshots/raspoznavanie.md`, кадр `04.jpg`) — «OCR-фильтр» на
диаграмме use-case, возможно, не опечатка, а устоявшееся в проекте сокращение
(вероятно Opportunity Cost Rate). Вывод «вероятная опечатка» выше — не факт,
решение/подтверждение за владельцем.
