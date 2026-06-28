from app.collectors.base import BaseCollector
from app.schemas.hotspot import HotspotItem


class RSSHubCollector(BaseCollector):
    """RSSHub 采集器占位实现。"""

    name = "rsshub"

    def collect(self) -> list[HotspotItem]:
        """采集 RSSHub 热点数据。"""
        # 第一版先不接真实逻辑，等待具体来源清单收敛后再实现。
        return []
