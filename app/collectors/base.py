from abc import ABC, abstractmethod

from app.schemas.hotspot import HotspotItem


class BaseCollector(ABC):
    """采集器抽象基类。"""

    name: str

    @abstractmethod
    def collect(self) -> list[HotspotItem]:
        """采集热点并返回标准对象列表。"""
