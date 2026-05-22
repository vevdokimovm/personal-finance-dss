from fastapi import APIRouter

from app.api.routes_analysis import router as analysis_router
from app.api.routes_banks import router as banks_router
from app.api.routes_demo import router as demo_router
from app.api.routes_goals import router as goals_router
from app.api.routes_liquid_assets import router as liquid_assets_router
from app.api.routes_obligations import router as obligations_router
from app.api.routes_planning import router as planning_router
from app.api.routes_recommendation import router as recommendation_router
from app.api.routes_transactions import router as transactions_router
from app.api.routes_user_prefs import router as user_prefs_router
from app.config import settings


router = APIRouter(prefix=settings.API_PREFIX)
router.include_router(transactions_router)
router.include_router(obligations_router)
router.include_router(goals_router)
router.include_router(liquid_assets_router)
router.include_router(user_prefs_router)
router.include_router(analysis_router)
router.include_router(recommendation_router)
router.include_router(demo_router)
router.include_router(banks_router)
router.include_router(planning_router)
