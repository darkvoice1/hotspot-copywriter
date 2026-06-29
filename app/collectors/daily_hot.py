from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote

import httpx

from app.collectors.base import BaseCollector
from app.core.config import settings
from app.schemas.hotspot import HotspotItem


class WeiboHotCollector(BaseCollector):
    """微博热搜采集器。"""

    name = "weibo_hot"

    def __init__(self, timeout_seconds: float = settings.collector_timeout_seconds) -> None:
        """初始化微博热搜采集配置。"""
        self.timeout_seconds = timeout_seconds

    def collect(self) -> list[HotspotItem]:
        """采集微博热搜数据。"""
        response = httpx.get(
            "https://weibo.com/ajax/side/hotSearch",
            headers={
                "Referer": "https://weibo.com/",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                ),
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        return self.map_response(payload)

    def map_response(self, payload: dict[str, Any]) -> list[HotspotItem]:
        """将微博热搜返回内容映射为标准热点对象。"""
        realtime_items = payload.get("data", {}).get("realtime", [])
        if not isinstance(realtime_items, list):
            return []

        hotspots: list[HotspotItem] = []
        for index, item in enumerate(realtime_items, start=1):
            if not isinstance(item, dict):
                continue

            title = item.get("word") or item.get("word_scheme")
            if not title:
                continue

            title_text = str(title)
            hotspots.append(
                HotspotItem(
                    title=title_text,
                    summary=_to_optional_string(item.get("word_scheme") or f"#{title_text}#"),
                    source_platform="weibo",
                    source_channel="热搜榜",
                    source_url=f"https://s.weibo.com/weibo?q={quote(title_text)}",
                    rank=index,
                    score=_to_optional_string(item.get("num")),
                    published_at=_to_datetime(item.get("onboard_time")),
                    region="cn",
                    language="zh-CN",
                    raw_payload=item,
                )
            )

        return hotspots


DailyHotCollector = WeiboHotCollector


def _to_optional_string(value: Any) -> str | None:
    """将可选值转换为字符串。"""
    if value is None:
        return None
    return str(value)


def _to_datetime(value: Any) -> datetime | None:
    """将秒级时间戳转换为 UTC 时间。"""
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(float(value), tz=UTC)
    except (TypeError, ValueError, OSError):
        return None
