from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RawHotspot(Base):
    """原始热点数据表。"""

    __tablename__ = "raw_hotspots"

    # 保存采集器返回的原始热点结果，方便后续追溯和重跑。
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_platform: Mapped[str] = mapped_column(String(100), index=True)
    source_channel: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score: Mapped[str | None] = mapped_column(String(100), nullable=True)
    region: Mapped[str] = mapped_column(String(20), default="cn")
    language: Mapped[str] = mapped_column(String(20), default="zh-CN")
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    raw_payload: Mapped[dict] = mapped_column(JSON)


class StandardHotspot(Base):
    """标准化后的热点数据表。"""

    __tablename__ = "standard_hotspots"

    # 保存统一对象结构，供阶段二和阶段三继续消费。
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    raw_hotspot_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_platform: Mapped[str] = mapped_column(String(100), index=True)
    source_channel: Mapped[str] = mapped_column(String(100), index=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score: Mapped[str | None] = mapped_column(String(100), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    region: Mapped[str] = mapped_column(String(20), default="cn")
    language: Mapped[str] = mapped_column(String(20), default="zh-CN")
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
