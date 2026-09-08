"""Согласия пользователя: выдача, отзыв, текущее состояние (юрблок L1, L3, L4).

Ключевое правило подсистемы: **запись согласия неизменяема по смыслу**. Отзыв
проставляет `withdrawn_at`, но не удаляет строку и не меняет тип или версию —
доказательство обязано пережить отзыв, иначе нечем подтвердить, что в такой-то
период обработка велась на законном основании. Повторная выдача создаёт новую
строку, а не воскрешает старую.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.legal import (
    CONSENT_TYPES,
    UNWITHDRAWABLE,
    current_version,
    is_known,
)
from app.database.models import UserConsent, utcnow


class ConsentWithdrawalNotAllowed(Exception):
    """Отзыв согласия, которое является основанием обработки.

    Отозвать согласие на обработку ПДн, сохранив аккаунт, нельзя: это оставило
    бы данные без правового основания. Путь пользователя — удаление аккаунта,
    которое уносит и данные, и согласия.
    """


def _require_known(consent_type: str) -> None:
    if not is_known(consent_type):
        raise ValueError(f"неизвестный тип согласия: {consent_type}")


def _active(db: Session, user_id: str,
            consent_type: str) -> Optional[UserConsent]:
    """Действующее согласие данного типа: на текущую редакцию, иначе самое свежее.

    🔴 Выбор по СМЫСЛУ, а не по одной отметке времени. С тех пор как подтверждение
    новой редакции заводит отдельную запись, действующих записей у типа бывает
    несколько, и порядок «последняя по `granted_at`» зависит от совпадения отметок:
    две выдачи в одну микросекунду (двойной клик, повтор запроса) дают неопределённый
    результат. Победи там запись на прежнюю редакцию — `is_current` остался бы `false`
    навсегда, а кнопка «Подтвердить новую редакцию» плодила бы строки, ничего не меняя.

    Согласие на прежнюю редакцию при этом остаётся действующим: доступ при расхождении
    не отзывается, иначе смена редакции документа заперла бы человека вне его данных.

    Args:
        db: Сессия БД.
        user_id: Владелец согласия.
        consent_type: Тип из `CONSENT_TYPES`.

    Returns:
        Запись согласия или `None`, если действующих нет.
    """
    rows = (db.query(UserConsent)
            .filter(UserConsent.user_id == user_id,
                    UserConsent.consent_type == consent_type,
                    UserConsent.withdrawn_at.is_(None))
            .order_by(UserConsent.granted_at.desc())
            .all())
    if not rows:
        return None
    actual = current_version(consent_type)
    for row in rows:
        if row.doc_version == actual:
            return row
    return rows[0]


def grant_consent(db: Session, user_id: str, consent_type: str, *,
                  source_ip: Optional[str] = None,
                  user_agent: Optional[str] = None) -> UserConsent:
    """Выдать согласие на ДЕЙСТВУЮЩУЮ редакцию документа.

    Действующее согласие на ту же редакцию возвращается как есть — повторный заход
    на экран не должен плодить строки. А вот согласие на **прежнюю** редакцию заводит
    новую запись: по 152-ФЗ согласие даётся на конкретную редакцию, и подтверждение
    новой — это новое согласие, а не обновление старого.

    🔴 **Прежняя редакция сравнивала только факт наличия и делала повторную выдачу
    no-op.** Для `personal_data` это был тупик без обходного пути: тип входит
    в `UNWITHDRAWABLE`, отозвать и выдать заново нельзя. Поднятие версии политики
    обработки ПДн — самого частого к пересмотру документа — перевело бы всех
    пользователей в состояние «согласие на устаревшую редакцию» без способа выйти,
    кроме удаления аккаунта. Найдено третьим проходом независимого аудита 08.09.2026,
    через сутки после того, как расхождение научились ЗАМЕЧАТЬ (`is_current`).

    🔴 **Прежняя запись не трогается.** В период между редакциями обработка шла
    на её основании, и она остаётся доказательством этого основания.

    Args:
        db: Сессия БД.
        user_id: Владелец согласия.
        consent_type: Тип из `CONSENT_TYPES`.
        source_ip: IP, с которого дано согласие (доказательство).
        user_agent: Клиент, из которого дано согласие (доказательство).

    Returns:
        Действующая запись согласия на текущую редакцию.

    Raises:
        ValueError: Если тип согласия неизвестен.
    """
    _require_known(consent_type)
    existing = _active(db, user_id, consent_type)
    if existing is not None and existing.doc_version == current_version(consent_type):
        return existing
    record = UserConsent(
        user_id=user_id,
        consent_type=consent_type,
        doc_version=current_version(consent_type),
        granted_at=utcnow(),
        source_ip=source_ip,
        user_agent=user_agent,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def withdraw_consent(db: Session, user_id: str, consent_type: str) -> bool:
    """Отозвать согласие. Строки сохраняются, проставляется `withdrawn_at`.

    🔴 Гасятся ВСЕ действующие записи типа, а не последняя. С тех пор как
    подтверждение новой редакции заводит отдельную запись, у типа их может быть
    несколько без `withdrawn_at` одновременно. Прежняя редакция гасила только
    новейшую — прежняя оставалась действующей, `has_consent` продолжал отвечать
    `True`, и отзыв не срабатывал вовсе: кнопка нажата, ответ успешный, обработка
    идёт. Для отзываемых типов это прямое нарушение 152-ФЗ.

    Записи не удаляются: они доказательство того, на каком основании и в какой
    период данные обрабатывались.

    Args:
        db: Сессия БД.
        user_id: Владелец согласия.
        consent_type: Тип из `CONSENT_TYPES`.

    Returns:
        `True`, если было что отзывать; `False`, если действующих записей нет.

    Raises:
        ConsentWithdrawalNotAllowed: Для типов из `UNWITHDRAWABLE`.
        ValueError: Если тип согласия неизвестен.
    """
    _require_known(consent_type)
    if consent_type in UNWITHDRAWABLE:
        raise ConsentWithdrawalNotAllowed(consent_type)
    records = (db.query(UserConsent)
               .filter(UserConsent.user_id == user_id,
                       UserConsent.consent_type == consent_type,
                       UserConsent.withdrawn_at.is_(None))
               .all())
    if not records:
        return False
    moment = utcnow()
    for record in records:
        record.withdrawn_at = moment
    db.commit()
    return True


def has_consent(db: Session, user_id: str, consent_type: str) -> bool:
    _require_known(consent_type)
    return _active(db, user_id, consent_type) is not None


def active_consents(db: Session, user_id: str) -> dict[str, UserConsent]:
    """Действующие согласия пользователя по типам (отозванные не попадают).

    🔴 Выбор внутри типа делает `_active` — ОДИН источник правды на модуль.
    Прежняя редакция повторяла здесь запрос с `order_by(granted_at.desc())`
    и `setdefault`, то есть держала собственный, более слабый ответ на вопрос
    «какая запись действует»: гейты (`has_consent` → `_active`) и экран
    (`consent_state` → сюда) могли разойтись при совпавших отметках времени.

    Чем это грозило: экран показывает «редакция устарела», человек жмёт
    «Подтвердить новую редакцию», `grant_consent` спрашивает `_active`, видит
    запись на текущую редакцию и возвращает её как есть — кнопка есть всегда
    и не делает ничего. Для `personal_data` без обходного пути: отзыв запрещён.

    Args:
        db: Сессия БД.
        user_id: Владелец согласий.

    Returns:
        Отображение «тип согласия → действующая запись». Типы без действующих
        записей в результат не попадают.
    """
    types = {row[0] for row in (
        db.query(UserConsent.consent_type)
        .filter(UserConsent.user_id == user_id,
                UserConsent.withdrawn_at.is_(None))
        .distinct()
    )}
    state: dict[str, UserConsent] = {}
    for consent_type in types:
        record = _active(db, user_id, consent_type)
        if record is not None:
            state[consent_type] = record
    return state


def consent_state(db: Session, user_id: str) -> dict[str, dict]:
    """Состояние по ВСЕМ известным типам — форма ответа API.

    Возвращаются все типы, включая невыданные: фронту нужно знать не только что
    выдано, но и что предстоит спросить.
    """
    active = active_consents(db, user_id)
    state: dict[str, dict] = {}
    for consent_type in CONSENT_TYPES:
        record = active.get(consent_type)
        actual = current_version(consent_type)
        # 🔴 Согласие даётся на КОНКРЕТНУЮ редакцию (152-ФЗ), а проверка действующего
        # согласия редакцию не сравнивала вовсе: после публикации новой политики
        # обработка продолжалась по согласию на прежнюю, и никто ни о чём не спрашивал.
        # Cookie-баннер в этом же продукте ведёт себя правильно — сравнивает версии.
        #
        # Доступ здесь НЕ отзывается автоматически: автоотзыв запер бы человека вне его
        # собственных данных из-за того, что компания поменяла редакцию документа.
        # Код обязан дать факт расхождения; что с ним делать — решение владельца.
        state[consent_type] = {
            "granted": record is not None,
            "version": record.doc_version if record else actual,
            "current_version": actual,
            "is_current": record is not None and record.doc_version == actual,
            "granted_at": record.granted_at.isoformat() if record else None,
            "withdrawable": consent_type not in UNWITHDRAWABLE,
        }
    return state


def purge_consents(db: Session, user_id: str) -> None:
    """Удалить согласия при удалении аккаунта (152-ФЗ, право на удаление).

    Здесь право на удаление перевешивает интерес хранить доказательство: данных,
    для которых нужно основание, больше нет.
    """
    db.execute(delete(UserConsent).where(UserConsent.user_id == user_id))
