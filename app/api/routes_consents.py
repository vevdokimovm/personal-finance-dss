"""Согласия и юридические документы (юрблок L1, L3, L4, L5).

Три эндпоинта состояния/выдачи/отзыва плюс публичный реестр документов: фронту
нужно знать не только что показать, но и КАКУЮ РЕДАКЦИЮ он показывает, чтобы
записать именно её.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import BASE_DIR
from app.core.legal import DISCLAIMER_39FZ, LEGAL_DOCUMENTS, is_known
from app.database.db import get_db
from app.database.models import User
from app.dependencies import require_user
from app.services.consent import (
    ConsentWithdrawalNotAllowed,
    consent_state,
    grant_consent,
    withdraw_consent,
)

router = APIRouter(tags=["Согласия и право"])


class ConsentState(BaseModel):
    """Состояние одного согласия.

    `withdrawable` — не удобство, а требование: по нему интерфейс решает, показывать ли
    кнопку отзыва. Согласие-основание (обработка ПДн) отозвать нельзя иначе как удалением
    аккаунта — кнопка там гарантированно дала бы 409, то есть тупик ([IA-04]).
    """

    granted: bool
    version: str
    #: Действующая редакция документа. Вместе с `version` отвечает на вопрос, надо ли
    #: спрашивать согласие заново: одно поле без другого сравнить не с чем.
    current_version: str
    #: Совпадает ли редакция, на которую человек соглашался, с действующей.
    #: 🔴 По 152-ФЗ согласие даётся на КОНКРЕТНУЮ редакцию, а проверка действующего
    #: согласия её не сравнивала: после публикации новой политики обработка шла
    #: по основанию, которого человек не давал. Доступ при расхождении не отзывается
    #: автоматически — это решение владельца, а не следствие правки редакции.
    is_current: bool
    granted_at: str | None = None
    withdrawable: bool


class ConsentsResponse(BaseModel):
    """Ответ `/consents`: состояние по ВСЕМ известным типам, включая невыданные.

    Схема заведена ДО фронта (v8.41.0): раньше эндпоинт был размечен `-> dict`. Цена
    рукописного типа здесь максимальна из всех — по этому ответу строится экран выдачи
    и отзыва согласий (L3), а невозможность отозвать согласие это нарушение 152-ФЗ,
    а не дефект интерфейса.
    """

    consents: dict[str, ConsentState]


@router.get("/consents", summary="Состояние согласий пользователя")
def get_consents(user: User = Depends(require_user),
                 db: Session = Depends(get_db)) -> ConsentsResponse:
    """Все известные типы, включая невыданные: фронт должен знать, что спросить."""
    return ConsentsResponse(
        consents={
            key: ConsentState(**value) for key, value in consent_state(db, user.id).items()
        }
    )


@router.post("/consents/{consent_type}", summary="Выдать согласие")
def grant(consent_type: str, request: Request,
          user: User = Depends(require_user),
          db: Session = Depends(get_db)) -> dict:
    if not is_known(consent_type):
        raise HTTPException(status_code=404, detail="Неизвестный тип согласия")
    record = grant_consent(
        db, user.id, consent_type,
        source_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return {"granted": True, "type": consent_type,
            "version": record.doc_version,
            "granted_at": record.granted_at.isoformat()}


@router.delete("/consents/{consent_type}", summary="Отозвать согласие")
def withdraw(consent_type: str, user: User = Depends(require_user),
             db: Session = Depends(get_db)) -> Response:
    if not is_known(consent_type):
        raise HTTPException(status_code=404, detail="Неизвестный тип согласия")
    try:
        withdraw_consent(db, user.id, consent_type)
    except ConsentWithdrawalNotAllowed as exc:
        raise HTTPException(
            status_code=409,
            detail="Это согласие — основание обработки ваших данных. "
                   "Отозвать его можно только вместе с удалением аккаунта: "
                   "DELETE /api/auth/account",
        ) from exc
    # 204 отдаётся явным Response без status_code в декораторе: иначе FastAPI
    # ставит application/json на пустое тело и WebKit ломается (engineering_practices).
    return Response(status_code=204)


class LegalDocument(BaseModel):
    """Один юридический документ.

    `version` и `effective_from` — не украшение: по 152-ФЗ согласие даётся на
    КОНКРЕТНУЮ редакцию, и интерфейс обязан показывать, на какую именно.
    """

    title: str
    version: str
    effective_from: str
    url: str


class LegalDocuments(BaseModel):
    """Ответ `/legal/documents`.

    Схема заведена ДО фронта (v8.40.0): раньше эндпоинт был размечен `-> dict`, то есть
    попадал в OpenAPI как `{[key: string]: unknown}`. Цена рукописного типа здесь выше
    обычной — по этим полям строится юридический контур (ссылки в футере L7, дисклеймер
    39-ФЗ L5), и расхождение означает отсутствие обязательного по закону элемента,
    а не косметический сбой.
    """

    documents: dict[str, LegalDocument]
    disclaimer_39fz: str


@router.get("/legal/documents", summary="Реестр юридических документов")
def legal_documents() -> LegalDocuments:
    """Публичный: версии нужны и до входа — на странице регистрации."""
    return LegalDocuments(
        documents={
            key: LegalDocument(
                title=doc["title"],
                version=doc["version"],
                effective_from=doc["effective_from"],
                url=doc["url"],
            )
            for key, doc in LEGAL_DOCUMENTS.items()
        },
        disclaimer_39fz=DISCLAIMER_39FZ,
    )


class LegalDocumentContent(LegalDocument):
    """Документ вместе с ТЕКСТОМ.

    Отдельно от `LegalDocument`: реестр отдаёт метаданные всех документов сразу и висит
    в футере каждой страницы — вкладывать в него шесть полных текстов значило бы возить
    десятки килобайт на каждой навигации ради ссылки из четырёх слов.

    Содержимое — markdown, как в официальном пакете (`docs/legal/`), а не HTML. Конверсия
    на бэкенде завела бы ТРЕТЬЮ редакцию документа рядом с `md` и `docx`, и доказывать
    в споре пришлось бы, какая из трёх показана человеку.
    """

    slug: str
    content: str


@router.get("/legal/documents/{slug}", summary="Текст юридического документа")
def legal_document_content(slug: str) -> LegalDocumentContent:
    """Текст документа из ЕДИНСТВЕННОГО источника — файла официального пакета.

    🔴 Публичный намеренно. Политику обработки ПДн человек обязан прочитать ДО
    регистрации, иначе согласие неинформированное — а это дефект юридический, а не
    интерфейсный. Требовать авторизации, чтобы прочитать условия обработки данных,
    значит замкнуть круг.

    🔴 Путь берётся из реестра ПО КЛЮЧУ и никогда не склеивается из ввода: иначе
    `../../.env` читался бы с диска через публичный эндпоинт. Неизвестный ключ — 404
    до всякого обращения к файловой системе.
    """
    doc = LEGAL_DOCUMENTS.get(slug)
    if doc is None:
        raise HTTPException(status_code=404, detail="Неизвестный документ")
    path = BASE_DIR / doc["path"]
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        # Файл пакета пропал или недоступен. Молча отдать пустой текст нельзя: снаружи
        # это неотличимо от документа, который так и написан, — и человек «ознакомился»
        # с пустой страницей.
        raise HTTPException(
            status_code=503,
            detail="Текст документа временно недоступен. Обратитесь в поддержку.",
        ) from exc
    return LegalDocumentContent(
        slug=slug,
        title=doc["title"],
        version=doc["version"],
        effective_from=doc["effective_from"],
        url=doc["url"],
        content=content,
    )
