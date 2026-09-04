from fastapi import APIRouter, Depends

from app.api.routes_analysis import router as analysis_router
from app.api.routes_auth import router as auth_router
from app.api.routes_banks import router as banks_router
from app.api.routes_budgets import router as budgets_router
from app.api.routes_categories import router as categories_router
from app.api.routes_consents import router as consents_router
from app.api.routes_demo import router as demo_router
from app.api.routes_experiments import admin_router as experiments_admin_router
from app.api.routes_experiments import router as experiments_router
from app.api.routes_fx import router as fx_router
from app.api._consent_guard import require_financial_consent
from app.api.routes_goals import router as goals_router
from app.api.routes_households import router as households_router
from app.api.routes_liquid_assets import router as liquid_assets_router
from app.api.routes_obligations import router as obligations_router
from app.api.routes_plaid import router as plaid_router
from app.api.routes_analytics import router as analytics_router
from app.api.routes_i18n import router as i18n_router
from app.api.routes_referral import router as referral_router
from app.api.routes_export import router as export_router
from app.api.routes_notifications import router as notifications_router
from app.api.routes_planning import router as planning_router
from app.api.routes_recommendation import router as recommendation_router
from app.api.routes_transactions import router as transactions_router
from app.api.routes_subscription import router as subscription_router
from app.api.routes_telegram import router as telegram_router
from app.api.routes_telemetry import router as telemetry_router
from app.api.routes_user_prefs import router as user_prefs_router
from app.config import settings

router = APIRouter(prefix=settings.API_PREFIX)
router.include_router(auth_router)
router.include_router(consents_router)

# Юрблок L1: финансовый портрет обрабатывается по ОТДЕЛЬНОМУ согласию.
# Гейт висит на роутерах целиком, а не на отдельных ручках: пропуск одной
# ручки означал бы обработку без основания, и заметить это было бы нечем.
_FIN = [Depends(require_financial_consent)]

router.include_router(transactions_router, dependencies=_FIN)
router.include_router(obligations_router, dependencies=_FIN)
router.include_router(goals_router, dependencies=_FIN)
router.include_router(households_router)
router.include_router(liquid_assets_router, dependencies=_FIN)
router.include_router(telemetry_router, dependencies=_FIN)
router.include_router(categories_router)
router.include_router(user_prefs_router)
router.include_router(analysis_router, dependencies=_FIN)
router.include_router(recommendation_router, dependencies=_FIN)
router.include_router(demo_router)
router.include_router(banks_router)
router.include_router(budgets_router, dependencies=_FIN)
router.include_router(planning_router, dependencies=_FIN)
router.include_router(notifications_router)
router.include_router(export_router, dependencies=_FIN)
router.include_router(analytics_router)
router.include_router(referral_router)
router.include_router(i18n_router)
router.include_router(fx_router)
# 🔴 Plaid обменивает public_token на access_token банка и тянет транзакции — финансовые
# данные в самом прямом смысле. Периметр `_FIN` его не покрывал (H3, подтверждена v8.30.2).
#
# Решение владельца v8.27.0 требует ставить гейт ТОЛЬКО вместе с фронтом, иначе экран
# отдаёт 403 без объяснения (SEV1 `CONSENT-GATE-NO-UI`). Проверено по диску
# (`docs/reports/decisions/2026-09-04_h3_and_jinja_removal_order.md`): у `plaid_router`
# фронта нет ВООБЩЕ — ни в `app.js`, ни в React, а в РФ-сборке он отвечает 404 на всё.
# Оговорка защищает от отказа без объяснения; здесь защищать нечего.
#
# `banks_router` — другой случай: его зовёт `app.js` (импорт выписки), и гейт туда приедет
# вместе с переносом импорта в React, в одном батче с ним.
router.include_router(plaid_router, dependencies=_FIN)
router.include_router(experiments_router)
router.include_router(experiments_admin_router)
router.include_router(telegram_router)
router.include_router(subscription_router)
