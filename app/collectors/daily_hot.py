from app.collectors.base import BaseCollector
from app.schemas.hotspot import HotspotItem


class DailyHotCollector(BaseCollector):
    """DailyHotApi 采集器占位实现。"""

    name = "daily_hot_api"

    def collect(self) -> list[HotspotItem]:
        """采集 DailyHotApi 热点数据。"""
        # 当前只保留占位结构，后续在真实链路任务中接入接口调用。
        return []
