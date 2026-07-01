from fastapi import APIRouter

from app.api.collect_runs import router as collect_runs_router
from app.api.health import router as health_router
from app.api.hotspots import router as hotspots_router

router = APIRouter()
router.include_router(health_router)
router.include_router(collect_runs_router)
router.include_router(hotspots_router)
