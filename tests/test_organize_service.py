from uuid import uuid4

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.schemas.hotspot import HotspotItem
from app.services.hotspot_service import save_standard_hotspot
from app.services.organize_service import clean_hotspot_title, deduplicate_hotspots_by_batch


def test_clean_hotspot_title_removes_topic_wrapper_and_extra_spaces() -> None:
    """验证热点标题清洗会去除话题符号和多余空格。"""
    cleaned_title = clean_hotspot_title("  #  测试   热点  #  ")

    assert cleaned_title == "测试 热点"


def test_deduplicate_hotspots_by_batch_merges_same_cleaned_title() -> None:
    """验证同批次内清洗后标题相同的热点会被合并。"""
    init_db()
    batch_id = f"organize-dedup-test-{uuid4().hex}"

    with SessionLocal() as session:
        weibo_hotspot = save_standard_hotspot(
            session=session,
            item=HotspotItem(
                title="#测试热点#",
                source_platform="weibo",
                source_channel="热搜榜",
                rank=2,
                raw_payload={"source": "weibo"},
            ),
            batch_id=batch_id,
        )
        douyin_hotspot = save_standard_hotspot(
            session=session,
            item=HotspotItem(
                title="测试热点",
                source_platform="douyin",
                source_channel="热点榜",
                rank=1,
                raw_payload={"source": "douyin"},
            ),
            batch_id=batch_id,
        )

        deduplicated_items = deduplicate_hotspots_by_batch(session=session, batch_id=batch_id)

    assert len(deduplicated_items) == 1
    assert deduplicated_items[0].cleaned_title == "测试热点"
    assert deduplicated_items[0].representative_hotspot_id == douyin_hotspot.id
    assert deduplicated_items[0].source_hotspot_ids == [douyin_hotspot.id, weibo_hotspot.id]
    assert deduplicated_items[0].source_platforms == ["douyin", "weibo"]
    assert deduplicated_items[0].source_count == 2


def test_deduplicate_hotspots_by_batch_keeps_different_titles() -> None:
    """验证不同标题的热点不会被错误合并。"""
    init_db()
    batch_id = f"organize-keep-test-{uuid4().hex}"

    with SessionLocal() as session:
        save_standard_hotspot(
            session=session,
            item=HotspotItem(
                title="热点甲",
                source_platform="weibo",
                source_channel="热搜榜",
                raw_payload={},
            ),
            batch_id=batch_id,
        )
        save_standard_hotspot(
            session=session,
            item=HotspotItem(
                title="热点乙",
                source_platform="bilibili",
                source_channel="热门榜",
                raw_payload={},
            ),
            batch_id=batch_id,
        )

        deduplicated_items = deduplicate_hotspots_by_batch(session=session, batch_id=batch_id)

    assert [item.cleaned_title for item in deduplicated_items] == ["热点甲", "热点乙"]


def test_deduplicate_hotspots_by_batch_returns_empty_list_for_empty_batch() -> None:
    """验证空批次会返回空去重结果。"""
    init_db()

    with SessionLocal() as session:
        deduplicated_items = deduplicate_hotspots_by_batch(
            session=session,
            batch_id=f"empty-batch-{uuid4().hex}",
        )

    assert deduplicated_items == []
