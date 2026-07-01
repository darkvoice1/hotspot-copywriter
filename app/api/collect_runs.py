from fastapi import APIRouter

from app.scheduler.runner import run_collectors_once
from app.schemas.collect_run import CollectRunResponse

router = APIRouter(tags=["collect-runs"])


@router.post("/collect-runs", response_model=CollectRunResponse)
def create_collect_run() -> CollectRunResponse:
    """手动触发一次热点采集。"""
    summary = run_collectors_once()
    return CollectRunResponse.from_summary(summary)

