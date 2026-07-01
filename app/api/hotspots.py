from fastapi import APIRouter, Query

from app.schemas.hotspot import StandardHotspotResponse
from app.schemas.organized_hotspot import OrganizedHotspotResponse
from app.services.hotspot_service import list_standard_hotspots_by_batch_id
from app.services.organize_service import list_organized_hotspots_by_batch_id

router = APIRouter(prefix="/hotspots", tags=["hotspots"])


@router.get("/standard", response_model=list[StandardHotspotResponse])
def list_standard_hotspots(
    batch_id: str = Query(..., description="采集批次号。"),
) -> list[StandardHotspotResponse]:
    """按批次查询阶段一标准热点。"""
    hotspots = list_standard_hotspots_by_batch_id(batch_id=batch_id)
    return [StandardHotspotResponse.from_model(hotspot) for hotspot in hotspots]


@router.get("/organized", response_model=list[OrganizedHotspotResponse])
def list_organized_hotspots(
    batch_id: str = Query(..., description="采集批次号。"),
) -> list[OrganizedHotspotResponse]:
    """按批次查询阶段二整理结果。"""
    hotspots = list_organized_hotspots_by_batch_id(batch_id=batch_id)
    return [OrganizedHotspotResponse.from_model(hotspot) for hotspot in hotspots]
