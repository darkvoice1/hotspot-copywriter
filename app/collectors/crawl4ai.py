from app.collectors.base import BaseCollector
from app.schemas.hotspot import HotspotItem


class Crawl4AICollector(BaseCollector):
    """Crawl4AI 采集器占位实现。"""

    name = "crawl4ai"

    def collect(self) -> list[HotspotItem]:
        """采集需要补漏的热点数据。"""
        # 第一版不做广域抓取，只为后续定点补漏预留入口。
        return []
