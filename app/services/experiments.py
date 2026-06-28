"""
A/B-эксперименты (P3.5): назначение с фиксацией, управление, измерение.

Назначение детерминированное (`core/experiments.assign_variant`) и ЛОЧИТСЯ при первом показе —
сохраняется в `experiment_assignments`, поэтому смена весов/вариантов не перекидывает уже
назначенных пользователей (ноль контаминации). Гонка двух одновременных назначений одного
subject разрешается через UNIQUE + повторное чтение.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.experiments import assign_variant
from app.database.models import Experiment, ExperimentAssignment
from app.services.event_logger import log_event

STATUSES = ("draft", "running", "stopped")
EXPOSURE_EVENT = "experiment_exposure"


def _subject_id(user_id: Optional[str], session_id: Optional[str]) -> Optional[str]:
    return user_id or session_id or None


def _variant_pairs(experiment: Experiment) -> list[tuple[str, int]]:
    return [(v["name"], int(v["weight"])) for v in (experiment.variants or [])]


def validate_variants(variants: object) -> list[dict]:
    """Нормализует и валидирует варианты: непустой список `{name, weight>0}`."""
    if not isinstance(variants, list) or not variants:
        raise ValueError("variants: ожидается непустой список {name, weight}")
    normalized: list[dict] = []
    for item in variants:
        try:
            name = str(item["name"]).strip()
            weight = int(item["weight"])
        except (KeyError, TypeError, ValueError):
            raise ValueError("variants: каждый элемент — {name: str, weight: int}")
        if not name or weight <= 0:
            raise ValueError("variants: name непустой, weight > 0")
        normalized.append({"name": name, "weight": weight})
    return normalized


# ── Управление экспериментами (админ) ────────────────────────────────────
def create_experiment(
    db: Session,
    key: str,
    *,
    name: str = "",
    description: Optional[str] = None,
    variants: object = None,
    conversion_event: Optional[str] = None,
    status: str = "draft",
) -> Experiment:
    if status not in STATUSES:
        raise ValueError(f"status ∈ {STATUSES}")
    experiment = Experiment(
        key=key,
        name=name,
        description=description,
        variants=validate_variants(variants),
        conversion_event=conversion_event,
        status=status,
    )
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return experiment


def get_experiment(db: Session, key: str) -> Optional[Experiment]:
    return db.query(Experiment).filter(Experiment.key == key).first()


def list_experiments(db: Session) -> list[Experiment]:
    return db.query(Experiment).order_by(Experiment.created_at.desc()).all()


def update_experiment(
    db: Session,
    key: str,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    variants: object = None,
    conversion_event: Optional[str] = None,
    status: Optional[str] = None,
) -> Optional[Experiment]:
    experiment = get_experiment(db, key)
    if experiment is None:
        return None
    if name is not None:
        experiment.name = name
    if description is not None:
        experiment.description = description
    if variants is not None:
        experiment.variants = validate_variants(variants)
    if conversion_event is not None:
        experiment.conversion_event = conversion_event
    if status is not None:
        if status not in STATUSES:
            raise ValueError(f"status ∈ {STATUSES}")
        experiment.status = status
    db.commit()
    db.refresh(experiment)
    return experiment


def delete_experiment(db: Session, key: str) -> bool:
    experiment = get_experiment(db, key)
    if experiment is None:
        return False
    db.query(ExperimentAssignment).filter(
        ExperimentAssignment.experiment_id == experiment.id
    ).delete()
    db.delete(experiment)
    db.commit()
    return True


# ── Назначение варианта (для приложения) ─────────────────────────────────
def get_or_assign_variant(
    db: Session,
    key: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Optional[str]:
    """Возвращает вариант subject в эксперименте; при первом показе фиксирует и логирует.

    None — если нет subject, эксперимент не найден / не `running`, или варианты пусты.
    Назначение лочится: повторные вызовы (и смена конфига) возвращают тот же вариант.
    """
    subject = _subject_id(user_id, session_id)
    if not subject:
        return None
    experiment = get_experiment(db, key)
    if experiment is None or experiment.status != "running":
        return None

    existing = (
        db.query(ExperimentAssignment)
        .filter(
            ExperimentAssignment.experiment_id == experiment.id,
            ExperimentAssignment.subject_id == subject,
        )
        .first()
    )
    if existing is not None:
        return existing.variant

    variant = assign_variant(key, subject, _variant_pairs(experiment))
    if variant is None:
        return None

    db.add(
        ExperimentAssignment(experiment_id=experiment.id, subject_id=subject, variant=variant)
    )
    try:
        db.commit()
    except IntegrityError:
        # гонка: параллельный запрос уже назначил этого subject — берём его назначение
        db.rollback()
        raced = (
            db.query(ExperimentAssignment)
            .filter(
                ExperimentAssignment.experiment_id == experiment.id,
                ExperimentAssignment.subject_id == subject,
            )
            .first()
        )
        return raced.variant if raced is not None else variant

    log_event(
        EXPOSURE_EVENT,
        {"experiment": key, "variant": variant},
        session_id=session_id,
        user_id=user_id,
    )
    return variant
