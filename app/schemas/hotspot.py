from datetime import datetime

from pydantic import BaseModel


class HotspotItem(BaseModel):
    title: str
    summary: str | None = None
    source_platform: str
    source_channel: str
    source_url: str | None = None
    rank: int | None = None
    score: str | None = None
    published_at: datetime | None = None
    fetched_at: datetime | None = None
    region: str = "cn"
    language: str = "zh-CN"
    raw_payload: dict | None = None
