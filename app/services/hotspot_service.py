from app.schemas.hotspot import HotspotItem


def normalize_hotspot(item: HotspotItem) -> HotspotItem:
    """按统一 schema 再校验一次热点对象。"""
    return HotspotItem.model_validate(item.model_dump())
