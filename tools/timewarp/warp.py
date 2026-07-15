"""Pytest-плагин «машина времени»: сдвигает app.utils.time.utcnow на WARP_DAYS вперёд.

Назначение — аудит календарных мин: тест, зелёный сегодня, но красный при сдвиге
часов вперёд, завязан на календарную константу против окна от реальных часов.
Патчится ЕДИНАЯ точка времени (ADR-002) ДО импорта модулей приложения, поэтому
все `from app.utils.time import utcnow` получают сдвинутую функцию.
Не применять к auth/JWT-тестам: iat/exp токенов живут на реальных часах.
"""
import os
from datetime import timedelta

import app.utils.time as _t

_real = _t.utcnow
_offset = timedelta(days=int(os.environ.get("WARP_DAYS", "90")))


def _warped():
    return _real() + _offset


_t.utcnow = _warped
