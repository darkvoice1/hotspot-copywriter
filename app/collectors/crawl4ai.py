from app.collectors.base import BaseCollector
from app.schemas.hotspot import HotspotItem


class Crawl4AICollector(BaseCollector):
    name = "crawl4ai"

    def collect(self) -> list[HotspotItem]:
        """Placeholder collector for Crawl4AI integration."""
        return []
