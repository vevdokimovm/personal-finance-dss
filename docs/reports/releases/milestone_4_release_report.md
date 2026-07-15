# Release-отчёт: Веха 4 (бэкенд + hardening)

- **Диапазон:** ветка версий `v4.x`, закрытие на `v4.30.2`.
- **Период:** до 2026-07-01.

## 1. Цель вехи
Довести бэкенд до production-уровня: доделать бэк-код, техдолг, хвосты и, ключевое, **cybersecurity
hardening (раздел 4.4)** — уровень безопасности серьёзного финпродукта (JWT, шифрование, ПДн, MFA).

## 2. Что вошло (финальный отрезок 4.4)
| Версия | Тип | Суть |
|---|---|---|
| v4.26.0 | MINOR | JWT-revocation: `revoked_tokens` + `tokens_valid_since`; `logout` (по `jti`) и `logout-all`. |
| v4.27.0 | MINOR | Смена/сброс пароля гасит все сессии (follow-up к JWT). |
| v4.28.0 | MINOR | Ротация ключа шифрования Fernet → MultiFernet («в покое»). |
| v4.29.0 | MINOR | Security-регрессии + старт-гард ключа шифрования. |
| v4.30.0 | MINOR | MFA/TOTP — последняя бэк-задача 4.4. |
| v4.30.1 | PATCH | Хвосты: фикс reverse-миграции 0009, BUG-027, чистка чекбоксов 4.4. |
| v4.30.2 | PATCH | Гигиена: выравнивание flake8-гейта на весь проект. |

## 3. Итог
Веха 4 **закрыта полностью** (бэк-код + техдолг + хвосты + flake8-гейт). Раздел 4.4 выполнен:
инвалидация сессий, ротация ключей, старт-гард, MFA, security-регрессии. Итоговый security-срез —
`docs/reports/security/finpilot_security_audit.md`.

## 4. Инциденты и уроки в ходе вехи
- Post-mortem'ы: `postgres_incident_postmortem.md`, `dependencies_cve_postmortem.md`,
  `e2e_incident_postmortem.md`, `cbr_keyrate_param_incident.md` (см. `docs/reports/incidents/`).
- Расследования: `browsers_sandbox_investigation.md`, `visual_flakiness_investigation.md`,
  a11y-серия (см. `docs/reports/investigations/`).
- Грабли — `docs/pitfalls.md`.

## 5. Что перенесено дальше
- Инфраструктурные хвосты 4.4: Redis-backed rate limiting, CSP nonce-policy — к деплой-вехе.
- **Веха 5** (текущая, организационная): репозитории, база знаний, документация, отчётность.
