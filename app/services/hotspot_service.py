from app.schemas.hotspot import HotspotItem


def normalize_hotspot(item: HotspotItem) -> HotspotItem:
    """Normalize collector output into the shared hotspot schema."""
    return item
