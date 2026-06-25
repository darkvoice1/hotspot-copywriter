from app.collectors.base import BaseCollector
from app.schemas.hotspot import HotspotItem


class DailyHotCollector(BaseCollector):
    name = "daily_hot_api"

    def collect(self) -> list[HotspotItem]:
        """Placeholder collector for DailyHotApi integration."""
        return []
