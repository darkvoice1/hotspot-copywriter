from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.hotspot import StandardHotspot
from app.schemas.hotspot import HotspotItem


def normalize_hotspot(item: HotspotItem) -> HotspotItem:
    """按统一 schema 再校验一次热点对象。"""
    return HotspotItem.model_validate(item.model_dump())


def save_standard_hotspot(
    session: Session,
    item: HotspotItem,
    batch_id: str,
    raw_hotspot_id: int | None = None,
) -> StandardHotspot:
    """保存标准热点对象并返回数据库记录。"""
    normalized_item = normalize_hotspot(item)
    hotspot = StandardHotspot(
        batch_id=batch_id,
        raw_hotspot_id=raw_hotspot_id,
        title=normalized_item.title,
        summary=normalized_item.summary,
        source_platform=normalized_item.source_platform,
        source_channel=normalized_item.source_channel,
        source_url=normalized_item.source_url,
        rank=normalized_item.rank,
        score=normalized_item.score,
        published_at=normalized_item.published_at,
        fetched_at=normalized_item.fetched_at,
        region=normalized_item.region,
        language=normalized_item.language,
        raw_payload=normalized_item.raw_payload,
    )

    session.add(hotspot)
    session.commit()
    session.refresh(hotspot)
    return hotspot


def get_standard_hotspot(session: Session, hotspot_id: int) -> StandardHotspot | None:
    """按 ID 读取标准热点记录。"""
    return session.get(StandardHotspot, hotspot_id)


def list_standard_hotspots_by_batch(session: Session, batch_id: str) -> list[StandardHotspot]:
    """按批次读取标准热点记录。"""
    statement = (
        select(StandardHotspot)
        .where(StandardHotspot.batch_id == batch_id)
        .order_by(StandardHotspot.rank.is_(None), StandardHotspot.rank, StandardHotspot.id)
    )
    return list(session.scalars(statement).all())
