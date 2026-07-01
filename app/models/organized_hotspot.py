from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OrganizedHotspot(Base):
    """阶段二整理后的热点主题表。"""

    __tablename__ = "organized_hotspots"

    # 保存阶段二整理结果，供后续分类、摘要和文案生成复用。
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    batch_id: Mapped[str] = mapped_column(String(64), index=True)
    topic_title: Mapped[str] = mapped_column(String(500), index=True)
    representative_hotspot_id: Mapped[int] = mapped_column(Integer, index=True)
    source_hotspot_ids: Mapped[list[int]] = mapped_column(JSON)
    source_platforms: Mapped[list[str]] = mapped_column(JSON)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    organize_version: Mapped[str] = mapped_column(String(50), default="v1", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

