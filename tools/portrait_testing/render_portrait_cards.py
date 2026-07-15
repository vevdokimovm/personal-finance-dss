"""Рендерер синтетических портретов FINPILOT в человекочитаемые карточки (СУХИЕ).

Числа берутся РОВНО из движкового генератора (tools/portrait_testing/generator.py).
Синтезируется только детерминированная «обёртка-персона»: демография, разбивка
доходов/расходов, банки/типы/сроки долгов, человеческие названия целей, сплит
ликвидности. Все разбивки сводятся точно к движковым тоталам.

ВАЖНО: карточка — это ТОЛЬКО входные данные портрета (как эталонные 6 кейсов).
Никаких вычисленных показателей (Rt/Lt/ПДН) и вердиктов модели: их считает эксперт,
иначе теряется объективность оценки.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Any

# --- импорт реального движкового генератора (числа = один-в-один) ---
# Работает и из корня репо (python -m ...), и standalone рядом с генератором.
try:
    from tools.portrait_testing.generator import PortraitGenerator  # запуск из корня репо
except ImportError:
    _here = Path(__file__).resolve().parent
    cands = [_here / "tools" / "portrait_testing", _here,
             _here / "proj" / "finpilot_v5_18_4_intl" / "tools" / "portrait_testing"]
    for cand in cands:
        if (cand / "generator.py").exists():
            sys.path.insert(0, str(cand))
            break
    from generator import PortraitGenerator  # noqa: E402

MONTHS = ["", "январь", "февраль", "март", "апрель", "май", "июнь",
          "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]

FIRST_M = ["Дмитрий", "Игорь", "Михаил", "Виктор", "Александр", "Сергей", "Андрей",
           "Алексей", "Николай", "Владимир", "Иван", "Павел", "Роман", "Максим",
           "Артём", "Денис", "Евгений", "Константин", "Олег", "Юрий", "Кирилл",
           "Егор", "Тимофей", "Станислав"]
FIRST_F = ["Анна", "Ольга", "Мария", "Елена", "Наталья", "Ирина", "Татьяна",
           "Светлана", "Юлия", "Екатерина", "Ксения", "Дарья", "Марина", "Виктория",
           "Полина", "Алина", "Вера", "Людмила", "Галина", "Оксана", "Надежда",
           "Валентина", "Анастасия", "София"]
SUR_M = ["Петров", "Соколов", "Кузнецов", "Соловьёв", "Лебедев", "Морозов", "Смирнов",
         "Волков", "Козлов", "Новиков", "Попов", "Васильев", "Зайцев", "Павлов",
         "Семёнов", "Голубев", "Виноградов", "Богданов", "Воробьёв", "Фёдоров",
         "Михайлов", "Беляев", "Тарасов", "Белов", "Комаров", "Орлов", "Киселёв",
         "Макаров", "Андреев", "Ковалёв"]
PATR_M = ["Александрович", "Сергеевич", "Иванович", "Петрович", "Николаевич",
          "Владимирович", "Андреевич", "Дмитриевич", "Викторович", "Степанович"]
PATR_F = ["Александровна", "Сергеевна", "Ивановна", "Петровна", "Николаевна",
          "Владимировна", "Андреевна", "Дмитриевна", "Викторовна", "Степановна"]

CITIES = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань",
          "Нижний Новгород", "Челябинск", "Самара", "Омск", "Ростов-на-Дону", "Уфа",
          "Красноярск", "Воронеж", "Пермь", "Волгоград", "Краснодар", "Тюмень",
          "Ижевск", "Тула", "Ярославль", "Иркутск", "Хабаровск", "Владивосток",
          "Калининград"]

BANKS = ["Сбер", "ВТБ", "Т-Банк", "Альфа-Банк", "Газпромбанк", "Совкомбанк",
         "Райффайзен", "Открытие", "Росбанк", "Почта Банк"]

PROF_BANDS = [
    (0, ["в поиске работы", "в декретном отпуске", "студент(ка) на подработке", "временно без дохода"]),
    (45_000, ["библиотекарь", "продавец-консультант", "оператор call-центра", "воспитатель",
              "почтальон", "лаборант", "кассир", "администратор"]),
    (80_000, ["учитель", "инженер-технолог", "бухгалтер", "медсестра/медбрат", "логист",
              "junior-разработчик", "мастер участка", "дизайнер"]),
    (130_000, ["опытный бухгалтер", "инженер-проектировщик", "middle-разработчик",
               "менеджер проектов", "врач в поликлинике", "маркетолог", "прораб"]),
    (200_000, ["senior-разработчик", "руководитель группы", "врач частной клиники",
               "финансовый аналитик", "начальник отдела", "архитектор ПО"]),
    (350_000, ["team lead", "руководитель направления", "хирург частной клиники",
               "senior product manager", "IT-консультант"]),
    (10 ** 12, ["технический директор", "собственник бизнеса", "engineering manager",
                "директор по разработке", "партнёр практики"]),
]

GOALS_SMALL = ["Отпуск у моря", "Новый ноутбук", "Ремонт кухни", "Смена телефона",
               "Курсы английского", "Велосипед", "Подарок родителям", "Зимняя резина",
               "Абонемент в зал", "Новая мебель"]
GOALS_MID = ["Подушка безопасности", "Автомобиль (доплата)", "Обучение / курсы",
             "Ремонт квартиры", "Свадьба", "Резерв на лечение", "Первый взнос (старт)",
             "Техника для дома", "Резерв на налоги"]
GOALS_LARGE = ["Первоначальный взнос на ипотеку", "Покупка автомобиля",
               "Инвест-квартира (взнос)", "Расширение бизнеса", "Образование детей",
               "Загородный дом", "Взнос на квартиру ребёнку"]

# нейтральные структурные метки (описывают ВХОД, не поведение модели)
KIND_LABEL = {
    "zero_income": ("Нулевой доход", "доход = 0"),
    "zero_expenses": ("Нулевые расходы", "расходы = 0"),
    "deficit_cf": ("Расходы выше дохода", "расходы превышают доход"),
    "overleveraged": ("Высокая долговая нагрузка", "платежи по кредитам — крупная доля дохода"),
    "cheap_debts_only": ("Только дешёвые кредиты", "все ставки по кредитам ниже рыночной"),
    "no_goals": ("Без целей", "нет целей накопления"),
    "funded_goal": ("Цель уже профинансирована", "накоплено ≥ целевой суммы"),
    "huge_bliq": ("Очень крупный резерв", "ликвидная подушка — десятки месяцев расходов"),
    "many_goals": ("Восемь целей", "восемь целей одновременно"),
    "plain": ("Типовой профиль", "без граничных особенностей"),
}


def fmt_money(x: float) -> str:
    return f"{int(round(x)):,}".replace(",", " ")


def fmt_pct(x: float) -> str:
    return f"{x * 100:.1f} %"


def years_word(age: int) -> str:
    if 11 <= age % 100 <= 14:
        return "лет"
    d = age % 10
    if d == 1:
        return "год"
    if d in (2, 3, 4):
        return "года"
    return "лет"


def persona_rng(index: int) -> random.Random:
    return random.Random((index + 1) * 2_654_435_761 % (2 ** 32))


def remaining_term_months(principal: float, annual_rate: float, payment: float) -> int | None:
    if payment <= 0:
        return None
    r = annual_rate / 12.0
    if r <= 1e-9:
        return max(1, math.ceil(principal / payment))
    if payment <= principal * r:
        return 600
    n = -math.log(1 - r * principal / payment) / math.log(1 + r)
    return max(1, min(600, math.ceil(n)))


def distribute(total: float, weights: list[tuple[str, float]]) -> list[tuple[str, int]]:
    total_i = int(round(total))
    if total_i <= 0 or not weights:
        return [(weights[0][0] if weights else "—", 0)]
    wsum = sum(w for _, w in weights)
    amounts = [(label, int(round(total_i * w / wsum))) for label, w in weights]
    diff = total_i - sum(a for _, a in amounts)
    if diff != 0:
        idx = max(range(len(amounts)), key=lambda i: amounts[i][1])
        amounts[idx] = (amounts[idx][0], amounts[idx][1] + diff)
    return amounts


def pick_profession(rng: random.Random, income: float) -> str:
    if income <= 0:
        return rng.choice(PROF_BANDS[0][1])
    for ceiling, options in PROF_BANDS[1:]:
        if income < ceiling:
            return rng.choice(options)
    return rng.choice(PROF_BANDS[-1][1])


def build_persona(p: dict[str, Any]) -> dict[str, Any]:
    rng = persona_rng(p["index"])
    female = rng.random() < 0.5
    first = rng.choice(FIRST_F if female else FIRST_M)
    sur = rng.choice(SUR_M)
    if female:
        sur = sur + "а"  # -ов/-ев/-ёв → -ова/-ева/-ёва
    income = p["income_total"]
    has_kids = False
    base_age = 22 + int(rng.random() * 41)
    if p["goals"] and len(p["goals"]) >= 5:
        base_age = max(base_age, 35)
    age = base_age
    patr = rng.choice(PATR_F if female else PATR_M) if age >= 45 else None
    prof = pick_profession(rng, income)
    city = rng.choice(CITIES)

    if age < 27:
        family = rng.choice(["не замужем, живёт одна" if female else "не женат, живёт один",
                             "не замужем, снимает комнату" if female else "не женат, снимает комнату"])
    elif age < 45:
        r = rng.random()
        if r < 0.4:
            family = "в браке, детей нет"
        elif r < 0.8:
            n = rng.randint(1, 2)
            family = f"в браке, {'ребёнок' if n == 1 else 'двое детей'}-школьник{'и' if n == 2 else ''}"
            has_kids = True
        else:
            family = rng.choice(["в разводе, ребёнок школьного возраста", "одинок(а)"])
            has_kids = "ребёнок" in family
    else:
        family = "в браке, взрослые дети, есть внуки" if rng.random() < 0.7 else "в браке, дети живут отдельно"

    renter = (age < 40 and rng.random() < 0.55) or family.startswith("в разводе")
    owner_mortgage = any(o["amount"] >= 2_000_000 and o["interest_rate"] <= 0.14 for o in p["obligations"])
    if owner_mortgage:
        renter = False

    signals = []
    if p["kind"] == "zero_income":
        signals.append("сейчас без источника дохода, живёт на накопления")
    elif p["kind"] == "deficit_cf":
        signals.append("текущие расходы и платежи превышают доход")
    elif p["kind"] == "overleveraged":
        signals.append("несколько кредитов, крупные ежемесячные платежи")
    elif p["kind"] == "huge_bliq":
        signals.append("крупный резерв на депозите, копил(а) годами")
    elif p["kind"] == "cheap_debts_only":
        signals.append("все кредиты — льготные, со ставкой ниже рыночной")
    elif p["kind"] == "many_goals":
        signals.append("много финансовых целей одновременно")
    elif p["kind"] == "funded_goal":
        signals.append("ключевая цель уже перевыполнена по накоплениям")
    if renter:
        signals.append("снимает жильё")
    elif owner_mortgage:
        signals.append("своя квартира в ипотеке")
    context = "; ".join(signals) if signals else "типовая финансовая ситуация без крайностей"

    return {"female": female, "first": first, "surname": sur, "patronymic": patr,
            "age": age, "profession": prof, "city": city, "family": family,
            "has_kids": has_kids, "renter": renter, "owner_mortgage": owner_mortgage,
            "context": context}


def income_sources(p: dict[str, Any], persona: dict[str, Any]) -> list[tuple[str, int]]:
    income = p["income_total"]
    if income <= 0:
        return [("Нет дохода (граничный кейс)", 0)]
    rng = persona_rng(p["index"] * 7 + 1)
    total_i = int(round(income))
    prof = persona["profession"]
    if any(k in prof for k in ("разработчик", "lead", "IT", "архитектор")):
        if rng.random() < 0.5 and total_i > 120_000:
            free = int(round(total_i * rng.uniform(0.1, 0.25)))
            return [("Зарплата (белая)", total_i - free), ("Фриланс (сторонние проекты)", free)]
    if persona["family"].startswith("в разводе") and rng.random() < 0.7:
        alim = int(round(total_i * rng.uniform(0.08, 0.18)))
        return [("Зарплата", total_i - alim), ("Алименты", alim)]
    if rng.random() < 0.25:
        bonus = int(round(total_i * rng.uniform(0.05, 0.15)))
        return [("Оклад", total_i - bonus), ("Премии / подработка", bonus)]
    return [("Зарплата (белая, стабильная)", total_i)]


def expense_breakdown(p: dict[str, Any], persona: dict[str, Any]) -> list[tuple[str, int]]:
    exp = p["expense_total"]
    if exp <= 0:
        return [("— (нулевые расходы, граничный кейс)", 0)]
    if persona["renter"]:
        weights = [("Аренда жилья", 0.38), ("Продукты", 0.22), ("Транспорт", 0.08),
                   ("Связь и интернет", 0.05), ("Здоровье", 0.05), ("Кафе и развлечения", 0.10),
                   ("Быт и хозяйство", 0.06), ("Прочее", 0.06)]
    else:
        weights = [("Продукты", 0.34), ("ЖКХ", 0.12), ("Транспорт", 0.10),
                   ("Связь и интернет", 0.04), ("Здоровье", 0.07), ("Кафе и развлечения", 0.13),
                   ("Одежда и быт", 0.12), ("Прочее", 0.08)]
    if persona["has_kids"]:
        weights = [(l, w * 0.9) for l, w in weights] + [("Дети (школа, кружки)", sum(w for _, w in weights) * 0.1)]
    return distribute(exp, weights)


def debt_type(rng: random.Random, amount: float, rate: float, kind: str) -> str:
    if kind == "cheap_debts_only":
        return rng.choice(["Льготный кредит", "Рассрочка от магазина", "Образовательный кредит (господдержка)",
                           "Ипотека (льготная)"])
    if rate < 0.01:
        return "Рассрочка"
    if amount >= 2_000_000:
        return "Ипотека" if rate <= 0.12 else "Кредит под залог недвижимости"
    if 300_000 <= amount < 2_000_000 and 0.10 <= rate <= 0.20:
        return "Автокредит"
    if rate >= 0.20:
        return rng.choice(["Кредит наличными", "Потребительский кредит"])
    return "Потребительский кредит"


def liquid_split(p: dict[str, Any], persona: dict[str, Any]) -> list[tuple[str, int]]:
    bliq = p["bliq"]
    if bliq <= 0:
        return [("Баланс на картах", 0)]
    months = bliq / max(p["expense_total"], 1.0)
    if months >= 12:
        return distribute(bliq, [("Баланс на картах", 0.08), ("Депозит / накопительный счёт", 0.92)])
    if months >= 3:
        return distribute(bliq, [("Баланс на картах", 0.45), ("Депозит / ОФЗ", 0.55)])
    return [("Баланс на картах", int(round(bliq)))]


def goal_names(p: dict[str, Any]) -> list[str]:
    rng = persona_rng(p["index"] * 13 + 5)
    names: list[str] = []
    used: set[str] = set()
    for g in p["goals"]:
        remaining = g["target_amount"] - g["current_amount"]
        pool = GOALS_SMALL if g["target_amount"] < 150_000 else (
            GOALS_MID if g["target_amount"] < 600_000 else GOALS_LARGE)
        if p["kind"] == "funded_goal" or remaining <= 0:
            names.append("Профинансированная цель")
            continue
        choice = rng.choice(pool)
        guard = 0
        while choice in used and guard < 20:
            choice = rng.choice(pool)
            guard += 1
        used.add(choice)
        names.append(choice)
    return names


def render_card(p: dict[str, Any], persona: dict[str, Any]) -> str:
    idx = p["index"]
    kind_ru = KIND_LABEL[p["kind"]][0]
    fio = f"{persona['first']} {persona['patronymic'] + ' ' if persona['patronymic'] else ''}{persona['surname']}"
    L: list[str] = []
    L.append(f"## SP-{idx:05d} · {fio}, {persona['age']} {years_word(persona['age'])} — [тип: {kind_ru}]\n")

    L.append("**Демография**\n")
    L.append("| Поле | Значение |")
    L.append("|---|---|")
    L.append(f"| Возраст | {persona['age']} {years_word(persona['age'])} |")
    L.append(f"| Профессия | {persona['profession']} |")
    L.append(f"| Город | {persona['city']} |")
    L.append(f"| Семейное положение | {persona['family']} |")
    L.append(f"| Контекст | {persona['context']} |")
    L.append("")

    inc = income_sources(p, persona)
    L.append(f"**Доходы — {fmt_money(p['income_total'])} ₽/мес**\n")
    L.append("| Источник | Сумма (₽) |")
    L.append("|---|---:|")
    for label, amt in inc:
        L.append(f"| {label} | {fmt_money(amt)} |")
    L.append(f"| **Итого** | **{fmt_money(p['income_total'])}** |")
    L.append("")

    exp = expense_breakdown(p, persona)
    L.append(f"**Расходы — {fmt_money(p['expense_total'])} ₽/мес** (без платежей по кредитам)\n")
    L.append("| Статья | Сумма (₽) |")
    L.append("|---|---:|")
    for label, amt in exp:
        L.append(f"| {label} | {fmt_money(amt)} |")
    L.append(f"| **Итого** | **{fmt_money(p['expense_total'])}** |")
    L.append("")

    L.append("**Обязательства**\n")
    if p["obligations"]:
        rng = persona_rng(idx * 17 + 3)
        L.append("| # | Банк | Тип | Остаток (₽) | Платёж (₽/мес) | Ставка | Срок (мес) |")
        L.append("|---|---|---|---:|---:|---:|---:|")
        total_debt = total_pay = 0.0
        for i, o in enumerate(p["obligations"], 1):
            bank = rng.choice(BANKS)
            dtype = debt_type(rng, o["amount"], o["interest_rate"], p["kind"])
            term = remaining_term_months(o["amount"], o["interest_rate"], o["monthly_payment"])
            term_s = "—" if term is None else (f"{term}+" if term >= 600 else str(term))
            total_debt += o["amount"]
            total_pay += o["monthly_payment"]
            L.append(f"| {i} | {bank} | {dtype} | {fmt_money(o['amount'])} | "
                     f"{fmt_money(o['monthly_payment'])} | {o['interest_rate'] * 100:.1f} % | {term_s} |")
        L.append(f"| | **Итого** | | **{fmt_money(total_debt)}** | **{fmt_money(total_pay)}** | | |")
    else:
        L.append("Нет действующих кредитов и рассрочек.")
    L.append("")

    liq = liquid_split(p, persona)
    L.append(f"**Ликвидная позиция — {fmt_money(p['bliq'])} ₽**\n")
    L.append("| Источник | Сумма (₽) |")
    L.append("|---|---:|")
    for label, amt in liq:
        L.append(f"| {label} | {fmt_money(amt)} |")
    L.append(f"| **Итого ликвидных средств** | **{fmt_money(p['bliq'])}** |")
    L.append("")

    L.append("**Цели накопления**\n")
    if p["goals"]:
        names = goal_names(p)
        L.append("| # | Название | Цель (₽) | Накоплено (₽) | Осталось (₽) | Готовность | Дедлайн |")
        L.append("|---|---|---:|---:|---:|---:|---|")
        for i, (g, nm) in enumerate(zip(p["goals"], names), 1):
            remaining = max(g["target_amount"] - g["current_amount"], 0.0)
            ready = (g["current_amount"] / g["target_amount"]) if g["target_amount"] > 0 else 0.0
            dl = g["deadline"]
            dl_s = "без срока" if dl is None else f"{MONTHS[dl.month]} {dl.year}"
            L.append(f"| {i} | {nm} | {fmt_money(g['target_amount'])} | {fmt_money(g['current_amount'])} | "
                     f"{fmt_money(remaining)} | {fmt_pct(ready)} | {dl_s} |")
    else:
        L.append("Целей накопления нет (граничный кейс «без целей»).")
    L.append("")

    L.append("**Профиль риска и рыночные параметры (вход модели)**\n")
    L.append("| Параметр | Значение |")
    L.append("|---|---|")
    L.append(f"| Профиль риска (1–5) | {p['risk_tolerance']} |")
    L.append(f"| r_bench (доходность-бенчмарк) | {p['r_bench'] * 100:.2f} % |")
    L.append(f"| L_min (порог ликвидности) | {p['l_min']:.2f} |")
    L.append("\n---\n")
    return "\n".join(L)


def portrait_record(p: dict[str, Any]) -> dict[str, Any]:
    """Чистый движковый вход портрета — объективная фикстура (без синтеза, без метрик)."""
    return {
        "id": f"SP-{p['index']:05d}",
        "index": p["index"],
        "kind": p["kind"],
        "engine": {
            "income_total": p["income_total"], "expense_total": p["expense_total"],
            "bliq": p["bliq"], "r_bench": p["r_bench"], "risk_tolerance": p["risk_tolerance"],
            "l_min": p["l_min"],
            "obligations": [dict(o) for o in p["obligations"]],
            "goals": [{**g, "deadline": g["deadline"].isoformat() if g["deadline"] else None}
                      for g in p["goals"]],
        },
    }


def legend_block(n: int, seed: int, kind_counts: Counter, stats: dict[str, Any]) -> str:
    L: list[str] = []
    L.append("# Синтетические портреты FINPILOT — сухой досье-набор (только вход)\n")
    L.append(f"> **{n} портретов**, воспроизводимых детерминированно из движкового генератора "
             f"`tools/portrait_testing/generator.py` (seed = {seed}). Каждый портрет описан по формату "
             "шести эталонных кейсов: демография, доходы, расходы, обязательства, ликвидность, цели, "
             "профиль риска. **Только входные данные — без вычисленных показателей и без оценок модели.** "
             "Rt/Lt/ПДН и рекомендации считает эксперт самостоятельно, чтобы сохранить объективность.\n")
    L.append("## Что здесь настоящее, а что синтезировано\n")
    L.append("- **Настоящие движковые числа** (вход модели): доход, расходы, суммы/ставки/платежи по "
             "кредитам, целевые и накопленные суммы целей, дедлайны, подушка B_liq, r_bench, профиль "
             "риска, L_min. Эти значения выдаёт генератор один-в-один.\n")
    L.append("- **Синтезированная обёртка-персона** (детерминирована по индексу, только для читаемости): "
             "ФИО, возраст, профессия, город, семейное положение, разбивка дохода по источникам, разбивка "
             "расходов по статьям, банк/тип/срок кредита, человеческие названия целей, сплит ликвидности "
             "на карты/депозит. Все разбивки сводятся **точно** к движковым тоталам и не меняют вход модели.\n")
    L.append("## Как идентифицировать портрет\n")
    L.append("Уникальный ID вида `SP-00042` (порядковый индекс) + структурный тег в заголовке. "
             "Один и тот же ID всегда даёт один и тот же портрет.\n")
    L.append("## Легенда структурных типов (особенность ВХОДА)\n")
    L.append("| Тип | Метка | Структурная особенность | Кол-во в наборе |")
    L.append("|---|---|---|---:|")
    for k in ("plain", "zero_income", "zero_expenses", "deficit_cf", "overleveraged",
              "cheap_debts_only", "no_goals", "funded_goal", "huge_bliq", "many_goals"):
        ru, note = KIND_LABEL[k]
        L.append(f"| `{k}` | {ru} | {note} | {kind_counts.get(k, 0)} |")
    L.append("")
    L.append("## Состав набора (структурная статистика входа)\n")
    L.append("| Метрика | Значение |")
    L.append("|---|---:|")
    L.append(f"| Всего портретов | {n} |")
    L.append(f"| Граничных (edge) | {stats['edge']} ({stats['edge'] * 100 // n} %) |")
    L.append(f"| Типовых (plain) | {stats['plain']} |")
    L.append(f"| Без кредитов | {stats['no_debt']} |")
    L.append(f"| Без целей | {stats['no_goals']} |")
    L.append(f"| Медианный доход, ₽ | {fmt_money(stats['median_income'])} |")
    L.append(f"| Медианные расходы, ₽ | {fmt_money(stats['median_expense'])} |")
    L.append("\n---\n")
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=12000)
    ap.add_argument("--seed", type=int, default=20260702)
    ap.add_argument("--outdir", default="out")
    args = ap.parse_args()

    gen = PortraitGenerator(seed=args.seed)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    kind_counts: Counter = Counter()
    incomes: list[float] = []
    expenses: list[float] = []
    edge = plain = no_debt = no_goals_c = 0

    records: list[dict[str, Any]] = []
    cards: list[str] = []
    sample_cards: list[str] = []
    sample_seen: set[str] = set()

    for i in range(args.n):
        p = gen.generate(i)
        persona = build_persona(p)

        kind_counts[p["kind"]] += 1
        incomes.append(p["income_total"])
        expenses.append(p["expense_total"])
        if p["kind"] == "plain":
            plain += 1
        else:
            edge += 1
        if not p["obligations"]:
            no_debt += 1
        if not p["goals"]:
            no_goals_c += 1

        card = render_card(p, persona)
        cards.append(card)
        records.append(portrait_record(p))

        tag_kind = p["kind"]
        tag_risk = f"risk{p['risk_tolerance']}"
        if tag_kind not in sample_seen or tag_risk not in sample_seen:
            sample_cards.append(card)
            sample_seen.add(tag_kind)
            sample_seen.add(tag_risk)

    incomes.sort()
    expenses.sort()
    stats = {"edge": edge, "plain": plain, "no_debt": no_debt, "no_goals": no_goals_c,
             "median_income": incomes[len(incomes) // 2], "median_expense": expenses[len(expenses) // 2]}

    header = legend_block(args.n, args.seed, kind_counts, stats)
    (outdir / "synthetic_portraits_12000_cards.md").write_text(header + "\n".join(cards), encoding="utf-8")

    (outdir / "synthetic_portraits_sample.md").write_text(
        legend_block(args.n, args.seed, kind_counts, stats).replace(
            "сухой досье-набор (только вход)", "сухой досье-набор — ВЫБОРКА")
        + "> Репрезентативная выборка: по одному портрету на каждый структурный тип и на каждый "
          "профиль риска. Полный набор — в основном файле.\n\n---\n\n" + "\n".join(sample_cards),
        encoding="utf-8")

    with (outdir / "portraits_12000.jsonl").open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"OK: {len(records)} портретов | kinds: {dict(kind_counts)}")
    print(f"stats: {stats}")


if __name__ == "__main__":
    main()
