"""Категория бюджета уникальна В ПРЕДЕЛАХ ВЛАДЕЛЬЦА, а не глобально.

🔴 Найдено `/code-review` 05.09.2026. `budgets.category` нёс глобальный `unique=True`
(миграция 0006, ни разу не правившаяся), тогда как поиск существующей строки
в `crud.create_budget` идёт через `_owner_filter` — то есть в пределах владельца.

Следствие: второй пользователь, заводящий «Продукты», своей строки не находит,
идёт на INSERT и получает `IntegrityError` — **500 на ровном месте**. Бюджеты
ломались бы у всех, кроме первого зарегистрировавшегося, и **только на проде**:
в однопользовательской разработке конфликт не возникает.

Уникальность нужна: на ней стоит upsert по категории (FR-22, «завести бюджет
повторно = изменить лимит»). Поэтому индекс не снимается, а сужается до пары
`(user_id, category)`.

`household_id` в ключ НЕ входит сознательно: общий бюджет принадлежит своему создателю
(`user_id` у него заполнен), и пара уже различает записи. Добавить третью колонку
значило бы разрешить одному человеку две строки «Продукты» — личную и семейную —
а `create_budget` ищет по одной категории и перезаписал бы произвольную из них.

Revision ID: 0036
Revises: 0035
"""
from alembic import op

revision = "0036"
down_revision = "0035"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # batch_alter_table нужен SQLite: он не умеет ALTER для индексов и пересоздаёт
    # таблицу целиком. На PostgreSQL операция проходит напрямую.
    with op.batch_alter_table("budgets") as batch:
        batch.drop_index("ix_budgets_category")
        batch.create_index("ix_budgets_category", ["category"], unique=False)
        batch.create_index(
            "uq_budgets_owner_category", ["user_id", "category"], unique=True
        )


def downgrade() -> None:
    with op.batch_alter_table("budgets") as batch:
        batch.drop_index("uq_budgets_owner_category")
        batch.drop_index("ix_budgets_category")
        batch.create_index("ix_budgets_category", ["category"], unique=True)
