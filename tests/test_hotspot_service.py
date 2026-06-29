from datetime import datetime

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.schemas.hotspot import HotspotItem
from app.services.hotspot_service import get_standard_hotspot, save_standard_hotspot


def test_save_and_read_standard_hotspot() -> None:
    """验证标准热点对象可以写入并读回。"""
    init_db()
    item = HotspotItem(
        title="测试热点",
        summary="测试摘要",
        source_platform="unit_test",
        source_channel="hot_search",
        source_url="https://example.com/hotspot",
        rank=1,
        score="1000",
        published_at=datetime(2026, 6, 29, 8, 0, 0),
        region="cn",
        language="zh-CN",
        raw_payload={"title": "测试热点"},
    )

    with SessionLocal() as session:
        saved_hotspot = save_standard_hotspot(
            session=session,
            item=item,
            batch_id="test-batch-001",
        )
        loaded_hotspot = get_standard_hotspot(session, saved_hotspot.id)

    assert loaded_hotspot is not None
    assert loaded_hotspot.batch_id == "test-batch-001"
    assert loaded_hotspot.title == "测试热点"
    assert loaded_hotspot.source_platform == "unit_test"
    assert loaded_hotspot.raw_payload == {"title": "测试热点"}
