# Г41 — Какие ещё математические рамки существуют для задачи FINPILOT и что из них взять в ядро (сырьё, 17.09.2026)

> Постановка: `docs/research/queue/GAP_QUEUE.md`, раздел «Г40–Г41», часть Г41 (восемь рамок).
> Вход: `docs/research/raw/math_core_audit_2026-09-17.md`, блок `## ИТОГ Г40` и «Вопросы для Г41».
> Режим: исследование. Канон модели, формулировка новизны, код продукта и `tests/` НЕ правятся.
> Скрипты — `/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/fe25aad2-149b-48bd-a8b2-c62cc04ce4a1/scratchpad/g41/`, код и вывод — дословно ниже.
> Файл дописывается по одной рамке (`cat >>`), чтобы пережить обрыв.
> Подача для владельца: аналогия → суть → что дало бы нашему пользователю на сквозном примере → цена.

**Сквозной пример (один на все рамки).** Человек: зарплата 90 000 ₽/мес, обязательные расходы 55 000 ₽,
кредитная карта 120 000 ₽ под 35 % годовых (минимальный платёж 6 000 ₽), займ МФО 30 000 ₽ под 0,8 % в день
(≈292 % годовых, платёж 9 000 ₽), подушка 20 000 ₽, цель «отпуск» 80 000 ₽ через 8 месяцев.
Свободный поток: 90 000 − 55 000 − 6 000 − 9 000 = **20 000 ₽/мес**.

**Состояние каналов, 17.09.2026 (замер `curl`, коды HTTP):**
Semantic Scholar `graph/v1/paper/search/bulk` — 200; Crossref `api.crossref.org/works/DOI` — 200;
OpenAlex `api.openalex.org/works?search=` — 200; Unpaywall (`email=research@example.org`) — 200;
EuropePMC REST — 200; `r.jina.ai` без браузерного UA — 200; Exa `mcp__exa__web_search_exa` — работает
(выдача по Wierzbicki получена); `pdftotext` — есть (`/usr/local/bin/pdftotext`);
`.venv/bin/python` проекта — есть, numpy 2.4.4, **scipy/highspy/PuLP — НЕТ** (решатель ставится
в отдельный венв скрэтчпада `g41/sv`, не в проект). IIASA Pure (`pure.iiasa.ac.at`) — 200, PDF.

**Процесс, честно.** Классификация запроса — **breadth-first** (восемь независимых рамок, одна таблица
на каждую). Подагентов — 0 на старте: у вахты уже загружены итоги девяти прошлых тем по тем же рамкам
(38 DP, 40 солверы, 13 GBI, 36 поведенческие, 9 бандиты, 18 регуляторика, 14 долги, 34 статистика РФ, Г40),
и подагент начал бы с нуля. Прошлое сырьё не переискивается, а цитируется со ссылкой на файл.
**Порядок записи рамок:** 5 (многоцелевая — главный вопрос Г40, считается числом) → 1 → 2 → 3 → 4 → 6 → 7 → 8 → ИТОГ.

---

## Рамка 5. Многоцелевая оптимизация «по-настоящему»: фронт Парето, ε-ограничения, точка отсчёта, интерактивные методы

### 5.0. Аналогия → суть

**Аналогия.** Взвешенная сумма — это весы с гирьками: поставил гирьку «долг 0,25», «подушка 0,30» — и весы
падают в одну сторону целиком. Точка отсчёта — это навигатор: человек называет, куда хочет приехать
(«отпуск к маю, подушка хотя бы на месяц»), и система ищет ближайший достижимый маршрут без лишних потерь.
ε-ограничение — это «обязательная остановка по пути»: сначала гарантируем отпуск к сроку, а из остатка
выжимаем максимум по долгам.

**Суть (каждый символ расшифрован).**
- *Фронт Парето* — множество планов, у которых нельзя улучшить один критерий, не ухудшив другой.
- *Взвешенная сумма* $U(a)=\sum_i w_i \hat q_i(a)$: $a$ — план, $\hat q_i$ — нормированный $i$-й критерий, $w_i$ — вес.
- *ε-ограничение* (Haimes et al. 1971; Miettinen 1999, гл. 3): максимизировать один критерий при условии,
  что остальные не хуже заданных порогов $q_j(a)\ge\varepsilon_j$.
- *Функция достижения* Вежбицкого (achievement scalarizing function, ASF):
  $s(a)=\min_i \dfrac{q_i(a)-\bar q_i}{\rho_i} + \epsilon\sum_i \dfrac{q_i(a)-\bar q_i}{\rho_i}$,
  где $\bar q_i$ — желаемый уровень (точка отсчёта), $\rho_i$ — размах критерия (идеал минус антиидеал),
  $\epsilon$ — малое число (у нас 0,001), чтобы не выбирать слабо-Парето точки. Выбирается план с максимальным $s$:
  «тянем вверх самый отстающий от желания критерий».
- *Интерактивный метод* (NIMBUS): человек смотрит на текущий план и классифицирует критерии —
  «улучшить», «улучшить до уровня», «оставить», «можно ухудшить до границы», «пусть меняется».

### 5.1. Литература — дословно

1. **Wierzbicki A. P. (1979), «The Use of Reference Objectives in Multiobjective Optimization — Theoretical
   Implications and Practical Experience», IIASA WP-79-066.** `https://pure.iiasa.ac.at/id/eprint/1117/1/WP-79-066.pdf`,
   `curl -skL` HTTP 200, 1 094 933 байт, `pdftotext -layout` → 79 262 байта, 17.09.2026. Дословно (с. 1, реферат):
   > «Any point in the objective space--no matter whether it is attainable or not, ideal or not--can be used instead of
   > weighting coefficients to derive scalarizing functions which have minima at Pareto points only.»

   🔴 И — ровно дефект Г40 «91 % решений — угол симплекса», описанный в 1979 году (стр. PDF ≈ 17–18, строки 1030–1058 текста):
   > «Since the solutions of linear programming problems correspond to vertices of a simplex, some crucial decision
   > variables often tend to take on-off character; exaggerating, the "optimal" solution can be often interpreted as
   > "first invest all GNP for two years and do not consume, then do not invest for three years and consume all GNP."
   > Clearly, such an "optimal" solution would be never accepted by a decision maker […]»
   > «An introduction of other optimization criteria being accounted for by weighting coefficients does not solve the
   > problem; the weighted objective function remains linear and tends again to produce on-off solutions. Therefore, a
   > widely used approach is to introduce additional constraints, limiting the set of admissible solutions. This is in
   > fact equivalent to goal programming: aspiration levels for other criteria are determined and used as constraints
   > […] But this approach has all drawbacks of goal programming: the aspiration levels must be attainable in order not
   > to make the set of feasible solutions empty, and it is difficult therefore to devise interactive procedures […]»
   (В тексте PDF буквы разнесены пробелами — артефакт скана; цитата восстановлена слитно без изменения слов.)

2. **Wierzbicki A. P. (1980), «A Mathematical Basis for Satisficing Decision Making», IIASA WP-80-090.**
   `https://pure.iiasa.ac.at/id/eprint/1379/1/WP-80-090.pdf`, HTTP 200, 1 022 166 байт, `pdftotext` 63 075 байт, 17.09.2026. Дословно:
   > «It is shown that the notions of reference objective levels and achievement scalarizing functions form a
   > mathematical basis not only for satisficing decision making but also for Pareto optimization; this basis is an
   > alternative to or even stronger than the approaches based on weighting coefficients or typical value functions.»
   > «Lemma 2 can be used, for example, for checking the attainability and Pareto optimality of a given q […] This
   > cannot be achieved when using weighting coefficients or typical value or utility functions.»
   Лемма 2 там же (дословно фрагмент): «Observe that Lemma 2 is a necessary condition for D-maximality […] even for
   nonconvex sets» — то есть ASF достаёт и те неулучшаемые точки, которые взвешенная сумма не видит.

3. **Lewandowski A., Grauer M. (1982), «The Reference Point Optimization Approach — Methods of Efficient
   Implementation», IIASA** (`http://pure.iiasa.ac.at/id/eprint/1990`, фрагменты через Exa, 17.09.2026; PDF не открывался):
   > «The reference point approach introduced by Wierzbicki has already been described […] This method is a
   > generalization of the well-known goal programming method and of the method of displaced ideals developed by Zeleny.»
   > «[…] the problem of finding from within the Pareto set the point nearest to the reference point»
   Статус: 🟡 фрагмент выдачи Exa, не полный текст.

4. **Miettinen K. (2005), «IND-NIMBUS for Demanding Interactive Multiobjective Optimization», MCDM 2005 (Katowice).**
   `https://mcdm.ue.katowice.pl/files/papers/mcdm05(1)_9.pdf`, `curl -skL` HTTP 200, 361 126 байт, `pdftotext`, 17.09.2026. Дословно:
   > «The idea of the interactive NIMBUS method is to move around the set of Pareto optimal solutions, where the value of
   > an objective function can only be improved by allowing at least one of the others to impair»
   > «the decision maker is asked to classify the objective functions into up to five classes»
   > «The starting point of the solution process can come from the decision maker or it can be some neutral compromise
   > between the objectives. To get the neutral compromise solution we set z̄i = (zinad + zi*)/2 for all i»
   > «The weighting coefficients 1/(z nad j − z ?? j) have proven to facilitate capturing the preferences of the
   > decision maker well.»
   Первоисточник синхронной версии — Miettinen & Mäkelä, EJOR 170(3), 2006, DOI 10.1016/j.ejor.2004.07.052:
   Semantic Scholar HTTP 200, `openAccessPdf.status: CLOSED`, реферат скрыт издателем — **не открыт**.

5. **Miettinen K. (1999), *Nonlinear Multiobjective Optimization*, гл. 3** (текст ознакомительных страниц уже добыт в Г40,
   `scratchpad/g40/mie_978-1-4615-5563-6_4.txt`, Springer HTTP 200). Дословно:
   > «Basic methods are the weighting method and the €-constraint method. […] The method of weighted metrics […] It is
   > followed by the handling of achievement scalarizing functions.»

6. **Haimes Y. Y., Lasdon L. S., Wismer D. A. (1971), IEEE Trans. SMC-1(3), DOI 10.1109/TSMC.1971.4308298** —
   первоисточник ε-ограничений. Semantic Scholar HTTP 200, 1 370 цитирований, реферат скрыт, `CLOSED`;
   Unpaywall (`email=research@example.org`) HTTP 200, `is_oa: false`, `has_repository_copy: false`. **Текст не открыт**;
   метод опирается на Miettinen (п. 5) как вторичный, но авторитетный источник.

### 5.2. Проверка числом — три скрипта

**(а) Как канон ведёт сквозного человека 8 месяцев** (`f5a.py`; план пересчитывается каждый месяц, состояние — остатки
долгов, подушка, копилка отпуска — переносится; деньги сходятся до рубля: «чистая позиция = 150 000 − проценты»).

| Профиль | Проценты за 8 мес. | Подушка в конце | Отпуск (из 80 000) | Долг в конце |
|---|---|---|---|---|
| 1 (консервативный) | 44 684 ₽ | 122 297 ₽ | **0 ₽** | 16 981 ₽ |
| 2–3 | 37 303 ₽ | 109 950 ₽ | **2 748 ₽** | 0 |
| 4–5 | 37 303 ₽ | 92 901 ₽ | **19 796 ₽** | 0 |

Первые два месяца — «всё в подушку» (лексикографический floor), пока МФО под 292 % начисляет ~7 300 ₽ в месяц;
месяцы 3–6 — «всё в долг»; в месяц 8, за месяц до отпуска, — «всё в подушку». **Отпуск срывается у всех пяти профилей.**

**(б) То же, но оптимально на 8 месяцев вперёд (MILP, HiGHS 1.15.1 через `highspy`, отдельный венв скрэтчпада)** —
это одновременно рамка 1 и **фронт ε-ограничений в рублях**: минимизировать проценты при условии «отпуск ≥ V к месяцу 8»
и «подушка ≥ 1 месяц расходов (55 000 ₽) начиная с месяца k».

| Подушка ≥ 55 000 ₽ начиная с | Отпуск 80 000 ₽ к сроку | Проценты | Цена отпуска в процентах |
|---|---|---|---|
| месяца 2 (как у канона) | ✅ 80 000 | 36 458 ₽ | +1 420 ₽ (против 35 038 без отпуска) |
| месяца 3 | ✅ 80 000 | 26 206 ₽ | +1 129 ₽ (против 25 077) |
| месяца 4 | ✅ 80 000 | 25 055 ₽ | — |
| месяц 1 | невозможно | — | — |

**Что это значит на примере.** При том же требовании к подушке, что и у канона (месяц расходов к концу второго месяца),
оптимальный 8-месячный план платит **почти те же проценты (36 458 против 37 303 ₽)**, но **доводит отпуск до 80 000 ₽ в срок**
вместо 2 748 ₽ — за счёт того, что не раздувает подушку до двух месяцев и не держит отпуск «на потом».
А если человек согласен набрать месячную подушку не за 2, а за 3 месяца, это **экономит 10 252 ₽ процентов** (36 458 → 26 206):
МФО под 292 % закрывается на месяц раньше. Вот такое предложение («подушка на месяц позже — минус 10 тысяч переплаты,
отпуск всё равно успеваем») и есть результат метода ε-ограничений — число в рублях, понятное без формул.

🔴 Честная оговорка: большая часть выигрыша — не «умнее считает», а **другие ограничения**: канон не знает про срок отпуска
(Г40 № 6) и держит floor 2 месяца. Разница в чистых деньгах при одинаковой подушке — 845 ₽, а не 13 800 ₽
(13 800 получаются, только если снять требование к подушке совсем — это уже выбор человека, а не метода).

**(в) Надстройка над уже перебранными 66 точками без правки ядра** (`f5c.py`; критерии в натуральных единицах:
$q_1$ — проценты, которых избегаем за год, ₽; $q_2$ — подушка после плана, месяцев; $q_3$ — обеспеченность цели).

| Что проверено | Результат |
|---|---|
| Сквозной пример, месяц 1 (подушка 20 000 < floor) | 🔴 после лексикографического floor остаётся **1 точка из 66** — выбирать нечего никакому методу: ни фронту, ни ASF, ни ε |
| Тот же человек, подушка 60 000 (floor пройден) | фронт Парето = **все 66 точек** (при линейных критериях каждая доля строго полезна своему критерию) |
| Канон (W), профиль 3 | 100 % в долг |
| ASF, нейтральный компромисс (середина идеал/антиидеал, как старт NIMBUS) | **40 % долг / 40 % подушка / 20 % отпуск** |
| ASF, желание человека (макс. экономия, подушка 1 мес., отпуск по графику) | **60 % долг / 0 / 40 % отпуск** |
| ε: «отпуск ≥ 10 000 ₽/мес», затем макс. экономия | 50 % долг / 0 / 50 % отпуск |
| 🔴 ASF с недостижимым за месяц желанием («цель обеспечена полностью», $\bar q_3=1$) | **всё в цель** — ASF тянет самый отстающий критерий; желание должно быть месячным |
| Популяция 232 портрета (генератор Г40, seed 909): доля «угловых» решений (≥ 90 % в одно) | **W 87,1 %** · ASF-нейтральный **0,0 %** · ASF-желание 38,8 % · ε 62,1 % |
| Та же популяция: все ставки ×4 → меняется ли выбор? | **W 0,0 % · ASF 0,0 % · ε 0,0 %** |

### 5.3. 🔴 Два вывода, которые важнее таблицы

1. **Вырождение в «одну корзину» надстройкой лечится полностью**: ASF с нейтральной точкой отсчёта на тех же 66 точках даёт
   0 % угловых решений против 87 % у взвешенной суммы. Цена — ~40 строк кода поверх `ranked`, ноль изменений в `app/core`.
2. **Нечувствительность к ставке надстройкой НЕ лечится ни одним методом рамки 5.** Причина математическая: все методы
   нормируют критерий его размахом *у этого же человека* ($\rho_i$), а умножение всех ставок на 4 умножает на 4 и $q_1$,
   и его размах — выбор инвариантен. Лечится только **общей денежной шкалой** между направлениями (сколько рублей стоит
   месяц подушки против рубля сэкономленных процентов) — это рамки 3–4, а не 5. И **floor**: пока он лексикографический,
   в самых важных случаях (подушка ниже floor, дорогой долг) выбирать не из чего; ε-ограничение по пути
   («месячная подушка к месяцу k») вместо «всё в подушку, пока не наберётся» — единственное, что это меняет.

### 5.4. Таблица рамки

| Параметр | Оценка |
|---|---|
| **Что умеет лучше нашей** | Достаёт неугловые компромиссы (0 % углов у ASF против 87 %); принимает желания человека в его единицах («отпуск к маю», «месяц подушки»); ε даёт цену компромисса в рублях; проверка «достижимо ли желание» (лемма 2 Вежбицкого) |
| **Чего не умеет** | Не делает критерии сравнимыми в деньгах → ставка по-прежнему не влияет; не видит будущих месяцев (однопериодная); при лексикографическом floor не получает альтернатив; ASF с недостижимым желанием снова вырождается в угол |
| **Данные** | Те же, что сейчас; плюс **желаемые уровни** от человека (срок цели уже есть в данных, подушка — из floor) — у нас есть |
| **Сложность соло** | Фильтр Парето + ASF + ε на готовом `ranked`: **4–8 часов** с тестами, без библиотек. Показ 3–5 представителей на экране — отдельная фронт-задача, 1–2 дня. Интерактивный NIMBUS-диалог — 1–2 недели интерфейса |
| **Объяснимость** | 🟢 высокая: «вы сказали X — ближайший достижимый план Y; чтобы получить X, нужно пожертвовать Z ₽». Выше, чем у весов профиля |
| **Закон (темы 18, 19)** | 🟢 не меняет предмета — по-прежнему собственные деньги и долги, без финансовых инструментов; 🟡 показ нескольких равноправных вариантов снижает риск «навязанной рекомендации» (22-МР, тема 36) |
| **Что взять кусочком** | (1) ASF-выбор поверх `ranked` вместо/рядом с `utility`; (2) ε-правило «цель со сроком получает не меньше нужного в месяц, если это допустимо»; (3) 3–5 представителей фронта на экран сравнения |
| **Какую проблему Г40 закрывает** | № 4/22 (угол симплекса, 85 % недостижимых компромиссов) — **закрывает**; № 6 (срок цели) — ε **закрывает**; № 12 (тождественные $\hat R$, $\hat D$) — ASF по натуральным критериям (один долговой критерий) **закрывает**; № 5 (вес без диапазона) — ASF работает с размахами явно (Miettinen: 1/(z^nad − z*)), **частично**; нечувствительность к ставке — **не закрывает** |

### Скрипты рамки 5 (дословно)

**f5a.py**

```python
"""G41 frame 5 (a) [v2: money-conserving state update]: running example through the canon core, month by month for 8 months, all 5 profiles.
State feedback: debts -> new_amount accrues r/12 and pays new_payment; cushion += reserve; goal += goal money."""
import sys
from datetime import datetime, timedelta
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.services.planning import run_planning
T0 = datetime(2026, 9, 17)
INC, EXP = 90_000, 55_000

def initial():
    obls = [{"id": "cc", "name": "Кредитка", "amount": 120_000.0, "interest_rate": 0.35, "monthly_payment": 6_000.0},
            {"id": "mfo", "name": "МФО", "amount": 30_000.0, "interest_rate": 2.92, "monthly_payment": 9_000.0}]
    return obls, 20_000.0, 0.0

def roll(profile, months=8, verbose=False):
    obls, bliq, vac = initial(); interest = 0.0; log = []
    for m in range(months):
        today = T0 + timedelta(days=30 * m)
        goals = [{"id": "vac", "name": "Отпуск", "target_amount": 80_000, "current_amount": vac,
                  "deadline": T0 + timedelta(days=243), "category": "emotional"}] if vac < 80_000 - 1 else []
        r = run_planning(INC, EXP, obls, goals, bliq=bliq, r_bench=0.14, risk_tolerance=profile, today=today)
        if r["crisis_plan"] is not None:
            log.append((m + 1, "CRISIS")); break
        b = r["best"]
        xd, xr, xg = b["x_obl_effective"], b["x_reserve_effective"], sum(b.get("goal_allocation", {}).values())
        bliq += xr; vac += xg
        new = []
        before = {o["id"]: o for o in obls}
        for o in b["obligation_allocation"]:
            o0 = before[o["id"]]
            rate = o["interest_rate"]
            i = o0["amount"] * rate / 12; interest += i          # interest on start-of-month balance (same timing as MILP)
            amt2 = o["new_amount"] + i - o0["monthly_payment"]     # old payment was deducted from flow this month
            if amt2 <= 0.5:
                bliq += max(0.0, -amt2)                            # overpaid last installment returns to cushion
                continue
            new.append({"id": o["id"], "name": o["name"], "amount": amt2, "interest_rate": rate,
                        "monthly_payment": min(o["new_payment"], amt2 * (1 + rate / 12))})
        log.append((m + 1, round(xd), round(xr), round(xg), b["id"]))
        obls = new
    debt_left = sum(o["amount"] for o in obls)
    return log, round(interest), round(bliq), round(vac), round(debt_left), [o["name"] for o in obls]

if __name__ == "__main__":
    for p in (1, 2, 3, 4, 5):
        log, interest, bliq, vac, debt, alive = roll(p)
        print("profile", p, "| month:(debt,reserve,goal,id):", log)
        print("   after 8 months: interest paid", interest, " cushion", bliq, " vacation fund", vac, "of 80000", " debt left", debt, alive, " net position", bliq + vac - debt, " check 150000-interest =", 150000 - interest)
```

**Вывод f5a.py:**
```
profile 1 | month:(debt,reserve,goal,id): [(1, 0, 20000, 0, 'a0100'), (2, 4000, 16000, 0, 'a280'), (3, 12763, 8509, 0, 'a640'), (4, 7715, 18002, 0, 'a370'), (5, 2903, 26130, 0, 'a190'), (6, 23354, 5838, 0, 'a820'), (7, 27455, 3051, 0, 'a910'), (8, 28896, 3211, 0, 'a910')]
   after 8 months: interest paid 44684  cushion 122297  vacation fund 0 of 80000  debt left 16981 ['Кредитка']  net position 105316  check 150000-interest = 105316
profile 2 | month:(debt,reserve,goal,id): [(1, 0, 20000, 0, 'a0100'), (2, 4000, 16000, 0, 'a280'), (3, 21272, 0, 0, 'a1000'), (4, 29000, 0, 0, 'a1000'), (5, 30550, 0, 0, 'a1000'), (6, 32237, 0, 0, 'a1000'), (7, 14301, 17048, 2748, 'a550'), (8, 0, 35000, 0, 'a0100')]
   after 8 months: interest paid 37303  cushion 109950  vacation fund 2748 of 80000  debt left 0 []  net position 112698  check 150000-interest = 112697
profile 3 | month:(debt,reserve,goal,id): [(1, 0, 20000, 0, 'a0100'), (2, 4000, 16000, 0, 'a280'), (3, 21272, 0, 0, 'a1000'), (4, 29000, 0, 0, 'a1000'), (5, 30550, 0, 0, 'a1000'), (6, 32237, 0, 0, 'a1000'), (7, 14301, 17048, 2748, 'a550'), (8, 0, 35000, 0, 'a0100')]
   after 8 months: interest paid 37303  cushion 109950  vacation fund 2748 of 80000  debt left 0 []  net position 112698  check 150000-interest = 112697
profile 4 | month:(debt,reserve,goal,id): [(1, 0, 20000, 0, 'a0100'), (2, 4000, 16000, 0, 'a280'), (3, 21272, 0, 0, 'a1000'), (4, 29000, 0, 0, 'a1000'), (5, 30550, 0, 0, 'a1000'), (6, 32237, 0, 0, 'a1000'), (7, 14301, 0, 19796, 'a505'), (8, 0, 35000, 0, 'a0100')]
   after 8 months: interest paid 37303  cushion 92901  vacation fund 19796 of 80000  debt left 0 []  net position 112697  check 150000-interest = 112697
profile 5 | month:(debt,reserve,goal,id): [(1, 0, 20000, 0, 'a0100'), (2, 4000, 16000, 0, 'a280'), (3, 21272, 0, 0, 'a1000'), (4, 29000, 0, 0, 'a1000'), (5, 30550, 0, 0, 'a1000'), (6, 32237, 0, 0, 'a1000'), (7, 14301, 0, 19796, 'a505'), (8, 0, 35000, 0, 'a0100')]
   after 8 months: interest paid 37303  cushion 92901  vacation fund 19796 of 80000  debt left 0 []  net position 112697  check 150000-interest = 112697
```

**f5b.py** (запуск: `scratchpad/g41/sv/bin/python`, HiGHS 1.15.1, numpy)

```python
"""G41 frame 5/1 (b): 8-month MILP (HiGHS) for the running example = epsilon-constraint front in RUBLES.
min total interest  s.t. vacation fund >= V by month 8, cushion >= C_end at month 8, monthly budget, min payments."""
import highspy, numpy as np
FLOW = 90_000 - 55_000           # income - mandatory expenses, before debt payments
DEBTS = [("Кредитка", 120_000, 0.35, 6_000), ("МФО", 30_000, 2.92, 9_000)]
T, M = 8, 1e7


def solve(V, C_end, C0=20_000, cushion_path=None, debts=DEBTS, flow=FLOW, horizon=T):
    h = highspy.Highs(); h.setOptionValue("output_flag", False)
    inf = highspy.kHighsInf
    idx = {}

    def var(name, lb=0.0, ub=inf, integer=False, cost=0.0):
        h.addVar(lb, ub); j = h.getNumCol() - 1
        h.changeColCost(j, cost)
        if integer:
            h.changeColIntegrality(j, highspy.HighsVarType.kInteger)
        idx[name] = j; return j
    K = len(debts)
    for k, (_, B0, r, m) in enumerate(debts):
        for t in range(horizon + 1):
            var(("B", k, t), cost=(r / 12 if t < horizon else 0.0))   # interest accrues on balance at start of month t
        for t in range(horizon):
            var(("y", k, t)); var(("z", k, t), 0, 1, True)
    for t in range(horizon):
        var(("s", t)); var(("g", t))
    for t in range(horizon + 1):
        var(("C", t))

    def row(coefs, lo, hi):
        ind = [idx[n] for n, _ in coefs]; val = [c for _, c in coefs]
        h.addRow(lo, hi, len(ind), np.array(ind, dtype=np.int32), np.array(val, dtype=float))
    for k, (_, B0, r, m) in enumerate(debts):
        row([(("B", k, 0), 1)], B0, B0)
        for t in range(horizon):
            g = 1 + r / 12
            row([(("B", k, t + 1), 1), (("B", k, t), -g), (("y", k, t), 1)], 0, 0)       # balance dynamics
            row([(("y", k, t), 1), (("z", k, t), -m)], 0, inf)                            # alive -> pay >= min
            row([(("B", k, t), g), (("z", k, t), -M)], -inf, m)                           # balance*(1+r) > m -> alive
    row([(("C", 0), 1)], C0, C0)
    for t in range(horizon):
        row([(("y", k, t), 1) for k in range(K)] + [(("s", t), 1), (("g", t), 1)], flow, flow)
        row([(("C", t + 1), 1), (("C", t), -1), (("s", t), -1)], 0, 0)
        if cushion_path:
            row([(("C", t + 1), 1)], cushion_path[t], inf)
    row([(("g", t), 1) for t in range(horizon)], V, inf)
    row([(("C", horizon), 1)], C_end, inf)
    h.run()
    if h.getModelStatus() != highspy.HighsModelStatus.kOptimal:
        return None
    x = h.getSolution().col_value
    val = lambda n: x[idx[n]]
    interest = sum(val(("B", k, t)) * debts[k][2] / 12 for k in range(K) for t in range(horizon))
    plan = [(t + 1, round(sum(val(("y", k, t)) for k in range(K))), round(val(("s", t))), round(val(("g", t)))) for t in range(horizon)]
    close = [next((t for t in range(horizon + 1) if val(("B", k, t)) < 1), None) for k in range(K)]
    return (round(interest), plan, round(val(("C", horizon))), round(sum(val(("g", t)) for t in range(horizon))),
            close, round(sum(val(("B", k, horizon)) for k in range(K))))


if __name__ == "__main__":
    print("epsilon-constraint front (8 months): vacation target V, end cushion C -> min interest")
    for C_end in (20_000, 55_000, 110_000):
        for V in (0, 40_000, 80_000):
            r = solve(V, C_end)
            if r is None:
                print(f"V={V:>6} C_end={C_end:>7}: INFEASIBLE"); continue
            interest, plan, C, g, close, debt = r
            print(f"V={V:>6} C_end={C_end:>7}: interest {interest:>6}  cushion {C:>7}  vacation {g:>6}  debt left {debt:>7}  closed at month-start index (cc,mfo)={close}")
    print("detail V=80000, C_end=55000 (month, total debt payment incl. minimums, reserve, goal):")
    print(solve(80_000, 55_000)[1])
    print("detail V=80000, C_end=55000, cushion path >=20000 m1-2, >=40000 m3-7, >=55000 m8:")
    r = solve(80_000, 55_000, cushion_path=[20_000, 20_000, 40_000, 40_000, 40_000, 40_000, 40_000, 55_000]); print(r[0], r[1], r[4], r[5])


if __name__ == "__main__":
    print("extra: cushion >= 1 month of expenses (55000) from month k onward, vacation 80000 by month 8")
    for k in (1, 2, 3, 4):
        path = [20_000] * (k - 1) + [55_000] * (T - k + 1)
        r = solve(80_000, 55_000, cushion_path=path)
        print(f"  from month {k}:", "INFEASIBLE" if r is None else f"interest {r[0]}  plan {r[1]}  close {r[4]}  debt left {r[5]}  vacation {r[3]}")
    print("extra: same cushion rule, vacation dropped (V=0) -> price of the vacation in interest")
    for k in (2, 3):
        path = [20_000] * (k - 1) + [55_000] * (T - k + 1)
        r = solve(0, 55_000, cushion_path=path)
        print(f"  from month {k}: interest {r[0]}  debt left {r[5]}")
```

**Вывод f5b.py:**
```
epsilon-constraint front (8 months): vacation target V, end cushion C -> min interest
V=     0 C_end=  20000: interest  21824  cushion   58176  vacation  70000  debt left       0  closed at month-start index (cc,mfo)=[5, 2]
V= 40000 C_end=  20000: interest  21824  cushion   20000  vacation 108176  debt left       0  closed at month-start index (cc,mfo)=[5, 2]
V= 80000 C_end=  20000: interest  21824  cushion   20000  vacation 108176  debt left       0  closed at month-start index (cc,mfo)=[5, 2]
V=     0 C_end=  55000: interest  21824  cushion   55000  vacation  73176  debt left       0  closed at month-start index (cc,mfo)=[5, 2]
V= 40000 C_end=  55000: interest  21824  cushion   55000  vacation  73176  debt left       0  closed at month-start index (cc,mfo)=[5, 2]
V= 80000 C_end=  55000: interest  23530  cushion   55000  vacation  80000  debt left    8530  closed at month-start index (cc,mfo)=[None, 2]
V=     0 C_end= 110000: interest  21824  cushion  110000  vacation  18176  debt left       0  closed at month-start index (cc,mfo)=[5, 2]
V= 40000 C_end= 110000: interest  25326  cushion  110000  vacation  40000  debt left   25326  closed at month-start index (cc,mfo)=[None, 2]
V= 80000 C_end= 110000: interest  31019  cushion  110000  vacation  80000  debt left   71019  closed at month-start index (cc,mfo)=[None, 2]
detail V=80000, C_end=55000 (month, total debt payment incl. minimums, reserve, goal):
[(1, 35000, 0, 0), (2, 35000, 0, 0), (3, 35000, 0, 0), (4, 35000, 0, 0), (5, 7000, 6000, 22000), (6, 6000, 0, 29000), (7, 6000, 29000, 0), (8, 6000, 0, 29000)]
detail V=80000, C_end=55000, cushion path >=20000 m1-2, >=40000 m3-7, >=55000 m8:
24820 [(1, 35000, 0, 0), (2, 35000, 0, 0), (3, 15000, 20000, 0), (4, 35000, 0, 0), (5, 27000, 8000, 0), (6, 6000, 0, 29000), (7, 6000, 0, 29000), (8, 6000, 7000, 22000)] [None, 2] 9820
extra: cushion >= 1 month of expenses (55000) from month k onward, vacation 80000 by month 8
  from month 1: INFEASIBLE
  from month 2: interest 36458  plan [(1, 20000, 15000, 0), (2, 15000, 20000, 0), (3, 35000, 0, 0), (4, 35000, 0, 0), (5, 35000, 0, 0), (6, 13000, 0, 22000), (7, 6000, 0, 29000), (8, 6000, 0, 29000)]  close [None, 3]  debt left 21458  vacation 80000
  from month 3: interest 26206  plan [(1, 35000, 0, 0), (2, 29000, 6000, 0), (3, 6000, 29000, 0), (4, 35000, 0, 0), (5, 35000, 0, 0), (6, 13000, 0, 22000), (7, 6000, 0, 29000), (8, 6000, 0, 29000)]  close [None, 2]  debt left 11206  vacation 80000
  from month 4: interest 25055  plan [(1, 35000, 0, 0), (2, 35000, 0, 0), (3, 29000, 6000, 0), (4, 6000, 29000, 0), (5, 35000, 0, 0), (6, 13000, 0, 22000), (7, 6000, 0, 29000), (8, 6000, 0, 29000)]  close [None, 2]  debt left 10055  vacation 80000
extra: same cushion rule, vacation dropped (V=0) -> price of the vacation in interest
  from month 2: interest 35038  debt left 0
  from month 3: interest 25077  debt left 0
```

**f5c.py**

```python
"""G41 frame 5 (c): a posteriori MOO on top of the canon's already enumerated grid (no core change).
For every ranked alternative take criteria in natural units:
  q1 = annual interest avoided by this month's prepayment, RUB/yr  (sum paid_in_k * r_k)
  q2 = cushion after plan, months of expenses (Lt_new)
  q3 = goal provision Si (canon criterion, 0..1)
Methods compared on the floor-optimal level (canon lexicographic step kept):
  W  = canon weighted sum (r["best"])
  PF = Pareto filter size, and 'knee' = 3-5 representatives
  ASF= Wierzbicki achievement scalarizing function, reference point = user aspiration
       s(q) = min_i (q_i - ref_i)/range_i + rho * sum_i (q_i - ref_i)/range_i, rho = 1e-3 (augmented)
  EPS= epsilon-constraint: goal on schedule (goal money >= needed/month, if feasible), then max q1, tie -> max q2
Corner = one of the three directions gets >= 90 % of free flow."""
import sys, random
from datetime import datetime, timedelta
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.services.planning import run_planning
TODAY = datetime(2026, 9, 17)
RHO = 1e-3


def q_of(a):
    q1 = sum(p["paid_in"] * p["interest_rate"] for p in a["avalanche_detail"]["passed"])
    return (q1, a["Lt_new"], a["Si"])


def shares(a):
    d, r, g = a["x_obl_effective"], a["x_reserve_effective"], sum(a.get("goal_allocation", {}).values())
    s = d + r + g
    return (d / s, r / s, g / s) if s > 0 else (0, 0, 0)


def corner(a):
    return max(shares(a)) >= 0.9 - 1e-9


def dominates(u, v):
    return all(x >= y - 1e-9 for x, y in zip(u, v)) and any(x > y + 1e-9 for x, y in zip(u, v))


def pareto(A):
    Q = [(q_of(a), a) for a in A]
    return [a for q, a in Q if not any(dominates(q2, q) for q2, _ in Q)]


def asf_pick(P, ref):
    Q = [q_of(a) for a in P]
    rng = [max(1e-9, max(q[i] for q in Q) - min(q[i] for q in Q)) for i in range(3)]
    def s(q):
        z = [(q[i] - ref[i]) / rng[i] for i in range(3)]
        return min(z) + RHO * sum(z)
    return max(P, key=lambda a: s(q_of(a)))


def eps_pick(P, need_goal_money):
    ok = [a for a in P if sum(a.get("goal_allocation", {}).values()) >= need_goal_money - 1]
    pool = ok or P
    return max(pool, key=lambda a: (q_of(a)[0], q_of(a)[1]))


def top_floor(r):
    tf = max(a["floor_level"] for a in r["ranked"])
    return [a for a in r["ranked"] if a["floor_level"] >= tf - 1e-9]


def describe(a):
    d, r, g = shares(a)
    q = q_of(a)
    return f"{a['id']:>6} debt/res/goal={d:.0%}/{r:.0%}/{g:.0%}  interest avoided {q[0]:>8.0f} RUB/yr  cushion {q[1]:.2f} mo  Si {q[2]:.2f}"


def example(rate_cc, rate_mfo, bliq, profile=3, label=""):
    obls = [{"id": "cc", "name": "Кредитка", "amount": 120_000, "interest_rate": rate_cc, "monthly_payment": 6_000},
            {"id": "mfo", "name": "МФО", "amount": 30_000, "interest_rate": rate_mfo, "monthly_payment": 9_000}]
    goals = [{"id": "vac", "name": "Отпуск", "target_amount": 80_000, "current_amount": 0, "deadline": TODAY + timedelta(days=243), "category": "emotional"}]
    r = run_planning(90_000, 55_000, obls, goals, bliq=bliq, r_bench=0.14, risk_tolerance=profile, today=TODAY)
    A = top_floor(r); P = pareto(A)
    print(f"--- {label} cc {rate_cc:.0%} mfo {rate_mfo:.0%} cushion {bliq} profile {profile}: floor-level alternatives {len(A)}, Pareto {len(P)}")
    print("  W   (canon) :", describe(r["best"]))
    ref = (max(q_of(a)[0] for a in P), 1.0, 1.0)   # aspiration: max interest avoided, 1 month cushion, goal fully on track
    print("  ASF ref=(max q1, 1 mo, Si 1):", describe(asf_pick(P, ref)))
    ref2 = (0.0, 1.0, 1.0)
    print("  ASF ref=(0, 1 mo, Si 1)     :", describe(asf_pick(P, ref2)))
    print("  EPS goal>=10000/mo, max q1  :", describe(eps_pick(P, 10_000)))
    am, au = asf_variants(P, 10_000)
    print("  ASF ref=midpoint ideal/nadir (goal as on-track ratio):", describe(am))
    print("  ASF ref=(max q1, 1 mo, on-track 1)                  :", describe(au))
    Ps = sorted(P, key=lambda a: shares(a)[0])
    reps = [Ps[0], Ps[len(Ps) // 4], Ps[len(Ps) // 2], Ps[3 * len(Ps) // 4], Ps[-1]] if len(Ps) >= 5 else Ps
    print("  3-5 Pareto representatives (by debt share):")
    for a in {x["id"]: x for x in reps}.values():
        print("     ", describe(a))


def portrait(rng):
    inc = rng.choice([60_000, 100_000, 180_000]); exp = inc * rng.uniform(0.3, 0.65)
    obls = []
    for k in range(rng.randint(1, 3)):
        amt = rng.uniform(2e4, 1.2e6); rate = rng.choice([0.16, 0.22, 0.35, 0.6]); n = rng.choice([12, 36, 120, 300]); rm = rate / 12
        obls.append({"id": f"o{k}", "name": "l", "amount": amt, "interest_rate": rate, "monthly_payment": amt * rm / (1 - (1 + rm) ** -n)})
    goals = [{"id": f"g{s}", "name": "g", "target_amount": rng.uniform(3e4, 2e6), "current_amount": 0,
              "deadline": TODAY + timedelta(days=rng.randint(90, 3000)), "category": rng.choice(["income_growth", "safety", "material", "emotional"])} for s in range(rng.randint(1, 2))]
    return inc, exp, obls, goals, exp * rng.choice([2.2, 3.5, 6, 9]), rng.randint(1, 5)


def population(n=400, seed=909):
    rng = random.Random(seed)
    tot = cW = cA = cE = 0; psize = []; rate_sens = {"W": 0, "ASF": 0, "EPS": 0}; rs_n = 0
    for _ in range(n):
        inc, exp, obls, goals, bliq, p = portrait(rng)
        r = run_planning(inc, exp, obls, goals, bliq=bliq, r_bench=0.14, risk_tolerance=p, today=TODAY)
        if r["crisis_plan"] is not None or not r["ranked"]:
            continue
        A = top_floor(r); P = pareto(A)
        if len(P) < 2:
            continue
        tot += 1; psize.append(len(P))
        ref = (max(q_of(a)[0] for a in P), 1.0, 1.0)
        need = 0.0
        for gl in goals:
            months = max(1, (gl["deadline"] - TODAY).days / 30)
            need += gl["target_amount"] / months
        aW, aA, aE = r["best"], asf_pick(P, ref), eps_pick(P, need)
        cW += corner(aW); cA += corner(aA); cE += corner(aE)
        # rate sensitivity: multiply every rate by 4 (0.16 -> 0.64 etc), rebuild payments with same term proxy
        obls4 = [dict(o, interest_rate=o["interest_rate"] * 4) for o in obls]
        r4 = run_planning(inc, exp, obls4, goals, bliq=bliq, r_bench=0.14, risk_tolerance=p, today=TODAY)
        if r4["crisis_plan"] is None and r4["ranked"]:
            rs_n += 1
            A4 = top_floor(r4); P4 = pareto(A4)
            ref4 = (max(q_of(a)[0] for a in P4), 1.0, 1.0)
            rate_sens["W"] += r4["best"]["id"] != aW["id"]
            rate_sens["ASF"] += asf_pick(P4, ref4)["id"] != aA["id"]
            rate_sens["EPS"] += eps_pick(P4, need)["id"] != aE["id"]
    psize.sort()
    print(f"POPULATION (seed {seed}): portraits with >=2 Pareto points {tot}; Pareto size p50 {psize[len(psize)//2]} p90 {psize[int(.9*(len(psize)-1))]}")
    print(f"  corner solutions (>=90% of flow in one direction): W {cW/tot:.1%}  ASF {cA/tot:.1%}  EPS {cE/tot:.1%}")
    print(f"  choice changes when all rates x4 (n={rs_n}): W {rate_sens['W']/rs_n:.1%}  ASF {rate_sens['ASF']/rs_n:.1%}  EPS {rate_sens['EPS']/rs_n:.1%}")


def q_track(a, need):
    """criteria with goal expressed as on-track ratio: goal money this month / money needed per month to hit deadline (capped at 1)."""
    q1, q2, _ = q_of(a)
    g = sum(a.get("goal_allocation", {}).values())
    return (q1, q2, min(1.0, g / need) if need > 0 else 1.0)


def asf_generic(P, qf, ref, scale):
    def s(q):
        z = [(q[i] - ref[i]) / scale[i] for i in range(3)]
        return min(z) + RHO * sum(z)
    return max(P, key=lambda a: s(qf(a)))


def asf_variants(P, need):
    qf = lambda a: q_track(a, need)
    Q = [qf(a) for a in P]
    ideal = [max(q[i] for q in Q) for i in range(3)]; nadir = [min(q[i] for q in Q) for i in range(3)]
    scale = [max(1e-9, ideal[i] - nadir[i]) for i in range(3)]
    mid = [(ideal[i] + nadir[i]) / 2 for i in range(3)]
    user = [ideal[0], 1.0, 1.0]   # aspiration: as much interest avoided as possible, 1 month cushion, goal on track
    return asf_generic(P, qf, mid, scale), asf_generic(P, qf, user, scale)


def population2(n=400, seed=909):
    rng = random.Random(seed)
    tot = 0; c = {"W": 0, "ASFmid": 0, "ASFuser": 0}; ch = {"W": 0, "ASFmid": 0, "ASFuser": 0}; rs_n = 0
    for _ in range(n):
        inc, exp, obls, goals, bliq, p = portrait(rng)
        r = run_planning(inc, exp, obls, goals, bliq=bliq, r_bench=0.14, risk_tolerance=p, today=TODAY)
        if r["crisis_plan"] is not None or not r["ranked"]:
            continue
        P = pareto(top_floor(r))
        if len(P) < 2:
            continue
        need = sum(gl["target_amount"] / max(1, (gl["deadline"] - TODAY).days / 30) for gl in goals)
        tot += 1
        am, au = asf_variants(P, need)
        c["W"] += corner(r["best"]); c["ASFmid"] += corner(am); c["ASFuser"] += corner(au)
        obls4 = [dict(o, interest_rate=o["interest_rate"] * 4) for o in obls]
        r4 = run_planning(inc, exp, obls4, goals, bliq=bliq, r_bench=0.14, risk_tolerance=p, today=TODAY)
        if r4["crisis_plan"] is None and r4["ranked"]:
            rs_n += 1
            am4, au4 = asf_variants(pareto(top_floor(r4)), need)
            ch["W"] += r4["best"]["id"] != r["best"]["id"]; ch["ASFmid"] += am4["id"] != am["id"]; ch["ASFuser"] += au4["id"] != au["id"]
    print(f"POPULATION-2 (seed {seed}, goal as on-track ratio): portraits {tot}")
    print("  corner share:", {k: f"{v/tot:.1%}" for k, v in c.items()})
    print(f"  choice changes when all rates x4 (n={rs_n}):", {k: f"{v/rs_n:.1%}" for k, v in ch.items()})


if __name__ == "__main__":
    example(0.35, 2.92, 20_000, label="running example, month 1")
    example(0.35, 2.92, 60_000, label="same person, cushion above floor")
    example(0.15, 0.90, 60_000, label="rates lower")
    for p in (1, 5):
        example(0.35, 2.92, 60_000, profile=p, label="profile sweep")
    population()
    population2()
```

**Вывод f5c.py:**
```
--- running example, month 1 cc 35% mfo 292% cushion 20000 profile 3: floor-level alternatives 1, Pareto 1
  W   (canon) :  a0100 debt/res/goal=0%/100%/0%  interest avoided        0 RUB/yr  cushion 0.73 mo  Si 0.00
  ASF ref=(max q1, 1 mo, Si 1):  a0100 debt/res/goal=0%/100%/0%  interest avoided        0 RUB/yr  cushion 0.73 mo  Si 0.00
  ASF ref=(0, 1 mo, Si 1)     :  a0100 debt/res/goal=0%/100%/0%  interest avoided        0 RUB/yr  cushion 0.73 mo  Si 0.00
  EPS goal>=10000/mo, max q1  :  a0100 debt/res/goal=0%/100%/0%  interest avoided        0 RUB/yr  cushion 0.73 mo  Si 0.00
  ASF ref=midpoint ideal/nadir (goal as on-track ratio):  a0100 debt/res/goal=0%/100%/0%  interest avoided        0 RUB/yr  cushion 0.73 mo  Si 0.00
  ASF ref=(max q1, 1 mo, on-track 1)                  :  a0100 debt/res/goal=0%/100%/0%  interest avoided        0 RUB/yr  cushion 0.73 mo  Si 0.00
  3-5 Pareto representatives (by debt share):
       a0100 debt/res/goal=0%/100%/0%  interest avoided        0 RUB/yr  cushion 0.73 mo  Si 0.00
--- same person, cushion above floor cc 35% mfo 292% cushion 60000 profile 3: floor-level alternatives 66, Pareto 66
  W   (canon) :  a1000 debt/res/goal=100%/0%/0%  interest avoided    58400 RUB/yr  cushion 1.09 mo  Si 0.00
  ASF ref=(max q1, 1 mo, Si 1):  a0010 debt/res/goal=0%/0%/100%  interest avoided        0 RUB/yr  cushion 1.09 mo  Si 0.25
  ASF ref=(0, 1 mo, Si 1)     :  a0010 debt/res/goal=0%/0%/100%  interest avoided        0 RUB/yr  cushion 1.09 mo  Si 0.25
  EPS goal>=10000/mo, max q1  :   a505 debt/res/goal=50%/0%/50%  interest avoided    29200 RUB/yr  cushion 1.09 mo  Si 0.12
  ASF ref=midpoint ideal/nadir (goal as on-track ratio):   a442 debt/res/goal=40%/40%/20%  interest avoided    23360 RUB/yr  cushion 1.24 mo  Si 0.05
  ASF ref=(max q1, 1 mo, on-track 1)                  :   a604 debt/res/goal=60%/0%/40%  interest avoided    35040 RUB/yr  cushion 1.09 mo  Si 0.10
  3-5 Pareto representatives (by debt share):
       a0100 debt/res/goal=0%/100%/0%  interest avoided        0 RUB/yr  cushion 1.45 mo  Si 0.00
        a145 debt/res/goal=10%/40%/50%  interest avoided     5840 RUB/yr  cushion 1.24 mo  Si 0.12
        a343 debt/res/goal=30%/40%/30%  interest avoided    17520 RUB/yr  cushion 1.24 mo  Si 0.07
        a514 debt/res/goal=50%/10%/40%  interest avoided    29200 RUB/yr  cushion 1.13 mo  Si 0.10
       a1000 debt/res/goal=100%/0%/0%  interest avoided    58400 RUB/yr  cushion 1.09 mo  Si 0.00
--- rates lower cc 15% mfo 90% cushion 60000 profile 3: floor-level alternatives 66, Pareto 66
  W   (canon) :  a1000 debt/res/goal=100%/0%/0%  interest avoided    18000 RUB/yr  cushion 1.09 mo  Si 0.00
  ASF ref=(max q1, 1 mo, Si 1):  a0010 debt/res/goal=0%/0%/100%  interest avoided        0 RUB/yr  cushion 1.09 mo  Si 0.25
  ASF ref=(0, 1 mo, Si 1)     :  a0010 debt/res/goal=0%/0%/100%  interest avoided        0 RUB/yr  cushion 1.09 mo  Si 0.25
  EPS goal>=10000/mo, max q1  :   a505 debt/res/goal=50%/0%/50%  interest avoided     9000 RUB/yr  cushion 1.09 mo  Si 0.12
  ASF ref=midpoint ideal/nadir (goal as on-track ratio):   a442 debt/res/goal=40%/40%/20%  interest avoided     7200 RUB/yr  cushion 1.24 mo  Si 0.05
  ASF ref=(max q1, 1 mo, on-track 1)                  :   a604 debt/res/goal=60%/0%/40%  interest avoided    10800 RUB/yr  cushion 1.09 mo  Si 0.10
  3-5 Pareto representatives (by debt share):
       a0100 debt/res/goal=0%/100%/0%  interest avoided        0 RUB/yr  cushion 1.45 mo  Si 0.00
        a145 debt/res/goal=10%/40%/50%  interest avoided     1800 RUB/yr  cushion 1.24 mo  Si 0.12
        a343 debt/res/goal=30%/40%/30%  interest avoided     5400 RUB/yr  cushion 1.24 mo  Si 0.07
        a514 debt/res/goal=50%/10%/40%  interest avoided     9000 RUB/yr  cushion 1.13 mo  Si 0.10
       a1000 debt/res/goal=100%/0%/0%  interest avoided    18000 RUB/yr  cushion 1.09 mo  Si 0.00
--- profile sweep cc 35% mfo 292% cushion 60000 profile 1: floor-level alternatives 66, Pareto 66
  W   (canon) :   a190 debt/res/goal=10%/90%/0%  interest avoided     5840 RUB/yr  cushion 1.42 mo  Si 0.00
  ASF ref=(max q1, 1 mo, Si 1):  a0010 debt/res/goal=0%/0%/100%  interest avoided        0 RUB/yr  cushion 1.09 mo  Si 0.25
  ASF ref=(0, 1 mo, Si 1)     :  a0010 debt/res/goal=0%/0%/100%  interest avoided        0 RUB/yr  cushion 1.09 mo  Si 0.25
  EPS goal>=10000/mo, max q1  :   a505 debt/res/goal=50%/0%/50%  interest avoided    29200 RUB/yr  cushion 1.09 mo  Si 0.12
  ASF ref=midpoint ideal/nadir (goal as on-track ratio):   a442 debt/res/goal=40%/40%/20%  interest avoided    23360 RUB/yr  cushion 1.24 mo  Si 0.05
  ASF ref=(max q1, 1 mo, on-track 1)                  :   a604 debt/res/goal=60%/0%/40%  interest avoided    35040 RUB/yr  cushion 1.09 mo  Si 0.10
  3-5 Pareto representatives (by debt share):
       a0100 debt/res/goal=0%/100%/0%  interest avoided        0 RUB/yr  cushion 1.45 mo  Si 0.00
        a145 debt/res/goal=10%/40%/50%  interest avoided     5840 RUB/yr  cushion 1.24 mo  Si 0.12
        a343 debt/res/goal=30%/40%/30%  interest avoided    17520 RUB/yr  cushion 1.24 mo  Si 0.07
        a514 debt/res/goal=50%/10%/40%  interest avoided    29200 RUB/yr  cushion 1.13 mo  Si 0.10
       a1000 debt/res/goal=100%/0%/0%  interest avoided    58400 RUB/yr  cushion 1.09 mo  Si 0.00
--- profile sweep cc 35% mfo 292% cushion 60000 profile 5: floor-level alternatives 66, Pareto 66
  W   (canon) :  a1000 debt/res/goal=100%/0%/0%  interest avoided    58400 RUB/yr  cushion 1.09 mo  Si 0.00
  ASF ref=(max q1, 1 mo, Si 1):  a0010 debt/res/goal=0%/0%/100%  interest avoided        0 RUB/yr  cushion 1.09 mo  Si 0.25
  ASF ref=(0, 1 mo, Si 1)     :  a0010 debt/res/goal=0%/0%/100%  interest avoided        0 RUB/yr  cushion 1.09 mo  Si 0.25
  EPS goal>=10000/mo, max q1  :   a505 debt/res/goal=50%/0%/50%  interest avoided    29200 RUB/yr  cushion 1.09 mo  Si 0.12
  ASF ref=midpoint ideal/nadir (goal as on-track ratio):   a442 debt/res/goal=40%/40%/20%  interest avoided    23360 RUB/yr  cushion 1.24 mo  Si 0.05
  ASF ref=(max q1, 1 mo, on-track 1)                  :   a604 debt/res/goal=60%/0%/40%  interest avoided    35040 RUB/yr  cushion 1.09 mo  Si 0.10
  3-5 Pareto representatives (by debt share):
       a0010 debt/res/goal=0%/0%/100%  interest avoided        0 RUB/yr  cushion 1.09 mo  Si 0.25
        a154 debt/res/goal=10%/50%/40%  interest avoided     5840 RUB/yr  cushion 1.27 mo  Si 0.10
        a334 debt/res/goal=30%/30%/40%  interest avoided    17520 RUB/yr  cushion 1.20 mo  Si 0.10
        a541 debt/res/goal=50%/40%/10%  interest avoided    29200 RUB/yr  cushion 1.24 mo  Si 0.03
       a1000 debt/res/goal=100%/0%/0%  interest avoided    58400 RUB/yr  cushion 1.09 mo  Si 0.00
POPULATION (seed 909): portraits with >=2 Pareto points 232; Pareto size p50 66 p90 66
  corner solutions (>=90% of flow in one direction): W 87.1%  ASF 98.7%  EPS 62.1%
  choice changes when all rates x4 (n=232): W 0.0%  ASF 0.0%  EPS 0.0%
POPULATION-2 (seed 909, goal as on-track ratio): portraits 232
  corner share: {'W': '87.1%', 'ASFmid': '0.0%', 'ASFuser': '38.8%'}
  choice changes when all rates x4 (n=232): {'W': '0.0%', 'ASFmid': '0.0%', 'ASFuser': '0.0%'}
```

---

## Рамка 1. Математическое программирование: MILP, стохастическое программирование, робастная оптимизация

> База, которую не переискиваем: тема 40 (`raw/optimization_solvers_2026-09-10.md`) — постановка как MILP возможна;
> HiGHS решает 60/60 инстансов, медиана 224 мс; Rios-Solis et al. 2017 (PLoS ONE, CC BY) — Avalanche не оптимален,
> задача NP-трудна; цена робастности — Bertsimas & Thiele 2006; Gurobi/CPLEX для РФ закрыты, HiGHS — MIT.
> Здесь — только то, чего там нет: **многомесячная постановка на сквозном примере, VSS и робастный вариант числом**.

### 1.0. Аналогия → суть

**Аналогия.** Наш перебор — это выбор лучшего хода в шахматах **на один ход вперёд** из 66 заготовленных.
MILP — это расчёт **всей партии на 8 ходов** при известных ходах соперника. Стохастическое программирование — расчёт
партии, когда соперник ходит случайно (с вероятностью 10 % человек потеряет работу на два месяца), и первый ход
должен быть хорош во всех ветках. Робастная оптимизация — готовимся к худшему ходу соперника, какова бы ни была вероятность.

**Суть.**
- *MILP* (mixed-integer linear programming): минимизировать линейную функцию (у нас — сумму процентов за 8 месяцев)
  при линейных ограничениях; часть переменных — 0/1 (у нас $z_{k,t}$ = «долг $k$ ещё жив в месяце $t$, значит минимальный
  платёж обязателен»).
- *Двухэтапная стохастическая программа*: решения месяцев 1–2 ($x$) общие для всех сценариев $\omega$; решения месяцев 3–8
  ($y_\omega$) свои в каждом; минимизируется **ожидание** $\sum_\omega p_\omega\,\text{проценты}(x, y_\omega)$.
- *VSS* (value of the stochastic solution, Birge 1982): насколько хуже в ожидании первый ход, выбранный по **средним**
  прогнозам, чем первый ход стохастической программы. $VSS = EEV - RP$, где $RP$ — ожидание при стохастическом решении,
  $EEV$ — ожидание при первом ходе из детерминированной задачи «на средних».
- *Робастная*: первый ход выбирается против худшего сценария.

### 1.1. Литература — дословно

1. **Birge J. R. (1982), «The value of the stochastic solution in stochastic linear programs with fixed recourse»,
   *Mathematical Programming* 24, 314–325, DOI 10.1007/BF01585113** — реквизиты по Crossref (HTTP 200, 17.09.2026);
   текст не открывался (Springer, закрыт). Используется только как источник термина VSS.
2. **Rasmussen K. M., Madsen C. A., Poulsen R. (2014), «Can Household Benefit from Stochastic Programming Models?»,
   *Computational Management Science*, DOI 10.1007/s10287-013-0170-x.** Карточка DTU Orbit
   `https://orbit.dtu.dk/en/publications/can-household-benefit-from-stochastic-programming-models/`, `curl` HTTP 200,
   47 392 байта, 17.09.2026. Реферат дословно:
   > «most Danish mortgage banks advise private home-owners based on simple, if sensible, rules of thumb. […] This paper
   > gives an empirical comparison of performance over the period 2000–2010 of the rules of thumb to the model-based
   > strategies. While the rules of thumb slightly outperform a passive benchmark on average and are less risky than pure
   > adjustable rate loans, we find considerable gains from using the model-based strategies. Using a strategy that
   > minimizes conditional-value-at-risk lowers average effective yearly interest rate over a 10-year horizon by 0.3–0.9
   > %-points (depending on the borrower's level of conservatism) compared to the rules of thumb without increasing the
   > risk. The answer to the question in the title is thus affirmative.»
   Статус 🟡: реферат; объект — выбор ипотечных облигаций в Дании (не наш), но это **единственная найденная эмпирическая
   сверка «стохастическая программа против правил банка» на домохозяйствах**.
3. **Pedersen A. M. B., Weissensteiner A., Poulsen R. (2013), «Financial planning for young households», *Annals of
   Operations Research* 205, 55–76, DOI 10.1007/s10479-012-1205-3.** RePEc
   `https://ideas.repec.org/a/spr/annopr/v205y2013i1p55-7610.1007-s10479-012-1205-3.html`, HTTP 200, 64 185 байт. Реферат:
   > «The problems are solved using a multi-stage stochastic programming model where the uncertainty is described by a
   > scenario tree […] We find strong evidence of the importance of taking into account the multi-stage nature of the
   > problem, as well as the need to consider the asset and liability sides jointly.»
4. **Moriggia V., Consigli G., Iaquinta G., «Optimal Stochastic Programming-Based Personal Financial Planning with
   Intermediate and Long-Term Goals»** (World Scientific, глава; RePEc `wsi/wschap/9789814407519_0003`, фрагмент через Exa,
   текст не открывался): «Inflation-adjusted living costs and investment or consumption targets over the planning horizon
   lead to the definition of a comprehensive decision support tool». 🟡 только аннотация.
5. **Rios-Solis et al. 2017** — дословные цитаты уже в `raw/optimization_solvers_2026-09-10.md`, раздел Г30.1-20;
   важная для нас деталь оттуда же (тема 38): выигрыш MILP над Avalanche **берётся в том числе из умышленной просрочки**.

### 1.2. Проверка числом

**(а) Детерминированный 8-месячный MILP** — см. рамку 5, `f5b.py`: при той же подушке (месяц расходов к концу месяца 2)
проценты 36 458 ₽ против 37 303 ₽ у канона, **отпуск 80 000 ₽ в срок против 2 748 ₽**; подушка к месяцу 3 вместо 2 —
**−10 252 ₽** процентов. Время решения — доли секунды (HiGHS 1.15.1).

**(б) Стохастический и робастный варианты** (`f1a.py`): месяцы 1–2 решаются сейчас; с вероятностью 10 % в месяцах 3–4
дохода нет (поток до платежей −55 000 ₽/мес.), с 90 % — всё как обычно; отпуск обязателен только в благополучной ветке.

| Модель нехватки денег | Первый ход стохастической программы (RP) | Ожидаемые проценты RP | VSS | Первый ход канона → потеря в ожидании |
|---|---|---|---|---|
| Экстренный займ по ставке МФО (292 %) | м.1: закрыть МФО целиком (43 300 ₽, в т.ч. 8 300 ₽ **из подушки**); м.2: 29 000 ₽ в подушку | 28 000 ₽ | **5 750 ₽** | «всё в подушку» → **+15 361 ₽** |
| Кредита нет; просрочка 20 %/год (кэп неустойки 353-ФЗ) и вред 0 ₽ | 🔴 модель **сама уходит в просрочку** даже в благополучной ветке (пик 105 800 ₽) | 15 552 ₽ | 0 | +16 716 ₽ |
| То же, вред 0,25 ₽ на рубль пиковой просрочки | м.1: всё в долги + 20 000 ₽ из подушки | 21 764 ₽ | 0 | +14 204 ₽ |
| То же, вред 1 ₽ на рубль | как в первой строке | 28 733 ₽ | 2 258 ₽ | +13 992 ₽ |
| Робастный (шок наверняка), 292 % и вред 1 ₽ | тот же первый ход, что RP | = RP | — | цена робастности **0 ₽** |

**Что это значит на примере.** Во всех моделях, где деньгами оценён ущерб от нехватки, лучший первый ход один и тот же:
**«в первый месяц убить МФО, даже взяв часть подушки; во второй — пополнить подушку»**. Канон делает обратное — два месяца
«всё в подушку», пока МФО под 292 % начисляет проценты, — и в ожидании переплачивает **14–17 тыс. ₽ за 8 месяцев**
(это ~15–19 % месячного дохода). Робастный первый ход здесь совпал со стохастическим — «цена осторожности» нулевая,
потому что закрытие МФО снижает и обязательные платежи на случай шока (9 000 ₽/мес.).

🔴 **Опасная сторона, пойманная числом.** Модель, которая считает только деньги, при дешёвой неустойке **рекомендует
не платить** (строка 2) — ровно механизм, которым Rios-Solis получает свои 4 % (тема 38). Значит, если когда-нибудь брать
оптимизацию во времени, **запрет просрочки и floor должны быть ограничениями, а не слагаемыми цены** — как у нас сейчас.
И ещё: стохастическая программа «тратит подушку на долг» — это совпадает с арифметикой, но противоречит полевым данным
о co-holding как устройстве самоконтроля (Gathergood & Weber, тема 36) и с человеческой стороны может не быть принято.

### 1.3. Таблица рамки

| Параметр | Оценка |
|---|---|
| **Что умеет лучше нашей** | Видит время: срок цели, момент закрытия дорогого долга, «подушка чуть позже — минус 10 тыс.»; точный оптимум, а не лучший из 66; с деревом сценариев — первый ход, устойчивый к потере дохода; цена компромиссов в рублях (двойственные оценки в LP-части) |
| **Чего не умеет** | Не знает предпочтений человека — нужна целевая функция (проценты? полезность?); оптимизирует ошибки прогноза (DeMiguel/Michaud, тема 40); деньги-только модель предлагает просрочку и «съесть подушку»; сценарии и вероятности надо откуда-то взять; объяснение решения MILP дорого (тема 40, X-MILP) |
| **Данные** | Остатки, ставки, минимальные платежи, сроки целей — **есть**. Вероятность и длительность потери дохода, доступность экстренного кредита, цена просрочки — **нет** (для РФ помесячных шоков дохода не добыто, ЗАДОЛЖЕННОСТЬ Г40 № 10) |
| **Сложность соло** | Детерминированный MILP на 12 мес. — 1–2 дня (`highspy`, MIT); с деревом сценариев — неделя + генератор сценариев; боевой контур с таймаутами и фолбэком — ещё неделя (тема 40) |
| **Объяснимость** | 🟡 план по месяцам понятен («сначала МФО, потом подушка, с 6-го месяца отпуск»), но **почему** именно так — только через контрфактические прогоны («если подушку к месяцу 2 — +10 тыс.») |
| **Закон** | 🟢 предмет тот же — свои долги и деньги; 🔴 рекомендация «не платите, выгоднее просрочка» недопустима по 353-ФЗ/этике и ведёт к вреду — запрещать ограничением |
| **Что взять кусочком** | (1) **MILP как офлайн-оракул** на синтетике: «сколько рублей теряет канон против оптимума на 8–12 мес.» (метрика Г39, скрипт `f5b.py` — готовая основа); (2) **правило «сначала токсичный долг, даже из части подушки выше аварийного минимума»**, выведенное оптимизацией, проверить как ε-правило внутри перебора; (3) VSS-замер на портретах ADR-015 — стоит ли вообще стохастика |
| **Какую проблему Г40 закрывает** | № 2 (кризисный floor при токсичном долге) и № 3 («всё или ничего» у floor) — **даёт количественное основание** правки; № 6 (срок цели) — многопериодная постановка **закрывает по построению**; вырождение в угол — **не лечит** (LP сам даёт вершины, Вежбицкий 1979); нечувствительность к ставке — **закрывает** (ставка входит в цель напрямую, в рублях) |

### Скрипт рамки 1 (дословно)

**f1a.py** (запуск: `scratchpad/g41/sv/bin/python`, HiGHS 1.15.1)

```python
"""G41 frame 1 (a): two-stage stochastic MILP on the running example, value of the stochastic solution (VSS).
Months 1-2 are decided now (shared by all scenarios); from month 3 the future branches:
  S0 p=0.90: income as usual (free flow before debt payments 35 000)
  S1 p=0.10: job lost in months 3-4 (income 0 -> flow before debt payments = -55 000), back from month 5
Cushion can be spent (reserve move s may be negative, cushion C >= 0). If cash is short, an emergency loan E
at the MFO rate (292 %/yr) is taken. Vacation 80 000 by month 8 is required in S0 only (postponed in S1).
Objective: minimise EXPECTED interest (incl. emergency loan) = maximise expected net position (identity checked in f5a).
RP  = stochastic solution; EV = solve with expected flows, fix months 1-2, re-evaluate in the tree (EEV);
NOM = solve assuming no shock, fix months 1-2, re-evaluate (ENOM). VSS = EEV - RP."""
import highspy, numpy as np
DEBTS = [("cc", 120_000, 0.35, 6_000), ("mfo", 30_000, 2.92, 9_000)]
R_EMERG = 2.92
T, M, FIRST = 8, 1e7, 2
BASE = 35_000
SHOCK = -55_000


def build(scen, fix_first=None, vac_in=(0,), r_emerg=None, lam=0.0):
    """scen: list of (prob, flows[T]). fix_first: dict name->value for first-stage vars. Returns (obj, sol dict)."""
    R_E = R_EMERG if r_emerg is None else r_emerg
    h = highspy.Highs(); h.setOptionValue("output_flag", False); inf = highspy.kHighsInf
    idx = {}

    def var(n, lb=0.0, ub=inf, integer=False, cost=0.0):
        h.addVar(lb, ub); j = h.getNumCol() - 1; h.changeColCost(j, cost)
        if integer:
            h.changeColIntegrality(j, highspy.HighsVarType.kInteger)
        idx[n] = j

    def row(c, lo, hi):
        h.addRow(lo, hi, len(c), np.array([idx[n] for n, _ in c], dtype=np.int32), np.array([v for _, v in c], dtype=float))
    for s, (p, flows) in enumerate(scen):
        for k, (_, B0, r, m) in enumerate(DEBTS):
            for t in range(T + 1):
                var(("B", s, k, t), cost=p * r / 12 if t < T else 0)
            for t in range(T):
                var(("y", s, k, t)); var(("z", s, k, t), 0, 1, True)
        for t in range(T + 1):
            var(("E", s, t), cost=p * R_E / 12 if t < T else 0); var(("C", s, t))
        for t in range(T):
            var(("s", s, t), -inf, inf); var(("g", s, t)); var(("e", s, t))
        for k, (_, B0, r, m) in enumerate(DEBTS):
            row([(("B", s, k, 0), 1)], B0, B0)
            for t in range(T):
                gr = 1 + r / 12
                row([(("B", s, k, t + 1), 1), (("B", s, k, t), -gr), (("y", s, k, t), 1)], 0, 0)
                row([(("y", s, k, t), 1), (("z", s, k, t), -m)], 0, inf)
                row([(("B", s, k, t), gr), (("z", s, k, t), -M)], -inf, m)
        row([(("C", s, 0), 1)], 20_000, 20_000); row([(("E", s, 0), 1)], 0, 0)
        for t in range(T):
            ge = 1 + R_E / 12
            # budget: debt payments + reserve move + goal + emergency repayment = flow + new emergency borrowing
            row([(("y", s, k, t), 1) for k in range(len(DEBTS))] + [(("s", s, t), 1), (("g", s, t), 1), (("E", s, t + 1), -1), (("E", s, t), ge)], flows[t], flows[t])
            row([(("C", s, t + 1), 1), (("C", s, t), -1), (("s", s, t), -1)], 0, 0)
        if s in vac_in:
            row([(("g", s, t), 1) for t in range(T)], 80_000, inf)
        var(("PK", s), cost=p * lam)                 # non-monetary harm proxy: lam RUB per RUB of peak shortfall
        for t in range(T + 1):
            row([(("PK", s), 1), (("E", s, t), -1)], 0, inf)
    # non-anticipativity for first-stage months
    names = lambda s, t: [("s", s, t), ("g", s, t)] + [("y", s, k, t) for k in range(len(DEBTS))]
    for s in range(1, len(scen)):
        for t in range(FIRST):
            for a, b in zip(names(0, t), names(s, t)):
                row([(a, 1), (b, -1)], 0, 0)
    if fix_first:
        for t in range(FIRST):
            for n in names(0, t):
                v = fix_first[(n[0],) + n[2:]]
                row([(n, 1)], v - 0.5, v + 0.5)
    h.run()
    if h.getModelStatus() != highspy.HighsModelStatus.kOptimal:
        return None, None
    x = h.getSolution().col_value
    val = {n: x[j] for n, j in idx.items()}
    obj = h.getInfo().objective_function_value
    return obj, val


def first_stage(val):
    out = {}
    for t in range(FIRST):
        out[("s", t)] = val[("s", 0, t)]; out[("g", t)] = val[("g", 0, t)]
        for k in range(len(DEBTS)):
            out[("y", k, t)] = val[("y", 0, k, t)]
    return out


def show(label, val, scen):
    fs = first_stage(val)
    parts = []
    for t in range(FIRST):
        parts.append(f"m{t+1}: debt {round(sum(fs[('y', k, t)] for k in range(len(DEBTS))))} reserve {round(fs[('s', t)])} goal {round(fs[('g', t)])}")
    tail = []
    for s in range(len(scen)):
        C = val[("C", s, T)]; E = val[("E", s, T)]; G = sum(val[("g", s, t)] for t in range(T)); B = sum(val[("B", s, k, T)] for k in range(len(DEBTS)))
        Emax = max(val[("E", s, t)] for t in range(T + 1))
        tail.append(f"S{s}: cushion {round(C)} vacation {round(G)} debt {round(B)} emergency-loan peak {round(Emax)}")
    print(f"{label}: " + " | ".join(parts)); print("      " + " | ".join(tail))


if __name__ == "__main__":
    f0 = [BASE] * T
    f1 = [BASE, BASE, SHOCK, SHOCK] + [BASE] * 4
    tree = [(0.9, f0), (0.1, f1)]
    rp, vrp = build(tree)
    print(f"RP (stochastic) expected interest {rp:,.0f}"); show("RP ", vrp, tree)
    ev_flows = [0.9 * a + 0.1 * b for a, b in zip(f0, f1)]
    _, vev = build([(1.0, ev_flows)])
    eev, veev = build(tree, fix_first=first_stage(vev))
    print(f"EEV (expected-value plan's months 1-2, then best recourse) expected interest {eev:,.0f}   VSS = {eev - rp:,.0f} RUB"); show("EEV", veev, tree)
    _, vn = build([(1.0, f0)])
    en, ven = build(tree, fix_first=first_stage(vn))
    print(f"ENOM (no-shock plan's months 1-2, then best recourse) expected interest {en:,.0f}   loss vs RP = {en - rp:,.0f} RUB"); show("NOM", ven, tree)
    # canon months 1-2 from f5a (profile 3): m1 all 20000 to reserve, m2 4000 debt / 16000 reserve (+ minimums 15000 each month)
    canon = {("s", 0): 20_000, ("g", 0): 0, ("s", 1): 16_000, ("g", 1): 0}
    # distribute debt payments as canon (avalanche: prepayment to MFO): m1 minimums only; m2 minimums + 4000 to mfo
    canon.update({("y", 0, 0): 6_000, ("y", 1, 0): 9_000, ("y", 0, 1): 6_000, ("y", 1, 1): 13_000})
    ec, vc = build(tree, fix_first=canon)
    print(f"ECANON (canon months 1-2, then best recourse) expected interest {ec:,.0f}   loss vs RP = {ec - rp:,.0f} RUB"); show("CAN", vc, tree)

    print()
    print("VARIANT: no emergency credit; shortfall = arrears at 20 %/yr (353-FZ late-fee cap) + harm proxy lam per RUB of peak arrears")
    for lam in (0.0, 0.25, 1.0):
        rp2, v2 = build(tree, r_emerg=0.20, lam=lam)
        _, vev2 = build([(1.0, ev_flows)], r_emerg=0.20, lam=lam)
        eev2, _ = build(tree, fix_first=first_stage(vev2), r_emerg=0.20, lam=lam)
        ec2, vc2 = build(tree, fix_first=canon, r_emerg=0.20, lam=lam)
        print(f" lam={lam}: RP {rp2:,.0f}  EEV {eev2:,.0f}  VSS {eev2 - rp2:,.0f}  canon-first-stage {ec2:,.0f} (loss {ec2 - rp2:,.0f})")
        show("   RP ", v2, tree)

    print()
    print("ROBUST (worst case = shock for sure): plan months 1-2 against S1 only, then evaluate in the tree")
    for r_e, lam in ((None, 0.0), (0.20, 1.0)):
        _, vrob = build([(1.0, f1)], vac_in=(), r_emerg=r_e, lam=lam)
        erob, verob = build(tree, fix_first=first_stage(vrob), r_emerg=r_e, lam=lam)
        rp3, _ = build(tree, r_emerg=r_e, lam=lam)
        print(f" emergency rate {r_e or R_EMERG}, lam {lam}: robust-first-stage expected {erob:,.0f} vs RP {rp3:,.0f} (price of robustness {erob - rp3:,.0f})")
        show("   ROB", verob, tree)
```

**Вывод f1a.py:**
```
RP (stochastic) expected interest 28,000
RP : m1: debt 43300 reserve -8300 goal 0 | m2: debt 6000 reserve 29000 goal 0
      S0: cushion 0 vacation 130922 debt 0 emergency-loan peak 0 | S1: cushion 0 vacation 0 debt 0 emergency-loan peak 138299
EEV (expected-value plan's months 1-2, then best recourse) expected interest 33,750   VSS = 5,750 RUB
EEV: m1: debt 55000 reserve -20000 goal 0 | m2: debt 35000 reserve 0 goal 0
      S0: cushion 0 vacation 132551 debt 0 emergency-loan peak 0 | S1: cushion 0 vacation 0 debt 0 emergency-loan peak 210458
ENOM (no-shock plan's months 1-2, then best recourse) expected interest 33,750   loss vs RP = 5,750 RUB
NOM: m1: debt 55000 reserve -20000 goal 0 | m2: debt 35000 reserve 0 goal 0
      S0: cushion 0 vacation 132551 debt 0 emergency-loan peak 0 | S1: cushion 0 vacation 0 debt 0 emergency-loan peak 210458
ECANON (canon months 1-2, then best recourse) expected interest 43,361   loss vs RP = 15,361 RUB
CAN: m1: debt 15000 reserve 20000 goal 0 | m2: debt 19000 reserve 16000 goal 0
      S0: cushion 0 vacation 117910 debt 0 emergency-loan peak 0 | S1: cushion 0 vacation 0 debt 0 emergency-loan peak 174799

VARIANT: no emergency credit; shortfall = arrears at 20 %/yr (353-FZ late-fee cap) + harm proxy lam per RUB of peak arrears
 lam=0.0: RP 15,552  EEV 15,552  VSS 0  canon-first-stage 32,268 (loss 16,716)
   RP : m1: debt 160800 reserve -20000 goal 0 | m2: debt 0 reserve 0 goal 0
      S0: cushion 0 vacation 135507 debt 0 emergency-loan peak 105800 | S1: cushion 0 vacation 0 debt 0 emergency-loan peak 185919
 lam=0.25: RP 21,764  EEV 21,764  VSS 0  canon-first-stage 35,968 (loss 14,204)
   RP : m1: debt 55000 reserve -20000 goal 0 | m2: debt 35000 reserve 0 goal 0
      S0: cushion 0 vacation 132551 debt 0 emergency-loan peak 0 | S1: cushion 0 vacation 0 debt 0 emergency-loan peak 123017
 lam=1.0: RP 28,733  EEV 30,990  VSS 2,258  canon-first-stage 42,725 (loss 13,992)
   RP : m1: debt 43300 reserve -8300 goal 0 | m2: debt 6000 reserve 29000 goal 0
      S0: cushion 0 vacation 130922 debt 0 emergency-loan peak 0 | S1: cushion 0 vacation 0 debt 0 emergency-loan peak 81638

ROBUST (worst case = shock for sure): plan months 1-2 against S1 only, then evaluate in the tree
 emergency rate 2.92, lam 0.0: robust-first-stage expected 28,000 vs RP 28,000 (price of robustness 0)
   ROB: m1: debt 43300 reserve -8300 goal 0 | m2: debt 6000 reserve 29000 goal 0
      S0: cushion 0 vacation 130922 debt 0 emergency-loan peak 0 | S1: cushion 0 vacation 0 debt 0 emergency-loan peak 138299
 emergency rate 0.2, lam 1.0: robust-first-stage expected 28,733 vs RP 28,733 (price of robustness 0)
   ROB: m1: debt 43300 reserve -8300 goal 0 | m2: debt 6000 reserve 29000 goal 0
      S0: cushion 0 vacation 130922 debt 0 emergency-loan peak 0 | S1: cushion 0 vacation 0 debt 0 emergency-loan peak 81638
```

---

## Рамка 2. Динамическое программирование и марковские процессы решений (MDP)

> База: тема 38 (`raw/dp_vs_enumeration_2026-09-10.md`) — точное DP на нашей размерности невычислимо
> (N=3 долга, 2 цели, сетка 10 %: 1,95·10⁷ состояний, 13,7 ч; N=5 — 446 сут., по границе Rust 1997, с. 490);
> «оптимизированное правило большого пальца» теряет против DP < 0,5 % годового потребления (Love 2011, с. 3),
> с обновлением < 0,06 %; но при неопределённости предпочтений потери растут до 2 % (Love 2011, с. 4).
> Здесь нового: **классификация нашего ядра в единой таксономии политик** и **проверка числом, сколько даёт поиск
> по объяснимым правилам против стохастического оптимума** на сквозном примере.

### 2.0. Аналогия → суть

**Аналогия.** DP — это навигатор, который заранее просчитал **для каждого перекрёстка города** лучший поворот к цели.
Великолепно, но карта нашего «города» (все сочетания остатков долгов, подушки и копилок) слишком велика. На практике
навигаторы делают иначе: либо **пересчитывают маршрут на несколько кварталов вперёд на каждом перекрёстке**
(«скользящий горизонт», MPC), либо **едут по хорошему простому правилу**, параметры которого подобраны на тысячах
поездок («на перекрёстке держись главной дороги, если пробка меньше X»).

**Суть.** MDP: состояние $S_t$ (остатки долгов, подушка, копилки, доход), решение $x_t$ (куда деньги), случайность
$W_{t+1}$ (шок дохода, ставка), переход $S_{t+1}=f(S_t,x_t,W_{t+1})$. Ищется **политика** $X^\pi(S_t)$ — правило
«состояние → решение», максимизирующее ожидаемый итог. Уравнение Беллмана: $V_t(S)=\max_x\{C(S,x)+\mathbb E\,V_{t+1}(S')\}$,
где $V_t$ — «ценность оказаться в состоянии $S$ в месяце $t$», $C$ — выигрыш текущего месяца.

### 2.1. Литература — дословно

1. **Powell W. B. (2019), «From Reinforcement Learning to Optimal Control: A unified framework for sequential decisions»,
   arXiv:1912.03513.** `https://arxiv.org/pdf/1912.03513`, `curl` HTTP 200, 2 170 296 байт, `pdftotext`, 17.09.2026. Дословно:
   > «we claim that the four classes are universal: any policy proposed for any sequential decision problem will consist of
   > one of these four classes, and possibly a hybrid.»
   > «Many have found that Q-learning often does not work well. In fact, Q-learning, as with all approximate dynamic
   > programming algorithms, tend to work well only on a fairly small set of problems.»
2. **Powell W. B. (2023), «A Universal Framework for Sequential Decision Problems», *OR/MS Today*,
   DOI 10.1287/orms.2023.01.02.** Прямой `curl` — HTTP 403 (антибот INFORMS); `r.jina.ai` без UA — HTTP 200, 17 145 байт,
   17.09.2026. Дословно (четыре класса):
   > «Policy function approximations (PFAs). Analytical functions that map the information in the state variable direction to a decision.» [sic: «direction» в оригинале, по смыслу «directly»]
   > «Cost function approximations (CFAs). A parameterized optimization problem that is typically a deterministic approximation,
   > in which parameters have been introduced to make it work well under uncertainty. CFAs are widely used in industry in an
   > ad hoc way, but I have not been able to find this strategy formally studied in the research literature»
   > «Value function approximations (VFAs). Policies based on VFAs cover all methods based on Bellman's equation […] most
   > commonly today, reinforcement learning.»
   > «Deterministic DLAs are when we ignore uncertainty to create a deterministic lookahead model, a strategy that is often
   > called a rolling (or receding) horizon procedure, or model predictive control. It is possible to parameterize the
   > lookahead to help make it more robust to uncertainty, producing a hybrid CFA/DLA.»
   (Опечатка «direction» есть и в выдаче Exa, и в тексте `r.jina.ai` — это текст источника, сверено `grep` по `orms_j.txt`.)

**🔴 Куда в этой таксономии попадает FINPILOT.** Наш месячный цикл — **CFA**: параметризованная детерминированная
оптимизационная задача (перебор 66 точек со взвешенной суммой), параметры которой (веса профилей, floor, $L^*$, порог
токсичности 30 %, $r_{bench}$) введены, «чтобы работало в неопределённости», и **подобраны вручную** (петля Г31.4).
По Powell это законный и широко используемый в индустрии класс — и **его слабость ровно в ручной настройке параметров**.
Формулировка для магистерской: «политика класса CFA с экспертно заданными параметрами» — точнее, чем «эвристика».

### 2.2. Проверка числом: поиск по объяснимым правилам (policy search) против стохастического оптимума

`f2a.py`: тот же сценарный мир, что `f1a.py` (10 % — два месяца без дохода, экстренный кредит 292 %), своя
бухгалтерия (сохранение денег проверяется `assert`). Класс правил из 4 параметров, понятных человеку:
$\tau$ — ставка, выше которой долг «токсичный» и гасится первым; `keep` — сколько месяцев подушки не трогать ради
токсичного долга; $c$ — до скольки месяцев добивать подушку; `goal_first` — копить ли на цель по графику до досрочки.
Перебор 3×3×3×2 = 54 правил.

| Политика | Ожидаемые проценты за 8 мес. | Отпуск (благополучная ветка) | Подушка (благополучная ветка) |
|---|---|---|---|
| Подражание канону: «подушка до 1 мес., потом лавина, цель в конце» | 47 470 ₽ | 58 265 ₽ | 55 000 ₽ |
| **Лучшее правило**: $\tau$=100 %, keep=0, $c$=0,5 мес. | **31 525 ₽** | 80 000 ₽ | 49 620 ₽ |
| Стохастический оптимум MILP (`f1a.py`, RP) | 28 000 ₽ | ≥ 80 000 ₽ | 0 ₽ |

**Что это значит на примере.** Простое правило «займы дороже 100 % годовых гасим первыми, подушку держим на полмесяца,
остальное — лавиной» забирает **82 % возможного выигрыша** ((47 470 − 31 525)/(47 470 − 28 000)) и при этом
объясняется одной фразой. Остальные 18 % (3 525 ₽) — цена объяснимости. Это ровно тезис Love (2011) и тема 38,
теперь на нашем примере: **ценность не в DP, а в том, чтобы параметры правила подбирались симуляцией, а не голосованием экспертов.**
Оговорка: подражание канону — эмуляция в чужой бухгалтерии, а не вызов `app/core` (в реальном каноне отпуск 2 748 ₽, `f5a.py`).

### 2.3. Таблица рамки

| Параметр | Оценка |
|---|---|
| **Что умеет лучше нашей** | Решение во времени; учёт того, что сегодняшний ход меняет завтрашние возможности (закрытый долг освобождает платёж); оптимальная политика при известной модели мира; единый язык для всех остальных рамок (Powell) |
| **Чего не умеет** | Точное DP — проклятие размерности (тема 38: 13,7 ч – 446 сут.); VFA/RL «работают на узком классе задач» (Powell); политика-таблица необъяснима; чувствительна к модели дохода (замера для нашего случая нет — тема 38) |
| **Данные** | Переходы (как меняются долги) — есть; распределение шоков дохода по месяцам — **нет для РФ**; предпочтения (что важнее к сроку) — частично (сроки целей) |
| **Сложность соло** | Точное DP для 1 долга + подушки как эталон — 1 день (тема 38, п. 4); **policy search** по 4–6 параметрам правил на синтетике — 2–3 дня (`f2a.py` — прототип); ADP/RL — недели и без гарантий |
| **Объяснимость** | Таблица DP — 🔴; правило из policy search — 🟢 («гасим займы дороже X %, подушка Y мес.»); MPC — 🟡 |
| **Закон** | 🟢 то же, что сейчас, пока не учится на данных пользователей; 🟡 с обучением на логах — система ИИ по AI Act ст. 3(1) (тема 37, `causal_effect_measurement`, п. 42/46 Guidelines) |
| **Что взять кусочком** | (1) Назвать ядро **CFA по Powell** в научной формулировке; (2) **калибровать параметры канона (floor, порог токсичности, $L^*$) policy search-ем на симуляторе** вместо экспертного согласия — разрывает петлю Г31.4; (3) MILP из рамки 1 — как «оракул-DLA» для оценки потерь правила |
| **Какую проблему Г40 закрывает** | № 28 (параметры без внешней опоры) и № 14 (порог 30 % разворачивает весь поток) — **закрывает методически**: порог подбирается по ожидаемым потерям; № 2–3 (floor) — даёт число; углы, тождественные критерии — **не касается** |

### Скрипт рамки 2 (дословно)

**f2a.py** (запуск: `.venv/bin/python` проекта, без импорта `app`)

```python
"""G41 frame 2 (a): 'optimized rule of thumb' (Love 2011) = policy search over an explainable rule class,
evaluated in the same 2-scenario tree as f1a.py (p=0.1 two months without income, emergency credit at 292 %/yr).
Own ledger, no product code. Money conservation is asserted every run.
Rule(tau, keep, c, goal_first):
  1) pay minimums; if flow < 0 -> take from cushion, then emergency loan
  2) repay emergency loan first (highest rate)
  3) if some debt has rate > tau: send everything there, and also cushion above keep*E (E = monthly expenses)
  4) fill cushion up to c*E
  5) if goal_first: goal money up to the amount needed per remaining month
  6) the rest: highest-rate debt; when no debt: goal, then cushion
Metric: expected interest (incl. emergency), vacation in S0 by month 8, emergency peak in S1, and the MILP RP from f1a (28 000)."""
import itertools
E_EXP = 55_000
DEBTS0 = [["cc", 120_000.0, 0.35, 6_000.0], ["mfo", 30_000.0, 2.92, 9_000.0]]
R_EM = 2.92
T = 8
GOAL, GOAL_T = 80_000.0, 8


def simulate(policy, flows, check=True):
    tau, keep, c, goal_first = policy
    debts = [d[:] for d in DEBTS0]
    cushion, goal, em, interest, em_peak = 20_000.0, 0.0, 0.0, 0.0, 0.0
    start_total = cushion + goal - sum(d[1] for d in debts) - em
    inflow = 0.0
    for t in range(T):
        inflow += flows[t]
        # interest accrues on start-of-month balances
        for d in debts:
            i = d[1] * d[2] / 12; d[1] += i; interest += i
        i = em * R_EM / 12; em += i; interest += i
        cash = float(flows[t])
        for d in debts:                                  # 1) minimums
            pay = min(d[3], d[1]); d[1] -= pay; cash -= pay
        if cash < 0:
            take = min(cushion, -cash); cushion -= take; cash += take
            if cash < 0:
                em += -cash; cash = 0.0
        em_peak = max(em_peak, em)
        pay = min(em, cash); em -= pay; cash -= pay       # 2) emergency loan first
        toxic = [d for d in debts if d[1] > 0.5 and d[2] > tau]   # 3) toxic debt, also from cushion above keep
        if toxic:
            d = max(toxic, key=lambda x: x[2])
            extra = max(0.0, cushion - keep * E_EXP)
            pay = min(d[1], cash + extra)
            from_cash = min(pay, cash); cash -= from_cash; cushion -= pay - from_cash; d[1] -= pay
        top = max(0.0, c * E_EXP - cushion); put = min(top, cash); cushion += put; cash -= put   # 4)
        if goal_first:                                    # 5)
            need = max(0.0, GOAL - goal) / max(1, GOAL_T - t); put = min(need, cash); goal += put; cash -= put
        for d in sorted(debts, key=lambda x: -x[2]):      # 6)
            pay = min(d[1], cash); d[1] -= pay; cash -= pay
        put = min(max(0.0, GOAL - goal), cash); goal += put; cash -= put
        cushion += cash
        debts = [d for d in debts if d[1] > 0.5] + [[d[0], 0.0, d[2], d[3]] for d in debts if d[1] <= 0.5 and False]
    end_total = cushion + goal - sum(d[1] for d in debts) - em
    if check:
        assert abs((end_total - start_total) - (inflow - interest)) < 1.0, (end_total - start_total, inflow - interest)
    return interest, goal, cushion, em_peak, sum(d[1] for d in debts) + em


def evaluate(policy):
    f0 = [35_000] * T
    f1 = [35_000, 35_000, -55_000, -55_000] + [35_000] * 4
    i0, g0, c0, _, d0 = simulate(policy, f0)
    i1, g1, c1, p1, d1 = simulate(policy, f1)
    return 0.9 * i0 + 0.1 * i1, g0, c0, p1, i0, i1


if __name__ == "__main__":
    INF = 99.0
    canon_like = (INF, 0.0, 1.0, False)   # cushion to 1 month first, then avalanche, goal last  (the canon's month 1-2 behaviour)
    print("canon-like rule (cushion to 1 month first, then avalanche, goal last):")
    ei, g0, c0, p1, i0, i1 = evaluate(canon_like)
    print(f"   expected interest {ei:,.0f}  | S0: interest {i0:,.0f} vacation {g0:,.0f} cushion {c0:,.0f} | S1: interest {i1:,.0f} emergency peak {p1:,.0f}")
    grid = list(itertools.product([0.30, 1.0, INF], [0.0, 0.2, 0.5], [0.5, 1.0, 2.0], [False, True]))
    res = []
    for pol in grid:
        ei, g0, c0, p1, i0, i1 = evaluate(pol)
        res.append((ei, pol, g0, c0, p1))
    print("best rules by expected interest, among those that deliver the vacation in S0 (>= 79 999):")
    ok = sorted([r for r in res if r[2] >= 79_999], key=lambda r: r[0])
    for ei, pol, g0, c0, p1 in ok[:6]:
        print(f"   tau={pol[0]} keep={pol[1]} c={pol[2]} goal_first={pol[3]}: expected interest {ei:,.0f}  vacation {g0:,.0f}  cushion S0 {c0:,.0f}  S1 emergency peak {p1:,.0f}")
    print("best rules overall (vacation not required):")
    for ei, pol, g0, c0, p1 in sorted(res, key=lambda r: r[0])[:3]:
        print(f"   tau={pol[0]} keep={pol[1]} c={pol[2]} goal_first={pol[3]}: expected interest {ei:,.0f}  vacation {g0:,.0f}  cushion S0 {c0:,.0f}  S1 emergency peak {p1:,.0f}")
    print("reference: stochastic MILP RP from f1a.py = 28 000 (no cushion floor imposed, vacation required in S0)")
```

**Вывод f2a.py:**
```
canon-like rule (cushion to 1 month first, then avalanche, goal last):
   expected interest 47,470  | S0: interest 36,735 vacation 58,265 cushion 55,000 | S1: interest 144,077 emergency peak 113,646
best rules by expected interest, among those that deliver the vacation in S0 (>= 79 999):
   tau=1.0 keep=0.0 c=0.5 goal_first=False: expected interest 31,525  vacation 80,000  cushion S0 49,620  S1 emergency peak 127,630
   tau=1.0 keep=0.2 c=0.5 goal_first=False: expected interest 31,525  vacation 80,000  cushion S0 49,620  S1 emergency peak 127,630
   tau=0.3 keep=0.2 c=0.5 goal_first=False: expected interest 33,056  vacation 80,000  cushion S0 51,188  S1 emergency peak 157,710
   tau=0.3 keep=0.2 c=0.5 goal_first=True: expected interest 33,056  vacation 80,000  cushion S0 51,188  S1 emergency peak 157,710
   tau=0.3 keep=0.5 c=0.5 goal_first=False: expected interest 33,804  vacation 80,000  cushion S0 47,355  S1 emergency peak 127,630
   tau=1.0 keep=0.5 c=0.5 goal_first=False: expected interest 33,804  vacation 80,000  cushion S0 47,355  S1 emergency peak 127,630
best rules overall (vacation not required):
   tau=1.0 keep=0.0 c=0.5 goal_first=False: expected interest 31,525  vacation 80,000  cushion S0 49,620  S1 emergency peak 127,630
   tau=1.0 keep=0.2 c=0.5 goal_first=False: expected interest 31,525  vacation 80,000  cushion S0 49,620  S1 emergency peak 127,630
   tau=1.0 keep=0.0 c=1.0 goal_first=False: expected interest 31,779  vacation 71,724  cushion S0 55,000  S1 emergency peak 107,225
reference: stochastic MILP RP from f1a.py = 28 000 (no cushion floor imposed, vacation required in S0)
```

---

## Рамка 3. Экономические модели жизненного цикла: буферный запас Кэрролла, Мертон, потребление-сбережение с долгом, co-holding

> База: тема 13 (`raw/goal_based_investing_lifecycle_2026-09-09.md` §4) — Модильяни–Мертон про десятилетия и к нашему
> горизонту не переносятся; верная опора — buffer-stock (Carroll 1997, Deaton 1991, Gourinchas–Parker 2002), цитаты
> Дейтона дословно; тема 14 (`raw/debt_payoff_math_cashflow_forecast_2026-09-09.md` §3) — Telyukova, рабочая версия 2009;
> тема 34 (`raw/rf_household_finance_stats_v2_2026-09-10.md`, Г17.8) — Арженовский 2025 (ОДПФ): «Households prefer to reduce
> consumer spending in order to direct the freed-up income to debt servicing and/or savings to insure against income shocks,
> which is consistent with Carroll's buffer-stock theory» (аннотация).

### 3.0. Аналогия → суть

**Аналогия.** Буферный запас — это бак с водой на даче при ненадёжном водопроводе. Слишком маленький — в засуху сидишь
без воды (занимаешь у соседа под 292 %). Слишком большой — вода застаивается (деньги лежат под 0 % вместо погашения
кредитки под 35 %). Модель Кэрролла считает **размер бака из того, как часто и надолго отключают воду** (волатильность
дохода, вероятность месяца без дохода), насколько человек нетерпелив и как боится остаться без воды.

**Суть.** Человек каждый месяц выбирает потребление $c_t$ из «наличности под рукой» $m_t$ (всё, что есть, делённое на
постоянный доход); остаток $a_t=m_t-c_t$ переходит в следующий месяц: $m_{t+1}=\frac{R}{\Gamma\psi_{t+1}}a_t+\theta_{t+1}$,
где $R$ — доходность подушки, $\Gamma$ — рост дохода, $\psi$ — постоянный шок дохода, $\theta$ — временный шок (с вероятностью
$p_0$ дохода нет вовсе). Максимизируется ожидаемая полезность $\sum\beta^t u(c_t)$, $u(c)=c^{1-\rho}/(1-\rho)$: $\beta$ —
терпеливость, $\rho$ — неприятие риска и «осторожность». Главное свойство: существует **целевой запас** $m^*$ — ниже него
человек копит, выше — тратит.

### 3.1. Литература — дословно

1. **Carroll C. D. (2004), «Theoretical Foundations of Buffer Stock Saving», NBER WP 10867.**
   `https://www.nber.org/system/files/working_papers/w10867/w10867.pdf`, `curl` HTTP 200, 371 428 байт, 44 с., `pdftotext`, 17.09.2026. Дословно:
   > «when consumers are both impatient and "prudent" there will be a target level of nonhuman wealth ('cash' for short) such
   > that if actual cash exceeds the target, the consumer will spend freely and cash will fall (in expectation), while if actual
   > cash is below the target the consumer will save and cash will rise.» (с. 2)
   > «Third, there exists a unique 'target' cash-on-hand-to-permanent-income ratio.» (с. 3)
   > «Define the target cash-on-hand-to-income ratio m∗ as the value of m such that Et[m̃t+1/mt] = 1 if mt = m∗.» (разд. 3.3, ур. 115)
   > «Gourinchas and Parker (2002) estimate the model and conclude that the buffer-stock saving phase of life lasts from age 25
   > until around age 40-45» (с. 2)
2. **Telyukova I. A. (2013), «Household Need for Liquidity and the Credit Card Debt Puzzle», *Review of Economic Studies*,
   DOI 10.1093/restud/rdt001.** Реферат журнальной версии — OpenAlex `api.openalex.org/works?search=…` HTTP 200, 17.09.2026:
   > «households that accumulate credit card debt may not pay it off using their money in the bank, because they anticipate
   > needing that money in situations where credit cards cannot be used. […] The model accounts for between 44% and 56% of the
   > households in the data who hold consumer debt and liquidity simultaneously, and for 100% of the liquidity held by a median
   > such household. Under reasonable calibration alternatives, the model can capture the entire puzzle group size as well.
   > One-half of money demand in the model is precautionary.»
   🔴 **Закрывает расхождение темы 14** («85–104 %» в рабочей версии 2009 против «44–56 %» по сниппету): окончательные числа —
   **44–56 % домохозяйств и 100 % ликвидности медианного**, это текст реферата журнальной версии (OpenAlex), а не сниппет.
   OA-копия `escholarship.org/content/qt0ww2c04z/qt0ww2c04z.pdf` вернула HTTP 202 (0 байт, очередь генерации) — полный текст не открыт.
3. **Druedahl J., Jørgensen C. N. (2018), «Precautionary borrowing and the credit card debt puzzle», *Quantitative Economics*
   9(2), DOI 10.3982/QE604.** Страница `doi.org/10.3982/qe604`, HTTP 200, 69 163 байта. Реферат:
   > «This paper addresses the credit card debt puzzle using a generalization of the buffer-stock consumption model with
   > long-term revolving debt contracts. […] We show that for some intermediate values of liquid net worth it is indeed optimal
   > for households to simultaneously hold positive gross debt and positive gross assets even though the interest rate on the
   > debt is much higher than the return rate on the assets.»
4. **Gross D. B., Souleles N. S. (2002), QJE 117(1), DOI 10.1162/003355302753399472** (OpenAlex, реферат):
   > «there are other results that conventional models cannot easily explain, for example, why so many people are borrowing on
   > their credit cards, and simultaneously holding low yielding assets. The long-run elasticity of debt to the interest rate is
   > approximately -1.3»
5. **Мертон** — полный текст WP 58 (1970) добыт в Г31.5 (тема 13); по Дейтону: «Merton showed that if risk is confined to
   financial assets […] Of course, that leaves a hole in the argument — earnings themselves are uncertain». Задача Мертона —
   выбор доли рискованных активов; у нас активов нет по закону (тема 18, S1/S6) — **рамка неприменима к ядру**.

### 3.2. Проверка числом: подушка из распределения дохода (`f3a.py`)

Модель Кэрролла, месячный шаг, метод эндогенной сетки, без внешних библиотек. Параметры **иллюстративные, не откалиброваны
на РФ** ($\rho=2$, $\beta=0{,}96$/год, $r=3$ %/год, рост дохода 3 %/год). Результат — целевая подушка в **месяцах дохода**:

| Разброс месячного дохода $\sigma_\theta$ \ вероятность месяца без дохода $p_0$ | 0,5 % | 2 % | 5 % |
|---|---|---|---|
| 0,05 (стабильная зарплата) | 0,83 | 1,41 | 2,09 |
| 0,10 | 0,89 | 1,48 | 2,13 |
| 0,30 (нерегулярный доход) | 1,50 | 1,97 | 2,59 |
| 0,60 (фриланс) | 3,19 | 3,51 | 4,02 |

Чувствительность при $\sigma_\theta=0{,}10$, $p_0=2$ %: терпеливость $\beta$ 0,90 → 0,98 даёт 1,12 → 1,76 мес.;
неприятие риска $\rho$ 1,5 → 5 даёт 1,29 → 2,65 мес.; ставка по подушке 0 % → 3 % даёт 1,26 → 1,48; 🔴 при 8 %
(ближе к российским вкладам) **целевого запаса нет** — нарушено условие нетерпеливости Кэрролла, модель говорит «копи всегда».

**Что это значит на примере.** Наш человек — зарплатник (разброс ~0,05–0,10). Если вероятность остаться месяц без дохода 2 %,
модель даёт цель **~1,4–1,5 месяца дохода** (≈130 000 ₽), при 0,5 % — **~0,9 месяца** (≈80 000 ₽). У фрилансера с тем же
средним доходом — 3,2–4,0 месяца. Размер подушки перестаёт быть «экспертные 2/3/6 месяцев» и становится **функцией того,
насколько рваный у человека доход** — именно той величины (CV с нулевыми месяцами), которую Г40 № 9 нашёл посчитанной неверно.
Цена: результат в 1,5–2 раза зависит от $\rho$ и $\beta$, которых мы у человека не знаем.

### 3.3. Что рамка говорит про co-holding и порог «гасить или копить»

Три независимые работы (Telyukova 2013, Druedahl & Jørgensen 2018, Gross & Souleles 2002) сходятся: **держать подушку при
дорогом долге рационально до некоторого уровня ликвидности**, потому что (а) часть трат нельзя оплатить кредитом,
(б) банк может закрыть доступ к новому кредиту именно тогда, когда случилась беда (корреляция с безработицей). Это
**согласуется с лексикографическим floor канона по направлению**, но **расходится с рамкой 1 по размеру**: MILP «съедает»
подушку, потому что в нём экстренный кредит всегда доступен. Для сквозного примера (кредитка + МФО) рамка 3 советует
держать небольшой floor (≈0,5 мес. — ровно лучший параметр `c` из policy search рамки 2), а не два месяца.

### 3.4. Таблица рамки

| Параметр | Оценка |
|---|---|
| **Что умеет лучше нашей** | **Выводит** размер подушки из риска дохода, а не задаёт экспертно; объясняет, почему подушка при дорогом долге рациональна (co-holding) и до какого уровня; опирается на российские микроданные (Арженовский 2025, ОДПФ) |
| **Чего не умеет** | Не знает целей со сроками и нескольких долгов; требует $\beta$, $\rho$ человека; при высокой ставке вкладов (РФ 2024–2026) условие существования цели нарушается; Мертон неприменим (нет активов по закону) |
| **Данные** | Помесячная история дохода — **есть** (ADR-015, `income_history`); вероятность нулевого месяца — считается из той же истории, но на 3–12 точках шумно; $\beta$, $\rho$ — **нет** (GPS для РФ по стране есть, тема 34 Д9.1, индивидуально — нет) |
| **Сложность соло** | Таблица целевой подушки, заранее посчитанная по сетке ($\sigma_\theta$, $p_0$) и вшитая как справочник: **1–2 дня** (`f3a.py` считает сетку за 14 с). Полная калибровка на ОДПФ — недели |
| **Объяснимость** | 🟢 «ваш доход скачет на ±30 % и раз в год бывает пустой месяц — поэтому подушка 2 месяца, а не 1» |
| **Закон** | 🟢 предмет — собственный резерв; инструментов не называет |
| **Что взять кусочком** | (1) **floor = f(CV дохода с нулевыми месяцами, доля пустых месяцев)** по заранее посчитанной таблице Кэрролла вместо «2/3/6»; (2) формулировка для защиты: floor — «целевой буферный запас» (Carroll 2004), а не экспертная константа; (3) в текстах канона заменить ссылку на Модильяни–Мертона на buffer-stock (уже рекомендация темы 13) |
| **Какую проблему Г40 закрывает** | № 28 и петля Г31.4 для floor и $L^*$ — **закрывает частично** (форма зависимости из теории, уровень — от $\beta,\rho$); № 9 (CV без нулевых месяцев) — **даёт правильную постановку** (нулевые месяцы — отдельный параметр $p_0$); вырождение в угол, ставка, тождественные критерии — **не касается** |

### Скрипт рамки 3 (дословно)

**f3a.py** (запуск: `.venv/bin/python` проекта, только numpy)

```python
"""G41 frame 3 (a): Carroll buffer-stock model (normalised by permanent income), solved by the endogenous grid method.
Question: can a cushion target be DERIVED from the income-risk distribution instead of expert '2/3/6 months'?
Monthly period. Target cash-on-hand m* solves E[m_{t+1}] = m_t (Carroll 2004, eq. 115); reported as end-of-period
assets a* = m* - c(m*) in MONTHS OF PERMANENT INCOME.
Parameters are illustrative, NOT calibrated to Russia (no monthly income-shock data for RF: G40 debt #10)."""
import numpy as np


def gh_lognormal(sigma, n=7):
    """equiprobable discretisation of a mean-one lognormal"""
    if sigma == 0:
        return np.ones(1), np.ones(1)
    from math import erf, sqrt
    q = (np.arange(n) + 0.5) / n
    # inverse normal via bisection (no scipy)
    def ppf(p):
        lo, hi = -10.0, 10.0
        for _ in range(80):
            mid = (lo + hi) / 2
            if 0.5 * (1 + erf(mid / sqrt(2))) < p:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    z = np.array([ppf(p) for p in q])
    x = np.exp(sigma * z - sigma ** 2 / 2)
    return x / x.mean(), np.full(n, 1.0 / n)


def solve(rho=2.0, beta_y=0.96, r_y=0.03, g_y=0.03, sig_psi_y=0.10, sig_theta=0.10, p_unemp=0.005, n=7):
    beta = beta_y ** (1 / 12); R = (1 + r_y) ** (1 / 12); G = (1 + g_y) ** (1 / 12)
    psi, wp = gh_lognormal(sig_psi_y / np.sqrt(12), n)
    th, wt = gh_lognormal(sig_theta, n)
    th = np.concatenate([[0.0], th / (1 - p_unemp)]); wt = np.concatenate([[p_unemp], wt * (1 - p_unemp)])
    a_grid = np.concatenate([np.linspace(0, 1, 40, endpoint=False), np.linspace(1, 60, 200)])
    m_pts = np.array([0.0, 1e-6]); c_pts = np.array([0.0, 1e-6])      # initial guess c(m) = m
    m_pts = np.linspace(0, 100, 5); c_pts = m_pts.copy()
    for it in range(5000):
        cfun = lambda m: np.interp(m, m_pts, c_pts)
        ev = np.zeros_like(a_grid)
        for i, (ps, pw) in enumerate(zip(psi, wp)):
            for j, (tt, tw) in enumerate(zip(th, wt)):
                mn = R / (G * ps) * a_grid + tt
                ev += pw * tw * (G * ps) ** (-rho) * np.maximum(cfun(mn), 1e-12) ** (-rho)
        c_new = (beta * R * ev) ** (-1 / rho)
        m_new = a_grid + c_new
        m_new = np.concatenate([[0.0], m_new]); c_new = np.concatenate([[0.0], c_new])
        diff = np.max(np.abs(np.interp(m_pts, m_new, c_new) - c_pts)) if it > 0 else 1
        m_pts, c_pts = m_new, c_new
        if diff < 1e-7:
            break
    cfun = lambda m: np.interp(m, m_pts, c_pts)
    def drift(m):
        a = m - cfun(m)
        return sum(pw * tw * (R / (G * ps) * a + tt) for ps, pw in zip(psi, wp) for tt, tw in zip(th, wt)) - m
    lo, hi = 0.5, 200.0
    if drift(hi) > 0:
        return None, it
    for _ in range(100):
        mid = (lo + hi) / 2
        if drift(mid) > 0:
            lo = mid
        else:
            hi = mid
    m_star = (lo + hi) / 2
    return m_star - cfun(m_star), it


if __name__ == "__main__":
    print("target end-of-month assets a* in MONTHS of permanent income (rho=2, beta=0.96/yr, r=3%/yr, g=3%/yr, sig_psi=0.10/yr)")
    print("rows: transitory monthly income sd (salaried ~0.1, irregular ~0.3-0.6); cols: monthly probability of a zero-income month")
    probs = [0.005, 0.02, 0.05]
    print("sig_theta \\ p0 " + "".join(f"{p:>10}" for p in probs))
    for sth in (0.05, 0.10, 0.30, 0.60):
        row = []
        for p in probs:
            a, it = solve(sig_theta=sth, p_unemp=p)
            row.append("  none" if a is None else f"{a:10.2f}")
        print(f"{sth:>13} " + "".join(row))
    print("sensitivity to impatience (sig_theta=0.10, p0=0.02): beta_y ->", {b: round(solve(beta_y=b, sig_theta=0.10, p_unemp=0.02)[0], 2) for b in (0.90, 0.93, 0.96, 0.98)})
    print("sensitivity to deposit rate r (beta 0.96): r_y ->", {r: (lambda a: None if a is None else round(a, 2))(solve(r_y=r, sig_theta=0.10, p_unemp=0.02)[0]) for r in (0.0, 0.03, 0.08)})
    print("sensitivity to risk aversion rho (beta 0.96): rho ->", {rh: round(solve(rho=rh, sig_theta=0.10, p_unemp=0.02)[0], 2) for rh in (1.5, 2.0, 3.0, 5.0)})
```

**Вывод f3a.py:**
```
target end-of-month assets a* in MONTHS of permanent income (rho=2, beta=0.96/yr, r=3%/yr, g=3%/yr, sig_psi=0.10/yr)
rows: transitory monthly income sd (salaried ~0.1, irregular ~0.3-0.6); cols: monthly probability of a zero-income month
sig_theta \ p0      0.005      0.02      0.05
         0.05       0.83      1.41      2.09
          0.1       0.89      1.48      2.13
          0.3       1.50      1.97      2.59
          0.6       3.19      3.51      4.02
sensitivity to impatience (sig_theta=0.10, p0=0.02): beta_y -> {0.9: np.float64(1.12), 0.93: np.float64(1.25), 0.96: np.float64(1.48), 0.98: np.float64(1.76)}
sensitivity to deposit rate r (beta 0.96): r_y -> {0.0: np.float64(1.26), 0.03: np.float64(1.48), 0.08: None}
sensitivity to risk aversion rho (beta 0.96): rho -> {1.5: np.float64(1.29), 2.0: np.float64(1.48), 3.0: np.float64(1.82), 5.0: np.float64(2.65)}
```

---

## Рамка 4. Теория полезности и поведенческие модели: ожидаемая полезность, вогнутые функции ценности, теория перспектив, ментальный учёт

> База, которую не переискиваем: тема 15 (`raw/mcda_saw_alternatives_2026-09-09.md` §5) — аддитивная свёртка законна только
> при взаимной независимости предпочтений (UK Government Analysis Function, дословно там же); Г40 п. 3.2 — Monat (2009):
> «the use of local scales precludes the use of importance weights in MCDA», Morton (2017): в MAVT «the weighting questions are
> phrased in terms of increments on different scales»; тема 36 (`raw/behavioral_finance_field_2026-09-10.md`) — λ ≈ 1,8–2,0
> по 607 оценкам (Brown et al.), при симметричном дизайне ≈ 1,07; λ = 2,25 в расчёты не брать; co-holding — ментальный учёт
> как устройство самоконтроля (Gathergood & Weber); тема 13 — Das, Markowitz, Scheid, Statman (2010): потеря от ментальных
> счетов 12 б.п., «small compared to the loss that occurs from investors inaccurately specifying their risk aversions».

### 4.0. Аналогия → суть

**Аналогия.** Первая ложка супа, когда голоден, ценнее десятой. Наша взвешенная сумма считает все ложки одинаковыми:
если рубль в долг «весит» чуть больше рубля в отпуск, туда уходят **все** рубли. Вогнутая функция ценности говорит:
первые 10 000 ₽ на отпуск (чтобы успеть к сроку) ценны очень, следующие — меньше; поэтому выгодно разложить понемногу.
А «глобальная шкала» — мерить сэкономленные проценты **в рублях относительно дохода**, а не «от худшего до лучшего варианта
этого же человека»: тогда 292 % и 35 % перестают выглядеть одинаково.

**Суть.** Аддитивная функция ценности (MAVT): $V(a)=\sum_i w_i\,v_i(q_i(a))$, где $q_i$ — критерий в натуральных единицах,
$v_i$ — функция ценности одного критерия (у нас сейчас $v_i$ = линейная min-max-нормировка **внутри человека**), $w_i$ — вес
«за прирост на шкале». Два независимых изменения: (1) **глобальная шкала** — $q_1$ = сэкономленные за год проценты / месячный
доход, $q_2$ = месяцы подушки, $q_3$ = «цель идёт по графику» (0…1); (2) **вогнутость** — $v(q)=q^\alpha$, $0<\alpha<1$.
Ожидаемая полезность — то же, но с усреднением по сценариям. Теория перспектив — ценность считается от точки отсчёта
(«сегодня»), потери весят сильнее выигрышей.

### 4.1. Проверка числом (`f4a.py`, те же 232 портрета Г40, веса — веса профилей канона, выбор среди точек floor-уровня)

| Функция ценности | Доля «угловых» планов | Выбор меняется при ставках ×4 | Направление при ставках ×4 |
|---|---|---|---|
| Канон (min-max внутри человека, линейно) | 87,1 % | **0,0 %** | — |
| Глобальная шкала, линейно ($\alpha$=1) | 65,5 % | 31,9 % | доля долга ↑ 74, = 158, **↓ 0** |
| Глобальная шкала, $\sqrt{\cdot}$ ($\alpha$=0,5) | **10,3 %** | **76,3 %** | доля долга ↑ 177, = 55, **↓ 0** |
| Глобальная шкала, $\alpha$=0,3 | 7,3 % | 72,4 % | — |

**Сквозной пример** (профиль 3):

| Ситуация | Канон | Глобальная линейная | Глобальная $\sqrt{\cdot}$ |
|---|---|---|---|
| Кредитка 35 %, МФО 292 %, подушка 60 000 | 100 % долг | 50 % долг / 50 % отпуск | **70 % долг / 30 % отпуск** |
| Кредитка 15 %, МФО 90 %, подушка 60 000 | 100 % долг | 50 % подушка / 50 % отпуск | **50 % долг / 50 % отпуск** |
| Кредитка 35 %, МФО 292 %, подушка 20 000 | 100 % подушка | 100 % подушка | 100 % подушка (floor) |

**Что это значит на примере.** С вогнутой функцией на общей шкале совет **впервые зависит от ставки**: при МФО под 292 %
70 % потока идёт в долг, при 90 % — половина; и **никогда** не уменьшает долю долга при росте ставок (0 перевёрнутых случаев
из 232). Отпуск при этом получает свои 10 000 ₽/мес. «по графику» в первом случае частично (30 % = 6 000 ₽), во втором
полностью. Это ровно то, что Г40 искал: одна правка — и уходят сразу **вырождение в угол** и **слепота к ставке**.

🔴 **Цена и честная оговорка.** (1) $\alpha$ и глобальные шкалы — новые параметры без внешней опоры; $\alpha$=0,5 и 0,3 дают
близкие доли (10 % и 7 % углов), то есть результат устойчив к выбору $\alpha$ в этом диапазоне, но **калибровать всё равно
надо** (рамки 2 и 6). (2) Floor-уровень остаётся лексикографическим — при подушке ниже floor выбора нет (как в рамке 5).
(3) Выбор $q_3$ «по графику» уже вносит срок цели — это наполовину ε-правило рамки 5.

### 4.2. Теория перспектив и ментальный учёт — где они НЕ математика ядра

- **Теория перспектив в оптимизацию месяца не входит**: в наших 66 альтернативах ни одно направление не уменьшается
  (доли ≥ 0, подушка не расходуется), значит «потерь» относительно сегодня нет, и функция с λ > 1 совпадает с функцией
  выигрышей. Она становится значимой, только если разрешить **тратить подушку на долг** (рамка 1 это предлагает) — тогда
  λ ≈ 1,8–2,0 объясняет, почему человек откажется. Применение — формулировки и показ сценариев (тема 36, ИТОГ 1 п. 2–3, 6).
- **Ментальный учёт** = отдельные «конверты» под цели; его математическое воплощение — GBI (рамка 8). Цена разбиения
  по счетам — 12 б.п. (Das et al. 2010, тема 13) против цены ошибки в неприятии риска — поэтому конверты оправданы.
- **Ожидаемая полезность** по сценариям — это рамка 1/2 с вогнутой целевой функцией; для нашего ядра сводится к
  вогнутым $v_i$ плюс сценарии Монте-Карло, которые уже есть, но в решение сейчас не входят (Г40 № 27).

### 4.3. Таблица рамки

| Параметр | Оценка |
|---|---|
| **Что умеет лучше нашей** | Уменьшающаяся ценность каждого направления → разложение вместо «всё в одно» (10 % углов против 87 %); общая денежная шкала → совет зависит от ставки монотонно; теоретически корректные веса «за прирост шкалы» (MAVT, swing) вместо «важности» |
| **Чего не умеет** | Не решает, КАКАЯ вогнутость у человека ($\alpha$, $\rho$ — данных нет); не видит времени; при нарушении взаимной независимости предпочтений аддитивная форма неверна; теория перспектив описательна, а не нормативна — оптимизировать по ней совет нельзя |
| **Данные** | Все критерии в рублях/месяцах — **есть** в `ranked`; параметр вогнутости — **нет** (GPS по стране — ориентир, индивидуально — нет) |
| **Сложность соло** | Замена нормировки и $v_i$ поверх `ranked` (или в `ranking.py` при переходе в канон): **1–2 дня** с тестами; калибровка $\alpha$ и шкал policy search-ем — ещё 2–3 дня |
| **Объяснимость** | 🟢 «первые 10 000 ₽ в отпуск нужны, чтобы успеть к сроку; дальше выгоднее гасить МФО под 292 %» — объяснение по убывающей ценности понятнее весов профиля |
| **Закон** | 🟢 предмет прежний; 🟡 «функцию полезности» не называть «инвестиционным профилем» и не описывать в терминах доходности/риска убытков (тема 18, запрет № 7) |
| **Что взять кусочком** | (1) **глобальные шкалы в рублях/месяцах** вместо min-max внутри человека; (2) **вогнутые $v_i$** ($\sqrt{\cdot}$ как стартовая точка); (3) $q_3$ как «цель по графику» вместо $S_n$; (4) один долговой критерий вместо пары $\hat R$/$\hat D$ |
| **Какую проблему Г40 закрывает** | № 4/22 (угол) — **закрывает** (87 % → 10 %); нечувствительность к ставке — **закрывает** (0 % → 76 %, монотонно); № 12 (тождественные критерии) — **закрывает** (один долговой критерий в рублях); № 5 (вес без диапазона) — **закрывает** (глобальные шкалы, Monat); № 6 (срок цели) — **частично** (через $q_3$) |

### Скрипт рамки 4 (дословно)

**f4a.py** (запуск: `.venv/bin/python` проекта; импортирует `app.services.planning`, `app.core.ranking` только на чтение и `f5c.py` из скрэтчпада)

```python
"""G41 frame 4 (a): additive value function with (i) GLOBAL scales in money units instead of per-person min-max and
(ii) concave single-criterion value functions v(q) = q**alpha, on the canon's already enumerated alternatives.
Separates two effects: global scale -> rate sensitivity; concavity -> interior (non-corner) plans.
Criteria per alternative (floor-optimal level kept, as canon):
  q1 = annual interest avoided by this month's prepayment / monthly income    (0 .. few)
  q2 = cushion after plan, months of expenses, capped at L* = 6               (0 .. 6)
  q3 = goal on-track ratio: goal money / money needed per month (cap 1)        (0 .. 1)
Weights: canon profile weights (w_rt + w_dt for debt, w_lt, w_goals)."""
import sys, random
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
sys.path.insert(0, "/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/fe25aad2-149b-48bd-a8b2-c62cc04ce4a1/scratchpad/g41")
import app.core.ranking as ranking
from app.services.planning import run_planning
from f5c import portrait, top_floor, shares, corner, TODAY
from datetime import timedelta


def crit(a, inc, need):
    q1 = sum(p["paid_in"] * p["interest_rate"] for p in a["avalanche_detail"]["passed"]) / inc
    q2 = min(a["Lt_new"], 6.0)
    g = sum(a.get("goal_allocation", {}).values())
    q3 = min(1.0, g / need) if need > 0 else 0.0
    return q1, q2, q3


def pick(A, inc, need, prof, alpha):
    w = ranking.RISK_PROFILES[prof]
    wd, wl, wg = w["w_rt"] + w["w_dt"], w["w_lt"], w["w_goals"]
    def U(a):
        q1, q2, q3 = crit(a, inc, need)
        return wd * q1 ** alpha + wl * q2 ** alpha + wg * q3 ** alpha
    return max(A, key=U)


def need_of(goals):
    return sum(g["target_amount"] / max(1, (g["deadline"] - TODAY).days / 30) for g in goals)


def population(n=400, seed=909):
    rng = random.Random(seed)
    stats = {k: [0, 0] for k in ("canon", "lin-global", "sqrt-global", "pow0.3-global")}
    tot = 0; rs = 0
    for _ in range(n):
        inc, exp, obls, goals, bliq, p = portrait(rng)
        r = run_planning(inc, exp, obls, goals, bliq=bliq, r_bench=0.14, risk_tolerance=p, today=TODAY)
        if r["crisis_plan"] is not None or not r["ranked"]:
            continue
        A = top_floor(r)
        if len(A) < 2:
            continue
        need = need_of(goals)
        obls4 = [dict(o, interest_rate=o["interest_rate"] * 4) for o in obls]
        r4 = run_planning(inc, exp, obls4, goals, bliq=bliq, r_bench=0.14, risk_tolerance=p, today=TODAY)
        if r4["crisis_plan"] is not None or not r4["ranked"]:
            continue
        A4 = top_floor(r4); tot += 1
        picks = {"canon": (r["best"], r4["best"])}
        for name, al in (("lin-global", 1.0), ("sqrt-global", 0.5), ("pow0.3-global", 0.3)):
            picks[name] = (pick(A, inc, need, p, al), pick(A4, inc, need, p, al))
        for k, (a, a4) in picks.items():
            stats[k][0] += corner(a); stats[k][1] += a["id"] != a4["id"]
    print(f"POPULATION seed {seed}: portraits {tot} (floor level with >=2 alternatives, both rate variants non-crisis)")
    for k, (c, ch) in stats.items():
        print(f"  {k:<14} corner share {c/tot:6.1%}   choice changes when all rates x4: {ch/tot:6.1%}")


def example():
    for rates, bliq in (((0.35, 2.92), 60_000), ((0.15, 0.90), 60_000), ((0.35, 2.92), 20_000)):
        obls = [{"id": "cc", "name": "Кредитка", "amount": 120_000, "interest_rate": rates[0], "monthly_payment": 6_000},
                {"id": "mfo", "name": "МФО", "amount": 30_000, "interest_rate": rates[1], "monthly_payment": 9_000}]
        goals = [{"id": "vac", "name": "Отпуск", "target_amount": 80_000, "current_amount": 0, "deadline": TODAY + timedelta(days=243), "category": "emotional"}]
        r = run_planning(90_000, 55_000, obls, goals, bliq=bliq, r_bench=0.14, risk_tolerance=3, today=TODAY)
        A = top_floor(r); need = 10_000
        out = [f"canon {r['best']['id']} {tuple(round(x, 2) for x in shares(r['best']))}"]
        for al in (1.0, 0.5, 0.3):
            a = pick(A, 90_000, need, 3, al)
            out.append(f"alpha={al}: {a['id']} {tuple(round(x, 2) for x in shares(a))}")
        print(f"example rates {rates} cushion {bliq}: " + " | ".join(out))


if __name__ == "__main__":
    example()
    population()


def direction(n=400, seed=909):
    """when rates x4: does the debt share move UP (economically expected), stay, or DOWN (perverse)?"""
    rng = random.Random(seed); cnt = {al: [0, 0, 0] for al in (1.0, 0.5)}
    for _ in range(n):
        inc, exp, obls, goals, bliq, p = portrait(rng)
        r = run_planning(inc, exp, obls, goals, bliq=bliq, r_bench=0.14, risk_tolerance=p, today=TODAY)
        obls4 = [dict(o, interest_rate=o["interest_rate"] * 4) for o in obls]
        r4 = run_planning(inc, exp, obls4, goals, bliq=bliq, r_bench=0.14, risk_tolerance=p, today=TODAY)
        if r["crisis_plan"] is not None or r4["crisis_plan"] is not None or not r["ranked"] or not r4["ranked"]:
            continue
        A, A4 = top_floor(r), top_floor(r4)
        if len(A) < 2:
            continue
        need = need_of(goals)
        for al in cnt:
            d0 = shares(pick(A, inc, need, p, al))[0]; d4 = shares(pick(A4, inc, need, p, al))[0]
            cnt[al][0 if d4 > d0 + 1e-9 else (1 if abs(d4 - d0) <= 1e-9 else 2)] += 1
    for al, (up, same, down) in cnt.items():
        print(f"  alpha={al}: debt share UP {up}, SAME {same}, DOWN {down} (of {up + same + down})")


if __name__ == "__main__":
    print("direction of change when all rates x4:")
    direction()
```

**Вывод f4a.py:**
```
example rates (0.35, 2.92) cushion 60000: canon a1000 (1.0, 0.0, 0.0) | alpha=1.0: a505 (0.5, 0.0, 0.5) | alpha=0.5: a703 (0.7, 0.0, 0.3) | alpha=0.3: a703 (0.7, 0.0, 0.3)
example rates (0.15, 0.9) cushion 60000: canon a1000 (1.0, 0.0, 0.0) | alpha=1.0: a055 (0.0, 0.5, 0.5) | alpha=0.5: a505 (0.5, 0.0, 0.5) | alpha=0.3: a604 (0.6, 0.0, 0.4)
example rates (0.35, 2.92) cushion 20000: canon a0100 (0.0, 1.0, 0.0) | alpha=1.0: a0100 (0.0, 1.0, 0.0) | alpha=0.5: a0100 (0.0, 1.0, 0.0) | alpha=0.3: a0100 (0.0, 1.0, 0.0)
POPULATION seed 909: portraits 232 (floor level with >=2 alternatives, both rate variants non-crisis)
  canon          corner share  87.1%   choice changes when all rates x4:   0.0%
  lin-global     corner share  65.5%   choice changes when all rates x4:  31.9%
  sqrt-global    corner share  10.3%   choice changes when all rates x4:  76.3%
  pow0.3-global  corner share   7.3%   choice changes when all rates x4:  72.4%
direction of change when all rates x4:
  alpha=1.0: debt share UP 74, SAME 158, DOWN 0 (of 232)
  alpha=0.5: debt share UP 177, SAME 55, DOWN 0 (of 232)
```

---

## Рамка 6. Байесовские методы: уточнение параметров человека по его истории и поведению

### 6.0. Аналогия → суть

**Аналогия.** Врач не ставит диагноз по одному анализу: у него есть «априорное» знание (как обычно бывает у людей этого
возраста), и каждый новый анализ **сдвигает** оценку, а не заменяет её. Три месяца зарплаты без пропусков не доказывают,
что пропусков не бывает; один пустой месяц из шести не значит, что пустым будет каждый шестой.

**Суть.** Параметр человека $\theta$ (вероятность пустого месяца, разброс дохода, «какой у него профиль») имеет
**априорное распределение** $p(\theta)$ по популяции; наблюдения $D$ дают **апостериорное** $p(\theta\mid D)\propto p(D\mid\theta)\,p(\theta)$.
Для доли пустых месяцев удобна пара Бета–Биномиальное: априори $\text{Beta}(a,b)$ (среднее $a/(a+b)$, «вес» $a+b$ псевдомесяцев),
после $n$ месяцев с $k$ пустыми — $\text{Beta}(a+k,\;b+n-k)$. Для предпочтений — модель выбора (логит):
вероятность выбрать вариант $j$ из показанных $\propto e^{U_j(\theta)/\tau}$, $\tau$ — «шум» выбора.

### 6.1. Литература — дословно

1. **Guo S., Sanner S. (2010), «Real-time Multiattribute Bayesian Preference Elicitation with Pairwise Comparison Queries»,
   AISTATS, PMLR 9:289–296.** `https://proceedings.mlr.press/v9/guo10b/guo10b.pdf`, `curl` HTTP 200, 984 035 байт, `pdftotext`, 17.09.2026. Дословно:
   > «Preference elicitation (PE) is an important component of interactive decision support systems that aim to make optimal
   > recommendations to users by actively querying their preferences. In this paper, we outline five principles important for PE in
   > real-world problems: (1) real-time, (2) multiattribute, (3) low cognitive load, (4) robust to noise, and (5) scalable.»
   > «Low cognitive load: Since the task of utility elicitation is cognitively difficult and error prone (Chajewska et al., 2000),
   > queries that are more difficult for users lead to higher noise and less certainty in the utility elicited. Thus, we focus on
   > pairwise comparison queries known to require low cognitive load for users (Conitzer, 2009).»
2. **Wang Y., Liu J., Kadziński M., Liao X. (2025), «Preference Construction: A Bayesian Interactive Preference Elicitation Framework
   Based on Monte Carlo Tree Search», arXiv:2503.15150** (реферат через Exa, 17.09.2026; PDF не открывался, 🟡):
   > «we apply the framework to Multiple Criteria Decision Aiding, with pairwise comparison as the preference information and an
   > additive value function as the preference model.»
   Это ровно наша форма (аддитивная функция ценности, рамка 4) — байесовское уточнение её весов по попарным сравнениям.
3. **Fisher W., Zhang Q., Song Y. (2024), «Approximate dynamic programming methods in Bayesian preference elicitation»,
   *Quality Engineering*, DOI 10.1080/08982112.2024.2440380** (реферат через Exa, 🟡):
   > «we find only a marginal improvement in D-efficiency through the use of non-greedy methods, suggesting that greedy methods are
   > sufficient for this problem.»
4. **Закон о рекомендательных технологиях** (уже в сырье темы 36, Г1): 149-ФЗ ст. 10.2-2 и приказы РКН № 149/150 от 06.10.2023
   распространяются на технологии «предоставления информации на основе сбора, систематизации и анализа сведений, относящихся к
   предпочтениям пользователей сети «Интернет»». Обучение профиля по поведению — прямой кандидат в этот контур (обязанность
   опубликовать правила применения); оценка частоты пустых месяцев по истории дохода — это анализ финансовых данных, а не
   «предпочтений» (вывод вахты, не цитата, юридически не проверен).

### 6.2. Проверка числом (`f6a.py`)

**(А) Вероятность пустого месяца → подушка по таблице Кэрролла (рамка 3, строка $\sigma_\theta=0{,}10$).**
Априори $\text{Beta}(1,49)$ — среднее 2 %, вес 50 псевдомесяцев (🔴 **допущение**: популяционная доля пустых месяцев для РФ не добыта).

| История человека | «Наивная» доля пустых | Апостериорное среднее (90 %-я верхняя) | Подушка по Кэрроллу, мес. дохода (осторожная) | Подушка по наивной оценке |
|---|---|---|---|---|
| Зарплатник, 3 мес., пустых нет | 0 % | 1,9 % (4,3 %) | 1,44 (1,99) | 0,89 |
| Зарплатник, 12 мес., пустых нет | 0 % | 1,6 % (3,7 %) | 1,33 (1,85) | 0,89 |
| 1 пустой из 6 | 16,7 % | 3,6 % (6,9 %) | 1,82 (2,54) | 4,66* |
| Фрилансер, 2 пустых из 12 | 16,7 % | 4,8 % (8,5 %) | 2,10 (2,89) | 4,66* |
| Фрилансер, 5 пустых из 24 | 20,8 % | 8,1 % (12,3 %) | 2,80 (3,72) | 5,56* |

\* линейная экстраполяция таблицы за $p_0$ = 5 % — только для порядка величины.

**Что это значит на примере.** Наш человек с 3 месяцами стабильной зарплаты: наивная оценка «пустых месяцев не бывает» дала бы
подушку 0,9 месяца (≈80 000 ₽), байесовская — 1,44 (≈130 000 ₽), потому что три месяца — это мало, чтобы исключить риск.
А один случайный пустой месяц из шести не раздувает подушку до 4,7 месяцев — только до 1,8. Байес **гасит шум короткой истории
в обе стороны** — именно то, чего не хватает SES/Holt на 3–8 точках (Г40 № 18) и CV без нулевых месяцев (Г40 № 9).

**(Б) Узнать профиль человека по его выбору.** Каждый месяц показываем 3 компромисса с фронта Парето, человек выбирает
(логит-модель, $\tau$ — шум). Сколько месяцев до апостериорной вероятности истинного профиля ≥ 0,8 (400 симуляций):

| Истинный профиль | $\tau$ = 0,01 (почти без шума): медиана / p90 | $\tau$ = 0,05 (шумный выбор) |
|---|---|---|
| 1 | 5 / 17 мес. | 21 / >36 мес. |
| 3 | 10 / 29 мес. | 18 / >36 мес. |
| 5 | 33 / >36 мес. | >36 / >36 мес. |

**Что это значит на примере.** Учиться по одному выбору в месяц **слишком медленно**: при реалистичном шуме профиль не
определяется и за три года. Поэтому байесовское уточнение предпочтений имеет смысл только **на входе** — 5–10 попарных
вопросов при онбординге («что вам важнее: закрыть МФО на месяц раньше или отпуск без сдвига?»), как у Guo & Sanner,
а не как обучение на поведении. Иллюстративные веса профилей в `f6a.py` — не канон; вывод касается порядка величины.

### 6.3. Таблица рамки

| Параметр | Оценка |
|---|---|
| **Что умеет лучше нашей** | Честно работает с короткой историей (3–12 мес.) — не принимает шум за закон; даёт не точку, а интервал (осторожная подушка по 90 %-й верхней оценке); уточняет параметры со временем без переписывания модели; попарные вопросы вместо «выберите профиль 1–5» |
| **Чего не умеет** | Нужен априор — популяционные доли для РФ **не добыты**; учиться предпочтениям по месячному поведению — годы (6.2 Б); не решает задачу выбора сама — только поставляет параметры другим рамкам |
| **Данные** | История дохода по месяцам — **есть** (ADR-015); популяционный априор — **нет** (кандидаты: ОДПФ, RLMS — тема 34, правовой вопрос RLMS снят Д9.3); ответы на попарные вопросы — **нет**, нужен экран онбординга |
| **Сложность соло** | Бета–Биномиальное и нормальное сопряжённые обновления — **часы**, без библиотек; байесовский опросник на 5–10 вопросов с логит-моделью — 3–5 дней с интерфейсом |
| **Объяснимость** | 🟢 «за 3 месяца без пропусков мы ещё не уверены, что пропусков не бывает — поэтому подушка чуть больше; через год станет точнее» |
| **Закон** | 🟢 параметры дохода — анализ собственных финансовых данных (152-ФЗ — согласие уже нужно); 🟡 обучение предпочтениям по поведению — кандидат в «рекомендательные технологии» (149-ФЗ ст. 10.2-2, приказы РКН № 149/150, тема 36 Г1); 🟡 с обучением по логам — система ИИ по AI Act ст. 3(1) (тема 37) |
| **Что взять кусочком** | (1) **байесовская оценка доли пустых месяцев и разброса дохода** с популяционным априором → вход в floor (рамка 3); (2) осторожная граница (90 %) для новых пользователей; (3) онбординг из попарных сравнений компромиссов вместо выбора профиля по анкете |
| **Какую проблему Г40 закрывает** | № 9 (CV без нулевых месяцев) — **закрывает** (пустые месяцы — отдельный параметр с априором); № 18 (Holt на 3–8 точках выдумывает тренд) — **закрывает методически** (сжатие к априору); № 28 (веса профилей без опоры) — **частично** (веса из ответов человека, а не экспертов); углы, ставка, тождественные критерии — **не касается** |

### Скрипт рамки 6 (дословно)

**f6a.py** (запуск: `.venv/bin/python` проекта, стандартная библиотека)

```python
"""G41 frame 6 (a): Bayesian updating of a person's parameters from their own history / behaviour.
(A) income risk: probability of a zero-income month p0 ~ Beta prior (population), updated by observed months;
    posterior mean + 90% credible upper bound -> cushion target via the Carroll table of f3a.py (sig_theta = 0.10 row).
(B) preference: which of 5 canon profiles (or which concavity alpha) the person has, learned from choices among
    3 Pareto representatives shown each month; choice model = logit on the f4a-style utility with temperature tau.
    How many monthly choices until the posterior on the true profile exceeds 0.8?"""
import math, random

# ---------- (A) Beta-Binomial for p0 ----------
CARROLL_ROW = {0.005: 0.89, 0.02: 1.48, 0.05: 2.13}   # f3a.py output, sig_theta = 0.10, months of permanent income


def carroll_floor(p0):
    xs = sorted(CARROLL_ROW); ys = [CARROLL_ROW[x] for x in xs]
    if p0 <= xs[0]:
        return ys[0]
    if p0 >= xs[-1]:
        return ys[-1] + (p0 - xs[-1]) * (ys[-1] - ys[-2]) / (xs[-1] - xs[-2])
    for (x0, y0), (x1, y1) in zip(zip(xs, ys), zip(xs[1:], ys[1:])):
        if x0 <= p0 <= x1:
            return y0 + (p0 - x0) * (y1 - y0) / (x1 - x0)


def beta_quantile(a, b, q, n=4000):
    """numerical quantile of Beta(a,b) via grid integration (no scipy)"""
    xs = [(i + 0.5) / n for i in range(n)]
    lg = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    dens = [math.exp(lg + (a - 1) * math.log(x) + (b - 1) * math.log(1 - x)) for x in xs]
    s = 0.0; tot = sum(dens)
    for x, d in zip(xs, dens):
        s += d
        if s / tot >= q:
            return x
    return 1.0


def part_a():
    a0, b0 = 1.0, 49.0   # prior mean 2 %, weight of 50 pseudo-months (ASSUMPTION: population share unknown for RF)
    print("(A) prior Beta(1,49): mean p0 = 2.0 %  -> Carroll cushion", round(carroll_floor(0.02), 2), "months of income")
    for months, zeros, who in ((3, 0, "salaried, 3 months of history"), (12, 0, "salaried, 12 months"),
                               (6, 1, "one empty month in 6"), (12, 2, "freelancer, 2 empty months in 12"),
                               (24, 5, "freelancer, 5 empty of 24")):
        a, b = a0 + zeros, b0 + months - zeros
        mean = a / (a + b); hi = beta_quantile(a, b, 0.9)
        naive = zeros / months
        print(f"   {who:<34}: naive {naive:5.1%} -> posterior mean {mean:5.1%} (90% upper {hi:5.1%}); cushion {carroll_floor(mean):.2f} mo (cautious {carroll_floor(hi):.2f}); naive-estimate cushion {carroll_floor(naive):.2f}")


# ---------- (B) preference learning ----------
REPS = [(0.0, 1.0, 0.0), (0.1, 0.4, 0.5), (0.3, 0.4, 0.3), (0.5, 0.1, 0.4), (1.0, 0.0, 0.0), (0.7, 0.0, 0.3), (0.5, 0.0, 0.5)]
PROFILES = {1: (0.30, 0.40, 0.30), 2: (0.40, 0.30, 0.30), 3: (0.50, 0.30, 0.20), 4: (0.50, 0.20, 0.30), 5: (0.50, 0.10, 0.40)}  # (debt, cushion, goal) weights, illustrative


def util(split, w, rate_scale, alpha=0.5):
    d, r, g = split
    q = (d * rate_scale, 1.0 + r, min(1.0, g / 0.5))   # interest avoided ~ rate, cushion months, goal on-track
    return sum(wi * qi ** alpha for wi, qi in zip(w, q))


def part_b(tau=0.02, trials=400, seed=7):
    rng = random.Random(seed)
    print(f"(B) logit choice among 3 random Pareto representatives per month, temperature tau={tau}")
    for true in (1, 3, 5):
        needed = []
        for _ in range(trials):
            post = {k: 0.2 for k in PROFILES}
            for month in range(1, 37):
                opts = rng.sample(REPS, 3); rs = rng.uniform(0.2, 1.5)
                us = [util(o, PROFILES[true], rs) for o in opts]
                m = max(us); pr = [math.exp((u - m) / tau) for u in us]; s = sum(pr)
                c = rng.choices(range(3), weights=[p / s for p in pr])[0]
                for k in post:
                    uk = [util(o, PROFILES[k], rs) for o in opts]; mk = max(uk)
                    ek = [math.exp((u - mk) / tau) for u in uk]
                    post[k] *= ek[c] / sum(ek)
                z = sum(post.values()); post = {k: v / z for k, v in post.items()}
                if post[true] >= 0.8:
                    needed.append(month); break
            else:
                needed.append(99)
        needed.sort()
        ok = sum(1 for x in needed if x < 99)
        print(f"   true profile {true}: posterior >= 0.8 reached in {ok}/{trials} runs within 36 months; median months {needed[len(needed)//2]}, p90 {needed[int(.9*(len(needed)-1))]}")


if __name__ == "__main__":
    part_a()
    for tau in (0.01, 0.05):
        part_b(tau=tau)
```

**Вывод f6a.py:**
```
(A) prior Beta(1,49): mean p0 = 2.0 %  -> Carroll cushion 1.48 months of income
   salaried, 3 months of history     : naive  0.0% -> posterior mean  1.9% (90% upper  4.3%); cushion 1.44 mo (cautious 1.99); naive-estimate cushion 0.89
   salaried, 12 months               : naive  0.0% -> posterior mean  1.6% (90% upper  3.7%); cushion 1.33 mo (cautious 1.85); naive-estimate cushion 0.89
   one empty month in 6              : naive 16.7% -> posterior mean  3.6% (90% upper  6.9%); cushion 1.82 mo (cautious 2.54); naive-estimate cushion 4.66
   freelancer, 2 empty months in 12  : naive 16.7% -> posterior mean  4.8% (90% upper  8.5%); cushion 2.10 mo (cautious 2.89); naive-estimate cushion 4.66
   freelancer, 5 empty of 24         : naive 20.8% -> posterior mean  8.1% (90% upper 12.3%); cushion 2.80 mo (cautious 3.72); naive-estimate cushion 5.56
(B) logit choice among 3 random Pareto representatives per month, temperature tau=0.01
   true profile 1: posterior >= 0.8 reached in 395/400 runs within 36 months; median months 5, p90 17
   true profile 3: posterior >= 0.8 reached in 383/400 runs within 36 months; median months 10, p90 29
   true profile 5: posterior >= 0.8 reached in 236/400 runs within 36 months; median months 33, p90 99
(B) logit choice among 3 random Pareto representatives per month, temperature tau=0.05
   true profile 1: posterior >= 0.8 reached in 294/400 runs within 36 months; median months 21, p90 99
   true profile 3: posterior >= 0.8 reached in 315/400 runs within 36 months; median months 18, p90 99
   true profile 5: posterior >= 0.8 reached in 131/400 runs within 36 months; median months 99, p90 99
```

---

## Рамка 7. Бандиты и обучение с подкреплением: где уместно и где опасно

> База: тема 9 (`raw/recsys_partial_results_2026-09-08.md`) — LinUCB, Thompson sampling, Netflix (малое пространство действий),
> Chaney et al. 2018 (confounding «homogenizes user behavior without increasing utility»), «Impatient Bandits» (задержка 2 мес.);
> тема 37 (`raw/causal_effect_measurement_2026-09-10.md`) — Bottou et al.: «Leveraging the problem structure seems more important in
> practice than perfecting an otherwise sound exploration strategy»; AI Act: детерминированное ядро вне определения системы ИИ,
> обучение политики по логам — внутри; темы 13/Г-хвосты — Alaluf et al. 2024 (arXiv:2403.06011, policy gradient на нашей же
> постановке «долг + цели») и Das et al. 2026 (JFDS, MetaRL для GBWM).

### 7.0. Аналогия → суть

**Аналогия.** Бандит — это новый повар, который учится готовить, пробуя блюда на посетителях: иногда нарочно подаёт
непроверенное блюдо, чтобы узнать, понравится ли. В кафе это нормально — невкусный суп забудется к вечеру. В финансовом совете
«непроверенное блюдо» — это план, из-за которого человек через год оказался в просрочке, а узнаём мы об этом **через год**.

**Суть.** *Контекстный бандит*: на каждом шаге по контексту $x$ (портрет человека) выбирается действие $a$ (план), наблюдается
награда $r$, политика обновляется; компромисс «исследовать/использовать». *RL*: то же, но действие меняет будущее состояние
(это MDP рамки 2), и политика учится по траекториям. Оба требуют **много наград** и **быстрых наград**.

### 7.1. Литература — дословно (новое к базе)

1. **Thomas P. S., Castro da Silva B., Barto A. G., Giguere S., Brun Y., Brunskill E. (2019), «Preventing undesirable behavior of
   intelligent machines», *Science* 366(6468), DOI 10.1126/science.aag3311.** Реферат — OpenAlex `works/doi:…` HTTP 200, 17.09.2026
   (полный текст за пейволлом, `oa_url: None`):
   > «Ensuring that they do not exhibit undesirable behavior-that they do not, for example, cause harm to humans-is therefore a pressing
   > problem. We propose a general and flexible framework for designing machine learning algorithms. This framework simplifies the
   > problem of specifying and regulating undesirable behavior. To show the viability of this framework, we used it to create machine
   > learning algorithms that precluded the dangerous behavior caused by standard machine learning algorithms in our experiments.»
   Для нас это единственный класс обучения, который вообще допустим в финсовете: **улучшение политики только с доказуемой
   (высокой вероятностью) непорчей относительно текущей**.
2. **Powell (2019), arXiv:1912.03513** (рамка 2): «Q-learning, as with all approximate dynamic programming algorithms, tend to work well
   only on a fairly small set of problems.»
3. **Das et al. (2026), JFDS 12:100186** — из сырья хвостов темы 13 (`gbi_tails_closed_2026-09-10.md` §1.1), дословно: «there are two
   decisions that must be optimized at each time step […] (1) Goal-taking […] and (2) Portfolio choice». RL в GBWM применяется там,
   где **модель мира известна и задана симулятором** (рыночные доходности), — то есть это RL как численный решатель DP,
   а не обучение на живых пользователях.

### 7.2. Проверка числом: сколько данных нужно учиться на исходах совета (`f7a.py`)

Исход — «просрочка 30+ дней в течение 12 месяцев», база 10 % (🔴 допущение для порядка величины), тест двух планов,
α = 0,05, мощность 0,8.

| Разница планов по доле просрочек | Пользователей на вариант | Месяцев до первого ответа при притоке 500 / 2 000 / 10 000 новых в месяц | «Лишних» просрочек у получивших худший план |
|---|---|---|---|
| 1 п.п. | 13 493 | 66 / 26 / 15 | ~135 |
| 2 п.п. | 3 211 | 25 / 16 / 13 | ~64 |
| 5 п.п. | 432 | 14 / 13 / 13 | ~22 |

**Что это значит на примере.** Чтобы бандит узнал, что «сначала МФО, потом подушка» лучше «сначала подушка», стартапу с 2 000 новых
пользователей в месяц нужно **16–26 месяцев** — и за это время несколько десятков человек **намеренно** получат худший план.
Для одного человека учиться нечему: одно решение в месяц, награда через год, за 3 года — не больше 24 сильно связанных наград.

### 7.3. Где уместно, где опасно

| Уместно | Опасно / недопустимо |
|---|---|
| Порядок и форма показа **равноправных** компромиссов с фронта (рамка 5): что человек открывает, принимает — награда быстрая (дни), вреда нет | Выбор **самого плана** распределения денег по наградам «через год» — медленно и с намеренным вредом при исследовании |
| RL/ADP **как решатель** на симуляторе (Das et al.; рамка 2) — офлайн, без людей | Обучение на логах собственных рекомендаций без рандомизации — confounding (Chaney et al.), политика учится на своих же ошибках |
| Безопасное улучшение политики (Thomas et al. 2019) — только если новая политика доказуемо не хуже текущей на логах | Награда «вовлечённость/удержание» вместо финансового исхода — оптимизирует не то (тема 9) |
| Напоминания и тексты (когда показать, как сформулировать) | Любое исследование, которое приводит к рекомендации «не платить» (рамка 1 показала, что деньги-только цель к этому склонна) |

### 7.4. Таблица рамки

| Параметр | Оценка |
|---|---|
| **Что умеет лучше нашей** | Учится на реальных исходах, а не на экспертном согласии; подстраивает показ под человека; RL как решатель справляется с большой размерностью, где DP невычислимо |
| **Чего не умеет** | Быстро учиться на наградах с задержкой в год; объяснять решение; гарантировать отсутствие вреда (кроме класса Seldonian); работать без большого числа пользователей |
| **Данные** | Исходы советов (просрочки, достижение целей через 6–12 мес.) — **нет и не будет до запуска + год**; логи показа — появятся после запуска |
| **Сложность соло** | Бандит для порядка показа (Thompson sampling, `space_bandits`/свой код) — 2–3 дня + логирование вероятностей (тема 37); RL-решатель на симуляторе — недели; безопасное улучшение политики — исследовательский проект |
| **Объяснимость** | 🔴 политика — чёрный ящик (оценка темы 13 по Alaluf et al.: «политика нейросети, вклад цели невосстановим» — формулировка вахты, не цитата статьи); 🟢 для порядка показа объяснять нечего |
| **Закон** | 🔴 обучение по логам → система ИИ по AI Act ст. 3(1) (тема 37) и «рекомендательные технологии» 149-ФЗ ст. 10.2-2 (тема 36 Г1); намеренное ухудшение совета части пользователей — риск по ЗоЗПП и 22-МР; 🟡 детерминированное ядро этого не несёт |
| **Что взять кусочком** | (1) **ничего в ядро распределения**; (2) бандит только на **порядок/форму показа** 3–5 компромиссов после запуска; (3) логировать показанные варианты и вероятности уже сейчас — это дешёвая подготовка к офлайн-оценке (тема 37) |
| **Какую проблему Г40 закрывает** | Ни одну из проблем ядра; косвенно № 28 (параметры без опоры) — **в перспективе года после запуска**, и только через офлайн-оценку, а не через исследование на людях |

### Скрипт рамки 7 (дословно)

**f7a.py**

```python
"""G41 frame 7 (a): how much data a bandit/A-B needs when the reward is a 12-month outcome of financial advice.
Two-proportion test, alpha=0.05 two-sided, power 0.8: n per arm = (z_a + z_b)^2 * (p1 q1 + p2 q2) / delta^2.
Outcome example: share of users with a 30+ day delinquency within 12 months (base 10 %, ASSUMPTION)."""
import math
Z_A, Z_B = 1.959964, 0.841621
print("base 10 %: delta (p.p.) -> users per arm; months until the first answer with a cohort of N new users per month (reward delay 12 months)")
for delta in (0.01, 0.02, 0.05):
    p1, p2 = 0.10, 0.10 - delta
    n = math.ceil((Z_A + Z_B) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / delta ** 2)
    row = []
    for N in (500, 2_000, 10_000):
        months_to_fill = math.ceil(2 * n / N)
        row.append(f"N={N}: {months_to_fill + 12} mo")
    print(f"  delta {delta*100:.0f} p.p.: {n:>6} per arm (x2 = {2*n}); " + ", ".join(row))
print("exploration cost: users deliberately given the (a priori) worse plan = n per arm; harm if the worse arm is worse by delta:")
for delta in (0.01, 0.02, 0.05):
    p1, p2 = 0.10, 0.10 - delta
    n = math.ceil((Z_A + Z_B) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / delta ** 2)
    print(f"  delta {delta*100:.0f} p.p.: extra delinquencies caused ~ {round(n * delta)}")
print("per-user learning: 1 decision/month, reward after 12 months, horizon 36 months -> at most", 36 - 12, "delayed rewards per user, all autocorrelated")
```

**Вывод f7a.py:**
```
base 10 %: delta (p.p.) -> users per arm; months until the first answer with a cohort of N new users per month (reward delay 12 months)
  delta 1 p.p.:  13493 per arm (x2 = 26986); N=500: 66 mo, N=2000: 26 mo, N=10000: 15 mo
  delta 2 p.p.:   3211 per arm (x2 = 6422); N=500: 25 mo, N=2000: 16 mo, N=10000: 13 mo
  delta 5 p.p.:    432 per arm (x2 = 864); N=500: 14 mo, N=2000: 13 mo, N=10000: 13 mo
exploration cost: users deliberately given the (a priori) worse plan = n per arm; harm if the worse arm is worse by delta:
  delta 1 p.p.: extra delinquencies caused ~ 135
  delta 2 p.p.: extra delinquencies caused ~ 64
  delta 5 p.p.: extra delinquencies caused ~ 22
per-user learning: 1 decision/month, reward after 12 months, horizon 36 months -> at most 24 delayed rewards per user, all autocorrelated
```

---

## Рамка 8. Goal-based investing и методы финансового планирования: что из темы 13 не взято в канон

> База (не переискиваем): `raw/goal_based_investing_lifecycle_2026-09-09.md` (§1.6 Брюнель, §2 дефект бинарной метрики,
> §3 приоритизация, §7 следствия) и `raw/gbi_tails_closed_2026-09-10.md` (Das et al. 2021/2022/2026, Bayraktar et al. 2025,
> Martellini/Milhau/Mulvey, Schwab Goal Tracker, Tharp 2021). Сверка с каноном — `grep` по `docs/math_model.md` (§11
> «Категории целей и взвешенная обеспеченность $S_n$»; слов «Brunel», «essential», «вероятность достижения», «Pareto» в каноне нет).

### 8.0. Аналогия → суть

**Аналогия.** Наш канон говорит о целях как об оценках в дневнике: «отпуск — важность 0,2, обеспечен на 25 %». Goal-based
подход говорит как пилот: «к посадке в мае мы должны прилететь **с вероятностью 90 %**, а если не долетим — **насколько**
не долетим». Важность цели — это не вес в сумме, а **требуемая надёжность**.

**Суть.** Для каждой цели $j$ задаются сумма $G_j$, срок $T_j$ и **требуемая вероятность** $\pi_j$ (Брюнель: «Needs» 90–95 %,
«Wants» 80–85 %, «Wishes» 65–75 %, «Dreams» 50–60 %); ограничение $P(W_{j,T_j}\ge G_j)\ge\pi_j$, где $W_{j,t}$ — накопленное на цель.
Цели делятся на **обязательные** (ограничения, floor — Martellini/Milhau/Mulvey) и **желательные** (оптимизируются).
При нехватке — **отказ или частичное выполнение** цели с меньшей полезностью (Das et al.) и отбор комбинаций по Парето.
Метрика провала — не только вероятность, но и **глубина недобора** $\mathbb E[(G_j-W_{j,T})^+]$ (Tharp 2021; Bayraktar et al. 2025).

### 8.1. Что есть в литературе и что из этого в каноне

| Элемент GBI / планирования | Источник (дословно — в файлах темы 13) | В каноне? |
|---|---|---|
| Важность цели = требуемая вероятность достижения (Needs 90–95 % … Dreams 50–60 %) | Brunel, Table 1 (тема 13 §1.6): «Brunel's Goal-Probability table can be used to classify investor goals into different probability values» | ❌ — важность = вес категории в $S_n$ (§11.1) |
| Обязательные цели — ограничение-floor, желательные — оптимизация | Martellini/Milhau/Mulvey (хвосты §2 (г)): floor, который «the strategy should respect at all times» | 🟡 только для подушки (лексикографический floor); цели со сроком — нет (Г40 № 6) |
| Разный порог «идёт по плану» для разных целей | Schwab Goal Tracker (хвосты §3): savings >50 % / 25–50 % / <25 %; income 90–75 % / <75 % | ❌ |
| Глубина недобора, а не только факт | Tharp 2021: «‘probability of success/failure’ entirely misses the dimension of ‘magnitude of success/failure’» | 🟡 $S_n$ — доля покрытия (не бинарная), но без вероятности |
| Отказ от цели / частичное выполнение с меньшей полезностью | Das et al. 2026 §2.1: «Goal-taking: whether or not to pay the cost needed to fulfill a currently available goal» | ❌ |
| Отбор комбинаций целей по Парето (30 → 24 → k_max = 13) | Das et al. 2021/2022, Прил. E (хвосты §2 (а)) | ❌ (перебор 66 без Парето-фильтра — рамка 5) |
| Взвешенная сумма недоборов при непрерывном распределении | Bayraktar, Han, Zhang 2025, (2.15): `inf E[Σ w_k (G_k − θ_k)^+]` | 🟡 форма близка к SAW по целям, но без ожидания по сценариям |
| Буферный запас вместо Модильяни–Мертона как теоретическая опора | Дейтон о Carroll (тема 13 §4.3) | ❌ в тексте канона (рамка 3) |
| Разделение по ментальным счетам стоит 12 б.п. | Das, Markowitz, Scheid, Statman 2010 (тема 13 §5.1) | — (обоснование, не механика) |

### 8.2. Проверка числом: «требуемая вероятность» для отпуска (`f8a.py`)

Отпуск 80 000 ₽ через 8 месяцев; в каждый месяц с вероятностью $p_0$ дохода нет и взнос пропускается.

| Взнос в обычный месяц | $p_0$ = 2 % | $p_0$ = 5 % | $p_0$ = 10 % |
|---|---|---|---|
| 10 000 ₽ (ровно 80 000 / 8) | 85,1 % («Wants») | 66,3 % («Wishes») | 43,0 % (ниже «Dreams») |
| 11 429 ₽ (80 000 / 7 — запас на один пропуск) | 99,0 % | 94,3 % («Needs») | 81,3 % |
| 13 334 ₽ (запас на два пропуска) | 100 % | 99,4 % | 96,2 % |

**Что это значит на примере.** «Откладывайте 10 000 ₽ в месяц» при 5 % риске пустого месяца — это отпуск с вероятностью лишь 2/3.
Если человек отмечает отпуск как «очень хочу, не сдвигать» («Wants/Needs»), правильный взнос — **11 429 ₽**, и это ε-ограничение
рамки 5 с числом, выведенным из надёжности, а не из веса категории «emotional». Вероятность $p_0$ берётся из рамки 6.

### 8.3. Таблица рамки

| Параметр | Оценка |
|---|---|
| **Что умеет лучше нашей** | Кодирует важность цели понятной человеку надёжностью («90 % успеть»), а не весом; делит цели на обязательные (ограничения) и желательные; умеет отказаться от цели или выполнить частично; меряет глубину провала |
| **Чего не умеет** | Долги как объект стратегии (ставки, досрочка), ПДН, неразменный резерв — во всех семи прочитанных источниках отсутствуют (хвосты темы 13, «Что ещё держится», п. 1–3); годовой шаг и инвестируемый капитал вместо месячного потока; вероятности требуют модели дохода |
| **Данные** | Сумма и срок цели — **есть**; требуемая надёжность — **нет** (нужен вопрос при создании цели); риск пустого месяца — из рамки 6 |
| **Сложность соло** | Поле «насколько критично успеть» (4 класса Брюнеля) + расчёт взноса по биномиальной/Монте-Карло формуле: **1–2 дня**; частичное выполнение и отказ от целей с Парето-отбором — неделя (это уже рамка 5 + 1) |
| **Объяснимость** | 🟢 «чтобы успеть с вероятностью 90 %, нужно 11 429 ₽ в месяц, а не 10 000» — пожалуй, самая понятная форма из всех восьми рамок |
| **Закон** | 🟢 для целей-накоплений на собственные траты; 🔴 **не переносить из GBI выбор портфеля** («Portfolio choice» у Das et al.) — это называние класса активов и ожидаемой доходности, запреты № 2 и № 3 темы 18 |
| **Что взять кусочком** | (1) **класс надёжности цели** (Needs/Wants/Wishes/Dreams) вместо веса категории; (2) **взнос по требуемой вероятности** как ε-ограничение (рамка 5); (3) **метрика глубины недобора** рядом с $S_n$; (4) явный сценарий «сдвинуть или уменьшить цель» при нехватке (goal-taking) |
| **Какую проблему Г40 закрывает** | № 6 (срок цели получает 0 ₽) — **закрывает** (ограничение надёжности); № 7 (недолитые деньги целей молча уходят в подушку) — **закрывает методически** (недобор виден как отдельная метрика); № 28 (веса категорий без опоры) — **частично** (надёжность спрашивается у человека); угол, ставка, тождественные критерии — **не касается** |

### Скрипт рамки 8 (дословно)

**f8a.py**

```python
"""G41 frame 8 (a): Brunel-style 'required probability' for a goal with a deadline.
Vacation 80 000 in 8 months; each month independently with prob p0 the person has no income and contributes 0.
Plan: contribute g per normal month. P(on time) = P(#normal months * g >= 80 000) = P(Bin(8, 1-p0) >= ceil(80000/g)).
Which monthly contribution reaches Brunel classes (Dreams 50-60, Wishes 65-75, Wants 80-85, Needs 90-95 %)?"""
import math


def p_on_time(g, p0, months=8, target=80_000):
    k_need = math.ceil(target / g - 1e-9)
    if k_need > months:
        return 0.0
    q = 1 - p0
    return sum(math.comb(months, k) * q ** k * p0 ** (months - k) for k in range(k_need, months + 1))


for p0 in (0.02, 0.05, 0.10):
    row = []
    for g in (10_000, 11_429, 13_334, 16_000):
        row.append(f"g={g}: {p_on_time(g, p0):.1%}")
    print(f"p0={p0:.0%}: " + " | ".join(row))
```

**Вывод f8a.py:**
```
p0=2%: g=10000: 85.1% | g=11429: 99.0% | g=13334: 100.0% | g=16000: 100.0%
p0=5%: g=10000: 66.3% | g=11429: 94.3% | g=13334: 99.4% | g=16000: 100.0%
p0=10%: g=10000: 43.0% | g=11429: 81.3% | g=13334: 96.2% | g=16000: 99.5%
```

---

## Сводная проверка пути (б): «оставить перебор, заменить правило выбора элементами других рамок» (`f9a.py`)

> 🔴 **Поправка к бухгалтерии `f5a.py` (v3).** При сборке сводной проверки найдено: канон §11.5 до перебора может закрыть
> близкую цель **из подушки** (`bliq_preallocation`), а бухгалтерия v2 это не учитывала. В `f5a.py` и `f9a.py` добавлены две строки
> (`pre = r.get("bliq_preallocation")…`). **Числа канона в рамке 5 не изменились** — у канона правило §11.5 на сквозном примере
> не сработало (вывод v3 ниже совпадает с v2 до рубля); у гибридов ниже — сработало, и учтено.

**Что сделано.** Альтернативы — те же 66 точек ядра `run_planning(...)["ranked"]`; бухгалтерия — `f5a.py` v3 (деньги сходятся:
«чистая позиция = 150 000 − проценты»). Заменено **только правило выбора** на месяц:
1. ε-подушка (рамки 3, 5): после плана подушка ≥ `c_min` месяцев расходов (вместо лексикографического «сначала весь floor»);
2. **токсичный долг первым** (рамка 2, параметр $\tau$ = 100 % из policy search), пока цель ещё успевается в оставшиеся месяцы;
3. ε-цель (рамки 5, 8): на цель не меньше нужного в месяц темпа;
4. среди оставшихся — вогнутая ценность на глобальных шкалах $\sqrt{\cdot}$ (рамка 4), веса профиля 3.

| План на 8 месяцев (сквозной пример) | Проценты | Отпуск к сроку | Подушка в конце | Долг в конце |
|---|---|---|---|---|
| Канон, профиль 3 | 37 303 ₽ | 2 748 ₽ | 109 950 ₽ | 0 |
| Гибрид без «токсичного первым», `c_min` 0,5 мес. | 38 139 ₽ | **80 000 ₽** | 35 401 ₽ | 3 539 ₽ |
| **Гибрид + токсичный первым, `c_min` 0,5 мес.** | **29 173 ₽** | **80 000 ₽** | 40 827 ₽ | **0** |
| Гибрид + токсичный первым, `c_min` 1 мес. | 41 782 ₽ | 80 000 ₽ | 43 286 ₽ | 15 068 ₽ |
| MILP, отпуск 80 000, подушка ≥ 20 000 только в конце (`f5b.py`) | 21 824 ₽ | ≥ 80 000 ₽ | 20 000 ₽ | 0 |

**Что это значит.** Не трогая перебор и Avalanche, одна замена правила выбора на сквозном примере даёт **−8 130 ₽ процентов и отпуск
в срок** вместо 2 748 ₽ — ценой подушки 0,74 месяца вместо двух. Остаток до MILP-оптимума (~7 400 ₽) — цена того, что
правило видит один месяц. И важная находка по ходу: **ε-цель «ровным темпом каждый месяц» без правила токсичного долга хуже
канона по процентам** (38 139 ₽) — ровный темп копит на отпуск, пока МФО под 292 % растёт. Порядок «сначала МФО, потом догнать
цель» — это знание о времени, которое однопериодная надстройка без рамки 1–2 не получает. `c_min` = 1 месяц снова портит
результат (41 782 ₽) — размер floor решает больше, чем способ свёртки.

### Скрипт сводной проверки (дословно, v3)

**f9a.py**

```python
"""[v3 17.09.2026: bliq_preallocation (canon §11.5) now applied to the ledger] G41 synthesis check: path (b) 'keep the enumeration, add elements of other frames' on the running example, 8 months,
same money-conserving ledger as f5a.py, alternatives come from the canon core (run_planning(...)['ranked'], all 66),
only the SELECTION rule is replaced:
  1) epsilon-floor (frames 3/5): cushion after plan >= c_min months of expenses, if any alternative achieves it
     (instead of the lexicographic 'fill the floor first');
  2) epsilon-goal (frames 5/8): goal money >= required per month * reliability buffer, if achievable;
  3) among the rest: additive value on global scales with concave v = sqrt (frame 4), canon profile-3 weights.
Compared with canon (f5a) and the 8-month MILP (f5b)."""
import sys
from datetime import datetime, timedelta
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
import app.core.ranking as ranking
from app.services.planning import run_planning
T0 = datetime(2026, 9, 17)
INC, EXP = 90_000, 55_000
DEADLINE_M = 8


def select(ranked, bliq, vac, month, c_min, buffer, prof=3, tau=None, obls=None):
    w = ranking.RISK_PROFILES[prof]; wd, wl, wg = w["w_rt"] + w["w_dt"], w["w_lt"], w["w_goals"]
    left = max(0.0, 80_000 - vac); months_left = max(1, DEADLINE_M - month)
    need = min(left, left / months_left * buffer) if left > 0 else 0.0
    def goal_money(a):
        return sum(a.get("goal_allocation", {}).values())
    def cushion_after(a):
        return (bliq + a["x_reserve_effective"]) / EXP
    pool = list(ranked)
    f1 = [a for a in pool if cushion_after(a) >= c_min - 1e-9]
    if f1:
        pool = f1
    else:
        best_c = max(cushion_after(a) for a in pool); pool = [a for a in pool if cushion_after(a) >= best_c - 1e-9]
    toxic_alive = tau is not None and any(o["interest_rate"] > tau and o["amount"] > 0.5 for o in (obls or []))
    if toxic_alive:
        # toxic-first (frame 2 policy search): postpone the goal pace while it stays feasible later
        pay_after = sum(o["monthly_payment"] for o in obls if o["interest_rate"] <= tau)
        if months_left > 1 and left / (months_left - 1) <= INC - EXP - pay_after:
            best_d = max(a["x_obl_effective"] for a in pool)
            return max([a for a in pool if a["x_obl_effective"] >= best_d - 1], key=lambda a: a["x_reserve_effective"])
    if need > 0:
        f2 = [a for a in pool if goal_money(a) >= need - 1]
        if f2:
            pool = f2
        else:
            best_g = max(goal_money(a) for a in pool); pool = [a for a in pool if goal_money(a) >= best_g - 1]
    def U(a):
        q1 = sum(p["paid_in"] * p["interest_rate"] for p in a["avalanche_detail"]["passed"]) / INC
        q2 = min(cushion_after(a), 6.0)
        q3 = min(1.0, goal_money(a) / need) if need > 0 else 0.0
        return wd * q1 ** 0.5 + wl * q2 ** 0.5 + wg * q3 ** 0.5
    return max(pool, key=U)


def roll(c_min, buffer, months=8, tau=None):
    obls = [{"id": "cc", "name": "Кредитка", "amount": 120_000.0, "interest_rate": 0.35, "monthly_payment": 6_000.0},
            {"id": "mfo", "name": "МФО", "amount": 30_000.0, "interest_rate": 2.92, "monthly_payment": 9_000.0}]
    bliq, vac, interest, log = 20_000.0, 0.0, 0.0, []
    for m in range(months):
        today = T0 + timedelta(days=30 * m)
        goals = [{"id": "vac", "name": "Отпуск", "target_amount": 80_000, "current_amount": vac,
                  "deadline": T0 + timedelta(days=243), "category": "emotional"}] if vac < 80_000 - 1 else []
        r = run_planning(INC, EXP, obls, goals, bliq=bliq, r_bench=0.14, risk_tolerance=3, today=today)
        if r["crisis_plan"] is not None:
            log.append((m + 1, "CRISIS")); break
        b = select(r["ranked"], bliq, vac, m, c_min, buffer, tau=tau, obls=obls)
        xd, xr, xg = b["x_obl_effective"], b["x_reserve_effective"], sum(b.get("goal_allocation", {}).values())
        pre = r.get("bliq_preallocation") or {}   # v3: canon §11.5 closes near goals from the cushion BEFORE the lattice
        bliq -= pre.get("bliq_used", 0.0); vac += sum(c["amount"] for c in pre.get("closed_goals", []))
        bliq += xr; vac += xg
        new = []; before = {o["id"]: o for o in obls}
        for o in b["obligation_allocation"]:
            o0 = before[o["id"]]; rate = o["interest_rate"]
            i = o0["amount"] * rate / 12; interest += i
            amt2 = o["new_amount"] + i - o0["monthly_payment"]
            if amt2 <= 0.5:
                bliq += max(0.0, -amt2); continue
            new.append({"id": o["id"], "name": o["name"], "amount": amt2, "interest_rate": rate,
                        "monthly_payment": min(o["new_payment"], amt2 * (1 + rate / 12))})
        log.append((m + 1, round(xd), round(xr), round(xg)))
        obls = new
    debt = sum(o["amount"] for o in obls)
    return log, round(interest), round(bliq), round(vac), round(debt)


if __name__ == "__main__":
    print("reference canon (f5a, profile 3): interest 37 303, cushion 109 950, vacation 2 748, debt 0")
    print("reference MILP (f5b): cushion>=55 000 from month 2 -> interest 36 458, vacation 80 000; from month 3 -> 26 206")
    for c_min in (0.5, 1.0):
        for buffer in (1.0, 8 / 7):
            log, interest, bliq, vac, debt = roll(c_min, buffer)
            print(f"hybrid c_min={c_min} mo, goal buffer x{buffer:.3f}: interest {interest}, cushion {bliq}, vacation {vac}, debt left {debt}, net {bliq + vac - debt}")
            print("    months (debt, reserve, goal):", log)

    print("variant with toxic-first (tau = 100 %/yr) from policy search f2a.py:")
    for c_min in (0.5, 1.0):
        log, interest, bliq, vac, debt = roll(c_min, 1.0, tau=1.0)
        print(f"hybrid+toxic c_min={c_min} mo: interest {interest}, cushion {bliq}, vacation {vac}, debt left {debt}, net {bliq + vac - debt}")
        print("    months (debt, reserve, goal):", log)
```

**Вывод f9a.py:**
```
reference canon (f5a, profile 3): interest 37 303, cushion 109 950, vacation 2 748, debt 0
reference MILP (f5b): cushion>=55 000 from month 2 -> interest 36 458, vacation 80 000; from month 3 -> 26 206
hybrid c_min=0.5 mo, goal buffer x1.000: interest 38139, cushion 35401, vacation 80000, debt left 3539, net 111862
    months (debt, reserve, goal): [(1, 2000, 8000, 10000), (2, 10300, 0, 10300), (3, 11945, 0, 11945), (4, 14282, 2856, 11425), (5, 17847, 0, 11898), (6, 18435, 3073, 9218), (7, 25417, 6354, 0), (8, 23288, 9981, 0)]
hybrid c_min=0.5 mo, goal buffer x1.143: interest 42077, cushion 39334, vacation 80000, debt left 11412, net 107922
    months (debt, reserve, goal): [(1, 0, 8000, 12000), (2, 8000, 0, 12000), (3, 11272, 0, 11272), (4, 5309, 10618, 10618), (5, 17414, 0, 11609), (6, 20984, 0, 8993), (7, 28046, 3116, 0), (8, 22964, 9842, 0)]
hybrid c_min=1.0 mo, goal buffer x1.000: interest 50297, cushion 57460, vacation 80000, debt left 37757, net 99703
    months (debt, reserve, goal): [(1, 0, 20000, 0), (2, 0, 16000, 4000), (3, 6000, 0, 14000), (4, 8825, 0, 13237), (5, 7665, 5110, 12775), (6, 14544, 0, 14544), (7, 29905, 0, 0), (8, 15821, 15821, 0)]
hybrid c_min=1.0 mo, goal buffer x1.143: interest 51950, cushion 57453, vacation 80000, debt left 39403, net 98050
    months (debt, reserve, goal): [(1, 0, 20000, 0), (2, 0, 16000, 4000), (3, 4000, 0, 16000), (4, 6412, 0, 14962), (5, 9550, 0, 14325), (6, 14500, 0, 14500), (7, 29815, 0, 0), (8, 15772, 15772, 0)]
variant with toxic-first (tau = 100 %/yr) from policy search f2a.py:
hybrid+toxic c_min=0.5 mo: interest 29173, cushion 40827, vacation 80000, debt left 0, net 120827
    months (debt, reserve, goal): [(1, 12000, 8000, 0), (2, 23600, 0, 0), (3, 14686, 0, 14686), (4, 15070, 0, 15070), (5, 15475, 0, 15475), (6, 19084, 0, 12723), (7, 19740, 0, 13160), (8, 14304, 19777, 0)]
hybrid+toxic c_min=1.0 mo: interest 41782, cushion 43286, vacation 80000, debt left 15068, net 108218
    months (debt, reserve, goal): [(1, 0, 20000, 0), (2, 4000, 16000, 0), (3, 21272, 0, 0), (4, 11600, 0, 17400), (5, 11848, 0, 17772), (6, 15135, 0, 15135), (7, 15564, 0, 15564), (8, 32038, 0, 0)]
```

**Правка f5a.py v2 → v3 (две строки перед `bliq += xr; vac += xg`) и вывод v3:**
```python
1:"""[v3 17.09.2026: bliq_preallocation (canon §11.5) now applied to the ledger] G41 frame 5 (a) [v2: money-conserving state update]: running example through the canon core, month by month for 8 months, all 5 profiles.
26:        pre = r.get("bliq_preallocation") or {}   # v3: canon §11.5 closes near goals from the cushion BEFORE the lattice
27:        bliq -= pre.get("bliq_used", 0.0); vac += sum(c["amount"] for c in pre.get("closed_goals", []))
```
```
profile 1 | month:(debt,reserve,goal,id): [(1, 0, 20000, 0, 'a0100'), (2, 4000, 16000, 0, 'a280'), (3, 12763, 8509, 0, 'a640'), (4, 7715, 18002, 0, 'a370'), (5, 2903, 26130, 0, 'a190'), (6, 23354, 5838, 0, 'a820'), (7, 27455, 3051, 0, 'a910'), (8, 28896, 3211, 0, 'a910')]
   after 8 months: interest paid 44684  cushion 122297  vacation fund 0 of 80000  debt left 16981 ['Кредитка']  net position 105316  check 150000-interest = 105316
profile 2 | month:(debt,reserve,goal,id): [(1, 0, 20000, 0, 'a0100'), (2, 4000, 16000, 0, 'a280'), (3, 21272, 0, 0, 'a1000'), (4, 29000, 0, 0, 'a1000'), (5, 30550, 0, 0, 'a1000'), (6, 32237, 0, 0, 'a1000'), (7, 14301, 17048, 2748, 'a550'), (8, 0, 35000, 0, 'a0100')]
   after 8 months: interest paid 37303  cushion 109950  vacation fund 2748 of 80000  debt left 0 []  net position 112698  check 150000-interest = 112697
profile 3 | month:(debt,reserve,goal,id): [(1, 0, 20000, 0, 'a0100'), (2, 4000, 16000, 0, 'a280'), (3, 21272, 0, 0, 'a1000'), (4, 29000, 0, 0, 'a1000'), (5, 30550, 0, 0, 'a1000'), (6, 32237, 0, 0, 'a1000'), (7, 14301, 17048, 2748, 'a550'), (8, 0, 35000, 0, 'a0100')]
   after 8 months: interest paid 37303  cushion 109950  vacation fund 2748 of 80000  debt left 0 []  net position 112698  check 150000-interest = 112697
profile 4 | month:(debt,reserve,goal,id): [(1, 0, 20000, 0, 'a0100'), (2, 4000, 16000, 0, 'a280'), (3, 21272, 0, 0, 'a1000'), (4, 29000, 0, 0, 'a1000'), (5, 30550, 0, 0, 'a1000'), (6, 32237, 0, 0, 'a1000'), (7, 14301, 0, 19796, 'a505'), (8, 0, 35000, 0, 'a0100')]
   after 8 months: interest paid 37303  cushion 92901  vacation fund 19796 of 80000  debt left 0 []  net position 112697  check 150000-interest = 112697
profile 5 | month:(debt,reserve,goal,id): [(1, 0, 20000, 0, 'a0100'), (2, 4000, 16000, 0, 'a280'), (3, 21272, 0, 0, 'a1000'), (4, 29000, 0, 0, 'a1000'), (5, 30550, 0, 0, 'a1000'), (6, 32237, 0, 0, 'a1000'), (7, 14301, 0, 19796, 'a505'), (8, 0, 35000, 0, 'a0100')]
   after 8 months: interest paid 37303  cushion 92901  vacation fund 19796 of 80000  debt left 0 []  net position 112697  check 150000-interest = 112697
```

---

## ИТОГ Г41

**Процесс, честно.** Классификация — breadth-first (восемь рамок). Подагентов — **0** (итоги девяти прошлых тем по тем же рамкам
уже были у вахты; подагент начал бы с нуля). `WebSearch` — **0**. Exa — **5 поисков**, 0 фетчей. Остальное — `curl` (IIASA ×2,
katowice, arXiv ×1, NBER, DTU Orbit, RePEc, PMLR ×2, doi.org), `r.jina.ai` ×1 (INFORMS, после 403), OpenAlex ×6 (два запроса по неверным DOI вернули не те работы — отброшены), Crossref ×2,
Semantic Scholar ×4, Unpaywall ×1 (адрес `research@example.org`; плюс замер канала в шапке). Скриптов — 11 (`f1a`, `f2a`, `f3a`, `f4a`, `f5a` v3, `f5b`, `f5c`,
`f6a`, `f7a`, `f8a`, `f9a`), все в `scratchpad/g41/`, приведены дословно. Код продукта, канон, `tests/` и формулировка новизны не менялись;
`app.core` только импортировался.

### 1. Сводная таблица восьми рамок

| # | Рамка | Главное, что умеет лучше | Главное, чего не умеет | Данные у нас | Цена соло | Объяснимость | Закон | Кусочек в ядро | Какие проблемы Г40 закрывает |
|---|---|---|---|---|---|---|---|---|---|
| 1 | MILP / стохастическое / робастное программирование | Время и точный оптимум: на примере −10 252 ₽ за подушку на месяц позже; первый ход «убить МФО» устойчив к потере дохода (VSS 5 750 ₽, цена робастности 0) | Деньги-только цель советует просрочку и «съесть подушку»; нужны вероятности шоков; дорогое объяснение | Долги, сроки — есть; шоки дохода РФ — нет | 1–2 дня (детерм.), неделя+ (сценарии) | 🟡 | 🔴 если допустить просрочку | **Офлайн-оракул** потерь канона; правило «токсичный первым» | Floor при токсичном долге (№ 2–3) числом; срок цели (№ 6); ставка — да; угол — нет |
| 2 | DP / MDP (таксономия Powell) | Язык политик; policy search: простое правило берёт 82 % выигрыша оптимума | Точное DP невычислимо; VFA/RL узки | Переходы — есть; шоки — нет | 2–3 дня (policy search) | 🟢 для правил | 🟢 без обучения на людях | Назвать ядро **CFA**; **калибровать пороги симуляцией** | № 14, № 28 (параметры без опоры) методически |
| 3 | Буферный запас, co-holding | **Выводит** подушку из риска дохода: 0,8–4 мес. дохода по волатильности и пустым месяцам | Нет целей и нескольких долгов; $\beta,\rho$ неизвестны; при ставке вкладов 8 % цели нет | История дохода — есть; $\beta,\rho$ — нет | 1–2 дня (таблица) | 🟢 | 🟢 | **floor = f(CV, доля пустых месяцев)** | № 9, петля Г31.4 для floor частично |
| 4 | Функции ценности / полезность / поведенческие | Вогнутость + общая шкала: углов 87 % → 10 %; выбор зависит от ставки (0 % → 76 %), монотонно | Параметр вогнутости без опоры; теория перспектив к ядру не применима (нет потерь в альтернативах) | Всё в `ranked`; $\alpha$ — нет | 1–2 дня | 🟢 | 🟢 (не звать «инвест-профилем») | **Глобальные шкалы, $\sqrt{\cdot}$, один долговой критерий** | № 4/22 угол, слепота к ставке, № 12 тождественные, № 5 вес без диапазона |
| 5 | Многоцелевая (Парето, ε, точка отсчёта, NIMBUS) | ASF с нейтральной точкой — 0 % углов на тех же 66 точках; ε даёт цену компромисса в рублях; желания в единицах человека | Ставка не влияет (размахи внутри человека); при лексикографическом floor выбирать не из чего | Всё есть | 4–8 ч (ядро), 1–2 дня (экран 3–5 вариантов) | 🟢 | 🟢 | **ASF/ε поверх `ranked`; 3–5 представителей фронта** | № 4/22, № 6, № 12, № 5 частично |
| 6 | Байесовские методы | Гасят шум короткой истории: 3 мес. без пропусков → подушка 1,44, а не 0,89 мес. | Нужен априор РФ; предпочтения по поведению — годы (медиана 10–33+ мес.) | История — есть; априор — нет | часы (сопряжённые), 3–5 дней (опросник) | 🟢 | 🟡 обучение предпочтениям — «рекомендательные технологии» | **Байес для доли пустых месяцев и CV**; попарные вопросы на онбординге | № 9, № 18, № 28 частично |
| 7 | Бандиты / RL | Учатся на исходах; RL как решатель на симуляторе | Награда через год: 3 211 человек на вариант и 16–26 мес. при 2 000 новых/мес.; намеренный вред при исследовании | Исходов нет до запуска + год | 2–3 дня (бандит показа) | 🔴 | 🔴 AI Act, 149-ФЗ 10.2-2 | **В ядро — ничего**; бандит только на порядок показа; логировать вероятности | Ни одну проблему ядра |
| 8 | Goal-based / планирование | Важность цели = требуемая надёжность; 10 000 ₽/мес. при 5 % пустых месяцев = отпуск лишь с вероятностью 66 %, 11 429 ₽ — 94 % | Долгов, ПДН, резерва нет ни в одном из 7 источников; годовой шаг | Сумма, срок — есть; надёжность — нужен вопрос | 1–2 дня | 🟢 (самая понятная) | 🟢; 🔴 не брать выбор портфеля | **Класс надёжности цели → взнос-ε; метрика глубины недобора** | № 6, № 7, № 28 частично |

### 2. 🔴 Рекомендация по развитию ядра — три пути

**(а) Оставить рамку и улучшить внутри неё** — закрыть шесть групп дефектов Г40 «до запуска», сетка 10 % → двухуровневая
(тема 40: ~242 точки ≈ точность 1 %), swing-веса по диапазонам.
- *Цена:* ~1–1,5 недели (дефекты Г40 — локальные правки, так записано в Г40).
- *Что даёт:* убирает ложные советы у обычных людей (окно месяца, кризис, CV, цели в подушку, экраны).
- *Чего не даёт (числом):* даже с глобальными шкалами линейная свёртка — **65,5 % углов**, ставка меняет выбор лишь в 31,9 % (`f4a.py`);
  лексикографический floor по-прежнему съедает первые месяцы при МФО под 292 %; срок цели не ограничение.
- *Риск:* низкий технически, **высокий содержательно** — рецензент и пользователь увидят «всё в одну корзину» и слепоту к ставке.

**(б) Дополнить элементами других рамок, не меняя перебор и Avalanche** — заменить **правило выбора** на месяц:
(1) критерии в рублях/месяцах на глобальных шкалах с вогнутой ценностью (рамка 4) — или ASF по нейтральной точке/желанию человека (рамка 5);
(2) floor — ε-ограничение с размером из таблицы Кэрролла и байесовской оценки пустых месяцев (рамки 3, 6);
(3) цель со сроком — ε-взнос по классу надёжности (рамка 8);
(4) «токсичный долг первым, пока цель успевается» с порогом, откалиброванным policy search-ем (рамка 2);
(5) MILP — офлайн-оракул для тестов (рамка 1), бандиты — только на порядок показа после запуска (рамка 7).
- *Цена:* ~2,5–3,5 недели соло: выбор поверх `ranked` 1–2 дня, ε-правила 2–4 дня, таблица Кэрролла + Байес 2–3 дня, policy search
  и MILP-оракул 4–6 дней, экран 3–5 компромиссов 2–3 дня; плюс канон/ADR/тесты по церемонии проекта.
- *Что даёт (числом, сквозной пример, 8 мес.):* **−8 130 ₽ процентов и отпуск 80 000 ₽ в срок вместо 2 748 ₽** (`f9a.py`);
  на популяции Г40 — углов 87 % → 10 %, совет зависит от ставки монотонно (`f4a.py`).
- *Риск:* (1) три новых параметра ($\alpha$, $\tau$, `c_min`) — без калибровки это та же петля Г31.4; `c_min` = 1 мес. вместо 0,5 уже
  портит результат (41 782 ₽); (2) меньшая подушка → хвостовой риск при потере дохода (в дереве `f1a` оправдано в ожидании, но
  пик экстренного долга в плохой ветке есть); (3) взаимодействие с кризисным режимом не проверено; (4) всё проверено на одном
  сквозном примере и одной популяции синтетики — не на портретах ADR-015.

**(в) Сменить рамку** — многопериодная стохастическая программа (DLA по Powell) с солвером в продукте.
- *Цена:* 4–8 недель: модель на 12 мес., генератор сценариев шоков (данных для РФ нет), HiGHS в контуре с таймаутами и фолбэком,
  подсистема объяснений (тема 40: X-MILP < 60 с/запрос, контрфактика — часы).
- *Что даёт сверх (б):* на примере ещё ~7 400 ₽ (29 173 → 21 824) при ослабленной подушке.
- *Риск:* **высокий** — деньги-только цель сама предлагает просрочку (`f1a.py`, строка «вред 0») и «съесть подушку», что противоречит
  поведенческим данным о co-holding; объяснимость, ради которой перебор выбран (тема 38), теряется; сценарии без данных — «точное решение
  неточной задачи» (тема 40, DeMiguel).

🔴 **Рекомендую путь (б), выполненный ПОСЛЕ правок «до запуска» из пути (а)**, и с MILP из пути (в) только как офлайн-оракулом.
Обоснование: (1) из четырёх проблем ядра Г40 (угол, ставка, тождественные критерии, недостижимые компромиссы) (а) не закрывает ни одну
полностью, (б) закрывает все четыре — числом на тех же 66 точках; (2) (б) забирает большую часть выигрыша (в) на примере
(8 130 из 15 479 ₽ разрыва канон–оптимум) без потери объяснимости и без солвера в продукте; (3) правило остаётся **политикой класса
CFA** (Powell) — законный, названный в литературе класс, что прямо помогает формулировке для магистерской из Г40 п. 9.
Решение за владельцем; канон этим файлом не меняется.

### 3. Что из этого закрывает конкретные проблемы Г40

| Проблема Г40 | Чем закрывается | Насколько (число) | Рамка |
|---|---|---|---|
| **Вырождение в «одну корзину»** (91 %; 85 % компромиссов недостижимы) | вогнутая ценность на глобальной шкале **или** ASF с нейтральной точкой отсчёта | углов 87,1 % → 10,3 % ($\sqrt{\cdot}$) / 0,0 % (ASF) на 232 портретах | 4, 5 |
| **Нечувствительность к ставке** (15 % = 90 %) | общая денежная шкала (сэкономленные ₽ / доход) + вогнутость; в многопериодной постановке — по построению | выбор меняется при ставках ×4: 0 % → 76,3 %, ни одного обратного сдвига; ASF/ε/Парето **не** лечат (0 %) | 4, 1 |
| **Тождественные критерии** ($\hat R\equiv1-\hat D$) | один долговой критерий в рублях сэкономленных процентов | тождество исчезает по построению | 4, 5 |
| **Недостижимые компромиссы** (фронт плоский) | ASF (лемма 2 Вежбицкого — необходимое условие и для невыпуклых) + показ 3–5 представителей фронта | нейтральный компромисс 40/40/20 вместо 100/0/0 на примере | 5 |
| Срок цели получает 0 ₽ (№ 6) | ε-взнос по классу надёжности | отпуск 2 748 → 80 000 ₽ (с правилом токсичного долга) | 8, 5, 1 |
| Floor «всё или ничего» при токсичном долге (№ 2–3) | ε-floor малого размера + «токсичный первым»; размер из Кэрролла/Байеса | −8 130 ₽ за 8 мес. на примере; в дереве шоков первый ход канона теряет 14–17 тыс. ₽ в ожидании | 1, 2, 3, 6 |
| CV без нулевых месяцев (№ 9); Holt на коротком ряду (№ 18) | доля пустых месяцев отдельным параметром с байесовским априором | 3 мес. без пропусков → подушка 1,44 вместо 0,89 мес.; 1 пустой из 6 → 1,82 вместо 4,66 | 6, 3 |
| Параметры без внешней опоры (№ 14, № 28) | policy search на симуляторе с MILP-оракулом вместо экспертного согласия | простое правило берёт 82 % выигрыша оптимума | 2, 1 |
| Вес без диапазона (№ 5) | глобальные шкалы (Monat 2009), веса «за прирост шкалы» (MAVT) | — (методически) | 4 |

**Противоречие между рамками, названное прямо.** Рамка 1 (стохастическая программа) советует **тратить подушку на МФО**, рамка 3
(Telyukova 2013; Druedahl & Jørgensen 2018) доказывает, что **держать подушку при дорогом долге рационально** до некоторого уровня.
Разрешение: рамка 1 предполагает экстренный кредит всегда доступным; рамка 3 — что банк закрывает кредит именно в беде. На примере
они сходятся на **малом** floor (~0,5 мес.: лучший `c` policy search и нижний край таблицы Кэрролла), а не на нуле и не на двух месяцах.

### 4. Вопросы для Г39 (как проверять выбранный путь)

1. **Оракул потерь.** На портретах ADR-015 и популяции Г40: разрыв в рублях за 12 мес. между (i) каноном, (ii) путём (б), (iii) MILP
   (`f5b.py` как основа) — медиана, p90, доля портретов, где (б) хуже канона. Порог приёмки (б) — «не хуже канона ни в одном портрете
   по просрочкам и срыву целей класса Needs».
2. **Метаморфные свойства нового правила** (Hypothesis): ставка ↑ → доля долга не ↓ (в `f4a` 0 нарушений — зафиксировать тестом);
   доход ↑ → план не хуже; срок цели ближе → взнос не ↓; класс надёжности выше → взнос не ↓; перестановка долгов/целей не меняет план.
3. **Доля угловых планов как регрессионная метрика** (сейчас 87 %, цель (б) ≤ 15 %) и **чувствительность к ставке** (сейчас 0 %).
4. **Калибровка $\alpha$, $\tau$, `c_min`** — policy search на симуляторе с шоками; проверить устойчивость: насколько меняется ожидаемая
   потеря при ±50 % каждого параметра (плоский ли максимум — как тема 40 проверяла для сетки).
5. **Хвостовой риск меньшей подушки** — в дереве с шоками (как `f1a.py`) доля сценариев с экстренным долгом и его пик; сравнить с каноном.
6. **Взаимодействие с кризисным режимом и §11.5** (разовое закрытие цели из подушки) — сквозные симуляции 12 мес., где месяц без дохода
   переводит ядро в кризис; в Г41 не проверено.
7. **Запрет просрочки как инвариант оракула** — MILP-оракул обязан иметь его ограничением; тест, что ни одно правило пути (б) не выдаёт
   план с пропуском минимального платежа.
8. **Априор для Байеса** — откуда (ОДПФ/RLMS, тема 34), и тест «новый пользователь с 3 месяцами истории получает осторожную подушку».
9. **Объяснимость** — для каждого совета (б) генерируется одна фраза-причина (какое ε-ограничение активно или какой критерий «самый
   отстающий» в ASF); тест на то, что причина совпадает с фактически активным ограничением.

### 5. ЗАДОЛЖЕННОСТЬ (не пройдено — с причиной и адресами)

**Литература, текст не открыт:**
1. Haimes, Lasdon, Wismer 1971 (ε-ограничения) — S2 `CLOSED`, Unpaywall `is_oa: false`, `has_repository_copy: false`.
2. Miettinen & Mäkelä 2006, EJOR (синхронный NIMBUS) — S2 `CLOSED`; использован открытый Miettinen 2005 (Katowice).
3. Birge 1982 (VSS) — только реквизиты Crossref; текст Springer не открывался.
4. Telyukova 2013 RES — полный текст: `escholarship.org/content/qt0ww2c04z/qt0ww2c04z.pdf` вернул HTTP 202, 0 байт (очередь генерации); использован реферат OpenAlex. Повторить позже тем же адресом.
5. Rasmussen, Madsen, Poulsen 2014 и Pedersen, Weissensteiner, Poulsen 2013 — только рефераты (DTU Orbit, RePEc); полные тексты Springer не пробовались (Unpaywall не запрашивался — не успел в этом батче).
6. Lewandowski & Grauer 1982 (IIASA) — фрагмент Exa; PDF `pure.iiasa.ac.at/id/eprint/1990` не скачивался.
7. Wang et al. 2025 (arXiv:2503.15150), Fisher et al. 2024 — рефераты Exa, PDF не открывались.
8. Thomas et al. 2019 (Science) — реферат OpenAlex, `oa_url: None`; авторская копия не искалась.
9. Moriggia, Consigli, Iaquinta (World Scientific) — аннотация RePEc через Exa.
10. Chajewska, Koller, Parr 2000 — только упоминание в Guo & Sanner; сам текст не искался.

**Вычисления, не сделанные:**
11. MILP-оракул на популяции портретов (сделан на одном сквозном примере) — нет распределения разрыва канон–оптимум.
12. VSS на портретах ADR-015 (сделан на одном примере с одним сценарием шока).
13. Путь (б) на популяции (сделан на одном примере) — главный пробел рекомендации, первым в Г39.
14. Калибровка модели Кэрролла на российских данных ($\beta$, $\rho$, популяционный $p_0$) — нет данных о помесячных шоках дохода РФ (та же задолженность Г40 № 10).
15. Policy search по **реальным** параметрам канона через `app.core` (в `f2a.py` — своя бухгалтерия и эмуляция канона).
16. Сквозной сценарий «месяц без дохода» через ядро (кризисный режим) — в `f5a`/`f9a` шоков нет.

**Право, не проверено:**
17. Подпадает ли байесовское уточнение предпочтений по поведению под 149-ФЗ ст. 10.2-2 — вывод вахты по тексту темы 36, без юридической проверки.
