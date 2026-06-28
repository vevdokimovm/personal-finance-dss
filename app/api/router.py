from fastapi import APIRouter

from app.api.routes_analysis import router as analysis_router
from app.api.routes_auth import router as auth_router
from app.api.routes_banks import router as banks_router
from app.api.routes_budgets import router as budgets_router
from app.api.routes_categories import router as categories_router
from app.api.routes_demo import router as demo_router
from app.api.routes_experiments import admin_router as experiments_admin_router
from app.api.routes_experiments import router as experiments_router
from app.api.routes_fx import router as fx_router
from app.api.routes_goals import router as goals_router
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
from app.api.routes_user_prefs import router as user_prefs_router
from app.config import settings

router = APIRouter(prefix=settings.API_PREFIX)
router.include_router(auth_router)
router.include_router(transactions_router)
router.include_router(obligations_router)
router.include_router(goals_router)
router.include_router(liquid_assets_router)
router.include_router(categories_router)
router.include_router(user_prefs_router)
router.include_router(analysis_router)
router.include_router(recommendation_router)
router.include_router(demo_router)
router.include_router(banks_router)
router.include_router(budgets_router)
router.include_router(planning_router)
router.include_router(notifications_router)
router.include_router(export_router)
router.include_router(analytics_router)
router.include_router(referral_router)
router.include_router(i18n_router)
router.include_router(fx_router)
router.include_router(plaid_router)
router.include_router(experiments_router)
router.include_router(experiments_admin_router)
