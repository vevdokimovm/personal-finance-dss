"""
Классификатор категорий транзакций (rules-engine).

Назначение: по описанию операции (мерчант / назначение платежа),
MCC-коду и типу операции определить каноническую категорию из
фиксированной таксономии Category.

Категоризатор детерминированный и объяснимый — что важно для СППР:
любую присвоенную категорию можно проследить до конкретного правила.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache


class Category(str, Enum):
    GROCERIES = "Продукты"
    CAFE = "Кафе и рестораны"
    TRANSPORT = "Транспорт"
    SUBSCRIPTIONS = "Подписки и сервисы"
    SHOPPING = "Покупки"
    HEALTH = "Здоровье"
    UTILITIES = "ЖКХ и связь"
    ENTERTAINMENT = "Развлечения"
    SALARY = "Зарплата"
    CASHBACK = "Кэшбэк"
    TRANSFER = "Переводы"
    OTHER_INCOME = "Прочий доход"
    OTHER = "Прочее"


@dataclass(frozen=True)
class Rule:
    """Правило категоризации: срабатывает по MCC-коду или ключевому слову."""

    category: Category
    keywords: tuple[str, ...] = ()
    mcc_codes: tuple[str, ...] = ()
    applies_to: str | None = None  # "income" | "expense" | None (оба типа)
    priority: int = 0  # выше — проверяется раньше

    def matches(self, text: str, mcc: str | None, txn_type: str) -> bool:
        if self.applies_to is not None and self.applies_to != txn_type:
            return False
        if mcc and self.mcc_codes and mcc.strip() in self.mcc_codes:
            return True
        return any(keyword in text for keyword in self.keywords)


class CategoryClassifier:
    """Перебирает правила по убыванию приоритета, возвращает первую подходящую категорию."""

    def __init__(self, rules: list[Rule], default: Category = Category.OTHER) -> None:
        self._rules = sorted(rules, key=lambda rule: rule.priority, reverse=True)
        self._default = default

    def classify(
        self,
        description: str | None,
        mcc: str | None = None,
        txn_type: str = "expense",
    ) -> Category:
        text = (description or "").casefold()
        for rule in self._rules:
            if rule.matches(text, mcc, txn_type):
                return rule.category
        if txn_type == "income":
            return Category.OTHER_INCOME
        return self._default


@lru_cache(maxsize=1)
def get_default_classifier() -> CategoryClassifier:
    """Кешированный синглтон классификатора на правилах по умолчанию."""
    from app.core.category_rules import DEFAULT_RULES

    return CategoryClassifier(DEFAULT_RULES)


def classify_transaction(
    description: str | None,
    mcc: str | None = None,
    txn_type: str = "expense",
) -> str:
    """Публичный хелпер: возвращает строковую метку категории для записи в БД."""
    return get_default_classifier().classify(description, mcc, txn_type).value


# --- P2.7: обучение категоризации на правках пользователя (детерминированно, без ML) ---

# Минимальная длина нормализованного токена правила. Guard: токены короче этого
# отсекаются, чтобы случайное правило не цепляло половину операций.
MIN_MATCH_TOKEN_LEN = 3


def normalize_match_key(text: str | None) -> str:
    """Нормализует текст для матчинга правил: casefold + схлопывание пробелов.

    Одинаково применяется к токену правила и к описанию операции, поэтому
    «STARBUCKS  Москва» и «starbucks москва» матчатся.
    """
    if not text:
        return ""
    return " ".join(text.casefold().split())


def classify_with_rules(
    description: str | None,
    mcc: str | None,
    txn_type: str,
    rules: Iterable[tuple[str, str]] = (),
) -> str:
    """Категоризация с приоритетом пользовательских правил-оверрайдов над дефолтным движком.

    `rules` — последовательность `(match_token, category)`, уже отфильтрованных вызывающим
    кодом по `user_id` и типу операции. Правило срабатывает, если его нормализованный токен
    (длиной >= `MIN_MATCH_TOKEN_LEN`) содержится в нормализованном описании операции; возвращается
    категория первого сработавшего правила. Если не сработало ни одно — fallback на
    детерминированный `classify_transaction`.

    Ядро не знает про БД: правила передаются снаружи (из crud), поэтому функция остаётся чистой.
    """
    text = normalize_match_key(description)
    if text:
        for token, category in rules:
            norm_token = normalize_match_key(token)
            if len(norm_token) >= MIN_MATCH_TOKEN_LEN and norm_token in text:
                return category
    return classify_transaction(description, mcc, txn_type)
