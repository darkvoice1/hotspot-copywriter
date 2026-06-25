from abc import ABC, abstractmethod

from app.schemas.hotspot import HotspotItem


class BaseCollector(ABC):
    name: str

    @abstractmethod
    def collect(self) -> list[HotspotItem]:
        """Collect hotspot items from a source."""
