from app.collectors.base import BaseCollector
from app.schemas.hotspot import HotspotItem


class RSSHubCollector(BaseCollector):
    name = "rsshub"

    def collect(self) -> list[HotspotItem]:
        """Placeholder collector for RSSHub integration."""
        return []
