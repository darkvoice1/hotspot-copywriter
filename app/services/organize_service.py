import re
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.hotspot import StandardHotspot
from app.models.organized_hotspot import OrganizedHotspot
from app.schemas.organized_hotspot import OrganizedHotspotItem
from app.services.hotspot_service import list_standard_hotspots_by_batch


@dataclass(frozen=True)
class DeduplicatedHotspot:
    """阶段二清洗去重后的热点中间结果。"""

    cleaned_title: str
    representative_hotspot_id: int
    source_hotspot_ids: list[int] = field(default_factory=list)
    source_platforms: list[str] = field(default_factory=list)
    representative_hotspot: StandardHotspot | None = None

    @property
    def source_count(self) -> int:
        """返回该热点聚合到的来源记录数量。"""
        return len(self.source_hotspot_ids)


_TOPIC_WRAPPER_PATTERN = re.compile(r"^[#＃]+|[#＃]+$")
_SPACE_PATTERN = re.compile(r"\s+")


def clean_hotspot_title(title: str) -> str:
    """清洗热点标题用于确定性去重。"""
    cleaned_title = title.strip()
    cleaned_title = _TOPIC_WRAPPER_PATTERN.sub("", cleaned_title)
    cleaned_title = _SPACE_PATTERN.sub(" ", cleaned_title)
    return cleaned_title.strip()


def deduplicate_hotspots(hotspots: list[StandardHotspot]) -> list[DeduplicatedHotspot]:
    """对标准热点列表做标题清洗和确定性去重。"""
    grouped_hotspots: dict[str, list[StandardHotspot]] = {}
    for hotspot in hotspots:
        cleaned_title = clean_hotspot_title(hotspot.title)
        if not cleaned_title:
            continue
        grouped_hotspots.setdefault(cleaned_title, []).append(hotspot)

    deduplicated_items: list[DeduplicatedHotspot] = []
    for cleaned_title, grouped_items in grouped_hotspots.items():
        representative = _select_representative_hotspot(grouped_items)
        source_hotspot_ids = [item.id for item in grouped_items]
        source_platforms = sorted({item.source_platform for item in grouped_items})
        deduplicated_items.append(
            DeduplicatedHotspot(
                cleaned_title=cleaned_title,
                representative_hotspot_id=representative.id,
                source_hotspot_ids=source_hotspot_ids,
                source_platforms=source_platforms,
                representative_hotspot=representative,
            )
        )

    return deduplicated_items


def deduplicate_hotspots_by_batch(session: Session, batch_id: str) -> list[DeduplicatedHotspot]:
    """按批次读取标准热点并输出清洗去重结果。"""
    hotspots = list_standard_hotspots_by_batch(session=session, batch_id=batch_id)
    return deduplicate_hotspots(hotspots)


def normalize_organized_hotspot(item: OrganizedHotspotItem) -> OrganizedHotspotItem:
    """按统一 schema 再校验一次整理结果对象。"""
    return OrganizedHotspotItem.model_validate(item.model_dump())


def save_organized_hotspot(session: Session, item: OrganizedHotspotItem) -> OrganizedHotspot:
    """保存阶段二整理结果并返回数据库记录。"""
    normalized_item = normalize_organized_hotspot(item)
    organized_hotspot = OrganizedHotspot(
        batch_id=normalized_item.batch_id,
        topic_title=normalized_item.topic_title,
        representative_hotspot_id=normalized_item.representative_hotspot_id,
        source_hotspot_ids=normalized_item.source_hotspot_ids,
        source_platforms=normalized_item.source_platforms,
        category=normalized_item.category,
        tags=normalized_item.tags,
        summary=normalized_item.summary,
        organize_version=normalized_item.organize_version,
    )

    session.add(organized_hotspot)
    session.commit()
    session.refresh(organized_hotspot)
    return organized_hotspot


def get_organized_hotspot(session: Session, organized_hotspot_id: int) -> OrganizedHotspot | None:
    """按 ID 读取阶段二整理结果。"""
    return session.get(OrganizedHotspot, organized_hotspot_id)


def list_organized_hotspots_by_batch(session: Session, batch_id: str) -> list[OrganizedHotspot]:
    """按批次读取阶段二整理结果。"""
    statement = (
        select(OrganizedHotspot)
        .where(OrganizedHotspot.batch_id == batch_id)
        .order_by(OrganizedHotspot.id)
    )
    return list(session.scalars(statement).all())


def list_organized_hotspots_by_batch_id(batch_id: str) -> list[OrganizedHotspot]:
    """按批次读取阶段二整理结果并自行管理数据库会话。"""
    init_db()
    with SessionLocal() as session:
        return list_organized_hotspots_by_batch(session=session, batch_id=batch_id)


def _select_representative_hotspot(hotspots: list[StandardHotspot]) -> StandardHotspot:
    """选择去重分组中的代表热点。"""
    return sorted(
        hotspots,
        key=lambda item: (
            item.rank is None,
            item.rank or 0,
            item.id,
        ),
    )[0]
